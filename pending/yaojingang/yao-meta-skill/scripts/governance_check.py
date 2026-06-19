#!/usr/bin/env python3
import argparse
import json
from datetime import datetime
from pathlib import Path


ALLOWED_STATUS = {"experimental", "active", "deprecated"}
ALLOWED_MATURITY = {"scaffold", "production", "library", "governed"}
ALLOWED_REVIEW_CADENCE = {"monthly", "quarterly", "semiannual", "annual", "per-release"}
DECLARED_MATURITY_MIN_SCORE = {
    "scaffold": 0,
    "production": 80,
    "library": 85,
    "governed": 90,
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_frontmatter(skill_md: Path) -> dict:
    if not skill_md.exists():
        return {}
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    payload = {}
    for line in parts[1].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        payload[key.strip()] = value.strip().strip("'\"")
    return payload


def has_files(path: Path) -> bool:
    return path.exists() and any(child.is_file() for child in path.rglob("*"))


def score_label(score: int) -> str:
    if score >= 90:
        return "governed"
    if score >= 80:
        return "production"
    if score >= 65:
        return "reusable"
    if score >= 45:
        return "emerging"
    return "draft"


def compute_score(root: Path, manifest: dict, frontmatter: dict, skill_text: str, manifest_valid: bool) -> tuple[int, dict]:
    breakdown = {
        "metadata_integrity": 0,
        "ownership_and_review": 0,
        "boundary_and_eval": 0,
        "operational_assets": 0,
        "maintenance_evidence": 0,
    }

    if manifest_valid and manifest:
        breakdown["metadata_integrity"] += 4
    if manifest.get("name") and frontmatter.get("name") and manifest["name"] == frontmatter["name"]:
        breakdown["metadata_integrity"] += 4
    if manifest.get("version"):
        breakdown["metadata_integrity"] += 3
    if manifest.get("updated_at"):
        breakdown["metadata_integrity"] += 3
    if manifest.get("status") in ALLOWED_STATUS:
        breakdown["metadata_integrity"] += 3
    if manifest.get("maturity_tier") in ALLOWED_MATURITY:
        breakdown["metadata_integrity"] += 3

    if manifest.get("owner"):
        breakdown["ownership_and_review"] += 10
    if manifest.get("review_cadence") in ALLOWED_REVIEW_CADENCE:
        breakdown["ownership_and_review"] += 10

    if frontmatter.get("description"):
        breakdown["boundary_and_eval"] += 5
    if any(marker in skill_text.lower() for marker in ("do not use", "out of scope", "should not trigger", "do not")):
        breakdown["boundary_and_eval"] += 10
    if has_files(root / "evals"):
        breakdown["boundary_and_eval"] += 10

    if (root / "agents" / "interface.yaml").exists():
        breakdown["operational_assets"] += 5
    if has_files(root / "references"):
        breakdown["operational_assets"] += 5
    if has_files(root / "scripts"):
        breakdown["operational_assets"] += 5
    if manifest.get("factory_components") or manifest.get("target_platforms"):
        breakdown["operational_assets"] += 5

    if has_files(root / "reports"):
        breakdown["maintenance_evidence"] += 5
    if has_files(root / "evals" / "history") or has_files(root / "failures"):
        breakdown["maintenance_evidence"] += 5
    if (
        has_files(root / "outputs")
        or has_files(root / "assets")
        or has_files(root / "examples")
        or has_files(root / "tests")
    ):
        breakdown["maintenance_evidence"] += 5

    total = sum(breakdown.values())
    return total, breakdown


def main() -> None:
    parser = argparse.ArgumentParser(description="Check skill governance metadata and lifecycle readiness.")
    parser.add_argument("skill_dir")
    parser.add_argument("--require-manifest", action="store_true")
    args = parser.parse_args()

    root = Path(args.skill_dir).resolve()
    manifest_path = root / "manifest.json"
    skill_md = root / "SKILL.md"
    failures = []
    warnings = []
    details = {"skill_dir": str(root), "manifest_present": manifest_path.exists()}

    frontmatter = read_frontmatter(skill_md)
    skill_text = skill_md.read_text(encoding="utf-8") if skill_md.exists() else ""
    manifest = {}
    manifest_valid = False
    if manifest_path.exists():
        try:
            manifest = load_json(manifest_path)
            manifest_valid = True
        except json.JSONDecodeError as exc:
            failures.append(f"Invalid manifest.json: {exc}")
    elif args.require_manifest:
        failures.append("Missing manifest.json")
    else:
        warnings.append("No manifest.json; governance metadata is unavailable.")

    if manifest:
        required = ["name", "version", "owner", "updated_at", "review_cadence", "status", "maturity_tier", "lifecycle_stage"]
        missing = [field for field in required if not manifest.get(field)]
        if missing:
            failures.append(f"Missing manifest fields: {', '.join(missing)}")

        if manifest.get("status") and manifest["status"] not in ALLOWED_STATUS:
            failures.append(f"Invalid status: {manifest['status']}")
        if manifest.get("maturity_tier") and manifest["maturity_tier"] not in ALLOWED_MATURITY:
            failures.append(f"Invalid maturity_tier: {manifest['maturity_tier']}")
        if manifest.get("lifecycle_stage") and manifest["lifecycle_stage"] not in ALLOWED_MATURITY:
            failures.append(f"Invalid lifecycle_stage: {manifest['lifecycle_stage']}")
        if manifest.get("review_cadence") and manifest["review_cadence"] not in ALLOWED_REVIEW_CADENCE:
            failures.append(f"Invalid review_cadence: {manifest['review_cadence']}")
        if manifest.get("updated_at"):
            try:
                datetime.strptime(manifest["updated_at"], "%Y-%m-%d")
            except ValueError:
                failures.append("updated_at must use YYYY-MM-DD")

        if frontmatter.get("name") and manifest.get("name") and frontmatter["name"] != manifest["name"]:
            failures.append("manifest name does not match SKILL.md frontmatter name")

        if manifest.get("status") == "deprecated" and not manifest.get("deprecation_note"):
            warnings.append("Deprecated skill should include deprecation_note in manifest.json.")

    score, breakdown = compute_score(root, manifest, frontmatter, skill_text, manifest_valid)
    computed_label = score_label(score)
    declared_tier = manifest.get("maturity_tier")
    required_minimum = DECLARED_MATURITY_MIN_SCORE.get(declared_tier)
    if declared_tier in ALLOWED_MATURITY and required_minimum is not None and score < required_minimum:
        warnings.append(
            f"Maturity tier says {declared_tier} but governance score is {score}/100, below the recommended minimum {required_minimum}."
        )

    report = {
        "ok": not failures,
        "failures": failures,
        "warnings": warnings,
        "details": {
            **details,
            "frontmatter_name": frontmatter.get("name"),
            "manifest_name": manifest.get("name"),
            "status": manifest.get("status"),
            "maturity_tier": manifest.get("maturity_tier"),
            "review_cadence": manifest.get("review_cadence"),
            "governance_score": score,
            "declared_maturity_minimum": required_minimum,
            "computed_governance_band": computed_label,
            "computed_maturity_tier": computed_label,
            "score_breakdown": breakdown,
        },
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
