# Post & User API / 帖子与用户接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---
## get_comment_replies

`GET /api/v1/sora2/get_comment_replies`

<!-- Full path: /api/v1/sora2/get_comment_replies -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| comment_id | string | ✅ | 一级评论ID/First-level comment ID | 68e659c5a37081919618c57baf499d0c |
| cursor | string |  | 翻页参数，从上一次响应中获取/Pagination cursor from previous response (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取一级评论的回复列表（二级评论）
 - 支持分页加载，每页返回 10 条回复
 - 用于展示评论的完整对话树
 - 本接口支持使用免费额度，每天可通过在用户后台签到获取免费调用次数。
  ### 参数:
 - comment_id: 一级评论的 ID，必填（可从 get_post_comments 接口的返回中获取）
 - cursor: 翻页参数（可选），首次请求留空，后续请求使用上一次响应中的 cursor 值
  ### 返回:
 - children: 回复数据
    - items: 回复列表（10条/页）
        - id: 回复 ID
        - text: 回复文本内容
        - posted_by: 回复者用户 ID
        - posted_at: 回复时间戳
        - like_count: 点赞数
        - profile: 回复者信息
            - username: 用户名
            - display_name: 显示名称
            - profile_picture_url: 头像链接
    - cursor: 下一页参数（用于获取更多回复，无更多时为 null）
    - has_more: 是否有更多数据

## get_feed

`GET /api/v1/sora2/get_feed`

<!-- Full path: /api/v1/sora2/get_feed -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| cursor | string |  | 翻页参数，从上一次响应中获取/Pagination cursor from previous response (default: '') |  |
| eager_views | string |  | >- (default: '') | {"views":[]} |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取 Sora 的 Feed 流（热门或推荐视频列表）
 - 默认返回过去 7 天的热门视频
 - 支持分页加载，每页返回约 15 条视频
 - 可通过 eager_views 参数提供观看记录来获得个性化推荐
 - 本接口支持使用免费额度，每天可通过在用户后台签到获取免费调用次数。
  ### 参数:
 - cursor: 翻页参数（可选），首次请求留空，后续请求使用上一次响应中的 cursor 值
 - eager_views: 观看记录（可选），JSON 字符串格式
    - 默认值：`{"views":[]}`（空观看记录，返回通用热门）
    - 包含观看记录示例：`{"views":[{"id":"s_xxx","watch_time":0.24,"dwell_time":3.94}]}`
    - 提供观看记录可获得更个性化的推荐结果
 ### 返回:
 - items: 视频列表（约15条/页）
    - post: 作品信息
        - id: 作品 ID
        - text: 作品描述
        - attachments: 视频附件信息
        - like_count: 点赞数
        - view_count: 浏览数
        - reply_count: 评论数
        - posted_at: 发布时间戳
    - profile: 作者信息
- cursor: 下一页参数（用于获取更多视频，无更多时为 null）
 - has_more: 是否有更多数据

## get_post_comments

`GET /api/v1/sora2/get_post_comments`

<!-- Full path: /api/v1/sora2/get_post_comments -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| post_id | string | ✅ | 作品ID/Post ID | s_68e647d78e5081918cdeaf27e7edc735 |
| cursor | string |  | 翻页参数，从上一次响应中获取/Pagination cursor from previous response (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取 Sora 作品的一级评论列表（顶层评论）
 - 支持分页加载，每页返回 10 条评论
 - 可用于评论展示、数据分析等场景
 - 本接口支持使用免费额度，每天可通过在用户后台签到获取免费调用次数。
  ### 参数:
 - post_id: 作品 ID，必填
 - cursor: 翻页参数（可选），首次请求留空，后续请求使用上一次响应中的 cursor 值
  ### 返回:
 - children: 评论数据
    - items: 评论列表（10条/页）
        - id: 评论 ID
        - text: 评论文本内容
        - posted_by: 评论者用户 ID
        - posted_at: 评论时间戳
        - like_count: 点赞数
        - reply_count: 回复数（二级评论数）
        - profile: 评论者信息
            - username: 用户名
            - display_name: 显示名称
            - profile_picture_url: 头像链接
    - cursor: 下一页参数（用于获取更多评论，无更多时为 null）
    - has_more: 是否有更多数据

## get_post_detail

`GET /api/v1/sora2/get_post_detail`

<!-- Full path: /api/v1/sora2/get_post_detail -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| post_id | string |  | 作品ID（可选）/Post ID (optional) (default: '') | s_68e853d2ad448191b3c81e830f53c3a2 |
| post_url | string |  | 作品链接（可选）/Post URL (optional) (default: '') | https://sora.chatgpt.com/p/s_68e853d2ad448191b3c81e830f53c3a2 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取 Sora 作品的完整详情信息，包括视频信息、作者信息、统计数据等
 - 支持通过作品 ID 或作品链接查询
 - 可用于数据分析、无水印视频下载等场景
 - 本接口支持使用免费额度，每天可通过在用户后台签到获取免费调用次数。
  ### 参数:
 - post_id: 作品 ID（可选），格式如 `s_68e853d2ad448191b3c81e830f53c3a2`
 - post_url: 作品链接（可选），格式如
`https://sora.chatgpt.com/p/s_68e853d2ad448191b3c81e830f53c3a2`
 - **注意**: post_id 和 post_url 至少提供一个
  ### 返回:
 - post: 作品详细信息
    - id: 作品 ID
    - text: 作品描述文本
    - attachments: 附件列表（视频信息）
        - url: 无水印视频链接
        - downloadable_url: 有水印视频链接
        - width/height: 视频尺寸
        - encodings: 不同质量的编码版本
    - like_count: 点赞数
    - view_count: 浏览数
    - reply_count: 评论数
    - remix_count: 混剪数
    - shared_by: 作者用户 ID
    - posted_at: 发布时间戳
    - permalink: 作品永久链接
- profile: 作者信息
    - user_id: 用户 ID
    - username: 用户名
    - display_name: 显示名称
    - profile_picture_url: 头像链接
    - follower_count: 粉丝数

## get_post_remix_list

`GET /api/v1/sora2/get_post_remix_list`

<!-- Full path: /api/v1/sora2/get_post_remix_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| post_id | string |  | 作品ID（可选）/Post ID (optional) (default: '') | s_690acc0f4fcc8191ab5a75a96b6b6caf |
| post_url | string |  | 作品链接（可选）/Post URL (optional) (default: '') | https://sora.chatgpt.com/p/s_690acc0f4fcc8191ab5a75a96b6b6caf |
| cursor | string |  | 翻页参数（可选）/Cursor for pagination (optional) (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取 Sora 作品的 Remix 列表
 - 支持通过作品 ID 或作品链接查询
 - 支持分页获取更多 Remix 作品
 - 本接口支持使用免费额度，每天可通过在用户后台签到获取免费调用次数。
  ### 参数:
 - post_id: 作品 ID（可选），格式如 `s_68e466aa780c8191b`
 - post_url: 作品链接（可选），格式如
`https://sora.chatgpt.com/p/s_68e466aa780c8191b2357907ce7d1a39`
 - cursor: 翻页参数（可选），从上一次响应的 cursor 字段获取
 - **注意**: post_id 和 post_url 至少提供一个
  ### 返回:
 - items: Remix 作品列表
    - id: 作品 ID
    - text: 作品描述文本
    - attachments: 附件列表（视频信息）
    - like_count: 点赞数
    - view_count: 浏览数
    - reply_count: 评论数
    - remix_count: 混剪数
    - shared_by: 作者用户 ID
    - posted_at: 发布时间戳
- cursor: 下一页参数，用于获取更多数据（如果为 null 表示已到末页）

## get_user_followers

`GET /api/v1/sora2/get_user_followers`

<!-- Full path: /api/v1/sora2/get_user_followers -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string | ✅ | 用户ID/User ID | user-xiCyLclE6KJcdTXyvVq3Ontc |
| cursor | string |  | 翻页参数，从上一次响应中获取/Pagination cursor from previous response (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取 Sora 用户的粉丝列表
 - 支持分页加载，每页返回 50 个粉丝
 - 可用于粉丝关系分析、社交网络研究等场景
 - 本接口支持使用免费额度，每天可通过在用户后台签到获取免费调用次数。
  ### 参数:
 - user_id: 用户 ID，必填
 - cursor: 翻页参数（可选），首次请求留空，后续请求使用上一次响应中的 cursor 值
  ### 返回:
 - items: 粉丝列表（50个/页）
    - user_id: 粉丝用户 ID
    - username: 粉丝用户名
    - display_name: 粉丝显示名称
    - profile_picture_url: 粉丝头像链接
    - follower_count: 粉丝的粉丝数
    - following_count: 粉丝的关注数
    - bio: 粉丝个人简介
    - is_verified: 是否认证用户
- cursor: 下一页参数（用于获取更多粉丝，无更多时为 null）
 - has_more: 是否有更多数据

## get_user_following

`GET /api/v1/sora2/get_user_following`

<!-- Full path: /api/v1/sora2/get_user_following -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string | ✅ | 用户ID/User ID | user-BOXD64QrAyZVybLCeXTqJWm3 |
| cursor | string |  | 翻页参数，从上一次响应中获取/Pagination cursor from previous response (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取 Sora 用户的关注列表（用户关注的其他人）
 - 支持分页加载，每页返回 50 个关注对象
 - 可用于关注关系分析、推荐算法等场景
 - 本接口支持使用免费额度，每天可通过在用户后台签到获取免费调用次数。
  ### 参数:
 - user_id: 用户 ID，必填
 - cursor: 翻页参数（可选），首次请求留空，后续请求使用上一次响应中的 cursor 值
  ### 返回:
 - items: 关注列表（50个/页）
    - user_id: 被关注用户 ID
    - username: 被关注用户名
    - display_name: 被关注用户显示名称
    - profile_picture_url: 被关注用户头像链接
    - follower_count: 被关注用户的粉丝数
    - following_count: 被关注用户的关注数
    - bio: 被关注用户个人简介
    - is_verified: 是否认证用户
- cursor: 下一页参数（用于获取更多关注，无更多时为 null）
 - has_more: 是否有更多数据

## get_user_posts

`GET /api/v1/sora2/get_user_posts`

<!-- Full path: /api/v1/sora2/get_user_posts -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string | ✅ | 用户ID/User ID | user-xiCyLclE6KJcdTXyvVq3Ontc |
| cursor | string |  | 翻页参数，从上一次响应中获取/Pagination cursor from previous response (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取 Sora 用户发布的作品列表
 - 支持分页加载，每页返回 30 条作品
 - 可用于用户主页展示、作品数据采集等场景
 - 本接口支持使用免费额度，每天可通过在用户后台签到获取免费调用次数。
  ### 参数:
 - user_id: 用户 ID，必填
 - cursor: 翻页参数（可选），首次请求留空，后续请求使用上一次响应中的 cursor 值
  ### 返回:
 - items: 作品列表（30条/页）
    - post: 作品信息
        - id: 作品 ID
        - text: 作品描述
        - attachments: 视频附件信息
        - like_count: 点赞数
        - view_count: 浏览数
        - reply_count: 评论数
        - posted_at: 发布时间戳
    - profile: 作者信息
- cursor: 下一页参数（用于获取更多作品，无更多时为 null）
 - has_more: 是否有更多数据

## get_user_profile

`GET /api/v1/sora2/get_user_profile`

<!-- Full path: /api/v1/sora2/get_user_profile -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string | ✅ | 用户ID/User ID | user-xiCyLclE6KJcdTXyvVq3Ontc |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取 Sora 用户的个人信息档案
 - 包含用户基本信息、统计数据、社交关系等
 - 可用于用户资料展示、数据分析等场景
 - 本接口支持使用免费额度，每天可通过在用户后台签到获取免费调用次数。
  ### 参数:
 - user_id: 用户 ID，必填，格式如 `user-xiCyLclE6KJcdTXyvVq3Ontc`
  ### 返回:
 - profile: 用户信息
    - user_id: 用户 ID
    - username: 用户名
    - display_name: 显示名称
    - bio: 个人简介
    - profile_picture_url: 头像链接
    - banner_image_url: 横幅图片链接
    - follower_count: 粉丝数
    - following_count: 关注数
    - post_count: 作品数
    - like_count: 获赞总数
    - view_count: 浏览总数
    - is_verified: 是否认证用户
    - created_at: 账号创建时间戳
    - social_links: 社交媒体链接（如有）

## get_video_download_info

`GET /api/v1/sora2/get_video_download_info`

<!-- Full path: /api/v1/sora2/get_video_download_info -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| post_id | string |  | 作品ID（可选）/Post ID (optional) (default: '') | s_68e853d2ad448191b3c81e830f53c3a2 |
| post_url | string |  | 作品链接（可选）/Post URL (optional) (default: '') | https://sora.chatgpt.com/p/s_68e853d2ad448191b3c81e830f53c3a2 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取 Sora 作品的简化下载信息，专为视频下载场景优化
 - 直接返回无水印视频链接和关键信息，无需解析复杂的完整数据
 - 适合需要快速下载视频的场景
 - 本接口支持使用免费额度，每天可通过在用户后台签到获取免费调用次数。
  ### 参数:
 - post_id: 作品 ID（可选），格式如 `s_68e853d2ad448191b3c81e830f53c3a2`
 - post_url: 作品链接（可选），格式如
`https://sora.chatgpt.com/p/s_68e853d2ad448191b3c81e830f53c3a2`
 - **注意**: post_id 和 post_url 至少提供一个
  ### 返回:
 - post_id: 作品 ID
 - title: 作品描述文本
 - video: 视频信息
    - no_watermark: 无水印视频链接（原始质量）
    - watermark: 有水印视频链接
    - width: 视频宽度
    - height: 视频高度
    - thumbnail: 缩略图链接
    - preview_gif: 预览 GIF 链接
    - medium_quality: 中等质量视频链接
- author: 作者信息
    - user_id: 用户 ID
    - username: 用户名
    - display_name: 显示名称
    - avatar: 头像链接
- stats: 统计数据
    - like_count: 点赞数
    - view_count: 浏览数
    - comment_count: 评论数
    - remix_count: 混剪数
- permalink: 作品永久链接
 - created_at: 创建时间戳

## search_users

`GET /api/v1/sora2/search_users`

<!-- Full path: /api/v1/sora2/search_users -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| username | string | ✅ | 搜索关键词（用户名）/Search keyword (username) | sam |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 搜索 Sora 用户（主要用于 @ 提及功能）
 - 根据用户名关键词搜索匹配的用户
 - 返回用户信息和提及 Token（用于在评论中 @ 用户）
 - 注意：实际返回结果可能超过 20 个，比预期的更多
 - 本接口支持使用免费额度，每天可通过在用户后台签到获取免费调用次数。
  ### 参数:
 - username: 搜索关键词，必填，支持部分匹配
  ### 返回:
 - items: 用户搜索结果列表
    - profile: 用户信息
        - user_id: 用户 ID
        - username: 用户名
        - display_name: 显示名称
        - profile_picture_url: 头像链接
        - follower_count: 粉丝数
        - following_count: 关注数
        - bio: 个人简介
        - is_verified: 是否认证用户
    - token: 提及 Token（用于 @ 提及功能）
        - 格式：`<@user-xxxxxxxx>`
        - 在评论中使用此 Token 可以提及该用户

---

See SKILL.md for cross-group orchestration patterns.