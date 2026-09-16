#!/usr/bin/env python3
"""
自动分块脚本（以章节边界优先）
用法: python split_chunks.py --input novel.txt --output_dir ./chunks --max_chars 80000
"""

import re
import argparse
from pathlib import Path

from chapter_patterns import CHUNK_CHAPTER_PATTERN


def split_by_paragraphs(text, max_chars):
    """无章节文件按段落边界切分"""
    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        # 计算块结束位置
        end = min(start + max_chars, text_len)

        if end < text_len:
            # 回溯到最近的段落边界（两个换行符）
            search_start = max(start, end - 200)
            paragraph_break = text.rfind('\n\n', search_start, end)
            if paragraph_break != -1:
                end = paragraph_break + 2  # 保留两个换行符
            else:
                # 如果没有段落边界，回溯到最近的换行符
                line_break = text.rfind('\n', search_start, end)
                if line_break != -1:
                    end = line_break + 1

        chunks.append(text[start:end])
        start = end

    return chunks


def split_by_chapters(text, max_chars=80000):
    """按章节边界分块，保持章节完整性"""
    chapters = list(CHUNK_CHAPTER_PATTERN.finditer(text))

    if not chapters:
        # 无章节，按段落边界切分
        return split_by_paragraphs(text, max_chars)

    chunks = []
    chunk_start = 0

    for i in range(1, len(chapters)):
        if chapters[i].start() - chunk_start > max_chars:
            split_pos = chapters[i - 1].start()
            chunk_text = text[chunk_start:split_pos]
            chunks.append(chunk_text)
            chunk_start = split_pos

    # 最后一块
    chunks.append(text[chunk_start:])

    return chunks


def main():
    parser = argparse.ArgumentParser(description='按章节边界分块小说文件')
    parser.add_argument('--input', required=True, help='输入小说文件路径')
    parser.add_argument('--output_dir', required=True, help='分块输出目录')
    parser.add_argument('--max_chars', type=int, default=80000, help='每块最大字符数，默认80000')
    parser.add_argument('--prefix', default='part', help='分块文件名前缀，默认part')
    parser.add_argument('--context_notes', action='store_true', default=True,
                        help='在每块开头添加上下文注释')
    args = parser.parse_args()

    with open(args.input, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()

    chunks = split_by_chapters(text, args.max_chars)

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    total_chars = 0
    for i, chunk in enumerate(chunks, 1):
        out_file = out_dir / f"{args.prefix}{i}.txt"

        # 在块开头添加上下文注释（仅对第2块及以后）
        if args.context_notes and i > 1:
            prev_chunk = chunks[i - 2] if i - 2 >= 0 else ''
            if prev_chunk:
                context = prev_chunk[-200:] if len(prev_chunk) > 200 else prev_chunk
                chapter_match = CHUNK_CHAPTER_PATTERN.search(context)
                if chapter_match:
                    context_note = f"<!-- 上下文提示：上一块结束于“{chapter_match.group(0).strip()}”附近 -->\n\n"
                    chunk = context_note + chunk

        with open(out_file, 'w', encoding='utf-8') as f:
            f.write(chunk)
        total_chars += len(chunk)
        print(f"分块 {i}: {len(chunk)} 字符 -> {out_file}")

    print(f"\n共 {len(chunks)} 个分块，总字符数: {total_chars}")
    print(f"原文总字符数: {len(text)}")


if __name__ == '__main__':
    main()