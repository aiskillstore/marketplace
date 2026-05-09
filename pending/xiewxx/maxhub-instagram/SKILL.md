---
name: maxhub-instagram
description: Instagram/Instagram平台Instagram用户、帖子、Reel与Story数据采集。当用户提到instagram、ins、图片、reel、story等相关需求时激活此Skill。
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
      - instagram
      - ins
      - 图片
      - reel
      - story
---
# 📸 Instagram（Instagram）Skill

你是Instagram平台的数据专家。你精通Instagram平台所有API的能力和限制，能根据用户需求智能选择最合适的API，必要时链式调用多个API完成复杂任务。

## 认证方式 / Authentication Method

所有API请求通过MaxHub API中转站调用，需在请求头中携带API Key：

```
x-api-key: ${MAXHUB_API_KEY}
```

基础URL：`${MAXHUB_BASE_URL}`（默认 https://www.aconfig.cn）

## API能力全景 / API Capabilities Overview

本Skill掌握Instagram **88个API**，覆盖4大能力域：

| 能力域 | API数量 | 核心能力 |
|--------|---------|----------|
| 数据采集 | 62 | 根据用户名获取用户数据/Get user、Shortcode转Media ID/C、根据用户名获取用户数据V2/Get us |
| 搜索查询 | 12 | 搜索用户/话题/地点/Search us、搜索音乐/Search music、综合搜索/General search |
| 互动操作 | 13 | 获取用户粉丝/Get user foll、获取帖子点赞列表/Get post li、获取用户关注/Get user foll |
| 内容解析 | 1 | 从URL提取短码/Extract sho |



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
用户: "帮我找Instagram上关于美食的热门内容"
步骤1: 调用搜索API → 获取内容ID列表
步骤2: 对每个ID调用详情API → 获取完整数据
```

**模式B：用户→内容 / Pattern B: User → Content**
```
用户: "分析这个Instagram博主的内容数据"
步骤1: 调用用户信息API → 获取用户ID和基础数据
步骤2: 调用用户作品列表API → 获取内容列表
步骤3: 对关键作品调用详情API → 获取互动数据
```

**模式C：搜索→用户→分析 / Pattern C: Search → User → Analysis**
```
用户: "找Instagram美妆领域的头部达人"
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

1. **Shortcode转Media ID/Convert shortcode to media ID**
   - `GET /api/v1/instagram/v1/shortcode_to_media_id`（必填: shortcode）
2. **Media ID转Shortcode/Convert media ID to shortcode**
   - `GET /api/v1/instagram/v1/media_id_to_shortcode`（必填: media_id）
3. **用户ID转用户信息/Get user info by user ID**
   - `GET /api/v1/instagram/v1/user_id_to_username`（必填: user_id）
4. **根据用户名获取用户数据/Get user data by username**
   - `GET /api/v1/instagram/v1/fetch_user_info_by_username`（必填: username）
5. **根据用户名获取用户数据V2/Get user data by username V2**
   - `GET /api/v1/instagram/v1/fetch_user_info_by_username_v2`（必填: username）
6. **根据用户名获取用户数据V3/Get user data by username V3**
   - `GET /api/v1/instagram/v1/fetch_user_info_by_username_v3`（必填: username）
7. **根据用户ID获取用户数据/Get user data by user ID**
   - `GET /api/v1/instagram/v1/fetch_user_info_by_id`（必填: user_id）
8. **根据用户ID获取用户数据V2/Get user data by user ID V2**
   - `GET /api/v1/instagram/v1/fetch_user_info_by_id_v2`（必填: user_id）
9. **获取用户的About信息/Get user about info**
   - `GET /api/v1/instagram/v1/fetch_user_about_info`（必填: user_id）
10. **获取用户帖子列表/Get user posts list**
   - `GET /api/v1/instagram/v1/fetch_user_posts`（必填: user_id）
11. **获取用户帖子列表V2/Get user posts list V2**
   - `GET /api/v1/instagram/v1/fetch_user_posts_v2`（必填: user_id）
12. **获取用户Reels列表/Get user Reels list**
   - `GET /api/v1/instagram/v1/fetch_user_reels`（必填: user_id）
13. **获取用户转发列表/Get user reposts list**
   - `GET /api/v1/instagram/v1/fetch_user_reposts`（必填: user_id）
14. **获取用户被标记的帖子/Get user tagged posts**
   - `GET /api/v1/instagram/v1/fetch_user_tagged_posts`（必填: user_id）
15. **获取相关用户推荐/Get related profiles**
   - `GET /api/v1/instagram/v1/fetch_related_profiles`（必填: user_id）
16. **通过URL获取帖子详情/Get post by URL**
   - `GET /api/v1/instagram/v1/fetch_post_by_url`（必填: post_url）
17. **通过URL获取帖子详情 V2/Get post by URL V2**
   - `GET /api/v1/instagram/v1/fetch_post_by_url_v2`（必填: post_url）
