from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "write_evidence.py"
SPEC = importlib.util.spec_from_file_location("write_evidence", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class WriteEvidenceTests(unittest.TestCase):
    def test_accepts_safe_node_id(self) -> None:
        self.assertEqual(MODULE.validate_node_id("build-01"), "build-01")

    def test_rejects_path_escape(self) -> None:
        with self.assertRaises(ValueError):
            MODULE.validate_node_id("../outside")

    def test_detects_bearer_value(self) -> None:
        self.assertTrue(MODULE.contains_sensitive_content("Authorization: Bearer example-secret"))

    def test_writes_inside_evidence_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = MODULE.safe_target(Path(directory), "test-01")
            target.write_text(MODULE.build_record("test-01", "Test record", "Safe output"), encoding="utf-8")
            self.assertEqual(target.parent.name, "evidence")
            self.assertIn("Safe output", target.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
