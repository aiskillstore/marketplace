#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
save_scout.py —— 在常见位置扫描某款单机游戏的候选存档，并顺带识别引擎。

解决问题的先后顺序是「先找到文件，再谈改文件」。常见存档位置（Windows）：

    %APPDATA% / %LOCALAPPDATA% / AppData\\LocalLow
    <用户>\\Documents / <用户>\\Saved Games
    Steam\\userdata\\<steamid>\\<appid>\\remote
    游戏安装目录自身（很多 RPG Maker 单机游戏的存档就在 exe 旁边）

用法
----
    python save_scout.py --game NTRPG2
    python save_scout.py --dir "D:/Games/<游戏>"
    python save_scout.py --game <名称> --changed-within 24   # 只看 24 小时内动过的
    python save_scout.py --game <名称> --json found.json

详细的引擎特征表见 references/engines.md。
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import human_size, load_json, sha256  # noqa: E402

# 存档候选文件名特征：强提示（几乎专属于存档）与弱提示（通用性的"数据"命名）
STRONG_NAME_HINTS = ("save", "slot", "persistent", "global", "progress",
                     "profile", "player", "record", "memory")
WEAK_NAME_HINTS = ("data", "config", "system", "user", "state", "rec")
SAVE_EXT = (
    ".rvdata2", ".rvdata", ".rxdata", ".save", ".sav", ".dat", ".bin",
    ".json", ".rpgsave", ".sav2", ".xml", ".dat.gz",
)
# 引擎专属存档扩展名 —— 命中基本可以断定就是存档
HIGH_CONF_EXT = (".rvdata2", ".rvdata", ".rxdata", ".rpgsave")
# 通用但常见的存档 / 状态文件扩展名
MID_CONF_EXT = (".save", ".sav", ".sav2", ".dat")
# 明确排除 —— 这些是游戏本体/资源，不是存档
EXCLUDE_EXT = (
    ".exe", ".dll", ".rpa", ".rgss3a", ".rgss2a", ".rgssad", ".xp3",
    ".pak", ".mp3", ".ogg", ".png", ".jpg", ".webm", ".png_",
)
MAX_FILES = 8000
MAX_DEPTH = 6


def candidate_roots() -> Dict[str, Path]:
    env = os.environ
    home = Path.home()
    roots: Dict[str, Path] = {}

    def add(name: str, value: Optional[str]) -> None:
        if not value:
            return
        p = Path(os.path.expandvars(value))
        if p.exists():
            roots[name] = p

    add("appdata_roaming", env.get("APPDATA"))
    add("appdata_local", env.get("LOCALAPPDATA"))
    add("appdata_locallow", str(home / "AppData" / "LocalLow"))
    add("home", str(home))
    add("documents", str(home / "Documents"))
    add("saved_games", str(home / "Saved Games"))
    return roots


def steam_userdata_roots() -> List[Path]:
    out: List[Path] = []
    for key in ("ProgramFiles(x86)", "ProgramFiles"):
        base = os.environ.get(key)
        if not base:
            continue
        candidate = Path(base) / "Steam" / "userdata"
        if candidate.exists():
            out.append(candidate)
    return out


def iter_files(root: Path, depth: int = 0) -> Iterable[Path]:
    if depth > MAX_DEPTH:
        return
    try:
        entries = list(root.iterdir())
    except (PermissionError, OSError):
        return
    for entry in entries:
        if entry.is_dir():
            yield from iter_files(entry, depth + 1)
        elif entry.is_file():
            yield entry


def score_file(f: Path, keyword: Optional[str],
               game_dir: Optional[Path] = None) -> Optional[int]:
    name = f.name.lower()
    ext = f.suffix.lower()
    if ext in EXCLUDE_EXT:
        return None
    score = 0
    # 分档：引擎专属存档扩展名的可信度远高于通用 .dat/.sav
    if ext in HIGH_CONF_EXT:
        score += 60
    elif ext in MID_CONF_EXT:
        score += 25
    elif ext in SAVE_EXT:
        score += 15
    elif ext == "":
        score += 5
    if any(h in name for h in STRONG_NAME_HINTS):
        score += 25
    elif any(h in name for h in WEAK_NAME_HINTS):
        score += 8
    if keyword and keyword.lower() in str(f).lower():
        score += 60
    # 位于游戏安装目录之下的，权重大幅提升
    if game_dir:
        try:
            f.relative_to(game_dir)
            score += 50
        except ValueError:
            pass
    size = f.stat().st_size
    if 0 < size < 512:
        score -= 20          # 太小的多半是配置文件而非存档
    elif size > 200 * 1024 * 1024:
        score -= 30
    return score if score >= 40 else None


