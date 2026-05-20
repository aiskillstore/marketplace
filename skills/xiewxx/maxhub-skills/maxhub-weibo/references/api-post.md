# Post & Comment API / 微博与评论接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---
## check_allow_comment_with_pic

`GET /api/v1/weibo/web_v2/check_allow_comment_with_pic`

<!-- Full path: /api/v1/weibo/web_v2/check_allow_comment_with_pic -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| id | string | ✅ | 微博ID/Weibo ID | 5092682368025584 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 检查指定微博是否允许用户在评论时上传图片。
### 参数:
- id: 微博ID（必填）
### 返回:
- result: true表示允许带图评论，false表示不允许
### 注意:
- 不同微博的图片评论权限可能不同

## fetch_advanced_search

`GET /api/v1/weibo/web_v2/fetch_advanced_search`

<!-- Full path: /api/v1/weibo/web_v2/fetch_advanced_search -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| q | string | ✅ | 搜索关键词/Search keyword | yu7 |
| search_type | string |  | >- | hot |
| include_type | string |  | >- | pic |
| timescope | string |  | 时间范围/Time scope (custom:start:end) | custom:2025-09-01-0:2025-09-08-23 |
| page | integer |  | 页码/Page number (default: 1) | 1 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 微博高级搜索，支持多维度筛选。
 ### 参数:
 - q: 搜索关键词（必填）
 - search_type: 搜索类型（all/hot/original/verified/media/viewpoint）
 - include_type: 包含类型（all/pic/video/music/link）
 - timescope: 时间范围（格式: custom:开始日期:结束日期，如
custom:2025-09-01-0:2025-09-08-23）
 - page: 页码（默认1）
 ### 返回:
 - 搜索结果列表，包含微博内容、作者信息、图片、视频、互动数据等
 ### 注意:
 - 视频播放需设置请求头 Referer=https://weibo.com/

## fetch_ai_related_search

`GET /api/v1/weibo/web_v2/fetch_ai_related_search`

<!-- Full path: /api/v1/weibo/web_v2/fetch_ai_related_search -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 搜索关键词/Search keyword | #微博奇遇记# |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取与关键词相关的内容扩展（相关问题、博主推荐、参考博文等）。
 ### 参数:
 - keyword: 搜索关键词（必填，建议使用话题格式#话题名#）
 ### 返回:
 - HTML格式的扩展内容，包含相关问题、博主推荐、参考博文等
 ### 注意:
 - 返回内容为HTML格式，需要进行HTML解析处理
 - HTML结构可能会发生变化，需要做好容错处理

## fetch_ai_search

`GET /api/v1/weibo/web_v2/fetch_ai_search`

<!-- Full path: /api/v1/weibo/web_v2/fetch_ai_search -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| query | string | ✅ | 搜索关键词/Search keyword | #法国# |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 通过微博AI智能搜索获取搜索结果。
 ### 参数:
 - query: 搜索关键词（必填，建议使用话题格式#话题名#）
 ### 返回:
 - AI搜索结果，包含推荐内容、相关话题等
 ### 注意:
 - AI搜索结果会根据用户行为进行个性化调整

## fetch_comment_replies

`GET /api/v1/weibo/web/fetch_comment_replies`

<!-- Full path: /api/v1/weibo/web/fetch_comment_replies -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| cid | string | ✅ | 根评论ID/Root comment ID | 5100663573318494 |
| max_id | string |  | 翻页ID，默认0为第一页/Pagination ID, default 0 for first page (default: '0') | 0 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取评论的子评论（回复）
 ### 参数:
 - cid: 根评论ID（从 fetch_post_comments 返回的评论中获取）
 - max_id: 翻页用的ID，默认0为第一页，从上一页返回结果中获取下一页的max_id
 ### 返回:
 - 子评论列表

## fetch_entertainment_ranking

`GET /api/v1/weibo/web_v2/fetch_entertainment_ranking`

<!-- Full path: /api/v1/weibo/web_v2/fetch_entertainment_ranking -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取微博文娱榜单数据（娱乐圈、影视、综艺等）。
 ### 参数:
 - 无需额外参数
 ### 返回:
 - 文娱话题列表，包含话题、热度值、排名、分类等
 ### 注意:
 - 建议缓存5-10分钟

