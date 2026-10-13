---
name: address-normalize
description: デジタル庁 アドレス・ベース・レジストリ(ABR)の公式マスタ(都道府県・市区町村・町字)で日本の住所文字列を分解・正規化する。全国47都道府県・1,918市区町村・町字レコードを使い、住所から都道府県・市区町村(全国地方公共団体コード)・町字(町字ID)・番地を切り出す。表記ゆれ(漢数字/全角/半角の丁目、郡名省略、都道府県名省略)を吸収。APIキー・ログイン不要。住居表示の番地・号の正規化やジオコーディング(緯度経度)は対象外。
license: MIT
metadata:
  category: address
  locale: ja-JP
---

# address-normalize

デジタル庁が整備する アドレス(住所・所在地)・ベース・レジストリ(ABR) の公開マスタで住所文字列を正規化するスキル。デジタル庁はユーザー登録なしで機械可読な住所マスタを公開している(利用はCC BY 4.0、サイト記載の利用規約に従う)。

**実測日: 2026-09-26。以下のURL・構造・件数はすべて当日の実測で確認。**

## エンドポイント一覧

| 内容 | URL |
| --- | --- |
| 都道府県マスタ(CSV zip) | `https://gov-csv-export-public.s3.ap-northeast-1.amazonaws.com/mt_pref/mt_pref_all.csv.zip` |
| 市区町村マスタ | `https://gov-csv-export-public.s3.ap-northeast-1.amazonaws.com/mt_city/mt_city_all.csv.zip` |
| 町字マスタ(都道府県別、13=東京都) | `https://gov-csv-export-public.s3.ap-northeast-1.amazonaws.com/mt_town/pref/mt_town_pref{PP}.csv.zip` |
| 町字マスタ(市区町村別) | `.../mt_town/city/mt_town_city{lg_code6桁}.csv.zip` |
| 町字マスタ フルセット(通称・字体不明レコード込み52列) | `.../mt_town_fullset/...` (パス構成は同上) |
| データセットカタログ(ArcGIS Hub API) | `https://dataset.address-br.digital.go.jp/api/search/v1/collections/all/items?q={検索語}` |
| 全データセットのDCAT-USフィード | `https://dataset.address-br.digital.go.jp/api/feed/dcat-us/1.1.json` |

**ミラー**: 原本ホスト `data.address-br.digital.go.jp` と同じパス構成で、S3 (`gov-csv-export-public.s3.ap-northeast-1.amazonaws.com`) にも置かれている。2026-09-26実測では原本ホストはネットワークによってCloudFront 403を返し、S3は安定して取得できた。両方を試すこと。

## 1. マスタの構造(2026-09-26実測)

| ファイル | サイズ | 行数 | 主な列 |
| --- | --- | --- | --- |
| mt_pref_all.csv | 2,690B | 47+ヘッダ | `lg_code,pref,pref_kana,pref_roma,efct_date,ablt_date,remarks` |
| mt_city_all.csv | 237,105B | 1,918+ヘッダ | 上記+`county,city,ward`(郡・政令市の区)と各カナ/ローマ字 |
| mt_town_pref13.csv(東京) | 1,159,208B | 5,940+ヘッダ | 上記+`machiaza_id,oaza_cho,chome,chome_kana,chome_number,koaza,rsdt_addr_flg,post_code` 等38列 |

- `lg_code`: 全国地方公共団体コード6桁。都道府県は下4桁が000を含む(北海道は010006)。市区町村で絞る主キー
- `machiaza_id`: 町字ID(市区町村内7桁)。`lg_code`+`machiaza_id` で町字を一意に特定できる
- `efct_date`/`ablt_date`: 効力発生日/廃止日。廃止済み(合併・消滅)レコードも残るので **ablt_date が空の行だけを正とする**
- フルセットは52列で、通称地名(`alias_oaza` 等)と字体不明レコード(`*_uncmn_*`)が追加される。正規化の基礎には基本38列で足りる

## 2. 表記ゆれの実例(2026-09-26実測)

