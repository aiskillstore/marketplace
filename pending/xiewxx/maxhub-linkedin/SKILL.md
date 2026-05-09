---
name: maxhub-linkedin
description: LinkedIn/LinkedIn平台LinkedIn职场数据、公司信息与职位搜索。当用户提到linkedin、职场、公司、职位、人脉等相关需求时激活此Skill。
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
      - linkedin
      - 职场
      - 公司
      - 职位
      - 人脉
---
# 💼 LinkedIn（LinkedIn）Skill

你是LinkedIn平台的数据专家。你精通LinkedIn平台所有API的能力和限制，能根据用户需求智能选择最合适的API，必要时链式调用多个API完成复杂任务。

## 认证方式 / Authentication Method

所有API请求通过MaxHub API中转站调用，需在请求头中携带API Key：

```
x-api-key: ${MAXHUB_API_KEY}
```

基础URL：`${MAXHUB_BASE_URL}`（默认 https://www.aconfig.cn）

## API能力全景 / API Capabilities Overview

本Skill掌握LinkedIn **68个API**，覆盖3大能力域：

| 能力域 | API数量 | 核心能力 |
|--------|---------|----------|
| 数据采集 | 56 | 获取用户推荐信/Get user rec、获取用户帖子/Get user post、获取用户视频/Get user vide |
| 互动操作 | 8 | 获取用户评论（在他人帖子下的评论）/Ge、获取用户粉丝/连接数/Get follo、获取用户粉丝和连接数/Get user  |
| 搜索查询 | 4 | 搜索职位/Search jobs、搜索用户/Search users、搜索用户/Search people |



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
用户: "帮我找LinkedIn上关于美食的热门内容"
步骤1: 调用搜索API → 获取内容ID列表
步骤2: 对每个ID调用详情API → 获取完整数据
```

**模式B：用户→内容 / Pattern B: User → Content**
```
用户: "分析这个LinkedIn博主的内容数据"
步骤1: 调用用户信息API → 获取用户ID和基础数据
步骤2: 调用用户作品列表API → 获取内容列表
步骤3: 对关键作品调用详情API → 获取互动数据
```

**模式C：搜索→用户→分析 / Pattern C: Search → User → Analysis**
```
用户: "找LinkedIn美妆领域的头部达人"
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

1. **获取用户资料/Get user profile**
   - `GET /api/v1/linkedin/web/get_user_profile`（必填: username）
2. **获取用户帖子/Get user posts**
   - `GET /api/v1/linkedin/web/get_user_posts`（必填: urn）
3. **获取用户联系信息/Get user contact information**
   - `GET /api/v1/linkedin/web/get_user_contact`（必填: username）
4. **获取用户推荐信/Get user recommendations**
   - `GET /api/v1/linkedin/web/get_user_recommendations`（必填: urn）
5. **获取用户视频/Get user videos**
   - `GET /api/v1/linkedin/web/get_user_videos`（必填: urn）
6. **获取用户图片/Get user images**
   - `GET /api/v1/linkedin/web/get_user_images`（必填: urn）
7. **获取公司资料/Get company profile**
   - `GET /api/v1/linkedin/web/get_company_profile`
8. **获取公司员工/Get company people**
   - `GET /api/v1/linkedin/web/get_company_people`（必填: company_id）
9. **获取公司帖子/Get company posts**
   - `GET /api/v1/linkedin/web/get_company_posts`（必填: company_id）
10. **获取公司职位/Get company jobs**
   - `GET /api/v1/linkedin/web/get_company_jobs`（必填: company_id）
11. **获取公司职位数量/Get company job count**
   - `GET /api/v1/linkedin/web/get_company_job_count`（必填: company_id）
12. **获取用户简介/Get user about**
   - `GET /api/v1/linkedin/web/get_user_about`（必填: urn）
13. **获取用户工作经历/Get user experience**
   - `GET /api/v1/linkedin/web/get_user_experience`（必填: urn）
14. **获取用户技能/Get user skills**
   - `GET /api/v1/linkedin/web/get_user_skills`（必填: urn）
