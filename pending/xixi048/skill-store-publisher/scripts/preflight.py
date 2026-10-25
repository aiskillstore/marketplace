#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
skill-publish-preflight —— 上架前体检（适配任意 SKILL.md 型技能，零第三方依赖）

把「技能被商店拒收」这件事从"事后救火"前移到"提交前一次跑完"。
检查项对齐真实商店规则（skills.sh 扫描路径、skillstore.io 安全审查、
扣子 Coze 商店文案规范、skillbay.sh 证据要求）。

用法:
    python preflight.py <skill_dir>                 # 体检报告
    python preflight.py <skill_dir> --json out.json # 机器可读结果
    python preflight.py <skill_dir> --strict        # WARN 也视为失败

退出码: 0=通过(或仅 INFO)  1=存在 ERROR  2=参数/环境错误

Python 3.8+
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------- 常量配置

LEVEL_ORDER = {"INFO": 0, "WARN": 1, "ERROR": 2}

# skills.sh / 多数 Claude-Code 系目录的标准扫描路径（相对仓库根）
# 参考 skills.sh 索引行为 + Agent Skills 开放规范
SCAN_PATHS = (
    "{name}/",
    "skills/{name}/",
    ".claude/skills/{name}/",
    ".codex/skills/{name}/",
    ".cursor/skills/{name}/",
    ".agent/skills/{name}/",
    ".agents/skills/{name}/",
    ".windsurf/skills/{name}/",
    "src/skills/{name}/",
)

# 会被多数商店安全审查拦截的高危点
DANGEROUS_PATTERNS: Dict[str, str] = {
    r"\beval\s*\(": "动态执行 eval()",
    r"\bexec\s*\(": "动态执行 exec()",
    r"\bcompile\s*\(": "动态编译 compile()",
    r"os\.system\s*\(": "shell 调用 os.system()",
    r"subprocess\.(Popen|run|call|check_output|check_call)\s*\(": "子进程 subprocess",
    r"shutil\.rmtree\s*\(": "递归删除 rmtree()",
    r"__import__\s*\(": "动态 import",
    r"pickle\.loads?\s*\(": "pickle 反序列化（可被构造恶意 payload）",
    r"marshal\.loads?\s*\(": "marshal 反序列化",
    r"pty\.spawn\s*\(": "伪终端 spawn",
}

NETWORK_PATTERNS: Dict[str, str] = {
    r"\brequests\.(get|post|put|delete|patch|head)\s*\(": "HTTP 请求 requests",
    r"\burllib\.request\.urlopen\s*\(": "HTTP 请求 urllib",
    r"\bsocket\.socket\s*\(": "原始 socket",
    r"https?://": "字面量 URL",
}

SECRET_PATTERNS: Dict[str, str] = {
    r"sk-[A-Za-z0-9]{20,}": "疑似 OpenAI API Key",
    r"ghp_[A-Za-z0-9]{30,}": "GitHub Personal Token",
    r"gho_[A-Za-z0-9]{30,}": "GitHub OAuth Token",
    r"AKIA[0-9A-Z]{16}": "AWS Access Key",
    r"xox[baprs]-[A-Za-z0-9-]{10,}": "Slack Token",
    r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----": "私钥文件",
    r"(?i)(api[_-]?key|secret|password|token)\s*=\s*[\"'][^\"']{8,}[\"']": "硬编码凭证字面量",
}

BINARY_EXT = {
    ".exe", ".dll", ".so", ".dylib", ".bin", ".msi", ".dmg",
    ".zip", ".tar", ".gz", ".7z", ".rar", ".jar",
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".mp4", ".mp3",
}
VCS_DIRS = {".git", ".svn", ".hg", ".hgignore"}
NOISE_DIRS = {"__pycache__", "node_modules", ".venv", "venv", ".idea", ".vscode", ".pytest_cache"}

MAX_SKILL_MD_LINES = 500          # 开放规范建议上限
MAX_SINGLE_FILE_BYTES = 200 * 1024
MAX_TOTAL_BYTES = 2 * 1024 * 1024
PERMISSIVE_LICENSES = ("mit", "apache-2.0", "apache 2.0", "bsd", "isc", "cc0", "ms-pl", "unlicense")