## fetch_hot_ranking_timeline

`GET /api/v1/weibo/web_v2/fetch_hot_ranking_timeline`

<!-- Full path: /api/v1/weibo/web_v2/fetch_hot_ranking_timeline -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| ranking_type | string | ✅ | >- | hour |
| since_id | string |  | 分页标识，默认为0/Pagination identifier, default is 0 (default: '0') | 0 |
| max_id | string |  | 最大ID，默认为0/Max ID, default is 0 (default: '0') | 0 |
| count | integer |  | 获取数量，默认10/Count, default is 10 (default: 10) | 10 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取微博平台各种类型的热门榜单内容。
 ### 参数:
 - ranking_type: 榜单类型（必填）
    - hour: 小时榜
    - yesterday: 昨日榜
    - day_before: 前日榜
    - week: 周榜
    - male: 男榜
    - female: 女榜
- max_id: 翻页游标，首次请求传"0"
 - count: 获取数量（默认10）
 ### 返回:
 - 热门微博列表，包含微博内容、作者信息、互动数据等
 ### 注意:
 - 不同榜单更新频率不同：小时榜实时性最强，周榜影响力较大

## fetch_hot_search

`GET /api/v1/weibo/app/fetch_hot_search`

<!-- Full path: /api/v1/weibo/web_v2/fetch_hot_search -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取微博实时热搜榜单数据。
 ### 参数:
 - 无需额外参数
 ### 返回:
 - 热搜数据，包含realtime（实时热搜）、hotgov等多个板块
 ### 注意:
 - 热搜更新频繁，建议缓存2-5分钟

## fetch_hot_search_index

`GET /api/v1/weibo/web_v2/fetch_hot_search_index`

<!-- Full path: /api/v1/weibo/web_v2/fetch_hot_search_index -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 快速获取微博热搜前10条。
### 参数:
- 无需额外参数
### 返回:
- 热搜词条列表，包含关键词、热度值、排名等
### 注意:
- 只返回前10条热搜
- 热搜更新频繁，建议缓存2-5分钟
- 如需完整热搜，使用fetch_hot_search_summary

## fetch_life_ranking

`GET /api/v1/weibo/web_v2/fetch_life_ranking`

<!-- Full path: /api/v1/weibo/web_v2/fetch_life_ranking -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取微博生活榜单数据（美食、旅游、健康、时尚等）。
### 参数:
- 无需额外参数
### 返回:
- 生活话题列表，包含话题、热度值、排名、分类等
### 注意:
- 建议缓存5-10分钟

## fetch_pic_search

`GET /api/v1/weibo/web_v2/fetch_pic_search`

<!-- Full path: /api/v1/weibo/web_v2/fetch_pic_search -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| query | string | ✅ | 搜索关键词/Search keyword | yu7 |
| page | integer |  | 页码/Page number (default: 1) | 1 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 搜索微博图片内容，按微博ID聚合多图。
 ### 参数:
 - query: 搜索关键词（必填）
 - page: 页码（默认1）
 ### 返回:
 - 图片列表，包含微博ID、缩略图、原图链接、作者信息、图片数量
 ### 注意:
 - 缩略图会自动转换为原图链接

## fetch_post_comments

`GET /api/v1/weibo/web/fetch_post_comments`

<!-- Full path: /api/v1/weibo/web/fetch_post_comments -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| post_id | string | ✅ | 微博ID/Post ID | 5100663548412324 |
| mid | string | ✅ | 微博MID/Post MID | 5100663548412324 |
| max_id | string |  | 翻页ID/Pagination ID |  |
| max_id_type | integer |  | 翻页ID类型/Pagination ID type (default: 0) | 0 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取微博的评论列表（热门评论流）
### 参数:
- post_id: 微博ID
- mid: 微博MID
- max_id: 翻页用的ID，从上一页返回结果中获取
- max_id_type: max_id类型，默认0
### 返回:
- 评论列表

## fetch_post_comments

`GET /api/v1/weibo/web/fetch_post_comments`

