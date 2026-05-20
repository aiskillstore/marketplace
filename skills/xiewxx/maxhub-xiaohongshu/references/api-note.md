# Note Data API / 笔记数据接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---
## extract_share_info

`GET /api/v1/xiaohongshu/app/extract_share_info`

<!-- Full path: /api/v1/xiaohongshu/app/extract_share_info -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| share_link | string | ✅ | 分享链接/Share link | https://xhslink.com/a/EZ4M9TwMA6c3 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 从分享链接中提取笔记ID和xsec_token
### 参数:
- share_link: 小红书分享链接，支持短链接和长链接
### 返回:
- 提取的信息对象，包含：
    - note_id: 笔记ID
    - xsec_token: 安全令牌（如果URL中包含）
 ### 使用说明:
- 支持短链接格式：https://xhslink.com/a/xxxxx
- 支持长链接格式：
    - https://www.xiaohongshu.com/discovery/item/xxxxx
    - https://www.xiaohongshu.com/explore/xxxxx
- 短链接会自动重定向获取真实链接
- 提取的note_id可用于get_note_info接口

## fetch_feed_notes_v2

`GET /api/v1/xiaohongshu/web_v2/fetch_feed_notes_v2`

<!-- Full path: /api/v1/xiaohongshu/web_v2/fetch_feed_notes_v2 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| note_id | string | ✅ | 笔记ID/Note ID | 66c9cc31000000001f03a4bc |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取单一笔记和推荐笔记
 ### 接口优先级:
 - 小红书接口推荐优先级: `App V2` > `App` > `Web V2（本接口）` > `Web`
 ### 参数:
 - note_id: 笔记ID，可以从小红书的分享链接中获取
 ### 返回:
 - 单一笔记和推荐笔记

## fetch_feed_notes_v3

`GET /api/v1/xiaohongshu/web_v2/fetch_feed_notes_v3`

<!-- Full path: /api/v1/xiaohongshu/web_v2/fetch_feed_notes_v3 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| short_url | string | ✅ | 短链/Short URL | http://xhslink.com/a/tyoREa3ciaAeb |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取单一笔记和推荐笔记
 ### 参数:
 - short_url: 短链，可以从小红书的分享链接中获取
 ### 返回:
 - 单一笔记和推荐笔记

## fetch_feed_notes_v4

`GET /api/v1/xiaohongshu/web_v2/fetch_feed_notes_v4`

<!-- Full path: /api/v1/xiaohongshu/web_v2/fetch_feed_notes_v4 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| note_id | string | ✅ | 笔记ID/Note ID | 66c9cc31000000001f03a4bc |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取单一笔记和推荐笔记，结构不同互动量有延时
 ### 参数:
 - note_id: 笔记ID，可以从小红书的分享链接中获取
 ### 返回:
 - 单一笔记和推荐笔记

## fetch_feed_notes_v5

`GET /api/v1/xiaohongshu/web_v2/fetch_feed_notes_v5`

<!-- Full path: /api/v1/xiaohongshu/web_v2/fetch_feed_notes_v5 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| note_id | string | ✅ | 笔记ID/Note ID | 66c9cc31000000001f03a4bc |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取单一笔记和推荐笔记，结构不同互动量有缺失
 ### 参数:
 - note_id: 笔记ID，可以从小红书的分享链接中获取
 ### 返回:
 - 单一笔记和推荐笔记
 ### 备注:
 - 互动数据仅有点赞数，没有评论数与收藏数

## fetch_home_notes

`GET /api/v1/xiaohongshu/web_v2/fetch_home_notes`

