#!/usr/bin/env python3
import argparse
import json
from datetime import date, datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from propose_adaptation import build_report as build_proposal_report
from propose_adaptation import render_markdown as render_proposals_markdown
from skillops_opportunity import build_opportunities, decision_policy_contract, summarize_opportunities
from summarize_user_signals import build_report as build_pattern_report
from summarize_user_signals import render_markdown as render_patterns_markdown


ROOT = Path(__file__).resolve().parent.parent
SCRIPT_INTERFACE = "cli"
SCRIPT_INTERFACE_REASON = "Renders a Daily SkillOps report that summarizes explicit-source patterns, proposals, approval state, and release evidence without scanning private logs or applying patches."

SUMMARY_FIELDS = [
    "decision",
    "source_supplied",
    "pattern_count",
    "proposal_count",
    "approval_count",
    "pending_review_count",
    "applied_count",
    "rollback_count",
    "local_blueprint_ready",
    "public_world_class_ready",
    "world_class_pending_count",
    "release_lock_ready",
    "evidence_consistency_ok",
    "writes_source_files",
    "auto_patch_enabled",
    "failure_count",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def report_date(generated_at: str) -> str:
    if len(generated_at) >= 10:
        candidate = generated_at[:10]
        try:
            date.fromisoformat(candidate)
            return candidate
        except ValueError:
            pass
    return date.today().isoformat()


def display_path(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return f"[external-explicit-source]/{path.name}"


def resolve_output(skill_dir: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else skill_dir / path


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def default_daily_path(skill_dir: Path, generated_at: str, suffix: str) -> Path:
    return skill_dir / "reports" / "skillops" / "daily" / f"{report_date(generated_at)}.{suffix}"


def source_summary(patterns: dict[str, Any]) -> dict[str, Any]:
    source = patterns.get("source", {}) if isinstance(patterns.get("source"), dict) else {}
    privacy = patterns.get("privacy_contract", {}) if isinstance(patterns.get("privacy_contract"), dict) else {}
    return {
        "path": source.get("path", ""),
        "fingerprint_sha256": source.get("fingerprint_sha256", ""),
        "record_count": source.get("record_count", 0),
        "explicit_source": privacy.get("explicit_source_required") is True,
        "raw_content_stored": privacy.get("raw_content_stored") is True,
        "redacted_excerpts_only": privacy.get("redacted_excerpts_only") is True,
    }


def compact_proposals(proposals: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for item in proposals.get("proposals", []):
        if not isinstance(item, dict):
            continue
        rows.append(
            {
                "proposal_id": item.get("proposal_id", ""),
                "pattern_id": item.get("pattern_id", ""),
                "title": item.get("title", ""),
                "risk_level": item.get("risk_level", ""),
                "status": item.get("status", ""),
                "requires_approval": item.get("requires_approval") is True,
                "target_files": item.get("target_files", []),
                "verification_commands": item.get("verification_commands", []),
            }
        )
    return rows


def build_actions(summary: dict[str, Any], proposal_rows: list[dict[str, Any]]) -> list[dict[str, str]]:
    actions: list[dict[str, str]] = []
    if summary["source_supplied"] is False and summary["pattern_count"] == 0:
        actions.append(
            {
                "key": "provide-explicit-source",
                "priority": "medium",
                "action": "Run daily-skillops with --source pointing to a curated JSONL or Markdown conversation summary.",
            }
        )
    if proposal_rows:
        actions.append(
            {
                "key": "review-adaptation-proposals",
                "priority": "high",
                "action": "Review proposal-only adaptation items before preparing any approval ledger entry.",
            }
        )
    if summary["pending_review_count"]:
        actions.append(
            {
                "key": "resolve-pending-approvals",
                "priority": "high",
                "action": "Approve, reject, or expire pending adaptive approval ledger entries before applying patches.",
            }
        )
    if summary["world_class_pending_count"]:
        actions.append(
            {
                "key": "close-world-class-evidence",
                "priority": "high",
                "action": "Collect accepted external or human evidence for the pending world-class ledger entries.",
            }
        )
    if summary["evidence_consistency_ok"] is not True:
        actions.append(
            {
                "key": "refresh-evidence-consistency",
                "priority": "high",
                "action": "Regenerate evidence-consistency before using this report for release decisions.",
            }
        )
    if not actions:
        actions.append(
            {
                "key": "monitor",
                "priority": "low",
                "action": "No action required beyond routine daily monitoring.",
            }
        )
    return actions


def build_report(
    skill_dir: Path,
    generated_at: str,
    source: Path | None = None,
    min_support: int = 2,
    allow_history_source: bool = False,
    patterns_json: Path | None = None,
    proposals_json: Path | None = None,
    write_source_reports: bool = True,
) -> dict[str, Any]:
    skill_dir = skill_dir.resolve()
    reports = skill_dir / "reports"
    patterns_path = resolve_output(skill_dir, str(patterns_json or "reports/user_patterns.json"))
    proposals_path = resolve_output(skill_dir, str(proposals_json or "reports/adaptation_proposals.json"))
    failures: list[str] = []

    if source is not None:
        pattern_report = build_pattern_report(
            skill_dir,
            source,
            min_support=max(2, min_support),
            generated_at=generated_at,
            allow_history_source=allow_history_source,
        )
        if pattern_report.get("ok") is True and write_source_reports:
            pattern_report["artifacts"] = {
                "json": display_path(patterns_path, skill_dir),
                "markdown": display_path(patterns_path.with_suffix(".md"), skill_dir),
            }
            write_json(patterns_path, pattern_report)
            write_text(patterns_path.with_suffix(".md"), render_patterns_markdown(pattern_report))
        else:
            failures.extend(pattern_report.get("failures", []))
    else:
        pattern_report = load_json(patterns_path)

    if pattern_report and pattern_report.get("ok") is True:
        proposal_source_path = patterns_path
        with TemporaryDirectory() as temp_dir:
            if source is not None and not write_source_reports:
                proposal_source_path = Path(temp_dir) / "user_patterns.json"
                write_json(proposal_source_path, pattern_report)
            proposal_report = build_proposal_report(skill_dir, proposal_source_path, generated_at)
        if proposal_report.get("ok") is True and write_source_reports:
            proposal_report["artifacts"] = {
                "json": display_path(proposals_path, skill_dir),
                "markdown": display_path(proposals_path.with_suffix(".md"), skill_dir),
            }
            write_json(proposals_path, proposal_report)
            write_text(proposals_path.with_suffix(".md"), render_proposals_markdown(proposal_report))
        elif proposal_report.get("ok") is not True:
            failures.extend(proposal_report.get("failures", []))
    else:
        proposal_report = load_json(proposals_path)
        if source is not None and not pattern_report:
            failures.append("Pattern report could not be built from the explicit source.")

    approval = load_json(reports / "adaptation_approval_ledger.json")
    regression = load_json(reports / "adaptation_regression_report.json")
    coverage = load_json(reports / "skill_os2_coverage.json")
    ledger = load_json(reports / "world_class_evidence_ledger.json")
    consistency = load_json(reports / "evidence_consistency.json")
    benchmark = load_json(reports / "benchmark_reproducibility.json")

    pattern_summary = pattern_report.get("summary", {}) if isinstance(pattern_report.get("summary"), dict) else {}
    proposal_summary = proposal_report.get("summary", {}) if isinstance(proposal_report.get("summary"), dict) else {}
    approval_summary = approval.get("summary", {}) if isinstance(approval.get("summary"), dict) else {}
    regression_summary = regression.get("summary", {}) if isinstance(regression.get("summary"), dict) else {}
    coverage_summary = coverage.get("summary", {}) if isinstance(coverage.get("summary"), dict) else {}
    ledger_summary = ledger.get("summary", {}) if isinstance(ledger.get("summary"), dict) else {}
    benchmark_summary = benchmark.get("summary", {}) if isinstance(benchmark.get("summary"), dict) else {}
    proposal_contract = proposal_report.get("proposal_contract", {}) if isinstance(proposal_report.get("proposal_contract"), dict) else {}

    proposal_rows = compact_proposals(proposal_report)
    pattern_rows = pattern_report.get("patterns", []) if isinstance(pattern_report.get("patterns"), list) else []
    opportunities = build_opportunities(pattern_rows, proposal_rows)
    opportunity_summary = summarize_opportunities(opportunities)
    failure_count = len(failures)
    summary = {
        "decision": "blocked" if failure_count else "proposal-review" if proposal_rows else "monitor",
        "source_supplied": source is not None,
        "pattern_count": int(pattern_summary.get("pattern_count", 0) or 0),
        "proposal_count": int(proposal_summary.get("proposal_count", 0) or len(proposal_rows)),
        "approval_count": int(approval_summary.get("approval_count", 0) or 0),
        "pending_review_count": int(approval_summary.get("pending_review_count", 0) or 0),
        "applied_count": int(approval_summary.get("applied_count", 0) or regression_summary.get("applied_count", 0) or 0),
        "rollback_count": int(approval_summary.get("rollback_count", 0) or regression_summary.get("rollback_count", 0) or 0),
        "local_blueprint_ready": coverage_summary.get("local_blueprint_ready") is True,
        "public_world_class_ready": coverage_summary.get("public_world_class_ready") is True,
        "world_class_pending_count": int(ledger_summary.get("pending_count", coverage_summary.get("world_class_evidence_pending_count", 0)) or 0),
        "release_lock_ready": benchmark_summary.get("release_lock_ready") is True,
        "evidence_consistency_ok": consistency.get("ok") is True,
        "writes_source_files": False,
        "auto_patch_enabled": False,
        "failure_count": failure_count,
    }
    actions = build_actions(summary, proposal_rows)
    operations_contract = {
        "schema_version": "1.0",
        "contract": "daily-skillops-report",
        "explicit_source_required_for_scan": True,
        "implicit_private_log_scan": False,
        "raw_content_stored": False,
        "redacted_excerpts_only": True,
        "proposal_only": proposal_contract.get("proposal_only") is not False,
        "approval_required_for_writes": True,
        "writes_source_files": False,
        "auto_patch_enabled": False,
        "daily_report_counts_as_world_class_evidence": False,
    }
    report = {
        "schema_version": "1.0",
        "ok": failure_count == 0,
        "generated_at": generated_at,
        "skill_dir": display_path(skill_dir, skill_dir),
        **{key: summary[key] for key in SUMMARY_FIELDS},
        "summary": summary,
        "operations_contract": operations_contract,
        "report_contract": {
            "schema_version": "1.0",
            "contract": "daily-skillops-report",
            "top_level_mirrors_summary": True,
            "summary_fields": SUMMARY_FIELDS,
            "source_of_truth": ["summary", "operations_contract"],
        },
        "source": source_summary(pattern_report) if pattern_report else {},
        "patterns": pattern_report.get("patterns", []) if isinstance(pattern_report.get("patterns"), list) else [],
        "proposals": proposal_rows,
        "opportunity_summary": opportunity_summary,
        "opportunities": opportunities,
        "decision_policy": decision_policy_contract(),
        "approval": {
            "approval_count": summary["approval_count"],
            "pending_review_count": summary["pending_review_count"],
            "applied_count": summary["applied_count"],
            "rollback_count": summary["rollback_count"],
        },
        "release_state": {
            "local_blueprint_ready": summary["local_blueprint_ready"],
            "public_world_class_ready": summary["public_world_class_ready"],
            "world_class_pending_count": summary["world_class_pending_count"],
            "release_lock_ready": summary["release_lock_ready"],
            "evidence_consistency_ok": summary["evidence_consistency_ok"],
        },
        "actions": actions,
        "failures": failures,
        "source_reports": {
            "patterns": display_path(patterns_path, skill_dir),
            "proposals": display_path(proposals_path, skill_dir),
            "approval_ledger": "reports/adaptation_approval_ledger.json",
            "regression": "reports/adaptation_regression_report.json",
            "skill_os2_coverage": "reports/skill_os2_coverage.json",
            "world_class_ledger": "reports/world_class_evidence_ledger.json",
            "evidence_consistency": "reports/evidence_consistency.json",
            "benchmark_reproducibility": "reports/benchmark_reproducibility.json",
        },
        "artifacts": {
            "json": str(default_daily_path(skill_dir, generated_at, "json").relative_to(skill_dir)),
            "markdown": str(default_daily_path(skill_dir, generated_at, "md").relative_to(skill_dir)),
        },
    }
    return report


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Daily SkillOps Report",
        "",
        f"Generated at: `{report['generated_at']}`",
        "",
        "## Summary",
        "",
        f"- decision: `{summary['decision']}`",
        f"- source supplied: `{str(summary['source_supplied']).lower()}`",
        f"- patterns: `{summary['pattern_count']}`",
        f"- proposals: `{summary['proposal_count']}`",
        f"- pending approvals: `{summary['pending_review_count']}`",
        f"- applied patches: `{summary['applied_count']}`",
        f"- rollbacks: `{summary['rollback_count']}`",
        f"- local blueprint ready: `{str(summary['local_blueprint_ready']).lower()}`",
        f"- public world-class ready: `{str(summary['public_world_class_ready']).lower()}`",
        f"- world-class pending: `{summary['world_class_pending_count']}`",
        f"- release lock ready: `{str(summary['release_lock_ready']).lower()}`",
        f"- evidence consistency ok: `{str(summary['evidence_consistency_ok']).lower()}`",
        "",
        "This report is an operations cockpit for explicit-source SkillOps. It does not scan private logs, write source files, apply patches, or count as world-class external or human evidence.",
        "",
        "## Privacy Boundary",
        "",
    ]
    contract = report["operations_contract"]
    for key in [
        "explicit_source_required_for_scan",
        "implicit_private_log_scan",
        "raw_content_stored",
        "redacted_excerpts_only",
        "proposal_only",
        "approval_required_for_writes",
        "writes_source_files",
        "auto_patch_enabled",
        "daily_report_counts_as_world_class_evidence",
    ]:
        lines.append(f"- {key}: `{str(contract[key]).lower()}`")
    lines.extend(["", "## Actions", ""])
    for action in report["actions"]:
        lines.append(f"- `{action['priority']}` {action['action']}")
    lines.extend(["", "## Opportunities", ""])
    opportunity_summary = report.get("opportunity_summary", {})
    lines.extend(
        [
            f"- count: `{opportunity_summary.get('opportunity_count', 0)}`",
            f"- top score: `{opportunity_summary.get('top_score', 0)}`",
            f"- ready for approval review: `{opportunity_summary.get('ready_for_approval_review_count', 0)}`",
        ]
    )
    for opportunity in report.get("opportunities", []):
        lines.extend(
            [
                f"### {opportunity.get('title', '')}",
                "",
                f"- ID: `{opportunity.get('opportunity_id', '')}`",
                f"- Action: `{opportunity.get('action_type', '')}`",
                f"- Decision: `{opportunity.get('decision', '')}`",
                f"- Score: `{opportunity.get('score', 0)}`",
                f"- Risk: `{opportunity.get('risk_level', '')}`",
                f"- Policy: {opportunity.get('policy_reason', '')}",
            ]
        )
    lines.extend(["", "## Patterns", ""])
    patterns = report.get("patterns", [])
    if not patterns:
        lines.append("- No repeated pattern met the support threshold.")
    for pattern in patterns:
        lines.append(
            f"- `{pattern.get('pattern_id', '')}`: {pattern.get('label', '')} "
            f"(support `{pattern.get('support_count', 0)}`, confidence `{pattern.get('confidence', '')}`)"
        )
    lines.extend(["", "## Proposals", ""])
    proposals = report.get("proposals", [])
    if not proposals:
        lines.append("- No adaptation proposals are waiting for review.")
    for proposal in proposals:
        lines.extend(
            [
                f"### {proposal['title']}",
                "",
                f"- ID: `{proposal['proposal_id']}`",
                f"- Pattern: `{proposal['pattern_id']}`",
                f"- Status: `{proposal['status']}`",
                f"- Risk: `{proposal['risk_level']}`",
                f"- Requires approval: `{str(proposal['requires_approval']).lower()}`",
                "- Target files:",
            ]
        )
        lines.extend(f"  - `{path}`" for path in proposal.get("target_files", []))
        lines.append("- Verification:")
        lines.extend(f"  - `{command}`" for command in proposal.get("verification_commands", []))
        lines.append("")
    lines.extend(["## Evidence", ""])
    for label, path in report["source_reports"].items():
        lines.append(f"- {label}: `{path}`")
    if report["failures"]:
        lines.extend(["", "## Failures", ""])
        lines.extend(f"- {failure}" for failure in report["failures"])
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a Daily SkillOps report from explicit-source adaptive evidence.")
    parser.add_argument("skill_dir", nargs="?", default=".")
    parser.add_argument("--source", help="Explicit curated source file to scan before rendering the daily report.")
    parser.add_argument("--patterns-json", default="reports/user_patterns.json")
    parser.add_argument("--proposals-json", default="reports/adaptation_proposals.json")
    parser.add_argument("--output-json")
    parser.add_argument("--output-md")
    parser.add_argument("--min-support", type=int, default=2)
    parser.add_argument("--generated-at", default=utc_now())
    parser.add_argument("--allow-history-source", action="store_true")
    parser.add_argument("--no-refresh-source-reports", action="store_true")
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir).resolve()
    report = build_report(
        skill_dir,
        args.generated_at,
        source=Path(args.source) if args.source else None,
        min_support=args.min_support,
        allow_history_source=args.allow_history_source,
        patterns_json=Path(args.patterns_json),
        proposals_json=Path(args.proposals_json),
        write_source_reports=not args.no_refresh_source_reports,
    )
    output_json = resolve_output(skill_dir, args.output_json) if args.output_json else default_daily_path(skill_dir, args.generated_at, "json")
    output_md = resolve_output(skill_dir, args.output_md) if args.output_md else default_daily_path(skill_dir, args.generated_at, "md")
    report["artifacts"] = {
        "json": display_path(output_json, skill_dir),
        "markdown": display_path(output_md, skill_dir),
    }
    write_json(output_json, report)
    write_text(output_md, render_markdown(report))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not report["ok"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
