# Trending & Billboard API / 热榜与趋势接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---
## author_hot_comment_tokens_v1

`GET /api/v1/douyin/xingtu/author_hot_comment_tokens_v1`

<!-- Full path: /api/v1/douyin/xingtu/author_hot_comment_tokens_v1 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| kolId | string | ✅ | 用户的kolId/User kolId | 7048929565493690398 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取kol热词分析评论V1
 - 该接口数据使用企业账号进行请求，收费较贵。
 ### 参数:
 - kolId: 用户的kolId, 可以从接口以下接口获取：
    - `/api/v1/douyin/xingtu/get_xingtu_kolid_by_uid`
    - `/api/v1/douyin/xingtu/get_xingtu_kolid_by_sec_user_id`
    - `/api/v1/douyin/xingtu/get_xingtu_kolid_by_unique_id`
### 返回:
 - kol热词分析评论

## fetch_brand_initiative_rank_weekly

`POST /api/v1/douyin/index/fetch_brand_initiative_rank_weekly`

<!-- Full path: /api/v1/douyin/index/fetch_brand_initiative_rank_weekly -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| brand_name | string | ✅ | 品牌名称/Brand name |  |
| start_date | string | ✅ | 开始日期/Start date YYYYMMDD |  |
| end_date | string | ✅ | 结束日期/End date YYYYMMDD |  |
| app_name | string (aweme/toutiao) |  | '平台/Platform: aweme(抖音), toutiao(头条)' (default: aweme) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取品牌主动排行周榜数据
### 参数:
- brand_name: 品牌名称
- start_date/end_date: 日期范围
- app_name: 平台选择
### 返回:
- 品牌在该周的主动排行数据

## fetch_brand_lines

`POST /api/v1/douyin/index/fetch_brand_lines`

<!-- Full path: /api/v1/douyin/index/fetch_brand_lines -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| brand_name | string | ✅ | 品牌名称/Brand name |  |
| start_date | string | ✅ | 开始日期/Start date YYYYMMDD |  |
| end_date | string | ✅ | 结束日期/End date YYYYMMDD |  |
| app_name | string (aweme/toutiao) |  | '平台/Platform: aweme(抖音), toutiao(头条)' (default: aweme) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取品牌的趋势线数据（热度随时间变化）
### 参数:
- brand_name: 品牌名称
- start_date/end_date: 日期范围
- app_name: 平台选择
### 返回:
- 品牌热度趋势线数据

## fetch_city_list

`GET /api/v1/douyin/billboard/fetch_city_list`

<!-- Full path: /api/v1/douyin/billboard/fetch_city_list -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取城市列表
### 参数:
- 无
### 返回:
- 中国城市列表

## fetch_content_author_portrait

`POST /api/v1/douyin/index/fetch_content_author_portrait`

<!-- Full path: /api/v1/douyin/index/fetch_content_author_portrait -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| tag_id | string | ✅ | >- |  |
| period | string (week/month) |  | '时间粒度/Period: week or month' (default: month) |  |
| end_date | string | ✅ | 结束日期/End date YYYYMMDD |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定垂类下**创作者**人群画像（即"发布该垂类视频的作者"画像）
 - 用于了解某垂类创作者的性别、年龄、地域、活跃时段等特征
 ### 参数:
 - tag_id: 垂类ID（**必填，不支持 0=全部**，需传入具体垂类 ID，可通过 fetch_item_filter_options
获取）
 - period: 时间粒度，"week"=按周（end_date 必须为周日）, "month"=按月（end_date 必须为月末，如
20260331）
 - end_date: 结束日期 YYYYMMDD，需与 period 对齐
 ### 返回:
 - 创作者画像数据：性别分布、年龄段分布、地域分布、设备分布、活跃时段等

## fetch_content_consume_trend

`POST /api/v1/douyin/index/fetch_content_consume_trend`

<!-- Full path: /api/v1/douyin/index/fetch_content_consume_trend -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| tag_id | string | ✅ | >- |  |
| start_date | string | ✅ | 开始日期/Start date YYYYMMDD |  |
| end_date | string | ✅ | 结束日期/End date YYYYMMDD |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定垂类的消费数据（播放量、观看时长等）随时间变化趋势
 - 衡量该垂类内容被用户实际消费（观看）的热度变化
 ### 参数:
 - tag_id: 垂类ID（**必填，不支持 0=全部**，需传入具体垂类 ID，可通过 fetch_item_filter_options
