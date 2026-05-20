# Tweet Data API / 推文数据接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---
## fetch_latest_post_comments

`GET /api/v1/twitter/web/fetch_latest_post_comments`

<!-- Full path: /api/v1/twitter/web/fetch_latest_post_comments -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| tweet_id | string | ✅ | 推文ID/Tweet ID | 1808168603721650364 |
| cursor | string |  | 游标/Cursor |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取最新的推文评论
 ### 参数:
 - tweet_id: 推文ID
 - cursor: 游标，默认为None，用于翻页，后续从上一次请求的返回结果中获取
 ### 返回:
 - 推文评论

## fetch_post_comments

`GET /api/v1/twitter/web/fetch_post_comments`

<!-- Full path: /api/v1/twitter/web/fetch_post_comments -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| tweet_id | string | ✅ | 推文ID/Tweet ID | 1835124037934367098 |
| cursor | string |  | 游标/Cursor |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取推文下的评论
 ### 参数:
 - tweet_id: 推文ID
 - cursor: 游标，默认为None，用于翻页，后续从上一次请求的返回结果中获取
 ### 返回:
 - 评论

## fetch_retweet_user_list

`GET /api/v1/twitter/web/fetch_retweet_user_list`

<!-- Full path: /api/v1/twitter/web/fetch_retweet_user_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| tweet_id | string | ✅ | 推文ID/Tweet ID | 1835124037934367098 |
| cursor | string |  | 游标/Cursor |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取转推用户列表
 ### 参数:
 - tweet_id:
推文ID，可以从推文链接中获取。例如：https://x.com/elonmusk/status/1808168603721650364 中的
1808168603721650364。
 - cursor: 游标，默认为None，用于翻页，后续从上一次请求的返回结果中获取
 ### 返回:
 - 转推用户列表

## fetch_tweet_detail

`GET /api/v1/twitter/web/fetch_tweet_detail`

<!-- Full path: /api/v1/twitter/web/fetch_tweet_detail -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| tweet_id | string | ✅ | 推文ID/Tweet ID | 1808168603721650364 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取单个推文数据
 ### 参数:
 - tweet_id:
推文ID，可以从推文链接中获取。例如：https://x.com/elonmusk/status/1808168603721650364 中的
1808168603721650364。
 ### 返回:
 - 推文数据

## fetch_user_followers

`GET /api/v1/twitter/web/fetch_user_followers`

<!-- Full path: /api/v1/twitter/web/fetch_user_followers -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| screen_name | string | ✅ | 用户名/Screen Name | elonmusk |
| cursor | string |  | 游标/Cursor |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取用户粉丝
 ### 参数:
 - screen_name:
用户名，例如：elonmusk，可以从用户主页链接中获取，例如：https://twitter.com/elonmusk 中的
elonmusk。
 - cursor: 游标，默认为None，用于翻页，后续从上一次请求的返回结果中获取
 ### 返回:
 - 用户粉丝

## fetch_user_followings

`GET /api/v1/twitter/web/fetch_user_followings`

<!-- Full path: /api/v1/twitter/web/fetch_user_followings -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| screen_name | string | ✅ | 用户名/Screen Name | elonmusk |
| cursor | string |  | 游标/Cursor |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取用户关注
 ### 参数:
 - screen_name:
用户名，例如：elonmusk，可以从用户主页链接中获取，例如：https://twitter.com/elonmusk 中的
elonmusk。
 - cursor: 游标，默认为None，用于翻页，后续从上一次请求的返回结果中获取
 ### 返回:
 - 用户关注

## fetch_user_media

`GET /api/v1/twitter/web/fetch_user_media`

<!-- Full path: /api/v1/twitter/web/fetch_user_media -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| screen_name | string | ✅ | 用户名/Screen Name | elonmusk |
| rest_id | integer |  | 用户ID/User ID | 44196397 |
| cursor | string |  | 翻页游标/Page Cursor |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取用户媒体
 ### 参数:
 - screen_name:
用户名，例如：elonmusk，可以从用户主页链接中获取，例如：https://twitter.com/elonmusk 中的
elonmusk。
 - rest_id: 用户ID，例如：44196397，如果使用用户ID则会忽略用户名，两者只能选其一。
 - cursor: 游标，默认为None，用于翻页，后续从上一次请求的返回结果中的 `next_cursor` 获取
 ### 返回:
 - 用户媒体

## fetch_user_post_tweet

`GET /api/v1/twitter/web/fetch_user_post_tweet`

<!-- Full path: /api/v1/twitter/web/fetch_user_post_tweet -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| screen_name | string |  | 用户名/Screen Name | elonmusk |
| rest_id | integer |  | 用户ID/User ID | 44196397 |
| cursor | string |  | 游标/Cursor |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取用户发帖
 ### 参数:
 - screen_name:
用户名，例如：elonmusk，可以从用户主页链接中获取，例如：https://twitter.com/elonmusk 中的
elonmusk。
 - rest_id: 用户ID，例如：44196397，如果使用用户ID则会忽略用户名，两者只能选其一。
 - cursor: 游标，默认为None，用于翻页，后续从上一次请求的返回结果中的JSON中获取。
 ### 返回:
 - 用户发帖

## fetch_user_profile

`GET /api/v1/twitter/web/fetch_user_profile`

<!-- Full path: /api/v1/twitter/web/fetch_user_profile -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| screen_name | string |  | 用户名/Screen Name | elonmusk |
| rest_id | integer |  | >- | 44196397 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取用户资料
 ### 参数:
 - screen_name:
用户名，例如：elonmusk，可以从用户主页链接中获取，例如：https://twitter.com/elonmusk 中的
elonmusk。
 - rest_id: 用户ID，例如：44196397，如果使用用户ID则会忽略用户名，两者只能选其一。
 ### 返回:
 - 用户资料

## fetch_user_tweet_replies

`GET /api/v1/twitter/web/fetch_user_tweet_replies`

<!-- Full path: /api/v1/twitter/web/fetch_user_tweet_replies -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| screen_name | string | ✅ | 用户名/Screen Name | elonmusk |
| cursor | string |  | 游标/Cursor |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取用户推文回复
 ### 参数:
 - screen_name:
用户名，例如：elonmusk，可以从用户主页链接中获取，例如：https://twitter.com/elonmusk 中的
elonmusk。
 - cursor: 游标，默认为None，用于翻页，后续从上一次请求的返回结果中获取
 ### 返回:
 - 用户推文回复

---

See SKILL.md for cross-group orchestration patterns.