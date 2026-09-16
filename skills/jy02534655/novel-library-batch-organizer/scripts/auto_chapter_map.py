#!/usr/bin/env python3
"""
半规整层自动映射：对候选行已是标准格式的小说，自动生成 mapping 并 apply
支持：第X章、Chapter X、一、 等格式
用法: python auto_chapter_map.py --input "NovelLibrary_Temp/分类/书名.txt"
"""

import re
import sys
import json
import argparse
from pathlib import Path

# 导入公共正则和工具函数
from chapter_patterns import (
    CANDIDATE_REGEX,
    CHAPTER_START_REGEX,
    chinese_to_number
)


def read_file_safe(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()


def extract_candidates(text):
    lines = text.splitlines()
    candidates = []
    for i, line in enumerate(lines):
        if CANDIDATE_REGEX.match(line):
            stripped = line.strip()
            if len(stripped) >= 2:
                candidates.append({'index': i, 'line': stripped})
    return candidates


def build_mapping(candidates):
    """扩展映射逻辑，支持 第X章、Chapter X、一、 格式，保留原标题内容"""
    mapping = []
    skipped = []

    for cand in candidates:
        line = cand['line']

        # 匹配 "第X章 标题" 格式
        m = re.match(r'^第([零一二三四五六七八九十百千\d]+)[章回节](?:\s+(.*))?$', line)
        if m:
            num_str = m.group(1)
            title = m.group(2) or ''
            num = int(num_str) if num_str.isdigit() else chinese_to_number(num_str)
            if num is not None:
                if title:
                    mapping.append({'original': line, 'new': f'第{num}章 {title}'})
                else:
                    mapping.append({'original': line, 'new': f'第{num}章'})
                continue

        # 匹配 "Chapter X 标题" 格式（修复：保留标题）
        m = re.match(r'^Chapter\s*(\d+)(?:\s+(.*))?$', line, re.IGNORECASE)
        if m:
            num = int(m.group(1))
            title = m.group(2) or ''
            if title:
                mapping.append({'original': line, 'new': f'第{num}章 {title}'})
            else:
                mapping.append({'original': line, 'new': f'第{num}章'})
            continue

        # 匹配 "一、标题" 格式（修复：保留标题）
        m = re.match(r'^([零一二三四五六七八九十百千\d]+)[、．.]\s*(.*)$', line)
        if m:
            num_str = m.group(1)
            title = m.group(2) or ''
            num = int(num_str) if num_str.isdigit() else chinese_to_number(num_str)
            if num is not None:
                if title:
                    mapping.append({'original': line, 'new': f'第{num}章 {title}'})
                else:
                    mapping.append({'original': line, 'new': f'第{num}章'})
                continue

        skipped.append(line)

    return mapping, skipped


def apply_mapping(text, mapping):
    for item in reversed(mapping):
        orig = item.get('original', '').strip()
        new = item.get('new', '')
        if not orig or not new:
            continue
        pattern = re.compile(r'^\s*' + re.escape(orig) + r'\s*$', re.MULTILINE)
        text = pattern.sub(new, text)
    return text


def process(input_path, temp_dir='./NovelLibrary_Temp', output_dir='./NovelLibrary_Processed'):
    input_path = Path(input_path).resolve()
    temp_path = Path(temp_dir).resolve()
    output_path = Path(output_dir).resolve()

    try:
        rel_path = input_path.relative_to(temp_path)
    except ValueError:
        print(f"错误: 输入文件 {input_path} 不在临时目录 {temp_path} 下")
        return False

    content = read_file_safe(input_path)
    candidates = extract_candidates(content)
    if not candidates:
        print('未检测到候选章节行，跳过自动映射')
        return False

    mapping, skipped = build_mapping(candidates)
    if not mapping:
        print('未能生成可自动映射的章节，跳过')
        return False

    mapping_path = input_path.parent / f'{input_path.stem}_mapping.json'
    mapping_data = {
        'book_name': input_path.stem,
        'mapping': mapping,
        'total_chapters': len(mapping),
        'skipped': skipped,
    }
    mapping_path.parent.mkdir(parents=True, exist_ok=True)
    with open(mapping_path, 'w', encoding='utf-8') as f:
        json.dump(mapping_data, f, ensure_ascii=False, indent=2)

    final = apply_mapping(content, mapping)

    output_file = output_path / rel_path
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(final)

    print(f'映射表已生成: {mapping_path}')
    print(f'处理完成: {output_file}')
    print(f'章节数: {len(mapping)}')
    if skipped:
        print(f'跳过候选: {len(skipped)}')
    return True


def main():
    parser = argparse.ArgumentParser(description='半规整层自动映射')
    parser.add_argument('--input', required=True, help='输入文件路径（临时目录下）')
    parser.add_argument('--temp', default='./NovelLibrary_Temp', help='临时目录路径')
    parser.add_argument('--output', default='./NovelLibrary_Processed', help='输出目录路径')
    args = parser.parse_args()

    success = process(args.input, args.temp, args.output)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()