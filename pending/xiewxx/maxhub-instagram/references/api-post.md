# Post Data API / 帖子数据接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---
## fetch_comment_replies

`GET /api/v1/instagram/v1/fetch_comment_replies`

<!-- Full path: /api/v1/instagram/v1/fetch_comment_replies -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| media_id | string | ✅ | 帖子ID（媒体ID）/Post ID (Media ID) | 3766120364183949816 |
| comment_id | string | ✅ | 父评论ID/Parent comment ID | 17871667485468098 |
| min_id | string |  | >- |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定评论下的子评论（二级评论/回复），支持分页
 ### 参数:
 - media_id: 帖子ID（媒体ID）
 - comment_id: 父评论ID（从fetch_post_comments_v2返回的评论pk字段获取）
 - min_id: 分页游标，首次请求不传，从上一次响应的`page_info.next_min_id`字段获取
 ### 返回:
 - `child_comments`: 子评论列表，每个评论包含：
  - `pk`: 评论ID
  - `text`: 评论内容
  - `created_at`/`created_at_utc`: 评论时间戳
  - `user`: 评论者信息（pk, username, full_name, is_verified, profile_pic_url等）
  - `comment_like_count`: 评论点赞数
  - `parent_comment_id`: 父评论ID
  - `has_translation`: 是否有翻译
- `child_comment_count`: 子评论总数
 - `has_more_tail_child_comments`: 是否有更多子评论
 - `next_min_child_cursor`: 下一页游标
 - `page_info`: 分页信息汇总

## fetch_comment_replies

`GET /api/v1/instagram/v1/fetch_comment_replies`

<!-- Full path: /api/v1/instagram/v2/fetch_comment_replies -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| code_or_url | string | ✅ | 帖子Shortcode或URL/Post shortcode or URL | DRhvwVLAHAG |
| comment_id | string | ✅ | 评论ID/Comment ID | 18067775592012345 |
| pagination_token | string |  | 分页token/Pagination token |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取评论的回复列表
- 需要先通过fetch_post_comments获取评论ID
- 支持分页获取
### 参数:
- code_or_url: 帖子Shortcode或完整URL
- comment_id: 评论ID
- pagination_token: 分页token，从上一次响应获取
### 返回:
- `data.items`: 回复列表
- `pagination_token`: 下一页token

## fetch_hashtag_posts

`GET /api/v1/instagram/v1/fetch_hashtag_posts`

<!-- Full path: /api/v1/instagram/v1/fetch_hashtag_posts -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| hashtag | string | ✅ | '话题标签名称（不含#号）/Hashtag name (without #)' | cat |
| end_cursor | string |  | 分页游标，用于获取下一页/Pagination cursor for next page |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取指定话题标签下的帖子列表
### 参数:
- hashtag: 话题标签名称（不含#号）
- end_cursor: 分页游标，首次请求不传
### 返回:
- GraphQL风格响应，包含`data.hashtag.edge_hashtag_to_media`

## fetch_hashtag_posts

`GET /api/v1/instagram/v1/fetch_hashtag_posts`

<!-- Full path: /api/v1/instagram/v2/fetch_hashtag_posts -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | '话题关键词（不含#号）/Hashtag keyword (without #)' | cat |
| feed_type | string |  | >- (default: top) |  |
| pagination_token | string |  | 分页token/Pagination token |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取指定话题标签下的帖子列表
- 支持按热门、最新或仅Reels筛选
- 支持分页获取
### 参数:
- keyword: 话题关键词（不含#号）
- feed_type: 帖子类型，"top"（热门）、"recent"（最新）或"reels"（仅Reels），默认top
- pagination_token: 分页token，从上一次响应获取
### 返回:
- `data.items`: 帖子列表
- `pagination_token`: 下一页token

## fetch_highlight_stories

`GET /api/v1/instagram/v2/fetch_highlight_stories`

<!-- Full path: /api/v1/instagram/v2/fetch_highlight_stories -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| highlight_id | string | ✅ | 精选ID/Highlight ID | 17895069621772257 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定精选（Highlight）中的所有故事
 - 需要先通过fetch_user_highlights获取精选ID
 ### 参数:
 - highlight_id: 精选ID（可带或不带"highlight:"前缀）
 ### 返回:
 - `data.items`: 故事列表，包含图片/视频URL、发布时间等

