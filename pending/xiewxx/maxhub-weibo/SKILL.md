---
name: maxhub-weibo
description: 微博/Weibo平台微博热搜、话题、用户与博文数据采集。当用户提到微博、weibo、热搜、超话、话题等相关需求时激活此Skill。
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
      - weibo
      - 微博
      - 热搜
      - 超话
---
# 📢 微博（Weibo）Skill

你是微博平台的数据专家。你精通微博平台所有API的能力和限制，能根据用户需求智能选择最合适的API，必要时链式调用多个API完成复杂任务。

## 认证方式 / Authentication Method

所有API请求通过MaxHub API中转站调用，需在请求头中携带API Key：

```
x-api-key: ${MAXHUB_API_KEY}
```

基础URL：`${MAXHUB_BASE_URL}`（默认 `https://www.aconfig.cn`）

## API能力全景 / API Capabilities Overview

本Skill掌握微博 **64个API**，覆盖4大能力域：

| 能力域 | API数量 | 核心能力 |
|--------|---------|----------|
| 数据采集 | 31 | 获取用户微博列表/Get user po、根据频道名称获取热门内容/Get cha、获取微博详情/Get post deta |
| 数据分析 | 5 | 获取微博生活榜单/Get Weibo l、获取微博文娱榜单/Get Weibo e、获取微博热门榜单时间轴/Get hot  |
| 互动操作 | 8 | 检查微博是否允许带图评论/Check i、获取评论子评论/Get comment 、获取微博子评论/Get Weibo su |
| 搜索查询 | 20 | 搜索微博/Search Weibo、获取搜索页热搜词/Get search 、获取热搜榜/Get hot search |



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
用户: "帮我找微博上关于美食的热门内容"
步骤1: 调用搜索API → 获取内容ID列表
步骤2: 对每个ID调用详情API → 获取完整数据
```

**模式B：用户→内容 / Pattern B: User → Content**
```
用户: "分析这个微博博主的内容数据"
步骤1: 调用用户信息API → 获取用户ID和基础数据
步骤2: 调用用户作品列表API → 获取内容列表
步骤3: 对关键作品调用详情API → 获取互动数据
```

**模式C：搜索→用户→分析 / Pattern C: Search → User → Analysis**
```
用户: "找微博美妆领域的头部达人"
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

1. **获取频道配置列表/Get channel config list**
   - `GET /api/v1/weibo/web/fetch_config_list`
2. **根据频道名称获取热门内容/Get channel feed by name**
   - `GET /api/v1/weibo/web/fetch_channel_feed`
3. **获取用户信息/Get user information**
   - `GET /api/v1/weibo/web/fetch_user_info`（必填: uid）
4. **获取用户微博列表/Get user posts**
   - `GET /api/v1/weibo/web/fetch_user_posts`（必填: uid）
5. **获取微博详情/Get post detail**
   - `GET /api/v1/weibo/web/fetch_post_detail`（必填: post_id）
6. **获取单个作品数据/Get single post data**
   - `GET /api/v1/weibo/web_v2/fetch_post_detail`（必填: id）
7. **获取用户信息/Get user information**
   - `GET /api/v1/weibo/web_v2/fetch_user_info`
8. **获取用户基本信息/Get user basic information**
   - `GET /api/v1/weibo/web_v2/fetch_user_basic_info`（必填: uid）
9. **获取微博用户文章数据/Get Weibo user posts**
   - `GET /api/v1/weibo/web_v2/fetch_user_posts`（必填: uid）
10. **获取微博用户原创微博数据/Get Weibo user original posts**
   - `GET /api/v1/weibo/web_v2/fetch_user_original_posts`（必填: uid）
11. **获取用户微博视频收藏夹列表/Get user video collection list**
   - `GET /api/v1/weibo/web_v2/fetch_user_video_collection_list`（必填: uid）
12. **获取用户微博视频收藏夹详情/Get user video collection detail**
   - `GET /api/v1/weibo/web_v2/fetch_user_video_collection_detail`（必填: cid）
