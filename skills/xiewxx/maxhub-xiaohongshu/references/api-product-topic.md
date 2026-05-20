# Product & Topic API / 商品与话题接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---
## fetch_product_list

`GET /api/v1/xiaohongshu/web_v2/fetch_product_list`

<!-- Full path: /api/v1/xiaohongshu/web_v2/fetch_product_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string | ✅ | 用户ID/User ID | 627e35aa00000000210275ae |
| page | string |  | 页码/Page number (default: '1') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取小红书商品列表
### 参数:
- user_id: 用户ID
- page: 页码
### 返回:
- 小红书商品列表

## get_product_recommendations

`GET /api/v1/xiaohongshu/app_v2/get_product_recommendations`

<!-- Full path: /api/v1/xiaohongshu/app_v2/get_product_recommendations -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| sku_id | string | ✅ | 商品SKU ID/Product SKU ID | 669ddd44e05f3700011067ed |
| cursor_score | string |  | 分页游标，首次请求留空/Pagination cursor, leave empty for first request (default: '') |  |
| region | string |  | 地区/Region (default: US) | US |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 根据商品 SKU ID 获取相关推荐商品列表，使用游标分页
 ### 参数:
 - sku_id: 商品 SKU ID（必需），如 "669ddd44e05f3700011067ed"
 - cursor_score: 分页游标，首次请求留空，翻页时传入上一次响应中返回的 cursor_score 值
 - region: 地区，默认 "US"
 ### 返回:
 - 推荐商品列表数据
 ### 翻页说明:
 - 首次请求：cursor_score 留空
 - 翻页请求：传入上一次响应中返回的 cursor_score 值

---

See SKILL.md for cross-group orchestration patterns.