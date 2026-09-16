#!/usr/bin/env python3
"""
扫描与分层分类（基于临时目录）
用法: python scan_and_classify.py --source ./NovelLibrary_Temp --output ./NovelLibrary_Processed
"""

import os
import sys
import json
import re
import argparse
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import random

# 导入公共正则（替代本地硬编码 CHAPTER_PATTERNS）
from chapter_patterns import CANDIDATE_REGEX

# 污染检测正则（保持不变）
POLLUTION_PATTERNS = [
    r'[\x00-\x08\x0b\x0c\x0e-\x1f]',
    r'[�]',
    r'锟斤拷',
    r'烫烫烫',
    r'屯屯屯',
    r'[^\u4e00-\u9fff\u0041-\u005a\u0061-\u007a\u3000-\u303f\uff00-\uffef\u0020-\u007e\n\r]'
]

ADVERTISEMENT_KEYWORDS = [
    '关注公众号', '添加微信', 'VIP章节', '付费阅读',
    '最新章节', '请订阅', '求收藏', '打赏', '月票'
]


def read_file_safe(file_path):
    """临时目录下的文件都是 UTF-8，直接读取"""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()


def detect_chapter_format(text):
    """采样跳过前20行元信息，使用公共正则 CANDIDATE_REGEX"""
    lines = text.splitlines()
    if len(lines) <= 20:
        sample_lines = lines
    else:
        remaining = lines[20:]
        sample_size = min(200, len(remaining))
        sample_lines = remaining[:sample_size]

        if len(remaining) > sample_size:
            random_indices = random.sample(
                range(sample_size, len(remaining)),
                min(50, len(remaining) - sample_size)
            )
            sample_lines.extend([remaining[i] for i in random_indices])

    matched = 0
    for line in sample_lines:
        line = line.strip()
        if len(line) < 2:
            continue
        if CANDIDATE_REGEX.match(line):
            matched += 1

    total = len([l for l in sample_lines if len(l.strip()) >= 2])
    return matched / max(total, 1)


def detect_pollution(text):
    abnormal = re.findall('|'.join(POLLUTION_PATTERNS), text)
    abnormal_count = len(abnormal)
    ad_count = sum(text.count(kw) for kw in ADVERTISEMENT_KEYWORDS)
    total_chars = len(text)
    if total_chars == 0:
        return 0, 0
    pollution_rate = (abnormal_count + ad_count * 10) / total_chars
    return min(pollution_rate, 1.0), abnormal_count


def scan_file(file_path, source_path):
    try:
        content = read_file_safe(file_path)
        lines = content.splitlines()
        file_size = os.path.getsize(file_path) / 1024
        chapter_match_rate = detect_chapter_format(content)
        pollution_rate, abnormal_count = detect_pollution(content)
        total_chars = len(content)
        total_lines = len(lines)
        non_empty_lines = len([l for l in lines if l.strip()])

        if chapter_match_rate > 0.8 and pollution_rate < 0.01:
            layer = 'regular'
        elif chapter_match_rate == 0 and pollution_rate < 0.01:
            layer = 'regular'
        elif chapter_match_rate > 0.5 or (pollution_rate < 0.05 and chapter_match_rate > 0):
            layer = 'semi_regular'
        else:
            layer = 'chaotic'

        if file_size < 500:
            size_layer = 'small'
        elif file_size < 5000:
            size_layer = 'medium'
        else:
            size_layer = 'large'

        return {
            'file_path': str(file_path),
            'file_name': file_path.name,
            'relative_path': str(file_path.relative_to(source_path)),
            'size_kb': round(file_size, 2),
            'size_layer': size_layer,
            'total_chars': total_chars,
            'total_lines': total_lines,
            'non_empty_lines': non_empty_lines,
            'chapter_match_rate': round(chapter_match_rate, 4),
            'pollution_rate': round(pollution_rate, 4),
            'abnormal_count': abnormal_count,
            'layer': layer,
            'needs_ai': layer in ('semi_regular', 'chaotic'),
            # 修复：基于字符数估算分块数，而非 KB
            'estimated_chunks': max(1, int(total_chars / 80000))
        }
    except Exception as e:
        return {
            'file_path': str(file_path),
            'file_name': file_path.name,
            'error': str(e),
            'layer': 'error'
        }


