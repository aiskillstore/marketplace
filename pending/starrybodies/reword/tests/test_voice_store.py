"""Synthetic evidence only: collection consent, provenance, erasure, and persistence."""

import copy
import hashlib
import importlib
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
voice_store = importlib.import_module("voice_store")


def collection():
    return voice_store.create_collection("Synthetic writer")


def commit(store, destination="general", *, trait="Compact turns", evidence_ids=None, samples=None):
    profile = {"name": store["name"], "traits": {"rhythm": trait}}
    if samples is not None:
        profile["samples"] = samples
    if evidence_ids is None:
        evidence_ids = [record["id"] for record in store["samples"] + store["feedback"]]
    return voice_store.commit_profile(store, destination, profile, evidence_ids,
                                      expected_revision=store["revision"])


class EvidenceAndConsent(unittest.TestCase):
    def test_default_consent_and_detached_values(self):
        original = collection()
        self.assertFalse(original["learning_enabled"])
        self.assertEqual(original["revision"], 0)
        copied = voice_store.validate_collection(original)
        copied["history"].append({"synthetic": True})
        self.assertEqual(original["history"], [])
        for name in ("", " " * 4, "n" * 81, "\ud800"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                voice_store.create_collection(name)
        for value in (1, None, "yes"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                voice_store.create_collection("Synthetic", value)

    def test_authored_reference_hash_and_exact_deduplication(self):
        original = collection()
        snapshot = copy.deepcopy(original)
        text = "Small synthetic note. A second turn."
        authored = voice_store.add_sample(original, text, destination="chat", label="Example A")
        record = authored["samples"][0]
        self.assertEqual(record["sha256"], hashlib.sha256(text.encode()).hexdigest())
        self.assertEqual((record["role"], record["destination"], record["label"]),
                         ("authored", "chat", "Example A"))
        duplicate = voice_store.add_sample(authored, text, destination="chat", label="Example A")
        independently_created = voice_store.add_sample(collection(), text, destination="chat", label="Example A")
        self.assertEqual(duplicate, authored)
        self.assertIsNot(duplicate, authored)
        self.assertEqual(record["id"], independently_created["samples"][0]["id"])
        duplicate["samples"][0]["label"] = "Changed only in copy"
        self.assertEqual(authored["samples"][0]["label"], "Example A")
        reference = voice_store.add_sample(authored, text, role="reference", destination="chat", label="Example A")
        self.assertEqual(len(reference["samples"]), 2)
        self.assertNotEqual(reference["samples"][0]["id"], reference["samples"][1]["id"])
        self.assertEqual(original, snapshot)
        self.assertEqual(reference["revision"], 2)
        self.assertEqual(reference["pending_evidence_ids"], [item["id"] for item in reference["samples"]])

    def test_automatic_feedback_requires_consent_and_never_authors_a_sample(self):
        original = collection()
        with self.assertRaisesRegex(ValueError, "enabled explicitly"):
            voice_store.add_feedback(original, kind="accept", final="Synthetic accepted draft.", automatic=True)
        enabled = voice_store.set_learning(original, True)
        enabled_copy = voice_store.set_learning(enabled, True)
        self.assertEqual(enabled_copy, enabled)
        self.assertIsNot(enabled_copy, enabled)
        accepted = voice_store.add_feedback(enabled, kind="accept", final="Synthetic accepted draft.", automatic=True)
        rejected = voice_store.add_feedback(accepted, kind="reject", draft="Synthetic rejected draft.")
        self.assertEqual(rejected["samples"], [])
        self.assertEqual([item["kind"] for item in rejected["feedback"]], ["accept", "reject"])
        self.assertEqual(rejected["revision"], 3)
        disabled = voice_store.set_learning(rejected, False)
        with self.assertRaises(ValueError):
            voice_store.add_feedback(disabled, kind="accept", final="Synthetic accepted draft.", automatic=True)
        self.assertFalse(original["learning_enabled"])

    def test_explicit_feedback_distinct_revision_and_latest_reversal(self):
        original = collection()
        with self.assertRaises(ValueError):
            voice_store.add_feedback(original, kind="preference")
        for values in ({"prefer": ["Direct questions"], "avoid": [" direct   QUESTIONS "]},
                       {"draft": "Synthetic draft", "final": "Synthetic draft"},
                       {"draft": "Synthetic draft", "final": " Synthetic draft "},
                       {"draft": "", "final": "Synthetic final"}):
            kind = "preference" if "prefer" in values else "revision"
            with self.subTest(values=values), self.assertRaises(ValueError):
                voice_store.add_feedback(original, kind=kind, **values)
        preferred = voice_store.add_feedback(original, kind="preference", prefer=["Direct questions", "direct QUESTIONS"])
        self.assertEqual(preferred["feedback"][0]["prefer"], ["Direct questions"])
        reversed_preference = voice_store.add_feedback(preferred, kind="preference", avoid=["Direct questions"])
        reasoned = voice_store.add_feedback(reversed_preference, kind="preference", reason="Keep the tentative phrasing.")
        revised = voice_store.add_feedback(reasoned, kind="revision", destination="essay",
                                           draft="Synthetic draft.", final="Synthetic author revision.")
        duplicate = voice_store.add_feedback(revised, kind="revision", destination="essay",
                                             draft="Synthetic draft.", final="Synthetic author revision.")
        self.assertEqual(duplicate, revised)
        self.assertEqual(len(revised["feedback"]), 4)
        self.assertEqual(revised["samples"], [])
        self.assertEqual(original, collection())

    def test_exact_preference_recurrence_after_reversal_gets_a_new_deterministic_event(self):
        first = voice_store.add_feedback(collection(), kind="preference", prefer=["Warm"])
        reversed_preference = voice_store.add_feedback(first, kind="preference", avoid=["Warm"])
        restored = voice_store.add_feedback(reversed_preference, kind="preference", prefer=["Warm"])
        self.assertEqual(len(restored["feedback"]), 3)
        self.assertEqual(restored["revision"], 3)
        self.assertEqual(restored["feedback"][-1]["prefer"], ["Warm"])
        self.assertEqual(restored["feedback"][-1]["occurrence"], 2)
        self.assertNotIn("occurrence", first["feedback"][0])
        self.assertNotEqual(restored["feedback"][-1]["id"], first["feedback"][0]["id"])
        duplicate = voice_store.add_feedback(restored, kind="preference", prefer=["Warm"])
        self.assertEqual(duplicate, restored)
        self.assertIsNot(duplicate, restored)
        replayed = collection()
        for direction in ("prefer", "avoid", "prefer"):
            replayed = voice_store.add_feedback(replayed, kind="preference", **{direction: ["Warm"]})
        self.assertEqual(replayed, restored)
        again_avoided = voice_store.add_feedback(restored, kind="preference", avoid=["Warm"])
        again_preferred = voice_store.add_feedback(again_avoided, kind="preference", prefer=["Warm"])
        self.assertEqual(again_preferred["feedback"][-1]["occurrence"], 3)
        self.assertEqual(len({record["id"] for record in again_preferred["feedback"]}), 5)
        self.assertEqual(voice_store.validate_collection(again_preferred), again_preferred)
        tampered = copy.deepcopy(restored)
        tampered["feedback"][-1]["occurrence"] = 1
        with self.assertRaises(ValueError):
            voice_store.validate_collection(tampered)

    def test_feedback_deduplication_scope_respects_destinations_and_cross_kind_guidance(self):
        first = voice_store.add_feedback(collection(), kind="preference", prefer=["Warm"])
        unrelated = voice_store.add_feedback(first, kind="preference", avoid=["Warm"], destination="email")
        unrelated = voice_store.add_feedback(unrelated, kind="accept", final="A synthetic model draft.")
        self.assertEqual(voice_store.add_feedback(unrelated, kind="preference", prefer=["Warm"]), unrelated)
        correction = voice_store.add_feedback(unrelated, kind="revision", draft="A synthetic old draft.",
                                              final="A synthetic revised draft.", avoid=["Warm"])
        restored = voice_store.add_feedback(correction, kind="preference", prefer=["Warm"])
        self.assertEqual(restored["revision"], correction["revision"] + 1)
        self.assertEqual(restored["feedback"][-1]["occurrence"], 2)
        self.assertEqual(len(restored["feedback"]), 5)
        self.assertEqual(restored["samples"], [])

    def test_accept_reject_accept_is_a_new_assessment_without_authored_training_text(self):
        accepted = voice_store.add_feedback(collection(), kind="accept", final="A synthetic model draft.")
        rejected = voice_store.add_feedback(accepted, kind="reject", final="A synthetic model draft.")
        accepted_again = voice_store.add_feedback(rejected, kind="accept", final="A synthetic model draft.")
        self.assertEqual([record["kind"] for record in accepted_again["feedback"]], ["accept", "reject", "accept"])
        self.assertEqual(accepted_again["feedback"][-1]["occurrence"], 2)
        self.assertEqual(accepted_again["samples"], [])
        self.assertEqual(voice_store.add_feedback(accepted_again, kind="accept", final="A synthetic model draft."),
                         accepted_again)

    def test_record_tampering_unknown_destinations_and_nonfinite_json_are_rejected(self):
        original = voice_store.add_sample(collection(), "A synthetic observation.")
        for field, replacement in (("id", "sample-forged"), ("sha256", "0" * 64), ("text", "A changed observation.")):
            tampered = copy.deepcopy(original)
            tampered["samples"][0][field] = replacement
            with self.subTest(field=field), self.assertRaises(ValueError):
                voice_store.validate_collection(tampered)
        for function, keywords in ((voice_store.add_sample, {"text": "A note.", "destination": "SMS"}),
                                   (voice_store.add_sample, {"text": "A note.", "role": "accepted"}),
                                   (voice_store.add_feedback, {"kind": "review", "reason": "Synthetic"}),
                                   (voice_store.add_feedback, {"kind": "accept", "automatic": 1})):
            with self.subTest(keywords=keywords), self.assertRaises(ValueError):
                function(original, **keywords)
        bad = collection()
        bad["revision"] = float("nan")
        with self.assertRaises(ValueError):
            voice_store.validate_collection(bad)


class ProfileHistoryAndForgetting(unittest.TestCase):
    def test_review_coverage_is_separate_from_inherited_provenance_and_survives_rollback(self):
        store = voice_store.add_sample(collection(), "Synthetic first essay sample.", destination="essay")
        store = voice_store.add_sample(store, "Synthetic second essay sample.", destination="essay")
        first_id, second_id = [item["id"] for item in store["samples"]]
        profile = {"traits": {"rhythm": "Compact turns"}}
        inherited = voice_store.commit_profile(store, "general", profile, [first_id, second_id],
                                               expected_revision=store["revision"],
                                               reviewed_evidence_ids=[first_id])
        entry = inherited["profiles"]["general"]
        self.assertEqual(set(entry["evidence_ids"]), {first_id, second_id})
        self.assertEqual(entry["reviewed_evidence_ids"], [first_id])
        self.assertEqual(inherited["pending_evidence_ids"], [second_id])
        self.assertEqual(inherited["history"][-1]["profiles"]["general"]["reviewed_evidence_ids"], [first_id])
        local = voice_store.commit_profile(inherited, "essay", profile, [first_id, second_id],
                                          expected_revision=inherited["revision"],
                                          reviewed_evidence_ids=[second_id])
        self.assertEqual(local["pending_evidence_ids"], [])
        self.assertEqual(local["profiles"]["essay"]["reviewed_evidence_ids"], [second_id])
        rolled = voice_store.rollback_profile(local, inherited["profile_version"])
        self.assertEqual(rolled["profiles"], inherited["profiles"])
        self.assertEqual(rolled["pending_evidence_ids"], [second_id])
        erased = voice_store.forget_evidence(rolled, second_id)
        self.assertEqual(erased["profiles"], {})
        self.assertEqual(erased["history"], [])
        self.assertNotIn(second_id, json.dumps(erased))

    def test_review_coverage_default_legacy_fallback_validation_and_duplicate_rules(self):
        store = voice_store.add_sample(collection(), "A synthetic sample.")
        evidence_id = store["samples"][0]["id"]
        profile = {"traits": {"rhythm": "Compact turns"}}
        unreviewed = voice_store.commit_profile(store, "general", profile, [evidence_id],
                                               expected_revision=store["revision"], reviewed_evidence_ids=[])
        reviewed = voice_store.commit_profile(unreviewed, "general", profile, [evidence_id],
                                             expected_revision=unreviewed["revision"])
        self.assertEqual(reviewed["revision"], unreviewed["revision"] + 1)
        self.assertEqual(reviewed["profiles"]["general"]["reviewed_evidence_ids"], [evidence_id])
        self.assertEqual(reviewed["pending_evidence_ids"], [])
        duplicate = voice_store.commit_profile(reviewed, "general", profile, [evidence_id],
                                              expected_revision=reviewed["revision"],
                                              reviewed_evidence_ids=[evidence_id])
        self.assertEqual(duplicate, reviewed)
        legacy = copy.deepcopy(reviewed)
        del legacy["profiles"]["general"]["reviewed_evidence_ids"]
        for snapshot in legacy["history"]:
            for entry in snapshot["profiles"].values():
                entry.pop("reviewed_evidence_ids", None)
        self.assertEqual(voice_store.validate_collection(legacy), legacy)
        self.assertEqual(voice_store.commit_profile(legacy, "general", profile, [evidence_id],
                                                   expected_revision=legacy["revision"]), legacy)
        for invalid in ([evidence_id, evidence_id], ["sample-missing"], "not-a-list"):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                voice_store.commit_profile(store, "general", profile, [evidence_id],
                                           expected_revision=store["revision"], reviewed_evidence_ids=invalid)
        absent_provenance = copy.deepcopy(reviewed)
        absent_provenance["profiles"]["general"]["evidence_ids"] = []
        with self.assertRaisesRegex(ValueError, "subset"):
            voice_store.validate_collection(absent_provenance)

    def test_stale_commit_and_provenance_are_checked_without_mutation(self):
        original = voice_store.add_sample(collection(), "A synthetic sample.")
        snapshot = copy.deepcopy(original)
        profile = {"traits": {"rhythm": "Compact turns"}}
        for ids, revision in ((["sample-missing"], original["revision"]),
                              ([original["samples"][0]["id"]], original["revision"] - 1)):
            with self.subTest(ids=ids, revision=revision), self.assertRaises(ValueError):
                voice_store.commit_profile(original, "general", profile, ids, expected_revision=revision)
        updated = commit(original)
        duplicate = voice_store.commit_profile(updated, "general", updated["profiles"]["general"]["profile"],
                                               updated["profiles"]["general"]["evidence_ids"],
                                               expected_revision=updated["revision"])
        self.assertEqual(duplicate, updated)
        self.assertIsNot(duplicate["profiles"], updated["profiles"])
        with self.assertRaisesRegex(ValueError, "Stale"):
            voice_store.commit_profile(updated, "general", profile, [original["samples"][0]["id"]],
                                       expected_revision=original["revision"])
        self.assertEqual(original, snapshot)
        self.assertEqual(updated["pending_evidence_ids"], [])

    def test_legacy_profile_bounds_are_enforced_locally(self):
        original = voice_store.add_sample(collection(), "A synthetic sample.")
        for profile in ({"preferences": ["x"] * 9}, {"avoid": ["x" * 101]},
                        {"samples": ["x" * 501]}, {"traits": {"unrecognized": "value"}},
                        {"contexts": {"email": {"case": "random"}}},
                        {"preferences": ["Direct"], "avoid": ["direct"]}, {"unrecognized": True}):
            with self.subTest(profile=profile), self.assertRaises(ValueError):
                voice_store.commit_profile(original, "general", profile, [], expected_revision=original["revision"])

    def test_rollback_preserves_corpus_and_reopens_uncovered_evidence(self):
        first = voice_store.add_sample(collection(), "Synthetic first sample.")
        first = commit(first)
        first_version = first["profile_version"]
        second = voice_store.add_sample(first, "Synthetic second sample.", destination="email")
        second = voice_store.add_feedback(second, kind="preference", prefer=["Plain openings"])
        second = commit(second, "email", trait="A longer rhythm")
        second = voice_store.set_learning(second, True)
        corpus = copy.deepcopy((second["samples"], second["feedback"]))
        rolled = voice_store.rollback_profile(second, first_version)
        self.assertEqual(rolled["profiles"], first["profiles"])
        self.assertEqual((rolled["samples"], rolled["feedback"]), corpus)
        self.assertTrue(rolled["learning_enabled"])
        self.assertGreater(rolled["profile_version"], second["profile_version"])
        self.assertEqual(rolled["revision"], second["revision"] + 1)
        self.assertEqual(set(rolled["pending_evidence_ids"]),
                         {second["samples"][1]["id"], second["feedback"][0]["id"]})
        self.assertEqual(rolled["history"][-1]["action"], "rollback")
        self.assertEqual(voice_store.rollback_profile(rolled, first_version), rolled)

    def test_forget_purges_cards_and_history_text_but_retains_other_explicit_feedback(self):
        secret = "SYNTHETIC-UNIQUE-TEXT-TO-FORGET"
        original = voice_store.add_sample(collection(), secret)
        forgotten_id = original["samples"][0]["id"]
        original = voice_store.add_sample(original, "A synthetic surviving sample.", role="reference")
        original = voice_store.add_feedback(original, kind="preference", prefer=["Keep short endings"])
        original = commit(original, samples=[secret])
        original = commit(original, "email", trait=secret)
        old_version = original["history"][0]["version"]
        frozen = copy.deepcopy(original)
        forgotten = voice_store.forget_evidence(original, forgotten_id)
        serialized = json.dumps(forgotten)
        self.assertNotIn(secret, serialized)
        self.assertNotIn(forgotten_id, serialized)
        self.assertEqual(forgotten["profiles"], {})
        self.assertEqual(forgotten["history"], [])
        self.assertEqual(forgotten["feedback"], original["feedback"])
        self.assertEqual(len(forgotten["samples"]), 1)
        self.assertEqual(set(forgotten["pending_evidence_ids"]),
                         {item["id"] for item in forgotten["samples"] + forgotten["feedback"]})
        with self.assertRaisesRegex(ValueError, "forgotten"):
            voice_store.rollback_profile(forgotten, old_version)
        self.assertEqual(original, frozen)
        self.assertEqual(voice_store.forget_evidence(forgotten, forgotten_id), forgotten)
        rebuilt = commit(forgotten)
        self.assertGreater(rebuilt["profile_version"], original["profile_version"])

    def test_forget_revision_removes_draft_final_and_inferred_traits(self):
        store = voice_store.add_feedback(collection(), kind="revision", draft="Synthetic old phrase.",
                                         final="SYNTHETIC-UNIQUE-REVISION", reason="A synthetic explanation.")
        feedback_id = store["feedback"][0]["id"]
        store = commit(store, trait="SYNTHETIC-UNIQUE-REVISION")
        erased = voice_store.forget_evidence(store, feedback_id)
        self.assertEqual(erased["feedback"], [])
        self.assertNotIn("SYNTHETIC-UNIQUE-REVISION", json.dumps(erased))
        self.assertEqual(erased["history"], [])

    def test_history_is_bounded_and_old_versions_expire(self):
        store = voice_store.add_sample(collection(), "A synthetic sample.")
        for number in range(voice_store.MAX_HISTORY + 3):
            store = commit(store, trait=f"Synthetic rhythm {number}")
        self.assertEqual(len(store["history"]), voice_store.MAX_HISTORY)
        self.assertEqual(store["history"][0]["version"], 4)
        with self.assertRaises(ValueError):
            voice_store.rollback_profile(store, 1)
        voice_store.validate_collection(store)


class PrivatePersistence(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.target = self.directory / "private" / "synthetic-voice.json"

    def test_private_creation_atomic_update_roundtrip_and_nonmutation(self):
        original = voice_store.add_sample(collection(), "A synthetic sample.")
        snapshot = copy.deepcopy(original)
        self.assertEqual(voice_store.save_collection(self.target, original, create=True), self.target)
        self.assertEqual(voice_store.load_collection(self.target), original)
        if os.name == "posix":
            self.assertEqual(stat.S_IMODE(self.target.stat().st_mode), 0o600)
            self.assertEqual(stat.S_IMODE(self.target.parent.stat().st_mode), 0o700)
        before = self.target.stat()
        updated = voice_store.add_feedback(original, kind="preference", avoid=["Generic cheerleading"])
        voice_store.save_collection(self.target, updated, expected_revision=original["revision"])
        self.assertEqual(voice_store.load_collection(self.target), updated)
        if os.name == "posix":
            self.assertNotEqual(before.st_ino, self.target.stat().st_ino)
            self.assertEqual(stat.S_IMODE(self.target.stat().st_mode), 0o600)
        self.assertEqual(original, snapshot)
        self.assertEqual(sorted(item.name for item in self.target.parent.iterdir()), [self.target.name])
        with self.assertRaises(FileExistsError):
            voice_store.save_collection(self.target, updated, create=True)

    def test_atomic_replacement_failure_preserves_old_file_and_cleans_temporary(self):
        original = collection()
        voice_store.save_collection(self.target, original, create=True)
        exact_bytes = self.target.read_bytes()
        updated = voice_store.add_sample(original, "A synthetic sample.")
        with patch.object(voice_store.os, "replace", side_effect=OSError("synthetic disk failure")):
            with self.assertRaisesRegex(OSError, "synthetic disk failure"):
                voice_store.save_collection(self.target, updated, expected_revision=original["revision"])
        self.assertEqual(self.target.read_bytes(), exact_bytes)
        self.assertEqual([item.name for item in self.target.parent.iterdir()], [self.target.name])

    def test_stale_and_conflicting_saves_are_rejected(self):
        original = collection()
        voice_store.save_collection(self.target, original, create=True)
        first = voice_store.add_sample(original, "A synthetic first branch.")
        conflict = voice_store.add_sample(original, "A synthetic second branch.")
        voice_store.save_collection(self.target, first, expected_revision=original["revision"])
        for stale in (original, conflict):
            with self.subTest(revision=stale["revision"]), self.assertRaisesRegex(ValueError, "Stale"):
                voice_store.save_collection(self.target, stale, expected_revision=first["revision"])
        self.assertEqual(voice_store.load_collection(self.target), first)
        voice_store.save_collection(self.target, first, expected_revision=first["revision"])
        with self.assertRaises(FileNotFoundError):
            voice_store.save_collection(self.directory / "missing.json", collection())

    def test_higher_revision_from_stale_ancestry_cannot_resurrect_forgotten_text(self):
        marker = "SYNTHETIC-FORGOTTEN-BY-ANOTHER-WRITER"
        original = voice_store.add_sample(collection(), marker)
        voice_store.save_collection(self.target, original, create=True)
        writer_a = voice_store.load_collection(self.target)
        writer_b = voice_store.load_collection(self.target)
        loaded_revision = writer_a["revision"]
        writer_a = voice_store.forget_evidence(writer_a, writer_a["samples"][0]["id"])
        voice_store.save_collection(self.target, writer_a, expected_revision=loaded_revision)
        writer_b = voice_store.add_feedback(writer_b, kind="preference", prefer=["Quiet endings"])
        writer_b = voice_store.set_learning(writer_b, True)
        self.assertGreater(writer_b["revision"], writer_a["revision"])
        snapshot = copy.deepcopy(writer_b)
        with self.assertRaisesRegex(ValueError, "Stale collection ancestry"):
            voice_store.save_collection(self.target, writer_b, expected_revision=loaded_revision)
        self.assertEqual(voice_store.load_collection(self.target), writer_a)
        self.assertNotIn(marker, self.target.read_text(encoding="utf-8"))
        self.assertEqual(writer_b, snapshot)
        self.assertEqual([item.name for item in self.target.parent.iterdir()], [self.target.name])

    def test_existing_updates_require_the_loaded_expected_revision(self):
        original = collection()
        voice_store.save_collection(self.target, original, create=True)
        updated = voice_store.add_sample(original, "A synthetic newer collection.")
        for candidate in (original, updated):
            with self.subTest(revision=candidate["revision"]), self.assertRaisesRegex(ValueError, "requires expected_revision"):
                voice_store.save_collection(self.target, candidate)
        for invalid in (True, -1, "0"):
            with self.subTest(expected_revision=invalid), self.assertRaises(ValueError):
                voice_store.save_collection(self.target, updated, expected_revision=invalid)
        self.assertEqual(voice_store.load_collection(self.target), original)
        voice_store.save_collection(self.target, updated, expected_revision=original["revision"])
        self.assertEqual(voice_store.load_collection(self.target), updated)

    def test_concurrent_target_replacement_is_detected(self):
        original = collection()
        voice_store.save_collection(self.target, original, create=True)
        updated = voice_store.add_sample(original, "Synthetic proposed update.")
        external = voice_store.add_sample(original, "Synthetic intervening update.")
        replacement = self.directory / "replacement.json"
        voice_store.save_collection(replacement, external, create=True)
        real_fsync = voice_store.os.fsync
        replaced = False

        def intervene(descriptor):
            nonlocal replaced
            real_fsync(descriptor)
            if not replaced:
                replaced = True
                replacement.replace(self.target)

        with patch.object(voice_store.os, "fsync", side_effect=intervene):
            with self.assertRaisesRegex(ValueError, "changed while saving"):
                voice_store.save_collection(self.target, updated, expected_revision=original["revision"])
        self.assertEqual(voice_store.load_collection(self.target), external)
        self.assertEqual([item.name for item in self.target.parent.iterdir()], [self.target.name])

    @unittest.skipUnless(hasattr(os, "symlink"), "Symlinks unavailable")
    def test_final_and_parent_symlinks_are_refused(self):
        voice_store.save_collection(self.target, collection(), create=True)
        link = self.directory / "link.json"
        try:
            link.symlink_to(self.target)
        except OSError as error:
            self.skipTest(str(error))
        for function, arguments in ((voice_store.load_collection, (link,)),
                                    (voice_store.save_collection, (link, collection()))):
            with self.subTest(function=function.__name__), self.assertRaisesRegex(ValueError, "symlink"):
                function(*arguments)
        with self.assertRaisesRegex(ValueError, "symlink"):
            voice_store.save_collection(link, collection(), create=True)
        parent_link = self.directory / "linked-parent"
        parent_link.symlink_to(self.target.parent, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            voice_store.load_collection(parent_link / self.target.name)
        with self.assertRaisesRegex(ValueError, "symlink"):
            voice_store.save_collection(parent_link / "new.json", collection(), create=True)
        dangling = self.directory / "dangling.json"
        dangling.symlink_to(self.directory / "missing.json")
        with self.assertRaisesRegex(ValueError, "symlink"):
            voice_store.save_collection(dangling, collection(), create=True)

    @unittest.skipUnless(os.name == "posix", "POSIX permission checks")
    def test_public_permissions_wrong_owner_and_special_files_are_refused(self):
        voice_store.save_collection(self.target, collection(), create=True)
        self.target.chmod(0o644)
        for function, arguments in ((voice_store.load_collection, (self.target,)),
                                    (voice_store.save_collection, (self.target, collection()))):
            with self.subTest(function=function.__name__), self.assertRaisesRegex(ValueError, "permissions"):
                function(*arguments)
        self.target.chmod(0o600)
        with patch.object(voice_store.os, "getuid", return_value=self.target.stat().st_uid + 1):
            with self.assertRaisesRegex(ValueError, "belong"):
                voice_store.load_collection(self.target)
        fifo = self.directory / "synthetic-fifo"
        os.mkfifo(fifo, 0o600)
        with self.assertRaisesRegex(ValueError, "regular"):
            voice_store.load_collection(fifo)

    def test_bounded_load_duplicate_keys_and_no_partial_creation(self):
        voice_store.save_collection(self.target, collection(), create=True)
        with patch.object(voice_store, "MAX_STORE_BYTES", 100):
            with self.assertRaisesRegex(ValueError, "limit"):
                voice_store.load_collection(self.target)
            with self.assertRaisesRegex(ValueError, "limit"):
                voice_store.save_collection(self.directory / "too-large.json", collection(), create=True)
        self.assertFalse((self.directory / "too-large.json").exists())
        self.target.write_text('{"schema_version":1,"schema_version":1}', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "valid"):
            voice_store.load_collection(self.target)

    def test_forgetting_is_persisted_with_no_recoverable_history(self):
        marker = "SYNTHETIC-PERSISTED-FORGET-MARKER"
        store = voice_store.add_sample(collection(), marker)
        sample_id = store["samples"][0]["id"]
        store = commit(store, samples=[marker])
        version = store["profile_version"]
        voice_store.save_collection(self.target, store, create=True)
        forgotten = voice_store.forget_evidence(voice_store.load_collection(self.target), sample_id)
        voice_store.save_collection(self.target, forgotten, expected_revision=store["revision"])
        reloaded = voice_store.load_collection(self.target)
        self.assertNotIn(marker, self.target.read_text(encoding="utf-8"))
        with self.assertRaises(ValueError):
            voice_store.rollback_profile(reloaded, version)


if __name__ == "__main__":
    unittest.main()
