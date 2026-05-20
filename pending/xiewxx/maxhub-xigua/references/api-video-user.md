# Video & User API / 视频与用户接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---
## fetch_one_video

`GET /api/v1/xigua/app/v2/fetch_one_video`

<!-- Full path: /api/v1/xigua/app/v2/fetch_one_video -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| item_id | string | ✅ | 作品id/Video id | 7354954305222377999 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取单个作品数据（信息较少，不包含标题等信息，但是包含相关视频的信息）
 ### 参数:
 - item_id: 作品id
 ### 返回:
 - 作品数据，其中包含视频链接的Base64编码播放地址，需要前端解码后使用，或者使用 /fetch_one_video_play_url
获取播放链接。

## fetch_one_video_play_url

`GET /api/v1/xigua/app/v2/fetch_one_video_play_url`

<!-- Full path: /api/v1/xigua/app/v2/fetch_one_video_play_url -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| item_id | string | ✅ | 作品id/Video id | 7354954305222377999 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取单个作品的播放链接，此接口返回的是已经解码后的播放链接，可以直接使用。
 ### 参数:
 - item_id: 作品id
 ### 返回:
 - 作品的播放链接的明文链接。

## fetch_one_video_v2

`GET /api/v1/xigua/app/v2/fetch_one_video_v2`

<!-- Full path: /api/v1/xigua/app/v2/fetch_one_video_v2 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| item_id | string | ✅ | 作品id/Video id | 7354954305222377999 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取单个作品数据（信息全面，包含标题等信息，但是不包含相关视频推荐信息）
 ### 参数:
 - item_id: 作品id
 ### 返回:
 - 作品数据，其中包含视频链接的Base64编码播放地址，需要前端解码后使用，或者使用 /fetch_one_video_play_url
获取播放链接。

## fetch_user_info

`GET /api/v1/xigua/app/v2/fetch_user_info`

<!-- Full path: /api/v1/xigua/app/v2/fetch_user_info -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string | ✅ | 用户id/User id | 52712347586 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 个人信息
### 参数:
- user_id: 用户id
### 返回:
- 个人信息

## fetch_user_post_list

`GET /api/v1/xigua/app/v2/fetch_user_post_list`

<!-- Full path: /api/v1/xigua/app/v2/fetch_user_post_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string | ✅ | 用户id/User id | 1922379661976311 |
| max_behot_time | string |  | 最大行为时间/Maximum behavior time |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取个人作品列表
 ### 参数:
 - user_id: 用户id
 - max_behot_time: 最大行为时间，默认空，第一次请求传空，后续请求传上一次请求返回数据中的JSON中的值。
 - max_behot_time的值可以是JSON路径为：$.data.data.[-1].behot_time
 - 也就是data中的最后一个元素的cursor值
 ### 返回:
 - 作品列表

## fetch_video_comment_list

`GET /api/v1/xigua/app/v2/fetch_video_comment_list`

<!-- Full path: /api/v1/xigua/app/v2/fetch_video_comment_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| item_id | string | ✅ | 作品id/Video id | 7354954305222377999 |
| offset | integer |  | 偏移量/Offset (default: 0) |  |
| count | integer |  | 数量/Count (default: 20) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 视频评论列表
 ### 参数:
 - item_id: 作品id
 - offset: 偏移量，第一次请求传0，后续请求传上一次请求返回的offset
 - count: 数量，默认20，建议保持默认。
 ### 返回:
 - 评论列表

## search_video

`GET /api/v1/xigua/app/v2/search_video`

<!-- Full path: /api/v1/xigua/app/v2/search_video -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 关键词/Keyword | 抖音 |
| offset | integer |  | 偏移量/Offset (default: 0) |  |
| order_type | string |  | 排序方式/Order type |  |
| min_duration | integer |  | 最小时长/Minimum duration |  |
| max_duration | integer |  | 最大时长/Maximum duration |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 搜索视频
 ### 参数:
 - keyword: 关键词
 - offset: 偏移量，第一次请求传0，后续请求传上一次请求返回的offset
 - order_type: 排序方式，为空时按照默认排序，以下为可选排序方式。
    - 最新: publish_time
    - 最热: play_count
- min_duration: 最小时长，默认空，单位秒。
 - max_duration: 最大时长，默认空，单位秒。
 ### 返回:
 - 视频列表

---

See SKILL.md for cross-group orchestration patterns.