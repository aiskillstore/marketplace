# Search API / 搜索接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---
## author_content_hot_comment_keywords_v1

`GET /api/v1/douyin/xingtu/author_content_hot_comment_keywords_v1`

<!-- Full path: /api/v1/douyin/xingtu/author_content_hot_comment_keywords_v1 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| kolId | string | ✅ | 用户的kolId/User kolId | 7048929565493690398 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取kol热词分析内容V1
 - 该接口数据使用企业账号进行请求，收费较贵。
 ### 参数:
 - kolId: 用户的kolId, 可以从接口以下接口获取：
    - `/api/v1/douyin/xingtu/get_xingtu_kolid_by_uid`
    - `/api/v1/douyin/xingtu/get_xingtu_kolid_by_sec_user_id`
    - `/api/v1/douyin/xingtu/get_xingtu_kolid_by_unique_id`
### 返回:
 - kol热词分析内容

## fetch_brand_hot_search_list

`GET /api/v1/douyin/app/v3/fetch_brand_hot_search_list`

<!-- Full path: /api/v1/douyin/app/v3/fetch_brand_hot_search_list -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取抖音品牌热榜分类数据
### 返回:
- 品牌热搜榜分类数据

## fetch_brand_suggest

`POST /api/v1/douyin/index/fetch_brand_suggest`

<!-- Full path: /api/v1/douyin/index/fetch_brand_suggest -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 品牌名称关键词/Brand keyword |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取品牌搜索的自动补全建议列表
### 参数:
- keyword: 品牌名称关键词
### 返回:
- 匹配的品牌列表（品牌名称、分类ID等）

## fetch_challenge_search_v1

`POST /api/v1/douyin/search/fetch_challenge_search_v1`

<!-- Full path: /api/v1/douyin/search/fetch_challenge_search_v1 -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取抖音 App 中的话题（挑战/标签）搜索结果。
 - 根据关键词返回关联的话题列表，包含话题热度、封面、参与人数等信息。
  ### 备注:
 - 仅返回话题类型内容。
 - 初次请求时 `cursor` 传 0，`search_id` 传空字符串。
 - 翻页查询时使用上次响应返回的 `cursor` 和 `search_id`。
  ### 参数:
 - keyword: 搜索关键词，例如 "美食"
 - cursor: 翻页游标（首次请求传 0，翻页时使用上次响应的 cursor）
 - sort_type: 排序方式
    - `0`: 综合排序
    - `1`: 最多点赞
    - `2`: 最新发布
- publish_time: 发布时间筛选
    - `0`: 不限
    - `1`: 最近一天
    - `7`: 最近一周
    - `180`: 最近半年
- filter_duration: 视频时长筛选
    - `0`: 不限
    - `0-1`: 1 分钟以内
    - `1-5`: 1-5 分钟
    - `5-10000`: 5 分钟以上
- content_type: 内容类型筛选
    - `0`: 不限
    - `1`: 视频
    - `2`: 图片
    - `3`: 文章
- search_id: 搜索ID（分页时使用）
  ### 请求体示例：
 ```json
 payload = {
    "keyword": "美食",
    "cursor": 0,
    "sort_type": "0",
    "publish_time": "0",
    "filter_duration": "0",
    "content_type": "0",
    "search_id": ""
}
 ```
  ### 返回（部分常用字段，实际返回字段更多，一切以实际响应为准）:
 - `cursor`: 翻页游标（用于下次请求）
 - `has_more`: 是否还有更多数据（1=有，0=无）
 - `challenge_list[]`: 话题列表
  - `challenge_info`:
    - `cid`: 话题ID
    - `cha_name`: 话题名称（如 "#美食探店"）
    - `desc`: 话题描述（通常为空）
    - `schema`: 抖音内部跳转链接（schema协议）
    - `share_info`:
      - `share_url`: 话题分享H5链接
      - `share_title`: 分享标题
      - `share_desc`: 分享描述
    - `view_count`: 话题总浏览量
    - `user_count`: 话题参与人数
    - `hashtag_profile`: 话题封面图URL
    - `challenge_status`: 话题状态（1=正常，0=异常）
  - `author`:
    - `uid`: 创建者用户ID
    - `nickname`: 创建者昵称
    - `follower_count`: 粉丝数量
    - `is_verified`: 是否认证
    - `region`: 地区
    - `avatar_thumb.url_list`: 小头像URL列表
    - `avatar_medium.url_list`: 中头像URL列表
    - `avatar_larger.url_list`: 高清头像URL列表
 - `extra`:
  - `now`: 当前服务器时间戳（毫秒）
  - `search_request_id`: 搜索请求唯一ID

## fetch_challenge_search_v2

`POST /api/v1/douyin/search/fetch_challenge_search_v2`

<!-- Full path: /api/v1/douyin/search/fetch_challenge_search_v2 -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取抖音 App 中话题(挑战/标签)搜索的结果，使用 V2 版本 API。
 - 支持关键词搜索，返回匹配的话题详情，包括话题名称、话题封面、浏览量、参与人数等。
  ### 备注:
 - 本接口专注于搜索话题（Challenge/Hashtag）内容，不包含视频或直播等其他类型。
 - 初次请求时 `cursor` 传入 0，`search_id` 传空字符串，后续翻页请使用上一次返回的 `cursor` 和
`search_id`。
  ### 参数:
 - keyword: 搜索关键词，如 "游戏"
 - cursor: 翻页游标（首次请求传 0，翻页时使用上次响应的 cursor）
 - sort_type: 排序方式
    - `0`: 综合排序
    - `1`: 最多点赞
    - `2`: 最新发布
- publish_time: 发布时间筛选
    - `0`: 不限
    - `1`: 最近一天
    - `7`: 最近一周
    - `180`: 最近半年
- filter_duration: 视频时长筛选
    - `0`: 不限
    - `0-1`: 1 分钟以内
    - `1-5`: 1-5 分钟
    - `5-10000`: 5 分钟以上
- content_type: 内容类型筛选
    - `0`: 不限
    - `1`: 视频
    - `2`: 图片
    - `3`: 文章
- search_id: 搜索ID（分页时使用）
  ### 请求体示例：
 ```json
 payload = {
    "keyword": "游戏",
    "cursor": 0,
    "sort_type": "0",
    "publish_time": "0",
    "filter_duration": "0",
    "content_type": "0",
    "search_id": ""
}
 ```
  ### 返回（部分常用字段，实际返回字段更多，一切以实际响应为准）:
 - `business_data`（话题搜索结果列表）
  - `data_id`: 结果的唯一编号
  - `type`: 数据类型（固定为 `2`）
  - `data.challenge_info`:
    - `cid`: 话题ID
    - `cha_name`: 话题名称
    - `desc`: 话题描述
    - `schema`: 话题跳转链接（aweme://开头，可跳转抖音 App 内话题详情）
    - `hashtag_profile`: 话题封面图 URL
    - `user_count`: 参与人数
    - `view_count`: 话题浏览量
    - `challenge_status`: 话题状态（1=正常，其他=异常）
    - `author`: 创建者信息
      - `uid`: 创建者抖音用户ID
      - `nickname`: 昵称
      - `avatar_thumb.url_list`: 缩略头像URL列表
      - `is_verified`: 是否认证
      - `follower_count`: 粉丝数
    - `share_info`:
      - `share_url`: 话题分享链接
      - `share_title`: 分享标题
      - `share_desc`: 分享描述

