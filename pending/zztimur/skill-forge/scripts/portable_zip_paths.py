"""Portable ZIP member-path policy shared by inspection and packaging.

ZIP names are not portable filesystem identities by default: a path that is
distinct on one host can overwrite another member on a case-insensitive,
Unicode-normalizing, or Windows filesystem.  This module is dependency-free so
both the inspector and package verifier can reject the same archive members
before extraction or release verification.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Iterable, List, Optional, Tuple


WINDOWS_RESERVED_BASENAMES = {
    "con", "prn", "aux", "nul",
    *(f"com{number}" for number in range(1, 10)),
    *(f"lpt{number}" for number in range(1, 10)),
}

WINDOWS_INVALID_CHARACTERS = frozenset('<>"|?*')

# Keep the generic policy stricter than common host-specific maximums.  The
# component limits cover both byte-oriented and UTF-16-oriented filesystems;
# the relative-path limit leaves room for an extraction destination prefix on
# Windows hosts without pretending to model every possible absolute path.
MAX_PORTABLE_COMPONENT_UTF8_BYTES = 255
MAX_PORTABLE_COMPONENT_UTF16_UNITS = 255
MAX_PORTABLE_RELATIVE_PATH_UTF16_UNITS = 240

IDENTITY_EXACT = "exact"
IDENTITY_CASEFOLD = "casefold"
IDENTITY_NFC = "nfc"
IDENTITY_NFC_CASEFOLD = "nfc_casefold"


@dataclass(frozen=True)
class PortableZipMember:
    """One archive member after path normalization for policy comparison."""

    raw_name: str
    is_directory: bool
    normalized_path: Optional[str]


@dataclass(frozen=True)
class PortableZipPathIssue:
    """A machine-readable path-policy violation."""

    code: str
    message: str
    raw_name: str
    normalized_path: Optional[str] = None
    conflicts_with: Optional[str] = None
    identity_kind: Optional[str] = None
    path_rule: Optional[str] = None
    component: Optional[str] = None
    utf8_bytes: Optional[int] = None
    utf16_units: Optional[int] = None
    limit: Optional[int] = None


def _contains_unsafe_control(text: str) -> bool:
    return any(ord(char) < 32 or 0x7F <= ord(char) <= 0x9F for char in text)


def _utf8_length(text: str) -> int:
    """Return a deterministic byte count even for a lone surrogate."""
    return len(text.encode("utf-8", errors="surrogatepass"))


def _utf16_length(text: str) -> int:
    """Return UTF-16 code units without adding a byte-order mark."""
    return len(text.encode("utf-16-le", errors="surrogatepass")) // 2


def _identity_values(path: str) -> Tuple[str, str, str, str]:
    normalized_nfc = unicodedata.normalize("NFC", path)
    return (
        path,
        path.casefold(),
        normalized_nfc,
        normalized_nfc.casefold(),
    )


def normalize_portable_path(name: str, is_directory: bool = False) -> Tuple[PortableZipMember, Optional[PortableZipPathIssue]]:
    """Normalize and validate one relative path for portable materialization."""
    member = PortableZipMember(name, is_directory, None)
    if not name:
        return member, PortableZipPathIssue(
            "zip_unsafe_member_path", "zip member path is empty", name,
            path_rule="unsafe_path",
        )
    if _contains_unsafe_control(name):
        return member, PortableZipPathIssue(
            "zip_control_character_member",
            "zip member path contains an unsafe control character",
            name,
            path_rule="control_character",
        )
    if "\\" in name:
        return member, PortableZipPathIssue(
            "zip_nonportable_separator_member",
            "zip member path uses a backslash separator, which is not portable",
            name,
            path_rule="nonportable_separator",
        )
    if name.startswith("/") or re.match(r"^[A-Za-z]:", name):
        return member, PortableZipPathIssue(
            "zip_unsafe_member_path", "zip member path is absolute", name,
            path_rule="unsafe_path",
        )

    parts: List[str] = []
    for part in PurePosixPath(name).parts:
        if part in {"", "."}:
            continue
        if part == "..":
            return member, PortableZipPathIssue(
                "zip_unsafe_member_path", "zip member path contains traversal", name,
                path_rule="unsafe_path",
            )
        if _contains_unsafe_control(part):
            return member, PortableZipPathIssue(
                "zip_control_character_member",
                "zip member path contains an unsafe control character",
                name,
                path_rule="control_character",
            )
        if ":" in part:
            return member, PortableZipPathIssue(
                "zip_windows_ads_member",
                "zip member path contains a Windows alternate-stream colon",
                name,
                path_rule="windows_ads",
            )
        invalid_character = next(
            (character for character in part if character in WINDOWS_INVALID_CHARACTERS),
            None,
        )
        if invalid_character is not None:
            return member, PortableZipPathIssue(
                "zip_windows_invalid_character_member",
                "zip member path contains a character that Windows does not allow in file names",
                name,
                path_rule="windows_invalid_character",
                component=part,
            )
        if part.endswith((" ", ".")):
            return member, PortableZipPathIssue(
                "zip_windows_trailing_dot_space_member",
                "zip member path segment ends with a space or period, which Windows ignores",
                name,
                path_rule="windows_trailing_dot_space",
            )
        basename = part.split(".", 1)[0].casefold()
        if basename in WINDOWS_RESERVED_BASENAMES:
            return member, PortableZipPathIssue(
                "zip_windows_reserved_name_member",
                "zip member path uses a Windows reserved device basename",
                name,
                path_rule="windows_reserved_name",
            )
        component_utf8_length = _utf8_length(part)
        component_utf16_length = _utf16_length(part)
        if component_utf8_length > MAX_PORTABLE_COMPONENT_UTF8_BYTES:
            return member, PortableZipPathIssue(
                "zip_path_component_too_long",
                "zip member path segment exceeds the portable UTF-8 byte limit",
                name,
                path_rule="component_too_long",
                component=part,
                utf8_bytes=component_utf8_length,
                utf16_units=component_utf16_length,
                limit=MAX_PORTABLE_COMPONENT_UTF8_BYTES,
            )
        if component_utf16_length > MAX_PORTABLE_COMPONENT_UTF16_UNITS:
            return member, PortableZipPathIssue(
                "zip_path_component_too_long",
                "zip member path segment exceeds the portable UTF-16 code-unit limit",
                name,
                path_rule="component_too_long",
                component=part,
                utf8_bytes=component_utf8_length,
                utf16_units=component_utf16_length,
                limit=MAX_PORTABLE_COMPONENT_UTF16_UNITS,
            )
        parts.append(part)

    if not parts:
        return member, PortableZipPathIssue(
            "zip_unsafe_member_path", "zip member path normalizes to empty", name,
            path_rule="unsafe_path",
        )
    normalized = "/".join(parts)
    path_utf16_length = _utf16_length(normalized)
    if path_utf16_length > MAX_PORTABLE_RELATIVE_PATH_UTF16_UNITS:
        return member, PortableZipPathIssue(
            "zip_path_too_long",
            "zip member relative path exceeds the portable UTF-16 code-unit limit",
            name,
            normalized_path=normalized,
            path_rule="path_too_long",
            utf8_bytes=_utf8_length(normalized),
            utf16_units=path_utf16_length,
            limit=MAX_PORTABLE_RELATIVE_PATH_UTF16_UNITS,
        )
    return PortableZipMember(name, is_directory, normalized), None


def normalize_member_path(name: str, is_directory: bool = False) -> Tuple[PortableZipMember, Optional[PortableZipPathIssue]]:
    """Compatibility wrapper for callers validating one ZIP member path."""
    return normalize_portable_path(name, is_directory)


def validate_portable_path_records(records_to_validate: Iterable[Tuple[str, bool]]) -> Tuple[List[PortableZipMember], List[PortableZipPathIssue]]:
    """Return normalized path records and every portable-identity violation.

    Collision precedence is intentional: exact identity, case-only identity,
    NFC identity, then NFC-plus-casefold identity. This reports one precise
    collision class for each later record while preserving deterministic order.

    ``path_rule`` is the neutral policy key that direct-folder consumers should
    route on. Existing ZIP finding codes remain on each issue so the compatibility
    wrapper can preserve its public result contract.
    """
    records: List[PortableZipMember] = []
    issues: List[PortableZipPathIssue] = []
    valid: List[PortableZipMember] = []
    for name, is_directory in records_to_validate:
        member, issue = normalize_portable_path(name, is_directory)
        records.append(member)
        if issue is not None:
            issues.append(issue)
        else:
            valid.append(member)

    seen_exact: dict[str, PortableZipMember] = {}
    seen_casefold: dict[str, PortableZipMember] = {}
    seen_nfc: dict[str, PortableZipMember] = {}
    seen_nfc_casefold: dict[str, PortableZipMember] = {}
    for member in valid:
        assert member.normalized_path is not None
        normalized = member.normalized_path
        (
            normalized_exact,
            normalized_casefold,
            normalized_nfc,
            normalized_nfc_casefold,
        ) = _identity_values(normalized)
        if normalized in seen_exact:
            issues.append(PortableZipPathIssue(
                "zip_duplicate_member",
                "zip contains duplicate member path",
                member.raw_name,
                normalized,
                seen_exact[normalized].normalized_path,
                identity_kind=IDENTITY_EXACT,
                path_rule="duplicate",
            ))
        elif normalized_casefold in seen_casefold:
            issues.append(PortableZipPathIssue(
                "zip_case_collision_member",
                "zip contains members that collide case-insensitively",
                member.raw_name,
                normalized,
                seen_casefold[normalized_casefold].normalized_path,
                identity_kind=IDENTITY_CASEFOLD,
                path_rule="portable_identity_collision",
            ))
        elif normalized_nfc in seen_nfc:
            issues.append(PortableZipPathIssue(
                "zip_unicode_normalization_collision_member",
                "zip contains members that collide after Unicode NFC normalization",
                member.raw_name,
                normalized,
                seen_nfc[normalized_nfc].normalized_path,
                identity_kind=IDENTITY_NFC,
                path_rule="portable_identity_collision",
            ))
        elif normalized_nfc_casefold in seen_nfc_casefold:
            issues.append(PortableZipPathIssue(
                "zip_unicode_casefold_collision_member",
                "zip contains members that collide after Unicode NFC normalization and case-folding",
                member.raw_name,
                normalized,
                seen_nfc_casefold[normalized_nfc_casefold].normalized_path,
                identity_kind=IDENTITY_NFC_CASEFOLD,
                path_rule="portable_identity_collision",
            ))
        seen_exact.setdefault(normalized_exact, member)
        seen_casefold.setdefault(normalized_casefold, member)
        seen_nfc.setdefault(normalized_nfc, member)
        seen_nfc_casefold.setdefault(normalized_nfc_casefold, member)

    files_by_exact: dict[str, PortableZipMember] = {}
    files_by_casefold: dict[str, PortableZipMember] = {}
    files_by_nfc: dict[str, PortableZipMember] = {}
    files_by_nfc_casefold: dict[str, PortableZipMember] = {}
    for member in valid:
        if member.is_directory or member.normalized_path is None:
            continue
        exact, casefold, nfc, nfc_casefold = _identity_values(member.normalized_path)
        files_by_exact.setdefault(exact, member)
        files_by_casefold.setdefault(casefold, member)
        files_by_nfc.setdefault(nfc, member)
        files_by_nfc_casefold.setdefault(nfc_casefold, member)

    for member in valid:
        assert member.normalized_path is not None
        parts = member.normalized_path.split("/")
        for index in range(1, len(parts)):
            prefix = "/".join(parts[:index])
            exact, casefold, nfc, nfc_casefold = _identity_values(prefix)
            identity_kind: Optional[str] = None
            file_member = files_by_exact.get(exact)
            if file_member is not None:
                identity_kind = IDENTITY_EXACT
            else:
                file_member = files_by_casefold.get(casefold)
                if file_member is not None:
                    identity_kind = IDENTITY_CASEFOLD
                else:
                    file_member = files_by_nfc.get(nfc)
                    if file_member is not None:
                        identity_kind = IDENTITY_NFC
                    else:
                        file_member = files_by_nfc_casefold.get(nfc_casefold)
                        if file_member is not None:
                            identity_kind = IDENTITY_NFC_CASEFOLD
            if file_member is not None and file_member.raw_name != member.raw_name:
                issues.append(PortableZipPathIssue(
                    "zip_file_directory_prefix_conflict_member",
                    "zip contains a file member whose portable identity is also a parent path of another member",
                    member.raw_name,
                    member.normalized_path,
                    file_member.normalized_path,
                    identity_kind=identity_kind,
                    path_rule="file_directory_prefix_conflict",
                ))
                break
    return records, issues


def validate_portable_zip_members(members: Iterable[Tuple[str, bool]]) -> Tuple[List[PortableZipMember], List[PortableZipPathIssue]]:
    """Compatibility wrapper for portable ZIP member-path validation."""
    return validate_portable_path_records(members)
