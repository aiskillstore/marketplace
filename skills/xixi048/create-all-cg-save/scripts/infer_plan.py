#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
infer_plan.py —— 从差分结果推断 CG 解锁位的阵列结构，并生成解锁计划。

一次差分只能告诉你"哪几个字节变了"；要解锁**全部** CG，需要进一步推断出
"这些位其实是一个等步长阵列（CG 标志数组）的一部分"。本脚本做这件事：

    1. 收集所有单字节变化（典型的布尔/枚举标志位）
    2. 用 GCD 拟合等差数列 —— 若能严格覆盖全部变化偏移，就说明找到了
       一个 start + stride 阵列；否则退化为"仅修补已观测到的偏移"
    3. 确定 off 字节（未解锁值）与 on 字节（已解锁值）
    4. 按 --count 或 --auto-extend 外扩到整个 CG 阵列，生成计划

    python infer_plan.py after1.diff.json after2.diff.json \
        --target Save01.rvdata2 --count 128 --out unlock-plan.json

生成的 plan JSON 交给 apply_plan.py 执行。参数详见 references/unlock-plan-schema.md。
"""
from __future__ import annotations

import argparse
import math
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (dump_json, die, load_json, require_abs, sha256, stderr)


def collect_changes(diffs: List[Dict[str, Any]]) -> Dict[int, Dict[str, bytes]]:
    """汇总多个 diff 的单字节变化，offset -> {'before':b, 'after':b}。"""
    table: Dict[int, Dict[str, bytes]] = {}
    for d in diffs:
        for r in d.get("runs", []):
            if r["length"] != 1:
                continue
            before = bytes.fromhex(r["before_hex"])
            after = bytes.fromhex(r["after_hex"])
            table.setdefault(r["offset"], {"before": before, "after": after})
    return table


def fit_progression(offsets: List[int]) -> Optional[Tuple[int, int]]:
    """尝试用 (start, stride) 覆盖所有 offset；成功返回 (start, stride)。"""
    if len(offsets) < 2:
        return None
    s = sorted(offsets)
    deltas = [b - a for a, b in zip(s, s[1:])]
    stride = 0
    for d in deltas:
        stride = math.gcd(stride, d)
    if stride <= 0:
        return None
    if all((o - s[0]) % stride == 0 for o in s):
        return s[0], stride
    return None


def modal(items: List[bytes]) -> bytes:
    if not items:
        return b""
    counts: Dict[bytes, int] = {}
    for b in items:
        counts[b] = counts.get(b, 0) + 1
    return max(counts.items(), key=lambda kv: kv[1])[0]


def auto_extend(data: bytes, start: int, stride: int, last_known: int,
                off: bytes, tolerance: int, max_count: int) -> Tuple[int, int]:
    """从已观测的最后一位继续向前扫描，直到连续 tolerance 个槽位不像该阵列。

    判定依据：槽位内容是 off 值（未解锁）或 on 值（已解锁），且扫描不越界。
    """
    # 先向前回溯到阵列起点前的第一个非 off/on 位置，用于估算阵列首元素
    idx = (last_known - start) // stride
    misses = 0
    end_idx = idx
    while end_idx + 1 < idx + max_count:
        nxt = start + (end_idx + 1) * stride
        if nxt + len(off) > len(data):
            break
        chunk = data[nxt:nxt + len(off)]
        if chunk == off:
            misses = 0
            end_idx += 1
            continue
        misses += 1
        if misses > tolerance:
            break
        end_idx += 1
    return idx, end_idx - idx + 1


def resolve_layout(offsets: List[int], forced_start: Optional[int],
                   forced_stride: Optional[int]) -> Tuple[int, int, str]:
    """确定 (start, stride, 来源)；forced 参数优先，其次拟合。

    步长歧义的处理：只有 1~2 个观测位点时，任意「delta 的约数」都能拟合
    （例如步长 4 的阵列只解锁了第 0、5 项，GCD 会给出 20）。这种情况必须
    显式告警并建议用 --stride 或更多快照，绝不能静默按最大值外扩。
    """
    fit = fit_progression(offsets)
    source = "fitted"

    if forced_stride:
        stride = forced_stride
        source = "cli-stride"
    elif fit:
        stride = fit[1]
    else:
        stride = 0
        source = "observed-only"

    if forced_start is not None:
        start = forced_start
        source += "+cli-start"
    else:
        # 以最早观测位点作为第 0 个槽位的锚点；若显式给了 --start，
        # 用户可自行向前对齐到阵列真实的第一个元素。
        start = offsets[0]

    return start, stride, source


def build_plan(diffs: List[Dict[str, Any]], target: Path,
               count: Optional[int], do_extend: bool, tolerance: int,
               max_count: int, on_hex: Optional[str], off_hex: Optional[str],
               note: str, forced_stride: Optional[int] = None,
               forced_start: Optional[int] = None) -> Dict[str, Any]:
    changes = collect_changes(diffs)
    if not changes:
        die("[!] 差分里没有可用的单字节变化，无法推断。"
            "请检查 diff 是否来自「解锁前 / 解锁后」两份不同状态的存档。")

    offsets = sorted(changes)
    print(f"# 观测到 {len(offsets)} 个单字节变化位点："
          f"{[hex(o) for o in offsets[:12]]}"
          f"{' …' if len(offsets) > 12 else ''}")

    start, stride, stride_source = resolve_layout(offsets, forced_start,
                                                  forced_stride)
    if stride > 0:
        print(f"  阵列结构：start={start:#x} stride={stride}（来源：{stride_source}）")
    else:
        stderr("  [!] 变化位点不构成等步长阵列，退化为「仅修补已观测位点」。\n"
               "     建议再多解锁几张 CG 各存一份，以便拟合出步长。")

    if stride > 0 and forced_stride is None and len(offsets) < 3:
        deltas = sorted({b - a for a, b in zip(offsets, offsets[1:])})
        stderr("  [!] 步长存在歧义：只有 " + str(len(offsets)) +
               " 个观测位点，任何 delta 的约数都能拟合。\n"
               f"     当前取 stride={stride}（=观测间距 {deltas}），"
               "若真实阵列更密，外扩会跳过大量槽位。\n"
               "     建议：多解锁 2~3 张 CG 各存一份，或用 --stride / "
               "--start 显式指定。")

    off = bytes.fromhex(off_hex) if off_hex else \
        modal([v["before"] for v in changes.values()])
    on = bytes.fromhex(on_hex) if on_hex else \
        modal([v["after"] for v in changes.values()])
    print(f"  解锁值 off={off.hex()} -> on={on.hex()}")

    if stride > 0:
        off_grid = [hex(o) for o in offsets if (o - start) % stride != 0]
        if off_grid:
            stderr("  [!] 以下观测位点不落在 start/stride 网格上，说明阵列结构推测有误："
                   f"{off_grid[:8]}{' …' if len(off_grid) > 8 else ''}\n"
                   "     请改用 --start / --stride 显式指定，或补充快照。")

    data = target.read_bytes()

    # 确定要覆盖的槽位
    if stride <= 0:
        slots = offsets
    elif count:
        slots = [start + i * stride for i in range(count)]
    elif do_extend:
        last = max(offsets)
        _, n = auto_extend(data, start, stride, last, off, tolerance,
                           max_count)
        slots = [start + i * stride for i in range(n)]
        print(f"  自动外扩：阵列约 {n} 个槽位"
              f"（{start:#x} ~ {start + (n - 1) * stride:#x}）")
    else:
        slots = offsets
        stderr("  [!] 未指定 --count/--auto-extend，仅修补已观测到的位点。")

    before_filter = len(slots)
    slots = [s for s in slots if s >= 0 and s + len(on) <= len(data)]
    dropped = before_filter - len(slots)
    if dropped:
        stderr(f"  [!] {dropped} 个推算槽位超出文件边界（文件 {len(data)} 字节），"
               "已丢弃。若占比很大，说明 stride/count 可能偏大，"
               "先小范围验证再全量写入。")

    patches: List[Dict[str, Any]] = []
    skipped = already = 0
    for off_i in slots:
        current = data[off_i:off_i + len(on)]
        if current == on:
            already += 1
            continue
        if current != off and current != bytes(len(off)):
            skipped += 1
            continue
        patches.append({
            "offset": off_i,
            "before_hex": current.hex(),
            "after_hex": on.hex(),
            "require_before": True,
            "note": f"slot@{(off_i - start) // stride if stride else 0}"
                    f" {off_i:#x}",
        })

    print(f"  生成补丁 {len(patches)} 条（已处于解锁态 {already}，"
          f"跳过异常字节 {skipped}）")

    return {
        "kind": "allcg-plan",
        "version": 1,
        "created": datetime.now().isoformat(timespec="seconds"),
        "target": str(target),
        "sha256_before": sha256(data),
        "description": note or "由差分推断生成的 CG 解锁计划",
        "inference": {
            "start": start,
            "stride": stride,
            "stride_source": stride_source,
            "slot_count_requested": count,
            "slots_dropped_out_of_range": dropped,
            "off_hex": off.hex(),
            "on_hex": on.hex(),
            "observed_offsets": offsets,
            "source_diffs": [d.get("before", {}).get("path") and
                             d.get("after", {}).get("path") for d in diffs],
        },
        "patches": patches,
        "backup_path": None,
    }


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="从差分推断 CG 解锁阵列并生成解锁计划",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("diffs", nargs="+", help="一个或多个 save_diff.py 产出的 JSON")
    ap.add_argument("--target", required=True, help="要打补丁的目标存档")
    ap.add_argument("--out", required=True, help="输出的解锁计划 JSON")
    ap.add_argument("--count", type=int,
                    help="CG 标志阵列的槽位数（最强约束，优先提供）")
    ap.add_argument("--stride", type=lambda s: int(s, 0),
                    help="强制指定阵列步长（十进制或 0x 前缀）。只有 1~2 个观测位点"
                         "时拟合结果必然歧义，此参数最可靠")
    ap.add_argument("--start", type=lambda s: int(s, 0),
                    help="强制指定阵列首元素的文件偏移（十进制或 0x 前缀）")
    ap.add_argument("--auto-extend", action="store_true",
                    help="自动向文件后方扫描推断阵列长度")
    ap.add_argument("--tolerance", type=int, default=2,
                    help="自动外扩时允许连续多少个槽位取值异常后停止（默认 2）")
    ap.add_argument("--max-count", type=int, default=4096,
                    help="自动外扩的最大槽位数（默认 4096）")
    ap.add_argument("--on-hex", help="强制指定解锁后的字节（hex，如 54 表示 'T'）")
    ap.add_argument("--off-hex", help="强制指定未解锁的字节（hex）")
    ap.add_argument("--note", help="写进计划的说明文字")
    args = ap.parse_args(argv)

    target = require_abs(args.target)
    if not target.exists():
        die(f"[!] 目标存档不存在：{target}")

    diffs = [load_json(require_abs(p)) for p in args.diffs]
    out = Path(args.out).resolve()
    plan = build_plan(diffs, target, args.count, args.auto_extend,
                      args.tolerance, args.max_count, args.on_hex,
                      args.off_hex, args.note, args.stride, args.start)
    dump_json(out, plan)
    print(f"[+] 已写出解锁计划 {out}（{len(plan['patches'])} 条补丁）")
    print(f"    下一步： python apply_plan.py {out.name} --dry-run")
    return 0


if __name__ == "__main__":
    sys.exit(main())
