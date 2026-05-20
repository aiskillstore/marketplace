# Post & User API / 帖子与用户接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---
## fetch_post_detail

`GET /api/v1/threads/web/fetch_post_detail`

<!-- Full path: /api/v1/threads/web/fetch_post_detail -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| post_id | string | ✅ | 帖子ID/Post ID | 3349029093483693129 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取Threads帖子详情
 ### 参数:
 - post_id: 帖子ID（纯数字），例如：3349029093483693129，可以从其他接口获取，如果是使用URL获取，去调用
/fetch_post_detail_v2 接口。
 ### 返回:
 - 帖子详情数据，包含:
    - id: 帖子ID
    - text: 帖子文本内容
    - user: 发布者信息
    - image_versions2: 图片信息
    - video_versions: 视频信息
    - like_count: 点赞数
    - text_post_app_info: 帖子应用信息
    - 等等...

## fetch_post_detail_v2

`GET /api/v1/threads/web/fetch_post_detail_v2`

<!-- Full path: /api/v1/threads/web/fetch_post_detail_v2 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| post_id | string |  | 帖子短代码/Post short code | DPVUglOjOUu |
| url | string |  | 完整帖子URL/Full post URL | https://www.threads.com/@taylorswift/post/DPVUglOjOUu |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取Threads帖子详情（支持短代码和完整URL）
 ### 参数:
 - post_id:
帖子短代码（可选），例如：DPVUglOjOUu，可以从帖子URL中提取，例如：https://www.threads.com/@taylorswift/post/DPVUglOjOUu
中的 DPVUglOjOUu
 - url:
完整的帖子URL（可选），例如：https://www.threads.com/@taylorswift/post/DPVUglOjOUu
 - 注意：post_id 和 url 至少提供一个参数
 ### 返回:
 - 帖子详情数据，包含:
    - post_id: 帖子ID
    - text: 帖子文本内容
    - user: 发布者信息
    - media: 媒体信息（图片、视频）
    - like_count: 点赞数
    - reply_count: 回复数
    - repost_count: 转发数
    - timestamp: 发布时间
    - 等等...

## search_profiles

`GET /api/v1/threads/web/search_profiles`

<!-- Full path: /api/v1/threads/web/search_profiles -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| query | string | ✅ | 搜索关键词/Search query | mark |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 搜索Threads用户档案
### 参数:
- query: 搜索关键词，例如：mark
### 返回:
- 搜索结果数据，包含:
    - users: 用户列表
    - 每个用户包含:
        - pk: 用户ID
        - username: 用户名
        - full_name: 全名
        - profile_pic_url: 头像URL
        - is_verified: 是否认证
        - follower_count: 粉丝数
        - 等等...

---

See SKILL.md for cross-group orchestration patterns.