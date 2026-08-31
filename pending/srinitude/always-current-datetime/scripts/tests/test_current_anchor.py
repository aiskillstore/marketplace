"""Behavior tests for the bundled current-date anchor script."""
import json
import os
import pathlib
import subprocess
import sys
import unittest
from datetime import date, timedelta

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = SKILL_DIR / "scripts" / "current_anchor.py"


def run_anchor(*arguments, timezone_marker="missing"):
    environment = os.environ.copy()
    environment.pop("PROFILE_TIMEZONE", None)
    if timezone_marker != "missing":
        environment["PROFILE_TIMEZONE"] = timezone_marker
    return subprocess.run(
        [sys.executable, str(SCRIPT), *arguments],
        capture_output=True,
        check=False,
        env=environment,
        text=True,
    )


class TestCurrentAnchor(unittest.TestCase):
    def test_help_is_available_without_emitting_json(self):
        result = run_anchor("--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("usage:", result.stdout)
        self.assertNotIn('"captured_at"', result.stdout)

    def test_profile_timezone_produces_one_complete_utc_record(self):
        result = run_anchor(timezone_marker="UTC")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(result.stdout.rstrip("\n").splitlines()), 1)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["source"], "profile-environment")
        self.assertEqual(payload["timezone"], "UTC")
        self.assertEqual(payload["utc_offset"], "+00:00")
        anchor = date.fromisoformat(payload["date"])
        self.assertEqual(payload["yesterday"], (anchor - timedelta(days=1)).isoformat())
        self.assertEqual(payload["tomorrow"], (anchor + timedelta(days=1)).isoformat())

    def test_explicit_timezone_overrides_profile_environment(self):
        result = run_anchor("--timezone", "UTC", timezone_marker="Asia/Tokyo")
        payload = json.loads(result.stdout)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(payload["source"], "argument")
        self.assertEqual(payload["timezone"], "UTC")

    def test_system_local_timezone_is_the_final_fallback(self):
        result = run_anchor()
        payload = json.loads(result.stdout)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(payload["source"], "system-local")
        self.assertTrue(payload["timezone"])
        self.assertTrue(payload["zone_abbreviation"])

    def test_invalid_timezone_fails_without_stdout(self):
        result = run_anchor(timezone_marker="Not/A_Zone")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("current_anchor_error: ZoneInfoNotFoundError:", result.stderr)
        self.assertIn("Not/A_Zone", result.stderr)

    def test_record_contains_the_full_temporal_schema(self):
        result = run_anchor(timezone_marker="UTC")
        payload = json.loads(result.stdout)
        expected = {
            "captured_at", "date", "source", "time", "timezone",
            "tomorrow", "utc_offset", "weekday", "yesterday",
            "zone_abbreviation",
        }
        self.assertEqual(set(payload), expected)
        self.assertRegex(payload["date"], r"^\d{4}-\d{2}-\d{2}$")
        self.assertRegex(payload["time"], r"^\d{2}:\d{2}:\d{2}$")


if __name__ == "__main__":
    unittest.main()
