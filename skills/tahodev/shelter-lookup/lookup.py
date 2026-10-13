#!/usr/bin/env python3
"""Find the nearest GSI designated emergency evacuation sites."""

from __future__ import annotations

import argparse
import csv
import math
import os
from pathlib import Path
import sys
import tempfile
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

SITES_URL = "https://hinanmap.gsi.go.jp/hinanjocp/defaultFtpData/csv/mergeFromCity_2.csv"
HISTORY_URL = "https://hinanmap.gsi.go.jp/hinanjocp/defaultFtpData/publicHistoryCSV/publicHistoryListData.csv"
EARTH_RADIUS_KM = 6371.0088
CACHE_STALE_DAYS = 7

HAZARDS = {
    "flood": "洪水",
    "landslide": "崖崩れ、土石流及び地滑り",
    "storm-surge": "高潮",
    "earthquake": "地震",
    "tsunami": "津波",
    "fire": "大規模な火事",
    "inland-flood": "内水氾濫",
    "volcano": "火山現象",
}
HAZARD_ALIASES = {
    **{key: key for key in HAZARDS},
    **{label: key for key, label in HAZARDS.items()},
    "崖崩れ": "landslide",
    "土石流": "landslide",
    "地滑り": "landslide",
    "大規模火災": "fire",
    "内水": "inland-flood",
    "火山": "volcano",
}


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return great-circle distance in kilometres between two WGS 84 coordinates."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    return EARTH_RADIUS_KM * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def download(url: str, destination: Path, timeout: int) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = Request(url, headers={"User-Agent": "kurashi-skill shelter-lookup/1.0"})
    try:
        with urlopen(request, timeout=timeout) as response, tempfile.NamedTemporaryFile(
            dir=destination.parent, delete=False
        ) as tmp:
            while chunk := response.read(1024 * 1024):
                tmp.write(chunk)
            temporary = Path(tmp.name)
        temporary.replace(destination)
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        raise RuntimeError(f"ダウンロードに失敗しました: {url} ({exc})") from exc


def load_update_dates(path: Path) -> dict[str, str]:
    dates: dict[str, str] = {}
    with path.open(encoding="utf-8-sig", newline="") as source:
        for row in csv.reader(source):
            if len(row) >= 4 and row[1] and row[3]:
                dates[row[1].strip()] = row[3].strip()
    return dates


def stale_caches(paths: list[Path], stale_days: int, now: float | None = None) -> list[tuple[Path, int]]:
    """Return cached files older than stale_days, each with its age in whole days."""
    moment = time.time() if now is None else now
    stale: list[tuple[Path, int]] = []
    for path in paths:
        try:
            age = int((moment - path.stat().st_mtime) // 86400)
        except OSError:
            continue
        if age > stale_days:
            stale.append((path, age))
    return stale


def nearest_sites(
    path: Path, latitude: float, longitude: float, hazard_column: str, limit: int
) -> list[tuple[float, dict[str, str]]]:
    matches: list[tuple[float, dict[str, str]]] = []
    with path.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        if not reader.fieldnames or hazard_column not in reader.fieldnames:
            raise RuntimeError(f"CSVに災害種別列「{hazard_column}」がありません")
        for row in reader:
            if row.get(hazard_column, "").strip() != "1":
                continue
            try:
                site_lat = float(row["緯度"])
                site_lon = float(row["経度"])
            except (KeyError, TypeError, ValueError):
                continue
            if not (math.isfinite(site_lat) and math.isfinite(site_lon)) or not (
                -90 <= site_lat <= 90 and -180 <= site_lon <= 180
            ):
                continue
            distance = haversine_km(latitude, longitude, site_lat, site_lon)
            matches.append((distance, row))
    return sorted(matches, key=lambda item: (item[0], item[1].get("施設・場所名", "")))[:limit]


def coordinate(value: str, minimum: float, maximum: float, label: str) -> float:
    try:
        number = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"{label}は数値で指定してください") from exc
    if not math.isfinite(number) or not minimum <= number <= maximum:
        raise argparse.ArgumentTypeError(f"{label}は{minimum}〜{maximum}で指定してください")
    return number


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="現在地に近い指定緊急避難場所を災害種別で検索")
    parser.add_argument("--latitude", required=True, type=lambda v: coordinate(v, -90, 90, "緯度"))
    parser.add_argument("--longitude", required=True, type=lambda v: coordinate(v, -180, 180, "経度"))
    parser.add_argument(
        "--hazard",
        required=True,
        help="flood/landslide/storm-surge/earthquake/tsunami/fire/inland-flood/volcano、または日本語名",
    )
    parser.add_argument("--limit", type=int, default=3, help="表示件数(既定: 3、最大: 20)")
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "kurashi-skill" / "shelter-lookup",
    )
    parser.add_argument("--refresh", action="store_true", help="キャッシュを使わず公式CSVを再取得")
    parser.add_argument("--timeout", type=int, default=120, help="ダウンロードのタイムアウト秒数")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    hazard_key = HAZARD_ALIASES.get(args.hazard)
    if not hazard_key:
        print(f"未対応の災害種別です: {args.hazard}", file=sys.stderr)
        print("対応: " + ", ".join(HAZARDS), file=sys.stderr)
        return 2
    if not 1 <= args.limit <= 20:
        print("--limit は1〜20で指定してください", file=sys.stderr)
        return 2

    sites_path = args.cache_dir / "mergeFromCity_2.csv"
    history_path = args.cache_dir / "publicHistoryListData.csv"
    try:
        for url, path in ((SITES_URL, sites_path), (HISTORY_URL, history_path)):
            if args.refresh or not path.exists():
                download(url, path, args.timeout)
        update_dates = load_update_dates(history_path)
        results = nearest_sites(sites_path, args.latitude, args.longitude, HAZARDS[hazard_key], args.limit)
    except (OSError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    for cached, age in stale_caches([sites_path, history_path], CACHE_STALE_DAYS):
        print(
            f"警告: キャッシュ {cached.name} は{age}日前のものです。避難所データは市町村によって更新されます。--refresh で再取得してください。",
            file=sys.stderr,
        )

    print(f"{HAZARDS[hazard_key]}に指定された最寄りの指定緊急避難場所 (上位{args.limit}件)")
    print("距離は入力座標からのHaversine法による直線距離です。道路距離・徒歩距離ではありません。")
    if not results:
        print("該当する場所が見つかりませんでした。公式CSVの取得状況と災害種別を確認してください。")
        return 0

    for index, (distance, row) in enumerate(results, 1):
        municipality = row.get("都道府県名及び市町村名", "").strip()
        updated = update_dates.get(municipality, "不明")
        print(f"{index}. {row.get('施設・場所名', '').strip()} - {distance:.2f} km")
        print(f"   住所: {row.get('住所', '').strip()}")
        print(f"   座標: {row.get('緯度', '').strip()}, {row.get('経度', '').strip()}")
        print(f"   災害種別: {HAZARDS[hazard_key]} / 自治体データ更新日: {updated}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
