#!/usr/bin/env python3
"""score.py prints a lifecycle sequence or refuses a generic drip and a cold email."""

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CELL = "super-secret-cell"


def run(args, stdin=None):
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "score.py"), *args],
        input=stdin,
        capture_output=True,
        text=True,
    )


class ScoreLifecycle(unittest.TestCase):
    def test_good_draft_prints_three(self):
        result = run(["--file", str(ROOT / "examples" / "lifecycle-good.json")])
        self.assertEqual(result.returncode, 0)
        self.assertIn("welcome: You asked for the trial checklist.", result.stdout)
        self.assertIn("bargain: The checklist is the bargain.", result.stdout)
        self.assertIn("nurture: The next note stays on the pain you showed: the trial dies after the first login.", result.stdout)

    def test_refused_exits_1(self):
        result = run(["--file", str(ROOT / "examples" / "lifecycle-refused.json")])
        self.assertEqual(result.returncode, 1)
        self.assertIn("a generic drip and a cold email", result.stdout)
        self.assertNotIn("welcome:", result.stdout)

    def test_bad_json_hides_input(self):
        bad = run(["--stdin"], stdin='{"welcome": "' + CELL)
        self.assertNotEqual(bad.returncode, 0)
        self.assertNotIn(CELL, bad.stdout + bad.stderr)
        self.assertIn("invalid JSON", bad.stderr)
        array = run(["--stdin"], stdin='["' + CELL + '"]')
        self.assertNotEqual(array.returncode, 0)
        self.assertNotIn(CELL, array.stdout + array.stderr)
        self.assertIn("JSON must be an object", array.stderr)


if __name__ == "__main__":
    unittest.main()
