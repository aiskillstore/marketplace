# Content & Ads API / 内容与广告接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---
## get_ad_detail

`GET /api/v1/linkedin/web/get_ad_detail`

<!-- Full path: /api/v1/linkedin/web/get_ad_detail -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| ad_id | string | ✅ | 广告ID/Ad ID | 637671316 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取LinkedIn广告的详情
 ### 参数:
- ad_id: 广告ID（必填）
 ### 返回:
- 广告详情数据

## get_comment_replies

`GET /api/v1/linkedin/web_v2/get_comment_replies`

<!-- Full path: /api/v1/linkedin/web_v2/get_comment_replies -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| comment_urn | string | ✅ | 父评论URN/Parent comment URN | >- |
| post_urn | string |  | >- | urn:li:activity:7193456789012345678 |
| count | integer |  | '' (default: 10) |  |
| pagination_token | string |  | 上一页响应里的 paginationToken |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 拉取一条评论下的子回复（楼中楼）。
 - 按 LinkedIn cursor 分页：首次调用留空 `pagination_token`，下一页用响应里返回的 token。
  ### 参数:
 - comment_urn: 父评论 URN
  - 推荐传完整形式：`urn:li:fsd_comment:(<commentId>,<postUrn>)`
  - 若只有数字 ID，需同时传 `post_urn`，后端会自动拼接
- post_urn: 帖子 URN（仅当 `comment_urn` 不完整时必填）
 - count: 每页数量（1-50，默认 10）
 - pagination_token: 分页游标，首次留空；下一页用响应里 `data.metadata.paginationToken`
  ### 返回:
 - data.elements: 回复数组，每条含回复者信息 / 文本 / 时间 / 点赞数 / 是否被作者赞过
 - data.metadata.paginationToken: 下一页游标（无下一页时为 null）

## get_comments_replies

`GET /api/v1/linkedin/web/get_comments_replies`

<!-- Full path: /api/v1/linkedin/web/get_comments_replies -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| post_id | string | ✅ | 帖子ID/Post ID | 7244804629786419202 |
| comment_id | string | ✅ | 评论ID/Comment ID |  |
| previous_replies_token | string | ✅ | 前一组回复的令牌/Previous replies token |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取LinkedIn评论的回复
 ### 参数:
- post_id: 帖子ID（必填）
- comment_id: 评论ID（必填）
- previous_replies_token: 前一组回复的令牌（必填）
 ### 返回:
- 评论回复数据

## search_ads

`GET /api/v1/linkedin/web/search_ads`

<!-- Full path: /api/v1/linkedin/web/search_ads -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string |  | >- | data |
| advertiser_name | string |  | 广告主名称/Advertiser name |  |
| country | string |  | 国家代码过滤/Country code filter | US |
| date | string |  | >- |  |
| pagination_token | string |  | 分页令牌/Pagination token |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 搜索LinkedIn广告库（Ad Library）
  ### 参数:
 - keyword: 搜索关键词（keyword 与 advertiser_name 至少提供一个）
 - advertiser_name: 广告主名称（可选）
 - country: 国家代码过滤，例如 US（可选）
 - date: 日期过滤，可选值：last-30-days, current-month, current-year, last-year
 - pagination_token: 分页令牌（可选）
  ### 返回:
 - 广告搜索结果数据

---

See SKILL.md for cross-group orchestration patterns.