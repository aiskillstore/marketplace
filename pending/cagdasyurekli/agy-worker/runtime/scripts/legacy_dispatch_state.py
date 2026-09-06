#!/usr/bin/env python3
"""Read and approval-gated migration support for retired dispatch-state formats.

The active dispatcher owns only the current V13 controller.  This adapter keeps
V1–V12 records readable and performs their already-approved one-way migration
without letting old state shape leak into ordinary controller transitions.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def is_legacy(state: dict[str, Any], api: Any) -> bool:
    """Return whether a decoded dispatch state predates the active format."""
    return state["schema_version"] < api.CURRENT_STATE_SCHEMA


def project_for_read(api: Any, value: Any, fields: set[str]) -> dict[str, Any] | None:
    """Validate and project a V1–V12 record into the read-only current view."""
    if not isinstance(value, dict):
        raise api.DispatchError("dispatch state fields are invalid")
    version = value.get("schema_version")
    if version == api.CURRENT_STATE_SCHEMA:
        return None
    legacy_fields = fields - api.STATE_PROJECT_FIELDS - {"provider_retry_after_seconds", "provider_retry_observed_epoch"} - api.STATE_V5_FIELDS - api.STATE_V6_FIELDS - api.STATE_V8_FIELDS - api.STATE_V9_FIELDS - api.STATE_V10_FIELDS - api.STATE_V11_FIELDS - api.STATE_V12_FIELDS - api.STATE_V13_FIELDS
    v3_fields = fields - {"provider_retry_after_seconds", "provider_retry_observed_epoch"} - api.STATE_V5_FIELDS - api.STATE_V6_FIELDS - api.STATE_V8_FIELDS - api.STATE_V9_FIELDS - api.STATE_V10_FIELDS - api.STATE_V11_FIELDS - api.STATE_V12_FIELDS - api.STATE_V13_FIELDS
    v4_fields = fields - api.STATE_V5_FIELDS - api.STATE_V6_FIELDS - api.STATE_V8_FIELDS - api.STATE_V9_FIELDS - api.STATE_V10_FIELDS - api.STATE_V11_FIELDS - api.STATE_V12_FIELDS - api.STATE_V13_FIELDS
    v5_fields = fields - api.STATE_V6_FIELDS - api.STATE_V8_FIELDS - api.STATE_V9_FIELDS - api.STATE_V10_FIELDS - api.STATE_V11_FIELDS - api.STATE_V12_FIELDS - api.STATE_V13_FIELDS
    expected = {
        1: legacy_fields, 3: v3_fields, 4: v4_fields, 5: v5_fields,
        6: fields - api.STATE_V8_FIELDS - api.STATE_V9_FIELDS - api.STATE_V10_FIELDS - api.STATE_V11_FIELDS - api.STATE_V12_FIELDS - api.STATE_V13_FIELDS,
        7: fields - api.STATE_V8_FIELDS - api.STATE_V9_FIELDS - api.STATE_V10_FIELDS - api.STATE_V11_FIELDS - api.STATE_V12_FIELDS - api.STATE_V13_FIELDS,
        8: fields - api.STATE_V9_FIELDS - api.STATE_V10_FIELDS - api.STATE_V11_FIELDS - api.STATE_V12_FIELDS - api.STATE_V13_FIELDS,
        9: fields - api.STATE_V10_FIELDS - api.STATE_V11_FIELDS - api.STATE_V12_FIELDS - api.STATE_V13_FIELDS,
        10: fields - api.STATE_V11_FIELDS - api.STATE_V12_FIELDS - api.STATE_V13_FIELDS,
        11: fields - api.STATE_V12_FIELDS - api.STATE_V13_FIELDS,
        12: fields - api.STATE_V13_FIELDS,
    }.get(version)
    if expected is None or set(value) != expected:
        raise api.DispatchError("dispatch state fields are invalid")
    value = dict(value)
    recognized = value["result_path"] is not None if version == 1 else bool(value["result_path"])
    common = {
        "candidate_recognized": recognized,
        "candidate_source": "provider_success" if recognized else "none",
        "result_available": recognized,
        "worktree_reconciliation": "not_applicable",
        "worktree_changes_present": None,
        "worktree_changed_since_dispatch": None,
        "driver_disposition": "unreviewed" if recognized else "not_applicable",
        "failure_stage": None,
        "last_activity": None,
        "next_action": "driver_review" if recognized else "none",
        "next_action_command": None,
        "worktree_baseline": None,
        "provider_schema_sha256": None,
        "provider_schema_identity": None,
        "canonical_schema_sha256": None,
        "canonical_schema_identity": None,
        "candidate_worktree_sha256": None,
        "candidate_worktree_entries": None,
        "selection_sha256": None,
        "selection_identity": None,
        "allow_scoped_repair": False,
        "repair_authority_sha256": None,
        "repair_lineage_sha256": None,
        "repair_parent_result_sha256": None,
        "repair_parent_worktree_sha256": None,
        "repair_lineage_attempt": None,
        "allow_self_verification": False,
        "self_verification_elapsed_seconds": 0.0,
        "self_verification_run": 0,
        "self_verification_started_epoch": None,
        "self_verification_return_phase": None,
        "provider_isolation": "native",
    }
    if version == 1:
        value.update({
            "workflow": "legacy", "max_cycles": 1, "cycle": value["attempt"],
            "phase": None, "assurance": None, "check_summary": None,
            "check_counts": {"passed": 0, "failed": 0, "advisory": 0, "missing": 0},
            "verification_path": None, "verification_sha256": None,
            "verification_identity": None, "continue_available": False,
            "last_success_path": None, "last_success_sha256": None,
            "last_success_identity": None, "project_boundary": None,
            "provider_retry_after_seconds": None,
            "provider_retry_observed_epoch": None,
            **common,
        })
    elif version == 3:
        value.update({"provider_retry_after_seconds": None, "provider_retry_observed_epoch": None, **common})
    elif version == 4:
        value.update(common)
    elif version == 5:
        value.update({"selection_sha256": None, "selection_identity": None})
    for key, default in {
        "allow_scoped_repair": False,
        "repair_authority_sha256": None,
        "repair_lineage_sha256": None,
        "repair_parent_result_sha256": None,
        "repair_parent_worktree_sha256": None,
        "repair_lineage_attempt": None,
        "allow_self_verification": False,
        "self_verification_elapsed_seconds": 0.0,
        "self_verification_run": 0,
        "self_verification_started_epoch": None,
        "self_verification_return_phase": None,
        "provider_isolation": "native",
    }.items():
        value.setdefault(key, default)
    return value


def upgrade(
    api: Any,
    state: dict[str, Any],
    command: dict[str, Any],
    *,
    migration_facts: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Prepare an eligible V1–V12 state for one atomic approved V13 write."""
    if not is_legacy(state, api):
        return state
    if state["schema_version"] == 1:
        raise api.DispatchError("legacy dispatch state has no migration authority")
    if state["schema_version"] in {3, 4} and migration_facts is None:
        raise api.DispatchError("legacy migration approval is required")
    value = dict(state)
    if value["phase"] == "provider-failed":
        value["phase"] = "attempt-failed"
    if value["workflow"] == "legacy":
        if value["candidate_recognized"]:
            value["phase"] = "awaiting-verification"
        elif value["status"] in api.TERMINAL:
            value["phase"] = "attempt-failed"
        else:
            value["phase"] = "dispatching"
        value["assurance"] = "pending"
    else:
        if value["attempt_origin"] == "conversation-continue" and value["status"] == "failed":
            value["phase"] = "repair-failed"
        elif value["candidate_recognized"]:
            value["phase"] = "awaiting-verification"
        elif value["status"] == "failed":
            value["phase"] = "attempt-failed"
        elif value["phase"] is None:
            value["phase"] = "dispatching"
        if value["assurance"] is None:
            value["assurance"] = "pending"
    if value["schema_version"] in {3, 4}:
        assert migration_facts is not None
        snapshot = migration_facts["semantic_snapshot"]
        root_identity = migration_facts["root_identity"]
    elif value["schema_version"] == 9:
        persisted_root = value.get("worktree_root_identity")
        current_root = api._dispatch_root_identity(command["workdir"])
        boundary = api._git_boundary_identity(command["workdir"])
        if persisted_root is None or current_root is None or persisted_root != current_root or persisted_root != boundary:
            raise api.DispatchError("legacy dispatch root identity cannot be proved")
        for key, expected in api._schema_bindings(command).items():
            if value.get(key) != expected:
                raise api.DispatchError("dispatch schema binding changed")
        if value.get("selection_sha256") != command.get("selection_sha256") or value.get("selection_identity") != command.get("selection_identity"):
            raise api.DispatchError("dispatch selection binding changed")
        expected = value.get("candidate_worktree_sha256") if value["candidate_recognized"] else None
        entries = value.get("candidate_worktree_entries") if value["candidate_recognized"] else None
        if expected is None and isinstance(value.get("worktree_baseline"), dict):
            expected, entries = value["worktree_baseline"].get("sha256"), value["worktree_baseline"].get("entries")
        observed = api._state_worktree_snapshot(value, command["workdir"])
        if observed is None or not isinstance(expected, str) or type(entries) is not int or observed["sha256"] != expected or observed["entries"] != entries:
            raise api.DispatchError("legacy dispatch root identity cannot be proved")
        root_identity, snapshot = persisted_root, observed
    else:
        expected = value.get("candidate_worktree_sha256") if value["candidate_recognized"] else None
        entries = value.get("candidate_worktree_entries") if value["candidate_recognized"] else None
        if expected is None and isinstance(value.get("worktree_baseline"), dict):
            expected, entries = value["worktree_baseline"].get("sha256"), value["worktree_baseline"].get("entries")
        observed = api._state_worktree_snapshot(value, command["workdir"])
        if observed is None or not isinstance(expected, str) or type(entries) is not int or observed["sha256"] != expected or observed["entries"] != entries:
            raise api.DispatchError("legacy dispatch root identity cannot be proved")
        root_identity = api._dispatch_root_identity(command["workdir"])
        if root_identity is None:
            raise api.DispatchError("legacy dispatch root identity cannot be proved")
        snapshot = api._worktree_snapshot(command["workdir"]) if value["schema_version"] in {5, 6} else observed
    if snapshot is None:
        raise api.DispatchError("legacy worktree cannot be bound")
    value.update(api._schema_bindings(command))
    value.update({
        "schema_version": api.CURRENT_STATE_SCHEMA,
        "worktree_snapshot_algorithm": api.CURRENT_WORKTREE_SNAPSHOT_ALGORITHM,
        "worktree_baseline": snapshot,
        "worktree_reconciliation": "available",
        "worktree_changes_present": snapshot["entries"] > 0,
        "worktree_changed_since_dispatch": False,
        "resume_available": bool(value["conversation_id"] and not value["candidate_recognized"] and value["status"] == "failed"),
        "selection_sha256": command.get("selection_sha256"),
        "selection_identity": command.get("selection_identity"),
        "worktree_root_identity": root_identity,
        "provider_terminal_status": "unknown",
        "provider_scope_path": None,
        "provider_scope_sha256": None,
        "provider_scope_identity": None,
        "approved_transmission_sha256": None,
        "transmission_sha256": None,
        "selected_content_sha256": None,
        "selected_file_count": None,
        "selected_tree_count": None,
        "provider_stage_path": None,
        "provider_stage_identity": None,
        "provider_stage_manifest_sha256": None,
        "reconciliation_manifest_sha256": None,
        "allow_scoped_repair": False,
        "repair_authority_sha256": None,
        "repair_lineage_sha256": None,
        "repair_parent_result_sha256": None,
        "repair_parent_worktree_sha256": None,
        "repair_lineage_attempt": None,
        "allow_self_verification": False,
        "self_verification_elapsed_seconds": 0.0,
        "self_verification_run": 0,
        "self_verification_started_epoch": None,
        "self_verification_return_phase": None,
        "provider_isolation": api._provider_isolation_for_command(command),
    })
    if value["candidate_recognized"]:
        value["candidate_worktree_sha256"] = snapshot["sha256"]
        value["candidate_worktree_entries"] = snapshot["entries"]
        value["driver_disposition"] = "unreviewed"
    value["continue_available"] = bool(
        value["workflow"] != "legacy" and value["candidate_recognized"]
        and value["candidate_source"] != "provider_cancelled" and value["conversation_id"]
        and value["status"] in {"succeeded", "failed"}
        and value["phase"] in {"awaiting-verification", "repair-failed"}
        and value["attempt"] < value["max_cycles"]
        and float(value["elapsed_seconds"]) < float(value["max_seconds"])
    )
    value["assurance"] = "pending"
    value["next_action"] = "none"
    value["next_action_command"] = None
    value["phase"] = api._controller_phase(value) or "attempt-failed"
    api.validate_state(value)
    return value


