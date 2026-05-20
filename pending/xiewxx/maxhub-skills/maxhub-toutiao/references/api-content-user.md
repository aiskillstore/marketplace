# Content & User API / 内容与用户接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---
## get_article_info

`GET /api/v1/toutiao/app/get_article_info`

<!-- Full path: /api/v1/toutiao/app/get_article_info -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| group_id | string | ✅ | 作品ID/Post ID | 7450114952884503059 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取指定文章的信息
### 参数:
- group_id: 作品ID，可以从链接中获取
    - 例如: https://www.toutiao.com/article/7450114952884503059/
### 返回:
- 作品信息

## get_article_info

`GET /api/v1/toutiao/app/get_article_info`

<!-- Full path: /api/v1/toutiao/web/get_article_info -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| aweme_id | string | ✅ | 作品ID/Post ID | 7450114952884503059 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取指定文章的信息
### 参数:
- aweme_id: 作品ID，可以从链接中获取
    - 例如: https://www.toutiao.com/article/7450114952884503059/
### 返回:
- 作品信息

## get_comments

`GET /api/v1/toutiao/app/get_comments`

<!-- Full path: /api/v1/toutiao/app/get_comments -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| group_id | string | ✅ | 作品ID/Post ID | 7453372680222523931 |
| offset | string | ✅ | 偏移量/Offset | 0 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定作品的评论
 ### 参数:
 - group_id: 作品ID，可以从链接中获取
    - 例如: https://www.toutiao.com/i7453372680222523931/
- offset: 偏移量，用于分页，默认为0，然后每次加20
 ### 返回:
 - 评论列表

## get_user_id

`GET /api/v1/toutiao/app/get_user_id`

<!-- Full path: /api/v1/toutiao/app/get_user_id -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_profile_url | string | ✅ | 用户主页链接/User profile URL | >- |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 从头条用户主页获取用户user_id
 ### 参数:
 - user_profile_url: 用户主页链接
    - 例如: https://www.toutiao.com/c/user/token/MS4wLjABAAAAwK6echNksY69R8l2vcZudupfhTItbGSGt-8ineO5UaB4L-djqkYDgB6TkAdMvrmW/
### 返回:
 - 用户ID

## get_user_info

`GET /api/v1/toutiao/app/get_user_info`

<!-- Full path: /api/v1/toutiao/app/get_user_info -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string | ✅ | 用户ID/User ID | 1352838578180211 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取指定用户的信息
### 参数:
- user_id: 用户ID，可以从以下接口获取：
    - `/api/v1/toutiao/app/get_user_id`
### 返回:
- 用户信息

## get_video_info

`GET /api/v1/toutiao/app/get_video_info`

<!-- Full path: /api/v1/toutiao/app/get_video_info -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| group_id | string | ✅ | 作品ID/Post ID | 7431543350882206242 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取指定视频的信息
### 参数:
- group_id: 作品ID，可以从链接中获取
    - 例如: https://www.toutiao.com/video/7431543350882206242/
### 返回:
- 作品信息

## get_video_info

`GET /api/v1/toutiao/app/get_video_info`

<!-- Full path: /api/v1/toutiao/web/get_video_info -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| aweme_id | string | ✅ | 作品ID/Post ID | 7431543350882206242 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取指定视频的信息
### 参数:
- aweme_id: 作品ID，可以从链接中获取
    - 例如: https://www.toutiao.com/video/7431543350882206242/
### 返回:
- 作品信息

---

See SKILL.md for cross-group orchestration patterns.