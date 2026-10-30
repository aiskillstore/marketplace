#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
submit_all.py —— 技能商店批量提交器（零第三方依赖）

设计原则：只走「公开 HTTP 接口」，不模拟浏览器。
凡是需要 OAuth 点击授权的渠道，脚本明确报 SKIP 并说明原因，
绝不用假凭据硬试。

已验证渠道：
  skillstore  POST https://skillstore.io/api/submit          仅需 github_url，服务端自拉仓库
  skillbay    POST https://skillbay.sh/api/v1/submissions/quick  multipart，需 contactEmail

用法：
  # 列出所有渠道
  python submit_all.py --list

  # 提交到 skillstore（已验证可匿名）
  python submit_all.py --channel skillstore \
      --repo https://github.com/xixi048/create-all-cg-save \
      --notes-file ../../cdq/STORE-LISTING.md

  # 提交到 skillbay（需要邮箱）
  python submit_all.py --channel skillbay \
      --repo https://github.com/xixi048/create-all-cg-save \
      --skill-md ../../cdq/create-all-cg-save/SKILL.md \
      --name xixi048 --email you@example.com

  # 查 skillstore 提交状态
  python submit_all.py --channel skillstore --status <submission_id>

  # 一次提交所有可用渠道
  python submit_all.py --all --repo ... --name ... --email ...
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

TIMEOUT = 60


# --------------------------------------------------------------------------
# 渠道注册表：每个渠道声明自己的提交形态与前置条件
# --------------------------------------------------------------------------
CHANNELS = {
    "skillstore": {
        "name": "skillstore.io",
        "endpoint": "https://skillstore.io/api/submit",
        "method": "json",
        "requires": ["repo"],
        "auth": "none",
        "note": "服务端自行拉取 GitHub 仓库并跑安全审计，创建 PR 待人工审核",
        "store_url": "https://skillstore.io",
    },
    "skillbay": {
        "name": "skillbay.sh",
        "endpoint": "https://skillbay.sh/api/v1/submissions/quick",
        "method": "multipart",
        "requires": ["skill_md", "name"],
        "auth": "none",
        "note": "AI-agent 友好 API，人工审核后会邮件索要 before/after 证据",
        "store_url": "https://skillbay.sh",
    },
    "skillsmd": {
        "name": "skillsmd.dev",
        "endpoint": "https://skillsmd.dev/api/submit",
        "method": "json",
        "requires": ["repo", "name"],
        "auth": "none",
        "note": "registry API，email 可选；repo 传 owner/repo 而非完整 URL",
        "store_url": "https://skillsmd.dev",
    },
    "cowagent": {
        "name": "cowagent.ai",
        "endpoint": "https://skills.cowagent.ai/api/skills/submit",
        "method": "json",
        "requires": ["repo"],
        "auth": "session",          # OAuth → 401
        "note": "需 GitHub OAuth 会话，纯脚本无法完成，需浏览器登录后取 cookie",
        "store_url": "https://skills.cowagent.ai",
    },
    "skills_sh": {
        "name": "skills.sh",
        "endpoint": None,
        "method": "auto_index",
        "requires": ["repo"],
        "auth": "none",
        "note": "无提交表单，靠路径匹配自动索引仓库中的 <name>/SKILL.md",
        "store_url": "https://skills.sh",
    },
}


