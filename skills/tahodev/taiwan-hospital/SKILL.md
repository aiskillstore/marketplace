---
name: taiwan-hospital
description: 健保特約醫療院所查詢——全台三萬七千家醫院診所的名稱、地址、電話、類型（健保署開放資料）。附近診所、醫院電話、牙醫診所地址、看診掛號電話的問題適用。免 API 金鑰、免登入。即時看診進度、掛號、醫師排班不適用。
license: MIT
metadata:
  category: health
  locale: zh-TW
---

# taiwan-hospital

> 實測日：2026-10-02（最近一次端對端實測；數值基準日各自標於內文）

用健保署開放資料 API 查全台健保特約醫療院所（醫院、診所、藥局、護理機構…）的基本資料。不需要 API 金鑰或登入。

## 基本流程

1. 大量下載資料集（一次 limit 拉高）或帶參數查詢
2. 依院名、縣市（地址開頭）、類型篩選
3. 回報名稱、地址、電話；註明資料為健保特約院所名錄（非即時看診資訊）

### 1. API 端點

```bash
# 院所基本資料:API 單次最多回 1,000 筆,先看 total 再分頁，分頁後存成 /tmp/hosp.json 供下一節使用(37,175 筆,2026-10-02 實測；9/20 為 37,133，總數會變動)
curl -sm 30 -A 'Mozilla/5.0' 'https://info.nhi.gov.tw/api/iode0010/v1/rest/datastore/A21030000I-D2100G-001?limit=1&offset=0' -o /tmp/hosp_meta.json

# 資料集目錄
curl -sm 30 -A 'Mozilla/5.0' 'https://info.nhi.gov.tw/api/iode0010/v1/rest/dataset?limit=100' -o /tmp/datasets.json
```

**全量下載要分頁**：這個 datastore API 把 limit 封頂在 1,000（2026-09-20 實測：帶 `limit=40000` 只回 1,000 筆、`result.limit` 顯示 1000；總數看 `result.total`）。用 offset 逐頁取：

```python
import json, urllib.request
UA = {'User-Agent': 'Mozilla/5.0'}
BASE = 'https://info.nhi.gov.tw/api/iode0010/v1/rest/datastore/A21030000I-D2100G-001'
def page(offset):
    req = urllib.request.Request(f'{BASE}?limit=1000&offset={offset}', headers=UA)
    return json.loads(urllib.request.urlopen(req, timeout=40).read())['result']
first = page(0)
total, recs = first['total'], list(first['records'])
for off in range(1000, total, 1000):
    recs += page(off)['records']
json.dump({'result': {'total': total, 'records': recs}}, open('/tmp/hosp.json', 'w'), ensure_ascii=False)
print(total, len(recs))   # 37175 37175 (2026-10-02 實測,38 頁；總數每週小幅變動)
```

2026-09-20 實測：HTTP 200、`{"success": true, "result": {...}}`、`result.total` = 37,133 筆（2026-10-02 重測為 37,175）。欄位：BRANCH_CODE（分區）、HOSP_ID、HOSP_ATTR_NAME（如 部立及直轄市立醫院）、HOSP_NAME、HOSP_ADDR、TEL_AREA/TEL、HOSP_CNT_TYPE、HOSP_TYPE、CONT_ORIG_DATE（簽約起日）。首筆實測範例：臺北市立聯合醫院、臺北市大同區鄭州路１４５號（代表）、(02)25553000。

有用的姊妹資料集（dataset 目錄可查）：D21006 固定服務時段（各院所門診時段表）、D2100C 診療科別。

### 2. 篩選範例

```python
import json
d = json.load(open('/tmp/hosp.json'))
recs = d['result']['records']
# 找名稱含「台大」的院所
for r in recs:
    if '台大' in r['HOSP_NAME'] or '臺大' in r['HOSP_NAME']:
        print(r['HOSP_NAME'], r['HOSP_ADDR'], f"({r['TEL_AREA']}){r['TEL']}")
```

### 3. 進階：服務時段與科別

D21006（固定服務時段）與 D2100C（診療科別）用同一 API 形式，把 resource id 換掉即可。要回答「這家診所週六有沒有看診」時，先從基本資料拿 HOSP_ID，再查服務時段資料集比對。

## 錯誤與失敗時的處理

- **這是名錄不是即時資訊**：看診進度（目前看到幾號）、網路掛號、臨時休診查不到，如實說明。
- **地址含全形字元與「（代表）」**：多分院體系只有代表地址；回報前不要自行刪改。
- **資料更新頻率**：健保署定期更新，新開業或歇業可能有落差；重要就醫決策建議電話確認。
- **success=false 或 HTTP 非 200**：帶瀏覽器 UA 重試；失敗回報資料源異常，不要背院所電話。
- **limit 封頂 1,000 筆**：`limit=40000` 不會一次回全量，只回 1,000 筆；全量要用 offset 分頁（2026-10-02 實測 total=37,175，約 8MB）。頻寬受限時用參數查詢（如 `?HOSP_NAME=台大`），但參數過濾行為可能因資料集而異，比對結果是否合理。

## English summary

Taiwan NHI-contracted medical providers directory, keyless. `GET https://info.nhi.gov.tw/api/iode0010/v1/rest/datastore/A21030000I-D2100G-001?limit=1000&offset=N` returns {"success":true, result:{records:[...], total: N}} - the API caps limit at 1,000 per call, so page with offset to fetch everything (verified 2026-09-20 and re-run 2026-10-02: total = 37,133 then 37,175 - the count drifts weekly, never hard-code it; hospitals/clinics/pharmacies, ~38 pages; name, address, phone, type, contract dates). Dataset catalog at `/api/iode0010/v1/rest/dataset?limit=100`; useful siblings: D21006 (service hours), D2100C (departments). Directory data only - no real-time queue status or appointment booking; say so when asked.
