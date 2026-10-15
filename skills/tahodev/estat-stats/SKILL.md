---
name: estat-stats
description: e-Stat(政府統計の総合窓口)APIで統計表の検索・メタ情報・データ取得を行う。人口、GDP、CPI、統計、調査データに対応。無料のappId(APIキー)が必要。統計表をWebサイトで見たいだけの場合はe-Statのサイトを案内する。
license: MIT
metadata:
  category: statistics
  locale: ja-JP
---

# estat-stats

e-Stat(政府統計の総合窓口)のAPI(バージョン3.0)で、統計表の検索からデータ取得までを行うスキル。総務省など各府省の公式統計3,000表以上をカバーする。

**実測日: 2026-09-13。本文のコマンド・構造は実測で確認したものを収録(個所ごとの日付は各所の記載を参照)。**

## appIdの準備(最初の1回だけ)

1. e-Statのユーザ登録ページ( https://www.e-stat.go.jp/mypage/user/preregister )で登録し、マイページからappIdを発行する(無料・即時)。
2. appIdはチャットやコード、コミットに書かない。環境変数(例: `ESTAT_APP_ID`)に入れて使う。
3. 利用には政府統計利用規約への同意が必要。取得データを使う成果物には出典(クレジット)を明記するルールがある。要件は https://www.e-stat.go.jp/api/api-info/credit を参照。

## 1. 統計表を検索する (getStatsList)

```bash
curl -s "https://api.e-stat.go.jp/rest/3.0/app/json/getStatsList?appId=${ESTAT_APP_ID}&searchWord=%E4%BA%BA%E5%8F%A3&limit=5"
```

- `searchWord`: 検索語(URLエンコードする。例の `%E4%BA%BA%E5%8F%A3` は「人口」)
- `limit`: 件数。`startPosition` でページング
- 応答の `GET_STATS_LIST.DATALIST_INF.TABLE_INF` が統計表の配列。`@id` が後続のAPIで使う統計表ID(statsDataId)。`STATISTICS_NAME`(調査名)、`TITLE.$`(表題)、`GOV_ORG.$`(所管)を見て絞る
- appIdなし・無効だと `RESULT.STATUS=100`「認証に失敗しました」のJSONが返る(HTTP 200のまま。2026-09-13実測)。**HTTPステータスではなく応答JSONの `STATUS` を見る**
- 2026-09-13に無料appIdで getStatsList/getMetaInfo/getStatsData の3連を実測(いずれも `STATUS=0`)。appIdの即時発行を確認

## 2. 表の構造を調べる (getMetaInfo)

例として `0000150002`(人口推計、総務省。2026-09-13に実キーで実測)を使う。

```bash
curl -s "https://api.e-stat.go.jp/rest/3.0/app/json/getMetaInfo?appId=${ESTAT_APP_ID}&statsDataId=0000150002"
```

- 応答の `METADATA_INF.CLASS_INF.CLASS_OBJ` に、表の軸(表章事項・分類事項・時間軸・地域)と各コード値が入る。この表の実測では `cat01`(年齢5歳階級、46コード)、`cat02`(男女別、3コード)、`cat03`(年、5コード)、`area`(全国)、`time`(時間軸) が返った
- データ取得で使う絞り込みコード(`cdArea`、`cdCat01` など)はここで得る。`@id` がパラメータ名の suffix、`CLASS` がコードと名称の一覧

## 3. データを取得する (getStatsData)

```bash
curl -s "https://api.e-stat.go.jp/rest/3.0/app/json/getStatsData?appId=${ESTAT_APP_ID}&statsDataId=0000150002&cdCat01=000&cdCat02=000&limit=5"
```

- `cdCat01=000&cdCat02=000` は getMetaInfo で得たコード(年齢総数・男女総数)による絞り込み。`cd<軸ID>=<コード>` の形式で付ける(2026-09-13実測)
- 応答の `STATISTICAL_DATA.DATA_INF.VALUE` が値の配列。`@time`(時間軸コード)、`@area`(地域コード)、`$`(値)を持つ。コードの意味は getMetaInfo の結果と突き合わせる
- 大きい表は `limit` + `startPosition` で分割取得する(次の開始位置は `RESULT_INF` の `TOTAL_NUMBER`/`FROM_NUMBER`/`TO_NUMBER` から計算する)

## エラー・失敗時の対応

共通の取得時チェックリストは [共通レスポンス契約](../docs/response-contract.md) の「取得時の落とし穴チェックリスト」を参照。

- **タイムアウトを付ける**: `curl -sm 30` のように必ず制限時間を付ける。
- **`STATUS=100` (認証エラー)**: appIdが未設定・無効。`ESTAT_APP_ID` が設定されているか確認し、「e-StatのappIdが無効な可能性があります。マイページで確認してください」と伝える。HTTPは200でもエラーなので、応答JSONの `RESULT.STATUS` を必ず見る(`0` が成功)。
- **`STATUS=1` / エラーメッセージ付き**: パラメータの誤り(存在しないstatsDataId、不正なコード値など)。`ERROR_MSG` をそのままユーザーに見せ、getMetaInfoでコードを取り直す。
- **結果が0件**: エラーではなく「条件に合う統計表・データがない」正常な結果。その旨を伝える。取得失敗と混同しない。
- **HTTP 5xx / タイムアウト**: 1〜2回だけ再試行。直らなければe-Stat側の障害の可能性として、 https://www.e-stat.go.jp/api/ のお知らせ確認を案内する。
- **短時間に大量リクエストしない**: 分割取得の間隔を空け、同一表の再取得は結果を使い回す。

## English summary

Searches and fetches Japanese government statistics via the official e-Stat API v3 (3,000+ tables: population, GDP, CPI, labor, regional data). Requires a free appId from e-Stat user registration - keep it in an environment variable, never in chat or commits. Flow: getStatsList to find a table ID, getMetaInfo to learn its axes and filter codes, getStatsData with pagination to fetch values. The API returns HTTP 200 even for auth failures (STATUS=100 in the JSON body), so always check RESULT.STATUS, not the HTTP status. Data use carries a source-citation requirement under the government's statistics terms.
