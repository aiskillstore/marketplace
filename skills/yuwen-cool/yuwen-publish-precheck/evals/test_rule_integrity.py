#!/usr/bin/env python3
"""规则库结构测试：防止编号、来源映射或正则在维护中悄悄失效。"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TERMS_PATH = ROOT / "scripts" / "terms.json"
REFERENCE_BY_DOC = {
    "general-community-safety": ROOT / "references" / "rules-common.md",
    "commercial-expression": ROOT / "references" / "rules-commercial.md",
    "medical-health": ROOT / "references" / "industry-medical.md",
    "finance": ROOT / "references" / "industry-finance.md",
}
VALID_SEVERITIES = {"critical", "high", "medium", "low"}


class RuleIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(TERMS_PATH.read_text(encoding="utf-8"))
        cls.terms = cls.payload["terms"]

    def test_rule_schema_ids_and_regexes(self):
        ids: list[str] = []
        for term in self.terms:
            with self.subTest(rule=term.get("rule")):
                self.assertTrue(
                    {"rule", "title", "severity", "pattern", "doc"} <= term.keys()
                )
                self.assertIn(term["severity"], VALID_SEVERITIES)
                self.assertIn(term["doc"], REFERENCE_BY_DOC)
                re.compile(term["pattern"])
                ids.append(term["rule"])
        self.assertEqual(len(ids), len(set(ids)), "内置规则编号重复")

    def test_every_scanner_rule_has_a_documented_heading(self):
        reference_text = {
            name: path.read_text(encoding="utf-8")
            for name, path in REFERENCE_BY_DOC.items()
        }
        for term in self.terms:
            short_id = term["rule"].rsplit(".", 1)[-1]
            with self.subTest(rule=term["rule"]):
                self.assertIn(f"### {short_id}｜", reference_text[term["doc"]])

    def test_official_source_links_are_https_and_verified(self):
        source_lines = []
        for path in REFERENCE_BY_DOC.values():
            source_lines.extend(
                line for line in path.read_text(encoding="utf-8").splitlines()
                if "[原文](" in line
            )
        self.assertGreater(len(source_lines), 0)
        for line in source_lines:
            with self.subTest(source=line[:80]):
                self.assertRegex(line, r"核验 20\d{2}-\d{2}-\d{2}")
                self.assertNotIn("[原文](http://", line)


if __name__ == "__main__":
    unittest.main(verbosity=1)
