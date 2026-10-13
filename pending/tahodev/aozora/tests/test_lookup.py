from pathlib import Path
#!/usr/bin/env python3
"""aozora lookup.py のパース回帰テスト(ネットワーク不要、fixture使用)。"""
import os, sys, unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import lookup

FIX = os.path.join(os.path.dirname(__file__), "fixtures")
CSV = os.path.join(FIX, "list_sample_utf8.csv")

class CsvTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = lookup.load_rows(CSV)

    def test_bom_handled(self):
        # utf-8-sig で読むので先頭列名にBOMが残らない
        self.assertIn("作品ID", self.rows[0])

    def test_rows_vs_works(self):
        # 1作品=複数行(著者+翻訳者)なので行数>作品数 (2026-09-30実測 19,502行/17,840作品)
        st = lookup.cmd_stats(self.rows)
        self.assertEqual(st["rows"], 5)
        self.assertEqual(st["distinct_works"], 4)
        self.assertEqual(st["copyrighted_works"], 1)  # 走れメロス(太宰)は著作権あり

    def test_author_search_concatenated_name(self):
        hits = [r for r in self.rows if (r["姓"] + r["名"]) == "夏目漱石" and r["役割フラグ"] == "著者"]
        self.assertEqual(len(hits), 2)

class CardTest(unittest.TestCase):
    def test_card_links(self):
        html = Path(FIX, "card789.html").read_text(encoding="utf-8")
        links = lookup.parse_card_links(html)
        # 2026-09-30実測: 本文URLの通し番号(14547)は作品ID(789)から推測不可。カードを読んで拾う
        self.assertEqual(links["text_html"], "files/789_14547.html")
        self.assertEqual(links["ruby_zip"], "files/789_ruby_5639.zip")
        self.assertEqual(links["ebk"], "files/789.ebk")

class TextTest(unittest.TestCase):
    def test_shift_jis_and_ruby(self):
        raw = Path(FIX, "text789_sample.html").read_bytes()
        text = lookup.extract_text(raw)
        # ルビは基底文字のみ残り、読み(わがはい)と<rp>の括弧は消える
        self.assertIn("吾輩は猫である。名前はまだ無い。", text)
        self.assertIn("見当がつかぬ", text)
        self.assertNotIn("わがはい", text)
        self.assertNotIn("（）", text)
        self.assertNotIn("<", text)

    def test_detect_encoding(self):
        sj = '<?xml version="1.0" encoding="Shift_JIS"?><meta charset="Shift_JIS">'.encode("ascii")
        self.assertEqual(lookup.detect_encoding(sj), "shift_jis")
        u8 = '<html><head><meta charset="utf-8"></head>'.encode("ascii")
        self.assertEqual(lookup.detect_encoding(u8), "utf-8")
        none_ = b"<html><body>plain</body></html>"
        self.assertEqual(lookup.detect_encoding(none_), "shift_jis")  # 青空文庫本文の既定

if __name__ == "__main__":
    unittest.main()