15. **获取用户教育背景/Get user educations**
   - `GET /api/v1/linkedin/web/get_user_educations`（必填: urn）
16. **获取用户出版物/Get user publications**
   - `GET /api/v1/linkedin/web/get_user_publications`（必填: urn）
17. **获取用户认证/Get user certifications**
   - `GET /api/v1/linkedin/web/get_user_certifications`（必填: urn）
18. **获取用户荣誉奖项/Get user honors**
   - `GET /api/v1/linkedin/web/get_user_honors`（必填: urn）
19. **获取用户感兴趣的群组/Get user interests groups**
   - `GET /api/v1/linkedin/web/get_user_interests_groups`（必填: urn）
20. **获取用户感兴趣的公司/Get user interests companies**
   - `GET /api/v1/linkedin/web/get_user_interests_companies`（必填: urn）
21. **获取职位详情/Get job detail**
   - `GET /api/v1/linkedin/web/get_job_detail`（必填: job_id）
22. **获取用户主页基础信息（可选附带子节）/Get user profile (optional sub-sections)**
   - `GET /api/v1/linkedin/web_v2/get_user_profile`（必填: username）
23. **获取用户帖子（动态标签）/Get user posts**
   - `GET /api/v1/linkedin/web_v2/get_user_posts`（必填: username）
24. **获取用户公开联系信息/Get contact info**
   - `GET /api/v1/linkedin/web_v2/get_user_contact_info`（必填: username）
25. **获取用户推荐信/Get recommendations**
   - `GET /api/v1/linkedin/web_v2/get_user_recommendations`（必填: username）
26. **获取用户视频帖子/Get user videos**
   - `GET /api/v1/linkedin/web_v2/get_user_videos`（必填: username）
27. **获取用户图片帖子/Get user images**
   - `GET /api/v1/linkedin/web_v2/get_user_images`（必填: username）
28. **获取用户简介摘要/Get user bio**
   - `GET /api/v1/linkedin/web_v2/get_user_bio`（必填: username）
29. **获取用户主页全部卡片原始结构/Get full profile cards**
   - `GET /api/v1/linkedin/web_v2/get_user_profile_cards`（必填: username）
30. **获取用户工作经历/Get experiences**
   - `GET /api/v1/linkedin/web_v2/get_user_experiences`（必填: username）
31. **获取用户技能/Get skills**
   - `GET /api/v1/linkedin/web_v2/get_user_skills`（必填: username）
32. **获取用户教育背景/Get educations**
   - `GET /api/v1/linkedin/web_v2/get_user_educations`（必填: username）
33. **获取用户出版物/Get publications**
   - `GET /api/v1/linkedin/web_v2/get_user_publications`（必填: username）
34. **获取用户认证/Get certifications**
   - `GET /api/v1/linkedin/web_v2/get_user_certifications`（必填: username）
35. **获取用户荣誉奖项/Get honors**
   - `GET /api/v1/linkedin/web_v2/get_user_honors`（必填: username）
36. **获取用户主页顶部卡片/Get profile top card**
   - `GET /api/v1/linkedin/web_v2/get_user_top_card`（必填: username）
37. **获取用户主页顶部卡片补充信息/Get top card supplementary**
   - `GET /api/v1/linkedin/web_v2/get_user_top_card_supplementary`（必填: username）
38. **获取用户近期动态聚合/Get recent activity summary**
   - `GET /api/v1/linkedin/web_v2/get_user_recent_activity`（必填: username）
39. **发现："基于公司 X"的相关推荐/Discovery relevant to company**
   - `GET /api/v1/linkedin/web_v2/get_discovery_relevant_to_company`（必填: universal_name）
40. **发现："基于用户 X"的相关推荐/Discovery relevant to user**
   - `GET /api/v1/linkedin/web_v2/get_discovery_relevant_to_user`（必填: username）
41. **获取公司主页资料/Get company profile**
   - `GET /api/v1/linkedin/web_v2/get_company_profile`（必填: universal_name）
42. **获取公司员工列表/Get employees**
   - `GET /api/v1/linkedin/web_v2/get_company_employees`（必填: universal_name）
