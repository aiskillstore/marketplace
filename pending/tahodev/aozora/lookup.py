#!/usr/bin/env python3
"""青空文庫の公開カタログ(list_person_all_extended_utf8.csv)と図書カードを読むヘルパー。

使い方:
  python3 aozora/lookup.py --title 吾輩は猫である      # タイトル部分一致検索
  python3 aozora/lookup.py --author 夏目漱石           # 著者名(スペースなし姓名)の作品一覧
  python3 aozora/lookup.py --work-id 000789            # 図書カードの本文リンクを取得
  python3 aozora/lookup.py --text 000789 --max-chars 300  # 本文をプレーンテキストで抽出
  python3 aozora/lookup.py --stats                     # カタログ全体の件数サマリ
  python3 aozora/lookup.py --csv /path/to/list.csv ... # ローカルCSVを使う(テスト用)

外部パッケージ不要。APIキー・ログイン・ユーザー登録不要。
実測日: 2026-09-30 (extended CSV 19,502行 / 17,840作品 / zip 2,092,746B)
"""
import argparse, csv, io, json, os, re, sys, time, urllib.request, zipfile

CSV_URL = "https://www.aozora.gr.jp/index_pages/list_person_all_extended_utf8.zip"
CACHE_DIR = os.path.join(os.path.expanduser("~"), ".cache", "aozora")
CACHE_TTL = 86400  # 24時間。一覧は不定期更新のスナップショット(実測: 最終更新2026-08-21)
UA = {"User-Agent": "kurashi-skill/aozora"}

def fetch(url, timeout=60):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def load_rows(csv_path=None):
    """extended CSVを読み、行リスト(dict)を返す。UTF-8 BOM付き。"""
    if csv_path is None:
        os.makedirs(CACHE_DIR, exist_ok=True)
        csv_path = os.path.join(CACHE_DIR, "list_person_all_extended_utf8.csv")
        if not (os.path.exists(csv_path) and time.time() - os.path.getmtime(csv_path) < CACHE_TTL):
            zf = zipfile.ZipFile(io.BytesIO(fetch(CSV_URL)))
            name = zf.namelist()[0]
            open(csv_path, "wb").write(zf.read(name))
    with open(csv_path, encoding="utf-8-sig") as f:  # BOM対策: utf-8-sig 必須
        return list(csv.DictReader(f))

def card_url_to_base(card_url):
    """図書カードURLから /cards/XXXXXX/ までのベースを返す。"""
    m = re.match(r"(https://www\.aozora\.gr\.jp/cards/\d+/)", card_url)
    return m.group(1) if m else None

def parse_card_links(card_html):
    """図書カードHTMLから本文・ルビzip・ebkのファイル名を抜く。

    罠: 本文のURL(作品ID_通し番号.html)は作品IDから推測できない。
    必ずカードページを取りに行ってリンクを拾う。
    """
    hrefs = re.findall(r'href="(?:\./)?(files/[^"]+)"', card_html)
    text, ruby, ebk = None, None, None
    for h in hrefs:
        if re.search(r"files/\d+_\d+\.html$", h) and text is None:
            text = h
        elif h.endswith(".zip") and "_ruby_" in h and ruby is None:
            ruby = h
        elif h.endswith(".ebk") and ebk is None:
            ebk = h
    return {"text_html": text, "ruby_zip": ruby, "ebk": ebk}

def detect_encoding(raw, default="shift_jis"):
    """meta/宣言のcharsetを見る。青空文庫はカード=UTF-8、本文=Shift_JISが混在。"""
    head = raw[:2000].decode("ascii", errors="ignore")
    m = re.search(r'charset=["\']?([A-Za-z0-9_-]+)', head, re.I)
    if m:
        cs = m.group(1).lower()
        if cs in ("utf-8", "utf8"):
            return "utf-8"
        if cs in ("shift_jis", "shift-jis", "sjis", "x-sjis"):
            return "shift_jis"
    return default