获取）
 - start_date: 起始日期 YYYYMMDD（含）
 - end_date: 结束日期 YYYYMMDD（含）
 ### 返回:
 - 按日聚合的消费数据：每日播放总量、观看时长、独立观看人数等

## fetch_content_consumer_portrait

`POST /api/v1/douyin/index/fetch_content_consumer_portrait`

<!-- Full path: /api/v1/douyin/index/fetch_content_consumer_portrait -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| tag_id | string | ✅ | >- |  |
| period | string (week/month) |  | '时间粒度/Period: week or month' (default: month) |  |
| end_date | string | ✅ | 结束日期/End date YYYYMMDD |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定垂类下**消费者**人群画像（即"观看该垂类视频的用户"画像）
 - 与 fetch_content_author_portrait 互为补充：一个看作者，一个看观众
 ### 参数:
 - tag_id: 垂类ID（**必填，不支持 0=全部**，需传入具体垂类 ID，可通过 fetch_item_filter_options
获取）
 - period: 时间粒度，"week"=按周（end_date 必须为周日）, "month"=按月（end_date 必须为月末，如
20260331）
 - end_date: 结束日期 YYYYMMDD，需与 period 对齐
 ### 返回:
 - 消费者画像数据：性别分布、年龄段分布、地域分布、兴趣偏好、设备分布等

## fetch_content_creative_duration

`POST /api/v1/douyin/index/fetch_content_creative_duration`

<!-- Full path: /api/v1/douyin/index/fetch_content_creative_duration -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| tag_id | string | ✅ | >- |  |
| period | string (week/month) |  | '时间粒度/Period: week=周, month=月' (default: week) |  |
| end_date | string | ✅ | 结束日期/End date YYYYMMDD |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定垂类下视频时长分布数据
 - 用于了解该垂类创作者偏好的视频时长结构
 ### 参数:
 - tag_id: 垂类ID（**必填，不支持 0=全部**，需传入具体垂类 ID，可通过 fetch_item_filter_options
获取）
 - period: 时间粒度，"week"=按周（end_date 必须为周日）, "month"=按月（end_date 必须为月末）
 - end_date: 结束日期 YYYYMMDD，需与 period 对齐
 ### 返回:
 - 各时长区间（如 0-15 秒/15-60 秒/60-180 秒/大于 180 秒）的视频数量与占比

## fetch_content_interact_trend

`POST /api/v1/douyin/index/fetch_content_interact_trend`

<!-- Full path: /api/v1/douyin/index/fetch_content_interact_trend -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| tag_id | string | ✅ | >- |  |
| start_date | string | ✅ | 开始日期/Start date YYYYMMDD |  |
| end_date | string | ✅ | 结束日期/End date YYYYMMDD |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定垂类的互动数据（点赞/评论/分享/收藏等）随时间变化趋势
 - 衡量该垂类内容引发用户互动的活跃程度
 ### 参数:
 - tag_id: 垂类ID（**必填，不支持 0=全部**，需传入具体垂类 ID，可通过 fetch_item_filter_options
获取）
 - start_date: 起始日期 YYYYMMDD（含）
 - end_date: 结束日期 YYYYMMDD（含）
 ### 返回:
 - 按日聚合的互动数据：每日点赞总数、评论总数、分享总数、收藏总数等

## fetch_content_publish_trend

`GET /api/v1/douyin/index/fetch_content_publish_trend`

<!-- Full path: /api/v1/douyin/index/fetch_content_publish_trend -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| tag_id | string | ✅ | >- |  |
| start_date | string | ✅ | 开始日期/Start date YYYYMMDD |  |
| end_date | string | ✅ | 结束日期/End date YYYYMMDD |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定垂类的视频发布数量随时间变化趋势
 - 用于了解某垂类的内容供给热度变化
 ### 参数:
 - tag_id: 垂类ID（**必填，不支持 0=全部**，需传入具体垂类 ID，可通过 fetch_item_filter_options
获取）
 - start_date: 起始日期 YYYYMMDD（含）
 - end_date: 结束日期 YYYYMMDD（含）
 ### 返回:
 - 按日聚合的发布量数据（日期 + 当日发布作品数）

