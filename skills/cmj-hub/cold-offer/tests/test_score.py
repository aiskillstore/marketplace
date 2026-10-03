#!/usr/bin/env python3
"""score.py prints a cold offer or refuses email one that sells the paid product."""

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


class ScoreColdOffer(unittest.TestCase):
    def test_good_draft_prints_three(self):
        result = run(["--file", str(ROOT / "examples" / "offer-good.json")])
        self.assertEqual(result.returncode, 0)
        self.assertIn("leak: The homepage asks for a meeting before it shows any work.", result.stdout)
        self.assertIn("prototype: A one-page sample that leads with one finding", result.stdout)
        self.assertIn("email one: Your homepage asks for a meeting before it shows any work.", result.stdout)
        self.assertNotIn("email one that sells the paid product", result.stdout)

    def test_sell_exits_1(self):
        result = run(["--file", str(ROOT / "examples" / "offer-sells.json")])
        self.assertEqual(result.returncode, 1)
        self.assertIn("email one that sells the paid product", result.stdout)
        self.assertNotIn("leak:", result.stdout)

    def test_bad_json_hides_input(self):
        bad = run(["--stdin"], stdin='{"email_one": "' + CELL)
        self.assertNotEqual(bad.returncode, 0)
        self.assertNotIn(CELL, bad.stdout + bad.stderr)
        self.assertIn("invalid JSON", bad.stderr)
        array = run(["--stdin"], stdin='["' + CELL + '"]')
        self.assertNotEqual(array.returncode, 0)
        self.assertNotIn(CELL, array.stdout + array.stderr)
        self.assertIn("JSON must be an object", array.stderr)


if __name__ == "__main__":
    unittest.main()
