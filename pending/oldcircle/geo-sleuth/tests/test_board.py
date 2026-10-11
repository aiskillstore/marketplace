#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Offline board regressions. Run: uv run skills/geo-sleuth/tests/test_board.py"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import board  # noqa: E402


class CorridorPendingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.path = self.root / "board.json"
        self.output = self.root / "scan.json"
        self.output.write_text('{"hits": []}', encoding="utf-8")
        self.run_board("init", "--photo", "photo.jpg")

    def run_board(self, *args, ok=True):
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / "board.py"), "--board", str(self.path), *args],
            cwd=self.root, capture_output=True, text=True, encoding="utf-8",
        )
        if ok:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def read_board(self):
        return json.loads(self.path.read_text(encoding="utf-8"))

    def clue(self, kind="infra", status="observed", *extra):
        self.run_board("clue", "A spatial observation or its computed test", "--kind", kind,
                       "--status", status, *extra)

    def pending(self):
        return board._corridor_pending(self.read_board())

    def test_alias_is_normalized_when_recorded(self):
        self.clue("infrastructure")
        self.assertEqual(self.read_board()["clues"]["K1"]["kind"], "infra")
        self.assertEqual(self.pending(), ["K1"])
        self.assertIn("infrastructure clue K1", self.run_board("next").stdout)

    def test_legacy_alias_is_detected_without_rewriting_board(self):
        self.clue()
        data = self.read_board()
        data["clues"]["K1"]["kind"] = "infrastructure"
        self.path.write_text(json.dumps(data), encoding="utf-8")
        before = self.path.read_bytes()
        self.assertEqual(self.pending(), ["K1"])
        self.assertIn("infrastructure clue K1", self.run_board("next").stdout)
        self.assertEqual(self.path.read_bytes(), before)

    def test_unlinked_computations_do_not_clear_infrastructure(self):
        self.clue()
        self.clue("infrastructure", "read")
        for kind in ("terrain", "corridor", "infra"):
            with self.subTest(kind=kind):
                self.clue(kind, "computed", "--file", str(self.output))
                self.assertEqual(self.pending(), ["K1", "K2"])

    def test_computation_clears_only_explicitly_linked_clues(self):
        self.clue()
        self.clue("infrastructure", "read")
        self.clue("terrain", "computed", "--file", str(self.output), "--resolves", "K1")
        self.assertEqual(self.pending(), ["K2"])
        self.assertIn("infrastructure clue K2", self.run_board("next").stdout)
        self.assertEqual(self.read_board()["clues"]["K3"]["resolves"], ["K1"])
        self.clue("corridor", "computed", "--file", str(self.output),
                  "--resolves", "K1", "--resolves", "K2")
        self.assertEqual(self.pending(), [])
        self.assertNotIn("infrastructure clue", self.run_board("next").stdout)
        # Recording a computation is separate from scoring candidate evidence.
        self.assertEqual(self.read_board()["evidence"], [])

    def test_unrelated_explicit_link_does_not_clear_infrastructure(self):
        self.clue()
        self.clue("terrain")
        self.clue("terrain", "computed", "--file", str(self.output), "--resolves", "K2")
        self.assertEqual(self.pending(), ["K1"])

    def test_invalid_completion_is_rejected_without_mutation(self):
        self.clue()
        before = self.path.read_bytes()
        cases = [
            ("--status", "observed", "--file", str(self.output), "--resolves", "K1"),
            ("--status", "computed", "--file", str(self.output), "--resolves", "K99"),
            ("--status", "computed", "--file", str(self.output), "--resolves", "K1", "--resolves", "K99"),
            ("--status", "computed", "--resolves", "K1"),
            ("--status", "computed", "--file", str(self.root / "missing.json"), "--resolves", "K1"),
            ("--status", "computed", "--file", str(self.root), "--resolves", "K1"),
        ]
        for args in cases:
            with self.subTest(args=args):
                self.run_board("clue", "An invalid completion", "--kind", "terrain", *args, ok=False)
                self.assertEqual(self.path.read_bytes(), before)

    def test_missing_output_no_longer_counts_as_completion(self):
        self.clue()
        self.clue("terrain", "computed", "--file", str(self.output), "--resolves", "K1")
        self.assertEqual(self.pending(), [])
        self.output.unlink()
        self.assertEqual(self.pending(), ["K1"])

    def test_relative_output_link_survives_a_different_working_directory(self):
        self.clue()
        self.clue("terrain", "computed", "--file", "scan.json", "--resolves", "K1")
        saved = self.read_board()["clues"]["K2"]["file"]
        self.assertEqual(Path(saved), self.output.resolve())
        self.assertEqual(self.pending(), [])
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / "board.py"), "--board", str(self.path), "next"],
            cwd=self.root.parent, capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("infrastructure clue", result.stdout)


