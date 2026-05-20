# Video & Content API / 视频与内容接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---
## fetch_one_video

`GET /api/v1/kuaishou/app/fetch_one_video`

<!-- Full path: /api/v1/kuaishou/app/fetch_one_video -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| photo_id | string | ✅ | '' | 3xhpk3xcf6e4iac |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取单个作品数据接口 V1。
### 参数:
- photo_id: 作品ID，作品ID可以从分享链接中提取
    - 格式备注：支持纯数字版本的ID，也支持短字符串版本（eID）的ID，两种ID可以混合使用。
### 返回:
- 视频数据

## fetch_one_video_by_url

`GET /api/v1/kuaishou/app/fetch_one_video_by_url`

<!-- Full path: /api/v1/kuaishou/app/fetch_one_video_by_url -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| share_text | string | ✅ | '' | https://v.kuaishou.com/cNYP0Z |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 ### 参数:
 - share_text: 作品链接或分享文本
 ### 返回:
 - 视频数据

## fetch_one_video_comment

`GET /api/v1/kuaishou/app/fetch_one_video_comment`

<!-- Full path: /api/v1/kuaishou/app/fetch_one_video_comment -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| photo_id | string | ✅ | '' | 3x7gxp2zhgjv832 |
| pcursor | string |  | '' |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取单个作品评论数据
 ### 参数:
 - photo_id: 作品ID
    - 格式备注：支持纯数字版本的ID，也支持短字符串版本（eID）的ID，两种ID可以混合使用。
- pcursor: 评论游标，第一次请求为空，后续请求使用返回响应中的pcursor值进行翻页。
 ### 返回:
 - 评论数据

## fetch_videos_batch

`GET /api/v1/kuaishou/app/fetch_videos_batch`

<!-- Full path: /api/v1/kuaishou/app/fetch_videos_batch -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| photo_ids | string | ✅ | >- | 5228960823332207296,5196309727975443273,5222486898325987583 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 批量获取多个作品数据，单次请求最多支持40个视频ID。
 ### 参数:
 - photo_ids: 作品ID列表，多个ID用英文逗号分隔，单次最多40个
    - 格式备注：支持纯数字版本的ID，也支持短字符串版本（eID）的ID，两种ID可以混合使用。
### 返回:
 - 视频数据列表

## search_comprehensive

`GET /api/v1/kuaishou/app/search_comprehensive`

<!-- Full path: /api/v1/kuaishou/app/search_comprehensive -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | '' | 汽车之家 |
| pcursor | string |  | '' |  |
| sort_type | string |  | '可选值: all(综合排序), newest(最新发布), most_likes(最多点赞)' (default: all) |  |
| publish_time | string |  | '可选值: all(全部), one_day(近一日), one_week(近一周), one_month(近一月)' (default: all) |  |
| duration | string |  | >- (default: all) |  |
| search_scope | string |  | '可选值: all(全部)' (default: all) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 快手综合搜索接口，支持搜索视频、用户等内容，并提供多维度筛选功能。
 ### 参数:
 - keyword: 搜索关键词（必填）
 - pcursor: 分页游标，首次请求为空，后续使用响应中的pcursor值
 - sort_type: 排序方式
    - all: 综合排序（默认）
    - newest: 最新发布
    - most_likes: 最多点赞
- publish_time: 发布时间筛选
    - all: 全部时间（默认）
    - one_day: 近一日
    - one_week: 近一周
    - one_month: 近一月
- duration: 作品时长筛选
    - all: 全部时长（默认）
    - under_1_min: 1分钟以内
    - 1_to_5_min: 1-5分钟
    - over_5_min: 5分钟以上
- search_scope: 搜索范围
    - all: 全部（默认）
### 返回:
 - 搜索结果数据

---

See SKILL.md for cross-group orchestration patterns.