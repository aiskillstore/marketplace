import argparse
import csv
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest

MODULE_PATH = Path(__file__).resolve().parents[1] / "lookup.py"
SPEC = importlib.util.spec_from_file_location("shelter_lookup", MODULE_PATH)
lookup = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(lookup)


class ShelterLookupTests(unittest.TestCase):
    def test_haversine_known_distance(self):
        # One degree of longitude at the equator is about 111.2 km.
        self.assertAlmostEqual(lookup.haversine_km(0, 0, 0, 1), 111.195, places=3)

    def test_rejects_nonfinite_input_coordinates(self):
        for value in ("nan", "inf", "-inf"):
            with self.subTest(value=value):
                with self.assertRaises(argparse.ArgumentTypeError):
                    lookup.coordinate(value, -90, 90, "緯度")

    def test_skips_invalid_site_coordinates(self):
        headers = ["施設・場所名", "洪水", "緯度", "経度"]
        rows = [
            ["nan site", "1", "nan", "139"],
            ["infinite site", "1", "35", "inf"],
            ["out of range", "1", "91", "139"],
            ["valid", "1", "35.01", "139"],
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sites.csv"
            with path.open("w", encoding="utf-8-sig", newline="") as target:
                writer = csv.writer(target)
                writer.writerow(headers)
                writer.writerows(rows)
            results = lookup.nearest_sites(path, 35, 139, "洪水", 20)
        self.assertEqual([row["施設・場所名"] for _, row in results], ["valid"])

    def test_filters_hazard_sorts_and_limits(self):
        headers = ["施設・場所名", "洪水", "地震", "緯度", "経度"]
        rows = [
            ["far", "1", "", "35.1", "139"],
            ["wrong hazard", "", "1", "35.001", "139"],
            ["near", "1", "", "35.01", "139"],
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sites.csv"
            with path.open("w", encoding="utf-8-sig", newline="") as target:
                writer = csv.writer(target)
                writer.writerow(headers)
                writer.writerows(rows)
            results = lookup.nearest_sites(path, 35, 139, "洪水", 1)
        self.assertEqual(results[0][1]["施設・場所名"], "near")


    def test_stale_caches_flags_only_old_files(self):
        with tempfile.TemporaryDirectory() as directory:
            fresh = Path(directory) / "fresh.csv"
            old = Path(directory) / "old.csv"
            missing = Path(directory) / "missing.csv"
            fresh.write_text("x", encoding="utf-8")
            old.write_text("x", encoding="utf-8")
            old_epoch = 1_700_000_000
            os.utime(old, (old_epoch, old_epoch))
            os.utime(fresh, (old_epoch + 9 * 86400, old_epoch + 9 * 86400))
            stale = lookup.stale_caches([fresh, old, missing], 7, now=old_epoch + 10 * 86400)
        self.assertEqual([(p.name, age) for p, age in stale], [("old.csv", 10)])


if __name__ == "__main__":
    unittest.main()
