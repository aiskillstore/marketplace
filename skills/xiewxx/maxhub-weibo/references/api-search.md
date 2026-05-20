# Search API / 搜索接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---
## fetch_ai_smart_search

`GET /api/v1/weibo/app/fetch_ai_smart_search`

<!-- Full path: /api/v1/weibo/app/fetch_ai_smart_search -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| query | string | ✅ | 搜索关键词 | 人工智能 |
| page | integer |  | 页码 (default: 1) | 1 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 使用微博AI智搜功能进行搜索，返回AI增强的搜索结果。
 ### 参数:
 - query: 搜索关键词（必填）
 - page: 页码，从1开始（默认1）
 ### 返回:
 - AI智搜结果，包含AI增强的搜索内容
 ### 注意:
 - 此接口为AI增强搜索，返回结果经过AI处理

## fetch_hot_search

`GET /api/v1/weibo/app/fetch_hot_search`

<!-- Full path: /api/v1/weibo/app/fetch_hot_search -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| category | string |  | >- (default: realtimehot) | realtimehot |
| page | integer |  | 页码 (default: 1) | 1 |
| count | integer |  | 每页数量 (default: 20) | 20 |
| region_name | string |  | >- | 北京 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取微博热搜榜，支持多个分类。
 ### 参数:
 - category: 热搜分类
    - mineband: 我的热搜
    - realtimehot: 实时热搜（默认）
    - social: 社会热搜
    - fun: 文娱热搜
    - technologynav: 科技热搜
    - lifenav: 生活热搜
    - region: 同城热搜（需配合 region_name 指定城市）
    - sportnav: 体育热搜
    - gamenav: ACG热搜
- page: 页码，从1开始（默认1）
 - count: 每页数量，默认20，最大50
 - region_name: 同城热搜城市名称，仅 category=region 时有效，默认北京
 ### 返回:
 - 热搜榜数据，包含热搜词条、热度等
 ### 注意:
 - 热搜榜实时更新

## fetch_hot_search

`GET /api/v1/weibo/app/fetch_hot_search`

<!-- Full path: /api/v1/weibo/web/fetch_hot_search -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取微博实时热搜榜（Top 50）和实时上升热点
 ### 返回:
 - 热搜榜列表，包含：
    - **实时热搜榜**: 当前最热门的50个话题，按热度排序
    - **实时上升热点**: 正在快速上升的热门话题
### 说明:
 - 这是微博官方热搜榜数据
 - 每个热搜包含：排名、话题名、热度值、标签（如：新、热、沸）等
 - 与 `fetch_search_topics` 不同，此接口返回的是完整的热搜排行榜

## fetch_hot_search_categories

`GET /api/v1/weibo/app/fetch_hot_search_categories`

<!-- Full path: /api/v1/weibo/app/fetch_hot_search_categories -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取微博热搜榜的所有可用分类列表。
 ### 参数:
 - 无
 ### 返回:
 - 热搜分类列表数据，包含各分类名称和标识
 ### 注意:
 - 返回的分类可用于 fetch_hot_search 接口的 category 参数

## fetch_hot_search_summary

`GET /api/v1/weibo/web_v2/fetch_hot_search_summary`

<!-- Full path: /api/v1/weibo/web_v2/fetch_hot_search_summary -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取微博完整热搜榜单（50条）。
 ### 参数:
 - 无需额外参数
 ### 返回:
 - 完整热搜列表，包含排名、关键词、标签（热点/沸点/官宣/新）、热度值
 ### 注意:
 - 与fetch_hot_search_index的区别：本接口返回50条，fetch_hot_search_index返回10条
 - rank为0表示置顶内容
 - 建议缓存5-10分钟

## fetch_realtime_search

`GET /api/v1/weibo/web_v2/fetch_realtime_search`

<!-- Full path: /api/v1/weibo/web_v2/fetch_realtime_search -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| query | string | ✅ | 搜索关键词/Search keyword | yu7 |
| page | integer |  | 页码/Page number (default: 1) | 1 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取微博实时搜索结果（按时间排序的最新微博）。
 ### 参数:
 - query: 搜索关键词（必填）
 - page: 页码（默认1）
 ### 返回:
 - 实时搜索结果列表，包含微博内容、作者信息、图片、视频、互动数据等
 ### 注意:
 - 视频播放需设置请求头 Referer=https://weibo.com/
 - 返回结构与高级搜索一致

## fetch_search_all

`GET /api/v1/weibo/app/fetch_search_all`

<!-- Full path: /api/v1/weibo/app/fetch_search_all -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| query | string | ✅ | 搜索关键词 | NVIDIA |
| page | integer |  | 页码 (default: 1) | 1 |
| search_type | integer |  | >- (default: 1) | 1 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 在微博中进行综合搜索，返回相关内容。支持多种搜索类型。
 ### 参数:
 - query: 搜索关键词（必填）
 - page: 页码，从1开始（默认1）
 - search_type: 搜索类型
    - 1: 综合（默认）
    - 61: 实时
    - 3: 用户
    - 64: 视频
    - 63: 图片
    - 62: 关注
    - 60: 热门
    - 21: 全网
    - 38: 话题
    - 98: 超话
    - 92: 地点
    - 97: 商品
### 返回:
 - 搜索结果列表，包含微博内容、作者信息、图片、视频等
 ### 注意:
 - 搜索结果按相关度排序
 - 仅使用 page 参数进行翻页

## fetch_search_topics

`GET /api/v1/weibo/web/fetch_search_topics`

<!-- Full path: /api/v1/weibo/web/fetch_search_topics -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取搜索页的热搜词列表（搜索建议/热门话题）
 ### 返回:
 - 搜索热词列表
 ### 说明:
 - 这是搜索页面展示的热门搜索词
 - 通常用于搜索框下方的热门推荐
 - 与 `fetch_hot_search` 不同，此接口返回的是搜索建议词

## fetch_topic_search

`GET /api/v1/weibo/web_v2/fetch_topic_search`

<!-- Full path: /api/v1/weibo/web_v2/fetch_topic_search -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| query | string | ✅ | 搜索关键词/Search keyword | yu7 |
| page | integer |  | 页码/Page number (default: 1) | 1 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 搜索微博话题，获取话题名称、封面、讨论量、阅读量。
 ### 参数:
 - query: 搜索关键词（必填）
 - page: 页码（默认1）
 ### 返回:
 - 话题列表，包含话题名、封面图、讨论数、阅读数
 ### 注意:
 - 数量单位（万/亿）已转换为整数

## fetch_video_search

`GET /api/v1/weibo/web_v2/fetch_video_search`

<!-- Full path: /api/v1/weibo/web_v2/fetch_video_search -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| query | string | ✅ | 搜索关键词/Search keyword | yu7 |
| mode | string |  | 搜索模式：hot=热门 / all=全部 (default: hot) | hot |
| page | integer |  | 页码/Page number (default: 1) | 1 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 搜索微博视频内容，支持热门和全部模式。
### 参数:
- query: 搜索关键词（必填）
- mode: 搜索模式 hot=热门 / all=全部（默认hot）
- page: 页码（默认1）
### 返回:
- 视频列表，包含微博ID、作者、内容、视频链接、互动数据
### 注意:
- 播放视频需设置Referer=https://weibo.com/

---

See SKILL.md for cross-group orchestration patterns.