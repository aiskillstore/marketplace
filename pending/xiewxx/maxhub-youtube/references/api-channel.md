# Channel Data API / 频道数据接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---
## get_channel_community_posts

`GET /api/v1/youtube/web_v2/get_channel_community_posts`

<!-- Full path: /api/v1/youtube/web_v2/get_channel_community_posts -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| channel_id | string | ✅ | 频道ID/Channel ID | UCkRfArvrzheW2E7b6SVT7vQ |
| language_code | string |  | 语言代码（如zh-CN, en-US等）/Language code (default: zh-CN) | zh-CN |
| country_code | string |  | 国家代码（如US, JP等）/Country code (default: US) | US |
| continuation_token | string |  | 分页token，用于获取下一页/Pagination token for next page |  |
| need_format | boolean |  | 是否需要清洗数据，提取关键内容，移除冗余数据/Whether to clean and format the data (default: true) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取YouTube频道的帖子（社区帖子）列表
 - 支持分页获取，可通过 continuation_token 获取更多帖子
  ### 参数详解:
  #### 必选参数:
 **channel_id** (string)
 - **作用**: 频道ID
 - **获取方式**: 从频道URL中提取，例如
`https://www.youtube.com/channel/UCkRfArvrzheW2E7b6SVT7vQ`
 - **示例**: `"UCkRfArvrzheW2E7b6SVT7vQ"`
  #### 可选参数:
 **language_code** (string, 可选)
 - **作用**: 语言代码，影响返回的文本语言
 - **默认值**: `"zh-CN"`
  **country_code** (string, 可选)
 - **作用**: 国家代码
 - **默认值**: `"US"`
  **continuation_token** (string, 可选)
 - **作用**: 分页token，用于获取下一页帖子
 - **获取方式**: 从上一次请求的响应中获取
  **need_format** (bool, 可选)
 - **作用**: 是否格式化数据
 - **默认值**: `true`
  ### 返回数据:
 #### 当 need_format=true 时:
 - channel_id: 频道ID
 - posts: 帖子列表
  - post_id: 帖子ID
  - post_url: 帖子URL
  - author_name: 作者名称
  - author_channel_id: 作者频道ID
  - author_url: 作者频道URL
  - author_thumbnails: 作者头像缩略图
  - content_text: 帖子文本内容
  - published_time: 发布时间（相对时间）
  - vote_count: 点赞数
  - comment_count: 评论数
  - attachment: 附件（图片/多图/视频/投票等，可能为null）
- continuation_token: 下一页分页token
 - has_more: 是否还有更多帖子
 - total_count: 当前页帖子数量
  #### 当 need_format=false 时:
 - 返回原始响应数据
  ### 使用流程:
 1. 首次请求：只传 channel_id 参数
 2. 获取响应中的 continuation_token
 3. 下次请求：传入 channel_id 和 continuation_token
 4. 重复步骤 2-3 直到 has_more 为 false
  ### 注意事项:
 - 每页通常返回 20 个左右的帖子
 - 帖子附件支持: 图片、多图、视频、投票等类型
 - 部分频道可能没有帖子/社区标签页

## get_channel_description

`GET /api/v1/youtube/web_v2/get_channel_description`

<!-- Full path: /api/v1/youtube/web_v2/get_channel_description -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| channel_id | string |  | >- | UCeu6U67OzJhV1KwBansH3Dg |
| continuation_token | string |  | >- |  |
| language_code | string |  | 语言代码（如zh-CN, en-US等）/Language code (default: zh-CN) | zh-CN |
| country_code | string |  | 国家代码（如US, JP等）/Country code (default: US) | US |
| need_format | boolean |  | 是否需要清洗数据，提取关键内容，移除冗余数据/Whether to clean and format the data (default: true) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取YouTube频道的介绍信息（订阅数、视频数、观看次数、注册时间、社交链接等）
  ### 重要提示 - 需要两次请求获取完整数据:
 - **第一次请求**（使用channel_id）: 返回基本信息（频道名称、描述、订阅数、视频数、头像、横幅等）
 - **第二次请求**（使用continuation_token）: 返回高级信息（**注册时间、社交媒体链接、国家、观看次数**等）
  ### 如何获取channel_id:
 - 如果你只有频道URL（如 `https://www.youtube.com/@CozyCraftYT`），请先调用
