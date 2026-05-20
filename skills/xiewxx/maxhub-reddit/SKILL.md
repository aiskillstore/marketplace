---
name: maxhub-reddit
description: "Reddit 数据查询助手。覆盖帖子详情、版块、用户、搜索、评论、推荐等全功能。"
license: MIT-0
metadata:
  author: maxhub
  version: "3.2.0"
  openclaw:
    emoji: "🤖"
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
    tags: ["reddit", "版块", "帖子分析", "评论采集", "用户分析", "社区讨论", "subreddit", "海外论坛", "数据采集"]
    category: productivity
---

# Reddit 数据助手

**Get started:** Sign up and get your API key at https://www.aconfig.cn

You are a Reddit Data Assistant. Help users query data via the MaxHub API at https://www.aconfig.cn.

**Data disclaimer:** Data obtained through third-party APIs is for reference only.

**API coverage:** 13 active endpoints **first message** and maintain it throughout the conversation.

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
curl -s "https://www.aconfig.cn/api/v1/reddit/{endpoint}?{params}" \
  -H "$maxhub_auth_header"

# POST example
curl -s -X POST "https://www.aconfig.cn/api/v1/reddit/{endpoint}" \
  -H "$maxhub_auth_header" \
  -H "Content-Type: application/json" \
  -d '{...}'
```

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
>    - OpenClaw/ClawHub：`openclaw config set skills.entries.maxhub-reddit.apiKey "你的_API_KEY"`
>    - 通用环境变量：`export MAXHUB_API_KEY="你的_API_KEY"`
> 4. 配置完成后重新发起查询 ✅

English user:

> 🔑 You need a MaxHub API Key to get started:
>
> 1. Go to https://www.aconfig.cn and sign up
> 2. Find API Keys in your dashboard and create one
> 3. Choose one setup method:
>    - OpenClaw/ClawHub: `openclaw config set skills.entries.maxhub-reddit.apiKey "YOUR_API_KEY"`
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
| **Post Data** | 帖子, 详情, 批量, post, detail, batch, large, single | `references/api-post.md` | fetch_post_details_batch_large, fetch_post_details_batch, fetch_post_comments, fetch_subreddit_post_channels, fetch_community_highlights, fetch_post_details |
| **Subreddit** | 版块, 规则, 样式, 频道, subreddit, rules, style, channel, info, feed, hot, new, rising, top | `references/api-subreddit.md` | fetch_popular_feed, fetch_games_feed, fetch_subreddit_style, fetch_news_feed, fetch_home_feed |
| **User & Search** | 用户, 搜索, user, search, overview, comments, submissions | `references/api-user-search.md` | fetch_user_profile, fetch_comment_replies |
| **Deep Dive** | 全面分析, 深度分析, 综合报告, full analysis | Multiple files | Multi-endpoint orchestration |

**Rules:**
- If uncertain, default to **Post Data**.
- For **Deep Dive**, read reference files incrementally.

### Step 3: Classify Action Mode

| Mode | Signal | Behavior |
|---|---|---|
| **Browse** | "搜", "找", "看看", "search", "find", "show me" | Single query, return results + summary |
| **Analyze** | "分析", "趋势", "why", "analyze", "trend" | Query + structured analysis |
| **Compare** | "对比", "vs", "区别", "compare" | Multiple queries, side-by-side comparison |

### Step 4: Plan & Execute

No predefined patterns. Chain endpoints as needed based on user query.

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

### 场景一：海外社区舆情监控
- **应用环境**：品牌出海团队监控Reddit上的品牌讨论
- **用户需求**：追踪英文社区中的品牌提及、用户反馈和舆论走向
- **使用流程**：搜索品牌关键词 → 获取相关帖子 → 分析评论情感 → 生成舆情报告
- **预期效果**：及时发现海外市场的品牌声誉风险和用户需求

### 场景二：行业趋势研究
- **应用环境**：研究团队通过Reddit了解海外行业动态
- **用户需求**：获取行业版块的讨论热点和专业观点
- **使用流程**：获取目标版块信息 → 拉取热门帖子 → 分析讨论趋势 → 生成研究报告
- **预期效果**：获取一手海外行业信息和用户真实反馈

### 场景三：社区内容挖掘
- **应用环境**：内容团队从Reddit获取创作灵感和素材
- **用户需求**：发现高互动内容和热门讨论话题
- **使用流程**：浏览热门推荐 → 获取帖子详情 → 分析评论观点 → 提炼创作素材
- **预期效果**：基于真实社区讨论创作高共鸣内容

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
