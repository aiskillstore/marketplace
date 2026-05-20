# Search & Comments API / 搜索与评论接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---
## get_general_search_v2

`GET /api/v1/youtube/web_v2/get_general_search_v2`

<!-- Full path: /api/v1/youtube/web_v2/get_general_search_v2 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string |  | 搜索关键词（首次请求必填）/Search keyword (required for first request) | Python tutorial |
| continuation_token | string |  | 分页token，用于获取下一页/Continuation token for next page |  |
| upload_date | string |  | 上传时间过滤/Upload date filter |  |
| type | string |  | 类型过滤/Type filter |  |
| duration | string |  | '时长过滤/Duration filter: short (<4min), medium (4-20min), long (>20min)' |  |
| features | string |  | >- |  |
| sort_by | string |  | 排序方式/Sort by |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 搜索 YouTube 视频、Shorts、频道、播放列表
 - 返回清洗后的结构化数据（相比 get_general_search 返回原始数据）
 - 支持多种过滤条件和排序方式
 - 支持分页加载更多结果
  ### 参数:
 - keyword: 搜索关键词（首次请求必填）
 - continuation_token: 分页token（获取下一页时传入，从上一次返回结果中获取）
 - upload_date: 上传时间过滤 - last_hour/today/this_week/this_month/this_year
 - type: 结果类型过滤 - video/channel/playlist/movie
 - duration: 视频时长过滤 - short(<4分钟)/medium(4-20分钟)/long(>20分钟)
 - features: 特性过滤（多个用逗号分隔）-
live/4k/hd/subtitles/creative_commons/360/vr180/3d/hdr
 - sort_by: 排序方式 -
relevance(相关性)/upload_date(上传日期)/view_count(播放量)/rating(评分)
  ### 返回数据:
 - videos: 视频列表（标题、时长、播放量、作者、频道ID、缩略图等）
 - shorts: Shorts 短视频列表
 - channels: 频道列表
 - playlists: 播放列表
 - continuation_token: 下一页 token
 - completion_suggestions: 搜索建议词
  ### 使用流程:
 1. 首次搜索传入 keyword（可选过滤参数）
 2. 加载更多时传入上一次返回的 continuation_token

---

See SKILL.md for cross-group orchestration patterns.