import csv, importlib.util, io, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("air_quality_lookup", ROOT / "lookup.py")
lookup = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(lookup)

ROWS = list(csv.reader(io.StringIO((ROOT / "tests" / "fixtures" / "noudoAll.csv").read_text(encoding="utf-8"))))
HDR, DATA = ROWS[0], ROWS[1:]

class AirQualityLookupTests(unittest.TestCase):
    def test_top_by_value(self):
        hit = lookup.select_hits(HDR, DATA, "PM2.5")
        self.assertEqual(hit[0][0], 28.0)  # 国設尼崎が最大
        self.assertIsNone(hit[-1][0])      # '-' (未測定) は末尾

    def test_keyword_filter(self):
        hit = lookup.select_hits(HDR, DATA, "PM2.5", keyword="尼崎")
        self.assertEqual(len(hit), 1)
        self.assertEqual(hit[0][0], 28.0)

    def test_pref_filter_zerofill(self):
        hit = lookup.select_hits(HDR, DATA, "PM2.5", pref="1")
        self.assertEqual(len(hit), 1)  # 01=北海道にゼロ埋め
        self.assertEqual(hit[0][1][HDR.index("市区町村名")], "札幌市")

    def test_station_exact(self):
        hit = lookup.select_hits(HDR, DATA, "PM2.5", station="13101010")
        self.assertEqual(hit[0][0], 7.0)

if __name__ == "__main__":
    unittest.main()