# --------------------------------------------------------------------------
# 全量渠道注册表（含不可脚本化的渠道；用于 --registry 出表与人工跟进）
#
# kind:  api=公开 HTTP 接口 | pr=GitHub PR | cli=登录式 CLI | form=网页表单/OAuth
#        auto=仓库自动索引 | tool=宿主内置工具 | port=平台托管，必须移植
# paid:  none=仅免费 | paid=支持收费 | port=移植后才能收费
# --------------------------------------------------------------------------
REGISTRY = [
    ("github",   "GitHub",                "global", "repo", "none", "仓库本身；topics + skills/<name>/SKILL.md，是所有爬取型目录站的数据源"),
    ("skills_sh", "skills.sh",            "global", "auto", "none", "只索引 skills/<name>/SKILL.md，按安装量排行；无提交表单"),
    ("skillsmp",  "SkillsMP",             "global", "auto", "none", "爬公开仓库，需 >=2 stars；也有账号+人工审核 listing 表单"),
    ("agentskill","agentskill.sh",        "global", "form", "none", "https://agentskill.sh/submit（SPA，贴仓库 URL 后 Analyze & Import）"),
    ("skillstore","skillstore.io",        "global", "api",  "none", "POST /api/submit，匿名；服务端拉仓库 + 安全审计 → 机器人开 PR"),
    ("skillbay",  "skillbay.sh",          "global", "api",  "paid", "快速提交匿名；定价/上架需 seller 账号 + Stripe"),
    ("skillsmd",  "skillsmd.dev",         "global", "api",  "none", "POST /api/submit，repo 传 owner/repo"),
    ("buildwith", "buildwithclaude",      "global", "pr",   "none", "PR 到 plugins/all-skills/skills/<name>/SKILL.md"),
    ("composio",  "awesome-claude-skills","global", "pr",   "none", "PR 加一个 <name>/SKILL.md 目录 + README 表格行"),
    ("clawhub",   "ClawHub (openclaw)",   "global", "cli",  "none", "clawhub login + clawhub skill publish ./<dir> --slug --version"),
    ("tank",     "Tank (tankpkg.dev)",   "global", "cli",  "none", "npm i -g @tankpkg/cli; tank login; tank init; tank scan; tank publish"),
    ("skilld",    "skilld.dev",           "global", "cli",  "none", "Rust CLI 型注册中心，需发布者账号"),
    ("cowagent",  "Cow Skill Hub",        "global", "form", "none", "需 GitHub/Google 登录；上传 zip，SKILL.md 必须在包根"),
    ("cindyhub",  "Cindy SkillHub",       "cn",     "tool", "none", "宿主 publish_skill 工具，public 需审核；create 时必须显式指定 visibility"),
    ("tencentskillhub","腾讯 SkillHub",   "cn",     "form", "none", "ClawHub 本土镜像，https://skillhub.tencent.com/"),
    ("coze",      "扣子 Coze 技能商店",    "cn",     "port", "paid", "国内实测唯一支持 Skill 交易，创作者约 70%；需入驻商户"),
    ("zhipu",     "智谱 AgentMore",       "cn",     "port", "none", "Skills 广场，一键零 Token 安装"),
    ("alibaba",   "阿里 虾小宝 / 百炼",    "cn",     "port", "paid", "JVS Claw 内置 skill 市场；百炼 Agent Store 有打赏+分润"),
    ("bytedance", "字节 Find Skill",      "cn",     "form", "paid", "火山引擎侧入口，与扣子并列"),
    ("gptstore",  "GPT Store",            "global", "port", "paid", "抽 15%；需 ChatGPT Plus + Builder Profile"),
    ("msagent",   "Windows Agent Store",  "global", "port", "paid", "开发者 85%"),
    ("dify",      "Dify 市场",            "global", "port", "paid", "自建市场，私有部署 0 抽成"),
    # ---- 第二轮补遗（容易漏掉的一批）----
    ("lobehub",  "LobeHub Skills",        "global", "auto", "none", "lobehub.com/skills，Agent Skills 市场，无 /submit 入口（自动索引/账号提交）"),
    ("agentskills_cli", "agentskills.in",  "global", "cli",  "none", "「Universal Skill Manager」CLI 型，无网页提交页"),
    ("cursordir","Cursor Directory",      "global", "form", "none", "cursor.directory（MCP 为主），有 Vercel 人机校验"),
    ("xfyun",    "讯飞 Astron SkillHub",  "cn",     "form", "none", "skill.xfyun.cn/publish 有发布页，需讯飞账号"),
    ("kimi",     "月之暗面 Kimi Claw",     "cn",     "port", "none", "△ 二手信源，需移植为平台形态"),
    ("redbook",  "小红书 Red Skill",       "cn",     "form", "none", "△ 仅支持 Markdown 等有限格式"),
    ("meituan",  "美团 虾345 (xia345)",    "cn",     "form", "none", "△ Skill Hunter 聚合 SkillHub/ClawHub，域名未核实"),
    ("workbuddy","WorkBuddy 技能中心",     "cn",     "form", "none", "腾讯生态 agent，技能目录形态"),
    ("anthropics_skills", "anthropics/skills", "global", "pr", "none", "官方示例仓库，PR 新增 skills/<name>/"),
    ("claudeconn","Claude Connectors Directory","global","form","none","官方连接器目录，需审核"),
    ("mcpdirs",  "MCP 目录群",            "global", "form", "none", "Official MCP Registry / Smithery / Glama / mcp.so / PulseMCP — 需交付可跑的 MCP 服务"),
    ("awesomelists", "Awesome 列表群",     "global", "pr",   "none", "ComposioHQ/awesome-claude-skills、VoltAgent/awesome-agent-skills、hesreallyhim/awesome-claude-code、trailofbits/skills-curated"),
    ("wellknown","自建发现端点",           "global", "auto", "none", "/.well-known/agent-skills/index.json — 让任何 agent 直接发现你的技能源"),
]