**get_channel_id** 接口获取channel_id
 - 该接口会返回类似 `UCeu6U67OzJhV1KwBansH3Dg` 的频道ID
  ### 参数详解:
  #### 📌 必选参数（二选一）:
 **channel_id** (string)
 - **作用**: 频道ID，用于第一次请求获取频道基本信息
 - **格式**: 通常以 `UC` 开头的24位字符串
 - **示例**: `"UCeu6U67OzJhV1KwBansH3Dg"`
 - **获取方式**: 调用 **get_channel_id** 接口，传入频道URL即可获取
  **continuation_token** (string)
 - **作用**: 翻页标志，用于第二次请求获取频道的高级信息
 - **获取方式**: 从第一次请求的响应中获取 `continuation_token` 字段
 - **注意**: `channel_id` 和 `continuation_token` 必须提供其中一个
  #### ⚙️ 可选参数:
 **language_code** (string, 可选)
 - **作用**: 设置显示语言偏好
 - **默认值**: `"zh-CN"`
 - **可用值**: `"zh-CN"`, `"en-US"`, `"ja-JP"`, `"ko-KR"` 等
  **country_code** (string, 可选)
 - **作用**: 设置地区代码
 - **默认值**: `"US"`
 - **可用值**: `"US"`, `"JP"`, `"GB"` 等
  **need_format** (boolean, 可选)
 - **作用**: 是否返回清洗后的精简数据
 - **默认值**: `true`
 - **可用值**:
  - `false` - 返回原始完整数据
  - `true` - 返回清洗后的精简数据（推荐，默认）
 ### 使用流程（三步获取完整数据）:
 1. **获取channel_id**: 如果只有频道URL，先调用
`get_channel_id?channel_url=https://www.youtube.com/@CozyCraftYT`
 2. **第一次请求**: 使用 `channel_id` 参数获取频道基本信息，同时获取 `continuation_token`
 3. **第二次请求**: 使用 `continuation_token` 获取高级信息（注册时间、社交链接等）
  ### 返回数据结构 (need_format=true):
  #### 第一次请求返回（使用channel_id）:
 ```json
 {
  "channel_id": "UCeu6U67OzJhV1KwBansH3Dg",
  "title": "CozyCraft",
  "handle": "CozyCraftYT",
  "description": "频道介绍...",
  "subscriber_count": "9.84万位订阅者",
  "video_count": "181 个视频",
  "view_count": null,
  "country": null,
  "creation_date": null,
  "links": [],
  "avatar": [{"url": "...", "width": 900, "height": 900}],
  "banner": [{"url": "...", "width": 2560, "height": 424}],
  "keywords": "Minecraft Ambience...",
  "channel_url": "https://www.youtube.com/channel/UCeu6U67OzJhV1KwBansH3Dg",
  "vanity_url": "http://www.youtube.com/@CozyCraftYT",
  "rss_url": "https://www.youtube.com/feeds/videos.xml?channel_id=UCeu6U67OzJhV1KwBansH3Dg",
  "is_family_safe": true,
  "verified": false,
  "has_business_email": false,
  "has_membership": true,
  "continuation_token": "4qmFsgJg..."
}
 ```
  #### 第二次请求返回（使用continuation_token）:
 ```json
 {
  "channel_id": "UCeu6U67OzJhV1KwBansH3Dg",
  "title": null,
  "handle": "CozyCraftYT",
  "description": "完整频道介绍...",
  "subscriber_count": "98.4K subscribers",
  "video_count": "181 videos",
  "view_count": "53,218,926 views",
  "country": "United States",
  "creation_date": "Oct 28, 2022",
  "links": [
    {"name": "Discord", "url": "https://discord.gg/tvuxxcsgSS"},
    {"name": "Twitter", "url": "https://twitter.com/..."}
  ],
  "avatar": [],
  "banner": [],
  "verified": false,
  "has_business_email": true,
  "continuation_token": null
}
 ```
  ### 注意事项:
 - **必须进行两次请求才能获取完整的频道信息**
 - 第一次请求: 获取基本信息（title、avatar、banner、keywords、rss_url等）和
continuation_token
 - 第二次请求: 获取高级信息（creation_date、links、view_count、country等）
 - 建议两次请求都设置 `need_format=true` 获取清洗后的数据
 - 可以合并两次请求的结果来获得完整的频道信息

