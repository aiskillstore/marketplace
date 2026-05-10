---
name: maxhub-xiaohongshu
description: 小红书/Xiaohongshu平台小红书笔记搜索、用户分析与种草数据采集。当用户提到小红书、xiaohongshu、red、种草、笔记等相关需求时激活此Skill。
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
      - xiaohongshu
      - 小红书
      - 种草
      - 笔记
---
# 📕 小红书（Xiaohongshu）Skill

你是小红书平台的数据专家。你精通小红书平台所有API的能力和限制，能根据用户需求智能选择最合适的API，必要时链式调用多个API完成复杂任务。

## 认证方式 / Authentication Method

所有API请求通过MaxHub API中转站调用，需在请求头中携带API Key：

```
x-api-key: ${MAXHUB_API_KEY}
```

基础URL：`${MAXHUB_BASE_URL}`（默认 `https://www.aconfig.cn`）

## API能力全景 / API Capabilities Overview

本Skill掌握小红书 **76个API**，覆盖6大能力域：

| 能力域 | API数量 | 核心能力 |
|--------|---------|----------|
| 数据采集 | 39 | 获取用户笔记列表/Fetch user 、获取首页推荐/Fetch homepag、获取笔记详情/Fetch note de |
| 互动操作 | 17 | 获取笔记二级评论列表/Get note 、获取笔记评论/Fetch note co、获取用户收藏笔记列表/Get user  |
| 搜索查询 | 15 | 搜索笔记/Search notes、获取搜索联想词/Fetch search、搜索用户/Search users |
| 数据分析 | 1 | 获取热搜词/Fetch trending |
| 创作者/达人 | 2 | 获取创作者热点灵感列表/Get crea、获取创作者推荐灵感列表/Get crea |
| 内容解析 | 2 | 从分享链接中提取用户ID和xsec_to、提取分享链接信息/Extract sha |



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
用户: "帮我找小红书上关于美食的热门内容"
步骤1: 调用搜索API → 获取内容ID列表
步骤2: 对每个ID调用详情API → 获取完整数据
```

**模式B：用户→内容 / Pattern B: User → Content**
```
用户: "分析这个小红书博主的内容数据"
步骤1: 调用用户信息API → 获取用户ID和基础数据
步骤2: 调用用户作品列表API → 获取内容列表
步骤3: 对关键作品调用详情API → 获取互动数据
```

**模式C：搜索→用户→分析 / Pattern C: Search → User → Analysis**
```
用户: "找小红书美妆领域的头部达人"
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

1. **获取笔记详情/Fetch note detail**
   - `GET /api/v1/xiaohongshu/web_v3/fetch_note_detail`（必填: note_id, xsec_token）
2. **获取首页推荐/Fetch homepage feed**
   - `GET /api/v1/xiaohongshu/web_v3/fetch_homefeed`
3. **获取首页分类列表/Fetch homepage categories**
   - `GET /api/v1/xiaohongshu/web_v3/fetch_homefeed_categories`
4. **获取用户信息/Fetch user info**
   - `GET /api/v1/xiaohongshu/web_v3/fetch_user_info`（必填: user_id）
5. **获取用户笔记列表/Fetch user notes**
   - `GET /api/v1/xiaohongshu/web_v3/fetch_user_notes`（必填: user_id）
6. **获取图文笔记详情/Get image note detail**
   - `GET /api/v1/xiaohongshu/app_v2/get_image_note_detail`
7. **获取视频笔记详情/Get video note detail**
   - `GET /api/v1/xiaohongshu/app_v2/get_video_note_detail`
8. **获取用户信息/Get user info**
   - `GET /api/v1/xiaohongshu/app_v2/get_user_info`
9. **获取用户笔记列表/Get user posted notes**
   - `GET /api/v1/xiaohongshu/app_v2/get_user_posted_notes`