class Result:
    def __init__(self, channel: str):
        self.channel = channel
        self.state = "PENDING"     # OK | FAIL | SKIP | PENDING
        self.detail = ""
        self.data: dict = {}

    def ok(self, detail: str, data: dict | None = None) -> "Result":
        self.state, self.detail = "OK", detail
        self.data = data or {}
        return self

    def fail(self, detail: str) -> "Result":
        self.state, self.detail = "FAIL", detail
        return self

    def skip(self, detail: str) -> "Result":
        self.state, self.detail = "SKIP", detail
        return self

    def as_dict(self) -> dict:
        return {"channel": self.channel, "state": self.state,
                "detail": self.detail, "data": self.data}


# --------------------------------------------------------------------------
# HTTP 基础
# --------------------------------------------------------------------------
def _request(url: str, data: bytes | None = None,
             headers: dict | None = None, method: str | None = None):
    hdrs = {"User-Agent": UA, "Accept": "application/json, text/plain, */*"}
    if headers:
        hdrs.update(headers)
    req = urllib.request.Request(url, data=data, headers=hdrs,
                                 method=method or ("POST" if data else "GET"))
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            raw = resp.read().decode("utf-8", "replace")
            return resp.status, raw
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", "replace")
        return exc.code, raw
    except urllib.error.URLError as exc:
        return 0, f"URLError: {exc.reason}"


def _post_json(url: str, payload: dict, extra_headers: dict | None = None):
    headers = {"Content-Type": "application/json"}
    if extra_headers:
        headers.update(extra_headers)
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    return _request(url, data=body, headers=headers, method="POST")


def _post_multipart(url: str, fields: dict, files: dict):
    """files: {field_name: (filename, bytes, content_type)}"""
    boundary = "----SkillPub" + uuid.uuid4().hex
    parts: list[bytes] = []

    for key, val in fields.items():
        if val is None or val == "":
            continue
        parts.append(
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="{key}"\r\n\r\n'
            f"{val}\r\n".encode("utf-8"))

    for key, (fname, blob, ctype) in files.items():
        parts.append(
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="{key}"; filename="{fname}"\r\n'
            f"Content-Type: {ctype}\r\n\r\n".encode("utf-8"))
        parts.append(blob)
        parts.append(b"\r\n")

    parts.append(f"--{boundary}--\r\n".encode("utf-8"))
    body = b"".join(parts)

    return _request(url, data=body, headers={
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Content-Length": str(len(body)),
    }, method="POST")


def _parse(raw: str):
    try:
        return json.loads(raw)
    except Exception:                                  # noqa: BLE001
        return {"_raw": raw[:400]}


# --------------------------------------------------------------------------
# 各渠道实现
# --------------------------------------------------------------------------
def submit_skillstore(repo: str, notes: str = "", notify: bool = False) -> Result:
    r = Result("skillstore")
    if not re.match(r"^https://github\.com/[\w-]+/[\w.-]+(?:/tree/[\w.-]+)?$", repo):
        return r.fail(f"仓库地址不合规（必须 https://github.com/user/repo）：{repo}")

    payload = {"github_url": repo, "notify_via_github": notify}
    if notes:
        payload["notes"] = notes

    code, raw = _post_json(CHANNELS["skillstore"]["endpoint"], payload, {
        "Origin": "https://skillstore.io",
        "Referer": "https://skillstore.io/submit",
    })
    body = _parse(raw)

    if code == 200 and body.get("success"):
        d = body.get("data", {})
        return r.ok(
            f"submission_id={d.get('submission_id')} status={d.get('status')} "
            f"skills={d.get('estimated_skills')} eta={d.get('estimated_time')}",
            d)
    msg = (body.get("error") or {}).get("message") or str(body)[:200]
    return r.fail(f"HTTP {code}: {msg}")


