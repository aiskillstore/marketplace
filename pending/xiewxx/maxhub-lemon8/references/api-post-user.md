# Post & User API / 帖子与用户接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---
## fetch_discover_tab_information_tabs

`GET /api/v1/lemon8/app/fetch_discover_tab_information_tabs`

<!-- Full path: /api/v1/lemon8/app/fetch_discover_tab_information_tabs -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取发现页（搜索页下方的推荐内容 - Editor's Picks）
### 返回:
- 推荐内容

## fetch_post_comment_list

`GET /api/v1/lemon8/app/fetch_post_comment_list`

<!-- Full path: /api/v1/lemon8/app/fetch_post_comment_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| group_id | string | ✅ | 作品的group_id/Post's group_id | 7361926875709129222 |
| item_id | string | ✅ | 作品的item_id/Post's item_id | 7361926875709129222 |
| media_id | string | ✅ | 作品的media_id/Post's media_id | 7428056850216862763 |
| offset | string |  | 翻页参数/Pagination parameter (default: '0') | 0 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定作品的评论列表
 ### 参数:
 - group_id: 作品的group_id，可以从接口`/lemon8/app/fetch_post_detail`获取
 - item_id: 作品的item_id，可以从接口`/lemon8/app/fetch_post_detail` 或
`/lemon8/app/get_item_id`获取
 - media_id: 作品的media_id，可以从接口`/lemon8/app/fetch_post_detail`获取
 - offset: 翻页参数，可以从上一次请求的返回结果中获取，第一次请求为空，后续请求使用上一次请求返回的offset进行翻页。
 ### 返回:
 - 评论列表

## fetch_post_detail

`GET /api/v1/lemon8/app/fetch_post_detail`

<!-- Full path: /api/v1/lemon8/app/fetch_post_detail -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| item_id | string | ✅ | 作品ID/Post ID | 7361926875709129222 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定作品的信息
 ### 参数:
 - item_id: 作品ID，可以从接口`/lemon8/app/get_item_id`获取
 ### 返回:
 - 作品信息

## fetch_topic_info

`GET /api/v1/lemon8/app/fetch_topic_info`

<!-- Full path: /api/v1/lemon8/app/fetch_topic_info -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| forum_id | string | ✅ | 话题ID/Topic ID | 7174447913778593798 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取话题信息
### 参数:
- forum_id: 话题ID，可以从下面的接口获取
    - 获取指定作品的信息：`/lemon8/app/fetch_post_detail`
    - 获取发现页的 Editor's Picks：`/lemon8/app/fetch_discover_tab_information_tabs`
    - 通过接口搜索 Hashtag：`/lemon8/app/fetch_search?search_tab=hashtag&keyword=lemon8`
### 返回:
- 话题信息

## fetch_topic_post_list

`GET /api/v1/lemon8/app/fetch_topic_post_list`

<!-- Full path: /api/v1/lemon8/app/fetch_topic_post_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| category | string | ✅ | 话题分类 ID/Topic category ID | 590 |
| max_behot_time | string |  | 翻页参数/Pagination parameter (default: '') |  |
| category_parameter | string | ✅ | 分类参数/Category parameter | 7174447913778593798 |
| hashtag_name | string | ✅ | Hashtag名称/Hashtag name | lemon8christmas |
| sort_type | string |  | 排序方式/Sort type (default: '0') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取话题作品列表
 ### 参数:
 - category: 话题分类 ID，可以从接口`/lemon8/app/fetch_topic_info`获取
 - max_behot_time:
翻页参数，可以从上一次请求的返回结果中获取，第一次请求为空，后续请求使用上一次请求返回的max_behot_time进行翻页。
 - category_parameter: 分类参数ID，可以从接口`/lemon8/app/fetch_topic_info`获取
 - hashtag_name: Hashtag名称，可以从接口`/lemon8/app/fetch_topic_info`获取
 - sort_type: 排序方式，0为默认排序，当前只支持使用默认排序，请不要传入其他值。
 ### 返回:
 - 作品列表

## fetch_user_follower_list

`GET /api/v1/lemon8/app/fetch_user_follower_list`

<!-- Full path: /api/v1/lemon8/app/fetch_user_follower_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string | ✅ | 用户ID/User ID | 7428056850216862763 |
| cursor | string |  | 翻页参数/Pagination parameter (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定用户的粉丝列表
 ### 参数:
 - user_id: 用户ID，可以从接口`/lemon8/app/get_user_id`获取
 - cursor: 翻页参数，可以从上一次请求的返回结果中获取，第一次请求为空，后续请求使用上一次请求返回的cursor进行翻页。
 ### 返回:
 - 粉丝列表

## fetch_user_following_list

`GET /api/v1/lemon8/app/fetch_user_following_list`

<!-- Full path: /api/v1/lemon8/app/fetch_user_following_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string | ✅ | 用户ID/User ID | 7428056850216862763 |
| cursor | string |  | 翻页参数/Pagination parameter (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定用户的关注列表
 ### 参数:
 - user_id: 用户ID，可以从接口`/lemon8/app/get_user_id`获取
 - cursor: 翻页参数，可以从上一次请求的返回结果中获取，第一次请求为空，后续请求使用上一次请求返回的cursor进行翻页。
 ### 返回:
 - 关注列表

## fetch_user_profile

`GET /api/v1/lemon8/app/fetch_user_profile`

<!-- Full path: /api/v1/lemon8/app/fetch_user_profile -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string | ✅ | 用户ID/User ID | 7217844966059656197 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定用户的信息
 ### 参数:
 - user_id: 用户ID，可以从接口`/lemon8/app/get_user_id`获取
 ### 返回:
 - 用户信息

## get_item_id

`GET /api/v1/lemon8/app/get_item_id`

<!-- Full path: /api/v1/lemon8/app/get_item_id -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| share_text | string | ✅ | 分享链接/Share link | https://v.lemon8-app.com/al/OghwFTppx |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 通过分享链接获取作品ID
 ### 参数:
 - share_text: 分享链接，支持长链接和短链接，可以从网页端以及APP中的分享按钮获取并复制。
 ### 返回:
 - 作品ID

## get_item_ids

`POST /api/v1/lemon8/app/get_item_ids`

<!-- Full path: /api/v1/lemon8/app/get_item_ids -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 通过分享链接批量获取作品ID，一次最多获取10个
 ### 参数:
 - share_texts: 分享链接列表，支持长链接和短链接，可以从网页端以及APP中的分享按钮获取并复制。
 ### 返回:
 - 作品ID列表

## get_user_id

`GET /api/v1/lemon8/app/get_user_id`

<!-- Full path: /api/v1/lemon8/app/get_user_id -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| share_text | string | ✅ | 分享链接/Share link | https://v.lemon8-app.com/al/OgZrsUppx |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 通过分享链接获取用户ID
 ### 参数:
 - share_text: 分享链接，支持长链接和短链接，可以从网页端以及APP中的分享按钮获取并复制。
 ### 返回:
 - 用户ID

## get_user_ids

`POST /api/v1/lemon8/app/get_user_ids`

<!-- Full path: /api/v1/lemon8/app/get_user_ids -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 通过分享链接批量获取用户ID，一次最多获取10个
 ### 参数:
 - share_texts: 分享链接列表，支持长链接和短链接，可以从网页端以及APP中的分享按钮获取并复制。
 ### 返回:
 - 用户ID列表

---

See SKILL.md for cross-group orchestration patterns.