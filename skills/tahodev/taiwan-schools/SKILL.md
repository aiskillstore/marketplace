---
name: taiwan-schools
description: 學校名錄與班級學生數查詢——教育部統計處校別資料（國小、國中的學校代碼、縣市鄉鎮、班級數、學生數）。某某國小在哪、學校有多少學生、偏鄉小校、學校代碼的問題適用。免 API 金鑰、免登入。大專校院明細、即時招生狀況不適用。
license: MIT
metadata:
  category: education
  locale: zh-TW
---

# taiwan-schools

> 實測日：2026-09-19（最近一次端對端實測；數值基準日各自標於內文）

抓教育部統計處的校別資料開放檔，查國小、國中的學校名錄與班級/學生數。不需要 API 金鑰或登入。

## 基本流程

1. 依階段挑檔案（國中全年份單檔；國小一學年度一檔）
2. 依縣市、鄉鎮、校名篩選
3. 回報校名、地址層級（縣市+鄉鎮）、班級數、學生數，附學年度

### 1. 檔案

```bash
# 國中:全學年度單檔(104-114 學年度)
curl -sm 30 -A 'Mozilla/5.0' -o /tmp/basej.csv 'https://stats.moe.gov.tw/files/opendata/basej.csv'
# 國小:一學年度一檔(103-114),如 114 學年度
curl -sm 30 -A 'Mozilla/5.0' -o /tmp/basec114.csv 'https://stats.moe.gov.tw/files/detail/114/114_basec.csv'
```

2026-09-19 實測：

- `basej.csv`（國民中學校別資料，data.gov.tw 資料集 6239）：HTTP 200、約 942KB、UTF-8 BOM、10,594 列，學年度 104-114 多年併存。欄位：學年度、縣市代碼、縣市名稱、學校代碼、學校名稱、班級數 7/8/9 年級、學生數各年級男女、畢業生數、專任教師數、職員數。
- `114_basec.csv`（國民小學校別資料，資料集 6240，103-114 每年一檔）：HTTP 200、約 297KB、2,663 校，欄位多一個「鄉鎮市區」。欄位順序（0 起）：0 學年度、1 縣市代碼、2 縣市名稱、3 鄉鎮市區、4 學校代碼、5 學校名稱、**6-11 = 1-6 年級班級數、12-23 = 1-6 年級男女學生數**（每年級男、女各一欄）、24-25 上學年畢業生、26-29 專任教師與職員。

實測範例：114 學年度私立淡江高中附設國小部（新北市淡水區，代碼 011301）1-6 年級各 2-3 班；國中檔有新北市立學校 114 學年度列。

### 2. 篩選範例

```python
import csv, io
rows = list(csv.reader(io.StringIO(open('/tmp/basec114.csv','rb').read().decode('utf-8-sig'))))
# 114 學年度台南市的國小
for r in rows[1:]:
    if r[2] == '臺南市':
        classes  = sum(int(x) for x in r[6:12]  if x.isdigit())  # 欄 6-11:1-6 年級班級數
        students = sum(int(x) for x in r[12:24] if x.isdigit())  # 欄 12-23:1-6 年級男+女學生數
        print(r[5], r[3], classes, '班', students, '名學生')
```

### 3. 回報範式

「114 學年度（2025-26）台南市有 N 所國小；例：○○國小（○○區）1-6 年級共 X 班、Y 名學生。」學年度記得換算：114 學年度 = 2025 年 8 月起到 2026 年 7 月。

## 錯誤與失敗時的處理

- **學年度≠西元年**：114 學年度是 2025-08~2026-07，回報時換算避免誤會。
- **UTF-8 BOM**：用 utf-8-sig 讀。
- **國中檔是多年併存**：同一學校每年一列，篩最新學年度（114）。
- **大專/高中不在本組檔案**：高中職與大專的校別檔名不同（stats.moe.gov.tw 另有目錄），本 skill 只收錄實測過的國中/國小檔；要其他階段先實測再說。
- **學校代碼是教育部代碼**：可用於跨資料集串接（如會考統計）。
- **curl 失敗**：帶瀏覽器 UA 重試；持續失敗回報資料源異常。

## English summary

Taiwan school directory & enrollment (MOE statistics), keyless. Junior high: `https://stats.moe.gov.tw/files/opendata/basej.csv` (one file, school years 104-114, 10,594 rows). Elementary: per-year files `https://stats.moe.gov.tw/files/detail/114/114_basec.csv` (school year 114 = Aug 2025-Jul 2026, 2,663 schools; files exist for 103-114, CSV and JSON). UTF-8 BOM. Columns (0-based, elementary file): 0 school year, 1 county code, 2 county name, 3 district, 4 school code, 5 school name, 6-11 class counts for grades 1-6, 12-23 student counts by grade and gender (male/female pair per grade), 24-25 last-year graduates, 26-29 teachers/staff. Verified 2026-09-19. School-year vs calendar-year conversion required in answers; high schools/universities use different files not covered here.
