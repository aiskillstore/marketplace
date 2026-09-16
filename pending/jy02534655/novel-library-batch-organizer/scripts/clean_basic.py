#!/usr/bin/env python3
"""
规整层处理：纯本地排版清洗和章节标题保留（基于临时目录）
覆盖所有章节标题格式的标准化
"""

import os, re, json, argparse
from pathlib import Path
from chapter_patterns import CHAPTER_REGEX, SPECIAL_CHAPTERS, chinese_to_number_simple

# ===== 标点转换 =====
def smart_punct_convert(text):
    protected = []
    def protect(m):
        protected.append(m.group(0))
        return f"\x00{len(protected)-1}\x00"
    text = re.sub(r'\d+\.\d+', protect, text)
    text = re.sub(r'[a-zA-Z]\.[a-zA-Z]', protect, text)
    text = re.sub(r'\.{3,}', protect, text)
    text = re.sub(r'https?://[^\s]+', protect, text)
    punct_map = {',':'，','!':'！','?':'？',';':'；',':':'：',
                 '(':'（',')':'）','[':'【',']':'】'}
    for eng, chn in punct_map.items():
        text = text.replace(eng, chn)
    text = re.sub(r'(?<![a-zA-Z0-9])\.(?![a-zA-Z0-9])', '。', text)
    for i, s in enumerate(protected):
        text = text.replace(f"\x00{i}\x00", s)
    return text

def clean_text(text):
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    lines = [line.rstrip() for line in text.splitlines()]
    cleaned = []; prev_empty = False
    for line in lines:
        is_empty = (line.strip() == '')
        if is_empty and prev_empty: continue
        cleaned.append(line)
        prev_empty = is_empty
    text = '\n'.join(cleaned)
    text = re.sub(r'[ \t]+', '', text)
    text = smart_punct_convert(text)
    text = text.replace('\u3000', ' ')
    return text

# ===== 章节标题标准化 =====
CN_MAP = {'零':'0','一':'1','二':'2','三':'3','四':'4','五':'5','六':'6','七':'7','八':'8','九':'9'}

