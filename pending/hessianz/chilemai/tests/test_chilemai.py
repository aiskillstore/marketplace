"""离线合成样本：不代表真实餐品、营养或价格，不调用点餐接口。"""

import json
from pathlib import Path
import subprocess
import sys
import unittest

from scripts import chilemai as c


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"


class FixtureCase(unittest.TestCase):
    def setUp(self):
        self.nutrition = c.parse_nutrition(
            (FIXTURES / "nutrition.sample.txt").read_text(encoding="utf-8")
        )
        self.menu = c.extract_menu_items(
            json.loads((FIXTURES / "menu.sample.json").read_text(encoding="utf-8"))
        )


class MatchingTests(FixtureCase):
    def test_punctuation_matches_but_cup_sizes_remain_uncertain(self):
        exact, uncertain, unmatched = c.match_menu(self.menu, self.nutrition)
        self.assertIn("drink", [item["code"] for item in exact])
        soda = next(item for item in uncertain if item["code"] == "ambiguous")
        self.assertNotIn("nutrition", soda)
        self.assertEqual(set(soda["candidates"]), {"雪碧（小杯）", "雪碧（大杯）"})
        reversed_result = c.match_menu(self.menu, list(reversed(self.nutrition)))
        self.assertEqual(uncertain, reversed_result[1])
        self.assertEqual([item["code"] for item in unmatched], ["unknown"])

    def test_prefix_match_is_not_confirmed_nutrition(self):
        _, uncertain, _ = c.match_menu(self.menu, self.nutrition)
        combo = next(item for item in uncertain if item["code"] == "combo")
        self.assertTrue(combo["combo"])
        self.assertNotIn("nutrition", combo)

    def test_conflicting_normalized_names_are_not_resolved_by_row_order(self):
        self.nutrition.append(dict(self.nutrition[0], energyKcal=600))
        exact, uncertain, _ = c.match_menu(self.menu[:1], self.nutrition)
        self.assertEqual(exact, [])
        self.assertEqual(uncertain[0]["code"], "main-a")

    def test_invalid_numeric_values_are_unknown(self):
        for value in ("NaN", "inf", "-10", "not-a-number"):
            with self.subTest(value=value):
                self.assertIsNone(c._to_number(value))

    def test_only_identical_nutrition_rows_are_deduplicated(self):
        self.assertEqual(len(self.nutrition), 6)
        text = (FIXTURES / "nutrition.sample.txt").read_text(encoding="utf-8")
        rows = c.parse_nutrition(text + "  轻食鸡肉堡,null,1255,600,15,8,30,400,100\n")
        self.assertEqual(len(rows), 7)

    def test_invalid_header_is_not_reported_as_an_empty_menu(self):
        for text in ("unexpected response", "[1]{productName,protein}:\n堡,20"):
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    c.parse_nutrition(text)


