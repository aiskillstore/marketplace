#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
save_diff.py —— 两份存档的字节级差分，输出后续"推断解锁位"所需的 diff JSON。

这是全 CG 存档流程里最关键的一环：

    同一款游戏，先存一份「未解锁」存档 A，再在游戏里解锁 1~2 张 CG，
    立刻再存一份「已解锁」存档 B。对 A/B 做差分，变化的字节就是
    CG 解锁状态位所在的位置。

    python save_diff.py A.save B.save --json out.diff.json

差分会把连续或邻近（由 --gap 控制)的变化合并成一个 run，并剔除只由
时间戳/随机种子造成的噪声（可用 --ignore 排除区间）。

输出 JSON 结构见 references/unlock-plan-schema.md。
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (dump_json, die, hexdump, human_size, load_json,
                    plausible_text, require_abs, setify, sha256, stderr)


def find_runs(before: bytes, after: bytes, gap: int) -> List[Dict[str, Any]]:
    """逐字节比较，把邻近的差分区合并成 run。"""
    n = min(len(before), len(after))
    offsets = [i for i in range(n) if before[i] != after[i]]
    if not offsets:
        return []
    runs: List[Dict[str, Any]] = []
    start = prev = offsets[0]
    for off in offsets[1:]:
        if off - prev > gap:
            runs.append((start, prev))
            start = off
        prev = off
    runs.append((start, prev))

    out = []
    for lo, hi in runs:
        length = hi - lo + 1
        b = before[lo:hi + 1]
        a = after[lo:hi + 1]
        out.append({
            "offset": lo,
            "length": length,
            "before_hex": b.hex(),
            "after_hex": a.hex(),
            "before_ascii": b.decode("latin-1") if plausible_text(b) else None,
            "after_ascii": a.decode("latin-1") if plausible_text(a) else None,
        })
    return out


def build_diff(a_path: Path, b_path: Path, gap: int,
               ignore: Optional[List[int]], max_run: int) -> Dict[str, Any]:
    A = a_path.read_bytes()
    B = b_path.read_bytes()
    runs = find_runs(A, B, gap)
    if ignore:
        ignore_set = set(ignore)
        runs = [r for r in runs
                if not any(off in ignore_set
                           for off in range(r["offset"],
                                            r["offset"] + r["length"]))]
    runs = [r for r in runs if r["length"] <= max_run]
    return {
        "kind": "allcg-diff",
        "version": 1,
        "created": datetime.now().isoformat(timespec="seconds"),
        "before": {
            "path": str(a_path), "size": len(A), "sha256": sha256(A),
        },
        "after": {
            "path": str(b_path), "size": len(B), "sha256": sha256(B),
        },
        "params": {"gap": gap, "max_run": max_run, "ignore": ignore or []},
        "runs": runs,
        "size_delta": len(B) - len(A),
    }


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="两份存档的字节差分",
        epilog="典型用法：先存一份未解锁存档，解锁 1~2 张 CG 后再存一份，然后 diff。")
    ap.add_argument("before", help="解锁前的存档（快照）")
    ap.add_argument("after", help="解锁后的存档（快照）")
    ap.add_argument("--gap", type=int, default=8,
                    help="差值小于该字节数的相邻变化合并为一个 run（默认 8）")
    ap.add_argument("--max-run", type=int, default=64,
                    help="长度超过该值的 run 视为结构变化，剔除（默认 64）")
    ap.add_argument("--ignore", metavar="OFFSETS",
                    help="忽略这些偏移（如 0x10,0x11 或范围 0x10-0x20）")
    ap.add_argument("--json", metavar="OUT", help="输出 diff JSON")
    ap.add_argument("--show", action="store_true",
                    help="打印每个 run 的上下文 hexdump")
    args = ap.parse_args(argv)

    a = require_abs(args.before)
    b = require_abs(args.after)
    if not a.exists() or not b.exists():
        die("[!] 输入文件不存在")

    ignore = None
    if args.ignore:
        txt = ",".join(f"{int(x, 0)}" for x in
                       [p.strip() for p in args.ignore.split(",") if p.strip()])
        ignore = setify(txt)

    diff = build_diff(a, b, args.gap, ignore, args.max_run)
    print(f"# 差分：{a.name} -> {b.name}")
    print(f"  文件大小 {human_size(diff['before']['size'])} -> "
          f"{human_size(diff['after']['size'])} "
          f"(Δ{diff['size_delta']:+d} 字节)")
    print(f"  发现 {len(diff['runs'])} 个变化区间")

    if not diff["runs"]:
        stderr("[!] 两份存档完全一致，无法定位解锁位。"
               "请确认它们是「解锁前 / 解锁后」的两个不同状态。")

    for r in diff["runs"][:80]:
        line = (f"  @{r['offset']:#x} ({r['length']}B)  "
                f"{r['before_hex']} -> {r['after_hex']}")
        if r["before_ascii"] and not r["after_ascii"]:
            line += f"   {r['before_ascii']!r} -> (二进制)"
        elif r["after_ascii"] and r["before_ascii"]:
            line += f"   {r['before_ascii']!r} -> {r['after_ascii']!r}"
        print(line)
        if args.show:
            data = bytes.fromhex(r["before_hex"] + r["after_hex"])
            print(hexdump(data, base=r["offset"], limit=8))
    if len(diff["runs"]) > 80:
        print(f"  …另有 {len(diff['runs']) - 80} 个区间，见 JSON")

    if args.json:
        out = require_abs(args.json) if args.json.startswith(("/", "\\")) \
            else Path(args.json).resolve()
        dump_json(out, diff)
        print(f"[+] 已写出 {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
