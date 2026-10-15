#!/usr/bin/env python3
"""国立国会図書館サーチ(NDL Search) APIで書誌を検索するヘルパー。

使い方:
  python3 ndl-books/lookup.py --isbn 9784101010014    # ISBNで照会
  python3 ndl-books/lookup.py --title 雪国 --cnt 5    # タイトル検索(部分一致)
  python3 ndl-books/lookup.py --creator 夏目漱石      # 著者名で検索
  python3 ndl-books/lookup.py --keyword 東京 防災     # 任意キーワード(AND)

外部パッケージ不要。APIキー・ログイン・ユーザー登録不要。
実測日: 2026-09-29 (OpenSearch / SRU ともに同日実測)
"""
import argparse, json, sys, urllib.request, urllib.parse
import xml.etree.ElementTree as ET

BASE = "https://ndlsearch.ndl.go.jp/api/opensearch"
LEGACY = "https://iss.ndl.go.jp/api/opensearch"  # 旧ホスト(303で新ホストへ)

def fetch(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": "kurashi-skill/ndl-books"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def localname(tag):
    return tag.rsplit("}", 1)[-1]

def first(elem, name):
    for child in elem:
        if localname(child.tag) == name:
            return (child.text or "").strip()
    return ""

def identifiers(elem):
    """dc:identifier を xsi:type 別に集める -> {ISBN, NII-BibID, ...}"""
    out = {}
    for child in elem:
        if localname(child.tag) != "identifier":
            continue
        type_ = ""
        for k, v in child.attrib.items():
            if localname(k) == "type":
                type_ = v.rsplit(":", 1)[-1]
        out[type_ or "unknown"] = (child.text or "").strip()
    return out

def parse_items(xml_bytes):
    root = ET.fromstring(xml_bytes)
    total, per_page, start = None, None, None
    items = []
    channel = None
    for child in root:
        if localname(child.tag) == "channel":
            channel = child
            break
    if channel is None:
        return 0, []
    for child in channel:
        ln = localname(child.tag)
        if ln == "totalResults":
            total = int(child.text)
        elif ln == "itemsPerPage":
            per_page = int(child.text)
        elif ln == "startIndex":
            start = int(child.text)
        elif ln == "item":
            ids = identifiers(child)
            cats = [ (c.text or "").strip() for c in child if localname(c.tag) == "category" ]
            items.append({
                "title": first(child, "title"),
                "title_yomi": first(child, "titleTranscription"),
                "creator": first(child, "creator"),
                "creator_yomi": first(child, "creatorTranscription"),
                "publisher": first(child, "publisher"),
                "date": first(child, "date"),
                "isbn": ids.get("ISBN13") or ids.get("ISBN", ""),
                "bib_id": ids.get("NIIBibID", ""),
                "material": cats,  # 例: ["図書","紙"], ["図書","電子"]
                "link": first(child, "link"),
            })
    return (total or 0), items

def build_url(args):
    params = {}
    if args.isbn:
        params["isbn"] = args.isbn.replace("-", "")
    if args.title:
        params["title"] = args.title
    if args.creator:
        params["creator"] = args.creator
    if args.keyword:
        params["any"] = " ".join(args.keyword)
    if args.mediatype:
        params["mediatype"] = args.mediatype
    if args.cnt is not None:
        params["cnt"] = str(args.cnt)
    if args.idx is not None:
        params["idx"] = str(args.idx)
    return BASE + "?" + urllib.parse.urlencode(params)

def main():
    ap = argparse.ArgumentParser(description="NDL Search 書誌検索")
    ap.add_argument("--isbn", help="ISBN(ハイフン可)")
    ap.add_argument("--title", help="タイトル(部分一致)")
    ap.add_argument("--creator", help="著者名")
    ap.add_argument("--keyword", nargs="+", help="任意キーワード(スペース区切りでAND)")
    ap.add_argument("--mediatype", help="books / periodicals / thesis / digital など")
    ap.add_argument("--cnt", type=int, default=10, help="件数(既定10, 最大200。省略時はAPI既定=200)")
    ap.add_argument("--idx", type=int, default=None, help="開始位置(1始まり)")
    args = ap.parse_args()
    if not (args.isbn or args.title or args.creator or args.keyword):
        ap.error("--isbn / --title / --creator / --keyword のいずれかが必要")
    url = build_url(args)
    total, items = parse_items(fetch(url))
    out = {"query_url": url, "total": total, "count": len(items), "items": items}
    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
    print()

if __name__ == "__main__":
    main()
