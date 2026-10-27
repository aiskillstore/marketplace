#!/usr/bin/env python3
"""仓库自检：frontmatter、相对链接、agents 元数据、示例中的编号泄露与手机号。

用法：python3 scripts/validate.py   （只用标准库，退出码 0 = 通过）
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
errors = []


def err(msg):
    errors.append(msg)


# 1. SKILL.md frontmatter
skill = ROOT / "SKILL.md"
text = skill.read_text(encoding="utf-8")
m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
if not m:
    err("SKILL.md 缺少 YAML frontmatter")
else:
    fm = dict(re.findall(r"^(\w+):\s*(.+)$", m.group(1), re.M))
    if fm.get("name") != ROOT.name and fm.get("name") != "resume-claim-guard":
        err(f"frontmatter name={fm.get('name')!r} 与仓库名不一致")
    if not fm.get("description"):
        err("frontmatter 缺少 description")
    elif len(fm["description"]) > 1024:
        err("description 超过 1024 字符")

# 2. agents/openai.yaml
oa = ROOT / "agents" / "openai.yaml"
if not oa.exists():
    err("缺少 agents/openai.yaml")
else:
    y = oa.read_text(encoding="utf-8")
    for key in ("display_name", "short_description", "default_prompt"):
        if key + ":" not in y:
            err(f"agents/openai.yaml 缺少 {key}")
    if "$resume-claim-guard" not in y:
        err("default_prompt 未引用 $resume-claim-guard")

# 3. Markdown 相对链接都能找到
link_re = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")
for md in ROOT.rglob("*.md"):
    if ".git" in md.parts:
        continue
    for target in link_re.findall(md.read_text(encoding="utf-8")):
        if re.match(r"^[a-z]+:", target):
            continue
        if not (md.parent / target).resolve().exists():
            err(f"{md.relative_to(ROOT)}: 链接不存在 -> {target}")

# 4. 对外文件不得出现内部编号：示例里定向写出的简历（resume-targeted*）。
#    体检用的输入简历（resume.html 等）可能故意含泄露，不在此查。
id_re = re.compile(r"\b[FC]-\d{2}\b")
for f in ROOT.glob("examples/**/*"):
    if not f.is_file():
        continue
    name = f.name.lower()
    if not name.startswith("resume-targeted"):
        continue
    body = re.sub(r"<!--.*?-->", "", f.read_text(encoding="utf-8"), flags=re.S)
    if name.endswith(".md"):
        body = body.split("\n## 内部对照")[0]  # 示例简历可在文末附内部对照表
    for hit in sorted(set(id_re.findall(body))):
        err(f"{f.relative_to(ROOT)}: 对外正文出现内部编号 {hit}")

# 5. 网页版提示词必须带上核心规则，防止和 SKILL.md 漂移
prompt = (ROOT / "PROMPT.md").read_text(encoding="utf-8")
for must in ("参与/协助", "计划 → 原型", "确认", "最多 3 个", "不要输出通过率", "统一口径"):
    if must not in prompt:
        err(f"PROMPT.md 缺少核心规则关键词：{must}")

# 6. 不提交疑似真实手机号
phone_re = re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)")
for f in ROOT.rglob("*"):
    if f.is_file() and ".git" not in f.parts and f.suffix in {".md", ".html", ".txt", ".yaml", ".py"}:
        if phone_re.search(f.read_text(encoding="utf-8", errors="ignore")):
            err(f"{f.relative_to(ROOT)}: 疑似手机号")

if errors:
    print("FAIL")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print("OK")
