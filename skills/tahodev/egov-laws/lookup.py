#!/usr/bin/env python3
"""e-Gov 法令API v2 で法令・条文・改正履歴・全文検索を引くヘルパー。

使い方:
  python3 egov-laws/lookup.py search 民法                      # 法令名で検索(部分一致)
  python3 egov-laws/lookup.py article 民法 709                  # 第709条の本文
  python3 egov-laws/lookup.py article 民法 3の2                 # 枝番(第3条の2)
  python3 egov-laws/lookup.py article 民法 4 --asof 2017-04-01  # 時点指定(2017-04-01以降)
  python3 egov-laws/lookup.py revisions 民法                   # 改正履歴(施行済み+未施行)
  python3 egov-laws/lookup.py keyword 暴力 --max 3              # 条文本文の全文検索

外部パッケージ不要。APIキー・ログイン不要。
実測日: 2026-10-02 (https://laws.e-gov.go.jp/api/2/)
"""
import argparse, json, re, sys, urllib.request, urllib.parse, urllib.error

BASE = "https://laws.e-gov.go.jp/api/2"
UA = {"User-Agent": "kurashi-skill/egov-laws"}

def fetch_json(path, timeout=60):
    req = urllib.request.Request(f"{BASE}/{path}", headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
    except urllib.error.HTTPError as e:
        raw = e.read()  # 400でもJSONエラー {"code":"400021","message":"..."} が読める
    try:
        d = json.loads(raw)
    except ValueError:
        # メンテナンス中はHTML(403)が返る。JSONではないのでそう伝える
        raise SystemExit(json.dumps({"error": "JSONではない応答(メンテナンス中の可能性)", "head": raw[:120].decode("utf-8", "replace")}, ensure_ascii=False))
    if isinstance(d, dict) and "code" in d and "message" in d and "law_info" not in d:
        raise SystemExit(json.dumps({"error": d["message"], "code": d["code"]}, ensure_ascii=False))
    return d

def q(**kw):
    return urllib.parse.urlencode({k: v for k, v in kw.items() if v is not None})

def parse_article_num(s):
    """'709' -> '709' / '3の2' '3-2' '3_2' -> '3_2' (枝番は _ 区切りがXMLのNum属性)"""
    s = s.strip().translate(str.maketrans("０１２３４５６７８９", "0123456789"))
    s = re.sub(r"[の\-－ー]", "_", s)
    if not re.fullmatch(r"\d+(_\d+)*", s):
        raise SystemExit(json.dumps({"error": f"条番号を解釈できません: {s!r} (例: 709 / 3の2)"}, ensure_ascii=False))
    return s

def resolve_law(name):
    """法令名 -> law_id。完全一致(正式名称/略称)を優先。曖昧なら候補を示して止まる。"""
    if re.fullmatch(r"[0-9A-Z]{10,}", name):  # law_idそのもの
        return name
    d = fetch_json("laws?" + q(law_title=name, limit=50))
    laws = d.get("laws", [])
    exact = [l for l in laws
             if l["revision_info"].get("law_title") == name or l["revision_info"].get("abbrev") == name]
    if len(exact) == 1:
        return exact[0]["law_info"]["law_id"]
    cands = exact or laws
    if len(cands) == 1:
        return cands[0]["law_info"]["law_id"]
    raise SystemExit(json.dumps({
        "error": "法令名が一意に決まりません" if cands else "該当する法令がありません",
        "candidates": [{"law_id": l["law_info"]["law_id"], "title": l["revision_info"]["law_title"]} for l in cands[:10]],
    }, ensure_ascii=False))

def node_text(n):
    if isinstance(n, str):
        return n
    return "".join(node_text(c) for c in n.get("children", []))

BLOCK = {"Paragraph", "Item", "Subitem1", "Subitem2", "Subitem3"}

def render_article(art):
    """Article要素 -> 読める本文。項・号ごとに改行。"""
    lines = []
    def walk(n, depth):
        if isinstance(n, str):
            return
        tag = n["tag"]
        if tag == "ArticleCaption":
            lines.append(node_text(n))
        elif tag == "ArticleTitle":
            lines.append(node_text(n))
        elif tag in BLOCK:
            head = " ".join(t for t in (node_text(c) for c in n["children"] if not isinstance(c, str) and c["tag"] not in BLOCK) if t)
            lines.append("  " * max(depth - 1, 0) + head)
            for c in n["children"]:
                if not isinstance(c, str) and c["tag"] in BLOCK:
                    walk(c, depth + 1)
        else:
            for c in n.get("children", []):
                walk(c, depth)
    for c in art["children"]:
        walk(c, 1 if c["tag"] in BLOCK else 0)
    return "\n".join(l for l in lines if l.strip())

def main_provision(law_full_text):
    body = next(c for c in law_full_text["children"] if isinstance(c, dict) and c["tag"] == "LawBody")
    return next(c for c in body["children"] if isinstance(c, dict) and c["tag"] == "MainProvision")

def find_articles(n, acc):
    if isinstance(n, dict):
        if n["tag"] == "Article":
            acc.append(n)
        for c in n.get("children", []):
            find_articles(c, acc)
    return acc

def find_article(law_full_text, num):
    """条番号(Num属性)で本則のArticleを探す。elm=Article[N] はN番目の要素であって第N条ではない。"""
    arts = find_articles(main_provision(law_full_text), [])
    for i, a in enumerate(arts, 1):
        if a["attr"].get("Num") == num:
            return a, i, len(arts)
    return None, None, len(arts)

def cmd_search(args):
    d = fetch_json("laws?" + q(law_title=args.name, limit=args.max))
    out = {"total": d["total_count"], "laws": [{
        "law_id": l["law_info"]["law_id"], "title": l["revision_info"]["law_title"],
        "abbrev": l["revision_info"].get("abbrev"), "law_num": l["law_info"]["law_num"],
        "type": l["law_info"]["law_type"],
        "enforced": l["revision_info"]["amendment_enforcement_date"],
        "status": l["revision_info"]["current_revision_status"]} for l in d["laws"]]}
    return out

def cmd_article(args):
    law_id = resolve_law(args.law)
    num = parse_article_num(args.article)
    d = fetch_json(f"law_data/{law_id}" + ("?" + q(asof=args.asof) if args.asof else ""))
    art, idx, total = find_article(d["law_full_text"], num)
    ri = d["revision_info"]
    if art is None:
        raise SystemExit(json.dumps({"error": f"本則に第{args.article}条がありません", "law": ri["law_title"],
                                     "articles_in_main": total}, ensure_ascii=False))
    return {"law": ri["law_title"], "law_id": law_id, "revision": ri["law_revision_id"],
            "enforced": ri["amendment_enforcement_date"], "asof": args.asof,
            "article_num": num, "element_index": idx, "text": render_article(art)}

def cmd_revisions(args):
    law_id = resolve_law(args.law)
    d = fetch_json(f"law_revisions/{law_id}")
    revs = sorted(d["revisions"], key=lambda r: r["amendment_enforcement_date"] or "9999")
    return {"law_id": law_id, "count": len(revs), "revisions": [{
        "enforced": r["amendment_enforcement_date"], "status": r["current_revision_status"],
        "amended_by": r.get("amendment_law_title"), "revision_id": r["law_revision_id"]} for r in revs[-args.max:]]}

def cmd_keyword(args):
    d = fetch_json("keyword?" + q(keyword=args.q, limit=args.max))
    return {"laws_hit": d["total_count"], "sentences_returned": d["sentence_count"], "items": [{
        "law_id": it["law_info"]["law_id"], "title": it["revision_info"]["law_title"],
        "sentences": [s["text"][:200] for s in it["sentences"][:2]]} for it in d["items"]]}

def main():
    ap = argparse.ArgumentParser(description="e-Gov 法令API v2")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search"); s.add_argument("name"); s.add_argument("--max", type=int, default=10); s.set_defaults(f=cmd_search)
    a = sub.add_parser("article"); a.add_argument("law"); a.add_argument("article")
    a.add_argument("--asof", help="時点指定 YYYY-MM-DD (2017-04-01以降)"); a.set_defaults(f=cmd_article)
    r = sub.add_parser("revisions"); r.add_argument("law"); r.add_argument("--max", type=int, default=10); r.set_defaults(f=cmd_revisions)
    k = sub.add_parser("keyword"); k.add_argument("q"); k.add_argument("--max", type=int, default=3); k.set_defaults(f=cmd_keyword)
    args = ap.parse_args()
    json.dump(args.f(args), sys.stdout, ensure_ascii=False, indent=2)
    print()

if __name__ == "__main__":
    main()
