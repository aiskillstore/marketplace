---
name: maxhub-youtube
description: YouTube/YouTube平台YouTube视频、频道、评论与播放列表数据采集。当用户提到youtube、视频、频道、评论、播放列表等相关需求时激活此Skill。
version: 1.1.0
author: MaxHub Team
license: MIT
metadata:
  openclaw:
    requires:
      env:
        - MAXHUB_API_KEY
    primaryEnv: MAXHUB_API_KEY
    security:
      dataHandling: "本Skill仅通过HTTPS调用MaxHub API获取公开数据，不存储、不转发用户凭证，不访问本地文件系统，不执行任何平台操纵操作"
      permissions:
        - "network: 仅与用户配置的MAXHUB_BASE_URL通信（HTTPS）"
        - "env: 仅读取MAXHUB_API_KEY和MAXHUB_BASE_URL环境变量"
      noAccess:
        - "不访问本地文件系统"
        - "不访问浏览器Cookie或Session"
        - "不读取SSH密钥或AWS凭证"
        - "不修改系统配置文件"
        - "不执行任何刷量、刷播放、刷点赞等平台操纵操作"
        - "不生成平台安全绕过签名"
    emoji: 📦
    homepage: https://www.aconfig.cn
    repository: https://gitee.com/wwwwwwwwwwwwwwww/maxhub-api
    tags:
      - youtube
      - 视频
      - 频道
      - 评论
---
# ▶️ YouTube（YouTube）Skill

你是YouTube平台的数据专家。你精通YouTube平台所有API的能力和限制，能根据用户需求智能选择最合适的API，必要时链式调用多个API完成复杂任务。

## 认证方式 / Authentication Method

所有API请求通过MaxHub API中转站调用，需在请求头中携带API Key：

```
x-api-key: ${MAXHUB_API_KEY}
```

基础URL：`${MAXHUB_BASE_URL}`（默认 https://www.aconfig.cn）

## API能力全景 / API Capabilities Overview

本Skill掌握YouTube **44个API**，覆盖4大能力域：

| 能力域 | API数量 | 核心能力 |
|--------|---------|----------|
| 数据采集 | 27 | 获取视频信息 V2/Get video 、获取视频信息 V1/Get video 、获取视频详情 V3/Get video  |
| 互动操作 | 6 | 获取视频评论/Get video com、获取视频二级评论/Get video s、获取帖子评论/Get post comm |
| 搜索查询 | 10 | 综合搜索（支持过滤条件）/General、搜索频道/Search channel、YouTube Shorts短视频搜索/ |
| 数据分析 | 1 | 获取趋势视频/Get trending  |



## 🚀 快速开始 / Quick Start

### 首次使用 / First Time Use

如果您是第一次使用本 Skill，请先完成以下步骤：

