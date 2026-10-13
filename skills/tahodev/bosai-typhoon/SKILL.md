---
name: bosai-typhoon
description: 気象庁の台風情報JSONで現在発生中の台風の有無と情報を確認する。台風、台風何号、台風接近、進路の質問に対応。APIキー・ログイン不要。地震・津波・気象警報はbosai-alert、天気予報はjma-weather、雨雲はamagumoを使う。
license: MIT
metadata:
  category: disaster
  locale: ja-JP
---

# bosai-typhoon

気象庁の台風情報JSONを読み、現在発生中の台風情報の有無を確認するスキル。気象庁はユーザー登録なしで機械可読な気象・防災データを公開している。APIキー不要。

**実測日: 2026-09-11。本文のコマンド・構造は実測で確認したものを収録(個所ごとの日付は各所の記載を参照)。**

## 基本の流れ

```bash
curl -sm 30 -w '\nHTTP %{http_code}\n' https://www.jma.go.jp/bosai/typhoon/data/list.json
```

**HTTPステータスで状態を判断する:**

- **200で配列が返る** → 発生中の台風情報がある。内容を読んで伝える。
- **404** → 現在発生中の台風情報はない。2026-09-11の実測では、台風非発生時にこのURLは404を返した。これは異常ではなく平時の正常な状態。
- **それ以外(5xx、タイムアウト、空)** → 取得失敗。1〜2回リトライし、駄目なら失敗と明示する。

404をエラーとしてリトライしてはいけない。逆に、本当の取得失敗を「台風はいない」と報告してもいけない(bosai-alertと同じ原則: 「ない」と「取れない」は別の意味)。

## 発生時の詳細データについて

台風発生時のlist.jsonの各要素・詳細JSONのフィールド構成は、**本スキルの収録時点(2026-09-11)では台風が発生しておらず実測できていない**。kurashi-skillは実際に動かして確認したものだけを記録する方針(CONTRIBUTING.mdの実測主義)なので、フィールド名を推測で書いていない。次に台風が発生したときに実測して追記する。あわせて、list.json が番号の付かない熱帯低気圧(TD)を含むのか番号付き台風のみなのかも未確認なので、その時に確認する。発生時は、人間向けの確認として気象庁の防災情報ページ(https://www.jma.go.jp/bosai/map.html)を併せて案内する。

## エラー・失敗時の対応

共通の取得時チェックリストは [共通レスポンス契約](../docs/response-contract.md) の「取得時の落とし穴チェックリスト」を参照。

- **404**: エラーではない。「現在発生中の台風情報はない」と伝えられる正常な応答。
- **取得失敗を「台風なし」と言わない**: ステータスコードで区別する。取れなければ「取得できなかった」と明言し、map.htmlを案内する。
- **curlにはタイムアウトを付ける**(`-sm 30`)。応答がないまま待ち続けない。

## 注意

- 台風情報は命に関わる。接近・影響の判断はこのスキルの結果だけで行わず、気象庁・自治体の公式発表を確認するよう必ず添える。
- 確認時刻を一緒に伝える(「○時○分時点では発生中の台風情報はなかった」)。台風はいつ発生するかわからない。

## English summary

Checks JMA's typhoon JSON feed for currently active typhoon information. No API key or login. The key behavior is status-code driven: HTTP 200 with an array means active typhoon data exists; HTTP 404 means no active typhoon - that is the normal quiet-time state (verified 2026-09-11), not an error to retry; anything else is a fetch failure and must be reported as such, never as "no typhoon". Field-level detail of the active-typhoon payload is intentionally undocumented because no typhoon was active at collection time (the repo records only what was actually run and verified). Always attach the check time and point to official JMA announcements for safety decisions.