## get_channel_id

`GET /api/v1/youtube/web/get_channel_id`

<!-- Full path: /api/v1/youtube/web/get_channel_id -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| channel_name | string | ✅ | 频道名称/Channel name | LinusTechTips |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取频道ID。
### 参数:
- channel_name: 频道名称。
### 返回:
- 频道ID。

## get_channel_id

`GET /api/v1/youtube/web/get_channel_id`

<!-- Full path: /api/v1/youtube/web_v2/get_channel_id -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| channel_url | string | ✅ | >- | https://www.youtube.com/@CozyCraftYT |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 从YouTube频道URL转换获取频道ID（channel_id）。
 - 支持多种URL格式，包括@用户名格式、/channel/格式、/c/格式、/user/格式。
 ### 参数:
 - channel_url: 频道URL。
 ### 返回:
 - channel_id: 频道ID（如：UCeu6U67OzJhV1KwBansH3Dg）
 - channel_url: 标准化的频道URL
 - source: 数据来源（url_parse表示直接从URL解析，page_parse表示从页面解析）

## get_channel_id_v2

`GET /api/v1/youtube/web/get_channel_id_v2`

<!-- Full path: /api/v1/youtube/web/get_channel_id_v2 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| channel_url | string | ✅ | >- | https://www.youtube.com/@CozyCraftYT |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 从YouTube频道URL转换获取频道ID（channel_id）。
 - 支持多种URL格式，包括@用户名格式、/channel/格式、/c/格式、/user/格式。
 ### 参数:
 - channel_url: 频道URL。
 ### 返回:
 - channel_id: 频道ID（如：UCeu6U67OzJhV1KwBansH3Dg）
 - channel_url: 标准化的频道URL
 - source: 数据来源（url_parse表示直接从URL解析，page_parse表示从页面解析）

## get_channel_url

`GET /api/v1/youtube/web/get_channel_url`

<!-- Full path: /api/v1/youtube/web/get_channel_url -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| channel_id | string | ✅ | 频道ID/Channel ID (格式如：UCeu6U67OzJhV1KwBansH3Dg) | UCeu6U67OzJhV1KwBansH3Dg |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 从YouTube频道ID转换获取频道Handle (@用户名)
- 与 get_channel_id_v2 接口互为反向操作
 ### 参数:
- channel_id: 频道ID（如：UCeu6U67OzJhV1KwBansH3Dg）
 ### 返回:
- channel_id: 频道ID
- handle: 频道Handle（如：CozyCraftYT）
- title: 频道名称
- channel_url: 标准频道URL（/channel/格式）
- vanity_url: 个性化URL（/@用户名格式）
 ### 使用场景:
- 当你有频道ID但需要获取@用户名格式的URL时
- 需要展示用户友好的频道链接时

## get_channel_url

`GET /api/v1/youtube/web/get_channel_url`

<!-- Full path: /api/v1/youtube/web_v2/get_channel_url -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| channel_id | string | ✅ | 频道ID/Channel ID (格式如：UCeu6U67OzJhV1KwBansH3Dg) | UCeu6U67OzJhV1KwBansH3Dg |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 从YouTube频道ID转换获取频道Handle (@用户名)
- 与 get_channel_id 接口互为反向操作
 ### 参数:
- channel_id: 频道ID（如：UCeu6U67OzJhV1KwBansH3Dg）
 ### 返回:
- channel_id: 频道ID
- handle: 频道Handle（如：CozyCraftYT）
- title: 频道名称
- channel_url: 标准频道URL（/channel/格式）
- vanity_url: 个性化URL（/@用户名格式）
 ### 使用场景:
- 当你有频道ID但需要获取@用户名格式的URL时
- 需要展示用户友好的频道链接时

## get_post_comment_replies

`GET /api/v1/youtube/web_v2/get_post_comment_replies`

