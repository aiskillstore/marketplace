#!/usr/bin/env python3
"""Model Intelligence v1: validate evidence datasets, import study reports, and compute deterministic Pareto advisories."""

from __future__ import annotations

import contextlib
import datetime
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import stat
import sys
from typing import Any, Sequence

sys.dont_write_bytecode = True

MAX_DATASET_BYTES = 512 * 1024
MAX_REPORT_BYTES = 16 * 1024 * 1024
SHA256_RE = re.compile(r"^[0-9a-f]{64}\Z")
DATE_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}\Z")
ID_RE = re.compile(r"^[a-z0-9._-]{1,100}\Z")
URI_RE = re.compile(r"^(https://[a-zA-Z0-9_./-]{1,2000}|local://[a-zA-Z0-9_./-]{1,2000})\Z")
SAFE_STR_RE = re.compile(r"^[a-zA-Z0-9._:+-]{1,100}\Z")

TOKEN_DISCLAIMER = (
    "Token observations are telemetry counts only and must never be used to "
    "infer billing, quota, allowance, or general cost savings."
)
VALID_MAINTAINER_DISPOSITIONS = {"collect", "defer", "not-applicable"}
VALID_EVIDENCE_STATES = {
    "inventory-added",
    "inventory-removed",
    "binding-changed",
    "dataset-expired",
    "stale-evidence",
    "missing-evidence",
    "unreviewed",
}
MAX_TRACKED_MODELS = 1000


class ModelIntelligenceError(Exception):
    """Model intelligence validation, parsing, or bounds failure."""


