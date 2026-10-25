"""Behavioral checks for conservative diagnostics; no third-party packages."""

import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from audit_text import audit
from compare_revisions import compare, numeric_claims
from text_common import citation_spans, location, mask_spans, protected_spans


def codes(report):
    return [item["code"] for item in report["findings"]]


class AuditBehavior(unittest.TestCase):
    def test_clean_persian_zwnj_is_preserved_and_unflagged(self):
        text = "این روش کار می‌کند. نتیجه را نمی‌دانیم."
        report = audit(text)
        self.assertEqual(report["lang"], "fa")
        self.assertEqual(report["findings"], [])
        self.assertEqual(text, "این روش کار می‌کند. نتیجه را نمی‌دانیم.")

    def test_arabic_letters_only_in_prose_have_original_locations(self):
        text = 'سرآغاز\nاين كلمه است. «اين كلمه» `اين كلمه` https://example.test/اين/كلمه\n'
        report = audit(text, "fa")
        found = [x for x in report["findings"] if x["code"] == "FA_ARABIC_LETTER"]
        self.assertEqual([(x["line"], x["column"]) for x in found], [(2, 2), (2, 5)])
        self.assertTrue(all(x["severity"] == "advisory" for x in found))

    def test_quotation_containing_url_and_code_is_fully_protected(self):
        text = '«اين كلمه https://example.test/اين و `كلمه`»\n> اين كلمه https://example.test/a\n'
        self.assertEqual(audit(text, "fa")["findings"], [])
        spans = protected_spans(text, quotes=True)
        self.assertEqual([span.kind for span in spans], ["quote", "quote"])

    def test_fences_indented_code_destinations_and_inline_code_are_masked(self):
        text = ('```python\nاين كلمه\n```\n    اين كلمه\n'
                '`اين كلمه` [پیوند](اين/كلمه "عنوان")\n'
                '[مرجع]: https://example.test/اين "كلمه"\n')
        self.assertNotIn("FA_ARABIC_LETTER", codes(audit(text, "fa")))
        masked = mask_spans(text, protected_spans(text, quotes=True))
        self.assertEqual(len(masked), len(text))
        self.assertEqual([i for i, ch in enumerate(masked) if ch == "\n"],
                         [i for i, ch in enumerate(text) if ch == "\n"])

    def test_narrow_prefix_spacing_positive_and_negative_controls(self):
        self.assertIn("FA_PREFIX_SPACING", codes(audit("من می دانم.", "fa")))
        for text in ("من می‌دانم.", "ماه می زمان سفر است.", "میوه رسیده است."):
            with self.subTest(text=text):
                self.assertNotIn("FA_PREFIX_SPACING", codes(audit(text, "fa")))

    def test_contextual_lexical_prompt_is_not_a_verdict(self):
        report = audit("It is important to note that the samples were frozen.")
        self.assertEqual(codes(report), ["LEXICAL_REVIEW"])
        self.assertEqual(report["findings"][0]["severity"], "advisory")
        self.assertIn("Check whether", report["findings"][0]["message"])
        self.assertNotIn("LEXICAL_REVIEW", codes(audit("The specimens were frozen before transport.")))
        self.assertNotIn("LEXICAL_REVIEW", codes(audit('“It is important to note that” is the quoted phrase.')))

    def test_language_selection_and_profiles_are_metadata_not_penalties(self):
        self.assertEqual(audit("یک روش برای RNA.")["lang"], "mixed")
        self.assertEqual(audit("123 🙂")["detected_lang"], "undetermined")
        text = "It is important to note that this is a qualification."
        reports = [audit(text, "en", p) for p in ("general", "academic", "web", "copy")]
        self.assertEqual([r["profile"] for r in reports], ["general", "academic", "web", "copy"])
        self.assertTrue(all(r["findings"] == reports[0]["findings"] for r in reports))
        self.assertEqual(audit("اين كلمه", "en")["findings"], [])

    def test_repetition_locations_and_sentence_metrics(self):
        report = audit("We measured cells.\n\nWe measured cells.")
        self.assertIn("REPEATED_SENTENCE", codes(report))
        self.assertIn("REPEATED_PARAGRAPH_START", codes(report))
        self.assertTrue(all(x["line"] == 3 for x in report["findings"]))
        self.assertEqual(report["metrics"]["sentence_words"]["mean"], 3)
        self.assertEqual(report["metrics"]["sentence_words"]["population_stdev"], 0)

    def test_empty_and_all_protected_text(self):
        for text in ("", " \r\n\t", "```\nnot may 123\n```", '«اين كلمه»'):
            with self.subTest(text=text):
                report = audit(text)
                self.assertEqual(report["findings"], [])
                self.assertEqual(report["metrics"]["words"], 0)
                self.assertEqual(report["metrics"]["sentences"], 0)


