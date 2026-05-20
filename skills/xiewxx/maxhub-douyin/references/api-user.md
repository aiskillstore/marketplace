# User Data API / 用户数据接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---
## encrypt_uid_to_sec_user_id

`GET /api/v1/douyin/web/encrypt_uid_to_sec_user_id`

<!-- Full path: /api/v1/douyin/web/encrypt_uid_to_sec_user_id -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| uid | string | ✅ | 用户uid(short_id)/User uid(short_id) | 1673937488185292 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 加密用户uid到sec_user_id
### 参数:
- uid: 用户uid，也就是抖音号的short_id
### 返回:
- 用户信息

## fetch_batch_user_profile_v1

`GET /api/v1/douyin/web/fetch_batch_user_profile_v1`

<!-- Full path: /api/v1/douyin/web/fetch_batch_user_profile_v1 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| sec_user_ids | string | ✅ | 用户sec_user_id列表，用逗号分隔/User sec_user_id list, separated by commas | >- |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取批量用户信息，最多支持10个用户
 ### 参数:
 - sec_user_ids: 用户sec_user_id列表，用逗号分隔，最多10个
 ### 返回:
 - 批量用户信息

## fetch_batch_user_profile_v2

`GET /api/v1/douyin/web/fetch_batch_user_profile_v2`

<!-- Full path: /api/v1/douyin/web/fetch_batch_user_profile_v2 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| sec_user_ids | string | ✅ | 用户sec_user_id列表，用逗号分隔/User sec_user_id list, separated by commas | >- |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取批量用户信息，最多支持50个用户
 ### 参数:
 - sec_user_ids: 用户sec_user_id列表，用逗号分隔，最多50个
 ### 返回:
 - 批量用户信息

## fetch_daren_compare_users_stable

`POST /api/v1/douyin/index/fetch_daren_compare_users_stable`

<!-- Full path: /api/v1/douyin/index/fetch_daren_compare_users_stable -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_list | string | ✅ | 达人抖音 uid 列表，逗号分隔，最多5个 / Daren uid list, comma separated, max 5 |  |
| days | string ('7'/'30') |  | '天数/Days: 7 or 30' (default: '7') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 对比多个达人的趋势数据（粉丝增长、互动量等）
 ### 参数:
 - user_list: 达人抖音 uid 列表，逗号分隔，**最多5个**
 - days: 对比天数，仅支持 7 或 30
 ### 返回:
 - 每个达人在指定天数内的趋势数据对比

## fetch_daren_great_user_fans_info

`POST /api/v1/douyin/index/fetch_daren_great_user_fans_info`

<!-- Full path: /api/v1/douyin/index/fetch_daren_great_user_fans_info -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string | ✅ | '达人抖音 uid (纯数字) / Douyin uid (numeric). Example: 3100268042915212' |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取达人粉丝分析数据
### 参数:
- user_id: 达人抖音 uid（纯数字，如 "3100268042915212"）
### 返回:
- 粉丝性别分布、年龄分布、地域分布、活跃时间等

## fetch_daren_similar_users

`POST /api/v1/douyin/index/fetch_daren_similar_users`

<!-- Full path: /api/v1/douyin/index/fetch_daren_similar_users -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string | ✅ | '达人抖音 uid (纯数字) / Douyin uid (numeric). Example: 3100268042915212' |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取与指定达人相似的达人列表
### 参数:
- user_id: 达人抖音 uid（纯数字，如 "3100268042915212"）
### 返回:
- 相似达人列表

## fetch_daren_sug_great_user_list

`POST /api/v1/douyin/index/fetch_daren_sug_great_user_list`

<!-- Full path: /api/v1/douyin/index/fetch_daren_sug_great_user_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 搜索关键词/Search keyword |  |
| total | string |  | 返回数量/Return count (default: '20') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 搜索达人，获取达人列表建议
 ### 参数:
 - keyword: 达人昵称关键词
 - total: 返回数量，默认20
 ### 返回:
 - 匹配的达人列表（包含达人ID、昵称、头像、粉丝数等）

## fetch_encrypt_user_id

`GET /api/v1/douyin/index/fetch_encrypt_user_id`

<!-- Full path: /api/v1/douyin/index/fetch_encrypt_user_id -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| uid | string | ✅ | '抖音 uid (纯数字) / Douyin uid (numeric). Example: 3100268042915212' |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 将抖音 uid（纯数字）转换为抖音指数 API 内部使用的加密 user_id
 - 达人相关接口（如 fetch_daren_similar_users、fetch_daren_great_item_mile_info 等）
  已自动处理此转换，通常无需手动调用本接口
- 本接口仅用于调试或需要直接拿到加密 user_id 的特殊场景
 ### 参数:
 - uid: 抖音 uid，纯数字字符串
 ### 返回:
 - uid: 原始输入的抖音 uid
 - user_id: 加密后的 user_id

## fetch_get_user_sub_word

`POST /api/v1/douyin/index/fetch_get_user_sub_word`

