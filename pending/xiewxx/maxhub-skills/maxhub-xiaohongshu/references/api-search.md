# Search API / 搜索接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---
## fetch_search_suggest

`GET /api/v1/xiaohongshu/web_v3/fetch_search_suggest`

<!-- Full path: /api/v1/xiaohongshu/web_v3/fetch_search_suggest -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string |  | 关键词 (可为空)/Keyword (optional) (default: '') | 口红 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取搜索联想词，keyword 为空时返回热门推荐
 ### 接口优先级:
 - 小红书接口推荐优先级: `App V2` > `App` > `Web V3（本接口）` > `Web V2` > `Web`
 ### 参数:
 - keyword: 关键词 (可为空)
 ### 返回:
 - 联想词列表

## fetch_trending

`GET /api/v1/xiaohongshu/web_v3/fetch_trending`

<!-- Full path: /api/v1/xiaohongshu/web_v3/fetch_trending -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取热搜词列表
 ### 接口优先级:
 - 小红书接口推荐优先级: `App V2` > `App` > `Web V3（本接口）` > `Web V2` > `Web`
 ### 返回:
 - 热搜词列表

## search_groups

`GET /api/v1/xiaohongshu/app_v2/search_groups`

<!-- Full path: /api/v1/xiaohongshu/app_v2/search_groups -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 搜索关键词/Search keyword | 上海 |
| page_no | integer |  | 页码，从0开始/Page number, start from 0 (default: 0) | 0 |
| search_id | string |  | 搜索ID，翻页时传入首次搜索返回的值/Search ID for pagination (default: '') |  |
| source | string |  | 来源/Source (default: unifiedSearchGroup) | unifiedSearchGroup |
| is_recommend | integer |  | '是否推荐：0=否, 1=是/Is recommend: 0=no, 1=yes' (default: 0) | 0 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 根据关键词搜索小红书群聊列表，支持分页
 ### 参数:
 - keyword: 搜索关键词（必需），如 "上海"
 - page_no: 页码，从 0 开始
 - search_id: 搜索ID，翻页时传入首次搜索返回的值
 - source: 来源，默认 "unifiedSearchGroup"
 - is_recommend: 是否推荐，0=否, 1=是
 ### 返回:
 - 搜索结果数据，包含群聊列表和分页信息
 ### 翻页说明:
 - 首次请求：search_id 留空（自动生成），page_no 传 0
 - 翻页请求：传入首次搜索返回的 search_id，page_no 递增

## search_images

`GET /api/v1/xiaohongshu/app_v2/search_images`

<!-- Full path: /api/v1/xiaohongshu/app_v2/search_images -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 搜索关键词/Search keyword | 壁纸 |
| page | integer |  | 页码，从1开始/Page number, start from 1 (default: 1) | 1 |
| search_id | string |  | 搜索ID，翻页时传入首次搜索返回的值/Search ID for pagination (default: '') |  |
| search_session_id | string |  | 搜索会话ID，翻页时传入首次搜索返回的值/Search session ID for pagination (default: '') |  |
| word_request_id | string |  | 词请求ID，翻页时传入首次搜索返回的值/Word request ID for pagination (default: '') |  |
| source | string |  | 来源/Source (default: explore_feed) | explore_feed |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 根据关键词搜索小红书图片，每页返回 20 条结果，支持分页
 ### 参数:
 - keyword: 搜索关键词（必需），如 "壁纸"
 - page: 页码，从 1 开始
 - search_id: 搜索ID，翻页时传入首次搜索返回的值
 - search_session_id: 搜索会话ID，翻页时传入首次搜索返回的值
 - word_request_id: 词请求ID，翻页时传入首次搜索返回的值
 - source: 来源，默认 "explore_feed"
 ### 返回:
 - 搜索结果数据，包含图片列表和分页信息
 ### 翻页说明:
 - 首次请求：只传keyword和page
 - 翻页请求：传入首次搜索返回的 search_id、search_session_id 和 word_request_id

## search_products

`GET /api/v1/xiaohongshu/app/search_products`

<!-- Full path: /api/v1/xiaohongshu/app/search_products -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 搜索关键词/Search keyword | 充电宝 |
| page | integer | ✅ | 页码（从1开始）/Page number (start from 1) | 1 |
| search_id | string |  | 搜索ID，翻页时使用/Search ID for pagination |  |
| session_id | string |  | 会话ID，翻页时使用/Session ID for pagination |  |
| sort | string |  | >- | sales_qty |
| scope | string |  | '搜索范围：purchased-买过的店、following-关注的店/Scope: purchased, following' | purchased |
| service_guarantee | string |  | 物流权益，多选用英文逗号分割/Service guarantee, comma separated | 24小时发货,七天无理由 |
| min_price | string |  | 最低价/Min price | 1 |
| max_price | string |  | 最高价/Max price | 100 |
| super_promotion | string |  | 标签ID/Promotion tag ID | 695fb0a330425100017ff555 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 搜索小红书商品
 ### 参数:
 - keyword: 搜索关键词（必需）
 - page: 页码，从1开始（必需）
 - search_id: 搜索ID，第一次请求可不传，翻页时需要携带服务端返回的searchId
 - session_id: 会话ID，第一次请求可不传，翻页时携带服务端返回的sessionId
 - sort: 排序规则，默认综合
    - "sales_qty": 销量
    - "price_asc": 价格升序
    - "price_desc": 价格降序
- scope: 搜索范围，默认不限
    - "purchased": 买过的店
    - "following": 关注的店
- service_guarantee: 物流权益，多选用英文逗号分割
    - 可选值: "24小时发货", "七天无理由", "现货", "退货包运费"
- min_price: 最低价
 - max_price: 最高价
 - super_promotion: 标签ID
 ### 返回:
 - 搜索结果数据，包含：
    - items: 商品列表
    - searchId: 搜索ID（翻页必需）
    - sessionId: 会话ID（翻页必需）
    - has_more: 是否有更多数据
 ### 翻页说明:
 - 首次搜索：只传keyword和page=1
 - 翻页搜索：传入相同keyword，递增page，并携带首次返回的searchId和sessionId
 - 注意：更换关键词时不要复用之前的searchId

## search_products

`GET /api/v1/xiaohongshu/app/search_products`

<!-- Full path: /api/v1/xiaohongshu/app_v2/search_products -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 搜索关键词/Search keyword | 手机壳 |
| page | integer |  | 页码，从1开始/Page number, start from 1 (default: 1) | 1 |
| search_id | string |  | 搜索ID，翻页时传入首次搜索返回的值/Search ID for pagination (default: '') |  |
| source | string |  | 来源/Source (default: explore_feed) | explore_feed |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 根据关键词搜索小红书商品，每页返回 20 条结果，支持分页
 ### 参数:
 - keyword: 搜索关键词（必需），如 "手机壳"
 - page: 页码，从 1 开始
 - search_id: 搜索ID，翻页时传入首次搜索返回的值
 - source: 来源，默认 "explore_feed"
 ### 返回:
 - 搜索结果数据，包含商品列表和分页信息
 ### 翻页说明:
 - 首次请求：只传keyword和page
 - 翻页请求：传入首次搜索返回的 search_id

---

See SKILL.md for cross-group orchestration patterns.