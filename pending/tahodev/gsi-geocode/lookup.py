#!/usr/bin/env python3
"""国土地理院の公開APIで、住所→緯度経度、緯度経度→標高、緯度経度→住所(市区町村+町丁目)を引く。

使い方:
  python3 gsi-geocode/lookup.py geocode "東京都港区芝公園4-2-8" [--limit 5]
  python3 gsi-geocode/lookup.py elevation --lat 35.6812 --lon 139.7671
  python3 gsi-geocode/lookup.py reverse --lat 35.658649 --lon 139.745468

APIキー不要。標高と逆ジオコーダは「データなし」を HTTP 200 で返す(例外にしない)。
根拠・実測日: gsi-geocode/SKILL.md(2026-10-04)
"""
import argparse, json, re, sys, unicodedata, urllib.parse, urllib.request

ADDRESS_URL = 'https://msearch.gsi.go.jp/address-search/AddressSearch?q='
ELEVATION_URL = 'https://cyberjapandata2.gsi.go.jp/general/dem/scripts/getelevation.php'
REVERSE_URL = 'https://mreversegeocoder.gsi.go.jp/reverse-geocoder/LonLatToAddress'
MUNI_URL = 'https://maps.gsi.go.jp/js/muni.js'


def http_get(url, timeout=30):
    req = urllib.request.Request(url, headers={'User-Agent': 'kurashi-skill/gsi-geocode'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode('utf-8')


def norm(s):
    """全角/半角を揃える(APIの title は「千代田１番」のように全角数字)。"""
    return unicodedata.normalize('NFKC', s)


def parse_geocode(body, query, limit=5):
    items = json.loads(body)
    q = norm(query)
    rows = []
    for f in items:
        lon, lat = f['geometry']['coordinates']
        title = f['properties']['title']
        rows.append({'title': title, 'lat': lat, 'lon': lon, 'prefix_match': norm(title).startswith(q)})
    # APIの並びは関連度順ではない(「東京タワー」の先頭が札幌市東区になる)。前方一致を先に並べる。
    rows.sort(key=lambda r: not r['prefix_match'])
    out = {'query': query, 'total': len(rows), 'returned': min(limit, len(rows)), 'results': rows[:limit]}
    if len(rows) == 0:
        out['note'] = '該当なし。郵便番号は引けない(0件)。「都道府県+市区町村+町名+番地」か施設名で試す'
    elif len(rows) > 1:
        out['note'] = f'{len(rows)}件に曖昧一致。先頭を採用せず、都道府県・市区町村を足して絞る'
    return out


def parse_elevation(body):
    d = json.loads(body)
    if d.get('elevation') == '-----':
        return {'elevation_m': None, 'note': '標高データなし。海上・範囲外・入力不正はAPIが区別せず、すべて「-----」を返す'}
    return {'elevation_m': float(d['elevation']), 'source': d['hsrc']}


def parse_muni_js(text):
    muni = {}
    for key, val in re.findall(r'MUNI_ARRAY\["(\d+)"\]\s*=\s*\'([^\']*)\'', text):
        pref_no, pref, code, name = val.split(',', 3)
        muni[key] = {'pref': pref, 'name': name.replace('\u3000', ' ')}
    return muni


def muni_lookup(muni, muni_cd):
    # 逆ジオコーダは北海道を "01101" と返すが、muni.js のキーは先頭の0を落とした "1101"
    return muni.get(muni_cd) or muni.get(muni_cd.lstrip('0'))


def parse_reverse(body, muni):
    d = json.loads(body)
    r = d.get('results')
    if not r:
        return {'address': None, 'note': '該当なし。海上・国外・入力不正は空の {} が返る(HTTP 200)'}
    m = muni_lookup(muni, r['muniCd'])
    out = {'muniCd': r['muniCd'], 'town': r['lv01Nm']}
    if m:
        out.update({'pref': m['pref'], 'city': m['name'], 'address': m['pref'] + m['name'].replace(' ', '') + r['lv01Nm']})
    else:
        out['note'] = 'muni.js に市区町村コードがない'
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    g = sub.add_parser('geocode'); g.add_argument('query'); g.add_argument('--limit', type=int, default=5)
    for name in ('elevation', 'reverse'):
        p = sub.add_parser(name); p.add_argument('--lat', type=float, required=True); p.add_argument('--lon', type=float, required=True)
    a = ap.parse_args(argv)
    try:
        if a.cmd == 'geocode':
            out = parse_geocode(http_get(ADDRESS_URL + urllib.parse.quote(a.query)), a.query, a.limit)
        elif a.cmd == 'elevation':
            if not (-90 <= a.lat <= 90 and -180 <= a.lon <= 180):
                raise SystemExit(json.dumps({'error': '緯度経度の範囲外'}, ensure_ascii=False))
            out = parse_elevation(http_get(f'{ELEVATION_URL}?lon={a.lon}&lat={a.lat}&outtype=JSON'))
        else:
            body = http_get(f'{REVERSE_URL}?lat={a.lat}&lon={a.lon}')
            out = parse_reverse(body, parse_muni_js(http_get(MUNI_URL)))
    except SystemExit:
        raise
    except Exception as e:
        print(json.dumps({'error': f'取得失敗: {e}'}, ensure_ascii=False)); return 1
    print(json.dumps(out, ensure_ascii=False, indent=2)); return 0


if __name__ == '__main__':
    sys.exit(main())
