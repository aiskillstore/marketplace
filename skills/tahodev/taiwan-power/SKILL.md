---
name: taiwan-power
description: 台電電力供需即時資訊——今日系統供電能力、目前用電量、備轉容量率與供電燈號。電夠不夠、會不會缺電、限電、備轉容量、供電燈號的問題適用。免 API 金鑰、免登入。分區限電名單、個別電號用電量不適用。
license: MIT
metadata:
  category: utility
  locale: zh-TW
---

# taiwan-power

> 實測日：2026-09-19（最近一次端對端實測；數值基準日各自標於內文）

抓台電開放資料服務的「今日系統供需狀況」JSON，回報當前用電、預估尖峰與備轉容量率燈號。不需要 API 金鑰或登入。注意：台電主站 www.taipower.com.tw 有 CDN 擋程式存取（403），**要走開放資料主機 service.taipower.com.tw**。

## 基本流程

1. 抓今日供需 JSON
2. 解析 4 段記錄：目前用電、今日預估、昨日實績、即時尖峰
3. 回報備轉容量率與燈號，附發布時間

### 1. 抓資料

```bash
curl -sm 20 -A 'Mozilla/5.0' 'https://service.taipower.com.tw/data/opendata/apply/file/d006020/001.json'
```

2026-09-19 實測：HTTP 200、約 0.7KB，`records` 含 4 個物件：

- `curr_load`（目前用電，萬瓩）、`curr_util_rate`（目前使用率 %）
- `fore_maxi_sply_capacity`（預估最大供電）、`fore_peak_dema_load`（預估尖峰負載）、`fore_peak_resv_capacity`（預估備轉容量，萬瓩）、`fore_peak_resv_rate`（備轉容量率 %）、`fore_peak_resv_indicator`（燈號）、`fore_peak_hour_range`、`publish_time`（民國年+星期+時間）
- `yday_*`（昨日實績同欄位）
- `real_hr_maxi_sply_capacity`、`real_hr_peak_time`（即時最高，西元時間）

實測範例：publish_time 115.09.19（六）03:10，目前用電 2,733.5 萬瓩、使用率 72%，預估備轉容量率 26.21% 綠燈，昨日尖峰 3,747.2 萬瓩（11:38）。

### 2. 燈號對照

| indicator | 燈號 | 備轉容量率 |
|---|---|---|
| G | 綠燈（供電充裕） | ≥ 10% |
| Y | 黃燈（供電吃緊） | 6%~10% |
| O | 橘燈（供電警戒） | < 6% |
| R | 紅燈（限電警戒） | < 900MW 備轉 |
| B | 黑燈（限電準備） | 負值 |

### 3. 回報範式

「台電今日（09/19 03:10 發布）目前用電 2,733.5 萬瓩，預估尖峰 3,400 萬瓩、備轉容量率 26.21%，供電燈號綠燈，供電充裕。」

## 錯誤與失敗時的處理

- **www.taipower.com.tw 會 403**：CloudFront 擋海外/程式存取；一律用 service.taipower.com.tw 的 opendata 路徑。
- **success 是字串 "true"**：比對時注意型別。
- **民國年 publish_time**：115.09.19 = 2026-09-19；real_hr_peak_time 是西元，兩種並存注意。
- **單位是萬瓩**：1 萬瓩 = 10 MW；回報時保留原單位或換算清楚。
- **凌晨時段**：午夜前後 records 可能跨日混合，回報附 publish_time 讓使用者判斷。
- **curl 失敗**：帶瀏覽器 UA 重試；持續失敗回報資料源異常，不要編造備轉數字。

## English summary

Taiwan Taipower real-time power supply/demand, keyless. `GET https://service.taipower.com.tw/data/opendata/apply/file/d006020/001.json` (use a browser UA; the main site www.taipower.com.tw 403s datacenter traffic - always use the service host). Records: current load & utilization, today's forecast (max supply, peak demand, reserve capacity/rate, indicator G/Y/O/R/B, publish time in ROC calendar), yesterday's actuals, and the realtime peak. Verified 2026-09-19: load 2,733.5 (10k kW units), forecast reserve rate 26.21% green. `success` is a string; units are 10k kW (1 = 10 MW).
