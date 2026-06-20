#!/usr/bin/env python3
import argparse
import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = ROOT / "reports" / "review_annotations_input.json"
DEFAULT_OUTPUT_JSON = ROOT / "reports" / "review_annotations.json"
DEFAULT_OUTPUT_MD = ROOT / "reports" / "review_annotations.md"
VALID_GATES = {
    "intent-canvas",
    "trigger-lab",
    "output-lab",
    "context-budget",
    "runtime-matrix",
    "trust-report",
    "python-compat",
    "architecture-maintainability",
    "permission-gates",
    "permission-runtime",
    "skill-atlas",
    "operations-loop",
    "review-waivers",
    "world-class-evidence",
    "registry-audit",
    "release-notes",
}
VALID_SEVERITIES = {"info", "note", "warning", "blocker"}
VALID_STATUSES = {"open", "resolved", "deferred"}


def display_path(root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        try:
            return str(path.resolve().relative_to(ROOT.resolve()))
        except ValueError:
            return str(path.resolve())


def load_json(path: Path) -> tuple[dict[str, Any], list[str]]:
    if not path.exists():
        return {"schema_version": "1.0", "annotations": []}, []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"schema_version": "1.0", "annotations": []}, [f"Invalid annotation JSON {display_path(ROOT, path)}: {exc}"]
    if not isinstance(payload, dict):
        return {"schema_version": "1.0", "annotations": []}, [f"Annotation file root must be an object: {display_path(ROOT, path)}"]
    if not isinstance(payload.get("annotations", []), list):
        return {"schema_version": "1.0", "annotations": []}, ["annotations must be a list"]
    return payload, []


def template_payload() -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "review_contract": {
            "gate_key": "One Review Studio gate key, such as output-lab or trust-report.",
            "target_path": "Relative path to the source or report being annotated.",
            "line": "Optional positive integer line number.",
            "severity": "info | note | warning | blocker.",
            "status": "open | resolved | deferred.",
            "body": "Reviewer-visible annotation text.",
        },
        "annotations": [],
    }


def annotation_id(annotation: dict[str, Any]) -> str:
    if annotation.get("id"):
        return str(annotation["id"])
    raw = "|".join(
        [
            str(annotation.get("gate_key", "")),
            str(annotation.get("target_path", "")),
            str(annotation.get("line", "")),
            str(annotation.get("body", "")),
        ]
    )
    return "ann-" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]


def source_excerpt(path: Path, line: int | None) -> str:
    if line is None or not path.exists() or not path.is_file():
        return ""
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return ""
    if line < 1 or line > len(lines):
        return ""
    return lines[line - 1].strip()[:220]


def normalize_annotation(skill_dir: Path, raw: dict[str, Any], index: int) -> tuple[dict[str, Any], list[str]]:
    failures: list[str] = []
    if not isinstance(raw, dict):
        return {}, [f"annotation #{index} must be an object"]

    gate_key = str(raw.get("gate_key", "")).strip()
    if gate_key not in VALID_GATES:
        failures.append(f"{annotation_id(raw)}: invalid gate_key {gate_key!r}")

    severity = str(raw.get("severity", "note")).strip().lower()
    if severity not in VALID_SEVERITIES:
        failures.append(f"{annotation_id(raw)}: invalid severity {severity!r}")

    status = str(raw.get("status", "open")).strip().lower()
    if status not in VALID_STATUSES:
        failures.append(f"{annotation_id(raw)}: invalid status {status!r}")

    body = str(raw.get("body", "")).strip()
    if not body:
        failures.append(f"{annotation_id(raw)}: body is required")

    target_path = str(raw.get("target_path", "")).strip()
    if not target_path:
        failures.append(f"{annotation_id(raw)}: target_path is required")
    rel = Path(target_path)
    if rel.is_absolute():
        failures.append(f"{annotation_id(raw)}: target_path must be relative")
        target = skill_dir / "__invalid_absolute_path__"
    else:
        target = (skill_dir / rel).resolve()
        try:
            target.relative_to(skill_dir.resolve())
        except ValueError:
            failures.append(f"{annotation_id(raw)}: target_path escapes skill directory")
            target = skill_dir / "__invalid_escaped_path__"

    line_value = raw.get("line", None)
    line: int | None
    if line_value is None or line_value == "":
        line = None
    else:
        try:
            line = int(line_value)
        except (TypeError, ValueError):
            line = None
            failures.append(f"{annotation_id(raw)}: line must be a positive integer")
        else:
            if line < 1:
                failures.append(f"{annotation_id(raw)}: line must be a positive integer")

    normalized = {
        "id": annotation_id(raw),
        "gate_key": gate_key,
        "target_path": target_path,
        "line": line,
        "severity": severity,
        "status": status,
        "reviewer": str(raw.get("reviewer", "")).strip(),
        "created_at": str(raw.get("created_at", "")).strip(),
        "body": body,
        "suggested_action": str(raw.get("suggested_action", "")).strip(),
        "evidence": str(raw.get("evidence", "")).strip(),
        "target_exists": target.exists(),
        "source_excerpt": source_excerpt(target, line),
    }
    return normalized, failures


