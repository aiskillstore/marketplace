---
name: amagumo
description: 気象庁の雨雲レーダー(解析雨量・降水ナウキャスト)タイルから、今の雨の強さとこの後30〜60分の見通しを調べる。今雨降ってる、雨雲、あとどれくらいで雨、降水ナウキャストの質問に対応。APIキー・ログイン不要。明日以降の天気はjma-weather、警報・地震・津波はbosai-alertを使う。
license: MIT
metadata:
  category: weather
  locale: ja-JP
---

# amagumo

気象庁の雨雲レーダータイル(解析雨量・降水ナウキャスト)を取得し、指定地点の「今の雨の強さ」と短時間の見通しを読むスキル。気象庁はユーザー登録なしで機械可読な気象・防災データを公開している。APIキー不要、curlだけで取れる。

**実測日: 2026-09-11。本文のコマンド・構造は実測で確認したものを収録(個所ごとの日付は各所の記載を参照)。**

## 基本の流れ

### 1. 有効な時刻の一覧を取る

```bash
# 解析雨量(実況)
curl -sm 30 https://www.jma.go.jp/bosai/jmatile/data/nowc/targetTimes_N1.json

# 降水ナウキャスト(予報)
curl -sm 30 https://www.jma.go.jp/bosai/jmatile/data/nowc/targetTimes_N2.json
```

各要素は `basetime`(観測の基準時刻)、`validtime`(そのタイルが有効な時刻)、`elements`(`["hrpns","hrpns_nd"]`)を持つ。時刻は `YYYYMMDDHHMMSS` 形式のUTC。ユーザーに伝えるときはJST(+9時間)に変換する。2026-09-11に実測して両方200を確認。

### 2. 地点のタイル座標を計算する

タイルはXYZ形式(ズームz)。緯度lat・経度lonから:

```bash
python3 -c "
import math,sys
lat,lon,z=float(sys.argv[1]),float(sys.argv[2]),int(sys.argv[3])
n=2**z
x=int(n*((lon+180)/360))
y=int(n*(1-math.log(math.tan(math.radians(lat))+1/math.cos(math.radians(lat)))/math.pi)/2)
print(x,y)" 35.68 139.77 8   # 東京 → 227 100
```

街の規模なら z=8 前後が見やすい(東京なら x=227, y=100)。

### 3. タイル画像を取る

```bash
curl -sm 30 -o tile.png \
  "https://www.jma.go.jp/bosai/jmatile/data/nowc/{basetime}/none/{validtime}/surf/hrpns/{z}/{x}/{y}.png"
```

`{basetime}` と `{validtime}` には手順1のJSONの値をそのまま使う(推測で時刻を組み立てない)。2026-09-11に実測して200・PNG画像(256×256)を確認。

## 読み方

タイルは256×256の4ビットカラーマップPNG。パレットのインデックスが雨の強さに対応する。2026-09-11に実測したパレット:

| idx | RGB | めやす |
| --- | --- | --- |
| 0-1 | 白 | 雨なし |
| 2 | (242,242,255) | ごく弱い |
| 3 | (160,210,255) | 弱い |
| 4 | (33,140,255) | やや強い |
| 5 | (0,65,255) | 強い |
| 6 | (250,245,0) | 激しい |
| 7 | (255,153,0) | 非常に激しい |
| 8 | (255,40,0) | 猛烈 |
| 9 | (180,0,104) | 猛烈(上位) |

地点のピクセルはタイル内の画素位置で読む。PIL(Pillow)があれば:

```bash
python3 -c "
from PIL import Image
im=Image.open('tile.png').convert('P')
idx=im.getpixel((px,py))
print(idx, im.getpalette()[3*idx:3*idx+3])"   # px,pyはタイル内座標
```

「今降ってるか」と「この後どうなるか」は、同じ地点について実況(N1)の最新と予報(N2)の先の時刻を見比べると答えられる。

## エラー・失敗時の対応

共通の取得時チェックリストは [共通レスポンス契約](../docs/response-contract.md) の「取得時の落とし穴チェックリスト」を参照。

- **targetTimesが取れない(5xx・タイムアウト・空)**: 1〜2回リトライし、駄目なら「雨雲データを取得できなかった」と明示して気象庁の防災情報ページ(https://www.jma.go.jp/bosai/map.html)を案内する。取れなかったことを「雨は降っていない」とは言わない。
- **タイルが404**: basetime/validtimeを推測で組み立てていないか確認。手順1のJSONの値をそのまま使う。古い時刻のタイルは消えることがあるので、一覧を取り直す。
- **Pillowがない環境**: `pip install pillow`、またはImageMagickの `convert tile.png -format '%[pixel:p{px,py}]' info:` で色を読める。

## 注意

- **色→雨量の正式な対応表(凡例のmm/h値)は公式ドキュメントで確認できていない。** 上の「めやす」はパレット実測値と気象庁の強度表現(弱い/やや強い/強い/激しい/非常に激しい/猛烈)を対応づけた目安。正確なmm/hではなく「雨があるか、だいたいどのくらい強いか」の参考として伝える。
- タイルは画像であり点の観測値ではない。周囲数ピクセルの中央値を見るなど、ノイズに強い読み方をする。
- 答えるときは時刻(JST)を必ず添える(「14:50時点の実況では…」)。

## English summary

Reads JMA's rain-cloud radar tiles (analysis rainfall and precipitation nowcast) to answer "is it raining now at this spot, and will it get worse in the next hour". No API key or login. Flow: fetch targetTimes_N1.json (observed) / targetTimes_N2.json (forecast) for valid basetime/validtime pairs, convert lat/lon to XYZ tile coordinates, download the hrpns tile PNG, and read the palette index at the point. Timestamps are UTC - convert to JST for the user. The color-to-mm/h mapping is an estimate from the measured palette, not an official legend; present intensity as approximate. Never report "no rain" when the fetch failed.
