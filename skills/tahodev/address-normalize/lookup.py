#!/usr/bin/env python3
"""デジタル庁 アドレス・ベース・レジストリ(ABR)のマスタで住所文字列を正規化するヘルパー。

使い方:
  python3 address-normalize/lookup.py "東京都千代田区内幸町1丁目1-1"
  python3 address-normalize/lookup.py "新宿区歌舞伎町一丁目4-1" --pref 13
  python3 address-normalize/lookup.py --towns --pref 13 --keyword 歌舞伎

外部パッケージ不要。マスタCSVは ~/.cache/kurashi-skill/address-normalize/ に保存。
実測日: 2026-09-26 (DCAT-USフィード v1.1 / mt_pref・mt_city・mt_town)
"""
import argparse, csv, json, os, re, sys, unicodedata, urllib.request

S3 = "https://gov-csv-export-public.s3.ap-northeast-1.amazonaws.com"
CACHE = os.path.expanduser("~/.cache/kurashi-skill/address-normalize")
KANJI = "〇一二三四五六七八九十"

def fetch(url, timeout=120):
    req = urllib.request.Request(url, headers={"User-Agent": "kurashi-skill/address-normalize"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def load_csv(name, url, refresh=False):
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, name)
    if refresh or not os.path.exists(path):
        import zipfile, io
        z = zipfile.ZipFile(io.BytesIO(fetch(url)))
        inner = z.namelist()[0]
        open(path, "wb").write(z.read(inner))
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))

def norm_text(t):
    """比較用に正規化: NFKC + 空白除去"""
    return unicodedata.normalize("NFKC", t).replace(" ", "").replace("　", "")

def kanji_num(n):
    n = int(n)
    if n >= 100:
        return str(n)
    tens, ones = divmod(n, 10)
    s = ""
    if tens:
        s += ("" if tens == 1 else KANJI[tens]) + "十"
    if ones:
        s += KANJI[ones]
    return s

def chome_variants(number):
    """丁目の表記ゆれ: データ上は漢数字(一丁目)と全角数字(１丁目)が混在"""
    n = int(number)
    return {f"{kanji_num(n)}丁目", f"{n}丁目"}

K2D = str.maketrans("〇一二三四五六七八九", "0123456789")

def canon(s):
    """1文字対1文字の緩い比較形: NFKC + 漢数字1文字を算用数字に(条・丁目の表記ゆれ用)"""
    return norm_text(s).translate(K2D)

def parse_address(text, prefs, cities, towns_by_pref):
    """住所文字列 -> (pref, city行, town行, rest) の最長一致分解"""
    t = norm_text(text)
    # 1. 都道府県 (最長一致)
    pref = max((p for p in prefs if t.startswith(p["pref"])), key=lambda p: len(p["pref"]), default=None)
    rest = t[len(pref["pref"]):] if pref else t
    # 2. 市区町村(+郡・政令市の区)。候補は pref の lg_code 先頭2桁で絞る
    code2 = pref["lg_code"][:2] if pref else None
    cand = [c for c in cities if not code2 or c["lg_code"].startswith(code2)]
    def city_name(c):
        return (c["county"] or "") + (c["city"] or "") + (c["ward"] or "")
    city = max((c for c in cand if rest.startswith(city_name(c))), key=lambda c: len(city_name(c)), default=None)
    if not city:
        # 郡名なし・市区名のみでも試す(入力が郡を省略する場合)
        city = max((c for c in cand if rest.startswith((c["city"] or "") + (c["ward"] or ""))),
                   key=lambda c: len((c["city"] or "") + (c["ward"] or "")), default=None)
    if city:
        for form in sorted({city_name(city), (city["city"] or "") + (city["ward"] or "")}, key=len, reverse=True):
            if rest.startswith(form):
                rest = rest[len(form):]
                break
        # 都道府県の記載がなくても市区から補う
        if not pref:
            pref = next((x for x in prefs if x["lg_code"][:2] == city["lg_code"][:2]), None)
    # 3. 町字(+丁目)。市区が特定できたらその lg_code の行だけ
    town, town_rest = None, rest
    if pref and city:
        rows = [r for r in towns_by_pref(pref) if r["lg_code"] == city["lg_code"]]
        crest = canon(rest)  # canon は1:1置換なので長さが保存される
        best = None
        for r in rows:
            oaza = r["oaza_cho"] or ""
            if not oaza or not crest.startswith(canon(oaza)):
                continue
            after = rest[len(oaza):]
            cafter = crest[len(oaza):]
            chome_hit = ""
            if r["chome_number"]:
                for v in chome_variants(r["chome_number"]):
                    if canon(after).startswith(canon(v)):
                        chome_hit = v
                        break
                if not chome_hit:
                    # 丁目つき町字なのに丁目が続かない場合は不一致扱い(同名の別丁目への誤爆防止)
                    continue
            score = len(oaza) + len(chome_hit)
            if not best or score > best[0]:
                best = (score, r, chome_hit, after[len(norm_text(chome_hit)):])
        if best:
            _, town, chome_hit, town_rest = best
            town = dict(town)
            town["_chome_matched"] = chome_hit
    return pref, city, town, town_rest

def main():
    p = argparse.ArgumentParser()
    p.add_argument("address", nargs="?", help="正規化する住所文字列")
    p.add_argument("--pref", help="都道府県コード2桁で町字マスタの取得を絞る")
    p.add_argument("--towns", action="store_true", help="住所解析ではなく町字一覧モード")
    p.add_argument("--keyword", help="--towns の部分一致フィルタ")
    p.add_argument("--refresh", action="store_true")
    a = p.parse_args()

    prefs = load_csv("mt_pref_all.csv", f"{S3}/mt_pref/mt_pref_all.csv.zip", a.refresh)
    cities = load_csv("mt_city_all.csv", f"{S3}/mt_city/mt_city_all.csv.zip", a.refresh)

    def towns_by_pref(pref_row):
        pp = pref_row["lg_code"][:2]
        return load_csv(f"mt_town_pref{pp}.csv", f"{S3}/mt_town/pref/mt_town_pref{pp}.csv.zip", a.refresh)

    if a.towns:
        pref_row = next((x for x in prefs if x["lg_code"].startswith(a.pref.zfill(2))), None) if a.pref else None
        if not pref_row:
            sys.exit("--towns には --pref (2桁) が必要です")
        n = 0
        for r in towns_by_pref(pref_row):
            label = r["oaza_cho"] + (r["chome"] or "")
            if a.keyword and a.keyword not in label:
                continue
            print(f'{r["lg_code"]}\t{r["machiaza_id"]}\t{label}')
            n += 1
        print(f"# {n}件", file=sys.stderr)
        return

    if not a.address:
        p.error("住所文字列を指定してください")
    pref, city, town, rest = parse_address(a.address, prefs, cities, towns_by_pref)
    out = {
        "input": a.address,
        "pref": pref["pref"] if pref else None,
        "city": ((city["county"] or "") + (city["city"] or "") + (city["ward"] or "")) if city else None,
        "lg_code": city["lg_code"] if city else (pref["lg_code"] if pref else None),
        "town": ((town["oaza_cho"] or "") + (town["_chome_matched"] or "")) if town else None,
        "machiaza_id": town["machiaza_id"] if town else None,
        "town_kana": ((town["oaza_cho_kana"] or "") + (town["chome_kana"] or "")) if town else None,
        "town_roma": (town["oaza_cho_roma"] or "") if town else None,
        "rest": rest,
        "matched": bool(pref and city and town),
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
