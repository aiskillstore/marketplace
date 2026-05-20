---
name: maxhub-xiaohongshu
description: "小红书全场景数据查询助手。支持App和Web多版本API，覆盖笔记详情、用户数据、搜索、商品、评论、话题等全功能。"
license: MIT-0
metadata:
  author: maxhub
  version: "3.2.0"
  openclaw:
    emoji: "📕"
    primaryEnv: MAXHUB_API_KEY
    requires:
      env:
        - MAXHUB_API_KEY
      bins:
        - curl
    env:
      - name: MAXHUB_API_KEY
        description: "API key for MaxHub data APIs. Get one at https://www.aconfig.cn"
        required: true
        sensitive: true
    network:
      - https://www.aconfig.cn
  hermes:
    tags: ["小红书", "xiaohongshu", "种草", "笔记", "用户分析", "关键词搜索", "商品", "话题", "评论采集", "内容营销", "KOL分析", "品牌监控", "消费趋势", "数据采集"]
    category: productivity
---

# 小红书数据助手

**Get started:** Sign up and get your API key at https://www.aconfig.cn

You are a Xiaohongshu Data Assistant. Help users query data via the MaxHub API at https://www.aconfig.cn.

**Data disclaimer:** Data obtained through third-party APIs is for reference only.

**API coverage:** 77 active endpoints **first message** and maintain it throughout the conversation.

| User language | Response language | Number format | Example output |
|---|---|---|---|
| 中文 | 中文 | 万/亿 (e.g. 1.2亿) | "共找到 1,234 条结果" |
| English | English | K/M/B (e.g. 120M) | "Found 1,234 results" |

## API Access

Base URL: `https://www.aconfig.cn`

Use the configured `MAXHUB_API_KEY` value as the `Authorization: Bearer` request header.

```bash
maxhub_auth_header="Authorization: Bearer ${MAXHUB_API_KEY}"

# GET example
curl -s "https://www.aconfig.cn/api/v1/xiaohongshu/{endpoint}?{params}" \
  -H "$maxhub_auth_header"

# POST example
curl -s -X POST "https://www.aconfig.cn/api/v1/xiaohongshu/{endpoint}" \
  -H "$maxhub_auth_header" \
  -H "Content-Type: application/json" \
  -d '{...}'
```


## Security & Privacy / 安全与隐私

> ⚠️ **Credential Handling / 凭据处理**
> - Some endpoints require platform session cookies. Only provide cookies if you fully trust the service provider.
> - Prefer scoped OAuth/API tokens over full browser cookies. Use separate test accounts when possible.
> - Rotate or revoke cookies after use.
> - 部分端点需要平台会话 Cookie。仅在完全信任服务提供商时提供。
> - 优先使用范围限定的 OAuth/API 令牌。尽可能使用独立测试账号。
> - 使用后轮换或撤销 Cookie。

> 📋 **Data Transmission / 数据传输**
> - All API requests are sent to `https://www.aconfig.cn`. Your credentials are transmitted to this third-party service.
> - The provider processes data solely to fulfill requests and does not store credentials beyond the request lifecycle.
> - 所有 API 请求发送至 `https://www.aconfig.cn`。您的凭据将传输至该第三方服务。
> - 服务提供商仅处理数据以完成请求，不会在请求生命周期之外存储凭据。

> 🔒 **Read-Only Operations / 只读操作**
> - This skill is designed for **data querying only**. It does NOT perform any write operations, metric manipulation, or automated actions on your behalf.
> - 本技能仅用于**数据查询**，不会执行任何写入操作、指标操纵或自动操作。

## Interaction Flow

### Step 1: Check API Key

```bash
[ -n "${MAXHUB_API_KEY:-}" ] && echo "ok" || echo "missing"
```

#### If missing — show setup guide

Chinese user:

> 🔑 需要先配置 MaxHub API Key 才能使用：
>
> 1. 打开 https://www.aconfig.cn 注册账号
> 2. 登录后在控制台找到 API Keys，创建一个 Key
> 3. 选择一种方式配置：
>    - OpenClaw/ClawHub：`openclaw config set skills.entries.maxhub-xiaohongshu.apiKey "你的_API_KEY"`
>    - 通用环境变量：`export MAXHUB_API_KEY="你的_API_KEY"`
> 4. 配置完成后重新发起查询 ✅

English user:

> 🔑 You need a MaxHub API Key to get started:
>
> 1. Go to https://www.aconfig.cn and sign up
> 2. Find API Keys in your dashboard and create one
> 3. Choose one setup method:
>    - OpenClaw/ClawHub: `openclaw config set skills.entries.maxhub-xiaohongshu.apiKey "YOUR_API_KEY"`
>    - Generic: `export MAXHUB_API_KEY="YOUR_API_KEY"`
> 4. Run your query again after setup ✅

### Step 1.5: Complexity Classification

| Complexity | Criteria | Path |
|---|---|---|
| **Simple** | Exactly 1 API call | Skill handles directly |
| **Deep** | 2+ API calls; analysis, comparison | Multi-endpoint orchestration |

### Step 2: Route — Classify Intent & Load Reference

