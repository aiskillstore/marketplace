"""Lineage tests for the native-to-port meaning contract."""
import json
import pathlib
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]
EXPECTED_FILES = {
    "SKILL.md": "dac89519a06ca944c0a14e2b0a46fdc1687627cb80014d55d6efbb2e31143e4c",
    "references/eval-contract.md": "e20a0622b583f2c9c78e6d21cf335a5dbf886c9b3a352bac1376c65f3058b97e",
    "references/eval-cases.json": "1245c83719bd94418654567f23f4dade91b6226eab400c9e79f2b893e695b8aa",
    "scripts/current_anchor.py": "dc2e2ff4edc302ed26b2b194ab6db31c5a6badf2223f42efd2d9ef088819b68f",
}
EXPECTED_CASES = [f"ACDT-{number:03d}" for number in range(1, 13)]


def load(relative):
    return json.loads((SKILL_DIR / relative).read_text(encoding="utf-8"))


class TestSourceMapping(unittest.TestCase):
    def test_lineage_binds_every_native_file_and_case(self):
        lineage = load("evals/source-lineage.json")
        files = {entry["path"]: entry["sha256"]
                 for entry in lineage["source_files"]}
        self.assertEqual(files, EXPECTED_FILES)
        self.assertEqual(lineage["source_case_ids"], EXPECTED_CASES)
        self.assertEqual(
            lineage["native_manifest_sha256"],
            "b647248569c7664ae8dcba5161a748ccfc7eafa33c5d9bb6d5378fed63c9bc86",
        )

    def test_mapping_has_no_drop_and_covers_every_source_section(self):
        mapping = load("evals/source-mapping.json")
        self.assertEqual(mapping["source_files"], list(EXPECTED_FILES))
        self.assertEqual(mapping["source_case_ids"], EXPECTED_CASES)
        self.assertEqual(mapping["coverage"], 1.0)
        self.assertNotIn("drop", {entry["action"] for entry in mapping["clauses"]})
        covered = {entry["source_path"] for entry in mapping["clauses"]}
        self.assertEqual(covered, set(EXPECTED_FILES))


if __name__ == "__main__":
    unittest.main()
