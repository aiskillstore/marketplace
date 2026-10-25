#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rgss_save.py —— RPG Maker XP / VX / VX Ace (RGSS1/2/3) 存档的引擎专属通道。

为什么需要它
------------
RGSS3 的存档是标准的 Ruby Marshal Dump，因此**不需要做字节差分**也能精确定位
CG 解锁位：

    DataManager.make_save_header    -> 第 1 个 Marshal 流（存档界面显示用）
    DataManager.make_save_contents  -> 第 2 个 Marshal 流（真正的游戏状态）

后者是一个 11 项 Hash，其中 :switches (Game_Switches) 与 :variables
(Game_Variables) 的 @data 数组就是开关 / 变量表。绝大多数以事件驱动的 CG 回想
室，解锁条件都挂在开关上 —— 把这些开关置为 true 即可解锁画廊。

布尔值在 Marshal 里是单字节 'T'(0x54) / 'F'(0x46)，因此**等长替换**即可完成写入，
完全不改变文件长度，是所有写入方式里风险最低的一种。

命令
----
    python rgss_save.py inspect       Save02.rvdata2
    python rgss_save.py plan-switches Save02.rvdata2 --all --out plan.json
    python rgss_save.py plan-switches Save02.rvdata2 --ids 1,3,5-20 --out plan.json
    python rgss_save.py plan-variables Save02.rvdata2 --set 41=1,42=3 --out plan.json

生成的 plan.json 交给 scripts/apply_plan.py 执行。
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE.parent))

from ruby_marshal import Node, encode_bool, encode_int, read_streams  # noqa: E402
from common import (die, dump_json, human_size, require_abs, setify,  # noqa: E402
                    sha256)

CONTENT_KEYS = {"system", "timer", "message", "switches", "variables",
                "self_switches", "actors", "party", "troop", "map", "player"}


# ---------- 定位 ----------

def load_contents(path: Path) -> Tuple[List[Node], Node]:
    """返回 (全部 Marshal 流, 承载游戏状态的那个 Hash 节点)。"""
    data = path.read_bytes()
    try:
        streams = read_streams(data)
    except Exception as exc:                # noqa: BLE001
        die(f"[!] 不是可解析的 Ruby Marshal 文件：{exc}")
    for s in streams:
        if s.kind == "hash" and any(str(k.value) in CONTENT_KEYS
                                    for k, _ in s.value):
            return streams, s
    die("[!] 未能在该文件中找到 RGSS 的 save_contents，"
        "它可能不是 RGSS 存档（或使用了自定义封装）。")


def content_map(contents: Node) -> Dict[str, Node]:
    return {str(k.value): v for k, v in contents.value}


def get_data_array(obj: Node) -> Optional[Node]:
    return obj.value.get("@data") if obj.kind == "object" else None


def describe_array(name: str, arr: Node) -> Dict[str, Any]:
    items = arr.value
    kind = "bool" if any(x.kind in ("true", "false") for x in items) else "num"
    stride = (items[1].pos - items[0].pos) if len(items) > 1 else 0
    return {
        "name": name, "count": len(items), "kind": kind,
        "array_pos": arr.pos, "first_item_pos": items[0].pos if items else None,
        "stride": stride, "items": items,
    }


# ---------- 命令 ----------

def cmd_inspect(path: Path, show_true: int) -> int:
    streams, contents = load_contents(path)
    print(f"# {path.name}  ({human_size(path.stat().st_size)})")
    print(f"  Marshal 流数量：{len(streams)}")
    for i, s in enumerate(streams, 1):
        print(f"    [{i}] {s.pos:#x} ~ {s.end:#x}  "
              f"{human_size(s.raw_len)}  {s.kind}"
              + (f"  keys={[str(k.value) for k, _ in s.value][:4]}…"
                 if s.kind == "hash" else ""))
    print()
    cm = content_map(contents)
    print("  save_contents:")
    for k, v in contents.value:
        name = str(k.value)
        extra = ""
        arr = get_data_array(v)
        if arr is not None and arr.kind == "array":
            extra = f"  @data[{len(arr.value)}]"
        print(f"    :{name:<14} {v.kind:<10} "
              f"cls={str(v.ruby_class):<16} @{v.pos:#x}{extra}")

    for name in ("switches", "variables", "self_switches"):
        if name not in cm:
            continue
        arr = get_data_array(cm[name])
        if arr is None or arr.kind != "array":
            continue
        info = describe_array(name, arr)
        if info["count"] == 0:
            print(f"\n  :{name}  @data 为空数组（该存档尚未写入任何 "
                  f"{'开关' if name == 'switches' else '变量'}）")
            continue
        print()
        print(f"  :{name}  @data 共 {info['count']} 项"
              f"（@{info['array_pos']:#x}，首元素 @{info['first_item_pos']:#x}"
              f"，步长 {info['stride']}）")
        if info["kind"] == "bool":
            on = [i for i, x in enumerate(arr.value) if x.kind == "true"]
            off = [i for i, x in enumerate(arr.value) if x.kind == "false"]
            nil = [i for i, x in enumerate(arr.value) if x.kind == "nil"]
            print(f"     true={len(on)} false={len(off)} nil(未分配)={len(nil)}")
            if on:
                print(f"     已置 ON 的开关 ID（前 {show_true} 个）：{on[:show_true]}")
        else:
            nz = [(i, x.value) for i, x in enumerate(arr.value)
                  if getattr(x, "value", 0)]
            print(f"     非零变量：{nz[:show_true]}")
    return 0