## fetch_content_creative_keywords

`POST /api/v1/douyin/index/fetch_content_creative_keywords`

<!-- Full path: /api/v1/douyin/index/fetch_content_creative_keywords -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| tag_id | string | ✅ | >- |  |
| period | string ('1'/'3'/'7') |  | '时间周期/Period: 1=近1天, 3=近3天, 7=近7天' (default: '7') |  |
| end_date | string | ✅ | >- |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定垂类下创作热门关键词
 ### 参数:
 - tag_id: 垂类ID（与 fetch_item_query 的 category_id 含义一致）
    - **本接口不支持 "0=全部"，必须传入具体的垂类 ID**（如 "601"=剧情, "628"=美食 等）
    - 完整垂类列表见 fetch_item_filter_options
- period: 时间周期，可选 "1"(近1天) / "3"(近3天) / "7"(近7天)
 - end_date: 结束日期（YYYYMMDD）。**仅当 period=7 时必须为周日**，period=1/3 时可为任意日期
 ### 返回:
 - 该垂类下热门关键词列表

## fetch_content_creative_topic

`POST /api/v1/douyin/index/fetch_content_creative_topic`

<!-- Full path: /api/v1/douyin/index/fetch_content_creative_topic -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| tag_id | string | ✅ | >- |  |
| period | string ('1'/'3'/'7') |  | '时间周期/Period: 1, 3, 7' (default: '7') |  |
| end_date | string | ✅ | >- |  |
| rank_type | string (index/rise) |  | '排序类型/Rank type: index=指数排序, rise=飙升排序' (default: index) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定垂类下创作热门话题
 ### 参数:
 - tag_id: 垂类ID（同 fetch_item_query 的 category_id）
    - **本接口不支持 "0=全部"，必须传入具体的垂类 ID**（如 "601"=剧情, "628"=美食 等）
    - 完整垂类列表见 fetch_item_filter_options
- period: 时间周期 "1"/"3"/"7"
 - end_date: 结束日期。**仅当 period=7 时必须为周日**，period=1/3 时可为任意日期
 - rank_type: 排序类型，"index"=指数, "rise"=飙升
 ### 返回:
 - 该垂类下热门话题列表

## fetch_creator_hot_topic_billboard

`GET /api/v1/douyin/creator/fetch_creator_hot_topic_billboard`

<!-- Full path: /api/v1/douyin/creator/fetch_creator_hot_topic_billboard -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| billboard_tag | integer |  | >- (default: 0) |  |
| order_key | integer |  | >- (default: 1) |  |
| time_filter | integer |  | >- (default: 1) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取抖音创作者热门话题榜单数据
 ### 参数:
 - billboard_tag: 榜单标签，0=全部，其他值请通过config接口获取
    - 0: 全部
    - 333: 美食
    - 334: 旅行
    - 299: 泛生活
    - 335: 汽车
    - 336: 科技
    - 302: 游戏
    - 296: 二次元
    - 337: 娱乐
    - 311: 明星
    - 298: 体育
    - 300: 文化教育
    - 301: 校园
    - 297: 政务
    - 305: 时尚
    - 306: 才艺
    - 669: 财经
    - 314: 随拍
    - 307: 动植物
    - 309: 图文控
    - 308: 剧情
    - 315: 亲子
    - 718: 三农
    - 310: 创意
    - 312: 户外
    - 926: 公益
- order_key: 排序键
    - 1: 播放最高
    - 2: 点赞最多
    - 3: 评论最多
    - 4: 投稿最多
- time_filter: 时间筛选
    - 1: 24小时
    - 2: 7天
    - 3: 30天
### 返回:
 - 创作者热门话题榜单数据

## fetch_discuss_search

`POST /api/v1/douyin/search/fetch_discuss_search`

<!-- Full path: /api/v1/douyin/search/fetch_discuss_search -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取抖音 App 中讨论区/问答内容的搜索结果。
 - 支持关键词、排序方式、发布时间、内容类型等筛选条件。
  ### 备注:
 - 此接口专注于讨论区内容搜索（如问答讨论视频），不包含其他类型的内容。
 - 初次请求时 `cursor` 传入 0，`search_id` 传空字符串。
 - 返回内容包括视频信息、作者信息、播放信息、互动数据、话题标签等。
  ### 参数:
 - keyword: 搜索关键词，例如 "出国留学"
 - cursor: 翻页游标（首次请求传 0，翻页时使用上次响应的 cursor）
 - sort_type: 排序方式
  - `0`: 综合排序
  - `1`: 最多点赞
  - `2`: 最新发布
- publish_time: 发布时间筛选
  - `0`: 不限
  - `1`: 最近一天
  - `7`: 最近一周
  - `180`: 最近半年
- filter_duration: 视频时长筛选
  - `0`: 不限
  - `0-1`: 1 分钟以内
  - `1-5`: 1-5 分钟
  - `5-10000`: 5 分钟以上
- content_type: 内容类型筛选
  - `0`: 不限
  - `1`: 视频
  - `2`: 图片
  - `3`: 文章
- search_id: 搜索ID（分页时使用）
  ### 请求体示例：
 ```json
 payload = {
    "keyword": "出国留学",
    "cursor": 0,
    "sort_type": "0",
    "publish_time": "0",
    "filter_duration": "0",
    "content_type": "0",
    "search_id": ""
}
 ```
  ### 返回（部分常用字段，实际返回字段更多，一切以实际响应为准）:
 - `data`: 搜索结果列表
  - `type`: 结果类型（一般为 `1`）
  - `aweme_info`: 视频信息
    - `aweme_id`: 视频ID
    - `desc`: 视频描述内容
    - `author`: 作者信息
      - `uid`: 用户唯一ID
      - `nickname`: 用户昵称
      - `is_verified`: 是否认证用户
      - `region`: 用户地区
      - `avatar_thumb.url_list`: 缩略头像列表
      - `avatar_medium.url_list`: 中等尺寸头像列表
      - `avatar_larger.url_list`: 高清头像列表
    - `video`: 视频播放与封面信息
      - `play_addr.url_list`: 播放地址列表
      - `cover.url_list`: 视频封面列表
      - `dynamic_cover.url_list`: 动态封面列表
      - `origin_cover.url_list`: 原始封面列表
      - `width`: 视频宽度（像素）
      - `height`: 视频高度（像素）
      - `ratio`: 视频分辨率比例（如540p）
      - `duration`: 视频时长（毫秒）
      - `download_addr.url_list`: 带水印下载地址
    - `statistics`: 视频数据
      - `comment_count`: 评论数
      - `digg_count`: 点赞数
      - `share_count`: 分享数
      - `play_count`: 播放次数
      - `collect_count`: 收藏次数
    - `cha_list`: 话题标签
      - `cha_name`: 标签名称
      - `share_url`: 标签分享链接
    - `music`: 音乐信息
      - `id_str`: 音乐ID
      - `title`: 音乐标题
      - `author`: 音乐作者昵称
      - `play_url.url_list`: 音乐播放链接列表
    - `status`: 视频状态
      - `is_delete`: 是否被删除
      - `is_private`: 是否设为私密
      - `allow_share`: 是否允许分享
      - `allow_comment`: 是否允许评论
    - `share_url`: 视频外部分享链接

