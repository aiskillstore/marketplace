#!/usr/bin/env python3
import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from skill_ir_paths import candidate_paths, find_skill_ir, find_skill_ir_path  # noqa: E402


TMP = ROOT / "tests" / "tmp_skill_ir_paths"


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    shutil.rmtree(TMP, ignore_errors=True)
    TMP.mkdir(parents=True, exist_ok=True)

    root_ir, root_path = find_skill_ir(ROOT, "yao-meta-skill", require_schema=True)
    assert root_path == "skill-ir/examples/yao-meta-skill.json", root_path
    assert root_ir["schema_version"] == "2.0.0", root_ir
    assert find_skill_ir_path(ROOT, "yao-meta-skill", require_schema=True) == root_path

    preferred = TMP / "reports" / "skill-ir.json"
    example = TMP / "skill-ir" / "examples" / "demo-skill.json"
    write_json(preferred, {"schema_version": "2.0.0", "name": "reports-copy"})
    write_json(example, {"schema_version": "2.0.0", "name": "example-copy"})
    payload, source = find_skill_ir(TMP, "demo-skill", require_schema=True)
    assert source == "reports/skill-ir.json", source
    assert payload["name"] == "reports-copy", payload

    preferred.unlink()
    payload, source = find_skill_ir(TMP, "demo-skill", require_schema=True)
    assert source == "skill-ir/examples/demo-skill.json", source
    assert payload["name"] == "example-copy", payload

    example.unlink()
    write_json(TMP / "skill-ir" / "examples" / "zzz-extra.json", {"schema_version": "2.0.0", "name": "wildcard"})
    payload, source = find_skill_ir(TMP, "missing-name", require_schema=True)
    assert source == "skill-ir/examples/zzz-extra.json", source
    assert payload["name"] == "wildcard", payload

    (TMP / "skill-ir" / "examples" / "zzz-extra.json").unlink()
    write_json(TMP / "reports" / "skill-ir.json", {"name": "no-schema"})
    assert find_skill_ir_path(TMP, "demo-skill", require_schema=True, fallback_source="missing") == "missing"
    assert find_skill_ir_path(TMP, "demo-skill", require_schema=False) == "reports/skill-ir.json"

    paths = [str(path.relative_to(TMP)) for path in candidate_paths(TMP, "demo-skill")]
    assert paths[:3] == [
        "reports/skill-ir.json",
        "skill-ir/examples/demo-skill.json",
        "skill-ir/examples/tmp_skill_ir_paths.json",
    ], paths

    print(json.dumps({"ok": True}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