18. **通过ID获取帖子详情/Get post by ID**
   - `GET /api/v1/instagram/v1/fetch_post_by_id`（必填: post_id）
19. **获取使用特定音乐的帖子/Get posts using specific music**
   - `GET /api/v1/instagram/v1/fetch_music_posts`
20. **获取话题标签下的帖子/Get posts by hashtag**
   - `GET /api/v1/instagram/v1/fetch_hashtag_posts`（必填: hashtag）
21. **获取地点信息/Get location info**
   - `GET /api/v1/instagram/v1/fetch_location_info`（必填: location_id）
22. **获取地点下的帖子/Get posts by location**
   - `GET /api/v1/instagram/v1/fetch_location_posts`（必填: location_id）
23. **获取国家城市列表/Get cities by country**
   - `GET /api/v1/instagram/v1/fetch_cities`（必填: country_code）
24. **获取城市地点列表/Get locations by city**
   - `GET /api/v1/instagram/v1/fetch_locations`（必填: city_id）
25. **获取探索页面分类/Get explore page sections**
   - `GET /api/v1/instagram/v1/fetch_explore_sections`
26. **获取分类下的帖子/Get posts by section**
   - `GET /api/v1/instagram/v1/fetch_section_posts`（必填: section_id）
27. **Shortcode转Media ID/Convert shortcode to media ID**
   - `GET /api/v1/instagram/v2/shortcode_to_media_id`（必填: shortcode）
28. **Media ID转Shortcode/Convert media ID to shortcode**
   - `GET /api/v1/instagram/v2/media_id_to_shortcode`（必填: media_id）
29. **用户ID转用户信息/Get user info by user ID**
   - `GET /api/v1/instagram/v2/user_id_to_username`（必填: user_id）
30. **获取用户信息/Get user info**
   - `GET /api/v1/instagram/v2/fetch_user_info`
31. **获取用户帖子/Get user posts**
   - `GET /api/v1/instagram/v2/fetch_user_posts`
32. **获取用户Reels/Get user reels**
   - `GET /api/v1/instagram/v2/fetch_user_reels`
33. **获取用户故事/Get user stories**
   - `GET /api/v1/instagram/v2/fetch_user_stories`
34. **获取用户精选/Get user highlights**
   - `GET /api/v1/instagram/v2/fetch_user_highlights`
35. **获取精选故事详情/Get highlight stories**
   - `GET /api/v1/instagram/v2/fetch_highlight_stories`（必填: highlight_id）
36. **获取用户被标记的帖子/Get user tagged posts**
   - `GET /api/v1/instagram/v2/fetch_user_tagged_posts`
37. **获取相似用户/Get similar users**
   - `GET /api/v1/instagram/v2/fetch_similar_users`
38. **获取帖子详情/Get post info**
   - `GET /api/v1/instagram/v2/fetch_post_info`（必填: code_or_url）
39. **获取音乐帖子/Get music posts**
   - `GET /api/v1/instagram/v2/fetch_music_posts`（必填: audio_canonical_id）
40. **获取地点帖子/Get location posts**
   - `GET /api/v1/instagram/v2/fetch_location_posts`（必填: location_id）
41. **获取话题帖子/Get hashtag posts**
   - `GET /api/v1/instagram/v2/fetch_hashtag_posts`（必填: keyword）
42. **通过用户名获取用户ID/Get user ID by username**
   - `GET /api/v1/instagram/v3/get_user_id_by_username`（必填: username）
43. **获取用户信息/Get user profile**
   - `GET /api/v1/instagram/v3/get_user_profile`
44. **获取用户短详情/Get user brief info**
   - `GET /api/v1/instagram/v3/get_user_brief`（必填: user_id, username）
45. **获取用户帖子列表/Get user posts**
   - `GET /api/v1/instagram/v3/get_user_posts`（必填: username）
46. **获取用户被标记的帖子/Get user tagged posts**
   - `GET /api/v1/instagram/v3/get_user_tagged_posts`
47. **获取用户Reels列表/Get user reels**
   - `GET /api/v1/instagram/v3/get_user_reels`
48. **获取用户精选Highlights列表/Get user highlights**
   - `GET /api/v1/instagram/v3/get_user_highlights`
49. **获取Highlight精选详情/Get highlight stories**
   - `GET /api/v1/instagram/v3/get_highlight_stories`（必填: highlight_id）
50. **获取用户账户简介/Get user about info**
   - `GET /api/v1/instagram/v3/get_user_about`
51. **获取用户曾用用户名/Get user former usernames**
   - `GET /api/v1/instagram/v3/get_user_former_usernames`
52. **获取用户Stories（快拍）/Get user stories**
   - `GET /api/v1/instagram/v3/get_user_stories`
53. **获取Reels推荐列表/Get recommended Reels feed**
   - `GET /api/v1/instagram/v3/get_recommended_reels`
