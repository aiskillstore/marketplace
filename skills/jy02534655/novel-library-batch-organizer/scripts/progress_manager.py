#!/usr/bin/env python3
"""
全局进度管理器
提供进度的读取、更新、查询功能
使用原子写入 + 文件锁保证并发安全
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime

try:
    import fcntl
    HAS_FCNTL = True
except ImportError:
    HAS_FCNTL = False

if not HAS_FCNTL:
    try:
        import msvcrt
        HAS_MSVCRT = True
    except ImportError:
        HAS_MSVCRT = False
else:
    HAS_MSVCRT = False


def _lock_file(lf, exclusive=False):
    if HAS_FCNTL:
        flags = fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH
        flags |= fcntl.LOCK_NB
        start = time.time()
        while True:
            try:
                fcntl.flock(lf.fileno(), flags)
                return
            except BlockingIOError:
                if time.time() - start > LOCK_TIMEOUT:
                    raise TimeoutError(f"获取锁超时: {lf.name}")
                time.sleep(0.1)
    elif HAS_MSVCRT:
        # msvcrt 的 locking 是进程级文件锁，兼容 Windows
        start = time.time()
        while True:
            try:
                msvcrt.locking(lf.fileno(), msvcrt.LK_NBLCK, 1)
                return
            except OSError:
                if time.time() - start > LOCK_TIMEOUT:
                    raise TimeoutError(f"获取锁超时: {lf.name}")
                time.sleep(0.1)
    else:
        # 无锁降级：直接返回，依赖原子写操作
        return


def _unlock_file(lf):
    if HAS_FCNTL:
        fcntl.flock(lf.fileno(), fcntl.LOCK_UN)
    elif HAS_MSVCRT:
        try:
            msvcrt.locking(lf.fileno(), msvcrt.LK_UNLCK, 1)
        except OSError:
            pass


PROGRESS_FILE = '.organizer_progress/task_progress.json'
LOCK_TIMEOUT = 5  # 锁超时时间（秒）


def get_progress():
    """读取全局进度（带读锁）"""
    Path(PROGRESS_FILE).parent.mkdir(parents=True, exist_ok=True)
    if not Path(PROGRESS_FILE).exists():
        return None

    lock_file = PROGRESS_FILE + '.lock'
    with open(lock_file, 'w') as lf:
        _lock_file(lf, exclusive=False)
        try:
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        finally:
            _unlock_file(lf)


def init_progress(source_dir, temp_dir, output_dir):
    progress = {
        'task_id': datetime.now().strftime('%Y%m%d_%H%M%S'),
        'start_time': datetime.now().isoformat(),
        'last_update': datetime.now().isoformat(),
        'status': 'initialized',
        'source_dir': str(source_dir),
        'temp_dir': str(temp_dir),
        'output_dir': str(output_dir),
        'phases': {
            'preprocess': {'status': 'pending'},
            'scan': {'status': 'pending'},
            'regular_layer': {'status': 'pending'},
            'semi_regular_layer': {'status': 'pending'},
            'chaotic_layer': {'status': 'pending'},
            'validate': {'status': 'pending'}
        }
    }
    save_progress(progress)
    return progress


def save_progress(progress):
    """
    保存全局进度
    使用临时文件 + 原子重命名 + 文件锁
    """
    progress['last_update'] = datetime.now().isoformat()
    Path(PROGRESS_FILE).parent.mkdir(parents=True, exist_ok=True)

    lock_file = PROGRESS_FILE + '.lock'
    with open(lock_file, 'w') as lf:
        _lock_file(lf, exclusive=True)
        try:
            temp_file = PROGRESS_FILE + '.tmp'
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(progress, f, ensure_ascii=False, indent=2)
            os.replace(temp_file, PROGRESS_FILE)
        finally:
            _unlock_file(lf)


def update_phase(phase_name, status, **kwargs):
    progress = get_progress()
    if not progress:
        return None
    if phase_name not in progress['phases']:
        return None
    progress['phases'][phase_name]['status'] = status
    for key, value in kwargs.items():
        progress['phases'][phase_name][key] = value
    if status == 'completed':
        progress['phases'][phase_name]['completed_at'] = datetime.now().isoformat()
    save_progress(progress)
    return progress


def get_phase_status(phase_name):
    progress = get_progress()
    if not progress:
        return None
    return progress['phases'].get(phase_name, {}).get('status')


def is_completed():
    progress = get_progress()
    if not progress:
        return False
    for phase in progress['phases'].values():
        if phase.get('status') != 'completed':
            return False
    return True


def get_next_phase():
    phase_order = ['preprocess', 'scan', 'regular_layer', 'semi_regular_layer', 'chaotic_layer', 'validate']
    progress = get_progress()
    if not progress:
        return phase_order[0]
    for phase in phase_order:
        if progress['phases'].get(phase, {}).get('status') in ('pending', 'in_progress'):
            return phase
    return None


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--show', action='store_true', help='显示当前进度')
    parser.add_argument('--init', action='store_true', help='初始化进度')
    parser.add_argument('--source', default='./NovelLibrary')
    parser.add_argument('--temp', default='./NovelLibrary_Temp')
    parser.add_argument('--output', default='./NovelLibrary_Processed')
    parser.add_argument('--update', help='更新阶段状态: phase_name:status')
    parser.add_argument('--current_file', help='当前处理的文件路径')
    parser.add_argument('--processed', type=int, help='已处理数量')
    parser.add_argument('--total', type=int, help='总数量')
    parser.add_argument('--failed', type=int, help='失败数量')
    parser.add_argument('--ai_calls', type=int, help='AI调用次数')
    args = parser.parse_args()

    if args.show:
        progress = get_progress()
        if progress:
            print(json.dumps(progress, ensure_ascii=False, indent=2))
        else:
            print('未找到进度文件')
    elif args.init:
        progress = init_progress(args.source, args.temp, args.output)
        print(f'进度已初始化: {PROGRESS_FILE}')
    elif args.update:
        parts = args.update.split(':')
        if len(parts) == 2:
            phase, status = parts
            kwargs = {}
            if args.current_file:
                kwargs['current_file'] = args.current_file
            if args.processed is not None:
                kwargs['processed'] = args.processed
            if args.total is not None:
                kwargs['total'] = args.total
            if args.failed is not None:
                kwargs['failed'] = args.failed
            if args.ai_calls is not None:
                kwargs['ai_calls'] = args.ai_calls
            result = update_phase(phase, status, **kwargs)
            if result:
                print(f'阶段 {phase} 已更新为 {status}')
            else:
                print(f'更新失败')
        else:
            print('格式错误，请使用 --update phase_name:status')
    else:
        print('请指定 --show 或 --init 或 --update')


if __name__ == '__main__':
    main()