# ---------------------------------------------------------------- 数据模型

class Finding:
    __slots__ = ("level", "code", "message", "hint")

    def __init__(self, level: str, code: str, message: str, hint: str = "") -> None:
        self.level = level
        self.code = code
        self.message = message
        self.hint = hint

    def as_dict(self) -> Dict[str, str]:
        return {"level": self.level, "code": self.code,
                "message": self.message, "hint": self.hint}


class Report:
    def __init__(self) -> None:
        self.findings: List[Finding] = []

    def add(self, level: str, code: str, message: str, hint: str = "") -> None:
        self.findings.append(Finding(level, code, message, hint))

    def info(self, code: str, message: str, hint: str = "") -> None:
        self.add("INFO", code, message, hint)

    def warn(self, code: str, message: str, hint: str = "") -> None:
        self.add("WARN", code, message, hint)

    def error(self, code: str, message: str, hint: str = "") -> None:
        self.add("ERROR", code, message, hint)

    def worst(self) -> str:
        if not self.findings:
            return "INFO"
        return max((f.level for f in self.findings), key=lambda lv: LEVEL_ORDER[lv])


# ---------------------------------------------------------------- 工具函数

def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def parse_yaml_frontmatter(text: str) -> Optional[Dict[str, Any]]:
    """手写一个够用的 frontmatter 解析（避免引入 PyYAML 依赖）。"""
    if not text.startswith("---"):
        return None
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return None

    body = lines[1:end]
    meta: Dict[str, Any] = {}
    current_key: Optional[str] = None
    current_indent = 0
    sub: Dict[str, Any] = {}

    for raw in body:
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip())
        stripped = raw.strip()

        kv = re.match(r"^([A-Za-z_][\w.-]*)\s*:\s*(.*)$", stripped)
        if kv and (indent == 0 or current_key is None):
            if current_key and sub:
                meta[current_key] = dict(sub)
                sub = {}
            current_key = kv.group(1)
            value = kv.group(2).strip()
            meta[current_key] = _strip_quotes(value)
            current_indent = indent
        elif kv and current_key is not None and indent > current_indent:
            if not isinstance(meta.get(current_key), dict):
                if meta.get(current_key) not in ("", None):
                    sub = {}
                else:
                    meta[current_key] = {}
                    sub = meta[current_key]
            if isinstance(meta.get(current_key), dict):
                meta[current_key][kv.group(1)] = _strip_quotes(kv.group(2).strip())
        elif current_key is not None and isinstance(meta.get(current_key), str) and indent > current_indent:
            # 多行标量（YAML 折叠写法）
            meta[current_key] = (meta[current_key] + " " + stripped).strip()

    if current_key and sub:
        meta[current_key] = dict(sub)

    return meta


def _strip_quotes(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ("'", '"'):
        return s[1:-1]
    return s


def kebab_ok(name: str) -> bool:
    return bool(re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name or ""))


def iter_files(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames
                       if d not in VCS_DIRS and d not in NOISE_DIRS]
        for fn in filenames:
            yield Path(dirpath) / fn


def scan_patterns(files: List[Path]) -> Dict[str, List[str]]:
    hits: Dict[str, List[str]] = {}
    for f in files:
        if f.suffix.lower() not in (".py", ".sh", ".bash", ".js", ".ts", ".mjs", ".rb", ".ps1", ".md"):
            continue
        text = read_text(f)
        if not text:
            continue
        for name, table in (("dangerous", DANGEROUS_PATTERNS),
                            ("network", NETWORK_PATTERNS),
                            ("secret", SECRET_PATTERNS)):
            flags = re.IGNORECASE if name == "secret" else 0
            for pat, label in table.items():
                try:
                    found = re.search(pat, text, flags)
                except re.error:
                    continue
                if found:
                    rel = str(f)
                    hits.setdefault(name, []).append(f"{label}  @ {rel}")
    return hits


# ---------------------------------------------------------------- 检查项

