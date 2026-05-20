# Video Data API / 视频数据接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---
## get_channel_info

`GET /api/v1/youtube/web/get_channel_info`

<!-- Full path: /api/v1/youtube/web/get_channel_info -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| channel_id | string | ✅ | 频道ID/Channel ID | UCXuqSBlHAE6Xw-yeJA0Tunw |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取频道信息。
### 参数:
- channel_id: 频道ID。
### 返回:
- 频道信息。

## get_channel_short_videos

`GET /api/v1/youtube/web/get_channel_short_videos`

<!-- Full path: /api/v1/youtube/web/get_channel_short_videos -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| channel_id | string | ✅ | 频道ID/Channel ID | UCXuqSBlHAE6Xw-yeJA0Tunw |
| continuation_token | string |  | 翻页令牌/Pagination token |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取频道短视频。
 ### 参数:
 - channel_id: 频道ID。
 - continuation_token: 用于继续获取频道短视频的令牌。默认为None。
 ### 返回:
 - 频道短视频。

## get_channel_shorts

`GET /api/v1/youtube/web_v2/get_channel_shorts`

<!-- Full path: /api/v1/youtube/web_v2/get_channel_shorts -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| channel_id | string |  | 频道ID/Channel ID (e.g., UCuAXFkgsw1L7xaCfnd5JJOw) | UCuAXFkgsw1L7xaCfnd5JJOw |
| channel_url | string |  | >- | https://www.youtube.com/channel/UCuAXFkgsw1L7xaCfnd5JJOw |
| continuation_token | string |  | 分页token/Pagination token |  |
| need_format | boolean |  | 是否格式化数据/Whether to format data (default: true) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取YouTube频道的短视频(Shorts)列表
 - 支持分页获取更多短视频
  ### 参数:
 - channel_id: 频道ID（推荐，如 UCuAXFkgsw1L7xaCfnd5JJOw）
 - channel_url: 频道URL（可选，如果提供channel_id则忽略）
 - continuation_token: 分页token（可选，用于获取下一页）
 - need_format: 是否格式化数据（默认 true）
  - true: 返回格式化的结构化数据（推荐）
  - false: 返回原始的 YouTube API 结构（用于调试）
 ### 返回数据包含:
 #### 当 need_format=true 时:
 - channel_id: 频道ID
 - shorts: 短视频列表
  - video_id: 短视频的ID
  - title: 标题
  - view_count_text: 观看次数文本（如 "1.2M views"）
  - thumbnails: 缩略图列表
  - accessibility_text: 无障碍文本描述
  - video_url: 短视频链接
- continuation_token: 下一页的分页token
 - has_more: 是否还有更多短视频
 - total_count: 当前页短视频数量
  #### 当 need_format=false 时:
 - channel_id: 频道ID
 - shorts: 原始的 reelItemRenderer 对象列表
 - continuation_token: 下一页的分页token
 - has_more: 是否还有更多短视频
 - total_count: 当前页短视频数量
  ### 使用流程:
 1. 首次请求：只传 channel_id 参数
 2. 获取响应中的 continuation_token
 3. 下次请求：传入 channel_id 和 continuation_token
 4. 重复步骤 2-3 直到 has_more 为 false
  ### 注意事项:
 - 每页通常返回 30 个左右的短视频
 - ⚠️ 目前暂不支持 @username 格式，请使用频道ID（UCxxxx 格式）

## get_channel_videos

`GET /api/v1/youtube/web_v2/get_channel_videos`

<!-- Full path: /api/v1/youtube/web_v2/get_channel_videos -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| channel_id | string | ✅ | 频道ID/Channel ID | UCJHBJ7F-nAIlMGolm0Hu4vg |
| language_code | string |  | 语言代码（如zh-CN, en-US等）/Language code (default: zh-CN) | zh-CN |
| country_code | string |  | 国家代码（如US, JP等）/Country code (default: US) | US |
| continuation_token | string |  | 分页token，用于获取下一页/Pagination token for next page |  |
| need_format | boolean |  | 是否需要清洗数据，提取关键内容，移除冗余数据/Whether to clean and format the data (default: true) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取YouTube频道的视频列表
 - 支持分页获取，可通过 continuation_token 获取更多视频
  ### 参数详解:
  #### 📌 必选参数:
 **channel_id** (string)
 - **作用**: 频道ID
 - **获取方式**:
  - 从频道URL中提取，例如 `https://www.youtube.com/channel/UCJHBJ7F-nAIlMGolm0Hu4vg`
  - 或从 `@用户名` 格式的URL中，先访问频道页面获取真实的频道ID
- **示例**: `"UCJHBJ7F-nAIlMGolm0Hu4vg"`
  #### ⚙️ 可选参数:
 **language_code** (string, 可选)
 - **作用**: 设置语言偏好
 - **默认值**: `"zh-CN"`
 - **可用值**: `"zh-CN"`, `"en-US"`, `"ja-JP"`, `"ko-KR"` 等
  **country_code** (string, 可选)
 - **作用**: 设置地区代码
 - **默认值**: `"US"`
 - **可用值**: `"US"`, `"JP"`, `"GB"` 等
  **continuation_token** (string, 可选)
 - **作用**: 分页token，用于获取下一页视频
 - **获取方式**: 从上一次请求的响应中提取
 - **首次请求**: 不传此参数或传 `null`
  **need_format** (boolean, 可选)
 - **作用**: 是否返回清洗后的精简数据
 - **默认值**: `true`
 - **可用值**:
  - `false` - 返回原始完整数据
  - `true` - 返回清洗后的精简数据（推荐，默认）
 ### 返回数据结构 (need_format=true):
 ```json
 {
  "videos": [
    {
      "video_id": "zd3yCa1bJCM",
      "title": "Minecraft: DREAM! - Asleep Custom Map",
      "thumbnail": "https://i.ytimg.com/vi/zd3yCa1bJCM/hqdefault.jpg",
      "thumbnails": [
        {"url": "...", "width": 168, "height": 94},
        {"url": "...", "width": 336, "height": 188}
      ],
      "moving_thumbnail": "https://i.ytimg.com/an_webp/zd3yCa1bJCM/mqdefault_6s.webp?...",
      "duration": "16:57",
      "duration_accessibility": "16分钟57秒钟",
      "view_count": "343,369次观看",
      "short_view_count": "34万次观看",
      "published_time": "18小时前",
      "description": "Today, we're trapped in a super weird dream...",
      "is_live": false,
      "is_verified": true,
      "url": "https://www.youtube.com/watch?v=zd3yCa1bJCM",
      "playback_url": "https://rr5---sn-ogueln67.googlevideo.com/initplayback?..."
    }
  ],
  "continuation_token": "下一页token"
}
 ```
  ### 清洗后的字段说明:
 - `video_id`: 视频ID
 - `title`: 视频标题
 - `thumbnail`: 最高清晰度缩略图URL
 - `thumbnails`: 所有分辨率的缩略图列表
 - `moving_thumbnail`: 动态缩略图URL（webp格式，鼠标悬停预览）
 - `duration`: 视频时长（如"16:57"）
 - `duration_accessibility`: 时长无障碍文本（如"16分钟57秒钟"）
 - `view_count`: 完整观看次数（如"343,369次观看"）
 - `short_view_count`: 简短观看次数（如"34万次观看"）
 - `published_time`: 发布时间（如"18小时前"）
 - `description`: 视频描述片段
 - `is_live`: 是否为直播
 - `is_verified`: 频道是否已认证
 - `url`: 视频播放页URL
 - `playback_url`: 视频播放初始化URL（googlevideo.com，可能为空）
 - `continuation_token`: 下一页的分页token

