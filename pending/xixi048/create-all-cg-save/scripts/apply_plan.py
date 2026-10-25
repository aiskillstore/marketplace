#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_plan.py —— 把解锁计划（patch plan）落书到存档，带备份与一键回滚。

    python apply_plan.py plan.json --dry-run     # 预演，不落盘
    python apply_plan.py plan.json               # 备份后写入
    python apply_plan.py plan.json rollback      # 从备份还原

补丁写入策略（自动选择）：
  - 若所有 patch 的 before/after 长度相等 —— 就地字节替换，最安全。
  - 若存在长度变化的 patch —— 重建字节序列。对于 Ruby Marshal 这类
    "顺序自描述、无全局偏移表与校验和"的格式是安全的；但对于带有长度
    前缀容器的格式（如 Marshal 的 TYPE_USRDEF）需要先修前缀，脚本会
    显式警告并要求 --allow-resize。
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (atomic_write, confirm_target_for_write, dump_json,
                    die, human_size, load_json, make_backup, require_abs,
                    sha256)

MAX_REPORT_ROWS = 20


def load_plan(path: Path) -> Dict[str, Any]:
    plan = load_json(path)
    if plan.get("kind") not in ("allcg-plan", None):
        die(f"[!] 不是合法的解锁计划文件：{path}")
    if "target" not in plan or "patches" not in plan:
        die(f"[!] 计划缺少 target / patches 字段：{path}")
    return plan


def compute_new_bytes(original: bytes, patches: List[Dict[str, Any]]
                     ) -> tuple[bytes, List[str], List[str]]:
    """按顺序应用补丁，返回 (新字节, 成功记录, 失败记录)。"""
    src = bytearray(original)
    applied: List[str] = []
    failed: List[str] = []
    shift = 0
    resizing = False

    # 先判断是否全部等长
    uniform = all(len(bytes.fromhex(p["before_hex"])) ==
                  len(bytes.fromhex(p["after_hex"])) for p in patches)

    for p in patches:
        before = bytes.fromhex(p["before_hex"])
        after = bytes.fromhex(p["after_hex"])
        offset = int(p["offset"]) + shift
        require_before = p.get("require_before", True)
        want_before = before if require_before else None
        if offset < 0 or offset + len(before) > len(src):
            failed.append(f"@{p['offset']:#x} 越界（偏移超出文件）")
            continue
        current = bytes(src[offset:offset + len(before)])
        if want_before is not None and current != want_before:
            failed.append(
                f"@{p['offset']:#x} 原始字节不匹配：期望 {before.hex()} "
                f"实际 {current.hex()}" + (f"  {p.get('note', '')}"))
            continue
        src[offset:offset + len(before)] = after
        if len(after) != len(before):
            shift += len(after) - len(before)
            resizing = True
        applied.append(f"@{p['offset']:#x} {before.hex()} -> {after.hex()}"
                       + (f"  {p.get('note', '')}" if p.get("note") else ""))

    return bytes(src), applied, failed


