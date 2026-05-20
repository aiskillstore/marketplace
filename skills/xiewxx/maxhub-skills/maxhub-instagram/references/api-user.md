# User Data API / 用户数据接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---
## fetch_location_info

`GET /api/v1/instagram/v1/fetch_location_info`

<!-- Full path: /api/v1/instagram/v1/fetch_location_info -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| location_id | string | ✅ | 地点ID/Location ID | 703457703 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定地点的详细信息
 ### 参数:
 - location_id: 地点ID
 ### 返回:
 - `location_info`: 地点信息，包含名称、地址、坐标等

## fetch_related_profiles

`GET /api/v1/instagram/v1/fetch_related_profiles`

<!-- Full path: /api/v1/instagram/v1/fetch_related_profiles -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string | ✅ | Instagram用户ID/Instagram user ID | 25025320 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取与指定用户相关/相似的用户推荐列表
### 参数:
- user_id: Instagram用户ID
### 返回:
- GraphQL风格响应，包含`data.user.edge_related_profiles`

## fetch_search

`GET /api/v1/instagram/v1/fetch_search`

<!-- Full path: /api/v1/instagram/v1/fetch_search -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| query | string | ✅ | 搜索关键词/Search keyword | taylorswift |
| select | string |  | >- |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 根据关键词搜索Instagram上的用户、话题标签或地点
### 参数:
- query: 搜索关键词
- select: 筛选类型（可选）
  - `users`: 仅返回用户
  - `hashtags`: 仅返回话题标签
  - `places`: 仅返回地点
  - 不传: 返回所有类型
### 返回:
- `users`: 用户列表
- `hashtags`: 话题列表
- `places`: 地点列表

## fetch_similar_users

`GET /api/v1/instagram/v2/fetch_similar_users`

<!-- Full path: /api/v1/instagram/v2/fetch_similar_users -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| username | string |  | 用户名/Username | instagram |
| user_id | string |  | 用户ID/User ID | 18527 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取与指定用户相似的用户推荐列表
- 基于Instagram的推荐算法
### 参数:
- username: 用户名（与user_id二选一）
- user_id: 用户ID（与username二选一）
### 返回:
- `data.items`: 相似用户列表

## fetch_user_followers

`GET /api/v1/instagram/v2/fetch_user_followers`

<!-- Full path: /api/v1/instagram/v2/fetch_user_followers -->

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
- 获取Instagram用户的粉丝列表
- 支持分页获取
### 参数:
- username: 用户名（与user_id二选一）
- user_id: 用户ID（与username二选一）
- pagination_token: 分页token，从上一次响应获取
### 返回:
- `data.items`: 粉丝列表
- `pagination_token`: 下一页token

## fetch_user_following

`GET /api/v1/instagram/v2/fetch_user_following`

<!-- Full path: /api/v1/instagram/v2/fetch_user_following -->

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
- 获取Instagram用户关注的用户列表
- 支持分页获取
### 参数:
- username: 用户名（与user_id二选一）
- user_id: 用户ID（与username二选一）
- pagination_token: 分页token，从上一次响应获取
### 返回:
- `data.items`: 关注列表
- `pagination_token`: 下一页token

## fetch_user_highlights

`GET /api/v1/instagram/v2/fetch_user_highlights`

<!-- Full path: /api/v1/instagram/v2/fetch_user_highlights -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| username | string |  | 用户名/Username | instagram |
| user_id | string |  | 用户ID/User ID | 18527 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取Instagram用户的精选故事（Highlights）列表
- 精选是用户保存的故事合集
### 参数:
- username: 用户名（与user_id二选一）
- user_id: 用户ID（与username二选一）
### 返回:
- `data.items`: 精选列表，包含精选ID、标题、封面等

## fetch_user_info

`GET /api/v1/instagram/v2/fetch_user_info`

<!-- Full path: /api/v1/instagram/v2/fetch_user_info -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| username | string |  | 用户名/Username | instagram |
| user_id | string |  | 用户ID/User ID | 18527 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取Instagram用户的详细信息
 - 支持通过用户名或用户ID查询
 ### 参数:
 - username: 用户名（与user_id二选一）
 - user_id: 用户ID（与username二选一）
 ### 返回:
 - `data`: 用户信息，包含用户名、头像、简介、粉丝数、关注数、帖子数等
 - 此接口会返回用户的关于信息，包括国家，加入时间，是否认证等信息。

## fetch_user_info_by_id

`GET /api/v1/instagram/v1/fetch_user_info_by_id`

<!-- Full path: /api/v1/instagram/v1/fetch_user_info_by_id -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string | ✅ | Instagram用户ID/Instagram user ID | 25025320 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 根据Instagram用户ID获取用户数据
 ### 参数:
 - user_id: Instagram用户ID
 ### 返回:
 - 用户信息对象，包含时间线媒体、高清头像等完整数据

