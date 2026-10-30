#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打包任意技能为 WorkBuddy 开放平台可上传的 .zip。

为什么需要：开放平台对 SKILL.md frontmatter 要求 8 个必填字段
（name / display_name / display_name_en / description / description_zh /
description_en / version / author），而通用 Skill 规范只要 name + description。
直接在源文件里堆字段会污染其他商店的上架物料 —— 所以只在打包时注入。

用法：
    python build_wb.py --skill-dir <技能目录> \
        --display-name "中文名" --display-name-en "English Name" \
        --desc-zh "中文简介" --desc-en "English description" \
        [--version 1.0.0] [--author xixi048] [--out <输出目录>]

不传 --version 时读 frontmatter 里的（支持 metadata.version 与顶层 version 两种写法）。

产物：<out>/<技能名>-wb-<version>.zip，SKILL.md 在包根，最多两层目录。
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import zipfile

REQUIRED = [
    "name",
    "display_name",
    "display_name_en",
    "description",
    "description_zh",
    "description_en",
    "version",
    "author",
]

# 允许进包的顶层子目录（WorkBuddy 要求最多两层）
SUBDIRS = ("references", "scripts", "templates", "assets", "data")

# 永不打包
SKIP_DIRS = {"__pycache__", ".git", "node_modules", ".venv", "dist"}
SKIP_EXT = {".pyc", ".pyo", ".DS_Store"}


def yaml_str(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def split_frontmatter(text: str):
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?(.*)$", text, re.S)
    if not m:
        raise SystemExit("SKILL.md 不是以 --- frontmatter 开头")
    return m.group(1).splitlines(), m.group(2)


def existing_keys(fm_lines) -> set:
    return {ln.split(":", 1)[0].strip() for ln in fm_lines if re.match(r"^[A-Za-z_-]+:", ln)}


def detect_version(fm_lines) -> str | None:
    """先找缩进的 metadata.version，再找顶层 version。"""
    for line in fm_lines:
        m = re.match(r"^\s+version:\s*[\"']?([^\"'\s]+)", line)
        if m:
            return m.group(1)
    for line in fm_lines:
        m = re.match(r"^version:\s*[\"']?([^\"'\s]+)", line)
        if m:
            return m.group(1)
    return None


def detect_name(fm_lines) -> str:
    for line in fm_lines:
        m = re.match(r"^name:\s*[\"']?([^\"'\s]+)", line)
        if m:
            return m.group(1)
    raise SystemExit("frontmatter 里没找到 name")


def iter_files(skill_dir: str):
    """产出 (磁盘路径, 包内相对路径)。跳过缓存与非法目录。"""
    for sub in SUBDIRS:
        d = os.path.join(skill_dir, sub)
        if not os.path.isdir(d):
            continue
        for root, dirs, files in os.walk(d):
            dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
            for fn in sorted(files):
                if fn in SKIP_EXT or os.path.splitext(fn)[1] in SKIP_EXT:
                    continue
                p = os.path.join(root, fn)
                rel = os.path.relpath(p, skill_dir).replace("\\", "/")
                yield p, rel


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skill-dir", required=True)
    ap.add_argument("--display-name", required=True)
    ap.add_argument("--display-name-en", required=True)
    ap.add_argument("--desc-zh", required=True)
    ap.add_argument("--desc-en", required=True)
    ap.add_argument("--version", default=None)
    ap.add_argument("--author", default="xixi048")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    skill_dir = os.path.abspath(args.skill_dir)
    src = os.path.join(skill_dir, "SKILL.md")
    if not os.path.isfile(src):
        raise SystemExit("找不到 SKILL.md: " + src)

    with open(src, encoding="utf-8") as f:
        text = f.read()

    fm_lines, body = split_frontmatter(text)
    have = existing_keys(fm_lines)
    name = detect_name(fm_lines)
    version = args.version or detect_version(fm_lines)
    if not version:
        raise SystemExit("没传 --version，frontmatter 里也没有 version")

    inject = []
    if "display_name" not in have:
        inject.append("display_name: " + yaml_str(args.display_name))
    if "display_name_en" not in have:
        inject.append("display_name_en: " + yaml_str(args.display_name_en))
    if "description_zh" not in have:
        inject.append("description_zh: " + yaml_str(args.desc_zh))
    if "description_en" not in have:
        inject.append("description_en: " + yaml_str(args.desc_en))
    if "version" not in have:
        inject.append("version: " + yaml_str(version))
    if "author" not in have:
        inject.append("author: " + yaml_str(args.author))

    out_fm = list(fm_lines)
    try:
        idx = next(i for i, l in enumerate(out_fm) if l.startswith("license:"))
    except StopIteration:
        idx = len(out_fm)
    out_fm[idx:idx] = inject

    new_text = "---\n" + "\n".join(out_fm) + "\n---\n" + body

    # 自检
    keys = existing_keys(out_fm)
    missing = [k for k in REQUIRED if k not in keys]
    if missing:
        raise SystemExit("仍缺必填字段: " + ", ".join(missing))
    if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", name):
        raise SystemExit("name 不是 hyphen-case: " + name)
    if re.search(r"[<>]", "\n".join(out_fm)):
        raise SystemExit("frontmatter 含尖括号，会被驳回")

    out_dir = args.out or os.path.join(skill_dir, "dist")
    os.makedirs(out_dir, exist_ok=True)
    out_zip = os.path.join(out_dir, "%s-wb-%s.zip" % (name, version))

    count = 0
    deepest = 0
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("SKILL.md", new_text)
        count += 1
        for p, rel in iter_files(skill_dir):
            z.write(p, rel)
            count += 1
            deepest = max(deepest, rel.count("/"))

    size = os.path.getsize(out_zip)
    if size > 3 * 1024 * 1024:
        raise SystemExit("包超过 3MB 上限: %.2f MB" % (size / 1048576.0))

    print("OK ->", out_zip)
    print("   name:", name, "| version:", version)
    print("   files:", count, "| 最深路径层级:", deepest, "(WorkBuddy 建议 <=2)")
    print("   size: %.1f KB (上限 3MB)" % (size / 1024.0))
    if deepest > 2:
        print("   WARN: 路径超过两层，可能需要拍平")


if __name__ == "__main__":
    main()
