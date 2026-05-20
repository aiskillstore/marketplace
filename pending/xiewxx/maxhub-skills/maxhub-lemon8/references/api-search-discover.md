# Search & Discover API / 搜索与发现接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---
## fetch_discover_banners

`GET /api/v1/lemon8/app/fetch_discover_banners`

<!-- Full path: /api/v1/lemon8/app/fetch_discover_banners -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取发现页Banner（搜索页上方的滚动内容）
### 返回:
- Banner列表

## fetch_discover_tab

`GET /api/v1/lemon8/app/fetch_discover_tab`

<!-- Full path: /api/v1/lemon8/app/fetch_discover_tab -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取发现页（搜索页主体内容）
### 返回:
- 主体内容

## fetch_hot_search_keywords

`GET /api/v1/lemon8/app/fetch_hot_search_keywords`

<!-- Full path: /api/v1/lemon8/app/fetch_hot_search_keywords -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取热搜关键词
### 返回:
- 热搜关键词列表

## fetch_search

`GET /api/v1/lemon8/app/fetch_search`

<!-- Full path: /api/v1/lemon8/app/fetch_search -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| query | string | ✅ | 搜索关键词/Search keyword | lemon8 |
| max_cursor | string |  | 翻页参数/Pagination parameter (default: '') |  |
| filter_type | string |  | 搜索过滤类型/Search filter type (default: '') |  |
| order_by | string |  | 搜索排序方式/Search sort type (default: '') |  |
| search_tab | string |  | 搜索类型/Search type (default: main) | main |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 搜索接口
 ### 参数:
 - query: 搜索关键词
 - max_cursor:
翻页参数，可以从上一次请求的返回结果中获取，第一次请求为空，后续请求使用上一次请求返回的`max_cursor`进行翻页，可以通过返回结果的`has_more`字段判断是否还有更多数据。
 - filter_type: 搜索过滤类型，默认为空字符串，可选值如下：
    - 空字符串：All（全部，默认使用此参数搜索）
    - video：只搜索视频作品
    - posts：只搜索文章作品
- order_by: 搜索排序方式，默认为空字符串，可选值如下：
    - 空字符串：Relevance（相关度，默认使用此参数排序）
    - popular：流行度排序
    - recent：从新到旧排序
- search_tab: 搜索类型，默认为`main`，可选值如下：
    - main：APP中显示为 `Top`（综合搜索，默认使用此参数搜索）
    - user：APP中显示为 `Accounts` （搜索用户账号）
    - hashtag：APP中显示为 `Hashtags`（搜索话题）
    - article：APP中显示为 `Posts`（搜索文章）
### 返回:
 - 搜索结果

---

See SKILL.md for cross-group orchestration patterns.