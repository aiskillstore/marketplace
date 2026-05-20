# User Data API / 用户数据接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---
## fetch_creator_info_and_milestones

`GET /api/v1/tiktok/analytics/fetch_creator_info_and_milestones`

<!-- Full path: /api/v1/tiktok/analytics/fetch_creator_info_and_milestones -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string | ✅ | 用户id/User id | 107955 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取TikTok创作者账号的基本信息和关键统计数据
 - 查看创作者账号的成长历程和达成的重要里程碑
 - 分析创作者账号发展轨迹，了解粉丝增长和内容影响力变化
  ### 参数:
 - user_id: 创作者用户ID，必填参数，可从用户主页URL或TikTok后台获取
  ### 返回内容说明:
 - `user_id`: 请求的创作者ID
 - `creator_info`: The creator's basic information
  - `nickname`: 创作者昵称
  - `sec_user_id`: 安全用户ID
  - `unique_id`: 唯一用户名
  - `avatar_url`: 头像URL
  - `follower_count`: 粉丝数量
  - `like_count`: 获赞总数
- `milestones`: 创作者账号里程碑列表，每个里程碑包含:
  - `milestone`: 里程碑类型ID
  - `milestone_title`: 里程碑标题（如"达到100万粉丝"）
  - `milestone_year`: 里程碑达成年份
  - `milestone_month_day`: 里程碑达成月日
  - `creator_summary`: 里程碑相关描述
 ### 示例响应:
 ```json
 {
  "code": 200,
  "router": "/api/v1/tiktok/analytics/fetch_creator_info_and_milestones",
  "params": {
    "user_id": "107955"
  },
  "data": {
    "user_id": "107955",
    "creator_info": {
      "avatar_url": "https://p19-pu-sign-useast8.tiktokcdn-us.com/tos-useast5-avt-0068-tx/ba67b11de451691939223e9d978e613a~tplv-tiktokx-cropcenter:720:720.webp",
      "follower_count": 89812099,
      "like_count": 382411162,
      "nickname": "TikTok",
      "sec_user_id": "MS4wLjABAAAAv7iSuuXDJGDvJkmH_vz1qkDZYo1apxgzaxdBSeIuPiM",
      "unique_id": "tiktok"
    },
    "milestones": [
      {
        "milestone": 6,
        "milestone_month_day": "10/4",
        "milestone_title": "Reached 1 million followers",
        "milestone_year": "2015"
      },
      {
        "milestone": 1,
        "milestone_month_day": "2/27",
        "milestone_title": "Started posting on TikTok",
        "milestone_year": "2015"
      }
    ]
  }
}
 ```

## fetch_search_live

`GET /api/v1/tiktok/web/fetch_search_live`

<!-- Full path: /api/v1/tiktok/web/fetch_search_live -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 搜索关键词/Search keyword | TikTok |
| count | integer |  | 每页数量/Number per page (default: 20) |  |
| offset | integer |  | 翻页游标/Page cursor (default: 0) |  |
| search_id | string |  | 搜索id，翻页时需要提供/Search id, need to provide when paging (default: '') |  |
| cookie | string |  | 用户cookie(按需提供)/User cookie(if needed) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 搜索直播
 ### 参数:
 - keyword: 搜索关键词
 - count: 每页数量
 - offset: 翻页游标，第一次请求时为0，第二次请求时从上一次请求的返回响应中获取。
 - search_id: 搜索id，第一次请求时为空，第二次翻页时需要提供，需要从上一次请求的返回响应中获取。
    - 例如: search_id = "20240828035554C02011379EBB6A00E00B"
    - JSON Path-1 : $.data.extra.logid
    - JSON Path-2 : $.data.log_pb.impr_id
- cookie: 用户cookie(如果你需要使用自己的账号搜索，或者遇到接口报错，可以自行提供cookie，默认不需要提供)
 ### 返回:
 - 直播列表

## fetch_search_user

`GET /api/v1/tiktok/web/fetch_search_user`

