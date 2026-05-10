---
name: maxhub-bilibili
description: B站/Bilibili平台B站视频数据、UP主分析与弹幕采集。当用户提到b站、bilibili、弹幕、视频、番剧等相关需求时激活此Skill。
version: 1.1.0
author: MaxHub Team
license: MIT
metadata:
  openclaw:
    requires:
      env:
        - MAXHUB_API_KEY
        - MAXHUB_BASE_URL
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
      - bilibili
      - b站
      - 弹幕
      - 视频
      - 番剧
---
# 📺 B站（Bilibili）Skill

你是B站平台的数据专家。你精通B站平台所有API的能力和限制，能根据用户需求智能选择最合适的API，必要时链式调用多个API完成复杂任务。

## 认证方式 / Authentication Method

所有API请求通过MaxHub API中转站调用，需在请求头中携带API Key：

```
x-api-key: ${MAXHUB_API_KEY}
```

基础URL：`${MAXHUB_BASE_URL}`（默认 `https://www.aconfig.cn`）

## API能力全景 / API Capabilities Overview

本Skill掌握B站 **41个API**，覆盖6大能力域：

| 能力域 | API数量 | 核心能力 |
|--------|---------|----------|
| 数据采集 | 29 | 获取单个视频详情信息V2/Get sin、获取单个视频播放信息/Get singl、获取单个视频详情信息/Get singl |
| 搜索查询 | 4 | 获取综合搜索信息/Get general、综合搜索/search all、获取热门搜索信息/Get hot sea |
| 数据分析 | 2 | 获取用户关系状态统计/Get user 、获取UP主状态统计/Get UP sta |
| 互动操作 | 4 | 获取视频评论列表/Get video c、获取二级评论回复/Get reply d、获取视频下指定评论的回复/Get rep |
| 工具服务 | 1 | 通过bv号获得视频aid号/Genera |
| 内容解析 | 1 | 提取用户ID/Extract user  |



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
用户: "帮我找B站上关于美食的热门内容"
步骤1: 调用搜索API → 获取内容ID列表
步骤2: 对每个ID调用详情API → 获取完整数据
```

**模式B：用户→内容 / Pattern B: User → Content**
```
用户: "分析这个B站博主的内容数据"
步骤1: 调用用户信息API → 获取用户ID和基础数据
步骤2: 调用用户作品列表API → 获取内容列表
步骤3: 对关键作品调用详情API → 获取互动数据
```

**模式C：搜索→用户→分析 / Pattern C: Search → User → Analysis**
```
用户: "找B站美妆领域的头部达人"
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

1. **获取单个视频详情信息/Get single video data**
   - `GET /api/v1/bilibili/web/fetch_one_video`（必填: bv_id）
2. **获取单个视频详情信息V2/Get single video data V2**
   - `GET /api/v1/bilibili/web/fetch_one_video_v2`（必填: a_id, c_id）
3. **获取单个视频详情信息V3/Get single video data V3**
   - `GET /api/v1/bilibili/web/fetch_one_video_v3`（必填: url）
4. **获取单个视频详情/Get single video detail**
   - `GET /api/v1/bilibili/web/fetch_video_detail`（必填: aid）
5. **获取单个视频播放信息/Get single video play info**
   - `GET /api/v1/bilibili/web/fetch_video_play_info`（必填: url）
6. **获取视频字幕信息/Get video subtitle info**
   - `GET /api/v1/bilibili/web/fetch_video_subtitle`（必填: a_id, c_id）
7. **获取视频流地址/Get video playurl**
   - `GET /api/v1/bilibili/web/fetch_video_playurl`（必填: bv_id, cid）
8. **获取大会员清晰度视频流地址/Get VIP video playurl**
   - `POST /api/v1/bilibili/web/fetch_vip_video_playurl`
9. **获取用户主页作品数据/Get user homepage video data**
   - `GET /api/v1/bilibili/web/fetch_user_post_videos`（必填: uid）
10. **获取用户所有收藏夹信息/Get user collection folders**
   - `GET /api/v1/bilibili/web/fetch_collect_folders`（必填: uid）
11. **获取指定收藏夹内视频数据/Gets video data from a collection folder**
   - `GET /api/v1/bilibili/web/fetch_user_collection_videos`（必填: folder_id）
12. **获取指定用户的信息/Get information of specified user**
   - `GET /api/v1/bilibili/web/fetch_user_profile`（必填: uid）
13. **获取综合热门视频信息/Get comprehensive popular video information**
   - `GET /api/v1/bilibili/web/fetch_com_popular`
14. **获取指定用户动态/Get dynamic information of specified user**
   - `GET /api/v1/bilibili/web/fetch_user_dynamic`（必填: uid）
