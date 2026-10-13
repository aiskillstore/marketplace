---
name: garbage-day
description: 5374(ゴミナシ)形式の公開データと自治体公式のオープンデータで、ごみの収集日と品目別の分別・出し方を調べる。ごみの日、収集日、燃えるごみ、資源ごみの曜日、乾電池・スプレー缶など品目ごとの分別に対応。対象外の自治体や最新ルールの確証が必要な場合は、自治体の公式案内を案内する。
license: MIT
metadata:
  category: living
  locale: ja-JP
---

# garbage-day

2つのことを調べるスキル。APIキー・ログイン不要。

1. **収集日**: 5374.jp 形式(Code for Kanazawa発のオープンソース)で公開されている自治体の収集日データを読み、地区・ごみの種類ごとの収集曜日を答える
2. **品目別の分別・出し方**: 同じ5374の `target.csv` と、自治体公式の品目別オープンデータ(多摩市・横浜市など)を読み、「この品物は何ごみ?」を答える

> **データの性質**: 5374のデータはシビックテックのボランティアが自治体の公表情報をもとにCSV化したもので、自治体公式の配信ではない。収集日も分別ルールも変わることがあるため、引っ越し直後や祝日・年末年始の確認など確実性が必要な場面では、自治体の公式案内もあわせて確認するよう案内する。

**実測日: 2026-09-19。本文のコマンド・構造は実測で確認したものを収録(個所ごとの日付は各所の記載を参照)。**

## 5374形式のデータ構造

各地域の5374サイトは `data/` ディレクトリのCSV5本で動く(2026-09-13に codeforkanazawa-org/5374 の LOCALIZE.md と実データで確認):

- `area_days.csv`: **収集日の本体**。地区名、センター名、3列目以降にごみのカテゴリ(燃やすごみ、資源など)ごとの収集曜日
- `target.csv`: **品目別の本体**。カテゴリ別の品目一覧(「この品物は何ごみ?」を引く表)。列構成は自治体で違う(下記)
- `description.csv`: カテゴリの説明(袋の指定など)
- `center.csv`: 収集センターの休止期間(年末年始など)
- `remarks.csv`: 注意事項

### 収集曜日の書式(area_days.csv)

- `月 木` … 毎週月曜と木曜(半角スペース区切り)
- `月1` … 毎月第1月曜。`水2 水4` なら第2・第4水曜
- `20140301 20140325` … 不定期な日付の直接指定(YYYYMMDD)

実例(金沢市の `area_days.csv` 先頭、2026-09-13実測):

```csv
校下・地区,センター,燃やすごみ,燃やさないごみ,資源,あきびん
浅野川,東部管理センター,月 木,水4,火1 火3 火5,水2
```

### 品目別の書式(target.csv)

列は `分別区分,品目名,注意点,ふりがな頭文字` の4列が基本だが、1列目のヘッダ名とカテゴリ表記は自治体で違う。引く前に必ず1行目を読む(2026-09-19実測):

- 金沢市・大分市(後述の理由で実質金沢データ): `type,name,notice,furigana`
- 美唄市・松前町・笠間市・上砂川町: `label,name,notice,furigana`
- 笠間市は分別区分が「資源・有害」のように複合名で、notice列に `資源／` `有害／` の内訳が入る

実例(金沢市の `target.csv` から乾電池・スプレー缶を引いた結果、2026-09-19実測):

```csv
資源,カセットボンベ(スプレー),使い切って火気のない屋外で穴をあける,か
資源,缶(スプレー)スプレー缶,スプレー缶 使い切って火気のない屋外で穴をあける,か
資源,乾電池(水銀),,か
```

## 公開データがある自治体(2026-09-19実測で到達確認)

GitHub上の raw CSV を直接読める。ブランチ名は自治体で異なる。

```bash
# 金沢市 (Code for Kanazawa 本家)
curl -s https://raw.githubusercontent.com/codeforkanazawa-org/5374/kanazawa/data/area_days.csv

# 美唄市(北海道)
curl -s https://raw.githubusercontent.com/govtech-bibai/5374-bibai/master/data/area_days.csv

# 松前町(北海道)
curl -s https://raw.githubusercontent.com/matsumaetown/5374/master/data/area_days.csv

# 笠間市(茨城県)
curl -s https://raw.githubusercontent.com/cfkasama/5374/master/data/area_days.csv

# 上砂川町(北海道)
curl -s https://raw.githubusercontent.com/Kamisunagawa-town/5374/master/data/area_days.csv
```

`area_days.csv` を `target.csv` に変えれば品目別表が取れる。

使い方の例:

