# Search & Trending API / 搜索与热门接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---
## fetch_home_feed

`GET /api/v1/pipixia/app/fetch_home_feed`

<!-- Full path: /api/v1/pipixia/app/fetch_home_feed -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| cursor | string |  | 翻页游标/Page cursor (default: '0') | 0 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取首页推荐数据。
 ### 参数:
 - cursor: 翻页游标，默认为0，后续页码从上一页返回的 `loadmore_cursor` Key中获取对应值。
 ### 返回:
 - 首页推荐数据

## fetch_home_short_drama_feed

`GET /api/v1/pipixia/app/fetch_home_short_drama_feed`

<!-- Full path: /api/v1/pipixia/app/fetch_home_short_drama_feed -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| page | integer |  | 页码/Page number (default: 1) | 1 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取首页短剧推荐数据。
### 参数:
- page: 页码，默认为1，每次翻页加1。
### 返回:
- 首页短剧推荐数据

## fetch_hot_search_words

`GET /api/v1/pipixia/app/fetch_hot_search_words`

<!-- Full path: /api/v1/pipixia/app/fetch_hot_search_words -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取热搜词条数据。
### 返回:
- 热搜词条数据

## fetch_search

`GET /api/v1/pipixia/app/fetch_search`

<!-- Full path: /api/v1/pipixia/app/fetch_search -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 搜索关键词/Search keyword | 皮皮虾 |
| offset | string |  | 翻页游标/Page cursor (default: '0') | 0 |
| search_type | string |  | 搜索类型/Search type (default: '1') | 1 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 搜索接口，支持搜索用户、作品等。
 ### 参数:
 - keyword: 搜索关键词。
 - offset: 翻页游标，默认为0，后续页码从上一页返回的 `offset` Key中获取对应值。
 - search_type: 搜索类型，可用值如下：
    - 1: 综合
    - 8: 热门
    - 9: 新鲜
    - 2：视频
    - 3：图文
    - 4：用户
    - 5：话题
### 返回:
 - 搜索结果

## fetch_short_url

`GET /api/v1/pipixia/app/fetch_short_url`

<!-- Full path: /api/v1/pipixia/app/fetch_short_url -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| original_url | string | ✅ | 原始链接/Original URL | https://h5.pipix.com/item/7385813877985909043 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 生成短连接。
### 参数:
- original_url: 原始链接，可以是任意链接。
### 返回:
- 短连接

---

See SKILL.md for cross-group orchestration patterns.