def migration_facts(api: Any, job: Path, state: dict[str, Any], state_sha: str) -> dict[str, Any]:
    """Prove a V3/V4 transition without giving a pathname lasting authority."""
    if state["schema_version"] not in {3, 4}:
        raise api.DispatchError("legacy migration is unavailable")
    if api._legacy_prior_result_is_unknown(state):
        raise api.DispatchError("unknown legacy result has no migration authority")
    command = api._load_bound_command(job, state, stage_readonly=False)
    if api._job_is_inside_worktree(job, command["workdir"]):
        raise api.DispatchError("legacy migration is unavailable for jobs inside the worktree")
    command, checked = api._bound_lifecycle_inputs(job, state, command, read_legacy=True)
    selection = api._load_bound_selection(command, checked, legacy_command_binding=True)
    root_identity = api._dispatch_root_identity(command["workdir"])
    snapshot = api._worktree_snapshot(command["workdir"])
    if root_identity is None or snapshot is None:
        raise api.DispatchError("legacy dispatch root identity cannot be proved")
    artifact: dict[str, Any] | None = None
    if checked["candidate_recognized"]:
        api._bound_current_candidate(job, checked)
        artifact = {"sha256": checked["result_sha256"], "identity": checked["result_identity"], "source": checked["candidate_source"]}
    return {
        "kind": "agy-worker-legacy-migration-v1", "state_sha256": state_sha,
        "legacy_schema_version": checked["schema_version"], "command_sha256": checked["command_sha256"],
        "command_identity": checked["command_identity"], "stage_sha256": checked["stage_sha256"],
        "stage_identity": checked["stage_identity"],
        "selection": {"sha256": command.get("selection_sha256"), "identity": command.get("selection_identity"), "schema_version": None if selection is None else selection.get("schema_version")},
        "schemas": api._schema_bindings(command), "root_identity": root_identity,
        "semantic_snapshot": snapshot, "project_boundary": checked["project_boundary"],
        "workflow": checked["workflow"], "attempt_origin": checked["attempt_origin"],
        "status": checked["status"], "candidate": artifact,
        "provider_launch_authorized": api._selection_launch_is_authorized(selection),
        "historical_result_provenance": "unknown_bound_legacy" if api._legacy_prior_result_is_unknown(checked) else None,
    }


def migration_sha(api: Any, job: Path | None, state: dict[str, Any], state_sha: str) -> str | None:
    if job is None or state["schema_version"] not in {3, 4}:
        return None
    try:
        return api.digest(api.canonical(migration_facts(api, job, state, state_sha)))
    except (OSError, api.DispatchError):
        return None


def approved_migration(api: Any, job: Path, state: dict[str, Any], raw: bytes, approval: str | None) -> tuple[dict[str, Any], dict[str, Any]]:
    if state["schema_version"] not in {3, 4}:
        return api._load_bound_command(job, state, stage_readonly=False), state
    if not isinstance(approval, str) or api.SHA_RE.fullmatch(approval) is None:
        raise api.DispatchError("legacy migration approval is missing or invalid")
    facts = migration_facts(api, job, state, api.digest(raw))
    if api.digest(api.canonical(facts)) != approval:
        raise api.DispatchError("legacy migration approval is stale")
    command = api._load_bound_command(job, state, stage_readonly=False)
    return command, upgrade(api, state, command, migration_facts=facts)