<!-- Full path: /api/v1/youtube/web_v2/get_post_comment_replies -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| continuation_token | string | ✅ | >- |  |
| language_code | string |  | 语言代码（如zh-CN, en-US等）/Language code (default: zh-CN) | zh-CN |
| country_code | string |  | 国家代码（如US, JP等）/Country code (default: US) | US |
| need_format | boolean |  | 是否需要清洗数据，提取关键内容，移除冗余数据/Whether to clean and format the data (default: true) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取帖子评论的回复（二级评论）
  ### 参数详解:
  #### 必选参数:
 **continuation_token** (string)
 - **作用**: 回复的continuation token
 - **获取方式**: 从帖子一级评论的响应数据中获取 `reply_continuation_token` 字段
  #### 可选参数:
 **language_code** (string, 可选) - 语言代码，默认 `"zh-CN"`
  **country_code** (string, 可选) - 国家代码，默认 `"US"`
  **need_format** (bool, 可选) - 是否格式化数据，默认 `true`
  ### 使用流程:
 1. 先调用 `/get_post_comments` 获取帖子一级评论
 2. 从一级评论中找到 `reply_continuation_token` 字段
 3. 使用该 token 调用本接口获取该评论的所有回复
 4. 如果还有更多回复，使用返回的 `continuation_token` 继续获取
  ### 返回数据 (need_format=true):
 - comments: 回复评论列表
  - comment_id: 评论ID
  - content: 评论内容文本
  - published_time: 发布时间
  - like_count: 点赞数
  - author: 作者信息
- continuation_token: 下一页token（如果有更多回复）

## get_post_comments

`GET /api/v1/youtube/web_v2/get_post_comments`

<!-- Full path: /api/v1/youtube/web_v2/get_post_comments -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| post_id | string |  | 帖子ID（首次请求时必填）/Post ID (required for first request) | UgkxiCSRfD6g7SPlWGPDa3vbP7aIsytXRkvy |
| continuation_token | string |  | >- |  |
| language_code | string |  | 语言代码（如zh-CN, en-US等）/Language code (default: zh-CN) | zh-CN |
| country_code | string |  | 国家代码（如US, JP等）/Country code (default: US) | US |
| need_format | boolean |  | 是否需要清洗数据，提取关键内容，移除冗余数据/Whether to clean and format the data (default: true) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取YouTube帖子（社区帖子）的评论列表
 - 支持分页获取更多评论
  ### 参数详解:
  #### 参数（至少提供一个）:
 **post_id** (string)
 - **作用**: 帖子ID，首次请求时必填
 - **获取方式**: 从帖子URL中提取，例如
`https://www.youtube.com/post/UgkxiCSRfD6g7SPlWGPDa3vbP7aIsytXRkvy`
 - **示例**: `"UgkxiCSRfD6g7SPlWGPDa3vbP7aIsytXRkvy"`
  **continuation_token** (string)
 - **作用**: 分页token
 - **获取方式**:
  - 从 `get_post_detail` 返回的 `comments_continuation_token` 字段获取（首次请求）
  - 或从上一次评论请求的响应中获取 `continuation_token`（分页请求）
 #### 可选参数:
 **language_code** (string, 可选) - 语言代码，默认 `"zh-CN"`
  **country_code** (string, 可选) - 国家代码，默认 `"US"`
  **need_format** (bool, 可选) - 是否格式化数据，默认 `true`
  ### 返回数据 (need_format=true):
 - comments: 评论列表
  - comment_id: 评论ID
  - content: 评论内容文本
  - published_time: 发布时间
  - like_count: 点赞数
  - like_count_a11y: 点赞数无障碍文本
  - reply_count: 回复数
  - reply_count_text: 回复数文本
  - reply_continuation_token: 回复的continuation token（用于获取二级评论）
  - author: 作者信息
    - channel_id: 作者频道ID
    - display_name: 显示名称
    - channel_url: 频道URL
    - avatar_url: 头像URL
    - is_verified: 是否认证
    - is_creator: 是否为创作者
- continuation_token: 下一页评论的分页token
  ### 使用流程:
 1. 首次请求：传入 post_id（或从 get_post_detail 获取 comments_continuation_token 作为
continuation_token）
 2. 获取响应中的 continuation_token
 3. 下次请求：传入 continuation_token 获取更多评论
 4. 每条评论如有回复，可用 reply_continuation_token 调用 get_post_comment_replies

## get_shorts_search_v2

`GET /api/v1/youtube/web_v2/get_shorts_search_v2`

