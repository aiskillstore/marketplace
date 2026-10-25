#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_package.py —— 为不同商店生成对应形态的上架包（零第三方依赖）

各商店对"包长什么样"的要求不一致，这是最容易被忽略、也最容易导致提交被拒的一环：

  skills.sh / skillstore.io  → 直接给 GitHub 仓库 URL，怕的是**路径布局**对不上
  Cow Skill Hub / machina    → 上传 zip，且要求 **SKILL.md 位于 zip 根目录**
  扣子 / 元器 / 文心         → 不接受 SKILL.md，需要移植（见 03-worldB-porting.md）

因此本脚本产出三种形态：
  repo     —— 保持原样（推 GitHub，靠布局约定被发现）
  skillroot —— 把技能子目录提到 zip 根，使 SKILL.md 位于顶层
  flat     —— skillroot + 剔除开发期噪声（tests/ __pycache__ 等）

用法:
    python build_package.py <repo_root> <skill_subdir> [--version x.y.z] [--out DIR]

Python 3.8+
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import zipfile
from pathlib import Path
from typing import List, Tuple

SKIP_NAMES = {
    ".git", ".gitignore", ".github", ".svn", ".hg",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    "node_modules", ".venv", "venv", ".idea", ".vscode", ".DS_Store",
    ".pre-commit-config.yaml",
}
SKIP_SUFFIX = {".pyc", ".pyo", ".bak", ".tmp", ".log", ".orig", ".rej"}
# 开发期验证样本 + 备份：对外发布必须剔除（同时也是版权红线）
SKIP_DIRS_DEV = {"tests", "test", "samples", "artifacts"}


def should_skip(p: Path, root: Path, include_dev: bool) -> bool:
    rel = p.relative_to(root)
    parts = set(rel.parts)
    if parts & SKIP_NAMES:
        return True
    if p.name in SKIP_NAMES:
        return True
    if p.suffix.lower() in SKIP_SUFFIX:
        return True
    if not include_dev and any(str(rel).startswith(d + os.sep) or rel.parts[0] == d
                               for d in SKIP_DIRS_DEV):
        return True
    if p.name.endswith(".allcg-bak") or re.search(r"\.allcg-bak-\d{8}-\d{6}", p.name):
        return True
    return False


def collect(root: Path, include_dev: bool) -> List[Path]:
    out: List[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        d = Path(dirpath)
        dirnames[:] = [x for x in dirnames
                       if x not in SKIP_NAMES and not should_skip(d / x, root, include_dev)]
        for fn in filenames:
            f = d / fn
            if should_skip(f, root, include_dev):
                continue
            out.append(f)
    return sorted(out, key=lambda x: str(x).lower())


def write_zip(files: List[Path], base: Path, out_path: Path,
              arc_root: str = "") -> Tuple[int, str]:
    # 注意：不要用 unlink 清理旧文件。ZipFile('w') 本身就会截断覆盖，
    # 额外的删除步骤在某些环境（回收站/沙箱钩子）下会失败并中断流程。
    out_path.parent.mkdir(parents=True, exist_ok=True)
    h = hashlib.sha256()
    n = 0
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for f in files:
            rel = f.relative_to(base).as_posix()
            arc = f"{arc_root}/{rel}" if arc_root else rel
            data = f.read_bytes()
            h.update(data)
            z.writestr(arc, data)
            n += 1
    digest = h.hexdigest()
    (out_path.with_suffix(out_path.suffix + ".sha256")).write_text(
        f"{digest}  {out_path.name}\n", encoding="utf-8")
    return n, digest


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="为不同商店生成上架包")
    ap.add_argument("repo_root", help="仓库根目录")
    ap.add_argument("skill_subdir", help="技能子目录（内含 SKILL.md）")
    ap.add_argument("--version", default=None, help="版本号，缺省从 frontmatter 读")
    ap.add_argument("--out", default=None, help="输出目录，默认 <repo>/dist")
    ap.add_argument("--include-dev", action="store_true",
                    help="包含 tests/ 等开发样本（默认剔除，发布请勿开）")
    args = ap.parse_args(argv)

    repo = Path(args.repo_root).expanduser().resolve()
    skill = Path(args.skill_subdir)
    skill_dir = skill if skill.is_absolute() else repo / skill
    skill_dir = skill_dir.resolve()

    if not skill_dir.is_dir() or not (skill_dir / "SKILL.md").is_file():
        print(f"[FATAL] 技能目录无效或缺少 SKILL.md：{skill_dir}", file=sys.stderr)
        return 2

    version = args.version
    if not version:
        # version 可能平铺，也可能缩进写在 metadata: 子映射里
        m = re.search(r'^\s*version:\s*["\']?([\w.\-]+)',
                      (skill_dir / "SKILL.md").read_text(encoding="utf-8", errors="replace"),
                      re.MULTILINE)
        version = m.group(1) if m else "0.0.0"

    name = skill_dir.name
    out_dir = Path(args.out).expanduser().resolve() if args.out else repo / "dist"
    out_dir.mkdir(parents=True, exist_ok=True)

    results = {}

    # 形态 A：skillroot —— SKILL.md 提到 zip 根
    files_a = collect(skill_dir, include_dev=False)
    p_a = out_dir / f"{name}-v{version}-skillroot.zip"
    n, dig = write_zip(files_a, skill_dir, p_a)
    results["skillroot"] = {"path": str(p_a), "files": n, "sha256": dig,
                            "note": "SKILL.md 位于 zip 根；适用于 Cow Skill Hub / machina.directory"}

    # 形态 B：flat —— 与 A 同构但明确剔除 references 以外的开发噪声（当前等价于 A，
    #         保留此形态用于将来把 assets/ 加回来而仍排除 tests/）
    results["flat"] = dict(results["skillroot"])
    results["flat"]["note"] = ("同 skillroot；若将来加入 assets/ 或 examples/，"
                               "此形态仍保证不含测试样本与备份文件")

    # 形态 C：repo —— 不打包，输出路径布局体检
    rel = skill_dir.relative_to(repo).as_posix()
    standard = [
        "{name}/", "skills/{name}/", ".claude/skills/{name}/", ".codex/skills/{name}/",
        ".cursor/skills/{name}/", ".agent/skills/{name}/", ".agents/skills/{name}/",
        ".windsurf/skills/{name}/", "src/skills/{name}/",
    ]
    hit = [p for p in standard if p.format(name=name).strip("/") == rel]
    results["repo"] = {
        "path": str(repo),
        "skill_relpath": rel,
        "matches_standard_scan_path": bool(hit),
        "matched_pattern": hit[0] if hit else None,
        "note": "用于 skills.sh / skillstore.io 的仓库 URL 提交",
    }

    manifest = out_dir / f"package-manifest-v{version}.json"
    manifest.write_text(json.dumps(
        {"skill": name, "version": version, "built_by": "build_package.py",
         "variants": results},
        ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"技能 [{name}] v{version}")
    print(f"  仓库形态    : {rel}  "
          f"{'✔ 命中标准扫描路径 ' + (hit[0] if hit else '') if hit else '✘ 未命中任何标准扫描路径'}")
    print(f"  skillroot   : {p_a.name}  ({n} 个文件)")
    print(f"                sha256 {dig[:32]}…")
    print(f"  清单        : {manifest.name}")
    if args.include_dev:
        print("\n  ⚠ 本次打包包含了开发样本/备份文件，仅供本地验证，不要对外发布")
    return 0


if __name__ == "__main__":
    sys.exit(main())
