#!/usr/bin/env python3
"""Validate the dependency-free audit and release-report contract.

This verifies that the canonical JSON contract, checklists, report template,
and example report keep their gate IDs, enums, caps, routing rules, and
evidence boundaries mechanically aligned.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path, PurePath
from typing import Any, List, Mapping, Optional, Sequence

from package_skill import FORBIDDEN_RUNTIME_PATHS
from runtime_manifest import SKILL_FORGE_RUNTIME_SELECTORS, runtime_boundary_issues


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = REPO_ROOT / "references" / "audit-contract.json"
CHECKLIST_PATH = REPO_ROOT / "references" / "release-gate-checklist.md"
TEMPLATE_PATH = REPO_ROOT / "references" / "report-template.md"
EXAMPLE_PATH = REPO_ROOT / "references" / "example-report.md"
RUBRIC_PATH = REPO_ROOT / "references" / "evaluation-rubric.md"
PRESSURE_PATH = REPO_ROOT / "references" / "pressure-test-suite.md"
ROUTING_PATH = REPO_ROOT / "references" / "input-routing.md"
MATRIX_PATH = REPO_ROOT / "references" / "artifact-and-mode-matrix.md"
PLATFORM_PATH = REPO_ROOT / "references" / "platform-compatibility.md"
VALIDATOR_EVIDENCE_PATH = REPO_ROOT / "references" / "validator-evidence.md"
INSPECTOR_SCHEMA_PATH = REPO_ROOT / "references" / "inspector-output-schema.md"
INSPECTOR_PATH = REPO_ROOT / "scripts" / "inspect_skill_package.py"
SKILL_PATH = REPO_ROOT / "SKILL.md"
README_PATH = REPO_ROOT / "README.md"
AUDIT_CHECKLIST_PATH = REPO_ROOT / "references" / "audit-checklist.md"
OPENAI_METADATA_PATH = REPO_ROOT / "agents" / "openai.yaml"
SOURCE_ONLY_DECLARATION_PATTERN = re.compile(
    r"<!--\s*skill-forge:source-only\s+(.+?)\s*-->",
    re.IGNORECASE | re.DOTALL,
)

EXPECTED_RESULTS = ["Pass", "Fail", "Partial", "Not Assessed", "Not Applicable"]
EXPECTED_EVIDENCE = ["Verified", "Inferred", "Unverified"]
EXPECTED_PROFILES = ["portable", "openai"]
EXPECTED_VALIDATOR_OUTCOMES = ["Pass", "Artifact Fail", "Unavailable", "Execution Error", "Not Applicable"]
EXPECTED_COMPATIBILITY_RESULTS = ["Compatible", "Incompatible", "Unverified", "Not Applicable"]
EXPECTED_QUALITY_POLICY_RESULTS = EXPECTED_RESULTS
EXPECTED_ARTIFACT_ROLES = [
    "Pasted draft",
    "Release ZIP",
    "Installed runtime",
    "Mutable source checkout",
    "General repository",
    "Portfolio or multi-Skill input",
]
EXPECTED_ARTIFACT_ROLE_CONTRACTS = {
    "Pasted draft": {
        "new_release_pass_allowed": False,
        "release_evidence_role": "design_evidence_only",
        "required_release_evidence": [],
    },
    "Release ZIP": {
        "new_release_pass_allowed": True,
        "release_evidence_role": "exact_artifact",
        "required_release_evidence": ["exact_release_zip_inspection"],
    },
    "Installed runtime": {
        "new_release_pass_allowed": False,
        "release_evidence_role": "installed_state_only",
        "required_release_evidence": [],
    },
    "Mutable source checkout": {
        "new_release_pass_allowed": True,
        "release_evidence_role": "packaging_source",
        "required_release_evidence": ["committed_release_archive", "explicit_packaging_authority"],
    },
    "General repository": {
        "new_release_pass_allowed": False,
        "release_evidence_role": "adjacent_review_only",
        "required_release_evidence": [],
    },
    "Portfolio or multi-Skill input": {
        "new_release_pass_allowed": False,
        "release_evidence_role": "independent_member_results_only",
        "required_release_evidence": [],
    },
}
EXPECTED_PRESSURE_METHODS = ["Static simulation", "Synthetic execution", "Live host observation"]
EXPECTED_OBSERVATION_METHODS = {
    "Instruction semantics": ["Static simulation", "Synthetic execution", "Live host observation"],
    "Artifact execution": ["Synthetic execution", "Live host observation"],
    "Live host behavior": ["Live host observation"],
}
EXPECTED_PRESSURE_RESULT_FIELDS = [
    "test",
    "input",
    "expected_behavior",
    "observation_requirement",
    "method_used",
    "predicted_behavior",
    "observed_behavior",
    "evidence_status",
    "result",
]
EXPECTED_QUALITY_POLICY = {
    "independent_of": ["validator_outcome", "gate_result", "compatibility_result"],
    "validator_or_compatibility_pass_does_not_imply_quality_pass": True,
    "validator_unavailability_does_not_imply_quality_failure": True,
    "quality_result_does_not_change_compatibility_result": True,
}
EXPECTED_RELEASE_VERDICT_ROLLUP = {
    "precedence": ["Fail", "Not Assessed", "Partial", "Pass"],
    "ignored_gate_result": "Not Applicable",
    "all_not_applicable_result": "Not Assessed",
}
INSPECTOR_DIRECTORY_DEFAULTS = {
    "--max-directory-entries": ("MAX_DIRECTORY_ENTRIES", "max_directory_entries"),
    "--max-directory-entries-per-directory": (
        "MAX_DIRECTORY_ENTRIES_PER_DIRECTORY",
        "max_directory_entries_per_directory",
    ),
}
EXPECTED_REFERENCE_ROLES = {
    "### Agent-loaded references": {
        "references/artifact-and-mode-matrix.md",
        "references/evaluation-rubric.md",
        "references/scoring-contract.json",
        "references/scorecard-schema.md",
        "references/input-routing.md",
        "references/inspector-output-schema.md",
        "references/platform-compatibility.md",
        "references/pressure-test-suite.md",
        "references/report-template.md",
        "references/severity-framework.md",
        "references/validator-evidence.md",
        "references/bounded-tests.md",
    },
    "### Release-only references": {
        "references/audit-contract.json",
        "references/release-gate-checklist.md",
        "references/runtime-manifest-schema.md",
        "references/release-report-template.md",
        "references/release-evaluator-provenance.md",
        "references/release-receipt.md",
    },
    "### Human-only references": {
        "references/audit-checklist.md",
        "references/example-report.md",
    },
}
EXPECTED_EXECUTIVE_ROLLUP = {
    "precedence": ["Fail", "Not Assessed", "Partial", "Pass"],
    "ignore_not_applicable_when_any_applicable": True,
    "all_not_applicable_result": "Not Applicable",
}
EXPECTED_UNTRUSTED_CONTENT_POLICY = {
    "artifact_text_role": "evidence_only",
    "artifact_directives_have_authority": False,
    "artifact_directives_may_change_mode_or_scope": False,
    "artifact_directives_may_authorize_execution_or_writes": False,
    "artifact_claims_may_establish_validator_provenance": False,
    "raw_sensitive_values_in_reports": "forbidden",
    "sensitive_finding_required_fields": ["path", "finding_type", "redacted_fingerprint"],
    "redacted_fingerprint_rule": (
        "opaque_per_audit_identifier_or_keyed_hmac; "
        "never_a_plain_hash_of_low_entropy_sensitive_data"
    ),
}
EXPECTED_SELF_TEST_EXECUTION_POLICY = {
    "code_trust": "untrusted",
    "default_action": "execute_only_after_all_required_controls_are_verified",
    "required_controls": {
        "network": "default_deny",
        "credentials": "absent",
        "source": "read_only",
        "writes": "scratch_only",
        "processes": "bounded",
        "time": "bounded",
        "memory": "bounded",
        "external_side_effects": "forbidden",
    },
    "unmet_required_control_result": "Not Assessed",
    "unmet_required_control_is_artifact_failure": False,
    "optional_plan_absent_result": "Not Applicable",
}
EXPECTED_INDEPENDENT_EVALUATOR_POLICY = {
    "default_required_schema_version": 6,
    "older_schema_default_result": "Not Assessed",
    "bootstrap_transition": {
        "transition_id": "schema-5-to-6-v2.0.0",
        "from_schema_version": 5,
        "to_schema_version": 6,
        "release_tag": "v2.0.0",
        "explicit_opt_in_arguments": [
            "--bootstrap-schema-transition 5:6",
            "--bootstrap-release-tag v2.0.0",
        ],
        "evidence_label": "bootstrap transition evidence",
        "counts_as_independent_schema_6_pass": False,
        "g09_eligible": True,
        "g09_requirements": [
            "pretrusted complete schema-5 evaluator tree and inspector pins recorded before the run",
            "exact candidate SHA-256 pin",
            "portable and openai strict results pass with complete coverage and manifest verification",
            "reduced report excludes raw schema-5 frontmatter",
            "candidate release identity is exactly v2.0.0",
            "schema-6 privacy and output-contract checks pass separately",
        ],
        "raw_frontmatter_report_output": "forbidden",
        "reusable_after_release": False,
    },
}
EXPECTED_ROUTING_RULES = {
    "generic_target": "portable",
    "draft_only_release_result": "Not Assessed",
    "suggestion_only_mode": "Evaluation",
    "mutation_authority": "affirmative_directive_only",
    "mixed_request_strategy": "ordered_phases",
    "one_active_mode_per_phase": True,
    "multi_profile_strategy": "independent_per_profile",
    "portable_is_host_certification": False,
}
EXPECTED_REQUEST_ROUTING_CASES = [
    ("negated-fix-is-evaluation", "Audit this and explain how to fix it. Do not edit.", ["Evaluation"], False),
    ("quoted-fix-is-evaluation", "The old request said 'fix the parser'; audit the current version.", ["Evaluation"], False),
    ("affirmative-fix-is-repair", "Fix the parser.", ["Repair"], True),
    ("repair-then-release", "Fix these findings, then assess release readiness.", ["Repair", "Release gate"], True),
    ("validation-negates-edit", "Validate but do not edit.", ["Validation"], False),
    ("affirmative-improve-is-repair", "Improve this skill.", ["Repair"], True),
    ("audit-then-improve", "Audit and improve it.", ["Evaluation", "Repair"], True),
    ("suggest-improvements-is-evaluation", "Suggest improvements.", ["Evaluation"], False),
    ("how-to-improve-is-evaluation", "How can I improve it?", ["Evaluation"], False),
    ("improve-with-no-edit-is-evaluation", "Improve this skill, but do not edit files.", ["Evaluation"], False),
    ("quoted-improve-is-evaluation", "The old request said 'improve this skill'; audit the current version.", ["Evaluation"], False),
    ("improve-then-release", "Improve this skill, then assess release readiness.", ["Repair", "Release gate"], True),
]
EXPECTED_PROFILE_ROUTING_CASES = [
    ("generic-agent-skill", False, ["portable"], [], None),
]
SEVERITY_FINDING_SECTIONS = [
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
]

FINDING_CATALOG_START = "<!-- inspector-finding-catalog:start -->"
FINDING_CATALOG_END = "<!-- inspector-finding-catalog:end -->"
LIMITS_TABLE_START = "<!-- inspector-limits-table:start -->"
LIMITS_TABLE_END = "<!-- inspector-limits-table:end -->"
EFFECTIVE_LIMITS_START = "<!-- inspector-effective-limits:start -->"
EFFECTIVE_LIMITS_END = "<!-- inspector-effective-limits:end -->"
SEVERITY_SECTIONS_START = "<!-- inspector-severity-sections:start -->"
SEVERITY_SECTIONS_END = "<!-- inspector-severity-sections:end -->"
REPAIR_ROUTING_FIXTURES = [
    "Improve this skill.",
    "Apply these fixes.",
    "Fix the parser.",
    "Correct this frontmatter.",
    "Rewrite this workflow.",
    "Refactor this script.",
]


class DuplicateJsonKeyError(ValueError):
    """Raised when a canonical contract object repeats a key."""


def reject_duplicate_json_keys(pairs: List[tuple[str, Any]]) -> Mapping[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateJsonKeyError(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def load_contract_json(text: str) -> Any:
    return json.loads(text, object_pairs_hook=reject_duplicate_json_keys)


def repo_relative(path: PurePath, root: PurePath = REPO_ROOT) -> str:
    """Return one canonical POSIX identity below the repository root."""

    return path.relative_to(root).as_posix()


def read_text(path: Path, issues: List[str]) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        issues.append(f"cannot read {repo_relative(path)}: {exc}")
        return ""


def add_if_missing(text: str, token: str, location: Path, issues: List[str]) -> None:
    if token not in text:
        issues.append(f"{repo_relative(location)} is missing {token!r}")


def require_mapping(value: Any, label: str, issues: List[str]) -> Mapping[str, Any]:
    if isinstance(value, dict):
        return value
    issues.append(f"{label} must be an object")
    return {}


def require_strings(value: Any, label: str, issues: List[str]) -> List[str]:
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return list(value)
    issues.append(f"{label} must be a list of strings")
    return []


def expected_validator_gate_result(mapping: Mapping[str, Any], outcome: str, required: bool) -> Optional[str]:
    outcome_mapping = mapping.get(outcome)
    if not isinstance(outcome_mapping, dict):
        return None
    key = "required_gate_result" if required else "optional_gate_result"
    value = outcome_mapping.get(key)
    return value if isinstance(value, str) else None


def validate_target_contracts(root: Mapping[str, Any], issues: List[str]) -> None:
    contracts = require_mapping(root.get("target_contracts"), "target_contracts", issues)
    if list(contracts) != EXPECTED_PROFILES:
        issues.append(f"target_contracts must define exactly {EXPECTED_PROFILES!r} in order")
        return
    required_top_level = {
        "verification",
        "frontmatter",
        "name_rule",
        "description_rule",
        "root_layout",
        "product_upload_limit_bytes",
        "openai_metadata_requirement",
        "quality_recommendations",
    }
    for target, value in contracts.items():
        profile = require_mapping(value, f"target_contracts.{target}", issues)
        missing = sorted(required_top_level - set(profile))
        if missing:
            issues.append(f"target_contracts.{target} is missing fields: {', '.join(missing)}")
        verification = require_mapping(profile.get("verification"), f"target_contracts.{target}.verification", issues)
        if verification.get("verified_on") != "2026-07-15":
            issues.append(f"target_contracts.{target}.verification.verified_on must be 2026-07-15")
        if verification.get("source_type") not in {"skill_forge_policy", "host_documentation", "host_documentation_plus_skill_forge_policy"}:
            issues.append(f"target_contracts.{target}.verification.source_type is invalid")
        if verification.get("source_type") == "skill_forge_policy":
            if verification.get("source") is not None or verification.get("host_verified_rule_keys") != []:
                issues.append(f"target_contracts.{target} policy-only verification must not claim a host source")
        elif not isinstance(verification.get("source"), str) or not verification["source"].startswith("https://"):
            issues.append(f"target_contracts.{target}.verification.source must be an https URL")
        if not isinstance(verification.get("host_verified_rule_keys"), list) or not all(isinstance(item, str) and item for item in verification.get("host_verified_rule_keys", [])):
            issues.append(f"target_contracts.{target}.verification.host_verified_rule_keys must be a list of non-empty strings")

        frontmatter = require_mapping(profile.get("frontmatter"), f"target_contracts.{target}.frontmatter", issues)
        for key in ("required_fields", "optional_fields", "recommended_fields"):
            require_strings(frontmatter.get(key), f"target_contracts.{target}.frontmatter.{key}", issues)
        required_fields = frontmatter.get("required_fields")
        if isinstance(required_fields, list) and not all(isinstance(item, str) for item in required_fields):
            issues.append(f"target_contracts.{target}.frontmatter.required_fields must be strings")

        name_rule = require_mapping(profile.get("name_rule"), f"target_contracts.{target}.name_rule", issues)
        if not isinstance(name_rule.get("mode"), str) or not name_rule["mode"]:
            issues.append(f"target_contracts.{target}.name_rule.mode must be a non-empty string")
        if name_rule.get("max_length") is not None and (not isinstance(name_rule.get("max_length"), int) or name_rule["max_length"] <= 0):
            issues.append(f"target_contracts.{target}.name_rule.max_length must be a positive integer or null")
        require_strings(name_rule.get("reserved_terms"), f"target_contracts.{target}.name_rule.reserved_terms", issues)

        description_rule = require_mapping(profile.get("description_rule"), f"target_contracts.{target}.description_rule", issues)
        if not isinstance(description_rule.get("required"), bool):
            issues.append(f"target_contracts.{target}.description_rule.required must be a boolean")
        for key in ("max_length", "advisory_max_length", "listing_max_length"):
            value = description_rule.get(key)
            if value is not None and (not isinstance(value, int) or value <= 0):
                issues.append(f"target_contracts.{target}.description_rule.{key} must be a positive integer or null")

        root_layout = require_mapping(profile.get("root_layout"), f"target_contracts.{target}.root_layout", issues)
        if not isinstance(root_layout.get("directory_name_mode"), str) or not root_layout["directory_name_mode"]:
            issues.append(f"target_contracts.{target}.root_layout.directory_name_mode must be a non-empty string")
        if not isinstance(root_layout.get("zip_top_level_folder_required"), bool):
            issues.append(f"target_contracts.{target}.root_layout.zip_top_level_folder_required must be a boolean")
        upload_limit = profile.get("product_upload_limit_bytes")
        if upload_limit is not None and (not isinstance(upload_limit, int) or upload_limit <= 0):
            issues.append(f"target_contracts.{target}.product_upload_limit_bytes must be a positive integer or null")
        if profile.get("openai_metadata_requirement") not in {"conditional", "not_applicable"}:
            issues.append(f"target_contracts.{target}.openai_metadata_requirement must be conditional or not_applicable")
        recommendations = require_strings(profile.get("quality_recommendations"), f"target_contracts.{target}.quality_recommendations", issues)
        if not recommendations:
            issues.append(f"target_contracts.{target} must have at least one Skill Forge quality recommendation")


def validate_outcome_mapping_and_golden_cases(root: Mapping[str, Any], issues: List[str]) -> None:
    if root.get("validator_outcome_enums") != EXPECTED_VALIDATOR_OUTCOMES:
        issues.append(f"validator_outcome_enums must be exactly {EXPECTED_VALIDATOR_OUTCOMES!r}")
    if root.get("compatibility_result_enums") != EXPECTED_COMPATIBILITY_RESULTS:
        issues.append(f"compatibility_result_enums must be exactly {EXPECTED_COMPATIBILITY_RESULTS!r}")
    if root.get("quality_policy_result_enums") != EXPECTED_QUALITY_POLICY_RESULTS:
        issues.append(f"quality_policy_result_enums must be exactly {EXPECTED_QUALITY_POLICY_RESULTS!r}")

    mapping = require_mapping(root.get("validator_outcome_gate_results"), "validator_outcome_gate_results", issues)
    if list(mapping) != EXPECTED_VALIDATOR_OUTCOMES:
        issues.append("validator_outcome_gate_results must define every validator outcome in enum order")
    for outcome in EXPECTED_VALIDATOR_OUTCOMES:
        entry = require_mapping(mapping.get(outcome), f"validator_outcome_gate_results.{outcome}", issues)
        for key in ("optional_gate_result", "required_gate_result"):
            if entry.get(key) not in EXPECTED_RESULTS:
                issues.append(f"validator_outcome_gate_results.{outcome}.{key} must be a gate result")
        if entry.get("compatibility_result") not in EXPECTED_COMPATIBILITY_RESULTS:
            issues.append(f"validator_outcome_gate_results.{outcome}.compatibility_result must be a compatibility result")
        if not isinstance(entry.get("supports_validator_derived_artifact_defect"), bool):
            issues.append(f"validator_outcome_gate_results.{outcome}.supports_validator_derived_artifact_defect must be a boolean")
        if bool(entry.get("supports_validator_derived_artifact_defect")) != (outcome == "Artifact Fail"):
            issues.append("only Artifact Fail may support a validator-derived artifact defect")

    golden_cases = root.get("validator_outcome_golden_cases")
    expected_pairs = [
        (outcome, required)
        for outcome in EXPECTED_VALIDATOR_OUTCOMES
        for required in (False, True)
    ]
    actual_pairs = [
        (case.get("validator_outcome"), case.get("validator_required"))
        for case in golden_cases
        if isinstance(case, dict)
    ] if isinstance(golden_cases, list) else []
    case_ids = [case.get("id") for case in golden_cases if isinstance(case, dict)] if isinstance(golden_cases, list) else []
    if actual_pairs != expected_pairs or len(case_ids) != len(set(case_ids)):
        issues.append(
            "validator_outcome_golden_cases must cover all 10 ordered "
            "validator-outcome x required-status pairs exactly once"
        )
    else:
        for case in golden_cases:
            if not isinstance(case, dict):
                issues.append("validator_outcome_golden_cases entries must be objects")
                continue
            outcome = case.get("validator_outcome")
            required = case.get("validator_required")
            expected_gate = expected_validator_gate_result(mapping, outcome, required) if isinstance(outcome, str) and isinstance(required, bool) else None
            if expected_gate != case.get("expected_gate_result"):
                issues.append(f"validator golden case {case.get('id', '<unknown>')} does not match validator_outcome_gate_results")
            outcome_mapping = mapping.get(outcome) if isinstance(outcome, str) else None
            if not isinstance(outcome_mapping, dict) or outcome_mapping.get("compatibility_result") != case.get("expected_compatibility_result"):
                issues.append(f"validator golden case {case.get('id', '<unknown>')} does not match compatibility mapping")
        optional_execution_error = next(
            (
                case
                for case in golden_cases
                if case.get("validator_outcome") == "Execution Error"
                and case.get("validator_required") is False
            ),
            {},
        )
        if optional_execution_error.get("expected_gate_result") != "Not Assessed":
            issues.append("optional Execution Error must map to Not Assessed")

    target_contracts = root.get("target_contracts") if isinstance(root.get("target_contracts"), dict) else {}
    target_cases = root.get("target_contract_golden_cases")
    if not isinstance(target_cases, list) or {case.get("target") for case in target_cases if isinstance(case, dict)} != set(EXPECTED_PROFILES):
        issues.append("target_contract_golden_cases must cover every target profile")
    else:
        for case in target_cases:
            if not isinstance(case, dict):
                issues.append("target_contract_golden_cases entries must be objects")
                continue
            target = case.get("target")
            profile = target_contracts.get(target) if isinstance(target, str) else None
            if not isinstance(profile, dict):
                continue
            frontmatter = profile.get("frontmatter") if isinstance(profile.get("frontmatter"), dict) else {}
            name_rule = profile.get("name_rule") if isinstance(profile.get("name_rule"), dict) else {}
            description_rule = profile.get("description_rule") if isinstance(profile.get("description_rule"), dict) else {}
            root_layout = profile.get("root_layout") if isinstance(profile.get("root_layout"), dict) else {}
            expected_values = {
                "expected_required_fields": frontmatter.get("required_fields"),
                "expected_name_mode": name_rule.get("mode"),
                "expected_description_max_length": description_rule.get("max_length"),
                "expected_zip_top_level_folder_required": root_layout.get("zip_top_level_folder_required"),
                "expected_product_upload_limit_bytes": profile.get("product_upload_limit_bytes"),
            }
            for key, actual in expected_values.items():
                if case.get(key) != actual:
                    issues.append(f"target golden case {case.get('id', '<unknown>')} disagrees with target_contracts.{target}.{key}")


def validate_pressure_test_policy(root: Mapping[str, Any], issues: List[str]) -> None:
    policy = require_mapping(root.get("pressure_test_policy"), "pressure_test_policy", issues)
    if policy.get("methods") != EXPECTED_PRESSURE_METHODS:
        issues.append(f"pressure_test_policy.methods must be exactly {EXPECTED_PRESSURE_METHODS!r}")
    if policy.get("observation_requirement_methods") != EXPECTED_OBSERVATION_METHODS:
        issues.append(
            "pressure_test_policy.observation_requirement_methods must preserve "
            "the static, synthetic, and live observation hierarchy"
        )
    if policy.get("required_result_fields") != EXPECTED_PRESSURE_RESULT_FIELDS:
        issues.append(
            "pressure_test_policy.required_result_fields must define the nine-field "
            "evidence record exactly"
        )
    if policy.get("static_simulation_evidence_status") != "Inferred":
        issues.append("Static simulation evidence must be Inferred")
    if policy.get("insufficient_method_result") != "Not Assessed":
        issues.append("an insufficient pressure-test method must result in Not Assessed")
    expected = {
        "g20_measures": "coverage_and_behavioral_success",
        "partial_counts_as_completed_coverage": True,
        "partial_is_behavioral_success": False,
        "partial_triggers_79_point_cap": False,
        "failed_or_missing_required_pressure_evidence_triggers_79_point_cap": True,
    }
    for key, value in expected.items():
        if policy.get(key) != value:
            issues.append(f"pressure_test_policy.{key} must be {value!r}")
    rules = require_mapping(policy.get("g20_result_rules"), "pressure_test_policy.g20_result_rules", issues)
    if list(rules) != EXPECTED_RESULTS or not all(isinstance(value, str) and value for value in rules.values()):
        issues.append("pressure_test_policy.g20_result_rules must define every gate result in enum order")


def validate_release_evidence_semantics(root: Mapping[str, Any], issues: List[str]) -> None:
    """Keep quality, artifact eligibility, and release verdicts independent and deterministic."""
    quality_policy = require_mapping(
        root.get("quality_policy_result_policy"), "quality_policy_result_policy", issues
    )
    if dict(quality_policy) != EXPECTED_QUALITY_POLICY:
        issues.append(
            "quality_policy_result_policy must remain independent of validator, gate, "
            "and compatibility results"
        )

    roles = root.get("artifact_roles")
    if roles != EXPECTED_ARTIFACT_ROLES:
        issues.append(f"artifact_roles must be exactly {EXPECTED_ARTIFACT_ROLES!r}")
    role_contracts = require_mapping(
        root.get("artifact_role_contracts"), "artifact_role_contracts", issues
    )
    if dict(role_contracts) != EXPECTED_ARTIFACT_ROLE_CONTRACTS:
        issues.append(
            "artifact_role_contracts must keep Release ZIP as exact-artifact evidence, "
            "Installed runtime ineligible for a new-release Pass, and source packaging gated"
        )

    release_rollup = require_mapping(
        root.get("release_verdict_rollup"), "release_verdict_rollup", issues
    )
    if dict(release_rollup) != EXPECTED_RELEASE_VERDICT_ROLLUP:
        issues.append(
            "release_verdict_rollup must use Fail > Not Assessed > Partial > Pass "
            "while ignoring Not Applicable"
        )

    g23 = next(
        (
            gate
            for gate in root.get("gates", [])
            if isinstance(gate, dict) and gate.get("id") == "G23"
        ),
        {},
    )
    if g23.get("artifact_scope") != ["Skill Forge"]:
        issues.append("G23 must apply only to Skill Forge")
    if g23.get("artifact_roles") != ["Release ZIP", "Mutable source checkout"]:
        issues.append("G23 artifact roles must be Release ZIP and Mutable source checkout")
    gates = {
        gate.get("id"): gate
        for gate in root.get("gates", [])
        if isinstance(gate, dict) and isinstance(gate.get("id"), str)
    }
    g20_evidence = " ".join(gates.get("G20", {}).get("required_evidence", []))
    if not all(
        marker in g20_evidence
        for marker in ("nine pressure_test_policy fields", "observation requirement and method", "predicted and observed")
    ):
        issues.append("G20 must require complete method-aware pressure evidence")
    g22_evidence = " ".join(gates.get("G22", {}).get("required_evidence", []))
    if not all(marker in g22_evidence for marker in ("per-profile", "overall cross-profile", "release_verdict_rollup")):
        issues.append("G22 must reconcile per-profile and overall release verdicts")
    g12_evidence = " ".join(gates.get("G12", {}).get("required_evidence", []))
    if not all(
        marker in g12_evidence
        for marker in ("run_source_tests.py", "run_self_tests.py", "extracted", "source-proved")
    ):
        issues.append("G12 must require source-only and extracted source-proved runtime tests")
    g23_evidence = " ".join(g23.get("required_evidence", []))
    if not all(
        marker in g23_evidence
        for marker in (
            "Release ZIP",
            "exact-artifact",
            "canonical runtime-manifest archive integrity",
            "local Git source proof",
            "manifest-digest binding",
            "portable and openai profiles",
            "extracted-runtime tests",
            "explicit packaging authority",
            "archive built from a committed revision",
        )
    ):
        issues.append("G23 must require canonical archive, source, digest-binding, profile, runtime-test, and authorized committed-revision evidence")


def validate_trust_policies(root: Mapping[str, Any], issues: List[str]) -> None:
    """Keep artifact-content and untrusted-code boundaries fail closed."""
    untrusted_content = require_mapping(
        root.get("untrusted_content_policy"), "untrusted_content_policy", issues
    )
    if dict(untrusted_content) != EXPECTED_UNTRUSTED_CONTENT_POLICY:
        issues.append(
            "untrusted_content_policy must preserve evidence-only artifact text, "
            "non-authority, and safe sensitive-value redaction"
        )

    self_tests = require_mapping(
        root.get("self_test_execution_policy"), "self_test_execution_policy", issues
    )
    if dict(self_tests) != EXPECTED_SELF_TEST_EXECUTION_POLICY:
        issues.append(
            "self_test_execution_policy must require the complete default-deny "
            "sandbox and map an unmet control to Not Assessed"
        )

    independent_evaluator = require_mapping(
        root.get("independent_evaluator_policy"),
        "independent_evaluator_policy",
        issues,
    )
    if dict(independent_evaluator) != EXPECTED_INDEPENDENT_EVALUATOR_POLICY:
        issues.append(
            "independent_evaluator_policy must keep schema 6 as the default and "
            "allow only the non-reusable schema 5 to 6 v2.0.0 bootstrap transition"
        )

    gates = {
        gate.get("id"): gate
        for gate in root.get("gates", [])
        if isinstance(gate, dict) and isinstance(gate.get("id"), str)
    }
    g11_evidence = " ".join(gates.get("G11", {}).get("required_evidence", []))
    if not all(
        marker in g11_evidence
        for marker in ("every self_test_execution_policy control verified", "Not Assessed")
    ):
        issues.append("G11 required evidence must enforce every sandbox control and Not Assessed fallback")
    g15_evidence = " ".join(gates.get("G15", {}).get("required_evidence", []))
    if not all(marker in g15_evidence for marker in ("path", "finding_type", "redacted_fingerprint")):
        issues.append("G15 required evidence must use the redacted sensitive-finding record")
    g09_evidence = " ".join(gates.get("G09", {}).get("required_evidence", []))
    if not all(
        marker in g09_evidence
        for marker in (
            "Skill Forge v2.0.0",
            "independent_evaluator_policy.bootstrap_transition",
            "every transition requirement passes",
            "bootstrap transition evidence",
            "rather than an independent schema-6 pass",
        )
    ):
        issues.append(
            "G09 must keep the schema 5 to 6 bootstrap exception exact, bounded, "
            "and distinct from an independent schema-6 pass"
        )


def validate_routing_contract(root: Mapping[str, Any], issues: List[str]) -> None:
    """Enforce affirmative mutation, phased modes, and independent profiles."""
    routing = require_mapping(root.get("routing_rules"), "routing_rules", issues)
    if dict(routing) != EXPECTED_ROUTING_RULES:
        issues.append(f"routing_rules must be exactly {EXPECTED_ROUTING_RULES!r}")

    request_cases = root.get("request_routing_golden_cases")
    actual_request_cases: List[tuple[Any, Any, Any, Any]] = []
    if isinstance(request_cases, list):
        actual_request_cases = [
            (case.get("id"), case.get("request"), case.get("expected_phases"), case.get("mutation_authorized"))
            for case in request_cases
            if isinstance(case, dict) and isinstance(case.get("request"), str) and case.get("request")
        ]
    if actual_request_cases != EXPECTED_REQUEST_ROUTING_CASES:
        issues.append("request_routing_golden_cases must preserve exact requests and outcomes for suggestions, questions, negation, quotation, Repair, phased Release, and no-edit cases")

    profile_cases = root.get("profile_routing_golden_cases")
    actual_profile_cases: List[tuple[Any, Any, Any, Any, Any]] = []
    if isinstance(profile_cases, list):
        actual_profile_cases = [
            (
                case.get("id"),
                case.get("clarification_required"),
                case.get("expected_profiles"),
                case.get("unresolved_surfaces"),
                case.get("unresolved_result"),
            )
            for case in profile_cases
            if isinstance(case, dict) and isinstance(case.get("request"), str) and case.get("request")
        ]
    if actual_profile_cases != EXPECTED_PROFILE_ROUTING_CASES:
        issues.append("profile_routing_golden_cases must preserve portable fallback and independent named-profile results")


def parse_example_counts(text: str, issues: List[str]) -> Mapping[str, int]:
    match = re.search(
        r"\*\*Required-gate counts:\*\*\s*"
        r"Pass:\s*(\d+);\s*Fail:\s*(\d+);\s*Partial:\s*(\d+);\s*"
        r"Not Assessed:\s*(\d+);\s*Not Applicable:\s*(\d+);\s*Applicable:\s*(\d+)",
        text,
    )
    if not match:
        issues.append("example report lacks parseable required-gate counts")
        return {}
    labels = EXPECTED_RESULTS + ["Applicable"]
    return {label: int(value) for label, value in zip(labels, match.groups())}


def marked_region(text: str, start: str, end: str, label: str, issues: List[str]) -> str:
    """Return one explicitly bounded machine-checked documentation region."""
    if text.count(start) != 1 or text.count(end) != 1:
        issues.append(f"inspector schema must contain exactly one {label} marker pair")
        return ""
    before, remainder = text.split(start, 1)
    del before
    region, trailing = remainder.split(end, 1)
    del trailing
    return region


def parse_example_gate_rows(text: str, issues: List[str]) -> List[tuple[str, str]]:
    """Preserve ordered matrix rows so duplicate or reordered gates cannot hide."""
    rows: List[tuple[str, str]] = []
    row_start = re.compile(r"^\|\s*(G\d[^|]*)\|", re.MULTILINE)
    valid_row = re.compile(
        r"^\|\s*(G\d{2})\s*\|\s*[^|]+\|\s*"
        r"(Pass|Fail|Partial|Not Assessed|Not Applicable)\s*\|\s*[^|]+\|\s*$"
    )
    for line in text.splitlines():
        if not row_start.match(line):
            continue
        match = valid_row.match(line)
        if not match:
            issues.append(f"example report has malformed gate row: {line}")
            continue
        rows.append((match.group(1), match.group(2)))
    return rows


def validate_example_gate_rows(rows: Sequence[tuple[str, str]], issues: List[str]) -> None:
    expected_ids = [f"G{index:02d}" for index in range(1, 24)]
    ids = [gate_id for gate_id, _ in rows]
    duplicates = sorted({gate_id for gate_id in ids if ids.count(gate_id) > 1})
    missing = [gate_id for gate_id in expected_ids if gate_id not in ids]
    extra = [gate_id for gate_id in ids if gate_id not in expected_ids]
    if duplicates:
        issues.append(f"example report has duplicate gate rows: {', '.join(duplicates)}")
    if missing:
        issues.append(f"example report is missing gate rows: {', '.join(missing)}")
    if extra:
        issues.append(f"example report has unsupported gate rows: {', '.join(extra)}")
    if ids != expected_ids:
        issues.append("example report gate rows must be G01 through G23 exactly once and in order")


def roll_up_executive_result(results: Sequence[str], rules: Mapping[str, Any]) -> str:
    applicable = [result for result in results if result != "Not Applicable"]
    if not applicable:
        return str(rules["all_not_applicable_result"])
    for result in rules["precedence"]:
        if result in applicable:
            return result
    raise ValueError("executive roll-up has no matching precedence result")


def roll_up_release_verdict(results: Sequence[str], rules: Mapping[str, Any]) -> str:
    ignored = rules.get("ignored_gate_result")
    applicable = [result for result in results if result != ignored]
    if not applicable:
        return str(rules["all_not_applicable_result"])
    for result in rules["precedence"]:
        if result in applicable:
            return result
    raise ValueError("release-verdict roll-up has no matching precedence result")


def validate_example_executive_rollups(
    text: str,
    contract: Mapping[str, Any],
    gate_rows: Sequence[tuple[str, str]],
    issues: List[str],
) -> None:
    groups = contract.get("executive_summary_groups")
    rules = contract.get("executive_summary_rollup")
    if not isinstance(groups, list) or not isinstance(rules, dict):
        return
    row_pattern = re.compile(
        r"^\|\s*([^|]+?)\s*\|\s*(G\d{2}–G\d{2})\s*\|\s*"
        r"(Pass|Fail|Partial|Not Assessed|Not Applicable)\s*\|\s*[^|]+\|\s*$"
    )
    executive_rows = [match.groups() for line in text.splitlines() if (match := row_pattern.match(line))]
    if len(executive_rows) != len(groups):
        issues.append("example report must have exactly one executive row for every configured group")
        return
    for group, actual in zip(groups, executive_rows):
        if not isinstance(group, dict):
            continue
        title = group.get("title")
        gate_ids = group.get("gate_ids")
        if not isinstance(title, str) or not isinstance(gate_ids, list) or not gate_ids:
            continue
        expected_label = f"{gate_ids[0]}–{gate_ids[-1]}"
        if actual[0] != title or actual[1] != expected_label:
            issues.append("example report executive rows must match the configured group titles and gate ranges in order")
            continue
        group_results = [result for gate_id, result in gate_rows if gate_id in gate_ids]
        if len(group_results) != len(gate_ids):
            continue
        expected_rollup = roll_up_executive_result(group_results, rules)
        if actual[2] != expected_rollup:
            issues.append(
                f"example report executive result for {title!r} is {actual[2]!r}; expected {expected_rollup!r}"
            )


def validate_example_release_verdict(
    text: str,
    contract: Mapping[str, Any],
    gate_rows: Sequence[tuple[str, str]],
    issues: List[str],
) -> None:
    match = re.search(
        r"\*\*Release gate verdict:\s*(Pass|Fail|Partial|Not Assessed)\*\*",
        text,
    )
    if match is None:
        issues.append("example report lacks a parseable release gate verdict")
        return
    rules = contract.get("release_verdict_rollup")
    if not isinstance(rules, dict) or not gate_rows:
        return
    expected = roll_up_release_verdict([result for _, result in gate_rows], rules)
    if match.group(1) != expected:
        issues.append(
            f"example report release gate verdict is {match.group(1)!r}; expected {expected!r}"
        )


def validate_example_safety_consistency(text: str, issues: List[str]) -> None:
    claim = re.search(r"\*\*Potential safety/privacy concerns:\*\*\s*([^\n]+)", text, re.IGNORECASE)
    if claim is None or not re.search(r"\bnone\b", claim.group(1), re.IGNORECASE):
        return
    later_text = text[claim.end():]
    failed_privacy_row = re.search(
        r"^\|\s*Safety/privacy\s*\|[^|]*\|[^|]*\|[^|]*\|\s*(?:Fail|Partial)\s*\|",
        later_text,
        re.IGNORECASE | re.MULTILINE,
    )
    later_secret_or_safety_defect = re.search(
        r"`(?:secret_[a-z0-9_]+|script_dangerous_command[a-z0-9_]*)`|"
        r"\b(?:privacy|PII)[^\n]*\b(?:defect|gap|missing|fail)\b",
        later_text,
        re.IGNORECASE,
    )
    if failed_privacy_row or later_secret_or_safety_defect:
        issues.append("example report cannot claim no safety/privacy concerns before reporting a safety or privacy defect")


def validate_scoring_contract(data: Any, issues: List[str]) -> Mapping[str, Any]:
    """Validate the complete v1 scoring vocabulary, arithmetic, and evidence floor."""
    root = require_mapping(data, "scoring_contract", issues)
    expected_keys = {"scorecard_version", "rubric_version", "schema_version", "assessment_profiles", "profiles", "result_enums", "earned_fractions", "evidence_methods", "evidence_labels", "categories", "criteria", "deduction_policy", "arithmetic", "legacy_policy"}
    def check(ok: bool, message: str) -> None:
        if not ok:
            issues.append("scoring_contract: " + message)
    check(set(root) == expected_keys, "unexpected or missing root fields")
    check(type(root.get("schema_version")) is int and root.get("schema_version") == 1, "schema_version must be integer 1")
    check(root.get("scorecard_version") == "1.0" and root.get("rubric_version") == "2.0", "scorecard/rubric versions changed")
    profiles = ["design", "execution", "host"]
    check(root.get("assessment_profiles") == profiles, "assessment profiles must be design, execution, host")
    profile_map = require_mapping(root.get("profiles"), "scoring_contract.profiles", issues)
    check(set(profile_map) == set(profiles), "all profile definitions required")
    for name in profiles:
        definition = profile_map.get(name)
        check(isinstance(definition, dict) and set(definition) == {"claim"} and isinstance(definition.get("claim"), str) and bool(definition["claim"].strip()), "profile claim required: " + name)
    check(root.get("result_enums") == ["Pass", "Partial", "Fail", "Not Assessed", "Not Applicable"], "outcomes changed")
    fractions = root.get("earned_fractions")
    check(fractions == {"Pass": 1, "Partial": 0.5, "Fail": 0} and isinstance(fractions, dict) and all(type(v) in (int, float) for v in fractions.values()), "earned fractions changed")
    methods = ["Static inspection", "Static simulation", "Synthetic execution", "Live host observation"]
    check(root.get("evidence_methods") == methods, "evidence methods changed")
    check(root.get("evidence_labels") == ["Verified", "Inferred", "Unverified"], "evidence labels changed")
    categories = root.get("categories")
    expected_categories = [("triggering", 20), ("workflow", 20), ("reliability", 20), ("resources", 15), ("errors", 10), ("safety", 10), ("maintenance", 5)]
    check(isinstance(categories, list) and [(c.get("id"), c.get("weight")) for c in categories if isinstance(c, dict)] == expected_categories, "seven category weights must remain 20/20/20/15/10/10/5")
    for category in categories if isinstance(categories, list) else []:
        check(isinstance(category, dict) and set(category) == {"id", "title", "weight"} and type(category.get("weight")) is int and isinstance(category.get("title"), str) and bool(category["title"].strip()), "invalid category")
    criteria = root.get("criteria")
    check(isinstance(criteria, list) and len(criteria) > 0, "nonempty criteria required")
    seen = set()
    sums = {name: 0 for name, _ in expected_categories}
    for criterion in criteria if isinstance(criteria, list) else []:
        if not isinstance(criterion, dict):
            check(False, "criterion must be an object")
            continue
        check(set(criterion) == {"id", "category", "weight", "claim_type", "anchors", "required_methods", "not_applicable_reasons"}, "criterion fields invalid")
        cid = criterion.get("id")
        valid_id = isinstance(cid, str) and re.fullmatch(r"C[0-9]{2}", cid) is not None
        check(valid_id and cid not in seen, "criterion IDs must be unique Cnn strings")
        if valid_id:
            seen.add(cid)
        cat, weight = criterion.get("category"), criterion.get("weight")
        valid_weight = type(weight) is int and weight > 0
        check(isinstance(cat, str) and cat in sums and valid_weight, "invalid criterion category or weight")
        if isinstance(cat, str) and cat in sums and valid_weight:
            sums[cat] += weight
        anchors = criterion.get("anchors")
        check(isinstance(anchors, dict) and set(anchors) == {"Pass", "Partial", "Fail"} and all(isinstance(v, str) and v.strip() for v in anchors.values()) and len(set(str(v).strip() for v in anchors.values())) == 3, "three distinct nonempty anchors required")
        kind = criterion.get("claim_type")
        check(kind in ("static", "behavior"), "claim_type must be static or behavior")
        required = criterion.get("required_methods")
        check(isinstance(required, dict) and set(required) == set(profiles), "required_methods must cover every profile")
        for profile in profiles:
            allowed = required.get(profile) if isinstance(required, dict) else None
            expected = methods if profile == "design" else ["Synthetic execution", "Live host observation"] if kind == "behavior" and profile == "execution" else ["Live host observation"] if kind == "behavior" else ["Static inspection", "Synthetic execution", "Live host observation"]
            check(allowed == expected, "required evidence floor changed for " + str(cid) + "/" + profile)
        reasons = criterion.get("not_applicable_reasons")
        check(isinstance(reasons, list) and all(isinstance(r, str) and r.strip() for r in reasons) and len(set(str(r) for r in reasons)) == len(reasons), "NA reasons must be unique nonempty strings")
    check(sums == dict(expected_categories), "criterion weights must sum to category weights")
    check(root.get("deduction_policy") == {"primary_criterion_per_defect": True, "finding_and_evidence_required": True, "additional_deduction_requires_distinct_impact": True}, "deduction policy weakened")
    check(root.get("arithmetic") == {"coverage": "E/A", "assessed_only_score": "100*P/E if E>0 else null", "quality_score": "100*P/A if E=A>0 else null", "rounding": "exact fractions internally; round once to one decimal using ROUND_HALF_UP"}, "arithmetic changed")
    check(root.get("legacy_policy") == {"enabled_by_default": False, "requires_complete_quality_score": True, "requires_cap_reasons": True, "caps": {"unresolved_critical": 49, "unresolved_high": 79, "missing_or_failed_required_pressure_evidence": 79}}, "legacy projection policy changed")
    return root


def validate_contract(data: Any, issues: List[str]) -> Mapping[str, Any]:
    root = require_mapping(data, "contract", issues)
    if root.get("contract_version") != 5:
        issues.append("contract_version must be 5")
    if root.get("result_enums") != EXPECTED_RESULTS:
        issues.append(f"result_enums must be exactly {EXPECTED_RESULTS!r}")
    if root.get("evidence_labels") != EXPECTED_EVIDENCE:
        issues.append(f"evidence_labels must be exactly {EXPECTED_EVIDENCE!r}")
    if root.get("profiles") != EXPECTED_PROFILES:
        issues.append(f"profiles must be exactly {EXPECTED_PROFILES!r}")
    validate_target_contracts(root, issues)
    validate_outcome_mapping_and_golden_cases(root, issues)
    validate_routing_contract(root, issues)
    validate_trust_policies(root, issues)
    validate_pressure_test_policy(root, issues)
    validate_release_evidence_semantics(root, issues)

    if root.get("scoring_contract") != {"path": "scoring-contract.json", "schema_version": 1, "score_caps_scope": "legacy_policy_score_only", "quality_independent_of_release": True}:
        issues.append("scoring_contract must bind v1 with independent quality and legacy-only caps")
    caps = require_mapping(root.get("score_caps"), "score_caps", issues)
    expected_caps = {
        "unresolved_critical": 49,
        "unresolved_high": 79,
        "missing_or_failed_required_pressure_evidence": 79,
    }
    if dict(caps) != expected_caps:
        issues.append(f"score_caps must be exactly {expected_caps!r}")

    pressure = root.get("required_pressure_categories")
    expected_pressure_ids = [f"P{index:02d}" for index in range(1, 12)]
    if not isinstance(pressure, list) or [entry.get("id") for entry in pressure if isinstance(entry, dict)] != expected_pressure_ids:
        issues.append("required_pressure_categories must define P01 through P11 in order")
    elif not all(isinstance(entry.get("title"), str) and entry["title"] for entry in pressure):
        issues.append("every pressure category must have a title")

    gates = root.get("gates")
    expected_gate_ids = [f"G{index:02d}" for index in range(1, 24)]
    if not isinstance(gates, list):
        issues.append("gates must be a list")
        return root
    gate_ids = [gate.get("id") for gate in gates if isinstance(gate, dict)]
    if gate_ids != expected_gate_ids:
        issues.append("gates must define G01 through G23 in order with no omissions")
    required_keys = {
        "id",
        "title",
        "profiles",
        "artifact_roles",
        "required_evidence",
        "allowed_results",
        "blocks_release",
    }
    for gate in gates:
        if not isinstance(gate, dict):
            issues.append("every gate must be an object")
            continue
        gate_id = gate.get("id", "<unknown>")
        missing = sorted(required_keys - set(gate))
        if missing:
            issues.append(f"{gate_id} is missing contract fields: {', '.join(missing)}")
        if not isinstance(gate.get("title"), str) or not gate.get("title"):
            issues.append(f"{gate_id} needs a non-empty title")
        profiles = require_strings(gate.get("profiles"), f"{gate_id}.profiles", issues)
        if any(profile not in EXPECTED_PROFILES for profile in profiles):
            issues.append(f"{gate_id} has an unknown profile")
        artifact_roles = require_strings(gate.get("artifact_roles"), f"{gate_id}.artifact_roles", issues)
        if not artifact_roles:
            issues.append(f"{gate_id} must apply to at least one artifact role")
        elif any(role not in EXPECTED_ARTIFACT_ROLES for role in artifact_roles):
            issues.append(f"{gate_id} has an unknown artifact role")
        if not require_strings(gate.get("required_evidence"), f"{gate_id}.required_evidence", issues):
            issues.append(f"{gate_id} must state required evidence")
        if gate.get("allowed_results") != EXPECTED_RESULTS:
            issues.append(f"{gate_id}.allowed_results must match result_enums")
        if not isinstance(gate.get("blocks_release"), bool):
            issues.append(f"{gate_id}.blocks_release must be a boolean")

    groups = root.get("executive_summary_groups")
    if not isinstance(groups, list) or len(groups) != 5:
        issues.append("executive_summary_groups must contain exactly five rows")
    else:
        flattened = [gate_id for group in groups if isinstance(group, dict) for gate_id in group.get("gate_ids", [])]
        if flattened != expected_gate_ids:
            issues.append("executive summary groups must cover G01 through G23 exactly once in order")
    if root.get("executive_summary_rollup") != EXPECTED_EXECUTIVE_ROLLUP:
        issues.append("executive_summary_rollup must define the deterministic configured precedence and Not Applicable rule")
    return root


def assignment_value(tree: ast.AST, name: str) -> Any:
    for node in getattr(tree, "body", []):
        if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
            return ast.literal_eval(node.value)
    raise ValueError(f"missing literal assignment {name}")


def inspector_effective_limit_fields(tree: ast.AST) -> List[str]:
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef) or node.name != "InspectionLimits":
            continue
        for member in node.body:
            if not isinstance(member, ast.FunctionDef) or member.name != "as_dict":
                continue
            for statement in member.body:
                if isinstance(statement, ast.Return) and isinstance(statement.value, ast.Dict):
                    keys = [key.value for key in statement.value.keys if isinstance(key, ast.Constant) and isinstance(key.value, str)]
                    return keys + ["tree_limit", "target_product_upload_limit_bytes"]
    raise ValueError("could not read InspectionLimits.as_dict output keys")


def inspector_safety_flags(tree: ast.AST) -> List[str]:
    flags: List[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute) or node.func.attr != "add_argument":
            continue
        for argument in node.args:
            if isinstance(argument, ast.Constant) and isinstance(argument.value, str):
                flag = argument.value
                if flag == "--tree-limit" or flag.startswith("--max-"):
                    flags.append(flag)
    return sorted(set(flags))


def markdown_codes(region: str) -> List[str]:
    return re.findall(r"`([a-z][a-z0-9_]+)`", region)


def validate_inspector_policy_documentation(
    tree: ast.AST,
    schema: str,
    example_report: str,
    issues: List[str],
) -> None:
    """Bind documented safety defaults and notes to inspector source literals."""
    limits_region = marked_region(schema, LIMITS_TABLE_START, LIMITS_TABLE_END, "limits table", issues)
    documented_defaults = {
        flag: value
        for flag, value in re.findall(
            r"^\|\s*`(--[a-z0-9-]+)`\s*\|[^|]*\|\s*`([^`]+)`\s*\|",
            limits_region,
            re.MULTILINE,
        )
    }
    for flag, (constant_name, _field_name) in INSPECTOR_DIRECTORY_DEFAULTS.items():
        try:
            expected = str(assignment_value(tree, constant_name))
        except ValueError as exc:
            issues.append(f"could not read inspector default for {flag}: {exc}")
            continue
        actual = documented_defaults.get(flag)
        if actual != expected:
            issues.append(
                f"inspector schema default for {flag} must match {constant_name}={expected}; found {actual!r}"
            )

    try:
        secret_note = assignment_value(tree, "SECRET_SCAN_NOTE")
    except ValueError as exc:
        issues.append(f"could not read inspector secret-scan note: {exc}")
        return
    if not isinstance(secret_note, str) or not secret_note:
        issues.append("SECRET_SCAN_NOTE must be a non-empty string literal")
    elif secret_note not in example_report:
        issues.append("example report must include the inspector's exact current SECRET_SCAN_NOTE")


def minimal_success_example(schema: str, issues: List[str]) -> Mapping[str, Any]:
    section = schema.split("## Minimal Successful Output Example", 1)
    if len(section) != 2:
        issues.append("inspector schema lacks a Minimal Successful Output Example")
        return {}
    match = re.search(r"```json\s*(\{.*?\})\s*```", section[1], re.DOTALL)
    if match is None:
        issues.append("inspector schema lacks a parseable minimal successful JSON example")
        return {}
    try:
        value = json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        issues.append(f"inspector schema minimal successful JSON is invalid: {exc}")
        return {}
    if not isinstance(value, dict):
        issues.append("inspector schema minimal successful JSON must be an object")
        return {}
    return value


def validate_inspector_documentation(issues: List[str]) -> None:
    """Keep inspector code, JSON examples, limits, and finding docs synchronized."""
    inspector_source = read_text(INSPECTOR_PATH, issues)
    schema = read_text(INSPECTOR_SCHEMA_PATH, issues)
    example_report = read_text(EXAMPLE_PATH, issues)
    if not inspector_source or not schema or not example_report:
        return
    try:
        tree = ast.parse(inspector_source)
        finding_catalog = assignment_value(tree, "FINDING_CODE_CATALOG")
        finding_sections = assignment_value(tree, "FINDING_SECTION_KEYS")
        schema_version = assignment_value(tree, "INSPECTION_SCHEMA_VERSION")
        effective_fields = inspector_effective_limit_fields(tree)
        safety_flags = inspector_safety_flags(tree)
    except (SyntaxError, ValueError) as exc:
        issues.append(f"could not read inspector output contract: {exc}")
        return
    if not isinstance(finding_catalog, tuple) or not all(isinstance(code, str) for code in finding_catalog):
        issues.append("FINDING_CODE_CATALOG must be a tuple of strings")
        return
    if len(finding_catalog) != len(set(finding_catalog)):
        issues.append("FINDING_CODE_CATALOG must not contain duplicate codes")
    if list(finding_sections) != SEVERITY_FINDING_SECTIONS:
        issues.append("FINDING_SECTION_KEYS must match the ordered severity-bearing output contract")
    if "if code not in FINDING_CODE_SET:" not in inspector_source:
        issues.append("inspector finding() must reject unregistered finding codes")

    documented_catalog = markdown_codes(marked_region(
        schema, FINDING_CATALOG_START, FINDING_CATALOG_END, "finding catalog", issues
    ))
    catalog_set = set(finding_catalog)
    documented_set = set(documented_catalog)
    missing_codes = sorted(catalog_set - documented_set)
    stale_codes = sorted(documented_set - catalog_set)
    if missing_codes:
        issues.append(f"inspector finding catalog is missing emitted codes: {', '.join(missing_codes)}")
    if stale_codes:
        issues.append(f"inspector finding catalog documents codes that cannot emit: {', '.join(stale_codes)}")
    if len(documented_catalog) != len(documented_set):
        issues.append("inspector finding catalog must not repeat a code")

    limits_region = marked_region(schema, LIMITS_TABLE_START, LIMITS_TABLE_END, "limits table", issues)
    documented_flags = set(re.findall(r"`(--(?:tree-limit|max-[a-z0-9-]+))`", limits_region))
    missing_flags = sorted(set(safety_flags) - documented_flags)
    stale_flags = sorted(documented_flags - set(safety_flags))
    if missing_flags:
        issues.append(f"inspector schema is missing CLI safety-limit docs: {', '.join(missing_flags)}")
    if stale_flags:
        issues.append(f"inspector schema documents retired CLI safety limits: {', '.join(stale_flags)}")
    validate_inspector_policy_documentation(tree, schema, example_report, issues)

    effective_region = marked_region(schema, EFFECTIVE_LIMITS_START, EFFECTIVE_LIMITS_END, "effective-limits", issues)
    documented_effective_fields = set(markdown_codes(effective_region))
    missing_effective = sorted(set(effective_fields) - documented_effective_fields)
    stale_effective = sorted(documented_effective_fields - set(effective_fields))
    if missing_effective:
        issues.append(f"inspector schema is missing effective_limits fields: {', '.join(missing_effective)}")
    if stale_effective:
        issues.append(f"inspector schema documents retired effective_limits fields: {', '.join(stale_effective)}")

    severity_region = marked_region(schema, SEVERITY_SECTIONS_START, SEVERITY_SECTIONS_END, "severity sections", issues)
    documented_sections = markdown_codes(severity_region)
    if documented_sections != SEVERITY_FINDING_SECTIONS:
        issues.append("inspector schema severity-bearing sections must match the current ordered output contract")

    example = minimal_success_example(schema, issues)
    if not example:
        return
    required_example_fields = {
        "requested_target",
        "canonical_target",
        "target_alias_used",
        "target_deprecation_note",
        "target_profile",
        "coverage_complete",
        "coverage_findings",
        "unscanned_paths",
        "manifest_verification_complete",
        "unverified_manifests",
        "frontmatter",
        "description_length",
        "effective_limits",
        "summary",
    }
    missing_example_fields = sorted(required_example_fields - set(example))
    if missing_example_fields:
        issues.append(f"inspector schema minimal successful example is missing fields: {', '.join(missing_example_fields)}")
    if example.get("schema_version") != schema_version:
        issues.append("inspector schema minimal successful example has a stale schema_version")
    if example.get("requested_target") != "portable" or example.get("canonical_target") != "portable":
        issues.append("inspector schema minimal successful example must show canonical portable target identity")
    if example.get("target_alias_used") is not False or example.get("target_deprecation_note") is not None:
        issues.append("inspector schema minimal successful example must show a non-alias target state")
    frontmatter = example.get("frontmatter")
    expected_frontmatter_fields = {
        "redacted",
        "validated_name",
        "present_keys",
        "value_types",
        "unrecognized_key_count",
        "description_length",
    }
    if not isinstance(frontmatter, dict):
        issues.append("inspector schema minimal successful example must include a redacted frontmatter summary")
    else:
        if set(frontmatter) != expected_frontmatter_fields:
            issues.append("inspector schema frontmatter example must contain only the schema-6 redacted summary fields")
        if frontmatter.get("redacted") is not True:
            issues.append("inspector schema frontmatter example must mark parsed values redacted")
        present_keys = frontmatter.get("present_keys")
        value_types = frontmatter.get("value_types")
        if not isinstance(present_keys, list) or present_keys != sorted(present_keys):
            issues.append("inspector schema frontmatter present_keys must be a sorted list")
        if not isinstance(value_types, dict) or set(value_types) != set(present_keys or []):
            issues.append("inspector schema frontmatter value_types must cover exactly the recognized present_keys")
        if frontmatter.get("description_length") != example.get("description_length"):
            issues.append("inspector schema frontmatter and top-level description_length must match")
        if not isinstance(frontmatter.get("unrecognized_key_count"), int):
            issues.append("inspector schema frontmatter unrecognized_key_count must be an integer")
    limits = example.get("effective_limits")
    if not isinstance(limits, dict) or set(effective_fields) - set(limits):
        issues.append("inspector schema minimal successful example must include every active effective_limits field")
    elif isinstance(limits, dict):
        for _flag, (constant_name, field_name) in INSPECTOR_DIRECTORY_DEFAULTS.items():
            try:
                expected = assignment_value(tree, constant_name)
            except ValueError as exc:
                issues.append(f"could not read inspector example default {constant_name}: {exc}")
                continue
            if limits.get(field_name) != expected:
                issues.append(
                    f"inspector schema minimal successful example {field_name} must match "
                    f"{constant_name}={expected}"
                )


def validate_skill_control_plane(issues: List[str]) -> None:
    """Guard the compact, safety-preserving mandatory Skill Forge control plane."""
    skill = read_text(SKILL_PATH, issues)
    if not skill:
        return
    word_count = len(re.findall(r"\b[\w/-]+\b", skill))
    if word_count > 1000:
        issues.append(f"SKILL.md must stay within the 1000 word upper control-plane budget; found {word_count}")
    frontmatter = re.match(r"^---\n(.*?)\n---", skill, re.DOTALL)
    description = re.search(r"^description:\s*(.+)$", frontmatter.group(1), re.MULTILINE) if frontmatter else None
    if description is None or len(description.group(1)) >= 200:
        issues.append("SKILL.md frontmatter description must remain under 200 characters")
    elif not all(token in description.group(1).lower() for token in ("audit", "validate", "skills", "release")):
        issues.append("SKILL.md frontmatter description must retain audit, validation, Skill, and release triggers")

    normalized_skill = " ".join(skill.split())
    for marker in (
        "fix, correct, rewrite, or refactor",
        "Compact:",
        "Standard:",
        "Release:",
        "complete authoritative\n     G01–G23 matrix",
        "Report mode changes presentation only",
        "statically review bundled",
        "before\nexecuting any of them",
        "package self-test evidence",
        "separately installed trusted Skill Forge release",
        "previously verified archive",
        "another independent evaluator",
        "own passing tests to an\nindependent release pass",
        "untrusted evidence only",
        "default-deny",
        "source read-only",
        "scratch-only writes",
        "Never reproduce raw\n   secrets or sensitive PII",
        "ordered phases",
        "affirmative directive",
        "multiple named hosts",
        "independently",
    ):
        if " ".join(marker.split()) not in normalized_skill:
            issues.append(f"SKILL.md is missing required control-plane rule: {marker!r}")
    for marker in (
        "ambiguity, mutation,",
        "references/inspector-output-schema.md",
        "Standard does not\nrequire the full Release contract",
        "source contract validation keeps mirrored\nrules synchronized",
        "Release loads `references/audit-contract.json`",
    ):
        if " ".join(marker.split()) not in normalized_skill:
            issues.append(f"SKILL.md is missing required conditional reference map rule: {marker!r}")
    classified: dict[str, str] = {}
    for heading, expected_paths in EXPECTED_REFERENCE_ROLES.items():
        parts = skill.split(heading, 1)
        if len(parts) != 2:
            issues.append(f"SKILL.md is missing reference role section {heading!r}")
            continue
        section = re.split(r"\n###\s+", parts[1], maxsplit=1)[0]
        actual_paths = set(re.findall(r"`(references/[^`]+)`", section))
        missing = sorted(expected_paths - actual_paths)
        unexpected = sorted(actual_paths - expected_paths)
        if missing:
            issues.append(f"{heading} is missing classified references: {', '.join(missing)}")
        if unexpected:
            issues.append(f"{heading} has references assigned to the wrong role: {', '.join(unexpected)}")
        for path in actual_paths:
            if path in classified:
                issues.append(f"{path} is classified in more than one reference role section")
            classified[path] = heading
    shipped_references = {
        repo_relative(path)
        for path in (REPO_ROOT / "references").iterdir()
        if path.is_file()
    }
    unclassified = sorted(shipped_references - set(classified))
    nonexistent = sorted(set(classified) - shipped_references)
    if unclassified:
        issues.append(f"SKILL.md has unclassified shipped references: {', '.join(unclassified)}")
    if nonexistent:
        issues.append(f"SKILL.md classifies nonexistent references: {', '.join(nonexistent)}")
    if "11/10" in skill:
        issues.append("SKILL.md must not advertise an 11/10 result")


def source_only_declaration_paths(skill_text: str, issues: List[str]) -> tuple[str, ...]:
    """Parse the one reserved source-only declaration without accepting prose."""
    matches = SOURCE_ONLY_DECLARATION_PATTERN.findall(skill_text)
    if len(matches) != 1:
        issues.append(
            "SKILL.md must contain exactly one skill-forge:source-only declaration"
        )
        return ()
    paths = tuple(matches[0].split())
    if not paths:
        issues.append("SKILL.md source-only declaration must list one or more paths")
    elif len(paths) != len(set(paths)):
        issues.append("SKILL.md source-only declaration must not repeat paths")
    return paths


def validate_runtime_boundary_contract(issues: List[str]) -> None:
    """Keep source docs, manifest selectors, and package exclusions aligned."""
    skill = read_text(SKILL_PATH, issues)
    if not skill:
        return
    declaration_issues: List[str] = []
    declared_paths = source_only_declaration_paths(skill, declaration_issues)
    issues.extend(declaration_issues)
    issues.extend(
        runtime_boundary_issues(
            SKILL_FORGE_RUNTIME_SELECTORS,
            FORBIDDEN_RUNTIME_PATHS,
            declared_paths,
        )
    )


def validate_documents(contract: Mapping[str, Any], issues: List[str]) -> None:
    texts = {
        CHECKLIST_PATH: read_text(CHECKLIST_PATH, issues),
        TEMPLATE_PATH: read_text(TEMPLATE_PATH, issues),
        EXAMPLE_PATH: read_text(EXAMPLE_PATH, issues),
        RUBRIC_PATH: read_text(RUBRIC_PATH, issues),
        PRESSURE_PATH: read_text(PRESSURE_PATH, issues),
        ROUTING_PATH: read_text(ROUTING_PATH, issues),
        MATRIX_PATH: read_text(MATRIX_PATH, issues),
        PLATFORM_PATH: read_text(PLATFORM_PATH, issues),
        VALIDATOR_EVIDENCE_PATH: read_text(VALIDATOR_EVIDENCE_PATH, issues),
        README_PATH: read_text(README_PATH, issues),
        AUDIT_CHECKLIST_PATH: read_text(AUDIT_CHECKLIST_PATH, issues),
        OPENAI_METADATA_PATH: read_text(OPENAI_METADATA_PATH, issues),
    }
    release_template = REPO_ROOT / "references" / "release-report-template.md"
    release_provenance = REPO_ROOT / "references" / "release-evaluator-provenance.md"
    release_text = read_text(release_template, issues)
    matrix_ids = re.findall(r"^\| (G\d{2}) \|", release_text, re.MULTILINE)
    if matrix_ids != [f"G{i:02d}" for i in range(1, 24)]:
        issues.append("references/release-report-template.md must retain the complete ordered G01-G23 matrix")
    texts[TEMPLATE_PATH] += "\n" + release_text
    texts[VALIDATOR_EVIDENCE_PATH] += "\n" + read_text(release_provenance, issues)
    gates = contract.get("gates") if isinstance(contract.get("gates"), list) else []
    gate_ids = [gate.get("id") for gate in gates if isinstance(gate, dict)]
    for gate_id in gate_ids:
        add_if_missing(texts[CHECKLIST_PATH], gate_id, CHECKLIST_PATH, issues)
        add_if_missing(texts[TEMPLATE_PATH], gate_id, TEMPLATE_PATH, issues)
        add_if_missing(texts[EXAMPLE_PATH], gate_id, EXAMPLE_PATH, issues)

    for document in (CHECKLIST_PATH, TEMPLATE_PATH, EXAMPLE_PATH):
        text = texts[document]
        for result in EXPECTED_RESULTS:
            add_if_missing(text, result, document, issues)
        for label in EXPECTED_EVIDENCE:
            add_if_missing(text, label, document, issues)
        if "Not Applicable" not in text or "rationale" not in text.lower():
            issues.append(f"{repo_relative(document)} must support Not Applicable with a rationale")

    for document in (RUBRIC_PATH, TEMPLATE_PATH, EXAMPLE_PATH):
        text = texts[document]
        for cap in ("49/100", "79/100"):
            add_if_missing(text, cap, document, issues)
    for label in EXPECTED_EVIDENCE:
        add_if_missing(texts[RUBRIC_PATH], label, RUBRIC_PATH, issues)

    pressure_titles = [entry.get("title") for entry in contract.get("required_pressure_categories", []) if isinstance(entry, dict)]
    for title in pressure_titles:
        add_if_missing(texts[PRESSURE_PATH], title, PRESSURE_PATH, issues)
        add_if_missing(texts[TEMPLATE_PATH], title, TEMPLATE_PATH, issues)
    for marker in (
        "Static simulation",
        "Synthetic execution",
        "Live host observation",
        "observation_requirement",
        "method_used",
        "predicted_behavior",
        "observed_behavior",
        "evidence_status",
        "insufficient",
        "Not Assessed",
    ):
        add_if_missing(texts[PRESSURE_PATH], marker, PRESSURE_PATH, issues)

    if "--target portable" not in texts[ROUTING_PATH] or "generic" not in texts[ROUTING_PATH].lower():
        issues.append("input routing must map generic requests to --target portable")
    if "Not Assessed" not in texts[MATRIX_PATH] or "draft-only" not in texts[MATRIX_PATH].lower():
        issues.append("artifact matrix must map draft-only release results to Not Assessed")
    if "suggest improvements" not in texts[MATRIX_PATH].lower() or "Evaluation" not in texts[MATRIX_PATH]:
        issues.append("artifact matrix must map suggestion-only improvements to Evaluation")
    for fixture in REPAIR_ROUTING_FIXTURES:
        if fixture not in texts[MATRIX_PATH] or "Repair" not in texts[MATRIX_PATH]:
            issues.append(f"artifact matrix must keep the Repair routing fixture {fixture!r}")
    for mutation_verb in ("improve", "fix", "correct", "rewrite", "refactor"):
        if mutation_verb not in texts[ROUTING_PATH].lower() or mutation_verb not in texts[MATRIX_PATH].lower():
            issues.append(f"routing references must classify {mutation_verb!r} as Repair")
    for marker in (
        "ordered phases",
        "affirmative directive",
        "Quoted, negated",
        "One invocation per supported canonical profile",
        "cannot certify any host",
    ):
        add_if_missing(texts[ROUTING_PATH], marker, ROUTING_PATH, issues)
    for marker in (
        "quoted, negated",
        "Repair → Release gate",
        "independent profile phase",
        "cannot hide",
    ):
        add_if_missing(texts[MATRIX_PATH], marker, MATRIX_PATH, issues)

    platform = texts[PLATFORM_PATH]
    for marker in (
        "target_contracts",
        "two audit target profiles",
        "No product upload limit is encoded",
        "one inspector invocation",
        "must not hide",
    ):
        add_if_missing(platform, marker, PLATFORM_PATH, issues)

    validator_evidence = texts[VALIDATOR_EVIDENCE_PATH]
    for marker in (
        "validator_outcome",
        "gate_result",
        "compatibility_result",
        "quality_policy_result",
        "Artifact Fail",
        "Skill Forge Self-Audit Bootstrap",
        "independent release pass",
        "untrusted evidence only",
        "redacted_fingerprint",
        "Network access is default-deny",
        "source is read-only",
        "process, wall-time, and memory limits",
        "all 10",
        "independent",
        "--bootstrap-schema-transition 5:6",
        "--bootstrap-release-tag v2.0.0",
        "bootstrap transition evidence",
        "raw schema-5 frontmatter",
        "not reusable after that release",
    ):
        add_if_missing(validator_evidence, marker, VALIDATOR_EVIDENCE_PATH, issues)

    template = texts[TEMPLATE_PATH]
    for marker in ("Skill Forge strict inspection", "Validator outcome", "Package self-tests"):
        add_if_missing(template, marker, TEMPLATE_PATH, issues)
    for marker in ("Compact", "Standard", "Release", "complete G01–G23"):
        add_if_missing(template, marker, TEMPLATE_PATH, issues)
    if not all(gate_id in template for gate_id in ("G09", "G10", "G11")):
        issues.append("report template must keep helper, official-validator, and self-test gates separate")
    for marker in ("validator_outcome", "gate_result", "compatibility_result", "quality_policy_result", "target_contracts"):
        add_if_missing(template, marker, TEMPLATE_PATH, issues)
    for marker in (
        "Requested outcome phases",
        "Requested host surfaces",
        "Selected canonical profile(s)",
        "Per-profile results",
        "Overall cross-profile verdict",
        "without changing or hiding any member result",
    ):
        add_if_missing(template, marker, TEMPLATE_PATH, issues)
    for marker in (
        "untrusted evidence only",
        "network default-deny",
        "source read-only",
        "scratch-only writes",
        "redacted_fingerprint",
        "never raw secrets or sensitive PII",
        "Static simulation",
        "Synthetic execution",
        "Live host observation",
        "exact artifact",
        "explicit packaging authority",
        "bootstrap transition evidence",
        "independent_evaluator_policy.bootstrap_transition",
        "never reuse it after `v2.0.0`",
    ):
        add_if_missing(template, marker, TEMPLATE_PATH, issues)
    for marker in EXPECTED_PRESSURE_RESULT_FIELDS:
        add_if_missing(template, marker, TEMPLATE_PATH, issues)

    checklist = texts[CHECKLIST_PATH]
    for marker in (
        "untrusted evidence only",
        "network default-deny",
        "source read-only",
        "scratch-only writes",
        "redacted_fingerprint",
        "plain hash of low-entropy sensitive data",
        "Fail > Not Assessed > Partial > Pass",
        "exact artifact",
        "Installed runtime",
        "explicit packaging authority",
        "independent_evaluator_policy.bootstrap_transition",
        "bootstrap transition evidence",
        "not reusable after `v2.0.0`",
    ):
        add_if_missing(checklist, marker, CHECKLIST_PATH, issues)

    for marker in (
        "--bootstrap-schema-transition 5:6",
        "--bootstrap-release-tag v2.0.0",
        "bootstrap transition evidence",
        "cannot be reused after",
    ):
        add_if_missing(texts[README_PATH], marker, README_PATH, issues)

    for marker in (
        "bootstrap transition evidence",
        "independent_evaluator_policy.bootstrap_transition",
        "not an independent schema-6 pass",
    ):
        add_if_missing(
            texts[AUDIT_CHECKLIST_PATH], marker, AUDIT_CHECKLIST_PATH, issues
        )

    rubric = texts[RUBRIC_PATH]
    for marker in (
        "Static simulation",
        "Synthetic execution",
        "Live host observation",
        "Fail > Not Assessed > Partial > Pass",
        "Installed runtime",
    ):
        add_if_missing(rubric, marker, RUBRIC_PATH, issues)

    example = texts[EXAMPLE_PATH]
    if "**Target profile:** Portable" not in example:
        issues.append("example report must use Portable for a generic/no-host target")
    if "Unknown" in example:
        issues.append("example report must not use Unknown as a generic target profile")
    if "**Validator outcome:** Unavailable" not in example or "**Gate result derived from validator outcome:** Not Applicable" not in example:
        issues.append("example report must map unavailable optional validation to Not Applicable")
    if "**Score cap applied:** 79/100" not in example:
        issues.append("example report must state the applicable 79/100 score cap")
    for marker in ("**Validator outcome:**", "**Gate result derived from validator outcome:**", "**Compatibility result:**", "**Quality-policy result:**", "Partial rows count as completed coverage"):
        add_if_missing(example, marker, EXAMPLE_PATH, issues)
    for marker in (
        "Static simulation",
        "Synthetic execution",
        "Live host observation",
        "exact artifact",
        "Fail > Not Assessed > Partial > Pass",
    ):
        add_if_missing(example, marker, EXAMPLE_PATH, issues)

    gate_rows = parse_example_gate_rows(example, issues)
    validate_example_gate_rows(gate_rows, issues)
    validate_example_executive_rollups(example, contract, gate_rows, issues)
    validate_example_release_verdict(example, contract, gate_rows, issues)
    validate_example_safety_consistency(example, issues)
    counts = parse_example_counts(example, issues)
    if counts and gate_rows:
        actual = {result: [gate_result for _, gate_result in gate_rows].count(result) for result in EXPECTED_RESULTS}
        if any(counts.get(result) != actual[result] for result in EXPECTED_RESULTS):
            issues.append("example report required-gate counts do not match its detailed matrix")
        applicable = len(gate_rows) - actual["Not Applicable"]
        if counts.get("Applicable") != applicable:
            issues.append("example report applicable-gate count does not match its detailed matrix")
    try:
        from score_audit import score_audit
        payload = re.search(r"```json scorecard\n(.*?)\n```", example, re.DOTALL)
        if not payload:
            raise ValueError("missing scorecard")
        card = json.loads(payload.group(1))
        scoring = json.loads((REPO_ROOT / "references/scoring-contract.json").read_text())
        computed = score_audit(card, scoring)
        for label, key in (("Quality score", "quality_score"), ("Assessed-only score", "assessed_only_score"), ("Legacy policy score", "legacy_policy_score")):
            if f"**{label}:** {computed[key]}/100" not in example:
                issues.append("example report scorecard total does not match " + label)
        if {row["id"]: row["result"] for row in card["release"]["required_gates"]} != dict(gate_rows):
            issues.append("example scorecard gates differ from detailed matrix")
        if "**Release verdict:** " + computed["release_verdict"] not in example:
            issues.append("example scorecard release verdict mismatch")
    except (ValueError, TypeError, KeyError, OSError) as exc:
        issues.append("example report scorecard invalid: " + type(exc).__name__)
    if "### High" not in example or "**Evidence status:** Verified" not in example:
        issues.append("example report must include a Verified High-severity issue")
    if "**Release verdict:** Fail" not in example:
        issues.append("example report must reconcile its failed gates to a Fail release verdict")
    if "11/10" in texts[RUBRIC_PATH] or "11/10" in texts[TEMPLATE_PATH]:
        issues.append("rating references must not advertise an 11/10 result")

    sandbox_policy = (
        "network default-deny, credentials absent, source read-only, scratch-only writes, "
        "bounded process/time/memory, and external side effects forbidden"
    )
    sandbox_fallback = "required evidence is Not Assessed"
    for document in (README_PATH, AUDIT_CHECKLIST_PATH, PRESSURE_PATH):
        normalized = re.sub(r"\s+", " ", texts[document])
        add_if_missing(normalized, sandbox_policy, document, issues)
        add_if_missing(normalized, sandbox_fallback, document, issues)
        if "where possible" in texts[document].lower():
            issues.append(f"{repo_relative(document)} must not weaken sandbox controls with 'where possible'")

    standard_release_markers = {
        RUBRIC_PATH: ("without loading the full Release contract", "source contract validator keeps"),
        TEMPLATE_PATH: ("without loading the full Release contract", "mirrored Standard rules"),
        PLATFORM_PATH: ("without loading the full Release contract", "Release audits load"),
    }
    for document, markers in standard_release_markers.items():
        normalized = re.sub(r"\s+", " ", texts[document])
        for marker in markers:
            add_if_missing(normalized, marker, document, issues)

    openai_metadata = texts[OPENAI_METADATA_PATH]
    add_if_missing(
        openai_metadata,
        'default_prompt: "Use $skill-forge to run a read-only Standard audit of this Skill package."',
        OPENAI_METADATA_PATH,
        issues,
    )


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate the Skill Forge audit/report contract.")
    parser.add_argument("--json", action="store_true", help="emit a machine-readable result")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    issues: List[str] = []
    try:
        data = load_contract_json(CONTRACT_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, DuplicateJsonKeyError) as exc:
        issues.append(f"cannot load references/audit-contract.json: {exc}")
        data = {}
    contract = validate_contract(data, issues)
    try:
        scoring = load_contract_json((REPO_ROOT / "references/scoring-contract.json").read_text(encoding="utf-8"))
        validate_scoring_contract(scoring, issues)
    except (OSError, ValueError) as exc:
        issues.append("cannot load scoring contract: " + str(exc))
    validate_documents(contract, issues)
    validate_inspector_documentation(issues)
    validate_skill_control_plane(issues)
    validate_runtime_boundary_contract(issues)
    report = {
        "status": "pass" if not issues else "fail",
        "contract": repo_relative(CONTRACT_PATH),
        "issue_count": len(issues),
        "issues": issues,
    }
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    elif issues:
        print("Audit contract: FAIL")
        for issue in issues:
            print(f"- {issue}")
    else:
        print("Audit contract: PASS (23 gates, 11 pressure categories, 5 executive rows)")
    return 0 if not issues else 1


if __name__ == "__main__":
    raise SystemExit(main())
