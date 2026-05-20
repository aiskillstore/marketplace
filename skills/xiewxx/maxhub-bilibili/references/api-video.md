# Video Data API / 视频数据接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---
## bv_to_aid

`GET /api/v1/bilibili/web/bv_to_aid`

<!-- Full path: /api/v1/bilibili/web/bv_to_aid -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| bv_id | string | ✅ | 作品id/Video id | BV1M1421t7hT |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 通过bv号获得视频aid号
### 参数:
- bv_id: 作品id
### 返回:
- 视频aid号

## fetch_com_popular

`GET /api/v1/bilibili/web/fetch_com_popular`

<!-- Full path: /api/v1/bilibili/web/fetch_com_popular -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| pn | integer |  | 页码/Page number (default: 1) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取综合热门视频信息
### 参数:
- pn: 页码
### 返回:
- 综合热门视频信息

## fetch_comment_reply

`GET /api/v1/bilibili/web/fetch_comment_reply`

<!-- Full path: /api/v1/bilibili/web/fetch_comment_reply -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| bv_id | string | ✅ | 作品id/Video id | BV1M1421t7hT |
| pn | integer |  | 页码/Page number (default: 1) |  |
| rpid | string | ✅ | 回复id/Reply id | 237109455120 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取视频下指定评论的回复
### 参数:
- bv_id: 作品id
- pn: 页码
- rpid: 回复id
### 返回:
- 指定评论的回复数据

## fetch_dynamic_detail

`GET /api/v1/bilibili/web/fetch_dynamic_detail`

<!-- Full path: /api/v1/bilibili/web/fetch_dynamic_detail -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| dynamic_id | string | ✅ | 动态id/Dynamic id | 1172584638000922630 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取指定动态的详情信息（v1接口）
### 参数:
- dynamic_id: 动态id
### 返回:
- 动态详情数据

## fetch_dynamic_detail_v2

`GET /api/v1/bilibili/web/fetch_dynamic_detail_v2`

<!-- Full path: /api/v1/bilibili/web/fetch_dynamic_detail_v2 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| dynamic_id | string | ✅ | 动态id/Dynamic id | 1172584638000922630 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取指定动态的详情信息（v2接口）
### 参数:
- dynamic_id: 动态id
### 返回:
- 动态详情数据

## fetch_home_feed

`GET /api/v1/bilibili/app/fetch_home_feed`

<!-- Full path: /api/v1/bilibili/app/fetch_home_feed -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| idx | integer |  | 页面索引/Page index |  |
| flush | integer |  | 刷新标记/Flush flag (0=普通加载, 1=刷新) (default: 0) |  |
| pull | boolean |  | 是否下拉刷新/Pull to refresh (default: true) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取主页推荐视频流
### 参数:
- idx: 页面索引，默认使用当前时间戳
- flush: 刷新标记（0=普通加载, 1=刷新）
- pull: 是否下拉刷新
### 返回:
- 推荐视频流数据

## fetch_live_room_detail

`GET /api/v1/bilibili/web/fetch_live_room_detail`

<!-- Full path: /api/v1/bilibili/web/fetch_live_room_detail -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| room_id | string | ✅ | 直播间ID/Live room ID | 22816111 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取指定直播间信息
### 参数:
- room_id: 直播间ID
### 返回:
- 指定直播间信息

## fetch_live_videos

`GET /api/v1/bilibili/web/fetch_live_videos`

<!-- Full path: /api/v1/bilibili/web/fetch_live_videos -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| room_id | string | ✅ | 直播间ID/Live room ID | 1815229528 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取指定直播间视频流
### 参数:
- room_id: 直播间ID
### 返回:
- 指定直播间视频流

## fetch_one_video

`GET /api/v1/bilibili/app/fetch_one_video`

<!-- Full path: /api/v1/bilibili/app/fetch_one_video -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| av_id | string |  | AV号/AV ID | 115568241811221 |
| bv_id | string |  | BV号/BV ID | BV18SCrBGE9E |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取单个视频详情信息（APP接口）
### 参数:
- av_id: AV号（与bv_id二选一）
- bv_id: BV号（与av_id二选一）
### 返回:
- 视频详情信息

