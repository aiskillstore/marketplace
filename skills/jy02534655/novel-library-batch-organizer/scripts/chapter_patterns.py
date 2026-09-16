#!/usr/bin/env python3
"""公共正则表达模块"""

import re

# 候选章节提取正则
CANDIDATE_REGEX = re.compile(
    r'^\s*(?:'
    r'第[零一二三四五六七八九十百千万\d]+[章回节集卷部](?:\s*.*)?|'
    r'Chapter\s*\d+(?:\s*.*)?|'
    r'[\(（]\d+[\)）](?:\s*.*)?|'
    r'[\(（][零一二三四五六七八九十百千万\d]+[\)）](?:\s*.*)?|'
    r'[零一二三四五六七八九十百千\d]+[、．.]\s*\S+|'
    r'[【\[]\s*[零一二三四五六七八九十百千\d]+\s*[、，,\.]\s*\S+[】\]]|'
    r'[※☆★●◆◇○■□▲△▶►]+\s*\S+|'
    r'.{0,30}[（(][零一二三四五六七八九十百千万\d]+[）)]\s*$'
    r')\s*$',
    re.MULTILINE | re.IGNORECASE
)

# 章节标题匹配正则（严格匹配，用于规整层）
CHAPTER_REGEX = re.compile(
    r'^\s*(?:'
    r'第[零一二三四五六七八九十百千万\d]+[章回节集卷部](?:\s*.*)?|'
    r'Chapter\s*\d+(?:\s*.*)?|CHAPTER\s*\d+(?:\s*.*)?|'
    r'[\(（]\d+[\)）](?:\s*.*)?|'
    r'[\(（][零一二三四五六七八九十百千万\d]+[\)）](?:\s*.*)?|'
    r'[零一二三四五六七八九十百千\d]+[、．.]\s*\S+|'
    r'[【\[]\s*[零一二三四五六七八九十百千\d]+\s*[、，,\.]\s*\S+[】\]]|'
    r'[※☆★●◆◇○■□▲△▶►]+\s*\S+|'
    r'.{0,30}[（(][零一二三四五六七八九十百千万\d]+[）)]\s*$'
    r')\s*$',
    re.MULTILINE | re.IGNORECASE
)

# 章节模式正则（用于重编号）
CHAPTER_PATTERN = re.compile(
    r'^\s*(?:'
    r'第[零一二三四五六七八九十百千万\d]+[章回节集卷部]|'
    r'Chapter\s*\d+|CHAPTER\s*\d+|'
    r'[\(（]\d+[\)）]|'
    r'[\(（][零一二三四五六七八九十百千万\d]+[\)）]|'
    r'[【\[]\s*[零一二三四五六七八九十百千\d]+\s*[、，,\.]\s*[^】\]]{2,}[】\]]|'
    r'[零一二三四五六七八九十百千\d]+\s*[、．.．]\s*\S+|'
    r'.{0,30}[（(][零一二三四五六七八九十百千万\d]+[）)]\s*$'
    r')(?:\s*.*)?$',
    re.MULTILINE | re.IGNORECASE
)

# 特殊章节
SPECIAL_CHAPTERS = re.compile(
    r'^\s*(?:序章|楔子|尾声|后记|番外|外传|引子|前言|引言|跋|第零章)',
    re.MULTILINE | re.IGNORECASE
)

# 章节标题开始模式
CHAPTER_START_REGEX = re.compile(
    r'^(?:[零一二三四五六七八九十百千\d]+[、．.]|第[零一二三四五六七八九十百千\d]+[章回节集卷部]|Chapter\s*\d+)',
    re.IGNORECASE
)

# 用于分块的章节边界检测
CHUNK_CHAPTER_PATTERN = re.compile(
    r'^\s*(?:第[零一二三四五六七八九十百千万\d]+[章回节集卷部]|第\d+[章回节集卷部])',
    re.MULTILINE
)

# 中文数字转换工具函数
NUM_MAP = {'零':0,'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,'十':10,'百':100,'千':1000,'万':10000}

def chinese_to_number(chinese_str):
    if not chinese_str: return None
    if chinese_str.isdigit(): return int(chinese_str)
    if chinese_str in NUM_MAP: return NUM_MAP[chinese_str]
    result, current = 0, 0
    for char in chinese_str:
        if char in NUM_MAP:
            val = NUM_MAP[char]
            if val >= 10:
                if current == 0: current = 1
                result += current * val; current = 0
            else: current = val
        else: return None
    result += current
    return result if result > 0 else None

def chinese_to_number_simple(chinese_str):
    if not chinese_str: return None
    if chinese_str.isdigit(): return chinese_str
    m = {
        '零':'0','一':'1','二':'2','三':'3','四':'4','五':'5','六':'6','七':'7','八':'8','九':'9',
        '十':'10','十一':'11','十二':'12','十三':'13','十四':'14','十五':'15',
        '十六':'16','十七':'17','十八':'18','十九':'19','二十':'20',
        '二十一':'21','二十二':'22','二十三':'23','二十四':'24','二十五':'25',
        '二十六':'26','二十七':'27','二十八':'28','二十九':'29','三十':'30',
    }
    return m.get(chinese_str) if chinese_str in m else str(chinese_to_number(chinese_str) or '')