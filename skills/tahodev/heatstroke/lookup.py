#!/usr/bin/env python3
"""環境省 熱中症予防情報サイト API v1 で暑さ指数(WBGT)を調べるヘルパー。

使い方:
  python3 heatstroke/lookup.py --keyword 東京              # 地点を探す
  python3 heatstroke/lookup.py --lat 35.68 --lon 139.69    # 最寄り地点の予測値
  python3 heatstroke/lookup.py --station 44132 --mode survey --date 2026-09-01

外部パッケージ不要。地点マスタは ~/.cache/kurashi-skill/heatstroke/ に保存。
実測日: 2026-09-26 (API仕様書 第1.1版 / man15NH/wbgt_data_api_service_manual.pdf)
"""
import argparse, csv, io, json, math, os, sys, urllib.request, urllib.parse, datetime

BASE = "https://www.wbgt.env.go.jp"
MASTER_URL = BASE + "/man15NH/wbgt_point_master-20260515.csv"
CACHE = os.path.expanduser("~/.cache/kurashi-skill/heatstroke")

LEVELS = [(31, "危険"), (28, "厳重警戒"), (25, "警戒"), (21, "注意"), (0, "ほぼ安全")]

def fetch(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": "kurashi-skill/heatstroke"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def level(v):
    """WBGT値(℃) -> 環境省の5段階"""
    for th, name in LEVELS:
        if v >= th:
            return name
    return "ほぼ安全"

def master_path(refresh=False):
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, "wbgt_point_master.csv")
    if refresh or not os.path.exists(path):
        open(path, "wb").write(fetch(MASTER_URL))
    return path

def load_stations(path):
    """地点マスタ -> [{no, name, lat, lon, measured}]"""
    out = []
    with open(path, encoding="utf-8-sig") as f:
        rd = csv.DictReader(f)
        # ヘッダは ", " 区切りで各項目名の先頭に空白が入る -> 正規化
        rd.fieldnames = [h.strip() for h in (rd.fieldnames or [])]
        for r in rd:
            r = {k.strip(): v for k, v in r.items()}
            try:
                lat = float(r["Latitude"]) + float(r["Latitude_3"]) / 60
                lon = float(r["Longitude"]) + float(r["Longitude_4"]) / 60
            except (ValueError, TypeError):
                continue
            out.append({
                "no": r["地点番号"].strip(), "name": r["観測所名"].strip(),
                "lat": lat, "lon": lon,
                "measured": bool(r.get("実測開始日", "").strip()),
            })
    return out

def hav(lat1, lon1, lat2, lon2):
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))

def nearest(stations, lat, lon):
    return min(stations, key=lambda s: hav(lat, lon, s["lat"], s["lon"]))

def latest_announcement(now=None):
    """予測の発表時刻(05/11/17時 JST)の直近を YYYYMMDDHHMMSS で返す"""
    now = now or datetime.datetime.now()
    for h in (17, 11, 5):
        cand = now.replace(hour=h, minute=0, second=0, microsecond=0)
        if cand <= now:
            return cand.strftime("%Y%m%d%H%M%S")
    return (now - datetime.timedelta(days=1)).replace(hour=17, minute=0, second=0, microsecond=0).strftime("%Y%m%d%H%M%S")

def api(path, params):
    qs = urllib.parse.urlencode(params, doseq=True)
    raw = fetch(f"{BASE}/api/v1/{path}?{qs}")
    obj = json.loads(raw.decode("utf-8"))
    if obj.get("status") != "success":
        sys.exit("APIエラー: " + "; ".join(obj.get("errMsg", ["unknown"])))
    return obj

def cmd_stations(stations, a):
    for s in stations:
        if a.keyword and a.keyword not in s["name"]:
            continue
        print(f'{s["no"]}\t{s["name"]}\t{"実測あり" if s["measured"] else "推定のみ"}')
    print(f"# {len(stations)}件中 {sum(1 for s in stations if not a.keyword or a.keyword in s['name'])}件", file=sys.stderr)

def cmd_forecast(no, a):
    origin = a.origin or latest_announcement()
    obj = api("getForecastData", {
        "location_type": 1, "date_search_type": 3,
        "wbgt_nos": [no], "forecast_origin_date": origin})
    rows = obj.get("data", [])
    if not rows:
        sys.exit(f"予測データなし (発表時刻 {origin})。サービス期間(概ね4-10月)外か、発表時刻の指定を確認。")
    print(f"# 発表 {rows[0]['reference_time']} / 地点 {no} / {len(rows)}件")
    for r in rows[: a.hours // 3 + 1]:
        v = int(r["forecast_val"]) / 10
        print(f"{r['forecast_time']}\t{v:.1f}℃\t{level(v)}")

def cmd_survey(no, a):
    date = (a.date or (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")).replace("-", "")
    obj = api("getSurveyData", {
        "data_type": [0, 1], "location_type": 1, "wbgt_nos": [no],
        "date_from": date + "000000", "date_to": date + "235959"})
    rows = obj.get("data", [])
    if not rows:
        sys.exit("実況データなし。実況推定値の更新にはラグがあり、シーズン外は配信されません。")
    print(f"# 地点 {no} / {len(rows)}件 (wbgt_WO=屋外, wbgt_WI=屋内)")
    mx = 0.0
    for r in rows:
        wo = r.get("wbgt_WO", "")
        try:
            v = float(wo)
            mx = max(mx, v)
        except ValueError:
            v = None
        print(f"{r['wbgt_date']}\tWO {wo}℃\t{level(v) if v is not None else '-'}")
    print(f"# 日最大(屋外) {mx:.1f}℃ {level(mx)}")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--keyword", help="観測所名の部分一致 (地点検索)")
    p.add_argument("--station", help="地点番号 (例: 44132=東京)")
    p.add_argument("--lat", type=float); p.add_argument("--lon", type=float)
    p.add_argument("--mode", choices=["forecast", "survey", "stations"], default=None)
    p.add_argument("--date", help="survey対象日 YYYY-MM-DD (既定: 昨日)")
    p.add_argument("--origin", help="forecast発表時刻 YYYYMMDDHHMMSS (既定: 直近の05/11/17時)")
    p.add_argument("--hours", type=int, default=24)
    p.add_argument("--refresh", action="store_true")
    a = p.parse_args()

    stations = load_stations(master_path(a.refresh))

    if a.keyword and not a.station and not (a.lat and a.lon):
        return cmd_stations(stations, a)
    if a.lat is not None and a.lon is not None:
        s = nearest(stations, a.lat, a.lon)
        d = hav(a.lat, a.lon, s["lat"], s["lon"])
        print(f"# 最寄り: {s['name']} ({s['no']}) 約{d:.1f}km", file=sys.stderr)
        a.station = s["no"]
    if not a.station:
        p.error("--station か --lat/--lon か --keyword を指定してください")
    mode = a.mode or "forecast"
    if mode == "forecast":
        cmd_forecast(a.station, a)
    else:
        cmd_survey(a.station, a)

if __name__ == "__main__":
    main()