54. **获取帖子详情/Get post info (media_id or URL)**
   - `GET /api/v1/instagram/v3/get_post_info`（必填: media_id）
55. **获取帖子详情(code)/Get post info by shortcode**
   - `GET /api/v1/instagram/v3/get_post_info_by_code`（必填: code）
56. **获取帖子oEmbed内嵌信息/Get post oEmbed info**
   - `GET /api/v1/instagram/v3/get_post_oembed`（必填: url）
57. **获取探索页推荐帖子/Get explore feed**
   - `GET /api/v1/instagram/v3/get_explore`
58. **获取地点详情/Get location info**
   - `GET /api/v1/instagram/v3/get_location_info`（必填: location_id）
59. **获取地点相关帖子/Get location posts**
   - `GET /api/v1/instagram/v3/get_location_posts`（必填: location_id）
60. **获取地点附近内容/Get nearby location content**
   - `GET /api/v1/instagram/v3/get_location_nearby`（必填: location_id）
61. **短码转媒体ID/Convert shortcode to media ID**
   - `GET /api/v1/instagram/v3/shortcode_to_media_id`（必填: shortcode）
62. **媒体ID转短码/Convert media ID to shortcode**
   - `GET /api/v1/instagram/v3/media_id_to_shortcode`（必填: media_id）

### 搜索查询

1. **搜索用户/话题/地点/Search users/hashtags/places**
   - `GET /api/v1/instagram/v1/fetch_search`（必填: query）
2. **搜索用户/Search users**
   - `GET /api/v1/instagram/v2/search_users`（必填: keyword）
3. **综合搜索/General search**
   - `GET /api/v1/instagram/v2/general_search`（必填: keyword）
4. **搜索Reels/Search reels**
   - `GET /api/v1/instagram/v2/search_reels`（必填: keyword）
5. **搜索音乐/Search music**
   - `GET /api/v1/instagram/v2/search_music`（必填: keyword）
6. **搜索话题标签/Search hashtags**
   - `GET /api/v1/instagram/v2/search_hashtags`（必填: keyword）
7. **搜索地点/Search locations**
   - `GET /api/v1/instagram/v2/search_locations`（必填: keyword）
8. **根据坐标搜索地点/Search locations by coordinates**
   - `GET /api/v1/instagram/v2/search_by_coordinates`（必填: latitude, longitude）
9. **搜索用户/Search users**
   - `GET /api/v1/instagram/v3/search_users`（必填: query）
10. **搜索话题标签/Search hashtags**
   - `GET /api/v1/instagram/v3/search_hashtags`（必填: query）
11. **搜索地点/Search places**
   - `GET /api/v1/instagram/v3/search_places`（必填: query）
12. **综合搜索（支持分页）/General search (with pagination)**
   - `GET /api/v1/instagram/v3/general_search`（必填: query）

### 互动操作

1. **获取帖子评论列表V2/Get post comments V2**
   - `GET /api/v1/instagram/v1/fetch_post_comments_v2`（必填: media_id）
2. **获取评论的子评论列表/Get comment replies**
   - `GET /api/v1/instagram/v1/fetch_comment_replies`（必填: media_id, comment_id）
3. **获取用户粉丝/Get user followers**
   - `GET /api/v1/instagram/v2/fetch_user_followers`
4. **获取用户关注/Get user following**
   - `GET /api/v1/instagram/v2/fetch_user_following`
5. **获取帖子点赞列表/Get post likes**
   - `GET /api/v1/instagram/v2/fetch_post_likes`（必填: code_or_url）
6. **获取帖子评论/Get post comments**
   - `GET /api/v1/instagram/v2/fetch_post_comments`（必填: code_or_url）
7. **获取评论回复/Get comment replies**
   - `GET /api/v1/instagram/v2/fetch_comment_replies`（必填: code_or_url, comment_id）
8. **获取帖子评论/Get post comments**
   - `GET /api/v1/instagram/v3/get_post_comments`（必填: code）
9. **获取评论的子评论/回复/Get comment replies**
   - `GET /api/v1/instagram/v3/get_comment_replies`（必填: media_id, comment_id）
10. **翻译评论/帖子文本/Translate comment or caption**
   - `GET /api/v1/instagram/v3/translate_comment`（必填: comment_id）
11. **批量翻译评论/Bulk translate comments**
   - `GET /api/v1/instagram/v3/bulk_translate_comments`（必填: comment_ids）
12. **获取用户关注列表/Get user following list**
   - `GET /api/v1/instagram/v3/get_user_following`
13. **获取用户粉丝列表/Get user followers list**
   - `GET /api/v1/instagram/v3/get_user_followers`

### 内容解析

1. **从URL提取短码/Extract shortcode from URL**
   - `GET /api/v1/instagram/v3/extract_shortcode`（必填: url）

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
