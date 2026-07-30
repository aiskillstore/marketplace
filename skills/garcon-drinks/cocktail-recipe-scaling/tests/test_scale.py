import importlib.util
import json
import unittest
from pathlib import Path


PACKAGE = Path(__file__).parents[1]
SCRIPT = PACKAGE / "scripts" / "scale.py"
SPEC = importlib.util.spec_from_file_location("recipe_scale", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def fixture(name):
    return json.loads((Path(__file__).parent / "fixtures" / name).read_text())


class ScaleTests(unittest.TestCase):
    def test_success_accounts_for_every_line(self):
        result = MODULE.calculate(fixture("success.json"))

        self.assertEqual(result["scale_factor"], "8")
        self.assertEqual(result["review_state"], "READY FOR RECIPE REVIEW")
        self.assertEqual(len(result["ingredients"]), 4)
        self.assertEqual(result["ingredients"][0]["rounded_amount"], "16")
        self.assertEqual(result["ingredients"][3]["status"], "manual_review")

    def test_edge_reports_container_fit(self):
        result = MODULE.calculate(fixture("edge.json"))

        self.assertEqual(result["scale_factor"], "8.333333333333333333333333333")
        self.assertEqual(result["container_fit"]["container_count"], 2)
        self.assertEqual(result["container_fit"]["unused_capacity"], "250")
        self.assertEqual(result["tolerance_blockers"], [])

    def test_failure_for_mismatched_yield_units(self):
        payload = fixture("success.json")
        payload["target_yield"]["unit"] = "ml"

        with self.assertRaisesRegex(MODULE.InputError, "must match"):
            MODULE.calculate(payload)

    def test_failure_for_duplicate_ingredient(self):
        payload = fixture("success.json")
        payload["ingredients"][1]["name"] = "gin"

        with self.assertRaisesRegex(MODULE.InputError, "duplicate ingredient"):
            MODULE.calculate(payload)

    def test_outside_tolerance_blocks_review(self):
        payload = fixture("edge.json")
        payload["tolerance_percent"] = 0
        payload["ingredients"][0]["rounding_increment"] = 7

        result = MODULE.calculate(payload)

        self.assertEqual(result["review_state"], "NOT READY: ROUNDING OR INPUT BLOCKER")
        self.assertIn("spirit", result["tolerance_blockers"])


if __name__ == "__main__":
    unittest.main()