def cmd_plan_switches(path: Path, ids: Optional[List[int]], all_: bool,
                     out: Path, note: str) -> int:
    _, contents = load_contents(path)
    cm = content_map(contents)
    if "switches" not in cm:
        die("[!] 该存档没有 :switches，无法生成开关计划")
    arr = get_data_array(cm["switches"])
    if arr is None:
        die("[!] Game_Switches 里没有 @data")
    items = arr.value

    if all_:
        ids = list(range(len(items)))
    elif not ids:
        die("[!] 请用 --ids 指定要置 ON 的开关，或 --all 置全部")

    data = path.read_bytes()
    patches: List[Dict[str, Any]] = []
    already = 0
    invalid: List[int] = []
    for idx in ids:
        if idx < 0 or idx >= len(items):
            invalid.append(idx)
            continue
        node = items[idx]
        current = data[node.pos:node.pos + 1]
        if current == b"T":
            already += 1
            continue
        patches.append({
            "offset": node.pos,
            "before_hex": current.hex(),
            "after_hex": encode_bool(True).hex(),
            "require_before": True,
            "note": f"switch[{idx}] -> true",
        })

    plan = {
        "kind": "allcg-plan",
        "version": 1,
        "created": datetime.now().isoformat(timespec="seconds"),
        "target": str(path),
        "sha256_before": sha256(data),
        "engine": "rgss3-switches",
        "description": note or f"RGSS 开关置 ON（共 {len(patches)} 个）",
        "inference": {
            "switch_count": len(items),
            "requested_ids": ids,
            "array_pos": arr.pos,
            "first_item_pos": items[0].pos if items else None,
            "stride": (items[1].pos - items[0].pos) if len(items) > 1 else 0,
        },
        "patches": patches,
        "backup_path": None,
    }
    print(f"# 开关计划：共 {len(items)} 个槽位，已 ON {already}，"
          f"待写入 {len(patches)}")
    if invalid:
        print(f"  [!] 以下 ID 越界已忽略：{invalid[:20]}")
    dump_json(out, plan)
    print(f"[+] 已写出 {out}")
    print(f"    下一步： python apply_plan.py {out.name} --dry-run")
    return 0


def cmd_plan_variables(path: Path, assignments: List[Tuple[int, int]],
                       out: Path) -> int:
    _, contents = load_contents(path)
    cm = content_map(contents)
    if "variables" not in cm:
        die("[!] 该存档没有 :variables")
    arr = get_data_array(cm["variables"])
    if arr is None:
        die("[!] Game_Variables 里没有 @data")
    items = arr.value
    data = path.read_bytes()

    patches: List[Dict[str, Any]] = []
    resizing = False
    for idx, value in assignments:
        if idx < 0 or idx >= len(items):
            print(f"  [!] 变量 {idx} 越界，跳过")
            continue
        node = items[idx]
        new_bytes = encode_int(value)
        # 定位该整数节点在文件中的实际字节范围
        start = node.pos
        end = node.end
        current = data[start:end]
        if current == new_bytes:
            continue
        if len(current) != len(new_bytes):
            resizing = True
        patches.append({
            "offset": start,
            "before_hex": current.hex(),
            "after_hex": new_bytes.hex(),
            "require_before": True,
            "note": f"variable[{idx}] -> {value}",
        })

    plan = {
        "kind": "allcg-plan",
        "version": 1,
        "created": datetime.now().isoformat(timespec="seconds"),
        "target": str(path),
        "sha256_before": sha256(data),
        "engine": "rgss3-variables",
        "description": f"RGSS 变量赋值（{len(patches)} 项）",
        "inference": {"assignments": assignments, "may_resize": resizing},
        "patches": patches,
        "backup_path": None,
    }
    print(f"# 变量计划：待写入 {len(patches)} 项"
          + ("（部分值会让文件长度变化）" if resizing else "（等长替换）"))
    dump_json(out, plan)
    print(f"[+] 已写出 {out}")
    if resizing:
        print("    注意：长度会变化，apply 时需要 --allow-resize")
    return 0


def parse_assignments(text: str) -> List[Tuple[int, int]]:
    out = []
    for part in text.split(","):
        part = part.strip()
        if not part or "=" not in part:
            die(f"[!] --set 的格式应为 ID=值，收到：{part}")
        k, v = part.split("=", 1)
        out.append((int(k.strip()), int(v.strip())))
    return out


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="RGSS(RPG Maker XP/VX/VX Ace) 存档检查与解锁计划生成")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("inspect", help="查看存档结构与开关/变量状态")
    p1.add_argument("save")
    p1.add_argument("--show-true", type=int, default=40,
                    help="最多列出多少个已 ON 的开关 ID（默认 40）")

    p2 = sub.add_parser("plan-switches", help="生成把开关置 ON 的解锁计划")
    p2.add_argument("save")
    p2.add_argument("--ids", help="要置 ON 的开关 ID，如 1,3,5-20")
    p2.add_argument("--all", action="store_true", help="置全部已分配槽位为 ON")
    p2.add_argument("--out", required=True, help="输出计划 JSON")
    p2.add_argument("--note", help="计划说明文字")

    p3 = sub.add_parser("plan-variables", help="生成变量赋值计划")
    p3.add_argument("save")
    p3.add_argument("--set", required=True, help="如 41=1,42=3")
    p3.add_argument("--out", required=True)

    args = ap.parse_args(argv)
    save = require_abs(args.save)
    if not save.exists():
        die(f"[!] 存档不存在：{save}")

    if args.cmd == "inspect":
        return cmd_inspect(save, args.show_true)
    if args.cmd == "plan-switches":
        ids = setify(args.ids)
        return cmd_plan_switches(save, ids, args.all,
                                 Path(args.out).resolve(), args.note or "")
    if args.cmd == "plan-variables":
        return cmd_plan_variables(save, parse_assignments(args.set),
                                  Path(args.out).resolve())
    return 1


if __name__ == "__main__":
    sys.exit(main())
