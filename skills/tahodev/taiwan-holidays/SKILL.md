---
name: taiwan-holidays
description: 查台灣政府行政機關辦公日曆表——國定假日、連假、補班日。放假嗎、補班嗎、下個連假、春節幾號、國慶連假、人事行政總處日曆的問題適用。免 API 金鑰、免登入。公司行號自訂行事曆、學校行事曆的細節不適用（學校另有規定）。
license: MIT
metadata:
  category: government
  locale: zh-TW
---

# taiwan-holidays

> 實測日：2026-09-12（最近一次端對端實測；數值基準日各自標於內文）

用行政院人事行政總處公布的「政府行政機關辦公日曆表」查台灣的放假日與補班日。不需要 API 金鑰或登入。資料來源：https://www.dgpa.gov.tw/informationlist?uid=30 與 data.gov.tw 資料集 14718（106 年至 116 年的 CSV 都在這裡）。

## 主要方式：結構化 CSV（所有年份，含當年度）

資料集 https://data.gov.tw/dataset/14718 有 106-116 年的 CSV。欄位：`西元日期,星期,是否放假,備註`（西元日期為 YYYYMMDD；是否放假 0=上班、2=放假；補班日為 0 且備註「補行上班」；假日遇例假日順延的補假備註「補假」）。**注意：自 114 年下半年起官方已廢除「調整上班日補行上班」制度**，115 年起原則上沒有補班日。

115 年（2026）CSV（2026-09-12 實測 HTTP 200、6,499 bytes、UTF-8 含 BOM、CRLF）：
```bash
curl -sm 30 -o /tmp/cal115.csv 'https://www.dgpa.gov.tw/FileConversion?filename=dgpa/files/202506/a52331bd-a189-466b-b0f0-cae3062bbf74.csv&nfix=&name=115.csv'
# 放假日一覽
awk -F, 'NR>1 && $3==2 {print $1, $2, $4}' /tmp/cal115.csv
# 補班日（檔案是 CRLF，比對最後一欄前先去 \r；115 年無補班日）
awk -F, 'NR>1{sub(/\r$/,"",$4)} $4=="補行上班" {print $1, $2}' /tmp/cal115.csv
```
2026-09-12 實測：365 列，平日放假日 16 天（1/1、2/16-20 春節、2/27、4/3、4/6、5/1、6/19、9/25、9/28、10/9、10/26、12/25），放假日總數 120，與人事總處公告一致。

116 年（2027）CSV 也已存在：`https://www.dgpa.gov.tw/FileConversion?filename=dgpa/files/202607/f538b1ff-ba60-4c63-9477-10db8e6612d1.csv&nfix=&name=116.csv`（2026-09-12 實測 200、UTF-8 含 BOM）。

114 年（2025）**要用更新版**：官方在 114/10/20 更新過日曆（新增教師節、光復節、行憲紀念日放假與補假），舊版 CSV 會漏答 2025 年 9 月之後的假日。更新版（2026-09-12 實測 200、6,029 bytes、**Big5 編碼**、CRLF）：
```bash
curl -sm 30 'https://www.dgpa.gov.tw/FileConversion?filename=dgpa/files/202510/b84cb88a-803c-4621-a843-d637b2775615.csv&nfix=&name=114.csv' | iconv -f big5 -t utf-8 > /tmp/cal114.csv
awk -F, 'NR>1{sub(/\r$/,"",$4)} ($1=="20250929"||$1=="20251024"||$1=="20251225")' /tmp/cal114.csv
# 預期輸出三列都是 2（放假）：9/29 補假、10/24 補假、12/25 行憲紀念日
```

**編碼依檔案而不同**（2026-09-12 實測）：115、116 與舊版 114 是 UTF-8 含 BOM；114 更新版是 Big5。處理前先 `file` 或 `head -c` 確認——看到「西元日期」亂碼就 `iconv -f big5 -t utf-8`。106-113 年的 CSV 同樣在資料集 14718 頁面，連結格式相同，編碼依檔案確認。

## 備援與交叉驗證：官方 xlsx 月曆

當年度 xlsx（115 年）：https://www.dgpa.gov.tw/uploads/dgpa/files/202511/1d88999f-f893-47dd-8757-ee7df20765a5.xlsx （2026-09-12 實測 200、19,770 bytes）。放假日以**粉紅底色**標示（週六、週日與國定假日的儲存格 fill 為 FFFF99FF，樣式 id 31/34/38；一般上班日無底色、樣式 9）。CSV 抓不到或要驗證時用這個：

```bash
curl -sm 30 -o /tmp/cal.xlsx 'https://www.dgpa.gov.tw/uploads/dgpa/files/202511/1d88999f-f893-47dd-8757-ee7df20765a5.xlsx'
```