## fetch_user_reels

`GET /api/v1/instagram/v1/fetch_user_reels`

<!-- Full path: /api/v1/instagram/v1/fetch_user_reels -->

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
- 获取用户Reels短视频列表，支持分页
### 参数:
- user_id: Instagram用户ID
- count: 每页数量，默认12
- max_id: 分页游标，首次请求不传
### 返回:
- `items`: Reels列表
- `paging_info`: 分页信息

## fetch_user_reels

`GET /api/v1/instagram/v1/fetch_user_reels`

<!-- Full path: /api/v1/instagram/v2/fetch_user_reels -->

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
- 获取Instagram用户发布的Reels短视频列表
- 支持分页获取
### 参数:
- username: 用户名（与user_id二选一）
- user_id: 用户ID（与username二选一）
- pagination_token: 分页token，从上一次响应获取
### 返回:
- `data.items`: Reels列表
- `pagination_token`: 下一页token

## fetch_user_stories

`GET /api/v1/instagram/v2/fetch_user_stories`

<!-- Full path: /api/v1/instagram/v2/fetch_user_stories -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| username | string |  | 用户名/Username | instagram |
| user_id | string |  | 用户ID/User ID | 18527 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取Instagram用户当前发布的故事（Stories）
 - 故事在24小时后过期
 ### 参数:
 - username: 用户名（与user_id二选一）
 - user_id: 用户ID（与username二选一）
 ### 返回:
 - `data.items`: 故事列表，包含图片/视频URL、发布时间等

## get_recommended_reels

`GET /api/v1/instagram/v3/get_recommended_reels`

<!-- Full path: /api/v1/instagram/v3/get_recommended_reels -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| first | integer |  | 获取数量/Number of reels to fetch (default: 12) |  |
| after | string |  | >- |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取Instagram Reels推荐列表
 - 支持分页获取更多Reels
 ### 参数:
 - first: 每次获取的Reels数量（默认12，最大50）
 - after: 分页游标，首次请求不传，从上一次响应的 `data.page_info.end_cursor` 获取
 ### 返回:
 - `data.edges`: Reels列表
    - `node.media`: Reels媒体信息
        - `code`: 帖子短代码
        - `pk`: 帖子ID
        - `like_count`: 点赞数
        - `comment_count`: 评论数
        - `play_count`: 播放数
        - `caption.text`: 描述文本
        - `user`: 发布者信息
        - `video_versions`: 视频版本列表
        - `image_versions2`: 封面图版本列表
- `data.page_info`: 分页信息
    - `has_next_page`: 是否有下一页
    - `end_cursor`: 下一页游标（传给下次请求的after参数）
### 分页使用方法:
 1. 首次请求：只传 `first` 参数
 2. 获取响应中的 `data.page_info.end_cursor`
 3. 下次请求：传入 `first` 和 `after` (使用上次的end_cursor)
 4. 重复步骤 2-3 直到 `data.page_info.has_next_page` 为 false

## get_user_about

`GET /api/v1/instagram/v3/get_user_about`

<!-- Full path: /api/v1/instagram/v3/get_user_about -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string |  | 用户ID/User ID | 791258468 |
| username | string |  | 用户名（与user_id二选一）/Username (alternative to user_id) | instagram |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取Instagram用户的账户简介信息（About This Account）
 - 包含账户创建日期、所在地区、曾用名等信息
 ### 参数:
 - user_id: Instagram用户ID（数字，与username二选一）
 - username: Instagram用户名（与user_id二选一，传入后会自动转换为user_id）
 ### 返回:
 - 账户创建日期
 - 账户所在地区/国家
 - 曾用名历史
 - 其他账户相关信息

## get_user_former_usernames

`GET /api/v1/instagram/v3/get_user_former_usernames`

<!-- Full path: /api/v1/instagram/v3/get_user_former_usernames -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string |  | 用户ID/User ID | 17841403122371231 |
| username | string |  | 用户名（与user_id二选一）/Username (alternative to user_id) | instagram |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取Instagram用户的曾用用户名历史
 ### 参数:
 - user_id: Instagram用户ID（数字，与username二选一）
 - username: Instagram用户名（与user_id二选一，传入后会自动转换为user_id）
 ### 返回:
 - 曾用用户名列表及更改时间
 ### 注意:
 - 如果用户没有曾用名，也会正常返回空数据并扣费

## get_user_highlights

`GET /api/v1/instagram/v3/get_user_highlights`

