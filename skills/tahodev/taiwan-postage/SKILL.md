---
name: taiwan-postage
description: 中華郵政郵資查詢——國內信函、明信片、掛號、限時、包裹、國際郵件的資費表。寄信多少錢、郵資、掛號費、寄包裹運費、明信片資費的問題適用。免 API 金鑰、免登入。郵件追蹤、郵局據點查詢不適用。
license: MIT
metadata:
  category: civic
  locale: zh-TW
---

# taiwan-postage

> 實測日：2026-09-19（最近一次端對端實測；數值基準日各自標於內文）

抓中華郵政官網的資費表頁面，回答「寄這個要多少錢」。不需要 API 金鑰或登入。

## 基本流程

1. 依郵件種類選資費表頁面（見下方頁面清單）
2. 抓頁面解析表格，依重量級距與種類（普通/限時/掛號）取資費
3. 回報時註明級距與種類；郵資會調整，回答以抓到的頁面為準

### 頁面清單（2026-09-19 實測可達）

| 內容 | URL |
|---|---|
| 簡明國內函件資費表 | https://www.post.gov.tw/post/internet/Postal/index.jsp?ID=2020106 |
| 國內函件資費查詢(試算) | https://www.post.gov.tw/post/internet/Postal/index.jsp?ID=2020105 |
| 國內包裹資費表 | https://www.post.gov.tw/post/internet/Postal/index.jsp?ID=2030103 |
| 國內快捷郵件資費表 | https://www.post.gov.tw/post/internet/Postal/index.jsp?ID=2010103 |
| 國際函件資費表 | https://www.post.gov.tw/post/internet/Postal/index.jsp?ID=2020204 |

### 1. 抓簡明國內函件資費表

```bash
curl -sm 30 -A 'Mozilla/5.0' 'https://www.post.gov.tw/post/internet/Postal/index.jsp?ID=2020106' -o /tmp/post.html
```

2026-09-19 實測：HTTP 200、約 224KB、UTF-8，含 6 張表：信函/印刷物分重量級距表（普通 8/16/24/40/72/112/160 元，掛號 +20 元起）、小包表（每 100 公克一級）、明信片每件 5 元（限時 12 元）、郵簡每件 6 元、特種資費表（掛號費 20 元、限時費 7 元、存證信函首頁 50 元…）、便利袋/箱售價與資費（1 號袋 36 元…）。

### 2. 解析建議

表格結構是巢狀 `<td>`，直接 HTML 解析較穩：去標籤後依「種類 | 計費標準 | 各級距金額」對齊。常見問答可直接記重點：

- 國內普通信函不逾 20 公克：**8 元**（2026-09-19 實測頁面）
- 明信片：每件 5 元；郵簡：每件 6 元
- 掛號另加掛號費 20 元；限時另加 7 元
- 逾 2 公斤每續重 1 公斤加收 48 元（信函類）

### 3. 回報範式

「寄國內普通信函，20 公克以內 8 元；掛號的話再加 20 元掛號費，共 28 元。」國際件或包裹引導對應資費表頁面；重量不明時先問重量。

## 錯誤與失敗時的處理

- **資費會調整**：永遠以抓下來的頁面為準，回報附「依中華郵政資費表（查詢日期）」；抓不到就說抓不到，不要背舊郵資。
- **頁面是 JSP 選單結構**：ID=2010104 之類的頁面是目錄不是表格，要用上表的直接連結。
- **編碼 UTF-8**，但全形數字與空白多，解析時 normalize。
- **國際資費分區複雜**：國際函件依地區分區計費，頁面有分區表；不確定分區就如實說並給頁面連結。
- **curl 失敗**：帶瀏覽器 UA 重試；持續失敗回報資料源異常。

## English summary

Taiwan Chunghwa Post postage lookup, keyless. Key page: simplified domestic letter rates at `https://www.post.gov.tw/post/internet/Postal/index.jsp?ID=2020106` (UTF-8, 6 tables: letters by weight tier, small packets, postcards 5 TWD, letter sheets 6 TWD, surcharges - registration +20, timed +7, convenience box prices). Verified 2026-09-19 (domestic letter <=20g ordinary = 8 TWD; registered adds 20 TWD). Related pages for parcels/express/international listed in the skill. Always answer from the fetched page with query date - rates change; never recite remembered postage.