## fetch_experience_search

`POST /api/v1/douyin/search/fetch_experience_search`

<!-- Full path: /api/v1/douyin/search/fetch_experience_search -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取抖音 App 中经验（知识/教程）内容的搜索结果。
 - 支持通过关键词检索，与经验类内容（如攻略、教程、分享等）相关的视频信息。
  ### 备注:
 - 此接口专注于经验类内容，不包含其他类型的内容。
 - 初次请求时，`cursor` 应传 0，`search_id` 传空字符串，翻页时使用上次响应返回的 cursor 和 search_id。
 - 返回的结果中包含视频详情、作者信息、背景音乐、话题标签、播放地址、互动数据等。
  ### 参数:
 - keyword: 搜索关键词，例如 "游戏攻略"
 - cursor: 翻页游标，首次请求传 0
 - sort_type: 排序方式
  - `0`: 综合排序
  - `1`: 最多点赞
  - `2`: 最新发布
- publish_time: 发布时间筛选
  - `0`: 不限
  - `1`: 最近一天
  - `7`: 最近一周
  - `180`: 最近半年
- filter_duration: 视频时长筛选
  - `0`: 不限
  - `0-1`: 1分钟以内
  - `1-5`: 1-5分钟
  - `5-10000`: 5分钟以上
- content_type: 内容类型筛选（通常固定为视频）
 - search_id: 分页查询时需要传上次响应返回的 `search_id`
  ### 请求体示例：
 ```json
 payload = {
    "keyword": "游戏攻略",
    "cursor": 0,
    "sort_type": 0,
    "publish_time": 0,
    "filter_duration": 0,
    "content_type": 1,
    "search_id": ""
}
  ### 返回（部分常用字段，实际返回字段更多，一切以实际响应为准）:
 - business_data: 搜索结果业务数据列表
  - data_id: 数据块ID
  - type: 数据类型（如 999 表示内容列表）
  - data:
    - height: 显示区域高度
    - aweme_list: 视频列表
      - aweme_id: 视频ID
      - desc: 视频描述内容
      - create_time: 视频发布时间（时间戳）
      - author: 作者信息
        - uid: 作者UID
        - nickname: 作者昵称
        - avatar_thumb.url_list: 作者头像缩略图
        - is_verified: 是否是认证账号
        - follower_count: 粉丝数
      - music: 背景音乐信息
        - id_str: 音乐ID
        - title: 音乐标题
        - author: 音乐作者昵称
      - cha_list: 关联的话题标签列表
        - cha_name: 话题名称
      - video: 视频播放信息
        - play_addr.url_list: 视频播放地址列表
        - cover.url_list: 视频封面图地址
        - width: 视频宽度
        - height: 视频高度
        - duration: 视频时长（单位毫秒）
      - statistics: 视频互动数据
        - digg_count: 点赞数
        - comment_count: 评论数
        - share_count: 分享数
        - play_count: 播放次数
      - status: 视频状态信息
        - is_delete: 是否已删除
        - is_private: 是否私密
      - share_url: 视频外部分享链接

## fetch_general_search_v1

`POST /api/v1/douyin/search/fetch_general_search_v1`

<!-- Full path: /api/v1/douyin/search/fetch_general_search_v1 -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取抖音 App 中综合搜索栏的搜索结果（非单独视频搜索）。
 - 支持关键词、排序方式、发布时间、视频时长、内容类型等筛选条件。
 - 支持翻页查询，通过 `cursor`、`search_id` 和 `backtrace` 分页。
  ### 备注:
 - 初次请求时 `cursor` 传入 0，`search_id` 和 `backtrace` 传空字符串。
 - 翻页时需从上一次响应中获取 `cursor`、`search_id` 和 `backtrace` 字段值。
 - 返回的内容包含视频、作者、话题标签、播放信息、音乐、互动数据等丰富信息。
  ### 参数:
 - keyword: 搜索关键词，如 "猫咪"
 - cursor: 翻页游标（首次请求传 0，翻页时使用上次响应的 cursor）
 - sort_type: 排序方式
    - `0`: 综合排序
    - `1`: 最多点赞
    - `2`: 最新发布
- publish_time: 发布时间筛选
    - `0`: 不限
    - `1`: 最近一天
    - `7`: 最近一周
    - `180`: 最近半年
- filter_duration: 视频时长筛选
    - `0`: 不限
    - `0-1`: 1 分钟以内
    - `1-5`: 1-5 分钟
    - `5-10000`: 5 分钟以上
- content_type: 内容类型筛选
    - `0`: 不限
    - `1`: 视频
    - `2`: 图片
    - `3`: 文章
- search_id: 搜索ID（首次请求传空，翻页时从上次响应获取）
 - backtrace: 翻页回溯标识（首次请求传空，翻页时从上次响应获取）
  ### 请求体示例：
 ```json
 payload = {
  "keyword": "猫咪",
  "cursor": 0,
  "sort_type": "0",
  "publish_time": "0",
  "filter_duration": "0",
  "content_type": "0",
  "search_id": "",
  "backtrace": ""
}
 ```
  ### 返回（部分常用字段，实际返回字段更多，一切以实际响应为准）:
 - `data`: 搜索结果列表
 - `type`: 结果类型（通常为 `1`）
 - `aweme_info`: 视频详细信息
 - `aweme_id`: 视频ID
 - `desc`: 视频描述内容
 - `author`: 作者信息
  - `uid`: 用户唯一ID
  - `nickname`: 用户昵称
  - `is_verified`: 是否认证用户（True=已认证，False=未认证）
  - `region`: 用户地区，如 "CN"
  - `avatar_thumb.url_list`: 缩略头像地址列表
  - `avatar_medium.url_list`: 中等尺寸头像地址列表
  - `avatar_larger.url_list`: 高清头像地址列表
- `music`: 背景音乐信息
  - `id_str`: 音乐ID
  - `title`: 音乐标题，如"原创声音"
  - `author`: 音乐作者昵称
  - `play_url.url_list`: 音乐播放地址列表
- `cha_list`: 关联话题标签列表
  - `cha_name`: 话题名（例如 "#猫宝宝"）
  - `share_url`: 话题分享链接
- `video`: 视频播放与封面信息
  - `play_addr.url_list`: 视频播放地址列表
  - `cover.url_list`: 视频封面地址列表
  - `dynamic_cover.url_list`: 动态封面地址列表
  - `origin_cover.url_list`: 原始封面地址列表
  - `width`: 视频宽度（像素）
  - `height`: 视频高度（像素）
  - `ratio`: 视频分辨率比例（如540p）
  - `duration`: 视频时长（单位：毫秒）
  - `download_addr.url_list`: 带水印下载地址
- `statistics`: 视频统计信息
  - `comment_count`: 评论数
  - `digg_count`: 点赞数
  - `share_count`: 分享数
  - `play_count`: 播放次数
  - `collect_count`: 收藏次数
- `status`: 视频发布状态
  - `is_delete`: 是否被删除
  - `is_private`: 是否设为私密
  - `allow_share`: 是否允许分享
  - `allow_comment`: 是否允许评论
- `share_url`: 视频外部分享链接

## fetch_general_search_v2

`POST /api/v1/douyin/search/fetch_general_search_v2`

<!-- Full path: /api/v1/douyin/search/fetch_general_search_v2 -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取抖音 App 中综合搜索栏的搜索结果（非单独视频搜索）。
 - 此接口稳定性可能不如 V1版本，作为备用接口。
 - 支持关键词、排序方式、发布时间、视频时长、内容类型等筛选条件。
 - 支持翻页查询，通过 `cursor`、`search_id` 和 `backtrace` 分页。
  ### 备注:
 - 初次请求时 `cursor` 传入 0，`search_id` 和 `backtrace` 传空字符串。
 - 翻页时需从上一次响应中获取 `cursor`、`search_id` 和 `backtrace` 字段值。
 - 返回的内容包含视频、作者、话题标签、播放信息、音乐、互动数据等丰富信息。
  ### 参数:
 - keyword: 搜索关键词，如 "猫咪"
 - cursor: 翻页游标（首次请求传 0，翻页时使用上次响应的 cursor）
 - sort_type: 排序方式
    - `0`: 综合排序
    - `1`: 最多点赞
    - `2`: 最新发布
- publish_time: 发布时间筛选
    - `0`: 不限
    - `1`: 最近一天
    - `7`: 最近一周
    - `180`: 最近半年
- filter_duration: 视频时长筛选
    - `0`: 不限
    - `0-1`: 1 分钟以内
    - `1-5`: 1-5 分钟
    - `5-10000`: 5 分钟以上
- content_type: 内容类型筛选
    - `0`: 不限
    - `1`: 视频
    - `2`: 图片
    - `3`: 文章
- search_id: 搜索ID（首次请求传空，翻页时从上次响应获取）
 - backtrace: 翻页回溯标识（首次请求传空，翻页时从上次响应获取）
  ### 请求体示例：
 ```json
 payload = {
  "keyword": "猫咪",
  "cursor": 0,
  "sort_type": "0",
  "publish_time": "0",
  "filter_duration": "0",
  "content_type": "0",
  "search_id": "",
  "backtrace": ""
}
 ```
  ### 返回（部分常用字段，实际返回字段更多，一切以实际响应为准）:
 - `data`: 搜索结果列表
 - `type`: 结果类型（通常为 `1`）
 - `aweme_info`: 视频详细信息
 - `aweme_id`: 视频ID
 - `desc`: 视频描述内容
 - `author`: 作者信息
  - `uid`: 用户唯一ID
  - `nickname`: 用户昵称
  - `is_verified`: 是否认证用户（True=已认证，False=未认证）
  - `region`: 用户地区，如 "CN"
  - `avatar_thumb.url_list`: 缩略头像地址列表
  - `avatar_medium.url_list`: 中等尺寸头像地址列表
  - `avatar_larger.url_list`: 高清头像地址列表
- `music`: 背景音乐信息
  - `id_str`: 音乐ID
  - `title`: 音乐标题，如"原创声音"
  - `author`: 音乐作者昵称
  - `play_url.url_list`: 音乐播放地址列表
- `cha_list`: 关联话题标签列表
  - `cha_name`: 话题名（例如 "#猫宝宝"）
  - `share_url`: 话题分享链接
- `video`: 视频播放与封面信息
  - `play_addr.url_list`: 视频播放地址列表
  - `cover.url_list`: 视频封面地址列表
  - `dynamic_cover.url_list`: 动态封面地址列表
  - `origin_cover.url_list`: 原始封面地址列表
  - `width`: 视频宽度（像素）
  - `height`: 视频高度（像素）
  - `ratio`: 视频分辨率比例（如540p）
  - `duration`: 视频时长（单位：毫秒）
  - `download_addr.url_list`: 带水印下载地址
- `statistics`: 视频统计信息
  - `comment_count`: 评论数
  - `digg_count`: 点赞数
  - `share_count`: 分享数
  - `play_count`: 播放次数
  - `collect_count`: 收藏次数
- `status`: 视频发布状态
  - `is_delete`: 是否被删除
  - `is_private`: 是否设为私密
  - `allow_share`: 是否允许分享
  - `allow_comment`: 是否允许评论
- `share_url`: 视频外部分享链接

## fetch_hot_account_fans_interest_search_list

`GET /api/v1/douyin/billboard/fetch_hot_account_fans_interest_search_list`

<!-- Full path: /api/v1/douyin/billboard/fetch_hot_account_fans_interest_search_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| sec_uid | string | ✅ | 用户sec_id | MS4wLjABAAAA8U_l6rBzmy7bcy6xOJel4v0RzoR_wfAubGPeJimN__4 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取粉丝近3天搜索词 10个搜索词
### 参数:
- sec_uid: 用户sec_id
### 返回:
- 粉丝近3天搜索词 10个搜索词

## fetch_hot_search_list

`GET /api/v1/douyin/app/v3/fetch_hot_search_list`

<!-- Full path: /api/v1/douyin/app/v3/fetch_hot_search_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| board_type | string |  | 榜单类型/Board type (default: '0') |  |
| board_sub_type | string |  | 榜单子类型/Board sub type (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取抖音热榜数据，包括：
    - 热点榜
    - 种草榜
    - 娱乐榜
    - 社会榜
    - 挑战榜
### 参数:
- board_type:
    - 0: 热点榜（默认）
    - 2: 其他榜单，如种草榜等，需要传入对应的board_sub_type参数。
- board_sub_type:
    - 空字符串: 热点榜（默认）
    - seeding: 种草榜
    - 2: 娱乐榜
    - 4: 社会榜
    - hotspot_challenge: 挑战榜
### 返回:
- 热搜榜数据

## fetch_hot_search_result

`GET /api/v1/douyin/web/fetch_hot_search_result`

<!-- Full path: /api/v1/douyin/web/fetch_hot_search_result -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取抖音热榜数据
### 返回:
- 热榜数据

## fetch_hot_total_high_search_list

`POST /api/v1/douyin/billboard/fetch_hot_total_high_search_list`

<!-- Full path: /api/v1/douyin/billboard/fetch_hot_total_high_search_list -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取热度飙升的搜索榜
### 参数:
- page_num: 页码
- page_size: 每页数量
- date_window: 时间窗口，1 按小时 2 按天
- keyword: 搜索关键字
### 返回:
- 热度飙升的搜索榜

## fetch_hot_total_high_topic_list

`POST /api/v1/douyin/billboard/fetch_hot_total_high_topic_list`

<!-- Full path: /api/v1/douyin/billboard/fetch_hot_total_high_topic_list -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取热度飙升的话题榜
 ### 参数:
 - page: 页码
 - page_size: 每页数量
 - date_window: 时间窗口，1 按小时 2 按天
 - tags: 子级垂类标签，空则为全部，多个标签需传入
    {"value": "{顶级垂类标签id}", "children": [
        {"value": "{子级垂类标签id}"},
        {"value": "{子级垂类标签id}"}
    ]}
### 返回:
 - 热度飙升的话题榜

## fetch_hot_total_search_list

`POST /api/v1/douyin/billboard/fetch_hot_total_search_list`

<!-- Full path: /api/v1/douyin/billboard/fetch_hot_total_search_list -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取搜索榜
### 参数:
- page_num: 页码
- page_size: 每页数量
- date_window: 时间窗口，1 按小时 2 按天
- keyword: 搜索关键字
### 返回:
- 搜索榜

## fetch_hot_total_topic_list

`POST /api/v1/douyin/billboard/fetch_hot_total_topic_list`

<!-- Full path: /api/v1/douyin/billboard/fetch_hot_total_topic_list -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取话题榜
 ### 参数:
 - page: 页码
 - page_size: 每页数量
 - date_window: 时间窗口，1 按小时 2 按天
 - tags: 子级垂类标签，空则为全部，多个标签需传入
    {"value": "{顶级垂类标签id}", "children": [
        {"value": "{子级垂类标签id}"},
        {"value": "{子级垂类标签id}"}
    ]}
### 返回:
 - 话题榜

## fetch_hot_words

`GET /api/v1/douyin/index/fetch_hot_words`

<!-- Full path: /api/v1/douyin/index/fetch_hot_words -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| app_name | string (aweme/toutiao) |  | '平台/Platform: aweme(抖音), toutiao(头条)' (default: aweme) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取当前热门搜索关键词列表
### 参数:
- app_name: 平台选择，aweme=抖音，toutiao=头条
### 返回:
- 关键词名称、搜索指数、增长率等

## fetch_image_search

`POST /api/v1/douyin/search/fetch_image_search`

<!-- Full path: /api/v1/douyin/search/fetch_image_search -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取抖音 App 中图片内容搜索的结果。
 - 主要返回带有多张图片的帖子（图片合集）。
  ### 备注:
 - 仅返回图片类型的内容，适用于图片展示类应用场景。
 - 初次请求 `cursor` 传 0，`search_id` 传空字符串。
 - 翻页时使用上一次响应中的 `cursor` 和 `search_id`。
  ### 参数:
 - keyword: 搜索关键词，如 "猫咪"
 - cursor: 翻页游标（首次请求传0）
 - sort_type: 排序方式
  - `0`: 综合排序
  - `1`: 最多点赞
  - `2`: 最新发布
- publish_time: 发布时间筛选
  - `0`: 不限
  - `1`: 最近一天
  - `7`: 最近一周
  - `180`: 最近半年
- filter_duration: 视频时长筛选
  - `0`: 不限
- content_type: 内容类型（固定传 2 表示图片内容）
 - search_id: 搜索ID（翻页使用）
  ### 请求体示例：
 ```json
 payload = {
    "keyword": "猫咪",
    "cursor": 0,
    "sort_type": "0",
    "publish_time": "0",
    "filter_duration": "0",
    "content_type": "2",
    "search_id": ""
}
 ```
  ### 返回（部分常用字段，实际返回字段更多，一切以实际响应为准）:
 - `cursor`: 下一页游标
 - `has_more`: 是否还有更多数据（1=有，0=无）
 - `data[]`: 图片内容列表
  - `aweme_info`:
    - `aweme_id`: 内容ID
    - `desc`: 帖子描述文字
    - `create_time`: 创建时间戳
    - `author`:
      - `uid`: 作者ID
      - `nickname`: 昵称
      - `is_verified`: 是否认证
      - `avatar_thumb.url_list`: 缩略头像URL列表
      - `avatar_medium.url_list`: 中等头像URL列表
      - `avatar_larger.url_list`: 高清头像URL列表
    - `image_post_info`:
      - `images[]`: 图片列表
        - `url_list`: 图片地址数组（通常包含webp/jpg）
        - `width`: 图片宽度（像素）
        - `height`: 图片高度（像素）
    - `statistics`:
      - `comment_count`: 评论数
      - `digg_count`: 点赞数
      - `share_count`: 分享数
      - `play_count`: 播放数
      - `collect_count`: 收藏数
    - `status`:
      - `is_delete`: 是否删除
      - `is_private`: 是否私密
    - `share_url`: 外部分享链接
 - `extra`:
  - `now`: 当前服务器时间戳
  - `logid`: 请求日志ID
  - `search_request_id`: 搜索请求ID

## fetch_image_search_v3

`POST /api/v1/douyin/search/fetch_image_search_v3`

<!-- Full path: /api/v1/douyin/search/fetch_image_search_v3 -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取抖音 App 中图文内容搜索的结果。
 - 返回带有多张图片的帖子（aweme_type=68），适用于图文展示类应用场景。
  ### 备注:
 - 该接口与 `fetch_image_search` 使用不同的数据源，返回结果可能有所差异。
 - 推荐用于需要高质量图文内容的场景。
 - 初次请求时 `cursor` 传 0，`search_id` 传空字符串。
 - 翻页请求时，使用上一次响应返回的 `cursor` 和 `search_id`。
 - 每页返回约 12 条数据。
  ### 参数:
 - keyword: 搜索关键词，如 "美食"
 - cursor: 翻页游标（首次请求传 0）
 - search_id: 搜索ID（翻页时使用上次响应中的值）
  ### 请求体示例：
 ```json
 payload = {
    "keyword": "美食",
    "cursor": 0,
    "search_id": ""
}
 ```
  ### 返回（部分常用字段，实际返回字段更多，一切以实际响应为准）:
 - `status_code`: 状态码（0=成功）
 - `business_data[]`: 图文内容列表
  - `data`:
    - `aweme_list[]`: 内容列表
      - `aweme_id`: 内容ID
      - `aweme_type`: 内容类型（68=图文）
      - `desc`: 帖子描述文字
      - `create_time`: 创建时间戳
      - `author`:
        - `uid`: 作者ID
        - `nickname`: 昵称
        - `avatar_thumb.url_list`: 缩略头像URL列表
      - `image_post_info`:
        - `images[]`: 图片列表
          - `url_list`: 图片地址数组
          - `width`: 图片宽度（像素）
          - `height`: 图片高度（像素）
      - `statistics`:
        - `comment_count`: 评论数
        - `digg_count`: 点赞数
        - `share_count`: 分享数
        - `collect_count`: 收藏数
      - `share_url`: 外部分享链接
- `extra`:
  - `now`: 当前服务器时间戳
  - `logid`: 请求日志ID
 ---

## fetch_keyword_valid_date

`POST /api/v1/douyin/index/fetch_keyword_valid_date`

<!-- Full path: /api/v1/douyin/index/fetch_keyword_valid_date -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword_list | string | ✅ | 关键词列表，逗号分隔/Keyword list, comma separated |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取指定关键词在抖音指数中的有效日期范围
### 参数:
- keyword_list: 关键词列表，多个关键词用逗号分隔，如 "美食,旅游"
### 返回:
- 各关键词可查询的起止日期

## fetch_multi_keyword_hot_trend

`POST /api/v1/douyin/index/fetch_multi_keyword_hot_trend`

<!-- Full path: /api/v1/douyin/index/fetch_multi_keyword_hot_trend -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword_list | string | ✅ | 关键词列表，逗号分隔/Keyword list, comma separated |  |
| start_date | string | ✅ | 开始日期/Start date, YYYYMMDD |  |
| end_date | string | ✅ | 结束日期/End date, YYYYMMDD |  |
| app_name | string (aweme/toutiao) |  | '平台/Platform: aweme(抖音), toutiao(头条)' (default: aweme) |  |
| region | string |  | 地区列表，逗号分隔/Region list, comma separated (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取多个关键词在指定时间范围内的热度趋势数据
- 可对比多个关键词的热度变化
### 参数:
- keyword_list: 关键词列表，逗号分隔，如 "美食,旅游"
- start_date: 开始日期，格式 YYYYMMDD
- end_date: 结束日期，格式 YYYYMMDD
- app_name: 平台选择，aweme=抖音，toutiao=头条
- region: 地区筛选，逗号分隔（如 "云南,上海,北京"），留空表示全国
### 返回:
- 每日热度趋势数据

## fetch_multi_keyword_interpretation

`POST /api/v1/douyin/index/fetch_multi_keyword_interpretation`

<!-- Full path: /api/v1/douyin/index/fetch_multi_keyword_interpretation -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword_list | string | ✅ | 关键词列表，逗号分隔/Keyword list, comma separated |  |
| start_date | string | ✅ | 开始日期/Start date, YYYYMMDD |  |
| end_date | string | ✅ | 结束日期/End date, YYYYMMDD |  |
| app_name | string (aweme/toutiao) |  | '平台/Platform: aweme(抖音), toutiao(头条)' (default: aweme) |  |
| region | string |  | 地区列表，逗号分隔/Region list, comma separated (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取多个关键词的指数解读数据（综合指数、搜索指数、内容指数等）
 - 建议配合 fetch_multi_keyword_hot_trend 一起使用
 ### 参数:
 - keyword_list: 关键词列表，逗号分隔
 - start_date: 开始日期，格式 YYYYMMDD
 - end_date: 结束日期，格式 YYYYMMDD
 - app_name: 平台选择，aweme=抖音，toutiao=头条
 - region: 地区筛选，逗号分隔，留空表示全国
 ### 返回:
 - 关键词综合指数、搜索指数、内容指数解读

## fetch_multi_search

`POST /api/v1/douyin/search/fetch_multi_search`

<!-- Full path: /api/v1/douyin/search/fetch_multi_search -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取抖音 App 中多种类型（视频、用户、音乐、话题等）的综合搜索结果。
  ### 备注:
 - 初次请求 `cursor` 传 0，`search_id` 传空字符串。
 - 返回内容丰富，适合搭建搜索聚合页、推荐页等场景。
  ### 参数:
 - keyword: 搜索关键词，如 "人工智能"
 - cursor: 翻页游标（首次请求传 0，翻页时使用上次响应的 cursor）
 - sort_type: 排序方式
    - `0`: 综合排序
    - `1`: 最多点赞
    - `2`: 最新发布
- publish_time: 发布时间筛选
    - `0`: 不限
    - `1`: 最近一天
    - `7`: 最近一周
    - `180`: 最近半年
- filter_duration: 视频时长筛选
    - `0`: 不限
    - `0-1`: 1 分钟以内
    - `1-5`: 1-5 分钟
    - `5-10000`: 5 分钟以上
- content_type: 内容类型筛选
    - `0`: 不限
    - `1`: 视频
    - `2`: 图片
    - `3`: 文章
- search_id: 搜索ID（分页时使用）
  ### 请求体示例：
 ```json
 payload = {
    "keyword": "人工智能",
    "cursor": 0,
    "sort_type": "0",
    "publish_time": "0",
    "filter_duration": "0",
    "content_type": "0",
    "search_id": ""
}
 ```
  ### 返回（部分常用字段，实际返回字段更多，一切以实际响应为准）:
 - `cursor`: 下一页翻页游标
 - `has_more`: 是否还有更多数据（1=有，0=无）
 - `business_data[]`: 搜索结果列表
  - `data_id`: 结果数据编号
  - `type`: 结果类型
    - `1`: 视频（aweme_info）
    - `2`: 用户（user_info）
    - `4`: 音乐（music_info）
    - `6`: 话题（cha_info）
  - `data`: 具体数据内容，按type类型解析
    - 如果 type = 1（视频）:
      - `aweme_info`:
        - `aweme_id`: 视频ID
        - `desc`: 视频描述
        - `author`: 作者信息
          - `uid`: 用户ID
          - `nickname`: 用户昵称
          - `avatar_thumb.url_list`: 小头像
          - `is_verified`: 是否认证
          - `region`: 地区
        - `music`: 音乐信息
          - `id_str`: 音乐ID
          - `title`: 音乐标题
        - `video`: 视频播放与封面信息
          - `play_addr.url_list`: 播放地址
          - `cover.url_list`: 封面
          - `duration`: 视频时长（毫秒）
        - `statistics`:
          - `comment_count`: 评论数
          - `digg_count`: 点赞数
          - `share_count`: 分享数
          - `play_count`: 播放数
        - `status`:
          - `is_delete`: 是否被删除
          - `is_private`: 是否私密
        - `share_url`: 视频外链
    - 如果 type = 2（用户）:
      - `user_info`:
        - `uid`: 用户ID
        - `nickname`: 用户昵称
        - `signature`: 个人签名
        - `follower_count`: 粉丝数
        - `avatar_thumb.url_list`: 小头像
        - `region`: 地区
        - `is_verified`: 是否认证
    - 如果 type = 4（音乐）:
      - `music_info`:
        - `id_str`: 音乐ID
        - `title`: 音乐标题
        - `author`: 作者名
        - `play_url.url_list`: 播放地址
    - 如果 type = 6（话题）:
      - `cha_info`:
        - `cha_name`: 话题名
        - `desc`: 话题描述
        - `share_url`: 话题分享链接
        - `user_count`: 话题参与人数
        - `view_count`: 话题浏览次数
 - `extra`:
  - `now`: 当前服务器时间戳
  - `logid`: 请求日志ID

## fetch_report_search

`POST /api/v1/douyin/index/fetch_report_search`

<!-- Full path: /api/v1/douyin/index/fetch_report_search -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| current_page | string |  | 页码/Page number (default: '1') |  |
| page_size | string |  | 每页数量/Page size (default: '16') |  |
| type | string (''/行业洞察/产品洞察/用户洞察/趋势洞察) |  | >- (default: '') |  |
| business | string |  | >- (default: '') |  |
| report_time | string |  | 发布年份列表，逗号分隔/Year list, comma separated. e.g. 2024,2023 (default: '') |  |
| search | string |  | 报告关键词搜索/Search keyword (default: '') |  |
| category | string |  | >- (default: '6') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 搜索抖音指数下的趋势报告，支持类型/产品/年份/关键词四维筛选
### 参数:
- current_page / page_size: 分页参数（字符串）
- type: 报告类型，空字符串表示全部
    - "行业洞察" / "产品洞察" / "用户洞察" / "趋势洞察"
- business: 所属产品（逗号分隔），可选值：
    - "巨量引擎", "今日头条", "抖音", "西瓜视频", "抖音电商", "仕小禄", "其他"
- report_time: 发布年份（逗号分隔），如 "2024,2023"
- search: 报告标题关键词
- category: 顶层分类ID，默认 "6"（抖音指数趋势报告固定值，一般无需修改）
### 返回:
- 报告列表（标题、封面、发布时间、产品标签、报告ID 等）

## fetch_school_search

`POST /api/v1/douyin/search/fetch_school_search`

<!-- Full path: /api/v1/douyin/search/fetch_school_search -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取抖音 App 中学校信息的搜索结果。
 - 根据关键词返回学校名称列表，常用于用户设置学校资料、兴趣推荐等场景。
  ### 备注:
 - 本接口专注于学校信息搜索，仅返回学校的名称字段。
 - 初次请求时 `cursor` 应传 0，分页时使用上一次返回的 `cursor`。
 - 本接口响应体较简单，适合快速检索学校数据。
  ### 参数:
 - keyword: 搜索关键词，如学校名称 "北京大学"、地区名 "北京"
  ### 请求体示例：
 ```json
 payload = {
    "keyword": "北京大学"
}
 ```
  ### 返回（部分常用字段，实际返回字段更多，一切以实际响应为准）:
 - `schools[]`: 学校列表
  - `name`: 学校名称（如 "北京大学"、"北京四中"）
- `extra`:
  - `now`: 当前服务器时间戳（毫秒）
  - `logid`: 请求日志ID
  - `fatal_item_ids`: 错误项目ID列表（通常为空）
- `log_pb`:
  - `impr_id`: 曝光追踪ID（用于链路追踪）
- `status_code`: 状态码（0=成功）
 - `status_msg`: 状态信息（通常为空）

## fetch_topic_query

`POST /api/v1/douyin/index/fetch_topic_query`

<!-- Full path: /api/v1/douyin/index/fetch_topic_query -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 话题关键词/Topic keyword |  |
| start_date | string | ✅ | 开始日期/Start date YYYYMMDD |  |
| end_date | string | ✅ | 结束日期/End date YYYYMMDD |  |
| app_name | string (aweme/toutiao) |  | '平台/Platform: aweme(抖音), toutiao(头条)' (default: aweme) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 搜索话题，获取话题详情和相关数据
### 参数:
- keyword: 话题关键词
- start_date: 开始日期，格式 YYYYMMDD
- end_date: 结束日期，格式 YYYYMMDD
- app_name: 平台选择
### 返回:
- 话题详情、话题热度、相关视频数等

## fetch_topic_suggest

`POST /api/v1/douyin/index/fetch_topic_suggest`

<!-- Full path: /api/v1/douyin/index/fetch_topic_suggest -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 话题关键词/Topic keyword |  |
| app_name | string (aweme/toutiao) |  | '平台/Platform: aweme(抖音), toutiao(头条)' (default: aweme) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取话题搜索的自动补全建议列表
### 参数:
- keyword: 话题关键词
- app_name: 平台选择，aweme=抖音，toutiao=头条
### 返回:
- 匹配的话题列表

## fetch_vision_search

`POST /api/v1/douyin/search/fetch_vision_search`

<!-- Full path: /api/v1/douyin/search/fetch_vision_search -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 抖音APP图像识别搜索（以图搜图/视觉搜索）。
 - 通过图片进行视觉搜索，返回相似的视频/图文内容。
 - `image_uri` 可从抖音其他接口的返回数据中获取（如视频详情、搜索结果、用户主页等接口的图片uri字段）。
  ### 备注:
 - 初次请求时 `cursor` 传入 0，`search_id` 传空字符串。
 - 翻页时需从上一次响应中获取 `cursor` 和 `search_id` 字段值。
 - `image_uri` 是必填参数，需要先通过抖音图片上传接口获取，或在单一视频接口中获取，其他途径如各类搜索接口返回的图片URI均可使用。
 - `detection` 表示图片中需要识别的区域，格式为 "x1,y1,x2,y2"，默认 "0.1,0.1,0.9,0.9" 表示全图。
  ### 参数:
 - image_uri: 图片URI，通过图片上传接口获取，或在单一视频接口中获取，其他途径如各类搜索接口返回的图片URI均可使用。（必填）
 - cursor: 翻页游标（首次请求传 0）
 - search_id: 搜索ID（首次请求传空，翻页时从上次响应获取）
 - search_source: 搜索来源
    - `graphic_detail`: 图片详情页搜索（默认）
    - `visual_normal_search`: 带关键词追加搜索（需要传入 user_query）
- detection: 检测区域坐标，格式为 "x1,y1,x2,y2"
 - detection_index: 检测索引，默认 0
 - user_query: 搜索关键词，仅当 search_source="visual_normal_search" 时使用
 - aweme_id: 原视频ID，仅当 search_source="visual_normal_search" 时使用
  ### 请求体示例：
 基础图片搜索：
 ```json
 payload = {
    "image_uri": "20251221204239F0C21D7645F172B6085C",
    "cursor": 0,
    "search_id": "",
    "search_source": "graphic_detail",
    "detection": "0.1,0.1,0.9,0.9",
    "detection_index": 0
}
 ```
  带关键词的追加搜索：
 ```json
 payload = {
    "image_uri": "20251221204239F0C21D7645F172B6085C",
    "cursor": 0,
    "search_id": "2025122120452038252994F25A4BAEB043",
    "search_source": "visual_normal_search",
    "detection": "0.1,0.1,0.9,0.9",
    "detection_index": 0,
    "user_query": "游戏",
    "aweme_id": "7523532488087817529"
}
 ```
  ### 返回（部分常用字段，实际返回字段更多，一切以实际响应为准）:
 - `status_code`: 响应状态码（0为成功）
 - `cursor`: 下一页游标
 - `has_more`: 是否还有更多数据（1=有，0=无）
 - `search_id`: 搜索ID，翻页时使用
 - `data[]`: 搜索结果列表
  - `type`: 结果类型
  - `aweme_info`: 视频/图文详细信息
    - `aweme_id`: 视频ID
    - `desc`: 视频描述
    - `author`: 作者信息
    - `video`: 视频播放信息
    - `statistics`: 互动统计

## get_all_webcast_id

`POST /api/v1/douyin/web/get_all_webcast_id`

<!-- Full path: /api/v1/douyin/web/get_all_webcast_id -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 提取列表直播间号
### 参数:
- url: 直播间链接列表（最多支持20个链接）
### 返回:
- 直播间号列表

## get_author_content_hot_keywords

`GET /api/v1/douyin/xingtu_v2/get_author_content_hot_keywords`

<!-- Full path: /api/v1/douyin/xingtu_v2/get_author_content_hot_keywords -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| author_id | string | ✅ | 创作者ID/Creator author ID | 7589271892177518598 |
| keyword_type | integer |  | 热词类型/Keyword type (default: 0) | 0 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取创作者内容热词
### 参数:
- author_id: 创作者ID
- keyword_type: 热词类型，默认0
### 返回:
- 创作者内容热词数据

## get_demander_mcn_list

`GET /api/v1/douyin/xingtu_v2/get_demander_mcn_list`

<!-- Full path: /api/v1/douyin/xingtu_v2/get_demander_mcn_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| mcn_name | string |  | MCN机构名称，支持模糊搜索/MCN name, supports fuzzy search (default: '') |  |
| page | integer |  | 页码/Page number (default: 1) | 1 |
| limit | integer |  | 每页数量/Page size (default: 20) | 20 |
| order_by | string |  | 排序方式/Sort by (default: platform_scores) | platform_scores |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 搜索MCN机构列表
### 参数:
- mcn_name: MCN机构名称，支持模糊搜索
- page: 页码，默认1
- limit: 每页数量，默认20
- order_by: 排序方式，`platform_scores`=平台评分
### 返回:
- MCN机构列表数据

## get_sign_image

`GET /api/v1/douyin/xingtu/get_sign_image`

<!-- Full path: /api/v1/douyin/xingtu/get_sign_image -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| uri | string | ✅ | 图片的uri/Image URI | tos-cn-i-0813c000-ce/oMKzDA3A9QGAuebfsDIAwlDoAfCFEEzSEw8FQZ |
| durationTS | integer |  | 有效期时长（秒）/Duration in seconds (default: 86400) | 86400 |
| format | string |  | 图片格式/Image format (default: webp) | webp |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 解析星图加密图片，获取可访问的图片URL
### 参数:
- uri: 图片的uri，通常从其他星图接口返回的数据中获取
    - 例如：`tos-cn-i-0813c000-ce/oMKzDA3A9QGAuebfsDIAwlDoAfCFEEzSEw8FQZ`
- durationTS: 有效期时长（秒），默认86400（24小时）
- format: 图片格式，默认webp，支持：webp、jpg、png等
### 返回:
- 解析后的图片数据，包含可访问的图片URL

## get_webcast_id

`GET /api/v1/douyin/web/get_webcast_id`

<!-- Full path: /api/v1/douyin/web/get_webcast_id -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| url | string | ✅ | '' | https://live.douyin.com/775841227732 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 提取列表直播间号
### 参数:
- url: 直播间链接
### 返回:
- 直播间号

## open_douyin_app_to_keyword_search

`GET /api/v1/douyin/app/v3/open_douyin_app_to_keyword_search`

<!-- Full path: /api/v1/douyin/app/v3/open_douyin_app_to_keyword_search -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 关键词/Keyword | 雷军 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 生成抖音分享链接，唤起抖音APP，跳转指定关键词搜索结果。
  ### 参数:
 - keyword: 关键词
  ### 返回:
 - 分享链接

## search_kol_v1

`GET /api/v1/douyin/xingtu/search_kol_v1`

<!-- Full path: /api/v1/douyin/xingtu/search_kol_v1 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 关键词/Keyword | 抖音 |
| platformSource | string | ✅ | 平台来源/Platform Source | _1 |
| page | integer | ✅ | 页码/Page | 1 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 关键词搜索kol V1
 - 该接口数据使用企业账号进行请求，收费较贵。
 ### 参数:
 - keyword: 关键词
 - platformSource:
    - 平台来源，支持以下参数:
    - _1 :抖音(douyin)
    - _2 :头条(toutiao)
    - _3 :西瓜(xigua)
- page: 页码，从1开始
 ### 返回:
 - kol列表

## search_kol_v2

`GET /api/v1/douyin/xingtu/search_kol_v2`

<!-- Full path: /api/v1/douyin/xingtu/search_kol_v2 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 关键词/Keyword | 美妆 |
| followerRange | string |  | 粉丝范围(可选)/Follower Range (optional), 例如 10-100 表示10万-100万粉丝 | 10-100 |
| contentTag | string |  | 内容标签(可选)/Content Tag (optional), 例如 tag-1 或 tag_level_two-7 | tag-1 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 高级搜索kol V2，支持粉丝范围和内容标签筛选
 - 该接口数据使用企业账号进行请求，收费较贵。
 ### 参数:
 - keyword: 关键词
 - followerRange (可选): 粉丝范围，格式：最小值-最大值
    - 例如：10-100 表示粉丝范围在 10万-100万 之间
    - 不传递此参数则不限制粉丝范围
- contentTag (可选): 内容标签，支持以下格式:
    - tag-{id}: 一级标签，例如 tag-1 (美妆)
    - tag_level_two-{id}: 二级标签，例如 tag_level_two-7 (穿搭)
    - 标签列表参考文档中的 contentTag 映射表
    - 不传递此参数则不限制内容标签
### 返回:
 - kol列表（支持高级筛选）

## webcast_id_2_room_id

`GET /api/v1/douyin/web/webcast_id_2_room_id`

<!-- Full path: /api/v1/douyin/web/webcast_id_2_room_id -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| webcast_id | string | ✅ | 直播间号/Webcast id | 775841227732 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 直播间号转房间号
### 参数:
- webcast_id: 直播间号
### 返回:
- 房间号

---

See SKILL.md for cross-group orchestration patterns.