<!-- Full path: /api/v1/douyin/index/fetch_get_user_sub_word -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取当前登录用户在抖音指数中订阅的关键词列表
 ### 返回:
 - 用户已订阅的关键词列表

## fetch_hot_account_fans_interest_account_list

`GET /api/v1/douyin/billboard/fetch_hot_account_fans_interest_account_list`

<!-- Full path: /api/v1/douyin/billboard/fetch_hot_account_fans_interest_account_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| sec_uid | string | ✅ | 用户sec_id | MS4wLjABAAAA8U_l6rBzmy7bcy6xOJel4v0RzoR_wfAubGPeJimN__4 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取粉丝兴趣作者 20个用户
### 参数:
- sec_uid: 用户sec_id
### 返回:
- 粉丝兴趣作者 20个用户

## fetch_hot_account_fans_portrait_list

`GET /api/v1/douyin/billboard/fetch_hot_account_fans_portrait_list`

<!-- Full path: /api/v1/douyin/billboard/fetch_hot_account_fans_portrait_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| sec_uid | string | ✅ | 用户sec_id | MS4wLjABAAAA8U_l6rBzmy7bcy6xOJel4v0RzoR_wfAubGPeJimN__4 |
| option | integer |  | >- (default: 1) | 1 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取粉丝画像
### 参数:
- sec_uid: 用户sec_id
- option: 选项，默认值为：1 手机价格分布
    - `1` = 手机价格分布
    - `2` = 性别分布
    - `3` = 年龄分布
    - `4` = 地域分布-省份
    - `5` = 地域分布-城市
    - `6` = 城市等级
    - `7` = 手机品牌分布
    - `8` = 兴趣标签分析 百分比
### 返回:
- 粉丝画像

## fetch_hot_account_search_list

`GET /api/v1/douyin/billboard/fetch_hot_account_search_list`

<!-- Full path: /api/v1/douyin/billboard/fetch_hot_account_search_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 搜索的用户名或抖音号 | rmrbxmt |
| cursor | integer | ✅ | 游标，默认空 | 0 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取搜索用户名或抖音号
### 参数:
- keyword: 搜索的用户名或抖音号
- cursor: 游标，默认空
### 返回:
- 搜索结果

## fetch_hot_account_trends_list

`GET /api/v1/douyin/billboard/fetch_hot_account_trends_list`

<!-- Full path: /api/v1/douyin/billboard/fetch_hot_account_trends_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| sec_uid | string | ✅ | 用户sec_id | MS4wLjABAAAA8U_l6rBzmy7bcy6xOJel4v0RzoR_wfAubGPeJimN__4 |
| option | integer |  | 选项，2 新增点赞量 3 新增作品量 4 新增评论量 5 新增分享量 (default: 2) |  |
| date_window | integer |  | 时间窗口，1 按小时 2 按天 (default: 24) | 24 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取账号粉丝数据趋势
### 参数:
- sec_uid: 用户sec_id
- option: 选项，2 新增点赞量 3 新增作品量 4 新增评论量 5 新增分享量
- date_window: 时间窗口，1 按小时 2 按天
### 返回:
- 账号粉丝数据趋势

## fetch_hot_total_high_like_list

`POST /api/v1/douyin/billboard/fetch_hot_total_high_like_list`

<!-- Full path: /api/v1/douyin/billboard/fetch_hot_total_high_like_list -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取高点赞率榜
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
 - 高点赞率榜

## fetch_live_gift_ranking

`GET /api/v1/douyin/web/fetch_live_gift_ranking`

<!-- Full path: /api/v1/douyin/web/fetch_live_gift_ranking -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| room_id | string | ✅ | 直播间room_id/Room room_id | 7356585666190461731 |
| rank_type | integer |  | 排行类型/Leaderboard type (default: 30) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取直播间送礼用户排行榜
### 参数:
- room_id: 直播间room_id
- rank_type: 排行类型，默认为30不用修改。
### 返回:
- 排行榜数据

## fetch_live_hot_search_list

`GET /api/v1/douyin/app/v3/fetch_live_hot_search_list`

<!-- Full path: /api/v1/douyin/app/v3/fetch_live_hot_search_list -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取抖音直播热搜榜数据
### 返回:
- 直播热搜榜数据

## fetch_live_room_history_list

`POST /api/v1/douyin/creator_v2/fetch_live_room_history_list`

<!-- Full path: /api/v1/douyin/creator_v2/fetch_live_room_history_list -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取抖音创作者的直播场次历史记录
 - 查看指定时间范围内的所有直播场次数据
 - 支持查询正在进行的直播和历史直播记录
 - **此接口需要用户提供有效的抖音创作者平台Cookie**