<!-- Full path: /api/v1/youtube/web_v2/get_shorts_search_v2 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string |  | 搜索关键词（首次请求必填）/Search keyword (required for first request) | coding tips |
| continuation_token | string |  | 分页token，用于获取下一页/Continuation token for next page |  |
| upload_date | string |  | 上传时间过滤/Upload date filter |  |
| sort_by | string |  | 排序方式/Sort by |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 专门搜索 YouTube Shorts 短视频
 - 返回清洗后的结构化数据（相比 get_shorts_search 返回原始数据）
 - 自动过滤非 Shorts 内容，仅返回短视频结果
 - 支持分页加载更多
  ### 参数:
 - keyword: 搜索关键词（首次请求必填）
 - continuation_token: 分页token（从上一次返回结果获取）
 - upload_date: 上传时间过滤 - last_hour/today/this_week/this_month/this_year
 - sort_by: 排序方式 - relevance/upload_date/view_count/rating
  ### 返回数据:
 - shorts: Shorts 列表（video_id、标题、播放量、作者、频道ID、缩略图、URL）
 - continuation_token: 下一页 token

## search_channel

`GET /api/v1/youtube/web/search_channel`

<!-- Full path: /api/v1/youtube/web/search_channel -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| channel_id | string | ✅ | 频道ID/Channel ID | UCXuqSBlHAE6Xw-yeJA0Tunw |
| search_query | string | ✅ | 搜索关键字/Search keyword | AMD |
| language_code | string |  | 语言代码/Language code (default: en) |  |
| country_code | string |  | 国家代码/Country code (default: us) |  |
| continuation_token | string |  | 翻页令牌/Pagination token |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 搜索频道。
 ### 参数:
 - search_query: 搜索关键字。
 - language_code: 语言代码，默认为en。
 - country_code: 国家代码，默认为us。
 - continuation_token: 用于继续获取搜索结果的令牌。默认为None。
 ### 返回:
 - 搜索结果。

## search_channels

`GET /api/v1/youtube/web_v2/search_channels`

<!-- Full path: /api/v1/youtube/web_v2/search_channels -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string |  | 搜索关键词/Search keyword | Rick Astley |
| continuation_token | string |  | 分页token/Pagination token |  |
| need_format | boolean |  | 是否格式化数据/Whether to format data (default: true) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 搜索YouTube频道
 - 只返回频道类型的搜索结果（过滤掉视频、播放列表等）
 - 支持分页获取更多频道
  ### 参数:
 - keyword: 搜索关键词（首次请求必填）
 - continuation_token: 分页token（可选，用于获取下一页）
 - need_format: 是否格式化数据（默认 true）
  - true: 返回格式化的结构化数据（推荐）
  - false: 返回原始的 YouTube API 结构（用于调试）
 ### 返回数据包含:
 #### 当 need_format=true 时:
 - keyword: 搜索关键词
 - channels: 频道列表
  - channel_id: 频道ID（如 "UCjuNibFJ21MiSNpu8LZyV4w"）
  - title: 频道名称
  - handle: 频道自定义handle（如 "@chaijing2023"）
  - subscriber_count_text: 订阅者数量文本（如 "1.11M subscribers"）
  - description: 频道描述片段
  - thumbnails: 缩略图列表（包含不同尺寸）
  - is_subscribed: 当前用户是否已订阅该频道（布尔值）
  - canonical_url: 频道规范URL路径（如 "/@chaijing2023"）
  - channel_url: 频道完整URL（优先使用自定义URL）
- continuation_token: 下一页的分页token
 - has_more: 是否还有更多频道
 - total_count: 当前页频道数量
  #### 当 need_format=false 时:
 - keyword: 搜索关键词
 - channels: 原始的 channelRenderer 对象列表
 - continuation_token: 下一页的分页token
 - has_more: 是否还有更多频道
 - total_count: 当前页频道数量
  ### 使用流程:
 1. 首次请求：只传 keyword 参数
 2. 获取响应中的 continuation_token
 3. 下次请求：传入 continuation_token（keyword 可选）
 4. 重复步骤 2-3 直到 has_more 为 false
  ### 注意事项:
 - 每页通常返回 10-20 个频道
 - 搜索结果只包含频道，不包含视频、播放列表等
 - 搜索结果的顺序和数量由 YouTube 算法决定

---

See SKILL.md for cross-group orchestration patterns.