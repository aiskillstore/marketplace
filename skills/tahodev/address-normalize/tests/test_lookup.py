import importlib.util, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("addr_lookup", ROOT / "lookup.py")
lookup = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(lookup)

FIX = ROOT / "tests" / "fixtures"
import csv as _csv
def load(name):
    with open(FIX / name, encoding="utf-8") as f:
        return list(_csv.DictReader(f))
PREFS = load("mt_pref_all.csv")
CITIES = load("mt_city_all.csv")
TOWNS = load("mt_town_pref13.csv")

def towns_by_pref(pref_row):
    return TOWNS

class AddressNormalizeTests(unittest.TestCase):
    def parse(self, s):
        return lookup.parse_address(s, PREFS, CITIES, towns_by_pref)

    def test_full_address(self):
        pref, city, town, rest = self.parse("東京都千代田区内幸町1丁目1-1")
        self.assertEqual(pref["pref"], "東京都")
        self.assertEqual(city["lg_code"], "131016")
        self.assertEqual(town["machiaza_id"], "0001001")
        self.assertEqual(rest, "1-1")

    def test_chome_kanji_variant(self):
        # データは全角「１丁目」でも入力の漢数字「一丁目」に一致する
        pref, city, town, rest = self.parse("新宿区歌舞伎町一丁目4-1")
        self.assertIsNotNone(pref)  # 市区から都道府県を補う
        self.assertEqual(pref["pref"], "東京都")
        self.assertEqual(town["oaza_cho"], "歌舞伎町")
        self.assertEqual(rest, "4-1")

    def test_chome_missing_is_not_matched(self):
        # 丁目つき町字に丁目なしの入力は誤爆させない
        _, _, town, _ = self.parse("東京都千代田区内幸町")
        self.assertIsNone(town)

    def test_kanji_num(self):
        self.assertEqual(lookup.kanji_num(1), "一")
        self.assertEqual(lookup.kanji_num(10), "十")
        self.assertEqual(lookup.kanji_num(23), "二十三")

    def test_canon_is_length_preserving(self):
        self.assertEqual(lookup.canon("北一条西２丁目"), "北1条西2丁目")
        self.assertEqual(len(lookup.canon("北一条西")), len("北一条西"))

if __name__ == "__main__":
    unittest.main()
