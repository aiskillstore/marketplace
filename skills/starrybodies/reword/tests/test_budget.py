"""Guidance budgets must never achieve a small prompt by dropping requirements."""

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("budget", ROOT / "scripts/budget.py")
budget = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(budget)


class Measurement(unittest.TestCase):
    def test_unicode_counts_and_estimate_are_distinct(self):
        text = "é👋e\u0301"
        result = budget.measure_guidance(text)
        self.assertEqual(result["characters"], 4)
        self.assertEqual(result["utf8_bytes"], 9)
        self.assertIsNone(result["tokens"])
        self.assertEqual(result["estimated_tokens"], 3)
        self.assertEqual(result["token_measurement"], "estimate")
        self.assertIn("not a bound", result["estimation_method"])

    def test_empty_text_is_zero_not_unknown_usage(self):
        result = budget.measure_guidance("")
        self.assertEqual(result["characters"], 0)
        self.assertEqual(result["estimated_tokens"], 0)
        self.assertNotIn("cost", result)
        self.assertNotIn("usage", result)

    def test_supplied_exact_counter_sees_all_text(self):
        seen = []

        def exact(text):
            seen.append(text)
            return 11

        text = "Keep <|endoftext|> literally."
        result = budget.measure_guidance(text, "fixture-encoding", token_counter=exact)
        self.assertEqual(seen, [text])
        self.assertEqual(result["tokens"], 11)
        self.assertIsNone(result["estimated_tokens"])
        self.assertEqual(result["token_measurement"], "exact")
        self.assertEqual(result["encoding"], "fixture-encoding")
        self.assertNotIn("estimation_method", result)

    def test_counter_failure_does_not_silently_become_an_estimate(self):
        def broken(text):
            raise RuntimeError("tokenizer is unavailable")

        with self.assertRaises(RuntimeError):
            budget.measure_guidance("Keep everything.", token_counter=broken)

    def test_invalid_measurement_input_and_counter_results(self):
        for text, encoding in [(None, "o200k_base"), ("Text.", "")]:
            with self.subTest(text=text, encoding=encoding):
                with self.assertRaises(ValueError):
                    budget.measure_guidance(text, encoding)
        for count in [-1, 1.5, True, None]:
            with self.subTest(count=count):
                with self.assertRaises(ValueError):
                    budget.measure_guidance("Text.", token_counter=lambda text: count)


class OptionalExamples(unittest.TestCase):
    def test_whole_examples_and_all_separators_fit(self):
        examples = ["First example", "Second example"]
        required = len("\n\n".join(examples))
        self.assertEqual(budget.fit_examples(examples, remaining_chars=required), examples)
        self.assertEqual(budget.fit_examples(examples, remaining_chars=required - 1), examples[:1])

    def test_skips_oversize_optional_example_without_truncation(self):
        self.assertEqual(budget.fit_examples(["x" * 30, "Whole."], remaining_chars=6), ["Whole."])

    def test_default_caps_are_independent_of_available_space(self):
        selected = budget.fit_examples(["a" * 440, "b" * 440, "c"], remaining_chars=10000)
        self.assertEqual(len(selected), 2)
        self.assertLessEqual(len("\n\n".join(selected)), 900)
        self.assertEqual(budget.fit_examples(["a" * 901], remaining_chars=10000), [])

    def test_invalid_limits_and_string_instead_of_list_are_rejected(self):
        for kwargs in [{"remaining_chars": -1}, {"remaining_chars": 50, "max_examples": True},
                       {"remaining_chars": 50, "max_chars": -1}]:
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    budget.fit_examples(["Example."], **kwargs)
        with self.assertRaises(ValueError):
            budget.fit_examples("not a sequence of examples", remaining_chars=50)


class Assembly(unittest.TestCase):
    def test_explicit_preferences_locks_and_source_are_never_shortened(self):
        parts = ["Preserve all claims.", "Use UK spelling; keep warmth.",
                 "Lock: Northlight Works", 'Source: "Never alter this quotation."']
        original_parts = list(parts)
        required = "\n\n".join(parts)
        result = budget.assemble_guidance(parts, ["Optional example"], max_chars=len(required))
        self.assertEqual(result["text"], required)
        self.assertEqual(parts, original_parts)
        self.assertEqual(result["examples_used"], 0)
        self.assertEqual(result["examples_omitted"], 1)

    def test_required_overflow_is_explicit_and_measured(self):
        with self.assertRaises(budget.GuidanceBudgetError) as caught:
            budget.assemble_guidance(["Keep this exact requirement."], ["Example"], max_chars=10)
        self.assertIn("nothing was removed", str(caught.exception))
        self.assertEqual(caught.exception.measurement["characters"], 28)

    def test_joined_text_respects_character_cap_including_prefix(self):
        result = budget.assemble_guidance(["Core"], ["abc", "def"], max_chars=8)
        self.assertEqual(result["text"], "Core")
        result = budget.assemble_guidance(["Core"], ["abc", "def"], max_chars=9)
        self.assertEqual(result["text"], "Core\n\nabc")
        self.assertEqual(result["measurement"]["characters"], 9)

    def test_estimates_are_never_used_as_exact_token_limits(self):
        result = budget.assemble_guidance(["Required"], target_tokens=1)
        self.assertEqual(result["text"], "Required")
        self.assertIsNone(result["measurement"]["tokens"])
        self.assertFalse(result["limits"]["token_target_enforced"])

    def test_exact_token_budget_removes_optional_examples_first(self):
        result = budget.assemble_guidance(["core"], ["first", "second"],
                                          token_counter=len, target_tokens=11)
        self.assertEqual(result["text"], "core\n\nfirst")
        self.assertEqual(result["examples_used"], 1)
        self.assertEqual(result["examples_omitted"], 1)
        self.assertTrue(result["limits"]["token_target_enforced"])

    def test_exact_token_budget_cannot_remove_required_material(self):
        with self.assertRaises(budget.GuidanceBudgetError):
            budget.assemble_guidance(["required"], token_counter=len, target_tokens=7)

    def test_no_examples_does_not_repeat_exact_tokenization(self):
        seen = []

        def exact(text):
            seen.append(text)
            return len(text)

        budget.assemble_guidance(["required"], token_counter=exact)
        self.assertEqual(seen, ["required"])

    def test_empty_required_text_needs_no_prefix_separator(self):
        result = budget.assemble_guidance([], ["example"], max_chars=7)
        self.assertEqual(result["text"], "example")

    def test_cli_reports_only_estimate_and_reliable_character_status(self):
        result = subprocess.run([sys.executable, str(ROOT / "scripts/budget.py"), "--max-chars", "4"],
                                input="12345", text=True, capture_output=True)
        self.assertEqual(result.returncode, 1, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["characters"], 5)
        self.assertFalse(report["within_character_budget"])
        self.assertEqual(report["token_measurement"], "estimate")

    def test_cli_file_measurement_preserves_crlf(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "guidance.txt"
            source.write_bytes(b"a\r\nb\r\n")
            result = subprocess.run([sys.executable, str(ROOT / "scripts/budget.py"), str(source)],
                                    text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["characters"], 6)
            self.assertEqual(report["utf8_bytes"], 6)


if __name__ == "__main__":
    unittest.main()