def check_frontmatter(skill_dir: Path, rep: Report) -> Dict[str, Any]:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        rep.error("FM-001", "缺少 SKILL.md —— 所有商店都把它当硬性准入条件",
                  "技能根目录下必须有 SKILL.md")
        return {}

    text = read_text(skill_md)
    meta = parse_yaml_frontmatter(text)
    if meta is None:
        rep.error("FM-002", "SKILL.md 没有合法的 YAML frontmatter（缺 --- 包裹）",
                  "文件开头必须是 `---\\nname: ...\\n---`")
        return {}

    name = str(meta.get("name", "")).strip()
    desc = str(meta.get("description", "")).strip()

    # --- name ---
    if not name:
        rep.error("FM-010", "frontmatter 缺 name")
    elif not kebab_ok(name):
        rep.error("FM-011", f"name `{name}` 不是小写连字符格式",
                  "商店用它做目录名/ID，只允许 a-z 0-9 和单个连字符")
    elif skill_dir.name != name:
        rep.warn("FM-012",
                 f"目录名 `{skill_dir.name}` 与 frontmatter name `{name}` 不一致",
                 "skills.sh 等按路径索引时会产生歧义，建议改成同名")

    # --- description ---
    if not desc:
        rep.error("FM-020", "frontmatter 缺 description")
    else:
        words = len(re.findall(r"[\w\u4e00-\u9fff]+", desc))
        if words < 15:
            rep.warn("FM-021", f"description 只有 {words} 个词，信息量偏低",
                     "要同时回答「它能干什么」和「什么时候该用它」，30 词以上更稳")
        if not re.search(r"[\u4e00-\u9fff]", desc) and not re.search(r"[A-Za-z]{3,}", desc):
            rep.error("FM-022", "description 没有可读自然语言")
        lower = desc.lower()
        has_what = any(k in lower for k in ("use", "when", "will", "用于", "触发", "关键词"))
        if not has_what:
            rep.warn("FM-023", "description 没写清触发时机",
                     "补上 `Use when ...` / `触发词：...`，否则模型难以判断何时加载")

    # --- 推荐元数据（开放规范写在 metadata 子映射里，也兼容平铺写法） ---
    nested = meta.get("metadata")
    nested = nested if isinstance(nested, dict) else {}
    for key in ("version", "author"):
        if key in meta or key in nested:
            continue
        rep.info("FM-030", f"建议补充 metadata.{key}",
                 "非强制，但商店抓取作者/版本时有用")

    return {"name": name, "description": desc, "meta": meta, "text": text}


def check_structure(skill_dir: Path, rep: Report) -> None:
    skill_md = skill_dir / "SKILL.md"
    if skill_md.is_file():
        n = len(read_text(skill_md).splitlines())
        if n > MAX_SKILL_MD_LINES:
            rep.warn("ST-010", f"SKILL.md 共 {n} 行，超过建议上限 {MAX_SKILL_MD_LINES}",
                     "正文应只放决策树与红线，细节拆到 references/")

    files = list(iter_files(skill_dir))
    if not files:
        rep.error("ST-020", "技能目录为空")
        return

    total = 0
    big: List[str] = []
    binaries: List[str] = []
    for f in files:
        try:
            size = f.stat().st_size
        except OSError:
            continue
        total += size
        if size > MAX_SINGLE_FILE_BYTES:
            big.append(f"{f.name} ({size // 1024}KB)")
        if f.suffix.lower() in BINARY_EXT and f.name != "SKILL.md":
            binaries.append(f.name)

    if big:
        rep.warn("ST-030", "存在过大文件：" + ", ".join(big),
                 f"单文件建议 <{MAX_SINGLE_FILE_BYTES // 1024}KB，大文件建议外部托管")
    if total > MAX_TOTAL_BYTES:
        rep.warn("ST-031", f"技能总大小 {total // 1024}KB，超过 {MAX_TOTAL_BYTES // 1024}KB",
                 "技能是按需加载的指令包，不是代码仓库")
    if binaries:
        rep.warn("ST-040", "包含二进制/图片资源：" + ", ".join(binaries),
                 "skillstore.io 明文认定 `no binaries`；图标应 monospace ASCII 或外链")

    # 引用完整性：SKILL.md 里出现的 references/ 文件必须真实存在
    if skill_md.is_file():
        text = read_text(skill_md)
        missing = []
        for m in re.finditer(r"references/([\w./-]+\.md)", text):
            rel = m.group(1)
            if not (skill_dir / "references" / Path(rel)).is_file():
                missing.append(rel)
        if missing:
            rep.warn("ST-050", "SKILL.md 引用了不存在的参考文件：" + ", ".join(sorted(set(missing))),
                     "断裂的引用会让加载方找不到文档")


