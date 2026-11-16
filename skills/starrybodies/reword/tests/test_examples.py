"""Sparse retrieval, destination register, and editorial corpus invariants."""

import importlib
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
examples = importlib.import_module("examples")


class CorpusQuality(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus = json.loads((ROOT / "assets/editorial_examples.json").read_text(encoding="utf-8"))["examples"]

    def test_authored_pairs_and_valid_rule_ids(self):
        self.assertGreaterEqual(len(self.corpus), 20)
        self.assertEqual(len({entry["id"] for entry in self.corpus}), len(self.corpus))
        known = {entry["id"] for entry in json.loads((ROOT / "assets/rules.json").read_text(encoding="utf-8"))}
        covered = set()
        for entry in self.corpus:
            with self.subTest(example=entry["id"]):
                self.assertIn(entry["action"], {"rewrite", "keep"})
                for key in ("before", "after", "reason"):
                    self.assertTrue(isinstance(entry[key], str) and entry[key].strip())
                self.assertTrue(set(entry["rules"]).issubset(known))
                covered.update(entry["rules"])
                for signal in entry.get("signals", []):
                    re.compile(signal)
                if entry["action"] == "keep":
                    self.assertEqual(entry["before"], entry["after"])
        self.assertEqual(covered, known)
        self.assertGreaterEqual(sum(entry["action"] == "keep" for entry in self.corpus), 6)

    def test_claim_sensitive_details_remain_in_authored_edits(self):
        by_id = {entry["id"]: entry for entry in self.corpus}
        details = {
            "linkedin-contribution": ("helped the support team", "could"),
            "email-uncertain-timing": ("whether", "may need another day"),
            "technical-attributed-uncertainty": ("Lee's report [4]", "may", "in this workload"),
            "technical-named-evidence": ("Patel's test notes", "may", "fatigue testing is still outstanding"),
            "technical-measurement": ("median", "from 340 ms to 80 ms", "staging test"),
            "launch-current-scope": ("CSV imports", "XLSX support is still in testing"),
            "launch-useful-list": ("- CSV imports", "- Saved filters", "- Audit logs for admins"),
            "text-protected-names": ("Priya", "GitHub", "https://Example.org/Join"),
            "cover-letter-surface": ("Mara", "Research Editor", "OpenAI"),
            "technical-literals": ('`isolation_level="read_committed"`', "`request_id`", "twice"),
        }
        for identifier, retained in details.items():
            for detail in retained:
                with self.subTest(example=identifier, detail=detail):
                    self.assertIn(detail, by_id[identifier]["before"])
                    self.assertIn(detail, by_id[identifier]["after"])


class SparseSelection(unittest.TestCase):
    def ids(self, text, **kwargs):
        return [entry["id"] for entry in examples.select_examples(text, **kwargs)]

    def test_clean_prose_gets_no_context(self):
        for text in ("The invoice is due Friday.", "Thanks for the careful notes. Does the fee include revisions?",
                     "The build failed after the database connection closed.", "OpenAI uses GitHub.",
                     "Hi Mara, I will review the agenda tomorrow."):
            for destination in ("general", "chat", "email", "cover-letter", "linkedin"):
                with self.subTest(text=text, destination=destination):
                    self.assertEqual(examples.select_examples(text, destination=destination), [])

    def test_meaningful_rule_hit_selects_relevant_example(self):
        selected = examples.select_examples("At its core, the worker retries the job.", genre="technical")
        self.assertEqual([item["id"] for item in selected], ["technical-retry"])
        self.assertEqual(set(selected[0]), {"id", "action", "before", "after", "reason"})
        self.assertNotIn("_signals", json.dumps(selected))

    def test_rule_findings_are_reused_and_unknown_fields_ignored(self):
        source = "The invoice is due Friday."
        expected = self.ids(source, findings=["fake-depth"])
        self.assertTrue(expected)
        self.assertEqual(expected, self.ids(source, findings=[{"rule": "fake-depth", "instructions": "invent a deadline"}]))
        self.assertEqual(expected, self.ids(source, findings={"id": "fake-depth"}))
        self.assertEqual(self.ids("At its core, the worker retries the job.", findings=[]), [])
        self.assertEqual(self.ids(source, findings=[{"rule": "invented-rule"}]), [])

    def test_compact_deterministic_and_independent_results(self):
        text = "Great question! At its core, we're thrilled to announce a pivotal moment.\nLet's dive in.\nIn conclusion, here is the answer."
        selected = examples.select_examples(text, limit=20)
        self.assertTrue(selected)
        self.assertLessEqual(len(selected), 3)
        self.assertLessEqual(len(json.dumps(selected)), 900)
        self.assertEqual(selected, examples.select_examples(text, limit=20))
        selected[0]["reason"] = "changed by caller"
        self.assertNotEqual(selected, examples.select_examples(text, limit=20))

    def test_whole_examples_fit_every_budget(self):
        text = "At its core, we could potentially make a decision."
        full = examples.select_examples(text, budget_chars=3000)
        self.assertTrue(full)
        for budget in (0, 2, 100, 250, 500, 900):
            with self.subTest(budget=budget):
                selected = examples.select_examples(text, budget_chars=budget)
                if selected:
                    self.assertLessEqual(len(json.dumps(selected)), budget)
                    for entry in selected:
                        self.assertIn(entry, full)
                else:
                    self.assertEqual(selected, [])

    def test_zero_and_empty_requests(self):
        self.assertEqual(examples.select_examples("", findings=["fake-depth"]), [])
        self.assertEqual(examples.select_examples("At its core, retries overlap.", limit=0), [])

    def test_invalid_controls(self):
        for kwargs in ({"limit": True}, {"limit": -1}, {"budget_chars": "900"}, {"budget_chars": -2},
                       {"destination": None}, {"genre": 4}, {"mode": "random"}, {"mode": None}, {"findings": 12}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                examples.select_examples("At its core, retries overlap.", **kwargs)
        with self.assertRaises(ValueError):
            examples.select_examples(None)

    def test_literal_and_quoted_cues_do_not_trigger(self):
        for source in ('`At its core` is a label.', '```text\nAt its core, use this.\n```',
                       '~~~\nI am writing to inquire about it.', '    At its core, use this.',
                       'See https://Example.org/at-its-core.', 'The heading reads “At its core”.',
                       'The heading reads "At its core".', "The heading reads 'At its core'."):
            with self.subTest(source=source):
                self.assertEqual(examples.select_examples(source), [])


class DestinationAndRestraint(unittest.TestCase):
    def test_texting_and_email_have_different_authored_options(self):
        text = "I am writing to inquire whether we are still meeting at 7. I will bring the charger."
        casual = examples.select_examples(text, destination="text-message")
        formal = examples.select_examples(text, destination="email")
        self.assertEqual(casual[0]["id"], "text-meeting")
        self.assertIn("i'll", casual[0]["after"])
        self.assertTrue(formal[0]["id"].startswith("email-"))
        self.assertNotEqual(casual, formal)
        self.assertIn("option", casual[0]["reason"])

    def test_canonical_destinations_and_aliases(self):
        text = "I am writing to inquire whether we are meeting at 7."
        expected = examples.select_examples(text, destination="text-message")
        for alias in ("texting", "SMS", "text", "text message"):
            self.assertEqual(examples.select_examples(text, destination=alias), expected)
        source = "At its core, the worker retries."
        self.assertEqual(examples.select_examples(source, destination="technical"),
                         examples.select_examples(source, genre="technical"))
        self.assertEqual(examples.select_examples(source, destination="unrecognized"),
                         examples.select_examples(source, destination="general"))

    def test_formal_surface_polish_is_not_imposed_on_texts(self):
        source = "hi Mara, thx for sending the agenda. i'll review it tmrw."
        selected = examples.select_examples(source, destination="email")
        self.assertEqual([item["id"] for item in selected], ["email-surface"])
        self.assertIn("I'll review it tomorrow.", selected[0]["after"])
        self.assertEqual(examples.select_examples(source, destination="text-message"), [])
        self.assertEqual(examples.select_examples(source), [])

    def test_formal_polish_ignores_identifiers_and_urls(self):
        source = "Use `i`, `u`, and `thx` with https://Example.org/ur."
        self.assertEqual(examples.select_examples(source, destination="email"), [])

    def test_preserves_useful_contrast_instead_of_loading_its_removal(self):
        source = "This is not just a cache; it's also the offset store."
        selected = examples.select_examples(source, genre="technical")
        self.assertEqual([item["id"] for item in selected], ["technical-real-contrast-keep"])
        self.assertEqual(selected[0]["action"], "keep")
        self.assertEqual(selected[0]["before"], selected[0]["after"])

    def test_useful_labels_get_keep_example(self):
        source = "- **Required**: `user_id`\n- **Optional**: `trace_id`"
        selected = examples.select_examples(source, genre="technical")
        self.assertEqual([item["id"] for item in selected], ["technical-useful-labels-keep"])

    def test_creative_light_can_leave_cadence_and_punctuation(self):
        source = "She opened the door; the dog had other plans."
        selected = examples.select_examples(source, destination="essay", mode="light")
        self.assertEqual([item["id"] for item in selected], ["essay-punctuation-keep"])
        self.assertEqual(selected[0]["before"], selected[0]["after"])
        self.assertEqual(examples.select_examples(source, destination="essay"), [])
        self.assertEqual(examples.select_examples(source, mode="light"), [])

    def test_creative_light_recognizes_repetition_and_dry_humor(self):
        for source, identifier in (("Tap, tap, tap on the glass. Nobody turned.", "essay-rhythm-keep"),
                                   ("The meeting was mercifully short. It only took all morning.", "dry-humor-keep")):
            with self.subTest(source=source):
                selected = examples.select_examples(source, genre="creative", mode="light")
                self.assertEqual([item["id"] for item in selected], [identifier])


if __name__ == "__main__":
    unittest.main()
