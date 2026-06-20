#!/usr/bin/env python3
import argparse
import json
import shlex
from pathlib import Path
from typing import Any

from render_adoption_drift_report import SENSITIVE_FIELDS, display_path


SCHEMA_VERSION = "1.0"
DEFAULT_RECIPES = [
    {
        "id": "browser-extension",
        "client": "Browser extension",
        "command": "browser-extension",
        "event": "skill_activation",
        "activation_type": "explicit",
        "outcome": "accepted",
        "failure_type": "none",
        "trigger_points": [
            "Skill is explicitly selected by the user.",
            "Skill activation is accepted by the host client.",
        ],
    },
    {
        "id": "chrome-extension",
        "client": "Chrome extension",
        "command": "chrome-extension",
        "event": "skill_output",
        "activation_type": "manual",
        "outcome": "edited",
        "failure_type": "none",
        "trigger_points": [
            "User keeps or edits a skill-generated artifact.",
            "Extension records only the final outcome class, not page content.",
        ],
    },
    {
        "id": "vscode-extension",
        "client": "VS Code extension",
        "command": "vscode-extension",
        "event": "skill_activation",
        "activation_type": "implicit",
        "outcome": "accepted",
        "failure_type": "none",
        "trigger_points": [
            "Workspace skill route chooses this skill.",
            "Extension records route outcome without file paths or code snippets.",
        ],
    },
    {
        "id": "cli-wrapper",
        "client": "CLI wrapper",
        "command": "cli-wrapper",
        "event": "script_run",
        "activation_type": "manual",
        "outcome": "unknown",
        "failure_type": "none",
        "trigger_points": [
            "Wrapper starts or finishes a known skill workflow command.",
            "Wrapper records command family only, never command arguments.",
        ],
    },
    {
        "id": "provider-adapter",
        "client": "Provider adapter",
        "command": "provider-adapter",
        "event": "skill_output",
        "activation_type": "manual",
        "outcome": "accepted",
        "failure_type": "none",
        "trigger_points": [
            "Provider adapter receives an accepted or rejected skill output signal.",
            "Adapter records only normalized outcome metadata.",
        ],
    },
]


def default_spool(skill_dir: Path) -> Path:
    return skill_dir / ".yao" / "telemetry_spool" / "external_events.jsonl"


def command_text(argv: list[str]) -> str:
    return shlex.join(argv)


def emit_argv(skill_dir: Path, output_jsonl: Path, recipe: dict[str, Any], dry_run: bool = False) -> list[str]:
    argv = [
        "python3",
        "scripts/yao.py",
        "telemetry-emit",
        display_path(skill_dir),
        "--output-jsonl",
        display_path(output_jsonl),
        "--event",
        recipe["event"],
        "--activation-type",
        recipe["activation_type"],
        "--outcome",
        recipe["outcome"],
        "--failure-type",
        recipe["failure_type"],
        "--command",
        recipe["command"],
    ]
    if dry_run:
        argv.append("--dry-run")
    return argv


def import_argv(skill_dir: Path, output_jsonl: Path) -> list[str]:
    return [
        "python3",
        "scripts/yao.py",
        "telemetry-import",
        display_path(skill_dir),
        "--input-jsonl",
        display_path(output_jsonl),
    ]