## fetch_content_tag

`GET /api/v1/douyin/billboard/fetch_content_tag`

<!-- Full path: /api/v1/douyin/billboard/fetch_content_tag -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取垂类内容标签
 ### 参数:
 - 无
 ### 返回:
 - 垂类内容标签
 ### 注意:
 - 该接口用于获取垂类内容标签，用于query_tag参数构建
 ### 示例:
 已知顶级垂类内容标签 `美食`，它的顶级垂类id为 `628`；`美食` 的子垂类标签 `品酒教学`，它的子垂类id为 `62802`。
 那么构建标签查询参数为 `{"value": 628, "children": [{"value": 62808}]}`
  如果需要多个子垂类标签，所有的美食子垂类标签为
`{"value":628,"children":[{"value":62808},{"value":62804},{"value":62806},{"value":62803},{"value":62802},{"value":62801},{"value":62811},{"value":62807},{"value":62805},{"value":62810}]}`

## fetch_content_valid_date

`GET /api/v1/douyin/index/fetch_content_valid_date`

<!-- Full path: /api/v1/douyin/index/fetch_content_valid_date -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取创作指南各类型数据的有效日期范围
### 返回:
- 创作指南可查询的起止日期

## fetch_creator_activity_list

`GET /api/v1/douyin/creator/fetch_creator_activity_list`

<!-- Full path: /api/v1/douyin/creator/fetch_creator_activity_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| start_time | integer | ✅ | 开始时间戳/Start timestamp | 1756656000 |
| end_time | integer | ✅ | 结束时间戳/End timestamp | 1759247999 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取抖音创作者活动列表数据
### 参数:
- start_time: 开始时间戳
- end_time: 结束时间戳
### 返回:
- 创作者活动列表数据

## fetch_creator_content_category

`GET /api/v1/douyin/creator/fetch_creator_content_category`

<!-- Full path: /api/v1/douyin/creator/fetch_creator_content_category -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取抖音创作者平台内容创作的合集分类列表
### 参数:
- 无需额外参数
### 返回:
- 内容创作合集分类数据

## fetch_creator_content_course

`GET /api/v1/douyin/creator/fetch_creator_content_course`

<!-- Full path: /api/v1/douyin/creator/fetch_creator_content_course -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| category_id | integer | ✅ | 分类ID/Category ID | 180 |
| order | integer |  | 排序方式/Order type (1=推荐排序, 2=最受欢迎, 3=最新上传) (default: 1) | 1 |
| limit | integer |  | 每页数量/Items per page (default: 24) | 24 |
| offset | integer |  | 偏移量/Offset (starting position) (default: 0) | 0 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取抖音创作者平台指定分类的内容创作课程
 ### 参数:
 - category_id: 分类ID (更多分类ID请通过内容创作合集分类接口获取)
    常见分类ID示例:
    - 184: 视频创作
    - 185: 直播创作
    - 186: 图文创作
    - 188: 美食视频创作
    - 180: 内容创作基础
- order: 排序方式 (1=推荐排序, 2=最受欢迎, 3=最新上传)
 - limit: 每页数量 (建议24，范围1-100)
 - offset: 偏移量 (起始位置)
 ### 返回:
 - 指定分类的内容创作课程数据

## fetch_creator_hot_challenge_billboard

`GET /api/v1/douyin/creator/fetch_creator_hot_challenge_billboard`

<!-- Full path: /api/v1/douyin/creator/fetch_creator_hot_challenge_billboard -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取抖音创作者平台热门挑战榜单数据
 ### 返回:
 - 热门挑战榜单数据

## fetch_creator_hot_course

`GET /api/v1/douyin/creator/fetch_creator_hot_course`