<!-- Full path: /api/v1/tiktok/web/fetch_search_user -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 搜索关键词/Search keyword | TikTok |
| cursor | integer |  | 翻页游标/Page cursor (default: 0) |  |
| search_id | string |  | 搜索id，翻页时需要提供/Search id, need to provide when paging (default: '') |  |
| cookie | string |  | 用户cookie(按需提供)/User cookie(if needed) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 搜索用户
 ### 参数:
 - keyword: 搜索关键词
 - cursor: 翻页游标，第一次请求时为0，第二次请求时从上一次请求的返回响应中获取，一般这个值的关键字为offset或者cursor。
 - search_id: 搜索id，第一次请求时为空，第二次翻页时需要提供，需要从上一次请求的返回响应中获取。
    - 例如: search_id = "20240828035554C02011379EBB6A00E00B"
    - JSON Path-1 : $.data.extra.logid
    - JSON Path-2 : $.data.log_pb.impr_id
- cookie: 用户cookie(如果你需要使用自己的账号搜索，或者遇到接口报错，可以自行提供cookie，默认不需要提供)
 ### 返回:
 - 用户列表
 ### 备注:
 - 如果接口响应的 `data` 字段中的 `status_code` 不为0，说明搜索请求未成功，此时请检查响应里的异常，有可能你在搜索
TikTok 不允许的关键词，或者搜索了敏感内容，请更换关键词重试。

## fetch_user_collect

`GET /api/v1/tiktok/web/fetch_user_collect`

<!-- Full path: /api/v1/tiktok/web/fetch_user_collect -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| cookie | string | ✅ | 用户cookie/User cookie | Your_Cookie |
| secUid | string | ✅ | 用户secUid/User secUid | Your_SecUid |
| cursor | integer |  | 翻页游标/Page cursor (default: 0) |  |
| count | integer |  | 每页数量/Number per page (default: 30) |  |
| coverFormat | integer |  | 封面格式/Cover format (default: 2) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取用户的收藏列表
 - 注意: 该接口目前只能获取自己的收藏列表，需要提供自己账号的cookie。
 ### 参数:
 - cookie: 用户cookie
 - secUid: 用户secUid
 - cursor: 翻页游标
 - count: 每页数量
 - coverFormat: 封面格式
 ### 返回:
 - 用户的收藏列表
 ### 备注:
 - 此接口返回的所有视频CDN链接均需要携带返回的 `tt_chain_token` 参数才能正常访问，否则会返回HTTP403错误。
 - 在访问视频CDN链接时，请务必在请求头中携带 `Cookie: tt_chain_token={tt_chain_token}`，其中
`{tt_chain_token}` 替换为接口返回的 `tt_chain_token` 参数值。
 - **如果访问视频CDN链接时返回HTTP 403错误**:
  1. 请使用接口响应中以 `https://www.tiktok.com/aweme/v1/play/` 开头的视频链接(通常在响应数据的 `video.playAddr` 或类似字段中)
  2. 在请求该链接时，务必在请求头中添加 `Cookie: tt_chain_token={tt_chain_token}`，其中 `{tt_chain_token}` 为接口返回的 `tt_chain_token` 参数值
  3. 示例请求头: `Cookie: tt_chain_token=xxx`
- 如果需要绕过此限制获取可以直接访问的无水印视频CDN链接，请使用 TikTok APP V3 目录下的接口。

## fetch_user_fans

`GET /api/v1/tiktok/web/fetch_user_fans`

<!-- Full path: /api/v1/tiktok/web/fetch_user_fans -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| secUid | string | ✅ | 用户secUid/User secUid | MS4wLjABAAAAv7iSuuXDJGDvJkmH_vz1qkDZYo1apxgzaxdBSeIuPiM |
| count | integer |  | 每页数量/Number per page (default: 30) |  |
| maxCursor | integer |  | 最大游标/Max cursor (default: 0) |  |
| minCursor | integer |  | 最小游标/Min cursor (default: 0) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取用户的粉丝列表
 ### 参数:
 - secUid: 用户secUid
 - count: 每页数量
 - maxCursor: 最大游标
 - minCursor: 最小游标
 ### 返回:
 - 用户的粉丝列表
 ### 备注:
 - 此接口返回的所有视频CDN链接均需要携带返回的 `tt_chain_token` 参数才能正常访问，否则会返回HTTP403错误。
 - 在访问视频CDN链接时，请务必在请求头中携带 `Cookie: tt_chain_token={tt_chain_token}`，其中
`{tt_chain_token}` 替换为接口返回的 `tt_chain_token` 参数值。
 - **如果访问视频CDN链接时返回HTTP 403错误**:
  1. 请使用接口响应中以 `https://www.tiktok.com/aweme/v1/play/` 开头的视频链接(通常在响应数据的 `video.playAddr` 或类似字段中)
  2. 在请求该链接时，务必在请求头中添加 `Cookie: tt_chain_token={tt_chain_token}`，其中 `{tt_chain_token}` 为接口返回的 `tt_chain_token` 参数值
  3. 示例请求头: `Cookie: tt_chain_token=xxx`
