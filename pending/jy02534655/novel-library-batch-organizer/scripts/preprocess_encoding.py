#!/usr/bin/env python3
"""
预处理：遍历源目录所有文件，检测编码，统一转为 UTF-8 输出到临时目录
用法: python preprocess_encoding.py --source ./NovelLibrary --temp ./NovelLibrary_Temp
"""

import os
import sys
import json
import chardet
import argparse
import time
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import shutil


def detect_encoding(file_path):
    """检测文件编码，采样扩大到 100KB 提高准确率"""
    with open(file_path, 'rb') as f:
        raw = f.read(100000)
    if not raw:
        return 'utf-8'
    result = chardet.detect(raw)
    return result['encoding'] or 'utf-8'


def safe_resolve_path(path_str, allow_parent=False):
    """
    安全解析路径，防止路径遍历攻击
    :param path_str: 用户输入的路径字符串
    :param allow_parent: 是否允许父目录引用（默认 False）
    :return: 解析后的 Path 对象
    :raises ValueError: 如果路径包含危险模式
    """
    path = Path(path_str).resolve()

    # 检查是否包含 .. 路径遍历
    if not allow_parent:
        # 检查解析后的路径是否包含 '..' 组件
        try:
            # 用相对路径检测
            rel = Path(path_str)
            if '..' in rel.parts:
                raise ValueError(f"路径包含 '..' 目录遍历: {path_str}")
        except Exception:
            pass

    # 检查路径是否太短（如 / 或 C:\）
    if str(path) in ['/', '\\', 'C:\\', 'D:\\']:
        raise ValueError(f"路径是根目录，禁止操作: {path_str}")

    return path


def convert_to_utf8(file_path, temp_path, source_root, temp_root):
    relative_path = str(file_path.relative_to(source_root))
    temp_file = temp_root / relative_path

    try:
        encoding = detect_encoding(file_path)

        encodings_to_try = [encoding, 'utf-8', 'utf-16', 'gbk', 'gb18030', 'big5']
        content = None
        used_encoding = None

        for enc in encodings_to_try:
            if enc is None:
                continue
            try:
                with open(file_path, 'r', encoding=enc, errors='strict') as f:
                    content = f.read()
                used_encoding = enc
                break
            except (UnicodeDecodeError, LookupError):
                continue

        if content is None:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            used_encoding = 'utf-8(ignore)'

        temp_file.parent.mkdir(parents=True, exist_ok=True)
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(content)

        return {
            'relative_path': relative_path,
            'original_encoding': used_encoding,
            'detected_encoding': encoding,
            'success': True,
            'chars': len(content)
        }

    except Exception as e:
        return {
            'relative_path': relative_path,
            'original_encoding': 'unknown',
            'detected_encoding': 'unknown',
            'success': False,
            'error': str(e)
        }


def preprocess_all(source_dir, temp_dir, max_workers=4, force=False):
    # 使用安全路径解析
    source_path = safe_resolve_path(source_dir)
    temp_path = safe_resolve_path(temp_dir)

    # 目录安全检查
    if temp_path == source_path:
        raise ValueError(f"临时目录不能和源目录相同: {temp_dir} == {source_dir}")

    if source_path in temp_path.parents:
        raise ValueError(f"临时目录不能是源目录的子目录: {temp_dir} 是 {source_dir} 的子目录")

    if temp_path in source_path.parents:
        raise ValueError(f"临时目录不能是源目录的父目录: {temp_dir} 是 {source_dir} 的父目录")

    if temp_path == Path('.').resolve():
        raise ValueError("临时目录不能是当前工作目录 (.)")

    if temp_path == Path.home().resolve():
        raise ValueError("临时目录不能是用户主目录")

    if not source_path.exists():
        raise FileNotFoundError(f"源目录不存在: {source_dir}")

    # 清空临时目录
    if temp_path.exists():
        existing_files = list(temp_path.rglob('*'))
        if existing_files:
            file_count = len([f for f in existing_files if f.is_file()])
            print(f"警告: 临时目录 {temp_dir} 已存在且包含 {file_count} 个文件")
            if not force:
                print("将在 5 秒后继续清空... 按 Ctrl+C 取消")
                for i in range(5, 0, -1):
                    print(f"  {i}...")
                    time.sleep(1)
                print("继续执行...")
            else:
                print("--force 已指定，直接清空...")
        shutil.rmtree(temp_path)

    temp_path.mkdir(parents=True, exist_ok=True)

    files = list(source_path.rglob('*.txt'))
    print(f"发现 {len(files)} 个TXT文件，开始转码...")

    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(convert_to_utf8, f, temp_path, source_path, temp_path): f
            for f in files
        }
        for i, future in enumerate(as_completed(futures), 1):
            result = future.result()
            results.append(result)
            status = "[OK]" if result['success'] else "[FAIL]"
            enc = result.get('original_encoding', 'unknown')
            print(f"[{i}/{len(files)}] {result['relative_path']} -> {enc} {status}")

    progress_dir = temp_path / '.preprocess_progress'
    progress_dir.mkdir(parents=True, exist_ok=True)

    stats = {
        'total': len(results),
        'success': sum(1 for r in results if r['success']),
        'failed': sum(1 for r in results if not r['success']),
        'encodings': {}
    }

    for r in results:
        enc = r.get('original_encoding', 'unknown')
        stats['encodings'][enc] = stats['encodings'].get(enc, 0) + 1

    report = {
        'preprocess_time': datetime.now().isoformat(),
        'source_dir': str(source_dir),
        'temp_dir': str(temp_dir),
        'stats': stats,
        'details': results
    }

    with open(progress_dir / 'preprocess_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    from progress_manager import update_phase, init_progress
    if not Path('.organizer_progress/task_progress.json').exists():
        init_progress(source_dir, temp_dir, Path('./NovelLibrary_Processed'))
    update_phase('preprocess', 'completed',
                 total_files=stats['total'],
                 processed_files=stats['success'],
                 failed_files=stats['failed'])

    print("\n" + "=" * 50)
    print("转码完成")
    print(f"总计: {stats['total']} 个文件")
    print(f"成功: {stats['success']}")
    print(f"失败: {stats['failed']}")
    print(f"编码分布:")
    for enc, count in sorted(stats['encodings'].items(), key=lambda x: -x[1]):
        print(f"  {enc}: {count}")
    print(f"报告已保存: {progress_dir / 'preprocess_report.json'}")
    print("=" * 50)

    return report


def main():
    parser = argparse.ArgumentParser(description='统一转码小说文件到 UTF-8')
    parser.add_argument('--source', default='./NovelLibrary', help='源目录路径')
    parser.add_argument('--temp', default='./NovelLibrary_Temp', help='临时目录路径')
    parser.add_argument('--workers', type=int, default=4, help='并行线程数')
    parser.add_argument('--force', action='store_true', help='跳过确认倒计时，直接执行')
    args = parser.parse_args()

    preprocess_all(args.source, args.temp, args.workers, args.force)


if __name__ == '__main__':
    main()