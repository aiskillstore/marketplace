#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Offline regressions for region packs and country context. Run: uv run skills/geo-sleuth/tests/test_regions.py"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SKILL = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL / "scripts"
sys.path.insert(0, str(SCRIPTS))
import regions  # noqa: E402

# A fake second country whose area code 020 collides with China's, and whose 0120 covers two districts
FIXTURE = {
    "region.json": {"code": "QQ", "name": "Testland", "names": ["Testland", "TL"], "status": "community", "docs": ["clues.md"],
                    "admin_levels": {"1": "admin1", "2": "admin2"},
                    "lookups": {"area-code": {"file": "data/area_codes.json"}}},
    "data/area_codes.json": {"_meta": {"kind": "area-code", "source": ["https://example.org/codes"], "fetched": "2026-10-08",
                                       "license": "CC0", "count": 3, "normalize": {"digits_only": True, "ensure_prefix": "0"}},
                             "entries": {"020": [{"admin1": "North", "admin2": "Porta"}],
                                         "0120": [{"admin1": "North", "admin2": "Alda"}, {"admin1": "North", "admin2": "Brin"}],
                                         "0431": [{"admin1": "吉林省", "admin2": "长春市", "district": "朝阳区"}]}},
    "tests.json": [{"kind": "area-code", "value": "0120-555", "expect": [{"admin1": "North", "admin2": "Alda"}, {"admin1": "North", "admin2": "Brin"}]}],
    "clues.md": "# Testland\n\n## Signs\n\n### Blue signs\n- Look for: blue\n- Points to: North\n- Strength: weak\n- Counterexamples: none seen\n- Sources: test\n",
}


def write_pack(root: Path, files: dict) -> Path:
    d = root / "qq"
    for rel, body in files.items():
        f = d / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(body if isinstance(body, str) else json.dumps(body, ensure_ascii=False), encoding="utf-8")
    return d


def run(script: str, *args: str, env: dict | None = None, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPTS / script), *args], capture_output=True, text=True, encoding="utf-8",
                          env={**os.environ, "PYTHONUTF8": "1", **(env or {})}, cwd=cwd)


class BundledPacks(unittest.TestCase):
    def test_bundled_packs_pass_lint(self):
        r = run("regions.py", "lint")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_cn_lookups_keep_their_answers(self):
        m = regions.lookup("plate", "粤B·12345", "cn")["matches"]
        self.assertEqual([(x["admin1"], x.get("admin2")) for x in m], [("广东省", "深圳市")])
        m = regions.lookup("area-code", "0817-1234567")["matches"]
        self.assertEqual([(x["country_code"], x["admin2"]) for x in m], [("CN", "南充市")])

    def test_descriptions_are_not_places(self):
        # Wikipedia cells like "市区普通汽车" (city-area cars) used to become fake candidates
        m = regions.lookup("plate", "京A", "cn")["matches"]
        self.assertEqual(len(m), 1)
        self.assertEqual({k for k in regions.MATCH_LEVELS if m[0].get(k)}, {"admin1"})

    def test_unknown_country_is_unsupported_not_china(self):
        r = run("clues.py", "lookup", "area-code", "020", "--country", "India", "--json")
        d = json.loads(r.stdout)
        self.assertEqual(d["status"], "unsupported")
        self.assertEqual(d["matches"], [])

    def test_country_without_that_table_is_unsupported(self):
        d = regions.lookup("plate", "ABC", "jp")
        self.assertEqual(d["status"], "unsupported")

    def test_foreign_plate_format_is_not_matched_against_cn(self):
        d = regions.lookup("plate", "KA01AB1234")
        self.assertEqual(d["matches"], [])

    def test_same_name_districts_stay_apart(self):
        rows = run("clues.py", "lookup", "admin", "朝阳区", "--json")
        chains = {tuple(m["chain"]) for m in json.loads(rows.stdout)["matches"]}
        self.assertIn(("北京市", "朝阳区"), chains)
        self.assertIn(("吉林省", "长春市", "朝阳区"), chains)


