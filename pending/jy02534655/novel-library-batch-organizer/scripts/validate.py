#!/usr/bin/env python3
"""
校验最终输出（对比临时目录和输出目录）
用法: python validate.py --source ./NovelLibrary_Temp --output ./NovelLibrary_Processed
"""

import os
import sys
import json
import re
import argparse
from pathlib import Path
from datetime import datetime

# 导入公共正则
from chapter_patterns import CHAPTER_PATTERN


def count_chapters(text):
    """
    统计章节数并检查连续性
    使用公共正则 CHAPTER_PATTERN，支持 章/回/节 三种格式
    """
    matches = list(CHAPTER_PATTERN.finditer(text))

    if not matches:
        return 0, [], True

    numbers = []
    for m in matches:
        line = m.group(0)
        num = re.search(r'\d+', line)
        if num:
            numbers.append(int(num.group()))

    if not numbers:
        return 0, [], True

    is_continuous = True
    expected = 1
    for n in numbers:
        if n != expected:
            is_continuous = False
            break
        expected += 1

    return len(numbers), numbers, is_continuous


def validate_file(source_path, output_path):
    """同时读取源文件（临时目录）和输出文件进行对比"""
    try:
        with open(source_path, 'r', encoding='utf-8', errors='ignore') as f:
            original = f.read()
    except Exception as e:
        return {
            'file_path': str(output_path),
            'passed': False,
            'issues': [f'无法读取源文件: {e}']
        }

    try:
        with open(output_path, 'r', encoding='utf-8', errors='ignore') as f:
            processed = f.read()
    except Exception as e:
        return {
            'file_path': str(output_path),
            'passed': False,
            'issues': [f'无法读取输出文件: {e}']
        }

    original_chars = len(original)
    new_chars = len(processed)
    diff_rate = abs(new_chars - original_chars) / max(original_chars, 1)
    chars_diff_ok = diff_rate < 0.10

    chapter_count, chapter_numbers, is_continuous = count_chapters(processed)

    # 检查标题格式是否统一（使用公共正则检测残留）
    other_pattern = re.compile(
        r'^(?:第[零一二三四五六七八九十百千万]+[章回节]|Chapter\s*\d+|[\(（]?\d+[\)）]|[零一二三四五六七八九十百千万]+[、\.]|[※☆★●◆◇○■□▲△▶►]+)',
        re.MULTILINE
    )
    valid_pattern = re.compile(r'^第\d+[章回节集卷部]')
    other_matches = [m for m in other_pattern.finditer(processed)
                     if not valid_pattern.match(m.group())]

    # 检查广告残留
    ad_keywords = ['关注公众号', '添加微信', 'VIP章节', '付费阅读', '最新章节', '请订阅', '求收藏', '打赏', '月票']
    ad_count = sum(processed.count(kw) for kw in ad_keywords)

    # 附加质量检查
    quality_warnings = []

    # 检查首行是否为章节标题
    first_line = processed.split('\n')[0].strip()
    if not re.match(r'^第\d+[章回节集卷部]', first_line):
        quality_warnings.append('首行非章节标题')

    # 检查文件头部是否有元数据残留
    header_pats = [
        re.compile(r'^(?:书名|作者|排版|字数)[：:]\s*\S+'),
        re.compile(r'^\s*www\.\S+'),
        re.compile(r'^治疗阳萎的天使$'),
        re.compile(r'^\s*欢迎阅读\S+'),
    ]
    for line in processed.split('\n')[:5]:
        if any(p.match(line) for p in header_pats):
            quality_warnings.append('文件头有元数据残留')
            break

    # 检查有无裸标题（第N章后面没有标题内容）
    bare_count = len(re.findall(r'^第\d+[章回节集卷部]$', processed, re.MULTILINE))
    if bare_count > 0:
        quality_warnings.append(f'裸标题×{bare_count}')

    # 连续性检查：降级为 warning，不影响 pass/fail
    continuity_warnings = []
    if not is_continuous:
        continuity_warnings.append(f"章节编号不连续: {chapter_numbers[:10]}...")

    issues = []
    if other_matches:
        issues.append(f"发现 {len(other_matches)} 个未规范化的标题残留")
    if not chars_diff_ok:
        issues.append(f"字符数变化率 {diff_rate*100:.2f}% 超过10%阈值")
    if ad_count > 5:
        issues.append(f"发现 {ad_count} 处疑似广告残留")

    return {
        'file_path': str(output_path),
        'original_chars': original_chars,
        'new_chars': new_chars,
        'diff_rate': round(diff_rate, 4),
        'chars_diff_ok': chars_diff_ok,
        'chapter_count': chapter_count,
        'is_continuous': is_continuous,
        'continuity_warnings': continuity_warnings,
        'quality_warnings': quality_warnings,
        'has_other_titles': len(other_matches) > 0,
        'other_title_count': len(other_matches),
        'ad_count': ad_count,
        'issues': issues,
        'passed': len(issues) == 0
    }