<!-- Full path: /api/v1/instagram/v3/get_user_highlights -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string |  | 用户ID/User ID | 58208242181 |
| username | string |  | 用户名（与user_id二选一）/Username (alternative to user_id) | instagram |
| first | integer |  | 每页数量/Number of highlights per page (default: 10) |  |
| after | string |  | 向后翻页游标/Forward pagination cursor |  |
| before | string |  | 向前翻页游标/Backward pagination cursor |  |
| last | integer |  | 向前翻页时每页数量/Number of highlights per page (backward) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取Instagram用户的精选Highlights列表
 - 返回用户创建的所有精选集合
 - 支持分页获取
 ### 参数:
 - user_id: Instagram用户ID（数字，与username二选一）
 - username: Instagram用户名（与user_id二选一，传入后会自动转换为user_id）
 - first: 每页精选数量（默认10，最大50）
 - after: 向后翻页游标，从上一次响应的 `data.page_info.end_cursor` 获取
 - before: 向前翻页游标，从上一次响应的 `data.page_info.start_cursor` 获取
 - last: 向前翻页时每页数量，配合 `before` 使用
 ### 返回:
 - `data.edges`: 精选列表
    - `node.id`: 精选ID（格式: highlight:xxx）
    - `node.title`: 精选标题
    - `node.cover_media`: 封面媒体信息
    - `node.cover_media_cropped_thumbnail`: 裁剪后的封面缩略图
    - `node.media_count`: 精选中的故事数量
- `data.page_info`: 分页信息
    - `has_next_page`: 是否有下一页
    - `end_cursor`: 下一页游标（传给下次请求的after参数）
### 分页使用方法:
 1. 首次请求：只传 `user_id` 和 `first` 参数
 2. 获取响应中的 `data.page_info.end_cursor`
 3. 下次请求：传入 `user_id`、`first` 和 `after` (使用上次的end_cursor)
 4. 重复步骤 2-3 直到 `data.page_info.has_next_page` 为 false

## get_user_id_by_username

`GET /api/v1/instagram/v3/get_user_id_by_username`

<!-- Full path: /api/v1/instagram/v3/get_user_id_by_username -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| username | string | ✅ | 用户名/Username | liensue.talks |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 通过Instagram用户名获取用户ID
 - 用户ID是Instagram内部使用的唯一标识符，通常为数字字符串
 ### 参数:
 - username: Instagram用户名
 ### 返回:
 - `data.user_id`: 用户ID

## get_user_profile

`GET /api/v1/instagram/v3/get_user_profile`

<!-- Full path: /api/v1/instagram/v3/get_user_profile -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string |  | 用户ID/User ID | 58208242181 |
| username | string |  | 用户名（与user_id二选一）/Username (alternative to user_id) | instagram |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取Instagram用户的完整个人资料信息
 - 包含用户基本信息、统计数据、最近帖子等
 ### 参数:
 - user_id: Instagram用户ID（数字，与username二选一）
 - username: Instagram用户名（与user_id二选一，传入后会自动转换为user_id）
  ### 返回:
 - `data.user.id`: 用户ID
 - `data.user.username`: 用户名
 - `data.user.full_name`: 全名
 - `data.user.biography`: 个人简介
 - `data.user.external_url`: 外部链接
 - `data.user.profile_pic_url`: 头像URL（标准）
 - `data.user.profile_pic_url_hd`: 头像URL（高清）
 - `data.user.is_verified`: 是否认证
 - `data.user.is_private`: 是否私密账号
 - `data.user.edge_followed_by.count`: 粉丝数
 - `data.user.edge_follow.count`: 关注数
 - `data.user.edge_owner_to_timeline_media.count`: 帖子总数
 - `data.user.edge_felix_video_timeline.count`: Reels/视频数

## get_user_reels

`GET /api/v1/instagram/v3/get_user_reels`

<!-- Full path: /api/v1/instagram/v3/get_user_reels -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string |  | 用户ID/User ID | 58208242181 |
| username | string |  | 用户名（与user_id二选一）/Username (alternative to user_id) | instagram |
| first | integer |  | 向后翻页时每页数量/Number of reels per page (forward) (default: 12) |  |
| after | string |  | 向后翻页游标（end_cursor）/Forward pagination cursor (end_cursor) |  |
| before | string |  | 向前翻页游标（start_cursor）/Backward pagination cursor (start_cursor) |  |
| last | integer |  | 向前翻页时每页数量/Number of reels per page (backward) |  |
| page_size | integer |  | 每页视频数量/Videos per page (default: 12) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取Instagram用户的Reels列表
 - 支持分页获取用户发布的所有Reels
 ### 参数:
 - user_id: Instagram用户ID（数字，与username二选一）
 - username: Instagram用户名（与user_id二选一，传入后会自动转换为user_id）
 - first: 向后翻页时每页数量（默认12，最大50）
 - after: 向后翻页游标，从上一次响应的 `data.page_info.end_cursor` 获取
 - before: 向前翻页游标，从上一次响应的 `data.page_info.start_cursor` 获取
 - last: 向前翻页时每页数量，配合 `before` 使用
 - page_size: 每页视频数量（默认12）
 ### 返回:
 - `data.edges`: Reels列表
    - `node.media`: Reels媒体信息
        - `code`: 帖子短代码
        - `pk`: 帖子ID
        - `like_count`: 点赞数
        - `comment_count`: 评论数
        - `play_count`: 播放数
        - `caption.text`: 描述文本
        - `user`: 发布者信息
        - `video_versions`: 视频版本列表
        - `image_versions2`: 封面图版本列表
