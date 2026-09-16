#!/usr/bin/env python3
"""
合并后统一重新编号为 1-N 连续
用法: python renumber.py --input input.txt --output output.txt
"""

import os
import re
import argparse
from pathlib import Path

# 导入公共正则
from chapter_patterns import CHAPTER_PATTERN, SPECIAL_CHAPTERS


def renumber_chapters(text):
    """重新编号为 1-N 连续，特殊章节保留原名"""
    regular_positions = []

    for match in CHAPTER_PATTERN.finditer(text):
        line = match.group(0)
        if not SPECIAL_CHAPTERS.match(line):
            regular_positions.append(match)

    if not regular_positions:
        return text, 0

    for idx, match in enumerate(reversed(regular_positions), 1):
        old = match.group(0)
        title_content = re.sub(
            r'^\s*(?:第[零一二三四五六七八九十百千万]+|\d+)[章回节]\s*',
            '',
            old
        )
        new_num = len(regular_positions) - idx + 1
        if title_content.strip():
            new_title = f"第{new_num}章 {title_content.strip()}"
        else:
            new_title = f"第{new_num}章"
        text = text[:match.start()] + new_title + text[match.end():]

    return text, len(regular_positions)


def process_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    final, count = renumber_chapters(content)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final)

    print(f"处理完成: {input_path} -> {output_path} (章节数: {count})")
    return count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True, help='输入文件路径')
    parser.add_argument('--output', required=True, help='输出文件路径')
    args = parser.parse_args()

    process_file(Path(args.input), Path(args.output))


if __name__ == '__main__':
    main()