---
name: volcano
description: 気象庁の火山情報(噴火速報・噴火警報/噴火警戒レベル・火山の状況に関する解説情報)を公開JSONから取得する。火山、噴火、噴火警戒レベル、噴火速報の確認に対応。APIキー・ログイン不要。地震・津波はbosai-alert、気象警報はbosai-alertを使う。
license: MIT
metadata:
  category: disaster
  locale: ja-JP
---

# volcano

気象庁の防災情報サイトが公開する火山関連JSONから、噴火速報・噴火警報(噴火警戒レベル)・解説情報を取得するスキル。APIキー・ログイン不要。

**実測日: 2026-09-19。以下のcurl・構造はすべて当日の実測で確認。**

## エンドポイント一覧

| 内容 | URL |
| --- | --- |
| 噴火速報 | `https://www.jma.go.jp/bosai/volcano/data/eruption.json` |
| 噴火警報・予報(噴火警戒レベル) | `https://www.jma.go.jp/bosai/volcano/data/warning.json` |
| 火山の状況に関する解説情報 | `https://www.jma.go.jp/bosai/volcano/data/info.json` |
| 火山マスタ(コード・名前・緯度経度) | `https://www.jma.go.jp/bosai/volcano/const/volcano_list.json` |

## 基本の流れ

### 1. 噴火速報の有無を見る

```bash
curl -s https://www.jma.go.jp/bosai/volcano/data/eruption.json
```

噴火速報が出ていない平常時は空配列 `[]` が返る(2026-09-19実測)。**空配列はエラーではなく「現在発表中の噴火速報はない」という意味**。要素がある場合は `reportDatetime` と `eventId`(火山コード)を見る。

### 2. 噴火警報・噴火警戒レベルを見る

```bash
curl -s https://www.jma.go.jp/bosai/volcano/data/warning.json
```

発表中の噴火警報・予報の配列。読み方:

- `eventId`: 火山コード。`volcano_list.json` の `code` と一致させると火山名(`name_jp` / `name_en`)が引ける。
- `volcanoInfos[].items[].name`: 「レベル２（火口周辺規制）」「レベル３（入山規制）」のような警戒レベル文字列、または「火口周辺危険」等のキーワード。
- `volcanoInfos[].items[].condition`: 「継続」「切替」など(2026-09-19にwarning.jsonの実データで存在を確認)。

2026-09-19実測の例: 阿蘇山(503)がレベル２、十勝岳(108)がレベル３で発表中だった。

**注意: 解除されず残っている古い発表が混ざる。** 硫黄島(329)の2007-12-01発表分が2026-09-19現在も配列に残っていることを実測。回答には必ず `reportDatetime` を併記し、「その時点の発表が継続中」であることを伝える。新しい順に並んでいるとは限らないので `reportDatetime` でソートする。

### 3. 解説情報を見る

```bash
curl -s https://www.jma.go.jp/bosai/volcano/data/info.json
```

「火山の状況に関する解説情報」の一覧。`headTitle`(見出し)、`reportDatetime`、`eventId`、`within24` / `within120`(24時間/120時間以内の発表か)を持つ。定期発表なので活動が活発な火山ほど頻繁に現れる。

### 4. 火山名を引く

```bash
curl -s https://www.jma.go.jp/bosai/volcano/const/volcano_list.json
```

`code`・`name_jp`・`name_en`・`latlon` の一覧。`eventId` との突き合わせに使う。

## エラー・失敗時の対応

共通の取得時チェックリストは [共通レスポンス契約](../docs/response-contract.md) の「取得時の落とし穴チェックリスト」を参照。

- **空配列 `[]`**: エラーではなく発表なし。「現在発表中の情報はありません」と根拠(空配列)を添えて伝える。
- **404が返るパスがある**: `data/list.json`・`data/marinevolcano.json` は2026-09-19実測で404。これらを直打ちするURLを推測で書かない。使うのは上の表の4本だけ。
- **5xxやタイムアウト**: 気象庁サイト側の一時障害の可能性。時間をおいて再試行し、取れない間は「気象庁のデータにアクセスできない」と明示して推測で答えない。

## 注意

- 噴火警戒レベルの意味(レベル1=留意 〜 レベル5=避難)は気象庁の解説に従う。レベル文字列は `items[].name` に全角で入る(例: 「レベル３（入山規制）」)。
- 噴火警報の対象が「居住地域に及ぶ」(レベル3以上)のか「火口周辺」のものかを区別して伝える。
- 海底火山の情報(`marinevolcano.json`)は2026-09-19時点で公開JSONが存在しない(404)。海底火山を聞かれたら「このスキルの対象外」と明示する。

## English summary

Fetches JMA volcano information from the public bosai JSON endpoints: eruption bulletins (eruption.json, empty array = none currently issued), eruption warnings and alert levels (warning.json), volcano commentary (info.json), and the volcano master list (const/volcano_list.json). No API key or login. Verified live on 2026-09-19. Caveats: unrescinded warnings persist in warning.json (a 2007 Ioto entry is still present), so always quote reportDatetime; empty arrays mean "no active bulletins", not errors; marinevolcano.json does not exist (404 as of 2026-09-19) - out of scope.
