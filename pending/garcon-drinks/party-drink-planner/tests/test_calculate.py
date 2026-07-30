import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "calculate.py"
SPEC = importlib.util.spec_from_file_location("party_calculate", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def base_input():
    return {
        "total_guests": 24,
        "drinking_guests": 18,
        "duration_hours": 4,
        "country": "US",
        "mix": {"beer": 0.35, "wine": 0.25, "cocktails": 0.4},
        "planning_assumptions": {
            "alcoholic_servings_per_drinking_guest": 4,
            "nonalcoholic_servings_per_guest": 3,
            "water_liters_per_guest": 1.2,
            "ice_amount_per_guest": 1.5,
            "ice_unit": "lb",
            "source": "host-approved base scenario",
            "reviewed_on": "2026-07-27",
        },
        "package_yields": {
            "beer_units": 1,
            "wine_bottles": 5,
            "spirit_bottles": 16,
        },
        "buffer_percent": 10,
    }


class CalculateTests(unittest.TestCase):
    def test_success_with_inventory_and_recipe(self):
        payload = base_input()
        payload["inventory"] = {
            "beer_units": 12,
            "wine_bottles": 2,
            "spirit_bottles": 1,
        }
        payload["cocktail_recipes"] = [
            {
                "name": "Daiquiri",
                "share": 1,
                "ingredients": [
                    {"name": "light rum", "amount_oz": 2, "inventory_oz": 12},
                    {"name": "lime juice", "amount_oz": 1},
                ],
            }
        ]

        result = MODULE.calculate(payload)

        self.assertEqual(result["total_planned_servings"], 80)
        self.assertEqual(sum(result["servings"].values()), 80)
        self.assertEqual(result["cocktail_batches"][0]["servings"], 32)
        self.assertEqual(
            result["cocktail_batches"][0]["ingredients"][0]["shopping_gap_oz"], 52
        )
        self.assertEqual(
            result["assumptions"]["planning_assumptions"]["source"],
            "host-approved base scenario",
        )

    def test_edge_with_no_drinking_guests(self):
        payload = base_input()
        payload.update(
            {
                "total_guests": 12,
                "drinking_guests": 0,
                "duration_hours": 2,
                "country": "GB",
            }
        )
        payload["planning_assumptions"].update(
            {
                "alcoholic_servings_per_drinking_guest": 0,
                "ice_amount_per_guest": 0.68,
                "ice_unit": "kg",
            }
        )

        result = MODULE.calculate(payload)

        self.assertEqual(result["total_planned_servings"], 0)
        self.assertEqual(result["shopping_gaps"]["spirit_bottles"], 0)
        self.assertGreater(result["non_alcoholic"]["servings"], 0)
        self.assertEqual(result["non_alcoholic"]["ice_unit"], "kg")

    def test_failure_for_invalid_mix(self):
        payload = base_input()
        payload["mix"] = {"beer": 0.6, "wine": 0.3, "cocktails": 0.3}

        with self.assertRaisesRegex(MODULE.InputError, "total 1.0"):
            MODULE.calculate(payload)

    def test_failure_for_missing_assumptions(self):
        payload = base_input()
        del payload["planning_assumptions"]

        with self.assertRaisesRegex(
            MODULE.InputError, "planning_assumptions must be an object"
        ):
            MODULE.calculate(payload)

    def test_failure_for_missing_assumption_source(self):
        payload = base_input()
        payload["planning_assumptions"]["source"] = ""

        with self.assertRaisesRegex(MODULE.InputError, "source must be non-empty"):
            MODULE.calculate(payload)

    def test_failure_for_invalid_package_yield(self):
        payload = base_input()
        payload["package_yields"]["wine_bottles"] = 0

        with self.assertRaisesRegex(
            MODULE.InputError, "package_yields.wine_bottles must be positive"
        ):
            MODULE.calculate(payload)


if __name__ == "__main__":
    unittest.main()