## fetch_location_posts

`GET /api/v1/instagram/v1/fetch_location_posts`

<!-- Full path: /api/v1/instagram/v1/fetch_location_posts -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| location_id | string | ✅ | 地点ID/Location ID | 703457703 |
| tab | string |  | '排序方式：ranked(热门)/recent(最新)/Sorting: ranked(top)/recent(latest)' (default: ranked) |  |
| end_cursor | string |  | 分页游标，用于获取下一页/Pagination cursor for next page |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取指定地点标记的帖子列表
### 参数:
- location_id: 地点ID
- tab: 排序方式，ranked(热门)/recent(最新)
- end_cursor: 分页游标，首次请求不传
### 返回:
- `edges`: 帖子列表
- `page_info`: 分页信息

## fetch_location_posts

`GET /api/v1/instagram/v1/fetch_location_posts`

<!-- Full path: /api/v1/instagram/v2/fetch_location_posts -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| location_id | string | ✅ | 地点ID/Location ID | 331004901 |
| pagination_token | string |  | 分页token/Pagination token |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取指定地点的帖子列表
- 地点ID可通过search_locations获取
- 支持分页获取
### 参数:
- location_id: 地点ID
- pagination_token: 分页token，从上一次响应获取
### 返回:
- `data.items`: 帖子列表
- `pagination_token`: 下一页token

## fetch_music_posts

`GET /api/v1/instagram/v1/fetch_music_posts`

<!-- Full path: /api/v1/instagram/v1/fetch_music_posts -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| music_id | string |  | 音乐ID/Music ID | 564058920086577 |
| music_url | string |  | 音乐URL（与music_id二选一）/Music URL (alternative to music_id) | https://www.instagram.com/reels/audio/564058920086577 |
| max_id | string |  | 分页游标，用于获取下一页/Pagination cursor for next page |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取使用指定音乐/音频的Reels和帖子列表
 ### 参数:
 - music_id: 音乐ID（与music_url二选一）
 - music_url: 音乐URL，会自动提取ID（与music_id二选一）
 - max_id: 分页游标，首次请求不传
 ### 返回:
 - `items`: 帖子列表
 - `metadata`: 音乐元数据
 - `paging_info`: 分页信息

## fetch_music_posts

`GET /api/v1/instagram/v1/fetch_music_posts`

<!-- Full path: /api/v1/instagram/v2/fetch_music_posts -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| audio_canonical_id | string | ✅ | 音频ID/Audio ID | 564058920086577 |
| pagination_token | string |  | 分页token/Pagination token |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取使用指定音乐的帖子列表
- 音频ID可从帖子详情中获取
- 支持分页获取
### 参数:
- audio_canonical_id: 音频ID
- pagination_token: 分页token，从上一次响应获取
### 返回:
- `data.items`: 帖子列表
- `pagination_token`: 下一页token

## fetch_post_by_id

`GET /api/v1/instagram/v1/fetch_post_by_id`

<!-- Full path: /api/v1/instagram/v1/fetch_post_by_id -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| post_id | string | ✅ | 帖子ID/Post ID | 3742637871112032100 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 通过ID获取单个帖子的详细信息
### 参数:
- post_id: 帖子ID
### 返回:
- 帖子详情对象，包含媒体、点赞数、评论等

## fetch_post_by_url

`GET /api/v1/instagram/v1/fetch_post_by_url`

<!-- Full path: /api/v1/instagram/v1/fetch_post_by_url -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| post_url | string | ✅ | 帖子URL/Post URL | https://www.instagram.com/p/DPwhVB-jo9k/ |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 通过URL获取单个帖子的详细信息
### 参数:
- post_url: 帖子URL
### 返回:
- 帖子详情对象，包含媒体、点赞数、评论等

## fetch_post_by_url_v2

`GET /api/v1/instagram/v1/fetch_post_by_url_v2`