```bash
# 金沢市で「浅野川」地区の収集日を引く
curl -s https://raw.githubusercontent.com/codeforkanazawa-org/5374/kanazawa/data/area_days.csv | grep '^浅野川,'
# -> 浅野川,東部管理センター,月 木,水4,火1 火3 火5,水2
#    = 燃やすごみ: 毎週月・木、燃やさないごみ: 第4水曜、資源: 第1・3・5火曜、あきびん: 第2水曜

# 金沢市で「乾電池」の分別を引く
curl -s https://raw.githubusercontent.com/codeforkanazawa-org/5374/kanazawa/data/target.csv | grep '乾電池'
# -> 資源,乾電池(水銀),,か
#    = 資源(水銀を含むもの)として出す
```

地区名が分からない場合は、まず1列目の一覧を出して候補を見せる。

```bash
curl -s https://raw.githubusercontent.com/codeforkanazawa-org/5374/kanazawa/data/area_days.csv | cut -d, -f1
```

### 注意: 大分市版は金沢市データのコピー状態

`codeforoita/5374` は全ブランチ(gh-pages/master/dev/fix-center/fix-setting/kanazawa)が金沢市のデータ(浅野川・東部管理センター等)のままで、大分市の実データに差し替わっていない(2026-09-19実測)。**大分市の質問にはこのリポジトリを使わず**、大分市公式の収集日案内を案内する。過去の版では到達確認済みとして載せていたが、内容の実測でテンプレート状態と判明した。

## 対応自治体マトリクス(2026-09-19実測)

収集日・品目別のデータ有無と、代表品目の区分の違い。品目数はヘッダ行を除く実測値。

| 自治体 | 収集日 area_days | 品目別データ | 品目数 | 乾電池の区分 | スプレー缶の出し方 |
| --- | --- | --- | --- | --- | --- |
| 金沢市 | ○ | target.csv | 1,251 | 資源(水銀) | 資源。使い切って火気のない屋外で穴をあける |
| 美唄市 | ○ | target.csv(4件のみのスタブ) | 4 | 未収録 | 未収録 |
| 松前町 | ○ | target.csv | 54 | 燃えないごみ(黄)。電池回収袋(役場で無料配布)に入れて | 燃えないごみ(黄)。ガス抜きをしてから |
| 笠間市 | ○ | target.csv | 50 | 有害(充電式は端子をテープで絶縁) | 資源。使い切り必ず穴を開ける |
| 上砂川町 | ○ | target.csv | 65 | 危険ごみ | 危険ごみ。使い切って穴を開ける |
| 大分市 | ×(金沢データのコピー) | ×(同上) | - | - | - |
| 多摩市 | - | 公式品目別索引CSV(下記) | 1,641 | 有害性ごみ | 有害性ごみ。中身は使い切って |
| 横浜市 | - | 公式出し方一覧表CSV(下記) | 3,513 | 電池類(テープ等で絶縁) | スプレー缶。使い切り、**穴はあけない** |

同じ品目でも自治体で区分がまったく違う(乾電池が資源・有害・危険ごみ・電池類のいずれにもなる)。**別自治体の区分を類推で答えない**。

## 自治体公式の品目別オープンデータ

5374未展開の自治体でも、公式に品目別データを公開しているところがある。2026-09-19にダウンロードと内容を実測確認。

### 多摩市(東京都): ごみ・資源品目別索引CSV

CC BY 4.0。UTF-8・BOMなし。品目名にカナ・英字よみと粗大ごみ料金列まで付く。

```bash
curl -s https://www.city.tama.lg.jp/_res/projects/default_project/_page_/001/012/082/132241_tamashi_garbage_separate.csv | grep 'スプレー缶'
# -> 132241,132241GMLT000722,多摩市,全域,スプレー缶,スプレーカン,Spray can,有害性ごみ,,中身は必ず使い切ってから出してください,
```

索引ページ(出典表記の確認用): https://www.city.tama.lg.jp/kurashi/gomi/bunbetsu/1012082.html

### 横浜市: ごみと資源物の出し方一覧表CSV

横浜市オープンデータポータル公開(令和8年2月更新版を2026-09-19に実測)。**文字コードがCP932(Shift_JIS系)なのでiconvで変換してから引く**。

```bash
curl -s https://www.city.yokohama.lg.jp/kurashi/sumai-kurashi/gomi-recycle/gomi/dashikata.files/0141_20260209.csv \
  | iconv -f CP932 -t UTF-8 -c | grep '乾電池'
# -> 465,か,乾電池(マンガン、アルカリ、リチウム一次電池),,電池類,可能な限り使い切って、テープなどで絶縁をしてください。
```

データセットページ: https://data.city.yokohama.lg.jp/dataset/shigen_dashikata

横浜市はスプレー缶を「使い切って、穴はあけない」と案内しており、穴あけを求める自治体(金沢・笠間・上砂川)と正反対。リチウムイオン電池の出し方も令和7年12月1日に変更されている(CSV内の告知行より)。**「過去に聞いたルール」ではなく必ず最新のデータで答える**。

