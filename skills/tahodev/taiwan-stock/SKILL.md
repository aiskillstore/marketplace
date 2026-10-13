---
name: taiwan-stock
description: 台股行情快照——上市（TWSE）與上櫃（TPEX）每日收盤行情、個股本月每日成交、大盤指數。台股今天、台積電收盤、漲跌幅排行、大盤指數、上市上櫃行情的問題適用。免 API 金鑰、免登入。盤中即時報價、期貨、財報明細不適用（本技能是每日收盤後的統計資料）。
license: MIT
metadata:
  category: finance
  locale: zh-TW
---

# taiwan-stock

> 實測日：2026-10-02（最近一次端對端實測；數值基準日各自標於內文）

用證交所（TWSE）與櫃買中心（TPEX）的公開 JSON API 查台股每日收盤行情。不需要 API 金鑰或登入。資料是**每日收盤後**的統計，非盤中即時報價。日期欄位用民國年（1150911 = 2026-09-11）。

## 1. 上市全市場每日收盤（openapi.twse.com.tw）

```bash
curl -sm 30 'https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL' -o /tmp/twse.json
```

2026-09-12 實測：HTTP 200、約 319KB JSON 陣列，每筆一檔股票。**注意更新延遲**：這個 openapi 端點比 www.twse.com.tw 的 STOCK_DAY 慢約半天——收盤當晚 STOCK_DAY 已有當日資料時，STOCK_DAY_ALL 還停在前一交易日（2026-09-12 清晨實測：openapi 顯示 1150910，STOCK_DAY 已有 1150911）。要最新交易日資料用第 3 節的 STOCK_DAY 或 TPEX 端點。欄位：`Date`（民國年月日）、`Code`、`Name`、`TradeVolume`（成交股數）、`TradeValue`（成交金額）、`OpeningPrice`、`HighestPrice`、`LowestPrice`、`ClosingPrice`、`Change`（漲跌，字串，含 +/-）、`Transaction`（成交筆數）。

```bash
# 查台積電
jq -r '.[] | select(.Code=="2330") | "\(.Name) 收 \(.ClosingPrice) 漲跌 \(.Change) 量 \(.TradeVolume)"' /tmp/twse.json
# 最近交易日漲幅前 10：漲幅% = Change / (收盤 - Change)，不是 Change 的絕對值
# 收盤價或 Change 為空字串（停牌、無成交）、昨收為 0 的筆數直接略過
jq -r '[ .[]
  | (.ClosingPrice | tonumber? // null) as $c
  | (.Change | tonumber? // null) as $d
  | select($c != null and $d != null and ($c - $d) > 0)
  | {Code, Name, ClosingPrice, Change, pct: ($d / ($c - $d) * 100)} ]
  | sort_by(.pct) | reverse | .[0:10][]
  | "\(.Code) \(.Name) \(.ClosingPrice) \(.Change) \(.pct * 100 | round / 100)%"' /tmp/twse.json
```

## 2. 上櫃每日收盤（TPEX openapi）

```bash
curl -sm 30 'https://www.tpex.org.tw/openapi/v1/tpex_mainboard_daily_close_quotes' -o /tmp/tpex.json
```

2026-09-12 實測：HTTP 200、約 4.4MB JSON 陣列（最新交易日 1150911）。欄位：`Date`、`SecuritiesCompanyCode`、`CompanyName`、`Close`、`Change`、`Open`、`High`、`Low`、`Average`、`TradingShares` 等。

```bash
jq -r '.[0:3][] | "\(.SecuritiesCompanyCode) \(.CompanyName) 收 \(.Close)"' /tmp/tpex.json
```

## 3. 個股本月每日成交（www.twse.com.tw）

```bash
# date=當月任意一天（YYYYMMDD），回該月全部交易日
curl -sm 30 'https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date=20260901&stockNo=2330' -o /tmp/stock.json
```

2026-09-12 實測：HTTP 200、`stat:"OK"`，`fields` 為 日期/成交股數/成交金額/開盤價/最高價/最低價/收盤價/漲跌價差/成交筆數/註記，`data` 每列一個交易日（日期是民國 `115/09/01` 格式）。

```bash
jq -r '.data[] | "\(.[0]) 收 \(.[6]) 漲跌 \(.[7])"' /tmp/stock.json
```

## 4. 大盤與分類指數（MI_INDEX）

```bash
curl -sm 30 'https://www.twse.com.tw/exchangeReport/MI_INDEX?response=json&date=20260911&type=ALLBUT0999' -o /tmp/mi.json
```

2026-09-12 實測：HTTP 200、約 249KB。回傳 `tables` 陣列——第 0 個表是「價格指數」（發行量加權股價指數等的收盤指數、漲跌點數），其後是各類股成交統計。**注意：非交易日（週末、國定假日）查詢會回 `stat:"很抱歉，沒有符合條件的資料!"` 或空 tables**——遇到時往前回推到最近交易日再查。

## 錯誤與失敗時的處理

- **非交易日**：假日沒有資料不是錯誤。先查 STOCK_DAY_ALL（永遠回最新交易日），需要指定日時若回空，往前找最近交易日。
- **民國年換算**：API 的 `Date`/`日期` 是民國年，西元年 = 民國 + 1911（115 → 2026）。
- **數字是字串**：`ClosingPrice`、`Change` 等全是字串，jq 計算前要 `tonumber`；停牌或無成交的筆數收盤價是空字串，要略過。
- **漲幅排名不能直接排 `Change`**：`Change` 是價差（元），高價股會永遠排前面；漲幅% 要用 `Change / (收盤 - Change)`，昨收為 0 的筆數略過（2026-10-02 實測 1151001 的 1,380 筆，前 10 名漲幅 9.9%～10%，與依價差排序的結果不同）。
- **盤中資料**：本 API 盤中不更新；若使用者要即時報價，說明這是收盤統計資料。
- **HTTP 200 但內容是 HTML**：可能是 WAF 暫時攔截，換 openapi.twse.com.tw 主機（或反向）再試一次；兩個主機都失敗就回報資料源異常，不要靜默編造數字。

## English summary

Taiwan stock daily-close snapshots, keyless. TWSE (listed): `https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL` (all stocks, latest trading day, JSON) and `https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date=YYYYMMDD&stockNo=<code>` (one stock's daily rows for that month) plus `MI_INDEX` for index levels. TPEX (over-the-counter): `https://www.tpex.org.tw/openapi/v1/tpex_mainboard_daily_close_quotes`. All verified 2026-09-12. Note the openapi STOCK_DAY_ALL feed lags the www endpoints by about half a day (on 2026-09-12 early morning it still showed 1150910 while STOCK_DAY/MI_INDEX/TPEX already had 1150911) - for the very latest trading day use the STOCK_DAY or TPEX endpoints. Dates are ROC years (1150911 = 2026-09-11); numbers are strings; non-trading days return empty - roll back to the latest trading day. Daily-close statistics only, not intraday quotes.