class FixturePack(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        write_pack(self.root / "packs", FIXTURE)
        self.env = {"GEO_SLEUTH_REGIONS": str(self.root / "packs")}

    def tearDown(self):
        self.tmp.cleanup()

    def lookup(self, *args):
        return json.loads(run("clues.py", "lookup", *args, "--json", env=self.env).stdout)

    def test_no_country_returns_every_country(self):
        d = self.lookup("area-code", "020")
        self.assertEqual(sorted(m["country_code"] for m in d["matches"]), ["CN", "QQ"])
        self.assertIn("several countries", d["note"])

    def test_country_restricts(self):
        d = self.lookup("area-code", "020", "--country", "Testland")
        self.assertEqual([m["admin2"] for m in d["matches"]], ["Porta"])
        d = self.lookup("area-code", "020", "--country", "cn")
        self.assertEqual([m["admin2"] for m in d["matches"]], ["广州市"])

    def test_removing_the_pack_leaves_cn_unchanged(self):
        with_pack = [m for m in self.lookup("area-code", "0817")["matches"] if m["country_code"] == "CN"]
        without = json.loads(run("clues.py", "lookup", "area-code", "0817", "--json").stdout)["matches"]
        self.assertEqual(with_pack, without)

    def test_multi_place_key_gives_one_candidate_each(self):
        board = self.root / "board.json"
        run("board.py", "--board", str(board), "init", "--photo", "x.jpg", env=self.env)
        r = run("board.py", "--board", str(board), "apply", "--kind", "area-code", "--value", "0120-555", "--country", "qq", env=self.env)
        self.assertEqual(r.returncode, 0, r.stderr)
        b = json.loads(board.read_text(encoding="utf-8"))
        self.assertIn("Alda", b["candidates"])
        self.assertIn("Brin", b["candidates"])
        self.assertEqual(b["candidates"]["Alda"]["cid"], "QQ/North/Alda")
        # one piece of evidence per place
        self.assertEqual(sum(1 for e in b["evidence"] if e["candidate"] == "North"), 1)

    def test_siblings_listed_by_children_are_down_weighted(self):
        # children records candidates with parent = the listed area; a lookup naming one of them must still count against the rest
        board = self.root / "board.json"
        run("board.py", "--board", str(board), "init", "--photo", "x.jpg", env=self.env)
        run("board.py", "--board", str(board), "add", "Porta", "Cora", "--level", "admin2", "--parent", "North", env=self.env)
        run("board.py", "--board", str(board), "apply", "--kind", "area-code", "--value", "020", "--country", "qq", env=self.env)
        b = json.loads(board.read_text(encoding="utf-8"))
        lr = {e["candidate"]: e["lr"] for e in b["evidence"]}
        self.assertGreater(lr["Porta"], 1)
        self.assertLess(lr["Cora"], 1)

    def test_same_name_elsewhere_gets_its_own_candidate(self):
        board = self.root / "board.json"
        run("board.py", "--board", str(board), "init", "--photo", "x.jpg", env=self.env)
        run("board.py", "--board", str(board), "add", "朝阳区", "--level", "district", "--parent", "北京市", env=self.env)
        r = run("board.py", "--board", str(board), "apply", "--kind", "area-code", "--value", "0431", "--country", "qq", env=self.env)
        self.assertEqual(r.returncode, 0, r.stderr)
        b = json.loads(board.read_text(encoding="utf-8"))
        self.assertIn("朝阳区 (长春市)", b["candidates"])
        beijing = [e for e in b["evidence"] if e["candidate"] == "朝阳区"]
        self.assertTrue(all(e["lr"] < 1 for e in beijing), beijing)

    def test_board_country_drives_apply_and_next(self):
        board = self.root / "board.json"
        run("board.py", "--board", str(board), "init", "--photo", "x.jpg", "--country", "cn", env=self.env)
        run("board.py", "--board", str(board), "apply", "--kind", "area-code", "--value", "020", env=self.env)
        b = json.loads(board.read_text(encoding="utf-8"))
        self.assertNotIn("Porta", b["candidates"])
        run("board.py", "--board", str(board), "add", "A区", "B区", "--level", "district", env=self.env)
        out = run("board.py", "--board", str(board), "next", env=self.env).stdout
        self.assertIn("baidu_pano.py sample", out)
        run("board.py", "--board", str(board), "country", "none", env=self.env)
        out = run("board.py", "--board", str(board), "next", env=self.env).stdout
        self.assertIn("gsv.py sheet", out)

    def board(self, *args):
        return run("board.py", "--board", str(self.root / "board.json"), *args, env=self.env)

    def read_board(self):
        return json.loads((self.root / "board.json").read_text(encoding="utf-8"))

    def test_country_without_the_table_is_not_down_weighted(self):
        # India has no pack here: an area code that isn't Chinese says nothing about India
        self.board("init", "--photo", "x.jpg")
        self.board("add", "China", "India", "Testland", "--level", "country")
        self.board("apply", "--kind", "area-code", "--value", "0817")
        lr = {}
        for e in self.read_board()["evidence"]:
            lr.setdefault(e["candidate"], []).append(e["lr"])
        self.assertEqual(lr["China"], [20.0])
        self.assertNotIn("India", lr)
        self.assertEqual(lr["Testland"], [0.05])   # its table was searched and had no 0817

    def test_country_context_doesnt_stand_in_for_unknown_countries(self):
        for how in (("init", "--photo", "x.jpg", "--country", "cn"), ("init", "--photo", "x.jpg")):
            (self.root / "board.json").unlink(missing_ok=True)
            self.board(*how)
            self.board("add", "China", "India", "--level", "country")
            self.board("apply", "--kind", "area-code", "--value", "0817", "--country", "cn")
            cands = {e["candidate"] for e in self.read_board()["evidence"]}
            self.assertIn("China", cands)
            self.assertNotIn("India", cands, how)

    def test_province_and_same_stem_city_are_two_places(self):
        self.board("init", "--photo", "x.jpg")
        self.board("add", "吉林省", "--level", "admin1")
        self.board("add", "吉林市", "--level", "admin2", "--parent", "吉林省")
        self.board("apply", "--kind", "plate", "--value", "吉B", "--country", "cn")
        b = self.read_board()
        self.assertEqual(sorted(b["candidates"]), ["吉林市", "吉林省"])
        self.assertEqual(b["candidates"]["吉林市"]["level"], "admin2")
        ev = {e["candidate"] for e in b["evidence"] if e["lr"] > 1}
        self.assertEqual(ev, {"吉林市", "吉林省"})

    def test_country_context_doesnt_overwrite_global_observations(self):
        self.board("init", "--photo", "x.jpg", "--country", "us")
        self.board("add", "United States", "Japan", "--level", "country")
        self.board("apply", "--kind", "driving-side", "--value", "left")
        lr = {e["candidate"]: e["lr"] for e in self.read_board()["evidence"]}
        self.assertGreater(lr["Japan"], 1)
        self.assertLess(lr["United States"], 1)
        self.board("country", "cn")
        r = self.board("apply", "--kind", "driving-side", "--value", "right")
        self.assertNotIn("returned nothing", r.stdout)

    def test_broken_pack_doesnt_break_other_countries(self):
        bad = self.root / "packs" / "zz"
        bad.mkdir(parents=True)
        (bad / "region.json").write_text(json.dumps({"code": "ZZ", "name": "Brokenland", "names": ["Brokenland"], "status": "stub",
                                                     "docs": [], "lookups": {"area-code": {"file": "data/missing.json"}}}), encoding="utf-8")
        d = self.lookup("area-code", "0817")
        self.assertEqual([m["country_code"] for m in d["matches"]], ["CN"])
        self.assertIn("ZZ pack is broken", d["note"])
        self.assertEqual(self.lookup("area-code", "0817", "--country", "zz")["status"], "error")
        # valid JSON of the wrong shape: same isolation, and lint reports it instead of crashing
        (bad / "data").mkdir()
        (bad / "data" / "missing.json").write_text("[]", encoding="utf-8")
        d = self.lookup("area-code", "0817")
        self.assertEqual([m["country_code"] for m in d["matches"]], ["CN"])
        r = run("regions.py", "lint", "zz", env=self.env)
        self.assertEqual(r.returncode, 1)
        self.assertIn("must be an object", r.stdout)
        self.assertNotIn("Traceback", r.stderr)

    def test_lint_rejects_code_merged_names_and_missing_sources(self):
        bad = json.loads(json.dumps(FIXTURE))
        bad["data/area_codes.json"]["_meta"].pop("source")
        bad["data/area_codes.json"]["entries"]["0120"] = [{"admin1": "North", "admin2": "Alda / Brin"}]
        bad["helper.py"] = "print('hi')\n"
        bad["clues.md"] = FIXTURE["clues.md"].replace("- Counterexamples: none seen\n", "")
        d = write_pack(self.root / "bad", bad)
        regions.packs(reload=True)
        errs, _ = regions.lint(dict(json.loads((d / "region.json").read_text()), dir=d))
        text = "\n".join(errs)
        self.assertIn("helper.py", text)
        self.assertIn("_meta.source", text)
        self.assertIn("Alda / Brin", text)
        self.assertIn("Counterexamples", text)


class GlobalTables(unittest.TestCase):
    def test_driving_side_of_split_countries(self):
        import clues
        side = {c: clues.lookup_driving_side(None, c)["matches"][0]["side"] for c in
                ("China", "Hong Kong", "Macau", "United Kingdom", "Japan", "India", "United States", "Canada", "Ireland")}
        self.assertEqual(side, {"China": "right", "Hong Kong": "left", "Macau": "left", "United Kingdom": "left", "Japan": "left",
                                "India": "left", "United States": "right", "Canada": "right", "Ireland": "left"})


class SameNamesAndPoi(unittest.TestCase):
    def test_same_name_under_another_parent_is_kept(self):
        import board
        b = {"candidates": {}}
        for parent, cid in (("南京市", "CN/江苏省/南京市/鼓楼区"), ("福州市", "CN/福建省/福州市/鼓楼区")):
            key = board._slot(b, "鼓楼区", parent, cid, "district")
            self.assertIsNotNone(key)
            b["candidates"][key] = {"parent": parent, "cid": cid, "level": "district"}
        self.assertEqual(sorted(b["candidates"]), ["鼓楼区", "鼓楼区 (福州市)"])
        self.assertIsNone(board._slot(b, "鼓楼区", "福州市", "CN/福建省/福州市/鼓楼区", "district"))
        self.assertIsNone(board._slot(b, "鼓楼区", "南京市", None, "district"))

    def test_poi_region_without_pack_keeps_the_country_filter(self):
        import poi
        from unittest.mock import patch
        seen = {}

        def fake_osm(kw, city, n, proxy, country):
            seen["country"] = country
            return []
        with patch.object(poi, "search_osm", fake_osm), patch.object(poi, "search_so", side_effect=AssertionError("360 used")), \
                patch.object(sys, "argv", ["poi.py", "Connaught Place", "--region", "in"]):
            poi.main()
        self.assertEqual(seen["country"], "in")
        with patch.object(sys, "argv", ["poi.py", "x", "--region", "Narnia"]), self.assertRaises(SystemExit):
            poi.main()


if __name__ == "__main__":
    unittest.main(verbosity=2)
