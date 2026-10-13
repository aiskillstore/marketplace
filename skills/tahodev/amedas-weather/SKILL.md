---
name: amedas-weather
description: 気象庁のアメダス(地域気象観測システム)最新観測値を取得する。今の気温・湿度・風・降水量・気圧を全国約1,300観測所から調べる。「今の気温」「今の雨量」「今の風」の質問に対応。APIキー・ログイン不要。予報はjma-weather、雨雲の動きはamagumo、警報はbosai-alertを使う。
license: MIT
metadata:
  category: weather
  locale: ja-JP
---

# amedas-weather

気象庁のアメダス最新観測値(JSON)から、全国約1,300観測所の「今」の気象を読むスキル。気象庁はユーザー登録なしで機械可読な気象・防災データを公開している。APIキー不要、curlだけで取れる。予報(jma-weather)ではなく観測の話である点に注意。

**実測日: 2026-09-20。本文のコマンド・構造は実測で確認したものを収録(個所ごとの日付は各所の記載を参照)。**

## 基本の流れ

### 1. 最新の観測時刻を取る

```bash
curl -sm 30 https://www.jma.go.jp/bosai/amedas/data/latest_time.txt
```

`2026-09-20T13:20:00+09:00` のようなISO形式の時刻が1行だけ返る(JST、JSONではない)。2026-09-20に実測して200を確認。観測は10分間隔。

### 2. 全観測所の最新値を取る

時刻を `YYYYMMDDHHMMSS` に変換してmapファイルを取る。

```bash
# {amedas_time} は latest_time.txt を YYYYMMDDHHMMSS に直した値(例: 2026-09-20T13:20:00+09:00 → 20260920132000)
curl -sm 30 -o amap.json https://www.jma.go.jp/bosai/amedas/data/map/{amedas_time}.json
```

2026-09-20実測: 200、約251KB、1,286観測所分。キーは観測所コード、値は各要素の `[値, フラグ]` の組。

主な要素: `temp`(気温℃)、`humidity`(湿度%)、`wind`(風速m/s)、`windDirection`(風向。1〜16の16方位、0は静穏)、`precipitation10m`/`1h`/`3h`/`24h`(降水量mm)、`sun10m`/`sun1h`(日照)、`pressure`(気圧hPa)、`normalPressure`(気圧平年値)。**観測所によって持つ要素が違う**(気圧は一部だけ)。要素がない観測所ではキー自体が出ない。

### 3. 観測所名と場所を引く

```bash
curl -sm 30 -o stations.json https://www.jma.go.jp/bosai/amedas/const/amedastable.json
```

2026-09-20実測: 200、1,286観測所。各要素は `type`、`lat` `[度, 分]`、`lon` `[度, 分]`、`alt`(標高m)、`kjName`(漢字名)、`knName`(カナ)、`enName`(英語名)を持つ。`type` の内訳実測: A=56(全要素)、B=95、C=1,131、ほか数件(G/D/E/F)。**ファイル名は `amedastable.json`。`amedastation.json` は404になる**(2026-09-20実測)。

緯度経度は度分なので、十進に直すなら `度 + 分/60`。2026-09-20 13:20 JST実測の例: 東京(44132)は 気温22.8℃・湿度92%・過去24時間の降水量15.0mm。

### 4. 近い観測所を探す

ユーザーの場所(緯度経度)から最寄りの観測所コードを探すなら:

```bash
python3 - <<'PYEOF'
import json
st=json.load(open('stations.json'))
def dec(d): return d[0]+d[1]/60
def dist(a,b): return (dec(a['lat'])-b[0])**2+(dec(a['lon'])-b[1])**2
me=(35.68, 139.77)  # 東京駅あたり
best=min(st.items(), key=lambda kv: dist(kv[1], me))
print(best[0], best[1]['kjName'])
PYEOF
```

## エラー・失敗時の対応

共通の取得時チェックリストは [共通レスポンス契約](../docs/response-contract.md) の「取得時の落とし穴チェックリスト」を参照。

- **mapファイルが404**: 時刻の組み立てを推測していないか確認。必ず `latest_time.txt` の値を `YYYYMMDDHHMMSS` に変換して使う(コロンと `+09:00` を除く)。古い時刻のファイルは残っていないことがあるので、取り直す。
- **latest_time.txt自体が取れない(5xx・タイムアウト)**: 1〜2回リトライし、駄目なら「アメダスのデータを取得できなかった」と明示し、気象庁の防災情報ページ(https://www.jma.go.jp/bosai/map.html)を案内する。取れなかったことを「晴れている」とは言わない。
- **目的の要素が観測所にない**: その観測所では測っていない。type A(全要素)の近所の観測所に切り替えるか、「この観測所では気圧は観測していない」と正直に伝える。

## 注意

- 値は10分間隔の最新観測。回答には必ず観測時刻(JST)と観測所名を添える(「13:20時点の東京の観測では…」)。
- 予報ではない。「この後どうなるか」はjma-weather(予報)やamagumo(雨雲ナウキャスト)に振る。
- `[値, フラグ]` のフラグは品質情報。異常値の扱いが必要な用途では気象庁の定義を確認する(通常利用では0=正常として読んでよい)。

## English summary

Fetches the latest AMeDAS (Automated Meteorological Data Acquisition System) observations from JMA's public JSON feeds. Flow: read latest_time.txt (a single ISO timestamp line in JST, not JSON), convert it to YYYYMMDDHHMMSS and download /bosai/amedas/data/map/<ts>.json (~1,286 stations, values as [value, flag] pairs), and resolve station names/locations from /bosai/amedas/const/amedastable.json (note: amedastation.json 404s). Elements vary by station type (type A has all elements including pressure). Observations update every 10 minutes. Always quote the observation time and station name. This is observed weather, not forecast - use jma-weather for forecasts. No API key or login. Verified live on 2026-09-20.
