---
name: heatstroke
description: 環境省 熱中症予防情報サイトの公式API v1から暑さ指数(WBGT)の予測値・実況値(推定/実測)を取得する。全国865の情報提供地点の地点マスタ(緯度経度つき)、1日3回発表の3時間ごと予測、時間単位の実況値に対応。「今日の暑さ指数」「熱中症リスクは?」の質問に答える。APIキー・ログイン不要。救急搬送統計や特別警戒アラート本文は対象外。
license: MIT
metadata:
  category: health
  locale: ja-JP
---

# heatstroke

環境省 熱中症予防情報サイト(wbgt.env.go.jp)の **API v1**(2026-06-24掲載の仕様書 第1.1版)で暑さ指数(WBGT)を読むスキル。APIキー・ログイン・ユーザー登録は不要。環境省はユーザー登録なしで機械可読な気象・防災データを公開している。

**実測日: 2026-09-26。以下のURL・構造・件数はすべて当日の実測で確認。**

## エンドポイント一覧

| 内容 | URL |
| --- | --- |
| 予測値API(JSON) | `https://www.wbgt.env.go.jp/api/v1/getForecastData` |
| 実況値API(JSON) | `https://www.wbgt.env.go.jp/api/v1/getSurveyData` |
| 情報提供地点マスタ(CSV) | `https://www.wbgt.env.go.jp/man15NH/wbgt_point_master-20260515.csv` |
| API仕様書(PDF・第1.1版) | `https://www.wbgt.env.go.jp/man15NH/wbgt_data_api_service_manual.pdf` |

## 0. 旧CSVサービスは終了 — API v1に移行済み

以前の直ファイルCSV(`https://www.wbgt.env.go.jp/prev15WG/dl/yohou_{yyyymmdd}.csv` など)は **404**(196バイトのHTML)を返す(2026-09-26実測)。検索で上位に来る旧手順・旧URLは使わない。現行はAPI v1(レスポンスはJSON)のみ。

## 1. 地点マスタを取る

```bash
curl -sO https://www.wbgt.env.go.jp/man15NH/wbgt_point_master-20260515.csv
```

2026-09-26実測: 200、130,112バイト、865地点(+ヘッダ)。UTF-8(BOMつき)。列: `地方, 振興局, 地点番号, 観測所名, よみがな, ローマ字表記, 所在地, Latitude, Latitude_3, Longitude, Longitude_4, ...`。

**罠(実測)**: ヘッダとデータ行は `,`(カンマ+空白)区切りで、**各フィールド先頭に空白が入る**。DictReaderのキーが `Latitude` のようになりそのままでは引けない。キーを strip してから使うこと(lookup.py で対応済み)。緯度経度は 度/分 の2列分割(例: 東京 35度41.4分)。`実測開始日` が入っている地点だけ実測値あり(それ以外は推定のみ)。

## 2. 予測値を取る(getForecastData)

```bash
curl -s 'https://www.wbgt.env.go.jp/api/v1/getForecastData?location_type=1&date_search_type=3&wbgt_nos=44132&forecast_origin_date=20260925170000'
```

- `location_type`: 1=地点別 / 2=都道府県別 / 3=全地点
- `date_search_type`: 3=特定時刻(発表時刻を `forecast_origin_date` で指定)。**発表は1日3回・05/11/17時 JST**。直近の発表時刻を計算して渡す(lookup.py の `latest_announcement`)
- 1=連続期間指定(`range_date_from`/`range_date_to`)、2=特定期間指定(`fixed_time_dates`)

2026-09-26実測(東京 44132、発表 2026/09/25 17:00): `count: 19`、3時間ごと・約57時間先まで。レコード例:

```json
{"reference_time":"2026/09/25 17:00:00","wbgt_no":44132,"forecast_val":"210","forecast_time":"2026/09/25 18:00:00","flag":0}
```

**`forecast_val` は10倍値**: `"210"` = 21.0℃。表示前に必ず10で割る。

## 3. 実況値を取る(getSurveyData)

```bash
curl -s 'https://www.wbgt.env.go.jp/api/v1/getSurveyData?data_type=0&data_type=1&location_type=1&wbgt_nos=44132&date_from=20260901000000&date_to=20260901235959'
```

