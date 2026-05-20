# Live & Comment API / 直播与评论接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---
## fetch_all_live_areas

`GET /api/v1/bilibili/web/fetch_all_live_areas`

<!-- Full path: /api/v1/bilibili/web/fetch_all_live_areas -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取所有直播分区列表
### 参数:
### 返回:
- 所有直播分区列表

## fetch_live_streamers

`GET /api/v1/bilibili/web/fetch_live_streamers`

<!-- Full path: /api/v1/bilibili/web/fetch_live_streamers -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| area_id | string | ✅ | 直播分区id/Live area ID | 9 |
| pn | integer |  | 页码/Page number (default: 1) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取指定分区正在直播的主播
### 参数:
- area_id: 直播分区id
- pn: 页码
### 返回:
- 指定分区正在直播的主播

---

See SKILL.md for cross-group orchestration patterns.