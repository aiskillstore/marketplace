---
name: taiwan-aqi
description: 查台灣各縣市與測站的每小時空氣品質指標（AQI）、主要污染物、PM2.5、PM10 與發布時間。今天空氣好嗎、空氣污染、AQI、PM2.5、敏感族群適不適合外出的問題適用。使用環境部官方 AQX_P_432 資料集，需要免費註冊取得 MOENV API 金鑰。
license: MIT
metadata:
  category: environment
  locale: zh-TW
---

# taiwan-aqi

> 實測日：2026-09-20（最近一次端對端實測；數值基準日各自標於內文）

查環境部環境資料開放平臺的「空氣品質指標（AQI）」資料集（`AQX_P_432`）。資料由空氣品質監測網提供，每小時更新，含測站、縣市、AQI、主要污染物、狀態、PM2.5、PM10、氣體濃度、發布時間與座標。

**需要 API 金鑰（免費）：** 到 https://data.moenv.gov.tw/api-term 註冊後取得 API 金鑰，放在環境變數 `MOENV_API_KEY` 或安全的憑證儲存中。金鑰不要寫進 repo、命令輸出或回覆。資料集說明：[環境部 AQX_P_432](https://data.moenv.gov.tw/dataset/detail/AQX_P_432)。

## 基本流程

1. 確認 `MOENV_API_KEY` 已設定
2. 呼叫 `AQX_P_432`，先取回全台測站
3. 用 `jq` 依縣市或測站篩選
4. 回報 AQI、`status`、主要污染物、PM2.5、PM10 與 `publishtime`
5. 先檢查資料時間與缺值，不用舊值或空值推測現況

### 1. 下載目前資料

```bash
curl -fsS --max-time 30 \
  --get 'https://data.moenv.gov.tw/api/v2/aqx_p_432' \
  --data-urlencode 'format=json' \
  --data-urlencode 'offset=0' \
  --data-urlencode 'limit=1000' \
  --data-urlencode "api_key=$MOENV_API_KEY" \
  -o /tmp/taiwan-aqi.json
```

回傳最外層是 JSON 陣列。每筆常用欄位：

- `sitename`、`county`、`siteid`
- `aqi`、`status`、`pollutant`
- `pm2.5`、`pm2.5_avg`、`pm10`、`pm10_avg`
- `o3`、`o3_8hr`、`co`、`co_8hr`、`so2`、`so2_avg`、`no2`
- `wind_speed`、`wind_direc`
- `publishtime`、`longitude`、`latitude`

### 2. 依縣市查詢

縣市名稱以資料內的 `county` 為準（如 `臺北市`、`新北市`）。把「台」正規化成「臺」再比對：

```bash
COUNTY='台北市'
COUNTY=${COUNTY//台/臺}
jq --arg county "$COUNTY" '
  map(select((.county | gsub("台"; "臺")) == $county))
  | sort_by((.aqi | tonumber? // -1)) | reverse
  | map({sitename, aqi, status, pollutant, "pm2.5": .["pm2.5"], pm10, publishtime})
' /tmp/taiwan-aqi.json
```

同一縣市有多個測站。不要只取第一筆：可列全部，或回報 AQI 最高的測站並註明這是縣市內測站比較，不是整個縣市單一 AQI。

### 3. 依測站查詢

```bash
SITE='板橋'
jq --arg site "$SITE" '
  map(select(.sitename == $site))
  | map({sitename, county, aqi, status, pollutant, "pm2.5": .["pm2.5"], "pm2.5_avg": .["pm2.5_avg"], pm10, pm10_avg, publishtime})
' /tmp/taiwan-aqi.json
```

同名或近似站名不確定時，先列出候選，不要猜：

```bash
jq -r '.[].sitename' /tmp/taiwan-aqi.json | sort -u
```

## AQI 等級

環境部標準：[空氣品質指標](https://airtw.moenv.gov.tw/cht/Information/Standard/AirQualityIndicator.aspx)

| AQI | 狀態 |
|---|---|
| 0-50 | 良好 |
| 51-100 | 普通 |
| 101-150 | 對敏感族群不健康 |
| 151-200 | 對所有族群不健康 |
| 201-300 | 非常不健康 |
| 301-500 | 危害 |

優先使用 API 的 `status` 原文。若 `aqi` 或 `status` 缺值，不自行補算等級；直接說該測站目前缺值。

## 實測記錄

- 2026-09-20：以有效 MOENV API 金鑰呼叫 `AQX_P_432?format=json&offset=0&limit=2`，HTTP 200，回傳最外層 JSON 陣列。樣本：汐止與基隆皆為 AQI 52、狀態「普通」、主要污染物「細懸浮微粒」，發布時間 `2026/09/20 12:00:00`。
- 2026-09-20：資料集頁確認代碼 `AQX_P_432`、更新頻率 1 小時與 24 個欄位。平台開發指南列出的 API 格式為 `https://data.moenv.gov.tw/api/v2/{DataID}?format=...&offset=...&limit=...&api_key=...`。

## 錯誤與失敗時的處理

- **401 / 403 或認證錯誤**：金鑰遺漏、無效或失效。確認安全儲存中的值，必要時到會員頁重取；不要把金鑰印出來除錯。
- **HTTP 200 但不是 JSON 陣列**：視為 API 錯誤。保留 HTTP 狀態與不含秘密的錯誤訊息後停止，不要把錯誤頁當資料。
- **空陣列**：先確認 `offset`、`limit`、資料集代碼與平台公告。不要解讀成全台空氣品質良好。
- **測站缺值**：`aqi`、污染物或濃度可能是空字串。原樣標示「目前無資料」，可提供同縣市其他有值測站，但不要替缺值站推估。
- **資料延遲**：解析 `publishtime`，附在回答中。相對目前時間明顯落後時說明資料可能延遲，不把它稱為即時值。
- **平台逾時 / 5xx**：等待數秒後重試一次；仍失敗就回報環境部平台暫時不可用，並給資料集頁與空氣品質監測網連結。不要用記憶中的 AQI 代替。
- **健康建議**：AQI 是一般資訊，不是醫療診斷。需要活動建議時引用環境部標準；有症狀或個人疾病問題請依醫療專業建議。
- **金鑰保密**：範例只用 `$MOENV_API_KEY`。不得把實際金鑰寫進文件、commit、issue、PR、日誌或回覆。

## English summary

Queries Taiwan's official hourly Air Quality Index dataset (`AQX_P_432`) from the Ministry of Environment. A free MOENV open-data API key is required; keep it in `MOENV_API_KEY` or secure credential storage and never commit or echo it. `GET https://data.moenv.gov.tw/api/v2/aqx_p_432?format=json&offset=0&limit=1000&api_key=...` returns a top-level JSON array with station/county, AQI, status, dominant pollutant, PM2.5/PM10 and averages, gas readings, publication time and coordinates. Verified end to end with a valid key on 2026-09-20 (HTTP 200; Xizhi and Keelung samples both AQI 52, Moderate, dominant pollutant PM2.5, published 12:00). Filter client-side by county or station, normalize 台/臺 for county names, include `publishtime`, and never infer missing readings. Official AQI bands: 0-50 Good, 51-100 Moderate, 101-150 Unhealthy for Sensitive Groups, 151-200 Unhealthy, 201-300 Very Unhealthy, 301-500 Hazardous.
