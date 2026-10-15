---
name: taiwan-uv
description: 紫外線指數查詢——中央氣象署各測站每日紫外線指數最大值。今天紫外線強嗎、要不要防曬、UV index 的問題適用。需中央氣象署開放資料平台授權碼（免費申請）。逐時預報、即時觀測每小時更新值不適用（本資料集是每日最大值）。
license: MIT
metadata:
  category: weather
  locale: zh-TW
---

# taiwan-uv

> 實測日：2026-09-19（最近一次端對端實測；數值基準日各自標於內文）

查中央氣象署（CWA）開放資料平台的「氣象站每日紫外線指數最大值」資料集（O-A0005-001）。**需要授權碼**（API key）：到 https://opendata.cwa.gov.tw 免費註冊取得，放在環境變數或設定檔，**絕不寫進 repo 或回覆中**。

## 基本流程

1. 帶授權碼呼叫資料集 API
2. 依測站代號取出 UVIndex
3. 回報指數與等級（見對照表），註明這是「每日最大值」

### 1. 呼叫 API

```bash
curl -sm 20 "https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0005-001?Authorization=$CWA_API_KEY"
```

2026-09-19 實測：有授權碼時 HTTP 200、`success: "true"`，結構為 `records.weatherElement.location[]`，每筆含 `StationID` 與 `UVIndex`（浮點，當日最大值）。實測範例：全台 20+ 測站回傳，如 StationID 466920 UVIndex 8.0、466950 UVIndex 11.0。**無授權碼時回 401**，這是本資料集與免鑰資料集的主要差異。

### 2. 等級對照（國健署標準）

| UVIndex | 等級 | 建議 |
|---|---|---|
| 0-2 | 低量級 | 一般 |
| 3-5 | 中量級 | 建議防曬 |
| 6-7 | 高量級 | 防曬、戴帽 |
| 8-10 | 過量級 | 避免正午外出、完整防曬 |
| 11+ | 危險級 | 盡量避免外出 |

2026-09-19 實測範例：若回報「測站 466950 今日紫外線最大 11.0，危險級」。

### 3. 測站代號對應

資料只給 StationID（如 466920）。站名對照表在氣象署測站列表（opendata 平台另有測站資料集）；回報時若無法對應站名，以「站號 466920」回報並請用戶告知所在縣市協助挑最近站，不要猜站名。

## 錯誤與失敗時的處理

- **401 Forbidden**：授權碼錯誤或未帶。檢查環境變數；沒有金鑰就明說需要申請（免費），不要用記憶中的指數回答。
- **授權碼保密**：只能從安全儲存讀取，出現在命令列歷史或輸出時注意遮罩；不得寫入 SKILL 文件、commit、回覆。
- **每日最大值非即時**：早上查到的值可能是預報或昨日值；回報時說「今日預估最大」並附查詢時間。
- **success 為字串 "true"**：JSON 裡 success 是字串不是布林，比對時注意。
- **資料集改名/改版**：CWA 偶爾調整 resource id；404 時到 dataset 目錄查新 id，查不到回報資料源異常。

## English summary

Taiwan UV index (daily max per CWA station), REQUIRES a free CWA opendata API key (register at opendata.cwa.gov.tw; keep the key out of the repo and out of replies). `GET https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0005-001?Authorization=$CWA_API_KEY` returns records.weatherElement.location[] with StationID and UVIndex (verified 2026-09-19: 200 with key, 401 without; e.g. station 466950 UVIndex 11.0). Map to levels: 0-2 low, 3-5 moderate, 6-7 high, 8-10 very high, 11+ extreme. Values are daily maxima - say "today's forecast max", not a live reading. Note: `success` is a string, and station names are not included (station-id mapping caveat).