13. **获取微博用户全部视频/Get user all videos**
   - `GET /api/v1/weibo/web_v2/fetch_user_video_list`（必填: uid）
14. **获取用户粉丝列表/Get user fans list**
   - `GET /api/v1/weibo/web_v2/fetch_user_fans`（必填: uid）
15. **获取所有分组信息/Get all groups information**
   - `GET /api/v1/weibo/web_v2/fetch_all_groups`
16. **获取微博主页推荐时间轴/Get user recommend timeline**
   - `GET /api/v1/weibo/web_v2/fetch_user_recommend_timeline`
17. **地区省市映射/Region City List**
   - `GET /api/v1/weibo/web_v2/fetch_city_list`
18. **获取用户信息/Get user information**
   - `GET /api/v1/weibo/app/fetch_user_info`（必填: uid）
19. **获取用户详细信息/Get user detail information**
   - `GET /api/v1/weibo/app/fetch_user_info_detail`（必填: uid）
20. **获取用户发布的微博/Get user timeline**
   - `GET /api/v1/weibo/app/fetch_user_timeline`（必填: uid）
21. **获取用户视频列表/Get user videos**
   - `GET /api/v1/weibo/app/fetch_user_videos`（必填: uid）
22. **获取用户参与的超话列表/Get user super topics**
   - `GET /api/v1/weibo/app/fetch_user_super_topics`（必填: uid）
23. **获取用户相册/Get user album**
   - `GET /api/v1/weibo/app/fetch_user_album`（必填: uid）
24. **获取用户文章列表/Get user articles**
   - `GET /api/v1/weibo/app/fetch_user_articles`（必填: uid）
25. **获取用户音频列表/Get user audios**
   - `GET /api/v1/weibo/app/fetch_user_audios`（必填: uid）
26. **获取用户主页动态/Get user profile feed**
   - `GET /api/v1/weibo/app/fetch_user_profile_feed`（必填: uid）
27. **获取微博详情/Get post detail**
   - `GET /api/v1/weibo/app/fetch_status_detail`（必填: status_id）
28. **获取微博转发列表/Get post reposts**
   - `GET /api/v1/weibo/app/fetch_status_reposts`（必填: status_id）
29. **获取视频详情/Get video detail**
   - `GET /api/v1/weibo/app/fetch_video_detail`（必填: mid）
30. **获取短视频精选Feed流/Get video featured feed**
   - `GET /api/v1/weibo/app/fetch_video_featured_feed`
31. **获取首页推荐Feed流/Get home recommend feed**
   - `GET /api/v1/weibo/app/fetch_home_recommend_feed`

### 数据分析

1. **获取频道热门趋势/Get channel trend top**
   - `GET /api/v1/weibo/web/fetch_trend_top`（必填: containerid）
2. **获取微博热门榜单时间轴/Get hot ranking timeline**
   - `GET /api/v1/weibo/web_v2/fetch_hot_ranking_timeline`（必填: ranking_type）
3. **获取微博文娱榜单/Get Weibo entertainment ranking**
   - `GET /api/v1/weibo/web_v2/fetch_entertainment_ranking`
4. **获取微博生活榜单/Get Weibo life ranking**
   - `GET /api/v1/weibo/web_v2/fetch_life_ranking`
5. **获取微博社会榜单/Get Weibo social ranking**
   - `GET /api/v1/weibo/web_v2/fetch_social_ranking`

### 互动操作

1. **获取微博评论/Get post comments**
   - `GET /api/v1/weibo/web/fetch_post_comments`（必填: post_id, mid）
2. **获取评论子评论/Get comment replies**
   - `GET /api/v1/weibo/web/fetch_comment_replies`（必填: cid）
3. **检查微博是否允许带图评论/Check if Weibo allows image comments**
   - `GET /api/v1/weibo/web_v2/check_allow_comment_with_pic`（必填: id）
4. **获取微博评论/Get Weibo comments**
   - `GET /api/v1/weibo/web_v2/fetch_post_comments`（必填: id）
5. **获取微博子评论/Get Weibo sub-comments**
   - `GET /api/v1/weibo/web_v2/fetch_post_sub_comments`（必填: id）