class PlanningTests(FixtureCase):
    def plan(self, **kwargs):
        options = dict(goal="any", overrides={}, price_unit="yuan")
        options.update(kwargs)
        return c.plan_meals(self.menu, self.nutrition, **options)

    def test_constraints_apply_to_whole_meal_not_individual_items(self):
        result = self.plan(
            goal="high-protein",
            overrides={"min_protein": 25, "max_energyKcal": 500},
            budget_cents=2500,
        )
        meal = result["plans"][0]
        self.assertEqual(meal["items"], [
            {"productCode": "main-a", "quantity": 1},
            {"productCode": "main-b", "quantity": 1},
        ])
        self.assertEqual(meal["nutrition"]["protein"], 25)
        self.assertEqual(meal["nutrition"]["energyKcal"], 500)
        self.assertEqual(meal["menu_subtotal_cents"], 2250)

    def test_quantities_are_included_in_nutrition_and_price(self):
        result = self.plan(
            goal="high-protein", overrides={"min_protein": 30}, budget_cents=2500
        )
        meal = result["plans"][0]
        self.assertEqual(meal["items"], [{"productCode": "main-a", "quantity": 2}])
        self.assertEqual(meal["nutrition"]["energyKcal"], 600)
        self.assertEqual(meal["menu_subtotal_cents"], 2500)

    def test_every_plan_has_food_and_excludes_uncertain_items(self):
        result = self.plan(limit=20)
        for meal in result["plans"]:
            codes = {item["productCode"] for item in meal["items"]}
            self.assertTrue(codes & {"main-a", "main-b"})
            self.assertFalse(codes & {"ambiguous", "combo", "unknown"})
        self.assertEqual(result["pricing"], "menu_estimate")
        self.assertEqual(result["coverage"]["eligible"], 4)

    def test_missing_nutrient_is_not_counted_as_zero(self):
        self.nutrition[0]["sodium"] = None
        meal = c.plan_meals(
            self.menu[:1], self.nutrition, "any", {}, "yuan"
        )["plans"][0]
        self.assertIsNone(meal["nutrition"]["sodium"])
        result = self.plan(overrides={"max_sodium": 350}, limit=20)
        self.assertTrue(result["plans"])
        for meal in result["plans"]:
            self.assertNotIn("main-a", [item["productCode"] for item in meal["items"]])

    def test_exact_combo_name_still_needs_composition_verification(self):
        self.menu = [{"code": "combo", "name": "鸡肉堡套餐", "price": 20}]
        self.nutrition = [dict(self.nutrition[0], productName="鸡肉堡套餐")]
        self.assertEqual(self.plan()["plans"], [])

    def test_fen_prices_and_decimal_yuan_prices_agree(self):
        yuan = self.plan()
        for item in self.menu:
            item["price"] *= 100
        self.assertEqual(yuan, self.plan(price_unit="fen"))

    def test_zero_price_is_valid_but_fractional_cents_are_not(self):
        self.assertEqual(c._price_cents("0", "yuan"), 0)
        self.assertEqual(c._price_cents("12.34", "yuan"), 1234)
        self.assertIsNone(c._price_cents("12.345", "yuan"))
        self.assertIsNone(c._price_cents("12.5", "fen"))

    def test_unconstrained_goal_does_not_prefer_high_protein(self):
        meal = self.plan()["plans"][0]
        self.assertEqual(meal["items"], [{"productCode": "main-b", "quantity": 1}])

    def test_unpriced_items_are_not_treated_as_free(self):
        for item in self.menu:
            item["price"] = None
        self.assertEqual(self.plan()["plans"], [])

    def test_no_plan_does_not_relax_constraints(self):
        result = self.plan(overrides={"min_protein": 100}, budget_cents=2500)
        self.assertEqual(result["plans"], [])


class CliTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, "-B", str(ROOT / "scripts" / "chilemai.py"), *args],
            cwd=ROOT, capture_output=True, encoding="utf-8",
        )

    def test_plan_json_and_empty_result_exit_status(self):
        args = ["plan", "--menu", str(FIXTURES / "menu.sample.json"),
                "--nutrition", str(FIXTURES / "nutrition.sample.txt"), "--price-unit", "yuan"]
        result = self.run_cli(*args)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)["plans"])
        result = self.run_cli(*args, "--budget", "0")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(json.loads(result.stdout)["plans"], [])

    def test_price_unit_and_valid_limits_are_required(self):
        base = ["plan", "--menu", str(FIXTURES / "menu.sample.json")]
        self.assertEqual(self.run_cli(*base).returncode, 2)
        for extra in (["--limit", "0"], ["--budget", "NaN"], ["--min-protein", "-1"]):
            result = self.run_cli(*base, "--price-unit", "yuan", *extra)
            self.assertEqual(result.returncode, 2, result.stderr)

    def test_existing_filter_and_match_commands(self):
        result = self.run_cli("filter", "light", "-f", str(FIXTURES / "nutrition.sample.txt"), "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout))
        result = self.run_cli("match", "--menu", str(FIXTURES / "menu.sample.json"),
                              "--nutrition", str(FIXTURES / "nutrition.sample.txt"), "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(set(json.loads(result.stdout)), {"exact", "alias", "unmatched"})


if __name__ == "__main__":
    unittest.main()
