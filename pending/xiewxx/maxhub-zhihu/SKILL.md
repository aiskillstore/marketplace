---
name: maxhub-zhihu
description: 知乎/Zhihu平台知乎问答搜索、专栏文章与话题数据采集。当用户提到知乎、zhihu、问答、专栏、话题等相关需求时激活此Skill。
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
      - zhihu
      - 知乎
      - 问答
      - 专栏
---
# 💡 知乎（Zhihu）Skill

你是知乎平台的数据专家。你精通知乎平台所有API的能力和限制，能根据用户需求智能选择最合适的API，必要时链式调用多个API完成复杂任务。

## 认证方式 / Authentication Method

所有API请求通过MaxHub API中转站调用，需在请求头中携带API Key：

```
x-api-key: ${MAXHUB_API_KEY}
```

基础URL：`${MAXHUB_BASE_URL}`（默认 `https://www.aconfig.cn`）

## API能力全景 / API Capabilities Overview

本Skill掌握知乎 **34个API**，覆盖3大能力域：

| 能力域 | API数量 | 核心能力 |
|--------|---------|----------|
| 数据采集 | 11 | 获取知乎首页推荐/Get Zhihu H、获取知乎专栏文章列表/Get Zhihu、获取知乎相似专栏推荐/Get Zhihu |
| 互动操作 | 10 | 获取知乎评论区V5/Get Zhihu 、获取知乎子评论区V5/Get Zhihu、获取知乎用户关注列表/Get Zhihu |
| 搜索查询 | 13 | 获取知乎用户搜索V3/Get Zhihu、获取知乎论文搜索V3/Get Zhihu、获取知乎文章搜索V3/Get Zhihu |



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
用户: "帮我找知乎上关于美食的热门内容"
步骤1: 调用搜索API → 获取内容ID列表
步骤2: 对每个ID调用详情API → 获取完整数据
```

**模式B：用户→内容 / Pattern B: User → Content**
```
用户: "分析这个知乎博主的内容数据"
步骤1: 调用用户信息API → 获取用户ID和基础数据
步骤2: 调用用户作品列表API → 获取内容列表
步骤3: 对关键作品调用详情API → 获取互动数据
```

**模式C：搜索→用户→分析 / Pattern C: Search → User → Analysis**
```
用户: "找知乎美妆领域的头部达人"
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

1. **获取知乎专栏文章列表/Get Zhihu Column Articles**
   - `GET /api/v1/zhihu/web/fetch_column_articles`（必填: column_id）
2. **获取知乎专栏文章详情/Get Zhihu Column Article Detail**
   - `GET /api/v1/zhihu/web/fetch_column_article_detail`（必填: article_id）
3. **获取知乎相似专栏推荐/Get Zhihu Similar Column Recommend**
   - `GET /api/v1/zhihu/web/fetch_column_recommend`（必填: article_id）
4. **获取知乎专栏文章互动关系/Get Zhihu Column Article Relationship**
   - `GET /api/v1/zhihu/web/fetch_column_relationship`（必填: article_id）
5. **获取知乎首页推荐/Get Zhihu Hot Recommend**
   - `GET /api/v1/zhihu/web/fetch_hot_recommend`
6. **获取知乎首页热榜/Get Zhihu Hot List**
   - `GET /api/v1/zhihu/web/fetch_hot_list`
7. **获取知乎首页视频榜/Get Zhihu Video List**
   - `GET /api/v1/zhihu/web/fetch_video_list`
8. **获取知乎用户信息/Get Zhihu User Info**
   - `GET /api/v1/zhihu/web/fetch_user_info`（必填: user_url_token）
9. **获取知乎用户的文章列表/Get Zhihu User Articles**
   - `GET /api/v1/zhihu/web/fetch_user_articles`（必填: user_url_token）
10. **获取知乎用户的被收录文章列表/Get Zhihu User Included Articles**
   - `GET /api/v1/zhihu/web/fetch_user_included_articles`（必填: user_url_token）
11. **获取知乎问题回答列表/Get Zhihu Question Answers**
   - `GET /api/v1/zhihu/web/fetch_question_answers`（必填: question_id）

### 互动操作

1. **获取知乎专栏评论区配置/Get Zhihu Column Comment Config**
   - `GET /api/v1/zhihu/web/fetch_column_comment_config`（必填: article_id）
2. **获取知乎评论区V5/Get Zhihu Comment V5**
   - `GET /api/v1/zhihu/web/fetch_comment_v5`（必填: answer_id）
