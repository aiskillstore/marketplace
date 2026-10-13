---
name: gsi-geocode
description: 国土地理院の公開API(認証不要)で、住所から緯度経度、緯度経度から標高、緯度経度から住所(市区町村+町丁目)を引く。住所検索は曖昧一致で件数が多く、先頭が正解とは限らない点まで扱う。地図の描画・経路・郵便番号検索は対象外(郵便番号はzipcode-lookup、住所の正規化はaddress-normalize)。
license: MIT
metadata:
  category: geo
  locale: ja-JP
---

# gsi-geocode

国土地理院の公開API3つを使い、住所と緯度経度を相互に引き、標高を求めるスキル。APIキー・登録は不要。

**実測日: 2026-10-04。以下のURL・応答・件数はすべて同日の実測で確認。**

## エンドポイント(すべてGET、認証なし)

| 用途 | URL | 応答 |
| --- | --- | --- |
| 住所→緯度経度 | `https://msearch.gsi.go.jp/address-search/AddressSearch?q=<住所>` | GeoJSON風の配列。`geometry.coordinates` は `[経度, 緯度]` |
| 緯度経度→標高 | `https://cyberjapandata2.gsi.go.jp/general/dem/scripts/getelevation.php?lon=<経度>&lat=<緯度>&outtype=JSON` | `{"elevation": 3.6, "hsrc": "1m（レーザ）"}` |
| 緯度経度→住所 | `https://mreversegeocoder.gsi.go.jp/reverse-geocoder/LonLatToAddress?lat=<緯度>&lon=<経度>` | `{"results": {"muniCd": "13103", "lv01Nm": "芝公園四丁目"}}` |
| 市区町村コード→名称 | `https://maps.gsi.go.jp/js/muni.js` | JavaScript(1,919行)。逆ジオコーダの `muniCd` を名称に直すために必要 |

標高の公式説明(パラメータと `-----` の意味): https://maps.gsi.go.jp/development/elevation_s.html 。サーバに過度の負担をかけないこと、予告なく遮断・提供停止されうることが明記されている。

## 使い方(ヘルパー)

```bash
python3 gsi-geocode/lookup.py geocode "東京都港区芝公園4-2-8" --limit 5
python3 gsi-geocode/lookup.py elevation --lat 35.6812 --lon 139.7671
python3 gsi-geocode/lookup.py reverse --lat 35.658649 --lon 139.745468
```

`lookup.py` は外部パッケージ不要。結果はJSONで出る。

## 実測で確認したこと (2026-10-04)

- 東京駅付近(35.6812, 139.7671)の標高は 3.6m、データ元は「1m(レーザ)」。富士山頂付近(35.3606, 138.7274)は 3770.6m。北海道(札幌)は「5m(レーザ)」で、20.2m。
- 「東京都港区芝公園4-2-8」(東京タワーの住所)は「東京都港区芝公園四丁目２番」の1件で、緯度経度は (35.658649, 139.745468)。番地までは解決するが、号(8)は落ちる。
- 逆ジオコーダに (35.658649, 139.745468) を渡すと、`muniCd` 13103 と `lv01Nm` 「芝公園四丁目」が返り、 `muni.js` で「東京都港区」に直せる。

## 実測で確認した罠

1. **住所検索は関連度順ではない。** 「東京タワー」は50件返り、先頭は「北海道札幌市東区」、本物の「東京タワー」は**最後(50番目)**。曖昧一致が「東」で拾うため。先頭を採ると北海道の座標を返す。ヘルパーは前方一致を先に並べ、`prefix_match` と `total` を返す。
2. **件数に上限がない。** 「駅」だけで12,755件、応答は約2.2MB。短い語で検索しない。ヘルパーは `--limit` で返却数を絞る(取得自体は全件)。
3. **郵便番号は引けない。** 「100-0001」「〒100-0001」は0件。郵便番号はzipcode-lookupを使う。
4. **標高の「データなし」は文字列 `-----`。** 海上(140.5E, 34.5N)・国外(ロンドン)・不正な入力(`lon=abc`)のすべてが HTTP 200 で `{"elevation":"-----","hsrc":"-----"}`。数値として読むと壊れる。入力ミスとデータなしを区別できない。
5. **逆ジオコーダの「該当なし」は空の `{}`。** 国外・不正入力ともHTTP 200。エラーにならない。
6. **市区町村コードの桁が合わない。** 逆ジオコーダは北海道を `01101` と返すが、`muni.js` のキーは先頭の0がない `1101`。そのまま引くと見つからない(ヘルパーは先頭の0を外して再検索)。`muni.js` の北海道の区は「札幌市　中央区」のように全角空白が入る。
7. **応答の数字は全角。** `title` は「千代田１番」のように全角数字。比較はNFKC正規化してから。
8. **逆ジオコーダは都道府県名を返さない。** `muniCd` と町丁目だけなので、都道府県と市区町村は `muni.js` で補う。

## 注意(必ず伝える)

- 出典を書く: 「国土地理院」。国土地理院コンテンツ利用規約(www.gsi.go.jp/kikakuchousei/kikakuchousei40182.html)と出典の記載(www.gsi.go.jp/LAW/2930-meizi.html)を参照。www.gsi.go.jp はTLSの旧式再ネゴシエーションを要求し、新しいOpenSSLのcurlでは `unsafe legacy renegotiation disabled` で接続できない(2026-10-04実測)。ブラウザやweb取得ツールでは開ける。
- 標高は地点の地表面の標高(元データはDEM)で、建物の高さは含まない。数値の桁は `hsrc` で決まる(1m・5mのレーザは0.1m、10mは1m)。
- 測量・法的な根拠には使えない。位置は住所の代表点で、建物の正確な位置ではない。
- 連続して大量に叩かない(公式の注意)。

## 失敗時の対応

- **検索が0件:** 郵便番号・誤字・番地の書き方を疑う。「都道府県+市区町村+町名+番地」か施設名で再検索。
- **何件も返る:** 先頭を採用しない。都道府県・市区町村を足して絞り、候補をユーザーに見せる。
- **標高が `-----`:** 「データなし」と伝える。海上か国外か入力ミスかは分からない。緯度経度の順(lon, lat)を確認。
- **逆ジオコーダが `{}`:** 国外・海上の可能性。推測で住所を作らない。
- **ネットワークエラー:** `{"error": ...}` が返る。少し待って再試行。

## English summary

Looks up addresses and coordinates with the Geospatial Information Authority of Japan's public APIs (no key): address to lat/lon, lat/lon to elevation, and lat/lon to municipality and block via `muni.js`. Measured 2026-10-04 traps: the address search is fuzzy and unranked (the real "東京タワー" is the 50th of 50 hits, the first is a Sapporo ward), has no result cap (a one-character query returned 12,755 hits, about 2.2 MB), cannot look up postal codes, and the elevation and reverse-geocoder endpoints return "no data" with HTTP 200 (`"-----"` string and `{}`). Reverse-geocoder codes for Hokkaido have a leading zero (`01101`) that `muni.js` keys do not (`1101`). Attribute the source to the GSI.
