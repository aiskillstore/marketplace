---
name: taiwan-produce
description: 農產品批發市場行情查詢——全台 24 個批發市場蔬果的上價中價下價平均價與交易量。菜價、水果價格、高麗菜多少錢、香蕉行情、菜很貴的問題適用。免 API 金鑰、免登入。零售價（全聯、菜市場攤販實售價）不適用——這是批發行情。
license: MIT
metadata:
  category: agriculture
  locale: zh-TW
---

# taiwan-produce

> 實測日：2026-09-19（最近一次端對端實測；數值基準日各自標於內文）

抓農業部開放資料的「農產品交易行情」CSV，查全台果菜批發市場的即時行情。不需要 API 金鑰或登入。

## 基本流程

1. 下載 CSV（近 4 日全量，約 8,700 筆）
2. 依作物名稱與市場篩選
3. 回報時註明交易日期與「這是批發價」，並區分上/中/下/平均價

### 1. 下載 CSV

```bash
curl -sm 40 -A 'Mozilla/5.0' 'https://data.moa.gov.tw/Service/OpenData/FromM/FarmTransData.aspx?FOTT=CSV&IsTransData=1&UnitId=037' -o /tmp/produce.csv
```

2026-09-19 實測：HTTP 200、約 608KB、UTF-8 BOM、8,782 筆，涵蓋 4 個交易日（115.09.16-19，民國年）、24 個市場（台北一、台北二、三重區、台中市…）、944 種作物。欄位：交易日期、種類代碼、作物代號、作物名稱、市場代號、市場名稱、上價、中價、下價、平均價、交易量（公斤）。

### 2. 篩選範例

```python
import csv, io
raw = open('/tmp/produce.csv', 'rb').read().decode('utf-8-sig')   # BOM 要處理
rows = [r for r in csv.reader(io.StringIO(raw)) if len(r) >= 11]
latest = max(r[0] for r in rows[1:])
for r in rows[1:]:
    if r[0] == latest and r[3] == '香蕉' and r[5] == '台北二':
        print(f'{r[5]} {r[3]} 上{r[6]} 中{r[7]} 下{r[8]} 均{r[9]} 量{r[10]}kg')
```

2026-09-19 實測範例：115.09.18 台北二市場香蕉 上價 52.2、中價 26.8、下價 16.4、平均 29.8 元/公斤，交易量 11,047 公斤。

### 3. 回報範式

「9/18 台北二市場香蕉批發行情：平均價每公斤 29.8 元（上價 52.2／下價 16.4）。」跨市場比較或趨勢問題可對同作物多市場、多日列點。**零售價會明顯高於批發價**，用戶拿超市價格對比時要說明這是批發行情。

## 錯誤與失敗時的處理

- **UTF-8 BOM**：首欄會黏 \ufeff，用 utf-8-sig 解碼。
- **民國年日期**：115.09.18 = 2026-09-18；跨日比較先換算或用字串排序（格式固定沒問題）。
- **當日資料可能不完整**：交易日的資料邊交易邊上上傳，當天的量比價可能還在變；回報當日數字時註明「資料持續更新中」。
- **作物名要精確**：944 種作物名各異（如 甘藍 vs 高麗菜俗名），查不到時先列出相近名稱讓用戶確認，不要自行當成同一種。
- **缺列或欄位不足**：偶發短列（len<11）直接跳過。
- **curl 失敗/空檔**：重試一次；持續失敗回報資料源異常，不要用印象中的菜價回答。

## English summary

Taiwan wholesale produce prices, keyless. Download `https://data.moa.gov.tw/Service/OpenData/FromM/FarmTransData.aspx?FOTT=CSV&IsTransData=1&UnitId=037` (UTF-8 BOM CSV, ~8.8K rows, 4 trading days, 24 wholesale markets, 944 crops). Columns: date (ROC calendar), crop code/name, market code/name, high/mid/low/avg price per kg, volume kg. Filter by crop and market. Verified 2026-09-19 (e.g. banana at Taipei-2 on 115.09.18: avg 29.8 TWD/kg, 11,047 kg). These are WHOLESALE prices - retail runs higher; same-day rows update intraday; decode with utf-8-sig.
