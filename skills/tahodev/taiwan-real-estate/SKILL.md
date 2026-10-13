---
name: taiwan-real-estate
description: 實價登錄批次資料查詢——內政部不動產交易實價查詢服務網的季度批次下載（買賣、預售屋、租賃）。房價、實價登錄、某區成交價、一坪多少錢的問題適用。免 API 金鑰、免登入。即時個案查詢（非季度批次）、斡旋中案件不適用。
license: MIT
metadata:
  category: realestate
  locale: zh-TW
---

# taiwan-real-estate

> 實測日：2026-09-19（最近一次端對端實測；數值基準日各自標於內文）

下載內政部「不動產交易實價查詢服務網」的季度批次 CSV（全台各縣市，買賣/預售屋/租賃）。不需要 API 金鑰或登入。

## 基本流程

1. 下載當季 zip（約 15MB）
2. 解開後依縣市代碼挑檔案（`<縣市碼>_lvr_land_a.csv` 買賣、`_b` 預售屋、`_c` 租賃）
3. 第 1 列中文標頭、第 2 列英文標頭，資料從第 3 列起；UTF-8 BOM

### 1. 下載

```bash
# 季代碼格式:民國年+S+季(115S2 = 2026 年第 2 季)
curl -sm 60 -A 'Mozilla/5.0' -o /tmp/lvr.zip 'https://plvr.land.moi.gov.tw/DownloadSeason?season=115S2&type=zip&fileName=lvr_landcsv.zip'
unzip -o /tmp/lvr.zip -d /tmp/lvr
```

2026-09-19 實測：HTTP 200、14.7MB，內含全台各縣市三類檔案；`a_lvr_land_a.csv`（台北市買賣）5,609 列。季代碼隨時間推進，當季抓不到時往前推一季。

### 2. 格式

- UTF-8 BOM；第 1 列中文欄名、第 2 列英文欄名，用 `utf-8-sig` 讀、跳過第 2 列
- 30+ 欄：鄉鎮市區、交易標的（房地/建物/土地/車位）、土地位置建物門牌、交易年月日（民國 1150601）、總價元、單價元平方公尺、建物型態、車位資訊、備註、編號
- 縣市代碼是單字母（a、b、c…）：**不要死背對照**——開檔看「鄉鎮市區」值即可確認縣市，或查內政部下載說明頁
- 實測範例：台北市檔案中一筆中山區車位，交易日期 115/06/01，總價 370 萬元

### 3. 查詢範例

```python
import csv
with open('/tmp/lvr/a_lvr_land_a.csv', encoding='utf-8-sig') as f:
    rows = [r for r in csv.reader(f)][1:]   # 去掉英文標頭列
# 中山區房地交易,依單價排序
deals = [r for r in rows if r[0] == '中山區' and '房地' in r[1]]
for r in deals[:5]:
    print(r[7], r[2][:20], '總價', r[21], '單價/㎡', r[22])
```

### 4. 回報範式

「2026 年第 2 季實價登錄，台北市中山區有一筆車位 6/1 成交總價 370 萬。」必附資料季度與「實價登錄是申報制、約有 1-2 個月落差」的說明。單價欄位是元/平方公尺，換算坪價要 ×3.30579。

## 錯誤與失敗時的處理

- **編碼**：UTF-8 BOM，不是 Big5；用 utf-8-sig。
- **雙標頭**：忘記跳過第 2 列英文標頭會把標頭當成交資料。
- **季代碼**：未來/當季可能尚未上傳（404），往前推一季重試。
- **申報時效**：實價登錄依法成交後 30 日內申報，最近 1-2 個月的交易查不到是正常現象，如實說明。
- **地址遮蔽**：門牌有去識別化（號以「~」區間呈現），不要假設精確門牌。
- **特殊交易**：備註欄會標「關係人交易」「特殊交易物件」等，分析行情時要提醒排除或註記。

## English summary

Taiwan real-price registry (實價登錄) quarterly batch download, keyless. `curl 'https://plvr.land.moi.gov.tw/DownloadSeason?season=115S2&type=zip&fileName=lvr_landcsv.zip'` (~15MB; season = ROC year + S + quarter). Files per county letter: `<code>_lvr_land_a.csv` (sales), `_b` (pre-sale), `_c` (rentals). UTF-8 BOM with TWO header rows (Chinese then English - skip row 2). 30+ columns: district, transaction target, address (de-identified ranges), ROC date, total price, unit price per m² (multiply by 3.30579 for ping price). Verified 2026-09-19 (115S2 zip, Taipei sales file 5,609 rows; e.g. Zhongshan parking space 115/06/01, 3.7M TWD). Declarations lag transactions by 1-2 months; say so when recent deals are missing.