- 如果需要绕过此限制获取可以直接访问的无水印视频CDN链接，请使用 TikTok APP V3 目录下的接口。

## fetch_user_follow

`GET /api/v1/tiktok/web/fetch_user_follow`

<!-- Full path: /api/v1/tiktok/web/fetch_user_follow -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| secUid | string | ✅ | 用户secUid/User secUid | MS4wLjABAAAAv7iSuuXDJGDvJkmH_vz1qkDZYo1apxgzaxdBSeIuPiM |
| count | integer |  | 每页数量/Number per page (default: 30) |  |
| maxCursor | integer |  | 最大游标/Max cursor (default: 0) |  |
| minCursor | integer |  | 最小游标/Min cursor (default: 0) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取用户的关注列表
 ### 参数:
 - secUid: 用户secUid
 - count: 每页数量
 - maxCursor: 最大游标
 - minCursor: 最小游标
 ### 返回:
 - 用户的关注列表
 ### 备注:
 - 此接口返回的所有视频CDN链接均需要携带返回的 `tt_chain_token` 参数才能正常访问，否则会返回HTTP403错误。
 - 在访问视频CDN链接时，请务必在请求头中携带 `Cookie: tt_chain_token={tt_chain_token}`，其中
`{tt_chain_token}` 替换为接口返回的 `tt_chain_token` 参数值。
 - **如果访问视频CDN链接时返回HTTP 403错误**:
  1. 请使用接口响应中以 `https://www.tiktok.com/aweme/v1/play/` 开头的视频链接(通常在响应数据的 `video.playAddr` 或类似字段中)
  2. 在请求该链接时，务必在请求头中添加 `Cookie: tt_chain_token={tt_chain_token}`，其中 `{tt_chain_token}` 为接口返回的 `tt_chain_token` 参数值
  3. 示例请求头: `Cookie: tt_chain_token=xxx`
- 如果需要绕过此限制获取可以直接访问的无水印视频CDN链接，请使用 TikTok APP V3 目录下的接口。

## fetch_user_like

`GET /api/v1/tiktok/web/fetch_user_like`

<!-- Full path: /api/v1/tiktok/web/fetch_user_like -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| secUid | string | ✅ | 用户secUid/User secUid | >- |
| cursor | integer |  | 翻页游标/Page cursor (default: 0) |  |
| count | integer |  | 每页数量/Number per page (default: 20) |  |
| coverFormat | integer |  | 封面格式/Cover format (default: 2) |  |
| post_item_list_request_type | integer |  | 排序方式/Sort type (default: 0) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取用户的点赞列表
 - 注意: 该接口需要用户点赞列表为公开状态
 ### 参数:
 - secUid: 用户secUid
 - cursor: 翻页游标
 - count: 每页数量，默认为20，不可变更。
 - coverFormat: 封面格式
 - post_item_list_request_type: 排序方式
    - 0：默认排序
    - 1：热门排序
    - 2：最旧排序
### 返回:
 - 用户的点赞列表
 ### 备注:
 - 此接口返回的所有视频CDN链接均需要携带返回的 `tt_chain_token` 参数才能正常访问，否则会返回HTTP403错误。
 - 在访问视频CDN链接时，请务必在请求头中携带 `Cookie: tt_chain_token={tt_chain_token}`，其中
`{tt_chain_token}` 替换为接口返回的 `tt_chain_token` 参数值。
 - **如果访问视频CDN链接时返回HTTP 403错误**:
  1. 请使用接口响应中以 `https://www.tiktok.com/aweme/v1/play/` 开头的视频链接(通常在响应数据的 `video.playAddr` 或类似字段中)
  2. 在请求该链接时，务必在请求头中添加 `Cookie: tt_chain_token={tt_chain_token}`，其中 `{tt_chain_token}` 为接口返回的 `tt_chain_token` 参数值
  3. 示例请求头: `Cookie: tt_chain_token=xxx`
- 如果需要绕过此限制获取可以直接访问的无水印视频CDN链接，请使用 TikTok APP V3 目录下的接口。

## fetch_user_profile

`GET /api/v1/tiktok/web/fetch_user_profile`

