---
name: zipcode-lookup
description: 日本郵便の公式データで郵便番号と住所を相互検索する。郵便番号、〒、住所から郵便番号、郵便番号から住所、町域の検索に対応。公式CSVをダウンロードしてローカル検索するのでAPIキー・ログイン不要。宛名印刷・配送・ゆうびんID変換は対象外。
license: MIT
metadata:
  category: address
  locale: ja-JP
---

# zipcode-lookup

日本郵便が公開する郵便番号データ(UTF-8版 KEN_ALL)をダウンロードして、郵便番号⇄住所をローカル検索するスキル。APIキー不要。約12万件の全データを手元に持つので、件数制限なく繰り返し検索できる。

**実測日: 2026-09-12。本文のコマンド・構造は実測で確認したものを収録(個所ごとの日付は各所の記載を参照)。**

## 基本の流れ

### 1. データをダウンロードする

ダウンロードページはここ(2026-09-11にページ構造を確認):

```bash
curl -sm 30 -L -o utf-zip.html https://www.post.japanpost.jp/zipcode/dl/utf-zip.html
```

ページ内の「全国一括」のリンク(2026-09-11時点で `utf/zip/utf_ken_all.zip`)を取り出してダウンロードする。

```bash
href=$(grep -oE 'utf/zip/utf_ken_all\.zip' utf-zip.html | head -1)
curl -sm 120 -L -o utf_ken_all.zip "https://www.post.japanpost.jp/zipcode/dl/${href}"
unzip -o utf_ken_all.zip   # KEN_ALL.CSV (UTF-8) が出てくる
```

**直リンクを推測で書かない。** 必ずページを経由して、そのとき記載されているリンクを使う。

**データセンター系IPからはzipをダウンロードできない(重要)。** 2026-09-11と2026-09-12の実測では、データセンター系IPからのアクセスではzipが(ページから取り出した正規リンク・ブラウザ相当のUser-Agentでも)すべて404を返した。ダウンロードページ自体は200で見えるので「ページは開けるのにzipだけ404」なら、このIP制限にかかっている可能性が高い。クラウド上のエージェント実行環境はだいたいデータセンターIPなので、この環境ではダウンロード自体が成立しないことに注意。その場合の代替:

1. ユーザーに自分のPC(住宅回線)で `utf_ken_all.zip` をダウンロードしてもらい、ファイルを渡してもらう。
2. ユーザー側のマシンでこのスキルの手順を実行してもらう。
3. どちらも無理なら「この実行環境のIPからは日本郵便のデータを取得できない」と明示し、推測の値を答えない。

差分だけ欲しい場合は、同じページに「更新データ(追加・廃止・変更)」の月次zipがある。

### 2. 検索する

```bash
# 郵便番号 → 住所 (ハイフンなし7桁で検索)
grep '"1000001",' KEN_ALL.CSV   # 千代田区千代田(皇居)

# 住所 → 郵便番号 (部分一致)
grep '丸の内' KEN_ALL.CSV
```

## 読み方(CSVの列)

1行15列。文字列フィールドはすべてダブルクォートで囲まれている(郵便番号は `"1000001"` の形)。主要な列は: 1列目=全国地方公共団体コード、3列目=郵便番号(7桁)、7列目=都道府県名、8列目=市区町村名、9列目=町域名(4〜6列目はそれぞれのカナ表記)。

- 町域名が「以下に掲載がない場合」の行は、その市区町村で町域の記載がない地域すべてに対応する。
- 1つの郵便番号に複数行(複数町域)が対応することがある。最初の1行で打ち切らず、該当行をすべて返す。

## 更新サイクル

郵便番号データは月次で更新される(月末に当月分が公開)。検索のたびに取り直す必要はないが、「何月分のデータか」をユーザーに伝えられるように、ダウンロード日を控えておく。古いデータで廃止・変更された番号を案内しないよう、月1回程度は取り直す。

## エラー・失敗時の対応

共通の取得時チェックリストは [共通レスポンス契約](../docs/response-contract.md) の「取得時の落とし穴チェックリスト」を参照。

- **zipが404/403/タイムアウト**: 推測したURLを叩いていないか確認し、ダウンロードページからリンクを取り直す。ページは開けるのにzipだけ404が続くなら上記のデータセンターIP制限の可能性が高い。代替手順(ユーザー側でのダウンロード)を案内し、それでも駄目なら「日本郵便のサイトからデータを取得できなかった」と明示してページのURLを案内する。
- **住所が見つからない**: 町域名は郵便事業上の表記で、住居表示と異なることがある。丁目・番地を削って町域名の部分一致で探し直す。大字・小字はデータに含まれないことがある。
- **文字化け**: UTF-8版を使っている限り化けない。もし文字化けするならJIS版(`ken_all.zip`、Shift_JIS)を落としている可能性が高い。UTF-8版を取り直す。

## 注意

- 返す住所は郵便番号のための公式表記であり、住居表示・登記上の表記と一致しないことがある。「郵便番号データ上の表記」であることを必要に応じて伝える。
- データの基準日(何月分か)を添えて答える。

## English summary

Look up Japanese postal codes and addresses both ways using Japan Post's official KEN_ALL dataset (UTF-8 edition). No API key or login: download the national zip from the official download page and search locally. Never guess the zip's direct URL - datacenter IPs were served 404s for direct zip links on 2026-09-11 while the page itself returned 200; always extract the current link from the page. Data is updated monthly; tell the user which month's dataset you searched. Address spellings are Japan Post's postal notation, which can differ from residential addressing.