<!-- Full path: /api/v1/instagram/v1/fetch_post_by_url_v2 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| post_url | string | ✅ | 帖子URL/Post URL | https://www.instagram.com/p/DPwhVB-jo9k/ |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 通过URL获取单个帖子的详细信息 V2 - 数据没有V1完整，但速度更快，用于下载大量帖子时推荐使用。
 ### 参数:
 - post_url: 帖子URL
 ### 返回:
 - 帖子详情对象，包含媒体、点赞数、评论等

## fetch_post_comments

`GET /api/v1/instagram/v2/fetch_post_comments`

<!-- Full path: /api/v1/instagram/v2/fetch_post_comments -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| code_or_url | string | ✅ | 帖子Shortcode或URL/Post shortcode or URL | DRhvwVLAHAG |
| sort_by | string |  | '排序方式: recent(最新) 或 popular(热门)/Sort by: recent or popular' (default: recent) | recent |
| pagination_token | string |  | 分页token/Pagination token (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取帖子的评论列表
- 支持按最新或热门排序
- 支持分页获取
### 参数:
- code_or_url: 帖子Shortcode或完整URL
- sort_by: 排序方式，"recent"（最新）或"popular"（热门），默认recent
- pagination_token: 分页token，从上一次响应获取
### 返回:
- `data.items`: 评论列表
- `pagination_token`: 下一页token

## fetch_post_comments_v2

`GET /api/v1/instagram/v1/fetch_post_comments_v2`

<!-- Full path: /api/v1/instagram/v1/fetch_post_comments_v2 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| media_id | string | ✅ | 帖子ID（媒体ID）/Post ID (Media ID) | 3766120364183949816 |
| sort_order | string |  | '排序方式：popular(热门)/recent(最新)/Sorting: popular/recent' (default: recent) | recent |
| min_id | string |  | >- |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取帖子评论列表，支持分页
 - 返回的评论数据更完整，包含子评论预览和更多元数据
 ### 参数:
 - media_id: 帖子ID（媒体ID）
 - sort_order: 排序方式，popular(热门)/recent(最新)
 - min_id: 分页游标，首次请求不传，从上一次响应的`next_min_id`字段获取
 ### 返回:
 - `comment_count`: 评论总数
 - `comments`: 评论列表，每个评论包含：
  - `pk`: 评论ID
  - `text`: 评论内容
  - `created_at`/`created_at_utc`: 评论时间戳
  - `user`: 评论者信息（pk, username, full_name, is_verified, profile_pic_url等）
  - `comment_like_count`: 评论点赞数
  - `child_comment_count`: 子评论数量
  - `preview_child_comments`: 子评论预览列表
  - `is_liked_by_media_owner`: 是否被帖子作者点赞
  - `has_translation`: 是否有翻译
- `next_min_id`: 下一页游标（JSON格式字符串）
 - `has_more_headload_comments`: 是否有更多评论
 - `caption`: 帖子描述信息

## fetch_post_info

`GET /api/v1/instagram/v2/fetch_post_info`

<!-- Full path: /api/v1/instagram/v2/fetch_post_info -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| code_or_url | string | ✅ | 帖子Shortcode或URL/Post shortcode or URL | DRhvwVLAHAG |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取Instagram帖子的详细信息
- 支持Shortcode或完整URL
### 参数:
- code_or_url: 帖子Shortcode或完整URL
### 返回:
- `data`: 帖子详情，包含媒体资源、描述、点赞数、评论数等

## fetch_post_likes

`GET /api/v1/instagram/v2/fetch_post_likes`

<!-- Full path: /api/v1/instagram/v2/fetch_post_likes -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| code_or_url | string | ✅ | 帖子Shortcode或URL/Post shortcode or URL | DRhvwVLAHAG |
| end_cursor | string |  | 分页游标/Pagination cursor |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取帖子的点赞用户列表
- 支持分页获取
### 参数:
- code_or_url: 帖子Shortcode或完整URL
- end_cursor: 分页游标，从上一次响应获取
### 返回:
- `data.items`: 点赞用户列表
- `end_cursor`: 下一页游标

## fetch_section_posts

`GET /api/v1/instagram/v1/fetch_section_posts`

<!-- Full path: /api/v1/instagram/v1/fetch_section_posts -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| section_id | string | ✅ | >- | 10156104410190727 |
| count | integer |  | 每页数量/Count per page (default: 20) |  |
| max_id | string |  | 分页游标，用于获取下一页/Pagination cursor for next page |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取探索页面某个分类下的帖子列表
### 参数:
- section_id: 分类ID（可从fetch_explore_sections接口获取）
- count: 每页数量，默认20
- max_id: 分页游标，首次请求不传
### 返回:
- `section_name`: 分类名称
- `items`: 帖子列表
- `subsections`: 子分类列表
- `max_id`: 下一页游标
- `more_available`: 是否有更多数据

## fetch_user_posts

`GET /api/v1/instagram/v1/fetch_user_posts`

<!-- Full path: /api/v1/instagram/v1/fetch_user_posts -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string | ✅ | Instagram用户ID/Instagram user ID | 25025320 |
| count | integer |  | 每页数量/Count per page (default: 12) |  |
| max_id | string |  | 分页游标，用于获取下一页/Pagination cursor for next page |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取用户帖子列表，支持分页
### 参数:
- user_id: Instagram用户ID
- count: 每页数量，默认12
- max_id: 分页游标，首次请求不传
### 返回:
- `items`: 帖子列表
- `more_available`: 是否有更多数据
- `next_max_id`: 下一页游标

## fetch_user_posts

`GET /api/v1/instagram/v1/fetch_user_posts`

<!-- Full path: /api/v1/instagram/v2/fetch_user_posts -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| username | string |  | 用户名/Username | instagram |
| user_id | string |  | 用户ID/User ID | 18527 |
| pagination_token | string |  | 分页token/Pagination token |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取Instagram用户发布的帖子列表
- 支持分页获取
### 参数:
- username: 用户名（与user_id二选一）
- user_id: 用户ID（与username二选一）
- pagination_token: 分页token，从上一次响应获取
### 返回:
- `data.items`: 帖子列表
- `pagination_token`: 下一页token

## fetch_user_posts_v2

`GET /api/v1/instagram/v1/fetch_user_posts_v2`

<!-- Full path: /api/v1/instagram/v1/fetch_user_posts_v2 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string | ✅ | Instagram用户ID/Instagram user ID | 25025320 |
| count | integer |  | 每页数量/Count per page (default: 12) |  |
| end_cursor | string |  | 分页游标，用于获取下一页/Pagination cursor for next page |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取用户帖子列表，支持分页
### 参数:
- user_id: Instagram用户ID
- count: 每页数量，默认12
- end_cursor: 分页游标，首次请求不传
### 返回:
- GraphQL风格响应，包含`data.user.edge_owner_to_timeline_media`

## fetch_user_reposts

`GET /api/v1/instagram/v1/fetch_user_reposts`

<!-- Full path: /api/v1/instagram/v1/fetch_user_reposts -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string | ✅ | Instagram用户ID/Instagram user ID | 25025320 |
| max_id | string |  | 分页游标，用于获取下一页/Pagination cursor for next page |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取用户转发/分享的帖子列表，支持分页
### 参数:
- user_id: Instagram用户ID
- max_id: 分页游标，首次请求不传
### 返回:
- `items`: 转发帖子列表
- `more_available`: 是否有更多数据
- `next_max_id`: 下一页游标

## fetch_user_tagged_posts

`GET /api/v1/instagram/v1/fetch_user_tagged_posts`

<!-- Full path: /api/v1/instagram/v1/fetch_user_tagged_posts -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string | ✅ | Instagram用户ID/Instagram user ID | 25025320 |
| count | integer |  | 每页数量/Count per page (default: 12) |  |
| end_cursor | string |  | 分页游标，用于获取下一页/Pagination cursor for next page |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取其他用户帖子中标记了该用户的帖子列表
### 参数:
- user_id: Instagram用户ID
- count: 每页数量，默认12
- end_cursor: 分页游标，首次请求不传
### 返回:
- GraphQL风格响应，包含`data.user.edge_user_to_photos_of_you`

## fetch_user_tagged_posts

`GET /api/v1/instagram/v1/fetch_user_tagged_posts`

<!-- Full path: /api/v1/instagram/v2/fetch_user_tagged_posts -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| username | string |  | 用户名/Username | instagram |
| user_id | string |  | 用户ID/User ID | 18527 |
| pagination_token | string |  | 分页token/Pagination token |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取其他用户标记了该用户的帖子列表
- 支持分页获取
### 参数:
- username: 用户名（与user_id二选一）
- user_id: 用户ID（与username二选一）
- pagination_token: 分页token，从上一次响应获取
### 返回:
- `data.items`: 帖子列表
- `pagination_token`: 下一页token

## get_comment_replies

`GET /api/v1/instagram/v3/get_comment_replies`

<!-- Full path: /api/v1/instagram/v3/get_comment_replies -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| media_id | string | ✅ | 帖子媒体ID/Post media ID | 3829530490739515971 |
| comment_id | string | ✅ | 父评论ID/Parent comment ID | 18065937092249736 |
| min_id | string |  | >- |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取Instagram评论的子评论（回复）列表
 - 支持分页获取所有回复
 - 父评论的 comment_id 可从 get_post_comments 接口的评论列表中获取
 ### 参数:
 - media_id: 帖子的媒体ID（数字ID，必填），可通过 `/shortcode_to_media_id` 接口从短码转换获得
 - comment_id: 父评论ID（必填，从 get_post_comments 返回的评论中获取 `pk` 字段）
 - min_id: 分页游标，首次请求不传，从上一次响应的 `data.next_min_child_cursor` 获取
 ### 返回:
 - `data.child_comments`: 子评论列表
    - `user`: 评论者信息
    - `text`: 评论文本
    - `created_at`: 评论时间戳
    - `comment_like_count`: 评论点赞数
    - `pk`: 评论ID
- `data.next_min_child_cursor`: 下一页分页游标（传给下次请求的min_id参数）
 - `data.has_more_tail_child_comments`: 是否有更多子评论
 - `data.num_tail_child_comments`: 剩余子评论数
 ### 分页使用方法:
 1. 首次请求：传 `media_id` 和 `comment_id` 参数
 2. 获取响应中的 `data.next_min_child_cursor`
 3. 下次请求：将 `next_min_child_cursor` 原样传入 `min_id` 参数（无需预处理，接口会自动反转义）
 4. 重复步骤 2-3 直到 `data.has_more_tail_child_comments` 为 false
  ### 注意:
 - `min_id` 可能是转义 JSON 字符串（如 `{"key":"val"}`），直接原样传入即可，接口内部会自动反转义处理

## get_highlight_stories

`GET /api/v1/instagram/v3/get_highlight_stories`

<!-- Full path: /api/v1/instagram/v3/get_highlight_stories -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| highlight_id | string | ✅ | '精选ID/Highlight ID (格式/format: highlight:xxx)' | highlight:18064916456320419 |
| reel_ids | string |  | >- |  |
| first | integer |  | 每页数量/Items per page (default: 3) |  |
| last | integer |  | 获取最后N条/Get last N items (default: 2) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取Instagram Highlight精选的详细故事/帖子内容
 - 返回精选集合中的所有Stories媒体
 ### 参数:
 - highlight_id: 精选ID，格式为 `highlight:xxx`（从 get_user_highlights 接口获取）
 - reel_ids: 精选ID列表，逗号分隔（可选，如不提供则仅查询highlight_id指定的精选）
    - 例如: `highlight:18064916456320419,highlight:18155682898389765`
    - 可同时查询多个精选的内容
- first: 每页数量（默认3）
 - last: 获取最后N条（默认2）
 ### 返回:
 - `data.story_highlight_tray`: 精选故事集合
    - `id`: 精选ID
    - `title`: 精选标题
    - `items`: 故事列表
        - `id`: 故事ID
        - `pk`: 故事PK
        - `taken_at`: 发布时间戳
        - `media_type`: 媒体类型（1=图片, 2=视频）
        - `image_versions2`: 图片版本列表
        - `video_versions`: 视频版本列表（视频时存在）
        - `user`: 发布者信息

## get_post_comments

`GET /api/v1/instagram/v3/get_post_comments`

<!-- Full path: /api/v1/instagram/v3/get_post_comments -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| code | string | ✅ | 帖子短代码/Post shortcode (e.g., DUajw4YkorV) | DUajw4YkorV |
| min_id | string |  | >- |  |
| sort_order | string (popular/newest) |  | >- (default: popular) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取Instagram帖子的评论列表
 - 支持分页获取所有评论
 - 支持按热门或最新排序
 ### 参数:
 - code: 帖子短代码（如 DUajw4YkorV，必填）
 - min_id: 分页游标，首次请求不传，从上一次响应的 `data.next_min_id` 获取
 - sort_order: 排序方式
    - `popular`: 按热门排序（默认）
    - `newest`: 按最新排序
### 返回:
 - `data.comments`: 评论列表
    - `user`: 评论者信息
    - `text`: 评论文本
    - `created_at`: 评论时间戳
    - `comment_like_count`: 评论点赞数
    - `child_comment_count`: 子评论数
- `data.next_min_id`: 下一页分页游标（传给下次请求的min_id参数）
 - `data.has_more_comments`: 是否有更多评论
 - `data.comment_count`: 评论总数
 ### 分页使用方法:
 1. 首次请求：传 `code` 参数
 2. 获取响应中的 `data.next_min_id`
 3. 下次请求：将 `next_min_id` 原样传入 `min_id` 参数（无需预处理，接口会自动反转义）
 4. 重复步骤 2-3 直到 `data.has_more_comments` 为 false
  ### 注意:
 - `min_id` 是接口返回的转义 JSON 字符串（如
`"{"cached_comments_cursor":"xxx","bifilter_token":"xxx"}"`），直接原样传入即可，接口内部会自动反转义处理

## get_post_info

`GET /api/v1/instagram/v3/get_post_info`

<!-- Full path: /api/v1/instagram/v3/get_post_info -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| media_id | string |  | 帖子媒体ID/Post media ID（与 url 二选一） | 3850699893338385742 |
| url | string |  | 帖子URL/Post URL（与 media_id 二选一；支持 /p/、/reel/、/reels/、/tv/ 形式） | https://www.instagram.com/p/DUajw4YkorV/ |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 通过媒体ID或帖子URL获取帖子详情
 - 返回帖子的完整信息，包括图片/视频、点赞数、评论数、发布者信息等
 ### 参数:
 - media_id: 帖子的媒体ID（数字ID），可通过 `/shortcode_to_media_id` 接口从短码转换获得
 - url: 帖子URL，例如 `https://www.instagram.com/p/DUajw4YkorV/`，支持
`/p/`、`/reel/`、`/reels/`、`/tv/` 路径
 - **media_id 与 url 至少提供一个；都提供时优先使用 media_id**
 ### 返回:
 - `data.items`: 帖子信息列表（通常只有一个元素）
    - `id`: 帖子ID
    - `code`: 帖子短代码
    - `media_type`: 媒体类型（1=图片, 2=视频, 8=合集）
    - `like_count`: 点赞数
    - `comment_count`: 评论数
    - `caption.text`: 帖子文本
    - `user`: 发布者信息
    - `image_versions2`: 图片版本列表
    - `video_versions`: 视频版本列表（视频时存在）
    - `carousel_media`: 合集媒体列表（合集时存在）
    - `taken_at`: 发布时间戳

## get_post_info_by_code

`GET /api/v1/instagram/v3/get_post_info_by_code`

<!-- Full path: /api/v1/instagram/v3/get_post_info_by_code -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| code | string | ✅ | 帖子短代码/Post shortcode | DUajw4YkorV |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 通过帖子的短代码（code/shortcode）获取帖子详情
 - 短代码即帖子URL中的标识符，如 `https://www.instagram.com/p/DUajw4YkorV/` 中的
`DUajw4YkorV`
 - 返回帖子的完整信息
 ### 参数:
 - code: 帖子短代码（如 DUajw4YkorV，必填）
 ### 返回:
 - `data.items`: 帖子信息列表
    - `id`: 帖子ID
    - `code`: 帖子短代码
    - `media_type`: 媒体类型（1=图片, 2=视频, 8=合集）
    - `like_count`: 点赞数
    - `comment_count`: 评论数
    - `caption.text`: 帖子文本
    - `user`: 发布者信息
    - `image_versions2`: 图片版本列表
    - `video_versions`: 视频版本列表（视频时存在）
    - `carousel_media`: 合集媒体列表（合集时存在）
    - `taken_at`: 发布时间戳

## get_post_oembed

`GET /api/v1/instagram/v3/get_post_oembed`

<!-- Full path: /api/v1/instagram/v3/get_post_oembed -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| url | string | ✅ | Instagram帖子的完整URL/Full URL of Instagram post | https://www.instagram.com/reel/DUlObENDmJD |
| hidecaption | boolean |  | 是否隐藏帖子文本/Whether to hide caption (default: false) |  |
| maxwidth | integer |  | 最大宽度（像素）/Max width in pixels (default: 540) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取Instagram帖子的oEmbed内嵌信息
 - 返回可直接嵌入网页的HTML代码和帖子元信息
 - 适用于需要在第三方网站嵌入Instagram帖子的场景
 ### 参数:
 - url: Instagram帖子的完整URL（如 `https://www.instagram.com/p/xxx/` 或
`https://www.instagram.com/reel/xxx/`）
 - hidecaption: 是否隐藏帖子文本（默认false）
 - maxwidth: 嵌入的最大宽度（像素，默认540）
 ### 返回:
 - `data.version`: oEmbed版本
 - `data.title`: 帖子标题
 - `data.author_name`: 作者名称
 - `data.author_url`: 作者主页URL
 - `data.author_id`: 作者ID
 - `data.media_id`: 媒体ID
 - `data.provider_name`: 提供者名称（Instagram）
 - `data.provider_url`: 提供者URL
 - `data.type`: 类型（rich）
 - `data.width`: 宽度
 - `data.html`: HTML嵌入代码
 - `data.thumbnail_url`: 缩略图URL
 - `data.thumbnail_width`: 缩略图宽度
 - `data.thumbnail_height`: 缩略图高度

## get_user_brief

`GET /api/v1/instagram/v3/get_user_brief`

<!-- Full path: /api/v1/instagram/v3/get_user_brief -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string | ✅ | 用户ID/User ID | 791258468 |
| username | string | ✅ | 用户名/Username | 99brasil |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取Instagram用户的短详情/悬浮卡片信息
- 返回用户核心信息，响应速度比 get_user_profile 更快
- 适用于批量获取用户摘要信息的场景
### 参数:
- user_id: Instagram用户ID（数字，必填）
- username: Instagram用户名（必填）
### 返回:
- `data.id`: 用户ID
- `data.username`: 用户名
- `data.full_name`: 全名
- `data.biography`: 个人简介
- `data.profile_pic_url`: 头像URL
- `data.is_verified`: 是否认证
- `data.is_private`: 是否私密账号
- `data.edge_followed_by.count`: 粉丝数
- `data.edge_follow.count`: 关注数
- `data.edge_owner_to_timeline_media`: 最近帖子预览

## get_user_posts

`GET /api/v1/instagram/v3/get_user_posts`

<!-- Full path: /api/v1/instagram/v3/get_user_posts -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| username | string | ✅ | Instagram 用户名（不含 @）/Instagram username (without @) | 99brasil |
| first | integer |  | 向后翻页时每页数量/Number of posts per page (forward) (default: 12) |  |
| after | string |  | 向后翻页游标（end_cursor）/Forward pagination cursor (end_cursor) |  |
| before | string |  | 向前翻页游标（start_cursor）/Backward pagination cursor (start_cursor) |  |
| last | integer |  | 向前翻页时每页数量/Number of posts per page (backward) |  |
| count | integer |  | 首次请求数量/Number of posts for first request (default: 12) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 分页获取用户发布的帖子列表，支持向前/向后翻页
  ### 参数:
 - **username**: 用户名字符串（如 `99brasil`），**不是数字 user_id**
 - **first**: 向后翻页时每页数量（默认12，最大50）
 - **after**: 向后翻页游标，从上一次响应的 `page_info.end_cursor` 中获取
 - **before**: 向前翻页游标，从上一次响应的 `page_info.start_cursor` 中获取
 - **last**: 向前翻页时每页数量，配合 `before` 使用
 - **count**: 首次请求数量（默认12）
  ### 翻页说明:
 - **向后翻页**: 使用 `first` + `after` 组合
 - **向前翻页**: 使用 `last` + `before` 组合
 - 首次请求不传 `after`/`before`，从响应中获取游标
  ### 返回:
 - `data.edges`: 帖子列表
 - `data.page_info`: 分页信息
    - `has_next_page`: 是否有下一页
    - `end_cursor`: 下一页游标
    - `start_cursor`: 上一页游标

## get_user_tagged_posts

`GET /api/v1/instagram/v3/get_user_tagged_posts`

<!-- Full path: /api/v1/instagram/v3/get_user_tagged_posts -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string |  | 用户ID/User ID | 58208242181 |
| username | string |  | 用户名（与user_id二选一）/Username (alternative to user_id) | instagram |
| first | integer |  | 向后翻页时每页数量/Number of posts per page (forward) (default: 12) |  |
| after | string |  | 向后翻页游标（end_cursor）/Forward pagination cursor (end_cursor) |  |
| before | string |  | 向前翻页游标（start_cursor）/Backward pagination cursor (start_cursor) |  |
| last | integer |  | 向前翻页时每页数量/Number of posts per page (backward) |  |
| count | integer |  | 首次请求数量/Number of posts for first request (default: 12) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取Instagram用户被标记（tagged）的帖子列表
 - 即其他用户在帖子中标记了该用户的内容
 - 支持分页获取
 ### 参数:
 - user_id: Instagram用户ID（数字，与username二选一）
 - username: Instagram用户名（与user_id二选一，传入后会自动转换为user_id）
 - first: 向后翻页时每页数量（默认12，最大50）
 - after: 向后翻页游标，从上一次响应的 `data.page_info.end_cursor` 获取
 - before: 向前翻页游标，从上一次响应的 `data.page_info.start_cursor` 获取
 - last: 向前翻页时每页数量，配合 `before` 使用
 - count: 首次请求数量（默认12）
 ### 返回:
 - `data.edges`: 帖子列表
    - `node.id`: 帖子ID
    - `node.code`: 帖子短代码
    - `node.display_url`: 展示图片URL
    - `node.taken_at`: 发布时间戳
    - `node.like_count`: 点赞数
    - `node.comment_count`: 评论数
    - `node.caption.text`: 帖子文本
    - `node.user`: 发帖者信息
- `data.page_info`: 分页信息
    - `has_next_page`: 是否有下一页
    - `end_cursor`: 下一页游标（传给下次请求的after参数）
### 分页使用方法:
 1. 首次请求：只传 `user_id` 和 `first` 参数
 2. 获取响应中的 `data.page_info.end_cursor`
 3. 下次请求：传入 `user_id`、`first` 和 `after` (使用上次的end_cursor)
 4. 重复步骤 2-3 直到 `data.page_info.has_next_page` 为 false

## media_id_to_shortcode

`GET /api/v1/instagram/v2/media_id_to_shortcode`

<!-- Full path: /api/v1/instagram/v2/media_id_to_shortcode -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| media_id | string | ✅ | 帖子Media ID/Post media ID | 3774507992167247878 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 将Instagram帖子的Media ID转换为Shortcode
 - Shortcode可用于构建帖子URL：instagram.com/p/{shortcode}/
 ### 参数:
 - media_id: 帖子的Media ID
 ### 返回:
 - `status`: 转换状态
 - `media_id`: 原始Media ID
 - `shortcode`: 转换后的Shortcode

## shortcode_to_media_id

`GET /api/v1/instagram/v2/shortcode_to_media_id`

<!-- Full path: /api/v1/instagram/v2/shortcode_to_media_id -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| shortcode | string | ✅ | 帖子Shortcode/Post shortcode | DRhvwVLAHAG |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 将Instagram帖子的Shortcode转换为Media ID
 - Shortcode是帖子URL中的唯一标识，如 instagram.com/p/DRhvwVLAHAG/ 中的 DRhvwVLAHAG
 ### 参数:
 - shortcode: 帖子的Shortcode
 ### 返回:
 - `status`: 转换状态
 - `shortcode`: 原始Shortcode
 - `media_id`: 转换后的Media ID

---

See SKILL.md for cross-group orchestration patterns.