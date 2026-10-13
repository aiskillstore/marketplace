---
name: taiwan-oil-price
description: 台灣中油油價查詢——92/95/98 無鉛汽油與超級柴油的每週牌價（官方 open data JSON）與近 7 週歷史。油價、汽油多少錢、柴油價格、加油、下週油價的問題適用。免 API 金鑰、免登入。即時國際油價、預測漲跌、加油站個別售價不適用。
license: MIT
metadata:
  category: finance
  locale: zh-TW
---

# taiwan-oil-price

> 實測日：2026-09-21（最近一次端對端實測；數值基準日各自標於內文）

用台灣中油（CPC）官方 open data 查 92/95/98 無鉛汽油與超級柴油的每週牌價；歷史週次用官網歷史油價頁。不需要 API 金鑰或登入。

## 基本流程

1. 抓官方 open data JSON，篩「汽柴油零售」取得最新公告牌價
2. 看 `牌價生效日期` 判斷是「本週」還是「下週」價（週日中午公告次週牌價）
3. 需要歷史週次時才抓歷史油價頁

### 1. 抓官方 open data（主路徑）

```bash
curl -sm 30 'https://vipmbr.cpc.com.tw/opendata/sixtypeoillistprice' -o /tmp/oil.json
```

2026-09-20 實測：HTTP 200、約 17.5KB、51 列 JSON 陣列，不需瀏覽器 UA、免金鑰。這是中油刊登在 data.gov.tw（資料集 166537「台灣中油公司各項油品牌價」）的官方結構化資料。欄位：`型別名稱`、`產品名稱`、`參考牌價_金額`、`計價單位`、`牌價生效日期`（民國 yyyMMdd）等。

```bash
jq -r '.[] | select(.型別名稱=="汽柴油零售") | "\(.產品名稱) \(.參考牌價_金額) \(.牌價生效日期)"' /tmp/oil.json
```

2026-09-20 實測輸出（汽柴油零售 7 列）：98 無鉛 34.7、95 無鉛 32.7、92 無鉛 31.2、酒精汽油 32.7、超級柴油 29.9（元/公升，生效 1150921）；海運輕/重柴油單位是元/公秉，不是零售牌價。

### 2. 生效日期判讀（重要）

中油**週日中午公告次週牌價、週一零時生效**。所以週日下午到週日半夜查到的 `牌價生效日期` 會是**明天（下週）**：這是已公告的下週牌價，可以直接回答「下週會漲還是跌」——跟舊制「不能預測」不同，公告後就是確定值。回報時寫清楚生效日：「下週（09/21 生效）牌價：92 無鉛 31.2 元……」。生效日期還沒到之前，本週仍沿用上一週價格。民國年換算：1150921 = 2026-09-21（民國 + 1911）。

### 3. 歷史週次（備援路徑）

近 7 週的歷史牌價用官網歷史頁：

```bash
curl -sm 30 -A 'Mozilla/5.0' 'https://www.cpc.com.tw/historyprice.aspx?n=2890' -o /tmp/cpc.html
```

```python
import re, html
t = open('/tmp/cpc.html', encoding='utf-8', errors='replace').read()
rows = re.findall(r'<tr[^>]*>(.*?)</tr>', t, re.S)
for r in rows:
    cells = [html.unescape(re.sub(r'<[^>]+>', '', c)).strip()
             for c in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', r, re.S)]
    cells = [c for c in cells if c]
    if cells and re.match(r'\d+/', cells[0]):   # 資料列：調價日期、92、95、98、超柴
        print(cells)  # ['115/09/14', '31.2', '32.7', '34.7', '29.9']
```

2026-09-19 實測：HTTP 200、約 134KB、近 7 週（需瀏覽器 UA）；2026-09-14 當週 92=31.2、95=32.7、98=34.7、超柴 29.9，與 open data 一致。

## 錯誤與失敗時的處理

- **open data 失敗（5xx/逾時/非 JSON）**：退回歷史油價頁解析第一列；兩路都失敗就回報資料源異常，不要編造數字。
- **歷史頁結構變動**：CPC 改版會讓表格解析失敗；解析不到資料列時如實回報。
- **只列近 7 週**：更早的歷史需分頁 POST 查詢（本 skill 範圍外），如實說明。
- **台塑石化另有牌價**：本資料源是中油；用戶指名台塑時說明差異（通常差 0.1 元）。
- **燃料油、天然氣、液化石油氣也在同一 JSON**：篩 `型別名稱` 取用；單位各異（公升/公秉/立方公尺），回報時帶上 `計價單位`。

## English summary

Taiwan CPC fuel prices, keyless. Primary path: official open-data JSON `https://vipmbr.cpc.com.tw/opendata/sixtypeoillistprice` (registered on data.gov.tw dataset 166537) - a 51-row array covering retail gasoline/diesel plus fuel oil, gas and LPG; filter `型別名稱=="汽柴油零售"` for 92/95/98 unleaded and premium diesel (元/公升). Verified 2026-09-20: HTTP 200, no UA needed; 92=31.2, 95=32.7, 98=34.7, diesel=29.9. CPC announces next week's prices Sunday noon, effective Monday 00:00, so from Sunday afternoon the JSON's `牌價生效日期` (ROC yyyMMdd, +1911) is next week - announced prices are final, report them with the effective date. History (last ~7 weeks): parse the first rows of `https://www.cpc.com.tw/historyprice.aspx?n=2890` with a browser UA. If the JSON fails, fall back to the history page; never invent numbers.
