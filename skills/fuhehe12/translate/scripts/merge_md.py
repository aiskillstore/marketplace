#!/usr/bin/env python3
"""
merge_md.py — 合并翻译后的 Markdown 片段文件 + 格式校验

用法：
    python merge_md.py --manifest _split_manifest.json --output output_zh.md

读取 _split_manifest.json，按编号顺序合并 _part_NN_zh.md 片段，
然后执行格式校验并输出报告。
"""

import argparse
import io
import json
import re
import sys
from pathlib import Path

# Windows 下强制 UTF-8 输出，避免 GBK 编码错误
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


def parse_args():
    parser = argparse.ArgumentParser(description="合并翻译后的 Markdown 片段并校验格式")
    parser.add_argument("--manifest", required=True, help="拆分清单文件路径（_split_manifest.json）")
    parser.add_argument("--output", required=True, help="合并输出文件路径")
    parser.add_argument("--suffix", default="_zh", help="翻译文件后缀（默认 _zh）")
    return parser.parse_args()


def load_manifest(manifest_path: str) -> dict:
    """加载拆分清单。"""
    path = Path(manifest_path)
    if not path.exists():
        print(f"错误：清单文件不存在 - {manifest_path}", file=sys.stderr)
        sys.exit(1)
    return json.loads(path.read_text(encoding="utf-8"))


def get_translated_filename(original: str, suffix: str) -> str:
    """从原始片段文件名生成翻译文件名。"""
    # _part_01.md → _part_01_zh.md
    stem = Path(original).stem
    return f"{stem}{suffix}.md"


def merge_parts(manifest: dict, manifest_dir: Path, suffix: str) -> tuple[str, list[str]]:
    """
    按顺序合并所有翻译片段。
    返回 (合并内容, 错误列表)。
    """
    errors = []
    merged_parts = []

    for part_info in manifest["parts"]:
        original_file = part_info["file"]
        translated_file = get_translated_filename(original_file, suffix)
        translated_path = manifest_dir / translated_file

        if not translated_path.exists():
            errors.append(f"缺失翻译文件：{translated_file}（对应 {original_file}）")
            continue

        content = translated_path.read_text(encoding="utf-8")
        merged_parts.append(content)

    if errors:
        return "", errors

    # 合并时确保片段之间有换行分隔
    merged = ""
    for i, part in enumerate(merged_parts):
        if i > 0:
            # 确保前一片段末尾和当前片段开头之间只有一个空行
            if not merged.endswith("\n\n"):
                if merged.endswith("\n"):
                    merged += "\n"
                else:
                    merged += "\n\n"
        merged += part

    return merged, []


def check_heading_continuity(lines: list[str]) -> list[dict]:
    """检查标题层级是否连续（不跳级）。"""
    issues = []
    in_code = False
    last_level = 0

    for i, line in enumerate(lines):
        stripped = line.strip()

        if stripped.startswith("```"):
            in_code = not in_code
            continue

        if in_code:
            continue

        match = re.match(r'^(#{1,6})\s+', stripped)
        if match:
            level = len(match.group(1))
            if last_level > 0 and level > last_level + 1:
                issues.append({
                    "line": i + 1,
                    "type": "heading_skip",
                    "message": f"标题层级跳跃：从 H{last_level} 直接到 H{level}",
                    "content": stripped[:80]
                })
            last_level = level

    return issues


def check_code_blocks(lines: list[str]) -> list[dict]:
    """检查代码块是否闭合（``` 成对出现）。"""
    issues = []
    open_positions = []

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("```"):
            if open_positions:
                open_positions.pop()  # 闭合一个代码块
            else:
                open_positions.append(i + 1)  # 开启一个代码块

    for pos in open_positions:
        issues.append({
            "line": pos,
            "type": "unclosed_code_block",
            "message": f"未闭合的代码块（第 {pos} 行开始）",
            "content": lines[pos - 1].strip()[:80]
        })

    return issues


def check_links(lines: list[str]) -> list[dict]:
    """检查链接格式是否完整。"""
    issues = []
    in_code = False

    for i, line in enumerate(lines):
        stripped = line.strip()

        if stripped.startswith("```"):
            in_code = not in_code
            continue

        if in_code:
            continue

        # 检查断裂的链接：有 [text] 但下一行以 (url 开头
        # 使用更精确的模式，避免假阳性
        broken = re.findall(r'\[([^\]^\[]+)\]\s*$', line)
        for match in broken:
            # 排除脚注定义 [^note]
            if match.startswith('^'):
                continue
            # 排除复选框
            if match.strip() in ('x', 'X', ' ', ''):
                continue
            # 确认下一行以 (url) 开头才报告
            if i + 1 < len(lines) and re.match(r'^\s*\(', lines[i + 1]):
                issues.append({
                    "line": i + 1,
                    "type": "broken_link",
                    "message": f"链接可能断裂跨行：[{match[:40]}]",
                    "content": line.strip()[:80]
                })

    return issues


def validate_markdown(content: str) -> list[dict]:
    """执行所有格式校验，返回问题列表。"""
    lines = content.splitlines(keepends=True)
    # 对于校验函数，使用不带换行符的行
    plain_lines = content.splitlines()

    all_issues = []
    all_issues.extend(check_heading_continuity(plain_lines))
    all_issues.extend(check_code_blocks(plain_lines))
    all_issues.extend(check_links(plain_lines))

    # 按行号排序
    all_issues.sort(key=lambda x: x["line"])
    return all_issues


def format_report(issues: list[dict]) -> str:
    """格式化校验报告。"""
    if not issues:
        return "[PASS] 格式校验通过，未发现问题。"

    report_lines = [f"共发现 {len(issues)} 个潜在问题：", ""]

    type_labels = {
        "heading_skip": "标题跳级",
        "unclosed_code_block": "代码块未闭合",
        "broken_link": "链接断裂",
    }

    for issue in issues:
        label = type_labels.get(issue["type"], issue["type"])
        report_lines.append(f"  行 {issue['line']} [{label}] {issue['message']}")
        if issue.get("content"):
            report_lines.append(f"    → {issue['content']}")

    return "\n".join(report_lines)


def main():
    args = parse_args()
    manifest_path = Path(args.manifest).resolve()
    manifest_dir = manifest_path.parent
    output_path = Path(args.output).resolve()

    # 加载清单
    manifest = load_manifest(str(manifest_path))
    print(f"源文件：{manifest['source']}")
    print(f"片段数：{manifest['parts_count']}")

    # 合并片段
    content, merge_errors = merge_parts(manifest, manifest_dir, args.suffix)

    if merge_errors:
        print("\n合并失败：", file=sys.stderr)
        for err in merge_errors:
            print(f"  - {err}", file=sys.stderr)
        sys.exit(1)

    # 写入合并文件
    output_path.write_text(content, encoding="utf-8")
    merged_lines = content.splitlines()
    print(f"合并完成：{len(merged_lines)} 行 → {output_path.name}")

    # 格式校验
    print("\n--- 格式校验报告 ---")
    issues = validate_markdown(content)
    report = format_report(issues)
    print(report)

    # 以退出码反映是否有问题（0=无问题，1=有问题但已合并）
    if issues:
        # 有问题但文件已成功合并，使用退出码 0 但在输出中标明
        print(f"\n文件已合并至：{output_path}")
        print("请根据上述报告检查并修复问题。")
    else:
        print(f"\n文件已合并至：{output_path}")


if __name__ == "__main__":
    main()
