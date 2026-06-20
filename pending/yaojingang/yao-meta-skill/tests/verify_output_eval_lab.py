#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "run_output_eval.py"


def main() -> None:
    tmp_root = ROOT / "tests" / "tmp_output_eval"
    tmp_root.mkdir(parents=True, exist_ok=True)
    output_json = tmp_root / "output_quality_scorecard.json"
    output_md = tmp_root / "output_quality_scorecard.md"
    blind_pack_json = tmp_root / "output_blind_review_pack.json"
    blind_pack_md = tmp_root / "output_blind_review_pack.md"
    blind_answer_key_json = tmp_root / "output_blind_answer_key.json"
    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--cases",
            str(ROOT / "evals" / "output" / "cases.jsonl"),
            "--output-json",
            str(output_json),
            "--output-md",
            str(output_md),
            "--blind-pack-json",
            str(blind_pack_json),
            "--blind-pack-md",
            str(blind_pack_md),
            "--blind-answer-key-json",
            str(blind_answer_key_json),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(proc.stdout)
    assert payload["ok"], payload
    assert payload["summary"]["case_count"] == 5, payload
    assert payload["summary"]["file_backed_case_count"] == 1, payload
    assert payload["summary"]["near_neighbor_case_count"] == 1, payload
    assert payload["summary"]["boundary_case_count"] == 1, payload
    assert payload["summary"]["with_skill_pass_rate"] > payload["summary"]["baseline_pass_rate"], payload
    assert payload["summary"]["delta"] > 0, payload
    assert payload["summary"]["gate_pass"], payload
    assert payload["summary"]["blind_pair_count"] == 5, payload
    assert payload["blind_review"]["pair_count"] == 5, payload
    assert output_json.exists(), output_json
    assert output_md.exists(), output_md
    assert blind_pack_json.exists(), blind_pack_json
    assert blind_pack_md.exists(), blind_pack_md
    assert blind_answer_key_json.exists(), blind_answer_key_json
    blind_pack = json.loads(blind_pack_json.read_text(encoding="utf-8"))
    answer_key = json.loads(blind_answer_key_json.read_text(encoding="utf-8"))
    assert blind_pack["summary"]["pair_count"] == 5, blind_pack
    assert blind_pack["summary"]["answer_key_separate"], blind_pack
    assert answer_key["summary"]["pair_count"] == 5, answer_key
    assert "variant_a_role" not in json.dumps(blind_pack, ensure_ascii=False), blind_pack
    assert "variant_b_role" not in json.dumps(blind_pack, ensure_ascii=False), blind_pack
    assert "variant_a_role" in json.dumps(answer_key, ensure_ascii=False), answer_key
    assert all(pair["review_instruction"].startswith("Pick A or B") for pair in blind_pack["pairs"]), blind_pack
    markdown = output_md.read_text(encoding="utf-8")
    assert "Output Quality Scorecard" in markdown, markdown[:400]
    assert "with-skill" in markdown, markdown[:600]
    assert "Blind A/B pairs" in markdown, markdown[:800]
    assert "Failure Taxonomy" in markdown, markdown[:1200]
    blind_markdown = blind_pack_md.read_text(encoding="utf-8")
    assert "Output Blind A/B Review Pack" in blind_markdown, blind_markdown[:400]
    assert "Answer key separate" in blind_markdown, blind_markdown[:600]

    invalid_cases = tmp_root / "invalid_cases.jsonl"
    invalid_cases.write_text(json.dumps({"id": "bad", "prompt": "x"}) + "\n", encoding="utf-8")
    invalid_proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--cases",
            str(invalid_cases),
            "--output-json",
            str(tmp_root / "invalid.json"),
            "--output-md",
            str(tmp_root / "invalid.md"),
            "--blind-pack-json",
            str(tmp_root / "invalid_blind.json"),
            "--blind-pack-md",
            str(tmp_root / "invalid_blind.md"),
            "--blind-answer-key-json",
            str(tmp_root / "invalid_answer_key.json"),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert invalid_proc.returncode == 2, invalid_proc.stdout
    invalid_payload = json.loads(invalid_proc.stdout)
    assert not invalid_payload["ok"], invalid_payload
    assert invalid_payload["failures"], invalid_payload

    print(json.dumps({"ok": True}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