def skillstore_status(sid: str) -> Result:
    r = Result("skillstore-status")
    code, raw = _request(
        f"https://skillstore.io/api/submit?id={urllib.parse.quote(sid)}")
    body = _parse(raw)
    if code == 200 and body.get("success"):
        d = body.get("data", {})
        return r.ok(f"status={d.get('status')} pr={d.get('pr_url')} "
                    f"error={d.get('error_message')}", d)
    return r.fail(f"HTTP {code}: {raw[:200]}")


def submit_skillbay(skill_md_path: str, name: str, email: str,
                    title: str = "", description: str = "") -> Result:
    r = Result("skillbay")
    if not os.path.isfile(skill_md_path):
        return r.fail(f"SKILL.md 不存在：{skill_md_path}")
    if not email or "@" not in email:
        return r.skip("缺少有效 contactEmail（skillbay 审核后会邮件联系）")

    with open(skill_md_path, "rb") as fh:
        blob = fh.read()

    # frontmatter 里的 name/description 优先，否则交给平台自己读
    fields = {"contactName": name, "contactEmail": email}
    if title:
        fields["title"] = title
    if description:
        fields["description"] = description

    code, raw = _post_multipart(CHANNELS["skillbay"]["endpoint"], fields,
                                {"file": ("SKILL.md", blob, "text/markdown")})
    body = _parse(raw)
    if code in (200, 201):
        return r.ok(f"HTTP {code} 已提交待人工审核", body if isinstance(body, dict) else {})
    msg = (body.get("error") or {}).get("message") if isinstance(body, dict) else None
    return r.fail(f"HTTP {code}: {msg or str(body)[:200]}")


def submit_skillsmd(repo: str, name: str, description: str = "",
                    email: str = "") -> Result:
    """skillsmd.dev：repo 必须传 owner/repo，不接受完整 URL。"""
    r = Result("skillsmd")
    m = re.match(r"^https?://github\.com/([\w-]+/[\w.-]+?)(?:\.git)?/?$", repo or "")
    if m:
        slug = m.group(1)
    elif re.match(r"^[\w-]+/[\w.-]+$", repo or ""):
        slug = repo
    else:
        return r.fail(f"无法解析 owner/repo：{repo}")

    payload = {"repo": slug, "name": name or "create-all-cg-save"}
    if description:
        payload["description"] = description[:500]
    if email:
        payload["email"] = email

    code, raw = _post_json(CHANNELS["skillsmd"]["endpoint"], payload)
    body = _parse(raw)
    if code in (200, 201) and body.get("success"):
        return r.ok(f"id={body.get('id')} {body.get('message', '')}", body)
    msg = body.get("message") or body.get("error") or str(body)[:200]
    return r.fail(f"HTTP {code}: {msg}")


def submit_cowagent(repo: str) -> Result:
    r = Result("cowagent")
    code, _ = _post_json(CHANNELS["cowagent"]["endpoint"], {"github_url": repo})
    if code == 401:
        return r.skip("需要 GitHub OAuth 会话（401 Unauthorized）——纯 HTTP 无法自动完成")
    if code in (200, 201):
        return r.ok(f"HTTP {code} 已提交")
    return r.fail(f"HTTP {code}")


def probe_skills_sh(query: str) -> Result:
    """skills.sh 无提交接口，只能查是否已被索引。"""
    r = Result("skills_sh")
    url = f"https://skills.sh/api/search?q={urllib.parse.quote(query)}"
    code, raw = _request(url)
    if code != 200:
        return r.fail(f"HTTP {code}")
    body = _parse(raw)
    hits = body.get("skills") or []
    mine = [h for h in hits if "create-all-cg-save" in json.dumps(h).lower()]
    if mine:
        return r.ok(f"已被索引：{[h.get('id') for h in mine]}", {"hits": mine})
    return r.skip(f"尚未被索引（查询 {query!r} 命中 {len(hits)} 条，无本项目）")


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------
def cmd_registry():
    print(f"{'key':<12} {'名称':<22} {'区域':<7} {'形态':<6} {'收费':<6} 说明")
    print("-" * 120)
    for key, name, region, kind, paid, note in REGISTRY:
        print(f"{key:<12} {name:<22} {region:<7} {kind:<6} {paid:<6} {note}")
    print()
    print("kind: api=公开接口 pr=PR cli=登录CLI form=表单 auto=自动索引 tool=宿主工具 port=需移植")