## fetch_one_video

`GET /api/v1/bilibili/app/fetch_one_video`

<!-- Full path: /api/v1/bilibili/web/fetch_one_video -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| bv_id | string | ✅ | 作品id/Video id | BV1M1421t7hT |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取单个视频详情信息
### 参数:
- bv_id: 作品id
### 返回:
- 视频详情信息

## fetch_one_video_v2

`GET /api/v1/bilibili/web/fetch_one_video_v2`

<!-- Full path: /api/v1/bilibili/web/fetch_one_video_v2 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| a_id | string | ✅ | 作品id/Video id | 114006081739452 |
| c_id | string | ✅ | 作品cid/Video cid | 28400484458 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取单个视频详情信息V2
### 参数:
- a_id: 作品id
- c_id: 作品cid
### 返回:
- 视频详情信息V2

## fetch_one_video_v3

`GET /api/v1/bilibili/web/fetch_one_video_v3`

<!-- Full path: /api/v1/bilibili/web/fetch_one_video_v3 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| url | string | ✅ | 视频链接/Video URL | https://www.bilibili.com/video/BV1S5uKzzE4r |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取单个视频详情信息V3
### 参数:
- url: 视频链接
### 返回:
- 视频详情信息V3

## fetch_reply_detail

`GET /api/v1/bilibili/app/fetch_reply_detail`

<!-- Full path: /api/v1/bilibili/app/fetch_reply_detail -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| root | string | ✅ | 一级评论ID/Root comment ID | 241743663521 |
| av_id | string |  | AV号/AV ID | 113100682434775 |
| bv_id | string |  | BV号/BV ID | BV18SCrBGE9E |
| next_offset | integer |  | 下一页游标/Next page cursor (default: 0) |  |
| ps | integer |  | 每页数量/Page size (default: 20) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取二级评论回复
### 参数:
- root: 一级评论ID（必填）
- av_id: AV号（与bv_id二选一）
- bv_id: BV号（与av_id二选一）
- next_offset: 下一页游标
- ps: 每页数量
### 返回:
- 二级评论列表数据

## fetch_user_collection_videos

`GET /api/v1/bilibili/web/fetch_user_collection_videos`

<!-- Full path: /api/v1/bilibili/web/fetch_user_collection_videos -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| folder_id | string | ✅ | 收藏夹id/collection folder id | 1756059545 |
| pn | integer |  | 页码/Page number (default: 1) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取指定收藏夹内视频数据
### 参数:
- folder_id: 用户UID
- pn: 页码
### 返回:
- 指定收藏夹内视频数据

## fetch_user_post_videos

`GET /api/v1/bilibili/web/fetch_user_post_videos`

<!-- Full path: /api/v1/bilibili/web/fetch_user_post_videos -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| uid | string | ✅ | 用户UID | 178360345 |
| pn | integer |  | 页码/Page number (default: 1) |  |
| order | string |  | 排序方式/Order method (default: pubdate) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取用户发布的视频数据
### 参数:
- uid: 用户UID
- pn: 页码
- order: 排序方式
    - pubdate 最新发布
    - click 最多播放
    - stow 最多收藏
### 返回:
- 用户发布的视频数据

## fetch_user_videos

`GET /api/v1/bilibili/app/fetch_user_videos`

<!-- Full path: /api/v1/bilibili/app/fetch_user_videos -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string | ✅ | 用户ID/User ID | 203680252 |
| post_filter | string |  | 过滤类型/Filter type (archive/season/contribute) (default: archive) |  |
| page | integer |  | 页码/Page number (default: 1) |  |
| ps | integer |  | 每页数量/Page size (default: 20) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取用户投稿视频列表
### 参数:
- user_id: 用户ID（必填）
- post_filter: 过滤类型（archive=投稿, season=合集, contribute=贡献）
- page: 页码
- ps: 每页数量
### 返回:
- 用户投稿视频列表

## fetch_video_comments

