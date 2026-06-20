#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    proc = subprocess.run(
        [sys.executable, "scripts/promotion_checker.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    payload = json.loads(proc.stdout)
    if proc.returncode != 0:
        raise SystemExit(proc.returncode)

    summary = payload["summary"]
    assert summary["blocked"] == 0, payload
    assert summary["keep_current"] >= 1, payload

    targets = payload["targets"]
    assert len(targets) >= 3, payload

    candidate_registry = json.loads((ROOT / "reports" / "candidate_registry.json").read_text(encoding="utf-8"))
    assert len(candidate_registry["targets"]) == len(targets)

    for target in targets:
        assert target["decision"] in {"promote", "keep_current", "blocked"}
        assert target["promotion"]["gate_status"]["route_confusion_clean"] is True
        assert target["promotion"]["gate_status"]["judge_blind_agreement"] is True
        assert target["promotion"]["causes"], target
        if target["winner_label"] == "Current":
            assert target["decision"] == "keep_current", target
        if target["name"] == "governed-incident-command":
            assert "current_holdout_gap_present" in target["promotion"]["causes"], target

        bundle_dir = ROOT / "reports" / "iteration_bundles" / target["name"]
        assert (bundle_dir / "bundle.json").exists(), bundle_dir
        assert (bundle_dir / "bundle.md").exists(), bundle_dir
        assert (bundle_dir / "review.md").exists(), bundle_dir

        registry_entries = target["registry"]
        roles = {entry["role"] for entry in registry_entries}
        assert "baseline" in roles and "current" in roles, target
        assert any(entry["role"] == "candidate" for entry in registry_entries), target

    print(json.dumps({"ok": True, "summary": summary}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