## get_channel_videos_v2

`GET /api/v1/youtube/web/get_channel_videos_v2`

<!-- Full path: /api/v1/youtube/web/get_channel_videos_v2 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| channel_id | string | ✅ | 频道ID/Channel ID | UCXuqSBlHAE6Xw-yeJA0Tunw |
| lang | string |  | 视频结果语言代码/Video result language code (default: en-US) | en-US |
| sortBy | string |  | 排序方式/Sort by (default: newest) | newest |
| contentType | string |  | 内容类型/Content type (default: videos) | videos |
| nextToken | string |  | 翻页令牌/Pagination token (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取频道视频 V2，支持获取频道视频列表，频道短视频列表，频道直播列表。
  ### 参数:
 - channel_id: 频道ID或频道名称，如果是频道名称，则需要在前面加上 `@` 符号，例如：@LinusTechTips。
 - lang: 视频结果语言代码，默认为 `en-US`，任何语言代码均可，当提交不支持的语言代码时，默认使用 `en-US` 作为语言代码。
 - sortBy: 排序方式，默认为 `newest`，可选值为 `newest` 和 `oldest` 和 `mostPopular`：
    - newest: 按照最新排序，默认值。
    - oldest: 按照最旧排序。
    - mostPopular: 按照最热排序。
- contentType: 内容类型，默认为 `videos`，可选值为 `videos` 和 `shorts` 和 `live`：
    - videos: 视频列表，默认值。
    - shorts: 短视频列表。
    - live: 直播列表。
- nextToken: 用于继续获取视频的令牌。可选参数，默认值为空，从第一页开始获取。
    - 如果获取第一页，则nextToken参数为None。
    - 如果获取第二页，则nextToken参数为第一页请求返回的nextToken。
 ### 返回:
 - 频道视频列表，包含视频ID、标题、缩略图、观看次数、点赞次数、评论数、视频时长等信息。

## get_general_search

`GET /api/v1/youtube/web_v2/get_general_search`

<!-- Full path: /api/v1/youtube/web_v2/get_general_search -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| search_query | string | ✅ | 搜索关键字/Search keyword | Python编程 |
| language_code | string |  | 语言代码（如zh-CN, en-US等）/Language code (default: zh-CN) |  |
| country_code | string |  | 国家代码（如US, CN等）/Country code (default: US) |  |
| time_zone | string |  | 时区（如America/Los_Angeles, Asia/Shanghai等）/Time zone (default: America/Los_Angeles) |  |
| upload_time | string |  | 上传时间过滤 \| Upload time filter |  |
| duration | string |  | 视频时长过滤 \| Duration filter |  |
| content_type | string |  | 内容类型过滤 \| Content type filter |  |
| feature | string |  | 特征过滤 \| Feature filter |  |
| sort_by | string |  | 排序方式 \| Sort by |  |
| continuation_token | string |  | 翻页令牌/Pagination token |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### ⚠️ 推荐使用 V2 版本:
 - 本接口返回 YouTube 原始数据结构，需要自行解析
 - **清洗过的数据版本请使用 `/get_general_search_v2` 接口**，返回结构化的视频、Shorts、频道、播放列表数据
  ### 用途:
 - YouTube综合搜索，支持多种过滤条件，可以精确筛选搜索结果
  ### 参数详解:
 - **search_query**: 搜索关键字
 - **language_code**: 语言代码，推荐使用zh-CN（中文）或en-US（英文）
 - **country_code**: 国家代码，影响搜索结果的地区相关性
 - **time_zone**: 时区设置
  ### 过滤条件 (选择一个值即可):
 #### 上传时间 (upload_time):
 - `hour`: 过去1小时内上传
 - `today`: 今天上传
 - `week`: 本周上传
 - `month`: 本月上传
 - `year`: 今年上传
  #### 视频时长 (duration):
 - `short`: 短视频（少于4分钟）
 - `medium`: 中等时长（4-20分钟）
 - `long`: 长视频（超过20分钟）
  #### 内容类型 (content_type):
 - `video`: 视频
 - `channel`: 频道
 - `playlist`: 播放列表
 - `movie`: 电影
  #### 特征 (feature):
 - `hd`: 高清视频
 - `4k`: 4K视频
 - `subtitles`: 包含字幕
 - `live`: 直播
 - `creative_commons`: 知识共享许可
 - `360`: 360度视频
 - `vr180`: VR180视频
 - `3d`: 3D视频
 - `hdr`: HDR视频
 - `location`: 包含位置信息
 - `purchased`: 已购买内容
  #### 排序方式 (sort_by):
 - `relevance`: 相关性（默认）
 - `upload_date`: 上传日期
 - `view_count`: 观看次数
 - `rating`: 评分
  ### 返回:
 - 包含过滤条件的搜索结果

## get_post_detail

`GET /api/v1/youtube/web_v2/get_post_detail`

<!-- Full path: /api/v1/youtube/web_v2/get_post_detail -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| post_id | string | ✅ | 帖子ID/Post ID | UgkxiCSRfD6g7SPlWGPDa3vbP7aIsytXRkvy |
| language_code | string |  | 语言代码（如zh-CN, en-US等）/Language code (default: zh-CN) | zh-CN |
| country_code | string |  | 国家代码（如US, JP等）/Country code (default: US) | US |
| need_format | boolean |  | 是否需要清洗数据，提取关键内容，移除冗余数据/Whether to clean and format the data (default: true) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取YouTube帖子（社区帖子）的详细信息
 - 包含帖子内容、附件、互动数据等
  ### 参数详解:
  #### 必选参数:
 **post_id** (string)
 - **作用**: 帖子ID
 - **获取方式**: 从帖子URL中提取，例如
`https://www.youtube.com/post/UgkxiCSRfD6g7SPlWGPDa3vbP7aIsytXRkvy`
 - **示例**: `"UgkxiCSRfD6g7SPlWGPDa3vbP7aIsytXRkvy"`
  #### 可选参数:
 **language_code** (string, 可选) - 语言代码，默认 `"zh-CN"`
  **country_code** (string, 可选) - 国家代码，默认 `"US"`
  **need_format** (bool, 可选) - 是否格式化数据，默认 `true`
  ### 返回数据:
 #### 当 need_format=true 时:
 - post: 帖子详情
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
  - attachment: 附件数据（图片/多图/视频/投票等，可能为null）
- channel_metadata: 频道元数据（名称、描述、URL等）
 - comments_continuation_token: 评论分页token（可用于获取评论）
  #### 当 need_format=false 时:
 - 返回原始数据
  ### 注意事项:
 - post_id 以 "Ugk" 开头
 - 帖子附件支持: 图片、多图、视频、投票等类型

## get_relate_video

`GET /api/v1/youtube/web/get_relate_video`

<!-- Full path: /api/v1/youtube/web/get_relate_video -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| video_id | string | ✅ | 视频ID/Video ID | LuIL5JATZsc |
| continuation_token | string |  | 翻页令牌/Pagination token |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 根据视频ID获取推荐视频数据。
 ### 参数:
 - video_id:
视频ID，从URL中获取，例如：https://www.youtube.com/watch?v=LuIL5JATZsc，这里的video_id就是LuIL5JATZsc。
 - continuation_token: 用于继续获取推荐视频的令牌。默认为None。
 ### 返回:
 - 推荐视频数据。

## get_related_videos

`GET /api/v1/youtube/web_v2/get_related_videos`

<!-- Full path: /api/v1/youtube/web_v2/get_related_videos -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| video_id | string |  | 视频ID/Video ID | dQw4w9WgXcQ |
| video_url | string |  | 视频URL/Video URL (如果提供video_id则忽略此参数/Ignored if video_id is provided) | https://www.youtube.com/watch?v=dQw4w9WgXcQ |
| need_format | boolean |  | >- (default: true) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取YouTube视频的相似内容推荐（推荐视频列表）
 - 类似于视频播放页面右侧的相关视频
 - 一次性返回所有推荐视频（通常20-30个）
  ### 参数:
 - video_id: 视频ID（推荐）
 - video_url: 完整的视频URL（可选，如果提供video_id则忽略）
 - need_format: 是否格式化数据（默认 true）
  - true: 返回格式化的结构化数据（推荐）
  - false: 返回原始的 YouTube API 结构（用于调试或自定义解析）
 ### 返回数据包含:
 #### 当 need_format=true 时:
 - video_id: 当前视频ID
 - related_videos: 相关视频列表（格式化后的数据）
  - video_id: 相关视频的ID
  - title: 视频标题
  - author: 作者名称
  - author_id: 作者频道ID
  - author_url: 作者频道链接
  - length_text: 视频时长文本（如 "3:45"）
  - length_seconds: 视频时长（秒数）
  - view_count_text: 观看次数文本（如 "1.2M views"）
  - short_view_count_text: 简短观看次数文本（如 "1.2M"）
  - published_time_text: 发布时间文本（如 "2 days ago"）
  - thumbnails: 所有分辨率的缩略图列表
  - rich_thumbnail: 动态缩略图（如果有）
  - badges: 视频徽章（如 NEW、LIVE 等）
  - owner_badges: 作者徽章（如验证标识）
  - video_url: 视频链接
  - navigation_endpoint: 导航端点
- total_count: 推荐视频总数
  #### 当 need_format=false 时:
 - video_id: 当前视频ID
 - related_videos: 原始的 lockupViewModel 对象列表
 - total_count: 推荐视频总数
  ### 注意事项:
 - 每个视频的推荐内容由 YouTube 算法生成，可能会变化
 - 推荐列表通常包含 20-30 个视频
 - ⚠️ **此接口不支持分页**，一次性返回所有推荐视频

## get_search_suggestions

`GET /api/v1/youtube/web_v2/get_search_suggestions`

<!-- Full path: /api/v1/youtube/web_v2/get_search_suggestions -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 搜索关键词/Search keyword | Rick Astley |
| language | string |  | 语言代码/Language code (e.g., en, zh-cn, ja) (default: en) | en |
| region | string |  | 地区代码/Region code (e.g., US, SG, CN, JP) (default: US) | US |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取YouTube搜索推荐词（自动补全）
- 类似于在YouTube搜索框输入时显示的推荐词
 ### 参数:
- keyword: 搜索关键词（必填）
- language: 语言代码（可选，默认 en）
  - en: 英语
  - zh-cn: 简体中文
  - ja: 日语
  - ko: 韩语
- region: 地区代码（可选，默认 US）
  - US: 美国
  - SG: 新加坡
  - CN: 中国
  - JP: 日本
  - KR: 韩国
 ### 返回数据包含:
- keyword: 搜索关键词
- suggestions: 推荐词列表（字符串数组）
- total_count: 推荐词数量
 ### 注意事项:
- 推荐词会根据语言和地区有所不同
- 通常返回 10-20 个推荐词
- 响应速度非常快（< 1秒）

## get_shorts_search

`GET /api/v1/youtube/web_v2/get_shorts_search`

<!-- Full path: /api/v1/youtube/web_v2/get_shorts_search -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| search_query | string | ✅ | 搜索关键字/Search keyword | Python编程 |
| language_code | string |  | 语言代码（如zh-CN, en-US等）/Language code (default: en-US) | en-US |
| country_code | string |  | 国家代码（如US, CN等）/Country code (default: US) | US |
| time_zone | string |  | 时区（如America/Los_Angeles, Asia/Shanghai等）/Time zone (default: America/Los_Angeles) | America/Los_Angeles |
| upload_time | string |  | 上传时间过滤 \| Upload time filter for Shorts |  |
| sort_by | string |  | 排序方式 \| Sort by for Shorts |  |
| continuation_token | string |  | 翻页令牌/Pagination token |  |
| filter_mixed_content | boolean |  | >- (default: true) | true |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### ⚠️ 推荐使用 V2 版本:
 - 本接口返回 YouTube 原始数据结构，需要自行解析
 - **清洗过的数据版本请使用 `/get_shorts_search_v2` 接口**，返回结构化的 Shorts 列表数据，自动过滤非
Shorts 内容
  ### 用途:
 - YouTube Shorts短视频专门搜索，使用原生YouTube API接口
  ### 特点:
 - 🎬 专门搜索YouTube Shorts短视频（<60秒）
 - 🔍 支持多种过滤条件和排序方式
 - 📱 优化的移动端短视频内容
 - ⚡ 智能过滤：首次请求可能返回混合内容（长视频+短视频），默认自动过滤长视频
  ### 重要说明 - YouTube Shorts搜索机制:
 根据YouTube的搜索逻辑，Shorts搜索有以下特性：
 1. **首次请求**（无continuation_token）：可能返回混合内容（部分长视频 + 部分短视频）
 2. **后续请求**（有continuation_token）：仅返回纯短视频内容
 3. **解决方案**：
   - 方案A：使用 `filter_mixed_content=true`（默认），自动过滤掉长视频
   - 方案B：使用第一次返回的 continuation_token 进行第二次请求，获取纯Shorts内容
   - 方案C：设置 `filter_mixed_content=false`，获取原始混合内容
 ### 参数详解:
  #### 📌 必选参数 (Required Parameters):
  **search_query** (string)
 - **作用**: 搜索关键字，用于匹配Shorts视频的标题、描述等内容
 - **格式**: 任意字符串
 - **示例**: `"Python编程"`, `"gaming"`, `"cooking tutorial"`
 - **注意**: 支持中英文及其他语言，空格会被自动处理
  #### ⚙️ 可选参数 - 基础设置 (Optional Parameters - Basic Settings):
  **language_code** (string, 可选)
 - **作用**: 设置搜索结果的显示语言，影响返回内容的语言偏好
 - **默认值**: `"en-US"`
 - **可用值**:
  - `"zh-CN"` - 简体中文
  - `"zh-TW"` - 繁体中文
  - `"en-US"` - 英语（美国）
  - `"en-GB"` - 英语（英国）
  - `"ja-JP"` - 日语
  - `"ko-KR"` - 韩语
  - `"es-ES"` - 西班牙语
  - `"fr-FR"` - 法语
  - `"de-DE"` - 德语
  - 其他符合IETF BCP 47标准的语言代码
- **示例**: `language_code=zh-CN`
 - **影响**: 会影响搜索算法的语言匹配和结果排序
  **country_code** (string, 可选)
 - **作用**: 设置地区/国家代码，影响搜索结果的地域相关性和内容可用性
 - **默认值**: `"US"`
 - **可用值**:
  - `"US"` - 美国
  - `"CN"` - 中国
  - `"JP"` - 日本
  - `"KR"` - 韩国
  - `"GB"` - 英国
  - `"DE"` - 德国
  - `"FR"` - 法国
  - `"CA"` - 加拿大
  - 其他符合ISO 3166-1 alpha-2标准的国家代码
- **示例**: `country_code=JP`
 - **影响**: 某些Shorts可能因地区限制而不可见
  **time_zone** (string, 可选)
 - **作用**: 设置时区，影响时间相关过滤器（如"今天"、"本周"）的计算
 - **默认值**: `"America/Los_Angeles"`
 - **可用值**: 符合IANA时区数据库的时区标识符
  - `"America/Los_Angeles"` - 美国太平洋时区
  - `"America/New_York"` - 美国东部时区
  - `"Asia/Shanghai"` - 中国时区
  - `"Asia/Tokyo"` - 日本时区
  - `"Europe/London"` - 英国时区
  - `"Europe/Paris"` - 法国时区
- **示例**: `time_zone=Asia/Shanghai`
 - **影响**: 结合upload_time参数使用时，决定"今天"等时间段的具体范围
  **filter_mixed_content** (boolean, 可选)
 - **作用**: 控制是否自动过滤掉响应中的长视频（非Shorts内容）
 - **默认值**: `true`
 - **可用值**:
  - `true` - 自动过滤长视频，只返回Shorts（推荐）
  - `false` - 返回原始内容，可能包含长视频
- **示例**: `filter_mixed_content=true`
 - **使用场景**:
  - `true`: 当你只需要纯Shorts内容时使用（推荐首次请求使用）
  - `false`: 当你需要分析YouTube原始返回的混合内容时使用（调试用）
- **注意**: 只影响首次请求，使用continuation_token的请求本身就只返回Shorts
  #### 🎯 可选参数 - Shorts过滤条件 (Optional Parameters - Shorts Filters):
  **upload_time** (string, 可选)
 - **作用**: 按上传时间过滤Shorts，只返回指定时间段内上传的视频
 - **默认值**: `null` (不过滤)
 - **可用值**:
  - `"hour"` - 过去1小时内上传
  - `"today"` - 今天上传（基于time_zone参数）
  - `"week"` - 本周上传（最近7天）
  - `"month"` - 本月上传（最近30天）
  - `"year"` - 今年上传（最近365天）
- **示例**: `upload_time=week`
 - **使用场景**: 寻找最新、热门的Shorts内容
 - **注意**: 与time_zone参数配合使用，时间计算基于设定的时区
  **sort_by** (string, 可选)
 - **作用**: 设置搜索结果的排序方式
 - **默认值**: `null` (YouTube默认相关性排序)
 - **可用值**:
  - `"relevance"` - 按相关性排序（YouTube默认算法）
  - `"upload_date"` - 按上传日期排序（最新优先）
  - `"view_count"` - 按观看次数排序（最多观看优先）
  - `"rating"` - 按评分排序（最高评分优先）
- **示例**: `sort_by=view_count`
 - **使用场景**:
  - `relevance`: 寻找最相关的内容
  - `upload_date`: 寻找最新发布的Shorts
  - `view_count`: 寻找最受欢迎的Shorts
  - `rating`: 寻找质量最高的Shorts
- **优先级**: sort_by的优先级高于upload_time，两者同时使用时以sort_by为准
  #### 📄 可选参数 - 翻页控制 (Optional Parameters - Pagination):
  **continuation_token** (string, 可选)
 - **作用**: 用于获取下一页搜索结果的翻页令牌
 - **默认值**: `null` (获取第一页)
 - **格式**: YouTube返回的加密字符串
 - **示例**: `continuation_token=EqcBEgPkuKzor4YybhmgGk...`
 - **获取方式**: 从上一次请求的响应中提取（见"翻页机制详解"部分）
 - **使用场景**:
  - 首次搜索：不传此参数，获取第一页结果
  - 后续翻页：传入上次返回的token，获取下一页结果
- **注意**:
  - Token有时效性，通常在数小时内有效
  - 使用continuation_token时，必须保持search_query等其他参数一致
  - 使用token的请求会自动返回纯Shorts内容（无需过滤）
 ### 翻页机制详解:
 #### 如何获取 continuation_token：
 从响应JSON中提取，路径通常为以下之一：
 ```python
 # 路径1：在 onResponseReceivedCommands 中
 response["data"]["onResponseReceivedCommands"][0]["appendContinuationItemsAction"]["continuationItems"][-1]["continuationItemRenderer"]["continuationEndpoint"]["continuationCommand"]["token"]
  # 路径2：在 contents 中
 response["data"]["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"]["sectionListRenderer"]["contents"][-1]["continuationItemRenderer"]["continuationEndpoint"]["continuationCommand"]["token"]
 ```
  #### 使用流程：
 1. **首次请求**: 不传 continuation_token
   ```
   GET /api/v1/youtube_web/get_shorts_search?search_query=python
   ```
2. **提取token**: 从响应中找到 continuation_token
 3. **后续请求**: 传入 continuation_token 获取下一页
   ```
   GET /api/v1/youtube_web/get_shorts_search?search_query=python&continuation_token=xxx
   ```
 ### 响应数据结构:
 ```json
 {
  "code": 200,
  "data": {
    "contents": {
      "twoColumnSearchResultsRenderer": {
        "primaryContents": {
          "sectionListRenderer": {
            "contents": [
              {
                "itemSectionRenderer": {
                  "contents": [
                    {
                      "gridShelfViewModel": {
                        // Shorts视频列表
                        "items": [...]
                      }
                    }
                  ]
                }
              },
              {
                "continuationItemRenderer": {
                  "continuationEndpoint": {
                    "continuationCommand": {
                      "token": "xxx"  // 下一页的token
                    }
                  }
                }
              }
            ]
          }
        }
      }
    }
  }
}
 ```
  ### 返回:
 - 专门针对Shorts的搜索结果，包含视频列表和翻页token

## get_signed_stream_url

`GET /api/v1/youtube/web_v2/get_signed_stream_url`

<!-- Full path: /api/v1/youtube/web_v2/get_signed_stream_url -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| video_id | string |  | 视频ID/Video ID | dQw4w9WgXcQ |
| video_url | string |  | 视频URL/Video URL (如果提供video_id则忽略此参数/Ignored if video_id is provided) | https://www.youtube.com/watch?v=dQw4w9WgXcQ |
| itag | integer | ✅ | >- | 18 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定 itag 的已签名播放地址（可直接播放）
 - 配合 get_video_streams 接口使用，先获取所有格式，再选择 itag 获取播放地址
  ### 参数:
 - video_id: 视频ID（推荐）
 - video_url: 完整的视频URL（可选）
 - itag: 格式标识符，从 get_video_streams 接口返回的格式列表中选择
  ### 返回数据:
 - itag: 格式标识符
 - url: 已签名的播放地址（可直接使用）
 - expires_in_seconds: URL有效期（通常为6小时 = 21600秒）
  ### 注意事项:
 - 播放地址有时效性（约6小时），过期后需重新获取
 - URL 长度较长（约1000-2000字符）
 - 某些视频可能受地区限制

## get_trending_videos

`GET /api/v1/youtube/web/get_trending_videos`

<!-- Full path: /api/v1/youtube/web/get_trending_videos -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| language_code | string |  | 语言代码/Language code (default: en) |  |
| country_code | string |  | 国家代码/Country code (default: us) |  |
| section | string |  | 类型/Section (default: Now) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取趋势视频。
 ### 参数:
 - language_code: 语言代码，默认为en。
 - country_code: 国家代码，默认为us。
 - section: 类型，默认为Now，可选值为Music, Gaming, Movies。
 ### 返回:
 - 趋势视频。

## get_video_captions

`GET /api/v1/youtube/web_v2/get_video_captions`

<!-- Full path: /api/v1/youtube/web_v2/get_video_captions -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| video_id | string |  | 视频ID/Video ID | dQw4w9WgXcQ |
| video_url | string |  | 视频URL/Video URL | https://www.youtube.com/watch?v=dQw4w9WgXcQ |
| language_code | string |  | >- | en |
| format | string (srt/xml/json3/txt) |  | 字幕格式/Caption format (default: srt) | srt |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取视频的字幕列表或指定语言的字幕内容
 - 支持多种字幕格式输出
  ### 参数:
 - video_id: 视频ID（推荐）
 - video_url: 完整的视频URL（可选）
 - language_code: 语言代码（如 en, zh-Hans, a.en），为空时返回可用字幕列表
 - format: 字幕格式
  - srt: SubRip 字幕格式（带时间轴）
  - xml: 原始 XML 格式
  - json3: JSON 格式（YouTube 原始结构）
  - txt: 纯文本（无时间轴）
 ### 使用流程:
 1. 不传 language_code，获取字幕列表
 2. 从列表中选择 language_code，获取字幕内容
  ### 返回数据:
 #### 不传 language_code 时（字幕列表）:
 ```json
 {
  "captions": [
    {
      "language_code": "en",
      "language_name": "English",
      "kind": "",
      "is_translatable": true,
      "base_url": "xxxx"
    },
    {
      "language_code": "a.en",
      "language_name": "English (auto-generated)",
      "kind": "asr",
      "is_translatable": true,
      "base_url": "xxxx"
    }
  ]
}
 ```
  #### 传 language_code 时（字幕内容）:
 - format=srt: 标准 SRT 字幕文件内容（含序号、时间轴、文本）
 - format=txt: 纯文本（仅文字，无时间轴）
 - format=xml: YouTube 原始 XML 字幕
 - format=json3: YouTube JSON 格式字幕
  ### 注意事项:
 - kind 为 "asr" 表示自动生成的字幕
 - 并非所有视频都有字幕
 - video_id 和 video_url 至少提供一个

## get_video_captions_v2

`GET /api/v1/youtube/web_v2/get_video_captions_v2`

<!-- Full path: /api/v1/youtube/web_v2/get_video_captions_v2 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| video_id | string |  | 视频ID/Video ID | MWvpXswLFxA |
| video_url | string |  | 视频URL/Video URL | https://www.youtube.com/watch?v=MWvpXswLFxA |
| language_code | string |  | >- | en |
| format | string (srt/xml/json3/txt) |  | 字幕格式/Caption format (default: srt) | srt |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取视频的字幕列表或指定语言的字幕内容（V2 实现）
 - V2 为字幕接口的备用实现，对部分 `get_video_captions` 取不到字幕的视频有更好的覆盖
 - 支持多种字幕格式输出
  ### 参数:
 - video_id: 视频ID（推荐）
 - video_url: 完整的视频URL（可选）
 - language_code: 语言代码（如 en, zh-Hans, a.en），为空时返回可用字幕列表
 - format: 字幕格式
  - srt: SubRip 字幕格式（带时间轴）
  - xml: 原始 XML 格式
  - json3: JSON 格式（YouTube 原始结构）
  - txt: 纯文本（无时间轴）
 ### 使用流程:
 1. 不传 language_code，获取字幕列表
 2. 从列表中选择 language_code，获取字幕内容
  ### 注意事项:
 - kind 为 "asr" 表示自动生成的字幕
 - 并非所有视频都有字幕
 - video_id 和 video_url 至少提供一个
 - 若 `get_video_captions` 返回空字幕列表，可改用本接口重试

## get_video_comment_replies

`GET /api/v1/youtube/web_v2/get_video_comment_replies`

<!-- Full path: /api/v1/youtube/web_v2/get_video_comment_replies -->

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
 - 获取视频二级评论
  ### 参数详解:
  #### 📌 必选参数:
 **continuation_token** (string)
 - **作用**: 回复的continuation token
 - **获取方式**: 从一级评论的响应数据中获取 `reply_continuation_token` 字段
 - **示例**:
`"Eg0SC29hU05CejRxTVFZGAYygwEaUBIaVWd3WmhjUXVGUmJZTlhkUV85VjRBYUFCQWciAggAKhhVQ0pIQko3Ri1uQUlsTUdvbG0wSHU0dmcyC29hU05CejRxTVFZQAFICoIBAggBQi9jb21tZW50LXJlcGxpZXMtaXRlbS1VZ3daaGNRdUZSYllOWGRRXzlWNEFhQUJBZw%3D%3D"`
  #### ⚙️ 可选参数:
 **language_code** (string, 可选)
 - **作用**: 设置回复显示的语言偏好
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
 ### 使用流程:
 1. 先调用 `/get_video_comments` 接口获取一级评论
 2. 从一级评论的响应中找到 `reply_continuation_token` 字段
 3. 使用该 token 调用本接口获取该评论的所有回复
  ### 返回数据结构 (need_format=true):
 ```json
 {
  "comments": [
    {
      "comment_id": "UgwZhcQuFRbYNXdQ_9V4AaABAg.A2B3C4D5E6F7G8H9I0J1",
      "content": "回复内容文本",
      "published_time": "2天前",
      "reply_level": 1,
      "like_count": "5",
      "like_count_a11y": "5 次赞",
      "reply_count": "0",
      "author": {
        "channel_id": "UCxxxxxx",
        "display_name": "@username",
        "channel_url": "https://www.youtube.com/@username",
        "avatar_url": "https://yt3.ggpht.com/...",
        "is_verified": false,
        "is_creator": true,
        "is_artist": false
      }
    }
  ],
  "continuation_token": "下一页token（如果有更多回复）"
}
 ```
  ### 字段说明:
 - `reply_level`: 回复层级（1表示二级评论/回复）
 - `is_creator`: 是否为视频创作者（如果是创作者回复会标记为true）
 - 其他字段与一级评论相同

## get_video_comments

`GET /api/v1/youtube/web_v2/get_video_comments`

<!-- Full path: /api/v1/youtube/web_v2/get_video_comments -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| video_id | string | ✅ | 视频ID/Video ID | LuIL5JATZsc |
| language_code | string |  | 语言代码（如zh-CN, en-US等）/Language code (default: zh-CN) | zh-CN |
| country_code | string |  | 国家代码（如US, JP等）/Country code (default: US) | US |
| sort_by | string |  | 排序方式 \| Sort by (default: top) |  |
| continuation_token | string |  | 翻页令牌/Pagination token |  |
| need_format | boolean |  | 是否需要清洗数据，提取关键内容，移除冗余数据/Whether to clean and format the data (default: true) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取YouTube视频的一级评论
  ### 参数详解:
  #### 📌 必选参数:
 **video_id** (string)
 - **作用**: 视频ID
 - **格式**: YouTube视频ID字符串
 - **示例**: `"oaSNBz4qMQY"`
 - **获取方式**: 从URL `https://www.youtube.com/watch?v=oaSNBz4qMQY` 中提取
  #### ⚙️ 可选参数:
 **language_code** (string, 可选)
 - **作用**: 设置评论显示的语言偏好
 - **默认值**: `"zh-CN"`
 - **可用值**: `"zh-CN"`, `"en-US"`, `"ja-JP"`, `"ko-KR"` 等
  **country_code** (string, 可选)
 - **作用**: 设置地区代码
 - **默认值**: `"US"`
 - **可用值**: `"US"`, `"JP"`, `"GB"` 等
  **sort_by** (string, 可选)
 - **作用**: 评论排序方式
 - **默认值**: `"top"`
 - **可用值**:
  - `"top"` - 热门评论（按点赞数排序）
  - `"newest"` - 最新评论（按时间排序）
 **continuation_token** (string, 可选)
 - **作用**: 翻页令牌，用于获取下一页评论
 - **默认值**: `null`
 - **获取方式**: 从上一次请求的响应中提取
  **need_format** (boolean, 可选)
 - **作用**: 是否返回清洗后的精简数据
 - **默认值**: `true`
 - **可用值**:
  - `false` - 返回原始完整数据
  - `true` - 返回清洗后的精简数据（推荐，默认）
 ### 返回数据结构 (need_format=true):
 ```json
 {
  "comments": [
    {
      "comment_id": "UgzRDoUJAvDNn5_8i8p4AaABAg",
      "content": "评论内容文本",
      "published_time": "1天前",
      "reply_level": 0,
      "like_count": "2",
      "like_count_a11y": "2 次赞",
      "reply_count": "0",
      "reply_count_a11y": "0 条回复",
      "reply_count_text": "1 条回复",
      "reply_continuation_token": "...",
      "author": {
        "channel_id": "UCzRzHrLFuH0lHZYnrI84I8Q",
        "display_name": "@username",
        "channel_url": "https://www.youtube.com/@username",
        "avatar_url": "https://yt3.ggpht.com/...",
        "avatar_thumbnails": [
          {"url": "...", "width": 88, "height": 88}
        ],
        "is_verified": false,
        "is_creator": false,
        "is_artist": false
      },
      "creator_thumbnail_url": "https://yt3.ggpht.com/..."
    }
  ],
  "continuation_token": "下一页token"
}
 ```
  ### 字段说明:
 - `comment_id`: 评论唯一ID
 - `content`: 评论文本内容
 - `published_time`: 发布时间（相对时间，如"1天前"）
 - `reply_level`: 回复层级（0表示一级评论）
 - `like_count`: 点赞数
 - `reply_count`: 回复数
 - `reply_count_text`: 回复数文本（如"1 条回复"）
 - `reply_continuation_token`: 获取该评论回复的token
 - `author`: 评论作者信息
  - `channel_id`: 作者频道ID
  - `display_name`: 显示名称
  - `channel_url`: 频道URL
  - `avatar_url`: 头像URL
  - `is_verified`: 是否已认证
  - `is_creator`: 是否为视频创作者
  - `is_artist`: 是否为音乐人
- `creator_thumbnail_url`: 视频创作者头像URL

## get_video_info

`GET /api/v1/youtube/web/get_video_info`

<!-- Full path: /api/v1/youtube/web/get_video_info -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| video_id | string | ✅ | 视频ID/Video ID | LuIL5JATZsc |
| url_access | string |  | URL访问模式：normal（包含音视频URL）\| blocked（不包含音视频URL） / URL access mode (default: normal) |  |
| lang | string |  | 语言代码（IETF标签），默认en-US / Language code (default: en-US) | zh-CN |
| videos | string |  | >- (default: auto) |  |
| audios | string |  | >- |  |
| subtitles | boolean |  | 是否获取字幕 / Include subtitles (default: true) |  |
| related | boolean |  | 是否获取相关视频 / Include related content (default: true) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取视频元数据及下载信息
 ### 详细参数:
 - url_access:
    - normal: 包含音视频直链
    - blocked: 不包含直链
- videos/audios:
    - auto: 根据url_access自动选择（normal→true，blocked→false）
    - true: 返回简化格式信息
    - raw: 返回原始格式信息
    - false: 不包含该类型数据
### 返回:
 - 视频元数据 + 请求参数对应的资源信息

## get_video_info

`GET /api/v1/youtube/web/get_video_info`

<!-- Full path: /api/v1/youtube/web_v2/get_video_info -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| video_id | string | ✅ | 视频ID/Video ID | oaSNBz4qMQY |
| language_code | string |  | 语言代码（如zh-CN, en-US等）/Language code (default: zh-CN) | zh-CN |
| need_format | boolean |  | 是否需要清洗数据，提取关键内容，移除冗余数据/Whether to clean and format the data (default: true) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取YouTube视频详情信息
 - 返回原始完整数据（包含 playerResponse 和 initialData）
  ### 参数详解:
  #### 📌 必选参数:
 **video_id** (string)
 - **作用**: 视频ID
 - **获取方式**: 从视频URL中提取，例如
`https://www.youtube.com/watch?v=oaSNBz4qMQY`，video_id 就是 `oaSNBz4qMQY`
 - **示例**: `"oaSNBz4qMQY"`
  #### ⚙️ 可选参数:
 **language_code** (string, 可选)
 - **作用**: 设置语言偏好
 - **默认值**: `"zh-CN"`
 - **可用值**: `"zh-CN"`, `"en-US"`, `"ja-JP"`, `"ko-KR"` 等
  ### 返回数据结构:
 ```json
 {
  "playerResponse": {
    "videoDetails": {},
    "streamingData": {
      "formats": [],
      "adaptiveFormats": []
    },
    "microformat": {},
    ...
  },
  "initialData": {
    "contents": {
      "twoColumnWatchNextResults": {
        "results": {
          "results": {
            "contents": [
              {
                "videoPrimaryInfoRenderer": {...},
                "videoSecondaryInfoRenderer": {...}
              }
            ]
          }
        }
      }
    },
    ...
  }
}
 ```
  ### 主要字段说明:
 - `playerResponse`: YouTube 播放器响应数据
  - `videoDetails`: 视频基本信息（可能为空，取决于YouTube的返回）
  - `streamingData`: 视频流数据（包含 formats 和 adaptiveFormats，包含 googlevideo.com 的URL）
  - `microformat`: 元数据信息
- `initialData`: YouTube 页面初始化数据
  - `videoPrimaryInfoRenderer`: 主要信息（标题、观看次数、点赞数等）
  - `videoSecondaryInfoRenderer`: 次要信息（频道信息、描述等）

## get_video_info_v2

`GET /api/v1/youtube/web/get_video_info_v2`

<!-- Full path: /api/v1/youtube/web/get_video_info_v2 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| video_id | string | ✅ | 视频ID/Video ID | LuIL5JATZsc |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取视频元数据及下载信息
 ### 参数:
 - video_id:
视频ID，从URL中获取，例如：https://www.youtube.com/watch?v=LuIL5JATZsc，这里的video_id就是LuIL5JATZsc。
 ### 返回:
 - 视频元数据 + 请求参数对应的资源信息

## get_video_streams

`GET /api/v1/youtube/web_v2/get_video_streams`

<!-- Full path: /api/v1/youtube/web_v2/get_video_streams -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| video_id | string |  | 视频ID/Video ID | dQw4w9WgXcQ |
| video_url | string |  | 视频URL/Video URL (如果提供video_id则忽略此参数/Ignored if video_id is provided) | https://www.youtube.com/watch?v=dQw4w9WgXcQ |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### ⚠️ 重要说明:
 - **此接口仅返回格式信息，URL 字段为 null**
 - **必须搭配 get_signed_stream_url 接口获取播放地址**
 - 如需一次性获取所有 URL，请使用 get_video_streams_v2 接口
  ### 用途:
 - 获取YouTube视频所有清晰度的格式信息
 - 返回标准格式（音视频合并）和自适应格式（音视频分离）
  ### 参数:
 - video_id: 视频ID（推荐）
 - video_url: 完整的视频URL（可选，如果提供video_id则忽略）
  ### 返回数据包含:
 - 视频基本信息（标题、作者、时长、观看次数等）
 - formats: 标准格式流（包含音频和视频）
 - adaptive_formats: 自适应格式流（仅视频或仅音频）
  - 每个格式包含: itag、mime_type、质量标签、分辨率、比特率等
  - ⚠️ **url 字段为 null**（YouTube 需要签名解密才能获取真实播放地址）
  - has_signature 为 true 表示需要使用 get_signed_stream_url 接口
- hls_manifest_url: HLS流地址（如果有）
 - dash_manifest_url: DASH流地址（如果有）
 - available_qualities: 所有可用的清晰度列表
  ### 使用流程（两步法）:
 1. **第一步**: 调用此接口获取所有可用格式信息（URL 为 null）
 2. **第二步**: 从返回的 formats 或 adaptive_formats 中选择需要的 itag
 3. **第三步**: 调用 get_signed_stream_url 接口，传入 video_id 和 itag，获取真实播放地址
  ### 注意事项:
 - YouTube 视频播放地址需要签名解密，原始 API 返回的 URL 字段为 null 是正常现象
 - 播放地址必须通过 get_signed_stream_url 接口单独获取
 - 高清视频（720p+）通常需要分别下载音视频流并合并

## get_video_streams_v2

`GET /api/v1/youtube/web_v2/get_video_streams_v2`

<!-- Full path: /api/v1/youtube/web_v2/get_video_streams_v2 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| video_id | string |  | 视频ID/Video ID | dQw4w9WgXcQ |
| video_url | string |  | 视频URL/Video URL (如果提供video_id则忽略此参数/Ignored if video_id is provided) | https://www.youtube.com/watch?v=dQw4w9WgXcQ |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### ✅ 特性:
 - **自动返回所有格式的已解密播放地址**
 - 无需额外调用 get_signed_stream_url 接口
 - 一次性获取所有清晰度的可用链接
  ### 用途:
 - 获取YouTube视频所有清晰度的格式信息和播放地址
 - 返回标准格式（音视频合并）和自适应格式（音视频分离）
 - 适合需要展示所有清晰度选项的场景
  ### 参数:
 - video_id: 视频ID（推荐）
 - video_url: 完整的视频URL（可选，如果提供video_id则忽略）
  ### 返回数据包含:
 - 视频基本信息（标题、作者、时长、观看次数等）
 - formats: 标准格式流（包含音频和视频）
 - adaptive_formats: 自适应格式流（仅视频或仅音频）
  - 每个格式包含: itag、mime_type、质量标签、分辨率、比特率等
  - ✅ **url 字段包含已解密的播放地址，可直接使用**
  - has_signature 为 false 表示 URL 已解密，可直接播放
- hls_manifest_url: HLS流地址（如果有）
 - dash_manifest_url: DASH流地址（如果有）
 - available_qualities: 所有可用的清晰度列表
 - expires_in_seconds: URL 过期时间（约 6 小时 = 21600 秒）
  ### 与 get_video_streams 的区别:
 - **get_video_streams**: URL 为 null，需要搭配 get_signed_stream_url 使用（两步法）
 - **get_video_streams_v2 (本接口)**: 自动返回所有已解密的 URL（一步到位）
  ### 注意事项:
 - 播放地址有时效性（约6小时），建议获取后尽快使用
 - 高清视频（720p+）通常需要分别下载音视频流并合并
 - 响应时间较长（约10秒），因为需要为所有格式解密 URL

## get_video_subtitles

`GET /api/v1/youtube/web/get_video_subtitles`

<!-- Full path: /api/v1/youtube/web/get_video_subtitles -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| subtitle_url | string | ✅ | 字幕URL（需先调用获取视频详情接口） / Subtitle URL from video details | https://www.youtube.com/api/timedtext?v=... |
| format | string |  | 字幕格式：srt/xml/vtt/txt / Subtitle format (default: srt) |  |
| fix_overlap | boolean |  | 修复重叠字幕（默认开启） / Fix overlapping subtitles (default: true) |  |
| target_lang | string |  | 目标语言代码（留空保持原语言） / Target language code | zh-CN |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取视频字幕内容
 ### 使用流程:
 1. 先调用获取视频详情接口，从字幕数据中获取subtitleUrl
 2. 使用该URL作为本接口参数
 ### 参数说明:
 - fix_overlap: 特别适用于自动生成的字幕，会自动分割重叠的时间段

## search_video

`GET /api/v1/youtube/web/search_video`

<!-- Full path: /api/v1/youtube/web/search_video -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| search_query | string | ✅ | 搜索关键字/Search keyword | Minecraft |
| language_code | string |  | 语言代码/Language code (default: en) |  |
| order_by | string |  | 排序方式/Order by (default: this_month) |  |
| country_code | string |  | 国家代码/Country code (default: us) |  |
| continuation_token | string |  | 翻页令牌/Pagination token |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 搜索视频。
 ### 参数:
 - search_query: 搜索关键字。
 - language_code: 语言代码，默认为en。
 - order_by: 排序方式，默认为this_month，可选值为this_week, this_month, this_year,
last_hour, today。
 - country_code: 国家代码，默认为us。
 - continuation_token: 用于继续获取搜索结果的令牌。默认为None。
 ### 返回:
 - 搜索结果。

---

See SKILL.md for cross-group orchestration patterns.