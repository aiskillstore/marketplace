---
name: taiwan-suspension
description: 天然災害停止上班上課查詢——颱風豪雨時各縣市是否停班停課（人事行政總處公告）。停班停課、今天有上班嗎、颱風假、明天要上課嗎的問題適用。免 API 金鑰、免登入。一般公司行號是否放假、學校個別公告不適用。
license: MIT
metadata:
  category: civic
  locale: zh-TW
---

# taiwan-suspension

> 實測日：2026-10-02（最近一次端對端實測；數值基準日各自標於內文）

查行政院人事行政總處的「天然災害停止上班及上課情形」官方公告頁。不需要 API 金鑰或登入。這是颱風天「到底放不放假」的唯一官方來源。

## 基本流程

1. 抓公告頁
2. 判斷目前狀態：只讀公告表格（`Table_Body`）的列；「無停班停課訊息」代表全國正常上班上課；有公告時逐列取「縣市名稱＋公告內容」，頁尾的備註、法條與發布時限說明不算公告
3. **逐字引用公告內容並註明查詢時間**——散布不實停班停課訊息是刑事責任（災害防救法第 53 條），絕對不能猜

### 1. 抓頁面

```bash
curl -sm 30 -A 'Mozilla/5.0' 'https://www.dgpa.gov.tw/typh/daily/nds.html' -o /tmp/nds.html
```

2026-09-19 實測：HTTP 200、約 15KB、UTF-8，頁面標題為「天然災害停止上班及上課情形查詢」。

### 2. 解析狀態

```python
import re, html
t = open('/tmp/nds.html', encoding='utf-8', errors='replace').read()
m = re.search(r'<tbody[^>]*class="Table_Body"[^>]*>(.*?)</tbody>', t, re.S | re.I)
if not m:
    raise SystemExit('找不到公告表格（頁面改版？），請直接看官網，不要猜')

def text(cell):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', cell))).strip()

announcements, normal = [], False
for row in re.findall(r'<tr[^>]*>(.*?)</tr>', m.group(1), re.S | re.I):
    cells = [text(c) for c in re.findall(r'<td[^>]*>(.*?)</td>', row, re.S | re.I)]
    if len(cells) == 1 and '無停班停課訊息' in cells[0]:
        normal = True                      # 全國正常
    elif len(cells) == 2 and cells[0] and cells[1]:
        announcements.append((cells[0], cells[1]))   # 縣市, 公告內容；備註列是單一儲存格，不會進來
if announcements:
    for city, msg in announcements:
        print(f'{city}：{msg}')
elif normal:
    print('全國正常上班上課（頁面無停班停課公告）')
else:
    print('無法判讀公告表格，請直接看官網，不要猜')
```

2026-10-02 實測：頁面顯示「無停班停課訊息。」，上面程式輸出「全國正常上班上課」，不會把頁尾的刑責與發布時限說明當成公告。有公告時的列格式（縣市＋內容兩格）以 `tests/test_documented_code.py` 的合成 fixture 驗證，**尚未用真實颱風日頁面實測**。

### 3. 回報原則

- 正常時：「人事行政總處目前沒有停班停課公告，全國正常上班上課（查詢時間 HH:MM）。」
- 有公告時：逐字貼出公告（如「高雄市：今天停止上班、停止上課」），附上查詢時間與資料來源。
- **公告時效**：全日停班停課通常前一日 19:00-22:00 發布；半天或當日補發可能清晨 04:30 前更新。用戶深夜問「明天放不放假」時，若尚未公告就如實說「還沒有公告」，不要預測。

## 錯誤與失敗時的處理

- **絕對禁止編造**：放假訊息錯誤涉及刑事責任（頁面明列刑法 211/360 條、災防法 53 條）。解析失敗或內容異常時，直接請用戶看官網，不要猜。
- **僅政府機關與學校基準**：民間公司是否放假依勞基法由雇主決定，此公告是參考基準，回報時說明。
- **編碼**：本頁為 UTF-8；同站其他歷史頁可能是 Big5，解析出亂碼先換編碼。
- **curl 失敗**：帶瀏覽器 UA 重試；持續失敗回報資料源異常，勿用舊記憶回答。
- **頁面只反映最新狀態**：歷史公告不在此頁，查過去颱風假要明說查不到。

## English summary

Taiwan official work/class suspension announcements (typhoon days), keyless. Fetch `https://www.dgpa.gov.tw/typh/daily/nds.html` (DGPA, UTF-8). If the page contains "無停班停課訊息" everything is normal; otherwise quote county announcements VERBATIM with the query time. Never predict or fabricate - spreading false suspension info is a criminal offense in Taiwan, and the page itself cites the statutes. Full-day announcements typically publish 19:00-22:00 the prior evening; late-night "tomorrow?" questions before that window get "no announcement yet". Verified 2026-09-19 (page live, showing no suspensions).
