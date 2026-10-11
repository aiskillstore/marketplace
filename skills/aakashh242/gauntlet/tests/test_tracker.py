"""Deterministic unit/integration tests; no network, model, or target project needed."""
from __future__ import annotations
import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "gauntlet.py"
spec = importlib.util.spec_from_file_location("gauntlet", SCRIPT)
g = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(g)


def fresh(**kwargs):
    return g.make_state("Fixture only", "snapshot-A", **kwargs)


def complete(state, angle="boundary partition attack"):
    for task in state["tasks"]:
        g.apply_event(state, {"type": "task", "id": task, "status": "done", "evidence": "Fixture review result"})
    for name in state["required_checks"]:
        g.apply_event(state, {"type": "check", "id": name, "kind": "execution", "result": "pass",
                              "command": "fixture-test-command", "exit_code": 0, "evidence": "Fixture: passed"})
    g.apply_event(state, {"type": "close_round", "angle": angle, "independence": "solo-role-pass", "summary": "Fixture review completed"})


def finding(state, severity="medium"):
    g.apply_event(state, {"type": "finding", "id": "F001", "status": "confirmed", "severity": severity,
                          "title": "Duplicate commit", "location": "fixture.py:12", "claim": "Exactly one durable effect required",
                          "evidence": "Fixture reproduction shows two rows"})


