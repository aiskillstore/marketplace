---
name: air-quality
description: 環境省の大気汚染物質広域監視システム(AEROS・そらまめくん)から、PM2.5・光化学オキシダントなどの測定値(速報値)を取得する。全国約1,600測定局の最新1時間値・測定局ごとの今日/7日分・都道府県ごとの月次履歴に対応。「今のPM2.5」「空気が悪い?」の質問に答える。APIキー・ログイン不要。確定値(過去の公式統計)は対象外。
license: MIT
metadata:
  category: environment
  locale: ja-JP
---

# air-quality

環境省の大気汚染物質広域監視システム(AEROS、通称そらまめくん)が公開する測定値(速報値)を読むスキル。公式のAPI利用者向けコーナーが `soramame/api/data_search` を開発者向けに案内しており、APIキー・ログイン・ユーザー登録は不要。

**実測日: 2026-09-26。以下のURL・構造・件数はすべて当日の実測で確認。**

## エンドポイント一覧

| 内容 | URL |
| --- | --- |
| 全国の最新1時間値(全測定局) | `https://soramame.env.go.jp/data/sokutei/noudoAll/{YYYY}/{MM}/{DD}/{HH}.csv` |
| 測定局ごとの今日の値 | `https://soramame.env.go.jp/data/sokutei/NoudoTime/{SKT_CD}/today.csv` |
| 測定局ごとの直近7日 | `https://soramame.env.go.jp/data/sokutei/NoudoTime/{SKT_CD}/7day.csv` |
| 公式API(都道府県別・月次履歴JSON) | `https://soramame.env.go.jp/soramame/api/data_search?Start_YM={yyyymm}&TDFKN_CD={01-47}&REQUEST_DATA={項目}` |
| PM2.5注意喚起エリア | `https://soramame.env.go.jp/data/sokutei/pm25/alert.csv` |
| 最新データ時刻(地図用メタ) | `https://soramame.env.go.jp/data/map/kyokuNoudo/metadata.json` |

## 1. 全国の「今」を取る(noudoAll CSV)

```bash
curl -sm 60 -O https://soramame.env.go.jp/data/sokutei/noudoAll/2026/09/26/01.csv
```

最新の時は `metadata.json` の `latest`(2026-09-26実測: `2026/09/26 01:00:00`)から組み立てる。時は2桁の `01`〜`24` 表記に注意(01時のファイルは `01.csv`)。

2026-09-26 01:00 JST実測: 200、255,102バイト、1,594測定局。列は24列:

```
測定局コード,SO2,NO,NO2,NOX,CO,OX,NMHC,CH4,THC,SPM,PM2.5,SP,WD,WS,TEMP,HUM,測定局名称,住所,問い合わせ先,局種別,地域コード,都道府県コード,市区町村名
```

測定局名称・住所・局種別(一般局/自排局)・市区町村名を含むので、このCSVだけで局の検索もできる。内訳実測: 一般局1,244、自排局349。緯度経度の列はない(座標での最寄り検索はこのCSVではできない)。未測定の項目は空欄か `-`。PM2.5は全1,594局中1,031局で測定されていた(同時刻実測。平均8.9、最大28.0μg/m3=国設尼崎自動車交通環境測定所)。

同梱の `lookup.py` は、`metadata.json` から最新時刻を引き、noudoAll CSVをキャッシュしつつ、局名・住所・市区町村名の部分一致や都道府県コードで絞り込んで項目値の上位を表示する。外部パッケージは不要。

```bash
python3 air-quality/lookup.py --keyword 尼崎 --item PM2.5 --top 3
# 2026/09/26 01:00 JST 時点の速報値 (PM2.5)
# 28  国設尼崎自動車交通環境測定所 (自排局, 尼崎市)  ...
```

## 2. 測定局ごとの今日/7日を取る

```bash
curl -sm 30 https://soramame.env.go.jp/data/sokutei/NoudoTime/13101010/today.csv
```

列: `年,月,日,時,SO2,NO,NO2,NOX,CO,OX,NMHC,CH4,THC,SPM,PM2.5,SP,WD,WS,TEMP,HUM`。2026-09-26実測(東京の13101010): 200、01時の行が PM2.5=7、TEMP=24、HUM=73。`7day.csv` は同じ列で7日分。

