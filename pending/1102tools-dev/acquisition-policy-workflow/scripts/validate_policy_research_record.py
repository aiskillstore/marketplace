#!/usr/bin/env python3
"""Validate an acquisition-policy research record without network access."""

from __future__ import annotations

import argparse
import ipaddress
import json
import math
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlparse


REQUIRED = {
    "schema_version",
    "skill",
    "workflow_mode",
    "request",
    "scope",
    "document_register",
    "capabilities",
    "queries",
    "evidence",
    "policy_items",
    "findings",
    "timeline",
    "stakeholder_positions",
    "limitations",
    "conflicts",
    "unresolved_questions",
    "outputs",
    "validation",
}
LIST_FIELDS = REQUIRED - {
    "schema_version",
    "skill",
    "workflow_mode",
    "request",
    "scope",
    "validation",
}
AUDIENCE_LENSES = {"government", "industry", "neutral"}
SOURCE_CLASSES = {
    "user_document",
    "federal_mcp",
    "official_web",
    "user_statement",
    "calculation",
}
SOURCE_TYPES = {
    "codified_text",
    "federal_register_document",
    "regulations_docket",
    "public_comment",
    "model_deviation",
    "agency_deviation",
    "nonregulatory_guidance",
    "user_policy_document",
    "user_statement",
    "calculation",
}
POLICY_STATUSES = {
    "codified_current",
    "model_deviation",
    "agency_class_deviation",
    "proposed_rule",
    "final_rule_pending_effective",
    "final_rule_effective",
    "withdrawn",
    "superseded",
    "nonregulatory_guidance",
}
NONOPERATIVE_STATUSES = {
    "model_deviation",
    "proposed_rule",
    "final_rule_pending_effective",
    "withdrawn",
    "superseded",
    "nonregulatory_guidance",
}
FINDING_TYPES = {
    "source_fact",
    "user_supplied_fact",
    "inference",
    "documented_status",
}
STATUS_RESOLUTIONS = {"documented_clear", "documented_conflict", "authorized_resolution"}
CONFLICT_STATUSES = {"unresolved", "resolved_by_authorized_official"}
UNRESOLVED_CONTROL_CLAIMS = re.compile(
    r"(?<!does not )\bcontrols\b|(?<!does not )\bgoverns\b|\boperative threshold\b|"
    r"\bapplicable threshold\b|\blegally applies\b",
    re.I,
)
PROVIDERS = {"ecfr", "federal_register", "regulationsgov", "acquisition_gov"}
CAPABILITY_STATUSES = {"available", "missing", "unauthenticated", "limited", "not_required"}
ID_PATTERNS = {
    "evidence": re.compile(r"^E\d{3,}$"),
    "policy_items": re.compile(r"^P\d{3,}$"),
    "findings": re.compile(r"^F\d{3,}$"),
    "stakeholder_positions": re.compile(r"^S\d{3,}$"),
    "conflicts": re.compile(r"^C\d{3,}$"),
}
SECRET_PATTERNS = [
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\b(?:sk|cfat|SAM)-[A-Za-z0-9_-]{16,}\b", re.I),
    re.compile(r"(?:api[_ -]?key|secret|token|password)\s*[:=]\s*[^\s,}\]]{8,}", re.I),
]
UNSAFE_QUERY_KEYS = {
    "document_text",
    "full_text",
    "source_selection_information",
    "proprietary_data",
    "classified_data",
    "cui",
    "password",
    "api_key",
    "token",
    "secret",
    "local_path",
    "file_path",
}
SENSITIVE_URL_KEYS = {
    "access_token",
    "api_key",
    "apikey",
    "auth",
    "authorization",
    "key",
    "password",
    "secret",
    "sig",
    "signature",
    "token",
    "x-amz-credential",
    "x-amz-signature",
}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SHA_RE = re.compile(r"^(?:[0-9a-f]{64})?$", re.I)


def walk(value: Any):
    if isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from walk(item)
    elif isinstance(value, list):
        for item in value:
            yield from walk(item)
    else:
        yield value