<!-- Full path: /api/v1/xiaohongshu/web_v2/fetch_home_notes -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string | ✅ | 用户ID/User ID | 5e3a8ee700000000010070c6 |
| cursor | string |  | 游标/Cursor (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取主页笔记
### 参数:
- user_id: 用户ID
- cursor: 游标
### 返回:
- 主页笔记

## fetch_home_notes_app

`GET /api/v1/xiaohongshu/web_v2/fetch_home_notes_app`

<!-- Full path: /api/v1/xiaohongshu/web_v2/fetch_home_notes_app -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string | ✅ | 用户ID/User ID | 5e3a8ee700000000010070c6 |
| cursor | string |  | 游标/Cursor (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取App主页笔记
### 参数:
- user_id: 用户ID
- cursor: 游标
### 返回:
- 主页笔记

## fetch_homefeed

`GET /api/v1/xiaohongshu/web_v3/fetch_homefeed`

<!-- Full path: /api/v1/xiaohongshu/web_v3/fetch_homefeed -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| num | integer |  | 返回数量，最大40/Number of results, max 40 (default: 20) | 20 |
| cursor_score | string |  | 翻页游标/Pagination cursor (default: '') |  |
| category | string |  | 分类频道ID/Category channel ID (default: homefeed_recommend) | homefeed_recommend |
| need_filter_image | boolean |  | 仅图文/Image notes only (default: false) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取首页推荐笔记列表
 ### 接口优先级:
 - 小红书接口推荐优先级: `App V2` > `App` > `Web V3（本接口）` > `Web V2` > `Web`
 ### 参数:
 - num: 返回数量 (最大 40)
 - cursor_score: 翻页游标 (首次留空)
 - category: 分类频道 ID (从 /fetch_homefeed_categories 获取)
 - need_filter_image: true=只看图文, false=综合推荐(含视频)
 ### 返回:
 - 推荐笔记列表

## fetch_homefeed_categories

`GET /api/v1/xiaohongshu/web_v3/fetch_homefeed_categories`

<!-- Full path: /api/v1/xiaohongshu/web_v3/fetch_homefeed_categories -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取首页频道分类列表
 ### 接口优先级:
 - 小红书接口推荐优先级: `App V2` > `App` > `Web V3（本接口）` > `Web V2` > `Web`
 ### 返回:
 - 分类列表

## fetch_hot_list

`GET /api/v1/xiaohongshu/web_v2/fetch_hot_list`

<!-- Full path: /api/v1/xiaohongshu/web_v2/fetch_hot_list -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取小红书热榜
### 返回:
- 小红书热榜

## fetch_note_comments

`GET /api/v1/xiaohongshu/web_v2/fetch_note_comments`

<!-- Full path: /api/v1/xiaohongshu/web_v2/fetch_note_comments -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| note_id | string | ✅ | 笔记ID/Note ID | 651ccaa9000000001f03d7f7 |
| cursor | string |  | 游标/Cursor (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取笔记评论
### 参数:
- note_id: 笔记ID
- cursor: 游标
### 返回:
- 笔记评论

## fetch_note_comments

`GET /api/v1/xiaohongshu/web_v2/fetch_note_comments`

<!-- Full path: /api/v1/xiaohongshu/web_v3/fetch_note_comments -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| note_id | string | ✅ | 笔记ID/Note ID | 69f0817d000000002301ca13 |
| cursor | string |  | 游标/Cursor (default: '') |  |
| xsec_token | string | ✅ | >- | ABkUO3R6tKvwMzj0Y3pFBbab4YWPXwLhp7gfbNpfYY8Bg= |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取笔记评论列表
 ### 接口优先级:
 - 小红书接口推荐优先级: `App V2` > `App` > `Web V3（本接口）` > `Web V2` > `Web`
 ### 参数:
 - note_id: 笔记ID
 - cursor: 翻页游标
 - xsec_token: 安全令牌，可以从小红书的分享链接中获取（XHS 已升级评论接口风控，必填）
 ### 返回:
 - 评论列表

## fetch_note_detail

`GET /api/v1/xiaohongshu/web_v3/fetch_note_detail`

<!-- Full path: /api/v1/xiaohongshu/web_v3/fetch_note_detail -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| note_id | string | ✅ | 笔记ID/Note ID | 697ee7f5000000001a0225c1 |
| xsec_token | string | ✅ | >- | ABkR6BvFSbUES4IbFcbjZrtCRa3FSqpqsa1KjFLyurW8U= |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取笔记详情（图文/视频通用）
 ### 接口优先级:
 - 小红书接口推荐优先级: `App V2` > `App` > `Web V3（本接口）` > `Web V2` > `Web`
 ### 参数:
 - note_id: 笔记ID，可以从小红书的分享链接中获取
 - xsec_token: 安全令牌，可以从小红书的分享链接中获取
 ### 返回:
 - 笔记详情数据

## fetch_note_image

`GET /api/v1/xiaohongshu/web_v2/fetch_note_image`

<!-- Full path: /api/v1/xiaohongshu/web_v2/fetch_note_image -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| note_id | string | ✅ | 笔记ID/Note ID | 66c9cc31000000001f03a4bc |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取小红书笔记图片
 ### 参数:
 - note_id: 笔记ID，可以从小红书的分享链接中获取
 ### 返回:
 - 小红书笔记图片

## fetch_search_notes

`GET /api/v1/xiaohongshu/web_v2/fetch_search_notes`

<!-- Full path: /api/v1/xiaohongshu/web_v2/fetch_search_notes -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keywords | string | ✅ | 搜索关键词/Search keywords | 口红 |
| page | integer |  | 页码/Page number (default: 1) |  |
| sort_type | string |  | 排序方式/Sort type (default: general) |  |
| note_type | string |  | 笔记类型/Note type (default: '0') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取搜索笔记
### 参数:
- keywords：搜索关键词
- sort_type：排序方式
    - general：综合
    - time_descending：最新
    - popularity_descending：最热
- note_type: 笔记类型
    - 0：全部
    - 1：视频
    - 2：图文
### 返回:
- 搜索笔记

## fetch_search_notes

`GET /api/v1/xiaohongshu/web_v2/fetch_search_notes`

<!-- Full path: /api/v1/xiaohongshu/web_v3/fetch_search_notes -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 搜索关键词/Search keywords | 口红 |
| page | integer |  | 页码/Page number (default: 1) |  |
| sort | string |  | 排序方式/Sort type (default: general) |  |
| note_type | integer |  | 笔记类型/Note type (default: 0) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 搜索笔记
 ### 接口优先级:
 - 小红书接口推荐优先级: `App V2` > `App` > `Web V3（本接口）` > `Web V2` > `Web`
 ### 参数:
 - keyword: 搜索关键词
 - page: 页码
 - sort: 排序方式
    - general: 综合
    - time_descending: 最新
    - popularity_descending: 最热
- note_type: 笔记类型
    - 0: 全部
    - 1: 图文
    - 2: 视频
### 返回:
 - 搜索结果

## fetch_sub_comments

`GET /api/v1/xiaohongshu/web_v2/fetch_sub_comments`

<!-- Full path: /api/v1/xiaohongshu/web_v2/fetch_sub_comments -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| note_id | string | ✅ | 笔记ID/Note ID | 673c894c0000000007033f92 |
| comment_id | string | ✅ | 评论ID/Comment ID | 673ecdfc000000001503bf8b |
| cursor | string |  | 游标/Cursor (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取子评论
### 参数:
- note_id: 笔记ID
- comment_id: 评论ID
- cursor: 游标
### 返回:
- 子评论

## fetch_sub_comments

`GET /api/v1/xiaohongshu/web_v2/fetch_sub_comments`

<!-- Full path: /api/v1/xiaohongshu/web_v3/fetch_sub_comments -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| note_id | string | ✅ | 笔记ID/Note ID | 69f08d5f00000000350397ba |
| root_comment_id | string | ✅ | 父评论ID/Root comment ID | 69f09736000000002803832e |
| num | integer |  | 数量/Number (default: 10) |  |
| cursor | string |  | 游标/Cursor (default: '') |  |
| xsec_token | string | ✅ | >- | ABkUO3R6tKvwMzj0Y3pFBbaUK6gBt3Yj1Br95ogIzuXyI= |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取评论的子评论（回复）
 ### 接口优先级:
 - 小红书接口推荐优先级: `App V2` > `App` > `Web V3（本接口）` > `Web V2` > `Web`
 ### 参数:
 - note_id: 笔记ID
 - root_comment_id: 父评论ID
 - num: 返回数量
 - cursor: 翻页游标
 - xsec_token: 安全令牌，可以从小红书的分享链接中获取（XHS 已升级评论接口风控，必填）
 ### 返回:
 - 子评论列表

## fetch_user_info

`GET /api/v1/xiaohongshu/web_v2/fetch_user_info`

<!-- Full path: /api/v1/xiaohongshu/web_v2/fetch_user_info -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string | ✅ | 用户ID/User ID | 5e3a8ee700000000010070c6 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取用户信息
### 参数:
- user_id: 用户ID
### 返回:
- 用户信息

## fetch_user_info

`GET /api/v1/xiaohongshu/web_v2/fetch_user_info`

<!-- Full path: /api/v1/xiaohongshu/web_v3/fetch_user_info -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string | ✅ | 用户ID/User ID | 5e3a8ee700000000010070c6 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取用户公开资料
 ### 接口优先级:
 - 小红书接口推荐优先级: `App V2` > `App` > `Web V3（本接口）` > `Web V2` > `Web`
 ### 参数:
 - user_id: 用户ID
 ### 返回:
 - 用户信息

## fetch_user_info_app

`GET /api/v1/xiaohongshu/web_v2/fetch_user_info_app`

<!-- Full path: /api/v1/xiaohongshu/web_v2/fetch_user_info_app -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string | ✅ | 用户ID/User ID | 5e3a8ee700000000010070c6 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取用户信息
### 参数:
- user_id: 用户ID
### 返回:
- 用户信息

## fetch_user_notes

`GET /api/v1/xiaohongshu/web_v3/fetch_user_notes`

<!-- Full path: /api/v1/xiaohongshu/web_v3/fetch_user_notes -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string | ✅ | 用户ID/User ID | 5e3a8ee700000000010070c6 |
| cursor | string |  | 游标/Cursor (default: '') |  |
| num | integer |  | 数量/Number (default: 30) | 30 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取用户发布的笔记列表
 ### 接口优先级:
 - 小红书接口推荐优先级: `App V2` > `App` > `Web V3（本接口）` > `Web V2` > `Web`
 ### 参数:
 - user_id: 用户ID
 - cursor: 翻页游标
 - num: 返回数量 (最大 30)
 ### 返回:
 - 用户笔记列表

## get_creator_hot_inspiration_feed

`GET /api/v1/xiaohongshu/app_v2/get_creator_hot_inspiration_feed`

<!-- Full path: /api/v1/xiaohongshu/app_v2/get_creator_hot_inspiration_feed -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| cursor | string |  | 分页游标，首次请求留空/Pagination cursor, leave empty for first request (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取创作者中心的热点创作灵感流，使用游标分页
 ### 参数:
 - cursor: 分页游标，首次请求留空，翻页时传入上一次响应中返回的 cursor 值（如 "1", "2"...）
 ### 返回:
 - 热点灵感列表数据
 ### 翻页说明:
 - 首次请求：cursor 留空
 - 翻页请求：传入上一次响应中返回的 cursor 值

## get_creator_inspiration_feed

`GET /api/v1/xiaohongshu/app_v2/get_creator_inspiration_feed`

<!-- Full path: /api/v1/xiaohongshu/app_v2/get_creator_inspiration_feed -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| cursor | string |  | 分页游标，首次请求留空/Pagination cursor, leave empty for first request (default: '') |  |
| tab | integer |  | 标签类型/Tab type (default: 0) | 0 |
| source | string |  | 来源/Source (default: creator_center) | creator_center |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取创作者中心的推荐创作灵感流，使用游标分页
 ### 参数:
 - cursor: 分页游标，首次请求留空，翻页时传入上一次响应中返回的 cursor 值（如 "r_1", "r_2"...）
 - tab: 标签类型，默认 0
 - source: 来源，默认 "creator_center"
 ### 返回:
 - 推荐灵感列表数据
 ### 翻页说明:
 - 首次请求：cursor 留空
 - 翻页请求：传入上一次响应中返回的 cursor 值

## get_home_recommend

`POST /api/v1/xiaohongshu/web/get_home_recommend`

<!-- Full path: /api/v1/xiaohongshu/web/get_home_recommend -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取首页推荐
 ### 接口优先级:
 - 小红书接口推荐优先级: `App V2` > `App` > `Web V2` > `Web（本接口）`
 ### 参数:
 - feed_type: 推荐类型
    - 全部: 0
    - 穿搭: 1
    - 美食: 2
    - 彩妆: 3
    - 影视: 4
    - 职场: 5
    - 情感: 6
    - 家居: 7
    - 游戏: 8
    - 旅行: 9
    - 健身: 10
- need_filter_image: 是否只看图文笔记，默认为 False
 - cookie: 可选参数，用户自行提供的已登录的网页Cookie获取个性化推荐，如果不提供，则使用游客模式
 - proxy: 可选参数，网络代理，可降低封号概率，格式：http://用户名:密码@IP:端口/Proxy, format:
http://username:password@IP:port
 ### 返回:
 - 推荐列表

## get_image_note_detail

`GET /api/v1/xiaohongshu/app_v2/get_image_note_detail`

<!-- Full path: /api/v1/xiaohongshu/app_v2/get_image_note_detail -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| note_id | string |  | 笔记ID/Note ID (default: '') | 697c0eee000000000a03c308 |
| share_text | string |  | 分享链接/Share link (default: '') | http://xhslink.com/o/8GqargIxrko |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取图文笔记的完整详情数据
 ### 接口优先级:
 - ⭐ 小红书接口推荐优先级: `App V2（本接口）` > `App` > `Web V2` > `Web`
 ### 参数:
 - note_id: 笔记ID，如 "697c0eee000000000a03c308"
 - share_text: 小红书分享链接（支持APP和Web端分享链接）
 - 优先使用`note_id`，如果没有则使用`share_text`，两个参数二选一，如都携带则以`note_id`为准。
 ### 返回:
 - 图文笔记详情数据，包含笔记内容、图片列表、作者信息、互动数据等

## get_note_comment_replies

`GET /api/v1/xiaohongshu/web/get_note_comment_replies`

<!-- Full path: /api/v1/xiaohongshu/web/get_note_comment_replies -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| note_id | string | ✅ | 笔记ID/Note ID | 6683b283000000001f0052bf |
| comment_id | string | ✅ | 评论ID/Comment ID | 6683ec5b000000000303b91a |
| lastCursor | string |  | 上一页的游标/Last cursor |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取笔记评论回复 V1
 ### 参数:
 - note_id: 笔记ID，可以从小红书的分享链接中获取
 - comment_id: 评论ID
 - lastCursor: 第一次请求时为空，之后请求时使用上一次请求响应中返回的游标
 ### 返回:
 - 笔记评论回复列表

## get_note_comments

`GET /api/v1/xiaohongshu/app/get_note_comments`

<!-- Full path: /api/v1/xiaohongshu/app/get_note_comments -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| note_id | string | ✅ | 笔记ID/Note ID | 677d1909000000002002a892 |
| start | string |  | 翻页游标/Pagination cursor | 682b0133000000001c03618d |
| sort_strategy | integer |  | '排序策略：1-默认排序，2-最新评论/Sort strategy: 1-default, 2-latest' (default: 1) | 1 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取笔记的评论列表
### 参数:
- note_id: 笔记ID（必需）
- start: 翻页游标，从上一次请求的响应中获取，支持两种格式：
    1. 简单格式: "682b0133000000001c03618d"
    2. JSON格式: {"cursor":"682b0133000000001c03618d","index":2,"pageArea":"ALL"}
- sort_strategy: 排序策略
    - 1: 默认排序（默认值）
    - 2: 按最新评论排序
### 返回:
- 评论数据对象，包含：
    - comments: 评论列表数组，每个评论包含：
        - id: 评论ID
        - content: 评论内容
        - create_time: 创建时间戳
        - user_info: 评论者信息
            - user_id: 用户ID
            - nickname: 昵称
            - image: 头像URL
        - interact_info: 互动数据
            - liked_count: 点赞数
        - sub_comment_count: 子评论数量
        - sub_comment_cursor: 子评论翻页游标（如有子评论）
    - cursor: 翻页游标，用于获取下一页
    - has_more: 是否有更多数据（布尔值）
    - total: 总评论数
 ### 翻页说明:
- 首次请求不传start参数
- 获取下一页时，将上一次返回的cursor作为start参数传入
- 当has_more为false时，表示没有更多数据

## get_note_comments

`GET /api/v1/xiaohongshu/app/get_note_comments`

<!-- Full path: /api/v1/xiaohongshu/app_v2/get_note_comments -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| note_id | string |  | 笔记ID/Note ID (default: '') | 697c0eee000000000a03c308 |
| share_text | string |  | 分享链接/Share link (default: '') | http://xhslink.com/o/8GqargIxrko |
| cursor | string |  | 分页游标，首次请求留空/Pagination cursor, leave empty for first request (default: '') |  |
| index | integer |  | 评论索引，首次请求传0/Comment index, pass 0 for first request (default: 0) | 0 |
| pageArea | string |  | '折叠状态: UNFOLDED(默认-展开), FOLDED(折叠)' (default: UNFOLDED) | UNFOLDED |
| sort_strategy | string |  | '排序策略/Sort strategy: default, latest_v2, like_count' (default: latest_v2) | latest_v2 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定笔记的评论列表，支持分页和多种排序方式
 ### 参数:
 - note_id: 笔记ID，如 "697c0eee000000000a03c308"
 - share_text: 小红书分享链接（支持APP和Web端分享链接）
 - 优先使用`note_id`，如果没有则使用`share_text`，两个参数二选一，如都携带则以`note_id`为准。
 - cursor: 分页游标，首次请求留空，翻页时传入上一次响应中返回的 cursor 值
 - index: 评论索引，首次请求传 0，翻页时传入上一次响应中返回的 index 值
 - pageArea: 折叠状态，默认 "UNFOLDED"（展开），翻页时传入上一次响应中返回的 pageArea 值
 - sort_strategy: 排序策略
    - "latest_v2": 按时间倒序（最新，默认使用）
    - "like_count": 按点赞数排序（最热）
    - "default": 默认排序（不推荐，翻页时会丢失评论或重复抓取评论）
### 返回:
 - 评论数据对象，包含评论列表、分页游标等
 ### 翻页说明:
 - 首次请求：cursor留空，index传0
 - 翻页请求：传入上一次响应中返回的 cursor 和 index 和 pageArea 值

## get_note_comments

`GET /api/v1/xiaohongshu/app/get_note_comments`

<!-- Full path: /api/v1/xiaohongshu/web/get_note_comments -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| note_id | string | ✅ | 笔记ID/Note ID | 6683b283000000001f0052bf |
| lastCursor | string |  | 上一页的游标/Last cursor |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取笔记评论 V1
 ### 参数:
 - note_id: 笔记ID，可以从小红书的分享链接中获取
 - lastCursor: 第一次请求时为空，之后请求时使用上一次请求响应中返回的游标
 ### 返回:
 - 笔记评论列表

## get_note_id_and_xsec_token

`GET /api/v1/xiaohongshu/web/get_note_id_and_xsec_token`

<!-- Full path: /api/v1/xiaohongshu/web/get_note_id_and_xsec_token -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| share_text | string | ✅ | 分享链接/Share link | https://xhslink.com/a/EZ4M9TwMA6c3 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 通过分享链接获取小红书的Note ID 和 xsec_token
 ### 参数:
 - share_text: 小红书分享链接（支持APP和Web端分享链接）
 ### 返回:
 - Note ID 和 xsec_token

## get_note_info

`GET /api/v1/xiaohongshu/app/get_note_info`

<!-- Full path: /api/v1/xiaohongshu/app/get_note_info -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| note_id | string |  | 笔记ID/Note ID (default: '') | 665f95200000000006005624 |
| share_text | string |  | 分享链接/Share link (default: '') | https://xhslink.com/a/EZ4M9TwMA6c3 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取笔记信息 V1
 ### 接口优先级:
 - 小红书接口推荐优先级: `App V2` > `App（本接口）` > `Web V2` > `Web`
 ### 参数:
 - note_id: 笔记ID，可以从小红书的分享链接中获取
 - share_text: 小红书分享链接（支持APP和Web端分享链接）
 - 优先使用`note_id`，如果没有则使用`share_text`，两个参数二选一，如都携带则以`note_id`为准。
 ### 返回:
 - 笔记详情数据，包含以下主要字段：
    - note_id: 笔记ID
    - title: 笔记标题
    - desc: 笔记内容描述
    - type: 笔记类型（normal=图文笔记，video=视频笔记）
    - user: 作者信息对象
        - user_id: 用户ID
        - nickname: 用户昵称
        - avatar: 用户头像URL
    - image_list: 图片列表（图文笔记）
    - video_info: 视频信息（视频笔记）
    - interact_info: 互动数据
        - liked_count: 点赞数
        - collected_count: 收藏数
        - comment_count: 评论数
        - share_count: 分享数
    - tag_list: 话题标签列表
    - time: 发布时间戳
    - ip_location: IP属地

## get_note_info_v2

`GET /api/v1/xiaohongshu/app/get_note_info_v2`

<!-- Full path: /api/v1/xiaohongshu/app/get_note_info_v2 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| note_id | string |  | 笔记ID/Note ID (default: '') | 665f95200000000006005624 |
| share_text | string |  | 分享链接/Share link (default: '') | https://xhslink.com/a/EZ4M9TwMA6c3 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取笔记信息 V2
 - 除赞、评、藏数据之外此接口能获取到笔记的曝光量（impNum）、阅读量（readNum）、关注量（followCnt）。
 - 但是不是每一篇都有，如果是没有被小红书后台收录的笔记，赞评藏数据返回为0，但是笔记内容是完整的。
 - 通过作者userId，可以去作品列表接口拿到赞、评、藏数据
 ### 参数:
 - note_id: 笔记ID，可以从小红书的分享链接中获取
 - share_text: 小红书分享链接（支持APP和Web端分享链接）
 - 优先使用`note_id`，如果没有则使用`share_text`，两个参数二选一，如都携带则以`note_id`为准。
 ### 返回:
 - 笔记详情数据，包含以下主要字段：
    - note_id: 笔记ID
    - title: 笔记标题
    - desc: 笔记内容描述
    - type: 笔记类型（normal=图文笔记，video=视频笔记）
    - user: 作者信息对象
        - user_id: 用户ID
        - nickname: 用户昵称
        - avatar: 用户头像URL
    - image_list: 图片列表（图文笔记）
    - video_info: 视频信息（视频笔记）
    - interact_info: 互动数据
        - liked_count: 点赞数
        - collected_count: 收藏数
        - comment_count: 评论数
        - share_count: 分享数
    - tag_list: 话题标签列表
    - time: 发布时间戳
    - ip_location: IP属地

## get_note_info_v2

`GET /api/v1/xiaohongshu/app/get_note_info_v2`

<!-- Full path: /api/v1/xiaohongshu/web/get_note_info_v2 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| note_id | string |  | 笔记ID/Note ID (default: '') | 665f95200000000006005624 |
| share_text | string |  | 分享链接/Share link (default: '') | https://xhslink.com/a/EZ4M9TwMA6c3 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取笔记信息 V2
 ### 参数:
 - note_id: 笔记ID，可以从小红书的分享链接中获取
 - share_text: 小红书分享链接（支持APP和Web端分享链接）
 - 优先使用`note_id`，如果没有则使用`share_text`，两个参数二选一，如都携带则以`note_id`为准。
 ### 返回:
 - 笔记信息

## get_note_info_v4

`GET /api/v1/xiaohongshu/web/get_note_info_v4`

<!-- Full path: /api/v1/xiaohongshu/web/get_note_info_v4 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| note_id | string |  | 笔记ID/Note ID (default: '') | 665f95200000000006005624 |
| share_text | string |  | 分享链接/Share link (default: '') | https://xhslink.com/a/EZ4M9TwMA6c3 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取笔记信息V4
 ### 参数:
 - note_id: 笔记ID，可以从小红书的分享链接中获取
 - share_text: 小红书分享链接（支持APP和Web端分享链接）
 - 优先使用`note_id`，如果没有则使用`share_text`，两个参数二选一，如都携带则以`note_id`为准。
 ### 返回:
 - 笔记信息

## get_note_info_v5

`POST /api/v1/xiaohongshu/web/get_note_info_v5`

<!-- Full path: /api/v1/xiaohongshu/web/get_note_info_v5 -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取笔记信息V5，用户自行提供Cookie来获取笔记信息
 ### 参数:
 - note_id: 笔记ID，可以从小红书的分享链接中获取
 - xsec_token: X-Sec-Token，可以从搜索接口中获取，分享链接中也有/X-Sec-Token, can be
obtained from the search interface, also in the sharing link
 - cookie: 用户自行提供的已登录的网页Cookie
 - proxy: 代理，格式：http://用户名:密码@IP:端口/Proxy, format:
http://username:password@IP:port
 - 最好使用代理，避免被封号或其他未知问题。
  ### 返回:
 - 笔记信息

## get_note_info_v7

`GET /api/v1/xiaohongshu/web/get_note_info_v7`

<!-- Full path: /api/v1/xiaohongshu/web/get_note_info_v7 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| note_id | string |  | 笔记ID/Note ID (default: '') | 665f95200000000006005624 |
| share_text | string |  | 分享链接/Share link (default: '') | https://xhslink.com/a/EZ4M9TwMA6c3 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取笔记信息V7
 ### 参数:
 - note_id: 笔记ID，可以从小红书的分享链接中获取
 - share_text: 小红书分享链接（支持APP和Web端分享链接）
 - 优先使用`note_id`，如果没有则使用`share_text`，两个参数二选一，如都携带则以`note_id`为准。
 ### 返回:
 - 笔记信息

## get_note_sub_comments

`GET /api/v1/xiaohongshu/app_v2/get_note_sub_comments`

<!-- Full path: /api/v1/xiaohongshu/app_v2/get_note_sub_comments -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| note_id | string |  | 笔记ID/Note ID (default: '') | 699916e6000000001d0253da |
| share_text | string |  | 分享链接/Share link (default: '') | http://xhslink.com/o/8GqargIxrko |
| comment_id | string | ✅ | 父评论ID/Parent comment ID | 699fb9930000000008030db6 |
| cursor | string |  | >- (default: '') |  |
| index | integer |  | >- (default: 1) | 1 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定笔记某条评论下的子评论（回复）列表，使用游标分页
 ### 参数:
 - note_id: 笔记ID，如 "699916e6000000001d0253da"
 - share_text: 小红书分享链接（支持APP和Web端分享链接）
 - 优先使用`note_id`，如果没有则使用`share_text`，两个参数二选一，如都携带则以`note_id`为准。
 - comment_id: 父评论ID（必需），如 "699fb9930000000008030db6"
 - cursor: 分页游标，首次请求留空，翻页时从上一次响应的 `$.data.data.cursor` 中提取 `cursor` 字段的值
 - index: 分页索引，首次请求传 1，翻页时从上一次响应的 `$.data.data.cursor` 中提取 `index` 字段的值
 ### 返回:
 - 子评论数据对象，包含子评论列表、分页游标等
 ### 翻页说明:
 - 响应中的 `$.data.data.cursor` 是一个 JSON 对象，示例:
`{"cursor":"69a0c134000000000c00910d","index":3}`
 - 首次请求：cursor留空，index传1
 - 翻页请求：从 `$.data.data.cursor` 中提取 `cursor` 和 `index` 分别传入对应参数

## get_product_detail

`GET /api/v1/xiaohongshu/app/get_product_detail`

<!-- Full path: /api/v1/xiaohongshu/app/get_product_detail -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| sku_id | string | ✅ | 商品skuId/Product SKU ID | 68be7cbc8c331700011f89d1 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取小红书商品详情信息
### 参数:
- sku_id: 商品skuId（必需）
### 返回:
- 商品详情数据

## get_product_detail

`GET /api/v1/xiaohongshu/app/get_product_detail`

<!-- Full path: /api/v1/xiaohongshu/app_v2/get_product_detail -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| sku_id | string | ✅ | 商品SKU ID/Product SKU ID | 669ddd44e05f3700011067ed |
| source | string |  | 来源/Source (default: mall_search) | mall_search |
| pre_page | string |  | 前置页面/Previous page (default: mall_search) | mall_search |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 通过 SKU ID 获取商品的详细信息，包括价格、规格、库存、商品描述等
 ### 参数:
 - sku_id: 商品 SKU ID（必需），如 "669ddd44e05f3700011067ed"
 - source: 来源，默认 "mall_search"
 - pre_page: 前置页面，默认 "mall_search"
 ### 返回:
 - 商品详情数据，包含价格、规格、库存、商品描述等

## get_product_info

`GET /api/v1/xiaohongshu/web/get_product_info`

<!-- Full path: /api/v1/xiaohongshu/web/get_product_info -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| share_text | string |  | 分享链接/Share link (default: '') |  |
| item_id | string |  | 商品ID/Item ID (default: '') | 65fc2e6d6b92310001d24efb |
| xsec_token | string |  | X-Sec-Token (default: '') | XBC6LTqeaEDeJETMoXo436Eg-74GxFemVnNHeONYobv7k= |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 通过分享链接获取小红书的商品信息
 ### 参数:
 - share_text: 小红书分享链接（支持APP和Web端分享链接）
 - item_id: 商品ID
 - xsec_token: X-Sec-Token
 - 如果share_text不为空，则item_id和xsec_token会被忽略
 - 如果share_text为空，则item_id和xsec_token不能为空
 ### 返回:
 - 商品信息

## get_product_review_overview

`GET /api/v1/xiaohongshu/app_v2/get_product_review_overview`

<!-- Full path: /api/v1/xiaohongshu/app_v2/get_product_review_overview -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| sku_id | string | ✅ | 商品SKU ID/Product SKU ID | 669ddd44e05f3700011067ed |
| tab | integer |  | 标签类型/Tab type (default: 2) | 2 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取商品的评论统计信息，包括评分分布、好评率、评论标签等
 ### 参数:
 - sku_id: 商品 SKU ID（必需），如 "669ddd44e05f3700011067ed"
 - tab: 标签类型，默认 2
 ### 返回:
 - 商品评论总览数据，包含评分分布、好评率、评论标签等

## get_product_reviews

`GET /api/v1/xiaohongshu/app_v2/get_product_reviews`

<!-- Full path: /api/v1/xiaohongshu/app_v2/get_product_reviews -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| sku_id | string | ✅ | 商品SKU ID/Product SKU ID | 669ddd44e05f3700011067ed |
| page | integer |  | 页码，从0开始/Page number, start from 0 (default: 0) | 0 |
| sort_strategy_type | integer |  | '排序策略：0=综合排序, 1=最新排序/Sort strategy: 0=general, 1=latest' (default: 0) | 0 |
| share_pics_only | integer |  | '仅看有图评论：0=否, 1=是/Show reviews with images only: 0=no, 1=yes' (default: 0) | 0 |
| from_page | string |  | 来源页面/From page (default: score_page) | score_page |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取商品的用户评论列表，支持分页、排序和筛选有图评论
 ### 参数:
 - sku_id: 商品 SKU ID（必需），如 "669ddd44e05f3700011067ed"
 - page: 页码，从 0 开始
 - sort_strategy_type: 排序策略
    - 0: 综合排序（默认）
    - 1: 最新排序
- share_pics_only: 仅看有图评论，0=否, 1=是
 - from_page: 来源页面，默认 "score_page"
 ### 返回:
 - 商品评论列表数据
 ### 翻页说明:
 - page 从 0 开始递增

## get_sub_comments

`GET /api/v1/xiaohongshu/app/get_sub_comments`

<!-- Full path: /api/v1/xiaohongshu/app/get_sub_comments -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| note_id | string | ✅ | 笔记ID/Note ID | 677d1909000000002002a892 |
| comment_id | string | ✅ | 一级评论ID/Parent comment ID | 677f67e400000000220013f3 |
| start | string |  | 翻页游标/Pagination cursor | 6806642d000000001f01991b |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取评论的子评论（回复）列表
 ### 参数:
 - note_id: 笔记ID（必需）
 - comment_id: 一级评论ID，要查看哪条评论的子评论（必需）
 - start: 翻页游标，从上一次请求的响应中获取，从评论列表的最后一条子评论ID获取：
    格式如下: "6806642d000000001f01991b"
### 返回:
 - 子评论列表数组，每个子评论包含：
    - id: 子评论ID
    - content: 评论内容
    - create_time: 创建时间戳
    - user_info: 评论者信息
        - user_id: 用户ID
        - nickname: 昵称
        - image: 头像URL
    - target_comment: 被回复的评论信息（如果是回复其他子评论）
        - id: 被回复评论ID
        - user_info: 被回复者信息
            - nickname: 被回复者昵称
 ### 翻页说明:
 - 首次请求不传start参数
 - 获取更多时，将上一次请求返回的最后一条子评论ID作为start参数

## get_topic_feed

`GET /api/v1/xiaohongshu/app_v2/get_topic_feed`

<!-- Full path: /api/v1/xiaohongshu/app_v2/get_topic_feed -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| page_id | string | ✅ | 话题页面ID/Topic page ID | 5c1cc866febed9000184b7c1 |
| sort | string |  | '排序方式/Sort: trend(最热), time(最新)' (default: trend) | trend |
| cursor_score | string |  | 分页游标分数，翻页时传入/Pagination cursor score for next page (default: '') |  |
| last_note_id | string |  | 上一页最后一条笔记ID，翻页时传入/Last note ID from previous page (default: '') |  |
| last_note_ct | string |  | 上一页最后一条笔记创建时间，翻页时传入/Last note create time from previous page (default: '') |  |
| session_id | string |  | 会话ID，翻页时保持一致/Session ID, keep consistent for pagination (default: '') |  |
| first_load_time | string |  | 首次加载时间戳，翻页时保持一致/First load timestamp, keep consistent for pagination (default: '') |  |
| source | string |  | 来源/Source (default: normal) | normal |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定话题下的笔记列表，支持按最热或最新排序，使用游标分页
 ### 参数:
 - page_id: 话题页面ID（必需），如 "5c1cc866febed9000184b7c1"
 - sort: 排序方式
    - "trend": 最热（默认）
    - "time": 最新
- cursor_score: 分页游标分数，翻页时传入上一页最后一个 item 的 cursor_score
 - last_note_id: 上一页最后一条笔记ID，翻页时传入
 - last_note_ct: 上一页最后一条笔记创建时间，翻页时传入
 - session_id: 会话ID，翻页时保持一致
 - first_load_time: 首次加载时间戳，翻页时保持一致
 - source: 来源，默认 "normal"
 ### 返回:
 - 话题笔记列表数据
 ### 翻页说明:
 - 首次请求：只传 page_id 和 sort，其余留空
 - 翻页请求：取上一次响应最后一个 item 的字段:
    - cursor_score ← items[-1].cursor_score
    - last_note_id ← items[-1].id
    - last_note_ct ← items[-1].create_time
- 建议同时回传 session_id 和 first_load_time 保持会话一致

## get_topic_info

`GET /api/v1/xiaohongshu/app_v2/get_topic_info`

<!-- Full path: /api/v1/xiaohongshu/app_v2/get_topic_info -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| page_id | string | ✅ | 话题页面ID/Topic page ID | 5c1cc866febed9000184b7c1 |
| source | string |  | 来源/Source (default: normal) | normal |
| note_id | string |  | >- (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定话题的详细信息，包括话题名称、浏览量、讨论数、分享信息等
 ### 参数:
 - page_id: 话题页面ID（必需），如 "5c1cc866febed9000184b7c1"
 - source: 来源，默认 "normal"
 - note_id: 来源笔记ID，从笔记跳转到话题时传入（可选）
 ### 返回:
 - 话题详情数据，包含 page_info（名称/浏览量/讨论数）、tabs、share_info 等

## get_topic_notes

`GET /api/v1/xiaohongshu/app/get_topic_notes`

<!-- Full path: /api/v1/xiaohongshu/app/get_topic_notes -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| page_id | string | ✅ | 话题标签ID/Topic tag ID | 5c014b045b29cb0001ead530 |
| first_load_time | string | ✅ | 首次请求时间戳（毫秒）/First load timestamp (ms) | 1744978179304 |
| sort | string |  | '排序方式：hot-综合，time-最新，trend-最热/Sort: hot, time, trend' (default: hot) | hot |
| last_note_ct | string |  | 最后一条笔记create_time（翻页用）/Last note create_time (pagination) |  |
| last_note_id | string |  | 最后一条笔记ID（翻页用）/Last note ID (pagination) |  |
| cursor_score | string |  | 游标分数（翻页用）/Cursor score (pagination) |  |
| session_id | string |  | 会话ID，由服务端生成（翻页用）/Session ID, server-generated (pagination) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 根据话题标签获取相关笔记，对应新版App话题标签页面
 - 支持综合、最新、最热三种排序
 - 替代已弃用的 `get_notes_by_topic` 接口
 ### 参数:
 - page_id: 话题标签ID（必需）
 - first_load_time: 首次请求时间戳（毫秒级，必需）
    - 例: 1744978179304
    - Python获取当前时间戳: `int(time.time() * 1000)`
- sort: 排序方式
    - "hot": 综合排序（默认）
    - "time": 最新发布
    - "trend": 最热门
- last_note_ct: 上一页最后一条笔记的create_time，首次不传，翻页传
 - last_note_id: 上一页最后一条笔记的ID，首次不传，翻页传
 - cursor_score: 上一页最后一条笔记的cursor_score，首次不传，翻页传
 - session_id: 会话ID，首次不传由服务端生成，翻页传上一次返回的值
 ### 返回:
 - 话题笔记数据，包含：
    - notes: 笔记列表数组
    - session_id: 会话ID（翻页必需）
    - has_more: 是否有更多数据
 ### 翻页说明:
 - 首次请求：只传 page_id 和 first_load_time
 - 翻页请求：传入上一次返回的 session_id，以及最后一条笔记的
last_note_ct、last_note_id、cursor_score

## get_user_faved_notes

`GET /api/v1/xiaohongshu/app_v2/get_user_faved_notes`

<!-- Full path: /api/v1/xiaohongshu/app_v2/get_user_faved_notes -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string |  | 用户ID/User ID (default: '') | 5a8cf39111be10466d285d6b |
| share_text | string |  | 分享链接/Share link (default: '') | https://xhslink.com/a/EZ4M9TwMA6c3 |
| cursor | string |  | >- (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定用户公开收藏的笔记列表，使用游标分页
 ### 参数:
 - user_id: 用户ID，如 "5a8cf39111be10466d285d6b"
 - share_text: 小红书分享链接（支持APP和Web端分享链接）
 - 优先使用`user_id`，如果没有则使用`share_text`，两个参数二选一，如都携带则以`user_id`为准。
 - cursor: 分页游标，首次请求留空，翻页时传入上一页列表中最后一条笔记的 note_id
 ### 返回:
 - 用户收藏笔记列表数据，包含笔记基本信息和分页信息
 ### 翻页说明:
 - 首次请求：cursor留空
 - 翻页请求：传入上一页列表中最后一条笔记的 note_id

## get_user_info

`GET /api/v1/xiaohongshu/app/get_user_info`

<!-- Full path: /api/v1/xiaohongshu/app/get_user_info -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string | ✅ | 用户ID/User ID | 5c2f338a000000000701e1c6 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取用户详情信息
### 参数:
- user_id: 用户ID（必需）
### 返回:
- 用户详情数据，包含：
    - user_id: 用户ID
    - nickname: 昵称
    - desc: 个人简介
    - gender: 性别（0=女，1=男，2=未知）
    - images: 头像URL
    - imageb: 背景图URL
    - red_official_verify_type: 官方认证类型（0=无，1=个人，2=机构）
    - red_official_verify_show: 是否显示认证标识
    - level: 等级信息
        - image: 等级图标URL
        - name: 等级名称
    - follows: 关注数
    - fans: 粉丝数
    - interaction: 获赞与收藏总数
    - notes: 笔记数
    - boards: 专辑数
    - location: 所在地
    - collected: 收藏数
    - liked: 点赞数

## get_user_info

`GET /api/v1/xiaohongshu/app/get_user_info`

<!-- Full path: /api/v1/xiaohongshu/app_v2/get_user_info -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string |  | 用户ID/User ID (default: '') | 61b46d790000000010008153 |
| share_text | string |  | 分享链接/Share link (default: '') | https://xhslink.com/m/3ZSCJZAMz0a |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定用户的详细信息
 ### 参数:
 - user_id: 用户ID，如 "61b46d790000000010008153"
 - share_text: 小红书分享链接（支持APP和Web端分享链接）
 - 优先使用`user_id`，如果没有则使用`share_text`，两个参数二选一，如都携带则以`user_id`为准。
 ### 返回:
 - 用户详细信息，包含昵称、头像、简介、粉丝数、关注数、笔记数等

## get_user_info

`GET /api/v1/xiaohongshu/app/get_user_info`

<!-- Full path: /api/v1/xiaohongshu/web/get_user_info -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string | ✅ | 用户ID/User ID | 5f4a10070000000001006fc7 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取用户信息 V1
 ### 参数:
 - user_id: 用户ID，可以从小红书的分享链接中获取
 ### 返回:
 - 用户信息

## get_user_info_v2

`GET /api/v1/xiaohongshu/web/get_user_info_v2`

<!-- Full path: /api/v1/xiaohongshu/web/get_user_info_v2 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string |  | 用户ID/User ID (default: '') | 5f4a10070000000001006fc7 |
| share_text | string |  | 分享文本或链接/Share text or link (default: '') | >- |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取用户信息 V2
 ### 参数:
 - user_id: 用户ID，可以从小红书的分享链接中获取
 - share_text: 小红书分享文本或链接（支持APP和Web端分享链接）
 - 优先使用`user_id`，如果没有则使用`share_text`，两个参数二选一，如都携带则以`user_id`为准。
 ### 返回:
 - 用户信息

## get_user_notes

`GET /api/v1/xiaohongshu/app/get_user_notes`

<!-- Full path: /api/v1/xiaohongshu/app/get_user_notes -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string | ✅ | 用户ID/User ID | 5c57e6a4000000001802a013 |
| cursor | string |  | 翻页游标/Pagination cursor | 67ee399f000000001c02f36f |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取用户发布的笔记列表
### 参数:
- user_id: 用户ID（必需）
- cursor: 翻页索引，上一次请求返回的cursor字段，不传默认请求第一页
- cursor取值方式为notes列表的最后一条笔记的note_id
### 返回:
- 用户笔记列表数据，包含：
    - notes: 笔记数组，每个笔记包含：
        - note_id: 笔记ID
        - type: 类型（normal=图文，video=视频）
        - display_title: 标题
        - desc: 描述
        - liked_count: 点赞数
        - cover: 封面图信息
            - url: 图片URL
            - width: 宽度
            - height: 高度
        - user: 作者信息（通常与查询用户相同）
    - cursor: 翻页游标
    - has_more: 是否有更多数据
 ### 翻页说明:
- 首次请求：只传user_id
- 翻页请求：传入上一次返回的cursor
- 当has_more为false时，表示没有更多笔记

## get_user_notes_v2

`GET /api/v1/xiaohongshu/web/get_user_notes_v2`

<!-- Full path: /api/v1/xiaohongshu/web/get_user_notes_v2 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string | ✅ | 用户ID/User ID | 5f4a10070000000001006fc7 |
| lastCursor | string |  | 上一页的游标/Last cursor |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取用户的笔记
 ### 参数:
 - user_id: 用户ID，可以从小红书的分享链接中获取
 - lastCursor: 第一次请求时为空，之后请求时使用上一次请求响应中返回的最后一个NoteID
    - 例如: "662908190000000001007366"
    - JSON Path: $.data.data.notes.[-1].id
### 返回:
 - 用户的笔记列表

## get_user_posted_notes

`GET /api/v1/xiaohongshu/app_v2/get_user_posted_notes`

<!-- Full path: /api/v1/xiaohongshu/app_v2/get_user_posted_notes -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string |  | 用户ID/User ID (default: '') | 61b46d790000000010008153 |
| share_text | string |  | 分享链接/Share link (default: '') | http://xhslink.com/o/8GqargIxrko |
| cursor | string |  | 分页游标，首次请求留空/Pagination cursor, leave empty for first request (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定用户已发布的笔记列表，使用游标分页
 ### 参数:
 - user_id: 用户ID，如 "61b46d790000000010008153"
 - share_text: 小红书分享链接（支持APP和Web端分享链接）
 - 优先使用`user_id`，如果没有则使用`share_text`，两个参数二选一，如都携带则以`user_id`为准。
 - cursor: 分页游标，首次请求留空，翻页时传入上一次响应中返回的 cursor 值
    - 通常cursor取值方式为notes列表的最后一条笔记的 note_id
    - JSON路径示例: `$.data.data.notes[-1].cursor`
### 返回:
 - 用户笔记列表数据，包含笔记基本信息和分页信息
 ### 翻页说明:
 - 首次请求：cursor留空
 - 翻页请求：传入上一次响应中返回的 cursor 值

## get_video_note_detail

`GET /api/v1/xiaohongshu/app_v2/get_video_note_detail`

<!-- Full path: /api/v1/xiaohongshu/app_v2/get_video_note_detail -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| note_id | string |  | 笔记ID/Note ID (default: '') | 697c0eee000000000a03c308 |
| share_text | string |  | 分享链接/Share link (default: '') | http://xhslink.com/o/8GqargIxrko |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取视频笔记的完整详情数据
 ### 参数:
 - note_id: 笔记ID，如 "697c0eee000000000a03c308"
 - share_text: 小红书分享链接（支持APP和Web端分享链接）
 - 优先使用`note_id`，如果没有则使用`share_text`，两个参数二选一，如都携带则以`note_id`为准。
 ### 返回:
 - 视频笔记详情数据，包含视频播放地址、封面图、作者信息、互动数据等

## get_visitor_cookie

`GET /api/v1/xiaohongshu/web/get_visitor_cookie`

<!-- Full path: /api/v1/xiaohongshu/web/get_visitor_cookie -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| proxy | string |  | 代理/Proxy (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取小红书网页版的游客Cookie，可以用于爬取小红书的一些数据。
 ### 参数:
 - proxy: 代理，例如: http://username:password@host:port
 - 代理格式支持HTTP和SOCKS5，若不需要代理则留空
 ### 返回:
 - 游客Cookie

## search_notes

`GET /api/v1/xiaohongshu/app/search_notes`

<!-- Full path: /api/v1/xiaohongshu/app/search_notes -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 搜索关键词/Search keyword | 猫粮 |
| page | integer | ✅ | 页码（从1开始）/Page number (start from 1) | 1 |
| search_id | string |  | 搜索ID，翻页时使用/Search ID for pagination | 2egvdsiowvfm9thbt260w |
| session_id | string |  | 会话ID，翻页时使用/Session ID for pagination | 2egvdt4sl2b7rnfg8zk00 |
| sort_type | string |  | 排序方式/Sort type (default: general) | general |
| filter_note_type | string |  | 笔记类型筛选：不限、视频笔记、普通笔记/Note type filter (default: 不限) | 不限 |
| filter_note_time | string |  | 发布时间筛选：不限、一天内、一周内、半年内/Time filter (default: 不限) | 不限 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 搜索小红书笔记
 ### 参数:
 - keyword: 要搜索的关键词（必需）
 - page: 第几页，从1开始（必需）
 - search_id: 搜索ID，第一次请求可不传，服务端会生成searchId，翻页时需要携带服务端返回的searchId
 - session_id: 会话ID，第一次请求可不传，服务端会生成sessionId，翻页时携带服务端返回的sessionId
 - sort_type: 排序规则
    - "general": 综合排序（默认）
    - "time_descending": 最新发布
    - "popularity_descending": 最多点赞
    - "comment_descending": 最多评论
    - "collect_descending": 最多收藏
- filter_note_type: 筛选笔记类型
    - "不限": 所有类型（默认）
    - "视频笔记": 仅视频
    - "普通笔记": 仅图文
- filter_note_time: 筛选笔记发布时间
    - "不限": 所有时间（默认）
    - "一天内": 24小时内
    - "一周内": 7天内
    - "半年内": 6个月内
### 返回:
 - 搜索结果数据，包含：
    - items: 搜索结果列表，每个元素包含：
        - id: 元素ID
        - model_type: 模型类型（通常为"note"）
        - note: 笔记详情
            - note_id: 笔记ID
            - type: 类型（normal=图文，video=视频）
            - display_title: 标题（关键词会高亮）
            - desc: 内容描述（搜索接口无法返回完整的 desc，仅部分内容，请使用笔记详情接口获取完整内容）
            - user: 作者信息
            - interact_info: 互动数据
                - liked_count: 点赞数
            - cover: 封面图信息
    - searchId: 搜索ID（翻页必需，不同关键词不要复用）
    - sessionId: 会话ID（翻页必需）
    - has_more: 是否有更多数据
    - total_count: 搜索结果总数
 ### 翻页说明:
 - 首次搜索：只传keyword和page=1
 - 翻页搜索：传入相同keyword，递增page，并携带首次返回的searchId和sessionId
 - 注意：更换关键词时不要复用之前的searchId

## search_notes

`GET /api/v1/xiaohongshu/app/search_notes`

<!-- Full path: /api/v1/xiaohongshu/app_v2/search_notes -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 搜索关键词/Search keyword | 美食推荐 |
| page | integer |  | 页码，从1开始/Page number, start from 1 (default: 1) | 1 |
| sort_type | string |  | 排序方式/Sort type (default: general) | general |
| note_type | string |  | '笔记类型/Note type: 不限, 视频笔记, 普通笔记, 直播笔记' (default: 不限) | 不限 |
| time_filter | string |  | '发布时间筛选/Time filter: 不限, 一天内, 一周内, 半年内' (default: 不限) | 不限 |
| search_id | string |  | 搜索ID，翻页时传入首次搜索返回的值/Search ID for pagination (default: '') |  |
| search_session_id | string |  | 搜索会话ID，翻页时传入首次搜索返回的值/Search session ID for pagination (default: '') |  |
| source | string |  | 来源/Source (default: explore_feed) | explore_feed |
| ai_mode | integer |  | 'AI模式：0=关闭, 1=开启/AI mode: 0=off, 1=on' (default: 0) | 0 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 根据关键词搜索小红书笔记，支持多种排序方式、笔记类型筛选和发布时间筛选
 ### 参数:
 - keyword: 搜索关键词（必需），如 "美食推荐"
 - page: 页码，从 1 开始
 - sort_type: 排序方式
    - "general": 综合排序（默认）
    - "time_descending": 按时间倒序（最新）
    - "popularity_descending": 按点赞数排序（最多点赞）
    - "comment_descending": 按评论数排序（最多评论）
    - "collect_descending": 按收藏数排序（最多收藏）
    - "english_preferred": 英文优先
- note_type: 笔记类型筛选
    - "不限": 所有类型（默认）
    - "视频笔记": 仅视频
    - "普通笔记": 仅图文
    - "直播笔记": 仅直播
- time_filter: 发布时间筛选
    - "不限": 所有时间（默认）
    - "一天内": 24小时内
    - "一周内": 7天内
    - "半年内": 6个月内
- search_id: 搜索ID，翻页时传入首次搜索返回的值
 - search_session_id: 搜索会话ID，翻页时传入首次搜索返回的值
 - source: 来源，默认 "explore_feed"
 - ai_mode: AI模式，0=关闭, 1=开启
 ### 返回:
 - 搜索结果数据，包含笔记列表和分页信息
 ### 翻页说明:
 - 首次请求：只传keyword和page
 - 翻页请求：传入首次搜索返回的 search_id 和 search_session_id

## search_notes

`GET /api/v1/xiaohongshu/app/search_notes`

<!-- Full path: /api/v1/xiaohongshu/web/search_notes -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 搜索关键词/Keyword | 美食 |
| page | integer |  | 页码/Page (default: 1) | 1 |
| sort | string |  | 排序方式/Sort (default: general) | general |
| noteType | string |  | 笔记类型/Note type (default: _0) | _0 |
| noteTime | string |  | 发布时间/Release time (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 搜索笔记
### 参数:
- keyword: 搜索关键词
- page: 页码，默认为1
- sort: 排序方式
    - 综合排序（默认参数）: general
    - 最热排序: popularity_descending
    - 最新排序: time_descending
    - 最多评论: comment_descending
    - 最多收藏: collect_descending
- noteType: 笔记类型
    - 综合笔记（默认参数）: _0
    - 视频笔记: _1
    - 图文笔记: _2
    - 直播: _3
- noteTime: 发布时间
    - 不限: ""
    - 一天内 :一天内
    - 一周内 :一周内
    - 半年内 :半年内
### 返回:
- 笔记列表

## search_notes_v3

`GET /api/v1/xiaohongshu/web/search_notes_v3`

<!-- Full path: /api/v1/xiaohongshu/web/search_notes_v3 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 搜索关键词/Keyword | 美食 |
| page | integer |  | 页码/Page (default: 1) | 1 |
| sort | string |  | 排序方式/Sort (default: general) | general |
| noteType | string |  | 笔记类型/Note type (default: _0) | _0 |
| noteTime | string |  | 发布时间/Release time (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 搜索笔记 V3
### 参数:
- keyword: 搜索关键词
- page: 页码，默认为1
- sort: 排序方式
    - 综合排序（默认参数）: general
    - 最热排序: popularity_descending
    - 最新排序: time_descending
    - 最多评论: comment_descending
    - 最多收藏: collect_descending
- noteType: 笔记类型
    - 综合笔记（默认参数）: _0
    - 视频笔记: _1
    - 图文笔记: _2
    - 直播: _3
- noteTime: 发布时间
    - 不限: ""
    - 一天内 :一天内
    - 一周内 :一周内
    - 半年内 :半年内
### 返回:
- 笔记列表

## sign

`POST /api/v1/xiaohongshu/web/sign`

<!-- Full path: /api/v1/xiaohongshu/web/sign -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 小红书Web签名，用于获取小红书的一些数据。
- 生成 `X-s`, `X-t`, `X-s-common` 等签名参数。
### 参数:
- sign_request: 签名请求模型
    - path: 请求接口的路径，例如: `/api/sns/web/v1/homefeed`
    - data: 请求API的荷载数据
    - cookie: 请求接口的Cookie
### 返回:
- 签名参数(X-s, X-t, X-s-common等)

---

See SKILL.md for cross-group orchestration patterns.