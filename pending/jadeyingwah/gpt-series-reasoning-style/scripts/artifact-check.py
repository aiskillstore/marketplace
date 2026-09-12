#!/usr/bin/env python3
"""Structure checker for project governance artifacts (see references/project-artifacts.md).

Validates the STRUCTURE of gate records and governance ledgers inside a user
project. It deliberately does NOT judge content truthfulness: a structurally
valid gate record says nothing about whether authorization really happened —
that remains a human evidence check (same philosophy as selfcheck.py).

  python scripts/artifact-check.py <project-root>

Exit codes: 0 = all structural rules pass, 1 = structural problems found,
2 = usage / path error.

Checked rules:
  1. docs/gate/*.md     — each record carries the 11 gate-field labels (authoritative
                          list: GATE_FIELDS below, mirrored in SKILL.md and workflow
                          CN/EN), a legal status line, and a superseded pointer when
                          superseded.
  2. dispatch-ledger.md — if present, must be non-empty governance content.
  3. findings-ledger.md — if present, each round must name all four required
                          fields (round number / change & reason / open items /
                          evidence pointer); checked per round, not file-wide.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

GATE_FIELDS = [
    "我理解的目标",
    "风险分档",
    "形态选择",
    "已盘点可用资源",
    "最高影响问题",
    "推荐方案",
    "其他选项",
    "完整计划",
    "澄清方式",
    "需要你确认",
    "确认范围",
]
STATUSES = {"proposed", "confirmed", "rejected", "superseded"}
FINDINGS_FIELDS = ["轮次编号", "本轮改动与原因", "未解项", "证据指针"]
# a round heading like "## Round 3" / "## 第 3 轮" / "### Round 3 / 第3轮"
ROUND_HEADING = re.compile(r"^#{1,4}.*?(?:Round\s*\d+|第\s*\d+\s*轮)", re.M | re.I)


def fail(items: list, msg: str) -> None:
    items.append(msg)


def check_gate_record(path: pathlib.Path, items: list) -> None:
    text = path.read_text(encoding="utf-8", errors="replace")
    for field in GATE_FIELDS:
        if field not in text:
            fail(items, "{}: missing gate field [{}]".format(path.name, field))
    if not re.search(r"Date\s*/?\s*日期[:：]\s*\d{4}-\d{2}-\d{2}", text, re.I):
        fail(items, "{}: missing Date line (Date / 日期: YYYY-MM-DD)".format(path.name))
    if not re.search(r"Task tier\s*/?\s*任务分档[:：]\s*(轻|中|重)", text, re.I):
        fail(items, "{}: missing Task tier line (轻|中|重)".format(path.name))
    if not re.search(r"Form\s*/?\s*形态[:：]\s*(主干|子Agent|指挥官)", text, re.I):
        fail(items, "{}: missing Form line (主干|子Agent|指挥官)".format(path.name))
    m = re.search(r"Status\s*/?\s*状态[:：]\s*(\S+)", text, re.I)
    if not m:
        fail(items, "{}: missing status line (Status / 状态:)".format(path.name))
        return
    status = m.group(1).strip("`*# ").lower()
    if status not in STATUSES:
        fail(items, "{}: illegal status {!r} (allowed: {})".format(
            path.name, status, "/".join(sorted(STATUSES))))
        return
    if status == "superseded" and not re.search(
            r"Superseded-by\s*/?\s*作废指向[:：]\s*\S+", text, re.I):
        fail(items, "{}: superseded record lacks a Superseded-by pointer".format(path.name))


def check_dispatch_ledger(path: pathlib.Path, items: list) -> None:
    text = path.read_text(encoding="utf-8", errors="replace").strip()
    if not text:
        fail(items, "dispatch-ledger.md exists but is empty")
        return
    if "派发" not in text and "dispatch" not in text.lower():
        fail(items, "dispatch-ledger.md: no dispatch-related content header found")


def check_findings_ledger(path: pathlib.Path, items: list) -> None:
    text = path.read_text(encoding="utf-8", errors="replace")
    rounds = list(ROUND_HEADING.finditer(text))
    if not rounds:
        fail(items, "findings-ledger.md: no round headings (## Round N / 第 N 轮)")
        return
    # L5: check PER ROUND — file-wide containment let a single complete round
    # mask other rounds that were missing required fields.
    for i, m in enumerate(rounds):
        start = m.end()
        end = rounds[i + 1].start() if i + 1 < len(rounds) else len(text)
        seg = text[start:end]
        name = m.group(0).strip()
        for field in FINDINGS_FIELDS:
            if field not in seg:
                fail(items, "findings-ledger.md: [{}] missing field [{}]".format(name, field))


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Structure checker for project governance artifacts (docs/gate, ledgers)")
    ap.add_argument("root", help="project root whose docs/ governance artifacts are checked")
    args = ap.parse_args()
    root = pathlib.Path(args.root)
    if not root.is_dir():
        print("ERROR: not a directory: " + str(root))
        return 2

    items: list = []
    gate_dir = root / "docs" / "gate"
    n_gate = 0
    if gate_dir.is_dir():
        for p in sorted(gate_dir.glob("*.md")):
            n_gate += 1
            check_gate_record(p, items)
    elif (root / "docs").is_dir():
        # docs/ exists without gate/: fine for light-channel-only projects.

        # a docs/agents ledger without any gate dir is legal; nothing to do here.
        pass

    dispatch = root / "docs" / "agents" / "dispatch-ledger.md"
    if dispatch.is_file():
        check_dispatch_ledger(dispatch, items)
    findings = root / "docs" / "agents" / "findings-ledger.md"
    if findings.is_file():
        check_findings_ledger(findings, items)

    print("Project artifact structure check / 项目治理产物结构校验")
    print("- Project root: {}".format(root))
    print("- Gate records scanned: {}".format(n_gate))
    print("- dispatch-ledger.md: {}".format("present" if dispatch.is_file() else "absent"))
    print("- findings-ledger.md: {}".format("present" if findings.is_file() else "absent"))
    if items:
        print("- Result: {} structural problem(s)".format(len(items)))
        for it in items:
            print("  [FAIL] " + it)
        return 1
    if n_gate == 0 and not dispatch.is_file() and not findings.is_file():
        # P1-23: an empty directory must not read as "all pass" — nothing was validated.
        print("- Result: NO governance artifacts found — nothing was validated (not a pass)")
        print("  (Legal for light-channel-only projects; add docs/gate/, a dispatch ledger, or a findings ledger to have something checked.)")
        return 0
    print("- Result: all structural rules pass (structure only — content truth is a human check)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
