# Search & Feed API / 搜索与推荐接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---
## fetch_bangumi_tab

`GET /api/v1/bilibili/app/fetch_bangumi_tab`

<!-- Full path: /api/v1/bilibili/app/fetch_bangumi_tab -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取主页番剧推荐
### 返回:
- 番剧推荐数据

## fetch_cinema_tab

`GET /api/v1/bilibili/app/fetch_cinema_tab`

<!-- Full path: /api/v1/bilibili/app/fetch_cinema_tab -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取主页影视推荐
### 返回:
- 影视推荐数据

## fetch_general_search

`GET /api/v1/bilibili/web/fetch_general_search`

<!-- Full path: /api/v1/bilibili/web/fetch_general_search -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 搜索关键词/Search keyword | 火影忍者 |
| order | string | ✅ | 排序方式/Order method | totalrank |
| page | integer | ✅ | 页码/Page number | 1 |
| page_size | integer | ✅ | 每页数量/Number per page | 42 |
| duration | integer |  | 时长筛选/Duration filter (default: 0) |  |
| pubtime_begin_s | integer |  | 开始日期/Start date (10-digit timestamp) (default: 0) |  |
| pubtime_end_s | integer |  | 结束日期/End date (10-digit timestamp) (default: 0) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取综合搜索信息
 ### 参数:
 - keyword: 搜索关键词
 - order: 排序方式
    - totalrank 综合排序
    - click 最多播放
    - pubdate 最新发布
    - dm 最多弹幕
    - stow 最多收藏
- page: 页码
 - page_size: 每页数量
 - duration: 时长筛选
    - 0 全部时长
    - 1 10分钟以下
    - 2 10-30分钟
    - 3 30分钟-60分钟
    - 4 60分钟以上
- pubtime_begin_s: 开始日期，10位时间戳，需要小于结束日期
 - pubtime_end_s: 结束日期，10位时间戳，需要大于开始日期
 ### 返回:
 - 综合搜索信息

## fetch_hot_search

`GET /api/v1/bilibili/web/fetch_hot_search`

<!-- Full path: /api/v1/bilibili/web/fetch_hot_search -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| limit | string | ✅ | 返回数量/Return number | 10 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取热门搜索信息
### 参数:
- limit: 返回数量
### 返回:
- 热门搜索信息
### 说明:
- limit默认为10，上限为50

## fetch_popular_feed

`GET /api/v1/bilibili/app/fetch_popular_feed`

<!-- Full path: /api/v1/bilibili/app/fetch_popular_feed -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| idx | integer |  | 页面索引/Page index (default: 1) |  |
| last_param | string |  | 上一页最后一个视频ID/Last video ID |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取热门推荐视频
### 参数:
- idx: 页面索引（从1开始）
- last_param: 上一页最后一个视频的ID（用于分页）
### 返回:
- 热门推荐视频数据

## fetch_search_all

`GET /api/v1/bilibili/app/fetch_search_all`

<!-- Full path: /api/v1/bilibili/app/fetch_search_all -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 搜索关键词/Search keyword | 原神 |
| page | integer |  | 页码/Page number (default: 1) |  |
| page_size | integer |  | 每页数量/Page size (default: 20) |  |
| order | integer |  | 排序方式/Sort order (0=综合排序) (default: 0) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 综合搜索（返回所有类型的搜索结果）
 ### 参数:
 - keyword: 搜索关键词（必填）
 - page: 页码，从1开始
 - page_size: 每页结果数量
 - order: 排序方式（0=综合排序）
 ### 返回:
 - 搜索结果，包含nav（分类导航）、item（搜索结果）、pagination（分页信息）等

## fetch_search_by_type

`GET /api/v1/bilibili/app/fetch_search_by_type`

<!-- Full path: /api/v1/bilibili/app/fetch_search_by_type -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 搜索关键词/Search keyword | 原神 |
| search_type | string |  | 搜索类型/Search type (video/bangumi/pgc/live/article/user) (default: video) |  |
| page | integer |  | 页码/Page number (default: 1) |  |
| page_size | integer |  | 每页数量/Page size (default: 20) |  |
| order | integer |  | 排序方式/Sort order (0=综合, 1=最新, 2=播放量, 3=弹幕数) (default: 0) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 分类搜索（按类型搜索）
### 参数:
- keyword: 搜索关键词（必填）
- search_type: 搜索类型
    - video: 视频
    - bangumi: 番剧
    - pgc: 影视
    - live: 直播
    - article: 专栏
    - user: 用户
- page: 页码，从1开始
- page_size: 每页结果数量
- order: 排序方式
    - 0: 综合排序
    - 1: 最新发布
    - 2: 播放量
    - 3: 弹幕数
### 返回:
- 搜索结果

---

See SKILL.md for cross-group orchestration patterns.