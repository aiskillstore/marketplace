import importlib.util
import json
import unittest
from pathlib import Path


PACKAGE = Path(__file__).parents[1]
SCRIPT = PACKAGE / "scripts" / "audit.py"
SPEC = importlib.util.spec_from_file_location("inventory_audit", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def fixture(name):
    return json.loads((Path(__file__).parent / "fixtures" / name).read_text())


class AuditTests(unittest.TestCase):
    def test_success_accounts_for_both_sides(self):
        result = MODULE.calculate(fixture("success.json"))

        self.assertEqual(result["verification"], "EXHAUSTIVE REVIEW PACKAGE")
        self.assertEqual(result["record_count"], 3)
        self.assertEqual(result["observation_count"], 3)
        self.assertEqual(result["unaccounted_records"], [])
        self.assertEqual(result["external_edit"], "not performed")

    def test_edge_preserves_uncertain_duplicate(self):
        result = MODULE.calculate(fixture("edge.json"))

        self.assertEqual(result["counts"]["needs_review"], 1)
        self.assertEqual(result["counts"]["observation_needs_review"], 1)
        self.assertNotIn("observation_duplicate", result["counts"])

    def test_unaccounted_record_fails(self):
        payload = fixture("success.json")
        payload["record_dispositions"] = []

        with self.assertRaisesRegex(MODULE.InputError, "unaccounted record"):
            MODULE.calculate(payload)

    def test_duplicate_link_fails(self):
        payload = fixture("success.json")
        payload["links"][1]["record_id"] = "r1"

        with self.assertRaisesRegex(MODULE.InputError, "linked more than once"):
            MODULE.calculate(payload)


if __name__ == "__main__":
    unittest.main()
