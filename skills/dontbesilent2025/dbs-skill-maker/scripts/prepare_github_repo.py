#!/usr/bin/env python3
"""Prepare a local staging directory for a single-Skill GitHub repository."""

from __future__ import annotations

import argparse
import filecmp
import re
import shutil
from pathlib import Path


FRONTMATTER_PATTERN = re.compile(r"\A---\s*\n(.*?)\n---(?:\s*\n|\Z)", re.DOTALL)
ALLOWED_ENTRIES = ("SKILL.md", "agents", "references", "scripts", "assets")
EXCLUDED_NAMES = {".DS_Store", "__pycache__", "evals"}
OWNER_PATTERN = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$")
REPO_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")


def read_scalar(frontmatter: str, field: str) -> str:
    lines = frontmatter.splitlines()
    prefix = f"{field}:"
    for index, line in enumerate(lines):
        if not line.startswith(prefix):
            continue
        value = line[len(prefix) :].strip()
        if value not in {"|", ">"}:
            return value.strip("\"'")
        content: list[str] = []
        for continuation in lines[index + 1 :]:
            if continuation and not continuation[0].isspace():
                break
            content.append(continuation[2:] if continuation.startswith("  ") else continuation)
        return ("\n" if value == "|" else " ").join(content).strip()
    return ""


def copy_public_tree(source: Path, destination: Path) -> None:
    if source.is_symlink():
        raise SystemExit(f"拒绝复制软链，请先确认真实来源：{source}")
    if source.is_file():
        if source.name not in EXCLUDED_NAMES and source.suffix != ".pyc":
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        return

    destination.mkdir(parents=True, exist_ok=True)
    for child in sorted(source.iterdir()):
        if child.name in EXCLUDED_NAMES or child.suffix == ".pyc":
            continue
        copy_public_tree(child, destination / child.name)


def public_files(root: Path) -> dict[Path, Path]:
    files: dict[Path, Path] = {}
    for entry_name in ALLOWED_ENTRIES:
        entry = root / entry_name
        if not entry.exists():
            continue
        candidates = [entry] if entry.is_file() else sorted(entry.rglob("*"))
        for candidate in candidates:
            if candidate.is_symlink():
                raise SystemExit(f"拒绝打包软链接：{candidate}")
            if not candidate.is_file():
                continue
            if any(part in EXCLUDED_NAMES for part in candidate.relative_to(root).parts):
                continue
            if candidate.suffix == ".pyc":
                continue
            files[candidate.relative_to(root)] = candidate
    return files


def read_default_prompt(source: Path, name: str) -> str:
    openai_path = source / "agents" / "openai.yaml"
    if openai_path.is_file():
        match = re.search(r'^\s+default_prompt:\s*["\'](.*)["\']\s*$', openai_path.read_text(encoding="utf-8"), re.MULTILINE)
        if match:
            return match.group(1)
    return f"使用 ${name} 完成它所解决的任务。"


def detect_requirements(source: Path) -> list[str]:
    requirements = ["支持 Agent Skills 的客户端"]
    scripts = source / "scripts"
    if scripts.is_dir() and any(scripts.rglob("*.py")):
        requirements.append("Python 3（用于运行 Skill 内脚本）")
    if scripts.is_dir() and any(scripts.rglob("*.sh")):
        requirements.append("Bash（用于运行 Skill 内脚本）")
    openai_path = source / "agents" / "openai.yaml"
    if openai_path.is_file():
        text = openai_path.read_text(encoding="utf-8")
        for value in re.findall(r'^\s+value:\s*["\']?([^"\'\s]+)', text, re.MULTILINE):
            requirements.append(f"工具依赖：{value}")
    return requirements


def main() -> int:
    parser = argparse.ArgumentParser(description="准备单 Skill GitHub 仓库的本地 staging 目录")
    parser.add_argument("skill_directory")
    parser.add_argument("staging_directory")
    parser.add_argument("--owner", required=True)
    parser.add_argument("--repo", required=True)
    args = parser.parse_args()

    source = Path(args.skill_directory).expanduser().resolve()
    staging = Path(args.staging_directory).expanduser().resolve()
    owner = args.owner.strip()
    repo = args.repo.strip()
    if not source.is_dir():
        raise SystemExit(f"源 Skill 目录不存在：{source}")
    if not OWNER_PATTERN.fullmatch(owner):
        raise SystemExit("GitHub owner 格式无效")
    if not REPO_PATTERN.fullmatch(repo) or repo in {".", ".."}:
        raise SystemExit("GitHub repo 格式无效")
    skill_path = source / "SKILL.md"
    if not skill_path.is_file():
        raise SystemExit(f"源目录缺少 SKILL.md：{source}")
    if staging.exists():
        if not staging.is_dir():
            raise SystemExit(f"staging 路径已存在且不是目录：{staging}")
        if any(staging.iterdir()):
            raise SystemExit(f"staging 目录非空，未覆盖：{staging}")

    text = skill_path.read_text(encoding="utf-8")
    match = FRONTMATTER_PATTERN.match(text)
    if match is None:
        raise SystemExit("SKILL.md 缺少合法 frontmatter")
    name = read_scalar(match.group(1), "name")
    description = " ".join(read_scalar(match.group(1), "description").split())
    if not name or not description:
        raise SystemExit("SKILL.md 缺少 name 或 description")

    target_skill = staging / "skills" / name
    source_files = public_files(source)
    staging.mkdir(parents=True, exist_ok=True)
    for entry_name in ALLOWED_ENTRIES:
        entry = source / entry_name
        if entry.exists():
            copy_public_tree(entry, target_skill / entry_name)

    copied_files = public_files(target_skill)
    if set(source_files) != set(copied_files):
        missing = sorted(str(path) for path in set(source_files) - set(copied_files))
        extra = sorted(str(path) for path in set(copied_files) - set(source_files))
        raise SystemExit(f"打包资源清单不一致；缺少：{missing}；多出：{extra}")
    for relative, source_file in source_files.items():
        if not filecmp.cmp(source_file, copied_files[relative], shallow=False):
            raise SystemExit(f"打包后文件内容不一致：{relative}")

    locator = f"{owner}/{repo}"
    usage = read_default_prompt(source, name)
    requirement_lines = "\n".join(f"- {item}" for item in detect_requirements(source))
    readme = f"""# {name}

{description}

## 安装

```bash
npx -y skills add {locator} -g --all
```

## 使用

安装后，可以这样开始：

> {usage}

## 运行依赖

{requirement_lines}

## 内容

本仓库只发布运行这个 Skill 所需的文件。本地评测样本、预期答案和运行记录不包含在公开包中。
"""
    (staging / "README.md").write_text(readme, encoding="utf-8")
    (staging / ".gitignore").write_text(
        ".DS_Store\n__pycache__/\n*.pyc\nevals/\n",
        encoding="utf-8",
    )

    print(f"已准备：{staging}")
    print(f"安装命令：npx -y skills add {locator} -g --all")
    print("尚未创建远端仓库，也没有执行 git push。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
