#!/usr/bin/env python3
"""score.py prints one URL, one offer, and one action, or refuses a sitemap."""

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


class ScorePage(unittest.TestCase):
    def test_good_draft_prints_three(self):
        result = run(["--file", str(ROOT / "examples" / "page-good.json")])
        self.assertEqual(result.returncode, 0)
        self.assertIn("url: https://example.com/desk", result.stdout)
        self.assertIn("offer: A one-page desk that names the week's leak.", result.stdout)
        self.assertIn("action: Read the page and reply with the one number you want next.", result.stdout)
        self.assertNotIn("a sitemap", result.stdout)

    def test_sitemap_exits_1(self):
        result = run(["--file", str(ROOT / "examples" / "page-sitemap.json")])
        self.assertEqual(result.returncode, 1)
        self.assertIn("a sitemap", result.stdout)
        self.assertNotIn("url:", result.stdout)

    def test_bad_json_hides_input(self):
        bad = run(["--stdin"], stdin='{"url": "' + CELL)
        self.assertNotEqual(bad.returncode, 0)
        self.assertNotIn(CELL, bad.stdout + bad.stderr)
        self.assertIn("invalid JSON", bad.stderr)
        array = run(["--stdin"], stdin='["' + CELL + '"]')
        self.assertNotEqual(array.returncode, 0)
        self.assertNotIn(CELL, array.stdout + array.stderr)
        self.assertIn("JSON must be an object", array.stderr)


if __name__ == "__main__":
    unittest.main()
