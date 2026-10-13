---
name: postal-address
description: 台灣郵遞區號與地址英譯——3 碼郵遞區號查詢、縣市鄉鎮/村里/路街的中英對照（漢語拼音）。郵遞區號、地址英文怎麼寫、路名拼音、巷弄英譯的問題適用。免 API 金鑰、免登入。完整 3+3 投遞區段查詢不適用（見限制一節）。
license: MIT
metadata:
  category: government
  locale: zh-TW
---

# postal-address

> 實測日：2026-09-20（最近一次端對端實測；數值基準日各自標於內文）

用中華郵政官網下載區的公開對照表查郵遞區號（前 3 碼）與地址英譯。不需要 API 金鑰或登入。下載區總頁：https://www.post.gov.tw/post/internet/Download/all_list.jsp?ID=2201 （2026-09-12 實測可連）。**TXT 檔是 Big5 編碼**，處理前先 `iconv -f big5 -t utf-8`；XML 檔（County_h_10906.xml 等）是 UTF-8，**不要**過 iconv，會轉壞。

## 1. 3 碼郵遞區號（各鄉鎮市區）

```bash
curl -sm 30 'https://www.post.gov.tw/post/download/103.12.25-%E8%87%BA%E7%81%A3%E5%9C%B0%E5%8D%80%E9%83%B5%E9%81%9E%E5%8D%80%E8%99%9F%E5%89%8D3%E7%A2%BC%E4%B8%80%E8%A6%BD%E8%A1%A8.txt' | iconv -f big5 -t utf-8 > /tmp/zip3.txt
grep '大安' /tmp/zip3.txt
```

2026-09-12 實測：HTTP 200、純文字表格，依縣市分欄列出鄉鎮市區與 3 碼（例：台北市大安區 106）。另有經緯度版（XML）：`https://www.post.gov.tw/post/download/1050812_%E8%A1%8C%E6%94%BF%E5%8D%80%E7%B6%93%E7%B7%AF%E5%BA%A6%28toPost%29.xml`。

## 2. 地址英譯對照（漢語拼音，三層）

```bash
# 縣市鄉鎮中英對照（XML，54KB，UTF-8 編碼，直接讀取即可）
curl -sm 30 -o /tmp/county.xml 'https://www.post.gov.tw/post/download/County_h_10906.xml'
# 村里文字巷中英對照（TXT，約 222KB）
curl -sm 30 'https://www.post.gov.tw/post/download/%E6%9D%91%E9%87%8C%E6%96%87%E5%AD%97%E5%B7%B7%E4%B8%AD%E8%8B%B1%E5%B0%8D%E7%85%A7.TXT' | iconv -f big5 -t utf-8 > /tmp/village.txt
# 路街中英對照（TXT，約 743KB，115/01/16 更新）
curl -sm 30 'https://www.post.gov.tw/post/download/%E4%B8%AD%E8%8B%B1%E6%96%87%E8%A1%97%E8%B7%AF%E5%90%8D%E7%A8%B1%E5%B0%8D%E7%85%A7%E6%AA%941130401.TXT' | iconv -f big5 -t utf-8 > /tmp/roads.txt
```

2026-09-12 實測：三個檔都 HTTP 200。路街檔是兩欄 CSV 格式 `中文路名,English Name`（例：`一工路,Yigong Rd.`、`一心二路,Yixin 2nd Rd.`）。組英文地址時順序反轉（英文由小到大）：路街拼音 + 鄉鎮拼音 + 縣市拼音 + 郵遞區號 + Taiwan (R.O.C.)。

```bash
grep '^中正路,' /tmp/roads.txt | head -5
# 村里檔是引號 CSV 格式（"中文名,""English Name"""），且不含縣市/鄉鎮前綴，用村里名本身查：
grep '^"大安里,"' /tmp/village.txt | head -3
```

## 資料特性（2026-09-12 全檔掃描）

- 路街檔 30,031 列、村里檔 8,369 列，格式皆良好（無缺譯、無亂碼）。
- 路街檔的中文路名**不含縣市前綴**，同名路街有 21 組重複（如多個「中正路」）——只給路名時要提醒使用者可能有多個縣市。
- 村里檔的英文譯名有 220 列用彎撇號（U+2019，如 San’an Vil.），不是 ASCII 單引號；路街檔有 2 列英文欄含全形數字（如 Nanshi Sec. １）。

## 限制（要對使用者誠實說明）

- **完整 3+3 六碼投遞區段**：官方只透過 Windows 版「3+3 郵遞區號應用系統」（rar 安裝檔）與需申請的 Web Service 提供，沒有免登入的機讀全表。需要六碼時，導使用者到官方查詢頁 https://www.post.gov.tw 的「郵遞區號查詢」，本技能不要自己猜後三碼。
- 前 3 碼表是 103 年版本：行政區整併後的邊界個案（如部分縣市合併重劃）以官方查詢頁為準。2026-09-20 確認下載區總頁仍只有 103.12.25 版（另有同版 xls/ods），無更新版可換。
- 拼音是漢語拼音；護照用的威妥瑪或自訂拼法不在此表。

## 錯誤與失敗時的處理

- **亂碼**：TXT 檔忘了 iconv（Big5→UTF-8）；或反過來把 UTF-8 的 XML 檔也過了 iconv 轉壞。分工：.TXT/.txt=Big5 要轉，.xml=UTF-8 直接讀。
- **下載 404**：中華郵政改版時檔名會帶日期更新（如路街檔的 `1130401`）。回下載區總頁找最新檔名替換。
- **找不到的路名**：先查村里檔再查路街檔；都沒有就引導到官方中英對照查詢頁，不要翻譯充數。

## English summary

Taiwan postal codes (3-digit) and Chinese-to-English address transliteration (Hanyu Pinyin), keyless, from Chunghwa Post's official download area. Files verified 2026-09-12: the 3-digit postal code table (Big5 txt, plus a lat/lng XML), county/township, village, and road/street Chinese-English tables. The .TXT files are Big5 - run `iconv -f big5 -t utf-8` first; the .xml files (e.g. County_h_10906.xml) are UTF-8 - read them directly, do NOT iconv. The village file is quoted CSV ("name,""English""") with no district prefix - grep by the village/lane name itself. Full 3+3 six-digit delivery codes are NOT available as a keyless machine-readable table (official Windows app or registered web service only) - send users to post.gov.tw for those; never guess the last three digits.