def detect_engine_from_dir(d: Path) -> Optional[str]:
    """用少量目录特征快速判定引擎。详细特征表见 references/engines.md。"""
    try:
        names = {p.name.lower() for p in d.iterdir() if p.is_file()}
        dirs = {p.name.lower() for p in d.iterdir() if p.is_dir()}
    except OSError:
        return None
    if {"www", "js"} & dirs or "package.json" in names:
        return "RPG Maker MV/MZ (NW.js)"
    if ("game.exe" in names and "game.rgss3a" in names) or \
            any(n.endswith(".rvdata2") for n in names):
        return "RPG Maker VX Ace (RGSS3)"
    if "game.rgss2a" in names or "game.ini" in names and \
            any(n.endswith(".rvdata") for n in names):
        return "RPG Maker VX (RGSS2)"
    if "rgss100j.dll" in names:
        return "RPG Maker XP (RGSS1)"
    if any(n.endswith(".xp3") for n in names) or "krkr.itera" in names:
        return "Kirikiri / KAG"
    if any(n.endswith(".rpa") for n in names) or "renpy" in dirs:
        return "Ren'Py"
    if any(n.endswith("_data") for n in dirs) and "unityplayer.dll" in names:
        return "Unity"
    if any(n in dirs for n in ("content", "paks")):
        return "Unreal Engine"
    if any(n.endswith(".cpk") for n in names) or "gamedata0.pak" in names:
        return "Siglus"
    if any(n.endswith(".arc") for n in names) or "bd.bgi" in names:
        return "BGI / Ethornell"
    if any(n.endswith(".cs2") for n in names):
        return "CatSystem2"
    return None


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="扫描本地单机游戏的候选存档文件")
    ap.add_argument("--game", help="游戏名关键词（会匹配路径任意一段）")
    ap.add_argument("--dir", help="游戏安装目录（顺带做引擎识别）")
    ap.add_argument("--extra-root", action="append", default=[],
                    help="额外的搜索根目录，可重复指定")
    ap.add_argument("--changed-within", type=float,
                    help="只列出最近 N 小时内修改过的文件")
    ap.add_argument("--top", type=int, default=20, help="最多列出多少条")
    ap.add_argument("--json", help="输出结果的 JSON 路径")
    args = ap.parse_args(argv)

    if not any([args.game, args.dir, args.extra_root]):
        ap.error("至少提供 --game / --dir / --extra-root 中的一个")

    game_root: Optional[Path] = None
    if args.dir:
        d = Path(args.dir)
        if not d.exists():
            print(f"[!] 目录不存在：{d}")
        else:
            engine = detect_engine_from_dir(d)
            game_root = d.resolve()
            print(f"# 安装目录：{d}")
            print(f"  引擎判断：{engine or '未识别（参见 references/engines.md）'}")

    roots: Dict[str, Path] = {}
    # 游戏安装目录永远最先扫 —— 默认根目录下文件量极大，
    # 很容易在触及扫描上限之前就没机会扫到真正要找的存档。
    if args.dir:
        roots["game_dir"] = Path(args.dir)
    roots.update(candidate_roots())
    for extra in args.extra_root:
        p = Path(extra)
        if p.exists():
            roots[f"extra:{p.name}"] = p
    for sd in steam_userdata_roots():
        roots["steam_userdata"] = sd

    print(f"# 扫描根目录 {len(roots)} 个：{', '.join(sorted(roots))}")

    found: List[Dict[str, Any]] = []
    scanned = 0
    truncated = False
    now = time.time()
    for label, root in roots.items():
        for f in iter_files(root):
            scanned += 1
            if scanned > MAX_FILES:
                truncated = True
                break
            if args.game and args.game.lower() not in str(f).lower():
                # 关键词优先但仍保留命中的 Save name 特征
                if not any(h in f.name.lower() for h in ("save", "slot")):
                    continue
            try:
                st = f.stat()
            except OSError:
                continue
            age_h = (now - st.st_mtime) / 3600.0
            if args.changed_within and age_h > args.changed_within:
                continue
            s = score_file(f, args.game, game_root)
            if s is None:
                continue
            found.append({
                "path": str(f),
                "size": st.st_size,
                "size_human": human_size(st.st_size),
                "mtime": time.strftime("%Y-%m-%d %H:%M:%S",
                                       time.localtime(st.st_mtime)),
                "age_hours": round(age_h, 2),
                "score": s,
                "sha256_16": sha256(f.read_bytes())[:16],
                "root": label,
            })
        if scanned > MAX_FILES:
            break

    found.sort(key=lambda x: (-x["score"], -x["size"]))
    print(f"  已扫描 {scanned} 个文件，候选 {len(found)} 个"
          + ("（已触及扫描上限，建议用 --changed-within 或 --extra-root 缩小范围）"
             if truncated else "") + "\n")

    for item in found[:args.top]:
        print(f"  [{item['score']:>3}] {item['size_human']:>7}  "
              f"{item['mtime']}  {item['path']}")
    if len(found) > args.top:
        print(f"  …另有 {len(found) - args.top} 个候选")

    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(found, fh, ensure_ascii=False, indent=2)
        print(f"[+] 已写出 {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