def cmd_list():
    print(f"{'渠道':<12} {'登录要求':<10} {'前置条件':<28} 说明")
    print("-" * 100)
    for key, c in CHANNELS.items():
        req = ", ".join(c["requires"]) or "—"
        print(f"{key:<12} {c['auth']:<10} {req:<28} {c['note']}")
    print()
    print("auth=none 表示可直接脚本提交；session 表示必须浏览器/OAuth。")


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="技能商店批量提交器（仅走公开 HTTP 接口，不模拟浏览器）")
    ap.add_argument("--registry", action="store_true",
                    help="列出全量渠道注册表（含不可脚本化的渠道）")
    ap.add_argument("--list", action="store_true", help="列出可脚本提交的渠道与前置条件")
    ap.add_argument("--channel", help="指定渠道：" + ", ".join(CHANNELS))
    ap.add_argument("--all", action="store_true", help="提交所有可用渠道")
    ap.add_argument("--repo", help="GitHub 仓库地址")
    ap.add_argument("--skill-md", help="SKILL.md 路径")
    ap.add_argument("--notes", default="", help="给审核的说明")
    ap.add_argument("--notes-file", help="从文件读 notes")
    ap.add_argument("--name", default="", help="联系人姓名（skillbay）")
    ap.add_argument("--email", default="", help="联系人邮箱（skillbay）")
    ap.add_argument("--title", default="", help="自定义标题")
    ap.add_argument("--status", help="查询 skillstore 提交状态（传 submission_id）")
    ap.add_argument("--json", metavar="OUT", help="结果写入 JSON 文件")
    ap.add_argument("--dry-run", action="store_true", help="只打印将要发送的内容，不实际提交")
    args = ap.parse_args(argv)

    if args.registry:
        cmd_registry()
        return 0

    if args.list:
        cmd_list()
        return 0

    # ---------- 状态查询 ----------
    if args.status:
        r = skillstore_status(args.status)
        print(f"[{r.state}] {r.channel}: {r.detail}")
        return 0 if r.state == "OK" else 1

    # ---------- 需要 repo 的校验 ----------
    if not args.repo and (args.channel in ("skillstore", "skillsmd", "cowagent")
                          or args.all):
        print("错误：--repo 必填（形如 https://github.com/user/repo）", file=sys.stderr)
        return 2

    notes = args.notes
    if args.notes_file and os.path.isfile(args.notes_file):
        notes = open(args.notes_file, encoding="utf-8", errors="replace").read()[:4000]

    targets = list(CHANNELS) if args.all else ([args.channel] if args.channel else [])
    if not targets:
        ap.print_help()
        return 2

    results: list[Result] = []
    for key in targets:
        if key not in CHANNELS:
            print(f"未知渠道：{key}", file=sys.stderr)
            continue

        if args.dry_run:
            print(f"[DRY] {key}: 将 POST 到 {CHANNELS[key]['endpoint']}")
            continue

        t0 = time.time()
        if key == "skillstore":
            r = submit_skillstore(args.repo, notes)
        elif key == "skillbay":
            r = submit_skillbay(args.skill_md or "", args.name, args.email,
                                args.title)
        elif key == "skillsmd":
            r = submit_skillsmd(args.repo, args.name or "", notes, args.email)
        elif key == "cowagent":
            r = submit_cowagent(args.repo)
        elif key == "skills_sh":
            r = probe_skills_sh("all-cg-save")
        else:
            r = Result(key).skip("未实现")

        r.detail += f"  ({time.time() - t0:.1f}s)"
        results.append(r)
        print(f"[{r.state:^4}] {r.channel:<12} {r.detail}")

    # ---------- 汇总 ----------
    if results:
        summary = {"repo": args.repo, "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                   "results": [r.as_dict() for r in results]}
        n_ok = sum(1 for r in results if r.state == "OK")
        print()
        print(f"汇总：{n_ok}/{len(results)} 成功提交，"
              f"{sum(1 for r in results if r.state=='SKIP')} 跳过，"
              f"{sum(1 for r in results if r.state=='FAIL')} 失败")
        if args.json:
            with open(args.json, "w", encoding="utf-8") as fh:
                json.dump(summary, fh, ensure_ascii=False, indent=2)
            print(f"结果已写入 {args.json}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