- `data_type`: 0=実況推定値 / 1=実況実測値(配列で複数指定可)
- `date_from`/`date_to` は観測日時・14桁。必須

レコード例(2026-09-26実測、東京 2026/09/01 00:00): `wbgt_WO`(屋外)=21.9、`wbgt_WI`(屋内)=4.0、`wbgt_Tw`(湿球)=21.2、`wbgt_Tg`(黒球)=23.3、`wbgt_class`=1。**1日分で24レコード**。実況推定値の配信にはラグがある(同日未明に前日の特定時刻を絞ると空が返ることがある → 日単位で取る)。

## 4. 暑さ指数の5段階(環境省)

| WBGT | 区分 |
| --- | --- |
| 31℃以上 | 危険 |
| 28以上31未満 | 厳重警戒 |
| 25以上28未満 | 警戒 |
| 21以上25未満 | 注意 |
| 21未満 | ほぼ安全 |

回答には必ず地点名と基準時刻(発表時刻/観測日時・JST)を添える(「9月26日09時の予測で東京は20℃・ほぼ安全」)。

## 5. エラー形式と失敗時の対応

共通の取得時チェックリストは [共通レスポンス契約](../docs/response-contract.md) の「取得時の落とし穴チェックリスト」を参照。

- エラーはJSON: `{"status":"error","errMsg":["地点番号配列は少なくとも1件指定してください。"]}`。HTTPは200でも `status` を必ず見る。
- **`pref_cds` はJIS都道府県コードではない**(最大の罠・実測): `pref_cds=13`(JISの東京)を渡すと地点番号13061系(東京ではない)が返り、`44` を渡すと44046系(東京)が返る。アメダス観測所番号の上位ブロック番号体系。都道府県で絞るより、地点マスタで地点番号を引いて `wbgt_nos` を使う方が安全。
- **`data` が空** (`{"status":"success","data":[],"count":0}`): エラーではない。サービス期間(概ね4月下旬〜10月)外、推定値の配信ラグ、または発表時刻の指定ミス。
- **旧URLの404**: §0参照。「サンプルCSVが見つからない」ではなくサービスごとAPI v1に置き換わっている。
- **地点番号がわからない**: マスタCSVを観測所名・よみがな・所在地で検索するか、緯度経度から最近傍を取る(lookup.py)。

## ヘルパー

`heatstroke/lookup.py` (標準ライブラリのみ):

```bash
python3 heatstroke/lookup.py --keyword 東京            # 地点検索
python3 heatstroke/lookup.py --lat 35.68 --lon 139.69  # 最寄り地点の予測(5段階つき)
python3 heatstroke/lookup.py --station 44132 --mode survey --date 2026-09-01
```

マスタCSVは `~/.cache/kurashi-skill/heatstroke/` にキャッシュ。`--refresh` で再取得。テストは `heatstroke/tests/`(フィクスチャ5件)。

## 注意

- 暑さ指数は「熱中症リスクの目安」。運動可否の判断は環境省の運動指針・日本気象協会等の公式情報を案内する。
- 熱中症特別警戒アラートの発表状況・救急搬送人員速報は本スキルの検証範囲外(サイトの掲載ページを案内する)。
- 予測値は発表ごとに更新される。古い発表時刻の値を最新として伝えない。

## English summary

Reads WBGT (wet-bulb globe temperature) heat-stress index from Japan's Ministry of the Environment official API v1, no key or login. Forecasts: /api/v1/getForecastData (3-hour steps, ~57h ahead, announced 05/11/17 JST; forecast_val is 10x, "210" = 21.0 degC). Observations: /api/v1/getSurveyData (data_type 0=estimated / 1=measured, hourly, wbgt_WO outdoor / wbgt_WI indoor). Station master CSV at /man15NH/wbgt_point_master-20260515.csv (865 stations, verified 2026-09-26; header and fields are space-padded - strip keys; lat/lon split into degree/minute columns). Gotchas: the old CSV file service (/prev15WG/dl/...) is gone (404), pref_cds is NOT the JIS prefecture code (13 does not return Tokyo; 44 does) - use station numbers from the master; empty data array means out-of-season or lag, not an error; errors come as JSON status=error with errMsg. Helper lookup.py caches the master, finds nearest station by lat/lon, and maps values to the official 5-level scale (danger >=31, severe 28-31, warning 25-28, caution 21-25, safe <21).
