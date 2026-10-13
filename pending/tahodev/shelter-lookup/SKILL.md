---
name: shelter-lookup
description: 国土地理院の指定緊急避難場所・指定避難所データ(全国、市町村が指定した公式データ)をダウンロードして避難所を検索する。避難所、避難場所、ハザード時の逃げ場、災害種別ごとの避難場所の質問に対応。APIキー・ログイン不要。ハザードマップの範囲判定や浸水深の計算は対象外。
license: MIT
metadata:
  category: disaster
  locale: ja-JP
---

# shelter-lookup

国土地理院の「避難所等データダウンロードサイト」が公開する、市町村長指定の指定緊急避難場所・指定避難所データをダウンロードして検索するスキル。APIキー・ログイン不要。国土数値情報の避難施設データ(P20)は2012年度版で古いため使わない(後述)。

**実測日: 2026-09-19。以下のURL・構造・行数はすべて当日の実測で確認。**

## ダウンロード元

公開ページ: https://hinanmap.gsi.go.jp/hinanjocp/hinanbasho/koukaidate.html (国土地理院 指定緊急避難場所・指定避難所データ)

全国データは2系統ある(いずれもUTF-8 BOMつきCSV。GeoJSON版も同階層の `geoJSON/` にある)。

| データ | URL | 実測サイズ |
| --- | --- | --- |
| 指定避難所 | `https://hinanmap.gsi.go.jp/hinanjocp/defaultFtpData/csv/mergeFromCity_1.csv` | 約11.7MB |
| 指定緊急避難場所(災害種別フラグつき) | `https://hinanmap.gsi.go.jp/hinanjocp/defaultFtpData/csv/mergeFromCity_2.csv` | 約17.0MB |

```bash
curl -sm 120 -O https://hinanmap.gsi.go.jp/hinanjocp/defaultFtpData/csv/mergeFromCity_2.csv
```

## CSVの読み方

### 指定避難所(mergeFromCity_1.csv)

列: `NO,共通ID,都道府県名及び市町村名,施設・場所名,住所,指定緊急避難場所との住所同一,その他市町村長が必要と認める事項,受入対象者,緯度,経度,備考`

### 指定緊急避難場所(mergeFromCity_2.csv)

列: `NO,共通ID,都道府県名及び市町村名,施設・場所名,住所,洪水,崖崩れ、土石流及び地滑り,高潮,地震,津波,大規模な火事,内水氾濫,火山現象,指定避難所との住所同一,緯度,経度,備考`

災害種別の列は `1` が「その災害の避難場所として指定されている」、空欄は対象外。**災害種別を必ず確認する**: 洪水の避難場所が津波の避難場所とは限らない。

## 現在地から災害種別で最寄り3か所を探す

同梱の `lookup.py` は、ユーザーの緯度・経度を基準に、指定した災害種別のフラグが `1` の場所だけをHaversine法で距離順に並べる。既定では上位3か所を表示し、各自治体のデータ更新日も一覧CSVから付ける。外部パッケージは不要。

```bash
python3 shelter-lookup/lookup.py \
  --latitude 35.681236 \
  --longitude 139.767125 \
  --hazard flood \
  --cache-dir /tmp/kurashi-shelter-cache
```

`--hazard` は `flood`(洪水)、`landslide`(崖崩れ・土石流・地滑り)、`storm-surge`(高潮)、`earthquake`(地震)、`tsunami`(津波)、`fire`(大規模な火事)、`inland-flood`(内水氾濫)、`volcano`(火山現象)に対応する。日本語名も指定できる。取得済みCSVは `~/.cache/kurashi-skill/shelter-lookup/` に保存し、再取得は `--refresh` を使う。キャッシュが7日より古い場合は、市町村の更新を取りこぼす可能性があるため stderr に警告を出す。

出力例:

```text
洪水に指定された最寄りの指定緊急避難場所 (上位3件)
距離は入力座標からのHaversine法による直線距離です。道路距離・徒歩距離ではありません。
1. ○○小学校 - 0.42 km
   住所: 東京都○○区...
   座標: 35.x, 139.x
   災害種別: 洪水 / 自治体データ更新日: 2026-09-10
```

### 住所・施設名で簡易検索する

```bash
# 住所・施設名の部分一致 (ヘッダ行を落とす)
grep '千代田区' mergeFromCity_2.csv | head -5
# 津波指定のある施設だけ (津波列は10列目。awkは1始まり)
awk -F, '$10==1' mergeFromCity_2.csv | head -5
```

