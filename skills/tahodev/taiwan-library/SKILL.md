---
name: taiwan-library
description: 圖書館名錄查詢——國家圖書館彙編的全台 5,200+ 圖書館清單（公共圖書館、學校圖書館、專門圖書館）。附近圖書館、某某圖書館地址、公共圖書館有哪些的問題適用。免 API 金鑰、免登入。館藏查詢（借書）、開館時間即時狀態不適用。
license: MIT
metadata:
  category: culture
  locale: zh-TW
---

# taiwan-library

> 實測日：2026-09-19（最近一次端對端實測；數值基準日各自標於內文）

下載國家圖書館的「圖書館名錄」CSV，查全台各類圖書館的名稱、縣市、地址。不需要 API 金鑰或登入。

## 基本流程

1. 下載 CSV（**Big5 編碼**）
2. 依縣市、區域、館名或類型篩選
3. 回報館名、地址、類型

### 1. 下載

```bash
curl -sm 30 -A 'Mozilla/5.0' -o /tmp/lib.csv 'https://www.ncl.edu.tw/OpenDataFile/0Q112417873324994331/4cbfc49a-1127-45b1-9da6-113ebb444a12'
```

2026-09-19 實測：HTTP 200、約 477KB、**Big5 編碼**、5,207 館。欄位：序號、中文館名、郵遞區號、縣市、區域、中文地址、圖書館類型。

### 2. 類型分佈（2026-09-19 實測）

以下為類型欄**完全相符**的館數：國民小學圖書館 2,644、國民中學 747、公共圖書館 610、高級中等學校 535、專門圖書館 438、大專校院 192、國家圖書館 2。「公共圖書館」另有複合值 34 館（如「專門圖書館, 公共圖書館」）；本 skill 的篩選方式（**包含比對**）= 610 + 34 = **644 館**。引用數字時說明口徑。

### 3. 解析範例

```python
import csv, io
raw = open('/tmp/lib.csv', 'rb').read().decode('big5', errors='replace')  # Big5!
rows = list(csv.reader(io.StringIO(raw)))
pubs = [r for r in rows[1:] if len(r) >= 7 and '公共圖書館' in r[6] and r[3] == '臺北市']
for r in pubs[:5]:
    print(r[1], '-', r[5])
```

### 4. 回報範式

「台北市有 N 間公共圖書館（含分館），例如國家圖書館（中正區中山南路 20 號）。」用戶問「能不能借某本書」時：名錄沒有館藏資料，引導至各館館藏查詢系統（如台北市立圖書館館藏查詢）。

## 錯誤與失敗時的處理

- **Big5 編碼**：用 UTF-8 讀會全亂碼；`decode('big5', errors='replace')` 或 `iconv -f big5`。
- **名錄不含開館時間與館藏**：只是清單；如實說明並引導各館官網。
- **下載網址可能換發**：NCL 的 OpenDataFile URL 帶一次性路徑感，失效時回 data.gov.tw 資料集 8306 重取新連結。
- **複合類型**：比對類型用「包含」而非「等於」。
- **學校圖書館多數不對外開放**：回報公共圖書館時不要把學校圖書館算進對外可用的清單。

## English summary

Taiwan library directory, keyless. `curl 'https://www.ncl.edu.tw/OpenDataFile/0Q112417873324994331/4cbfc49a-1127-45b1-9da6-113ebb444a12'` - BIG5-encoded CSV, 5,207 libraries (verified 2026-09-19). Columns: id, name, postal code, county, district, address, type. Type counts (exact match): elementary 2,644 / junior-high 747 / public 610 / senior-high 535 / special 438 / university 192 / national 2. Composite values exist ("專門圖書館, 公共圖書館", 34 libraries), so contains-matching for public libraries gives 644 - state which count you are quoting, and match with "contains", not equality. Directory only: no opening hours, no holdings; school libraries are not open to the public. If the download URL rots, re-fetch the link from data.gov.tw dataset 8306.