15. **获取动态详情/Get dynamic detail**
   - `GET /api/v1/bilibili/web/fetch_dynamic_detail`（必填: dynamic_id）
16. **获取动态详情v2/Get dynamic detail v2**
   - `GET /api/v1/bilibili/web/fetch_dynamic_detail_v2`（必填: dynamic_id）
17. **获取视频实时弹幕/Get Video Danmaku**
   - `GET /api/v1/bilibili/web/fetch_video_danmaku`（必填: cid）
18. **获取指定直播间信息/Get information of specified live room**
   - `GET /api/v1/bilibili/web/fetch_live_room_detail`（必填: room_id）
19. **获取直播间视频流/Get live video data of specified room**
   - `GET /api/v1/bilibili/web/fetch_live_videos`（必填: room_id）
20. **获取指定分区正在直播的主播/Get live streamers of specified live area**
   - `GET /api/v1/bilibili/web/fetch_live_streamers`（必填: area_id）
21. **获取所有直播分区列表/Get a list of all live areas**
   - `GET /api/v1/bilibili/web/fetch_all_live_areas`
22. **通过bv号获得视频分p信息/Get Video Parts By bvid**
   - `GET /api/v1/bilibili/web/fetch_video_parts`（必填: bv_id）
23. **获取单个视频详情信息/Get single video data**
   - `GET /api/v1/bilibili/app/fetch_one_video`
24. **获取用户投稿视频/Get user videos**
   - `GET /api/v1/bilibili/app/fetch_user_videos`（必填: user_id）
25. **获取用户信息/Get user info**
   - `GET /api/v1/bilibili/app/fetch_user_info`（必填: user_id）
26. **获取主页推荐视频流/Get home feed**
   - `GET /api/v1/bilibili/app/fetch_home_feed`
27. **获取热门推荐/Get popular feed**
   - `GET /api/v1/bilibili/app/fetch_popular_feed`
28. **获取影视推荐/Get cinema tab**
   - `GET /api/v1/bilibili/app/fetch_cinema_tab`
29. **获取番剧推荐/Get bangumi tab**
   - `GET /api/v1/bilibili/app/fetch_bangumi_tab`

### 搜索查询

1. **获取热门搜索信息/Get hot search data**
   - `GET /api/v1/bilibili/web/fetch_hot_search`（必填: limit）
2. **获取综合搜索信息/Get general search data**
   - `GET /api/v1/bilibili/web/fetch_general_search`（必填: keyword, order, page, page_size）
3. **综合搜索/search all**
   - `GET /api/v1/bilibili/app/fetch_search_all`（必填: keyword）
4. **分类搜索/ search by type**
   - `GET /api/v1/bilibili/app/fetch_search_by_type`（必填: keyword）

### 数据分析

1. **获取UP主状态统计/Get UP stat (total likes and views)**
   - `GET /api/v1/bilibili/web/fetch_user_up_stat`（必填: uid）
2. **获取用户关系状态统计/Get user relation stat (following and followers)**
   - `GET /api/v1/bilibili/web/fetch_user_relation_stat`（必填: uid）

### 互动操作

1. **获取指定视频的评论/Get comments on the specified video**
   - `GET /api/v1/bilibili/web/fetch_video_comments`（必填: bv_id）
2. **获取视频下指定评论的回复/Get reply to the specified comment**
   - `GET /api/v1/bilibili/web/fetch_comment_reply`（必填: bv_id, rpid）
3. **获取视频评论列表/Get video comments**
   - `GET /api/v1/bilibili/app/fetch_video_comments`
4. **获取二级评论回复/Get reply detail**
   - `GET /api/v1/bilibili/app/fetch_reply_detail`（必填: root）

### 工具服务

1. **通过bv号获得视频aid号/Generate aid by bvid**
   - `GET /api/v1/bilibili/web/bv_to_aid`（必填: bv_id）

### 内容解析

1. **提取用户ID/Extract user ID**
   - `GET /api/v1/bilibili/web/fetch_get_user_id`（必填: share_link）

## 调用示例 / API Call Examples

### 基础调用 / Basic Call

```bash
curl -X GET "${MAXHUB_BASE_URL}/api/v1/bilibili/web/fetch_hot_search" \
  -H "x-api-key: $MAXHUB_API_KEY" \
  -H "Content-Type: application/json"
```


### 带参数调用 / Call with Parameters

```bash
curl -X GET "${MAXHUB_BASE_URL}/api/v1/bilibili/web/fetch_one_video?bvid=BV1234567890" \
  -H "x-api-key: $MAXHUB_API_KEY"
```

### POST请求 / POST Request

```bash
curl -X POST "${MAXHUB_BASE_URL}/api/v1/bilibili/web/fetch_user_info" \
  -H "x-api-key: $MAXHUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"mid": "12345"}'
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