def check_security(skill_dir: Path, rep: Report) -> None:
    files = list(iter_files(skill_dir))
    hits = scan_patterns(files)

    for line in sorted(set(hits.get("secret", []))):
        rep.error("SEC-001", "疑似泄露密钥：" + line,
                  "立刻吊销并改用环境变量；这类凭证一旦入库，历史里也删不干净")

    for line in sorted(set(hits.get("dangerous", []))):
        rep.warn("SEC-010", "高危调用：" + line,
                 "skillstore.io 会自动查 eval/exec/system；有正当理由也要在上架说明里写清")

    net = sorted(set(hits.get("network", [])))
    if net:
        rep.warn("SEC-020", "存在网络行为：" + "; ".join(net[:4]),
                 "审查重点项。纯离线技能建议连字面量 URL 都清掉")

    if not hits.get("dangerous") and not net:
        rep.info("SEC-000", "未发现高危调用与网络行为 —— 这是上架时最值钱的一条干净记录")


def check_repo(repo_root: Path, skill_dir: Path, rep: Report) -> None:
    if not (repo_root / "LICENSE").is_file() and not (skill_dir / "LICENSE").is_file():
        rep.error("REPO-010", "缺少 LICENSE 文件",
                  "skillstore.io 要求 MIT/Apache-2.0 等宽松协议；无许可证会被直接拒")
        return

    lic_text = ""
    for cand in (repo_root / "LICENSE", skill_dir / "LICENSE",
                 repo_root / "LICENSE.md", repo_root / "LICENSE.txt"):
        if cand.is_file():
            lic_text = read_text(cand)[:2000].lower()
            break

    if lic_text and not any(tok in lic_text for tok in PERMISSIVE_LICENSES):
        rep.warn("REPO-011", "LICENSE 看起来不是宽松协议", "建议 MIT 或 Apache-2.0")
    if re.search(r"<(作者|your name|copyright holder|year)>", lic_text, re.IGNORECASE):
        rep.error("REPO-012", "LICENSE 里还有未替换的作者/年份占位符",
                  "这是审核一眼可见的低级错误")
    elif lic_text.startswith("mit license") and "copyright" not in lic_text:
        rep.warn("REPO-013", "LICENSE 没有 Copyright 行，建议补上 `Copyright (c) <年份> <作者>`")

    if not (repo_root / "README.md").is_file():
        rep.warn("REPO-020", "缺少 README.md", "这是人工审核和 GitHub 冷启动流量的主入口")
    if not (repo_root / ".gitignore").is_file():
        rep.info("REPO-021", "建议加 .gitignore", "避免 __pycache__ / 临时文件入库")

    # skills.sh 扫描路径命中情况
    name = ""
    fm = parse_yaml_frontmatter(read_text(skill_dir / "SKILL.md")) or {}
    name = str(fm.get("name", skill_dir.name))
    try:
        rel = skill_dir.relative_to(repo_root).as_posix()
    except ValueError:
        rel = ""
    matched = []
    for pat in SCAN_PATHS:
        if rel == pat.format(name=name).strip("/"):
            matched.append(pat)
    if rel and not matched:
        rep.warn("REPO-030",
                 f"技能路径 `{rel}` 不在任何标准扫描路径内，skills.sh 可能索引不到",
                 "建议改成 " + " / ".join(SCAN_PATHS[:3]))
    elif matched:
        rep.info("REPO-031", f"命中标准扫描路径：{matched[0]}")


def check_listing_copy(skill_dir: Path, rep: Report) -> None:
    """上架文案物料是否齐备（对齐扣子商店要求：名称/简介/详述/图标/截图/分类/标签）"""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return
    text = read_text(skill_md)
    if not re.search(r"^#\s+\S", text, re.MULTILINE):
        rep.warn("LS-010", "SKILL.md 没有一级标题", "商店卡片通常取 H1 作为展示名")
    if "---" in text and re.search(r"\n#{2,3}\s*(红线|边界|不要|安全)", text):
        rep.info("LS-000", "包含边界/红线章节 —— 扣子、skillstore 审核会加分")


