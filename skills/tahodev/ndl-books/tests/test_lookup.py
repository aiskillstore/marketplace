from pathlib import Path
#!/usr/bin/env python3
"""ndl-books lookup.py の XML パース回帰テスト(ネットワーク不要、fixture使用)。"""
import os, sys, unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import lookup

FIX = os.path.join(os.path.dirname(__file__), "fixtures", "opensearch_title_yukiguni.xml")

class ParseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.total, cls.items = lookup.parse_items(Path(FIX).read_bytes())

    def test_total_and_count(self):
        # 2026-09-29実測: title=雪国&cnt=3 -> totalResults 7719, 3件
        self.assertEqual(self.total, 7719)
        self.assertEqual(len(self.items), 3)

    def test_item_fields(self):
        it = self.items[0]
        self.assertIn("雪国", it["title"])
        self.assertTrue(it["link"].startswith("https://ndlsearch.ndl.go.jp/books/"))
        self.assertIsInstance(it["material"], list)
        self.assertIn("title_yomi", it)

    def test_isbn_hyphen_stripped(self):
        class A: pass
        a = A(); a.isbn = "978-4-10-101001-4"; a.title = None
        a.creator = None; a.keyword = None; a.mediatype = None
        a.cnt = None; a.idx = None
        url = lookup.build_url(a)
        self.assertIn("isbn=9784101010014", url)
        self.assertNotIn("%2D", url)
        self.assertNotIn("-", url.split("isbn=")[1])

if __name__ == "__main__":
    unittest.main()
