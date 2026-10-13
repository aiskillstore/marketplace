---
name: taiwan-parking
description: 台北市停車場即時剩餘車位查詢——公有與民營停車場的可停車位數、場名地址、費率、充電樁狀態。停車、停車位、哪裡可以停車、剩餘車位、台北停車場的問題適用。免 API 金鑰、免登入。台北市以外縣市、路邊停車格即時空位不適用。
license: MIT
metadata:
  category: transport
  locale: zh-TW
---

# taiwan-parking

> 實測日：2026-09-26（最近一次端對端實測；數值基準日各自標於內文）

用台北市停車管理工程處的公開 JSON 查台北市停車場的即時剩餘車位。不需要 API 金鑰或登入。兩支 feed 搭配使用：**即時剩位**（allavailable）與**靜態資料**（alldesc：場名、地址、費率、總格數）。

## 基本流程

1. 抓靜態場站表（alldesc），用地名或場名找出停車場 id
2. 抓即時剩位表（allavailable），用 id 取出可停數
3. 回報時附上 allavailable 的 UPDATETIME，讓使用者知道資料有多新

### 1. 即時剩位（allavailable）

```bash
curl -sm 30 -o /tmp/park.json 'https://tcgbusfs.blob.core.windows.net/blobtcmsv/TCMSV_allavailable.json'
```

2026-09-26 實測：HTTP 200、約 474KB、1,188 場，UPDATETIME 與查詢時刻同小時（近即時）。場數會隨開歇業緩慢變動，本數字是該日實測值。欄位：`id`（場站代碼，如 TPE0001）、`availablecar`（小型車可停數）、`availablemotor`、`availablebus`、`availablehandicap`（身障格）、`availablepregnancy`（孕婦親子格）、`availableheavymotor`，部分場另有 `ChargeStation.scoketStatusList`（充電樁，spot_status 為 待機中/充電中）。

**`-9` = 該場無此車種資料**（2026-09-26 實測 1,188 場中 88 場 availablecar 為 -9），不是「停滿」也不是錯誤，回報時略過或說「無資料」。

### 2. 靜態場站表（alldesc）

```bash
curl -sm 30 -o /tmp/parkdesc.json 'https://tcgbusfs.blob.core.windows.net/blobtcmsv/TCMSV_alldesc.json'
```

2026-09-26 實測：HTTP 200、約 2.8MB、1,775 場（含無即時資料的場）。欄位：`id`、`area`（行政區）、`name`、`address`、`tel`、`payex`（費率說明文字）、`serviceTime`、`totalcar` 等總格數、`tw97x`/`tw97y`（TWD97 坐標，字串）。

### 3. 組合查詢範例

```bash
# 中山區還有車位的停車場,依剩位多寡排序
jq -r --slurpfile d /tmp/parkdesc.json '
  ($d[0].data.park | map({key:.id, value:{name:.name, area:.area, addr:.address}}) | from_entries) as $info
  | .data.park[] | select(.availablecar > 0 and $info[.id].area == "中山區")
  | "\($info[.id].name) 剩 \(.availablecar) 位 (\($info[.id].addr))"' /tmp/park.json | sort -t'剩' -k2 -rn | head -10
```

2026-09-19 實測範例：台灣聯通長春停車場（中山區長春路17號）當下可停 15 位。

## 錯誤與失敗時的處理

- **-9 的意義**：無此車種資料，勿當 0 也勿當錯誤。
- **只涵蓋台北市**：其他縣市不要拿這支 feed 硬查；回報「目前只支援台北市停管處場站」。
- **路邊停車格不在內**：本資料是停車場，路邊計費格的即時空位無公開 feed。
- **tw97x/y 是 TWD97 投影坐標不是經緯度**：要算距離需先轉換（或只回報地址）。
- **資料時效**：兩支 feed 各自有 UPDATETIME；即時表約數分鐘更新。回報必附時間。
- **blob.core.windows.net 連不上**：可能是暫時性網路問題，稍後重試；持續失敗則回報資料源異常，不要編造剩位數字。

## English summary

Taipei City parking availability, keyless. Real-time availability: `https://tcgbusfs.blob.core.windows.net/blobtcmsv/TCMSV_allavailable.json` (~474KB, 1,071 lots, fields availablecar/availablemotor/..., some with EV-charger status). Static details: `https://tcgbusfs.blob.core.windows.net/blobtcmsv/TCMSV_alldesc.json` (~2.8MB, 1,762 lots: name, area, address, pricing text, totals, TWD97 coords). Join on `id`. `-9` means "no data for this vehicle type" - not full, not an error. Verified 2026-10-13 (e.g. 台灣聯通長春停車場, Zhongshan Dist., 15 car spaces free at query time on 2026-09-19). Taipei only; roadside metered spaces not included; always cite the feed's UPDATETIME.
