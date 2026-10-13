---
name: taiwan-toilet
description: 全國公廁查詢——環境部全國公廁建檔資料（位置、管理單位、評鑑等級、尿布台）。附近公廁、哪裡有廁所、乾淨的公廁的問題適用。免註冊——用政府資料開放平臺公布的公用資料集存取金鑰。即時開放狀態（維修中）不適用。
license: MIT
metadata:
  category: civic
  locale: zh-TW
---

# taiwan-toilet

> 實測日：2026-10-02（最近一次端對端實測；數值基準日各自標於內文）

查環境部「全國公廁建檔資料」（data.gov.tw 資料集 30794）的公廁位置與評鑑。**不用自己註冊**：data.gov.tw 資料集頁公布了該資料集的 API 存取金鑰，直接用即可。

## 基本流程

1. 帶公布金鑰抓 API（分頁 limit=1000，用 offset 翻頁）
2. 依縣市代碼、鄉里、經緯度篩選
3. 回報名稱、地址、管理單位、評鑑等級；有經緯度可算最近公廁

### 1. 抓資料

```bash
BASE='https://data.moenv.gov.tw/api/v2/fac_p_07?api_key=b7df779e-71a6-4148-8379-5afbd441d803'
curl -sm 30 -A 'Mozilla/5.0' "$BASE&limit=1000&offset=0&sort=ImportDate%20desc&format=JSON" -o /tmp/toilet_p1.json
```

要找最近的公廁必須看全部頁面（只看第 1 頁會漏掉別頁更近的點）。下面把所有頁合併成 `/tmp/toilet_all.json`，回傳筆數 < 1,000 即到底：

```python
import json, urllib.request
BASE = 'https://data.moenv.gov.tw/api/v2/fac_p_07?api_key=b7df779e-71a6-4148-8379-5afbd441d803'
UA = {'User-Agent': 'Mozilla/5.0'}
rows, offset = [], 0
while True:
    req = urllib.request.Request(f'{BASE}&limit=1000&offset={offset}&sort=ImportDate%20desc&format=JSON', headers=UA)
    page = json.loads(urllib.request.urlopen(req, timeout=40).read())
    rows += page
    if len(page) < 1000:
        break
    offset += 1000
json.dump(rows, open('/tmp/toilet_all.json', 'w'), ensure_ascii=False)
print(len(rows))
```

2026-10-02 實測：合併 46 頁共 45,952 筆，約 77 秒（每頁約 1.3 秒）；只需附近幾個點時可先查詢縣市範圍再分頁。以台北車站附近座標（25.04, 121.51）試算，最近三筆是 0.12 km 的東吳大學城區部 5 大樓 1F。

2026-09-19 實測：HTTP 200、每頁 1,000 筆，offset 翻頁正常；回傳筆數 < limit 即到底。欄位：county（縣市代碼，如 65000=新北市、10018=新竹市）、areacode、village、number、name、address、administration（管理單位）、latitude/longitude、grade（評鑑等級：特優級、優等級…）、type/type2（公廁類型）、exec、diaper（尿布台）。

實測範例：「中油鶯歌加油站-男廁」（新北市鶯歌區南靖里文化路 152 號，台灣中油管理，特優級，24.9504, 121.3522）。

### 2. 縣市代碼

county 欄是內政部代碼（65000=新北市、10018=新竹市…）。沒有文字縣市名，**用 address 前幾個字判斷縣市更直覺**，或對照代碼表。

### 3. 找最近公廁

```python
import json, math
rows = json.load(open('/tmp/toilet_all.json'))   # 上一節合併後的全部頁面
def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None                                  # 空字串、缺值
def dist(la1, lo1, la2, lo2):
    return math.hypot((la1-la2)*111, (lo1-lo2)*111*math.cos(math.radians(la1)))  # km 粗估
cands = []
for r in rows:
    la, lo = num(r.get('latitude')), num(r.get('longitude'))
    if la is None or lo is None:                    # 緯度或經度任一缺值都略過
        continue
    cands.append((dist(25.04, 121.51, la, lo), r))
for d, r in sorted(cands, key=lambda x: x[0])[:3]:
    print(f"{d:.2f}km {r['name']} {r['address']} {r['grade']}")
```

## 錯誤與失敗時的處理

- **金鑰是 data.gov.tw 公布的資料集金鑰**：從資料集 30794 頁面的 resource URL 取得；若失效（401/403）回該頁重取新金鑰，不要自己註冊帳號。
- **分頁必做**：單頁上限 1,000 筆，全國資料需循環 offset 直到回傳 < 1,000。
- **建檔資料非即時**：評鑑與狀態定期更新，「維修中暫停開放」查不到；回報附資料性質說明。
- **經緯度缺值**：部分筆數 latitude 或 longitude 為空字串，上面的程式兩者任一缺值就略過；不要只檢查緯度。
- **grade 是評鑑結果**：分特優/優等/甲等…，代表清潔品質評鑑，引用時說明是評鑑等級。
- **JSON/CSV/XML 三格式**：同 resource 帶 format 參數；CSV 適合表格處理。

## English summary

Taiwan national public toilet registry (MOENV fac_p_07), keyless - use the resource API key published on the data.gov.tw dataset page 30794 (no self-signup needed; re-fetch it there if it ever 401s). `GET https://data.moenv.gov.tw/api/v2/fac_p_07?api_key=<published>&limit=1000&offset=N&format=JSON`, paginate with offset until a short page. Fields: county code, village, name, address, managing org, lat/lng, grade (inspection rating 特優級/優等級...), type, diaper station. Verified 2026-09-19 (2 pages x 1,000 rows; e.g. 中油鶯歌加油站-男廁, Yingge, New Taipei, top grade). Registry data, not live open/closed status; some rows lack coordinates.
