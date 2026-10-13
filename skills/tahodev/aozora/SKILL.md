---
name: aozora
description: 青空文庫の全作品カタログ(公式公開CSV)で著作権切れの文学作品を検索し、本文をプレーンテキストで取得する。タイトル部分一致・著者名・作品IDでの検索に対応し、作品ID・タイトル(読み)・著者・文字遣い種別・著作権フラグ・初出・図書カードURLを返す。APIキー・ログイン不要。書誌の網羅検索はndl-books、図書館の蔵書はcalil-booksを使う。現行の書籍の購入・在庫は対象外。
license: MIT
metadata:
  category: books
  locale: ja-JP
---

# aozora

青空文庫(著作権の切れた文学作品を無償公開する電子図書館)の公式カタログCSVと図書カードを読み、作品検索と本文取得を行うスキル。公式APIは存在しないが、全作品の一覧がCSVで公開されており、APIキー・ログイン・ユーザー登録は一切不要。

**実測日: 2026-09-30。以下のURL・構造・件数はすべて当日の実測で確認。**

青空文庫は「存在する本の書誌」ではなく「今すぐ全文読める本文」を提供する。書誌の網羅検索は `ndl-books`、図書館の蔵書は `calil-books` と棲み分ける。

## データソース

| データ | URL | 形式 |
| --- | --- | --- |
| 全作品一覧(拡張) | `https://www.aozora.gr.jp/index_pages/list_person_all_extended_utf8.zip` | zip内CSV (UTF-8, BOM付き) |
| 図書カード | `https://www.aozora.gr.jp/cards/{person_id}/card{work_id}.html` | HTML (UTF-8) |
| 本文(XHTML) | カードページ内のリンク `files/{work_id}_{serial}.html` | XHTML (**Shift_JIS**) |

## 使い方(ヘルパー)

```bash
python3 aozora/lookup.py --title 吾輩は猫である      # タイトル部分一致
python3 aozora/lookup.py --author 夏目漱石           # 著者の作品一覧
python3 aozora/lookup.py --work-id 000789            # カードのリンク一覧
python3 aozora/lookup.py --text 000789 --max-chars 500  # 本文をテキスト抽出
python3 aozora/lookup.py --stats                     # カタログ件数サマリ
```

ヘルパーはCSVを `~/.cache/aozora/` に24時間キャッシュする(2.1MBのzipを毎回取りに行かない)。

## 実測で確認したこと (2026-09-30)

- 拡張CSV: zip 2,092,746バイト、19,502行。**distinct作品は17,840、人物は1,335**。著作権フラグ「あり」の作品が928件混ざっている(著作者の許諾を得て公開中のもの。`--stats` で確認できる)。
- 著者別の作品数1位は夏目漱石(113)でも太宰治(274)でもなく**宮本百合子(1,186)**。2位は岸田国士(641)。
- 文字遣い種別の内訳: 新字新仮名 12,130行 / 新字旧仮名 4,856 / 旧字旧仮名 2,377 / 旧字新仮名 109 / その他 30。
- 2026年に公開された作品は71件。最終更新は2026-08-20のスナップショット(zipのLast-Modified 2026-08-21)。**一覧はリアルタイムではなく不定期更新のスナップショット**。

## 実測で確認した罠

1. **本文URLは作品IDから推測できない。** `card789.html` の本文は `files/789_14547.html` — 後ろの通し番号は作品IDと無関係。必ず図書カードのHTMLを取りに行って `files/` リンクを拾う(ヘルパーがやる)。
2. **文字コードがページで違う。** 図書カードはUTF-8、本文XHTMLは**Shift_JIS**。ヘッダのcharsetを見て切り替える(ヘルパーは自動判定)。
3. **CSVはBOM付きUTF-8。** 素の `utf-8` で読むと先頭列名にBOMが混入する。`utf-8-sig` で読む。
4. **1作品=複数行。** 翻訳物は著者+翻訳者で2行になる(ウェストミンスター寺院=アーヴィング著/高津春繁訳)。行数(19,502)は作品数(17,840)ではない。作品単位で数えるときは作品IDで畳む。
5. **ルビは `<ruby><rb><rt><rp>` 構造。** テキスト化するときは `<rt>`(読み)と `<rp>`(括弧)を要素ごと落とさないと「吾輩（）は猫である」のように空の括弧が残る。

## 失敗時の対応

- **作品が見つからない:** タイトルは正確な表記(旧字体・旧仮名遣いのまま登録されている場合あり)。著者検索は「夏目漱石」のように姓名をスペースなしで連結する。CSVが古い可能性があるのでキャッシュを削除して再取得する(`rm -rf ~/.cache/aozora`)。
- **文字化け:** 本文を直接 `curl` した場合、ターミナルがUTF-8だと文字化けする。Shift_JISなので `iconv -f shift_jis -t utf-8` を通すか、ヘルパーの `--text` を使う。
- **取得したHTMLに本文がない:** 青空文庫には図書カードがあっても本文未入力(入力中)の作品がある。カードの「本文」リンクの有無で判断する。

## English summary

Searches Aozora Bunko (Japan's public-domain digital library) using its official full-catalog CSV — no API key or login. Finds works by title (partial match) or author, then fetches the book-card page to locate the full text (the text URL contains a serial number that cannot be derived from the work ID). Extracts plain text from the Shift_JIS XHTML, stripping ruby annotations (keeps base characters only). Returns work ID, title (with kana reading), author, orthography type, copyright flag, first-publication info, and card URL. The catalog is a snapshot (19,502 rows / 17,840 works / 1,335 persons as of 2026-08-21, measured 2026-09-30), not a live API. For exhaustive bibliography use ndl-books; for library holdings use calil-books.