def cmd_apply(plan: Dict[str, Any], plan_path: Path, dry_run: bool,
              no_backup: bool, allow_resize: bool) -> int:
    target = require_abs(plan["target"])
    patches = sorted(plan["patches"], key=lambda p: int(p["offset"]))
    original = target.read_bytes()

    expect_sha = plan.get("sha256_before")
    if expect_sha and expect_sha != sha256(original):
        die(f"[!] 存档内容与计划记录的不一致：\n"
            f"    期望 sha256 {expect_sha}\n"
            f"    实际 sha256 {sha256(original)}\n"
            f"    说明计划是针对另一份存档生成的，拒绝写入。")

    new_bytes, applied, failed = compute_new_bytes(original, patches)
    resizing = any(len(bytes.fromhex(p["before_hex"])) !=
                   len(bytes.fromhex(p["after_hex"])) for p in patches)

    print(f"# 目标：{target}  ({human_size(len(original))})")
    print(f"  补丁总数 {len(patches)}，可应用 {len(applied)}，失败 {len(failed)}")
    if resizing:
        print(f"  变更长度：{len(original)} -> {len(new_bytes)} "
              f"({len(new_bytes) - len(original):+d} 字节)")
        if not allow_resize:
            die("[!] 该计划会改变文件长度。若目标格式是顺序自描述格式"
                "（如 Ruby Marshal）通常安全，请加 --allow-resize 确认继续。")

    for row in failed[:MAX_REPORT_ROWS]:
        print(f"  [x] {row}")
    if len(failed) > MAX_REPORT_ROWS:
        print(f"  …另有 {len(failed) - MAX_REPORT_ROWS} 条失败")

    if not applied:
        die("[!] 没有任何补丁可以应用，未做任何修改。")

    if dry_run:
        print("  （--dry-run：以上为预演，未写入磁盘）")
        for row in applied[:MAX_REPORT_ROWS]:
            print(f"  [ ] {row}")
        return 0

    if not no_backup:
        bak = make_backup(target)
        plan["backup_path"] = str(bak)
        plan["backup_sha256"] = sha256(bak.read_bytes())
        dump_json(plan_path, plan)
        print(f"  [+] 已备份 -> {bak.name}")

    atomic_write(target, new_bytes)
    print(f"  [+] 已写入 {target}")
    for row in applied[:MAX_REPORT_ROWS]:
        print(f"  [v] {row}")
    print(f"  [+] sha256 {sha256(original)[:16]}... -> "
          f"{sha256(new_bytes)[:16]}...")
    print("  提示：回滚命令 > python apply_plan.py "
          f"{plan_path.name} rollback")
    return 0


def cmd_rollback(plan: Dict[str, Any], plan_path: Path) -> int:
    bak = plan.get("backup_path")
    if not bak:
        die("[!] 该计划没有记录备份路径（可能未执行过 apply）")
    bak_path = require_abs(bak)
    if not bak_path.exists():
        die(f"[!] 备份文件已不存在：{bak_path}")
    expect = plan.get("backup_sha256")
    if expect and expect != sha256(bak_path.read_bytes()):
        die("[!] 备份文件完整性校验失败，拒绝回滚")
    target = require_abs(plan["target"])
    atomic_write(target, bak_path.read_bytes())
    print(f"[+] 已回滚 {target} <- {bak_path.name}")
    return 0


def cmd_verify(plan: Dict[str, Any]) -> int:
    target = require_abs(plan["target"])
    data = target.read_bytes()
    ok = fail = 0
    for p in plan["patches"]:
        after = bytes.fromhex(p["after_hex"])
        off = int(p["offset"])
        if data[off:off + len(after)] == after:
            ok += 1
        else:
            fail += 1
            print(f"  [x] @{off:#x} 期望 {after.hex()} "
                  f"实际 {data[off:off + len(after)].hex()}")
    print(f"# 校验：{ok} 处符合预期，{fail} 处不符")
    return 0 if fail == 0 else 1


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="应用/回滚全 CG 解锁补丁")
    ap.add_argument("plan", help="解锁计划 JSON")
    ap.add_argument("action", nargs="?", default="apply",
                    choices=["apply", "rollback", "verify"])
    ap.add_argument("--dry-run", action="store_true", help="预演，不写入")
    ap.add_argument("--no-backup", action="store_true",
                    help="不备份直接写（不推荐）")
    ap.add_argument("--allow-resize", action="store_true",
                    help="允许改变文件长度的补丁")
    args = ap.parse_args(argv)

    plan_path = require_abs(args.plan)
    if not plan_path.exists():
        die(f"[!] 计划文件不存在：{plan_path}")
    plan = load_plan(plan_path)
    confirm_target_for_write(require_abs(plan["target"]))

    if args.action == "apply":
        return cmd_apply(plan, plan_path, args.dry_run, args.no_backup,
                         args.allow_resize)
    if args.action == "rollback":
        return cmd_rollback(plan, plan_path)
    return cmd_verify(plan)


if __name__ == "__main__":
    sys.exit(main())
