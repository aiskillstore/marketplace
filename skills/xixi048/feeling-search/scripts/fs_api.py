#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
feeling-search · 感觉检索 API 客户端（零第三方依赖，Python 3.8+）

把一句口语化的「感觉」描述落到感受词 + 视觉风格上。两条路径：

  本地词典档   用缓存的词表做命中，不联网、不花钱（大多数情况走这条）
  云端 analyze 本地一个词都没命中、且显式允许上云时才调用，消耗 1 次额度

本地结果绝不会标成云端结果：source 字段只有 "local" / "cloud" 两个值。

子命令
    status                      额度/缓存/连通性体检
    dict [--refresh]            拉取或读出词表缓存
    analyze <文本>              感受词 + 风格（本地优先，零命中才上云）
    lookup <词>                 单个词的落点风格、共现词、对立词（免费）
    style-words <风格id>        某风格挂了哪些词（免费）
    style <风格id>              风格详情，含图片与出处（计费 1 次）
    images <id1,id2,...>        批量取图，最多 5 个（计费 1 次）

通用参数
    --json          输出 JSON（默认人类可读）
    --allow-cloud   允许在本地零命中时调用付费的 /v2/analyze
    --words N       返回词数 1–12（默认 8）
    --styles N      返回风格数 1–30（默认 12）
    --base URL      服务端点，默认 https://xiximm.cloud
    --offline       完全不联网，只用缓存

环境变量
    FS_API_BASE     服务端点（默认 https://xiximm.cloud）
    FS_QUOTA        云端额度 token；留空则永不调用付费端点
    FS_CACHE_DIR    词表缓存目录（默认 ~/.cache/feeling-search）
    FS_CACHE_TTL    缓存有效期秒数（默认 604800 = 7 天）
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

try:  # Windows 控制台默认 GBK，中文会炸
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

DEFAULT_BASE = "https://xiximm.cloud"
CACHE_FILE = "dictionary.json"
CACHE_TTL = 7 * 24 * 3600
TIMEOUT = 20

# 服务端口径：text 最长 500 字，>32KB 的请求体会被拒
MAX_CHARS = 500


class ApiError(Exception):
    """线上错误。code 是服务端 error 字段，http 是状态码，payload 是原始响应体。"""

    def __init__(self, message, code="", http=0, payload=None):
        super().__init__(message)
        self.code = code
        self.http = http
        self.payload = payload or {}


# ---------------------------------------------------------------- 基础 IO

def env_base():
    return (os.environ.get("FS_API_BASE") or DEFAULT_BASE).rstrip("/")


def env_quota():
    return (os.environ.get("FS_QUOTA") or "").strip()


def cache_dir():
    d = os.environ.get("FS_CACHE_DIR")
    if d:
        return os.path.abspath(os.path.expanduser(d))
    home = os.path.expanduser("~")
    return os.path.join(home, ".cache", "feeling-search")


def cache_path():
    return os.path.join(cache_dir(), CACHE_FILE)


def cache_ttl():
    try:
        return int(os.environ.get("FS_CACHE_TTL") or CACHE_TTL)
    except ValueError:
        return CACHE_TTL