def convert_title(text):
    """尝试所有已知章节标题格式，返回标准化结果。无法识别则返回原文本"""
    s = text.strip()
    if not s: return text

    # 0) 装饰前缀剥离：☆、※、正文 等
    s = re.sub(r'^[※☆★●◆◇○■□▲△▶►]+[、，,]\s*', '', s)
    s = re.sub(r'^正文\s+', '', s)

    # 1) 第X章/回/节 标题 — 已是标准格式
    m = re.match(r'^(第\d+[章回节])(.*)', s)
    if m:
        ch, rest = m.group(1), m.group(2).strip()
        return f'{ch} {rest}' if rest else ch

    # 2) 第一章/回/节 → 第1章
    m = re.match(r'^第([零一二三四五六七八九十百千万\d]+)([章回节])(.*)', s)
    if m:
        ns, unit, rest = m.group(1), m.group(2), m.group(3).strip()
        ar = chinese_to_number_simple(ns)
        if ar:
            return f'第{ar}{unit} {rest}' if rest else f'第{ar}{unit}'
        return text

    # 3) Chapter X → 第X章
    m = re.match(r'^Chapter\s*(\d+)(.*)', s, re.IGNORECASE)
    if m:
        num, rest = m.group(1), m.group(2).strip()
        return f'第{num}章 {rest}' if rest else f'第{num}章'

    # 4) （N）/(N) → 第N章
    m = re.match(r'^[\(（](\d+)[\)）](.*)', s)
    if m:
        num, rest = m.group(1), m.group(2).strip()
        return f'第{num}章 {rest}' if rest else f'第{num}章'

    # 5) （一）/（二）→ 第1章/第2章
    m = re.match(r'^[\(（]([零一二三四五六七八九十百千万\d]+)[\)）](.*)', s)
    if m:
        ns, rest = m.group(1), m.group(2).strip()
        ar = chinese_to_number_simple(ns)
        if ar:
            return f'第{ar}章 {rest}' if rest else f'第{ar}章'
        return text

    # 6) 【N、标题】→ 第N章 标题
    m = re.match(r'^【\s*(\d+)\s*[、，,\.]\s*(.+?)】\s*$', s)
    if m:
        return f'第{m.group(1)}章 {m.group(2).strip()}'

    # 7) 【一、标题】→ 第1章 标题
    m = re.match(r'^【\s*([零一二三四五六七八九十百千万\d]+)\s*[、，,\.]\s*(.+?)】\s*$', s)
    if m:
        ar = chinese_to_number_simple(m.group(1))
        if ar: return f'第{ar}章 {m.group(2).strip()}'
        return text

    # 8) 一、标题 / 1、标题 → 第1章 标题
    m = re.match(r'^([零一二三四五六七八九十百千万\d]+)[、，,\.]\s*(.*)', s)
    if m:
        ns, rest = m.group(1), m.group(2).strip()
        ar = chinese_to_number_simple(ns)
        rest = re.sub(r'^[:：]\s*', '', rest)
        if ar:
            return f'第{ar}章 {rest}' if rest else f'第{ar}章'
        return text

    # 9) 第一集/卷/部/回：标题 → 第1章 标题
    m = re.match(r'^第([零一二三四五六七八九十百千万\d]+)([集卷部回])\s*[：:]\s*(.*)', s)
    if m:
        ar = chinese_to_number_simple(m.group(1))
        rest = m.group(3).strip()
        return f'第{ar}章 {rest}' if rest else f'第{ar}章'

    # 10) 第一集/卷/部 标题 (有空格)
    m = re.match(r'^第([零一二三四五六七八九十百千万\d]+)([集卷部回])\s+(.*)', s)
    if m:
        ar = chinese_to_number_simple(m.group(1))
        rest = m.group(3).strip()
        return f'第{ar}章 {rest}'

    # 11) 第X集/卷/部/回无间隔标题 → 第X章 标题 (catch-all)
    m = re.match(r'^第([零一二三四五六七八九十百千万\d]+)([集卷部回])(.*)', s)
    if m:
        ns, unit, rest = m.group(1), m.group(2), m.group(3).strip()
        ar = chinese_to_number_simple(ns)
        if ar:
            return f'第{ar}章 {rest}' if rest else f'第{ar}章'
        return text

    # 12) N）→ 第N章 (缺左括号)
    m = re.match(r'^(\d+)[）)](.*)', s)
    if m:
        num, rest = m.group(1), m.group(2).strip()
        return f'第{num}章 {rest}' if rest else f'第{num}章'

    # 13) 第X部第Y章 → 第X部 第Y章 (加空格分离卷和章)
    m = re.match(r'^(第[零一二三四五六七八九十百千万\d]+[部卷集])(第[零一二三四五六七八九十百千万\d]+[章回节])(.*)', s)
    if m:
        vol, ch, tail = m.group(1), m.group(2), m.group(3).strip()
        return f'{vol} {ch} {tail}' if tail else f'{vol} {ch}'

    # 14) 书名（N）→ 第N章 (尾部括号数字/中文数字)
    m = re.search(r'[（(]([零一二三四五六七八九十百千万\d]+)[）)]\s*$', s)
    if m:
        ns = m.group(1)
        ar = chinese_to_number_simple(ns)
        if ar:
            return f'第{ar}章'
        return text

    return text

def normalize_chapters(text):
    lines = text.splitlines()
    new_lines = []
    for line in lines:
        if CHAPTER_REGEX.match(line):
            new_lines.append(convert_title(line))
        else:
            new_lines.append(line)
    return '\n'.join(new_lines)

def process_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    cleaned = clean_text(content)
    final = normalize_chapters(cleaned)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final)
    return len(CHAPTER_REGEX.findall(final))

def batch_process(source_dir, output_dir):
    from progress_manager import update_phase
    source = Path(source_dir); output = Path(output_dir)
    progress_dir = output / '.organizer_progress'
    regular_list = progress_dir / 'regular_list.json'
    if not regular_list.exists():
        print("未找到规整层清单"); return
    with open(regular_list, 'r', encoding='utf-8') as f:
        files = json.load(f)
    total = len(files)
    update_phase('regular_layer', 'in_progress', total=total, processed=0, failed=0)
    for idx, item in enumerate(files):
        rel_path = item.get('relative_path', '')
        if not rel_path: continue
        src_full = source / rel_path; out_full = output / rel_path
        if not src_full.exists(): continue
        try:
            count = process_file(src_full, out_full)
            print(f"OK: {rel_path} ({count} chapters)")
            update_phase('regular_layer', 'in_progress', total=total, processed=idx+1, current_file=rel_path)
        except Exception as e:
            print(f"FAIL: {rel_path} - {e}")
    update_phase('regular_layer', 'completed', total=total, processed=total, failed=0)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input'); parser.add_argument('--output')
    parser.add_argument('--batch', action='store_true')
    parser.add_argument('--source', default='./NovelLibrary_Temp')
    parser.add_argument('--output_dir', default='./NovelLibrary_Processed')
    args = parser.parse_args()
    if args.batch: batch_process(args.source, args.output_dir)
    elif args.input and args.output: process_file(Path(args.input), Path(args.output))
    else: print("请指定 --input 和 --output 或 --batch")

if __name__ == '__main__':
    main()