<!-- Full path: /api/v1/tiktok/web/fetch_user_profile -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| uniqueId | string |  | 用户uniqueId/User uniqueId (default: '') | tiktok |
| secUid | string |  | 用户secUid/User secUid (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取用户的个人信息
 ### 参数:
 - secUid: 用户secUid
 - uniqueId: 用户uniqueId
 - secUid和uniqueId至少提供一个, 优先使用uniqueId, 也就是用户主页的链接中的用户名。
 ### 返回:
 - 用户的个人信息

## generate_x_mssdk_info

`POST /api/v1/tiktok/web/generate_x_mssdk_info`

<!-- Full path: /api/v1/tiktok/web/generate_x_mssdk_info -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 生成 X-Mssdk-Info 和 X-Mssdk-RC，用于 TikTok Web 设备注册、登录等场景
 ### 参数:
 - user_agent (str, 可选): 用户代理字符串，目前不支持自定义，默认为固定的值
 ### 返回:
 - X-Mssdk-Info: 生成的签名信息
 - X-Mssdk-RC: 生成的 RC 值
 - user_agent: 使用的用户代理字符串
 - version: 签名使用的 webmssdk 版本

## get_creator_account_info

`POST /api/v1/tiktok/creator/get_creator_account_info`

<!-- Full path: /api/v1/tiktok/creator/get_creator_account_info -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取 TikTok Shop 创作者账号的基础信息，包括用户名、头像链接、账号ID、注册地区、绑定合作伙伴信息、权限列表等。
 - 可用于账号状态验证、账号信息展示、合作关系检查及后续业务逻辑处理。
  ### 备注:
 - 适用于所有 TikTok 创作者账号。
  ### 参数:
 - cookie: 用户 Cookie 字符串（用于身份认证）
 - proxy: 可选 HTTP 代理地址，如不使用可省略
    - 示例格式: `http://username:password@host:port`
 ### 返回内容说明:
 - `user_id`: 用户ID（字符串）
 - `user_type`: 用户类型（数字，代表账号类型）
 - `register_region_id`: 注册地区代码（如 "us"）
 - `user_name`: 用户名
 - `avatar`: 头像信息对象
  - `uri`: 头像资源URI
  - `url_list`: 头像图片URL列表
- `permission_list`: 权限列表（整数数组）
 - `partner_id`: 合作伙伴ID
 - `partner_name`: 合作伙伴名称
 - `shop_account_official`: 是否为官方认证店铺账号（布尔值）
 - `switch_info`: 功能开关信息（如直播功能开关，字符串格式）
 - `tt_uid`: TikTok UID（字符串）
 - `nick_name`: 昵称
 - `live_streamer_menu_experiment`: 直播菜单实验字段（字符串，可能为空）
 - `experiment_variants`: 实验变种配置（对象）

## get_hashtag_creator

`GET /api/v1/tiktok/ads/get_hashtag_creator`

<!-- Full path: /api/v1/tiktok/ads/get_hashtag_creator -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| hashtag | string | ✅ | '标签名称，不包含#符号/Hashtag name (without # symbol)' | blowup |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取特定标签的创作者信息和相关数据
- 了解标签的来源、创建者和使用情况
- 分析标签的影响力和传播路径
 ### 参数:
- hashtag_name: 标签名称，不需要包含#号
 ### 返回内容说明:
- `creators`: 创作者列表
  - `tcm_id`: TCM ID
  - `user_id`: 用户ID
  - `nick_name`: 昵称
  - `avatar_url`: 头像URL
  - `follower_cnt`: 粉丝数
  - `liked_cnt`: 获赞总数
  - `tt_link`: TikTok链接
  - `tcm_link`: TCM链接
  - `items`: 作品列表
    - `item_id`: 作品ID
    - `cover_url`: 封面URL
    - `tt_link`: TikTok链接
    - `vv`: 观看量
    - `liked_cnt`: 点赞数
    - `create_time`: 创建时间
 ### 示例响应:
```json
{
  "code": 200,
  "router": "/api/v1/tiktok/ads/get_hashtag_creator",
  "params": {
    "hashtag_name": "blowup"
  },
  "data": {
    "code": 0,
    "msg": "OK",
    "data": {
      "creators": [
        {
          "tcm_id": "7153957957875531782",
          "user_id": "7137978712880088065",
          "nick_name": "Ben🎧",
          "avatar_url": "https://p16-sign-sg.tiktokcdn.com/tos-alisg-avt-0068/dee2b881a7833ba36ed8811f3116abb2~tplv-tiktokx-cropcenter:100:100.png",
          "follower_cnt": 1123490,
          "liked_cnt": 45506383,
          "tt_link": "https://www.tiktok.com/@ur_localnpcs",
          "tcm_link": "https://creatormarketplace.tiktok.com/ad#/author/7153957957875531782",
          "items": [
            {
              "item_id": "7484029831462522119",
              "cover_url": "https://p16-sign-sg.tiktokcdn.com/tos-alisg-p-0037/oY1c0nzeEOyJAF47RDUI4gBnysS3BVDiEIYfRk~tplv-noop.image",
              "tt_link": "https://www.tiktok.com/@author/video/7484029831462522119",
              "vv": 1068946,
              "liked_cnt": 124292,
              "create_time": 1742511489
            },
            {
              "item_id": "7483385475252751623",
              "cover_url": "https://p16-sign-sg.tiktokcdn.com/tos-alisg-p-0037/oUew2qzADECItXAWFYGeoPQftQEZYPjUKLyIuM~tplv-noop.image",
              "tt_link": "https://www.tiktok.com/@author/video/7483385475252751623",
              "vv": 239239,
              "liked_cnt": 16919,
              "create_time": 1742361463
            }
          ]
        }
      ]
    }
  }
}
```

## get_live_analytics_summary

`POST /api/v1/tiktok/creator/get_live_analytics_summary`

<!-- Full path: /api/v1/tiktok/creator/get_live_analytics_summary -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取 TikTok Shop 创作者账号在指定时间范围内的直播表现数据概览。
 - 默认统计从 `start_date` 当月起 1 个自然月（如传入 2025-04-01，则统计整个 4 月的数据）。
  ### 返回内容说明:
 - `segments`（分段数据列表）:
  - `time_selector`: 时间范围设置（周期、起止时间戳、时区、语言）
  - `filter.creator_id`: 创作者 ID
  - `timed_stats`: 每个时间段（通常按日或月分段）的直播表现数据，包含：
    - `live_revenue.amount`: 直播带货收入
    - `live_show_gpm.amount`: 直播场均带货收入
    - `new_follower_cnt`: 新增粉丝数量
    - `sku_order_paid_cnt`: 已付款 SKU 数量
    - `item_sold_cnt`: 成交商品件数
    - `product_view`: 商品曝光次数（浏览量）
    - `product_click`: 商品点击次数
    - `live_pay_order_ucnt`: 直播支付订单人数
    - `live_ctr`: 直播点击率（Click-Through Rate）
    - `live_co`: 直播转化率（Conversion Rate）
    - `live_like_cnt`: 直播点赞次数
    - `live_comment_cnt`: 直播评论次数
    - `live_show_cnt`: 直播场次
    - `live_watch_cnt`: 直播观看人数
 ### 备注:
 - 此接口仅适用于 TikTok Shop 创作者账号。
 - 直播期间数据按自然日拆分。
  ### 参数:
 - cookie: 用户 Cookie 字符串（用于身份认证）
 - start_date: 查询开始时间（格式 `MM-DD-YYYY`），如 `04-01-2025`
 - proxy: 可选 HTTP 代理地址，如不使用可省略
    - 示例格式: `http://username:password@host:port`
 ### 返回:
 - 创作者账号直播数据概览

## get_query_suggestions

`GET /api/v1/tiktok/ads/get_query_suggestions`

<!-- Full path: /api/v1/tiktok/ads/get_query_suggestions -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| count | integer |  | 建议数量/Suggestion count (default: 50) |  |
| scenario | integer |  | 场景类型/Scenario type (default: 1) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取广告搜索的热门查询建议
- 了解当前流行的广告搜索关键词和趋势
- 帮助发现新的广告创意方向和热点话题
 ### 参数:
- count: 返回的建议数量，默认50
- scenario: 场景类型，默认1
 ### 返回内容说明:
- `query`: 查询建议列表（字符串数组）
 ### 示例响应:
```json
{
  "code": 200,
  "router": "/api/v1/tiktok/ads/get_query_suggestions",
  "params": {
    "count": "50",
    "scenario": "1"
  },
  "data": {
    "code": 0,
    "msg": "OK",
    "data": {
      "query": [
        "shop now",
        "50% off"
      ]
    }
  }
}
```

---

See SKILL.md for cross-group orchestration patterns.