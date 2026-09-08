#!/usr/bin/env python3
"""Inspect an Agent Skill package or folder and emit structured diagnostics."""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import stat
import sys
import tempfile
import zipfile
from urllib.parse import unquote
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

from portable_zip_paths import (
    normalize_member_path,
    validate_portable_path_records,
    validate_portable_zip_members,
)

MAX_DEFAULT_TREE_FILES = 200
MAX_ZIP_MEMBERS = 1000
MAX_ZIP_UNCOMPRESSED_BYTES = 100 * 1024 * 1024
MAX_ZIP_MEMBER_BYTES = 25 * 1024 * 1024
MAX_DIRECTORY_FILES = 1000
MAX_DIRECTORY_ENTRIES = 5000
MAX_DIRECTORY_DEPTH = 32
MAX_DIRECTORY_ENTRIES_PER_DIRECTORY = 1000
MAX_DIRECTORY_TOTAL_BYTES = 100 * 1024 * 1024
MAX_DIRECTORY_FILE_BYTES = 25 * 1024 * 1024
MAX_COMPRESSION_RATIO = 100.0
MAX_READ_BYTES = 1_000_000
# This is an inspector resource boundary, not a vendor upload claim.
MAX_INSPECTOR_INPUT_ZIP_BYTES = 30_000_000
INSPECTION_SCHEMA_VERSION = 6
ZIP_STREAM_CHUNK_BYTES = 1024 * 1024
TEXT_SNIFF_BYTES = 8192
MAX_YAML_NESTING_DEPTH = 64
MAX_YAML_INTEGER_DIGITS = 4096
SECRET_SCAN_NOTE = (
    "secret scanning is heuristic and non-exhaustive; it scans known text/config formats and "
    "regular files that pass bounded content sniffing. Eligible files are read completely "
    "within package safety limits unless --max-safety-scan-bytes explicitly requests "
    "exploratory partial scanning."
)
PORTABLE_FRONTMATTER_KEYS = {"name", "description"}
# These preserve the previous portable profile: fields are allowed because at
# least one supported surface understands them, but are surfaced for review.
OPTIONAL_PLATFORM_FRONTMATTER_KEYS = {"dependencies", "license", "allowed-tools", "metadata", "version", "compatibility"}
OPENAI_FRONTMATTER_KEYS = {"name", "description", "license", "metadata", "version", "compatibility"}
AGENT_SKILL_NAME_LIMIT = 64
AGENT_SKILL_DESCRIPTION_LIMIT = 1024
AGENT_SKILL_COMPATIBILITY_LIMIT = 500
OPENAI_SHORT_DESCRIPTION_MIN_LENGTH = 25
OPENAI_SHORT_DESCRIPTION_MAX_LENGTH = 64
OPENAI_ICON_FIELDS = ("icon_small", "icon_large")
TEXT_EXTENSIONS = {
    ".md", ".txt", ".py", ".sh", ".yaml", ".yml", ".json", ".toml",
    ".ini", ".cfg", ".conf", ".properties", ".csv", ".tsv", ".log",
    ".rst", ".xml", ".html", ".css", ".js", ".mjs", ".cjs", ".jsx",
    ".ts", ".tsx", ".ps1", ".psm1", ".psd1", ".bat", ".cmd", ".rb",
    ".php", ".pl", ".go", ".java", ".c", ".h", ".cc", ".cpp", ".hpp",
}
TEXT_FILENAMES = {".env", ".envrc", ".editorconfig", "makefile", "dockerfile"}
TEMPLATE_MARKER_PATTERNS = [
    # Match likely unfinished markers while avoiding docs that merely describe them.
    re.compile(r"(?im)^\s*(?:[-*]\s*)?(?:TO" + r"DO|FIXME|XXX)\b\s*:?") ,
    re.compile(r"<[^>\n]*place" + r"holder[^>\n]*>", re.IGNORECASE),
    re.compile(r"\[[^\]\n]*place" + r"holder[^\]\n]*\]", re.IGNORECASE),
    re.compile("replace with " + "actual", re.IGNORECASE),
    re.compile("example helper " + "script", re.IGNORECASE),
    re.compile("example " + "asset", re.IGNORECASE),
]
SECRET_FILENAME_PATTERNS = [
    re.compile(r"(^|/|\\)\.env($|\.)|\.env$", re.IGNORECASE),
    re.compile(r"id_rsa|id_dsa|id_ed25519|id_ecdsa", re.IGNORECASE),
    re.compile(r"private[-_ ]?key|\.pem$|\.p12$|\.pfx$", re.IGNORECASE),
    re.compile(r"secret|credential|token", re.IGNORECASE),
    re.compile(r"service[-_]?account", re.IGNORECASE),
]
SECRET_CONFIG_FILENAMES = {
    ".git-credentials", ".netrc", ".npmrc", ".pypirc",
    "auth", "config", "credential", "credentials", "settings",
}
SECRET_CONTENT_PATTERNS = [
    ("private key block", "secret_private_key_block", "error", re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----")),
    ("provider-style api key", "secret_provider_api_key", "error", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}\b")),
    ("OpenAI API key pattern", "secret_openai_api_key", "error", re.compile(r"\bsk-(?!ant-)[A-Za-z0-9_-]{20,}\b")),
    ("Stripe live secret key", "secret_stripe_live_key", "error", re.compile(r"\b(?:sk|rk)_live_[A-Za-z0-9]{16,}\b")),
    ("AWS access key ID", "secret_aws_access_key", "error", re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
    ("Google API key", "secret_google_api_key", "error", re.compile(r"\bAIza[A-Za-z0-9_-]{35}\b")),
    ("GitLab personal access token", "secret_gitlab_token", "error", re.compile(r"\bglpat-[A-Za-z0-9_-]{20,}\b")),
    ("GitHub fine-grained personal access token", "secret_github_fine_grained_token", "error", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b")),
    ("github token", "secret_github_token", "error", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b")),
    ("slack token", "secret_slack_token", "error", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b")),
    ("google service account", "secret_google_service_account", "error", re.compile(r"\"type\"\s*:\s*\"service_account\"")),
    ("jwt-like token", "secret_jwt_like_token", "error", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b")),
    ("api key assignment", "secret_api_key_assignment", "error", re.compile(r"(?i)\b(api[_-]?key|access[_-]?token|secret[_-]?key|client[_-]?secret|refresh[_-]?token)\b\s*[:=]\s*['\"]?[A-Za-z0-9_./+=:-]{12,}")),
    ("password assignment", "secret_password_assignment", "warning", re.compile(r"(?i)\bpassword\b\s*[:=]\s*['\"]?[^'\"\s]{8,}")),
]
HIGH_CONFIDENCE_PII_PATTERNS = (
    re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
    re.compile(r"(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)"),
)
# This reserved, self-scoped annotation documents repository-only helpers
# without turning them into runtime resource requirements. It deliberately
# uses an HTML comment rather than a normal Markdown resource link, so release
# archives may omit the named files. Only a validated Skill Forge package may
# use it; generic Skills retain the ordinary resource-reference rules.
SOURCE_ONLY_DECLARATION_PATTERN = re.compile(
    r"<!--\s*skill-forge:source-only(?:\s+(.*?))?\s*-->",
    re.IGNORECASE | re.DOTALL,
)
SHELL_SCRIPT_EXTENSIONS = {".bash", ".command", ".ksh", ".sh", ".zsh"}
POWERSHELL_SCRIPT_EXTENSIONS = {".ps1", ".psm1", ".psd1"}
WINDOWS_BATCH_EXTENSIONS = {".bat", ".cmd"}
PYTHON_SCRIPT_EXTENSIONS = {".py", ".pyw"}
JAVASCRIPT_SCRIPT_EXTENSIONS = {".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx"}
DANGEROUS_SCRIPT_EXTENSIONS = (
    SHELL_SCRIPT_EXTENSIONS
    | POWERSHELL_SCRIPT_EXTENSIONS
    | WINDOWS_BATCH_EXTENSIONS
    | PYTHON_SCRIPT_EXTENSIONS
    | JAVASCRIPT_SCRIPT_EXTENSIONS
)
# These are executable source formats when found outside the detected Skill
# root. They are deliberately broader than the command scanner, which covers
# only the high-confidence language patterns declared below.
EXECUTABLE_CODE_EXTENSIONS = DANGEROUS_SCRIPT_EXTENSIONS | {
    ".py", ".pyw", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx",
    ".rb", ".pl", ".php", ".lua", ".exe", ".com",
}
SHELL_SHEBANG_PATTERN = re.compile(r"#!.*\b(?:ba|z|k)?sh\b")
PYTHON_SHEBANG_PATTERN = re.compile(r"#!.*\bpython(?:[0-9.]*)?\b")
JAVASCRIPT_SHEBANG_PATTERN = re.compile(r"#!.*\b(?:node|deno|bun)\b")
DANGEROUS_COMMAND_PATTERNS = [
    (
        "remote script piped into a shell",
        re.compile(
            r"\b(?:curl|wget|fetch)\b[^\n|;]*\|\s*"
            r"(?:(?:['\"]?(?:/(?:[A-Za-z0-9._+-]+/)+)?(?:env|command)\b['\"]?)\s+)?"
            r"(?:sudo\s+(?:-\S+\s+)*)?"
            r"['\"]?(?:/(?:[A-Za-z0-9._+-]+/)+)?(?:ba|z|k)?sh\b['\"]?",
            re.IGNORECASE,
        ),
    ),
    ("remote script sourced from a shell", re.compile(r"\b(?:source|\.)\s*<\(\s*(?:curl|wget|fetch)\b", re.IGNORECASE)),
    ("remote script evaluated by a shell", re.compile(r"\beval\s+(?:['\"])?\$\(\s*(?:curl|wget|fetch)\b", re.IGNORECASE)),
    ("recursive force-remove of a root or home path", re.compile(r"\b(?:sudo\s+)?rm\b(?=[^\n]*(?:--(?:recursive|force)\b|-[A-Za-z]*[rf][A-Za-z]*))[^\n]*?(?:['\"]?(?:/|~|\$HOME|\$\{HOME\})['\"]?)(?:[\s/]|$)", re.IGNORECASE)),
    ("recursive permission change of a root or home path", re.compile(r"\b(?:sudo\s+)?chmod\b(?=[^\n]*(?:--recursive\b|-[A-Za-z]*R[A-Za-z]*))[^\n]*?(?:['\"]?(?:/|~|\$HOME|\$\{HOME\})['\"]?)(?:[\s/]|$)", re.IGNORECASE)),
    ("fork bomb", re.compile(r":\s*\(\s*\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;\s*:")),
    ("raw disk write via dd", re.compile(r"\bdd\b[^\n]*\bof\s*=\s*/dev/", re.IGNORECASE)),
    ("filesystem format via mkfs", re.compile(r"\bmkfs(?:\.\w+)?\b", re.IGNORECASE)),
    ("remote content piped into PowerShell evaluation", re.compile(r"\b(?:invoke-webrequest|iwr|invoke-restmethod|irm)\b[^\r\n|;]*\|\s*(?:invoke-expression|iex)\b", re.IGNORECASE)),
    ("remote content evaluated by PowerShell", re.compile(r"\b(?:invoke-expression|iex)\b\s*(?:\(?\s*(?:invoke-webrequest|iwr|invoke-restmethod|irm)\b|\$\([^\r\n]*(?:invoke-webrequest|iwr|invoke-restmethod|irm)\b)", re.IGNORECASE)),
    ("remote content piped into PowerShell", re.compile(r"\b(?:curl|wget)\b[^\r\n|;]*\|\s*(?:powershell|pwsh)(?:\.exe)?\b", re.IGNORECASE)),
    ("recursive forced deletion of a Windows root, home, or system path", re.compile(r"\b(?:remove-item|ri|rm|del)\b(?=[^\r\n]*(?:-recurse|/s\b))(?=[^\r\n]*(?:-force|/q\b))[^\r\n]*(?:[a-z]:\\+(?:windows(?:\\+|(?=\s*$))|(?=\s*$))|\$(?:home|env:userprofile|env:systemdrive|env:windir)\b|%(?:userprofile|homedrive|systemdrive|windir)%)", re.IGNORECASE)),
    ("recursive forced deletion of a Windows root, home, or system path", re.compile(r"\b(?:rd|rmdir)\b(?=[^\r\n]*/s\b)(?=[^\r\n]*/q\b)[^\r\n]*(?:[a-z]:\\+(?:windows(?:\\+|(?=\s*$))|(?=\s*$))|%(?:userprofile|homedrive|systemdrive|windir)%)", re.IGNORECASE)),
]
PYTHON_DANGEROUS_COMMAND_PATTERNS = [
    (
        "Python recursively removes a literal root or resolved home path",
        re.compile(
            r"\bshutil\.rmtree\s*\(\s*(?:[rubf]*['\"]/['\"]|(?:pathlib\.)?Path\.home\(\)|os\.path\.expanduser\(\s*['\"]~['\"]\s*\))",
            re.IGNORECASE,
        ),
    ),
    (
        "Python unlinks a literal root or resolved home path",
        re.compile(
            r"\bos\.(?:remove|unlink)\s*\(\s*(?:[rubf]*['\"]/['\"]|(?:pathlib\.)?Path\.home\(\)|os\.path\.expanduser\(\s*['\"]~['\"]\s*\))",
            re.IGNORECASE,
        ),
    ),
    (
        "Python Path removes a literal root or resolved home path",
        re.compile(
            r"(?:(?:pathlib\.)?Path\s*\(\s*['\"]/['\"]\s*\)|(?:pathlib\.)?Path\.home\(\))\s*\.(?:unlink|rmdir)\s*\(",
            re.IGNORECASE,
        ),
    ),
]
JAVASCRIPT_DANGEROUS_COMMAND_PATTERNS = [
    (
        "JavaScript recursively and forcibly removes a root or home path",
        re.compile(
            r"\b(?:fs\.)?rmSync\s*\(\s*(?:['\"]/['\"]|os\.homedir\(\))\s*,\s*\{(?=[^}]*\brecursive\s*:\s*true)(?=[^}]*\bforce\s*:\s*true)[^}]*\}",
            re.IGNORECASE | re.DOTALL,
        ),
    ),
    (
        "JavaScript recursively removes a root or home path",
        re.compile(
            r"\b(?:fs\.)?rmdirSync\s*\(\s*(?:['\"]/['\"]|os\.homedir\(\))\s*,\s*\{(?=[^}]*\brecursive\s*:\s*true)[^}]*\}",
            re.IGNORECASE | re.DOTALL,
        ),
    ),
]

# This is the single source of truth for every machine-readable finding code
# emitted by the inspector. ``finding`` rejects unknown codes so an
# implementation change cannot silently create an undocumented output
# contract. The audit-contract validator compares this catalog with the
# machine-checked catalog in references/inspector-output-schema.md.
FINDING_CODE_CATALOG = (
    "archive_directory_outside_skill_root",
    "archive_executable_code_outside_skill_root",
    "archive_file_outside_skill_root",
    "dangerous_command_scan_truncated",
    "dangerous_command_scan_truncated_outside_root",
    "dangerous_command_scan_unreadable",
    "dangerous_command_scan_unreadable_outside_root",
    "directory_depth_exceeded",
    "directory_file_outside_root",
    "directory_file_directory_prefix_conflict",
    "directory_file_too_large",
    "directory_nonportable_path",
    "directory_portable_identity_collision",
    "directory_root_lstat_failed",
    "directory_root_resolve_failed",
    "directory_root_symlink",
    "directory_scan_incomplete",
    "directory_symlink_found",
    "directory_too_many_entries",
    "directory_too_many_entries_in_directory",
    "directory_too_many_files",
    "directory_total_size_too_large",
    "directory_unsupported_entry",
    "frontmatter_description_too_long",
    "frontmatter_compatibility_invalid",
    "frontmatter_compatibility_too_long",
    "frontmatter_metadata_invalid",
    "frontmatter_description_angle_brackets",
    "frontmatter_description_missing",
    "frontmatter_description_short",
    "frontmatter_description_weak_trigger",
    "frontmatter_invalid_name",
    "frontmatter_missing_or_invalid",
    "frontmatter_name_directory_comparison_invalid",
    "frontmatter_name_directory_mismatch",
    "frontmatter_name_missing",
    "frontmatter_name_too_long",
    "frontmatter_parse_error",
    "frontmatter_platform_optional_keys",
    "frontmatter_unavailable",
    "frontmatter_unexpected_keys",
    "frontmatter_yaml_unsupported",
    "missing_resource_reference",
    "openai_metadata_default_prompt_invalid",
    "openai_metadata_default_prompt_missing_skill_reference",
    "openai_metadata_display_name_invalid",
    "openai_metadata_icon_missing",
    "openai_metadata_icon_path_invalid",
    "openai_metadata_interface_invalid",
    "openai_metadata_missing",
    "openai_metadata_missing_display_name",
    "openai_metadata_missing_interface",
    "openai_metadata_missing_short_description",
    "openai_metadata_short_description_invalid",
    "openai_metadata_short_description_length",
    "openai_metadata_unreadable",
    "openai_metadata_yaml_invalid",
    "openai_metadata_yaml_unsupported",
    "package_folder_large",
    "package_zip_too_large",
    "resource_graph_incomplete",
    "resource_reference_outside_root",
    "resource_reference_unsafe",
    "root_skill_md_missing",
    "scan_coverage_incomplete",
    "script_dangerous_command",
    "script_dangerous_command_outside_root",
    "secret_provider_api_key",
    "secret_provider_api_key_outside_root",
    "secret_api_key_assignment",
    "secret_api_key_assignment_outside_root",
    "secret_aws_access_key",
    "secret_aws_access_key_outside_root",
    "secret_github_fine_grained_token",
    "secret_github_fine_grained_token_outside_root",
    "secret_github_token",
    "secret_github_token_outside_root",
    "secret_gitlab_token",
    "secret_gitlab_token_outside_root",
    "secret_google_api_key",
    "secret_google_api_key_outside_root",
    "secret_google_service_account",
    "secret_google_service_account_outside_root",
    "secret_jwt_like_token",
    "secret_jwt_like_token_outside_root",
    "secret_openai_api_key",
    "secret_openai_api_key_outside_root",
    "secret_password_assignment",
    "secret_password_assignment_outside_root",
    "secret_private_key_block",
    "secret_private_key_block_outside_root",
    "secret_scan_truncated",
    "secret_scan_truncated_outside_root",
    "secret_scan_unreadable",
    "secret_scan_unreadable_outside_root",
    "secret_slack_token",
    "secret_slack_token_outside_root",
    "secret_stripe_live_key",
    "secret_stripe_live_key_outside_root",
    "secret_suspicious_filename",
    "secret_suspicious_filename_outside_root",
    "skill_md_missing",
    "skill_md_multiple",
    "target_upload_limit_exceeded",
    "target_zip_root_layout_invalid",
    "template_marker_found",
    "zip_bad_archive",
    "zip_case_collision_member",
    "zip_control_character_member",
    "zip_directory_member_has_payload",
    "zip_duplicate_member",
    "zip_encrypted_member",
    "zip_file_directory_prefix_conflict_member",
    "zip_high_compression_ratio",
    "zip_member_too_large",
    "zip_missing_top_level_skill_folder",
    "zip_nonportable_separator_member",
    "zip_path_component_too_long",
    "zip_path_too_long",
    "zip_read_error",
    "zip_symlink_member",
    "zip_too_many_members",
    "zip_uncompressed_size_too_large",
    "zip_unicode_casefold_collision_member",
    "zip_unicode_normalization_collision_member",
    "zip_unsafe_member_path",
    "zip_unsupported_member_type",
    "zip_windows_ads_member",
    "zip_windows_invalid_character_member",
    "zip_windows_reserved_name_member",
    "zip_windows_trailing_dot_space_member",
    "zip_zero_compressed_size",
)
FINDING_CODE_SET = frozenset(FINDING_CODE_CATALOG)

# Only these inspector-owned fields may contribute finding severity to summary
# and strict-mode decisions. Parsed manifests are untrusted data and may
# legitimately contain dictionaries named ``severity`` and ``code``.
FINDING_SECTION_KEYS = (
    "zip_preflight_findings",
    "directory_preflight_findings",
    "coverage_findings",
    "outside_root_findings",
    "secret_risk_findings",
    "platform_metadata_findings",
    "agent_metadata_findings",
    "package_size_findings",
    "frontmatter_validation_findings",
    "structural_findings",
    "template_leftover_findings",
    "dangerous_command_findings",
)


@dataclass(frozen=True)
class TargetProfile:
    """The documented contract and explicit compatibility scope for one host."""

    name: str
    summary: str
    recognized_frontmatter_keys: frozenset[str]
    unknown_key_severity: str
    unknown_key_code: str
    name_required: bool
    description_required: bool
    hyphen_case_name: bool
    name_limit: Optional[int]
    validate_openai_metadata: bool
    directory_name_mode: str
    requires_zip_top_level_folder: bool
    product_upload_limit_bytes: Optional[int]

    def json_summary(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "summary": self.summary,
            "product_upload_limit_bytes": self.product_upload_limit_bytes,
            "directory_name_mode": self.directory_name_mode,
            "requires_zip_top_level_folder": self.requires_zip_top_level_folder,
        }


# Target rules live here rather than being spread through validation branches.
# ``portable`` is deliberately conservative but is not a claim that every
# host-specific workflow has been validated.
TARGET_PROFILES: Dict[str, TargetProfile] = {
    "portable": TargetProfile(
        name="portable",
        summary="Conservative shared Agent Skills baseline; does not prove each host-specific workflow.",
        recognized_frontmatter_keys=frozenset(PORTABLE_FRONTMATTER_KEYS | OPTIONAL_PLATFORM_FRONTMATTER_KEYS),
        unknown_key_severity="error",
        unknown_key_code="frontmatter_unexpected_keys",
        name_required=True,
        description_required=True,
        hyphen_case_name=True,
        name_limit=AGENT_SKILL_NAME_LIMIT,
        validate_openai_metadata=True,
        directory_name_mode="exact",
        requires_zip_top_level_folder=False,
        product_upload_limit_bytes=None,
    ),
    "openai": TargetProfile(
        name="openai",
        summary="OpenAI metadata contract plus the shared SKILL.md baseline.",
        recognized_frontmatter_keys=frozenset(OPENAI_FRONTMATTER_KEYS),
        unknown_key_severity="error",
        unknown_key_code="frontmatter_unexpected_keys",
        name_required=True,
        description_required=True,
        hyphen_case_name=True,
        name_limit=AGENT_SKILL_NAME_LIMIT,
        validate_openai_metadata=True,
        directory_name_mode="exact",
        requires_zip_top_level_folder=False,
        product_upload_limit_bytes=None,
    ),
}
CANONICAL_TARGETS = tuple(TARGET_PROFILES)
TARGETS = set(CANONICAL_TARGETS)


def canonical_target(target: str) -> str:
    """Return the canonical target name and reject unknown profile requests."""
    if target not in TARGETS:
        raise ValueError(f"unsupported target profile: {target}")
    return target


def target_profile(target: str) -> TargetProfile:
    return TARGET_PROFILES[canonical_target(target)]


@dataclass(frozen=True)
class InspectionLimits:
    max_zip_members: int = MAX_ZIP_MEMBERS
    max_zip_uncompressed_bytes: int = MAX_ZIP_UNCOMPRESSED_BYTES
    max_zip_member_bytes: int = MAX_ZIP_MEMBER_BYTES
    max_directory_files: int = MAX_DIRECTORY_FILES
    max_directory_entries: int = MAX_DIRECTORY_ENTRIES
    max_directory_depth: int = MAX_DIRECTORY_DEPTH
    max_directory_entries_per_directory: int = MAX_DIRECTORY_ENTRIES_PER_DIRECTORY
    max_directory_total_bytes: int = MAX_DIRECTORY_TOTAL_BYTES
    max_directory_file_bytes: int = MAX_DIRECTORY_FILE_BYTES
    max_compression_ratio: float = MAX_COMPRESSION_RATIO
    max_input_zip_bytes: int = MAX_INSPECTOR_INPUT_ZIP_BYTES
    max_read_bytes: int = MAX_READ_BYTES
    # Normal safety scans read every eligible file completely, within the
    # package preflight bounds. This opt-in cap exists only for exploratory
    # inspection and necessarily makes safety coverage incomplete.
    max_safety_scan_bytes: Optional[int] = None
    max_resource_documents: int = 200
    max_resource_edges: int = 1000
    max_resource_depth: int = 32
    max_resource_text_bytes: int = 10 * 1024 * 1024

    def as_dict(self) -> Dict[str, Any]:
        return {
            "max_zip_members": self.max_zip_members,
            "max_zip_uncompressed_bytes": self.max_zip_uncompressed_bytes,
            "max_zip_member_bytes": self.max_zip_member_bytes,
            "max_directory_files": self.max_directory_files,
            "max_directory_entries": self.max_directory_entries,
            "max_directory_depth": self.max_directory_depth,
            "max_directory_entries_per_directory": self.max_directory_entries_per_directory,
            "max_directory_total_bytes": self.max_directory_total_bytes,
            "max_directory_file_bytes": self.max_directory_file_bytes,
            "max_compression_ratio": self.max_compression_ratio,
            "max_input_zip_bytes": self.max_input_zip_bytes,
            "max_read_bytes": self.max_read_bytes,
            "max_safety_scan_bytes": self.max_safety_scan_bytes,
            "max_resource_documents": self.max_resource_documents,
            "max_resource_edges": self.max_resource_edges,
            "max_resource_depth": self.max_resource_depth,
            "max_resource_text_bytes": self.max_resource_text_bytes,
            "safety_scans_read_full_eligible_files": self.max_safety_scan_bytes is None,
            # Kept as a backward-compatible JSON key for existing consumers. It is an
            # inspector resource boundary, never a claim about a host upload
            # product limit.
            "skill_upload_limit_bytes": self.max_input_zip_bytes,
            "inspector_input_zip_limit_bytes": self.max_input_zip_bytes,
        }


@dataclass
class DirectoryPreflight:
    """A single bounded snapshot used for every analysis of a folder input."""

    findings: List[Dict[str, Any]]
    entries: List[Path]
    excluded_directories: List[Path]
    total_bytes: int
    # Direct source-tree inputs may intentionally skip VCS/cache directories for
    # performance. Record those omissions explicitly so the result cannot be
    # mistaken for a release-safe complete scan.
    unscanned_paths: List[Path] = field(default_factory=list)
    coverage_complete: bool = False


@dataclass
class SafetyScanResult:
    """Findings plus the files whose eligible safety scans were incomplete."""

    findings: List[Dict[str, Any]] = field(default_factory=list)
    incomplete_paths: List[str] = field(default_factory=list)

    def extend(self, other: "SafetyScanResult") -> None:
        self.findings.extend(other.findings)
        self.incomplete_paths.extend(other.incomplete_paths)


def positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"must be a positive integer: {value}") from exc
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer greater than zero")
    return parsed


def positive_float(value: str) -> float:
    try:
        parsed = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"must be a positive number: {value}") from exc
    if not math.isfinite(parsed) or parsed <= 0:
        raise argparse.ArgumentTypeError("must be a finite positive number greater than zero")
    return parsed


def finding(severity: str, code: str, message: str, file: Optional[str] = None, **extra: Any) -> Dict[str, Any]:
    if code not in FINDING_CODE_SET:
        raise ValueError(f"unregistered inspector finding code: {code}")
    item: Dict[str, Any] = {"severity": severity, "code": code, "message": message}
    if file is not None:
        item["file"] = file
    item.update(extra)
    return item


def is_text_like_file(path: Path) -> bool:
    name = path.name.lower()
    if name in TEXT_FILENAMES or name.startswith(".env."):
        return True
    return path.suffix.lower() in TEXT_EXTENSIONS


def decode_text_bytes(data: bytes) -> str:
    """Decode supported Unicode text encodings without hiding BOM-marked data."""
    encodings = (
        ((b"\xff\xfe\x00\x00", b"\x00\x00\xfe\xff"), "utf-32"),
        ((b"\xff\xfe", b"\xfe\xff"), "utf-16"),
        ((b"\xef\xbb\xbf",), "utf-8-sig"),
    )
    for byte_order_marks, encoding in encodings:
        if data.startswith(byte_order_marks):
            try:
                return data.decode(encoding)
            except UnicodeDecodeError:
                return data.decode(encoding, errors="replace")
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("utf-8", errors="replace")


def safe_read_text(path: Path, max_bytes: Optional[int] = MAX_READ_BYTES, force: bool = False) -> Optional[str]:
    # force=True bypasses the extension allowlist (still bounded, still skips
    # symlinks) so callers can read files whose name or shebang marks them worth
    # scanning even without a known text extension (e.g. id_rsa, an installer).
    if (max_bytes is not None and max_bytes <= 0) or path.is_symlink():
        return None
    if not force and not is_text_like_file(path):
        return None
    try:
        with path.open("rb") as handle:
            data = handle.read() if max_bytes is None else handle.read(max_bytes)
    except OSError:
        return None
    return decode_text_bytes(data)


def sniff_text_content(path: Path, max_bytes: int = TEXT_SNIFF_BYTES) -> Optional[bool]:
    """Return whether an unknown regular file looks like text.

    Extensions are useful hints but are not a trustworthy safety boundary.
    This bounded byte-level sniff lets the secret scanner cover ordinary text
    and config files with unfamiliar names while avoiding obvious binaries.
    ``None`` means the file could not be read, which must fail coverage rather
    than being treated as a safe non-text file.
    """
    if path.is_symlink():
        return None
    try:
        with path.open("rb") as handle:
            data = handle.read(max_bytes)
    except OSError:
        return None
    if not data:
        return True
    if data.startswith((b"\xff\xfe", b"\xfe\xff", b"\xff\xfe\x00\x00", b"\x00\x00\xfe\xff")):
        return True
    if b"\x00" in data:
        return False
    control_bytes = sum(1 for byte in data if byte < 32 and byte not in (9, 10, 13, 12))
    return control_bytes * 20 <= len(data)


def is_secret_scan_candidate(path: Path) -> Optional[bool]:
    """Whether a regular file is eligible for content secret scanning.

    Known text/config names are always eligible. Other names use bounded
    content sniffing. An unreadable unknown file returns ``None`` so callers
    can record incomplete coverage instead of silently excluding it.
    """
    if is_text_like_file(path) or is_common_secret_config_name(path):
        return True
    return sniff_text_content(path)


def is_regular_file(path: Path) -> bool:
    try:
        return not path.is_symlink() and path.is_file()
    except OSError:
        return False


def is_metadata_path(path: Path) -> bool:
    return any(part == "__MACOSX" or part.startswith("._") for part in path.parts)


IGNORED_DIR_NAMES = {".git", "node_modules", ".venv", ".pytest_cache", "__pycache__"}


def is_ignored_dir(path: Path) -> bool:
    """True for a real (non-symlink) directory whose name is a known VCS/junk dir.

    A symlink or file that happens to share one of these names is not ignored:
    it still gets reported (e.g. as a suspicious symlink), just not descended into.
    """
    try:
        return path.name in IGNORED_DIR_NAMES and path.is_dir() and not path.is_symlink()
    except OSError:
        return False


def find_ignored_dirs(root: Path) -> List[str]:
    """Relative paths of VCS/junk directories (e.g. .git, node_modules) that
    traversal skips, at any depth under root. A root-level match returns just its
    name (its relative path); nested matches include their parent path."""
    found: List[str] = []
    stack: List[Path] = [root]
    while stack:
        current = stack.pop()
        try:
            entries = sorted(current.iterdir(), key=lambda item: str(item))
        except OSError:
            continue
        for entry in entries:
            if is_ignored_dir(entry):
                found.append(relative(entry, root))
                continue
            try:
                if not entry.is_symlink() and entry.is_dir() and not is_metadata_path(entry):
                    stack.append(entry)
            except OSError:
                continue
    return sorted(found)


def walk_paths_no_symlinks(root: Path) -> Iterable[Path]:
    try:
        if root.is_symlink():
            yield root
            return
    except OSError:
        return
    stack: List[Path] = [root]
    while stack:
        current = stack.pop()
        try:
            entries = sorted(current.iterdir(), key=lambda item: str(item))
        except OSError:
            continue
        for entry in entries:
            if is_ignored_dir(entry):
                continue
            yield entry
            if is_metadata_path(entry):
                continue
            try:
                if entry.is_symlink():
                    continue
                if entry.is_dir():
                    stack.append(entry)
            except OSError:
                continue


def extract_frontmatter(text: str) -> Tuple[Optional[str], Optional[str]]:
    if not text.startswith("---"):
        return None, "frontmatter must start with ---"
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, "frontmatter opening delimiter is invalid"
    for index in range(1, len(lines)):
        if lines[index].startswith("---") and lines[index].strip() == "---":
            return "\n".join(lines[1:index]) + "\n", None
    return None, "frontmatter closing delimiter is missing"


class YamlParseError(ValueError):
    """A line-aware error from the deliberately small, fail-closed YAML parser."""

    def __init__(self, line_number: int, message: str):
        super().__init__(f"line {line_number}: {message}")


class YamlUnsupportedSyntaxError(YamlParseError):
    """Valid YAML syntax the restricted parser deliberately does not verify."""


def strip_yaml_inline_comment(value: str) -> str:
    """Remove a YAML comment without treating # inside a quoted scalar as one."""
    quote: Optional[str] = None
    index = 0
    while index < len(value):
        char = value[index]
        if quote == '"' and char == "\\":
            index += 2
            continue
        if quote == "'" and char == "'" and index + 1 < len(value) and value[index + 1] == "'":
            index += 2
            continue
        if char in {"'", '"'}:
            if quote is None:
                quote = char
            elif quote == char:
                quote = None
        elif char == "#" and quote is None and (index == 0 or value[index - 1].isspace()):
            return value[:index].rstrip()
        index += 1
    return value.rstrip()


def split_yaml_flow_items(value: str, line_number: int) -> List[str]:
    """Split a flow collection on top-level commas, preserving quoted values."""
    items: List[str] = []
    current: List[str] = []
    quote: Optional[str] = None
    depth = 0
    index = 0
    while index < len(value):
        char = value[index]
        if quote == '"' and char == "\\":
            current.append(char)
            if index + 1 < len(value):
                current.append(value[index + 1])
            index += 2
            continue
        if quote == "'" and char == "'" and index + 1 < len(value) and value[index + 1] == "'":
            current.extend([char, value[index + 1]])
            index += 2
            continue
        if char in {"'", '"'}:
            if quote is None:
                quote = char
            elif quote == char:
                quote = None
        elif quote is None:
            if char in "[{":
                depth += 1
            elif char in "]}":
                if depth == 0:
                    raise YamlParseError(line_number, "flow collection has an unmatched closing delimiter")
                depth -= 1
            elif char == "," and depth == 0:
                item = "".join(current).strip()
                if not item:
                    raise YamlParseError(line_number, "flow collection contains an empty item")
                items.append(item)
                current = []
                index += 1
                continue
        current.append(char)
        index += 1
    if quote is not None:
        raise YamlParseError(line_number, "quoted scalar is not closed")
    if depth != 0:
        raise YamlParseError(line_number, "flow collection is not closed")
    final = "".join(current).strip()
    if not final and items:
        raise YamlParseError(line_number, "flow collection ends with an empty item")
    if final:
        items.append(final)
    return items


def parse_yaml_single_quoted(value: str, line_number: int) -> str:
    result: List[str] = []
    index = 1
    while index < len(value):
        char = value[index]
        if char != "'":
            result.append(char)
            index += 1
            continue
        if index + 1 < len(value) and value[index + 1] == "'":
            result.append("'")
            index += 2
            continue
        trailing = strip_yaml_inline_comment(value[index + 1:]).strip()
        if trailing:
            raise YamlParseError(line_number, "quoted scalar has unexpected trailing content")
        return "".join(result)
    raise YamlParseError(line_number, "quoted scalar is not closed")


def parse_yaml_integer(value: str, line_number: int) -> int:
    digits = value[1:] if value.startswith(("-", "+")) else value
    if len(digits) > MAX_YAML_INTEGER_DIGITS:
        raise YamlParseError(
            line_number,
            f"integer numeric scalar exceeds the {MAX_YAML_INTEGER_DIGITS}-digit verifier limit",
        )
    try:
        return int(value)
    except (OverflowError, ValueError) as exc:
        raise YamlParseError(
            line_number,
            "integer numeric scalar cannot be represented safely",
        ) from exc


def parse_yaml_float(value: str, line_number: int) -> float:
    try:
        parsed = float(value)
    except (OverflowError, ValueError) as exc:
        raise YamlParseError(
            line_number,
            "floating-point numeric scalar cannot be represented safely",
        ) from exc
    if not math.isfinite(parsed):
        raise YamlParseError(
            line_number,
            "floating-point numeric scalar must be finite",
        )
    return parsed


def parse_yaml_mapping_key(raw_key: str, line_number: int) -> str:
    """Keep supported quoted keys as strings; never coerce YAML scalar keys."""
    raw_key = raw_key.strip()
    if raw_key.startswith(("!", "&", "*")):
        raise YamlParseError(line_number, "YAML tags, anchors, and aliases are not supported")
    if raw_key.startswith(("?", "[", "{")):
        raise YamlUnsupportedSyntaxError(line_number, "complex mapping keys are not supported by this parser")
    quoted = raw_key.startswith(("'", '"'))
    key = parse_yaml_scalar(raw_key, line_number) if quoted else raw_key
    if not isinstance(key, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", key):
        raise YamlUnsupportedSyntaxError(line_number, "mapping key syntax is not supported by this parser")
    if not quoted:
        # Decimal forms with leading zeros/underscores and hexadecimal/octal
        # keys must not slip through the intentionally restricted value parser.
        numeric = re.fullmatch(r"(?:[0-9][0-9_]*|0[xX][0-9a-fA-F_]+|0[oO][0-7_]+)", key)
        if numeric or not isinstance(parse_yaml_scalar(key, line_number), str):
            raise YamlParseError(line_number, "mapping keys must be strings; quote numeric, boolean or null keys")
    return key


def parse_yaml_scalar(value: str, line_number: int, depth: int = 0) -> Any:
    if depth > MAX_YAML_NESTING_DEPTH:
        raise YamlUnsupportedSyntaxError(
            line_number,
            f"YAML nesting exceeds the verifier limit of {MAX_YAML_NESTING_DEPTH}",
        )
    value = strip_yaml_inline_comment(value).strip()
    if not value:
        return None
    if value.startswith('"'):
        try:
            parsed, consumed = json.JSONDecoder().raw_decode(value)
        except json.JSONDecodeError as exc:
            raise YamlParseError(line_number, f"invalid double-quoted scalar: {exc.msg}") from exc
        trailing = strip_yaml_inline_comment(value[consumed:]).strip()
        if trailing:
            raise YamlParseError(line_number, "quoted scalar has unexpected trailing content")
        if not isinstance(parsed, str):
            raise YamlParseError(line_number, "double-quoted scalar must decode to a string")
        return parsed
    if value.startswith("'"):
        return parse_yaml_single_quoted(value, line_number)
    if value.startswith("["):
        if not value.endswith("]"):
            raise YamlParseError(line_number, "flow sequence is not closed")
        body = value[1:-1].strip()
        return [] if not body else [
            parse_yaml_scalar(item, line_number, depth + 1)
            for item in split_yaml_flow_items(body, line_number)
        ]
    if value.startswith("{"):
        if not value.endswith("}"):
            raise YamlParseError(line_number, "flow mapping is not closed")
        result: Dict[str, Any] = {}
        body = value[1:-1].strip()
        if not body:
            return result
        for item in split_yaml_flow_items(body, line_number):
            if ":" not in item:
                raise YamlParseError(line_number, "flow mapping item is not a key-value pair")
            key, raw_value = item.split(":", 1)
            key = parse_yaml_mapping_key(key, line_number)
            if raw_value.strip().startswith(("!", "&", "*")):
                raise YamlParseError(line_number, "YAML tags, anchors, and aliases are not supported")
            if key in result:
                raise YamlParseError(line_number, f"duplicate key {key!r}")
            result[key] = parse_yaml_scalar(raw_value, line_number, depth + 1)
        return result
    if value.startswith(("!", "&", "*")):
        raise YamlParseError(line_number, "YAML tags, anchors, and aliases are not supported")
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if lowered in {"null", "~"}:
        return None
    if lowered in {".nan", "+.nan", "-.nan", ".inf", "+.inf", "-.inf"}:
        raise YamlParseError(
            line_number,
            "floating-point numeric scalar must be finite",
        )
    if re.fullmatch(r"[-+]?(?:0|[1-9][0-9]*)", value):
        return parse_yaml_integer(value, line_number)
    if re.fullmatch(r"[-+]?(?:[0-9]+\.[0-9]*|\.[0-9]+)(?:[eE][-+]?[0-9]+)?", value) or re.fullmatch(r"[-+]?[0-9]+[eE][-+]?[0-9]+", value):
        return parse_yaml_float(value, line_number)
    if re.search(r":(?=\s|$)", value):
        raise YamlParseError(line_number, "plain scalar contains a ':' mapping separator; quote the value")
    return value


class RestrictedYamlParser:
    """Parse the safe YAML subset needed by skill manifests without PyYAML.

    It supports mappings, sequences, quoted/plain scalars, flow collections,
    and block scalars. Anything else fails explicitly instead of being guessed
    into a possibly-valid manifest.
    """

    def __init__(self, text: str):
        self.lines = text.splitlines()
        self.ends_with_linebreak = text.endswith(("\n", "\r"))
        self.index = 0

    def ensure_depth(self, depth: int, line_number: int) -> None:
        if depth > MAX_YAML_NESTING_DEPTH:
            raise YamlUnsupportedSyntaxError(
                line_number,
                f"YAML nesting exceeds the verifier limit of {MAX_YAML_NESTING_DEPTH}",
            )

    def line_indent(self, index: int) -> int:
        raw = self.lines[index]
        prefix = raw[:len(raw) - len(raw.lstrip(" \t"))]
        if "\t" in prefix:
            raise YamlParseError(index + 1, "tabs are not allowed for indentation")
        return len(prefix)

    def skip_ignored(self) -> None:
        while self.index < len(self.lines):
            raw = self.lines[self.index]
            if not raw.strip() or raw.lstrip(" ").startswith("#"):
                self.index += 1
                continue
            break

    def next_content_index(self) -> Optional[int]:
        candidate = self.index
        while candidate < len(self.lines):
            raw = self.lines[candidate]
            if not raw.strip() or raw.lstrip(" ").startswith("#"):
                candidate += 1
                continue
            return candidate
        return None

    def parse(self) -> Dict[str, Any]:
        self.skip_ignored()
        if self.index >= len(self.lines):
            raise YamlParseError(1, "document is empty")
        if self.line_indent(self.index) != 0:
            raise YamlParseError(self.index + 1, "top-level mapping must start at column zero")
        return self.parse_mapping(0, depth=1)

    def parse_mapping_entry(self, content: str, line_number: int) -> Tuple[str, Optional[str]]:
        if content.startswith("? "):
            raise YamlUnsupportedSyntaxError(line_number, "complex mapping keys are not supported by this parser")
        if ":" not in content:
            raise YamlParseError(line_number, "mapping entry is missing ':'")
        key, raw_value = content.split(":", 1)
        key = parse_yaml_mapping_key(key, line_number)
        value = strip_yaml_inline_comment(raw_value).strip()
        if value.startswith(("!", "&", "*")):
            raise YamlParseError(line_number, "YAML tags, anchors, and aliases are not supported")
        if raw_value and not (raw_value[0].isspace() or raw_value[0] == "#"):
            raise YamlParseError(line_number, "a mapping ':' must be followed by whitespace or a comment")
        return key, value or None

    def assign_mapping_value(
        self,
        result: Dict[str, Any],
        key: str,
        raw_value: Optional[str],
        parent_indent: int,
        depth: int,
    ) -> None:
        if raw_value in {"|", "|-", "|+", ">", ">-", ">+"}:
            result[key] = self.parse_block_scalar(parent_indent, raw_value)
        elif raw_value is None:
            result[key] = self.parse_child_or_null(parent_indent, depth + 1)
        else:
            result[key] = parse_yaml_scalar(raw_value, self.index, depth)

    def parse_mapping(
        self,
        indent: int,
        result: Optional[Dict[str, Any]] = None,
        depth: int = 1,
    ) -> Dict[str, Any]:
        self.ensure_depth(depth, self.index + 1)
        result = {} if result is None else result
        while True:
            self.skip_ignored()
            if self.index >= len(self.lines):
                return result
            current_indent = self.line_indent(self.index)
            if current_indent < indent:
                return result
            if current_indent > indent:
                raise YamlParseError(self.index + 1, "unexpected indentation without a parent key")
            content = self.lines[self.index][current_indent:]
            if content == "-" or content.startswith("- "):
                raise YamlParseError(self.index + 1, "sequence item found where a mapping key was expected")
            key, raw_value = self.parse_mapping_entry(content, self.index + 1)
            if key in result:
                raise YamlParseError(self.index + 1, f"duplicate key {key!r}")
            self.index += 1
            self.assign_mapping_value(result, key, raw_value, indent, depth)

    def parse_inline_sequence_mapping(
        self, raw_value: str, sequence_indent: int, line_number: int, depth: int
    ) -> Dict[str, Any]:
        """Parse ``- key: value`` plus mapping entries nested under that item."""
        self.ensure_depth(depth, line_number)
        key, mapping_value = self.parse_mapping_entry(raw_value, line_number)
        result: Dict[str, Any] = {}
        mapping_indent = sequence_indent + 2
        self.assign_mapping_value(result, key, mapping_value, mapping_indent, depth)
        return self.parse_mapping(mapping_indent, result, depth)

    def parse_sequence(self, indent: int, depth: int) -> List[Any]:
        self.ensure_depth(depth, self.index + 1)
        result: List[Any] = []
        while True:
            self.skip_ignored()
            if self.index >= len(self.lines):
                return result
            current_indent = self.line_indent(self.index)
            if current_indent < indent:
                return result
            if current_indent > indent:
                raise YamlParseError(self.index + 1, "unexpected indentation in sequence")
            content = self.lines[self.index][current_indent:]
            if content != "-" and not content.startswith("- "):
                raise YamlParseError(self.index + 1, "mapping key found where a sequence item was expected")
            raw_value = strip_yaml_inline_comment(content[1:]).strip()
            self.index += 1
            if raw_value in {"|", "|-", "|+", ">", ">-", ">+"}:
                result.append(self.parse_block_scalar(indent, raw_value))
            elif raw_value:
                if re.search(r":(?=\s|$)", raw_value) and not raw_value.startswith(("'", '"', "[", "{")):
                    result.append(self.parse_inline_sequence_mapping(raw_value, indent, self.index, depth + 1))
                else:
                    result.append(parse_yaml_scalar(raw_value, self.index, depth + 1))
            else:
                result.append(self.parse_child_or_null(indent, depth + 1))

    def parse_child_or_null(self, parent_indent: int, depth: int) -> Any:
        self.ensure_depth(depth, self.index + 1)
        next_index = self.next_content_index()
        if next_index is None or self.line_indent(next_index) <= parent_indent:
            return None
        self.skip_ignored()
        child_indent = self.line_indent(self.index)
        content = self.lines[self.index][child_indent:]
        if content == "-" or content.startswith("- "):
            return self.parse_sequence(child_indent, depth)
        return self.parse_mapping(child_indent, depth=depth)

    def parse_block_scalar(self, parent_indent: int, indicator: str) -> str:
        block: List[str] = []
        while self.index < len(self.lines):
            raw = self.lines[self.index]
            if raw.strip() and self.line_indent(self.index) <= parent_indent:
                break
            block.append(raw)
            self.index += 1
        non_blank = [raw for raw in block if raw.strip()]
        common_indent = min((len(raw) - len(raw.lstrip(" ")) for raw in non_blank), default=0)
        lines = [raw[common_indent:] if raw.strip() else "" for raw in block]
        terminal_break = bool(block) and (self.index < len(self.lines) or self.ends_with_linebreak)
        if indicator.startswith("|"):
            value = "\n".join(lines) + ("\n" if terminal_break else "")
        else:
            # Fold only adjacent ordinary text lines. Blank paragraphs and
            # more-indented lines preserve their YAML-defined line breaks.
            positions = [i for i, line in enumerate(lines) if line]
            if not positions:
                value = "\n" * (max(0, len(lines)-1) + int(terminal_break))
            else:
                value = "\n" * positions[0] + lines[positions[0]]
                for previous, current in zip(positions, positions[1:]):
                    blanks = current - previous - 1
                    indented = lines[previous].startswith((" ", "\t")) or lines[current].startswith((" ", "\t"))
                    separator = "\n"*(blanks+1) if indented else "\n"*blanks if blanks else " "
                    value += separator + lines[current]
                value += "\n" * (len(lines)-positions[-1]-1 + int(terminal_break))
        if indicator.endswith("+"):
            return value
        stripped = value.rstrip("\n")
        if indicator.endswith("-") or not non_blank:
            return stripped
        return stripped + ("\n" if value.endswith("\n") else "")


def parse_yaml_mapping(text: str) -> Dict[str, Any]:
    try:
        return RestrictedYamlParser(text).parse()
    except RecursionError as exc:
        # Defensive fallback: all supported recursion paths are depth-bounded,
        # but never let an untrusted manifest escape as a Python traceback.
        raise YamlUnsupportedSyntaxError(
            1,
            f"YAML nesting exceeds the verifier limit of {MAX_YAML_NESTING_DEPTH}",
        ) from exc


def parse_frontmatter(frontmatter_text: str) -> Dict[str, Any]:
    try:
        return parse_yaml_mapping(frontmatter_text)
    except YamlUnsupportedSyntaxError as exc:
        return {"_parse_unsupported": str(exc)}
    except YamlParseError as exc:
        return {"_parse_error": str(exc)}


def validate_frontmatter(frontmatter: Dict[str, Any], target: str = "portable") -> List[Dict[str, Any]]:
    """Validate a manifest using the selected structured target profile."""
    profile = target_profile(target)
    findings: List[Dict[str, Any]] = []
    parser_keys = {key for key in frontmatter if key.startswith("_parse_")}
    if frontmatter.get("_parse_unsupported"):
        return [finding(
            "warning",
            "frontmatter_yaml_unsupported",
            f"frontmatter uses valid YAML syntax this restricted parser cannot verify: {frontmatter['_parse_unsupported']}",
        )]
    if frontmatter.get("_parse_error"):
        findings.append(finding("error", "frontmatter_parse_error", str(frontmatter["_parse_error"])))
    unexpected = sorted(set(frontmatter) - set(profile.recognized_frontmatter_keys) - parser_keys)
    if unexpected:
        findings.append(finding(
            profile.unknown_key_severity,
            profile.unknown_key_code,
            f"frontmatter contains keys not recognized by the {profile.name} target profile",
            key_count=len(unexpected),
        ))
    optional = sorted(set(frontmatter) & OPTIONAL_PLATFORM_FRONTMATTER_KEYS)
    if profile.name == "portable" and optional:
        findings.append(finding("info", "frontmatter_platform_optional_keys", "frontmatter contains optional platform-specific Agent Skills keys; validate against the target platform", keys=optional))

    name = frontmatter.get("name")
    description = frontmatter.get("description")
    has_name = isinstance(name, str) and bool(name.strip())
    has_description = isinstance(description, str) and bool(description.strip())
    if profile.name_required and not has_name:
        findings.append(finding("error", "frontmatter_name_missing", "frontmatter name is missing or not a string"))
    elif name is not None and not has_name:
        findings.append(finding("error", "frontmatter_name_invalid", "frontmatter name must be a non-empty string when present"))
    elif has_name:
        clean_name = name.strip()
        if profile.name_limit is not None and len(clean_name) > profile.name_limit:
            findings.append(finding(
                "error",
                "frontmatter_name_too_long",
                f"frontmatter name exceeds the {profile.name_limit}-character limit for the {profile.name} target profile",
                length=len(clean_name),
                limit=profile.name_limit,
            ))
        if profile.hyphen_case_name and re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", clean_name) is None:
            findings.append(finding("error", "frontmatter_invalid_name", f"frontmatter name must be lowercase hyphen-case for the {profile.name} target profile"))
    if profile.description_required and not has_description:
        findings.append(finding("error", "frontmatter_description_missing", "frontmatter description is missing or not a string"))
    elif description is not None and not has_description:
        findings.append(finding("error", "frontmatter_description_invalid", "frontmatter description must be a non-empty string when present"))
    elif has_description:
        desc = description.strip()
        if len(description) > AGENT_SKILL_DESCRIPTION_LIMIT:
            findings.append(finding("error", "frontmatter_description_too_long",
                                    "frontmatter description exceeds the Agent Skills 1024-character limit",
                                    length=len(description), limit=AGENT_SKILL_DESCRIPTION_LIMIT))
        if re.search(r"</?[A-Za-z][^>]*>", desc):
            findings.append(finding("error", "frontmatter_description_angle_brackets", "frontmatter description should not contain XML/HTML tags"))
        # Short length and English keywords cannot establish semantic trigger quality.
        # Keep objective validity checks here; qualitative evidence belongs in review.
    if "compatibility" in frontmatter:
        compatibility = frontmatter["compatibility"]
        if not isinstance(compatibility, str) or not compatibility.strip():
            findings.append(finding("error", "frontmatter_compatibility_invalid", "compatibility must be a non-empty string"))
        elif len(compatibility) > AGENT_SKILL_COMPATIBILITY_LIMIT:
            findings.append(finding("error", "frontmatter_compatibility_too_long",
                                    "compatibility exceeds the Agent Skills 500-character limit",
                                    length=len(compatibility), limit=AGENT_SKILL_COMPATIBILITY_LIMIT))
    if "metadata" in frontmatter:
        metadata = frontmatter["metadata"]
        if not isinstance(metadata, dict) or any(not isinstance(k, str) or not isinstance(v, str) for k, v in metadata.items()):
            findings.append(finding("error", "frontmatter_metadata_invalid", "metadata must map strings to strings"))
    return findings


def frontmatter_value_type(value: Any) -> str:
    """Return a stable type label without serializing package-controlled data."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, str):
        return "string"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, list):
        return "sequence"
    if isinstance(value, dict):
        return "mapping"
    return "unsupported"


def validated_frontmatter_name(frontmatter: Dict[str, Any], target: str) -> Optional[str]:
    """Return a name that satisfies the selected target's shape and length."""
    profile = target_profile(target)
    name = frontmatter.get("name")
    if not isinstance(name, str):
        return None
    clean_name = name.strip()
    within_limit = profile.name_limit is None or len(clean_name) <= profile.name_limit
    valid_shape = not profile.hyphen_case_name or re.fullmatch(
        r"[a-z0-9]+(?:-[a-z0-9]+)*", clean_name
    ) is not None
    return clean_name if clean_name and within_limit and valid_shape else None


def contains_sensitive_public_value(value: str) -> bool:
    """Suppress high-confidence secret or PII shapes from public summaries."""
    return any(pattern.search(value) for _, _, _, pattern in SECRET_CONTENT_PATTERNS) or any(
        pattern.search(value) for pattern in HIGH_CONFIDENCE_PII_PATTERNS
    )


@dataclass
class RedactionContext:
    """Private, audit-local substitutions; never serialize this context."""

    substitutions: Dict[str, str] = field(default_factory=dict, repr=False)
    reserved: Set[str] = field(default_factory=set, repr=False)
    next_id: int = 1

    def public_string(self, value: str) -> str:
        if not contains_sensitive_public_value(value):
            return value
        if value not in self.substitutions:
            while True:
                opaque = f"[redacted-{self.next_id:04d}]"
                self.next_id += 1
                if opaque not in self.reserved:
                    break
            self.reserved.add(opaque)
            self.substitutions[value] = opaque
        return self.substitutions[value]


def sanitize_public_output(data: dict, context: RedactionContext) -> dict:
    """Copy presentation data, redacting sensitive strings in values AND keys.

    Reserve existing strings before assigning IDs so an untrusted literal
    resembling an ID cannot overwrite a redacted dictionary key. Preserve
    aliases so the finding deduplication contract survives the copy.
    """
    pending: List[Any] = [data]
    visited: Set[int] = set()
    while pending:
        item = pending.pop()
        if isinstance(item, str):
            context.reserved.add(item)
        elif isinstance(item, (dict, list, tuple)) and id(item) not in visited:
            visited.add(id(item))
            if isinstance(item, dict):
                pending.extend(item.keys())
                pending.extend(item.values())
            else:
                pending.extend(item)
    copies: Dict[int, Any] = {}

    def copy_public(item: Any) -> Any:
        if isinstance(item, str):
            return context.public_string(item)
        if isinstance(item, (dict, list, tuple)):
            if id(item) in copies:
                return copies[id(item)]
            if isinstance(item, dict):
                copied: Any = {}
                copies[id(item)] = copied
                for key, value in item.items():
                    copied[copy_public(key)] = copy_public(value)
            else:
                copied = []
                copies[id(item)] = copied
                copied.extend(copy_public(value) for value in item)
            return copied
        return item

    return copy_public(data)


class PublicArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        # argparse includes rejected user values in its early stderr errors.
        safe = sanitize_public_output({"message": message}, RedactionContext())
        super().error(safe["message"])


def public_frontmatter_summary(frontmatter: Dict[str, Any], target: str) -> Dict[str, Any]:
    """Summarize parsed frontmatter without re-emitting untrusted values.

    The parser and validators retain the complete mapping internally. JSON and
    markdown consumers receive only bounded structural evidence plus a name
    that has already satisfied the selected target's portable name contract.
    Unknown key names and values are represented only by a count.
    """
    profile = target_profile(target)
    parser_keys = {key for key in frontmatter if key.startswith("_parse_")}
    recognized_keys = sorted(
        key for key in frontmatter
        if key in profile.recognized_frontmatter_keys
    )
    unknown_key_count = len(
        set(frontmatter) - set(profile.recognized_frontmatter_keys) - parser_keys
    )
    validated_name = validated_frontmatter_name(frontmatter, target)
    if validated_name is not None and contains_sensitive_public_value(validated_name):
        validated_name = None
    description = frontmatter.get("description")
    description_length = len(description.strip()) if isinstance(description, str) else None
    return {
        "redacted": True,
        "validated_name": validated_name,
        "present_keys": recognized_keys,
        "value_types": {
            key: frontmatter_value_type(frontmatter[key])
            for key in recognized_keys
        },
        "unrecognized_key_count": unknown_key_count,
        "description_length": description_length,
    }


def normalize_zip_name(name: str) -> Tuple[Optional[str], Optional[str]]:
    """Backward-compatible single-member view of the shared path policy."""
    member, issue = normalize_member_path(name)
    return member.normalized_path, issue.message if issue is not None else None


def zip_info_is_symlink(info: zipfile.ZipInfo) -> bool:
    return stat.S_ISLNK(info.external_attr >> 16)


def zip_info_unsupported_type(info: zipfile.ZipInfo) -> bool:
    """Whether an archive member is neither a normal file nor a directory.

    ZIP stores POSIX file types in the high external-attribute bits when a
    producer supplies them.  Treat devices, fifos, and sockets as unsafe just
    as direct-folder inspection does; a Skill package never needs them.
    """
    file_type = stat.S_IFMT(info.external_attr >> 16)
    if file_type in {0, stat.S_IFREG}:
        return False
    return file_type != stat.S_IFDIR or not info.is_dir()


def zip_directory_payload_metadata(info: zipfile.ZipInfo) -> bool:
    """Whether a directory entry declares non-empty uncompressed content.

    A valid deflated empty stream may have a nonzero ``compress_size``, so that
    field is deliberately not used as a rejection signal.
    """
    return info.is_dir() and (info.file_size != 0 or info.CRC != 0)


def zip_directory_stream_is_empty(
    archive: zipfile.ZipFile,
    info: zipfile.ZipInfo,
) -> bool:
    """Verify a directory stream is empty with a one-byte bounded read."""
    if not info.is_dir():
        return True
    with archive.open(info, "r") as source:
        return source.read(1) == b""


def zip_member_safety_error(info: zipfile.ZipInfo, limits: InspectionLimits) -> Optional[str]:
    """Return a concise extraction-time error for an unsafe member, if any.

    Archive preflight reports structured findings before extraction.  Repeat
    essential checks here so a changed archive cannot bypass the preflight in
    the gap between validation and extraction.
    """
    member, path_issue = normalize_member_path(info.filename, info.is_dir())
    if path_issue or member.normalized_path is None:
        assert path_issue is not None
        return f"{path_issue.code}: {path_issue.message}: {info.filename}"
    if info.flag_bits & 0x1:
        return f"zip contains encrypted member: {info.filename}"
    if zip_info_is_symlink(info):
        return f"zip contains symlink member: {info.filename}"
    if zip_info_unsupported_type(info):
        return f"zip contains unsupported special member: {info.filename}"
    if zip_directory_payload_metadata(info):
        return f"zip_directory_member_has_payload: directory member is not empty: {info.filename}"
    if info.file_size > limits.max_zip_member_bytes:
        return f"zip member exceeds size limit: {info.filename}"
    return None


def validate_zip_archive(zip_path: Path, limits: InspectionLimits, profile: TargetProfile) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    # Gate on the on-disk archive size BEFORE opening. zipfile parses the whole
    # central directory into memory at open() time, so a small-but-crafted
    # archive with hundreds of thousands of members can drive memory up before
    # any per-member limit fires. Capping the input size bounds the member count.
    try:
        zip_bytes = zip_path.stat().st_size
    except OSError as exc:
        return [finding("error", "zip_read_error", f"could not read zip archive: {exc}")]
    if profile.product_upload_limit_bytes is not None and zip_bytes > profile.product_upload_limit_bytes:
        findings.append(finding(
            "error",
            "target_upload_limit_exceeded",
            f"zip exceeds the documented {profile.name} upload limit",
            bytes=zip_bytes,
            limit=profile.product_upload_limit_bytes,
            target=profile.name,
            limit_kind="documented_product",
        ))
    if zip_bytes > limits.max_input_zip_bytes:
        findings.append(finding(
            "error",
            "package_zip_too_large",
            "zip exceeds Skill Forge's generic inspector input safety limit; this is not a host upload-limit claim",
            bytes=zip_bytes,
            limit=limits.max_input_zip_bytes,
            limit_kind="inspector_safety",
        ))
        return findings
    try:
        with zipfile.ZipFile(zip_path, "r") as archive:
            infos = archive.infolist()
            if len(infos) > limits.max_zip_members:
                findings.append(finding("error", "zip_too_many_members", f"zip has too many members: {len(infos)}", limit=limits.max_zip_members))
            members, path_issues = validate_portable_zip_members(
                (info.filename, info.is_dir()) for info in infos
            )
            for issue in path_issues:
                extra: Dict[str, Any] = {}
                for field_name in (
                    "normalized_path",
                    "conflicts_with",
                    "identity_kind",
                    "path_rule",
                    "component",
                    "utf8_bytes",
                    "utf16_units",
                    "limit",
                ):
                    value = getattr(issue, field_name)
                    if value is not None:
                        extra[field_name] = value
                findings.append(finding(
                    "error", issue.code, issue.message, file=issue.raw_name, **extra
                ))
            total_uncompressed = 0
            for info, member in zip(infos, members):
                raw = info.filename
                if member.normalized_path is None:
                    continue
                if info.flag_bits & 0x1:
                    findings.append(finding("error", "zip_encrypted_member", "zip contains encrypted member", file=raw))
                if zip_info_is_symlink(info):
                    findings.append(finding("error", "zip_symlink_member", "zip contains symlink member", file=raw))
                elif zip_info_unsupported_type(info):
                    findings.append(finding("error", "zip_unsupported_member_type", "zip contains a special member type that cannot be extracted safely", file=raw))
                directory_payload = zip_directory_payload_metadata(info)
                if (
                    info.is_dir()
                    and not directory_payload
                    and not (info.flag_bits & 0x1)
                    and not zip_info_is_symlink(info)
                    and not zip_info_unsupported_type(info)
                ):
                    try:
                        directory_payload = not zip_directory_stream_is_empty(archive, info)
                    except Exception:
                        # Archive-controlled compression/decompression failures
                        # are evidence that the directory cannot be proven empty.
                        directory_payload = True
                if directory_payload:
                    findings.append(finding(
                        "error",
                        "zip_directory_member_has_payload",
                        "zip directory member must have an empty uncompressed stream",
                        file=raw,
                        bytes=info.file_size,
                        compressed_bytes=info.compress_size,
                        crc32=f"{info.CRC:08x}",
                    ))
                if info.file_size > limits.max_zip_member_bytes:
                    findings.append(finding("error", "zip_member_too_large", "zip member exceeds size limit", file=raw, bytes=info.file_size, limit=limits.max_zip_member_bytes))
                total_uncompressed += info.file_size
                if total_uncompressed > limits.max_zip_uncompressed_bytes:
                    findings.append(finding("error", "zip_uncompressed_size_too_large", "zip uncompressed size exceeds limit", bytes=total_uncompressed, limit=limits.max_zip_uncompressed_bytes))
                    break
                if info.file_size > 0:
                    if info.compress_size == 0:
                        findings.append(finding("error", "zip_zero_compressed_size", "zip member has suspicious zero compressed size", file=raw, bytes=info.file_size))
                    else:
                        ratio = float(info.file_size) / float(info.compress_size)
                        if ratio > limits.max_compression_ratio:
                            findings.append(finding("error", "zip_high_compression_ratio", "zip member compression ratio is suspiciously high", file=raw, ratio=round(ratio, 2), limit=limits.max_compression_ratio))
    except zipfile.BadZipFile:
        findings.append(finding("error", "zip_bad_archive", "input is not a valid zip archive"))
    except OSError as exc:
        findings.append(finding("error", "zip_read_error", f"could not read zip archive: {exc}"))
    return findings


def safe_extract_zip(zip_path: Path, destination: Path, limits: InspectionLimits) -> None:
    """Extract a preflighted ZIP without trusting metadata-only byte counts.

    ``ZipInfo.file_size`` is useful for preflight but remains archive-supplied
    metadata.  Count bytes while copying as a second limit boundary, and stage
    each member in a temporary sibling so a rejected stream never leaves a
    partial final file behind.
    """
    with zipfile.ZipFile(zip_path, "r") as archive:
        infos = archive.infolist()
        if len(infos) > limits.max_zip_members:
            raise ValueError("zip has too many members during extraction")
        members, path_issues = validate_portable_zip_members(
            (info.filename, info.is_dir()) for info in infos
        )
        if path_issues:
            issue = path_issues[0]
            raise ValueError(f"{issue.code}: {issue.message}: {issue.raw_name}")
        for info in infos:
            safety_error = zip_member_safety_error(info, limits)
            if safety_error:
                raise ValueError(safety_error)
        for info in infos:
            if not info.is_dir():
                continue
            try:
                stream_is_empty = zip_directory_stream_is_empty(archive, info)
            except Exception as exc:
                # Convert every archive-controlled stream failure into the
                # same fail-closed extraction boundary without exposing a
                # target-specific traceback.
                raise ValueError(
                    "zip_directory_member_has_payload: could not verify empty directory stream: "
                    f"{info.filename}"
                ) from exc
            if not stream_is_empty:
                raise ValueError(
                    "zip_directory_member_has_payload: directory member stream is not empty: "
                    f"{info.filename}"
                )

        created_files: List[Path] = []
        created_directories: List[Path] = []
        staged_target: Optional[Path] = None

        def ensure_directory(directory: Path) -> None:
            try:
                relative_parts = directory.relative_to(destination).parts
            except ValueError as exc:
                raise ValueError(f"zip member escapes destination: {directory}") from exc
            current = destination
            if not current.exists() and not current.is_symlink():
                current.mkdir(parents=True)
                created_directories.append(current)
            elif current.is_symlink() or not current.is_dir():
                raise ValueError(f"extraction destination is not a real directory: {current}")
            for part in relative_parts:
                current = current / part
                if current.exists() or current.is_symlink():
                    if current.is_symlink() or not current.is_dir():
                        raise ValueError(f"zip member conflicts with existing non-directory path: {current}")
                else:
                    current.mkdir()
                    created_directories.append(current)

        extracted_total = 0
        try:
            for info, member in zip(infos, members):
                assert member.normalized_path is not None
                target = destination.joinpath(*member.normalized_path.split("/"))
                if info.is_dir():
                    ensure_directory(target)
                    continue
                ensure_directory(target.parent)
                if target.exists() or target.is_symlink():
                    raise ValueError(f"extraction would overwrite an existing destination: {info.filename}")
                with tempfile.NamedTemporaryFile(dir=target.parent, prefix=".skill-inspect-", delete=False) as sink:
                    staged_target = Path(sink.name)
                    extracted_member = 0
                    with archive.open(info, "r") as source:
                        while True:
                            chunk = source.read(ZIP_STREAM_CHUNK_BYTES)
                            if not chunk:
                                break
                            extracted_member += len(chunk)
                            extracted_total += len(chunk)
                            if extracted_member > limits.max_zip_member_bytes:
                                raise ValueError(f"zip member exceeded size limit while extracting: {info.filename}")
                            if extracted_total > limits.max_zip_uncompressed_bytes:
                                raise ValueError("zip exceeded total uncompressed size limit while extracting")
                            sink.write(chunk)
                # os.link has create-only semantics: unlike replace()/rename(),
                # it fails if a destination appeared after our existence check.
                os.link(staged_target, target)
                staged_target.unlink()
                staged_target = None
                created_files.append(target)
        except Exception:
            if staged_target is not None:
                try:
                    staged_target.unlink(missing_ok=True)
                except OSError:
                    pass
            for path in reversed(created_files):
                try:
                    path.unlink(missing_ok=True)
                except OSError:
                    pass
            for path in reversed(created_directories):
                try:
                    path.rmdir()
                except OSError:
                    pass
            raise


def validate_directory_tree(
    root: Path,
    limits: InspectionLimits,
    profile: TargetProfile,
    *,
    scan_ignored_directories: bool = False,
) -> DirectoryPreflight:
    """Inspect a direct folder once, with explicit traversal budgets.

    The returned entry snapshot lets downstream analyzers avoid re-walking an
    input after a safety failure. Enumeration errors are errors, not warnings:
    a partial scan must never look like a successful strict inspection.
    """
    findings: List[Dict[str, Any]] = []
    entries: List[Path] = []
    excluded_directories: List[Path] = []
    unscanned_paths: List[Path] = []
    try:
        if root.is_symlink():
            return DirectoryPreflight(
                [finding("error", "directory_root_symlink", "directory input root is a symlink; inspect the real folder path or a clean zip instead", file=str(root))],
                entries,
                excluded_directories,
                0,
            )
    except OSError as exc:
        return DirectoryPreflight(
            [finding("error", "directory_root_lstat_failed", f"could not inspect directory root: {exc}")],
            entries,
            excluded_directories,
            0,
        )
    if not root.exists() or not root.is_dir():
        return DirectoryPreflight(findings, entries, excluded_directories, 0)
    try:
        root_resolved = root.resolve()
    except OSError as exc:
        return DirectoryPreflight(
            [finding("error", "directory_root_resolve_failed", f"could not resolve directory root: {exc}")],
            entries,
            excluded_directories,
            0,
        )
    file_count = 0
    total_bytes = 0
    entry_count = 0
    portable_records: List[Tuple[str, bool]] = []
    stack: List[Tuple[Path, int]] = [(root, 0)]

    while stack:
        current, depth = stack.pop()
        try:
            with os.scandir(current) as scan:
                current_entries: List[os.DirEntry[str]] = []
                for item in scan:
                    if len(current_entries) >= limits.max_directory_entries_per_directory:
                        findings.append(finding(
                            "error",
                            "directory_too_many_entries_in_directory",
                            "directory contains too many entries to inspect safely",
                            file=relative(current, root),
                            limit=limits.max_directory_entries_per_directory,
                        ))
                        return DirectoryPreflight(findings, entries, excluded_directories, total_bytes)
                    current_entries.append(item)
        except OSError as exc:
            findings.append(finding(
                "error",
                "directory_scan_incomplete",
                f"could not enumerate directory; inspection is incomplete: {exc}",
                file=relative(current, root),
            ))
            return DirectoryPreflight(findings, entries, excluded_directories, total_bytes)

        for item in sorted(current_entries, key=lambda entry: entry.name):
            path = Path(item.path)
            rel = relative(path, root)
            entry_count += 1
            if entry_count > limits.max_directory_entries:
                findings.append(finding(
                    "error",
                    "directory_too_many_entries",
                    "directory contains too many entries to inspect safely",
                    limit=limits.max_directory_entries,
                ))
                return DirectoryPreflight(findings, entries, excluded_directories, total_bytes)
            try:
                if item.is_symlink():
                    findings.append(finding("error", "directory_symlink_found", "directory input contains a symlink; inspect a clean zip or remove the symlink before auditing", file=rel))
                    continue
                is_directory = item.is_dir(follow_symlinks=False)
                is_file = item.is_file(follow_symlinks=False)
            except OSError as exc:
                findings.append(finding(
                    "error",
                    "directory_scan_incomplete",
                    f"could not inspect directory entry; inspection is incomplete: {exc}",
                    file=rel,
                ))
                return DirectoryPreflight(findings, entries, excluded_directories, total_bytes)

            if is_directory or is_file:
                portable_records.append((rel, is_directory))
            if is_directory and path.name in IGNORED_DIR_NAMES and not scan_ignored_directories:
                excluded_directories.append(path)
                unscanned_paths.append(path)
                continue
            if not is_directory and not is_file:
                findings.append(finding(
                    "error",
                    "directory_unsupported_entry",
                    "directory contains a non-file, non-directory entry that cannot be inspected safely",
                    file=rel,
                ))
                continue

            entries.append(path)
            if is_directory:
                next_depth = depth + 1
                if next_depth > limits.max_directory_depth:
                    findings.append(finding(
                        "error",
                        "directory_depth_exceeded",
                        "directory nesting exceeds the inspection depth limit",
                        file=rel,
                        limit=limits.max_directory_depth,
                    ))
                    return DirectoryPreflight(findings, entries, excluded_directories, total_bytes)
                stack.append((path, next_depth))
                continue

            try:
                resolved = path.resolve()
                if resolved != root_resolved and root_resolved not in resolved.parents:
                    findings.append(finding("error", "directory_file_outside_root", "directory file resolves outside the inspected root", file=rel))
                    continue
                file_count += 1
                if file_count > limits.max_directory_files:
                    findings.append(finding("error", "directory_too_many_files", "directory contains too many files to inspect safely", limit=limits.max_directory_files))
                    return DirectoryPreflight(findings, entries, excluded_directories, total_bytes)
                size = item.stat(follow_symlinks=False).st_size
                total_bytes += size
                if size > limits.max_directory_file_bytes:
                    findings.append(finding("error", "directory_file_too_large", "directory file exceeds size limit", file=rel, bytes=size, limit=limits.max_directory_file_bytes))
                if total_bytes > limits.max_directory_total_bytes:
                    findings.append(finding("error", "directory_total_size_too_large", "directory total size exceeds inspection limit", bytes=total_bytes, limit=limits.max_directory_total_bytes))
                    return DirectoryPreflight(findings, entries, excluded_directories, total_bytes)
            except OSError as exc:
                findings.append(finding(
                    "error",
                    "directory_scan_incomplete",
                    f"could not inspect file metadata; inspection is incomplete: {exc}",
                    file=rel,
                ))
                return DirectoryPreflight(findings, entries, excluded_directories, total_bytes)
    _portable_entries, portable_issues = validate_portable_path_records(portable_records)
    portability_severity = "error"
    for issue in portable_issues:
        if issue.path_rule == "portable_identity_collision":
            code = "directory_portable_identity_collision"
        elif issue.path_rule == "file_directory_prefix_conflict":
            code = "directory_file_directory_prefix_conflict"
        else:
            code = "directory_nonportable_path"
        evidence: Dict[str, Any] = {"path_rule": issue.path_rule or "unknown"}
        for field_name in (
            "normalized_path",
            "conflicts_with",
            "identity_kind",
            "component",
            "utf8_bytes",
            "utf16_units",
            "limit",
        ):
            value = getattr(issue, field_name)
            if value is not None:
                evidence[field_name] = value
        findings.append(finding(
            portability_severity,
            code,
            "directory entry is not portable across supported extraction filesystems"
            if code == "directory_nonportable_path"
            else issue.message.replace("zip ", "directory ", 1),
            file=issue.raw_name,
            **evidence,
        ))

    return DirectoryPreflight(
        findings,
        entries,
        excluded_directories,
        total_bytes,
        unscanned_paths=unscanned_paths,
        coverage_complete=not unscanned_paths,
    )


def unpack_if_needed(input_path: Path, limits: InspectionLimits, profile: TargetProfile) -> Tuple[Path, Optional[tempfile.TemporaryDirectory[str]], Optional[str], List[Dict[str, Any]]]:
    if input_path.is_dir() or input_path.is_symlink():
        return input_path, None, None, []
    if input_path.is_file() and input_path.suffix.lower() == ".zip":
        zip_findings = validate_zip_archive(input_path, limits, profile)
        if any(item.get("severity") == "error" for item in zip_findings):
            return input_path.resolve(), None, "zip preflight failed", zip_findings
        temp_dir = tempfile.TemporaryDirectory(prefix="skill_inspect_")
        try:
            safe_extract_zip(input_path, Path(temp_dir.name), limits)
            return Path(temp_dir.name).resolve(), temp_dir, None, zip_findings
        except Exception as exc:
            temp_dir.cleanup()
            return input_path.resolve(), None, f"zip extraction failed: {exc}", zip_findings
    return input_path.resolve(), None, "input is neither a folder nor a .zip archive", []


def is_probably_skill_root(path: Path, entries: Optional[List[Path]] = None) -> Path:
    root_skill = path / "SKILL.md"
    if root_skill.exists() and is_regular_file(root_skill):
        return path
    candidates = entries if entries is not None else list(walk_paths_no_symlinks(path))
    skill_files = [
        candidate for candidate in candidates
        if candidate.name == "SKILL.md" and is_regular_file(candidate) and not is_metadata_path(candidate)
    ]
    if len(skill_files) == 1:
        return skill_files[0].parent
    if entries is None:
        try:
            children = [child for child in path.iterdir() if child.is_dir() and not child.is_symlink() and not is_metadata_path(child)]
        except OSError:
            return path
    else:
        children = [child for child in entries if child.parent == path and child.is_dir() and not is_metadata_path(child)]
    if len(children) == 1 and is_regular_file(children[0] / "SKILL.md"):
        return children[0]
    return path


def entries_within_root(entries: List[Path], root: Path) -> List[Path]:
    return [path for path in entries if root in path.parents]


def excluded_directories_within_root(excluded: List[Path], root: Path) -> List[str]:
    return sorted(relative(path, root) for path in excluded if root in path.parents)


def unscanned_paths_relative(unscanned: List[Path], base_path: Path) -> List[str]:
    """Return bounded, stable evidence for direct-tree scan omissions."""
    return sorted({relative(path, base_path) for path in unscanned})


def relative(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root)).replace(os.sep, "/")
    except ValueError:
        return str(path)


def build_tree(entries: List[Path], root: Path, limit: int) -> List[str]:
    files: List[str] = []
    for path in entries:
        rel = relative(path, root)
        if path.is_dir():
            rel += "/"
        files.append(rel)
        if len(files) >= limit:
            files.append(f"... truncated after {limit} entries")
            break
    return files


def find_skill_md_files(files: List[Path]) -> List[Path]:
    return [p for p in files if p.name == "SKILL.md"]


def scan_template_markers(files: List[Path], root: Path, max_read_bytes: int) -> List[Dict[str, str]]:
    findings: List[Dict[str, str]] = []
    for path in files:
        text = safe_read_text(path, max_bytes=max_read_bytes)
        if text is None:
            continue
        for pattern in TEMPLATE_MARKER_PATTERNS:
            if pattern.search(text):
                findings.append({"file": relative(path, root), "pattern": pattern.pattern})
                break
    return findings


def template_leftover_findings(marker_findings: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    return [
        finding(
            "warning",
            "template_marker_found",
            "possible template or placeholder marker found",
            file=item.get("file"),
            pattern=item.get("pattern", ""),
        )
        for item in marker_findings
    ]


def secret_filename_pattern(name_match_target: str, display_rel: str) -> Optional[str]:
    for pattern in SECRET_FILENAME_PATTERNS:
        if pattern.search(name_match_target) or pattern.search(display_rel):
            return pattern.pattern
    return None


def is_common_secret_config_name(path: Path) -> bool:
    return path.name.casefold() in SECRET_CONFIG_FILENAMES


def read_safety_text(path: Path, max_safety_scan_bytes: Optional[int]) -> Tuple[Optional[str], bool, Optional[str]]:
    """Read a safety-scan candidate and disclose any explicit partial scan.

    The normal path is unbounded because directory/ZIP preflight has already
    established file and package limits. A caller must explicitly supply the
    exploratory ``max_safety_scan_bytes`` override to allow a partial scan.
    """
    try:
        size = path.stat().st_size
    except OSError as exc:
        return None, False, f"could not stat file: {exc}"
    truncated = max_safety_scan_bytes is not None and size > max_safety_scan_bytes
    text = safe_read_text(path, max_bytes=max_safety_scan_bytes, force=True)
    if text is None:
        return None, truncated, "could not read file as text"
    return text, truncated, None


def secret_findings_for_path(
    path: Path,
    name_match_target: str,
    display_rel: str,
    max_safety_scan_bytes: Optional[int],
    outside_root: bool,
) -> SafetyScanResult:
    """Filename + content secret findings for one file, shared by the in-root and
    outside-root scanners. outside_root selects the _outside_root code variants
    and the message suffix."""
    result = SafetyScanResult()
    findings = result.findings
    suffix = "_outside_root" if outside_root else ""
    matched_pattern = secret_filename_pattern(name_match_target, display_rel)
    matched_name = matched_pattern is not None
    if matched_pattern:
        message = ("file outside the detected skill root has a credential-like name"
                   if outside_root else
                   "file name suggests possible bundled credentials or secrets")
        findings.append(finding("warning", f"secret_suspicious_filename{suffix}", message, file=display_rel, risk="suspicious filename", pattern=matched_pattern))
    # File names are a useful signal, but all regular text/config content is
    # eligible. Unknown names receive a bounded sniff so source files such as
    # .envrc and uncommon configuration formats do not become blind spots.
    scan_candidate = True if matched_name else is_secret_scan_candidate(path)
    if scan_candidate is False:
        return result
    if scan_candidate is None:
        findings.append(finding("error", f"secret_scan_unreadable{suffix}", "regular file could not be read to determine whether it needs secret scanning; inspection is incomplete", file=display_rel))
        result.incomplete_paths.append(display_rel)
        return result
    text, truncated, read_error = read_safety_text(path, max_safety_scan_bytes)
    if read_error or text is None:
        findings.append(finding("error", f"secret_scan_unreadable{suffix}", "eligible file could not be read for the bounded secret scan; inspection is incomplete", file=display_rel))
        result.incomplete_paths.append(display_rel)
        return result
    for label, code, severity, pattern in SECRET_CONTENT_PATTERNS:
        if pattern.search(text):
            message = f"possible {label} found" + (" outside the detected skill root" if outside_root else "")
            findings.append(finding(severity, f"{code}{suffix}", message, file=display_rel, risk=label, pattern=pattern.pattern))
            break
    if truncated:
        size = path.stat().st_size
        findings.append(finding("info", f"secret_scan_truncated{suffix}", "secret scan used the explicit exploratory safety-scan cap; coverage is incomplete", file=display_rel, bytes=size, limit=max_safety_scan_bytes))
        result.incomplete_paths.append(display_rel)
    return result


def scan_secret_risks(files: List[Path], root: Path, max_safety_scan_bytes: Optional[int], file_prefix: str = "") -> SafetyScanResult:
    result = SafetyScanResult()
    for path in files:
        rel = relative(path, root)
        display_rel = f"{file_prefix}{rel}" if file_prefix else rel
        result.extend(secret_findings_for_path(path, rel, display_rel, max_safety_scan_bytes, outside_root=False))
    return result


def dangerous_script_language(path: Path) -> Tuple[Optional[str], bool]:
    """Return the executable language and whether candidate detection completed."""
    suffix = path.suffix.lower()
    if suffix in SHELL_SCRIPT_EXTENSIONS:
        return "shell", True
    if suffix in POWERSHELL_SCRIPT_EXTENSIONS:
        return "powershell", True
    if suffix in WINDOWS_BATCH_EXTENSIONS:
        return "batch", True
    if suffix in PYTHON_SCRIPT_EXTENSIONS:
        return "python", True
    if suffix in JAVASCRIPT_SCRIPT_EXTENSIONS:
        return "javascript", True
    if path.suffix:
        return None, True
    text = safe_read_text(path, max_bytes=TEXT_SNIFF_BYTES, force=True)
    if text is None:
        return None, False
    first_line = text.splitlines()[0] if text.strip() else ""
    if SHELL_SHEBANG_PATTERN.match(first_line):
        return "shell", True
    if PYTHON_SHEBANG_PATTERN.match(first_line):
        return "python", True
    if JAVASCRIPT_SHEBANG_PATTERN.match(first_line):
        return "javascript", True
    return None, True


def dangerous_patterns_for_language(language: str) -> List[Tuple[str, re.Pattern[str]]]:
    if language == "python":
        return PYTHON_DANGEROUS_COMMAND_PATTERNS
    if language == "javascript":
        return JAVASCRIPT_DANGEROUS_COMMAND_PATTERNS
    return DANGEROUS_COMMAND_PATTERNS


def shell_match_starts_in_executable_context(text: str, offset: int) -> bool:
    """Distinguish live shell syntax from inert quoted examples/comments.

    This is deliberately bounded to the line prefix and the match's starting
    token. Quotes around a later command target therefore remain visible to
    the dangerous-command pattern. Known ``sh -c``/``eval`` string payloads
    remain executable contexts rather than becoming a quoting bypass.
    """
    line_start = text.rfind("\n", 0, offset) + 1
    prefix = text[line_start:offset]
    quote: Optional[str] = None
    quote_start: Optional[int] = None
    escaped = False
    for index, character in enumerate(prefix):
        if escaped:
            escaped = False
            continue
        if quote == "'":
            if character == "'":
                quote = None
                quote_start = None
            continue
        if character == "\\":
            escaped = True
            continue
        if quote == '"':
            if character == '"':
                quote = None
                quote_start = None
            continue
        if character in {"'", '"'}:
            quote = character
            quote_start = index
            continue
        if character == "#" and (
            index == 0
            or prefix[index - 1].isspace()
            or prefix[index - 1] in ";|&()"
        ):
            return False

    if quote is None:
        return True
    assert quote_start is not None
    quoted_prefix = prefix[quote_start + 1:]
    if quote == '"' and (
        re.search(r"(?<!\\)\$\(", quoted_prefix)
        or re.search(r"(?<!\\)`", quoted_prefix)
    ):
        return True
    before_quote = prefix[:quote_start].rstrip()
    return bool(
        re.search(
            r"(?:['\"]?(?:/(?:[A-Za-z0-9._+-]+/)+)?(?:ba|z|k)?sh['\"]?\s+-c|\beval)\s*$",
            before_quote,
            re.IGNORECASE,
        )
    )


def scan_dangerous_commands(
    files: List[Path],
    root: Path,
    max_safety_scan_bytes: Optional[int],
    *,
    file_prefix: str = "",
    outside_root: bool = False,
) -> SafetyScanResult:
    """Heuristically flag destructive commands in executable scripts.

    Non-exhaustive and executable-script-only by design, avoiding false
    positives in documentation that merely mentions dangerous commands. All
    matches are high-confidence dangerous behavior, including within the Skill
    root, so strict validation must fail.
    """
    result = SafetyScanResult()
    findings = result.findings
    for path in files:
        display_rel = f"{file_prefix}{relative(path, root)}" if file_prefix else relative(path, root)
        language, candidate_readable = dangerous_script_language(path)
        if language is None and candidate_readable:
            continue
        if not candidate_readable:
            findings.append(finding("error", f"dangerous_command_scan_unreadable{'_outside_root' if outside_root else ''}", "candidate executable script could not be read for dangerous-command scanning; inspection is incomplete", file=display_rel))
            result.incomplete_paths.append(display_rel)
            continue
        text, truncated, read_error = read_safety_text(path, max_safety_scan_bytes)
        if read_error or text is None:
            findings.append(finding("error", f"dangerous_command_scan_unreadable{'_outside_root' if outside_root else ''}", "candidate executable script could not be read for dangerous-command scanning; inspection is incomplete", file=display_rel))
            result.incomplete_paths.append(display_rel)
            continue
        assert language is not None
        for label, pattern in dangerous_patterns_for_language(language):
            match = next(
                (
                    candidate
                    for candidate in pattern.finditer(text)
                    if language != "shell"
                    or shell_match_starts_in_executable_context(
                        text, candidate.start()
                    )
                ),
                None,
            )
            if match is not None:
                location = " outside the detected skill root" if outside_root else ""
                findings.append(finding("error", f"script_dangerous_command{'_outside_root' if outside_root else ''}", f"bundled executable script{location} contains a potentially destructive command ({label}); review before running", file=display_rel, risk=label, pattern=pattern.pattern, language=language))
                break
        if truncated:
            size = path.stat().st_size
            findings.append(finding("info", f"dangerous_command_scan_truncated{'_outside_root' if outside_root else ''}", "dangerous-command scan used the explicit exploratory safety-scan cap; coverage is incomplete", file=display_rel, bytes=size, limit=max_safety_scan_bytes))
            result.incomplete_paths.append(display_rel)
    return result


def entries_outside_detected_root(base_path: Path, skill_root: Path, base_entries: Optional[List[Path]] = None) -> List[Path]:
    try:
        base = base_path.resolve()
        root = skill_root.resolve()
    except OSError:
        return []
    if base == root:
        return []
    paths = base_entries if base_entries is not None else walk_paths_no_symlinks(base)
    outside: List[Path] = []
    for path in paths:
        try:
            resolved = path.resolve()
        except OSError:
            continue
        if resolved != root and root not in resolved.parents:
            outside.append(path)
    return outside


def is_executable_code_file(path: Path) -> bool:
    """Recognize executable code unexpectedly bundled outside the Skill root."""
    if path.suffix.lower() in EXECUTABLE_CODE_EXTENSIONS:
        return True
    try:
        if path.stat().st_mode & stat.S_IXUSR:
            return True
    except OSError:
        return False
    text = safe_read_text(path, max_bytes=TEXT_SNIFF_BYTES, force=True)
    return bool(text and text.startswith("#!"))


def files_outside_detected_root(base_path: Path, skill_root: Path, base_entries: Optional[List[Path]] = None) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    try:
        base = base_path.resolve()
        root = skill_root.resolve()
    except OSError:
        return findings
    if base == root:
        return findings
    for path in entries_outside_detected_root(base_path, skill_root, base_entries):
        if path.is_dir():
            findings.append(finding("warning", "archive_directory_outside_skill_root", "archive contains a directory outside the detected skill root", file=relative(path, base)))
        elif is_regular_file(path):
            file_rel = relative(path, base)
            if is_executable_code_file(path):
                findings.append(finding("error", "archive_executable_code_outside_skill_root", "archive contains executable code outside the detected skill root; move it into the Skill root or exclude it from the package", file=file_rel))
            else:
                findings.append(finding("warning", "archive_file_outside_skill_root", "archive contains a file outside the detected skill root", file=file_rel))
    return findings


def scan_secret_risks_outside_detected_root(base_path: Path, skill_root: Path, max_safety_scan_bytes: Optional[int], base_entries: Optional[List[Path]] = None) -> SafetyScanResult:
    try:
        base = base_path.resolve()
        root = skill_root.resolve()
    except OSError:
        return SafetyScanResult()
    if base == root:
        return SafetyScanResult()
    result = SafetyScanResult()
    for path in entries_outside_detected_root(base_path, skill_root, base_entries):
        if not is_regular_file(path):
            continue
        rel_to_base = relative(path, base)
        display_rel = f"outside-root:{rel_to_base}"
        result.extend(secret_findings_for_path(path, path.name, display_rel, max_safety_scan_bytes, outside_root=True))
    return result


def strip_code_fences(text: str) -> str:
    """Drop lines inside ``` / ~~~ fenced code blocks.

    Fenced blocks hold illustrative examples (e.g. a sample skill layout), not
    the skill's own resources, so references found only inside a fence should not
    be treated as real (missing) resource links. Inline backtick refs in prose
    are preserved.
    """
    out: List[str] = []
    fence: Optional[str] = None
    for line in text.splitlines():
        marker = line.lstrip()[:3]
        if fence is None:
            if marker in ("```", "~~~"):
                fence = marker
            else:
                out.append(line)
        elif marker == fence:
            fence = None
    return "\n".join(out)


@dataclass
class ResourceGraph:
    documents: List[str] = field(default_factory=list)
    edges: List[Dict[str, Any]] = field(default_factory=list)
    unassessed: List[Dict[str, Any]] = field(default_factory=list)
    text_bytes: int = 0

    @property
    def complete(self) -> bool:
        return not self.unassessed

    def as_dict(self) -> Dict[str, Any]:
        return {"documents": self.documents, "edges": self.edges,
                "unassessed": self.unassessed, "text_bytes": self.text_bytes,
                "complete": self.complete}

    def projection(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {"existing": [], "missing": [], "unsafe": [],
                                  "unsafe_reasons": {}, "source_only": []}
        for edge in self.edges:
            status = edge["status"]
            if status not in {"existing", "missing", "unsafe"}:
                continue
            path = edge["target"] if status != "unsafe" else edge["reference"]
            result[status].append(path)
            if status == "unsafe":
                result["unsafe_reasons"][path] = edge["reason"]
        for status in ("existing", "missing", "unsafe"):
            result[status] = sorted(set(result[status]))
        return result


def markdown_destination(line: str, start: int) -> Optional[Tuple[str, int]]:
    """Scan one parenthesized destination; work is bounded by the source line."""
    depth = 1
    cursor = start + 1
    content_start = cursor
    while content_start < len(line) and line[content_start].isspace():
        content_start += 1
    quote: Optional[str] = None
    angle = False
    while cursor < len(line):
        char = line[cursor]
        if char == "\\":
            cursor += 2
            continue
        if quote:
            if char == quote:
                quote = None
        elif char in {"'", '"'} and cursor > start + 1 and line[cursor - 1].isspace():
            quote = char
        elif char == "<" and cursor == content_start:
            angle = True
        elif char == ">" and angle:
            angle = False
        elif not angle and char == "(":
            depth += 1
        elif not angle and char == ")":
            depth -= 1
            if depth == 0:
                raw = line[start + 1:cursor].strip()
                if raw.startswith("<"):
                    close = raw.find(">")
                    if close < 0:
                        return None
                    value = raw[1:close]
                else:
                    value = re.split(r'\s+[\'\"]', raw, maxsplit=1)[0]
                return re.sub(r"\\([()<>\\])", r"\1", value), cursor + 1
        cursor += 1
    return None


def inline_code_spans(line: str) -> Iterable[Tuple[int, int, str]]:
    """Pair equal backtick runs in linear passes, including multi-tick spans."""
    runs = list(re.finditer(r"`+", line))
    following: Dict[int, int] = {}
    last: Dict[int, int] = {}
    for index in range(len(runs) - 1, -1, -1):
        length = len(runs[index].group())
        if length in last:
            following[index] = last[length]
        last[length] = index
    index = 0
    while index < len(runs):
        closing = following.get(index)
        if closing is None:
            index += 1
            continue
        first, final = runs[index], runs[closing]
        yield first.start(), final.end(), line[first.end():final.start()]
        index = closing + 1


def local_document_links(text: str) -> Iterable[Tuple[str, int]]:
    """Read Markdown links and standalone inline file paths, never commands.

    Line-preserving fence/comment removal keeps source locations useful. Link
    destinations are document-relative; schemes and anchors are not resources.
    This intentionally does not parse source-code imports or HTML code examples.
    """
    lines = text.splitlines()
    fence: Optional[str] = None
    clean: List[str] = []
    for line in lines:
        marker = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if marker and fence is None:
            fence = marker.group(1)
            clean.append("")
        elif fence is not None:
            if re.match(r"^\s{0,3}" + re.escape(fence[0]) + "{" + str(len(fence)) + r",}\s*$", line):
                fence = None
            clean.append("")
        else:
            clean.append(line)
    body = "\n".join(clean)
    body = re.sub(r"<!--.*?-->", lambda m: "\n" * m.group().count("\n"), body, flags=re.S)
    body = re.sub(r"<(code|pre)\b[^>]*>.*?</\1\s*>",
                  lambda m: re.sub(r"[^\n]", " ", m.group()), body, flags=re.S | re.I)
    definitions: Dict[str, str] = {}
    definition = re.compile(r'^\s{0,3}\[([^\]]+)\]:\s*(<[^>]*>|\S+)(?:\s+.*)?$')
    def label(value: str) -> str:
        return " ".join(value.lower().split())
    for line in body.splitlines():
        match = definition.match(line)
        if match:
            definitions.setdefault(label(match.group(1)), match.group(2).strip("<>"))
    link_pattern = re.compile(r'!?\[([^\]\n]*)\]')
    for number, line in enumerate(body.splitlines(), 1):
        if definition.match(line):
            continue
        code_spans = list(inline_code_spans(line))
        masked = list(line)
        for start, end, _ in code_spans:
            masked[start:end] = " " * (end - start)
        markup = "".join(masked)
        spans: List[Tuple[int, int]] = []
        consumed = 0
        for match in link_pattern.finditer(markup):
            if match.start() < consumed:
                continue
            end = match.end()
            value = ""
            if end < len(markup) and markup[end] == "(":
                destination = markdown_destination(markup, end)
                if destination is None:
                    # Do not rescan an unmatched remainder for every label.
                    break
                value, end = destination
            elif end < len(markup) and markup[end] == "[":
                close = markup.find("]", end + 1)
                if close >= 0:
                    value = definitions.get(label(markup[end + 1:close] or match.group(1)), "")
                    end = close + 1
            else:
                value = definitions.get(label(match.group(1)), "")
            if value:
                consumed = end
                spans.append((match.start(), end))
                yield value, number
        for start, _, value in code_spans:
            if any(begin <= start < end for begin, end in spans):
                continue
            # Standalone inline paths retain resource semantics; commands and
            # embedded Markdown examples do not establish dependencies.
            if not re.search(r'\s|[<>*{}|]', value) and not value.endswith("/") and (
                value.startswith(("scripts/", "references/", "assets/", "./", "../"))
            ):
                yield value, number


def collect_resource_graph(skill_root: Path, entrypoint: Path, limits: InspectionLimits) -> ResourceGraph:
    """Collect a bounded, local-only graph from reachable instruction documents."""
    graph = ResourceGraph()
    root = skill_root.resolve()
    document_cap = min(limits.max_resource_documents, limits.max_directory_files, limits.max_zip_members)
    byte_cap = min(limits.max_resource_text_bytes, limits.max_directory_total_bytes, limits.max_zip_uncompressed_bytes)
    file_cap = min(limits.max_directory_file_bytes, limits.max_zip_member_bytes)
    depth_cap = min(limits.max_resource_depth, limits.max_directory_depth)
    queue: List[Tuple[Path, int]] = [(entrypoint, 0)]
    queued = {entrypoint.resolve()}
    cursor = 0
    while cursor < len(queue):
        document, depth = queue[cursor]
        cursor += 1
        source = relative(document, root)
        reason = None
        if depth > depth_cap:
            reason = "document depth limit"
        elif len(graph.documents) >= document_cap:
            reason = "document count limit"
        try:
            if document.resolve() != root and root not in document.resolve().parents:
                reason = "document outside root"
            elif any(part.is_symlink() for part in (document, *document.parents) if part != root and root in part.parents):
                reason = "symlink document"
            elif not is_regular_file(document):
                reason = "document unavailable or not regular"
            if reason is None:
                remaining = min(file_cap, byte_cap - graph.text_bytes)
                with document.open("rb") as stream:
                    payload = stream.read(max(0, remaining) + 1)
                if len(payload) > remaining:
                    reason = "document text byte limit"
                else:
                    text = payload.decode("utf-8")
        except (OSError, RuntimeError, UnicodeError, ValueError):
            reason = "document unreadable"
        if reason:
            graph.unassessed.append({"source": source, "reason": reason})
            continue
        graph.documents.append(source)
        graph.text_bytes += len(payload)
        for raw, line in local_document_links(text):
            drive_path = re.match(r"^[A-Za-z]:", raw) is not None
            external_scheme = re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", raw) is not None
            if not raw or raw.startswith(("#", "//")) or (external_scheme and not drive_path):
                continue
            if len(graph.edges) >= limits.max_resource_edges:
                graph.unassessed.append({"source": source, "line": line, "reason": "edge count limit"})
                break
            ref = unquote(raw.split("#", 1)[0].split("?", 1)[0])
            if not ref:
                continue
            edge: Dict[str, Any] = {"source": source, "line": line, "reference": raw, "target": ref, "status": "unsafe"}
            graph.edges.append(edge)
            path = PurePosixPath(ref)
            if path.is_absolute() or re.match(r"^[A-Za-z]:", ref) or "\\" in ref or "\x00" in ref:
                edge["reason"] = "resource references must be local relative paths, not absolute paths"
                continue
            candidate = document.parent.joinpath(*path.parts)
            try:
                resolved = candidate.resolve()
                if resolved != root and root not in resolved.parents:
                    edge["reason"] = "resource reference resolves outside the skill root"
                elif any(part.is_symlink() for part in (candidate, *candidate.parents) if part != root and root in part.parents):
                    edge["reason"] = "resource reference points through a symlink"
                elif candidate.exists() and not is_regular_file(candidate):
                    edge["reason"] = "resource reference must point to a regular file"
                else:
                    edge["target"] = relative(resolved, root)
                    edge["status"] = "existing" if candidate.exists() else "missing"
                    if edge["status"] == "existing" and resolved.suffix.lower() in {".md", ".markdown", ".txt", ".rst"} and resolved not in queued:
                        queue.append((resolved, depth + 1))
                        queued.add(resolved)
            except (OSError, RuntimeError, ValueError):
                edge["reason"] = "resource reference could not be inspected safely"
    return graph


def source_only_resources(
    skill_text: str,
    skill_root: Path,
    *,
    declared_skill_name: Optional[str] = None,
) -> Dict[str, Any]:
    unsafe: List[str] = []
    unsafe_reasons: Dict[str, str] = {}
    source_only: List[str] = []
    resolved_root = skill_root.resolve()
    # A Skill Forge source checkout has a few repository-maintenance helpers
    # that are deliberately excluded from its installable runtime. Keep their
    # declaration distinct from ordinary Markdown resource references: this
    # preserves strict missing-reference checks for every normal resource while
    # preventing direct-source orphan guidance from flagging known tooling.
    if declared_skill_name == "skill-forge":
        for match in SOURCE_ONLY_DECLARATION_PATTERN.finditer(strip_code_fences(skill_text)):
            declared = (match.group(1) or "").split()
            if not declared:
                unsafe.append("<source-only declaration>")
                unsafe_reasons["<source-only declaration>"] = (
                    "source-only declaration must list one or more safe scripts/ paths"
                )
                continue
            for ref in declared:
                raw_parts = ref.split("/")
                path = PurePosixPath(ref)
                if path.is_absolute():
                    unsafe.append(ref)
                    unsafe_reasons[ref] = "source-only declarations must not be absolute"
                    continue
                if ".." in raw_parts:
                    unsafe.append(ref)
                    unsafe_reasons[ref] = "source-only declarations must not use parent-directory traversal"
                    continue
                if (
                    "\\" in ref
                    or len(raw_parts) < 2
                    or raw_parts[0] != "scripts"
                    or any(part in {"", "."} for part in raw_parts)
                ):
                    unsafe.append(ref)
                    unsafe_reasons[ref] = "source-only declarations must list safe scripts/ paths"
                    continue
                candidate = skill_root.joinpath(*raw_parts)
                try:
                    resolved_candidate = candidate.resolve(strict=False)
                except OSError:
                    unsafe.append(ref)
                    unsafe_reasons[ref] = "source-only declaration could not be resolved safely"
                    continue
                if resolved_candidate != resolved_root and resolved_root not in resolved_candidate.parents:
                    unsafe.append(ref)
                    unsafe_reasons[ref] = "source-only declaration resolves outside the skill root"
                    continue
                source_only.append(ref)

    return {
        "existing": [],
        "missing": [],
        "unsafe": sorted(set(unsafe)),
        "unsafe_reasons": unsafe_reasons,
        "source_only": sorted(set(source_only)),
    }


def classify_top_level(files: List[Path], skill_root: Path) -> Dict[str, Any]:
    result: Dict[str, Any] = {name: [] for name in ["agents", "scripts", "references", "assets"]}
    for path in files:
        rel = relative(path, skill_root)
        head, sep, _ = rel.partition("/")
        if sep and head in result:
            result[head].append(rel)
    for name in result:
        result[name] = sorted(result[name])
    return result


def file_size_summary(files: List[Path], root: Path) -> Dict[str, Any]:
    total = 0
    largest: List[Tuple[int, str]] = []
    file_count = 0
    for path in files:
        try:
            size = path.stat().st_size
        except OSError:
            continue
        total += size
        file_count += 1
        largest.append((size, relative(path, root)))
    largest = sorted(largest, reverse=True)[:10]
    return {
        "file_count": file_count,
        "total_bytes_uncompressed": total,
        "largest_files": [{"file": name, "bytes": size} for size, name in largest],
    }


def package_size_findings(input_path: Path, root: Optional[Path], folder_total: int) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    # Zip archive size is gated in validate_zip_archive before the archive is
    # opened (package_zip_too_large there); here we only assess a direct folder
    # input's uncompressed size (already computed once), so the two never
    # double-report.
    try:
        if root is not None and root.exists() and not input_path.is_file():
            if folder_total > MAX_INSPECTOR_INPUT_ZIP_BYTES:
                findings.append(finding("warning", "package_folder_large", "folder uncompressed size exceeds Skill Forge's generic review threshold; it is not a host upload-limit claim", bytes=folder_total, limit=MAX_INSPECTOR_INPUT_ZIP_BYTES, limit_kind="inspector_safety"))
    except OSError:
        pass
    return findings


def find_orphaned_resource_candidates(files: List[Path], skill_root: Path, refs: Dict[str, List[str]]) -> List[str]:
    referenced = set(refs.get("existing", [])) | set(refs.get("source_only", []))
    candidates: List[str] = []
    # Grouped by directory (scripts, references, assets) to preserve output order;
    # within a group, files keep their traversal order.
    for dirname in ["scripts", "references", "assets"]:
        for path in files:
            rel = relative(path, skill_root)
            head, sep, _ = rel.partition("/")
            if sep and head == dirname and rel not in referenced:
                candidates.append(rel)
    return candidates


def validate_openai_icon_reference(
    skill_root: Path, field_name: str, value: Any
) -> List[Dict[str, Any]]:
    """Validate one optional OpenAI icon reference against the bundled contract."""
    metadata_file = "agents/openai.yaml"
    if not isinstance(value, str) or not value.strip():
        return [finding(
            "error",
            "openai_metadata_icon_path_invalid",
            f"interface.{field_name} must be a non-empty safe relative path",
            file=metadata_file,
            field=field_name,
        )]
    normalized = value.strip().replace("\\", "/")
    path = PurePosixPath(normalized)
    if path.is_absolute() or not path.parts or ".." in path.parts:
        return [finding(
            "error",
            "openai_metadata_icon_path_invalid",
            f"interface.{field_name} must be a safe relative path within the Skill directory",
            file=metadata_file,
            field=field_name,
        )]
    candidate = skill_root.joinpath(*path.parts)
    try:
        resolved_root = skill_root.resolve()
        resolved_candidate = candidate.resolve(strict=False)
    except OSError as exc:
        return [finding(
            "error",
            "openai_metadata_icon_path_invalid",
            f"interface.{field_name} could not be resolved safely: {exc}",
            file=metadata_file,
            field=field_name,
        )]
    if resolved_candidate != resolved_root and resolved_root not in resolved_candidate.parents:
        return [finding(
            "error",
            "openai_metadata_icon_path_invalid",
            f"interface.{field_name} resolves outside the Skill directory",
            file=metadata_file,
            field=field_name,
        )]
    if not candidate.exists():
        return [finding(
            "error",
            "openai_metadata_icon_missing",
            f"interface.{field_name} references an icon asset that does not exist",
            file=metadata_file,
            field=field_name,
        )]
    if not is_regular_file(candidate):
        return [finding(
            "error",
            "openai_metadata_icon_path_invalid",
            f"interface.{field_name} must reference a regular icon asset file",
            file=metadata_file,
            field=field_name,
        )]
    return []


def validate_agent_metadata(
    skill_root: Path,
    max_read_bytes: Optional[int],
    target: str = "portable",
    declared_skill_name: Optional[str] = None,
) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    profile = target_profile(target)
    if not profile.validate_openai_metadata:
        return findings
    agent_path = skill_root / "agents" / "openai.yaml"
    if not agent_path.exists():
        if profile.name == "openai":
            findings.append(finding("warning", "openai_metadata_missing", "OpenAI target profile has no agents/openai.yaml metadata; add it when the OpenAI packaging or UI workflow needs it", file="agents/openai.yaml"))
        return findings
    # OpenAI metadata is a critical manifest. Read it in full after preflight
    # rather than accepting a syntactically valid prefix that hides duplicate
    # or contradictory keys beyond the display-read cap.
    text = safe_read_text(agent_path, max_bytes=max_read_bytes)
    if text is None:
        findings.append(finding("error", "openai_metadata_unreadable", "OpenAI metadata agents/openai.yaml could not be read as text", file="agents/openai.yaml"))
        return findings
    meaningful_lines = [line for line in text.splitlines() if line.strip() and not line.lstrip(" ").startswith("#")]
    if not meaningful_lines:
        metadata: Dict[str, Any] = {}
    else:
        try:
            metadata = parse_yaml_mapping(text)
        except YamlUnsupportedSyntaxError as exc:
            findings.append(finding(
                "warning",
                "openai_metadata_yaml_unsupported",
                f"agents/openai.yaml uses valid YAML syntax this restricted parser cannot verify: {exc}",
                file="agents/openai.yaml",
            ))
            return findings
        except YamlParseError as exc:
            findings.append(finding("error", "openai_metadata_yaml_invalid", f"agents/openai.yaml is not valid supported YAML: {exc}", file="agents/openai.yaml"))
            return findings
    if "interface" not in metadata:
        findings.append(finding("warning", "openai_metadata_missing_interface", "agents/openai.yaml should include interface metadata for OpenAI workflows", file="agents/openai.yaml"))
        return findings
    interface = metadata["interface"]
    if not isinstance(interface, dict):
        findings.append(finding("error", "openai_metadata_interface_invalid", "agents/openai.yaml interface must be a mapping", file="agents/openai.yaml"))
        return findings
    display_name = interface.get("display_name")
    if display_name is None:
        findings.append(finding("warning", "openai_metadata_missing_display_name", "interface.display_name is missing for OpenAI workflows", file="agents/openai.yaml"))
    elif not isinstance(display_name, str) or not display_name.strip():
        findings.append(finding("error", "openai_metadata_display_name_invalid", "interface.display_name must be a non-empty string", file="agents/openai.yaml"))
    if "short_description" not in interface:
        findings.append(finding("warning", "openai_metadata_missing_short_description", "interface.short_description is missing for OpenAI workflows", file="agents/openai.yaml"))
    else:
        short_description = interface["short_description"]
        if not isinstance(short_description, str) or not short_description.strip():
            findings.append(finding("error", "openai_metadata_short_description_invalid", "interface.short_description must be a non-empty string", file="agents/openai.yaml"))
        elif not OPENAI_SHORT_DESCRIPTION_MIN_LENGTH <= len(short_description) <= OPENAI_SHORT_DESCRIPTION_MAX_LENGTH:
            findings.append(finding(
                "error",
                "openai_metadata_short_description_length",
                f"interface.short_description must be {OPENAI_SHORT_DESCRIPTION_MIN_LENGTH}-{OPENAI_SHORT_DESCRIPTION_MAX_LENGTH} characters",
                file="agents/openai.yaml",
                length=len(short_description),
                minimum=OPENAI_SHORT_DESCRIPTION_MIN_LENGTH,
                maximum=OPENAI_SHORT_DESCRIPTION_MAX_LENGTH,
            ))
    if "default_prompt" in interface:
        default_prompt = interface["default_prompt"]
        if not isinstance(default_prompt, str) or not default_prompt.strip():
            findings.append(finding("error", "openai_metadata_default_prompt_invalid", "interface.default_prompt must be a non-empty string when present", file="agents/openai.yaml"))
        elif isinstance(declared_skill_name, str) and declared_skill_name.strip() and f"${declared_skill_name.strip()}" not in default_prompt:
            findings.append(finding(
                "error",
                "openai_metadata_default_prompt_missing_skill_reference",
                f"interface.default_prompt must explicitly reference ${declared_skill_name.strip()}",
                file="agents/openai.yaml",
                expected_skill=f"${declared_skill_name.strip()}",
            ))
    for field_name in OPENAI_ICON_FIELDS:
        if field_name in interface:
            findings.extend(validate_openai_icon_reference(skill_root, field_name, interface[field_name]))
    return findings


def structural_findings(skill_md_count: int, main_skill_exists: bool, resource_refs: Dict[str, Any]) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    if skill_md_count == 0:
        findings.append(finding("error", "skill_md_missing", "no SKILL.md found"))
    elif skill_md_count > 1:
        findings.append(finding("error", "skill_md_multiple", f"multiple SKILL.md files found: {skill_md_count}"))
    if not main_skill_exists:
        findings.append(finding("error", "root_skill_md_missing", "no SKILL.md found at the detected skill root"))
    for ref in resource_refs.get("missing", []):
        findings.append(finding("error", "missing_resource_reference", "referenced resource does not exist", file=ref))
    for ref in resource_refs.get("unsafe", []):
        reason = resource_refs.get("unsafe_reasons", {}).get(ref, "resource reference is unsafe")
        code = "resource_reference_outside_root" if "outside" in reason or "parent-directory" in reason or "absolute" in reason else "resource_reference_unsafe"
        findings.append(finding("error", code, reason, file=ref))
    return findings


def directory_name_matches(profile: TargetProfile, directory_name: str, skill_name: str) -> bool:
    return directory_name == skill_name


def target_layout_findings(
    profile: TargetProfile,
    *,
    is_zip: bool,
    root_relative: Optional[str],
    directory_name: str,
    skill_name: Any,
    outside_root_findings: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Apply target-specific package-layout rules after a safe root is known."""
    findings: List[Dict[str, Any]] = []
    if is_zip and profile.requires_zip_top_level_folder:
        if root_relative in {None, "."}:
            findings.append(finding(
                "error",
                "target_zip_root_layout_invalid",
                f"{profile.name} requires a ZIP containing one top-level skill directory, not files at the archive root",
                target=profile.name,
            ))
        elif outside_root_findings:
            findings.append(finding(
                "error",
                "target_zip_root_layout_invalid",
                f"{profile.name} requires the skill directory to be the ZIP's single top-level entry",
                target=profile.name,
                outside_root_files=[item.get("file") for item in outside_root_findings],
            ))
    if not isinstance(skill_name, str) or not skill_name.strip():
        return findings
    clean_name = skill_name.strip()
    if profile.directory_name_mode == "human-normalized":
        directory_key = normalized_human_skill_name(directory_name)
        skill_key = normalized_human_skill_name(clean_name)
        if not directory_key or not skill_key:
            findings.append(finding(
                "error",
                "frontmatter_name_directory_comparison_invalid",
                f"skill directory name and frontmatter name must produce non-empty Unicode comparison keys for the {profile.name} target profile",
                directory_name=directory_name,
                directory_key=directory_key,
                match_mode=profile.directory_name_mode,
            ))
        elif directory_key != skill_key:
            findings.append(finding(
                "error",
                "frontmatter_name_directory_mismatch",
                f"skill directory name must match the frontmatter name for the {profile.name} target profile",
                expected=directory_name,
                match_mode=profile.directory_name_mode,
            ))
    elif profile.directory_name_mode != "none" and not directory_name_matches(profile, directory_name, clean_name):
        findings.append(finding(
            "error",
            "frontmatter_name_directory_mismatch",
            f"skill directory name must match the frontmatter name for the {profile.name} target profile",
            expected=directory_name,
            match_mode=profile.directory_name_mode,
        ))
    return findings


def inspect(input_path: Path, tree_limit: int = MAX_DEFAULT_TREE_FILES, limits: Optional[InspectionLimits] = None, target: str = "portable") -> Dict[str, Any]:
    canonical = canonical_target(target)
    profile = TARGET_PROFILES[canonical]
    limits = limits or InspectionLimits()
    base_path, temp_dir, unpack_error, zip_findings = unpack_if_needed(input_path, limits, profile)
    try:
        result: Dict[str, Any] = {
            "schema_version": INSPECTION_SCHEMA_VERSION,
            "input": str(input_path),
            "input_exists": input_path.exists(),
            "input_type": "zip" if input_path.is_file() and input_path.suffix.lower() == ".zip" else "directory" if input_path.is_dir() or input_path.is_symlink() else "other",
            # ``target`` is retained as the requested spelling for clients that
            # used it before canonical profile names and aliases were added.
            "target": target,
            "requested_target": target,
            "canonical_target": canonical,
            "target_alias_used": target != canonical,
            "target_deprecation_note": None,
            "target_profile": profile.json_summary(),
            "unpack_error": unpack_error,
            "detected_root": None,
            "detected_root_relative": None,
            "zip_preflight_findings": zip_findings,
            "directory_preflight_findings": [],
            "coverage_complete": False,
            "unscanned_paths": [],
            "coverage_findings": [],
            "manifest_verification_complete": False,
            "unverified_manifests": [],
            "effective_limits": {
                **limits.as_dict(),
                "tree_limit": tree_limit,
                "target_product_upload_limit_bytes": profile.product_upload_limit_bytes,
            },
            "strict_mode_note": "use --strict to exit 2 when validation findings contain errors, safety scan coverage is incomplete, or a critical YAML manifest is unverified; incomplete evidence cannot pass a release gate",
        }
        if input_path.is_file():
            try:
                result["zip_bytes"] = input_path.stat().st_size
            except OSError:
                pass
        if unpack_error or not base_path.exists():
            result["package_size_findings"] = package_size_findings(input_path, None, 0)
            return finalize_result(result)
        preflight = DirectoryPreflight([], [], [], 0)
        if base_path.is_dir() or base_path.is_symlink():
            scan_ignored_directories = input_path.is_file() and input_path.suffix.lower() == ".zip"
            preflight = validate_directory_tree(
                base_path,
                limits,
                profile,
                scan_ignored_directories=scan_ignored_directories,
            )
            result["directory_preflight_findings"] = preflight.findings
            portability_codes = {
                "directory_nonportable_path",
                "directory_portable_identity_collision",
                "directory_file_directory_prefix_conflict",
            }
            coverage_complete = preflight.coverage_complete and not any(
                item.get("severity") == "error" and item.get("code") not in portability_codes
                for item in preflight.findings
            )
            result["coverage_complete"] = coverage_complete
            result["unscanned_paths"] = unscanned_paths_relative(preflight.unscanned_paths, base_path)
            if not coverage_complete:
                unscanned_paths = result["unscanned_paths"]
                message = (
                    "safety scanning skipped bounded VCS/cache directories; strict and release validation cannot claim complete coverage"
                    if unscanned_paths
                    else "safety scanning could not establish complete bounded coverage; strict and release validation cannot pass"
                )
                result["coverage_findings"] = [finding(
                    "error",
                    "scan_coverage_incomplete",
                    message,
                    unscanned_paths=unscanned_paths,
                )]
            if any(item.get("severity") == "error" for item in preflight.findings):
                result["package_size_findings"] = package_size_findings(input_path, base_path, preflight.total_bytes)
                return finalize_result(result)
        root = is_probably_skill_root(base_path, preflight.entries)
        result["detected_root"] = str(root)
        try:
            root_relative = root.resolve().relative_to(base_path.resolve())
            result["detected_root_relative"] = root_relative.as_posix()
        except (OSError, ValueError):
            # ``detected_root`` remains useful diagnostic context if a path
            # changes mid-inspection; use null rather than a misleading value.
            result["detected_root_relative"] = None
        result["excluded_directories"] = excluded_directories_within_root(preflight.excluded_directories, root)
        # A zip whose SKILL.md sits at the archive root (no wrapping folder)
        # detects its root as the temp extraction dir, whose random name is not a
        # meaningful directory-name comparison. Track that so the name/directory
        # check can report an actionable finding instead of garbage.
        try:
            zip_without_top_level_folder = temp_dir is not None and root.resolve() == base_path.resolve()
        except OSError:
            zip_without_top_level_folder = False
        # One traversal of the detected root feeds every root-scoped analyzer,
        # instead of each re-walking (and re-stat-ing) the same tree.
        root_entries = entries_within_root(preflight.entries, root)
        root_files = [p for p in root_entries if is_regular_file(p)]
        result["tree"] = build_tree(root_entries, root, tree_limit)
        result["size_summary"] = file_size_summary(root_files, root)
        result["package_size_findings"] = package_size_findings(input_path, root, result["size_summary"]["total_bytes_uncompressed"])
        result["outside_root_findings"] = files_outside_detected_root(base_path, root, preflight.entries)
        skill_files = find_skill_md_files(root_files)
        result["skill_md_files"] = [relative(path, root) for path in skill_files]
        result["skill_md_count"] = len(skill_files)
        result["top_level_resources"] = classify_top_level(root_files, root)
        template_markers = scan_template_markers(root_files, root, limits.max_read_bytes)
        result["template_marker_findings"] = template_markers
        result["template_leftover_findings"] = template_leftover_findings(template_markers)
        secret_scan = scan_secret_risks(root_files, root, limits.max_safety_scan_bytes)
        secret_scan.extend(scan_secret_risks_outside_detected_root(base_path, root, limits.max_safety_scan_bytes, preflight.entries))
        result["secret_risk_findings"] = secret_scan.findings
        result["secret_scan_note"] = SECRET_SCAN_NOTE
        outside_files = [
            path for path in entries_outside_detected_root(base_path, root, preflight.entries)
            if is_regular_file(path)
        ]
        dangerous_scan = scan_dangerous_commands(root_files, root, limits.max_safety_scan_bytes)
        dangerous_scan.extend(scan_dangerous_commands(
            outside_files,
            base_path,
            limits.max_safety_scan_bytes,
            file_prefix="outside-root:",
            outside_root=True,
        ))
        result["dangerous_command_findings"] = dangerous_scan.findings
        result["dangerous_command_note"] = "dangerous-command scanning is heuristic and non-exhaustive; it inspects shell, PowerShell, Windows batch, Python, and JavaScript/TypeScript scripts both inside and outside the detected Skill root. High-confidence dangerous commands and executable code outside the root are errors. Eligible scripts are read completely unless --max-safety-scan-bytes explicitly requests exploratory partial scanning."
        incomplete_paths = sorted(set(secret_scan.incomplete_paths + dangerous_scan.incomplete_paths))
        if incomplete_paths:
            combined_unscanned = sorted(set(result["unscanned_paths"] + incomplete_paths))
            result["coverage_complete"] = False
            result["unscanned_paths"] = combined_unscanned
            coverage_findings = result["coverage_findings"]
            existing = next((item for item in coverage_findings if item.get("code") == "scan_coverage_incomplete"), None)
            if existing is None:
                coverage_findings.append(finding(
                    "error",
                    "scan_coverage_incomplete",
                    "one or more eligible secret or dangerous-command scans were incomplete; strict and release validation cannot pass",
                    unscanned_paths=combined_unscanned,
                ))
            else:
                existing["unscanned_paths"] = combined_unscanned
        main_skill = root / "SKILL.md"
        resource_refs: Dict[str, Any] = {
            "existing": [],
            "missing": [],
            "unsafe": [],
            "unsafe_reasons": {},
            "source_only": [],
        }
        declared_skill_name: Optional[str] = None
        if main_skill.exists() and not main_skill.is_symlink():
            # These control-plane manifests must never be parsed from a silent
            # prefix. Preflight rejects oversized files before this point.
            text = safe_read_text(main_skill, max_bytes=None, force=True) or ""
            frontmatter_text, fm_error = extract_frontmatter(text)
            result["frontmatter_error"] = fm_error
            if frontmatter_text is not None:
                frontmatter = parse_frontmatter(frontmatter_text)
                frontmatter_summary = public_frontmatter_summary(frontmatter, canonical)
                result["frontmatter"] = frontmatter_summary
                result["frontmatter_validation_findings"] = validate_frontmatter(frontmatter, canonical)
                if frontmatter.get("_parse_unsupported"):
                    result["unverified_manifests"].append("SKILL.md")
                name = frontmatter.get("name")
                declared_skill_name = frontmatter_summary["validated_name"]
                layout_skill_name = validated_frontmatter_name(frontmatter, canonical)
                try:
                    directory_name = root.resolve().name
                except OSError:
                    directory_name = root.name
                if isinstance(name, str) and name.strip() and zip_without_top_level_folder and not profile.requires_zip_top_level_folder and profile.directory_name_mode != "none":
                    result["frontmatter_validation_findings"].append(finding("warning", "zip_missing_top_level_skill_folder", "zip has no top-level folder named after the skill; package the skill directory as the archive root so it unpacks into a folder matching the skill name", expected=frontmatter_summary["validated_name"]))
                if not (zip_without_top_level_folder and not profile.requires_zip_top_level_folder):
                    result["frontmatter_validation_findings"].extend(target_layout_findings(
                        profile,
                        is_zip=temp_dir is not None,
                        root_relative=result["detected_root_relative"],
                        directory_name=directory_name,
                        skill_name=layout_skill_name,
                        outside_root_findings=result["outside_root_findings"],
                    ))
                result["name_valid_hyphen_case"] = isinstance(name, str) and re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name.strip()) is not None
                result["description_length"] = frontmatter_summary["description_length"]
            else:
                result["frontmatter_validation_findings"] = [finding("error", "frontmatter_missing_or_invalid", fm_error or "frontmatter missing or invalid")]
            graph = collect_resource_graph(root, main_skill, limits)
            result["resource_graph"] = graph.as_dict()
            resource_refs = graph.projection()
            declarations = source_only_resources(
                "\n".join(match.group() for match in SOURCE_ONLY_DECLARATION_PATTERN.finditer(strip_code_fences(text))),
                root, declared_skill_name=declared_skill_name,
            )
            resource_refs["source_only"] = declarations["source_only"]
            resource_refs["unsafe"] = sorted(set(resource_refs["unsafe"] + declarations["unsafe"]))
            resource_refs["unsafe_reasons"].update(declarations["unsafe_reasons"])
            result["resource_references"] = resource_refs
        else:
            result["frontmatter_error"] = "no root SKILL.md found"
            result["frontmatter_validation_findings"] = [finding("error", "frontmatter_unavailable", "frontmatter cannot be inspected because root SKILL.md is missing")]
            result["resource_references"] = resource_refs
        platform_metadata_findings = validate_agent_metadata(
            root,
            None,
            canonical,
            declared_skill_name=declared_skill_name,
        )
        result["platform_metadata_findings"] = platform_metadata_findings
        result["agent_metadata_findings"] = platform_metadata_findings
        if any(item.get("code") == "openai_metadata_yaml_unsupported" for item in platform_metadata_findings):
            result["unverified_manifests"].append("agents/openai.yaml")
        result["unverified_manifests"] = sorted(set(result["unverified_manifests"]))
        result["manifest_verification_complete"] = not result["unverified_manifests"]
        result["structural_findings"] = structural_findings(len(skill_files), main_skill.exists(), resource_refs)
        if result.get("resource_graph", {}).get("complete") is False:
            result["structural_findings"].append(finding(
                "error", "resource_graph_incomplete", "reachable local dependency inspection is incomplete",
                unassessed=result["resource_graph"]["unassessed"],
            ))
        result["orphaned_resource_candidates"] = find_orphaned_resource_candidates(root_files, root, resource_refs)
        return finalize_result(result)
    finally:
        if temp_dir is not None:
            temp_dir.cleanup()


def iter_findings(data: Any) -> Iterable[Dict[str, Any]]:
    """Yield findings only from inspector-owned severity-bearing sections.

    Dedupe by object identity so a finding surfaced under two aliased keys
    (e.g. platform_metadata_findings and agent_metadata_findings) is counted
    once. Parsed frontmatter and other untrusted package data are never finding
    sources, even if they contain dictionaries named ``severity`` and ``code``.
    """
    if not isinstance(data, dict):
        return
    seen: Set[int] = set()
    for key in FINDING_SECTION_KEYS:
        if key in data:
            yield from _iter_findings(data[key], seen)


def _iter_findings(data: Any, seen: Set[int]) -> Iterable[Dict[str, Any]]:
    if isinstance(data, dict):
        if data.get("severity") in {"error", "warning", "info"} and data.get("code") in FINDING_CODE_SET:
            if id(data) not in seen:
                seen.add(id(data))
                yield data
            return
        for value in data.values():
            yield from _iter_findings(value, seen)
    elif isinstance(data, list):
        for item in data:
            yield from _iter_findings(item, seen)


def has_error_findings(data: Dict[str, Any]) -> bool:
    return any(item.get("severity") == "error" for item in iter_findings(data))


def summarize_findings(data: Dict[str, Any]) -> Dict[str, Any]:
    findings = list(iter_findings(data))
    error_count = sum(1 for item in findings if item.get("severity") == "error")
    warning_count = sum(1 for item in findings if item.get("severity") == "warning")
    strict_pass = (
        bool(data.get("input_exists"))
        and not data.get("unpack_error")
        and data.get("coverage_complete") is True
        and data.get("manifest_verification_complete") is True
        and error_count == 0
    )
    return {
        "status": "pass" if strict_pass else "fail",
        "strict_pass": strict_pass,
        "error_count": error_count,
        "warning_count": warning_count,
        "finding_count": len(findings),
        "finding_codes": sorted({str(item.get("code")) for item in findings if item.get("code")}),
    }


def finalize_result(data: Dict[str, Any]) -> Dict[str, Any]:
    # Keep this top-level field for CI and release-gate integrations that read
    # summary.status or summary.strict_pass from JSON output.
    presentation = dict(data, summary=summarize_findings(data))
    return sanitize_public_output(presentation, RedactionContext())


def render_markdown(data: Dict[str, Any]) -> str:
    data = sanitize_public_output(data, RedactionContext())
    lines: List[str] = []
    lines.append("# Skill Package Inspection")
    lines.append("")
    lines.append(f"- Input: `{data.get('input')}`")
    lines.append(f"- Input type: `{data.get('input_type')}`")
    if "zip_bytes" in data:
        lines.append(f"- ZIP size: {data['zip_bytes']} bytes")
    if data.get("unpack_error"):
        lines.append(f"- Error: {data['unpack_error']}")
    if data.get("detected_root"):
        lines.append(f"- Detected root: `{data.get('detected_root')}`")
    if data.get("detected_root_relative") is not None:
        lines.append(f"- Detected root relative to input: `{data.get('detected_root_relative')}`")
    lines.append(f"- Target requested: `{data.get('requested_target', data.get('target', 'portable'))}`")
    lines.append(f"- Target canonical profile: `{data.get('canonical_target', data.get('target', 'portable'))}`")
    if data.get("target_alias_used"):
        lines.append(f"- Target alias notice: {data.get('target_deprecation_note')}")
    lines.append(f"- Safety scan coverage complete: `{data.get('coverage_complete') is True}`")
    if data.get("unscanned_paths"):
        lines.append(f"- Unscanned paths: {', '.join(data.get('unscanned_paths', []))}")
    lines.append(f"- Critical manifest verification complete: `{data.get('manifest_verification_complete') is True}`")
    if data.get("unverified_manifests"):
        lines.append(f"- Unverified manifests: {', '.join(data.get('unverified_manifests', []))}")
    if data.get("effective_limits"):
        active = data["effective_limits"]
        lines.append(f"- Effective limits: zip members {active.get('max_zip_members')}, directory files {active.get('max_directory_files')}, max read bytes {active.get('max_read_bytes')}")
    if "skill_md_count" in data:
        lines.append(f"- SKILL.md count: {data.get('skill_md_count')}")
        lines.append(f"- SKILL.md files: {', '.join(data.get('skill_md_files', [])) or 'none'}")
    size = data.get("size_summary", {})
    if size:
        lines.append(f"- Files: {size.get('file_count', 0)}")
        lines.append(f"- Uncompressed bytes: {size.get('total_bytes_uncompressed', 0)}")
    lines.append("")
    findings = list(iter_findings(data))
    if findings:
        lines.append("## Findings")
        for item in findings:
            file_text = f" `{item['file']}`" if item.get("file") else ""
            lines.append(f"- **{item.get('severity')}** `{item.get('code')}`{file_text}: {item.get('message')}")
        lines.append("")
    fm = data.get("frontmatter")
    if fm:
        lines.append("## Frontmatter")
        lines.append(f"- validated name: `{fm.get('validated_name')}`")
        lines.append(f"- description length: {fm.get('description_length')}")
        lines.append(f"- parsed values redacted: `{fm.get('redacted') is True}`")
        lines.append(f"- name valid hyphen-case: {data.get('name_valid_hyphen_case')}")
        lines.append("")
    if data.get("outside_root_findings"):
        lines.append("## Files Outside Detected Skill Root")
        for item in data["outside_root_findings"]:
            lines.append(f"- `{item['file']}`: {item['message']}")
        lines.append("")
    if data.get("secret_risk_findings"):
        lines.append("## Secret Risk Findings")
        for item in data["secret_risk_findings"]:
            lines.append(f"- **{item.get('severity', 'warning')}** `{item['file']}`: {item.get('risk', item.get('message'))}")
        lines.append(f"- Note: {data.get('secret_scan_note')}")
        lines.append("")
    refs = data.get("resource_references", {})
    if refs:
        lines.append("## Resource References")
        lines.append(f"- Existing: {', '.join(refs.get('existing', [])) or 'none'}")
        lines.append(f"- Missing: {', '.join(refs.get('missing', [])) or 'none'}")
        lines.append(f"- Unsafe: {', '.join(refs.get('unsafe', [])) or 'none'}")
        lines.append("")
    if data.get("orphaned_resource_candidates"):
        lines.append("## Orphaned Resource Candidates")
        for item in data["orphaned_resource_candidates"]:
            lines.append(f"- `{item}`")
        lines.append("")
    if data.get("tree"):
        lines.append("## Tree")
        for item in data.get("tree", []):
            lines.append(f"- `{item}`")
    summary = data.get("summary") or summarize_findings(data)
    if lines and lines[-1] != "":
        lines.append("")
    lines.append(
        f"Status: {summary.get('status')} / Findings: "
        f"{summary.get('error_count', 0)} errors, {summary.get('warning_count', 0)} warnings."
    )
    return "\n".join(lines)


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = PublicArgumentParser(description="Inspect an Agent Skill folder or zip archive.")
    parser.add_argument("path", help="path to an Agent Skill folder or skill .zip")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of markdown")
    parser.add_argument("--strict", action="store_true", help="exit with code 2 when validation findings contain errors")
    parser.add_argument("--target", choices=sorted(TARGETS), default="portable", help="validation profile: portable (default) or openai")
    parser.add_argument("--tree-limit", type=positive_int, default=MAX_DEFAULT_TREE_FILES, help="maximum tree entries to include")
    parser.add_argument("--max-zip-members", type=positive_int, default=MAX_ZIP_MEMBERS, help="maximum ZIP members allowed before reporting an unsafe archive")
    parser.add_argument("--max-zip-uncompressed-bytes", type=positive_int, default=MAX_ZIP_UNCOMPRESSED_BYTES, help="maximum total uncompressed ZIP bytes allowed")
    parser.add_argument("--max-zip-member-bytes", type=positive_int, default=MAX_ZIP_MEMBER_BYTES, help="maximum uncompressed size for any single ZIP member")
    parser.add_argument("--max-directory-files", type=positive_int, default=MAX_DIRECTORY_FILES, help="maximum files allowed in a direct folder input")
    parser.add_argument("--max-directory-entries", type=positive_int, default=MAX_DIRECTORY_ENTRIES, help="maximum total directory entries allowed in a direct folder input")
    parser.add_argument("--max-directory-depth", type=positive_int, default=MAX_DIRECTORY_DEPTH, help="maximum directory nesting depth allowed in a direct folder input")
    parser.add_argument("--max-directory-entries-per-directory", type=positive_int, default=MAX_DIRECTORY_ENTRIES_PER_DIRECTORY, help="maximum entries allowed in any one direct-input directory")
    parser.add_argument("--max-directory-total-bytes", type=positive_int, default=MAX_DIRECTORY_TOTAL_BYTES, help="maximum total bytes allowed in a direct folder input")
    parser.add_argument("--max-directory-file-bytes", type=positive_int, default=MAX_DIRECTORY_FILE_BYTES, help="maximum size for any single file in a direct folder input")
    parser.add_argument("--max-compression-ratio", type=positive_float, default=MAX_COMPRESSION_RATIO, help="maximum ZIP member compression ratio before reporting a suspicious archive")
    parser.add_argument("--max-input-zip-bytes", type=positive_int, default=MAX_INSPECTOR_INPUT_ZIP_BYTES, help="pre-open ZIP input safety limit; separate from documented host upload limits")
    parser.add_argument("--max-read-bytes", type=positive_int, default=MAX_READ_BYTES, help="maximum bytes to read from any text-like file")
    parser.add_argument("--max-safety-scan-bytes", type=positive_int, default=None, help="explicit exploratory cap for each eligible secret/dangerous-command scan; makes coverage incomplete when a file is truncated")
    args = parser.parse_args(list(argv) if argv is not None else None)
    limits = InspectionLimits(
        max_zip_members=args.max_zip_members,
        max_zip_uncompressed_bytes=args.max_zip_uncompressed_bytes,
        max_zip_member_bytes=args.max_zip_member_bytes,
        max_directory_files=args.max_directory_files,
        max_directory_entries=args.max_directory_entries,
        max_directory_depth=args.max_directory_depth,
        max_directory_entries_per_directory=args.max_directory_entries_per_directory,
        max_directory_total_bytes=args.max_directory_total_bytes,
        max_directory_file_bytes=args.max_directory_file_bytes,
        max_compression_ratio=args.max_compression_ratio,
        max_input_zip_bytes=args.max_input_zip_bytes,
        max_read_bytes=args.max_read_bytes,
        max_safety_scan_bytes=args.max_safety_scan_bytes,
    )
    input_path = Path(args.path).expanduser()
    data = inspect(input_path, tree_limit=args.tree_limit, limits=limits, target=args.target)
    if args.json:
        print(json.dumps(data, indent=2, sort_keys=True, allow_nan=False))
    else:
        print(render_markdown(data))
    if not data.get("input_exists"):
        return 1
    if data.get("unpack_error"):
        if args.strict and has_error_findings(data):
            return 2
        return 1
    if args.strict and (
        has_error_findings(data)
        or data.get("coverage_complete") is not True
        or data.get("manifest_verification_complete") is not True
    ):
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