class WorkflowTests(unittest.TestCase):
    def test_defaults_are_read_only_and_core(self):
        s = fresh()
        self.assertEqual(s["mode"], "review")
        self.assertEqual(s["lenses"], ["core"])
        self.assertEqual(g.gate(s)["outcome"], "BLOCKED")

    def test_unknown_lens_rejected(self):
        with self.assertRaises(g.GauntletError): fresh(lenses=["made-up"])

    def test_bool_is_not_a_budget(self):
        with self.assertRaises(g.GauntletError): fresh(max_rounds=True)

    def test_budget_range(self):
        for n in [0, -1, 21]:
            with self.assertRaises(g.GauntletError): fresh(max_rounds=n)

    def test_unknown_event_field_rejected(self):
        with self.assertRaises(g.GauntletError):
            g.apply_event(fresh(), {"type": "note", "text": "ok", "shell": "touch nowhere"})

    def test_duplicate_json_keys_rejected(self):
        with self.assertRaises(g.GauntletError): g.decode('{"type":"note","type":"target"}')

    def test_nonfinite_json_rejected(self):
        with self.assertRaises(g.GauntletError): g.decode('{"n":NaN}')

    def test_task_requires_evidence(self):
        with self.assertRaises(g.GauntletError):
            g.apply_event(fresh(), {"type": "task", "id": "core", "status": "done"})

    def test_core_cannot_be_excluded(self):
        with self.assertRaises(g.GauntletError):
            g.apply_event(fresh(), {"type": "task", "id": "core", "status": "not_applicable", "reason": "skip"})

    def test_other_lens_can_be_excluded_with_reason(self):
        s = fresh(lenses=["security-privacy"])
        g.apply_event(s, {"type": "task", "id": "security-privacy", "status": "not_applicable", "reason": "Reviewed scope contains prose only"})
        self.assertEqual(s["tasks"]["security-privacy"]["status"], "not_applicable")

    def test_review_mode_complete_with_confirmed_findings(self):
        s = fresh()
        finding(s)
        complete(s)
        self.assertEqual(g.gate(s)["outcome"], "REVIEW_COMPLETE")
        self.assertFalse(s["rounds"][0]["clean"])

    def test_candidate_blocks_review_completion(self):
        s = fresh()
        g.apply_event(s, {"type": "finding", "id": "F001", "status": "candidate", "severity": "low",
                          "title": "Suspected gap", "location": "fixture", "claim": "Possible mismatch"})
        complete(s)
        self.assertEqual(g.gate(s)["outcome"], "BLOCKED")

    def test_review_mode_cannot_claim_repairs(self):
        s = fresh()
        finding(s)
        g.apply_event(s, {"type": "target", "revision": "snapshot-B", "reason": "User updated artifact"})
        with self.assertRaises(g.GauntletError):
            g.apply_event(s, {"type": "finding", "id": "F001", "status": "patched", "root_cause": "race", "fix": "constraint", "regression": "duplicate replay"})

    def test_clean_repair_pass(self):
        s = fresh(mode="repair")
        complete(s)
        self.assertEqual(g.gate(s)["outcome"], "PASS_WITHIN_SCOPE")

    def test_critical_requires_distinct_two_passes(self):
        s = fresh(mode="repair", tier="critical")
        complete(s, "boundary partitions")
        self.assertEqual(g.gate(s)["outcome"], "BLOCKED")
        g.apply_event(s, {"type": "next_round", "reason": "Probe an independent failure family"})
        complete(s, "controlled cancellation scheduling")
        self.assertEqual(g.gate(s)["outcome"], "PASS_WITHIN_SCOPE")

    def test_repeated_angle_does_not_count_twice(self):
        s = fresh(mode="repair", tier="critical")
        complete(s, "Boundary PARTITIONS")
        g.apply_event(s, {"type": "next_round", "reason": "repeat"})
        complete(s, "  boundary   partitions ")
        self.assertEqual(g.clean_count(s), 1)
        self.assertEqual(g.gate(s)["outcome"], "BLOCKED")

    def test_missing_checks_block(self):
        s = fresh(mode="repair")
        g.apply_event(s, {"type": "task", "id": "core", "status": "done", "evidence": "Source inspection"})
        g.apply_event(s, {"type": "close_round", "angle": "boundaries", "independence": "solo-role-pass", "summary": "Execution unavailable"})
        self.assertTrue(any("missing" in x for x in g.gate(s)["reasons"]))

    def test_nonzero_exit_cannot_pass(self):
        with self.assertRaises(g.GauntletError):
            g.apply_event(fresh(), {"type": "check", "id": "baseline", "kind": "execution", "result": "pass", "exit_code": 1,
                                   "command": "test", "evidence": "failed"})

    def test_inspection_not_substitute_for_execution(self):
        s = fresh(mode="repair")
        g.apply_event(s, {"type": "task", "id": "core", "status": "done", "evidence": "inspected"})
        g.apply_event(s, {"type": "check", "id": "baseline", "kind": "inspection", "result": "pass", "command": "Read the contract", "evidence": "matches"})
        g.apply_event(s, {"type": "close_round", "angle": "prose", "independence": "solo-role-pass", "summary": "Inspection only"})
        self.assertTrue(any("execution was required" in x for x in g.gate(s)["reasons"]))

    def test_inspection_mode_is_supported(self):
        s = fresh(verification="inspection")
        g.apply_event(s, {"type": "task", "id": "core", "status": "done", "evidence": "Source checked"})
        g.apply_event(s, {"type": "check", "id": "baseline", "kind": "inspection", "result": "pass", "command": "Compare to source", "evidence": "Supported"})
        g.apply_event(s, {"type": "close_round", "angle": "counterexample search", "independence": "solo-role-pass", "summary": "Complete"})
        self.assertEqual(g.gate(s)["outcome"], "REVIEW_COMPLETE")

    def test_failed_additional_check_blocks(self):
        s = fresh(mode="repair")
        g.apply_event(s, {"type": "check", "id": "extra", "kind": "execution", "result": "fail", "command": "extra tests", "exit_code": 1, "evidence": "Failed"})
        complete(s)
        self.assertTrue(any("additional check extra" in x for x in g.gate(s)["reasons"]))

    def test_target_change_invalidates_checks_and_tasks(self):
        s = fresh(mode="repair")
        g.apply_event(s, {"type": "task", "id": "core", "status": "done", "evidence": "done"})
        g.apply_event(s, {"type": "check", "id": "baseline", "kind": "execution", "result": "pass", "command": "test", "exit_code": 0, "evidence": "ok"})
        g.apply_event(s, {"type": "target", "revision": "snapshot-B", "reason": "Patch applied"})
        self.assertEqual(s["tasks"]["core"]["status"], "pending")
        self.assertEqual(s["checks"], {})
        complete(s)
        self.assertFalse(s["rounds"][0]["clean"])

    def test_patch_requires_changed_revision(self):
        s = fresh(mode="repair")
        finding(s)
        with self.assertRaises(g.GauntletError):
            g.apply_event(s, {"type": "finding", "id": "F001", "status": "patched", "root_cause": "missing constraint", "fix": "constraint", "regression": "duplicate test"})

    def test_full_repair_lifecycle_and_reopening(self):
        s = fresh(mode="repair")
        finding(s)
        g.apply_event(s, {"type": "target", "revision": "snapshot-B", "reason": "Fix applied"})
        g.apply_event(s, {"type": "finding", "id": "F001", "status": "patched", "root_cause": "missing uniqueness", "fix": "enforced uniqueness", "regression": "before duplicate fails, after single record passes"})
        g.apply_event(s, {"type": "check", "id": "baseline", "kind": "execution", "result": "pass", "command": "run fixture", "exit_code": 0, "evidence": "passed"})
        g.apply_event(s, {"type": "finding", "id": "F001", "status": "verified", "verification": ["baseline"]})
        complete(s)
        self.assertFalse(s["rounds"][0]["clean"])
        g.apply_event(s, {"type": "next_round", "reason": "Attack neighboring event order"})
        complete(s, "reordered delivery")
        self.assertEqual(g.gate(s)["outcome"], "PASS_WITHIN_SCOPE")
        g.apply_event(s, {"type": "next_round", "reason": "User changed additional code"})
        g.apply_event(s, {"type": "target", "revision": "snapshot-C", "reason": "New target"})
        self.assertEqual(s["findings"]["F001"]["status"], "patched")
        self.assertEqual(g.clean_count(s), 0)

    def test_changed_target_reopens_accepted_risk(self):
        s = fresh(mode="repair")
        finding(s, "low")
        g.apply_event(s, {"type": "finding", "id": "F001", "status": "accepted", "reason": "Bounded risk accepted", "approval": "message-17"})
        g.apply_event(s, {"type": "target", "revision": "snapshot-B", "reason": "Other fix changes the artifact"})
        self.assertEqual(s["findings"]["F001"]["status"], "confirmed")
        self.assertEqual(s["findings"]["F001"]["approval"], "")

    def test_changed_target_reopens_readonly_confirmation(self):
        s = fresh()
        finding(s)
        g.apply_event(s, {"type": "target", "revision": "snapshot-B", "reason": "User submitted a new artifact"})
        self.assertEqual(s["findings"]["F001"]["status"], "candidate")

    def test_overwriting_fix_check_with_inspection_blocks(self):
        s = fresh(mode="repair")
        finding(s)
        g.apply_event(s, {"type": "target", "revision": "snapshot-B", "reason": "Fix applied"})
        g.apply_event(s, {"type": "finding", "id": "F001", "status": "patched", "root_cause": "missing uniqueness", "fix": "constraint", "regression": "duplicate operation"})
        g.apply_event(s, {"type": "check", "id": "fix-check", "kind": "execution", "result": "pass", "command": "run fixture", "exit_code": 0, "evidence": "passed"})
        g.apply_event(s, {"type": "finding", "id": "F001", "status": "verified", "verification": ["fix-check"]})
        g.apply_event(s, {"type": "check", "id": "fix-check", "kind": "inspection", "result": "pass", "command": "read code", "evidence": "looks consistent"})
        self.assertTrue(any("no longer execution-backed" in reason for reason in g.finding_gaps(s)))

    def test_corrupt_missing_lens_task_rejected(self):
        s = fresh(lenses=["security-privacy"])
        del s["tasks"]["security-privacy"]
        with self.assertRaises(g.GauntletError):
            g.validate_state(s)

    def test_verified_requires_named_evidence(self):
        s = fresh(mode="repair")
        finding(s)
        g.apply_event(s, {"type": "target", "revision": "snapshot-B", "reason": "Fix"})
        g.apply_event(s, {"type": "finding", "id": "F001", "status": "patched", "root_cause": "invariant", "fix": "enforce", "regression": "test"})
        with self.assertRaises(g.GauntletError):
            g.apply_event(s, {"type": "finding", "id": "F001", "status": "verified", "verification": ["missing"]})

    def test_candidate_cannot_jump_to_verified(self):
        s = fresh(mode="repair")
        finding(s)
        with self.assertRaises(g.GauntletError):
            g.apply_event(s, {"type": "finding", "id": "F001", "status": "verified"})

    def test_high_cannot_be_accepted(self):
        s = fresh(mode="repair")
        finding(s, "high")
        with self.assertRaises(g.GauntletError):
            g.apply_event(s, {"type": "finding", "id": "F001", "status": "accepted", "reason": "later", "approval": "user-message-1"})

    def test_accepted_risk_needs_approval(self):
        s = fresh(mode="repair")
        finding(s, "low")
        with self.assertRaises(g.GauntletError):
            g.apply_event(s, {"type": "finding", "id": "F001", "status": "accepted", "reason": "later"})

    def test_accepted_risk_is_exceptions_not_clean_bill(self):
        s = fresh(mode="repair")
        finding(s, "low")
        g.apply_event(s, {"type": "finding", "id": "F001", "status": "accepted", "reason": "Owner defers bounded cost", "approval": "user-message-17"})
        complete(s)
        g.apply_event(s, {"type": "next_round", "reason": "Check remaining scope"})
        complete(s, "normal behavior and boundary retest")
        self.assertEqual(g.gate(s)["outcome"], "PASS_WITH_EXCEPTIONS")

    def test_dismissed_false_positive_can_be_clean(self):
        s = fresh(mode="repair")
        finding(s)
        g.apply_event(s, {"type": "finding", "id": "F001", "status": "dismissed", "reason": "Fixture assertion was wrong", "evidence": "Contract explicitly permits independent operation IDs"})
        complete(s)
        self.assertEqual(g.gate(s)["outcome"], "PASS_WITHIN_SCOPE")

    def test_budget_exhaustion_and_explicit_extension(self):
        s = fresh(mode="repair", max_rounds=1)
        finding(s)
        complete(s)
        self.assertEqual(g.gate(s)["outcome"], "BUDGET_EXHAUSTED")
        with self.assertRaises(g.GauntletError):
            g.apply_event(s, {"type": "next_round", "reason": "more"})
        with self.assertRaises(g.GauntletError):
            g.apply_event(s, {"type": "budget", "max_rounds": 2, "reason": "more"})
        g.apply_event(s, {"type": "budget", "max_rounds": 2, "reason": "New strategy", "approval": "user-message-9"})
        g.apply_event(s, {"type": "next_round", "reason": "Investigate commit boundary"})
        self.assertEqual(s["round"], 2)

    def test_cannot_mutate_closed_round(self):
        s = fresh()
        complete(s)
        with self.assertRaises(g.GauntletError):
            g.apply_event(s, {"type": "target", "revision": "B", "reason": "mutation"})

    def test_new_round_stales_old_checks(self):
        s = fresh(mode="repair", tier="critical")
        complete(s)
        g.apply_event(s, {"type": "next_round", "reason": "new strategy"})
        self.assertTrue(any("stale" in x for x in g.gate(s)["reasons"]))

    def test_add_lens_requires_review_and_resets_clean_round(self):
        s = fresh(mode="repair")
        g.apply_event(s, {"type": "add_lens", "id": "security-privacy", "reason": "Discovered a tenant boundary"})
        self.assertIn("security-privacy", s["tasks"])
        complete(s)
        self.assertFalse(s["rounds"][0]["clean"])

    def test_duplicate_task_rejected(self):
        with self.assertRaises(g.GauntletError):
            g.apply_event(fresh(), {"type": "add_task", "id": "core", "lens": "core", "title": "skip"})

    def test_corrupt_state_rejected(self):
        s = fresh()
        s["round"] = "one"
        with self.assertRaises(g.GauntletError): g.validate_state(s)

    def test_report_includes_evidence_disclaimer(self):
        s = fresh()
        complete(s)
        report = g.report(s)
        self.assertIn("REVIEW_COMPLETE", report)
        self.assertIn("does not execute or authenticate", report)
        self.assertIn("Fixture review result", report)