10. **获取商品详情/Get product detail**
   - `GET /api/v1/xiaohongshu/app_v2/get_product_detail`（必填: sku_id）
11. **获取商品推荐列表/Get product recommendations**
   - `GET /api/v1/xiaohongshu/app_v2/get_product_recommendations`（必填: sku_id）
12. **获取话题详情/Get topic info**
   - `GET /api/v1/xiaohongshu/app_v2/get_topic_info`（必填: page_id）
13. **获取话题笔记列表/Get topic feed**
   - `GET /api/v1/xiaohongshu/app_v2/get_topic_feed`（必填: page_id）
14. **获取笔记信息 V1/Get note info V1**
   - `GET /api/v1/xiaohongshu/app/get_note_info`
15. **获取笔记信息 V2 (蒲公英商家后台)/Get note info V2 (Pugongying Business Backend)**
   - `GET /api/v1/xiaohongshu/app/get_note_info_v2`
16. **[已弃用/Deprecated] 根据话题标签获取作品/Get notes by topic**
   - `GET /api/v1/xiaohongshu/app/get_notes_by_topic`（必填: page_id, first_load_time）
17. **获取用户信息/Get user info**
   - `GET /api/v1/xiaohongshu/app/get_user_info`（必填: user_id）
18. **获取用户作品列表/Get user notes**
   - `GET /api/v1/xiaohongshu/app/get_user_notes`（必填: user_id）
19. **获取商品详情/Get product detail**
   - `GET /api/v1/xiaohongshu/app/get_product_detail`（必填: sku_id）
20. **获取单一笔记和推荐笔记 V1 (已弃用)/Fetch one note and feed notes V1 (deprecated)**
   - `GET /api/v1/xiaohongshu/web_v2/fetch_feed_notes`（必填: note_id）
21. **获取单一笔记和推荐笔记 V2/Fetch one note and feed notes V2(v2稳定, 推荐使用此接口)**
   - `GET /api/v1/xiaohongshu/web_v2/fetch_feed_notes_v2`（必填: note_id）
22. **获取单一笔记和推荐笔记 V3/Fetch one note and feed notes V3(通过短链获取笔记详情)**
   - `GET /api/v1/xiaohongshu/web_v2/fetch_feed_notes_v3`（必填: short_url）
23. **获取小红书笔记图片/Fetch Xiaohongshu note image**
   - `GET /api/v1/xiaohongshu/web_v2/fetch_note_image`（必填: note_id）
24. **获取Web用户主页笔记/Fetch web user profile notes**
   - `GET /api/v1/xiaohongshu/web_v2/fetch_home_notes`（必填: user_id）
25. **获取App用户主页笔记/Fetch App user home notes**
   - `GET /api/v1/xiaohongshu/web_v2/fetch_home_notes_app`（必填: user_id）
26. **获取用户信息/Fetch user info**
   - `GET /api/v1/xiaohongshu/web_v2/fetch_user_info`（必填: user_id）
27. **获取App用户信息/Fetch App user info**
   - `GET /api/v1/xiaohongshu/web_v2/fetch_user_info_app`（必填: user_id）
28. **获取小红书商品列表/Fetch Xiaohongshu product list**
   - `GET /api/v1/xiaohongshu/web_v2/fetch_product_list`（必填: user_id）
29. **获取小红书热榜/Fetch Xiaohongshu hot list**
   - `GET /api/v1/xiaohongshu/web_v2/fetch_hot_list`
30. **获取首页推荐/Get home recommend**
   - `POST /api/v1/xiaohongshu/web/get_home_recommend`
31. **获取笔记信息 V2/Get note info V2**
   - `GET /api/v1/xiaohongshu/web/get_note_info_v2`
32. **获取笔记信息 V4/Get note info V4**
   - `GET /api/v1/xiaohongshu/web/get_note_info_v4`
33. **获取笔记信息 V5 (自带Cookie)/Get note info V5 (Self-provided Cookie)**
   - `POST /api/v1/xiaohongshu/web/get_note_info_v5`
