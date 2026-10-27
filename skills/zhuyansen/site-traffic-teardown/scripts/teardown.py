#!/usr/bin/env python3
"""Competitor traffic + SEO teardown on the AIsa CLI.

Stages:
  discover  Semrush organic competitors + overview + 3-month visits for the target
  screen    one month of Similarweb visits per candidate (cheap filter)
  full      channels, Semrush overview, backlinks, Ahrefs DR, 3-month trend per domain
  keywords  Semrush top organic keywords (with landing URL) per domain

Without --run the script only quotes (free). With --run it calls, saves raw JSON
and writes a markdown summary. It never prints or stores the API key.
"""
import argparse, collections, datetime as dt, json, os, re, shutil, subprocess, sys

SW_TREND = "get_similarweb_traffic_engagement"
SW_CH = "get_similarweb_marketing_channel_sources_legacy"

TEXT = {
    "en": {
        "head": "| Domain | Visits (last month) | Trend | Search/Direct/Social/Referral | DR | Ref. domains | Links per domain | Semrush keywords | Semrush traffic |",
        "comp": "**Semrush organic competitors (noisy: drop sites that only share a few words)**",
        "comp_row": "- {d} · relevance {r} · common keywords {c} · total keywords {t}",
        "kw_head": "### {d} ({n} keywords) · landing page types {p}",
        "kw_cols": "| Keyword | Position | US monthly volume | CPC | Landing page |",
        "cost": "Charged ${c:.3f} (quoted ${q:.3f})",
        "failed": "; failed {f}",
    },
    "zh": {
        "head": "| 域名 | 月访问（最近月） | 趋势 | 搜索/直接/社媒/引荐 | DR | 引荐域名 | 外链/域名 | Semrush 词数 | Semrush 流量 |",
        "comp": "**Semrush 自然搜索竞品（含噪音，需人工筛掉只撞词的站）**",
        "comp_row": "- {d} · 相关度 {r} · 共同词 {c} · 总词 {t}",
        "kw_head": "### {d}（{n} 词）· 落地页类型 {p}",
        "kw_cols": "| 词 | 排名 | 美国月搜索量 | CPC | 落地页 |",
        "cost": "实扣 ${c:.3f}（预估 ${q:.3f}）",
        "failed": "；失败 {f}",
    },
}


def months_back(end, n):
    y, m = map(int, end.split("-"))
    m -= n - 1
    while m <= 0:
        m += 12
        y -= 1
    return f"{y:04d}-{m:02d}"


def last_full_month():
    d = dt.date.today().replace(day=1) - dt.timedelta(days=1)
    return d.strftime("%Y-%m")


def build(stage, target, domains, month, db):
    start = months_back(month, 3)
    sw = lambda d, s, e: {"domain": d, "start_date": s, "end_date": e,
                          "metrics": "visits", "main_domain_only": False}
    calls = []
    add = lambda d, kind, tool, args: calls.append(
        {"call_id": f"{d}|{kind}", "tool": tool, "arguments": args})
    if stage == "discover":
        add(target, "competitors", "get_semrush_organic_competitors", {"domain": target, "database": db})
        add(target, "overview", "get_semrush_domain_overview", {"domain": target, "database": db})
        add(target, "trend", SW_TREND, sw(target, start, month))
    elif stage == "screen":
        for d in domains:
            add(d, "trend", SW_TREND, sw(d, month, month))
    elif stage == "full":
        for d in [target] + domains:
            add(d, "trend", SW_TREND, sw(d, start, month))
            add(d, "channels", SW_CH, {"domain": d, "start_date": month, "end_date": month,
                                       "main_domain_only": False})
            add(d, "overview", "get_semrush_domain_overview", {"domain": d, "database": db})
            add(d, "backlinks", "get_semrush_backlinks_overview", {"target": d})
            add(d, "dr", "get_ahrefs_domain_rating", {"target": d, "date": f"{month}-01"})
    elif stage == "keywords":
        for d in [target] + domains:
            add(d, "keywords", "get_semrush_domain_organic_keywords", {"domain": d, "database": db})
    return {"calls": calls}


def aisa(cmd, path):
    out = subprocess.run(["aisa", cmd, "-f", path, "--json"], capture_output=True, text=True)
    try:
        return json.loads(out.stdout)
    except json.JSONDecodeError:
        sys.exit(f"aisa {cmd} failed (try `aisa whoami`): {(out.stderr or out.stdout).strip()[:300]}")


def csv_rows(data):
    s = data if isinstance(data, str) else json.dumps(data)
    lines = [l for l in s.replace("\r", "").split("\n") if l.strip()]
    if not lines:
        return []
    head = lines[0].split(";")
    return [dict(zip(head, l.split(";"))) for l in lines[1:]]


def visits(v, lang):
    if v is None:
        return "—"
    return f"{v / 1e4:.1f}万" if lang == "zh" else f"{v / 1e3:.1f}k"