### 公式データの見つけ方(上記以外の自治体)

1. 自治体のオープンデータカタログ(「自治体名 オープンデータ」で検索)で「ごみ 分別 品目」を探す
2. data.go.jp で「ごみ 分別」を自治体名で絞って検索する
3. 自治体公式サイトの「ごみ分別辞典」「品目別索引」ページ。Webアプリ型(さいたま市の分別辞典など)が多く、curlで表を落とせない場合はその検索ページのURLを案内する

見つけた公式データがこのスキルで扱える形式(CSV等)なら、上のマトリクスに実測日つきで追加していく。

## 対象の自治体がない場合

5374の展開はボランティア次第で、主要都市を含めカバーされていない自治体が多い。対象データが見つからない場合は推測で答えず、次を案内する:

1. 自治体の公式サイトの「ごみ収集日」「収集カレンダー」ページ(地区名+「ごみ収集日」での検索)
2. 自治体のオープンデータカタログや data.go.jp での「ごみ 収集日」「ごみ 分別」検索
3. 5374公式サイト ( http://5374.jp/ ) にある展開済み地域の案内。HTTPSは証明書が未設定で使えないため(2026-09-13実測、`*.github.com` の証明書が返りホスト名不一致)、httpでのアクセスになる

## 注意

- CSVの文字コードは自治体版により異なる。金沢市・美唄市・多摩市はUTF-8(2026-09-19実測)だが、横浜市はCP932。文字化けしたら `iconv -f CP932 -t UTF-8 -c` で変換する。
- ヘッダ行(カテゴリ名・列名)は自治体で違う。答える前に必ず1行目を読んで列の意味を確認する。
- 品目の表記ゆれが大きい(「乾電池」「アルカリ乾電池」「電池」など)。1件もヒットしないときは品目名の一部(「電池」「スプレー」)で引き直し、候補を並べて選んでもらう。
- 充電式電池・モバイルバッテリーは発火事故のため分別が厳格化されており、自治体ごとに指定回収・店頭回収・別袋指定が入り乱れる。乾電池と同じ区分とは限らないので、必ずその自治体のデータで確認する。
- センター休止期間(center.csv)は更新が古いままのことがある(金沢市版は2022/2023年の日付が残っていた)。年末年始の質問には公式案内を優先する。
- 祝日の収集の有無は自治体のルール次第で、5374の曜日データだけでは分からない。公式案内を確認するよう添える。

## エラー・失敗時の対応

共通の取得時チェックリストは [共通レスポンス契約](../docs/response-contract.md) の「取得時の落とし穴チェックリスト」を参照。

- **タイムアウトを付ける**: `curl -sm 30` のように必ず制限時間を付ける。
- **HTTP 404**: ブランチ名(kanazawa/master/gh-pages)かファイルパスの違いが主な原因。GitHubのリポジトリページで `data/` の有無を確認する。リポジトリ自体が消えている場合は、その自治体版は運用終了の可能性があるため公式案内に切り替える。
- **地区名が見つからない**: 丁目や字の表記ゆれ(「浅野川」と「浅野川町」など)を疑い、1列目の一覧から部分一致で候補を示す。それでもなければデータにない地区として、公式案内を案内する。推測で曜日を答えない。
- **品目が見つからない**: target.csv がスタブの自治体(美唄市は4件のみ)がある。表記ゆれで引き直してもなければ収録外として、自治体公式の分別案内へ送る。「たぶん燃えるごみ」のような推測で答えない。
- **HTTP 5xx / タイムアウト**: 1〜2回だけ再試行。直らなければGitHub側の障害の可能性として、自治体公式サイトの確認を案内する。

## English summary

Looks up municipal garbage collection days and item-level sorting rules from open datasets, no API key needed. Two source families, both verified live 2026-09-19:

- **5374.jp-format CSVs** (volunteer-maintained, Code for Kanazawa model): `area_days.csv` maps each district to weekly/nth-weekday collection days; `target.csv` answers "which category is this item?" with per-item notices. Verified municipalities: Kanazawa, Bibai (4-item stub), Matsumae, Kasama, Kamisunagawa. The Oita repo still carries Kanazawa's data on every branch, so never answer Oita questions from it.
- **Official municipal open data**: Tama City (item index CSV, UTF-8, CC BY 4.0, 1,641 items) and Yokohama City (disposal list CSV, CP932, 3,513 items, updated Feb 2026-Reiwa 8).

Sorting rules differ sharply by city even for the same item: dry-cell batteries are 資源 in Kanazawa, 有害 in Kasama, 危険ごみ in Kamisunagawa, 有害性ごみ in Tama and 電池類 in Yokohama; spray cans must be punctured in some cities and must NOT be punctured in Yokohama. Always answer from that city's own current data, never by analogy, and redirect to official city guidance when no dataset exists or certainty matters (moving, holidays, rechargeable batteries).
