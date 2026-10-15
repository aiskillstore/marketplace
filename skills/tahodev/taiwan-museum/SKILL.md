---
name: taiwan-museum
description: 博物館名錄查詢——文化部彙整的全台 144 間博物館清單（地址、票價、電話、經緯度、分類、官網連結）。博物館推薦、某某博物館在哪、門票多少、週末去哪逛的問題適用。免 API 金鑰、免登入。即時開館狀態、特展檔期不適用。
license: MIT
metadata:
  category: culture
  locale: zh-TW
---

# taiwan-museum

> 實測日：2026-09-19（最近一次端對端實測；數值基準日各自標於內文）

抓文化部文化地圖的博物館類開放資料（emap typeId=H），查全台博物館的基本資料。不需要 API 金鑰或登入。

## 基本流程

1. 抓 JSON（全量 144 館，單次回傳）
2. 依縣市（地址開頭）、分類、名稱篩選；有經緯度可算距離
3. 回報名稱、地址、票價、電話

### 1. 抓資料

```bash
curl -sm 30 -A 'Mozilla/5.0' 'https://cloud.culture.tw/frontsite/trans/emapOpenDataAction.do?method=exportEmapJson&typeId=H' -o /tmp/museum.json
```

2026-09-19 實測：HTTP 200、約 125KB、JSON 陣列 144 館。欄位：name、type（分類）、address、longitude/latitude（WGS84 經緯度，字串）、ticketPrice（票價說明文字）、phone、email、facebook、website、srcWebsite、name_eng、intro、cityName、version、hitRate。

分類分佈（實測）：歷史與人文 60、藝術與工藝 36、綜合與其他 24、自然與科學 24。

實測範例：國立故宮博物院 — 臺北市士林區至善路 2 段 221 號，普通參觀券 350 元（優惠券 150 元），座標 25.102357, 121.548492。

### 2. 查詢範例

```python
import json
d = json.load(open('/tmp/museum.json'))
taipei = [m for m in d if m['address'].startswith(('110','111','100','103','104','105','106','108','114','115','116')) or '臺北市' in m['address']]
for m in d:
    if '故宮' in m['name']:
        print(m['name'], m['address'], m['phone'])
```

### 3. 回報範式

「故宮在士林至善路二段 221 號，普通票 350 元；這是文化部 2026-09 名錄資料。」特展、開館日（週一休館等）名錄沒有，引導各館官網（website 欄位）。

## 錯誤與失敗時的處理

- **名錄非即時**：休館日、特展、整修閉館查不到；website/srcWebsite 欄位給用戶官方連結。
- **票價是自由文字**：格式不統一（含優惠條件全文），逐字引用，不要自行歸納成單一數字後失真。
- **部分欄位空白或缺鍵**：representImage、intro 常為空；website 欄位只有 102/144 館有值（2026-09-19 實測，部分條目整個鍵都沒有，用 .get() 取）；hitRate/version 是內部欄位忽略即可。
- **經緯度是字串**：算距離前轉 float；缺值時改用地址。
- **144 館不含所有展場**：文化部的「博物館」類不含一般文創園區、藝廊；用戶找其他場館時說明範圍。
- **curl 失敗**：帶瀏覽器 UA 重試；持續失敗回報資料源異常。

## English summary

Taiwan museum directory (Ministry of Culture emap), keyless. `curl 'https://cloud.culture.tw/frontsite/trans/emapOpenDataAction.do?method=exportEmapJson&typeId=H'` returns a JSON array of 144 museums with name, category (歷史與人文/藝術與工藝/綜合與其他/自然與科學), address, WGS84 lat/lng (as strings), free-text ticket prices, phone, and official website links. Verified 2026-09-19 (e.g. National Palace Museum, Shilin District, general admission 350 TWD). Directory only - no live opening status or special exhibitions; quote the ticketPrice field verbatim rather than compressing it; refer users to each venue's website for hours.