class ComparisonBehavior(unittest.TestCase):
    def test_digit_decimal_grouping_percent_and_known_unit_equivalence(self):
        pairs = [
            ("Dose: ۱٬۲۰۰٫۵۰ mg.", "Dose: 1,200.5 milligrams."),
            ("Rate: ١٠٪.", "Rate: 10 percent."),
            ("Value: 1.0.", "Value: ۱."),
            ("Volume: 5ml.", "Volume: ۵ میلی‌لیتر."),
            ("Cost: $20.", "Cost: ۲۰ دلار."),
            ("Cost: -$20.", "Cost: $-۲۰."),
            ("Change: ۵ واحد درصد.", "Change: 5 percentage points."),
            ("Zero: ۰٫۰۰.", "Zero: 0."),
        ]
        for original, revised in pairs:
            with self.subTest(original=original):
                report = compare(original, revised)
                self.assertEqual(report["metrics"]["original_numeric_claims"], 1)
                self.assertEqual(report["metrics"]["revised_numeric_claims"], 1)
                self.assertEqual(report["findings"], [])

    def test_bare_number_and_decimal_before_sentence_stop_are_checked(self):
        for original, revised in (("Count 20.", "Count 21."), ("Value 1.0.", "Value 2.0.")):
            with self.subTest(original=original):
                report = compare(original, revised)
                self.assertEqual(report["metrics"]["original_numeric_claims"], 1)
                self.assertIn("NUMERIC_CLAIM_REMOVED_REVIEW", codes(report))

    def test_units_signs_percent_and_percentage_points_are_reviewed(self):
        pairs = [("5 mg", "5 g"), ("+5", "-5"), ("5%", "5"),
                 ("5 percent", "5 percentage points"), ("5 دلار", "5 یورو")]
        for original, revised in pairs:
            with self.subTest(original=original):
                report = compare(original, revised)
                self.assertIn("NUMERIC_ATTRIBUTE_REVIEW", codes(report))
                self.assertTrue(all(x["severity"] == "advisory" for x in report["findings"]))

    def test_changed_value_and_added_or_removed_occurrence(self):
        report = compare("The dose is 10 mg.", "The dose is 15 mg.")
        self.assertIn("NUMERIC_CLAIM_REMOVED_REVIEW", codes(report))
        self.assertIn("NUMERIC_CLAIM_ADDED_REVIEW", codes(report))
        duplicate = compare("5 mg and 5 mg", "5 mg")
        self.assertEqual(codes(duplicate), ["NUMERIC_CLAIM_REMOVED_REVIEW"])

    def test_common_range_connectors_and_shared_units(self):
        for connector in ("-", " - ", " -", "–", "—", " to ", " through ", " تا ", " الی "):
            with self.subTest(connector=connector):
                report = compare("10{}20 mg".format(connector), "۱۰ تا ۲۰ میلی‌گرم")
                self.assertEqual(report["metrics"]["original_ranges"], 1)
                self.assertEqual(report["findings"], [])

    def test_signed_range_endpoints_and_unicode_minus(self):
        for original in ("-5--2 mg", "-5 - -2 mg", "−5 تا −2 mg"):
            with self.subTest(original=original):
                self.assertEqual(compare(original, "−۵ تا −۲ میلی‌گرم")["findings"], [])
        claims, ranges = numeric_claims("10 −20", [])
        self.assertEqual(len(ranges), 0)
        self.assertEqual([x["sign"] for x in claims], ["", "-"])

    def test_range_change_is_reported_even_when_values_survive(self):
        report = compare("10–20 mg", "10 mg and 20 mg")
        self.assertEqual(codes(report), ["RANGE_REVIEW"])
        changed_bound = compare("10–20 mg", "10–25 mg")
        self.assertIn("RANGE_REVIEW", codes(changed_bound))
        self.assertEqual(codes(compare("10 mg and 20 mg", "10–20 mg")), ["RANGE_ADDED_REVIEW"])

    def test_ordinary_identifiers_and_versions_are_not_quantities(self):
        for original in ("abc12", "12abc", "v1.2", "1.2.3", "12th", "var_12"):
            with self.subTest(original=original):
                self.assertEqual(compare(original, "replacement")["metrics"]["original_numeric_claims"], 0)

    def test_invalid_grouping_is_not_silently_normalized(self):
        report = compare("100 mg", "1,00 mg")
        self.assertIn("NUMERIC_CLAIM_REMOVED_REVIEW", codes(report))
        self.assertIn("NUMERIC_CLAIM_ADDED_REVIEW", codes(report))

    def test_code_urls_destinations_quotations_and_citations_are_exact(self):
        pairs = [
            ("Use `x = 10`.", "Use `x = 11`."),
            ("https://example.test/a", "https://example.test/b"),
            ("[link](local/a)", "[link](local/b)"),
            ('«حدود ۵ درصد»', '«۵ درصد»'),
            ('“The sample may change.”', '“The sample changes.”'),
            ("> A source says 10%\n", "> A source says 11%\n"),
            ("Result [12].", "Result [13]."),
            ("Result (Smith, 2024).", "Result (Smith, 2025)."),
            ("Result [^note].", "Result [^other]."),
        ]
        for original, revised in pairs:
            with self.subTest(original=original):
                report = compare(original, revised)
                self.assertIn("PROTECTED_SPAN_REVIEW", codes(report))
                self.assertNotIn("NUMERIC_CLAIM_REMOVED_REVIEW", codes(report))

    def test_protected_duplicates_and_protection_context(self):
        self.assertEqual(codes(compare('«exact» «exact»', '«exact»')), ["PROTECTED_SPAN_REVIEW"])
        self.assertIn("PROTECTED_SPAN_REVIEW", codes(compare('`exact`', '«exact»')))
        self.assertEqual(compare('«a https://example.test/x b»', '«a https://example.test/x b»')["findings"], [])

    def test_new_quotation_and_citation_need_source_review(self):
        for revised in ('The result is “certain”.', 'The result is certain [25].'):
            with self.subTest(revised=revised):
                self.assertIn("PROTECTED_SPAN_ADDED_REVIEW", codes(compare("The result is uncertain.", revised)))

    def test_markers_are_prompts_and_equivalent_paraphrase_can_be_flagged(self):
        report = compare("This may help some cells, but it is not proven.", "This helps cells and is proven.")
        self.assertIn("NEGATION_REMOVAL_REVIEW", codes(report))
        self.assertIn("UNCERTAINTY_REMOVAL_REVIEW", codes(report))
        self.assertIn("QUALIFICATION_REMOVAL_REVIEW", codes(report))
        paraphrase = compare("It may work.", "It is possible that it works.")
        self.assertIn("UNCERTAINTY_REMOVAL_REVIEW", codes(paraphrase))
        self.assertIn("paraphrases can be equivalent", paraphrase["findings"][0]["message"])
        self.assertTrue(all(x["severity"] == "advisory" for x in report["findings"]))

    def test_marker_substrings_and_protected_markers_are_negative_controls(self):
        self.assertEqual(compare("The notebook discusses mayonnaise.", "The book describes food.")["findings"], [])
        self.assertEqual(compare('The quote is “may not work”.', 'Here is “may not work”.')["findings"], [])

    def test_new_negation_and_uncertainty_also_need_review(self):
        report = compare("The result is proven.", "The result is not proven and may differ.")
        self.assertIn("NEGATION_ADDITION_REVIEW", codes(report))
        self.assertIn("UNCERTAINTY_ADDITION_REVIEW", codes(report))

    def test_persian_marker_removal(self):
        report = compare("این روش شاید برای برخی سلول‌ها مفید باشد؛ قطعی نیست.", "این روش برای سلول‌ها مفید و قطعی است.")
        self.assertIn("UNCERTAINTY_REMOVAL_REVIEW", codes(report))
        self.assertIn("NEGATION_REMOVAL_REVIEW", codes(report))
        self.assertIn("QUALIFICATION_REMOVAL_REVIEW", codes(report))

    def test_invariants_check_exact_strings_occurrences_and_terms(self):
        contract = {"protected_strings": ["approval pending"], "required_terms": ["RNA", "سلول"]}
        report = compare("approval pending; approval pending; RNA; سلول", "approval pending; rna; سلولی", contract)
        self.assertEqual(codes(report).count("INVARIANT_PROTECTED_REVIEW"), 1)
        self.assertEqual(codes(report).count("INVARIANT_REQUIRED_REVIEW"), 2)
        self.assertEqual(compare("RNA; سلول", "RNA; سلول", {"required_terms": ["RNA", "سلول"]})["findings"], [])

    def test_required_term_is_not_satisfied_by_a_substring(self):
        report = compare("cat", "concatenate", {"required_terms": ["cat"]})
        self.assertEqual(codes(report), ["INVARIANT_REQUIRED_REVIEW"])
        self.assertEqual(compare("C++", "Use C++.", {"required_terms": ["C++"]})["findings"], [])

    def test_contract_missing_baseline_remains_visible(self):
        report = compare("original", "revision", {"protected_strings": ["exact"]})
        self.assertIn("INVARIANT_BASELINE_REVIEW", codes(report))
        self.assertIn("INVARIANT_PROTECTED_REVIEW", codes(report))

    def test_compare_locations_refer_to_the_correct_input(self):
        report = compare("Intro\nDose 10 mg.", "New intro\nDose 11 mg.")
        old = next(x for x in report["findings"] if x["code"] == "NUMERIC_CLAIM_REMOVED_REVIEW")
        new = next(x for x in report["findings"] if x["code"] == "NUMERIC_CLAIM_ADDED_REVIEW")
        self.assertEqual((old["source"], old["line"], old["column"]), ("original", 2, 6))
        self.assertEqual((new["source"], new["line"], new["column"]), ("revised", 2, 6))

    def test_clean_result_does_not_claim_meaning_equivalence(self):
        report = compare("The enzyme activates the receptor.", "The enzyme destroys the receptor.")
        self.assertEqual(report["findings"], [])
        self.assertIn("no authorship determination", report["scope"])
        self.assertIn("no authorship determination", audit("Clear prose.")["scope"])


class SharedBehavior(unittest.TestCase):
    def test_unicode_points_crlf_and_citation_shapes(self):
        text = "الف🙂\r\nدوم [۲–۴] (Smith, 2024) [^a]"
        self.assertEqual(location(text, text.index("دوم")), (2, 1))
        self.assertEqual(location(text, text.index("🙂")), (1, 4))
        self.assertEqual([x.text for x in citation_spans(text, [])], ["[۲–۴]", "(Smith, 2024)", "[^a]"])


if __name__ == "__main__":
    unittest.main()
