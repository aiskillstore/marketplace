# Search & Trending API / 搜索与热门接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---
## fetch_ai_search

`GET /api/v1/zhihu/web/fetch_ai_search`

<!-- Full path: /api/v1/zhihu/web/fetch_ai_search -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| message_content | string | ✅ | 搜索内容/Search Content |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取知乎AI搜索
### 参数:
- message_content: 搜索内容
### 返回:
- 知乎AI搜索消息ID，用于请求搜索结果

## fetch_ai_search_result

`GET /api/v1/zhihu/web/fetch_ai_search_result`

<!-- Full path: /api/v1/zhihu/web/fetch_ai_search_result -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| message_id | string | ✅ | 消息ID/Message ID |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取知乎AI搜索结果
### 参数:
- message_id: 消息ID
### 返回:
- 知乎AI搜索结果

## fetch_ebook_search_v3

`GET /api/v1/zhihu/web/fetch_ebook_search_v3`

<!-- Full path: /api/v1/zhihu/web/fetch_ebook_search_v3 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 搜索关键词/Search Keywords |  |
| offset | string |  | 偏移量/Offset (default: '0') |  |
| limit | string |  | 每页电子书数量/Number of ebooks per page (default: '20') |  |
| search_hash_id | string |  | 搜索哈希ID/Search Hash ID (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取知乎电子书搜索V3
### 参数:
- keyword: 搜索关键词
- offset: 偏移量
- limit: 每页电子书数量
- search_hash_id: 搜索哈希ID
### 返回:
- 知乎电子书搜索V3

## fetch_hot_recommend

`GET /api/v1/zhihu/web/fetch_hot_recommend`

<!-- Full path: /api/v1/zhihu/web/fetch_hot_recommend -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| offset | string |  | 偏移量/Offset (default: '0') |  |
| page_number | string |  | 页码/Page Number (default: '1') |  |
| session_token | string |  | 会话令牌/Session Token (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取知乎首页推荐
### 参数:
- offset: 偏移量
- page_number: 页码
- session_token: 会话令牌
### 返回:
- 知乎首页推荐

## fetch_preset_search

`GET /api/v1/zhihu/web/fetch_preset_search`

<!-- Full path: /api/v1/zhihu/web/fetch_preset_search -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取知乎搜索预设词
### 参数:
- 无
### 返回:
- 知乎搜索预设词

## fetch_salt_search_v3

`GET /api/v1/zhihu/web/fetch_salt_search_v3`

<!-- Full path: /api/v1/zhihu/web/fetch_salt_search_v3 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 搜索关键词/Search Keywords |  |
| offset | string |  | 偏移量/Offset (default: '0') |  |
| limit | string |  | 每页内容数量/Number of contents per page (default: '20') |  |
| search_hash_id | string |  | 搜索哈希ID/Search Hash ID (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取知乎盐选内容搜索V3
### 参数:
- keyword: 搜索关键词
- offset: 偏移量
- limit: 每页内容数量
- search_hash_id: 搜索哈希ID
### 返回:
- 知乎盐选内容搜索V3

## fetch_scholar_search_v3

`POST /api/v1/zhihu/web/fetch_scholar_search_v3`

<!-- Full path: /api/v1/zhihu/web/fetch_scholar_search_v3 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 搜索关键词/Search Keywords |  |
| offset | string |  | 偏移量/Offset (default: '0') |  |
| limit | string |  | 每页论文数量/Number of papers per page (default: '25') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取知乎论文搜索V3
### 参数:
- keyword: 搜索关键词
- offset: 偏移量
- limit: 每页论文数量
- filter_fields: 过滤字段
### 返回:
- 知乎论文搜索V3

## fetch_search_recommend

`GET /api/v1/zhihu/web/fetch_search_recommend`

<!-- Full path: /api/v1/zhihu/web/fetch_search_recommend -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取知乎搜索发现
### 参数:
- 无
### 返回:
- 知乎搜索发现

## fetch_search_suggest

`GET /api/v1/zhihu/web/fetch_search_suggest`

<!-- Full path: /api/v1/zhihu/web/fetch_search_suggest -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 搜索关键词/Search Keywords |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 知乎搜索预测词
### 参数:
- keyword: 搜索关键词
### 返回:
- 知乎搜索预测词

## fetch_topic_search_v3

`GET /api/v1/zhihu/web/fetch_topic_search_v3`

<!-- Full path: /api/v1/zhihu/web/fetch_topic_search_v3 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 搜索关键词/Search Keywords |  |
| offset | string |  | 偏移量/Offset (default: '0') |  |
| limit | string |  | 每页话题数量/Number of topics per page (default: '25') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取知乎话题搜索V3
### 参数:
- keyword: 搜索关键词
- offset: 偏移量
- limit: 每页话题数量
### 返回:
- 知乎话题搜索V3

## fetch_video_list

`GET /api/v1/zhihu/web/fetch_video_list`

<!-- Full path: /api/v1/zhihu/web/fetch_video_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| offset | string |  | 偏移量/Offset (default: '0') |  |
| limit | string |  | 每页视频数量/Number of videos per page (default: '12') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取知乎首页视频榜
### 参数:
- offset: 偏移量
- limit: 每页视频数量
### 返回:
- 知乎首页视频榜

## fetch_video_search_v3

`GET /api/v1/zhihu/web/fetch_video_search_v3`

<!-- Full path: /api/v1/zhihu/web/fetch_video_search_v3 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 搜索关键词/Search Keywords |  |
| limit | string |  | 每页视频数量/Number of videos per page (default: '20') |  |
| offset | string |  | 偏移量/Offset (default: '0') |  |
| search_hash_id | string |  | 搜索哈希ID/Search Hash ID (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取知乎视频搜索V3
### 参数:
- keyword: 搜索关键词
- limit: 每页视频数量
- offset: 偏移量
- search_hash_id: 搜索哈希ID
### 返回:
- 知乎视频搜索V3

---

See SKILL.md for cross-group orchestration patterns.