def summarize(results, stage, lang="en"):
    T = TEXT[lang]
    by = collections.defaultdict(dict)
    for r in results:
        d, kind = r["call_id"].split("|", 1)
        by[d][kind] = r.get("data") if r.get("successful") else None
    out = []
    if stage in ("discover", "screen", "full"):
        out += [T["head"], "|---|---|---|---|---|---|---|---|---|"]
        for d, k in by.items():
            tr = [x.get("visits") for x in (k.get("trend") or {}).get("data", [])]
            last = tr[-1] if tr else None
            trend = "→".join(visits(v, lang) for v in tr) if tr else "—"
            mix = "—"
            if k.get("channels"):
                ch = {x["source_type"]: x.get("visits") or 0 for x in k["channels"]["data"]}
                tot = sum(ch.values()) or 1
                p = lambda n: f"{ch.get(n, 0) / tot * 100:.0f}%"
                mix = f"{p('Organic Search')}/{p('Direct')}/{p('Organic Social')}/{p('Referrals')}"
            dr = (k.get("dr") or {}).get("domain_rating", {}).get("domain_rating", "—")
            dr = int(dr) if isinstance(dr, float) else dr
            bl = csv_rows(k.get("backlinks") or "")
            rd = bl[0].get("domains_num", "—") if bl else "—"
            ratio = f"{int(bl[0]['total']) / max(int(bl[0]['domains_num']), 1):.0f}" if bl else "—"
            ov = csv_rows(k.get("overview") or "")
            kw = ov[0].get("Organic Keywords", "—") if ov else "—"
            ot = ov[0].get("Organic Traffic", "—") if ov else "—"
            out.append(f"| {d} | {round(last) if last is not None else '—'} | {trend} | {mix} | {dr} | {rd} | {ratio} | {kw} | {ot} |")
        comp = next((k.get("competitors") for k in by.values() if k.get("competitors")), None)
        if comp:
            out.append("\n" + T["comp"] + "\n")
            for row in csv_rows(comp)[:20]:
                out.append(T["comp_row"].format(d=row.get("Domain"), r=row.get("Competitor Relevance"),
                                                c=row.get("Common Keywords"), t=row.get("Organic Keywords")))
    if stage == "keywords":
        for d, k in by.items():
            rows = csv_rows(k.get("keywords") or "")
            pat = collections.Counter("/" + (re.sub(r"https?://[^/]+", "", r.get("Url", "")).split("/") + ["", ""])[1] for r in rows)
            out.append("\n" + T["kw_head"].format(d=d, n=len(rows), p=dict(pat.most_common(6))) + "\n")
            out.append(T["kw_cols"] + "\n|---|---|---|---|---|")
            for r in rows:
                out.append(f"| {r.get('Keyword')} | {r.get('Position')} | {r.get('Search Volume')} | {r.get('CPC')} | {r.get('Url')} |")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["discover", "screen", "full", "keywords"])
    ap.add_argument("--target", required=True, help="your domain")
    ap.add_argument("--competitors", default="", help="comma-separated domains")
    ap.add_argument("--month", default=last_full_month(), help="YYYY-MM, latest full month")
    ap.add_argument("--db", default="us", help="Semrush database")
    ap.add_argument("--out", default="teardown-out")
    ap.add_argument("--lang", choices=["en", "zh"], default="en", help="language of the summary")
    ap.add_argument("--run", action="store_true", help="actually call (billed); default quote only")
    ap.add_argument("--max-total", type=float, default=5.0, help="refuse to run above this quoted USD")
    ap.add_argument("--max-call", type=float, default=2.0, help="refuse to run if one call is quoted above this USD")
    a = ap.parse_args()
    if not shutil.which("aisa"):
        sys.exit("aisa CLI not found: npm i -g @aisa-one/cli && aisa login")
    domains = [d.strip() for d in a.competitors.split(",") if d.strip()]
    os.makedirs(a.out, exist_ok=True)
    tag = f"{a.stage}-{dt.datetime.now():%Y%m%d-%H%M%S}"
    req = os.path.join(a.out, f"{tag}.calls.json")
    plan = build(a.stage, a.target, domains, a.month, a.db)
    json.dump(plan, open(req, "w"), indent=1)

    q = aisa("quote", req)
    costs = {r["call_id"]: r["data"]["estimated_cost_micros_usd"] / 1e6
             for r in q.get("results", []) if (r.get("data") or {}).get("estimated_cost_micros_usd") is not None}
    for cid, c in costs.items():
        print(f"  quote {cid:<45} ${c:.3f}")
    unquoted = [c["call_id"] for c in plan["calls"] if c["call_id"] not in costs]
    if unquoted:
        print(f"  not quoted (dropped): {unquoted}")
    total = sum(costs.values())
    top = max(costs.values() or [0])
    print(f"QUOTED TOTAL ${total:.3f}  (max single ${top:.3f})")
    if not a.run:
        return
    if total > a.max_total:
        sys.exit(f"quoted ${total:.2f} > --max-total ${a.max_total:.2f}; not running")
    if top > a.max_call:
        sys.exit(f"a call is quoted ${top:.2f} > --max-call ${a.max_call:.2f}; not running")
    if unquoted:
        plan["calls"] = [c for c in plan["calls"] if c["call_id"] in costs]
        json.dump(plan, open(req, "w"), indent=1)

    r = aisa("call", req)
    raw = os.path.join(a.out, f"{tag}.results.json")
    json.dump(r, open(raw, "w"), ensure_ascii=False, indent=1)
    T = TEXT[a.lang]
    charged = sum((x.get("customer_cost_micros_usd") or 0) for x in r.get("results", [])) / 1e6
    failed = [x["call_id"] for x in r.get("results", []) if not x.get("successful")]
    md = summarize(r.get("results", []), a.stage, a.lang)
    md += "\n\n" + T["cost"].format(c=charged, q=total) + (T["failed"].format(f=failed) if failed else "")
    open(os.path.join(a.out, f"{tag}.md"), "w").write(md)
    print(md)


if __name__ == "__main__":
    main()
