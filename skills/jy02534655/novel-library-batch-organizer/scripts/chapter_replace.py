#!/usr/bin/env python3
"""
半规整层：提取候选章节行，根据映射表执行全文替换
用法: python chapter_replace.py --extract --input "NovelLibrary_Temp/分类/书名.txt"
      python chapter_replace.py --apply --input "NovelLibrary_Temp/分类/书名.txt" --mapping mapping.json
"""

import os
import re
import sys
import json
import argparse
from pathlib import Path

# 导入公共正则
from chapter_patterns import CANDIDATE_REGEX


def extract_candidates(text):
    lines = text.splitlines()
    candidates = []
    for i, line in enumerate(lines):
        if CANDIDATE_REGEX.match(line):
            stripped = line.strip()
            if len(stripped) >= 2:
                candidates.append({
                    'index': i,
                    'line': stripped,
                    'context': '\n'.join(lines[max(0, i-1):min(len(lines), i+2)])
                })
    return candidates


def apply_mapping(text, mapping):
    for item in reversed(mapping):
        orig = item.get('original', '').strip()
        new = item.get('new', '')
        if not orig or not new:
            continue
        pattern = re.compile(r'^\s*' + re.escape(orig) + r'\s*$', re.MULTILINE)
        text = pattern.sub(new, text)
    return text


def process_extract(input_path):
    with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    candidates = extract_candidates(content)

    output_path = Path(input_path).parent / f"{Path(input_path).stem}_candidates.txt"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"共提取 {len(candidates)} 个候选章节行\n")
        f.write("=" * 50 + "\n\n")
        for c in candidates:
            f.write(f"行号: {c['index']}\n")
            f.write(f"内容: {c['line']}\n")
            f.write(f"上下文:\n{c['context']}\n")
            f.write("-" * 30 + "\n")

    print(f"提取完成: {output_path}")
    print(f"候选行数: {len(candidates)}")
    return candidates


def process_apply(input_path, mapping_path, output_path=None, temp_dir='./NovelLibrary_Temp', output_dir='./NovelLibrary_Processed'):
    input_path = Path(input_path).resolve()
    temp_path = Path(temp_dir).resolve()
    output_path_root = Path(output_dir).resolve()

    with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    with open(mapping_path, 'r', encoding='utf-8') as f:
        mapping_data = json.load(f)

    mapping = mapping_data.get('mapping', [])
    if not mapping:
        print("映射表为空，直接复制原文件")
        final = content
    else:
        final = apply_mapping(content, mapping)

    if output_path is None:
        try:
            rel_path = input_path.relative_to(temp_path)
            output_path = output_path_root / rel_path
        except ValueError:
            output_path = input_path.parent / f"{input_path.stem}_processed.txt"
    else:
        output_path = Path(output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final)

    print(f"处理完成: {output_path}")
    print(f"替换章节数: {len(mapping)}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--extract', action='store_true', help='提取候选章节行')
    parser.add_argument('--apply', action='store_true', help='应用映射表执行替换')
    parser.add_argument('--input', required=True, help='输入文件路径（临时目录）')
    parser.add_argument('--mapping', help='映射表JSON文件路径')
    parser.add_argument('--output', help='输出文件路径（最终目录）')
    parser.add_argument('--temp', default='./NovelLibrary_Temp', help='临时目录路径')
    parser.add_argument('--output_dir', default='./NovelLibrary_Processed', help='输出目录路径')
    args = parser.parse_args()

    if args.extract:
        process_extract(Path(args.input))
    elif args.apply:
        if not args.mapping:
            print("请指定 --mapping")
            sys.exit(1)
        process_apply(
            Path(args.input),
            Path(args.mapping),
            Path(args.output) if args.output else None,
            args.temp,
            args.output_dir
        )
    else:
        print("请指定 --extract 或 --apply")


if __name__ == '__main__':
    main()