> ⚠️ **Security Notice / 安全提示**
> - This endpoint requires your platform session Cookie, which is a sensitive credential equivalent to a login session.
> - **Only provide your Cookie if you fully trust the service provider.**
> - Prefer using scoped OAuth/API tokens over full browser cookies when available.
> - Use a separate test account rather than your primary account.
> - Rotate or revoke your Cookie after use if possible.
> - 此端点需要您的平台会话 Cookie，这是等同于登录会话的敏感凭据。
> - **仅在完全信任服务提供商的情况下提供 Cookie。**
> - 尽可能使用范围限定的 OAuth/API 令牌而非完整浏览器 Cookie。
> - 使用独立的测试账号而非主账号。
> - 使用后尽可能轮换或撤销 Cookie。
 - **使用 POST 方法，Cookie 在请求体中传输，更安全**
  ### 请求体参数:
 - cookie: 用户的抖音创作者平台Cookie（必填，在请求体中传输）
> 📋 **Data Handling Disclosure / 数据处理披露**
> - Your Cookie/session data will be transmitted to a third-party API service (`https://www.aconfig.cn`) for processing.
> - The service provider processes your data solely to fulfill the API request and does not store your credentials beyond the request lifecycle.
> - For details, refer to the service provider's privacy policy and terms of service.
> - 您的 Cookie/会话数据将传输至第三方 API 服务进行处理。
> - 服务提供商仅处理您的数据以完成 API 请求，不会在请求生命周期之外存储您的凭据。
> - 详见服务提供商的隐私政策和服务条款。
> 📋 **Data Handling Disclosure / 数据处理披露**
> - Your Cookie/session data will be transmitted to a third-party API service (`https://www.aconfig.cn`) for processing.
> - The service provider processes your data solely to fulfill the API request and does not store your credentials beyond the request lifecycle.
> - For details, refer to the service provider's privacy policy and terms of service.
> - 您的 Cookie/会话数据将传输至第三方 API 服务进行处理。
> - 服务提供商仅处理您的数据以完成 API 请求，不会在请求生命周期之外存储您的凭据。
> - 详见服务提供商的隐私政策和服务条款。
 - start_date: 开始日期，格式为 YYYY-MM-DD（必填，例如: "2025-09-11"）
 - end_date: 结束日期，格式为 YYYY-MM-DD（必填，例如: "2025-10-11"）
 - limit: 每页数量限制，默认400，最多400条
 - need_living: 是否包含正在直播的场次（0=不包含, 1=包含，默认1）
 - download: 是否下载（0=不下载, 1=下载，默认0）
  ### 返回数据说明:
 返回直播场次历史记录列表，数据位于 `data.data.series` 数组中，每个场次包含以下信息：
  **基本信息**:
 - roomID: 直播间ID
 - roomTitle: 直播标题
 - coverUri: 直播封面图片URL
 - startTime: 开始时间（格式: "YYYY-MM-DD HH:mm:ss"）
 - endTime: 结束时间（格式: "YYYY-MM-DD HH:mm:ss"）
 - liveDurationWithoutPause: 直播时长（不含暂停时间，格式如: "1分钟5秒"）
 - playStatus: 播放状态（4=已结束）
  **流量数据**:
 - watchCnt: 总观看人次
 - serverWatchUcntTdDirect: 直接观看用户数（来自服务端统计）
 - pcu: 峰值同时在线人数（Peak Concurrent Users）
 - liveServerWatchDurationTdPavg: 平均观看时长
  **互动数据**:
 - serverLikeCntTd: 点赞数
 - clientCommentUcntTd: 评论用户数
 - liveNewFollowUcnt: 新增关注数
  **消费/转化数据**:
 - liveConsumeUcnt: 消费用户数
 - liveFansConsumeUcntTd: 粉丝消费用户数
 - roomLiveEarnScore: 直播收益积分
  ### 数据价值:
 - **历史回顾**: 查看所有直播场次的完整记录
 - **数据对比**: 对比不同场次的表现差异
 - **趋势分析**: 分析直播效果的变化趋势
 - **优化方向**: 找出高转化场次的共同特点
 - **时间规划**: 根据历史数据优化直播时间
 - **内容策略**: 根据不同主题的效果调整内容
  ### 应用场景:
 1. **定期复盘**: 每周/每月查看直播数据进行总结
 2. **效果评估**: 评估不同时段、不同主题的直播效果
 3. **数据报表**: 生成直播数据报表供团队分析
 4. **策略优化**: 基于历史数据制定下一步直播策略
 5. **KPI追踪**: 追踪直播相关的关键指标完成情况
 6. **趋势预测**: 预测未来直播的潜在表现
  ### 注意事项:
 1. **时间范围**: 建议查询时间不超过3个月，避免数据量过大
 2. **数量限制**: 单次最多返回400条记录
 3. **数据延迟**: 直播数据可能有1-2小时的延迟
 4. **正在直播**: 设置need_living=1可以查看当前正在进行的直播
 5. **Cookie有效性**: 确保Cookie未过期，否则无法获取数据
 6. **日期格式**: 必须使用YYYY-MM-DD格式，如2025-09-11
  ### Cookie 获取方式:
 1. 登录抖音创作者平台 (https://creator.douyin.com)
 2. 打开浏览器开发者工具（F12）
 3. 切换到 Network 标签
 4. 刷新页面或进行操作
 5. 找到任意请求，复制 Cookie 请求头的值

## fetch_live_room_product_result

`GET /api/v1/douyin/web/fetch_live_room_product_result`

<!-- Full path: /api/v1/douyin/web/fetch_live_room_product_result -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| room_id | string | ✅ | 直播间room_id/Room room_id | 7360830184578091776 |
| author_id | string | ✅ | 作者id/Author id | 1714858898241277 |
| offset | integer |  | 偏移量/Offset (default: 0) |  |
| limit | integer |  | 数量/Number (default: 20) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 抖音直播间商品信息
 ### 参数:
 - cookie: 用户网页版抖音Cookie(此接口需要用户提供自己的Cookie，如获取失败请手动过一次验证码)
 - room_id: 直播间room_id
 - author_id: 作者id
 - offset: 偏移量
 - limit: 数量
 ### 返回:
 - 商品信息
 ### 备注:
 author_id的获取方法：
    1. 通过用户的sec_user_id获取用户信息接口获取uid字段即为author_id。
    2. 通过直播间room_id获取直播间信息接口获取author_id字段。
roon_id不是固定不变的，每次开播都会变化。

## fetch_live_search_v1

`POST /api/v1/douyin/search/fetch_live_search_v1`

<!-- Full path: /api/v1/douyin/search/fetch_live_search_v1 -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取抖音 App 中直播搜索结果。
 - 返回正在直播的房间信息，包括主播资料、直播间封面、观众人数、拉流地址等。
  ### 备注:
 - 仅返回直播类型内容。
 - 初次请求时 `cursor` 传0，`search_id` 传空字符串。
 - 翻页请求时，使用上一次响应返回的 `cursor` 和 `search_id`。
  ### 参数:
 - keyword: 搜索关键词，如 "游戏"
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
- filter_duration: 视频时长过滤
  - `0`: 不限
- content_type: 内容类型（固定传直播类型）
 - search_id: 搜索ID（翻页时使用）
  ### 请求体示例：
 ```json
 payload = {
    "keyword": "游戏",
    "cursor": 0,
    "sort_type": "0",
    "publish_time": "0",
    "filter_duration": "0",
    "content_type": "1",
    "search_id": ""
}
 ```
  ### 返回（部分常用字段，实际返回字段更多，一切以实际响应为准）:
 - `cursor`: 下一页游标
 - `has_more`: 是否有更多数据（1=有，0=无）
 - `data[]`: 直播房间列表
  - `type`: 返回内容类型（固定为1）
  - `lives`:
    - `aweme_id`: 直播对应的内容ID
    - `group_id`: 群组ID（与aweme_id类似，可用于跳转）
    - `author`:
      - `uid`: 主播用户ID
      - `nickname`: 主播昵称
      - `short_id`: 主播短ID
      - `avatar_thumb.url_list`: 缩略头像URL列表
      - `avatar_medium.url_list`: 中等头像URL列表
      - `avatar_larger.url_list`: 高清头像URL列表
      - `room_id`: 当前直播间ID
      - `room_cover.url_list`: 直播封面图URL列表
    - `video`:
      - `tags[]`: 直播标签（如“游戏”、“聊天”等）
        - `title`: 标签标题
        - `url.url_list`: 标签图标URL列表
    - `rawdata`: 直播详细数据（结构化JSON字符串，可解析得到以下信息）
      - `title`: 直播标题
      - `user_count`: 当前在线观众数
      - `stream_url`: 拉流信息
        - `flv_pull_url`: 拉流地址列表（不同清晰度）
          - `SD1`: 标清
          - `SD2`: 高清
          - `HD1`: 超清
          - `FULL_HD1`: 蓝光
          - `ORIGION`: 原画
        - `hls_pull_url`: HLS播放地址（部分直播间可能存在）
      - `cover.url_list`: 直播间封面图
      - `size`: 分辨率（如1920x1080）
      - `stats.total_user`: 在线观众数
 - `extra`:
  - `now`: 当前服务器时间戳
  - `logid`: 请求日志ID
  - `search_request_id`: 搜索请求唯一ID

## fetch_query_user

`POST /api/v1/douyin/web/fetch_query_user`

<!-- Full path: /api/v1/douyin/web/fetch_query_user -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 查询抖音用户基本信息
 ### 参数:
 - cookie: 用户ttwid Cookie，获取方式：调用`/api/v1/douyin/web/generate_ttwid`接口获取。
 ### 返回:
 - 用户基本信息

## fetch_user_collects

`POST /api/v1/douyin/web/fetch_user_collects`

<!-- Full path: /api/v1/douyin/web/fetch_user_collects -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取用户收藏夹
 ### 参数:
 - max_cursor: 最大游标
 - count: 最大数量
 - cookie: 用户网页版抖音Cookie(此接口需要用户提供自己的Cookie)
 ### 返回:
 - 用户收藏夹数据

## fetch_user_fans_list

`GET /api/v1/douyin/app/v3/fetch_user_fans_list`

<!-- Full path: /api/v1/douyin/app/v3/fetch_user_fans_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| sec_user_id | string |  | 用户sec_user_id/User sec_user_id (default: MS4wLjABAAAA9y04iBlVdeMQqTJbqsQZKb-tqWqWW29jPVJqideHT70) |  |
| max_time | string |  | 最大时间戳/Maximum timestamp (default: '0') |  |
| count | integer |  | 数量/Number (default: 20) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取用户粉丝列表
 ### 参数:
 - sec_user_id: 用户sec_user_id
 - max_time: 最大时间戳，默认为0，后续从返回数据中获取，用于翻页。
 - count: 数量，默认为20，建议保持不变。
 ### 返回:
 - 粉丝列表

## fetch_user_fans_list

`GET /api/v1/douyin/app/v3/fetch_user_fans_list`

<!-- Full path: /api/v1/douyin/web/fetch_user_fans_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| sec_user_id | string |  | 用户sec_user_id/User sec_user_id (default: MS4wLjABAAAA9y04iBlVdeMQqTJbqsQZKb-tqWqWW29jPVJqideHT70) |  |
| max_time | string |  | 最大时间戳/Maximum timestamp (default: '0') |  |
| count | integer |  | 数量/Number (default: 20) |  |
| source_type | integer |  | 来源类型/Source type (default: 1) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取用户粉丝列表

第一次请求时，max_time传`0`，source_type传`2`，然后会返回一个空的粉丝列表，里面包含了max_time，然后再次请求时，max_time传上一次请求返回的max_time，source_type传`1`，即可获取到粉丝列表。
 - 如果不按照上述方式请求，可能会导致返回数据包含重复数据。
  ### 参数:
 - sec_user_id: 用户sec_user_id
 - max_time: 最大时间戳，默认为0，后续从返回数据中获取，用于翻页。
 - count: 数量，默认为20，建议保持不变。
 - source_type: 来源类型，默认为`1`，第一次请求时使用`2`作为来源类型，然后再次请求时使用`1`作为来源类型。
 ### 返回:
 - 粉丝列表

## fetch_user_following_list

`GET /api/v1/douyin/web/fetch_user_following_list`

<!-- Full path: /api/v1/douyin/web/fetch_user_following_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| sec_user_id | string |  | 用户sec_user_id/User sec_user_id (default: MS4wLjABAAAA9y04iBlVdeMQqTJbqsQZKb-tqWqWW29jPVJqideHT70) |  |
| max_time | string |  | 最大时间戳/Maximum timestamp (default: '0') |  |
| count | integer |  | 数量/Number (default: 20) |  |
| source_type | integer |  | 来源类型/Source type (default: 1) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取用户关注列表

第一次请求时，max_time传`0`，source_type传`2`，然后会返回一个空的粉丝列表，里面包含了max_time，然后再次请求时，max_time传上一次请求返回的max_time，source_type传`1`，即可获取到粉丝列表。
 - 如果不按照上述方式请求，可能会导致返回数据包含重复数据。
 ### 参数:
 - sec_user_id: 用户sec_user_id
 - max_time: 最大时间戳，默认为0，后续从返回数据中获取，用于翻页。
 - count: 数量，默认为20，建议保持不变。
 - source_type: 来源类型，默认为`1`，第一次请求时使用`2`作为来源类型，然后再次请求时使用`1`作为来源类型。
 ### 返回:
 - 关注列表

## fetch_user_live_info_by_uid

`GET /api/v1/douyin/web/fetch_user_live_info_by_uid`

<!-- Full path: /api/v1/douyin/web/fetch_user_live_info_by_uid -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| uid | string | ✅ | 用户UID/User UID | 3081254195702747 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 使用UID获取用户开播信息
### 参数:
- uid: 用户UID
### 返回:
- 用户开播信息，包含room_id与live_status

## fetch_user_profile_by_short_id

`GET /api/v1/douyin/web/fetch_user_profile_by_short_id`

<!-- Full path: /api/v1/douyin/web/fetch_user_profile_by_short_id -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| short_id | string | ✅ | 用户Short ID/User Short ID | 114131058 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 使用Short ID获取用户信息
### 参数:
- short_id: 用户Short ID
### 返回:
- 用户信息

## fetch_user_profile_by_uid

`GET /api/v1/douyin/web/fetch_user_profile_by_uid`

<!-- Full path: /api/v1/douyin/web/fetch_user_profile_by_uid -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| uid | string | ✅ | 用户UID/User UID | 68141954464 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 使用UID获取用户信息
### 参数:
- uid: 用户UID
### 返回:
- 用户信息

## fetch_user_search

`GET /api/v1/douyin/creator/fetch_user_search`

<!-- Full path: /api/v1/douyin/creator/fetch_user_search -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_name | string | ✅ | 用户名/Username (支持抖音号和抖音昵称) | Y |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 搜索抖音用户，支持抖音号和抖音昵称搜索
### 参数:
- user_name: 用户名 (支持抖音号和抖音昵称)
    - 抖音号: 如 "rmrbxmt"
    - 抖音昵称: 如 "Y"、"人民日报"
### 返回:
- 最多返回20个匹配的用户信息
- 包含用户基本信息如头像、昵称、抖音号等

## fetch_user_search

`POST /api/v1/douyin/creator/fetch_user_search`

<!-- Full path: /api/v1/douyin/search/fetch_user_search -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取抖音 App 中根据关键词搜索到的用户列表。
 - 支持通过粉丝数量、用户类型进行筛选查询。
  ### 备注:
 - 初次请求 `cursor` 传 0，`search_id` 传空字符串。
 - 返回的数据仅包含「用户信息」，不包括视频、话题、音乐等内容。
  ### 参数:
 - keyword: 搜索关键词，如 "人工智能"
 - cursor: 翻页游标（首次请求传0）
 - douyin_user_fans: 粉丝数量筛选
  - 为空: 不限
  - "0_1k": 1000以下
  - "1k_1w": 1000到1万
  - "1w_10w": 1万到10万
  - "10w_100w": 10万到100万
  - "100w_": 100万以上
- douyin_user_type: 用户类型筛选
  - 为空: 不限
  - "common_user": 普通用户
  - "enterprise_user": 企业认证用户
  - "personal_user": 个人认证用户
- search_id: 搜索ID（翻页使用）
  ### 请求体示例：
 ```json
 payload = {
    "keyword": "人工智能",
    "cursor": 0,
    "douyin_user_fans": "",
    "douyin_user_type": "",
    "search_id": ""
}
 ```
  ### 返回（部分常用字段，实际返回字段更多，一切以实际响应为准）:
 - `cursor`: 下一页游标
 - `has_more`: 是否还有更多数据（1=有，0=无）
 - `user_list[]`: 用户列表
  - `user_info`:
    - `uid`: 用户ID
    - `nickname`: 用户昵称
    - `gender`: 性别（0=未知，1=男，2=女）
    - `unique_id`: 抖音号
    - `sec_uid`: 安全UID
    - `signature`: 个性签名
    - `follower_count`: 粉丝数量
    - `avatar_thumb.url_list`: 小头像地址
    - `avatar_medium.url_list`: 中头像地址
    - `avatar_larger.url_list`: 大头像地址
    - `follow_status`: 是否已关注
    - `live_status`: 是否正在直播（0=否，1=是）
    - `enterprise_verify_reason`: 企业认证信息（若有）
    - `versatile_display`: 抖音号展示文案（例如"抖音号：xxx"）
- `extra`:
  - `now`: 当前服务器时间戳
  - `logid`: 请求日志ID
  - `search_request_id`: 搜索请求ID

## fetch_user_search_v2

`POST /api/v1/douyin/search/fetch_user_search_v2`

<!-- Full path: /api/v1/douyin/search/fetch_user_search_v2 -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取抖音 App 中根据关键词搜索到的用户列表。
- 不支持粉丝数量、用户类型筛选查询。
 ### 备注:
- 初次请求 `cursor` 传 0。
- 返回的数据仅包含「用户信息」，不包括视频、话题、音乐等内容。
 ### 参数:
- keyword: 搜索关键词，如 "人工智能"
- cursor: 翻页游标（首次请求传0）
 ### 请求体示例：
```json
payload = {
    "keyword": "人工智能",
    "cursor": 0
}
```
 ### 返回（部分常用字段，实际返回字段更多，一切以实际响应为准）:
- `cursor`: 下一页游标
- `has_more`: 是否还有更多数据（1=有，0=无）
- `user_list[]`: 用户列表
  - `user_info`:
    - `uid`: 用户ID
    - `nickname`: 用户昵称
    - `gender`: 性别（0=未知，1=男，2=女）
    - `unique_id`: 抖音号
    - `sec_uid`: 安全UID
    - `signature`: 个性签名
    - `follower_count`: 粉丝数量
    - `avatar_thumb.url_list`: 小头像地址
    - `avatar_medium.url_list`: 中头像地址
    - `avatar_larger.url_list`: 大头像地址
    - `follow_status`: 是否已关注
    - `live_status`: 是否正在直播（0=否，1=是）
    - `enterprise_verify_reason`: 企业认证信息（若有）
    - `versatile_display`: 抖音号展示文案（例如"抖音号：xxx"）
- `extra`:
  - `now`: 当前服务器时间戳
  - `logid`: 请求日志ID
  - `search_request_id`: 搜索请求ID

## get_all_sec_user_id

`POST /api/v1/douyin/web/get_all_sec_user_id`

<!-- Full path: /api/v1/douyin/web/get_all_sec_user_id -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 提取列表用户id
 ### 参数:
 - url: 用户主页链接列表（最多支持10个链接）
 ### 返回:
 - 如果链接成功获取到sec_user_id，则返回sec_user_id，否则返回原始的输入链接，后续可以手动校验链接无法获取sec_user_id的原因。

## get_content_trend_guide

`GET /api/v1/douyin/xingtu_v2/get_content_trend_guide`

<!-- Full path: /api/v1/douyin/xingtu_v2/get_content_trend_guide -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取内容趋势指南数据（CDN静态JSON，无需Cookie）
### 返回:
- 内容趋势指南数据

## get_sec_user_id

`GET /api/v1/douyin/web/get_sec_user_id`

<!-- Full path: /api/v1/douyin/web/get_sec_user_id -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| url | string | ✅ | '' | >- |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 提取单个用户id
 ### 参数:
 - url: 用户主页链接
 ### 返回:
 - 用户sec_user_id

## get_user_profile_qrcode

`GET /api/v1/douyin/xingtu_v2/get_user_profile_qrcode`

<!-- Full path: /api/v1/douyin/xingtu_v2/get_user_profile_qrcode -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| core_user_id | string |  | 用户核心ID(与sec_uid二选一)/User core ID (pick one with sec_uid) | 1113181577281568 |
| sec_uid | string |  | >- |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 生成用户主页二维码
- core_user_id和sec_uid二选一传入即可
### 参数:
- core_user_id: 用户核心ID（与sec_uid二选一）
- sec_uid: 用户sec_uid（与core_user_id二选一）
### 返回:
- 用户主页二维码数据

## get_xingtu_kolid_by_sec_user_id

`GET /api/v1/douyin/xingtu/get_xingtu_kolid_by_sec_user_id`

<!-- Full path: /api/v1/douyin/xingtu/get_xingtu_kolid_by_sec_user_id -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| sec_user_id | string | ✅ | 抖音用户sec_user_id/Douyin User sec_user_id | MS4wLjABAAAAoxwUZouIdKL6sZ8EB96KDjkrhfBMS1KbCgsMJR1kIUs |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 通过抖音sec_user_id获取游客星图kolid
 ### 参数:
 - sec_user_id: sec_user_id, 可以从接口以下接口获取：
    - `/api/v1/douyin/web/handler_user_profile`
    - `/api/v1/douyin/web/handler_user_profile_v2`
    - `/api/v1/douyin/web/handler_user_profile_v3`
    - `/api/v1/douyin/app/v3/handler_user_profile`
### 返回:
 - 游客星图kolid

## get_xingtu_kolid_by_uid

`GET /api/v1/douyin/xingtu/get_xingtu_kolid_by_uid`

<!-- Full path: /api/v1/douyin/xingtu/get_xingtu_kolid_by_uid -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| uid | string | ✅ | 抖音用户ID/Douyin User ID | 70452002324 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 通过抖音用户ID获取游客星图kolid
### 参数:
- uid: 用户ID, 可以从接口以下接口获取：
    - `/api/v1/douyin/web/fetch_user_profile_by_uid`
    - `/api/v1/douyin/web/fetch_user_profile_by_short_id`
    - `/api/v1/douyin/web/handler_user_profile`
    - `/api/v1/douyin/web/handler_user_profile_v2`
    - `/api/v1/douyin/web/handler_user_profile_v3`
    - `/api/v1/douyin/app/v3/handler_user_profile`
### 返回:
- 游客星图kolid

## handler_user_profile

`GET /api/v1/douyin/app/v3/handler_user_profile`

<!-- Full path: /api/v1/douyin/app/v3/handler_user_profile -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| sec_user_id | string | ✅ | 用户sec_user_id/User sec_user_id | >- |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定用户的信息
 ### 参数:
 - sec_user_id: 用户sec_user_id
 ### 返回:
 - 用户信息

## handler_user_profile

`GET /api/v1/douyin/app/v3/handler_user_profile`

<!-- Full path: /api/v1/douyin/web/handler_user_profile -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| sec_user_id | string | ✅ | 用户sec_user_id/User sec_user_id | >- |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定用户的信息
 ### 参数:
 - sec_user_id: 用户sec_user_id
 ### 返回:
 - 用户信息

## handler_user_profile_v2

`GET /api/v1/douyin/web/handler_user_profile_v2`

<!-- Full path: /api/v1/douyin/web/handler_user_profile_v2 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| unique_id | string | ✅ | 用户unique_id/User unique_id | TheChief |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 根据抖音号获取指定用户的信息
### 参数:
- unique_id: 用户unique_id
### 返回:
- 用户信息

## handler_user_profile_v3

`GET /api/v1/douyin/web/handler_user_profile_v3`

<!-- Full path: /api/v1/douyin/web/handler_user_profile_v3 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| uid | string | ✅ | 用户uid(short_id)/User uid(short_id) | 1673937488185292 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 根据抖音uid获取指定用户的信息
### 参数:
- uid: 用户uid，也就是抖音号的short_id
### 返回:
- 用户信息

## handler_user_profile_v4

`GET /api/v1/douyin/web/handler_user_profile_v4`

<!-- Full path: /api/v1/douyin/web/handler_user_profile_v4 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| sec_user_id | string | ✅ | 用户sec_user_id/User sec_user_id | >- |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定用户的信息
 ### 参数:
 - sec_user_id: 用户sec_user_id
 ### 返回:
 - 用户信息，包含性别，年龄，直播等级，直播间牌子
 ### 说明：
 - 性别：1为男，2为女，0为未知，在live_user字段中。
 - 年龄：在user字段中，-1为未知。

## kol_daily_fans_v1

`GET /api/v1/douyin/xingtu/kol_daily_fans_v1`

<!-- Full path: /api/v1/douyin/xingtu/kol_daily_fans_v1 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| kolId | string | ✅ | 用户的kolId/User kolId | 7048929565493690398 |
| startDate | string | ✅ | 开始日期/Start Date | 2024-12-01 |
| endDate | string | ✅ | 结束日期/End Date | 2025-01-01 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取kol粉丝趋势V1
 - 该接口数据使用企业账号进行请求，收费较贵。
 ### 参数:
 - kolId: 用户的kolId, 可以从接口以下接口获取：
    - `/api/v1/douyin/xingtu/get_xingtu_kolid_by_uid`
    - `/api/v1/douyin/xingtu/get_xingtu_kolid_by_sec_user_id`
    - `/api/v1/douyin/xingtu/get_xingtu_kolid_by_unique_id`
- startDate: 开始日期，格式为：yyyy-MM-dd
 - endDate: 结束日期，格式为：yyyy-MM-dd
 ### 返回:
 - kol粉丝趋势

## kol_fans_portrait_v1

`GET /api/v1/douyin/xingtu/kol_fans_portrait_v1`

<!-- Full path: /api/v1/douyin/xingtu/kol_fans_portrait_v1 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| kolId | string | ✅ | 用户的kolId/User kolId | 7048929565493690398 |
| fansType | string |  | 粉丝类型/Fans Type (default: _1) | _1 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取kol粉丝画像V1
 - 该接口数据使用企业账号进行请求，收费较贵。
 ### 参数:
 - kolId: 用户的kolId, 可以从接口以下接口获取：
    - `/api/v1/douyin/xingtu/get_xingtu_kolid_by_uid`
    - `/api/v1/douyin/xingtu/get_xingtu_kolid_by_sec_user_id`
    - `/api/v1/douyin/xingtu/get_xingtu_kolid_by_unique_id`
- fansType: 粉丝类型，支持以下参数:
    - _1: 粉丝画像 (Fans Portrait) - 默认值
    - _2: 粉丝团画像 (Fans Group Portrait)
    - _5: 铁粉画像 (Iron Fans Portrait)
### 返回:
 - kol粉丝画像

## kol_link_struct_v1

`GET /api/v1/douyin/xingtu/kol_link_struct_v1`

<!-- Full path: /api/v1/douyin/xingtu/kol_link_struct_v1 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| kolId | string | ✅ | 用户的kolId/User kolId | 7048929565493690398 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取kol连接用户V1
 - 该接口数据使用企业账号进行请求，收费较贵。
 ### 参数:
 - kolId: 用户的kolId, 可以从接口以下接口获取：
    - `/api/v1/douyin/xingtu/get_xingtu_kolid_by_uid`
    - `/api/v1/douyin/xingtu/get_xingtu_kolid_by_sec_user_id`
    - `/api/v1/douyin/xingtu/get_xingtu_kolid_by_unique_id`
### 返回:
 - kol连接用户

## kol_touch_distribution_v1

`GET /api/v1/douyin/xingtu/kol_touch_distribution_v1`

<!-- Full path: /api/v1/douyin/xingtu/kol_touch_distribution_v1 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| kolId | string | ✅ | 用户的kolId/User kolId | 7048929565493690398 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取kol连接用户来源V1
 - 该接口数据使用企业账号进行请求，收费较贵。
 ### 参数:
 - kolId: 用户的kolId, 可以从接口以下接口获取：
    - `/api/v1/douyin/xingtu/get_xingtu_kolid_by_uid`
    - `/api/v1/douyin/xingtu/get_xingtu_kolid_by_sec_user_id`
    - `/api/v1/douyin/xingtu/get_xingtu_kolid_by_unique_id`
### 返回:
 - kol连接用户来源

## open_douyin_app_to_user_profile

`GET /api/v1/douyin/app/v3/open_douyin_app_to_user_profile`

<!-- Full path: /api/v1/douyin/app/v3/open_douyin_app_to_user_profile -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| uid | string | ✅ | 用户id/User id | 96874812426 |
| sec_uid | string | ✅ | 用户sec_uid/User sec_uid | MS4wLjABAAAA9y04iBlVdeMQqTJbqsQZKb-tqWqWW29jPVJqideHT70 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 生成抖音分享链接，唤起抖音APP，跳转指定用户主页。
  ### 参数:
 - uid: 用户id
 - sec_uid: 用户sec_uid
 - 注意: 请确保user_id和sec_uid都有值，否则无法跳转到指定用户主页。
  ### 返回:
 - 分享链接

---

See SKILL.md for cross-group orchestration patterns.