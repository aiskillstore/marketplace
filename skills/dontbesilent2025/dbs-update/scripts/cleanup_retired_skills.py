#!/usr/bin/env python3
"""清理本机残留的已下线 dbskill Skill。

只处理 references/retired-skills.json 中登记的名称，并且只处理能确认来自官方的副本：
- 失效链接（目标已不存在）：移除链接；
- 指向官方历史版本的链接或目录联接：只移除链接本身，不碰目标；
- 内容与官方历史版本完全一致的目录：移到 ~/.dbs/retired-skills/<时间>/ 备份，不直接删除；
- 本工具生成、且真源已不存在的 Grok 适配层：同样移到备份目录。
内容被改过、指向其他来源或无法识别的同名项一律保留，并在结果中列出。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import time
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
RETIRED_PATH = SCRIPT_DIR.parent / "references" / "retired-skills.json"

# 与 dbs-install-skill 支持的 Agent 目录保持一致，含已停止维护的旧目录。
AGENT_SKILL_DIRS = (
    ".agents", ".claude", ".codex", ".workbuddy", ".hermes", ".kiro", ".qwen", ".cline",
    ".aider-desk", ".augment", ".codeartsdoer", ".codebuddy", ".codemaker", ".codestudio",
    ".continue", ".copilot", ".cursor", ".factory", ".forge", ".gemini", ".junie",
    ".kilocode", ".openclaw", ".openhands", ".qoder", ".roo", ".trae", ".trae-cn",
    ".vibe", ".zencoder",
)


def normalized_sha256(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
    except OSError:
        return None


def is_link(path: Path) -> bool:
    return path.is_symlink() or (hasattr(os.path, "isjunction") and os.path.isjunction(path))


def remove_link(path: Path) -> None:
    if path.is_symlink():
        path.unlink()
    else:
        os.rmdir(path)  # Windows 目录联接：只移除联接本身


def grok_bridge_source(skill_file: Path) -> str | None:
    try:
        text = skill_file.read_text(encoding="utf-8")
    except OSError:
        return None
    if "## Grok Bridge" not in text:
        return None
    for line in text.splitlines():
        if line.startswith("- Source of truth: "):
            return line.removeprefix("- Source of truth: ").strip()
    return None


def plan_for(path: Path, name: str, known: set[str]) -> tuple[str, str]:
    """返回 (动作, 说明)。动作为 unlink、backup 或 keep。"""
    if is_link(path):
        target = Path(os.path.realpath(path))
        if not target.exists():
            return "unlink", "失效链接"
        if normalized_sha256(target / "SKILL.md") in known:
            return "unlink", f"指向官方旧版本的链接（{target}）"
        return "keep", f"链接指向其他内容（{target}）"
    if path.is_dir():
        skill_file = path / "SKILL.md"
        if normalized_sha256(skill_file) in known:
            return "backup", "与官方旧版本一致的副本"
        source = grok_bridge_source(skill_file)
        if source and source.replace("\\", "/").endswith(f"/skills/{name}/SKILL.md") and not Path(source).exists():
            return "backup", "真源已不存在的 Grok 适配层"
        return "keep", "内容与官方版本不一致，可能是你自己的同名 Skill"
    return "keep", "同名文件，不是 Skill 目录"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="只列出计划，不改动文件")
    parser.add_argument("--home", default=os.environ.get("DBS_INSTALL_HOME") or str(Path.home()))
    args = parser.parse_args()

    home = Path(args.home)
    retired = json.loads(RETIRED_PATH.read_text(encoding="utf-8")).get("skills", [])
    backup_root = home / ".dbs" / "retired-skills" / time.strftime("%Y%m%d-%H%M%S")
    result = {"dry_run": args.dry_run, "removed": [], "backed_up": [], "kept": [], "backup_dir": None}

    for entry in retired:
        name = entry["name"]
        known = set(entry.get("sha256", []))
        for agent in (*AGENT_SKILL_DIRS, ".grok"):
            path = home / agent / "skills" / name
            if not (path.exists() or is_link(path)):
                continue
            action, reason = plan_for(path, name, known)
            record = {"path": str(path), "reason": reason}
            if action == "keep":
                result["kept"].append(record)
                continue
            if action == "unlink":
                if not args.dry_run:
                    remove_link(path)
                result["removed"].append(record)
            else:
                destination = backup_root / agent.lstrip(".") / name
                if not args.dry_run:
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(path), str(destination))
                    result["backup_dir"] = str(backup_root)
                record["backup"] = str(destination)
                result["backed_up"].append(record)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