34. **获取笔记信息 V7/Get note info V7**
   - `GET /api/v1/xiaohongshu/web/get_note_info_v7`
35. **获取用户信息 V1/Get user info V1**
   - `GET /api/v1/xiaohongshu/web/get_user_info`（必填: user_id）
36. **获取用户信息 V2/Get user info V2**
   - `GET /api/v1/xiaohongshu/web/get_user_info_v2`
37. **获取用户的笔记 V2/Get user notes V2**
   - `GET /api/v1/xiaohongshu/web/get_user_notes_v2`（必填: user_id）
38. **通过分享链接获取小红书的Note ID 和 xsec_token/Get Xiaohongshu Note ID and xsec_token by share link**
   - `GET /api/v1/xiaohongshu/web/get_note_id_and_xsec_token`（必填: share_text）
39. **获取小红书商品信息/Get Xiaohongshu product info**
   - `GET /api/v1/xiaohongshu/web/get_product_info`

### 互动操作

1. **获取笔记评论/Fetch note comments**
   - `GET /api/v1/xiaohongshu/web_v3/fetch_note_comments`（必填: note_id, xsec_token）
2. **获取子评论/Fetch sub comments**
   - `GET /api/v1/xiaohongshu/web_v3/fetch_sub_comments`（必填: note_id, root_comment_id, xsec_token）
3. **获取笔记评论列表/Get note comments**
   - `GET /api/v1/xiaohongshu/app_v2/get_note_comments`
4. **获取笔记二级评论列表/Get note sub comments**
   - `GET /api/v1/xiaohongshu/app_v2/get_note_sub_comments`（必填: comment_id）
5. **获取用户收藏笔记列表/Get user faved notes**
   - `GET /api/v1/xiaohongshu/app_v2/get_user_faved_notes`
6. **获取商品评论总览/Get product review overview**
   - `GET /api/v1/xiaohongshu/app_v2/get_product_review_overview`（必填: sku_id）
7. **获取商品评论列表/Get product reviews**
   - `GET /api/v1/xiaohongshu/app_v2/get_product_reviews`（必填: sku_id）
8. **获取笔记评论/Get note comments**
   - `GET /api/v1/xiaohongshu/app/get_note_comments`（必填: note_id）
9. **获取子评论/Get sub comments**
   - `GET /api/v1/xiaohongshu/app/get_sub_comments`（必填: note_id, comment_id）
10. **获取单一笔记和推荐笔记 V4 (互动量有延迟)/Fetch one note and feed notes V4 (interaction volume has a delay)**
   - `GET /api/v1/xiaohongshu/web_v2/fetch_feed_notes_v4`（必填: note_id）
11. **获取单一笔记和推荐笔记 V5 (互动量有缺失)/Fetch one note and feed notes V5 (interaction volume has a missing)**
   - `GET /api/v1/xiaohongshu/web_v2/fetch_feed_notes_v5`（必填: note_id）
12. **获取笔记评论/Fetch note comments**
   - `GET /api/v1/xiaohongshu/web_v2/fetch_note_comments`（必填: note_id）
13. **获取子评论/Fetch sub comments**
   - `GET /api/v1/xiaohongshu/web_v2/fetch_sub_comments`（必填: note_id, comment_id）
14. **获取用户粉丝列表/Fetch follower list**
   - `GET /api/v1/xiaohongshu/web_v2/fetch_follower_list`（必填: user_id）
15. **获取用户关注列表/Fetch following list**
   - `GET /api/v1/xiaohongshu/web_v2/fetch_following_list`（必填: user_id）
16. **获取笔记评论 V1/Get note comments V1**
   - `GET /api/v1/xiaohongshu/web/get_note_comments`（必填: note_id）
17. **获取笔记评论回复 V1/Get note comment replies V1**
   - `GET /api/v1/xiaohongshu/web/get_note_comment_replies`（必填: note_id, comment_id）