def build_recipe(skill_dir: Path, output_jsonl: Path, recipe: dict[str, Any]) -> dict[str, Any]:
    emit = emit_argv(skill_dir, output_jsonl, recipe)
    dry_run = emit_argv(skill_dir, output_jsonl, recipe, dry_run=True)
    return {
        **recipe,
        "source": "external",
        "native_auto_capture": False,
        "integration_status": "client-hook-recipe",
        "metadata_only": True,
        "emit_argv": emit,
        "emit_command": command_text(emit),
        "dry_run_argv": dry_run,
        "dry_run_command": command_text(dry_run),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Telemetry Hook Recipes",
        "",
        "These recipes show how Browser, Chrome, IDE, wrapper, or provider-side integrations can call `telemetry-emit` without collecting raw prompts, outputs, transcripts, messages, notes, arguments, or file content.",
        "",
        "They are client hook recipes, not proof that a host client is already natively integrated.",
        "",
        "## Summary",
        "",
        f"- Recipe count: `{report['summary']['recipe_count']}`",
        f"- Native auto-capture integrations claimed: `{report['summary']['native_auto_capture_count']}`",
        f"- Default spool: `{report['artifacts']['spool_jsonl']}`",
        "",
        "## Recipes",
        "",
        "| Client | Command | Event | Outcome | Dry run |",
        "| --- | --- | --- | --- | --- |",
    ]
    for recipe in report["recipes"]:
        lines.append(
            f"| {recipe['client']} | `{recipe['command']}` | `{recipe['event']}` | `{recipe['outcome']}` | `{recipe['dry_run_command']}` |"
        )
    lines.extend(
        [
            "",
            "## Import",
            "",
            "After a client finishes a batch, import the local spool:",
            "",
            "```bash",
            report["artifacts"]["import_command"],
            "```",
            "",
            "## Privacy Contract",
            "",
            "- Allowed fields: `event`, `skill`, `version`, `source`, `command`, `activation_type`, `outcome`, `failure_type`, `timestamp`.",
            f"- Blocked raw-content fields: `{', '.join(report['privacy_contract']['blocked_fields'])}`.",
            "- Client integrations must map local state to normalized outcome classes before calling the hook.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_recipes(
    skill_dir: Path,
    output_json: Path | None = None,
    output_md: Path | None = None,
    output_jsonl: Path | None = None,
) -> dict[str, Any]:
    skill_dir = skill_dir.resolve()
    reports_dir = skill_dir / "reports"
    output_json = (output_json or reports_dir / "telemetry_hook_recipes.json").resolve()
    output_md = (output_md or reports_dir / "telemetry_hook_recipes.md").resolve()
    output_jsonl = (output_jsonl or default_spool(skill_dir)).resolve()
    recipes = [build_recipe(skill_dir, output_jsonl, recipe) for recipe in DEFAULT_RECIPES]
    import_cmd = import_argv(skill_dir, output_jsonl)
    report = {
        "ok": True,
        "schema_version": SCHEMA_VERSION,
        "skill_dir": display_path(skill_dir),
        "summary": {
            "recipe_count": len(recipes),
            "native_auto_capture_count": sum(1 for recipe in recipes if recipe["native_auto_capture"]),
            "metadata_only_recipe_count": sum(1 for recipe in recipes if recipe["metadata_only"]),
        },
        "privacy_contract": {
            "raw_content_allowed": False,
            "blocked_fields": sorted(SENSITIVE_FIELDS),
            "allowed_fields": [
                "event",
                "skill",
                "version",
                "source",
                "command",
                "activation_type",
                "outcome",
                "failure_type",
                "timestamp",
            ],
        },
        "recipes": recipes,
        "artifacts": {
            "json": display_path(output_json),
            "markdown": display_path(output_md),
            "spool_jsonl": display_path(output_jsonl),
            "import_command": command_text(import_cmd),
            "import_argv": import_cmd,
        },
        "warnings": [
            "These recipes do not prove native host-client integration; they define the local metadata-only hook contract for those integrations."
        ],
        "failures": [],
    }
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    output_md.write_text(render_markdown(report), encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Render metadata-only telemetry client hook recipes.")
    parser.add_argument("skill_dir", nargs="?", default=".")
    parser.add_argument("--output-json")
    parser.add_argument("--output-md")
    parser.add_argument("--output-jsonl")
    args = parser.parse_args()
    report = render_recipes(
        Path(args.skill_dir),
        output_json=Path(args.output_json) if args.output_json else None,
        output_md=Path(args.output_md) if args.output_md else None,
        output_jsonl=Path(args.output_jsonl) if args.output_jsonl else None,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