class DatabaseAndCLITests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.db = self.root / "private" / "gauntlet.sqlite3"
        g.initialize(self.db, fresh())

    def tearDown(self):
        self.temp.cleanup()

    def test_creation_refuses_overwrite(self):
        with self.assertRaises(g.GauntletError): g.initialize(self.db, fresh())

    def test_missing_db_not_created_on_read(self):
        missing = self.root / "missing.sqlite3"
        with self.assertRaises(g.GauntletError): g.read_state(missing)
        self.assertFalse(missing.exists())

    def test_event_batch_atomicity(self):
        before = g.read_state(self.db)
        with self.assertRaises(g.GauntletError):
            g.record(self.db, [{"type": "note", "text": "must roll back"}, {"type": "no-such-event"}])
        self.assertEqual(before, g.read_state(self.db))
        with sqlite3.connect(self.db) as c:
            self.assertEqual(c.execute("SELECT count(*) FROM gauntlet_events").fetchone()[0], 1)

    def test_record_persists_and_audits(self):
        g.record(self.db, {"type": "note", "text": "Documented limitation"})
        self.assertEqual(g.read_state(self.db)["notes"][0]["text"], "Documented limitation")

    def test_symlink_database_rejected(self):
        link = self.root / "link.sqlite3"
        try:
            link.symlink_to(self.db)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable")
        with self.assertRaises(g.GauntletError): g.db_path(str(link))

    def test_concurrent_writers_do_not_lose_updates(self):
        processes = [subprocess.Popen([sys.executable, str(SCRIPT), "record", "--db", str(self.db),
                                       "--event", json.dumps({"type": "note", "text": f"writer-{i}"})],
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for i in range(6)]
        for process in processes:
            out, err = process.communicate(timeout=10)
            self.assertEqual(process.returncode, 0, err)
        self.assertEqual(len(g.read_state(self.db)["notes"]), 6)

    def test_cli_status_and_blocked_exit(self):
        p = subprocess.run([sys.executable, str(SCRIPT), "gate", "--db", str(self.db)], capture_output=True, text=True, timeout=10)
        self.assertEqual(p.returncode, 3)
        self.assertEqual(json.loads(p.stdout)["outcome"], "BLOCKED")

    def test_cli_bad_input_has_no_traceback(self):
        p = subprocess.run([sys.executable, str(SCRIPT), "record", "--db", str(self.db), "--event", "[]"], capture_output=True, text=True, timeout=10)
        self.assertEqual(p.returncode, 2)
        self.assertNotIn("Traceback", p.stderr)

    def test_stdin_event(self):
        p = subprocess.run([sys.executable, str(SCRIPT), "record", "--db", str(self.db), "--input", "-"], input='{"type":"note","text":"stdin"}', capture_output=True, text=True, timeout=10)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(g.read_state(self.db)["notes"][0]["text"], "stdin")

    def test_oversized_input_rejected(self):
        path = self.root / "huge.json"
        path.write_bytes(b" " * (g.MAX_INPUT + 1))
        p = subprocess.run([sys.executable, str(SCRIPT), "record", "--db", str(self.db), "--input", str(path)], capture_output=True, text=True, timeout=10)
        self.assertEqual(p.returncode, 2)
        self.assertIn("exceeds", p.stderr)

    def test_invalid_utf8_rejected(self):
        path = self.root / "bad.json"
        path.write_bytes(b"\xff\xfe")
        p = subprocess.run([sys.executable, str(SCRIPT), "record", "--db", str(self.db), "--input", str(path)], capture_output=True, text=True, timeout=10)
        self.assertEqual(p.returncode, 2)
        self.assertNotIn("Traceback", p.stderr)

    def test_sql_like_text_is_data(self):
        payload = "'); DROP TABLE gauntlet_state; --"
        g.record(self.db, {"type": "note", "text": payload})
        self.assertEqual(g.read_state(self.db)["notes"][0]["text"], payload)

    def test_filename_with_uri_metacharacters(self):
        path = self.root / "spaces ? hash #.sqlite3"
        g.initialize(path, fresh())
        self.assertEqual(g.read_state(path)["scope"], "Fixture only")

    def test_corrupt_sqlite_payload_rejected(self):
        with sqlite3.connect(self.db) as c:
            c.execute("UPDATE gauntlet_state SET payload='{}' WHERE id=1")
        p = subprocess.run([sys.executable, str(SCRIPT), "status", "--db", str(self.db)], capture_output=True, text=True, timeout=10)
        self.assertEqual(p.returncode, 2)
        self.assertIn("schema", p.stderr)
        self.assertNotIn("Traceback", p.stderr)


if __name__ == "__main__":
    unittest.main()
