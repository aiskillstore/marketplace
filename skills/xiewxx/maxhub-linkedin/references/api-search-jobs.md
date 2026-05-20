# Search & Jobs API / 搜索与职位接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---
## search_location

`GET /api/v1/linkedin/web/search_location`

<!-- Full path: /api/v1/linkedin/web/search_location -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 搜索关键词/Search keyword | san francisco |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 搜索LinkedIn地理位置
 ### 参数:
- keyword: 搜索关键词（必填）
 ### 返回:
- 地理位置搜索结果数据

## search_schools

`GET /api/v1/linkedin/web/search_schools`

<!-- Full path: /api/v1/linkedin/web/search_schools -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 搜索关键词/Search keyword | stanford |
| page | string |  | 页码/Page number (default: 1) | 1 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 搜索LinkedIn学校
 ### 参数:
- keyword: 搜索关键词（必填）
- page: 页码（可选），默认为1
 ### 返回:
- 学校搜索结果数据

## search_suggestion_industry

`GET /api/v1/linkedin/web/search_suggestion_industry`

<!-- Full path: /api/v1/linkedin/web/search_suggestion_industry -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 搜索关键词/Search keyword | software |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 搜索LinkedIn行业建议（用于行业ID查询）
 ### 参数:
- keyword: 搜索关键词（必填）
 ### 返回:
- 行业建议搜索结果数据

---

See SKILL.md for cross-group orchestration patterns.