3. **获取知乎子评论区V5/Get Zhihu Sub Comment V5**
   - `GET /api/v1/zhihu/web/fetch_sub_comment_v5`（必填: comment_id）
4. **获取知乎用户关注列表/Get Zhihu User Following**
   - `GET /api/v1/zhihu/web/fetch_user_followees`（必填: user_url_token）
5. **获取知乎用户粉丝列表/Get Zhihu User Followers**
   - `GET /api/v1/zhihu/web/fetch_user_followers`（必填: user_url_token）
6. **获取知乎用户订阅的专栏/Get Zhihu User Columns**
   - `GET /api/v1/zhihu/web/fetch_user_follow_columns`（必填: user_url_token）
7. **获取知乎用户关注的问题/Get Zhihu User Follow Questions**
   - `GET /api/v1/zhihu/web/fetch_user_follow_questions`（必填: user_url_token）
8. **获取知乎用户关注的收藏/Get Zhihu User Follow Collections**
   - `GET /api/v1/zhihu/web/fetch_user_follow_collections`（必填: user_url_token）
9. **获取知乎用户关注的话题/Get Zhihu User Follow Topics**
   - `GET /api/v1/zhihu/web/fetch_user_follow_topics`（必填: user_url_token）
10. **获取知乎推荐关注列表/Get Zhihu Recommend Followees**
   - `GET /api/v1/zhihu/web/fetch_recommend_followees`

### 搜索查询

1. **获取知乎文章搜索V3/Get Zhihu Article Search V3**
   - `GET /api/v1/zhihu/web/fetch_article_search_v3`（必填: keyword）
2. **获取知乎用户搜索V3/Get Zhihu User Search V3**
   - `GET /api/v1/zhihu/web/fetch_user_search_v3`（必填: keyword）
3. **获取知乎话题搜索V3/Get Zhihu Topic Search V3**
   - `GET /api/v1/zhihu/web/fetch_topic_search_v3`（必填: keyword）
4. **获取知乎论文搜索V3/Get Zhihu Scholar Search V3**
   - `POST /api/v1/zhihu/web/fetch_scholar_search_v3`（必填: keyword）
5. **获取知乎AI搜索/Get Zhihu AI Search**
   - `GET /api/v1/zhihu/web/fetch_ai_search`（必填: message_content）
6. **获取知乎AI搜索结果/Get Zhihu AI Search Result**
   - `GET /api/v1/zhihu/web/fetch_ai_search_result`（必填: message_id）
7. **获取知乎视频搜索V3/Get Zhihu Video Search V3**
   - `GET /api/v1/zhihu/web/fetch_video_search_v3`（必填: keyword）
8. **获取知乎专栏搜索V3/Get Zhihu Column Search V3**
   - `GET /api/v1/zhihu/web/fetch_column_search_v3`（必填: keyword）
9. **获取知乎盐选内容搜索V3/Get Zhihu Salt Search V3**
   - `GET /api/v1/zhihu/web/fetch_salt_search_v3`（必填: keyword）
10. **获取知乎电子书搜索V3/Get Zhihu Ebook Search V3**
   - `GET /api/v1/zhihu/web/fetch_ebook_search_v3`（必填: keyword）
11. **获取知乎搜索预设词/Get Zhihu Preset Search**
   - `GET /api/v1/zhihu/web/fetch_preset_search`
12. **获取知乎搜索发现/Get Zhihu Search Recommend**
   - `GET /api/v1/zhihu/web/fetch_search_recommend`
13. **知乎搜索预测词/Get Zhihu Search Suggest**
   - `GET /api/v1/zhihu/web/fetch_search_suggest`（必填: keyword）

## 调用示例 / API Call Examples

### 基础调用 / Basic Call

```bash
curl -X GET "${MAXHUB_BASE_URL}/api/v1/zhihu/web/fetch_hot_recommend" \
  -H "x-api-key: $MAXHUB_API_KEY"
```

### 带参数调用 / Call with Parameters

```bash
curl -X GET "${MAXHUB_BASE_URL}/api/v1/zhihu/web/fetch_column_articles?column_id=COLUMN_ID" \
  -H "x-api-key: $MAXHUB_API_KEY"
```

### POST请求 / POST Request

```bash
curl -X POST "${MAXHUB_BASE_URL}/api/v1/zhihu/web/fetch_scholar_search_v3" \
  -H "x-api-key: $MAXHUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"keyword": "AI"}'
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
