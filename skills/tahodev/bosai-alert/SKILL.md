---
name: bosai-alert
description: 気象庁の防災情報(地震速報・震度詳細、気象警報・注意報、津波情報)を公開JSONから取得する。地震、震度、警報、注意報、津波の確認に対応。APIキー・ログイン不要。ふだんの天気予報は対象外(jma-weatherを使う)。
license: MIT
metadata:
  category: disaster
  locale: ja-JP
---

# bosai-alert

気象庁の防災情報を公開JSONから取得するスキル。地震の速報と詳細、地域ごとの警報・注意報、津波情報をカバーする。APIキー不要。

**実測日: 2026-09-12。本文のコマンド・構造は実測で確認したものを収録(個所ごとの日付は各所の記載を参照)。**

## 地震情報

### 最新の地震一覧

```bash
curl -s https://www.jma.go.jp/bosai/quake/data/list.json
```

直近の地震イベントの配列。主なフィールド:

- `at`: 発生時刻 (ISO 8601)
- `anm`: 震源地名 (`en_anm` は英語表記)
- `mag`: マグニチュード
- `maxi`: 最大震度 (例: "3", "5-", "6+")
- `ttl`: 情報の種類 (震源・震度情報 など)
- `json`: 詳細JSONのファイル名(下記)

### 地震の詳細

一覧の `json` フィールドをそのまま使う。

```bash
# 下のURLは実際の発表をもとにした歴史的な例(2026-09-08 23:40発表分)
curl -s https://www.jma.go.jp/bosai/quake/data/20260908234330_20260908234052_VXSE5k_1.json
```

> **このURLは期限切れの歴史的な例**: 気象庁の個別JSONは発表から数日で公開終了となり404になる。実際に使うときは、直前の一覧取得で得た最新の `json` フィールドの値に置き換えること。期限切れが前提のURLなので、CIのURLチェックでは `scripts/check-urls.sh` の `EXCLUDE_URLS` で除外済み。

構造: `Control` (発表情報) と `Body` (震源、震度観測点のリストなど)。`Body.Intensity.Observation` に地域ごとの震度が入る。

## 気象警報・注意報

```bash
curl -s https://www.jma.go.jp/bosai/warning/data/warning/130000.json
```

`130000` は `offices` コード (気象庁エリア定義 `https://www.jma.go.jp/bosai/common/const/area.json` を参照)。

- `headlineText`: 見出し文
- `areaTypes[].areas[].warnings`: 地域ごとの警報・注意報。`code` と `status` (発表/継続/解除) を持つ。
- 新しい発表がない期間は、過去の発表がそのまま残ることがある(2026-09-12に `reportDatetime` が数か月前の応答を実測)。`reportDatetime` が古い場合は「最新の発表ではなく過去の発表が残っている可能性」を添えて伝え、発表時刻を必ず併記する。

## 津波情報

```bash
curl -s https://www.jma.go.jp/bosai/tsunami/data/list.json
```

発表中の津波情報一覧。空配列 `[]` なら現在発表なし。

## 注意

- 緊急時はこのスキルの結果だけで判断せず、気象庁・自治体の公式発表を確認するよう案内する。
- データは発表のたびに更新される。引用時は発表時刻を一緒に伝える。
- 短時間に連続リクエストしない。

## エラー・失敗時の対応

共通の取得時チェックリストは [共通レスポンス契約](../docs/response-contract.md) の「取得時の落とし穴チェックリスト」を参照。

- **タイムアウトを付ける**: `curl -sm 30` のように必ず制限時間を付ける。
- **空配列 `[]` はエラーではない**: 津波情報の list.json などで `[]` が返るのは「現在発表中の情報がない」という正常な結果。「津波情報は現在発表されていません」と伝える。HTTPエラーやタイムアウト(取得自体の失敗)と混同しない。
- **HTTP 404**: `offices` コードの間違いが原因になりやすい。`https://www.jma.go.jp/bosai/common/const/area.json` でコードを確認する。
- **HTTP 5xx / タイムアウト**: 1〜2回だけ再試行。直らなければ取得失敗であることを明示し、「気象庁の防災情報ページ https://www.jma.go.jp/bosai/map.html を直接確認してください」と案内する。失敗を「情報なし」とは絶対に言わない。
- **詳細JSONのURL**: 一覧の `json` フィールドをそのまま使う。ファイル名を自分で組み立てると404になりやすい。

## English summary

Fetches JMA disaster information: the latest earthquake list and per-quake details, weather warnings/advisories by area, and active tsunami information. No API key or login required. The detail JSON filename comes from the list's `json` field - never build the URL yourself. An empty array means "nothing currently in effect", not an error. In an emergency, always point the user to official JMA and local-government announcements.
