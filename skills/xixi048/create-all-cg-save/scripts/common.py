#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
common.py —— create-all-cg-save 各脚本共用的安全与 IO 工具。

贯穿全技能的三条硬规矩：
  1. 任何写操作默认先备份，备份永远落到独立文件，不做原地覆盖。
  2. 目标文件必须是绝对路径 —— 避免在错误的 cwd 下动错文件。
  3. 只读归档字段可以缺失/为空，但"把用户存档弄坏"是不可接受的，
     因此统一提供 sha256 前后校验与一键回滚。
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

# 出现这些标记时提示用户"目标可能不是存档"
NOT_SAVE_HINTS = (".exe", ".dll", ".zip", ".7z", ".rar", ".mp4", ".png", ".jpg")


def stderr(msg: str) -> None:
    # 先 flush stdout，避免警告和进度输出交错打乱顺序（管道/重定向时尤其明显）
    sys.stdout.flush()
    print(msg, file=sys.stderr)
    sys.stderr.flush()


def die(msg: str, code: int = 2) -> "None":
    stderr(msg)
    sys.exit(code)


def require_abs(path: str) -> Path:
    p = Path(path)
    if not p.is_absolute():
        die(f"[!] 必须使用绝对路径，收到：{path}")
    return p


def read_bytes(path: Path) -> bytes:
    return path.read_bytes()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def human_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.0f}{unit}" if unit == "B" else f"{n:.1f}{unit}"
        n /= 1024.0
    return f"{n:.1f}GB"


def stamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def backup_path(target: Path) -> Path:
    """备份文件路径：<name>.allcg-bak-<timestamp>"""
    return target.with_name(f"{target.name}.allcg-bak-{stamp()}")


def make_backup(target: Path) -> Path:
    dst = backup_path(target)
    shutil.copy2(target, dst)
    return dst


def atomic_write(target: Path, data: bytes) -> None:
    """先写临时文件再替换，避免写到一半崩溃留下半截存档。"""
    tmp = target.with_name(target.name + ".allcg-tmp")
    tmp.write_bytes(data)
    os.replace(tmp, target)


def load_json(path: Path) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def dump_json(path: Path, obj: Any, indent: int = 2) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=indent)


def hexdump(data: bytes, base: int = 0, limit: int = 16) -> str:
    out = []
    for i in range(0, len(data), limit):
        chunk = data[i:i + limit]
        hexpart = " ".join(f"{b:02x}" for b in chunk)
        asc = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        out.append(f"{base + i:08x}  {hexpart:<{limit * 3}}  |{asc}|")
    return "\n".join(out)


def plausible_text(data: bytes, min_ratio: float = 0.6) -> bool:
    """粗略判断一段字节是否像可打印文本。"""
    if not data:
        return False
    printable = sum(1 for b in data if 32 <= b < 127 or b in (9, 10, 13))
    return printable / len(data) >= min_ratio


def setify(values: Optional[str]) -> Optional[List[int]]:
    """把 '1,3,5-9' 解析成整数列表。"""
    if not values:
        return None
    out: List[int] = []
    for part in values.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            lo, hi = part.split("-", 1)
            out.extend(range(int(lo), int(hi) + 1))
        else:
            out.append(int(part))
    return sorted(set(out))


def confirm_target_for_write(target: Path, allow_missing: bool = False) -> None:
    if not allow_missing and not target.exists():
        die(f"[!] 目标文件不存在：{target}")
    if not target.is_file():
        die(f"[!] 目标不是普通文件：{target}")
    if target.stat().st_size == 0:
        die(f"[!] 目标文件为空，拒绝处理：{target}")


def report(title: str, lines: Iterable[str]) -> None:
    print(f"=== {title} ===")
    for line in lines:
        print("  " + line)