**注意: 改行を含む引用符付きレコードがある**(mergeFromCity_2.csv で2026-09-19実測147件)。`grep` や `awk` の行単位処理ではそのレコードの列がずれる。厳密な抽出には Python の `csv` モジュールを使う。

```bash
python3 - <<'EOF'
import csv
for row in csv.reader(open('mergeFromCity_2.csv', encoding='utf-8-sig')):
    if row[9] == '1':  # 津波列(10列目)
        print(row[2], row[3])
EOF
```

CSVには引用符を含むフィールドがありうるため、確実な検索・距離計算には `lookup.py` の `csv` モジュール処理を使う。

### データの新しさを確認する

市町村ごとのデータ更新日は公開ページと同じサーバの一覧CSVで分かる。

```bash
curl -s https://hinanmap.gsi.go.jp/hinanjocp/defaultFtpData/publicHistoryCSV/publicHistoryListData.csv | head -5
```

`市町村コード,市町村名,初回公開日,データ更新日` の4項目のCSV(行末に空列が2つ付く6列形式)。2026-09-19実測では 2026-09-11 更新の自治体(東京都板橋区など)があった。**回答には「この市町村のデータは○年○月更新」と更新日を添える。**

## エラー・失敗時の対応

共通の取得時チェックリストは [共通レスポンス契約](../docs/response-contract.md) の「取得時の落とし穴チェックリスト」を参照。

- **市町村ごとの個別ファイルは404**: `csv/<市町村コード>.csv` のような個別ファイルは2026-09-19実測で404(公開ページはブラウザ内でZIPを組み立てる方式)。直リンクを推測で書かず、全国ファイルをダウンロードしてgrepする。
- **座標または災害種別が不正**: 緯度は-90〜90、経度は-180〜180の範囲で指定する。未対応の災害種別は候補一覧とともに終了コード2で返す。
- **該当場所が0件**: データ取得エラーとは分けて「該当する場所が見つからない」と伝え、自治体の公式情報も確認する。
- **文字化け**: ファイルはUTF-8(BOMつき)。化けたらShift_JIS系の別データ(国土数値情報など)を掴んでいる可能性が高い。
- **国土数値情報 P20(避難施設データ)に注意**: 検索で先に出てくるが最新版は2012年度版(2013年作製)で、現在の指定状況を反映しない。避難所の検索には使わず、必ず国土地理院の上記データを使う。2026-09-19に P20-12_31_GML.zip (鳥取県) をダウンロードして内容が2013年作製であることを実測確認。

## 注意

- 指定緊急避難場所は災害種別ごとの指定。**場所の名前だけでなく、何の災害に対する指定かを必ず併記する。**
- 指定の主体は市町村長。データの更新日は国土地理院DBの更新日であり、市町村長の指定日とは異なる(公開ページの注記)。
- `lookup.py` の距離はWGS 84座標を球面上のHaversine法で計算した**直線距離の目安**。道路距離、徒歩距離、所要時間、経路の安全性を表さない。河川・崖・通行止めなどを考慮しないため、避難経路は自治体の公式案内で確認する。
- 避難の判断自体(今避難すべきか)はこのスキルの対象外。気象庁の警報等は bosai-alert、自治体の避難情報は公式発表を案内する。

## English summary

Downloads and searches Japan's official designated emergency evacuation site and shelter lists published by the Geospatial Information Authority of Japan (GSI). Two nationwide CSVs (UTF-8 with BOM): mergeFromCity_1.csv (designated shelters, ~11.7MB) and mergeFromCity_2.csv (designated emergency evacuation sites with per-hazard flags for flood, landslide, storm surge, earthquake, tsunami, fire, inland flooding, volcanic activity, ~17.0MB). GeoJSON versions exist under geoJSON/. Per-municipality update dates are in publicHistoryCSV/publicHistoryListData.csv. No API key or login. Verified live on 2026-09-19. Do NOT use the older Kokudo Suchi Joho P20 dataset (2012 edition, confirmed stale); The included `lookup.py` filters by hazard and sorts sites from the user's coordinates with the Haversine formula, returning the nearest three by default and each municipality's data update date. Its distance is straight-line distance, not walking or road distance. Always state which hazard a site is designated for and the municipality's data update date.
