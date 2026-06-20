#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
import yaml


VALID_EXECUTION_CONTEXTS = {"inline", "fork"}
VALID_SHELLS = {"bash", "powershell"}
VALID_SOURCE_TIERS = {"local", "managed", "plugin", "remote"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a skill package.")
    parser.add_argument("skill_dir")
    args = parser.parse_args()

    root = Path(args.skill_dir).resolve()
    failures = []
    warnings = []
    skill_md = root / "SKILL.md"
    interface = root / "agents" / "interface.yaml"
    manifest = root / "manifest.json"

    if not skill_md.exists():
        failures.append("Missing SKILL.md")
    if not interface.exists():
        failures.append("Missing agents/interface.yaml")

    if skill_md.exists():
        text = skill_md.read_text(encoding="utf-8")
        if not text.startswith("---"):
            failures.append("SKILL.md missing frontmatter")
        else:
            parts = text.split("---", 2)
            data = yaml.safe_load(parts[1]) or {}
            for field in ("name", "description"):
                if not data.get(field):
                    failures.append(f"Missing frontmatter field: {field}")

    if interface.exists():
        data = yaml.safe_load(interface.read_text(encoding="utf-8")) or {}
        meta = data.get("interface", {})
        compatibility = data.get("compatibility", {})
        activation = compatibility.get("activation", {})
        execution = compatibility.get("execution", {})
        trust = compatibility.get("trust", {})
        degradation = compatibility.get("degradation", {})
        for field in ("display_name", "short_description", "default_prompt"):
            if not meta.get(field):
                failures.append(f"Missing interface field: {field}")
        if not compatibility.get("canonical_format"):
            failures.append("Missing compatibility field: canonical_format")
        adapter_targets = compatibility.get("adapter_targets")
        if not adapter_targets or not isinstance(adapter_targets, list):
            failures.append("Missing compatibility field: adapter_targets")
            adapter_targets = []
        if not activation.get("mode"):
            failures.append("Missing compatibility.activation.mode")
        if activation.get("mode") == "path_scoped" and not activation.get("paths"):
            failures.append("path_scoped activation requires compatibility.activation.paths")
        if execution.get("context") not in VALID_EXECUTION_CONTEXTS:
            failures.append("Invalid compatibility.execution.context")
        if execution.get("shell") not in VALID_SHELLS:
            failures.append("Invalid compatibility.execution.shell")
        if trust.get("source_tier") not in VALID_SOURCE_TIERS:
            failures.append("Invalid compatibility.trust.source_tier")
        if trust.get("remote_inline_execution") not in {"forbid", "allow"}:
            failures.append("Invalid compatibility.trust.remote_inline_execution")
        if not trust.get("remote_metadata_policy"):
            failures.append("Missing compatibility.trust.remote_metadata_policy")
        for target in adapter_targets:
            if target not in degradation:
                failures.append(f"Missing compatibility.degradation entry for target: {target}")

    if manifest.exists():
        data = json.loads(manifest.read_text(encoding="utf-8"))
        for field in ("name", "version", "owner", "updated_at"):
            if not data.get(field):
                failures.append(f"Missing manifest field: {field}")
        if not data.get("review_cadence"):
            warnings.append("Manifest exists without review_cadence.")
        if not data.get("status"):
            warnings.append("Manifest exists without status.")
        if not data.get("maturity_tier"):
            warnings.append("Manifest exists without maturity_tier.")

    print(json.dumps({"ok": not failures, "failures": failures, "warnings": warnings}, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
