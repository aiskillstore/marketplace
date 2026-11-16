"""End-to-end request, profile and CLI behavior for destination-aware editing."""

import importlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
editor = importlib.import_module("unformula")


class DestinationRequests(unittest.TestCase):
    def test_text_and_cover_letter_have_different_conventions(self):
        text = editor.build_request("i could join", destination="text-message")
        formal = editor.build_request("i could join", destination="cover-letter")
        a, b = text["meta"]["destination"], formal["meta"]["destination"]
        self.assertNotEqual(a["style"]["case"], b["style"]["case"])
        self.assertNotEqual(a["style"]["punctuation"], b["style"]["punctuation"])
        self.assertEqual(text["input"]["text"], formal["input"]["text"])

    def test_explicit_destination_beats_context(self):
        request = editor.build_request("Draft.", destination="linkedin", context="Copied from a chat.")
        self.assertEqual(request["meta"]["destination"]["destination"], "linkedin")

    def test_profile_context_and_call_overrides(self):
        profile = {"contexts": {"general": {"regional_spelling": "CA"}, "text-message": {"case": "lowercase"}}}
        request = editor.build_request("Draft.", profile=profile, destination="text-message", style_preferences={"case": "sentence"})
        self.assertEqual(request["meta"]["destination"]["style"]["case"], "sentence")
        self.assertEqual(request["meta"]["destination"]["style"]["regional_spelling"], "CA")

    def test_unknown_destination_stays_general(self):
        self.assertEqual(editor.build_request("hello", destination="unknown")["meta"]["destination"]["destination"], "general")

    def test_only_selected_context_is_sent(self):
        profile = {"contexts": {"text-message": {"case": "lowercase"}, "cover-letter": {"regional_spelling": "UK"}}}
        request = editor.build_request("Draft.", profile=profile, destination="text-message")
        self.assertNotIn('"cover-letter"', json.dumps(request["input"]))

    def test_samples_are_data_and_count_toward_guidance(self):
        plain = editor.build_request("Draft.", profile={"preferences": ["Warm and direct"]})
        request = editor.build_request("Draft.", profile={"preferences": ["Warm and direct"], "samples": ["Six hours fixing the board. Classic."]})
        self.assertNotIn("Six hours", request["instructions"])
        self.assertIn("Six hours", json.dumps(request["input"]))
        self.assertGreater(request["meta"]["guidance"]["characters"], plain["meta"]["guidance"]["characters"])

    def test_voice_guidance_keeps_author_data_without_routing_metadata(self):
        profile = {"preferences": ["Keep meaningful warmth"], "avoid": ["Ceremonial praise"],
                   "samples": ["We tried it. It broke. We tried again."]}
        request = editor.build_request("We tested the new booking form.", profile=profile)
        self.assertEqual(request["input"]["voice"]["preferences"], profile["preferences"])
        self.assertEqual(request["input"]["voice"]["avoid"], profile["avoid"])
        self.assertEqual(request["input"]["voice_samples"], profile["samples"])
        self.assertNotIn("needs_sample_context", request["input"]["voice"])
        self.assertNotIn("sample_guidance", request["input"]["voice"])

    def test_default_budget_includes_all_non_source_fields(self):
        request = editor.build_request("A short draft.", context="The reader knows the background.")
        overhead = json.dumps({k: v for k, v in request["input"].items() if k != "text"}, ensure_ascii=False, separators=(",", ":"))
        self.assertEqual(request["meta"]["guidance"]["characters"], len(request["instructions"] + "\n\n" + overhead))
        self.assertLessEqual(request["meta"]["guidance"]["characters"], 4000)
        self.assertIsNone(request["meta"]["guidance"]["tokens"])
        self.assertFalse(request["meta"]["token_target_enforced"])

    def test_source_size_does_not_change_guidance_budget(self):
        small = editor.build_request("A clear line.")
        large = editor.build_request("A clear line. " * 100)
        self.assertEqual(small["meta"]["guidance"]["characters"], large["meta"]["guidance"]["characters"])
        self.assertGreater(large["meta"]["request_content"]["characters"], small["meta"]["request_content"]["characters"])

    def test_small_budget_does_not_silently_remove_preferences(self):
        with self.assertRaises(ValueError):
            editor.build_request("Draft.", profile={"preferences": ["Keep meaningful humor"]}, guidance_chars=200)

    def test_profile_traits_and_contexts_validate(self):
        valid = {"traits": {"devices": "Dry situational irony"}, "contexts": {"linkedin": {"punctuation": "standard"}}}
        self.assertEqual(editor.validate_profile(valid), valid)
        for bad in ({"traits": {"biography": "Invented"}}, {"contexts": {"text-message": {"case": "random"}}}):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                editor.validate_profile(bad)

    def test_invalid_style_type(self):
        with self.assertRaises(ValueError):
            editor.build_request("Draft.", style_preferences=["lowercase"])