<!-- Full path: /api/v1/douyin/creator/fetch_creator_hot_course -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| order | integer |  | 排序方式/Order type (1=推荐排序, 2=最受欢迎, 3=最新上传) (default: 1) | 1 |
| limit | integer |  | 每页数量/Items per page (建议24) (default: 24) | 24 |
| offset | integer |  | 偏移量/Offset (default: 0) | 0 |
| category_id | string |  | \|- |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取抖音创作者平台热门课程数据或精选专题课程
 ### 参数:
 - order: 排序方式 (1=推荐排序, 2=最受欢迎, 3=最新上传)
 - limit: 每页数量 (建议24，范围1-100)
 - offset: 偏移量 (起始位置)
 - category_id: 精选专题分类ID (不传则获取热门课程，传入则获取指定分类的精选专题)
    可选值:
    - 6976547830546582816: 知识品类
    - 6976547923849006336: 生活品类
    - 6976547940311633165: 娱乐品类
    - 6976547972108635404: 美食品类
    - 6980288134957272352: 正能量
    - 6980288181744766219: 游戏品类
    - 6980288219548011776: 通用
### 返回:
 - 热门课程数据或精选专题课程数据

## fetch_creator_hot_props_billboard

`GET /api/v1/douyin/creator/fetch_creator_hot_props_billboard`

<!-- Full path: /api/v1/douyin/creator/fetch_creator_hot_props_billboard -->

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
 - 获取抖音创作者热门道具榜单数据
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
    - 5: 投稿最多
    - 6: 展现最高
    - 7: 收藏最高
- time_filter: 时间筛选
    - 1: 24小时
    - 2: 7天
    - 3: 30天
### 返回:
 - 创作者热门道具榜单数据

## fetch_creator_hot_spot_billboard

`GET /api/v1/douyin/creator/fetch_creator_hot_spot_billboard`

<!-- Full path: /api/v1/douyin/creator/fetch_creator_hot_spot_billboard -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| billboard_tag | string |  | >- (default: '0') |  |
| hot_search_type | integer |  | >- (default: 1) |  |
| city_code | string |  | >- |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取抖音创作者热点榜单数据
### 参数:
- billboard_tag: 热点标签，多个标签用逗号分隔
    可选值:
    - 站内玩法: 1004,1000,1002,1003,1001
    - 话题互动: 20001,20006,20000,20003,20005,20002,20
    - 娱乐: 2007,2000,2011,2012,2009,2010,2004,2005,2003,2008,2001,2002,2006
    - 社会: 4005,4006,4007,4003,4004,4000
    - 二次元: 13000
    - 交通: 23000
    - 亲子: 19000
    - 体育: 5002,5000,5001
    - 军事: 21000
    - 剧情: 18000
    - 动物萌宠: 8000
    - 天气: 22001,22002
    - 才艺: 17000
    - 文化教育: 14000
    - 旅行: 10000
    - 时尚: 16000
    - 时政: 3000,3001,3002
    - 校园: 15000
    - 汽车: 11000
    - 游戏: 12000,12001
    - 科技: 6000
    - 美食: 9000
    - 财经: 7000
- hot_search_type: 热搜类型
    - 1: 热点总榜
    - 2: 同城热点榜
    - 3: 热点上升榜
- city_code: 城市代码，当hot_search_type=2时必需
### 返回:
- 创作者热点榜单数据

## fetch_current_hot_topic

`GET /api/v1/douyin/index/fetch_current_hot_topic`

<!-- Full path: /api/v1/douyin/index/fetch_current_hot_topic -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取抖音实时热点和飙升热点排行榜
### 返回:
- 热点名称、热点指数、排名变化等信息

## fetch_hot_account_fans_interest_topic_list

`GET /api/v1/douyin/billboard/fetch_hot_account_fans_interest_topic_list`

<!-- Full path: /api/v1/douyin/billboard/fetch_hot_account_fans_interest_topic_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| sec_uid | string | ✅ | 用户sec_id | MS4wLjABAAAA8U_l6rBzmy7bcy6xOJel4v0RzoR_wfAubGPeJimN__4 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取粉丝近3天感兴趣的话题 10个话题
### 参数:
- sec_uid: 用户sec_id
### 返回:
- 粉丝近3天感兴趣的话题 10个话题

## fetch_hot_account_list

`POST /api/v1/douyin/billboard/fetch_hot_account_list`

<!-- Full path: /api/v1/douyin/billboard/fetch_hot_account_list -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取热门账号
 ### 参数:
 - date_window: 时间窗口，格式 小时，默认24小时
 - page_num: 页码，默认1
 - page_size: 每页数量，默认20
 - query_tag: 子级垂类标签，空则为全部，多个标签需传入
 {"value": "{顶级垂类标签id}", "children": [
    {"value": "{子级垂类标签id}"},
    {"value": "{子级垂类标签id}"}
]}
 ### 返回:
 - 热门账号

