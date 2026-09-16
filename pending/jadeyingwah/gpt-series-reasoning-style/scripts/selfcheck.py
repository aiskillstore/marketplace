#!/usr/bin/env python3
"""静态自检——针对当前极简版（文件级渐进加载结构）。

检查什么（机器能验的）：
1. 版本一致性：SKILL.md 里的 version = VERSION 文件内容
2. 文件存在：SKILL.md、VERSION、references/{plan,review,multi-agent}.md、templates/*.md
3. 结构完整：frontmatter、五阶段流程、阶段2/5 的文件级渐进加载点、任务后遗忘规则
4. 八条纪律：规则已下沉到 references/review-rules.md，逐条关键词检查
5. 代码块配对：``` 数量是偶数

Python 3.7+ 标准库。退出码：0=全过，1=有失败，2=用法错。
"""
from __future__ import annotations

import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILL_MD = REPO_ROOT / "SKILL.md"
VERSION_FILE = REPO_ROOT / "VERSION"

failures = []
passes = []


def check(name: str, condition: bool, detail: str = ""):
    if condition:
        passes.append(f"  ✓ {name}")
    else:
        failures.append(f"  ✗ {name}" + (f" — {detail}" if detail else ""))


def main():
    # 1. 版本一致性
    if SKILL_MD.exists() and VERSION_FILE.exists():
        skill_text = SKILL_MD.read_text(encoding="utf-8")
        version_text = VERSION_FILE.read_text(encoding="utf-8").strip()
        m = re.search(r"^version:\s*(.+)$", skill_text, re.MULTILINE)
        skill_version = m.group(1).strip() if m else None
        check(
            "版本一致",
            skill_version == version_text,
            f"SKILL.md={skill_version}, VERSION={version_text}",
        )
    else:
        check("版本文件存在", False, "SKILL.md 或 VERSION 不存在")

    # 2. 文件存在（含「文件级渐进加载」的两个规则文件）
    check("SKILL.md 存在", SKILL_MD.exists())
    check("VERSION 存在", VERSION_FILE.exists())
    PLAN = REPO_ROOT / "references" / "plan-rules.md"
    REVIEW = REPO_ROOT / "references" / "review-rules.md"
    check("references/plan-rules.md 存在", PLAN.exists())
    check("references/review-rules.md 存在", REVIEW.exists())
    check("references/multi-agent.md 存在", (REPO_ROOT / "references/multi-agent.md").exists())
    check("templates/commander.md 存在", (REPO_ROOT / "templates/commander.md").exists())
    check("templates/executor.md 存在", (REPO_ROOT / "templates/executor.md").exists())
    check("templates/reviewer.md 存在", (REPO_ROOT / "templates/reviewer.md").exists())

    # 3. 结构完整（五阶段 + 文件级渐进加载点 + 任务后遗忘）
    if SKILL_MD.exists():
        text = SKILL_MD.read_text(encoding="utf-8")

        check("有 frontmatter", text.startswith("---\n"))
        check("有五阶段流程", "五阶段" in text)
        check("阶段2 指向 plan-rules.md", "plan-rules.md" in text)
        check("阶段5 指向 review-rules.md", "review-rules.md" in text)
        check("任务后遗忘规则内容", "彻底忘记" in text)

        # 4. 代码块配对
        fence_count = len(re.findall(r"^```", text, re.MULTILINE))
        check("代码块配对（``` 数量为偶数）", fence_count % 2 == 0, f"有 {fence_count} 个 ```")

        # 5. 行数统计
        line_count = len(text.splitlines())
        passes.append(f"  ℹ SKILL.md 共 {line_count} 行")

    # 6. 八条纪律（规则已下沉到 review-rules.md）
    if REVIEW.exists():
        rtext = REVIEW.read_text(encoding="utf-8")
        for kw in ("真打开看一眼", "未验证标注", "交付声明对得上", "失败两次换路",
                   "全绿不算证据", "关键数字重算", "临时物隔离", "防死循环"):
            check(f"纪律：{kw}", kw in rtext)
    else:
        check("纪律文件可读", False, "review-rules.md 不存在")

    # 输出结果
    print("=== selfcheck 结果 ===")
    for p in passes:
        print(p)
    for f in failures:
        print(f)
    print(f"\n通过 {len(passes)} 项，失败 {len(failures)} 项")

    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
