---
name: taiwan-water
description: 停水公告查詢——台灣自來水公司停水資訊開放資料（計畫性與臨時停水、降壓）。停水、什麼時候恢復供水、家裡沒水的問題適用。免 API 金鑰、免登入。水費查詢、水質資訊不適用。
license: MIT
metadata:
  category: utility
  locale: zh-TW
---

# taiwan-water

> 實測日：2026-09-19（最近一次端對端實測；數值基準日各自標於內文）

抓台灣自來水公司的停水資訊開放資料，查目前與即將發生的停水/降壓案件。不需要 API 金鑰或登入。

## 基本流程

1. 抓 JSON（或 CSV）全量清單
2. 依縣市、行政區、時間篩選
3. 回報案件時段、範圍、戶數、原因；**沒有案件時也要如實說「目前無停水公告」**

### 1. 抓資料

```bash
# JSON
curl -sm 20 -A 'Mozilla/5.0' 'https://web.water.gov.tw/wateroffapi/openData/export/json' -o /tmp/water.json
# 或 CSV(UTF-8)
curl -sm 20 -A 'Mozilla/5.0' 'https://web.water.gov.tw/wateroffapi/openData/export/csv-utf8' -o /tmp/water.csv
```

2026-09-19 實測：JSON HTTP 200（當下無案件，回 `[]`）；CSV HTTP 200，標頭欄位：案件編號、區處、廠所、連絡電話、案件日期時間、恢復日期時間、屬性、定時案件、停水類型、案件時長（小時）、停水戶數、影響縣市、影響行政區、停水地區、停水原因、降壓戶數、降壓地區、降壓原因、影響戶數。

### 2. 解讀重點

- `[]`（空陣列）= **目前全國無停水公告案件**，這是正常且常見的狀態
- 有案件時：以「影響縣市」「影響行政區」「停水地區」對使用者地點；「案件日期時間」「恢復日期時間」是預計時程
- 「降壓」與「停水」是不同類型，回報時區分
- 連絡電話是該區處服務所電話，一併提供方便用戶確認

### 3. 回報範式

- 無案件：「台水公司目前沒有停水或降壓公告（查詢時間 HH:MM）。」
- 有案件：「台北市中正區○○里一帶，9/20 09:00 起預計停水 8 小時（清洗水池），影響約 1,200 戶；預計 17:00 恢復。區處電話 02-xxxx-xxxx。」

## 錯誤與失敗時的處理

- **空清單不是錯誤**：`[]` 或只有標頭的 CSV 就是「無公告」，不要當成抓取失敗重試到懷疑人生。
- **資料僅台水公司轄區**：金門、馬祖及台北自來水事業處（台北市全部+新北部分）不在此系統；台北市用戶要說明「台北市屬北水處轄區，需查北水處公告」。
- **臨時爆管**：突發搶修可能來不及上公告；用戶已經沒水但查無案件時，建議直接打 1910 台水客服。
- **主站偶發 502**：web.water.gov.tw 首頁曾見 502，但 API 路徑正常；抓不到時隔幾分鐘重試一次，仍失敗回報資料源異常。
- **時間格式**：民國或西元並存可能，回報前確認欄位實際格式。

## English summary

Taiwan Water Corporation outage notices, keyless. JSON: `https://web.water.gov.tw/wateroffapi/openData/export/json`, CSV: `.../export/csv-utf8`. An empty array means NO current outages - a valid, common answer, not an error. Schema: case id, district office, contact phone, start/estimated-restore times, type (outage vs pressure reduction), households affected, county/district/area, cause. Verified 2026-09-19 (both endpoints 200; JSON was `[]`). Coverage: Taiwan Water Corp only - Taipei City is served by Taipei Water Department (different system); sudden pipe bursts may not appear - suggest the 1910 hotline when the user has no water but no listed case.