```python
import zipfile, re, bisect, xml.etree.ElementTree as ET
NS='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
z=zipfile.ZipFile('/tmp/cal.xlsx')
ss=[t.text or '' for t in ET.fromstring(z.read('xl/sharedStrings.xml')).iter(NS+'t')]
sheet=ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
def ci_of(ref):
    s=re.match(r'([A-Z]+)',ref).group(1); n=0
    for ch in s: n=n*26+ord(ch)-64
    return n-1
HDR=[3,17,31,45]          # 四個月份橫帶的標題列（1 起始列號；新版檔案若有變動，找含「月」字的列）
RED={'31','34','38'}      # 放假（粉紅底色 fillId=2）儲存格樣式 id；一般上班日是 '9'（無底色）
out=[]
for c in sheet.iter(NS+'c'):
    ref=c.get('r'); ri=int(re.search(r'\d+',ref).group()); ci=ci_of(ref)
    v=c.find(NS+'v')
    if v is None: continue
    val=(ss[int(v.text)] if c.get('t')=='s' else v.text).strip()
    if not re.fullmatch(r'\d{1,2}',val) or ci<1: continue
    block=(ci-1)//7; wd=(ci-1)%7     # 每橫帶 3 個月、每月 7 欄（日一二三四五六）
    if block>2: continue
    band=bisect.bisect_right(HDR,ri)-1
    if not 0<=band<=3: continue
    out.append((band*3+block+1, int(val), wd, c.get('s','0') in RED))
# out: (月, 日, 星期(0=日), 是否放假)
```

2026-09-12 實測：115 年 xlsx 解析出 365 天，星期全部與實際日期吻合，結果與 115 CSV 完全一致（LibreOffice 渲染目視確認：圖例為「□上班日／粉紅＝放假日」）。**月份不能讀標題文字**：十一月、十二月的「十」「一」分在兩個儲存格，直接用 `band*3+block+1` 推算最穩。

## 錯誤與失敗時的處理

- **CSV 連結 404 或要其他年份**：回資料集頁 https://data.gov.tw/dataset/14718 取最新 FileConversion 連結（每年一檔，檔名含年份；注意有「Google 行事曆專用」的另一變體，欄位不同，本技能用的是一般版）。
- **亂碼**：編碼依檔案不同（見上），先確認再決定要不要 iconv；另外檔案是 CRLF，awk 比對最後一欄（備註）前先 `sub(/\r$/,"",$4)`。
- **114 年查到 9 月後假日是上班**：用了舊版 CSV，換 1141020 更新版連結。
- **xlsx 連結 404**：人事總處每年換檔案 GUID。回列表頁 https://www.dgpa.gov.tw/informationlist?uid=30 找當年度公告取附件網址；解析邏輯不變，但要重驗 `HDR`（含「月」的列號）與 `RED`（粉紅底色樣式 id）兩個常數——驗法：1 月 1 日必須是有底色（RED 樣式）且星期正確（115 年為星期四；其他年份以該年實際星期為準）。
- **學校、銀行、股市的休市日不同**：本技能是行政機關日曆；股市休市請用 taiwan-stock 的交易日資料反推，不要混用。
- 重要判斷（請假、排程截止日）請提醒使用者回 https://www.dgpa.gov.tw 確認原文。

## English summary

Looks up Taiwan's official government work calendar (DGPA): national holidays, long weekends, and makeup workdays. Keyless. Primary path: the structured CSVs (西元日期,星期,是否放假,備註; 0=workday, 2=off, makeup Saturdays are 0 + 補行上班, deferred-holiday makeups are 補假) on data.gov.tw dataset 14718, which covers ROC 106-116 INCLUDING the current year - ROC 115 (2026) and even 116 (2027) CSVs exist (verified 2026-09-12: 115 = 365 rows, 16 weekday holidays, 120 total days off, matching the DGPA announcement; the makeup-workday system was abolished from late 2025, so 115+ has none). Use the UPDATED ROC-114 CSV (1141020更新, Big5, needs iconv) - the older 114 CSV misses the newly added Sep-Dec 2025 holidays. Encoding varies per file (115/116 UTF-8-BOM, updated 114 Big5; check with `file`); all are CRLF, so strip \r before matching the last column. Backup/cross-check: the current-year xlsx calendar (holidays are pink-filled cells, style ids 31/34/38 with fill FFFF99FF; month = band*3+block+1) parsed with the python3-stdlib recipe in this file - its 365-day result matches the CSV exactly (visually confirmed via render 2026-09-12). School/bank/stock-market calendars differ - do not mix.