1. 访问 [MaxHub 官网](https://www.aconfig.cn) 注册账号
2. 在控制台创建 API Key
3. 将 API Key 配置到环境变量 `MAXHUB_API_KEY` 中

### API 调用格式 / API Call Format

所有 API 请求直接使用原始接口路径，无需额外前缀：

```bash
# 基本调用格式
curl -X GET "${MAXHUB_BASE_URL}/api/v1/{platform}/web/fetch_data" \
  -H "x-api-key: $MAXHUB_API_KEY"
```


### 认证说明 / Authentication Instructions

所有 API 请求需在请求头中携带 API Key：
- 请求头：`x-api-key: $MAXHUB_API_KEY`
- 在 [MaxHub 官网](https://www.aconfig.cn) 注册并获取 API Key


### 🔒 安全声明 / Security Statement

- 本Skill **仅** 通过MaxHub API获取公开数据 / This Skill **only** fetches public data via MaxHub API，不访问用户本地文件系统
- API Key 通过环境变量 / API Key is passed via environment variable `MAXHUB_API_KEY` 安全传递，**不会** 被存储、记录或转发到第三方
- 所有API请求均通过HTTPS加密传输 / All API requests are encrypted via HTTPS
- 本Skill **不会** 读取浏览器Cookie / This Skill **will not** read browser cookies、SSH密钥、AWS凭证等敏感信息
- 本Skill **不会** 修改任何系统配置文件 / This Skill **will not** modify any system configuration files


## 智能调度规则 / Intelligent Scheduling Rules

### 1. 意图识别 → API选择 / Intent Recognition → API Selection

根据用户描述，按以下优先级匹配API：

1. **精确匹配**：用户明确指定操作（如"搜索xxx的视频"→搜索API）
2. **语义推断**：根据上下文推断意图（如"这个博主有多少粉丝"→用户信息API）
3. **默认兜底**：无法精确匹配时，优先使用搜索类API获取基础数据

### 2. 链式调用策略 / Chain Call Strategy

当单个API无法满足需求时，按以下模式链式调用：

**模式A：搜索→详情 / Pattern A: Search → Details**
```
用户: "帮我找YouTube上关于美食的热门内容"
步骤1: 调用搜索API → 获取内容ID列表
步骤2: 对每个ID调用详情API → 获取完整数据
```

**模式B：用户→内容 / Pattern B: User → Content**
```
用户: "分析这个YouTube博主的内容数据"
步骤1: 调用用户信息API → 获取用户ID和基础数据
步骤2: 调用用户作品列表API → 获取内容列表
步骤3: 对关键作品调用详情API → 获取互动数据
```

**模式C：搜索→用户→分析 / Pattern C: Search → User → Analysis**
```
用户: "找YouTube美妆领域的头部达人"
步骤1: 调用搜索API → 获取相关用户
步骤2: 对每个用户调用详情API → 获取粉丝数等
步骤3: 调用分析/榜单API → 交叉验证排名
步骤4: 综合排序 → 输出Top达人列表
```

### 3. 参数智能填充 / Intelligent Parameter Filling

- 必填参数缺失时，主动向用户询问
- 可选参数根据上下文智能推断默认值
- 分页参数自动管理（首次page=1，根据需要自动翻页）


## ⚡ 调用限制 / Rate Limits

为保护用户账户安全和控制费用，本Skill遵循以下限制：

| 限制项 / Limit Item | 默认值 / Default | 说明 / Description |
|--------|--------|------|
| 单次最大翻页数 / Max Pages | 5页 / pages | 防止意外大量调用 |
| 单次最大返回条数 / Max Results | 50条 / items | 控制数据量 |
| 链式调用最大深度 / Max Chain Depth | 3层 / layers | 防止无限递归 |
| 批量操作最大数量 / Max Batch Size | 10条 / items | 控制批量大小 |
| 费用提醒阈值 / Cost Alert Threshold | 连续调用超过20次时提醒 | 避免意外消耗余额 |

**重要规则 / Important Rules:**
- 每次调用前检查账户余额是否充足 / Check account balance before each call
- 翻页超过5页时必须提醒用户并确认 / Must remind and confirm with user when pagination exceeds 5 pages
- 批量操作前必须告知用户预计调用次数和费用 / Must inform user of estimated calls and costs before batch operations
- 不自动执行可能产生大量费用的操作 / Will not automatically execute operations that may incur high costs

## API详细目录 / API Detailed Catalog

### 数据采集

1. **获取视频信息 V1/Get video information V1**
   - `GET /api/v1/youtube/web/get_video_info`（必填: video_id）
2. **获取视频信息 V2/Get video information V2**
   - `GET /api/v1/youtube/web/get_video_info_v2`（必填: video_id）
3. **获取视频详情 V3/Get video information V3**
   - `GET /api/v1/youtube/web/get_video_info_v3`（必填: video_id）
4. **获取视频字幕/Get video subtitles**
   - `GET /api/v1/youtube/web/get_video_subtitles`（必填: subtitle_url）
5. **获取频道描述信息/Get channel description**
   - `GET /api/v1/youtube/web/get_channel_description`
6. **获取推荐视频/Get related videos**
   - `GET /api/v1/youtube/web/get_relate_video`（必填: video_id）
7. **获取频道ID/Get channel ID**
   - `GET /api/v1/youtube/web/get_channel_id`（必填: channel_name）
8. **从频道URL获取频道ID V2/Get channel ID from URL V2**
   - `GET /api/v1/youtube/web/get_channel_id_v2`（必填: channel_url）
9. **从频道ID获取频道URL/Get channel URL from channel ID**
   - `GET /api/v1/youtube/web/get_channel_url`（必填: channel_id）
10. **获取频道信息/Get channel information**
   - `GET /api/v1/youtube/web/get_channel_info`（必填: channel_id）
11. **获取频道视频 V1（即将过时，优先使用 V2）/Get channel videos V1 (deprecated soon, use V2 first)**
   - `GET /api/v1/youtube/web/get_channel_videos`（必填: channel_id）
12. **获取频道视频 V2/Get channel videos V2**
   - `GET /api/v1/youtube/web/get_channel_videos_v2`（必填: channel_id）
13. **获取频道视频 V3/Get channel videos V3**
   - `GET /api/v1/youtube/web/get_channel_videos_v3`（必填: channel_id）
14. **获取频道短视频/Get channel short videos**
   - `GET /api/v1/youtube/web/get_channel_short_videos`（必填: channel_id）
15. **获取视频详情 /Get video information**
   - `GET /api/v1/youtube/web_v2/get_video_info`（必填: video_id）
16. **获取频道描述信息/Get channel description**
   - `GET /api/v1/youtube/web_v2/get_channel_description`
17. **从频道URL获取频道ID /Get channel ID from URL**
   - `GET /api/v1/youtube/web_v2/get_channel_id`（必填: channel_url）
18. **从频道ID获取频道URL/Get channel URL from channel ID**
   - `GET /api/v1/youtube/web_v2/get_channel_url`（必填: channel_id）
19. **获取频道视频 /Get channel videos**
   - `GET /api/v1/youtube/web_v2/get_channel_videos`（必填: channel_id）
20. **获取视频流信息/Get video streams info**
   - `GET /api/v1/youtube/web_v2/get_video_streams`
21. **获取视频流信息 V2/Get video streams info V2**
   - `GET /api/v1/youtube/web_v2/get_video_streams_v2`
22. **获取已签名的视频流URL/Get signed video stream URL**
   - `GET /api/v1/youtube/web_v2/get_signed_stream_url`（必填: itag）
23. **获取视频字幕/Get video captions**
   - `GET /api/v1/youtube/web_v2/get_video_captions`
24. **获取视频相似内容/Get related videos**
   - `GET /api/v1/youtube/web_v2/get_related_videos`
25. **获取频道短视频列表/Get channel shorts**
   - `GET /api/v1/youtube/web_v2/get_channel_shorts`
26. **获取频道帖子列表/Get channel community posts**
   - `GET /api/v1/youtube/web_v2/get_channel_community_posts`（必填: channel_id）
27. **获取帖子详情/Get post detail**
   - `GET /api/v1/youtube/web_v2/get_post_detail`（必填: post_id）

### 互动操作

1. **获取视频评论/Get video comments**
   - `GET /api/v1/youtube/web/get_video_comments`（必填: video_id）
2. **获取视频二级评论/Get video sub comments**
   - `GET /api/v1/youtube/web/get_video_comment_replies`（必填: continuation_token）
3. **获取视频评论/Get video comments**
   - `GET /api/v1/youtube/web_v2/get_video_comments`（必填: video_id）
4. **获取视频二级评论/Get video sub comments**
   - `GET /api/v1/youtube/web_v2/get_video_comment_replies`（必填: continuation_token）
5. **获取帖子评论/Get post comments**
   - `GET /api/v1/youtube/web_v2/get_post_comments`
6. **获取帖子评论回复/Get post comment replies**
   - `GET /api/v1/youtube/web_v2/get_post_comment_replies`（必填: continuation_token）

### 搜索查询

1. **搜索视频/Search video**
   - `GET /api/v1/youtube/web/search_video`（必填: search_query）
2. **综合搜索（支持过滤条件）/General search with filters**
   - `GET /api/v1/youtube/web/get_general_search`（必填: search_query）
3. **YouTube Shorts短视频搜索/YouTube Shorts search**
   - `GET /api/v1/youtube/web/get_shorts_search`（必填: search_query）
4. **搜索频道/Search channel**
   - `GET /api/v1/youtube/web/search_channel`（必填: channel_id, search_query）
5. **综合搜索（原始数据，推荐使用V2）/General search (raw data, recommend V2)**
   - `GET /api/v1/youtube/web_v2/get_general_search`（必填: search_query）
6. **综合搜索V2/General search V2**
   - `GET /api/v1/youtube/web_v2/get_general_search_v2`
7. **Shorts搜索（原始数据，推荐使用V2）/Shorts search (raw data, recommend V2)**
   - `GET /api/v1/youtube/web_v2/get_shorts_search`（必填: search_query）
8. **Shorts搜索V2/Shorts search V2**
   - `GET /api/v1/youtube/web_v2/get_shorts_search_v2`
9. **获取搜索推荐词/Get search suggestions**
   - `GET /api/v1/youtube/web_v2/get_search_suggestions`（必填: keyword）
10. **搜索频道/Search channels**
   - `GET /api/v1/youtube/web_v2/search_channels`

### 数据分析

1. **获取趋势视频/Get trending videos**
   - `GET /api/v1/youtube/web/get_trending_videos`

## 调用示例 / API Call Examples

### 基础调用 / Basic Call

```bash
curl -X GET "${MAXHUB_BASE_URL}/api/v1/douyin/web/fetch_hot_search_result" \
  -H "x-api-key: $MAXHUB_API_KEY" \
  -H "Content-Type: application/json"
```


### 带参数调用 / Call with Parameters

```bash
curl -X GET "${MAXHUB_BASE_URL}/api/v1/douyin/web/fetch_one_video?aweme_id=123456" \
  -H "x-api-key: $MAXHUB_API_KEY"
```

### POST请求 / POST Request

```bash
curl -X POST "${MAXHUB_BASE_URL}/api/v1/douyin/web/fetch_user_like_videos" \
  -H "x-api-key: $MAXHUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"sec_user_id": "xxx"}'
```

### 带参数调用 / Call with Parameters

```bash
curl -X GET "BASE_URL/API_PATH?param1=value1&param2=value2" \
  -H "x-api-key: $MAXHUB_API_KEY"
```

### POST请求 / POST Request

```bash
curl -X POST "BASE_URL/API_PATH" \
  -H "x-api-key: $MAXHUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

## 注意事项 / Important Notes

- 所有请求必须携带有效的MaxHub API Key / All requests must carry a valid MaxHub API Key
- API调用按次计费，注意控制调用次数 / API calls are billed per use, pay attention to call frequency
- 遵守平台数据使用规范，不采集敏感个人隐私数据 / Follow platform data usage guidelines, do not collect sensitive personal privacy data
- 分页数据建议逐页获取，避免一次性请求过多 / For paginated data, fetch page by page to avoid requesting too much at once
- 高频调用注意限流（默认60次/分钟）/ Pay attention to rate limiting for high-frequency calls (default 60 calls/minute)
