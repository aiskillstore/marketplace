---
name: ndl-books
description: 国立国会図書館サーチ(NDL Search)の公式API(OpenSearch / SRU)で書誌を検索する。ISBN・タイトル・著者名・任意キーワードでの検索に対応し、タイトル(読み)・著者・出版社・刊行年・資料種別(紙/電子)・書誌IDを返す。APIキー・ログイン不要。図書館の蔵書・貸出状況はcalil-books、全文が読める青空文庫はaozora(採用予定)を使う。購入・書評・在庫(書店)は対象外。
license: MIT
metadata:
  category: books
  locale: ja-JP
---

# ndl-books

国立国会図書館サーチの公式APIで、日本のほぼ全ての刊行物の書誌(どんな本が存在するか)を検索するスキル。APIキー・ログイン・ユーザー登録は不要。国立国会図書館はユーザー登録なしで機械可読な書誌データを公開している。

**実測日: 2026-09-29。以下のURL・構造・件数はすべて当日の実測で確認。**

蔵書(どの図書館に実物があるか・貸出中か)はカーリルAPIの `calil-books` を使う。こちらは「存在する本の書誌」専用。

## エンドポイント

| API | URL | 形式 |
| --- | --- | --- |
| OpenSearch | `https://ndlsearch.ndl.go.jp/api/opensearch` | RSS 2.0 (XML) |
| SRU | `https://ndlsearch.ndl.go.jp/api/sru` (`operation=searchRetrieve`) | SRU (XML) |

旧ホスト `iss.ndl.go.jp` は **303 で `ndlsearch.ndl.go.jp` にリダイレクトされる**(2026-09-29実測)。古い手順記事は iss.ndl.go.jp のままのものが多い。今はリダイレクトで動くが、新しい方を直接使う。

## 使い方(ヘルパー)

```bash
python3 ndl-books/lookup.py --isbn 9784101010014
python3 ndl-books/lookup.py --title 雪国 --mediatype books --cnt 5
python3 ndl-books/lookup.py --creator 夏目漱石
python3 ndl-books/lookup.py --keyword 東京 防災
```

JSONで `{total, count, items[]}` を返す。items の各要素は `title` / `title_yomi`(タイトル読み) / `creator` / `creator_yomi` / `publisher` / `date` / `isbn` / `bib_id`(国立国会図書館書誌ID) / `material`(紙・電子など) / `link`(NDL Searchの書誌ページ)。

curl で直接読む場合:

```bash
curl -s "https://ndlsearch.ndl.go.jp/api/opensearch?isbn=9784101010014"
```

## 実測で確認した罠

1. **タイトル検索は部分一致。** `title=雪国` は 2026-09-29 実測で 7,719件。「ああ、大ゼキよ : 雪国」のような本も混ざる。`mediatype=books` を付けると 1,767件に絞れる。件数を見てから `cnt` と `idx` でページングする。
2. **1つのISBNに複数レコードが返る。** 9784101010014 (吾輩は猫である) は4件(2026-09-29実測)。紙・電子・改版など別レコードとして存在する。`material`(紙/電子)と `date` を見て選ぶ。
3. **ページングの既定は200件。** `cnt` を省略すると itemsPerPage=200 で返る(指定は1〜200)。大きなXMLを黙って受け取らないよう、必要なら `cnt` を小さく指定する。
4. **著者名は「姓, 名」形式。** `夏目, 漱石` のように姓と名の間がカンマ+空白。読みは `creatorTranscription` (ナツメ, ソウセキ) に入る。
5. **ISBNはハイフンなしで渡す。** ヘルパーはハイフンを除去するが、直接叩くときは `9784101010014` のように13桁(または10桁)の連続数字。
6. **応答の pubDate は刊行日ではない。** item の `pubDate` はレコードの更新日時。刊行年は `dc:date` / `dcterms:issued` を見る。

## SRU を使う場面

OpenSearch はパラメータ直指定(isbn/title/creator/any)だが、SRU は CQL クエリで柔軟に組める。

```bash
curl -s 'https://ndlsearch.ndl.go.jp/api/sru?operation=searchRetrieve&query=isbn%3D%229784101010014%22&maximumRecords=2'
```

`numberOfRecords` が件数。OpenSearchと同じ4件が返ることを2026-09-29に実測。複雑な条件(資料種別・年代の組合せ)が必要なときだけこちら。

## 失敗時の対応

- **空の応答(0件):** キーワードの表記(漢字/かな/カナ)を変えて再試行。書誌は存在するのに表記ゆれで0件になることがある。ISBNなら10桁↔13桁を両方試す。
- **接続エラー・5xx:** NDL Search のメンテナンス(毎週火曜夜間の予定メンテあり)の可能性。時間を置いて再試行。旧ホスト iss.ndl.go.jp 経由で叩いている場合は新ホストに切り替える。
- **XMLのパース失敗:** `&` を含むタイトルを手でURLに埋め込むとクエリが壊れる。必ずURLエンコードする(ヘルパーは自動で行う)。

## English summary

Searches the National Diet Library (NDL) Search API for bibliographic records of Japanese publications — no API key or login. Supports ISBN, title (partial match), creator, and free-keyword queries via the OpenSearch endpoint (RSS/XML), with SRU/CQL available for complex queries. Returns title (with kana reading), author, publisher, year, ISBN, NDL bib ID, material type (paper/electronic), and a link to the record. For library holdings and availability, use calil-books instead. Measured against the live API on 2026-09-29.