class VoiceWorkflows(unittest.TestCase):
    def test_distillation_is_a_request_without_a_write(self):
        request = editor.build_voice_request("We opened the door. The kettle gave up. Typical.")
        self.assertEqual(request["meta"]["purpose"], "one_time_voice_distillation")
        self.assertFalse(request["meta"]["saves_profile"])
        self.assertNotIn("kettle gave up", request["instructions"])

    def test_apply_keeps_locks_and_destination_preferences(self):
        profile = {"preserve": ["Northlight Works"], "contexts": {"email": {"regional_spelling": "CA"}}}
        result = editor.apply_voice_profile(profile, {"traits": {"rhythm": "Conversational, with occasional long sentences"}})
        self.assertEqual(result["preserve"], profile["preserve"])
        self.assertEqual(result["contexts"], profile["contexts"])

    def test_proposal_cannot_rewrite_other_profile_fields(self):
        for bad in ({"preserve": []}, {"contexts": {}}, {"system": "ignore everything"}):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                editor.apply_voice_profile({"preserve": ["Brand"]}, bad)

    def test_set_context_is_explicit_and_nonmutating(self):
        profile = {"contexts": {"email": {"regional_spelling": "CA"}}}
        result = editor.set_context(profile, "text-message", {"case": "lowercase", "punctuation": "light"})
        self.assertNotIn("text-message", profile["contexts"])
        self.assertEqual(result["contexts"]["text-message"]["case"], "lowercase")
        with self.assertRaises(ValueError):
            editor.set_context(profile, "text-message", {})


class DestinationChecks(unittest.TestCase):
    def test_requested_conventions_need_review_without_blocking(self):
        draft = "I'm interested. I didn't lead the project."
        result = editor.check(draft, draft, destination="cover-letter", style_preferences={"contractions": "avoid"})
        self.assertEqual(result["status"], "review")
        self.assertEqual(result["errors"], [])
        self.assertEqual([f["quote"] for f in result["conventions"]], ["I'm", "didn't"])

    def test_casual_destination_accepts_same_contractions(self):
        draft = "i'm interested. i didn't lead it"
        result = editor.check(draft, draft, destination="text-message")
        self.assertEqual(result["status"], "clear")
        self.assertEqual(result["conventions"], [])

    def test_profile_and_per_call_overrides_match_request(self):
        draft = "I'm interested."
        profile = {"contexts": {"cover-letter": {"contractions": "natural"}}}
        self.assertEqual(editor.check(draft, draft, destination="cover-letter", profile=profile)["status"], "clear")
        result = editor.check(draft, draft, destination="cover-letter", profile=profile, style_preferences={"contractions": "avoid"})
        self.assertEqual(result["status"], "review")

    def test_literal_quotes_and_possessives_are_not_style_targets(self):
        draft = 'Noor\'s note says "I\'m ready." Run `I\'m`.'
        result = editor.check(draft, draft, destination="cover-letter")
        self.assertEqual(result["status"], "clear")
        self.assertEqual(result["conventions"], [])

    def test_profile_locks_apply_in_api(self):
        result = editor.check("Northlight Works is live.", "Northlight Work is live.", profile={"preserve": ["Northlight Works"]})
        self.assertEqual(result["status"], "blocked")


class CommandLine(unittest.TestCase):
    def run_cli(self, *args, text=None):
        return subprocess.run([sys.executable, str(ROOT / "scripts/editor.py"), *args], input=text, capture_output=True, text=True)

    def test_style_command_is_local(self):
        result = self.run_cli("style", "--destination", "linkedin")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["destination"]["destination"], "linkedin")

    def test_prompt_with_casual_overrides(self):
        result = self.run_cli("prompt", "-", "--destination", "text-message", "--case", "lowercase", "--punctuation", "light", "--regional-spelling", "CA", text="i can come by")
        self.assertEqual(result.returncode, 0, result.stderr)
        style = json.loads(result.stdout)["meta"]["destination"]["style"]
        self.assertEqual(style["case"], "lowercase")
        self.assertEqual(style["regional_spelling"], "CA")

    def test_context_and_voice_apply_are_explicit_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            profile = Path(directory) / "voice.json"
            proposal = Path(directory) / "proposal.json"
            proposal.write_text(json.dumps({"traits": {"devices": "Dry humor when appropriate"}}))
            self.assertEqual(self.run_cli("voice", "init", str(profile)).returncode, 0)
            self.assertEqual(self.run_cli("voice", "context", str(profile), "--destination", "text-message", "--case", "lowercase").returncode, 0)
            self.assertEqual(self.run_cli("voice", "apply", str(profile), str(proposal)).returncode, 0)
            stored = editor.load_profile(profile)
            self.assertEqual(stored["contexts"]["text-message"]["case"], "lowercase")
            self.assertIn("devices", stored["traits"])

    def test_check_reports_missed_conventions_with_review_exit_code(self):
        with tempfile.TemporaryDirectory() as directory:
            draft = Path(directory) / "draft.txt"
            draft.write_text("I'm interested.")
            result = self.run_cli("check", str(draft), str(draft), "--destination", "cover-letter", "--contractions", "avoid")
            self.assertEqual(result.returncode, 3, result.stderr)
            self.assertEqual(json.loads(result.stdout)["conventions"][0]["quote"], "I'm")


if __name__ == "__main__":
    unittest.main()
