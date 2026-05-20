# Post & User API / 帖子与用户接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---
## fetch_hashtag_detail

`GET /api/v1/pipixia/app/fetch_hashtag_detail`

<!-- Full path: /api/v1/pipixia/app/fetch_hashtag_detail -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| hashtag_id | string | ✅ | 话题id/Hashtag id | 129559 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取话题详情数据。
### 参数:
- hashtag_id: 话题id，可以从分享链接中获取。
### 返回:
- 话题详情数据

## fetch_hashtag_post_list

`GET /api/v1/pipixia/app/fetch_hashtag_post_list`

<!-- Full path: /api/v1/pipixia/app/fetch_hashtag_post_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| hashtag_id | string | ✅ | 话题id/Hashtag id | 129559 |
| cursor | string |  | 翻页游标/Page cursor (default: '0') | 0 |
| feed_count | string |  | 翻页数量/Page count (default: '0') | 0 |
| hashtag_request_type | string |  | 话题请求类型/Hashtag request type (default: '0') | 0 |
| hashtag_sort_type | string |  | 话题排序类型/Hashtag sort type (default: '3') | 3 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取话题作品列表数据。
 ### 参数:
 - hashtag_id: 话题id，可以从分享链接中获取。
 - cursor: 翻页游标，默认为0，后续页码从上一页返回的 `loadmore_cursor` Key中获取对应值。
 - feed_count: 翻页数量，默认为0，后续每次翻页加1，比如第一页为0，第二页为1，第三页为2，以此类推。
 - hashtag_request_type: 话题请求类型，默认为0，可用值如下：
    - 0: 热门
    - 1: 最新
    - 2: 精华
- hashtag_sort_type: 话题排序类型，默认为3，可用值如下：
    - 3: 按热度
    - 2: 按时间，从新到旧
    - 1: 精华
### 返回:
 - 话题作品列表数据

## fetch_hot_search_board_detail

`GET /api/v1/pipixia/app/fetch_hot_search_board_detail`

<!-- Full path: /api/v1/pipixia/app/fetch_hot_search_board_detail -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| block_type | integer | ✅ | 榜单类型/Board type | 12 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取热搜榜单详情数据。
 ### 参数:
 - block_type: 榜单类型，可以从`/fetch_hot_search_board_list`接口中获取。
 ### 返回:
 - 热搜榜单详情数据

## fetch_hot_search_board_list

`GET /api/v1/pipixia/app/fetch_hot_search_board_list`

<!-- Full path: /api/v1/pipixia/app/fetch_hot_search_board_list -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取热搜榜单列表数据。
### 返回:
- 热搜榜单列表数据


### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| cell_id | string | ✅ | 作品id/Video id | 7411193113223371043 |
| cell_type | integer |  | 作品类型/Video type (default: 1) | 1 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 增加作品浏览数。
 ### 参数:
 - cell_id: 作品id，可以从分享链接中获取。
 - cell_type: 作品类型，1为视频，多大数保持默认值即可。
 ### 返回:
 - 执行结果

## fetch_post_comment_list

`GET /api/v1/pipixia/app/fetch_post_comment_list`

<!-- Full path: /api/v1/pipixia/app/fetch_post_comment_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| cell_id | string | ✅ | 作品id/Video id | 7411193113223371043 |
| cell_type | integer |  | 作品类型/Video type (default: 1) | 1 |
| offset | string |  | 翻页游标/Page cursor (default: '0') | 0 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取作品的评论列表。
 ### 参数:
 - cell_id: 作品id，可以从分享链接中获取。
 - cell_type: 作品类型，1为视频，多大数保持默认值即可。
 - offset: 翻页游标，默认为0，后续页码从上一页返回的 `offset` Key中获取对应值。
 ### 返回:
 - 作品评论列表

## fetch_post_detail

`GET /api/v1/pipixia/app/fetch_post_detail`

<!-- Full path: /api/v1/pipixia/app/fetch_post_detail -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| cell_id | string | ✅ | 作品id/Video id | 7411193113223371043 |
| cell_type | integer |  | 作品类型/Video type (default: 1) | 1 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取单个作品数据，支持图文、视频等。
 ### 参数:
 - cell_id: 作品id，可以从分享链接中获取。
 - cell_type: 作品类型，1为视频，多大数保持默认值即可。
 ### 返回:
 - 作品数据

## fetch_post_statistics

`GET /api/v1/pipixia/app/fetch_post_statistics`

<!-- Full path: /api/v1/pipixia/app/fetch_post_statistics -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| cell_id | string | ✅ | 作品id/Video id | 7411193113223371043 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取单个作品的统计数据，如点赞数、评论数、转发数等。
 ### 参数:
 - cell_id: 作品id，可以从分享链接中获取。
 ### 返回:
 - 作品统计数据

## fetch_user_follower_list

`GET /api/v1/pipixia/app/fetch_user_follower_list`

<!-- Full path: /api/v1/pipixia/app/fetch_user_follower_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string | ✅ | 用户id/User id | 1310254082831248 |
| cursor | string |  | 翻页游标/Page cursor (default: '0') | 0 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取用户的粉丝列表。
 ### 参数:
 - user_id: 用户id，可以从分享链接中获取。
 - cursor: 翻页游标，默认为0，后续页码从上一页返回的 `loadmore_cursor` Key中获取对应值。
 ### 返回:
 - 用户粉丝列表

## fetch_user_following_list

`GET /api/v1/pipixia/app/fetch_user_following_list`

<!-- Full path: /api/v1/pipixia/app/fetch_user_following_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string | ✅ | 用户id/User id | 1310254082831248 |
| cursor | string |  | 翻页游标/Page cursor (default: '0') | 0 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取用户的关注列表。
 ### 参数:
 - user_id: 用户id，可以从分享链接中获取。
 - cursor: 翻页游标，默认为0，后续页码从上一页返回的 `loadmore_cursor` Key中获取对应值。
 ### 返回:
 - 用户关注列表

## fetch_user_info

`GET /api/v1/pipixia/app/fetch_user_info`

<!-- Full path: /api/v1/pipixia/app/fetch_user_info -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string | ✅ | 用户id/User id | 1020401 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取用户信息，如昵称、性别、头像等。
### 参数:
- user_id: 用户id，可以从分享链接中获取。
### 返回:
- 用户信息

## fetch_user_post_list

`GET /api/v1/pipixia/app/fetch_user_post_list`

<!-- Full path: /api/v1/pipixia/app/fetch_user_post_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string | ✅ | 用户id/User id | 1310254082831248 |
| cursor | string |  | 翻页游标/Page cursor (default: '0') | 0 |
| feed_count | string |  | 翻页数量/Page count (default: '0') | 0 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取用户作品列表，如视频、图文等。
 ### 参数:
 - user_id: 用户id，可以从分享链接中获取。
 - cursor: 翻页游标，默认为0，后续页码从上一页返回的 `loadmore_cursor` Key中获取对应值。
 - feed_count: 翻页数量，默认为0，后续每次翻页加1，比如第一页为0，第二页为1，第三页为2，以此类推。
 ### 返回:
 - 用户作品列表

---

See SKILL.md for cross-group orchestration patterns.