import json, sys, unittest
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
import lookup  # noqa: E402

F = HERE / 'fixtures'


def read(name):
    return (F / name).read_text(encoding='utf-8')


class GeocodeTest(unittest.TestCase):
    def test_exact_facility_is_last_in_raw_response(self):
        raw = json.loads(read('geocode_tokyotower.json'))
        self.assertEqual(len(raw), 50)
        self.assertEqual(raw[0]['properties']['title'], '北海道札幌市東区')
        self.assertEqual(raw[-1]['properties']['title'], '東京タワー')

    def test_prefix_match_sorted_first_and_ambiguity_flagged(self):
        out = lookup.parse_geocode(read('geocode_tokyotower.json'), '東京タワー', limit=2)
        self.assertEqual(out['total'], 50)
        self.assertEqual(out['results'][0]['title'], '東京タワー')
        self.assertTrue(out['results'][0]['prefix_match'])
        self.assertIn('曖昧', out['note'])
        self.assertAlmostEqual(out['results'][0]['lat'], 35.658, places=2)

    def test_empty_result(self):
        out = lookup.parse_geocode(read('geocode_empty.json'), 'zzzzqqqq')
        self.assertEqual(out['total'], 0)
        self.assertIn('該当なし', out['note'])

    def test_norm_fullwidth_digits(self):
        self.assertEqual(lookup.norm('千代田１番'), '千代田1番')


class ElevationTest(unittest.TestCase):
    def test_value(self):
        out = lookup.parse_elevation(read('elev_tokyo.json'))
        self.assertEqual(out['elevation_m'], 3.6)
        self.assertEqual(out['source'], '1m（レーザ）')

    def test_no_data_is_string_dashes_not_error(self):
        raw = json.loads(read('elev_sea.json'))
        self.assertEqual(raw['elevation'], '-----')
        out = lookup.parse_elevation(read('elev_sea.json'))
        self.assertIsNone(out['elevation_m'])


class ReverseTest(unittest.TestCase):
    def setUp(self):
        self.muni = lookup.parse_muni_js(read('muni_excerpt.js'))

    def test_hokkaido_code_has_leading_zero_but_muni_key_does_not(self):
        self.assertEqual(json.loads(read('rev_sapporo.json'))['results']['muniCd'], '01101')
        self.assertNotIn('01101', self.muni)
        self.assertIn('1101', self.muni)
        out = lookup.parse_reverse(read('rev_sapporo.json'), self.muni)
        self.assertEqual(out['address'], '北海道札幌市中央区北一条西二丁目')

    def test_tokyo(self):
        out = lookup.parse_reverse(read('rev_shiba.json'), self.muni)
        self.assertEqual(out['address'], '東京都港区芝公園四丁目')

    def test_empty_object_means_no_data(self):
        self.assertEqual(read('rev_london.json').strip(), '{}')
        out = lookup.parse_reverse(read('rev_london.json'), self.muni)
        self.assertIsNone(out['address'])

    def test_unknown_muni_code(self):
        out = lookup.parse_reverse('{"results":{"muniCd":"99999","lv01Nm":"x"}}', self.muni)
        self.assertIn('note', out)


if __name__ == '__main__':
    unittest.main()
