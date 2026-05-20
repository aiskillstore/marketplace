# User Data API / 用户数据接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---
## fetch_user_follow_collections

`GET /api/v1/zhihu/web/fetch_user_follow_collections`

<!-- Full path: /api/v1/zhihu/web/fetch_user_follow_collections -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_url_token | string | ✅ | 用户ID/User ID |  |
| offset | string |  | 偏移量/Offset (default: '0') |  |
| limit | string |  | 每页收藏数量/Number of collections per page (default: '20') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取知乎用户关注的收藏
### 参数:
- user_url_token: 用户ID
- offset: 偏移量
- limit: 每页收藏数量
### 返回:
- 知乎用户关注的收藏

## fetch_user_follow_questions

`GET /api/v1/zhihu/web/fetch_user_follow_questions`

<!-- Full path: /api/v1/zhihu/web/fetch_user_follow_questions -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_url_token | string | ✅ | 用户ID/User ID |  |
| offset | string |  | 偏移量/Offset (default: '0') |  |
| limit | string |  | 每页问题数量/Number of questions per page (default: '20') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取知乎用户关注的问题
### 参数:
- user_url_token: 用户ID
- offset: 偏移量
- limit: 每页问题数量
### 返回:
- 知乎用户关注的问题

## fetch_user_follow_topics

`GET /api/v1/zhihu/web/fetch_user_follow_topics`

<!-- Full path: /api/v1/zhihu/web/fetch_user_follow_topics -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_url_token | string | ✅ | 用户ID/User ID |  |
| offset | string |  | 偏移量/Offset (default: '0') |  |
| limit | string |  | 每页话题数量/Number of topics per page (default: '20') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取知乎用户关注的话题
### 参数:
- user_url_token: 用户ID
- offset: 偏移量
- limit: 每页话题数量
### 返回:
- 知乎用户关注的话题

## fetch_user_followees

`GET /api/v1/zhihu/web/fetch_user_followees`

<!-- Full path: /api/v1/zhihu/web/fetch_user_followees -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_url_token | string | ✅ | 用户ID/User ID |  |
| offset | string |  | 偏移量/Offset (default: '0') |  |
| limit | string |  | 每页用户数量/Number of users per page (default: '20') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取知乎用户关注列表
### 参数:
- user_url_token: 用户ID
- offset: 偏移量
- limit: 每页用户数量
### 返回:
- 知乎用户关注列表

## fetch_user_followers

`GET /api/v1/zhihu/web/fetch_user_followers`

<!-- Full path: /api/v1/zhihu/web/fetch_user_followers -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_url_token | string | ✅ | 用户ID/User ID |  |
| offset | string |  | 偏移量/Offset (default: '0') |  |
| limit | string |  | 每页用户数量/Number of users per page (default: '20') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取知乎用户粉丝列表
### 参数:
- user_url_token: 用户ID
- offset: 偏移量
- limit: 每页用户数量
### 返回:
- 知乎用户粉丝列表

## fetch_user_info

`GET /api/v1/zhihu/web/fetch_user_info`

<!-- Full path: /api/v1/zhihu/web/fetch_user_info -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_url_token | string | ✅ | 用户ID/User ID |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取知乎用户信息
### 参数:
- user_url_token: 用户ID
### 返回:
- 知乎用户信息

## fetch_user_search_v3

`GET /api/v1/zhihu/web/fetch_user_search_v3`

<!-- Full path: /api/v1/zhihu/web/fetch_user_search_v3 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 搜索关键词/Search Keywords |  |
| offset | string |  | 偏移量/Offset (default: '0') |  |
| limit | string |  | 每页用户数量/Number of users per page (default: '25') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取知乎用户搜索V3
### 参数:
- keyword: 搜索关键词
- offset: 偏移量
- limit: 每页用户数量
### 返回:
- 知乎用户搜索V3

---

See SKILL.md for cross-group orchestration patterns.