def validate_all(source_dir, output_dir):
    source_path = Path(source_dir)
    output_path = Path(output_dir)
    progress_dir = output_path / '.organizer_progress'

    classification_file = progress_dir / 'classification.json'
    if not classification_file.exists():
        print("未找到分类报告，请先运行 scan_and_classify.py")
        return

    with open(classification_file, 'r', encoding='utf-8') as f:
        report = json.load(f)

    results = []
    for detail in report.get('details', []):
        if detail.get('layer') == 'error':
            continue
        rel_path = detail.get('relative_path')
        if not rel_path:
            continue
        src_file = source_path / rel_path
        out_file = output_path / rel_path
        if not src_file.exists():
            results.append({
                'file_path': rel_path,
                'passed': False,
                'issues': ['源文件不存在']
            })
            continue
        if not out_file.exists():
            results.append({
                'file_path': rel_path,
                'passed': False,
                'issues': ['输出文件不存在']
            })
            continue
        result = validate_file(src_file, out_file)
        result['file_path'] = rel_path
        results.append(result)

    passed = sum(1 for r in results if r.get('passed', False))
    total = len(results)

    report_file = progress_dir / 'validation_report.json'
    validation_result = {
        'validate_time': datetime.now().isoformat(),
        'source_dir': str(source_dir),
        'output_dir': str(output_dir),
        'total': total,
        'passed': passed,
        'failed': total - passed,
        'details': results
    }

    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(validation_result, f, ensure_ascii=False, indent=2)

    from progress_manager import update_phase
    update_phase('validate', 'completed',
                 total=total,
                 passed=passed,
                 failed=total-passed)

    print("\n" + "="*50)
    print("校验完成")
    print(f"总计: {total} 个文件")
    print(f"通过: {passed}")
    print(f"失败: {total - passed}")
    print(f"报告已保存: {report_file}")
    print("="*50)

    failed_items = [r for r in results if not r.get('passed', False)]
    if failed_items:
        print("\n失败文件列表:")
        for item in failed_items:
            issues = item.get('issues', ['未知错误'])
            print(f"  - {item.get('file_path', 'unknown')}: {', '.join(issues)}")

    warned_items = [r for r in results if r.get('continuity_warnings', []) or r.get('quality_warnings', [])]
    if warned_items:
        print("\n告警文件列表:")
        for item in warned_items:
            cw = item.get('continuity_warnings', [])
            qw = item.get('quality_warnings', [])
            all_w = cw + qw
            if all_w:
                print(f"  - {item.get('file_path', 'unknown')}: {'; '.join(all_w)}")

    quality_ok = sum(1 for r in results if not r.get('quality_warnings', []))
    continuity_ok = sum(1 for r in results if not r.get('continuity_warnings', []))
    print(f"\n质量明细:")
    print(f"  首行/裸标题/元数据检查通过: {quality_ok}/{total}")
    print(f"  章节连续性检查通过: {continuity_ok}/{total}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', default='./NovelLibrary_Temp')
    parser.add_argument('--output', default='./NovelLibrary_Processed')
    args = parser.parse_args()

    validate_all(args.source, args.output)


if __name__ == '__main__':
    main()