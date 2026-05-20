# Content API / 内容接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---
## fetch_column_article_detail

`GET /api/v1/zhihu/web/fetch_column_article_detail`

<!-- Full path: /api/v1/zhihu/web/fetch_column_article_detail -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| article_id | string | ✅ | 文章ID/Article ID |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取知乎专栏文章详情
### 参数:
- article_id: 文章ID
### 返回:
- 知乎专栏文章详情

## fetch_column_articles

`GET /api/v1/zhihu/web/fetch_column_articles`

<!-- Full path: /api/v1/zhihu/web/fetch_column_articles -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| column_id | string | ✅ | 专栏ID/Column ID |  |
| limit | string |  | 每页文章数量/Number of articles per page (default: '10') |  |
| offset | string |  | 偏移量/Offset (default: '0') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取知乎专栏文章列表
### 参数:
- column_id: 专栏ID
- limit: 每页文章数量
- offset: 偏移量
### 返回:
- 知乎专栏文章列表

## fetch_column_comment_config

`GET /api/v1/zhihu/web/fetch_column_comment_config`

<!-- Full path: /api/v1/zhihu/web/fetch_column_comment_config -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| article_id | string | ✅ | 文章ID/Article ID |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取知乎专栏评论区配置
### 参数:
- article_id: 文章ID
### 返回:
- 知乎专栏评论区配置

## fetch_column_recommend

`GET /api/v1/zhihu/web/fetch_column_recommend`

<!-- Full path: /api/v1/zhihu/web/fetch_column_recommend -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| article_id | string | ✅ | 文章ID/Article ID |  |
| limit | string |  | 每页专栏数量/Number of columns per page (default: '12') |  |
| offset | string |  | 偏移量/Offset (default: '0') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取知乎相似专栏推荐
### 参数:
- article_id: 文章ID
- limit: 每页专栏数量
- offset: 偏移量
### 返回:
- 知乎相似专栏推荐

## fetch_column_relationship

`GET /api/v1/zhihu/web/fetch_column_relationship`

<!-- Full path: /api/v1/zhihu/web/fetch_column_relationship -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| article_id | string | ✅ | 文章ID/Article ID |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取知乎专栏文章互动关系
### 参数:
- article_id: 文章ID
### 返回:
- 知乎专栏互动关系

## fetch_column_search_v3

`GET /api/v1/zhihu/web/fetch_column_search_v3`

<!-- Full path: /api/v1/zhihu/web/fetch_column_search_v3 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 搜索关键词/Search Keywords |  |
| offset | string |  | 偏移量/Offset (default: '0') |  |
| limit | string |  | 每页专栏数量/Number of columns per page (default: '20') |  |
| search_hash_id | string |  | 搜索哈希ID/Search Hash ID (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取知乎专栏搜索V3
### 参数:
- keyword: 搜索关键词
- offset: 偏移量
- limit: 每页专栏数量
- search_hash_id: 搜索哈希ID
### 返回:
- 知乎专栏搜索V3

## fetch_comment_v5

`GET /api/v1/zhihu/web/fetch_comment_v5`

<!-- Full path: /api/v1/zhihu/web/fetch_comment_v5 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| answer_id | string | ✅ | 回答ID/Answer ID |  |
| order_by | string |  | 排序/Sort (default: score) |  |
| limit | string |  | 每页评论数量/Number of comments per page (default: '20') |  |
| offset | string |  | 偏移量/Offset (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取知乎评论区V5
### 参数:
- answer_id: 回答ID
- order_by: 排序
    - score 最热排序
    - ts 最新排序
- limit: 每页评论数量
- offset: 偏移量/页码
### 返回:
- 知乎评论区V5

## fetch_hot_list

`GET /api/v1/zhihu/web/fetch_hot_list`

<!-- Full path: /api/v1/zhihu/web/fetch_hot_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| limit | string |  | 每页文章数量/Number of articles per page (default: '50') |  |
| desktop | string |  | 是否为桌面端/Is it a desktop (default: 'true') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取知乎首页热榜
### 参数:
- limit: 每页文章数量
- desktop: 是否为桌面端
### 返回:
- 知乎首页热榜

## fetch_sub_comment_v5

`GET /api/v1/zhihu/web/fetch_sub_comment_v5`

<!-- Full path: /api/v1/zhihu/web/fetch_sub_comment_v5 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| comment_id | string | ✅ | 评论ID/Comment ID |  |
| order_by | string |  | 排序/Sort (default: score) |  |
| limit | string |  | 每页评论数量/Number of comments per page (default: '20') |  |
| offset | string |  | 偏移量/Offset (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取知乎子评论区V5
### 参数:
- comment_id: 评论ID
- order_by: 排序
    - score 最热排序
    - ts 最新排序
- limit: 每页评论数量
- offset: 偏移量/页码
### 返回:
- 知乎子评论区V5

## fetch_user_articles

`GET /api/v1/zhihu/web/fetch_user_articles`

<!-- Full path: /api/v1/zhihu/web/fetch_user_articles -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_url_token | string | ✅ | 用户ID/User ID |  |
| offset | string |  | 偏移量/Offset (default: '0') |  |
| limit | string |  | 每页文章数量/Number of articles per page (default: '20') |  |
| sort_type | string (created/voteups) |  | 排序类型/Sort Type (default: created) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取知乎用户的文章列表
### 参数:
- user_url_token: 用户ID
- offset: 偏移量
- limit: 每页文章数量
- sort_type: 排序类型
    - created 按发布时间排序
    - voteups 按点赞数排序
### 返回:
- 知乎用户的文章列表

## fetch_user_follow_columns

`GET /api/v1/zhihu/web/fetch_user_follow_columns`

<!-- Full path: /api/v1/zhihu/web/fetch_user_follow_columns -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_url_token | string | ✅ | 用户ID/User ID |  |
| offset | string |  | 偏移量/Offset (default: '0') |  |
| limit | string |  | 每页专栏数量/Number of columns per page (default: '20') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取知乎用户订阅的专栏
### 参数:
- user_url_token: 用户ID
- offset: 偏移量
- limit: 每页专栏数量
### 返回:
- 知乎用户订阅的专栏

## fetch_user_included_articles

`GET /api/v1/zhihu/web/fetch_user_included_articles`

<!-- Full path: /api/v1/zhihu/web/fetch_user_included_articles -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_url_token | string | ✅ | 用户ID/User ID |  |
| offset | string |  | 偏移量/Offset (default: '0') |  |
| limit | string |  | 每页文章数量/Number of articles per page (default: '20') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取知乎用户的被收录文章列表
### 参数:
- user_url_token: 用户ID
- offset: 偏移量
- limit: 每页文章数量
### 返回:
- 知乎用户的被收录文章列表

---

See SKILL.md for cross-group orchestration patterns.