class LevelGapTests(unittest.TestCase):
    """A point added under the city instead of under its road: its evidence never reached the road ranking, and report named another road."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.path = self.root / "board.json"
        (self.root / "match.jpg").write_bytes(b"x")
        (self.root / "evidence.jpg").write_bytes(b"x")
        run = CorridorPendingTests.run_board
        self.run_board = lambda *a, ok=True: run(self, *a, ok=ok)
        self.run_board("init", "--photo", "photo.jpg")
        self.run_board("add", "City", "--level", "district")
        self.run_board("add", "A ST 100", "--level", "road", "--parent", "City", "--bbox", "49.20,-123.20,49.201,-123.19")
        self.run_board("add", "B ST 200", "--level", "road", "--parent", "City", "--bbox", "49.21,-123.20,49.211,-123.19")
        self.run_board("clue", "street view matches", "--kind", "municipal", "--status", "computed", "--file", "match.jpg")
        self.run_board("evidence", "--clue", "K1", "--for", "A ST 100:2", "--why", "partial", "--file", "match.jpg")

    def add_point(self, *extra):
        out = self.run_board("add", "spot", "--level", "point", "--parent", "City", "--bbox", "49.2159,-123.1095,49.2162,-123.1091", *extra)
        self.run_board("evidence", "--clue", "K1", "--for", "spot:10", "--why", "invariant features", "--file", "match.jpg")
        return out

    def ranking(self):
        return [r["name"] for r in board._scores(json.loads(self.path.read_text(encoding="utf-8")), "road", "uniform")]

    def test_skipped_level_is_flagged_everywhere(self):
        self.assertIn("2 road candidates", self.add_point().stdout)
        check = self.run_board("check")
        self.assertIn("FAIL spot (point) sits directly under City", check.stdout)
        self.assertIn("leaves the answer out", check.stdout)
        result = self.root / "result.json"
        result.write_text(json.dumps({"lat": 49.216, "lon": -123.1093, "radius_m": 20}), encoding="utf-8")
        report = self.run_board("report", "--merge", str(result)).stdout
        self.assertIn("outside the board's main answer A ST 100", report)
        self.assertTrue(json.loads(result.read_text(encoding="utf-8"))["board"]["level_gaps"])

    def test_moving_under_its_road_carries_support_up(self):
        self.add_point()
        self.run_board("add", "W 60 AVE 100", "--level", "road", "--parent", "City", "--bbox", "49.2158,-123.1112,49.2164,-123.1075")
        self.assertIn("lies inside W 60 AVE 100", self.run_board("check", ok=True).stdout)
        self.run_board("move", "spot", "--parent", "W 60 AVE 100")
        check = self.run_board("check").stdout
        self.assertNotIn("FAIL", check)
        self.assertIn("main answer W 60 AVE 100", check)
        self.assertEqual(self.ranking()[0], "W 60 AVE 100")
        result = self.root / "result.json"
        result.write_text(json.dumps({"lat": 49.216, "lon": -123.1093}), encoding="utf-8")
        self.assertNotIn("WARN", self.run_board("report", "--merge", str(result)).stdout)

    def test_against_on_a_point_does_not_reach_its_road(self):
        self.run_board("add", "spot2", "--level", "point", "--parent", "B ST 200")
        before = self.ranking()
        self.run_board("evidence", "--clue", "K1", "--against", "spot2:0.1", "--why", "no match", "--file", "match.jpg")
        self.assertEqual(self.ranking(), before)
        b = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual(board._inherited(b, "B ST 200", set()), [])

    def test_same_clue_counts_once(self):
        self.run_board("add", "spot3", "--level", "point", "--parent", "A ST 100")
        self.run_board("evidence", "--clue", "K1", "--for", "spot3:10", "--why", "same clue", "--file", "match.jpg")
        b = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual(board._inherited(b, "A ST 100", {"K1"}), [])   # A ST 100 already has its own K1 evidence

    def test_move_rejects_finer_parent(self):
        self.run_board("add", "spot4", "--level", "point", "--parent", "A ST 100")
        self.run_board("move", "A ST 100", "--parent", "spot4", ok=False)


if __name__ == "__main__":
    unittest.main()
