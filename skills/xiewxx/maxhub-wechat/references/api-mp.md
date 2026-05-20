# Media Platform API / 公众号接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---
## fetch_mp_article_ad

`GET /api/v1/wechat_mp/web/fetch_mp_article_ad`

<!-- Full path: /api/v1/wechat_mp/web/fetch_mp_article_ad -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| url | string | ✅ | 文章链接/Article URL | https://mp.weixin.qq.com/s/hrTDuwh0pWyJFYC93kKCrg |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取微信公众号广告
### 参数:
- url: 文章链接
### 返回:
- 广告

## fetch_mp_article_list

`GET /api/v1/wechat_mp/web/fetch_mp_article_list`

<!-- Full path: /api/v1/wechat_mp/web/fetch_mp_article_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| ghid | string | ✅ | 公众号ID/MP ID | gh_a3d35d4c9d3f |
| offset | string |  | 偏移量/Offset (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取微信公众号文章列表
### 参数:
- ghid: 公众号ID
- offset: 偏移量
### 返回:
- 文章列表

## fetch_mp_article_read_count

`GET /api/v1/wechat_mp/web/fetch_mp_article_read_count`

<!-- Full path: /api/v1/wechat_mp/web/fetch_mp_article_read_count -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| url | string | ✅ | 文章链接/Article URL | https://mp.weixin.qq.com/s/hrTDuwh0pWyJFYC93kKCrg |
| comment_id | string | ✅ | 评论ID/Comment ID |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取微信公众号文章阅读量
### 参数:
- url: 文章链接
- comment_id: 评论ID
### 返回:
- 阅读量

## fetch_mp_article_url

`GET /api/v1/wechat_mp/web/fetch_mp_article_url`

<!-- Full path: /api/v1/wechat_mp/web/fetch_mp_article_url -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| sogou_url | string | ✅ | 搜狗链接/Sogou URL | >- |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取微信公众号文章永久链接
 ### 参数:
 - sogou_url: 搜狗链接
 ### 返回:
 - 永久链接

## fetch_mp_article_url_conversion

`GET /api/v1/wechat_mp/web/fetch_mp_article_url_conversion`

<!-- Full path: /api/v1/wechat_mp/web/fetch_mp_article_url_conversion -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| url | string | ✅ | 文章链接/Article URL | >- |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取微信公众号长链接转短链接
 ### 参数:
 - url: 文章链接
 ### 返回:
 - 短链接

## fetch_mp_related_articles

`GET /api/v1/wechat_mp/web/fetch_mp_related_articles`

<!-- Full path: /api/v1/wechat_mp/web/fetch_mp_related_articles -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| url | string | ✅ | 文章链接/Article URL | https://mp.weixin.qq.com/s/Ko5V9jw9kwL8TO6Q7J3UqQ |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取微信公众号关联文章
### 参数:
- url: 文章链接
### 返回:
- 关联文章

---

See SKILL.md for cross-group orchestration patterns.