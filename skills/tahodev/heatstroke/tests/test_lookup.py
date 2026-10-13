import importlib.util, json, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("heatstroke_lookup", ROOT / "lookup.py")
lookup = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(lookup)

FIX = ROOT / "tests" / "fixtures"

class HeatstrokeLookupTests(unittest.TestCase):
    def test_master_space_padded_header(self):
        # 本物のマスタCSVは ", " 区切りで項目名に空白が入る
        stations = lookup.load_stations(str(FIX / "wbgt_point_master.csv"))
        self.assertEqual(len(stations), 2)
        tokyo = [s for s in stations if s["no"] == "44132"][0]
        self.assertEqual(tokyo["name"], "東京")
        self.assertAlmostEqual(tokyo["lat"], 35 + 41.4 / 60, places=4)
        self.assertTrue(tokyo["measured"])

    def test_forecast_tenths_and_levels(self):
        data = json.loads((FIX / "forecast.json").read_text())["data"]
        v1 = int(data[0]["forecast_val"]) / 10
        v2 = int(data[1]["forecast_val"]) / 10
        self.assertEqual(v1, 21.0)
        self.assertEqual(lookup.level(v1), "注意")
        self.assertEqual(lookup.level(v2), "厳重警戒")  # 28.5 -> 厳重警戒(28-31)

    def test_level_boundaries(self):
        self.assertEqual(lookup.level(31.0), "危険")
        self.assertEqual(lookup.level(30.9), "厳重警戒")
        self.assertEqual(lookup.level(28.0), "厳重警戒")
        self.assertEqual(lookup.level(25.0), "警戒")
        self.assertEqual(lookup.level(21.0), "注意")
        self.assertEqual(lookup.level(20.9), "ほぼ安全")

    def test_latest_announcement_slots(self):
        import datetime
        n = datetime.datetime(2026, 9, 26, 12, 30)
        self.assertEqual(lookup.latest_announcement(n), "20260926110000")
        n2 = datetime.datetime(2026, 9, 26, 4, 59)
        self.assertEqual(lookup.latest_announcement(n2), "20260925170000")

    def test_nearest_station(self):
        stations = lookup.load_stations(str(FIX / "wbgt_point_master.csv"))
        s = lookup.nearest(stations, 35.6895, 139.6917)  # 新宿
        self.assertEqual(s["no"], "44132")

if __name__ == "__main__":
    unittest.main()
