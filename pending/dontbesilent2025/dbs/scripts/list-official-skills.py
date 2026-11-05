#!/usr/bin/env python3
"""列出当前版本登记且已经安装的正式 dbskill Skill。"""

from __future__ import annotations

import json
import hashlib
import sys
from pathlib import Path


def find_project_root(start: Path) -> Path | None:
    for candidate in (start, *start.parents):
        if (candidate / ".claude-plugin" / "marketplace.json").is_file():
            return candidate
    return None


def read_frontmatter_description(skill_path: Path) -> str:
    lines = skill_path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        return ""

    for index, line in enumerate(lines[1:], start=1):
        if line == "---":
            break
        if not line.startswith("description:"):
            continue

        value = line.removeprefix("description:").strip()
        if value not in {"", "|", ">"}:
            return value.strip('"\'')

        parts: list[str] = []
        for continuation in lines[index + 1 :]:
            if continuation == "---" or (
                continuation and not continuation[0].isspace()
            ):
                break
            stripped = continuation.strip()
            if stripped:
                parts.append(stripped)
        return " ".join(parts)

    return ""


def read_frontmatter_handoff(skill_path: Path) -> str:
    """读取 metadata.dbs-handoff；没有时返回空字符串。"""
    lines = skill_path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        return ""
    in_metadata = False
    for index, line in enumerate(lines[1:], start=1):
        if line == "---":
            break
        if line.startswith("metadata:"):
            in_metadata = True
            continue
        if in_metadata and line and not line[0].isspace():
            in_metadata = False
        if not in_metadata or line.strip() != "dbs-handoff: |":
            continue
        key_indent = len(line) - len(line.lstrip())
        entries: list[str] = []
        for continuation in lines[index + 1 :]:
            if continuation == "---":
                break
            if not continuation.strip():
                continue
            if len(continuation) - len(continuation.lstrip()) <= key_indent:
                break
            entries.append(continuation.strip())
        return "\n".join(entries)
    return ""


def locate_installed_skill(name: str, search_roots: list[Path]) -> Path | None:
    """按 search_roots 的优先级返回第一份有效副本。

    search_roots 从高到低排列：项目 skills/、与 /dbs 同级的目录、各 Agent 的用户目录。
    名称不符的副本被忽略；多份有效副本内容不一致时选用优先级最高的一份，并在 stderr 报告冲突。
    """
    candidates = []
    for root in search_roots:
        candidate = root / name
        path = candidate / "SKILL.md"
        if not path.is_file():
            continue
        content = path.read_text(encoding="utf-8")
        if f"name: {name}\n" not in content:
            print(f"忽略定义名称不符的副本：{candidate}", file=sys.stderr)
            continue
        resolved = candidate.resolve()
        if resolved not in candidates:
            candidates.append(resolved)
    if not candidates:
        return None
    digests = {hashlib.sha256((x / "SKILL.md").read_bytes()).hexdigest() for x in candidates}
    if len(digests) != 1:
        others = "、".join(str(x) for x in candidates[1:])
        print(
            f"{name} 有多份内容不一致的副本，已选用 {candidates[0]}；其余副本：{others}",
            file=sys.stderr,
        )
    return candidates[0]


def load_catalog(skill_dir: Path, project_root: Path | None) -> list[dict[str, str]]:
    if project_root is not None:
        marketplace_path = project_root / ".claude-plugin" / "marketplace.json"
        marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
        return [
            {
                "name": plugin.get("name", ""),
                "description": plugin.get("description", ""),
            }
            for plugin in marketplace.get("plugins", [])
        ]

    snapshot_path = skill_dir / "references" / "official-skill-names.txt"
    if not snapshot_path.is_file():
        raise SystemExit("未找到 Marketplace 或正式 Skill 名称快照")
    return [
        {"name": line.strip(), "description": ""}
        for line in snapshot_path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def main() -> int:
    skill_dir = Path(__file__).resolve().parent.parent
    project_root = find_project_root(skill_dir)
    catalog = load_catalog(skill_dir, project_root)

    search_roots = [skill_dir.parent]
    if project_root is not None:
        search_roots.insert(0, project_root / "skills")
    user_root = Path.home()
    search_roots.extend(
        [
            user_root / ".agents" / "skills",
            user_root / ".codex" / "skills",
            user_root / ".claude" / "skills",
        ]
    )

    results: list[dict[str, str]] = []
    for entry in catalog:
        name = entry.get("name", "")
        if not name or name == "dbs" or "beta" in name or "private" in name:
            continue

        skill_dir_path = locate_installed_skill(name, [project_root / "skills"] if project_root is not None else search_roots)
        if skill_dir_path is None:
            continue
        skill_path = skill_dir_path / "SKILL.md"

        results.append(
            {
                "name": name,
                "description": read_frontmatter_description(skill_path)
                or entry.get("description", ""),
                "handoff": read_frontmatter_handoff(skill_path),
                "source": str(skill_dir_path),
            }
        )

    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