43. **获取公司主页帖子流/Get company posts**
   - `GET /api/v1/linkedin/web_v2/get_company_posts`（必填: universal_name）
44. **获取公司在招职位列表/Get company jobs**
   - `GET /api/v1/linkedin/web_v2/get_company_jobs`（必填: universal_name）
45. **获取公司在招职位总数/Get job count**
   - `GET /api/v1/linkedin/web_v2/get_company_job_count`（必填: universal_name）
46. **获取相似公司（People also viewed）/Get similar companies**
   - `GET /api/v1/linkedin/web_v2/get_company_similar_companies`（必填: universal_name）
47. **获取公司竞争对手/Get competitors**
   - `GET /api/v1/linkedin/web_v2/get_company_competitors`（必填: universal_name）
48. **获取上市公司股价/Get stock quote**
   - `GET /api/v1/linkedin/web_v2/get_company_stock_quote`（必填: universal_name）
49. **获取公司主页 CTA 按钮配置/Get CTA buttons**
   - `GET /api/v1/linkedin/web_v2/get_company_call_to_actions`（必填: universal_name）
50. **获取公司员工数量范围（各 segment）/Get employee count by segment**
   - `GET /api/v1/linkedin/web_v2/get_company_employee_count_ranges`（必填: universal_name）
51. **获取公司全部办公地点（按地理分组）/Get grouped locations**
   - `GET /api/v1/linkedin/web_v2/get_company_grouped_locations`（必填: universal_name）
52. **获取单条帖子详情（按 post URN）/Get post detail by URN**
   - `GET /api/v1/linkedin/web_v2/get_post_detail`（必填: post_urn）
53. **按 URL slug 获取帖子/Get post by URL slug**
   - `GET /api/v1/linkedin/web_v2/get_post_detail_by_slug`（必填: slug）
54. **获取帖子点赞/反应人列表/Get post reactions**
   - `GET /api/v1/linkedin/web_v2/get_post_reactions`（必填: post_urn）
55. **按 hashtag 获取话题动态流/Get hashtag feed**
   - `GET /api/v1/linkedin/web_v2/get_hashtag_feed`（必填: hashtag）
56. **获取职位详情/Get job detail**
   - `GET /api/v1/linkedin/web_v2/get_job_detail`（必填: job_id）

### 互动操作

1. **获取用户评论/Get user comments**
   - `GET /api/v1/linkedin/web/get_user_comments`（必填: urn）
2. **获取用户粉丝和连接数/Get user follower and connection**
   - `GET /api/v1/linkedin/web/get_user_follower_and_connection`（必填: username）
3. **获取用户评论（在他人帖子下的评论）/Get user comments**
   - `GET /api/v1/linkedin/web_v2/get_user_comments`（必填: username）
4. **获取用户粉丝/连接数/Get follower & connection count**
   - `GET /api/v1/linkedin/web_v2/get_user_follower_and_connection_count`（必填: username）
5. **获取用户关注的群组/Get followed groups**
   - `GET /api/v1/linkedin/web_v2/get_user_interested_groups`（必填: username）
6. **获取用户关注的公司/Get followed companies**
   - `GET /api/v1/linkedin/web_v2/get_user_interested_companies`（必填: username）
7. **获取帖子顶层评论/Get post top-level comments**
   - `GET /api/v1/linkedin/web_v2/get_post_comments`（必填: post_urn）
8. **获取评论的回复/Get comment replies**
   - `GET /api/v1/linkedin/web_v2/get_comment_replies`（必填: comment_urn）

### 搜索查询

1. **搜索职位/Search jobs**
   - `GET /api/v1/linkedin/web/search_jobs`（必填: keyword）
2. **搜索用户/Search people**
   - `GET /api/v1/linkedin/web/search_people`
3. **搜索用户/Search users**
   - `GET /api/v1/linkedin/web_v2/search_users`（必填: keywords）
4. **搜索职位/Search jobs**
   - `GET /api/v1/linkedin/web_v2/search_jobs`（必填: keywords）

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
