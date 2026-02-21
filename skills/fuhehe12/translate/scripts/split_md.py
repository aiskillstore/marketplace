#!/usr/bin/env python3
"""
split_md.py — 按语义边界拆分大 Markdown 文件

用法：
    python split_md.py input.md --max-lines 600 --min-lines 100 --output-dir ./_parts/

输出：
    _part_01.md, _part_02.md, ... + _split_manifest.json
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
    parser = argparse.ArgumentParser(description="按语义边界拆分大 Markdown 文件")
    parser.add_argument("input", help="输入 Markdown 文件路径")
    parser.add_argument("--max-lines", type=int, default=600, help="每个片段最大行数（默认 600）")
    parser.add_argument("--min-lines", type=int, default=100, help="每个片段最小行数（默认 100）")
    parser.add_argument("--output-dir", default="./_parts/", help="输出目录（默认 ./_parts/）")
    return parser.parse_args()


def read_lines(filepath: str) -> list[str]:
    """读取文件所有行，保留换行符。"""
    path = Path(filepath)
    if not path.exists():
        print(f"错误：文件不存在 - {filepath}", file=sys.stderr)
        sys.exit(1)
    return path.read_text(encoding="utf-8").splitlines(keepends=True)


def find_heading_positions(lines: list[str]) -> list[tuple[int, int]]:
    """
    找出所有标题行的位置和层级。
    返回 [(行号, 层级), ...]，行号从 0 开始。
    跳过代码块内的 # 符号。
    """
    headings = []
    in_code_block = False

    for i, line in enumerate(lines):
        stripped = line.strip()

        # 检测代码块边界
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue

        if in_code_block:
            continue

        # 匹配 ATX 风格标题
        match = re.match(r'^(#{1,6})\s+\S', line)
        if match:
            level = len(match.group(1))
            headings.append((i, level))

    return headings


def get_title_text(line: str) -> str:
    """从标题行提取标题文本。"""
    match = re.match(r'^#{1,6}\s+(.+?)(?:\s*#*\s*)?$', line.strip())
    return match.group(1).strip() if match else line.strip()


def precompute_code_block_ranges(lines: list[str]) -> list[tuple[int, int]]:
    """
    预计算所有代码块的行号区间。
    返回 [(start, end), ...]，start 是 ``` 开始行，end 是 ``` 结束行。
    代码块内部行号范围为 (start, end) 开区间。
    """
    ranges = []
    open_line = None

    for i, line in enumerate(lines):
        if line.strip().startswith("```"):
            if open_line is None:
                open_line = i
            else:
                ranges.append((open_line, i))
                open_line = None

    # 未闭合的代码块延伸到文件末尾
    if open_line is not None:
        ranges.append((open_line, len(lines)))

    return ranges


def is_in_code_block_fast(code_block_ranges: list[tuple[int, int]], line_idx: int) -> bool:
    """用二分搜索判断指定行是否在代码块内。"""
    if not code_block_ranges:
        return False

    lo, hi = 0, len(code_block_ranges) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        start, end = code_block_ranges[mid]
        if line_idx < start:
            hi = mid - 1
        elif line_idx > end:
            lo = mid + 1
        else:
            # line_idx 在 [start, end] 范围内（含边界的 ``` 行本身）
            return True
    return False


def is_in_list(lines: list[str], line_idx: int) -> bool:
    """判断指定行是否在列表中间。"""
    if line_idx >= len(lines):
        return False
    line = lines[line_idx].strip()
    # 如果当前行是列表项或者是列表项的续行（缩进的非空行）
    if re.match(r'^[-*+]\s|^\d+\.\s', line):
        return True
    # 检查是否是列表续行
    if line and line_idx > 0:
        prev = lines[line_idx - 1].strip()
        if re.match(r'^[-*+]\s|^\d+\.\s', prev):
            return True
    return False


def find_split_points(lines: list[str], headings: list[tuple[int, int]],
                      max_lines: int, min_lines: int) -> list[int]:
    """
    确定拆分点（行号列表）。
    优先在一级标题处拆，其次二级、三级。
    确保每个片段在 min_lines ~ max_lines 范围内。
    """
    total = len(lines)
    if total <= max_lines:
        return []  # 不需要拆分

    # 预计算代码块区间，后续查询用二分搜索
    code_block_ranges = precompute_code_block_ranges(lines)

    # 按层级分组标题位置
    h1_positions = [pos for pos, level in headings if level == 1]
    h2_positions = [pos for pos, level in headings if level == 2]
    h3_positions = [pos for pos, level in headings if level == 3]
    all_heading_positions = sorted([pos for pos, _ in headings])

    split_points = []
    current_start = 0

    while current_start < total:
        remaining = total - current_start

        # 如果剩余内容不超过 max_lines，结束
        if remaining <= max_lines:
            break

        # 在 [current_start + min_lines, current_start + max_lines] 范围内寻找最佳拆分点
        search_start = current_start + min_lines
        search_end = min(current_start + max_lines, total)

        best_point = None

        # 优先找 H1
        for pos in h1_positions:
            if search_start <= pos <= search_end:
                best_point = pos
                break  # 取第一个符合的 H1

        # 其次找 H2
        if best_point is None:
            for pos in h2_positions:
                if search_start <= pos <= search_end:
                    best_point = pos
                    break

        # 再找 H3
        if best_point is None:
            for pos in h3_positions:
                if search_start <= pos <= search_end:
                    best_point = pos
                    break

        # 找任意标题
        if best_point is None:
            for pos in all_heading_positions:
                if search_start <= pos <= search_end:
                    best_point = pos
                    break

        # 找空行作为段落边界
        if best_point is None:
            # 从 search_end 向前找空行
            for pos in range(search_end - 1, search_start - 1, -1):
                if pos < total and lines[pos].strip() == "":
                    # 确保不在代码块或列表中间
                    if not is_in_code_block_fast(code_block_ranges, pos) and not is_in_list(lines, pos):
                        best_point = pos + 1  # 拆分点在空行之后
                        break

        # 实在找不到，强制在 max_lines 处拆
        if best_point is None:
            best_point = search_end

        # 确保拆分点不在代码块中间
        if is_in_code_block_fast(code_block_ranges, best_point):
            # 向后找到代码块结束
            for pos in range(best_point, min(best_point + 100, total)):
                if lines[pos].strip().startswith("```"):
                    best_point = pos + 1
                    break

        split_points.append(best_point)
        current_start = best_point

    return split_points


def get_context_lines(lines: list[str], start: int, end: int,
                      prev_end: int, next_start: int) -> dict:
    """生成上下文信息。"""
    context = {}

    # 前文最后 5 行
    if start > 0:
        ctx_start = max(prev_end if prev_end >= 0 else 0, start - 5)
        context["preceding_lines"] = [l.rstrip("\n\r") for l in lines[ctx_start:start]]

    # 后文前 3 行
    if end < len(lines):
        ctx_end = min(next_start if next_start > 0 else len(lines), end + 3)
        context["following_lines"] = [l.rstrip("\n\r") for l in lines[end:ctx_end]]

    return context


def get_title_range(lines: list[str], start: int, end: int) -> str:
    """获取片段内的标题范围描述。"""
    titles = []
    in_code = False
    for i in range(start, min(end, len(lines))):
        stripped = lines[i].strip()
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        match = re.match(r'^#{1,6}\s+(.+?)(?:\s*#*\s*)?$', stripped)
        if match:
            titles.append(match.group(1).strip())

    if not titles:
        return f"Lines {start + 1}-{end}"
    if len(titles) == 1:
        return titles[0]
    return f"{titles[0]} ~ {titles[-1]}"


def main():
    args = parse_args()
    input_path = Path(args.input).resolve()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    lines = read_lines(str(input_path))
    total_lines = len(lines)

    print(f"文件：{input_path.name}")
    print(f"总行数：{total_lines}")

    if total_lines <= args.max_lines:
        print(f"文件行数 ({total_lines}) 未超过阈值 ({args.max_lines})，无需拆分。")
        sys.exit(0)

    # 找标题位置
    headings = find_heading_positions(lines)
    print(f"发现 {len(headings)} 个标题")

    # 确定拆分点
    split_points = find_split_points(lines, headings, args.max_lines, args.min_lines)

    if not split_points:
        print("未找到合适的拆分点。")
        sys.exit(0)

    # 生成片段
    boundaries = [0] + split_points + [total_lines]
    parts = []

    for i in range(len(boundaries) - 1):
        start = boundaries[i]
        end = boundaries[i + 1]
        part_num = i + 1
        part_filename = f"_part_{part_num:02d}.md"
        part_path = output_dir / part_filename

        # 写入片段文件
        content = "".join(lines[start:end])
        part_path.write_text(content, encoding="utf-8")

        # 上下文信息
        prev_end = boundaries[i - 1] if i > 0 else -1
        next_start = boundaries[i + 2] if i + 2 < len(boundaries) else -1
        context = get_context_lines(lines, start, end, prev_end, next_start)

        # 写上下文文件
        if context:
            ctx_path = output_dir / f"_part_{part_num:02d}_context.json"
            ctx_path.write_text(json.dumps(context, ensure_ascii=False, indent=2),
                                encoding="utf-8")

        title_range = get_title_range(lines, start, end)

        parts.append({
            "file": part_filename,
            "start_line": start + 1,  # 转为 1-based
            "end_line": end,
            "lines": end - start,
            "title_range": title_range
        })

        print(f"  {part_filename}: 行 {start + 1}-{end} ({end - start} 行) [{title_range}]")

    # 生成 manifest
    manifest = {
        "source": input_path.name,
        "source_path": str(input_path),
        "total_lines": total_lines,
        "parts_count": len(parts),
        "parts": parts
    }

    manifest_path = output_dir / "_split_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2),
                             encoding="utf-8")

    print(f"\n拆分完成：{len(parts)} 个片段")
    print(f"清单文件：{manifest_path}")


if __name__ == "__main__":
    main()