`GET /api/v1/bilibili/app/fetch_video_comments`

<!-- Full path: /api/v1/bilibili/app/fetch_video_comments -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| av_id | string |  | AV号/AV ID | 115568241811221 |
| bv_id | string |  | BV号/BV ID | BV18SCrBGE9E |
| mode | integer |  | 排序模式/Sort mode (3=热门/hot, 2=时间/time) (default: 3) |  |
| next_offset | integer |  | 分页游标/Pagination cursor (default: 1) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取视频评论列表
### 参数:
- av_id: AV号（与bv_id二选一）
- bv_id: BV号（与av_id二选一）
- mode: 排序模式（3=热门, 2=时间）
- next_offset: 分页游标
### 返回:
- 评论列表数据

## fetch_video_comments

`GET /api/v1/bilibili/app/fetch_video_comments`

<!-- Full path: /api/v1/bilibili/web/fetch_video_comments -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| bv_id | string | ✅ | 作品id/Video id | BV1M1421t7hT |
| pn | integer |  | 页码/Page number (default: 1) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取指定视频的评论
### 参数:
- bv_id: 作品id
- pn: 页码
### 返回:
- 指定视频的评论数据

## fetch_video_danmaku

`GET /api/v1/bilibili/web/fetch_video_danmaku`

<!-- Full path: /api/v1/bilibili/web/fetch_video_danmaku -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| cid | string | ✅ | 作品cid/Video cid | 1639235405 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取视频实时弹幕
### 参数:
- cid: 作品cid
### 返回:
- 视频实时弹幕

## fetch_video_detail

`GET /api/v1/bilibili/web/fetch_video_detail`

<!-- Full path: /api/v1/bilibili/web/fetch_video_detail -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| aid | string | ✅ | 作品id/Video id | 114902186396822 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取单个视频详情
### 参数:
- aid: 作品id
### 返回:
- 视频详情

## fetch_video_parts

`GET /api/v1/bilibili/web/fetch_video_parts`

<!-- Full path: /api/v1/bilibili/web/fetch_video_parts -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| bv_id | string | ✅ | 作品id/Video id | BV1vf421i7hV |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 通过bv号获得视频分p信息
### 参数:
- bv_id: 作品id
### 返回:
- 视频分p信息

## fetch_video_play_info

`GET /api/v1/bilibili/web/fetch_video_play_info`

<!-- Full path: /api/v1/bilibili/web/fetch_video_play_info -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| url | string | ✅ | 视频链接/Video URL | https://www.bilibili.com/video/BV1S5uKzzE4r |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取单个视频播放信息
### 参数:
- url: 视频链接
### 返回:
- 视频播放信息

## fetch_video_playurl

`GET /api/v1/bilibili/web/fetch_video_playurl`

<!-- Full path: /api/v1/bilibili/web/fetch_video_playurl -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| bv_id | string | ✅ | 作品id/Video id | BV1y7411Q7Eq |
| cid | string | ✅ | 作品cid/Video cid | 171776208 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取视频流地址
### 参数:
- bv_id: 作品id
- cid: 作品cid
### 返回:
- 视频流地址

## fetch_video_subtitle

`GET /api/v1/bilibili/web/fetch_video_subtitle`

<!-- Full path: /api/v1/bilibili/web/fetch_video_subtitle -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| a_id | string | ✅ | 作品id/Video id | 114006081739452 |
| c_id | string | ✅ | 作品cid/Video cid | 28400484458 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取视频字幕信息
### 参数:
- a_id: 作品id
- c_id: 作品cid
### 返回:
- 视频字幕信息

## fetch_vip_video_playurl

`POST /api/v1/bilibili/web/fetch_vip_video_playurl`

<!-- Full path: /api/v1/bilibili/web/fetch_vip_video_playurl -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取大会员清晰度视频流地址
### 参数:
- bv_id: 作品id
- cid: 作品cid
- cookie: 大会员用户Cookie
### 返回:
- 大会员清晰度视频流地址

---

See SKILL.md for cross-group orchestration patterns.