- `data.page_info`: 分页信息
    - `has_next_page`: 是否有下一页
    - `end_cursor`: 下一页游标（传给下次请求的after参数）
### 分页使用方法:
 1. 首次请求：只传 `user_id` 和 `first` 参数
 2. 获取响应中的 `data.page_info.end_cursor`
 3. 下次请求：传入 `user_id`、`first` 和 `after` (使用上次的end_cursor)
 4. 重复步骤 2-3 直到 `data.page_info.has_next_page` 为 false

## get_user_stories

`GET /api/v1/instagram/v3/get_user_stories`

<!-- Full path: /api/v1/instagram/v3/get_user_stories -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string |  | 用户ID/User ID | 58208242181 |
| username | string |  | 用户名（与user_id二选一）/Username (alternative to user_id) | instagram |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取Instagram用户的Stories（快拍）列表
 - 即点击用户头像后展示的24小时内发布的快拍内容
 ### 参数:
 - user_id: Instagram用户ID（数字，与username二选一）
 - username: Instagram用户名（与user_id二选一，传入后会自动转换为user_id）
 ### 返回:
 - `data.reels_media`: Stories列表（按用户分组）
    - `id`: 用户ID
    - `user`: 用户信息
        - `username`: 用户名
        - `full_name`: 全名
        - `profile_pic_url`: 头像URL
    - `items`: Stories条目列表
        - `id`: Story ID
        - `pk`: Story PK
        - `taken_at`: 发布时间戳
        - `media_type`: 媒体类型（1=图片, 2=视频）
        - `image_versions2`: 图片版本列表
        - `video_versions`: 视频版本列表（视频时存在）
        - `story_cta`: Story链接（如果有）
- `data.reels`: Stories详细信息
 ### 注意:
 - Stories有24小时有效期，过期后无法获取
 - 私密账号的Stories需要关注后才能查看

## search_reels

`GET /api/v1/instagram/v2/search_reels`

<!-- Full path: /api/v1/instagram/v2/search_reels -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 搜索关键词/Search keyword | cat |
| pagination_token | string |  | 分页token/Pagination token |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 根据关键词搜索Instagram Reels短视频
- 支持分页获取
### 参数:
- keyword: 搜索关键词
- pagination_token: 分页token，从上一次响应获取
### 返回:
- `data.items`: Reels列表
- `pagination_token`: 下一页token

## search_users

`GET /api/v1/instagram/v2/search_users`

<!-- Full path: /api/v1/instagram/v2/search_users -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 搜索关键词/Search keyword | instagram |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 根据关键词搜索Instagram用户
### 参数:
- keyword: 搜索关键词
### 返回:
- `data.items`: 用户列表

## search_users

`GET /api/v1/instagram/v2/search_users`

<!-- Full path: /api/v1/instagram/v3/search_users -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| query | string | ✅ | 搜索关键词/Search keyword | justin |
| rank_token | string |  | >- |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- Instagram用户搜索接口
- 仅返回用户搜索结果
### 参数:
- query: 搜索关键词
- rank_token: 上一次搜索返回的rank_token，用于翻页
### 返回:
- `data.users`: 用户搜索结果列表
- `data.rank_token`: 排序token
- `data.see_more`: 更多信息
- `data.inform_module`: 提示模块

## user_id_to_username

`GET /api/v1/instagram/v2/user_id_to_username`

<!-- Full path: /api/v1/instagram/v2/user_id_to_username -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string | ✅ | 用户ID/User ID | 18527 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 通过Instagram用户ID获取用户信息
- 可用于将用户ID转换为用户名及获取完整用户资料
### 参数:
- user_id: 用户ID
### 返回:
- `pk`/`pk_id`: 用户ID
- `username`: 用户名
- `full_name`: 用户全名
- `is_private`: 是否私密账户
- `is_verified`: 是否已认证
- `profile_pic_url`: 头像URL
- `biography`: 个人简介
- `follower_count`: 粉丝数
- `following_count`: 关注数
- `media_count`: 帖子数

---

See SKILL.md for cross-group orchestration patterns.