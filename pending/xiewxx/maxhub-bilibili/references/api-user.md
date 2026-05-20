# User Data API / 用户数据接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---
## fetch_collect_folders

`GET /api/v1/bilibili/web/fetch_collect_folders`

<!-- Full path: /api/v1/bilibili/web/fetch_collect_folders -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| uid | string | ✅ | 用户UID | 178360345 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取用户收藏作品数据
### 参数:
- uid: 用户UID
### 返回:
- 用户收藏夹信息

## fetch_get_user_id

`GET /api/v1/bilibili/web/fetch_get_user_id`

<!-- Full path: /api/v1/bilibili/web/fetch_get_user_id -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| share_link | string | ✅ | 用户分享链接/User share link | https://b23.tv/1ZuB5NC |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 提取用户ID
### 参数:
- share_link: 用户分享链接
### 返回:
- 用户ID

## fetch_user_dynamic

`GET /api/v1/bilibili/web/fetch_user_dynamic`

<!-- Full path: /api/v1/bilibili/web/fetch_user_dynamic -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| uid | string | ✅ | 用户UID | 16015678 |
| offset | string |  | 开始索引/offset (default: '') | 953154282154098691 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取指定用户动态
### 参数:
- uid: 用户UID
- offset: 开始索引
### 返回:
- 指定用户动态数据

## fetch_user_info

`GET /api/v1/bilibili/app/fetch_user_info`

<!-- Full path: /api/v1/bilibili/app/fetch_user_info -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string | ✅ | 用户ID/User ID | 203680252 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取用户信息
### 参数:
- user_id: 用户ID（必填）
### 返回:
- 用户信息（包含粉丝数、关注数、投稿数等）

## fetch_user_profile

`GET /api/v1/bilibili/web/fetch_user_profile`

<!-- Full path: /api/v1/bilibili/web/fetch_user_profile -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| uid | string | ✅ | 用户UID | 178360345 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取指定用户的信息
### 参数:
- uid: 用户UID
### 返回:
- 指定用户的个人信息

## fetch_user_relation_stat

`GET /api/v1/bilibili/web/fetch_user_relation_stat`

<!-- Full path: /api/v1/bilibili/web/fetch_user_relation_stat -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| uid | string | ✅ | 用户UID/User UID | 178360345 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取用户关系状态统计信息（关注数、粉丝数）
### 参数:
- uid: 用户UID
### 返回:
- 用户关系状态统计数据
    - following: 关注数
    - follower: 粉丝数

## fetch_user_up_stat

`GET /api/v1/bilibili/web/fetch_user_up_stat`

<!-- Full path: /api/v1/bilibili/web/fetch_user_up_stat -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| uid | string | ✅ | 用户UID/User UID | 178360345 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取UP主状态统计信息（总获赞数、总播放数）
### 参数:
- uid: 用户UID
### 返回:
- UP主状态统计数据
    - archive: 视频相关统计
        - view: 总播放数
    - likes: 总获赞数

---

See SKILL.md for cross-group orchestration patterns.