def scan_library(source_dir):
    source_path = Path(source_dir)
    if not source_path.exists():
        raise FileNotFoundError(f"临时目录不存在: {source_dir}")

    files = list(source_path.rglob('*.txt'))
    print(f"发现 {len(files)} 个TXT文件，开始扫描...")

    results = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(scan_file, f, source_path): f for f in files}
        for i, future in enumerate(as_completed(futures), 1):
            result = future.result()
            results.append(result)
            status = result.get('layer', 'error')
            print(f"[{i}/{len(files)}] {result['file_name']} -> {status}")

    return results


def generate_report(results, source_dir, output_dir):
    output_path = Path(output_dir)
    progress_dir = output_path / '.organizer_progress'
    progress_dir.mkdir(parents=True, exist_ok=True)

    stats = {
        'total': len(results),
        'by_layer': {'regular': 0, 'semi_regular': 0, 'chaotic': 0, 'error': 0},
        'by_size': {'small': 0, 'medium': 0, 'large': 0},
        'total_size_kb': 0,
        'needs_ai': 0,
        'total_chars': 0,
        'avg_chapter_match': 0,
        'avg_pollution': 0
    }

    for r in results:
        layer = r.get('layer', 'error')
        stats['by_layer'][layer] = stats['by_layer'].get(layer, 0) + 1
        stats['by_size'][r.get('size_layer', 'small')] += 1
        stats['total_size_kb'] += r.get('size_kb', 0)
        stats['total_chars'] += r.get('total_chars', 0)
        if r.get('needs_ai', False):
            stats['needs_ai'] += 1
        stats['avg_chapter_match'] += r.get('chapter_match_rate', 0)
        stats['avg_pollution'] += r.get('pollution_rate', 0)

    if stats['total'] > 0:
        stats['avg_chapter_match'] /= stats['total']
        stats['avg_pollution'] /= stats['total']

    by_layer = {
        'regular': [r for r in results if r.get('layer') == 'regular'],
        'semi_regular': [r for r in results if r.get('layer') == 'semi_regular'],
        'chaotic': [r for r in results if r.get('layer') == 'chaotic'],
        'error': [r for r in results if r.get('error')]
    }

    report = {
        'scan_time': datetime.now().isoformat(),
        'source_dir': str(source_dir),
        'output_dir': str(output_dir),
        'stats': stats,
        'by_layer': {
            layer: [{'path': r['relative_path'], 'size': r.get('size_kb', 0)}
                    for r in files]
            for layer, files in by_layer.items()
        },
        'details': results
    }

    with open(progress_dir / 'classification.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    for layer in ['regular', 'semi_regular', 'chaotic', 'error']:
        with open(progress_dir / f'{layer}_list.json', 'w', encoding='utf-8') as f:
            json.dump(by_layer.get(layer, []), f, ensure_ascii=False, indent=2)

    from progress_manager import update_phase
    update_phase('scan', 'completed',
                 total_files=stats['total'],
                 by_layer=stats['by_layer'])

    print("\n" + "="*50)
    print("扫描完成")
    print(f"总计: {stats['total']} 个文件")
    print(f"规整层: {stats['by_layer']['regular']} (零AI)")
    print(f"半规整层: {stats['by_layer']['semi_regular']} (优先自动映射)")
    print(f"混乱层: {stats['by_layer']['chaotic']} (AI逐本处理)")
    print(f"错误: {stats['by_layer']['error']}")
    print(f"需要AI介入: {stats['needs_ai']} 个文件")
    print(f"报告已保存: {progress_dir / 'classification.json'}")
    print("="*50)

    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', default='./NovelLibrary_Temp')
    parser.add_argument('--output', default='./NovelLibrary_Processed')
    args = parser.parse_args()

    results = scan_library(args.source)
    generate_report(results, args.source, args.output)


if __name__ == '__main__':
    main()