<!-- Full path: /api/v1/weibo/web_v2/fetch_post_comments -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| id | string | ✅ | 微博ID/Weibo ID | 5283919831764022 |
| count | integer |  | 评论数量/Number of comments (default: 10) | 10 |
| max_id | string |  | 页码/Page number (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定微博的一级评论列表。
 ### 参数:
 - id: 微博ID（必填）
 - count: 评论数量（默认10）
 - max_id: 翻页游标，首次请求传空，后续请求使用返回的max_id值
 ### 返回:
 - 评论列表数据，包含评论内容、评论者信息、点赞数等
 - 包含 max_id 字段用于翻页
 ### 注意:
 - 当没有更多评论时，max_id 为空

## fetch_post_detail

`GET /api/v1/weibo/web/fetch_post_detail`

<!-- Full path: /api/v1/weibo/web/fetch_post_detail -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| post_id | string | ✅ | 微博ID/Post ID | 5092682368025584 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取单条微博的详情
### 参数:
- post_id: 微博ID
### 返回:
- 微博详情

## fetch_post_detail

`GET /api/v1/weibo/web/fetch_post_detail`

<!-- Full path: /api/v1/weibo/web_v2/fetch_post_detail -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| id | string | ✅ | 作品id/Post id | 5092682368025584 |
| is_get_long_text | string |  | >- (default: 'true') | true |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定微博的详细信息，包括内容、作者、互动数据等。
 ### 参数:
 - id: 微博ID（必填）
 - is_get_long_text: 是否获取长微博全文（默认"true"）
 ### 返回:
 - 微博详细数据，包含完整文本、图片、视频、点赞数、评论数、转发数等

## fetch_post_sub_comments

`GET /api/v1/weibo/web_v2/fetch_post_sub_comments`

<!-- Full path: /api/v1/weibo/web_v2/fetch_post_sub_comments -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| id | string | ✅ | 主评论ID/Comment ID | 5283574244704555 |
| count | integer |  | 子评论数量/Number of sub-comments (default: 10) | 10 |
| max_id | string |  | 分页标识/Page identifier (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定评论的回复（子评论）列表。
 ### 参数:
 - id: 主评论ID（必填）
 - count: 子评论数量（默认10）
 - max_id: 翻页游标，首次请求传空，后续请求使用返回的max_id值
 ### 返回:
 - 子评论列表数据，包含回复内容、回复者信息、点赞数等
 - 包含 max_id 字段用于翻页
 ### 注意:
 - 与fetch_post_comments的区别：本接口获取的是评论的回复，而非微博的主评论

## fetch_search

`GET /api/v1/weibo/web/fetch_search`

<!-- Full path: /api/v1/weibo/web/fetch_search -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | '搜索关键词，支持话题搜索如 #话题名#/Search keyword, supports hashtag like #topic#' | 游戏 |
| page | integer |  | >- (default: 1) | 1 |
| search_type | string |  | '搜索类型/Search type: 1=综合, 61=实时, 3=用户, 60=热门, 64=视频, 63=图片, 21=文章' (default: '1') | 1 |
| time_scope | string |  | '时间范围/Time scope: hour=一小时内, day=一天内, week=一周内, month=一个月内, null=不限' |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 搜索微博内容
### 参数:
- **keyword**: 搜索关键词
    - 普通搜索: `游戏`、`新闻`
    - 话题搜索: `#话题名#`（如 `#大冰建议女生不要找老登#`）
- **page**: 页码
    - 从 **1** 开始递增: 1, 2, 3, 4...
    - 每页约返回 10-20 条结果
    - **不是** 1, 10, 20 这种偏移量模式
- **search_type**: 搜索类型
    - **1**: 综合（默认，按相关性排序）
    - **61**: 实时（按时间排序，最新优先）
    - **3**: 用户（搜索用户账号）
    - **60**: 热门（按热度排序）
    - **64**: 视频（仅视频内容）
    - **63**: 图片（仅图片内容）
    - **21**: 文章（仅长文章）
- **time_scope**: 时间范围筛选
    - **null/不传**: 不限时间（默认）
    - **hour**: 一小时内
    - **day**: 一天内（24小时）
    - **week**: 一周内
    - **month**: 一个月内
### 返回:
- 搜索结果列表
### 注意:
- 此接口会自动生成游客Cookie，无需登录即可使用
- 如遇到 432 错误，系统会自动重试

## fetch_similar_search

`GET /api/v1/weibo/web_v2/fetch_similar_search`

<!-- Full path: /api/v1/weibo/web_v2/fetch_similar_search -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 搜索关键词/Search keyword | #微博奇遇记# |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 根据关键词获取微博推荐的相似搜索词。
 ### 参数:
 - keyword: 搜索关键词（必填，支持话题标签格式如#话题名#）
 ### 返回:
 - 相似搜索词列表，包含推荐词、搜索次数等
 ### 注意:
 - 相似词推荐相对稳定，可缓存15-30分钟

## fetch_social_ranking

`GET /api/v1/weibo/web_v2/fetch_social_ranking`

<!-- Full path: /api/v1/weibo/web_v2/fetch_social_ranking -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取微博社会榜单数据（时事新闻、社会热点、民生话题等）。
 ### 参数:
 - 无需额外参数
 ### 返回:
 - 社会话题列表，包含话题、热度值、排名、分类等
 ### 注意:
 - 社会热点变化较快，建议缓存2-5分钟

## fetch_status_comments

`GET /api/v1/weibo/app/fetch_status_comments`

<!-- Full path: /api/v1/weibo/app/fetch_status_comments -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| status_id | string | ✅ | 微博ID | 5258708168476831 |
| max_id | string |  | 翻页游标 |  |
| sort_type | string |  | '排序类型: 0=按热度排序, 1=按时间排序' (default: '0') | 0 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定微博的一级评论列表（也适用于视频评论）。
 ### 参数:
 - status_id: 微博ID或视频ID（必填）
 - max_id: 翻页游标，首次请求不传，后续请求使用返回的max_id值
    - max_id json path: $.data.moreInfo.params.max_id
- sort_type: 评论排序类型
    - 0: 按热度排序（默认）
    - 1: 按时间排序
### 返回:
 - 评论列表数据，包含评论内容、评论者信息、点赞数等
 - 包含 max_id 字段用于翻页
 ### 注意:
 - 每次返回约20条评论
 - 当没有更多评论时，max_id 为空或相同

## fetch_status_detail

`GET /api/v1/weibo/app/fetch_status_detail`

<!-- Full path: /api/v1/weibo/app/fetch_status_detail -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| status_id | string | ✅ | 微博ID | 5016922058656962 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定微博的详细信息。
 ### 参数:
 - status_id: 微博ID（必填）
 ### 返回:
 - 微博详细数据，包含完整文本、图片、视频、点赞数、评论数、转发数等
 ### 注意:
 - 如果微博已被删除或设置为私密，可能无法获取

## fetch_status_likes

`GET /api/v1/weibo/app/fetch_status_likes`

<!-- Full path: /api/v1/weibo/app/fetch_status_likes -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| status_id | string | ✅ | 微博ID | 5016922058656962 |
| attitude_type | string |  | '点赞类型: 0=全部, 1=点赞, 2=开心, 3=惊讶, 4=伤心, 5=愤怒, 6=打赏, 8=抱抱' (default: '0') | 0 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取指定微博的点赞列表（也适用于视频点赞）。
### 参数:
- status_id: 微博ID或视频ID（必填）
- attitude_type: 点赞类型筛选
    - 0: 全部（默认）
    - 1: 点赞
    - 2: 开心
    - 3: 惊讶
    - 4: 伤心
    - 5: 愤怒
    - 6: 打赏
    - 8: 抱抱
### 返回:
- 点赞列表数据，包含点赞者信息、点赞类型等
### 注意:
- 每次返回约50条点赞记录

## fetch_status_reposts

`GET /api/v1/weibo/app/fetch_status_reposts`

<!-- Full path: /api/v1/weibo/app/fetch_status_reposts -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| status_id | string | ✅ | 微博ID | 5016922058656962 |
| max_id | string |  | 翻页游标 |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定微博的转发列表（也适用于视频转发）。
 ### 参数:
 - status_id: 微博ID或视频ID（必填）
 - max_id: 翻页游标，首次请求不传，后续请求使用返回的max_id值
 ### 返回:
 - 转发列表数据，包含转发内容、转发者信息等
 - 包含 max_id 字段用于翻页
 ### 注意:
 - 每次返回约20条转发
 - 当没有更多转发时，max_id 为空或相同

## fetch_user_info_detail

`GET /api/v1/weibo/app/fetch_user_info_detail`

<!-- Full path: /api/v1/weibo/app/fetch_user_info_detail -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| uid | string | ✅ | 用户ID | 7648703289 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取微博用户的详细信息，比基本信息更加完整，包括认证信息、标签、等级等。
 ### 参数:
 - uid: 用户ID（必填）
 ### 返回:
 - 用户详细信息数据
 ### 注意:
 - 如果用户设置了隐私保护，部分信息可能无法获取

## fetch_user_original_posts

`GET /api/v1/weibo/web_v2/fetch_user_original_posts`

<!-- Full path: /api/v1/weibo/web_v2/fetch_user_original_posts -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| uid | string | ✅ | 用户id/User id | 7277477906 |
| page | integer |  | 页数/Page number (default: 1) | 1 |
| since_id | string |  | 翻页标识，用于获取下一页数据/Pagination identifier for getting next page data (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定用户发布的原创微博列表（排除转发内容）。
 ### 参数:
 - uid: 用户ID（必填）
 - page: 页码，从1开始（默认1）
 - since_id: 翻页标识（第一页必须从fetch_user_posts接口获取）
 ### 返回:
 - 原创微博列表，包含微博内容、图片、视频、互动数据等
 ### 注意:
 - 与fetch_user_posts的区别：本接口只返回原创微博，排除转发
 - since_id必须先调用fetch_user_posts获取，第一页必传，后续页面不传

## fetch_user_posts

`GET /api/v1/weibo/web/fetch_user_posts`

<!-- Full path: /api/v1/weibo/web/fetch_user_posts -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| uid | string | ✅ | 用户ID/User ID | 7277477906 |
| page | integer |  | 页码/Page number (default: 1) | 1 |
| since_id | string |  | 翻页ID，从上一页结果获取/Pagination ID from previous page |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取微博用户的微博列表
### 参数:
- uid: 用户ID
- page: 页码，默认1
- since_id: 翻页用的ID，从上一页返回结果中获取
### 返回:
- 用户微博列表

## fetch_user_posts

`GET /api/v1/weibo/web/fetch_user_posts`

<!-- Full path: /api/v1/weibo/web_v2/fetch_user_posts -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| uid | string | ✅ | 用户id/User id | 7277477906 |
| page | integer |  | 页数/Page number (default: 1) | 1 |
| feature | integer |  | >- (default: 0) | 0 |
| since_id | string |  | 翻页标识，用于获取下一页数据/Pagination identifier for getting next page data (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定用户发布的微博列表，支持分页和多种数据详细程度。
 ### 参数:
 - uid: 用户ID（必填）
 - page: 页码，从1开始（默认1）
 - feature: 数据特征值（默认0）
    - 0: 返回10条基础数据
    - 1: 返回20条扩展数据
    - 2: 返回20条图片相关数据
    - 3: 返回20条完整数据
- since_id: 翻页标识，用于获取下一页数据
 ### 返回:
 - 微博列表数据，包含微博内容、图片、视频等信息
 - 包含 since_id 字段用于翻页
 ### 注意:
 - feature=0性能最佳，feature=3数据最全

## fetch_user_recommend_timeline

`GET /api/v1/weibo/web_v2/fetch_user_recommend_timeline`

<!-- Full path: /api/v1/weibo/web_v2/fetch_user_recommend_timeline -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| refresh | integer |  | 刷新类型，0=正常刷新，1=强制刷新/Refresh type, 0=normal refresh, 1=force refresh (default: 0) | 0 |
| group_id | string |  | 分组ID/Group ID (default: '102803') | 102803 |
| containerid | string |  | 容器ID/Container ID (default: '102803') | 102803 |
| extparam | string |  | 扩展参数/Extended parameters (default: discover|new_feed) | discover\|new_feed |
| max_id | string |  | 最大ID/Max ID (default: '0') | 0 |
| count | integer |  | 获取数量/Count (default: 10) | 10 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取微博主页的推荐时间轴内容，基于用户兴趣展示个性化推荐。
 ### 参数:
 - refresh: 刷新类型（0=正常刷新，1=强制刷新）
 - group_id: 分组ID（可通过fetch_all_groups获取）
 - containerid: 容器ID（通常与group_id相同）
 - extparam: 扩展参数（默认"discover|new_feed"）
 - max_id: 翻页游标，首次请求传"0"
 - count: 获取数量（默认10，建议5-20）
 ### 返回:
 - 推荐微博列表，包含微博内容、作者信息、互动数据等
 - 包含 max_id 字段用于翻页
 ### 注意:
 - 建议先调用fetch_all_groups获取可用分组

## fetch_user_timeline

`GET /api/v1/weibo/app/fetch_user_timeline`

<!-- Full path: /api/v1/weibo/app/fetch_user_timeline -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| uid | string | ✅ | 用户ID | 7648703289 |
| page | integer |  | 页码 (default: 1) | 1 |
| filter_type | string |  | 筛选类型 (default: all) | all |
| month | string |  | 时间筛选(YYYYMMDD格式) | 20251010 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定用户发布的微博列表，支持分页和多种内容筛选。
 ### 参数:
 - uid: 用户ID（必填）
 - page: 页码，从1开始（默认1）
 - filter_type: 筛选类型（默认"all"）
    - all: 全部微博
    - original: 原创微博
    - likes: 她/他的赞
    - video: 视频微博
    - pic: 图片微博
    - location: 签到足迹
    - month: 按时间筛选（需要同时传入month参数）
- month: 时间筛选参数，格式YYYYMMDD（仅当filter_type=month时使用）
 ### 返回:
 - 微博列表数据，包含微博内容、图片、视频等信息
 ### 注意:
 - 如果用户设置了隐私保护，可能无法获取微博列表
 - 每页返回数量约为20条微博
 - 使用时间筛选时必须同时指定filter_type=month和month参数

## fetch_user_video_collection_detail

`GET /api/v1/weibo/web_v2/fetch_user_video_collection_detail`

<!-- Full path: /api/v1/weibo/web_v2/fetch_user_video_collection_detail -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| cid | string | ✅ | 收藏夹ID/Collection ID | 4883992307236954 |
| cursor | string |  | 分页游标/Pagination cursor (default: '') |  |
| tab_code | integer |  | '排序方式：0=默认，1=最热，2=最新/Sort type: 0=default, 1=hottest, 2=latest' (default: 0) | 0 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定收藏夹的详细内容，包括视频列表。
 ### 参数:
 - cid: 收藏夹ID（必填，从fetch_user_video_collection_list获取）
 - cursor: 分页游标，首次请求传空，后续使用返回的cursor
 - tab_code: 排序方式（0=默认，1=最热，2=最新）
 ### 返回:
 - 收藏夹信息和视频列表，包含视频标题、封面、时长、播放数等
 - 包含 next_cursor 和 has_more 字段用于翻页
 ### 注意:
 - 不同排序方式的cursor不通用，切换排序需重新开始分页

## fetch_user_video_collection_list

`GET /api/v1/weibo/web_v2/fetch_user_video_collection_list`

<!-- Full path: /api/v1/weibo/web_v2/fetch_user_video_collection_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| uid | string | ✅ | 用户ID/User ID | 7277477906 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定用户的视频收藏夹列表。
 ### 参数:
 - uid: 用户ID（必填）
 ### 返回:
 - 收藏夹列表，包含收藏夹ID、名称、描述、视频数量等
 ### 注意:
 - 收藏夹列表受用户隐私设置影响
 - 部分用户可能没有创建视频收藏夹

## fetch_user_video_list

`GET /api/v1/weibo/web_v2/fetch_user_video_list`

<!-- Full path: /api/v1/weibo/web_v2/fetch_user_video_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| uid | string | ✅ | 用户ID/User ID | 7277477906 |
| cursor | string |  | 分页游标/Pagination cursor (default: '0') | 0 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定用户发布的所有视频内容（瀑布流展示）。
 ### 参数:
 - uid: 用户ID（必填）
 - cursor: 翻页游标，初次请求传"0"，后续请求使用返回的next_cursor值
 ### 返回:
 - 视频列表数据，包含视频标题、封面、播放量等信息
 - 包含 next_cursor 和 has_more 字段用于翻页
 ### 注意:
 - 与收藏夹接口的区别：本接口获取用户发布的视频，收藏夹接口获取用户收藏的视频

## fetch_video_detail

`GET /api/v1/weibo/app/fetch_video_detail`

<!-- Full path: /api/v1/weibo/app/fetch_video_detail -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| mid | string | ✅ | 视频微博ID | 5242977759006596 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取单个视频的详细信息，包括视频播放地址。
 - **重要**: 从微博视频链接（如
https://weibo.com/tv/show/1034:5232127105761312）获取真实视频ID的必需步骤
 ### 参数:
 - mid: 视频微博ID或链接中的ID（必填）
 ### 返回:
 - 视频详细数据，包含视频播放地址、封面、时长、标题等
 - **items[0].data.idstr**: 真实的视频微博ID，可用于获取评论等操作
 ### 注意:
 - 返回的视频地址可能有时效性
 - 支持获取高清视频地址
 - **获取评论前必须先调用此接口**: 链接中的ID不能直接用于获取评论，需要先通过此接口获取 items[0].data.idstr
中的真实ID

## search_user_posts

`GET /api/v1/weibo/web_v2/search_user_posts`

<!-- Full path: /api/v1/weibo/web_v2/search_user_posts -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| uid | string | ✅ | 用户ID/User ID | 7277477906 |
| q | string |  | 搜索关键词/Search keyword (default: '') |  |
| page | integer |  | 页数/Page number (default: 1) | 1 |
| starttime | string |  | 开始时间戳/Start timestamp (default: 1772294400) | 1772294400 |
| endtime | string |  | 结束时间戳/End timestamp (default: 1772294400) | 1772294400 |
| hasori | integer |  | 是否包含原创微博，1=包含，0=不包含/Include original posts, 1=include, 0=exclude (default: 1) | 1 |
| hasret | integer |  | 是否包含转发微博，1=包含，0=不包含/Include retweets, 1=include, 0=exclude (default: 1) | 1 |
| hastext | integer |  | 是否包含文字微博，1=包含，0=不包含/Include text posts, 1=include, 0=exclude (default: 1) | 1 |
| haspic | integer |  | 是否包含图片微博，1=包含，0=不包含/Include image posts, 1=include, 0=exclude (default: 1) | 1 |
| hasvideo | integer |  | 是否包含视频微博，1=包含，0=不包含/Include video posts, 1=include, 0=exclude (default: 1) | 1 |
| hasmusic | integer |  | 是否包含音乐微博，1=包含，0=不包含/Include music posts, 1=include, 0=exclude (default: 1) | 1 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 在指定用户的微博中搜索包含特定关键词的内容。
 ### 参数:
 - uid: 用户ID（必填）
 - q: 搜索关键词（非必填，空字符串表示搜索全部内容）
 - page: 页码，从1开始（默认1）
 - starttime: 开始时间戳（可选，Unix时间戳格式）
 - endtime: 结束时间戳（可选，Unix时间戳格式）
 - hasori: 是否包含原创（默认1包含）
 - hasret: 是否包含转发（默认1包含）
 - hastext: 是否包含文字（默认1包含）
 - haspic: 是否包含图片（默认1包含）
 - hasvideo: 是否包含视频（默认1包含）
 - hasmusic: 是否包含音乐（默认1包含）
 ### 返回:
 - 搜索结果列表，包含微博内容、作者信息、互动数据等
 ### 注意:
 - 搜索结果受用户隐私设置影响
 - 时间戳参数使用Unix时间戳格式

---

See SKILL.md for cross-group orchestration patterns.