def http_get(url, headers=None, offline=False):
    if offline:
        raise ApiError("离线模式：不允许联网（去掉 --offline 或先跑一次 dict）", "offline")
    req = urllib.request.Request(url, method="GET")
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    req.add_header("User-Agent", "feeling-search-skill/1.0")
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            raw = resp.read()
            return json.loads(raw.decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        body = {}
        try:
            body = json.loads(e.read().decode("utf-8", "replace"))
        except Exception:
            body = {}
        raise ApiError(body.get("message") or ("HTTP %s" % e.code),
                       body.get("error") or "http_error", e.code, body)
    except urllib.error.URLError as e:
        raise ApiError("连不上服务端：%s" % (e.reason,), "network_unreachable", 0)


def http_post(url, payload, headers=None, offline=False):
    if offline:
        raise ApiError("离线模式：不允许联网", "offline")
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json; charset=utf-8")
    req.add_header("User-Agent", "feeling-search-skill/1.0")
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            raw = resp.read()
            return json.loads(raw.decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        body = {}
        try:
            body = json.loads(e.read().decode("utf-8", "replace"))
        except Exception:
            body = {}
        raise ApiError(body.get("message") or ("HTTP %s" % e.code),
                       body.get("error") or "http_error", e.code, body)
    except urllib.error.URLError as e:
        raise ApiError("连不上服务端：%s" % (e.reason,), "network_unreachable", 0)


# ---------------------------------------------------------------- 词表缓存

def load_dictionary(refresh=False, offline=False):
    """读本地缓存；过期或缺失时联网拉取。返回 (数据, 来源)。"""
    path = cache_path()
    data = None
    if not refresh and os.path.isfile(path):
        age = time.time() - os.path.getmtime(path)
        if age < cache_ttl():
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
            except Exception:
                data = None
    if data and data.get("words"):
        return data, "cache"

    if offline:
        if data:
            return data, "cache-stale"
        raise ApiError("本地没有词表缓存且处于离线模式，先跑一次 `dict`", "no_cache_offline")

    data = http_get(env_base() + "/v2/dictionary", offline=offline)
    try:
        os.makedirs(cache_dir(), exist_ok=True)
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False)
        os.replace(tmp, path)
    except OSError:
        pass  # 写不进缓存不影响本次结果
    return data, "network"


# ---------------------------------------------------------------- 本地命中

def split_gloss(gloss):
    """gloss 是顿号分隔的词袋（近义词 + 易混词），拆开参与匹配。"""
    if not gloss:
        return []
    out = []
    for piece in str(gloss).replace(",", "、").split("、"):
        piece = piece.strip()
        if len(piece) >= 2:
            out.append(piece)
    return out


def score_words(text, dictionary, fuzzy=False):
    """在文本里找词：本词命中权重 1.0。

    默认**只认本词**。gloss 是「近义词 + 易混词」的词袋，里面刻意混着对立词
    （例如「温暖」的 gloss 带「冷寂」），拿它做模糊匹配会把反义拉进来，
    宁可少命中也不误命中——误命中会直接给出错误的风格。
    要更多召回时用 --fuzzy，近义词按 0.5 计分（仍低于本词）。
    """
    low = str(text).lower()
    hits = {}
    for rec in dictionary.get("words", []):
        w = rec.get("w") or ""
        if not w:
            continue
        best = 0.0
        if w.lower() in low:
            best = 1.0
        elif fuzzy:
            for near in split_gloss(rec.get("gloss")):
                if near.lower() in low:
                    best = max(best, 0.5)
        if best > 0:
            hits[w] = max(hits.get(w, 0.0), best)
    return hits


def direct_styles(text, dictionary):
    """用户直接说出风格名时不绕词表（中文名与英文名都认）。"""
    low = str(text).lower()
    out = []
    for s in dictionary.get("styles", []):
        for key in ((s.get("name") or "").strip(), (s.get("en") or "").strip()):
            if len(key) >= 2 and key.lower() in low:
                out.append(s.get("id"))
                break
    return out


def rank_styles(hits, direct, dictionary, limit):
    """与线上 /v2/analyze 同形状的打分：Σ q² / √词条数 / 向量模长，直命 +1.5。"""
    qnorm = sum(v * v for v in hits.values()) ** 0.5 or 1.0
    rows = []
    for s in dictionary.get("styles", []):
        terms = s.get("terms") or []
        hit = 0.0
        matched = []
        for t in terms:
            q = hits.get(t)
            if q is None:
                continue
            hit += q * q
            matched.append(t)
        is_direct = s.get("id") in direct
        if not hit and not is_direct:
            continue
        score = hit / (max(1, len(terms)) ** 0.5) / qnorm
        if is_direct:
            score += 1.5
        rows.append({
            "id": s.get("id"),
            "name": s.get("name"),
            "en": s.get("en"),
            "score": round(score, 4),
            "hits": len(matched),
            "matched": matched,
            "def": s.get("def"),
            "parent": s.get("parent"),
        })
    rows.sort(key=lambda r: (-r["score"], str(r["id"])))
    return rows[:limit]


def local_style_names(dictionary):
    return {s.get("id"): s.get("name") for s in dictionary.get("styles", [])}


def local_analyze(text, dictionary, words_n=8, styles_n=12, fuzzy=False):
    hits = score_words(text, dictionary, fuzzy=fuzzy)
    direct = direct_styles(text, dictionary)

    ranked = sorted(hits.items(), key=lambda kv: (-kv[1], kv[0]))
    top = ranked[:words_n]
    maxs = top[0][1] if top else 1.0
    share = {}
    index = {}
    for rec in dictionary.get("words", []):
        if rec.get("w"):
            share[rec["w"]] = rec.get("share", 0)
            index[rec["w"]] = rec.get("styles") or []
    words = [{
        "w": w,
        "score": round(s / maxs, 3),
        "share": share.get(w, 0),
        "styles": (index.get(w) or [])[:6],
    } for w, s in top]

    styles = rank_styles(hits, direct, dictionary, styles_n)
    return {
        "ok": True,
        "source": "local",
        "input": {"text": text, "chars": len(text)},
        "words": words,
        "styles": styles,
        "direct": direct,
        "meta": {
            "engine": "local-lexicon",
            "matched_words": len(hits),
            "counts": dictionary.get("counts") or {},
        },
    }


# ---------------------------------------------------------------- 子命令

def cmd_status(args):
    info = {
        "base": env_base(),
        "quota_configured": bool(env_quota()),
        "cache_dir": cache_dir(),
        "cache_file": cache_path(),
        "cache_exists": os.path.isfile(cache_path()),
        "cache_ttl_seconds": cache_ttl(),
        "offline": args.offline,
    }
    if info["cache_exists"]:
        try:
            with open(cache_path(), "r", encoding="utf-8") as fh:
                d = json.load(fh)
            info["cache_counts"] = d.get("counts") or {}
            info["cache_age_seconds"] = int(time.time() - os.path.getmtime(cache_path()))
        except Exception as exc:
            info["cache_error"] = str(exc)
    if not args.offline:
        try:
            http_get(env_base() + "/v2/dictionary", offline=False)
            info["reachable"] = True
        except ApiError as exc:
            info["reachable"] = False
            info["reach_error"] = "%s %s" % (exc.code, exc)
    return info


def cmd_dict(args):
    data, origin = load_dictionary(refresh=args.refresh, offline=args.offline)
    out = {
        "ok": True,
        "source": origin,
        "counts": data.get("counts") or {
            "words": len(data.get("words") or []),
            "styles": len(data.get("styles") or []),
        },
        "cache_file": cache_path(),
    }
    if args.with_items:
        out["words"] = [w.get("w") for w in data.get("words", [])]
        out["styles"] = [{"id": s.get("id"), "name": s.get("name")}
                         for s in data.get("styles", [])]
    return out


def cmd_analyze(args):
    text = (args.text or "").strip()
    if not text:
        raise ApiError("text 不能为空", "empty_text")
    if len(text) > MAX_CHARS:
        raise ApiError("text 最长 %d 字，当前 %d 字" % (MAX_CHARS, len(text)), "text_too_long")

    dictionary, _ = load_dictionary(refresh=args.refresh, offline=args.offline)
    result = local_analyze(text, dictionary, args.words, args.styles, fuzzy=args.fuzzy)

    if result["meta"]["matched_words"] > 0:
        return result

    # 本地一个词都没命中：先提示还有免费的模糊档没试，再谈付费
    if not args.fuzzy:
        result["hint"] = "零命中。可先免费加 --fuzzy（近义词匹配）再试，仍不行才考虑付费云端"
    if not args.allow_cloud:
        result["cloud_skipped"] = "未开启 --allow-cloud；本地零命中，未调用付费接口"
        return result
    if not env_quota():
        result["cloud_skipped"] = "未配置 FS_QUOTA 额度 token；付费接口会被 402 拦下"
        return result

    try:
        payload = {"text": text, "words": args.words, "styles": args.styles}
        cloud = http_post(env_base() + "/v2/analyze", payload,
                          headers={"X-FS-Quota": env_quota()}, offline=args.offline)
    except ApiError as exc:
        result["cloud_error"] = {"code": exc.code, "http": exc.http, "message": str(exc)}
        return result

    inner = cloud.get("result") if isinstance(cloud.get("result"), dict) else cloud
    inner["source"] = "cloud"
    return inner


def cmd_lookup(args):
    url = env_base() + "/v2/links?" + urllib.parse.urlencode({"word": args.word})
    return http_get(url, offline=args.offline)


def cmd_style_words(args):
    url = env_base() + "/v2/styles/" + urllib.parse.quote(args.style_id) + "/words"
    return http_get(url, offline=args.offline)


def cmd_style(args):
    url = env_base() + "/v2/styles/" + urllib.parse.quote(args.style_id)
    headers = {"X-FS-Quota": env_quota()} if env_quota() else {}
    return http_get(url, headers=headers, offline=args.offline)


def cmd_images(args):
    ids = [x.strip() for x in (args.ids or "").split(",") if x.strip()]
    if not ids:
        raise ApiError("缺少风格 id", "missing_ids")
    if len(ids) > 5:
        raise ApiError("一次最多 5 个风格 id", "too_many_ids")
    url = env_base() + "/v2/images?" + urllib.parse.urlencode({"ids": ",".join(ids)})
    headers = {"X-FS-Quota": env_quota()} if env_quota() else {}
    return http_get(url, headers=headers, offline=args.offline)


# ---------------------------------------------------------------- 渲染

def render(kind, data):
    if kind == "status":
        lines = ["感觉检索 · 状态"]
        lines.append("  服务端点     : %s" % data["base"])
        lines.append("  线上可达     : %s" % ("是" if data.get("reachable") else "否 %s" % data.get("reach_error", "")))
        lines.append("  额度已配置   : %s" % ("是" if data["quota_configured"] else "否（只会走免费路径）"))
        lines.append("  词表缓存     : %s" % ("有" if data["cache_exists"] else "无"))
        if data.get("cache_counts"):
            lines.append("  词表规模     : %s 词 / %s 风格" % (
                data["cache_counts"].get("words"), data["cache_counts"].get("styles")))
        return "\n".join(lines)

    if kind == "dict":
        c = data.get("counts", {})
        return "词表：%s 词 / %s 风格　来源：%s\n缓存：%s" % (
            c.get("words"), c.get("styles"), data.get("source"), data.get("cache_file"))

    if kind == "analyze":
        lines = ["来源：%s　匹配词数：%s" % (
            data.get("source"), (data.get("meta") or {}).get("matched_words"))]
        if data.get("hint"):
            lines.append("※ " + data["hint"])
        if data.get("cloud_skipped"):
            lines.append("※ " + data["cloud_skipped"])
        if data.get("cloud_error"):
            lines.append("※ 云端调用失败：" + json.dumps(data["cloud_error"], ensure_ascii=False))
        words = data.get("words") or []
        if words:
            lines.append("")
            lines.append("感受词：")
            for w in words:
                lines.append("  %-8s %5s  share=%-3s 风格=%s" % (
                    w.get("w"), w.get("score"), w.get("share"),
                    ",".join((w.get("styles") or [])[:4])))
        styles = data.get("styles") or []
        if styles:
            lines.append("")
            lines.append("视觉风格：")
            for s in styles:
                lines.append("  %-22s %-7s %s  %s" % (
                    s.get("name") or s.get("id"), s.get("score"), s.get("id"),
                    s.get("def") or ""))
        if not words and not styles:
            lines.append("（没有命中任何词或风格）")
        return "\n".join(lines)

    return json.dumps(data, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------- CLI

def build_parser():
    # 公共开关在两个位置都能用：写在子命令前或子命令后都行。
    # 子命令一侧用 SUPPRESS 作默认值，没显式给出时不覆盖顶层解析到的值。
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true", default=argparse.SUPPRESS,
                        help="输出 JSON")
    common.add_argument("--offline", action="store_true", default=argparse.SUPPRESS,
                        help="完全不联网，只用本地缓存")
    common.add_argument("--refresh", action="store_true", default=argparse.SUPPRESS,
                        help="强制刷新词表缓存")

    p = argparse.ArgumentParser(
        prog="fs_api.py",
        description="感觉检索 API 客户端（本地词典优先，云端付费兜底）")
    p.add_argument("--json", action="store_true", default=False, help="输出 JSON")
    p.add_argument("--offline", action="store_true", default=False, help="完全不联网")
    p.add_argument("--refresh", action="store_true", default=False, help="强制刷新词表缓存")
    sub = p.add_subparsers(dest="cmd")

    sub.add_parser("status", parents=[common], help="额度/缓存/连通性体检")

    sp = sub.add_parser("dict", parents=[common], help="词表缓存")
    sp.add_argument("--with-items", action="store_true", help="连词条一起输出")

    sp = sub.add_parser("analyze", parents=[common], help="一句描述 → 感受词 + 视觉风格")
    sp.add_argument("text")
    sp.add_argument("--words", type=int, default=8)
    sp.add_argument("--styles", type=int, default=12)
    sp.add_argument("--fuzzy", action="store_true",
                    help="连近义词一起匹配（免费，但可能带进易混词）")
    sp.add_argument("--allow-cloud", action="store_true",
                    help="本地零命中时调用付费的 /v2/analyze（消耗 1 次额度）")

    sp = sub.add_parser("lookup", parents=[common], help="查单个词（免费）")
    sp.add_argument("word")

    sp = sub.add_parser("style-words", parents=[common], help="某风格的词集（免费）")
    sp.add_argument("style_id")

    sp = sub.add_parser("style", parents=[common], help="风格详情含图（计费 1 次）")
    sp.add_argument("style_id")

    sp = sub.add_parser("images", parents=[common], help="批量取图，最多 5 个（计费 1 次）")
    sp.add_argument("ids")

    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.cmd:
        parser.print_help()
        return 2

    handlers = {
        "status": cmd_status,
        "dict": cmd_dict,
        "analyze": cmd_analyze,
        "lookup": cmd_lookup,
        "style-words": cmd_style_words,
        "style": cmd_style,
        "images": cmd_images,
    }

    try:
        data = handlers[args.cmd](args)
    except ApiError as exc:
        payload = {"ok": False, "error": exc.code, "message": str(exc),
                   "http": exc.http, "payload": exc.payload}
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print("失败：[%s] %s" % (exc.code, exc))
            if exc.code == "payment_required":
                print("      ↳ 付费端点需要额度。设置 FS_QUOTA 或改走免费端点"
                      "（dict / lookup / style-words）")
        return 1

    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(render(args.cmd, data))
    return 0


if __name__ == "__main__":
    sys.exit(main())