def valid_date(value: object, *, allow_empty: bool = True) -> bool:
    if value in (None, ""):
        return allow_empty
    if not isinstance(value, str) or not DATE_RE.fullmatch(value):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def public_url_failure(value: str) -> str | None:
    try:
        parsed = urlparse(value)
    except ValueError:
        return "is not a valid URL"
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return "must be a public HTTP(S) URL"
    host = parsed.hostname.lower().rstrip(".")
    if host == "localhost" or host.endswith((".local", ".internal", ".localhost")):
        return "must not use a local or internal host"
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        address = None
    if address and not address.is_global:
        return "must not use a private, loopback, reserved, or link-local address"
    query_keys = {key.lower() for key, _ in parse_qsl(parsed.query, keep_blank_values=True)}
    if query_keys & SENSITIVE_URL_KEYS:
        return "must not contain signed, credential, or secret query parameters"
    if parsed.username or parsed.password:
        return "must not contain URL credentials"
    return None


def required_string(item: dict[str, Any], field: str, label: str, failures: list[str]) -> None:
    if not isinstance(item.get(field), str):
        failures.append(f"{label}.{field} must be a string")


def validate_record(record: Any) -> dict[str, Any]:
    failures: list[str] = []
    if not isinstance(record, dict):
        return {"status": "fail", "failures": ["record must be a JSON object"]}

    missing = sorted(REQUIRED - set(record))
    extra = sorted(set(record) - REQUIRED)
    if missing:
        failures.append(f"missing top-level fields: {', '.join(missing)}")
    if extra:
        failures.append(f"unknown top-level fields: {', '.join(extra)}")
    if record.get("schema_version") != "1.1":
        failures.append("schema_version must be '1.1'")
    if record.get("skill") != "acquisition-policy-workflow":
        failures.append("skill must be acquisition-policy-workflow")
    if not isinstance(record.get("workflow_mode"), str) or not record.get("workflow_mode", "").strip():
        failures.append("workflow_mode must be a non-empty string")
    for field in sorted(LIST_FIELDS):
        if not isinstance(record.get(field), list):
            failures.append(f"{field} must be a list")

    request = record.get("request", {})
    if not isinstance(request, dict):
        failures.append("request must be an object")
        request = {}
    for field in ("question", "approved_scope", "approved_at"):
        required_string(request, field, "request", failures)
    if request.get("audience_lens") not in AUDIENCE_LENSES:
        failures.append("request.audience_lens must be government, industry, or neutral")

    scope = record.get("scope", {})
    if not isinstance(scope, dict):
        failures.append("scope must be an object")
        scope = {}
    if not valid_date(scope.get("as_of_date"), allow_empty=False):
        failures.append("scope.as_of_date must be a valid YYYY-MM-DD date")
    far_parts = scope.get("far_parts")
    if not isinstance(far_parts, list) or any(not isinstance(part, int) or part < 1 or part > 53 for part in far_parts):
        failures.append("scope.far_parts must contain integers from 1 through 53")
    procurement_dates = scope.get("procurement_dates")
    if not isinstance(procurement_dates, dict):
        failures.append("scope.procurement_dates must be an object")
    else:
        for key, value in procurement_dates.items():
            if not isinstance(key, str) or not valid_date(value):
                failures.append("scope.procurement_dates values must be empty or valid YYYY-MM-DD dates")
                break

    for index, item in enumerate(record.get("document_register", [])):
        if not isinstance(item, dict):
            failures.append(f"document_register[{index}] must be an object")
            continue
        if item.get("trust") != "untrusted_evidence":
            failures.append(f"document_register[{index}].trust must be untrusted_evidence")
        if not isinstance(item.get("embedded_instructions_ignored"), bool):
            failures.append(f"document_register[{index}].embedded_instructions_ignored must be boolean")

    for index, item in enumerate(record.get("capabilities", [])):
        if not isinstance(item, dict):
            failures.append(f"capabilities[{index}] must be an object")
            continue
        for field in ("name", "version"):
            required_string(item, field, f"capabilities[{index}]", failures)
        if item.get("status") not in CAPABILITY_STATUSES:
            failures.append(f"capabilities[{index}].status is not approved")

    ids: dict[str, set[str]] = {name: set() for name in ID_PATTERNS}
    item_maps: dict[str, dict[str, dict[str, Any]]] = {name: {} for name in ID_PATTERNS}
    for collection, pattern in ID_PATTERNS.items():
        values = record.get(collection, [])
        if not isinstance(values, list):
            continue
        for index, item in enumerate(values):
            if not isinstance(item, dict):
                failures.append(f"{collection}[{index}] must be an object")
                continue
            item_id = item.get("id")
            if not isinstance(item_id, str) or not pattern.fullmatch(item_id):
                failures.append(f"{collection}[{index}].id has an invalid format")
                continue
            if item_id in ids[collection]:
                failures.append(f"duplicate ID: {item_id}")
            ids[collection].add(item_id)
            item_maps[collection][item_id] = item

    for index, item in enumerate(record.get("evidence", [])):
        if not isinstance(item, dict):
            continue
        if item.get("source_class") not in SOURCE_CLASSES:
            failures.append(f"evidence[{index}].source_class is not approved")
        if item.get("source_type") not in SOURCE_TYPES:
            failures.append(f"evidence[{index}].source_type is not approved")
        for field in (
            "title",
            "locator",
            "canonical_url",
            "publication_date",
            "effective_date",
            "retrieved_at",
            "fact",
            "limitations",
            "content_sha256",
        ):
            required_string(item, field, f"evidence[{index}]", failures)
        for field in ("publication_date", "effective_date"):
            if not valid_date(item.get(field)):
                failures.append(f"evidence[{index}].{field} must be empty or YYYY-MM-DD")
        url = item.get("canonical_url")
        if isinstance(url, str) and url:
            problem = public_url_failure(url)
            if problem:
                failures.append(f"evidence[{index}].canonical_url {problem}")
        sha = item.get("content_sha256")
        if isinstance(sha, str) and not SHA_RE.fullmatch(sha):
            failures.append(f"evidence[{index}].content_sha256 must be empty or 64 hexadecimal characters")

    for index, item in enumerate(record.get("policy_items", [])):
        if not isinstance(item, dict):
            continue
        status = item.get("status")
        if status not in POLICY_STATUSES:
            failures.append(f"policy_items[{index}].status is not approved")
        for field in ("citation", "agency", "text", "effective_from", "effective_to", "applicability_summary"):
            required_string(item, field, f"policy_items[{index}]", failures)
        for field in ("effective_from", "effective_to"):
            if not valid_date(item.get(field)):
                failures.append(f"policy_items[{index}].{field} must be empty or YYYY-MM-DD")
        operative = item.get("operative_for_agency")
        if not isinstance(operative, bool):
            failures.append(f"policy_items[{index}].operative_for_agency must be boolean")
        elif operative and status in NONOPERATIVE_STATUSES:
            failures.append(f"policy_items[{index}] cannot mark {status} operative for an agency")
        refs = item.get("evidence_ids")
        if not isinstance(refs, list) or not refs:
            failures.append(f"policy_items[{index}] must cite at least one evidence ID")
            refs = []
        unknown = sorted(set(refs) - ids["evidence"])
        if unknown:
            failures.append(f"policy_items[{index}] cites unknown evidence IDs: {', '.join(unknown)}")
        if status == "agency_class_deviation" and operative:
            if not str(item.get("agency", "")).strip():
                failures.append(f"policy_items[{index}] operative agency deviation must name the agency")
            source_types = {
                item_maps["evidence"][ref].get("source_type")
                for ref in refs
                if ref in item_maps["evidence"]
            }
            if "agency_deviation" not in source_types:
                failures.append(f"policy_items[{index}] operative agency deviation must cite agency_deviation evidence")

    unresolved_conflict_ids: set[str] = set()
    for index, item in enumerate(record.get("conflicts", [])):
        if not isinstance(item, dict):
            continue
        required_string(item, "issue", f"conflicts[{index}]", failures)
        status = item.get("status")
        if status not in CONFLICT_STATUSES:
            failures.append(f"conflicts[{index}].status is not approved")
        refs = item.get("evidence_ids")
        if not isinstance(refs, list) or len(refs) < 2:
            failures.append(f"conflicts[{index}] must cite at least two evidence IDs")
            refs = []
        unknown = sorted(set(refs) - ids["evidence"])
        if unknown:
            failures.append(f"conflicts[{index}] cites unknown evidence IDs: {', '.join(unknown)}")
        for field in ("resolution", "resolved_by", "resolved_at"):
            required_string(item, field, f"conflicts[{index}]", failures)
        conflict_id = item.get("id")
        if status == "unresolved":
            if isinstance(conflict_id, str):
                unresolved_conflict_ids.add(conflict_id)
            if any(str(item.get(field, "")).strip() for field in ("resolution", "resolved_by", "resolved_at")):
                failures.append(f"conflicts[{index}] unresolved conflict must leave resolution fields empty")
        elif status == "resolved_by_authorized_official":
            for field in ("resolution", "resolved_by", "resolved_at"):
                if not str(item.get(field, "")).strip():
                    failures.append(f"conflicts[{index}].{field} is required for authorized resolution")

    documented_conflict_refs: set[str] = set()
    for index, item in enumerate(record.get("findings", [])):
        if not isinstance(item, dict):
            continue
        if item.get("finding_type") not in FINDING_TYPES:
            failures.append(f"findings[{index}].finding_type is not approved")
        required_string(item, "text", f"findings[{index}]", failures)
        evidence_refs = item.get("evidence_ids")
        if not isinstance(evidence_refs, list) or not evidence_refs:
            failures.append(f"findings[{index}] must cite at least one evidence ID")
            evidence_refs = []
        unknown_evidence = sorted(set(evidence_refs) - ids["evidence"])
        if unknown_evidence:
            failures.append(f"findings[{index}] cites unknown evidence IDs: {', '.join(unknown_evidence)}")
        policy_refs = item.get("policy_item_ids")
        if not isinstance(policy_refs, list):
            failures.append(f"findings[{index}].policy_item_ids must be a list")
            policy_refs = []
        unknown_policy = sorted(set(policy_refs) - ids["policy_items"])
        if unknown_policy:
            failures.append(f"findings[{index}] cites unknown policy item IDs: {', '.join(unknown_policy)}")
        if item.get("finding_type") == "documented_status" and not policy_refs:
            failures.append(f"findings[{index}] documented_status must cite a policy item")
        if item.get("finding_type") == "documented_status":
            status_resolution = item.get("status_resolution")
            if status_resolution not in STATUS_RESOLUTIONS:
                failures.append(f"findings[{index}].status_resolution is not approved")
            conflict_refs = item.get("conflict_ids")
            if not isinstance(conflict_refs, list):
                failures.append(f"findings[{index}].conflict_ids must be a list")
                conflict_refs = []
            unknown_conflicts = sorted(set(conflict_refs) - ids["conflicts"])
            if unknown_conflicts:
                failures.append(f"findings[{index}] cites unknown conflict IDs: {', '.join(unknown_conflicts)}")
            cited_unresolved = set(conflict_refs) & unresolved_conflict_ids
            if cited_unresolved:
                documented_conflict_refs.update(cited_unresolved)
                if status_resolution != "documented_conflict":
                    failures.append(f"findings[{index}] with unresolved conflicts must use documented_conflict")
                if UNRESOLVED_CONTROL_CLAIMS.search(str(item.get("text", ""))):
                    failures.append(f"findings[{index}] makes a controlling-value claim despite an unresolved conflict")
            if status_resolution == "documented_conflict" and not conflict_refs:
                failures.append(f"findings[{index}] documented_conflict must cite at least one conflict ID")
            if status_resolution == "authorized_resolution":
                if not conflict_refs:
                    failures.append(f"findings[{index}] authorized_resolution must cite a conflict ID")
                elif any(
                    item_maps["conflicts"].get(ref, {}).get("status") != "resolved_by_authorized_official"
                    for ref in conflict_refs
                ):
                    failures.append(f"findings[{index}] authorized_resolution requires official resolution of every conflict")

    unreported_conflicts = sorted(unresolved_conflict_ids - documented_conflict_refs)
    if unreported_conflicts:
        failures.append("unresolved conflicts must be reported by a documented_conflict finding: " + ", ".join(unreported_conflicts))
    if unresolved_conflict_ids:
        limitation_text = " ".join(str(item) for item in record.get("limitations", [])).lower()
        has_reserved_boundary = any(
            phrase in limitation_text
            for phrase in ("authorized official", "agency official", "contracting official", "policy official", "legal official")
        )
        if not has_reserved_boundary:
            failures.append("unresolved conflicts require a limitation reserving resolution to an authorized official")

    for index, item in enumerate(record.get("timeline", [])):
        if not isinstance(item, dict):
            failures.append(f"timeline[{index}] must be an object")
            continue
        if not valid_date(item.get("date"), allow_empty=False):
            failures.append(f"timeline[{index}].date must be YYYY-MM-DD")
        for field in ("event", "status"):
            required_string(item, field, f"timeline[{index}]", failures)
        refs = item.get("evidence_ids")
        if not isinstance(refs, list) or not refs:
            failures.append(f"timeline[{index}] must cite at least one evidence ID")
        elif set(refs) - ids["evidence"]:
            failures.append(f"timeline[{index}] cites unknown evidence IDs")

    for index, item in enumerate(record.get("stakeholder_positions", [])):
        if not isinstance(item, dict):
            continue
        for field in ("position", "submitter_type", "sample_method", "limitations"):
            if not isinstance(item.get(field), str) or not item.get(field, "").strip():
                failures.append(f"stakeholder_positions[{index}].{field} must be a non-empty string")
        for field in ("reviewed_count", "returned_count"):
            value = item.get(field)
            if not isinstance(value, int) or value < 0:
                failures.append(f"stakeholder_positions[{index}].{field} must be a nonnegative integer")
        if isinstance(item.get("reviewed_count"), int) and isinstance(item.get("returned_count"), int):
            if item["reviewed_count"] > item["returned_count"]:
                failures.append(f"stakeholder_positions[{index}] reviewed_count exceeds returned_count")
        refs = item.get("evidence_ids")
        if not isinstance(refs, list) or not refs:
            failures.append(f"stakeholder_positions[{index}] must cite at least one evidence ID")
        elif set(refs) - ids["evidence"]:
            failures.append(f"stakeholder_positions[{index}] cites unknown evidence IDs")

    for index, query in enumerate(record.get("queries", [])):
        if not isinstance(query, dict):
            failures.append(f"queries[{index}] must be an object")
            continue
        if query.get("provider") not in PROVIDERS:
            failures.append(f"queries[{index}].provider is not approved")
        for field in ("operation", "retrieved_at", "limitations"):
            required_string(query, field, f"queries[{index}]", failures)
        if not isinstance(query.get("count"), int) or query.get("count", -1) < 0:
            failures.append(f"queries[{index}].count must be a nonnegative integer")
        params = query.get("parameters")
        if not isinstance(params, dict):
            failures.append(f"queries[{index}].parameters must be an object")
            continue
        unsafe = sorted({str(key).lower() for key in params} & UNSAFE_QUERY_KEYS)
        if unsafe:
            failures.append(f"queries[{index}] contains unsafe parameter keys: {', '.join(unsafe)}")
        for key, value in params.items():
            if str(key).lower() not in {"url", "urls"}:
                continue
            urls = value if isinstance(value, list) else [value]
            for url in urls:
                if not isinstance(url, str):
                    failures.append(f"queries[{index}].parameters.{key} must contain URL strings")
                    continue
                problem = public_url_failure(url)
                if problem:
                    failures.append(f"queries[{index}].parameters.{key} {problem}")

    validation = record.get("validation", {})
    if not isinstance(validation, dict):
        failures.append("validation must be an object")
    else:
        for field in ("findings_approved", "brief_approved"):
            if not isinstance(validation.get(field), bool):
                failures.append(f"validation.{field} must be boolean")
        required_string(validation, "executive_summary", "validation", failures)

    serialized = json.dumps(record, sort_keys=True)
    for pattern in SECRET_PATTERNS:
        if pattern.search(serialized):
            failures.append("record appears to contain a credential or secret")
            break
    for value in walk(record):
        if isinstance(value, float) and not math.isfinite(value):
            failures.append("record contains NaN or infinite numeric data")
            break

    return {
        "status": "pass" if not failures else "fail",
        "evidence_count": len(ids["evidence"]),
        "policy_item_count": len(ids["policy_items"]),
        "finding_count": len(ids["findings"]),
        "stakeholder_position_count": len(ids["stakeholder_positions"]),
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        record = json.loads(args.record.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read record: {exc}", file=sys.stderr)
        return 2
    result = validate_record(record)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif result["status"] == "pass":
        print("Acquisition policy record validation passed.")
    else:
        print("VALIDATION FAILED")
        for failure in result["failures"]:
            print(f"- {failure}")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