def extract_text(raw):
    """本文XHTMLからプレーンテキストを抽出。ルビは基底文字のみ残す。"""
    enc = detect_encoding(raw, default="shift_jis")
    html = raw.decode(enc, errors="replace").replace("\r\n", "\n").replace("\r", "\n")
    m = re.search(r'<div class="main_text">(.*?)<div class="bibliographical_information"', html, re.S)
    body = m.group(1) if m else html
    body = re.sub(r"<rp>.*?</rp>", "", body, flags=re.S)   # <rp>（</rp> ごと落とす
    body = re.sub(r"<rt>.*?</rt>", "", body, flags=re.S)   # ルビの読みは落とす
    body = re.sub(r"</?r[btuyp]+>", "", body)              # 残った <rb> 等のタグだけ落とす
    body = re.sub(r"<br\s*/?>", "\n", body)
    body = re.sub(r"<[^>]+>", "", body)
    body = body.replace("&nbsp;", " ").replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
    return re.sub(r"\n{3,}", "\n\n", body).strip()

def work_rows(rows, work_id):
    return [r for r in rows if r.get("作品ID") == work_id]

def cmd_stats(rows):
    works = {r["作品ID"] for r in rows}
    persons = {r["人物ID"] for r in rows}
    return {"rows": len(rows), "distinct_works": len(works), "distinct_persons": len(persons),
            "copyrighted_works": len({r["作品ID"] for r in rows if r.get("作品著作権フラグ") == "あり"})}

def main():
    ap = argparse.ArgumentParser(description="青空文庫 作品検索・本文抽出")
    ap.add_argument("--title", help="作品名(部分一致)")
    ap.add_argument("--author", help="著者名(「夏目漱石」のように姓名連結)")
    ap.add_argument("--work-id", help="作品ID(6桁)で図書カードのリンク取得")
    ap.add_argument("--text", help="作品ID(6桁)の本文をプレーンテキスト抽出")
    ap.add_argument("--max-chars", type=int, default=None, help="--text の出力上限")
    ap.add_argument("--stats", action="store_true", help="カタログの件数サマリ")
    ap.add_argument("--csv", help="ローカルのextended CSVを使う(既定はダウンロード+24hキャッシュ)")
    ap.add_argument("--limit", type=int, default=20)
    args = ap.parse_args()

    if args.text or args.work_id:
        wid = args.text or args.work_id
        rows = load_rows(args.csv)
        wr = work_rows(rows, wid)
        if not wr:
            print(json.dumps({"error": f"作品ID {wid} がカタログにない"}, ensure_ascii=False))
            sys.exit(1)
        base = card_url_to_base(wr[0]["図書カードURL"])
        links = parse_card_links(fetch(wr[0]["図書カードURL"]).decode("utf-8", errors="replace"))
        out = {"work_id": wid, "title": wr[0]["作品名"],
               "authors": [r["姓"] + " " + r["名"] + "(" + r["役割フラグ"] + ")" for r in wr],
               "card_url": wr[0]["図書カードURL"],
               "text_url": base + links["text_html"] if base and links["text_html"] else None,
               "ruby_zip_url": base + links["ruby_zip"] if base and links["ruby_zip"] else None,
               "ebk_url": base + links["ebk"] if base and links["ebk"] else None}
        if args.text:
            raw = fetch(out["text_url"])
            text = extract_text(raw)
            out["text_length"] = len(text)
            out["text"] = text[: args.max_chars] if args.max_chars else text
        json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
        print()
        return

    rows = load_rows(args.csv)
    if args.stats:
        json.dump(cmd_stats(rows), sys.stdout, ensure_ascii=False, indent=2)
        print()
        return
    hits = rows
    if args.title:
        hits = [r for r in hits if args.title in r.get("作品名", "")]
    if args.author:
        hits = [r for r in hits if (r.get("姓", "") + r.get("名", "")) == args.author and r.get("役割フラグ") == "著者"]
    if not (args.title or args.author):
        ap.error("--title / --author / --work-id / --text / --stats のいずれかが必要")
    seen, items = set(), []
    for r in hits:
        if r["作品ID"] in seen:
            continue  # 1作品=複数行(著者+翻訳者など)なので作品単位に畳む
        seen.add(r["作品ID"])
        items.append({"work_id": r["作品ID"], "title": r["作品名"], "title_yomi": r["作品名読み"],
                      "author": r["姓"] + " " + r["名"], "kana_type": r["文字遣い種別"],
                      "copyright": r["作品著作権フラグ"], "first_pub": r["初出"],
                      "card_url": r["図書カードURL"]})
        if len(items) >= args.limit:
            break
    json.dump({"total": len({r["作品ID"] for r in hits}), "count": len(items), "items": items},
              sys.stdout, ensure_ascii=False, indent=2)
    print()

if __name__ == "__main__":
    main()
