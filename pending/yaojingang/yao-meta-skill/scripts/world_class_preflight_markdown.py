#!/usr/bin/env python3
"""Markdown renderer for the world-class evidence preflight report."""

from typing import Any


SCRIPT_INTERFACE = "internal-module"
SCRIPT_INTERFACE_REASON = "Imported by render_world_class_preflight.py to keep Markdown layout separate from preflight data assembly."


def md_cell(value: Any) -> str:
    return str(value).replace("|", "\\|")


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    role_contract = report["submissions"]["artifact_role_contract"]
    lines = [
        "# World-Class Evidence Preflight",
        "",
        f"Generated at: `{report['generated_at']}`",
        "",
        "## Summary",
        "",
        f"- decision: `{summary['decision']}`",
        f"- ready to claim world-class: `{str(summary['ready_to_claim_world_class']).lower()}`",
        f"- preflight counts as evidence: `{str(summary['preflight_counts_as_evidence']).lower()}`",
        f"- credential value exposed: `{str(summary['credential_value_exposed']).lower()}`",
        f"- collection ready: `{summary['collection_ready_count']}`",
        f"- collection blocked: `{summary['collection_blocked_count']}`",
        f"- source checks: `{summary['source_pass_count']}` pass / `{summary['source_check_count']}` total",
        f"- repair rows: `{summary['repair_blocked_count']}` blocked / `{summary['repair_checklist_count']}` total",
        f"- phase queue: `{summary['phase_queue_blocked_count']}` blocked / `{summary['phase_queue_count']}` phases",
        f"- phase queue rows: `{summary['phase_queue_row_count']}`",
        f"- next repair action: `{summary.get('next_repair_action_id', '')}`",
        f"- next repair owner: `{summary.get('next_repair_owner', '')}`",
        f"- next phase: `{summary.get('phase_queue_next_phase', '')}`",
        f"- next phase action: `{summary.get('phase_queue_next_action_id', '')}`",
        "",
        "This preflight report checks whether an operator can start collecting the remaining external or human evidence. It never accepts evidence, prints secret values, or changes the world-class ledger.",
        "",
        "## Submission Kit Handoff",
        "",
        f"- submissions directory: `{report['submissions']['directory']}`",
        f"- prepare drafts: `{report['submissions']['commands']['prepare_submission']}`",
        f"- prepare drafts with artifact SHA prefill: `{report['submissions']['commands']['prepare_prefilled_submission']}`",
        f"- validate intake: `{report['submissions']['commands']['validate_intake']}`",
        f"- review queue: `{report['submissions']['commands']['submission_review']}`",
        f"- refresh ledger: `{report['submissions']['commands']['refresh_ledger']}`",
        f"- guard claims: `{report['submissions']['commands']['guard_claim']}`",
        f"- drafts count as evidence: `{str(report['submissions']['drafts_count_as_evidence']).lower()}`",
        f"- artifact prefill counts as evidence: `{str(report['submissions']['artifact_prefill_counts_as_evidence']).lower()}`",
        f"- submission refs ready: `{role_contract['submission_ref_ready_count']}` / `{role_contract['submission_ref_total_count']}`",
        f"- supporting evidence ready: `{role_contract['supporting_evidence_ready_count']}` / `{role_contract['supporting_evidence_total_count']}`",
        "",
        "Generate the submission kit after the real provider, human, native-permission, or native-client work exists. The generated JSON drafts remain `template_only: true` until an operator edits them with real aggregate artifact references and matching SHA-256 digests. The prefill command only inserts local artifact SHA-256 digests; it does not make a draft count as evidence.",
        "",
        "| Role | Copy to artifact_refs | Ready | Meaning |",
        "| --- | --- | --- | --- |",
    ]
    for role in role_contract.get("roles", []):
        if role.get("role") == "submission-ref":
            ready = f"{role_contract['submission_ref_ready_count']} / {role_contract['submission_ref_total_count']}"
        else:
            ready = (
                f"{role_contract['supporting_evidence_ready_count']} / "
                f"{role_contract['supporting_evidence_total_count']}"
            )
        lines.append(
            f"| `{role['role']}` | `{str(role['copy_to_artifact_refs']).lower()}` | `{ready}` | "
            f"{md_cell(role['description'])} |"
        )
    lines.extend(
        [
            "",
            "`submission-ref` rows are the only checklist rows expected in `artifact_refs`; `supporting-evidence` rows stay available for audit context and reviewer traceability.",
            "",
            "## Phase Queue",
            "",
            "Phase queue rows group the same repair checklist into operator execution phases. They are procedural guidance only and do not count as completion evidence.",
            "",
            "| Priority | Phase | Status | Rows | Owners | Evidence | Verify | Next action |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in report.get("phase_queue", []):
        owners = ", ".join(str(owner) for owner in row.get("owners", []))
        evidence_keys = ", ".join(str(key) for key in row.get("evidence_keys", []))
        rows = f"{row.get('blocked_count', 0)} / {row.get('row_count', 0)} blocked"
        lines.append(
            f"| `{row.get('priority', '')}` | `{row.get('phase', '')}` | `{row.get('status', '')}` | "
            f"{md_cell(rows)} | {md_cell(owners)} | {md_cell(evidence_keys)} | "
            f"`{md_cell(row.get('verification_command', ''))}` | {md_cell(row.get('next_action', ''))} |"
        )
    lines.extend(
        [
            "",
            "## Evidence Items",
            "",
            "| Evidence | Status | Intake | Review | Next action |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for item in report["items"]:
        next_action = str(item.get("next_action", "")).replace("|", "\\|")
        lines.append(
            f"| `{item['evidence_key']}` | `{item['status']}` | `{item['intake_readiness']}` | `{item['review_state']}` | {next_action} |"
        )
    lines.extend(
        [
            "",
            "## Repair Checklist",
            "",
            "Repair rows convert preflight and source blockers into a prioritized operator queue. They are guidance only and do not count as completion evidence.",
            "",
            "| Priority | Phase | Owner | Evidence | Type | Target | Status | Verify | Next action |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in report.get("repair_checklist", []):
        lines.append(
            f"| `{row.get('priority', '')}` | `{row.get('phase', '')}` | {md_cell(row.get('owner', ''))} | "
            f"`{row['evidence_key']}` | `{row['repair_type']}` | `{row['target']}` | "
            f"`{row['status']}` | `{md_cell(row.get('verification_command', ''))}` | {md_cell(row['next_action'])} |"
        )
    for item in report["items"]:
        lines.extend(
            [
                "",
                f"## {item['label']}",
                "",
                f"- status: `{item['status']}`",
                f"- ledger: `{item['ledger_status']}`",
                f"- submission: `{item.get('submission_path') or 'missing'}`",
                f"- prepare draft: `{item['commands']['prepare_submission']}`",
                f"- prepare draft with artifact SHA prefill: `{item['commands']['prepare_prefilled_submission']}`",
                f"- submission refs ready: `{item['submission_kit']['artifact_role_contract']['submission_ref_ready_count']}` / `{item['submission_kit']['artifact_role_contract']['submission_ref_total_count']}`",
                f"- supporting evidence ready: `{item['submission_kit']['artifact_role_contract']['supporting_evidence_ready_count']}` / `{item['submission_kit']['artifact_role_contract']['supporting_evidence_total_count']}`",
                "",
                "### Prechecks",
                "",
                "| Check | Kind | Current | Status | Next action |",
                "| --- | --- | --- | --- | --- |",
            ]
        )
        for row in item.get("prechecks", []):
            action = md_cell(row.get("next_action", ""))
            lines.append(
                f"| {row['label']} | `{row['kind']}` | `{row['actual']}` | `{row['status']}` | {action} |"
            )
        lines.extend(
            [
                "",
                "### Source Checks",
                "",
                "| Check | Current | Expected | Status | Next action |",
                "| --- | --- | --- | --- | --- |",
            ]
        )
        for row in item.get("source_checklist", []):
            action = md_cell(row.get("next_action", ""))
            lines.append(
                f"| {row['label']} | `{row['actual']}` | `{row['expected']}` | `{row['status']}` | {action} |"
            )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- Environment variables are reported only as `set` or `not-set`; values are never printed.",
            "- Human-required and external-required states are operator actions, not accepted evidence.",
            "- The world-class ledger remains the source of truth for `ready_to_claim_world_class`.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"