### 搜索查询

1. **搜索笔记/Search notes**
   - `GET /api/v1/xiaohongshu/web_v3/fetch_search_notes`（必填: keyword）
2. **搜索用户/Search users**
   - `GET /api/v1/xiaohongshu/web_v3/fetch_search_users`（必填: keyword）
3. **获取搜索联想词/Fetch search suggestions**
   - `GET /api/v1/xiaohongshu/web_v3/fetch_search_suggest`
4. **搜索笔记/Search notes**
   - `GET /api/v1/xiaohongshu/app_v2/search_notes`（必填: keyword）
5. **搜索用户/Search users**
   - `GET /api/v1/xiaohongshu/app_v2/search_users`（必填: keyword）
6. **搜索图片/Search images**
   - `GET /api/v1/xiaohongshu/app_v2/search_images`（必填: keyword）
7. **搜索商品/Search products**
   - `GET /api/v1/xiaohongshu/app_v2/search_products`（必填: keyword）
8. **搜索群聊/Search groups**
   - `GET /api/v1/xiaohongshu/app_v2/search_groups`（必填: keyword）
9. **搜索笔记/Search notes**
   - `GET /api/v1/xiaohongshu/app/search_notes`（必填: keyword, page）
10. **搜索商品/Search products**
   - `GET /api/v1/xiaohongshu/app/search_products`（必填: keyword, page）
11. **获取搜索笔记/Fetch search notes**
   - `GET /api/v1/xiaohongshu/web_v2/fetch_search_notes`（必填: keywords）
12. **获取搜索用户/Fetch search users**
   - `GET /api/v1/xiaohongshu/web_v2/fetch_search_users`（必填: keywords）
13. **搜索笔记/Search notes**
   - `GET /api/v1/xiaohongshu/web/search_notes`（必填: keyword）
14. **搜索笔记 V3/Search notes V3**
   - `GET /api/v1/xiaohongshu/web/search_notes_v3`（必填: keyword）
15. **搜索用户/Search users**
   - `GET /api/v1/xiaohongshu/web/search_users`（必填: keyword）

### 数据分析

1. **获取热搜词/Fetch trending keywords**
   - `GET /api/v1/xiaohongshu/web_v3/fetch_trending`

### 创作者/达人

1. **获取创作者推荐灵感列表/Get creator inspiration feed**
   - `GET /api/v1/xiaohongshu/app_v2/get_creator_inspiration_feed`
2. **获取创作者热点灵感列表/Get creator hot inspiration feed**
   - `GET /api/v1/xiaohongshu/app_v2/get_creator_hot_inspiration_feed`

### 内容解析

1. **提取分享链接信息/Extract share link info**
   - `GET /api/v1/xiaohongshu/app/extract_share_info`（必填: share_link）
2. **从分享链接中提取用户ID和xsec_token/Extract user ID and xsec_token from share link**
   - `GET /api/v1/xiaohongshu/app/get_user_id_and_xsec_token`（必填: share_link）

## 调用示例 / API Call Examples

### 基础调用 / Basic Call

```bash
curl -X GET "${MAXHUB_BASE_URL}/api/v1/xiaohongshu/web_v3/fetch_homefeed" \
  -H "x-api-key: $MAXHUB_API_KEY"
```

### 带参数调用 / Call with Parameters

```bash
curl -X GET "${MAXHUB_BASE_URL}/api/v1/xiaohongshu/web_v3/fetch_note_detail?note_id=NOTE_ID&xsec_token=XSEC_TOKEN" \
  -H "x-api-key: $MAXHUB_API_KEY"
```

### POST请求 / POST Request

```bash
curl -X POST "${MAXHUB_BASE_URL}/api/v1/xiaohongshu/web/get_home_recommend" \
  -H "x-api-key: $MAXHUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{}'
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