# ---------------------------------------------------------------- 主流程

def detect_repo_root(skill_dir: Path) -> Path:
    """向上找仓库根：先看 .git，再看 LICENSE。

    不能只用 skill_dir.parent：标准布局是 `<repo>/skills/<name>/`，
    parent 是 `skills/`，会让「缺 LICENSE / 缺 README」变成永久误报。
    """
    for cand in [skill_dir, *skill_dir.parents]:
        if (cand / ".git").exists():
            return cand
    for cand in [skill_dir, *skill_dir.parents]:
        if (cand / "LICENSE").is_file() or (cand / "README.md").is_file():
            return cand
    return skill_dir.parent


def run_checks(repo_root: Path, skill_dir: Path) -> Report:
    rep = Report()
    rep.info("SYS-000", f"仓库根：{repo_root}")
    rep.info("SYS-001", f"技能目录：{skill_dir}")

    fm = check_frontmatter(skill_dir, rep)
    check_structure(skill_dir, rep)
    check_security(skill_dir, rep)
    check_repo(repo_root, skill_dir, rep)
    check_listing_copy(skill_dir, rep)

    name = fm.get("name") or skill_dir.name
    desc_words = len(re.findall(r"[\w\u4e00-\u9fff]+", fm.get("description", "")))
    rep.info("SYS-010", f"技能名：{name} ｜ description {desc_words} 词")
    return rep


def render(report: Report, strict: bool) -> None:
    line = "─" * 68
    print(line)
    print("  skill-publish-preflight · 上架前体检")
    print(line)

    order = {"ERROR": 0, "WARN": 1, "INFO": 2}
    marks = {"ERROR": "✗", "WARN": "!", "INFO": "·"}
    for lv in ("ERROR", "WARN", "INFO"):
        group = [f for f in report.findings if f.level == lv]
        if not group:
            continue
        print(f"\n[{lv}] ({len(group)})")
        for f in sorted(group, key=lambda x: x.code):
            print(f"  {marks[lv]} {f.code}  {f.message}")
            if f.hint:
                print(f"      ↳ {f.hint}")

    worst = report.worst()
    failed = LEVEL_ORDER[worst] >= LEVEL_ORDER["ERROR"] or (strict and worst == "WARN")
    print("\n" + line)
    print(f"  结论：{'不通过，先修再提交' if failed else '通过，可以提交'}"
          f"   最高等级 = {worst}")
    print(line)


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        prog="preflight.py",
        description="SKILL.md 型技能的上架前体检（零依赖）")
    ap.add_argument("skill_dir", help="技能目录（内含 SKILL.md）")
    ap.add_argument("--repo-root", default=None,
                    help="仓库根目录，默认取 skill_dir 的父目录")
    ap.add_argument("--json", metavar="OUT", default=None, help="额外输出 JSON 报告")
    ap.add_argument("--strict", action="store_true", help="WARN 也按失败处理")
    args = ap.parse_args(argv)

    skill_dir = Path(args.skill_dir).expanduser().resolve()
    if not skill_dir.is_dir():
        print(f"[FATAL] 技能目录不存在：{skill_dir}", file=sys.stderr)
        return 2
    repo_root = (Path(args.repo_root).expanduser().resolve()
                 if args.repo_root else detect_repo_root(skill_dir))

    report = run_checks(repo_root, skill_dir)
    render(report, args.strict)

    if args.json:
        payload = {
            "skill_dir": str(skill_dir),
            "repo_root": str(repo_root),
            "worst_level": report.worst(),
            "findings": [f.as_dict() for f in report.findings],
        }
        try:
            Path(args.json).write_text(
                json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"  JSON 已写入：{args.json}")
        except OSError as exc:
            print(f"[FATAL] 写 JSON 失败：{exc}", file=sys.stderr)
            return 2

    worst = report.worst()
    if LEVEL_ORDER[worst] >= LEVEL_ORDER["ERROR"]:
        return 1
    if args.strict and worst == "WARN":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