6. **获取用户关注列表/Get user following list**
   - `GET /api/v1/weibo/web_v2/fetch_user_following`（必填: uid）
7. **获取微博评论/Get post comments**
   - `GET /api/v1/weibo/app/fetch_status_comments`（必填: status_id）
8. **获取微博点赞列表/Get post likes**
   - `GET /api/v1/weibo/app/fetch_status_likes`（必填: status_id）

### 搜索查询

1. **搜索微博/Search Weibo**
   - `GET /api/v1/weibo/web/fetch_search`（必填: keyword）
2. **获取热搜榜/Get hot search ranking**
   - `GET /api/v1/weibo/web/fetch_hot_search`
3. **获取搜索页热搜词/Get search page hot topics**
   - `GET /api/v1/weibo/web/fetch_search_topics`
4. **搜索用户微博/Search user posts**
   - `GET /api/v1/weibo/web_v2/search_user_posts`（必填: uid）
5. **获取微博热搜词条(10条)/Get Weibo hot search index (10 items)**
   - `GET /api/v1/weibo/web_v2/fetch_hot_search_index`
6. **获取微博完整热搜榜单(50条)/Get Weibo complete hot search ranking (50 items)**
   - `GET /api/v1/weibo/web_v2/fetch_hot_search_summary`
7. **获取微博热搜榜单/Get Weibo hot search ranking**
   - `GET /api/v1/weibo/web_v2/fetch_hot_search`
8. **获取微博相似搜索词推荐/Get Weibo similar search recommendations**
   - `GET /api/v1/weibo/web_v2/fetch_similar_search`（必填: keyword）
9. **微博智能搜索/Weibo AI Search**
   - `GET /api/v1/weibo/web_v2/fetch_ai_search`（必填: query）
10. **微博AI搜索内容扩展/Weibo AI Search Content Extension**
   - `GET /api/v1/weibo/web_v2/fetch_ai_related_search`（必填: keyword）
11. **微博高级搜索/Weibo Advanced Search**
   - `GET /api/v1/weibo/web_v2/fetch_advanced_search`（必填: q）
12. **实时搜索/Weibo Realtime Search**
   - `GET /api/v1/weibo/web_v2/fetch_realtime_search`（必填: query）
13. **用户搜索/User search**
   - `GET /api/v1/weibo/web_v2/fetch_user_search`
14. **视频搜索（热门/全部）/Weibo video search (hot/all)**
   - `GET /api/v1/weibo/web_v2/fetch_video_search`（必填: query）
15. **图片搜索/Weibo picture search**
   - `GET /api/v1/weibo/web_v2/fetch_pic_search`（必填: query）
16. **话题搜索/Weibo topic search**
   - `GET /api/v1/weibo/web_v2/fetch_topic_search`（必填: query）
17. **综合搜索/Comprehensive search**
   - `GET /api/v1/weibo/app/fetch_search_all`（必填: query）
18. **AI智搜/AI Smart Search**
   - `GET /api/v1/weibo/app/fetch_ai_smart_search`（必填: query）
19. **获取热搜榜/Get hot search**
   - `GET /api/v1/weibo/app/fetch_hot_search`
20. **获取热搜分类列表/Get hot search categories**
   - `GET /api/v1/weibo/app/fetch_hot_search_categories`

## 调用示例 / API Call Examples

### 基础调用 / Basic Call

```bash
curl -X GET "${MAXHUB_BASE_URL}/api/v1/weibo/web/fetch_config_list" \
  -H "x-api-key: $MAXHUB_API_KEY"
```

### 带参数调用 / Call with Parameters

```bash
curl -X GET "${MAXHUB_BASE_URL}/api/v1/weibo/web/fetch_user_info?uid=123456" \
  -H "x-api-key: $MAXHUB_API_KEY"
```

### POST请求 / POST Request

当前 Skill 文档未列出可确认的 POST 接口，避免提供误导性 curl 示例；如需 POST 调用，请以本 Skill 的 API 列表为准。

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