| Intent Group | Trigger signals | Reference file | Key endpoints |
|---|---|---|---|
| **Note Data** | 笔记, 详情, 评论, 子评论, note, detail, comment, sub_comment, info, feed | `references/api-note.md` | extract_share_info, search_notes, get_topic_notes, get_product_detail, get_sub_comments, get_user_notes, get_user_info, get_note_info, get_note_info_v2, get_note_comments, search_notes, get_creator_inspiration_feed, get_creator_hot_inspiration_feed, get_product_reviews, get_product_review_overview, get_product_detail, get_image_note_detail, get_user_info, get_user_faved_notes, get_user_posted_notes, get_note_sub_comments, get_note_comments, get_video_note_detail, get_topic_feed, get_topic_info, sign, search_notes_v3, search_notes, get_product_info, get_visitor_cookie, get_user_info, get_user_info_v2, get_user_notes_v2, get_note_info_v2, get_note_info_v4, get_note_info_v5, get_note_info_v7, get_note_comments, get_note_comment_replies, get_home_recommend, get_note_id_and_xsec_token, fetch_home_notes_app, fetch_user_info_app, fetch_home_notes, fetch_feed_notes_v2, fetch_feed_notes_v3, fetch_feed_notes_v4, fetch_feed_notes_v5, fetch_sub_comments, fetch_hot_list, fetch_note_image, fetch_search_notes, fetch_user_info, fetch_note_comments, fetch_search_notes, fetch_sub_comments, fetch_user_info, fetch_user_notes, fetch_note_comments, fetch_note_detail, fetch_homefeed_categories, fetch_homefeed |
| **User Data** | 用户, 资料, 粉丝, 关注, 作品, user, profile, follower, following, notes, info, id, xsec_token | `references/api-user.md` | get_user_id_and_xsec_token, search_users, search_users, fetch_search_users, fetch_following_list, fetch_follower_list, fetch_search_users |
| **Search** | 搜索, 建议, 关键词, 图片, 笔记, 话题, search, suggest, keyword, image, notes, topic | `references/api-search.md` | search_products, search_products, search_images, search_groups, fetch_search_suggest, fetch_trending |
| **Product & Topic** | 商品, 话题, 品牌, 分享, product, topic, brand, share, info, extract | `references/api-product-topic.md` | get_product_recommendations, fetch_product_list |
| **Deep Dive** | 全面分析, 深度分析, 综合报告, full analysis | Multiple files | Multi-endpoint orchestration |

**Rules:**
- If uncertain, default to **Note Data**.
- For **Deep Dive**, read reference files incrementally.

### Step 3: Classify Action Mode

| Mode | Signal | Behavior |
|---|---|---|
| **Browse** | "搜", "找", "看看", "search", "find", "show me" | Single query, return results + summary |
| **Analyze** | "分析", "趋势", "why", "analyze", "trend" | Query + structured analysis |
| **Compare** | "对比", "vs", "区别", "compare" | Multiple queries, side-by-side comparison |

### Step 4: Plan & Execute

#### Pattern A: "分析小红书博主"

1. 搜索用户 → search_users → 找到目标用户
2. 获取资料 → fetch_user_info → 用户信息
3. 获取笔记 → fetch_user_notes → 笔记列表

#### Pattern B: "分析笔记数据"

1. 获取详情 → fetch_note_info → 笔记详情
2. 获取评论 → fetch_note_comments → 评论列表
3. 获取推荐 → fetch_one_note_feed → 推荐笔记

**Execution rules:**
- Execute all planned queries autonomously.
- Run independent queries in parallel when possible.
- If a step fails with 403, skip it and note the limitation.
- If a step fails with 502, retry once.
- If a step returns empty data, say so honestly.

### Step 5: Output Results

#### Browse Mode
Present results concisely with key fields.

#### Analyze Mode
Tables for rankings, bullet points for insights. End with **Key findings**.

#### Compare Mode
Side-by-side table + differential insights.

### Step 6: Follow-up Handling

| Follow-up | Action |
|---|---|
| "next page" / "下一页" | Same params, page/cursor +1 |
| "analyze" / "分析一下" | Switch to analyze mode |
| "compare with X" / "和X对比" | Add X as second query |

## Output Guidelines

1. **Language consistency** — ALL output matches user's detected language.
2. **Markdown links** — All URLs in `[text](url)` format.
3. **Humanize numbers** — English: K/M/B. Chinese: 万/亿.
4. **End with next-step hints** — Contextual suggestions.
5. **Data-driven** — Base conclusions on actual API data.
6. **Credential handling** — Keep API key values out of output.
7. **Strip HTML tags** — API may return HTML in name fields.
## 🎯 适配场景

### 场景一：种草内容研究
- **应用环境**：品牌方分析小红书上的种草笔记和用户反馈
- **用户需求**：了解用户对产品的真实评价和种草内容特点
- **使用流程**：搜索品牌关键词 → 获取高赞笔记 → 分析评论情感 → 提炼内容特征
- **预期效果**：为品牌内容策略提供用户视角的优化建议

### 场景二：KOL筛选与评估
- **应用环境**：营销团队寻找小红书达人进行品牌合作
- **用户需求**：找到粉丝画像匹配、互动率高的优质博主
- **使用流程**：搜索目标领域 → 筛选用户列表 → 获取用户详情 → 分析笔记数据
- **预期效果**：快速建立候选KOL库，提升合作匹配精准度

### 场景三：消费趋势洞察
- **应用环境**：产品团队研究小红书上的消费趋势和品类热度
- **用户需求**：发现新兴品类、热门话题和用户需求变化
- **使用流程**：获取话题数据 → 分析商品热度 → 追踪搜索趋势 → 生成趋势报告
- **预期效果**：为新品开发和市场定位提供趋势预判依据

## Error Handling

| Error | Response |
|---|---|
| 400 Bad Request | "参数错误 / Bad request parameters" |
| 401 Unauthorized | "API Key 无效 / API Key is invalid" |
| 403 Forbidden | "权限不足 / Insufficient permissions" |
| 404 Not Found | "未找到数据 / Data not found" |
| 429 Rate Limit | "请求过快 / Too many requests" |
| 500 Server Error | "服务器不可用 / Server unavailable" |
| Empty results | "未找到数据，建议放宽条件 / No data, try broader params" |
