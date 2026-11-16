"""End-to-end collection enrollment, consent, compact editing and control."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from voice_store import add_sample, create_collection, load_collection, save_collection
from voice_learning import apply_learning_proposal, build_learning_request


class VoiceCollectionCLI(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name)
        self.store = self.path / "voice.json"

    def cli(self, *args, text=None, env=None):
        variables = dict(os.environ)
        variables.pop("REWORD_VOICE", None)
        variables.update(env or {})
        return subprocess.run([sys.executable, str(ROOT / "scripts/reword.py"), *map(str, args)],
                              input=text, text=True, capture_output=True, env=variables)

    def create_fitted(self, learn=False):
        store = create_collection("Synthetic writer", learning_enabled=learn)
        store = add_sample(store, "The kettle stopped. We kept talking. The rain did the rest.")
        request = build_learning_request(store)
        proposal = {"request_hash": request["input"]["request_hash"],
                    "evidence_ids": request["input"]["evidence_ids"],
                    "traits": {"rhythm": "Short sentences, with a restrained reflective landing",
                               "openings": "Open with a concrete detail"}}
        store = apply_learning_proposal(store, request, proposal)
        save_collection(self.store, store, create=True)
        return store

    def test_onboard_invites_authored_and_reference_samples(self):
        result = self.cli("voice", "onboard")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("3–5", result.stdout)
        self.assertIn("inspiration", result.stdout)
        self.assertIn("opt in", result.stdout)

    def test_create_and_add_are_explicit_private_writes(self):
        result = self.cli("voice", "create", self.store, "--name", "My writing")
        self.assertEqual(result.returncode, 0, result.stderr)
        sample = self.path / "sample.md"
        sample.write_text("The window stuck. Rain found a way in.")
        result = self.cli("voice", "add", self.store, sample, "--role", "authored", "--destination", "essay")
        self.assertEqual(result.returncode, 0, result.stderr)
        store = load_collection(self.store)
        self.assertEqual(store["samples"][0]["text"], sample.read_text())
        self.assertFalse(store["learning_enabled"])
        if os.name == "posix":
            self.assertEqual(self.store.stat().st_mode & 0o777, 0o600)

    def test_prompt_uses_compact_traits_without_corpus(self):
        self.create_fitted()
        before = self.store.read_bytes()
        result = self.cli("prompt", "-", "--voice", self.store, "--destination", "email", text="The appointment moved to Friday.")
        self.assertEqual(result.returncode, 0, result.stderr)
        request = json.loads(result.stdout)
        self.assertIn("restrained reflective", json.dumps(request["input"]["voice"]))
        self.assertNotIn("kettle", json.dumps(request))
        self.assertNotIn("We kept talking", json.dumps(request))
        self.assertEqual(request["meta"]["voice_guidance_mode"], "personalized")
        self.assertLessEqual(request["meta"]["guidance"]["characters"], 4000)
        self.assertEqual(before, self.store.read_bytes())

    def test_configured_voice_applies_and_can_be_bypassed(self):
        self.create_fitted()
        configured = {"REWORD_VOICE": str(self.store)}
        result = self.cli("prompt", "-", text="Draft.", env=configured)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("voice_collection", json.loads(result.stdout)["meta"])
        result = self.cli("prompt", "-", "--no-voice", text="Draft.", env=configured)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("voice_collection", json.loads(result.stdout)["meta"])

    def test_automatic_feedback_requires_opt_in_and_pause_keeps_voice(self):
        self.create_fitted()
        before = self.store.read_bytes()
        args = ("voice", "feedback", self.store, "--kind", "preference", "--prefer", "Keep useful humor", "--automatic")
        self.assertEqual(self.cli(*args).returncode, 2)
        self.assertEqual(before, self.store.read_bytes())
        self.assertEqual(self.cli("voice", "learning", self.store, "--enabled").returncode, 0)
        self.assertEqual(self.cli(*args).returncode, 0)
        self.assertEqual(self.cli("voice", "learning", self.store, "--disabled").returncode, 0)
        result = self.cli("prompt", "-", "--voice", self.store, text="Draft.")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Keep useful humor", json.dumps(json.loads(result.stdout)["input"]))
        self.assertFalse(load_collection(self.store)["learning_enabled"])

    def test_refinement_update_rejects_stale_work(self):
        self.assertEqual(self.cli("voice", "create", self.store, "--name", "My writing", "--learn").returncode, 0)
        sample = self.path / "sample.txt"
        sample.write_text("We opened the gate. The path was still there. A good start.")
        self.assertEqual(self.cli("voice", "add", self.store, sample).returncode, 0)
        result = self.cli("voice", "refine", self.store)
        self.assertEqual(result.returncode, 0, result.stderr)
        request = json.loads(result.stdout)
        request_path, proposal_path = self.path / "request.json", self.path / "proposal.json"
        request_path.write_text(result.stdout)
        proposal_path.write_text(json.dumps({"request_hash": request["input"]["request_hash"],
            "evidence_ids": request["input"]["evidence_ids"], "traits": {"rhythm": "Short, concrete sentences"}}))
        result = self.cli("voice", "update", self.store, request_path, proposal_path, "--automatic")
        self.assertEqual(result.returncode, 0, result.stderr)
        before = self.store.read_bytes()
        self.assertEqual(self.cli("voice", "update", self.store, request_path, proposal_path).returncode, 2)
        self.assertEqual(before, self.store.read_bytes())

    def test_export_and_forget_do_not_restore_forgotten_inferences(self):
        store = self.create_fitted()
        result = self.cli("voice", "export", self.store, "--format", "card")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Short sentences", result.stdout)
        self.assertNotIn("kettle", result.stdout)
        result = self.cli("voice", "forget", self.store, store["samples"][0]["id"])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("kettle", self.store.read_text())
        self.assertFalse(load_collection(self.store)["profiles"])
        self.assertEqual(self.cli("voice", "rollback", self.store, "--version", "1").returncode, 2)

    def test_profile_and_collection_are_mutually_exclusive(self):
        result = self.cli("prompt", "-", "--profile", "profile.json", "--voice", "voice.json", text="Draft.")
        self.assertEqual(result.returncode, 2)

    def test_a_later_preference_can_reverse_an_earlier_reversal(self):
        self.assertEqual(self.cli("voice", "create", self.store, "--name", "My voice").returncode, 0)
        for option in ("--prefer", "--avoid", "--prefer"):
            result = self.cli("voice", "feedback", self.store, "--kind", "preference", option, "Short sentences")
            self.assertEqual(result.returncode, 0, result.stderr)
        result = self.cli("voice", "export", self.store)
        self.assertEqual(result.returncode, 0, result.stderr)
        profile = json.loads(result.stdout)
        self.assertIn("Short sentences", profile["preferences"])
        self.assertNotIn("Short sentences", profile.get("avoid", []))

    def test_new_cross_destination_samples_surface_global_refresh(self):
        self.create_fitted(learn=True)
        sample = self.path / "essay.md"
        sample.write_text("We left the window open. The room learned a little about the rain.")
        added = self.cli("voice", "add", self.store, sample, "--destination", "essay")
        self.assertEqual(added.returncode, 0, added.stderr)
        result = self.cli("prompt", "-", "--voice", self.store, "--destination", "email", text="The appointment is on Friday.")
        self.assertEqual(result.returncode, 0, result.stderr)
        metadata = json.loads(result.stdout)["meta"]["voice_collection"]
        self.assertTrue(metadata["needs_refresh"])
        self.assertGreater(metadata["pending_global_records"], 0)
        self.assertNotIn("room learned", result.stdout)


if __name__ == "__main__":
    unittest.main()