def canonical_bytes(data: Any) -> bytes:
    return json.dumps(
        data, ensure_ascii=True, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def parse_iso_date(date_str: Any, label: str) -> datetime.date:
    if not isinstance(date_str, str) or not DATE_RE.fullmatch(date_str):
        raise ModelIntelligenceError(f"{label} is not a valid ISO date (YYYY-MM-DD): {date_str!r}")
    try:
        year, month, day = map(int, date_str.split("-"))
        return datetime.date(year, month, day)
    except (ValueError, OverflowError) as exc:
        raise ModelIntelligenceError(f"{label} is an invalid calendar date: {date_str!r}") from None


def read_json_file(file_path: Path, max_bytes: int = MAX_DATASET_BYTES) -> tuple[dict[str, Any], str, bytes]:
    target = Path(os.path.abspath(os.fspath(file_path)))
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
    try:
        before = os.lstat(target)
        if not stat.S_ISREG(before.st_mode) or before.st_size > max_bytes:
            raise ModelIntelligenceError(f"file is not a bounded regular file: {target}")
        fd = os.open(target, flags)
        try:
            opened = os.fstat(fd)
            if (
                not stat.S_ISREG(opened.st_mode)
                or (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino)
                or opened.st_size > max_bytes
            ):
                raise ModelIntelligenceError("file changed before reading")
            chunks: list[bytes] = []
            total = 0
            while True:
                chunk = os.read(fd, min(8192, max_bytes + 1 - total))
                if not chunk:
                    break
                chunks.append(chunk)
                total += len(chunk)
                if total > max_bytes:
                    raise ModelIntelligenceError("file exceeded maximum byte size")
        finally:
            os.close(fd)
    except OSError as exc:
        raise ModelIntelligenceError(f"cannot read file safely: {exc}") from exc

    raw = b"".join(chunks)
    digest = hashlib.sha256(raw).hexdigest()
    try:
        parsed = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ModelIntelligenceError(f"file contains invalid JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise ModelIntelligenceError("JSON root must be an object")
    return parsed, digest, raw


def validate_evidence_item(item: Any) -> dict[str, Any]:
    if not isinstance(item, dict):
        raise ModelIntelligenceError("evidence item must be an object")
    required_keys = {
        "id", "provenance_type", "source_uri", "observed_date", "expiry_date",
        "harness", "harness_version", "agy_version", "requested_model",
        "observed_model", "substituted", "effort", "task_taxonomy",
        "sample_size", "calibration_only", "metrics", "telemetry_bindings",
        "confidence", "limitations",
    }
    if set(item) != required_keys:
        raise ModelIntelligenceError("evidence item keys mismatch")
    if not isinstance(item["id"], str) or not ID_RE.fullmatch(item["id"]):
        raise ModelIntelligenceError(f"invalid item id: {item.get('id')!r}")
    if item["provenance_type"] not in {"vendor", "independent", "local"}:
        raise ModelIntelligenceError(f"invalid provenance_type: {item.get('provenance_type')!r}")
    if not isinstance(item["source_uri"], str) or not URI_RE.fullmatch(item["source_uri"]):
        raise ModelIntelligenceError(f"invalid source_uri: {item.get('source_uri')!r}")
    parse_iso_date(item["observed_date"], "observed_date")
    parse_iso_date(item["expiry_date"], "expiry_date")
    for str_field in ("harness", "harness_version", "requested_model", "task_taxonomy"):
        val = item[str_field]
        if not isinstance(val, str) or not SAFE_STR_RE.fullmatch(val):
            raise ModelIntelligenceError(f"invalid string field {str_field}: {val!r}")
    for optional_str_field in ("agy_version", "observed_model"):
        val = item[optional_str_field]
        if val is not None and (not isinstance(val, str) or not SAFE_STR_RE.fullmatch(val)):
            raise ModelIntelligenceError(f"invalid string field {optional_str_field}: {val!r}")
    if item["substituted"] is not None and not isinstance(item["substituted"], bool):
        raise ModelIntelligenceError("substituted must be a boolean or null")
    if item["effort"] not in {"low", "medium", "high", "none", "unspecified"}:
        raise ModelIntelligenceError(f"invalid effort: {item.get('effort')!r}")
    if not isinstance(item["sample_size"], int) or not (1 <= item["sample_size"] <= 10_000_000):
        raise ModelIntelligenceError(f"sample_size must be integer between 1 and 10,000,000: {item.get('sample_size')!r}")
    if not isinstance(item["calibration_only"], bool):
        raise ModelIntelligenceError("calibration_only must be a boolean")

    # Validate metrics
    metrics = item["metrics"]
    if not isinstance(metrics, dict) or set(metrics) != {
        "quality_score", "latency_p50_seconds", "latency_p95_seconds",
        "mean_input_tokens", "mean_output_tokens", "mean_cached_tokens",
        "mean_thinking_tokens",
    }:
        raise ModelIntelligenceError("metrics keys mismatch")

    qual = metrics["quality_score"]
    if qual is not None:
        if not isinstance(qual, (int, float)) or isinstance(qual, bool) or not (0.0 <= float(qual) <= 100.0) or not math.isfinite(qual):
            raise ModelIntelligenceError("quality_score must be between 0 and 100")

    for key, max_val in (
        ("latency_p50_seconds", 1_000_000.0),
        ("latency_p95_seconds", 1_000_000.0),
        ("mean_input_tokens", 1_000_000_000.0),
        ("mean_output_tokens", 1_000_000_000.0),
        ("mean_cached_tokens", 1_000_000_000.0),
        ("mean_thinking_tokens", 1_000_000_000.0),
    ):
        val = metrics[key]
        if val is not None:
            if not isinstance(val, (int, float)) or isinstance(val, bool) or not math.isfinite(val) or not (0.0 <= float(val) <= max_val):
                raise ModelIntelligenceError(f"invalid metric {key}: {val!r}")

    # Validate telemetry bindings
    bindings = item["telemetry_bindings"]
    if not isinstance(bindings, dict) or set(bindings) != {
        "accounting", "tokenizer", "currency", "cost_basis", "estimated_cost_per_task",
    }:
        raise ModelIntelligenceError("telemetry_bindings keys mismatch")
    for str_b in ("accounting", "tokenizer", "currency"):
        val = bindings[str_b]
        if not isinstance(val, str) or not SAFE_STR_RE.fullmatch(val):
            raise ModelIntelligenceError(f"invalid telemetry binding {str_b}: {val!r}")
    if bindings["cost_basis"] not in {None, "observed_billed", "version_bound_list_price"}:
        raise ModelIntelligenceError(f"invalid cost_basis: {bindings.get('cost_basis')!r}")
    cost = bindings["estimated_cost_per_task"]
    if cost is not None:
        if not isinstance(cost, (int, float)) or isinstance(cost, bool) or not math.isfinite(cost) or not (0.0 <= float(cost) <= 1_000_000.0):
            raise ModelIntelligenceError(f"estimated_cost_per_task must be non-negative number up to 1,000,000: {cost!r}")

    if item["confidence"] not in {None, "high", "medium", "low"}:
        raise ModelIntelligenceError("invalid confidence")
    if not item["calibration_only"] and (
        item["agy_version"] is None
        or item["observed_model"] is None
        or item["substituted"] is None
        or item["confidence"] is None
        or bindings["cost_basis"] is None
    ):
        raise ModelIntelligenceError("non-calibration evidence requires complete model and confidence bindings")
    if not isinstance(item["limitations"], list) or len(item["limitations"]) > 100 or not all(
        isinstance(x, str) and 1 <= len(x) <= 1000 for x in item["limitations"]
    ):
        raise ModelIntelligenceError("limitations must be list of up to 100 strings (each <= 1000 chars)")
    return item


def validate_dataset(data: dict[str, Any]) -> dict[str, Any]:
    root_keys = {
        "schema_version", "kind", "dataset_id", "dataset_version",
        "created_date", "freshness_window_days", "expiry_date", "items",
    }
    if not isinstance(data, dict) or set(data) != root_keys:
        raise ModelIntelligenceError("dataset root keys mismatch")
    if data["schema_version"] != 1 or data["kind"] != "agy-model-intelligence-evidence":
        raise ModelIntelligenceError("dataset identity mismatch")
    if not isinstance(data["dataset_id"], str) or not ID_RE.fullmatch(data["dataset_id"]):
        raise ModelIntelligenceError(f"dataset_id is invalid: {data.get('dataset_id')!r}")
    if not isinstance(data["dataset_version"], str) or not (1 <= len(data["dataset_version"]) <= 50):
        raise ModelIntelligenceError("dataset_version is invalid")
    parse_iso_date(data["created_date"], "created_date")
    parse_iso_date(data["expiry_date"], "expiry_date")
    if not isinstance(data["freshness_window_days"], int) or not (1 <= data["freshness_window_days"] <= 730):
        raise ModelIntelligenceError(f"freshness_window_days must be integer between 1 and 730: {data.get('freshness_window_days')!r}")
    if not isinstance(data["items"], list) or len(data["items"]) > 1000:
        raise ModelIntelligenceError("dataset items must be a list of at most 1000 items")

    seen_ids: set[str] = set()
    for item in data["items"]:
        validated = validate_evidence_item(item)
        if validated["id"] in seen_ids:
            raise ModelIntelligenceError(f"duplicate item id: {validated['id']}")
        seen_ids.add(validated["id"])
    return data


def compute_advisory(
    dataset: dict[str, Any],
    dataset_sha: str,
    target_taxonomy: str | None = None,
    reference_date: str | None = None,
) -> dict[str, Any]:
    validate_dataset(dataset)
    if reference_date is None:
        raise ModelIntelligenceError("caller must provide a valid reference_date (YYYY-MM-DD)")
    ref_dt = parse_iso_date(reference_date, "reference_date")

    created_dt = parse_iso_date(dataset["created_date"], "created_date")
    root_expiry_dt = parse_iso_date(dataset["expiry_date"], "expiry_date")
    root_freshness_window = datetime.timedelta(days=dataset["freshness_window_days"])

    all_taxonomies = {item["task_taxonomy"] for item in dataset["items"]}
    if target_taxonomy is None:
        if len(all_taxonomies) == 1:
            target_taxonomy = next(iter(all_taxonomies))
        elif all_taxonomies:
            target_taxonomy = "swe-bench-lite" if "swe-bench-lite" in all_taxonomies else sorted(all_taxonomies)[0]
        else:
            target_taxonomy = "swe-bench-lite"
    elif not isinstance(target_taxonomy, str) or not SAFE_STR_RE.fullmatch(target_taxonomy):
        raise ModelIntelligenceError("target_taxonomy must be a bounded safe identifier")

    matching_items = [item for item in dataset["items"] if item["task_taxonomy"] == target_taxonomy]

    base_advisory: dict[str, Any] = {
        "schema_version": 1,
        "kind": "agy-model-intelligence-advisory",
        "evidence_dataset_sha256": dataset_sha,
        "task_taxonomy": target_taxonomy,
        "recommendation_only": True,
        "applied": False,
        "dispatch_authorized": False,
        "model_change_authorized": False,
        "effort_change_authorized": False,
        "acceptance_authorized": False,
        "git_authorized": False,
        "recommendation": "no_recommendation",
        "pareto_frontier": [],
        "reason_code": "no-comparable-models",
        "rationale": "No comparable models found.",
        "limitations": [
            "Advisory is recommendation-only; all dispatch and execution authority remains with caller.",
            TOKEN_DISCLAIMER,
        ],
        "token_inference_disclaimer": TOKEN_DISCLAIMER,
    }

    # 1. Enforce root dataset expiry and freshness window
    if ref_dt > root_expiry_dt:
        base_advisory["reason_code"] = "expired-evidence"
        base_advisory["rationale"] = f"Dataset root expiry ({dataset['expiry_date']}) exceeded relative to reference date {reference_date}."
        return base_advisory

    if ref_dt > (created_dt + root_freshness_window):
        base_advisory["reason_code"] = "stale-evidence"
        base_advisory["rationale"] = f"Dataset root freshness window ({dataset['freshness_window_days']} days) exceeded relative to reference date {reference_date}."
        return base_advisory

    if not dataset["items"]:
        base_advisory["reason_code"] = "no-comparable-models"
        base_advisory["rationale"] = "Evidence dataset contains zero items."
        return base_advisory

    if not matching_items:
        base_advisory["reason_code"] = "incomparable-taxonomy"
        base_advisory["rationale"] = f"No evidence records found for taxonomy {target_taxonomy!r}."
        return base_advisory

    # 2. Check per-item freshness and expiration
    unexpired_items: list[dict[str, Any]] = []
    for item in matching_items:
        obs_dt = parse_iso_date(item["observed_date"], "observed_date")
        exp_dt = parse_iso_date(item["expiry_date"], "expiry_date")
        if obs_dt <= ref_dt <= exp_dt and ref_dt <= (obs_dt + root_freshness_window):
            unexpired_items.append(item)

    if not unexpired_items:
        base_advisory["reason_code"] = "expired-evidence"
        base_advisory["rationale"] = f"All evidence records for {target_taxonomy!r} are expired or stale relative to {reference_date}."
        return base_advisory

    # 3. Check for calibration-only items
    non_calibration_items = [
        item for item in unexpired_items
        if not item["calibration_only"] and item["sample_size"] >= 30
    ]
    if not non_calibration_items:
        base_advisory["reason_code"] = "calibration-only"
        base_advisory["rationale"] = "Only calibration-only or small-sample evidence is available; no recommendation can be made."
        return base_advisory

    # 4. Check for substituted models
    valid_items = [
        item for item in non_calibration_items
        if not item["substituted"] and item["requested_model"] == item["observed_model"]
    ]
    if not valid_items:
        base_advisory["reason_code"] = "substituted-model"
        base_advisory["rationale"] = "Evidence items contain substituted or mismatched model observations."
        return base_advisory

    # 5. Check comparability bindings across candidates
    first_harness = valid_items[0]["harness"]
    first_harness_ver = valid_items[0]["harness_version"]
    first_agy_ver = valid_items[0]["agy_version"]
    first_provenance = valid_items[0]["provenance_type"]
    first_confidence = valid_items[0]["confidence"]
    first_accounting = valid_items[0]["telemetry_bindings"]["accounting"]
    first_tokenizer = valid_items[0]["telemetry_bindings"]["tokenizer"]
    first_currency = valid_items[0]["telemetry_bindings"]["currency"]
    first_cost_basis = valid_items[0]["telemetry_bindings"]["cost_basis"]

    if any(item["harness"] != first_harness or item["harness_version"] != first_harness_ver for item in valid_items):
        base_advisory["reason_code"] = "incomparable-harness"
        base_advisory["rationale"] = "Candidates use disparate evaluation harnesses."
        return base_advisory

    if any(item["agy_version"] != first_agy_ver for item in valid_items):
        base_advisory["reason_code"] = "incomparable-agy-version"
        base_advisory["rationale"] = "Candidates use disparate agy version bindings."
        return base_advisory

    if any(item["provenance_type"] != first_provenance for item in valid_items):
        base_advisory["reason_code"] = "incomparable-provenance"
        base_advisory["rationale"] = "Candidates use disparate provenance types."
        return base_advisory

    if any(item["confidence"] != first_confidence for item in valid_items):
        base_advisory["reason_code"] = "incomparable-confidence"
        base_advisory["rationale"] = "Candidates use disparate confidence levels."
        return base_advisory

    if any(item["telemetry_bindings"]["accounting"] != first_accounting for item in valid_items):
        base_advisory["reason_code"] = "incomparable-accounting"
        base_advisory["rationale"] = "Candidates use disparate accounting telemetry bindings."
        return base_advisory

    if any(item["telemetry_bindings"]["tokenizer"] != first_tokenizer for item in valid_items):
        base_advisory["reason_code"] = "incomparable-tokenizer"
        base_advisory["rationale"] = "Candidates use disparate tokenizer telemetry bindings."
        return base_advisory

    if any(
        item["telemetry_bindings"]["currency"] != first_currency
        or item["telemetry_bindings"]["cost_basis"] != first_cost_basis
        for item in valid_items
    ):
        base_advisory["reason_code"] = "incomparable-cost-basis"
        base_advisory["rationale"] = "Candidates use disparate cost basis or currency bindings."
        return base_advisory

    # 6. Check metrics completeness on all candidates
    candidates: list[dict[str, Any]] = []
    for item in valid_items:
        m = item["metrics"]
        if (
            m["quality_score"] is None
            or m["latency_p50_seconds"] is None
            or m["mean_input_tokens"] is None
            or m["mean_output_tokens"] is None
            or item["telemetry_bindings"]["estimated_cost_per_task"] is None
        ):
            base_advisory["reason_code"] = "incomplete-evidence"
            base_advisory["rationale"] = f"Candidate {item['id']} contains incomplete metrics."
            return base_advisory

        tot_tok = float(m["mean_input_tokens"] + m["mean_output_tokens"])
        candidates.append({
            "id": item["id"],
            "requested_model": item["requested_model"],
            "effort": item["effort"],
            "quality_score": float(m["quality_score"]),
            "latency_p50_seconds": float(m["latency_p50_seconds"]),
            "mean_total_tokens": float(tot_tok),
            "estimated_cost_per_task": float(item["telemetry_bindings"]["estimated_cost_per_task"]),
            "tradeoff_notes": "",
        })

    if len(candidates) < 2:
        c = candidates[0]
        c["tradeoff_notes"] = f"Single candidate available with quality score {c['quality_score']:.1f}%."
        slug = c["requested_model"] if c["effort"] in {"none", "unspecified"} else f"{c['requested_model']}:{c['effort']}"
        base_advisory["recommendation"] = "no_recommendation"
        base_advisory["reason_code"] = "single-candidate"
        base_advisory["rationale"] = f"Only one comparable non-calibration candidate ({slug}) available for {target_taxonomy}; Pareto advice requires at least two comparable candidates."
        base_advisory["pareto_frontier"] = [c]
        return base_advisory

    # 7. Pareto Evaluation across 4 dimensions:
    # Quality (max), Latency (min), Tokens (min), Cost (min)
    def dominates(a: dict[str, Any], b: dict[str, Any]) -> bool:
        qual_better = a["quality_score"] >= b["quality_score"]
        qual_strict = a["quality_score"] > b["quality_score"]

        lat_better = a["latency_p50_seconds"] <= b["latency_p50_seconds"]
        lat_strict = a["latency_p50_seconds"] < b["latency_p50_seconds"]

        tok_better = a["mean_total_tokens"] <= b["mean_total_tokens"]
        tok_strict = a["mean_total_tokens"] < b["mean_total_tokens"]

        cost_better = a["estimated_cost_per_task"] <= b["estimated_cost_per_task"]
        cost_strict = a["estimated_cost_per_task"] < b["estimated_cost_per_task"]

        weak = qual_better and lat_better and tok_better and cost_better
        strict = qual_strict or lat_strict or tok_strict or cost_strict
        return weak and strict

    frontier: list[dict[str, Any]] = []
    for cand in candidates:
        is_dominated = any(dominates(other, cand) for other in candidates if other["id"] != cand["id"])
        if not is_dominated:
            frontier.append(cand)

    max_qual = max(c["quality_score"] for c in frontier)
    min_lat = min(c["latency_p50_seconds"] for c in frontier)
    min_cost = min(c["estimated_cost_per_task"] for c in frontier)

    for c in frontier:
        notes: list[str] = []
        if c["quality_score"] == max_qual:
            notes.append(f"Highest quality score ({c['quality_score']:.1f}%)")
        if c["latency_p50_seconds"] == min_lat:
            notes.append(f"Lowest latency ({c['latency_p50_seconds']:.1f}s)")
        if c["estimated_cost_per_task"] == min_cost:
            notes.append(f"Lowest estimated cost (${c['estimated_cost_per_task']:.3f})")
        if not notes:
            notes.append(f"Balanced quality ({c['quality_score']:.1f}%)")
        c["tradeoff_notes"] = "; ".join(notes)

    if len(frontier) == 1 and len(candidates) > 1:
        dominant = frontier[0]
        slug = dominant["requested_model"] if dominant["effort"] in {"none", "unspecified"} else f"{dominant['requested_model']}:{dominant['effort']}"
        base_advisory["recommendation"] = slug
        base_advisory["reason_code"] = "pareto-dominant"
        base_advisory["rationale"] = f"Candidate {slug} dominates all other comparable candidates on the Pareto frontier."
        base_advisory["pareto_frontier"] = frontier
    else:
        base_advisory["recommendation"] = "no_recommendation"
        base_advisory["reason_code"] = "pareto-tradeoffs"
        base_advisory["rationale"] = (
            f"Found {len(frontier)} Pareto-optimal candidates offering distinct quality, latency, or cost trade-offs. "
            "No universal winner exists."
        )
        base_advisory["pareto_frontier"] = frontier

    return base_advisory


def _load_swebench_module() -> Any:
    study_path = Path(__file__).resolve(strict=True).parent / "swebench_workflow_study.py"
    if not study_path.is_file():
        raise ModelIntelligenceError(f"canonical swebench_workflow_study module not found at {study_path}")
    spec = importlib.util.spec_from_file_location("swebench_workflow_study", study_path)
    if spec is None or spec.loader is None:
        raise ModelIntelligenceError("cannot load swebench_workflow_study spec")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def import_study_report(
    report_path: Path,
    plan_path: Path,
    results_path: Path,
) -> dict[str, Any]:
    """Issue #78 exact canonical schema and full hash-chain import without fabricated metrics or cross-model ranking."""
    if report_path is None or plan_path is None or results_path is None:
        raise ModelIntelligenceError("import-study requires --report, --plan, and --results")

    plan_data, _plan_sha, plan_raw = read_json_file(plan_path, max_bytes=MAX_REPORT_BYTES)
    results_data, _results_sha, results_raw = read_json_file(results_path, max_bytes=MAX_REPORT_BYTES)
    report_data, report_sha, _report_raw = read_json_file(report_path, max_bytes=MAX_REPORT_BYTES)
    if (
        report_data.get("plan_sha256") != _plan_sha
        or report_data.get("imported_results_sha256") != _results_sha
    ):
        raise ModelIntelligenceError("study report is not bound to the supplied plan and imported results")

    swe = _load_swebench_module()
    try:
        validated_plan = swe.validate_plan(plan_data, require_binding=True)
        validated_imported = swe.validate_imported(results_data, validated_plan, plan_raw)
        validated_report = swe.validate_report(report_data, validated_plan, plan_raw, validated_imported, results_raw)
    except (Exception, SystemExit) as exc:
        raise ModelIntelligenceError(f"canonical study validation failure: {exc}") from exc

    denominators = validated_report.get("denominators", {})
    planned_tasks = denominators.get("planned_tasks", len(validated_plan.get("tasks", [])))

    agy_model = validated_plan.get("agy_model")
    if not isinstance(agy_model, str) or not SAFE_STR_RE.fullmatch(agy_model):
        raise ModelIntelligenceError(f"invalid agy_model in study plan: {agy_model!r}")

    agy_effort = validated_plan.get("agy_effort")
    if agy_effort not in {"low", "medium", "high", "none", "unspecified"}:
        raise ModelIntelligenceError(f"invalid agy_effort in study plan: {agy_effort!r}")

    dataset_rev = validated_plan.get("dataset_revision", "study")
    if not isinstance(dataset_rev, str) or not SAFE_STR_RE.fullmatch(dataset_rev):
        dataset_rev = "study"

    agy_bindings = validated_plan["telemetry_bindings"]["agy"]
    created_date = datetime.date.today().isoformat()
    expiry_date = (datetime.date.today() + datetime.timedelta(days=90)).isoformat()

    item_id = f"swebench-study-{report_sha[:12]}"
    items = [{
        "id": item_id,
        "provenance_type": "local",
        "source_uri": f"local://swebench-workflow-study/{report_sha}",
        "observed_date": created_date,
        "expiry_date": expiry_date,
        "harness": "swebench-workflow-study-v1",
        "harness_version": "1.0.0",
        "agy_version": None,
        "requested_model": agy_model,
        "observed_model": None,
        "substituted": None,
        "effort": agy_effort,
        "task_taxonomy": f"swebench-{dataset_rev}",
        "sample_size": planned_tasks,
        "calibration_only": True,
        "metrics": {
            "quality_score": None,
            "latency_p50_seconds": None,
            "latency_p95_seconds": None,
            "mean_input_tokens": None,
            "mean_output_tokens": None,
            "mean_cached_tokens": None,
            "mean_thinking_tokens": None,
        },
        "telemetry_bindings": {
            "accounting": agy_bindings["accounting"],
            "tokenizer": agy_bindings["tokenizer"],
            "currency": agy_bindings["currency"],
            "cost_basis": None,
            "estimated_cost_per_task": None,
        },
        "confidence": None,
        "limitations": [
            f"Imported from SWE-bench workflow study report SHA-256: {report_sha}.",
            f"Canonical plan SHA-256: {_plan_sha}; imported results SHA-256: {_results_sha}.",
            "The study does not attest the observed model, agy version, substitution status, model-level quality, latency percentiles, token means, cost, or confidence.",
            "This calibration-only provenance record is excluded from model ranking.",
            TOKEN_DISCLAIMER,
        ],
    }]

    dataset = {
        "schema_version": 1,
        "kind": "agy-model-intelligence-evidence",
        "dataset_id": f"imported-study-{report_sha[:8]}",
        "dataset_version": "1.0.0",
        "created_date": created_date,
        "freshness_window_days": 90,
        "expiry_date": expiry_date,
        "items": items,
    }
    return validate_dataset(dataset)


def _extract_model_inventory(
    data: dict[str, Any], label: str = "inventory"
) -> tuple[set[str], dict[str, Any], str, dict[str, Any]]:
    """Extract public model slugs, per-model bindings, source type, and metadata from an inventory binding or matrix dict."""
    if not isinstance(data, dict):
        raise ModelIntelligenceError(f"{label} must be a JSON object")

    meta: dict[str, Any] = {}
    model_bindings: dict[str, Any] = {}
    slugs: set[str] = set()

    source_families = sum(
        (
            "slugs" in data,
            "adjustable_models" in data or "fixed_models" in data,
            "models" in data,
        )
    )
    if source_families > 1:
        raise ModelIntelligenceError(f"{label} mixes incompatible inventory structures")

    if "slugs" in data:
        source_type = "inventory_binding"
        if data.get("schema_version") != 1 or isinstance(data.get("schema_version"), bool):
            raise ModelIntelligenceError(f"{label} has unsupported schema_version")
        raw_slugs = data.get("slugs")
        if not isinstance(raw_slugs, list) or len(raw_slugs) > MAX_TRACKED_MODELS or not raw_slugs:
            raise ModelIntelligenceError(
                f"{label} slugs must be a non-empty list of at most {MAX_TRACKED_MODELS} items"
            )
        for slug in raw_slugs:
            if not isinstance(slug, str) or not SAFE_STR_RE.fullmatch(slug):
                raise ModelIntelligenceError(f"{label} contains invalid model slug: {slug!r}")
            if slug in slugs:
                raise ModelIntelligenceError(f"{label} contains duplicate slugs")
            slugs.add(slug)
            model_bindings[slug] = {
                "model_id": slug,
            }
        meta = {
            "agy_version": data.get("agy_version"),
            "reviewed_source_revision": data.get("reviewed_source_revision"),
            "source_sha256": data.get("source_sha256"),
            "version_binding_sha256": data.get("version_binding_sha256"),
            "capture_record_sha256": data.get("capture_record_sha256"),
            "inventory_normalized_sha256": data.get("inventory_normalized_sha256"),
        }
    elif "adjustable_models" in data or "fixed_models" in data:
        source_type = "model_matrix"
        if data.get("schema_version") != 1 or isinstance(data.get("schema_version"), bool):
            raise ModelIntelligenceError(f"{label} has unsupported schema_version")
        adj = data.get("adjustable_models", [])
        fixed = data.get("fixed_models", [])
        if not isinstance(adj, list) or not isinstance(fixed, list):
            raise ModelIntelligenceError(f"{label} models must be lists")
        if len(adj) + len(fixed) > MAX_TRACKED_MODELS:
            raise ModelIntelligenceError(f"{label} model lists exceed maximum allowed length")
        seen_slugs: set[str] = set()
        seen_models: set[str] = set()
        for row in adj:
            if not isinstance(row, dict) or "resolutions" not in row or not isinstance(row["resolutions"], dict) or "model" not in row:
                raise ModelIntelligenceError(f"invalid adjustable model row in {label}")
            base_m = row["model"]
            if not isinstance(base_m, str) or not SAFE_STR_RE.fullmatch(base_m):
                raise ModelIntelligenceError(f"{label} contains invalid model name: {base_m!r}")
            if base_m in seen_models:
                raise ModelIntelligenceError(f"{label} contains duplicate model name: {base_m!r}")
            seen_models.add(base_m)
            unsupported = row.get("unsupported_efforts", [])
            if not isinstance(unsupported, list):
                raise ModelIntelligenceError(f"invalid unsupported_efforts in {label}")
            seen_unsupported: set[str] = set()
            for u in unsupported:
                if not isinstance(u, str) or not SAFE_STR_RE.fullmatch(u):
                    raise ModelIntelligenceError(f"invalid unsupported effort string in {label}")
                if u in seen_unsupported:
                    raise ModelIntelligenceError(f"duplicate unsupported effort in {label}")
                seen_unsupported.add(u)
            unsupported_sorted = sorted(unsupported)
            if not row["resolutions"] or len(row["resolutions"]) > MAX_TRACKED_MODELS:
                raise ModelIntelligenceError(f"invalid resolutions bound in {label}")
            for eff, res_slug in row["resolutions"].items():
                if not isinstance(eff, str) or not SAFE_STR_RE.fullmatch(eff):
                    raise ModelIntelligenceError(f"{label} contains invalid effort key: {eff!r}")
                if not isinstance(res_slug, str) or not SAFE_STR_RE.fullmatch(res_slug):
                    raise ModelIntelligenceError(f"{label} contains invalid resolution slug: {res_slug!r}")
                if res_slug in seen_slugs:
                    raise ModelIntelligenceError(f"{label} contains duplicate resolution slug: {res_slug!r}")
                seen_slugs.add(res_slug)
                slugs.add(res_slug)
                if len(slugs) > MAX_TRACKED_MODELS:
                    raise ModelIntelligenceError(f"{label} contains too many model slugs")
                model_bindings[res_slug] = {
                    "base_model": base_m,
                    "effort": eff,
                    "unsupported_efforts": unsupported_sorted,
                }
        for row in fixed:
            if not isinstance(row, dict) or "model_slug" not in row:
                raise ModelIntelligenceError(f"invalid fixed model row in {label}")
            f_slug = row["model_slug"]
            if not isinstance(f_slug, str) or not SAFE_STR_RE.fullmatch(f_slug):
                raise ModelIntelligenceError(f"{label} contains invalid fixed model slug: {f_slug!r}")
            if f_slug in seen_slugs:
                raise ModelIntelligenceError(f"{label} contains duplicate fixed model slug: {f_slug!r}")
            seen_slugs.add(f_slug)
            slugs.add(f_slug)
            if len(slugs) > MAX_TRACKED_MODELS:
                raise ModelIntelligenceError(f"{label} contains too many model slugs")
            classification = row.get("classification")
            if classification is not None and (not isinstance(classification, str) or not SAFE_STR_RE.fullmatch(classification)):
                raise ModelIntelligenceError(f"invalid classification in {label}")
            model_bindings[f_slug] = {
                "classification": classification,
            }
        meta = {
            "resolution_status": data.get("resolution_status"),
            "inventory": data.get("inventory"),
        }
        if not slugs:
            raise ModelIntelligenceError(f"{label} must contain at least one model slug")
    elif "models" in data:
        source_type = "models_list"
        raw_models = data["models"]
        if not isinstance(raw_models, list) or len(raw_models) > MAX_TRACKED_MODELS or not raw_models:
            raise ModelIntelligenceError(
                f"{label} models must be a non-empty list of at most {MAX_TRACKED_MODELS} items"
            )
        for m in raw_models:
            if not isinstance(m, str) or not SAFE_STR_RE.fullmatch(m):
                raise ModelIntelligenceError(f"{label} contains invalid model slug: {m!r}")
            if m in slugs:
                raise ModelIntelligenceError(f"{label} contains duplicate models")
            slugs.add(m)
            model_bindings[m] = {
                "model_id": m,
                "version": data.get("version"),
            }
        meta = {
            "version": data.get("version"),
        }
    else:
        raise ModelIntelligenceError(f"unrecognized {label} structure; expected inventory binding or matrix")

    return slugs, model_bindings, source_type, meta


def _get_reviewed_inventory_slugs() -> set[str]:
    default_binding = Path(__file__).resolve().parent.parent / "compat" / "agy-models-inventory-binding.json"
    try:
        data, _, _ = read_json_file(default_binding)
        slugs, _, _, _ = _extract_model_inventory(data, "default_inventory")
    except ModelIntelligenceError as exc:
        raise ModelIntelligenceError("reviewed inventory evidence is unavailable") from exc
    return slugs


def validate_benchmark_review_output(result: dict[str, Any]) -> dict[str, Any]:
    """Strict schema validation for benchmark review output."""
    if not isinstance(result, dict):
        raise ModelIntelligenceError("benchmark review output must be a JSON object")

    allowed_keys = {
        "schema_version",
        "kind",
        "status",
        "evidence_dataset_sha256",
        "reference_date",
        "reviews_due",
        "maintainer_disposition",
        "applied",
        "dispatch_authorized",
        "model_change_authorized",
        "effort_change_authorized",
        "acceptance_authorized",
        "git_authorized",
        "benchmark_run_authorized",
        "provider_call_authorized",
        "limitations",
        "token_inference_disclaimer",
    }
    if set(result.keys()) != allowed_keys:
        raise ModelIntelligenceError("benchmark review output keys do not match strict schema")

    if result["schema_version"] != 1 or isinstance(result["schema_version"], bool):
        raise ModelIntelligenceError("benchmark review schema_version must be integer 1")
    if result["kind"] != "agy-benchmark-review-tracker":
        raise ModelIntelligenceError("benchmark review kind must be agy-benchmark-review-tracker")
    if result["status"] not in {"benchmark-review-due", "unchanged"}:
        raise ModelIntelligenceError("benchmark review status must be benchmark-review-due or unchanged")

    if result["evidence_dataset_sha256"] is not None:
        if not isinstance(result["evidence_dataset_sha256"], str) or not SHA256_RE.fullmatch(result["evidence_dataset_sha256"]):
            raise ModelIntelligenceError("invalid evidence_dataset_sha256")

    parse_iso_date(result["reference_date"], "benchmark review reference_date")

    if not isinstance(result["reviews_due"], list) or len(result["reviews_due"]) > MAX_TRACKED_MODELS:
        raise ModelIntelligenceError(f"reviews_due must be a list of at most {MAX_TRACKED_MODELS} items")

    seen_review_models: set[str] = set()
    for item in result["reviews_due"]:
        if not isinstance(item, dict):
            raise ModelIntelligenceError("reviews_due item must be a dict")
        if set(item.keys()) != {"model_id", "evidence_state"}:
            raise ModelIntelligenceError("reviews_due item must contain strictly model_id and evidence_state")
        if not isinstance(item["model_id"], str) or not SAFE_STR_RE.fullmatch(item["model_id"]):
            raise ModelIntelligenceError("invalid model_id in reviews_due")
        if item["model_id"] in seen_review_models:
            raise ModelIntelligenceError("duplicate model_id in reviews_due")
        seen_review_models.add(item["model_id"])
        if item["evidence_state"] not in VALID_EVIDENCE_STATES:
            raise ModelIntelligenceError("invalid evidence_state in reviews_due")

    if [item["model_id"] for item in result["reviews_due"]] != sorted(seen_review_models):
        raise ModelIntelligenceError("reviews_due must be ordered by model_id")
    if (result["status"] == "benchmark-review-due") != bool(result["reviews_due"]):
        raise ModelIntelligenceError("benchmark review status does not match reviews_due")

    if result["maintainer_disposition"] is not None:
        if result["maintainer_disposition"] not in VALID_MAINTAINER_DISPOSITIONS:
            raise ModelIntelligenceError("invalid maintainer_disposition in output")
        if result["status"] != "benchmark-review-due" or not result["reviews_due"]:
            raise ModelIntelligenceError("maintainer disposition is not permitted when no benchmark review is due")

    for auth_key in (
        "applied",
        "dispatch_authorized",
        "model_change_authorized",
        "effort_change_authorized",
        "acceptance_authorized",
        "git_authorized",
        "benchmark_run_authorized",
        "provider_call_authorized",
    ):
        if result[auth_key] is not False:
            raise ModelIntelligenceError(f"{auth_key} must be false")

    if (
        not isinstance(result["limitations"], list)
        or not 1 <= len(result["limitations"]) <= 20
        or any(
            not isinstance(item, str)
            or not 1 <= len(item) <= 2000
            or any(ord(char) < 32 and char not in "\t" for char in item)
            for item in result["limitations"]
        )
    ):
        raise ModelIntelligenceError("limitations must contain bounded single-line strings")

    if result["token_inference_disclaimer"] != TOKEN_DISCLAIMER:
        raise ModelIntelligenceError("invalid token_inference_disclaimer")

    return result


def track_benchmark_review(
    *,
    dataset: dict[str, Any] | None = None,
    dataset_sha: str | None = None,
    baseline_inventory: dict[str, Any] | None = None,
    candidate_inventory: dict[str, Any] | None = None,
    baseline_matrix: dict[str, Any] | None = None,
    candidate_matrix: dict[str, Any] | None = None,
    reference_date: str | None = None,
    maintainer_disposition: str | None = None,
) -> dict[str, Any]:
    """Evaluate whether benchmark review is due when supported model inventory or dataset expiry changes."""
    if reference_date is None:
        raise ModelIntelligenceError("caller must provide a valid reference_date (YYYY-MM-DD)")
    ref_dt = parse_iso_date(reference_date, "reference_date")

    if maintainer_disposition is not None:
        if maintainer_disposition not in VALID_MAINTAINER_DISPOSITIONS:
            raise ModelIntelligenceError(
                f"invalid maintainer_disposition: {maintainer_disposition!r}; "
                f"must be one of {sorted(VALID_MAINTAINER_DISPOSITIONS)}"
            )

    if (baseline_inventory is None) != (candidate_inventory is None):
        raise ModelIntelligenceError("baseline and candidate inventory must be provided as a pair")

    if (baseline_matrix is None) != (candidate_matrix is None):
        raise ModelIntelligenceError("baseline and candidate matrix must be provided as a pair")

    if baseline_inventory is not None and baseline_matrix is not None:
        raise ModelIntelligenceError("inventory and matrix comparison pairs are mutually exclusive")

    base_slugs: set[str] = set()
    base_model_bindings: dict[str, Any] = {}
    cand_slugs: set[str] = set()
    cand_model_bindings: dict[str, Any] = {}

    if baseline_inventory is not None and candidate_inventory is not None:
        base_slugs, base_model_bindings, base_type, _ = _extract_model_inventory(baseline_inventory, "baseline_inventory")
        cand_slugs, cand_model_bindings, cand_type, _ = _extract_model_inventory(candidate_inventory, "candidate_inventory")
        if base_type != cand_type:
            raise ModelIntelligenceError("baseline and candidate inventory source types must match")
    elif baseline_matrix is not None and candidate_matrix is not None:
        base_slugs, base_model_bindings, base_type, _ = _extract_model_inventory(baseline_matrix, "baseline_matrix")
        cand_slugs, cand_model_bindings, cand_type, _ = _extract_model_inventory(candidate_matrix, "candidate_matrix")
        if base_type != cand_type:
            raise ModelIntelligenceError("baseline and candidate matrix source types must match")

    reviews_due: list[dict[str, Any]] = []
    seen_models: set[str] = set()

    # 1. Check inventory additions
    for slug in sorted(cand_slugs - base_slugs):
        reviews_due.append({
            "model_id": slug,
            "evidence_state": "inventory-added",
        })
        seen_models.add(slug)

    # 2. Check inventory removals
    for slug in sorted(base_slugs - cand_slugs):
        reviews_due.append({
            "model_id": slug,
            "evidence_state": "inventory-removed",
        })
        seen_models.add(slug)

    # 3. Check binding changes for common models (per-model comparison)
    for slug in sorted(cand_slugs & base_slugs):
        if slug not in seen_models:
            if base_model_bindings.get(slug) != cand_model_bindings.get(slug):
                reviews_due.append({
                    "model_id": slug,
                    "evidence_state": "binding-changed",
                })
                seen_models.add(slug)

    # 4. Check dataset expiry / freshness if dataset provided
    if dataset is not None:
        validate_dataset(dataset)
        root_exp_dt = parse_iso_date(dataset["expiry_date"], "expiry_date")
        root_created_dt = parse_iso_date(dataset["created_date"], "created_date")
        root_freshness = datetime.timedelta(days=dataset["freshness_window_days"])

        if cand_slugs:
            expiry_target_models = set(cand_slugs)
        else:
            expiry_target_models = _get_reviewed_inventory_slugs() | {it["requested_model"] for it in dataset["items"]}

        if ref_dt > root_exp_dt:
            for m in sorted(expiry_target_models):
                if m not in seen_models:
                    reviews_due.append({
                        "model_id": m,
                        "evidence_state": "dataset-expired",
                    })
                    seen_models.add(m)
        elif ref_dt > root_created_dt + root_freshness:
            for m in sorted(expiry_target_models):
                if m not in seen_models:
                    reviews_due.append({
                        "model_id": m,
                        "evidence_state": "stale-evidence",
                    })
                    seen_models.add(m)
        else:
            for item in dataset["items"]:
                m = item["requested_model"]
                item_exp = parse_iso_date(item["expiry_date"], "expiry_date")
                item_obs = parse_iso_date(item["observed_date"], "observed_date")
                if ref_dt > item_exp:
                    if m not in seen_models:
                        reviews_due.append({
                            "model_id": m,
                            "evidence_state": "dataset-expired",
                        })
                        seen_models.add(m)
                elif ref_dt > item_obs + root_freshness:
                    if m not in seen_models:
                        reviews_due.append({
                            "model_id": m,
                            "evidence_state": "stale-evidence",
                        })
                        seen_models.add(m)

    reviews_due.sort(key=lambda x: x["model_id"])
    status = "benchmark-review-due" if reviews_due else "unchanged"

    if maintainer_disposition is not None and not reviews_due:
        raise ModelIntelligenceError(
            f"maintainer disposition {maintainer_disposition!r} is not permitted when no benchmark review is due"
        )

    out = {
        "schema_version": 1,
        "kind": "agy-benchmark-review-tracker",
        "status": status,
        "evidence_dataset_sha256": dataset_sha,
        "reference_date": reference_date,
        "reviews_due": reviews_due,
        "maintainer_disposition": maintainer_disposition,
        "applied": False,
        "dispatch_authorized": False,
        "model_change_authorized": False,
        "effort_change_authorized": False,
        "acceptance_authorized": False,
        "git_authorized": False,
        "benchmark_run_authorized": False,
        "provider_call_authorized": False,
        "limitations": [
            "Benchmark review tracker is observational only; no benchmark execution, provider execution, routing change, or git write is authorized.",
            "Maintainer disposition (collect, defer, not-applicable) must be chosen explicitly by a maintainer and is never selected automatically.",
            TOKEN_DISCLAIMER,
        ],
        "token_inference_disclaimer": TOKEN_DISCLAIMER,
    }
    return validate_benchmark_review_output(out)


def main(argv: Sequence[str]) -> int:
    if len(argv) < 2:
        sys.stderr.write("usage: model-intelligence <validate|advise|import-study|benchmark-review> [options]\n")
        return 2

    subcmd = argv[1]
    if subcmd == "validate":
        dataset_path: Path | None = None
        idx = 2
        while idx < len(argv):
            arg = argv[idx]
            if arg == "--dataset" and idx + 1 < len(argv):
                dataset_path = Path(argv[idx + 1])
                idx += 2
            elif arg.startswith("--dataset="):
                dataset_path = Path(arg.partition("=")[2])
                idx += 1
            else:
                sys.stderr.write(f"model-intelligence validate: rejected argument {arg}\n")
                return 2
        if dataset_path is None:
            dataset_path = Path(__file__).resolve().parent.parent / "compat" / "model-intelligence" / "dataset.v1.json"

        try:
            data, digest_sha, _ = read_json_file(dataset_path)
            validate_dataset(data)
            out = {
                "status": "valid",
                "dataset_id": data["dataset_id"],
                "dataset_sha256": digest_sha,
                "item_count": len(data["items"]),
            }
            sys.stdout.write(json.dumps(out, indent=2) + "\n")
            return 0
        except ModelIntelligenceError as exc:
            sys.stderr.write(f"model-intelligence validation error: {exc}\n")
            return 1

    elif subcmd == "advise":
        dataset_path = None
        taxonomy = None
        ref_date = None
        out_path = None
        idx = 2
        while idx < len(argv):
            arg = argv[idx]
            if arg == "--dataset" and idx + 1 < len(argv):
                dataset_path = Path(argv[idx + 1])
                idx += 2
            elif arg.startswith("--dataset="):
                dataset_path = Path(arg.partition("=")[2])
                idx += 1
            elif arg == "--taxonomy" and idx + 1 < len(argv):
                taxonomy = argv[idx + 1]
                idx += 2
            elif arg.startswith("--taxonomy="):
                taxonomy = arg.partition("=")[2]
                idx += 1
            elif arg == "--reference-date" and idx + 1 < len(argv):
                ref_date = argv[idx + 1]
                idx += 2
            elif arg.startswith("--reference-date="):
                ref_date = arg.partition("=")[2]
                idx += 1
            elif arg == "--out" and idx + 1 < len(argv):
                out_path = Path(argv[idx + 1])
                idx += 2
            elif arg.startswith("--out="):
                out_path = Path(arg.partition("=")[2])
                idx += 1
            else:
                sys.stderr.write(f"model-intelligence advise: rejected argument {arg}\n")
                return 2

        if dataset_path is None:
            dataset_path = Path(__file__).resolve().parent.parent / "compat" / "model-intelligence" / "dataset.v1.json"

        if ref_date is None:
            sys.stderr.write("model-intelligence advise: missing required --reference-date YYYY-MM-DD\n")
            return 2

        try:
            data, digest_sha, _ = read_json_file(dataset_path)
            advisory = compute_advisory(data, digest_sha, target_taxonomy=taxonomy, reference_date=ref_date)
            formatted = json.dumps(advisory, indent=2) + "\n"
            if out_path is not None:
                out_path.write_text(formatted, encoding="utf-8")
            else:
                sys.stdout.write(formatted)
            return 0
        except ModelIntelligenceError as exc:
            sys.stderr.write(f"model-intelligence advise error: {exc}\n")
            return 1

    elif subcmd == "import-study":
        report_path: Path | None = None
        plan_path: Path | None = None
        results_path: Path | None = None
        out_path: Path | None = None
        idx = 2
        while idx < len(argv):
            arg = argv[idx]
            if arg == "--report" and idx + 1 < len(argv):
                report_path = Path(argv[idx + 1])
                idx += 2
            elif arg.startswith("--report="):
                report_path = Path(arg.partition("=")[2])
                idx += 1
            elif arg == "--plan" and idx + 1 < len(argv):
                plan_path = Path(argv[idx + 1])
                idx += 2
            elif arg.startswith("--plan="):
                plan_path = Path(arg.partition("=")[2])
                idx += 1
            elif arg == "--results" and idx + 1 < len(argv):
                results_path = Path(argv[idx + 1])
                idx += 2
            elif arg.startswith("--results="):
                results_path = Path(arg.partition("=")[2])
                idx += 1
            elif arg == "--out" and idx + 1 < len(argv):
                out_path = Path(argv[idx + 1])
                idx += 2
            elif arg.startswith("--out="):
                out_path = Path(arg.partition("=")[2])
                idx += 1
            else:
                sys.stderr.write(f"model-intelligence import-study: rejected argument {arg}\n")
                return 2

        if report_path is None or plan_path is None or results_path is None:
            sys.stderr.write("model-intelligence import-study: missing required --report, --plan, or --results\n")
            return 2

        try:
            imported = import_study_report(report_path, plan_path, results_path)
            formatted = json.dumps(imported, indent=2) + "\n"
            if out_path is not None:
                out_path.write_text(formatted, encoding="utf-8")
            else:
                sys.stdout.write(formatted)
            return 0
        except ModelIntelligenceError as exc:
            sys.stderr.write(f"model-intelligence import-study error: {exc}\n")
            return 1

    elif subcmd == "benchmark-review":
        dataset_path = None
        base_inv_path = None
        cand_inv_path = None
        base_mat_path = None
        cand_mat_path = None
        ref_date = None
        maintainer_disp = None
        out_path = None
        idx = 2
        while idx < len(argv):
            arg = argv[idx]
            if arg == "--reference-date" and idx + 1 < len(argv):
                ref_date = argv[idx + 1]
                idx += 2
            elif arg.startswith("--reference-date="):
                ref_date = arg.partition("=")[2]
                idx += 1
            elif arg == "--dataset" and idx + 1 < len(argv):
                dataset_path = Path(argv[idx + 1])
                idx += 2
            elif arg.startswith("--dataset="):
                dataset_path = Path(arg.partition("=")[2])
                idx += 1
            elif arg == "--baseline-inventory" and idx + 1 < len(argv):
                base_inv_path = Path(argv[idx + 1])
                idx += 2
            elif arg.startswith("--baseline-inventory="):
                base_inv_path = Path(arg.partition("=")[2])
                idx += 1
            elif arg == "--candidate-inventory" and idx + 1 < len(argv):
                cand_inv_path = Path(argv[idx + 1])
                idx += 2
            elif arg.startswith("--candidate-inventory="):
                cand_inv_path = Path(arg.partition("=")[2])
                idx += 1
            elif arg == "--baseline-matrix" and idx + 1 < len(argv):
                base_mat_path = Path(argv[idx + 1])
                idx += 2
            elif arg.startswith("--baseline-matrix="):
                base_mat_path = Path(arg.partition("=")[2])
                idx += 1
            elif arg == "--candidate-matrix" and idx + 1 < len(argv):
                cand_mat_path = Path(argv[idx + 1])
                idx += 2
            elif arg.startswith("--candidate-matrix="):
                cand_mat_path = Path(arg.partition("=")[2])
                idx += 1
            elif arg == "--maintainer-disposition" and idx + 1 < len(argv):
                maintainer_disp = argv[idx + 1]
                idx += 2
            elif arg.startswith("--maintainer-disposition="):
                maintainer_disp = arg.partition("=")[2]
                idx += 1
            elif arg == "--out" and idx + 1 < len(argv):
                out_path = Path(argv[idx + 1])
                idx += 2
            elif arg.startswith("--out="):
                out_path = Path(arg.partition("=")[2])
                idx += 1
            else:
                sys.stderr.write(f"model-intelligence benchmark-review: rejected argument {arg}\n")
                return 2

        if ref_date is None:
            sys.stderr.write("model-intelligence benchmark-review: missing required --reference-date YYYY-MM-DD\n")
            return 2

        if (base_inv_path is None) != (cand_inv_path is None):
            sys.stderr.write("model-intelligence benchmark-review: --baseline-inventory and --candidate-inventory must be provided as a pair\n")
            return 2

        if (base_mat_path is None) != (cand_mat_path is None):
            sys.stderr.write("model-intelligence benchmark-review: --baseline-matrix and --candidate-matrix must be provided as a pair\n")
            return 2

        try:
            ds_data = None
            ds_sha = None
            if dataset_path is not None:
                ds_data, ds_sha, _ = read_json_file(dataset_path)
            else:
                default_ds = Path(__file__).resolve().parent.parent / "compat" / "model-intelligence" / "dataset.v1.json"
                if default_ds.is_file():
                    ds_data, ds_sha, _ = read_json_file(default_ds)

            b_inv = None
            if base_inv_path is not None:
                b_inv, _, _ = read_json_file(base_inv_path)

            c_inv = None
            if cand_inv_path is not None:
                c_inv, _, _ = read_json_file(cand_inv_path)

            b_mat = None
            if base_mat_path is not None:
                b_mat, _, _ = read_json_file(base_mat_path)

            c_mat = None
            if cand_mat_path is not None:
                c_mat, _, _ = read_json_file(cand_mat_path)

            result = track_benchmark_review(
                dataset=ds_data,
                dataset_sha=ds_sha,
                baseline_inventory=b_inv,
                candidate_inventory=c_inv,
                baseline_matrix=b_mat,
                candidate_matrix=c_mat,
                reference_date=ref_date,
                maintainer_disposition=maintainer_disp,
            )
            formatted = json.dumps(result, indent=2) + "\n"
            if out_path is not None:
                out_path.write_text(formatted, encoding="utf-8")
            else:
                sys.stdout.write(formatted)
            return 0
        except (ModelIntelligenceError, OSError):
            sys.stderr.write("model-intelligence benchmark-review error: operation failed closed\n")
            return 1

    else:
        sys.stderr.write(f"model-intelligence: unknown subcommand {subcmd}\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