## 3. 公式APIで履歴を取る(data_search)

公式のAPI説明ページ(`/data/apiManual/3.html`)が案内するJSON API。月単位・都道府県単位。

```bash
curl -sm 120 'https://soramame.env.go.jp/soramame/api/data_search?Start_YM=202609&End_YM=202609&TDFKN_CD=13&REQUEST_DATA=PM2_5,TEMP'
```

- `Start_YM` 必須(yyyymm)、`End_YM` 省略で現在の年月
- `TDFKN_CD` 必須(01〜47)、`SKT_CD` 複数可(カンマ区切り)
- `REQUEST_DATA`: `SO2,NO,NO2,NOX,CO,OX,NMHC,CH4,THC,SPM,PM2_5,SP,WD,WS,TEMP,HUM`(PM2.5だけ `PM2_5` とアンダースコア)

返り値は `[{"SKT_CD":"13101010","SKT_DATE":"2026/09/01","SKT_TIME":"01","PM2_5":"3","TEMP":"24.3"}, ...]`。2026-09-26実測(東京都・2026年9月・PM2_5とTEMP): 200、約4.4MB、50,830行、85測定局。**月全体を取ると数MBになるので、最新だけ欲しい用途には noudoAll か today.csv を使う。** 未測定は `"-"`。速報値なので最新行は遅れる局がある(同日実測で最新行は前日22時の局もあった)。

## 4. PM2.5注意喚起を見る

```bash
curl -s https://soramame.env.go.jp/data/sokutei/pm25/alert.csv
```

`都道府県コード,都道府県名,地域コード,注意喚起実施日時,注意喚起解除日時`。2026-09-26実測: 200、ヘッダ行だけ(発表中の注意喚起なし)。空はエラーではなく「現在なし」。

## エラー・失敗時の対応

共通の取得時チェックリストは [共通レスポンス契約](../docs/response-contract.md) の「取得時の落とし穴チェックリスト」を参照。

- **noudoAll の時刻違いで404にならないがSPAページが返る**: 存在しないURLはSPAのシェルHTML(約2.6KB)が200で返る。**受け取ったら先頭行が `測定局コード` で始まるか必ず確認する。** HTMLが返ったら時刻の組み立て(ゼロ埋め2桁)か `metadata.json` のlatestを見直す。
- **`-` や空欄**: その局ではその項目を測っていない/未送信。推測で埋めない。測定局が少ない項目(例: PM2.5は約3割の局が未測定)は「この局では測定していない」と伝える。
- **data_search が大きすぎる**: 月×都道府県で数MB。`SKT_CD` で局を絞るか、期間を分割する。
- **確定値が欲しい**: このAPIは速報値。確定値は政府オープンデータカタログ(data.go.jp の環境省データ)を案内する。

## 注意

- 値は速報値。回答には必ず測定日時(JST)と測定局名を添える(「9月26日01時の国設尼崎…ではPM2.5が28」)。
- 一般局(住宅地などの環境大気)と自排局(自動車排出ガス監視、道路沿い)を区別して伝える。同じ町でも値の意味が違う。
- 健康の判断(外出・マスク等)はこのスキルの対象外。注意喚起の発表は alert.csv と自治体の公式発表を案内する。

## English summary

Reads Japan's Ministry of the Environment AEROS (Soramame-kun) air-pollution measurements from public endpoints, no API key or login. Nationwide latest hourly snapshot: /data/sokutei/noudoAll/{YYYY}/{MM}/{DD}/{HH}.csv (verified 2026-09-26: 255,102 bytes, 1,594 stations, includes station name/address/type; PM2.5 measured at 1,031 of them). Per-station today and 7-day CSVs under /data/sokutei/NoudoTime/{SKT_CD}/. Official documented JSON API /soramame/api/data_search for month-by-prefecture history (multi-MB). PM2.5 advisory areas at /data/sokutei/pm25/alert.csv (empty = none). Gotchas: unknown URLs return a 200 SPA shell HTML, so always check the CSV header; "-" means not measured, never guess; values are provisional (速報値), not finalized statistics; lat/lon is not provided in these endpoints.