## fetch_hot_calendar_list

`POST /api/v1/douyin/billboard/fetch_hot_calendar_list`

<!-- Full path: /api/v1/douyin/billboard/fetch_hot_calendar_list -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取活动日历
 ### 参数:
 - city_code: 城市编码，从城市列表获取，空为全部
 - category_code: 热点榜分类编码，从热点榜分类获取，空为全部
 - end_date: 快照结束时间 格式10位时间戳
 - start_date: 快照开始时间 格式10位时间戳
 ### 返回:
 - 活动日历

## fetch_hot_category_list

`GET /api/v1/douyin/billboard/fetch_hot_category_list`

<!-- Full path: /api/v1/douyin/billboard/fetch_hot_category_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| billboard_type | string | ✅ | 榜单类型 | rise |
| snapshot_time | string |  | 快照时间 格式yyyyMMddHHmmss (default: '20250106151500') |  |
| start_date | string |  | 快照开始时间 格式yyyyMMdd (default: '') |  |
| end_date | string |  | 快照结束时间 格式yyyyMMdd (default: '') |  |
| keyword | string |  | 热点搜索词 (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取热点榜分类的id与热度
 - 注意：使用start_date和end_date参数需要移除snapshot_time参数才可以生效
 ### 参数:
 - billboard_type: 榜单类型
    - rise 上升热点榜
    - city 城市热点榜
    - total 热点总榜
- snapshot_time: 快照时间
 - start_date: 快照开始时间
 - end_date: 快照结束时间
 - keyword: 热点搜索词
 ### 返回:
 - 热点榜分类

## fetch_hot_challenge_list

`GET /api/v1/douyin/billboard/fetch_hot_challenge_list`

<!-- Full path: /api/v1/douyin/billboard/fetch_hot_challenge_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| page | integer | ✅ | 页码 | 1 |
| page_size | integer | ✅ | 每页数量 | 10 |
| keyword | string |  | 热点搜索词 (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取挑战榜
### 参数:
- page: 页码
- page_size: 每页数量
- keyword: 热点搜索词
### 返回:
- 挑战榜

## fetch_hot_city_list

`GET /api/v1/douyin/billboard/fetch_hot_city_list`

<!-- Full path: /api/v1/douyin/billboard/fetch_hot_city_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| page | integer | ✅ | 页码 | 1 |
| page_size | integer | ✅ | 每页数量 | 10 |
| order | string | ✅ | 排序方式 |  |
| city_code | string |  | 城市编码，从城市列表获取，空为全部 (default: '') |  |
| sentence_tag | string |  | 热点分类标签，从热点榜分类获取，多个分类用逗号分隔，空为全部 (default: '') |  |
| keyword | string |  | 热点搜索词 (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取同城热点榜
 ### 参数:
 - page: 页码
 - page_size: 每页数量
 - order: 排序方式
    - rank 按热度排序
    - rank_diff 按排名变化
- city_code: 城市编码，从城市列表获取，空为全部
 - sentence_tag: 热点分类标签，从热点榜分类获取，多个分类用逗号分隔，空为全部
 - keyword: 热点搜索词
 ### 返回:
 - 同城热点榜

## fetch_hot_rise_list

`GET /api/v1/douyin/billboard/fetch_hot_rise_list`

<!-- Full path: /api/v1/douyin/billboard/fetch_hot_rise_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| page | integer | ✅ | 页码 | 1 |
| page_size | integer | ✅ | 每页数量 | 10 |
| order | string | ✅ | 排序方式 | rank |
| sentence_tag | string |  | 热点分类标签，从热点榜分类获取，多个分类用逗号分隔，空为全部 (default: '') |  |
| keyword | string |  | 热点搜索词 (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取上升热点榜
 ### 参数:
 - page: 页码
 - page_size: 每页数量
 - order: 排序方式
    - rank 按热度排序
    - rank_diff 按排名变化
- sentence_tag: 热点分类标签，从热点榜分类获取，多个分类用逗号分隔，空为全部
 - keyword: 热点搜索词
 ### 返回:
 - 上升热点榜

## fetch_hot_total_high_fan_list

`POST /api/v1/douyin/billboard/fetch_hot_total_high_fan_list`

<!-- Full path: /api/v1/douyin/billboard/fetch_hot_total_high_fan_list -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取高涨粉率榜
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
 - 高涨粉率榜

## fetch_hot_total_hot_word_list

`POST /api/v1/douyin/billboard/fetch_hot_total_hot_word_list`

<!-- Full path: /api/v1/douyin/billboard/fetch_hot_total_hot_word_list -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取全部内容词
### 参数:
- page_num: 页码
- page_size: 每页数量
- date_window: 时间窗口，1 按小时 2 按天
- keyword: 搜索关键字
### 返回:
- 全部内容词

## fetch_hot_total_list

`GET /api/v1/douyin/billboard/fetch_hot_total_list`

<!-- Full path: /api/v1/douyin/billboard/fetch_hot_total_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| page | integer | ✅ | 页码 | 1 |
| page_size | integer | ✅ | 每页数量 | 10 |
| type | string | ✅ | 快照类型 snapshot 按时刻查看 range 按时间范围 |  |
| snapshot_time | string |  | 快照时间 格式yyyyMMddHHmmss (default: '20250106151500') |  |
| start_date | string |  | 快照开始时间 格式yyyyMMdd (default: '') |  |
| end_date | string |  | 快照结束时间 格式yyyyMMdd (default: '') |  |
| sentence_tag | string |  | 热点分类标签，从热点榜分类获取，多个分类用逗号分隔，空为全部 (default: '') |  |
| keyword | string |  | 热点搜索词 (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取热点总榜
 ### 参数:
 - page: 页码
 - page_size: 每页数量
 - type: 快照类型 snapshot 按时刻查看 range 按时间范围。
    - 备注：snapshot_time 在 snapshot时有效，start_date 和 end_date 在 range 时有效
- snapshot_time: 快照时间 格式yyyyMMddHHmmss
 - start_date: 快照开始时间 格式yyyyMMdd
 - end_date: 快照结束时间 格式yyyyMMdd
 - sentence_tag: 热点分类标签，从热点榜分类获取，多个分类用逗号分隔，空为全部
 - keyword: 热点搜索词
 ### 返回:
 - 热点总榜

## fetch_hot_total_low_fan_list

`POST /api/v1/douyin/billboard/fetch_hot_total_low_fan_list`

<!-- Full path: /api/v1/douyin/billboard/fetch_hot_total_low_fan_list -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取低粉爆款榜
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
 - 低粉爆款榜

## fetch_relation_word

`POST /api/v1/douyin/index/fetch_relation_word`

<!-- Full path: /api/v1/douyin/index/fetch_relation_word -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 关键词/Keyword |  |
| start_date | string | ✅ | 开始日期（周一）/Start date (Monday) YYYYMMDD |  |
| end_date | string | ✅ | 结束日期（必须为周日）/End date (must be Sunday) YYYYMMDD |  |
| app_name | string (aweme/toutiao) |  | '平台/Platform: aweme(抖音), toutiao(头条)' (default: aweme) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取关键词的关联词分析，包含搜索关联词和内容关联词
 - 展示关联词图谱和关联词排名
 ### 参数:
 - keyword: 要分析的关键词
 - start_date: 开始日期（建议为周一），格式 YYYYMMDD
 - end_date: 结束日期（**必须为周日**），格式 YYYYMMDD
 - app_name: 平台选择，aweme=抖音，toutiao=头条
 ### 注意:
 - **关联分析的日期范围必须以周日为终止日期**，例如 start_date=20260330, end_date=20260405（周日）
 - 如果 end_date 不是周日，接口可能返回空数据
 ### 返回:
 - 搜索关联词列表、内容关联词列表、关联词图谱数据

## get_author_hot_comment_tokens

`GET /api/v1/douyin/xingtu_v2/get_author_hot_comment_tokens`

<!-- Full path: /api/v1/douyin/xingtu_v2/get_author_hot_comment_tokens -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| author_id | string | ✅ | 创作者ID/Creator author ID | 7589271892177518598 |
| num | integer |  | 返回热词数量/Number of hot tokens (default: 10) | 10 |
| without_emoji | boolean |  | 是否排除emoji/Whether to exclude emoji (default: true) | true |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取创作者评论热词
### 参数:
- author_id: 创作者ID
- num: 返回热词数量，默认10
- without_emoji: 是否排除emoji，默认True
### 返回:
- 创作者评论热词数据

## get_ip_activity_industry_list

`GET /api/v1/douyin/xingtu_v2/get_ip_activity_industry_list`

<!-- Full path: /api/v1/douyin/xingtu_v2/get_ip_activity_industry_list -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取星图IP日历的行业列表
### 返回:
- 行业列表数据

## get_ip_activity_list

`POST /api/v1/douyin/xingtu_v2/get_ip_activity_list`

<!-- Full path: /api/v1/douyin/xingtu_v2/get_ip_activity_list -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取星图IP日历活动列表
 ### 参数:
 - query_start_time: 查询开始时间戳，如`1767196800`
 - query_end_time: 查询结束时间戳，如`1774972799`
 - industry_id_list (可选): 行业ID列表，从`get_ip_activity_industry_list`获取
    - 例：`["1930"]`=美妆, `["1901"]`=3C及电器, `["1903"]`=食品饮料
- category_list (可选): IP类型列表
    - 1=星图大事件, 2=电商节点, 3=情绪节点, 4=创意营销, 5=行业活动
- status_list (可选): IP状态列表
    - 40=筹备中, 50=招商中, 30=资源上线, 20=已结束
### 返回:
 - IP日历活动列表数据

## get_ranking_list_catalog

`GET /api/v1/douyin/xingtu_v2/get_ranking_list_catalog`

<!-- Full path: /api/v1/douyin/xingtu_v2/get_ranking_list_catalog -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| codes | string |  | 分类代码，默认为空字符串/Classification codes, default is empty string (default: '') |  |
| biz_scene | string |  | 业务场景/Business scene (default: douyin_flow_split_video_author_ranks) | douyin_flow_split_video_author_ranks |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取星图热榜分类列表，返回qualifier_id等分类信息
 ### 参数:
 - codes: 分类代码，默认为空字符串
 - biz_scene: 业务场景
    - `douyin_flow_split_video_author_ranks`: 短视频达人热榜
    - `douyin_flow_split_live_author_ranks`: 直播达人热榜
### 返回:
 - 热榜分类数据

## get_ranking_list_data

`GET /api/v1/douyin/xingtu_v2/get_ranking_list_data`

<!-- Full path: /api/v1/douyin/xingtu_v2/get_ranking_list_data -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| code | integer |  | 榜单类型代码/Ranking type code (default: 1) | 1 |
| qualifier | string |  | 榜单分类ID，从get_ranking_list_catalog获取/Category qualifier_id (default: '1901') | 1901 |
| version | string |  | 版本/Version (default: flow_split) | flow_split |
| period | integer |  | 统计周期，7=周榜，30=月榜/Period, 7=weekly, 30=monthly (default: 30) | 30 |
| date | string |  | 统计日期，格式YYYYMMDD/Date, format YYYYMMDD (default: '20260131') | 20260131 |
| limit | integer |  | 返回数量/Result limit (default: 100) | 100 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取星图达人商业榜数据
 - qualifier可以从`get_ranking_list_catalog`接口获取
 ### 参数:
 - code: 榜单类型代码
    - 短视频-达人商业榜: 1=品牌优选榜, 2=A3种草榜, 3=看后搜榜, 4=带货榜, 5=投流榜, 6=高潜榜
    - 短视频-达人内容榜: 17=涨粉黑马榜, 18=头部必选榜
    - 直播达人榜-主播类型: 23=游戏主播, 30=其他主播, 37=带货主播 (version=base)
    - 直播达人榜-榜单类型: 23=游戏行业品牌优选榜, 24=非游戏行业品牌优选榜, 25=组件点击榜, 26=下载转化榜, 27=线索收集榜, 28=投流榜, 29=高潜榜
- qualifier: 榜单分类ID，从`get_ranking_list_catalog`获取
 - version: 版本，`flow_split`=短视频榜单默认，`base`=直播榜单常用
 - period: 统计周期，7=周榜，30=月榜
 - date: 统计日期，格式YYYYMMDD
 - limit: 返回数量，默认100
 ### 返回:
 - 达人商业榜数据

---

See SKILL.md for cross-group orchestration patterns.