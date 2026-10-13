#!/usr/bin/env python3
"""egov-laws lookup.py のパース・条番号解釈・エラー処理の回帰テスト(ネットワーク不要、fixture使用)。
fixtureは2026-10-02に実APIから取った民法の本則から第1,2,3,3の2,4,709,770条だけを残したもの。"""
import json, os, sys, unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import lookup

FIX = os.path.join(os.path.dirname(__file__), "fixtures")

def load(name):
    with open(os.path.join(FIX, name), encoding="utf-8") as f:
        return json.load(f)

class ArticleNumTest(unittest.TestCase):
    def test_plain_and_branch(self):
        self.assertEqual(lookup.parse_article_num("709"), "709")
        self.assertEqual(lookup.parse_article_num("3の2"), "3_2")
        self.assertEqual(lookup.parse_article_num("3-2"), "3_2")
        self.assertEqual(lookup.parse_article_num("３"), "3")  # 全角数字

    def test_invalid(self):
        with self.assertRaises(SystemExit):
            lookup.parse_article_num("第七百九条")

class FindArticleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.law = load("minpo_mini.json")["law_full_text"]

    def test_by_num_not_by_index(self):
        # 実測: 本物の民法では Article[709] は第643条を返す(N番目の要素 != 第N条)。
        # ここでは Num 属性で探すので、709を指定すれば第709条が返る
        art, idx, total = lookup.find_article(self.law, "709")
        self.assertEqual(art["attr"]["Num"], "709")
        self.assertEqual(total, 7)

    def test_branch_shifts_index(self):
        # 3の2があるせいで第4条は4番目ではなく5番目の要素になる(2026-10-02実測と同じ構造)
        art, idx, _ = lookup.find_article(self.law, "4")
        self.assertEqual(idx, 5)  # fixtureは 1,2,3,3_2,4 の順 -> 第4条は5番目の要素

    def test_missing(self):
        art, idx, _ = lookup.find_article(self.law, "2000")
        self.assertIsNone(art)

class RenderTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.law = load("minpo_mini.json")["law_full_text"]

    def test_caption_and_body(self):
        art, _, _ = lookup.find_article(self.law, "4")
        t = lookup.render_article(art)
        self.assertIn("（成年）", t)
        self.assertIn("年齢十八歳をもって、成年とする。", t)

    def test_items_are_indented(self):
        art, _, _ = lookup.find_article(self.law, "770")
        lines = lookup.render_article(art).split("\n")
        self.assertTrue(any(l.startswith("  一") for l in lines))

class ResolveTest(unittest.TestCase):
    def test_exact_title_wins_over_partial(self):
        # 実測: law_title=民法 は部分一致で11件(民法施行法 ほか)。完全一致を選ぶ
        with mock.patch.object(lookup, "fetch_json", return_value=load("laws_minpo.json")):
            self.assertEqual(lookup.resolve_law("民法"), "129AC0000000089")

    def test_law_id_passthrough(self):
        self.assertEqual(lookup.resolve_law("321CONSTITUTION"), "321CONSTITUTION")

    def test_ambiguous_stops(self):
        with mock.patch.object(lookup, "fetch_json", return_value=load("laws_minpo.json")):
            with self.assertRaises(SystemExit):
                lookup.resolve_law("特例")

class RevisionsAndErrorsTest(unittest.TestCase):
    def test_status_values_present(self):
        d = load("revisions_minpo.json")
        st = {r["current_revision_status"] for r in d["revisions"]}
        self.assertEqual(st, {"PreviousEnforced", "UnEnforced"})  # 実測: 民法に CurrentEnforced は無い

    def test_error_shapes(self):
        # 実測: asof < 2017-04-01 は HTTP 400 + このJSON。エラーは {"code","message"} で law_info を持たない
        e = load("error_asof.json")
        self.assertEqual(e["code"], "400044")
        self.assertIn("2017-04-01", e["message"])
        e2 = load("error_elm.json")
        self.assertEqual(e2["code"], "400021")

if __name__ == "__main__":
    unittest.main()