def append_annotation(source: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    annotations = list(source.get("annotations", []))
    raw = {
        "id": args.annotation_id,
        "gate_key": args.gate_key,
        "target_path": args.target_path,
        "line": args.line,
        "severity": args.severity,
        "status": args.status,
        "reviewer": args.reviewer,
        "created_at": args.created_at or str(date.today()),
        "body": args.body,
        "suggested_action": args.suggested_action,
        "evidence": args.evidence,
    }
    annotations.append({key: value for key, value in raw.items() if value is not None and value != ""})
    updated = dict(source)
    updated["annotations"] = annotations
    updated.setdefault("schema_version", "1.0")
    return updated


def build_summary(annotations: list[dict[str, Any]], failures: list[str]) -> dict[str, Any]:
    open_items = [item for item in annotations if item["status"] == "open"]
    resolved_items = [item for item in annotations if item["status"] == "resolved"]
    deferred_items = [item for item in annotations if item["status"] == "deferred"]
    open_blockers = [item for item in open_items if item["severity"] == "blocker"]
    open_warnings = [item for item in open_items if item["severity"] == "warning"]
    return {
        "annotation_count": len(annotations),
        "open_count": len(open_items),
        "resolved_count": len(resolved_items),
        "deferred_count": len(deferred_items),
        "open_blocker_count": len(open_blockers),
        "open_warning_count": len(open_warnings),
        "linked_gate_count": len({item["gate_key"] for item in annotations if item["gate_key"]}),
        "target_missing_count": sum(1 for item in annotations if not item["target_exists"]),
        "failure_count": len(failures),
    }


def render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Review Annotations",
        "",
        "This report renders reviewer annotations attached to Review Studio gates and source/report paths.",
        "",
        f"- Annotations: `{summary['annotation_count']}`",
        f"- Open: `{summary['open_count']}`",
        f"- Resolved: `{summary['resolved_count']}`",
        f"- Deferred: `{summary['deferred_count']}`",
        f"- Open blockers: `{summary['open_blocker_count']}`",
        f"- Open warnings: `{summary['open_warning_count']}`",
        "",
    ]
    if not payload["annotations"]:
        lines.extend(["No reviewer annotations recorded yet.", ""])
    else:
        lines.extend(
            [
                "## Annotation Ledger",
                "",
                "| ID | Gate | Severity | Status | Target | Reviewer | Note |",
                "| --- | --- | --- | --- | --- | --- | --- |",
            ]
        )
        for item in payload["annotations"]:
            line = f":{item['line']}" if item.get("line") else ""
            note = item["body"].replace("|", "\\|")
            lines.append(
                f"| {item['id']} | {item['gate_key']} | {item['severity']} | {item['status']} | "
                f"{item['target_path']}{line} | {item.get('reviewer', '')} | {note} |"
            )
            if item.get("source_excerpt"):
                excerpt = str(item["source_excerpt"]).replace("|", "\\|")
                lines.append(f"|  |  |  |  |  | excerpt | `{excerpt}` |")
    if payload.get("failures"):
        lines.extend(["", "## Failures", ""])
        for failure in payload["failures"]:
            lines.append(f"- {failure}")
    lines.extend(
        [
            "",
            "## Review Rule",
            "",
            "- Use annotations for reviewer comments tied to a gate or source line.",
            "- Use waivers only for explicit acceptance of warning-level release risk.",
            "- Open blocker annotations should block a release decision until resolved or deferred with rationale.",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def render_review_annotations(
    skill_dir: Path,
    source_json: Path,
    output_json: Path,
    output_md: Path,
    args: argparse.Namespace,
) -> dict[str, Any]:
    skill_dir = skill_dir.resolve()
    source, failures = load_json(source_json)
    template_written = False
    should_write_source = False
    if args.write_template and not source_json.exists():
        source_json.parent.mkdir(parents=True, exist_ok=True)
        source_json.write_text(json.dumps(template_payload(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        source = template_payload()
        template_written = True
    if args.add_annotation:
        source = append_annotation(source, args)
        should_write_source = True

    annotations: list[dict[str, Any]] = []
    seen = set()
    for index, raw in enumerate(source.get("annotations", []), start=1):
        normalized, item_failures = normalize_annotation(skill_dir, raw, index)
        failures.extend(item_failures)
        if normalized:
            if normalized["id"] in seen:
                failures.append(f"{normalized['id']}: duplicate annotation id")
            seen.add(normalized["id"])
            annotations.append(normalized)

    summary = build_summary(annotations, failures)
    if should_write_source and not failures:
        source_json.parent.mkdir(parents=True, exist_ok=True)
        source_json.write_text(json.dumps(source, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    payload = {
        "schema_version": "1.0",
        "ok": not failures,
        "skill_dir": display_path(ROOT, skill_dir),
        "source": display_path(skill_dir, source_json),
        "summary": summary,
        "annotations": annotations,
        "failures": failures,
        "template_written": template_written,
        "artifacts": {
            "json": display_path(skill_dir, output_json),
            "markdown": display_path(skill_dir, output_md),
        },
    }
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    output_md.write_text(render_markdown(payload), encoding="utf-8")
    return payload


def render_report(
    skill_dir: Path,
    annotations_json: Path | None = None,
    output_json: Path | None = None,
    output_md: Path | None = None,
) -> dict[str, Any]:
    skill_dir = skill_dir.resolve()
    args = argparse.Namespace(
        write_template=False,
        add_annotation=False,
        annotation_id=None,
        gate_key=None,
        target_path=None,
        line=None,
        severity="note",
        status="open",
        reviewer=None,
        created_at=None,
        body=None,
        suggested_action=None,
        evidence=None,
    )
    return render_review_annotations(
        skill_dir,
        annotations_json or skill_dir / "reports" / "review_annotations_input.json",
        output_json or skill_dir / "reports" / "review_annotations.json",
        output_md or skill_dir / "reports" / "review_annotations.md",
        args,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Render reviewer annotations for Review Studio gates and source paths.")
    parser.add_argument("skill_dir", nargs="?", default=".")
    parser.add_argument("--annotations-json")
    parser.add_argument("--output-json")
    parser.add_argument("--output-md")
    parser.add_argument("--write-template", action="store_true")
    parser.add_argument("--add-annotation", action="store_true")
    parser.add_argument("--annotation-id")
    parser.add_argument("--gate-key", choices=sorted(VALID_GATES))
    parser.add_argument("--target-path")
    parser.add_argument("--line", type=int)
    parser.add_argument("--severity", choices=sorted(VALID_SEVERITIES), default="note")
    parser.add_argument("--status", choices=sorted(VALID_STATUSES), default="open")
    parser.add_argument("--reviewer")
    parser.add_argument("--created-at")
    parser.add_argument("--body")
    parser.add_argument("--suggested-action")
    parser.add_argument("--evidence")
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir).resolve()
    annotations_json = Path(args.annotations_json).resolve() if args.annotations_json else skill_dir / "reports" / "review_annotations_input.json"
    output_json = Path(args.output_json).resolve() if args.output_json else skill_dir / "reports" / "review_annotations.json"
    output_md = Path(args.output_md).resolve() if args.output_md else skill_dir / "reports" / "review_annotations.md"

    if args.add_annotation:
        missing = [name for name in ("gate_key", "target_path", "body") if not getattr(args, name)]
        if missing:
            payload = {
                "schema_version": "1.0",
                "ok": False,
                "skill_dir": display_path(ROOT, skill_dir),
                "source": display_path(skill_dir, annotations_json),
                "summary": build_summary([], missing),
                "annotations": [],
                "failures": [f"--add-annotation requires {', '.join(missing)}"],
                "template_written": False,
                "artifacts": {
                    "json": display_path(skill_dir, output_json),
                    "markdown": display_path(skill_dir, output_md),
                },
            }
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            raise SystemExit(2)

    payload = render_review_annotations(skill_dir, annotations_json, output_json, output_md, args)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    raise SystemExit(0 if payload["ok"] else 2)


if __name__ == "__main__":
    main()