- **丁目の数字表記がデータ内で混在**: 千代田区 内幸町は `chome=一丁目`(漢数字)、新宿区 歌舞伎町は `chome=１丁目`(全角数字)。`chome_number` 列が半角数字で常に入るので、比較はこちらを使い、入力側は「1丁目/１丁目/一丁目」の3形を全部試す
- **条・丁目の漢数字**: 札幌の `北一条西` は入力では「北1条西」と書かれがち。漢数字1文字→算用数字の1:1置換で両側を揃えてから比較する(長さが変わらないので残り部分の切り出しが壊れない)
- **大字つき町字**: 東京でも島しょ部に `大字宮` のような行が残る(東京都内33行)。`大字` を落とした入力は落とした側で再試行する
- **郡名の省略**: 入力は郡名を省くことが多い。郡+市と市のみの両形で最長一致を試す

## 3. ヘルパー

`address-normalize/lookup.py`(標準ライブラリのみ):

```bash
python3 address-normalize/lookup.py "東京都千代田区内幸町1丁目1-1"
# {"pref":"東京都","city":"千代田区","lg_code":"131016","town":"内幸町1丁目",
#  "machiaza_id":"0001001","rest":"1-1","matched":true, ...}

python3 address-normalize/lookup.py --towns --pref 13 --keyword 歌舞伎
```

マスタは `~/.cache/kurashi-skill/address-normalize/` にキャッシュ。`--refresh` で再取得。テストは `address-normalize/tests/`(5件)。

## 4. エラー・失敗時の対応

共通の取得時チェックリストは [共通レスポンス契約](../docs/response-contract.md) の「取得時の落とし穴チェックリスト」を参照。

- **`matched: false` / `town: null`**: 住所が町字まで特定できなかった。`rest` に残った文字列を見て、丁目の有無・大字の有無・旧住所表記を疑う。町字は `lg_code`+`machiaza_id` で一意だが、住居表示の番地・号はこのマスタの対象外(住居表示住居マスタ `mt_rsdtdsp_rsdt` を使う)
- **同じ町字名が複数行**: 丁目違いで別行。丁目つき町字に丁目なしの入力を一致させない(誤爆防止で `town: null` を返す)
- **廃止レコードの混在**: `ablt_date` が入っている行は過去の地名。現行住所の判定に使わない
- **ダウンロード403**: 原本ホストがCloudFront 403を返すネットワークがある。S3ミラー(上記)に切り替える。zipの中身は同名のCSV1ファイル
- **更新頻度**: データセットごとに更新日が違う(Hubの各データセットの「最終更新日」、2026-09実測では9月中旬のものが多い)。古いキャッシュを使い回さず、正確性が要る用途は `--refresh`

## 注意

- 出力の `rest`(番地・号・建物名)は正規化していない。番地の正規化・緯度経度が必要なら、デジタル庁のOSS `abr-geocoder`(GitHub: digital-go-jp/abr-geocoder)や住居表示住居マスタを案内する
- 利用はCC BY 4.0。生成物に「アドレス・ベース・レジストリ(デジタル庁)」の出所を添える
- 合併履歴の遡及は `efct_date`/`ablt_date` と住基ネットの旧コード対応表で扱うのが本筋。このスキルは現行マスタの照合まで

## English summary

Normalizes Japanese address strings against the Digital Agency's Address Base Registry (ABR) public masters - no key or login (CC BY 4.0). Masters: prefectures (mt_pref_all.csv.zip, 47 rows), municipalities (mt_city_all.csv.zip, 1,918 rows, incl. counties and ordinance-city wards), town blocks per prefecture (mt_town/pref/mt_town_pref{PP}.csv.zip; Tokyo = 5,940 rows, 38 columns with machiaza_id town ID, oaza_cho, chome, chome_number). Mirrors: the origin host data.address-br.digital.go.jp may return CloudFront 403 from some networks; the same paths work on the S3 bucket gov-csv-export-public.s3.ap-northeast-1.amazonaws.com (verified 2026-09-26). Catalog via ArcGIS Hub API at dataset.address-br.digital.go.jp/api/search/v1 and a DCAT-US feed (9,345 datasets). Gotchas: chome digit notation is mixed WITHIN the data (kanji vs full-width) - compare via chome_number and try all input variants; kanji numerals in 条/丁目 names (北一条西 vs 北1条西) need 1:1 kanji-to-digit folding on both sides; abolished records persist (check ablt_date); street numbers (番地・号) and geocoding are out of scope - point to the OSS abr-geocoder. Helper lookup.py decomposes an address into pref / city / lg_code / town / machiaza_id / rest as JSON, with 5 fixture tests.
