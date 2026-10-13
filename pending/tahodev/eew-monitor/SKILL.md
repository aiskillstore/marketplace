---
name: eew-monitor
description: 緊急地震速報(EEW)の発表状況と直近の地震・津波情報を、キー不要の公開APIから取得する。緊急地震速報、EEW、強震モニタ、今地震あった?に対応。気象庁の確定した発表(震度詳細・警報)はbosai-alert、天気予報はjma-weatherを使う。
license: MIT
metadata:
  category: disaster
  locale: ja-JP
---

# eew-monitor

緊急地震速報(EEW)の発表状況と、直近の地震・津波情報をリアルタイム系の公開APIから取得するスキル。APIキー・ログイン不要。

> **情報源の性質**: ここで使うAPI(P2P地震情報、wolfx)はどちらも**気象庁の電文を中継するコミュニティ運営の非公式サービス**。速報性は高いが、気象庁の公式サイトではない。確定情報の確認には `bosai-alert`(気象庁公式JSON)を使い、緊急時の判断は必ず気象庁・自治体の公式発表で行うよう案内する。

**実測日: 2026-09-13。本文のコマンド・構造は実測で確認したものを収録(個所ごとの日付は各所の記載を参照)。**

## 緊急地震速報(EEW)の発表状況を見る

```bash
curl -s https://api.wolfx.jp/jma_eew.json
```

最新のEEW電文1件がJSONで返る(2026-09-13実測)。主なフィールド:

- `Title`: 「緊急地震速報(予報)」または「緊急地震速報(警報)」
- `Issue.Status`: `通常` はそのEEWが終了(最終報)した状態。`isFinal: true` と対応する
- `EventID`: 発生時刻ベースのID (例 `20260913053312`)
- `OriginTime`: 発生時刻 / `Hypocenter`: 震源 / `Latitude`,`Longitude`,`Depth`(km)
- `Magnitude`: マグニチュード(ペイロードには誤記の `Magunitude` も同居するが `Magnitude` を使う)
- `MaxIntensity`: 最大予測震度 (例 `"2"`)
- `isWarn`: `true` なら警報(最大震度5弱以上の予測)、`false` なら予報
- `isCancel`: キャンセル報なら `true`
- `WarnArea`: 警報対象地域名の配列(予報では空)
- `AnnouncedTime` / `Serial`: 発表時刻と報数(第何報か)

**終了後も直近の電文が残る**: EEWが出ていない平時でも、最後に発表されたEEWの最終報が返る(2026-09-13に05:32発生の奄美大島北東沖M5.1の最終報を実測)。「いま発表中か」は `Issue.Status` が `通常` かどうかと `OriginTime` の新しさで判断し、「現在発表中の緊急地震速報はありません(最終報: ○時○分発生 奄美大島北東沖 M5.1)」のように伝える。

## 直近の地震情報(P2P地震情報 API v2)

```bash
# 最新の地震情報(震源・震度の詳細)を5件
curl -s "https://api.p2pquake.net/v2/history?codes=551&limit=5"

# 気象庁発表の最新の地震情報1件
curl -s "https://api.p2pquake.net/v2/jma/quake?limit=1"

# 気象庁発表の最新の津波予報1件
curl -s "https://api.p2pquake.net/v2/jma/tsunami?limit=1"
```

すべて2026-09-13実測。`codes=551` は地震情報、`552` は津波予報。主なフィールド:

- `earthquake.time` / `hypocenter.name,magnitude,depth,latitude,longitude`: 発生時刻と震源
- `earthquake.maxScale`: 最大震度。`震度×10` の数値(例 `20`=震度2、2026-09-13実測)。仕様上 `45`=5弱、`50`=5強、`55`=6弱、`60`=6強、`70`=7
- `earthquake.domesticTsunami`: `None`(津波のおそれなし)など
- `points[]`: 観測点ごとの `addr`(地点名)、`pref`(都道府県)、`scale`
- `issue.type`: `DetailScale`(震源・震度詳細)などの情報種別

履歴は最大100件程度しか遡れない。期間指定の検索や確定情報の網羅的な一覧は気象庁側(`bosai-alert`)で行う。

## 強震モニタについて

強震モニタ(約700観測点のリアルタイム震度)は、気象庁の公式ページ https://www.kyoshin.bosai.go.jp/ でブラウザから見るのが確実。観測点ごとの数値をcurlで安定取得する公式の無償APIは確認できなかったため(2026-09-13にkmoni webserviceへの接続を試行するも応答なし)、このスキルでは扱わない。ブラウザ確認を案内する。

## 注意

- **緊急時の判断に使わない**: EEW系の非公式APIは遅延・欠損しうる。「EEWが返ってこない=安全」ではない。身を守る行動は気象庁・NHK・自治体の発表で判断するよう必ず添える。
- 短時間に連続リクエストしない。非公式サービスは個人・コミュニティの運営で、高頻度アクセスは運営を圧迫する。
- 引用時は発表時刻(`OriginTime`/`issue.time`)を必ず併記する。

## エラー・失敗時の対応

共通の取得時チェックリストは [共通レスポンス契約](../docs/response-contract.md) の「取得時の落とし穴チェックリスト」を参照。

- **タイムアウトを付ける**: `curl -sm 30` のように必ず制限時間を付ける。
- **HTTP 5xx / タイムアウト**: 非公式サービス側の障害の可能性。1〜2回だけ再試行し、直らなければ「速報系APIが応答していません」と明示したうえで、気象庁の防災情報ページ https://www.jma.go.jp/bosai/map.html と強震モニタ https://www.kyoshin.bosai.go.jp/ の直接確認を案内する。失敗を「EEWなし」とは絶対に言わない。
- **`[]` や古い最終報はエラーではない**: P2Pの履歴で `[]` が返る場合は対象コードの情報が期間内にない正常な結果。wolfxで古い最終報が返るのは平時の正常な状態。
- **フィールド欠損**: 第1報などでは `MaxIntensity` や `WarnArea` が空のことがある。欠損を0や「被害なし」と読み替えず、「まだ入っていない項目」として伝える。

## English summary

Checks live Earthquake Early Warning (EEW) status and recent quake/tsunami bulletins via keyless community-run relays of JMA telegrams: api.wolfx.jp for the latest EEW telegram and api.p2pquake.net (P2P Quake API v2) for quake history and tsunami bulletins. Both are unofficial relays, not JMA itself - always point users to official JMA/local-government announcements for decisions, and use the sibling bosai-alert skill for confirmed JMA publications. A stale final EEW telegram or an empty history array is normal quiet-time state, never an error; an unreachable API is never "no warning".
