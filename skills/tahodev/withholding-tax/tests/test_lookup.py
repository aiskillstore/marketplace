#!/usr/bin/env python3
"""withholding-tax lookup.py の回帰テスト(ネットワーク不要)。
期待値は国税庁「電算機計算の特例について」PDFに載っている公式の計算例(令和8年分・令和9年分、2026-10-03確認)。"""
import os, sys, unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import lookup as calc

class OfficialExamplesTest(unittest.TestCase):
    def test_r8_175000_two_dependents(self):
        # 公式例: 175,000円・配偶者+親族1人 -> 特例210円 (税額表は250円)
        self.assertEqual(calc.calc(175000, 2, 2026)["tax"], 210)

    def test_r8_446000_eight_dependents(self):
        # 公式例: 446,000円・配偶者+親族7人 -> 特例940円 (税額表は1,010円)
        self.assertEqual(calc.calc(446000, 8, 2026)["tax"], 940)

    def test_r8_775200_three_dependents(self):
        # 公式例: 775,200円・配偶者+親族2人 -> 特例59,470円 (税額表は59,477円)
        self.assertEqual(calc.calc(775200, 3, 2026)["tax"], 59470)

    def test_r9_177000_two_dependents(self):
        # 令和9年分の公式例: 177,000円・配偶者+親族1人 -> 特例110円 (税額表は150円)
        self.assertEqual(calc.calc(177000, 2, 2027)["tax"], 110)

class PiecesTest(unittest.TestCase):
    def test_kyuyo_kojo_bands(self):
        self.assertEqual(calc.kyuyo_kojo(100000, 2026), 54167)
        self.assertEqual(calc.kyuyo_kojo(175000, 2026), 59167)   # 175,000x30%+6,667
        self.assertEqual(calc.kyuyo_kojo(800000, 2026), 162500)

    def test_year_specific_constants(self):
        # 令和9年分から給与所得控除の下限と基礎控除が上がる(2026-10-03実測)
        self.assertEqual(calc.kyuyo_kojo(100000, 2027), 57500)
        self.assertEqual(calc.kiso_kojo(300000, 2026), 48334)
        self.assertEqual(calc.kiso_kojo(300000, 2027), 51667)

    def test_kiso_phaseout(self):
        self.assertEqual(calc.kiso_kojo(2120834, 2026), 40000)
        self.assertEqual(calc.kiso_kojo(2245834, 2026), 0)

    def test_rounding_to_10_yen(self):
        # 課税給与所得金額がちょうど4,125円: 4125x5.105%=210.58 -> 210
        self.assertEqual(calc.tax_from_taxable(4125), 210)
        self.assertEqual(calc.tax_from_taxable(0), 0)
        self.assertEqual(calc.tax_from_taxable(-5000), 0)

class InputTest(unittest.TestCase):
    def test_unsupported_year(self):
        with self.assertRaises(ValueError):
            calc.calc(300000, 0, 2025)

    def test_negative(self):
        with self.assertRaises(ValueError):
            calc.calc(-1, 0, 2026)

if __name__ == "__main__":
    unittest.main()
