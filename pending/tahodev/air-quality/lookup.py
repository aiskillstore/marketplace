#!/usr/bin/env python3
"""AEROS (そらまめくん) の全国最新1時間値(noudoAll CSV)を検索するヘルパー。

使い方:
  python3 air-quality/lookup.py --keyword 尼崎 --item PM2.5
  python3 air-quality/lookup.py --pref 13 --item PM2.5 --top 5
  python3 air-quality/lookup.py --station 13101010

外部パッケージ不要。CSVは ~/.cache/kurashi-skill/air-quality/ に保存し、
同一時刻の再取得はキャッシュを使う。--refresh で再取得。
"""
import argparse, csv, io, json, os, sys, urllib.request

BASE = "https://soramame.env.go.jp"
CACHE = os.path.expanduser("~/.cache/kurashi-skill/air-quality")

def fetch(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": "kurashi-skill/air-quality"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def latest_hour(refresh=False):
    meta = json.loads(fetch(BASE + "/data/map/kyokuNoudo/metadata.json").decode("utf-8"))
    # "2026/09/26 01:00:00" -> (2026, 09, 26, 01)
    d, t = meta["latest"].split(" ")
    y, m, day = d.split("/")
    hh = t.split(":")[0]
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, f"noudoAll-{y}{m}{day}{hh}.csv")
    if refresh or not os.path.exists(path):
        url = f"{BASE}/data/sokutei/noudoAll/{y}/{m}/{day}/{hh}.csv"
        raw = fetch(url)
        if not raw.startswith("測定局コード".encode("utf-8")):
            sys.exit("エラー: CSVではなくHTMLが返りました(存在しない時刻の可能性)。metadata.jsonのlatestを確認してください。")
        open(path, "wb").write(raw)
    return f"{y}/{m}/{day} {hh}:00", path


def select_hits(hdr, data, item, keyword=None, pref=None, station=None):
    """行リストから条件で絞り、(値, 行) を値降順で返す。未測定("","-")は末尾。"""
    col = hdr.index(item)
    name_i, addr_i, city_i = hdr.index("測定局名称"), hdr.index("住所"), hdr.index("市区町村名")
    pref_i, code_i = hdr.index("都道府県コード"), hdr.index("測定局コード")
    hit = []
    for r in data:
        if station and r[code_i] != station: continue
        if pref and r[pref_i] != pref.zfill(2): continue
        if keyword and keyword not in (r[name_i] + r[addr_i] + r[city_i]): continue
        v = r[col].strip()
        hit.append((float(v) if v not in ("", "-") else None, r))
    hit.sort(key=lambda x: (x[0] is None, -(x[0] or 0)))
    return hit

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--keyword", help="測定局名・住所・市区町村名の部分一致")
    p.add_argument("--pref", help="都道府県コード (01-47)")
    p.add_argument("--station", help="測定局コード (完全一致)")
    p.add_argument("--item", default="PM2.5", help="項目名 (例: PM2.5, OX, TEMP)")
    p.add_argument("--top", type=int, default=10)
    p.add_argument("--refresh", action="store_true")
    a = p.parse_args()

    when, path = latest_hour(a.refresh)
    rows = list(csv.reader(open(path, encoding="utf-8")))
    hdr, data = rows[0], rows[1:]
    try:
        col = hdr.index(a.item)
    except ValueError:
        sys.exit(f"項目 {a.item} はありません。候補: {', '.join(hdr[:17])}")
    name_i, addr_i, type_i, city_i = hdr.index("測定局名称"), hdr.index("住所"), hdr.index("局種別"), hdr.index("市区町村名")
    pref_i, code_i = hdr.index("都道府県コード"), hdr.index("測定局コード")

    hit = select_hits(hdr, data, a.item, keyword=a.keyword, pref=a.pref, station=a.station)

    print(f"{when} JST 時点の速報値 ({a.item}) - {min(a.top, len(hit))}件/{len(hit)}件")
    for v, r in hit[: a.top]:
        vs = f"{v:g}" if v is not None else "(未測定)"
        print(f"{vs}\t{r[name_i]} ({r[type_i]}, {r[city_i]})")
    print("※速報値です。確定値は政府オープンデータカタログを参照。")

if __name__ == "__main__":
    main()
