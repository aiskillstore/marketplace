#!/usr/bin/env python3
"""Validate observable structure and references for one Skill directory."""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path


ASCII_NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FRONTMATTER_PATTERN = re.compile(r"\A---\s*\n(.*?)\n---(?:\s*\n|\Z)", re.DOTALL)
LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
TEXT_SUFFIXES = {".md", ".json", ".yaml", ".yml", ".py", ".sh", ".txt"}
UNFINISHED_MARKERS = ("[TODO", "TODO:", "FIXME", "{说明", "{写入", "{可观察", "<待填写>")
LOCAL_PATH_PATTERN = re.compile(r"(?:/Users/[^/\s]+/|/home/[^/\s]+/|[A-Za-z]:\\\\Users\\\\[^\\\s]+\\\\)")
SECRET_PATTERN = re.compile(
    r"(?i)(?:api[_-]?key|access[_-]?token|secret|password)\s*[:=]\s*['\"]?([A-Za-z0-9_\-]{16,})"
)
ALLOWED_ROOT_ENTRIES = {"SKILL.md", "agents", "references", "scripts", "assets", "evals"}


def is_cjk(character: str) -> bool:
    codepoint = ord(character)
    return (
        0x3400 <= codepoint <= 0x4DBF
        or 0x4E00 <= codepoint <= 0x9FFF
        or 0xF900 <= codepoint <= 0xFAFF
    )


def valid_skill_name(name: str) -> bool:
    if not 1 <= len(name) < 64:
        return False
    if ASCII_NAME_PATTERN.fullmatch(name):
        return True
    if not any(is_cjk(character) for character in name):
        return False
    return all(
        character.isalnum() or character in "-_：:（）()"
        for character in name
    )


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


def read_text(path: Path, errors: list[str]) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        errors.append(f"文本文件不是 UTF-8：{path}")
        return None


def check_markdown_links(root: Path, path: Path, text: str, errors: list[str]) -> None:
    for link in LINK_PATTERN.findall(text):
        target = link.split("#", 1)[0].strip().strip("<>")
        if not target or target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        if target.startswith("/"):
            errors.append(f"引用使用了绝对路径：{path.relative_to(root)} -> {target}")
            continue
        resolved = (path.parent / target).resolve()
        if root not in resolved.parents and resolved != root:
            errors.append(f"引用越出 Skill 目录：{path.relative_to(root)} -> {target}")
        elif not resolved.exists():
            errors.append(f"引用不存在：{path.relative_to(root)} -> {target}")


def main() -> int:
    parser = argparse.ArgumentParser(description="校验单个 Skill 项目")
    parser.add_argument("skill_directory")
    args = parser.parse_args()

    root = Path(args.skill_directory).expanduser().resolve()
    errors: list[str] = []
    warnings: list[str] = []
    skill_path = root / "SKILL.md"

    if not root.is_dir():
        print(f"ERROR：目录不存在：{root}")
        return 1
    if not skill_path.is_file():
        print(f"ERROR：缺少 {skill_path}")
        return 1

    text = skill_path.read_text(encoding="utf-8")
    match = FRONTMATTER_PATTERN.match(text)
    if match is None:
        errors.append("SKILL.md 缺少合法的 YAML frontmatter")
        frontmatter = ""
    else:
        frontmatter = match.group(1)

    name = read_scalar(frontmatter, "name")
    description = read_scalar(frontmatter, "description")
    if not valid_skill_name(name):
        errors.append(
            "name 必须少于 64 个字符；纯英文名只使用小写英文、数字和连字符，"
            "中文名可使用中文、字母、数字、连字符、下划线、冒号和括号"
        )
    if name and name != root.name:
        errors.append(f"目录名 {root.name!r} 与 name {name!r} 不一致")
    if not 1 <= len(description) <= 1024:
        errors.append(f"description 长度为 {len(description)}，规范范围是 1～1,024")
    elif len(description) > 300:
        warnings.append(f"description 长度为 {len(description)}，建议检查是否可以收紧")
    if description and not any(token in description.lower() for token in ("时使用", "用户", "当", "when", "use for", "used for")):
        warnings.append("description 可能只说明了能力，建议补充使用条件")

    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if path.is_symlink():
            errors.append(f"不允许悬空或外部软链接：{relative}")
            continue
        if path.is_dir():
            if not any(path.iterdir()):
                warnings.append(f"空目录没有产生功能：{relative}")
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        file_text = read_text(path, errors)
        if file_text is None:
            continue
        is_validator_source = path.resolve() == Path(__file__).resolve()
        if not is_validator_source:
            for marker in UNFINISHED_MARKERS:
                if marker in file_text:
                    errors.append(f"仍有未完成占位符：{relative} -> {marker}")
            if LOCAL_PATH_PATTERN.search(file_text):
                errors.append(f"包含本机用户绝对路径：{relative}")
            if SECRET_PATTERN.search(file_text):
                errors.append(f"包含疑似密钥或密码：{relative}")
        if path.suffix.lower() == ".md":
            check_markdown_links(root, path, file_text, errors)

    for entry in sorted(root.iterdir()):
        if entry.name not in ALLOWED_ROOT_ENTRIES:
            warnings.append(f"Skill 根目录存在非标准条目：{entry.name}")

    line_count = len(text.splitlines())
    if line_count > 300:
        warnings.append(f"SKILL.md 共 {line_count} 行，建议检查渐进式披露")

    openai_path = root / "agents" / "openai.yaml"
    if openai_path.is_file():
        openai_text = openai_path.read_text(encoding="utf-8")
        if name and f"${name}" not in openai_text:
            errors.append("agents/openai.yaml 的 default_prompt 未显式包含 Skill 名")
        short_match = re.search(r'^\s+short_description:\s*["\'](.*)["\']\s*$', openai_text, re.MULTILINE)
        if short_match and not 25 <= len(short_match.group(1)) <= 64:
            errors.append("agents/openai.yaml 的 short_description 应为 25～64 个字符")
        display_match = re.search(r'^\s+display_name:\s*["\'](.*)["\']\s*$', openai_text, re.MULTILINE)
        if display_match and name and display_match.group(1) != name:
            errors.append("agents/openai.yaml 的 display_name 与 frontmatter name 不一致")

    scripts_dir = root / "scripts"
    if scripts_dir.is_dir():
        for script in sorted(scripts_dir.rglob("*.py")):
            try:
                compile(script.read_text(encoding="utf-8"), str(script), "exec")
            except SyntaxError as error:
                errors.append(f"Python 语法错误：{script.relative_to(root)}：{error}")
        for script in sorted(scripts_dir.rglob("*.sh")):
            result = subprocess.run(
                ["bash", "-n", str(script)],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode:
                detail = result.stderr.strip() or "bash -n 失败"
                errors.append(f"Shell 语法错误：{script.relative_to(root)}：{detail}")

    for warning in warnings:
        print(f"WARNING：{warning}")
    for error in errors:
        print(f"ERROR：{error}")

    if errors:
        print(f"校验失败：{len(errors)} 个错误，{len(warnings)} 个提醒。")
        return 1
    print(f"校验通过：{root}（{len(warnings)} 个提醒）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
