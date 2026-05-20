---
name: maxhub-skills
description: "MaxHub 技能仓库聚合入口。涵盖20个平台的数据查询技能，覆盖国内外主流社交媒体、短视频、职场、邮件等全场景API数据服务。"
license: MIT-0
metadata:
  author: maxhub
  version: "3.2.0"
  openclaw:
    emoji: "🌐"
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
    tags: ["maxhub", "api", "social-media", "data", "skills", "aggregation"]
    category: productivity
---

# MaxHub Skills 技能仓库

**Get started:** Sign up and get your API key at https://www.aconfig.cn

本仓库是 MaxHub 技能的聚合入口，包含 **20 个平台技能**，覆盖国内外主流社交媒体、短视频、职场、邮件等全场景 API 数据查询服务。

所有技能统一通过 `MAXHUB_API_KEY` 认证，Base URL 为 `https://www.aconfig.cn`。

## 技能总览

| # | 技能名称 | 平台 | 描述 | 版本 | 引用文件数 |
|---|---------|------|------|------|-----------|
| 1 | 📺 maxhub-bilibili | B站 | B站视频、用户、评论、弹幕、直播数据查询助手 | 3.2.0 | 5 |
| 2 | 🎵 maxhub-douyin | 抖音 | 抖音全场景数据查询助手，7大模块 | 3.2.0 | 8 |
| 3 | 📸 maxhub-instagram | Instagram | Instagram 全场景数据查询，V1/V2/V3三版API | 3.2.0 | 4 |
| 4 | 🎬 maxhub-kuaishou | 快手 | 快手全场景数据查询，App/Web双端API | 3.2.0 | 3 |
| 5 | 🍋 maxhub-lemon8 | Lemon8 | Lemon8 内容数据查询助手 | 3.2.0 | 3 |
| 6 | 💼 maxhub-linkedin | LinkedIn | LinkedIn 职场数据查询，V1/V2双版API | 3.2.0 | 5 |
| 7 | 🦐 maxhub-pipixia | 皮皮虾 | 皮皮虾数据查询助手 | 3.2.0 | 3 |
| 8 | 🤖 maxhub-reddit | Reddit | Reddit 数据查询助手 | 3.2.0 | 4 |
| 9 | 🎥 maxhub-sora2 | Sora2 | Sora2 视频平台数据查询助手 | 3.2.0 | 3 |
| 10 | 📧 maxhub-temp-mail | 临时邮箱 | 临时邮箱服务助手 | 3.2.0 | 2 |
| 11 | 🧵 maxhub-threads | Threads | Threads 数据查询助手 | 3.2.0 | 2 |
| 12 | 🎶 maxhub-tiktok | TikTok | TikTok 全场景数据查询，7大模块 | 3.2.0 | 5 |
| 13 | 📰 maxhub-toutiao | 今日头条 | 今日头条数据查询助手 | 3.2.0 | 2 |
| 14 | 𝕏 maxhub-twitter | Twitter/X | Twitter/X 数据查询助手 | 3.2.0 | 3 |
| 15 | 💬 maxhub-wechat | 微信 | 微信视频号和公众号数据查询 | 3.2.0 | 3 |
| 16 | 🐦 maxhub-weibo | 微博 | 微博全场景数据查询，多版本API | 3.2.0 | 6 |
| 17 | 📕 maxhub-xiaohongshu | 小红书 | 小红书全场景数据查询，多版本API | 3.2.0 | 5 |
| 18 | 🍉 maxhub-xigua | 西瓜视频 | 西瓜视频数据查询助手 | 3.2.0 | 2 |
| 19 | ▶️ maxhub-youtube | YouTube | YouTube 全场景数据查询，Web/V2双版API | 3.2.0 | 4 |
| 20 | 💡 maxhub-zhihu | 知乎 | 知乎数据查询助手 | 3.2.0 | 4 |

## 分类索引

### 🎬 短视频 & 视频平台

| 技能 | 目录 | 引用文件 |
|------|------|---------|
| 📺 B站 | `maxhub-bilibili/` | `api-live.md`, `api-search.md`, `api-user.md`, `api-video.md`, `param-mappings.md` |
| 🎵 抖音 | `maxhub-douyin/` | `api-creator.md`, `api-index.md`, `api-search.md`, `api-trending.md`, `api-user.md`, `api-video.md`, `api-xingtu.md`, `param-mappings.md` |
| 🎬 快手 | `maxhub-kuaishou/` | `api-user.md`, `api-video.md`, `param-mappings.md` |
| 🎶 TikTok | `maxhub-tiktok/` | `api-ads-analytics.md`, `api-search.md`, `api-user.md`, `api-video.md`, `param-mappings.md` |
| 🍉 西瓜视频 | `maxhub-xigua/` | `api-video-user.md`, `param-mappings.md` |
| ▶️ YouTube | `maxhub-youtube/` | `api-channel.md`, `api-search.md`, `api-video.md`, `param-mappings.md` |
| 🎥 Sora2 | `maxhub-sora2/` | `api-cameo.md`, `api-post-user.md`, `param-mappings.md` |

### 📱 社交媒体 & 社区

| 技能 | 目录 | 引用文件 |
|------|------|---------|
| 📸 Instagram | `maxhub-instagram/` | `api-post.md`, `api-search.md`, `api-user.md`, `param-mappings.md` |
| 🤖 Reddit | `maxhub-reddit/` | `api-post.md`, `api-subreddit.md`, `api-user-search.md`, `param-mappings.md` |
| 🧵 Threads | `maxhub-threads/` | `api-post-user.md`, `param-mappings.md` |
| 𝕏 Twitter/X | `maxhub-twitter/` | `api-search-trending.md`, `api-tweet.md`, `param-mappings.md` |
| 💬 微信 | `maxhub-wechat/` | `api-channels.md`, `api-mp.md`, `param-mappings.md` |
| 🐦 微博 | `maxhub-weibo/` | `api-post.md`, `api-search.md`, `api-trending.md`, `api-user.md`, `api-video-feed.md`, `param-mappings.md` |
| 📕 小红书 | `maxhub-xiaohongshu/` | `api-note.md`, `api-product-topic.md`, `api-search.md`, `api-user.md`, `param-mappings.md` |
| 💡 知乎 | `maxhub-zhihu/` | `api-content.md`, `api-search-trending.md`, `api-user.md`, `param-mappings.md` |
| 🦐 皮皮虾 | `maxhub-pipixia/` | `api-post-user.md`, `api-search-trending.md`, `param-mappings.md` |
| 🍋 Lemon8 | `maxhub-lemon8/` | `api-post-user.md`, `api-search-discover.md`, `param-mappings.md` |

### 💼 职场 & 工具

| 技能 | 目录 | 引用文件 |
|------|------|---------|
| 💼 LinkedIn | `maxhub-linkedin/` | `api-company.md`, `api-content.md`, `api-search-jobs.md`, `api-user.md`, `param-mappings.md` |
| 📰 今日头条 | `maxhub-toutiao/` | `api-content-user.md`, `param-mappings.md` |
| 📧 临时邮箱 | `maxhub-temp-mail/` | `api-email.md`, `param-mappings.md` |

## 仓库结构

```
skills-repo/
├── SKILL.md                    ← 本文件（聚合入口）
├── maxhub-bilibili/
│   ├── SKILL.md                ← 技能入口
│   ├── _meta.json              ← 元数据
│   ├── README.md               ← 英文说明
│   ├── README_CN.md            ← 中文说明
│   └── references/             ← API引用文件
│       ├── api-video.md
│       ├── api-user.md
│       ├── api-search.md
│       ├── api-live.md
│       └── param-mappings.md
├── maxhub-douyin/
│   ├── SKILL.md
│   ├── _meta.json
│   ├── README.md
│   ├── README_CN.md
│   └── references/
│       ├── api-video.md
│       ├── api-user.md
│       ├── api-search.md
│       ├── api-trending.md
│       ├── api-creator.md
│       ├── api-index.md
│       ├── api-xingtu.md
│       └── param-mappings.md
├── ...（其余18个技能目录结构相同）
└── maxhub-zhihu/
    ├── SKILL.md
    ├── _meta.json
    ├── README.md
    ├── README_CN.md
    └── references/
        ├── api-content.md
        ├── api-search-trending.md
        ├── api-user.md
        └── param-mappings.md
```

## 统一认证

所有技能共享同一认证方式：

```bash
MAXHUB_API_KEY="your_api_key_here"
maxhub_auth_header="Authorization: Bearer ${MAXHUB_API_KEY}"

curl -s "https://www.aconfig.cn/api/v1/{platform}/{endpoint}?{params}" \
  -H "$maxhub_auth_header"
```

获取 API Key：https://www.aconfig.cn

## 技能文件规范

每个技能目录包含以下标准文件：

| 文件 | 用途 | 必需 |
|------|------|------|
| `SKILL.md` | 技能入口，含 frontmatter 元数据、交互流程、路由表 | ✅ |
| `_meta.json` | 发布元数据（ownerId, slug, version, homepage） | ✅ |
| `README.md` | 英文说明文档 | ✅ |
| `README_CN.md` | 中文说明文档 | ✅ |
| `references/` | API 引用文件目录 | ✅ |
| `references/param-mappings.md` | 参数映射与转换规则 | ✅ |
| `references/api-*.md` | 按 API 分类的引用文件 | ✅ |

## 引用文件命名约定

| 命名模式 | 含义 | 示例 |
|---------|------|------|
| `api-video.md` | 视频相关接口 | 视频详情、播放、弹幕 |
| `api-user.md` | 用户相关接口 | 用户信息、粉丝、关注 |
| `api-search.md` | 搜索相关接口 | 综合搜索、关键词搜索 |
| `api-post.md` | 帖子/内容接口 | 帖子详情、评论 |
| `api-trending.md` | 热榜/趋势接口 | 热搜、排行榜 |
| `api-comment.md` | 评论相关接口 | 评论列表、回复 |
| `api-live.md` | 直播相关接口 | 直播间、直播流 |
| `api-channel.md` | 频道相关接口 | 频道信息、视频列表 |
| `api-company.md` | 公司/企业接口 | 公司资料、员工 |
| `api-email.md` | 邮件相关接口 | 临时邮箱、收件箱 |
| `param-mappings.md` | 参数映射规则 | 请求参数转换与校验 |

## 平台抓取指引

### 抓取流程

1. **解析本文件**：读取 `SKILL.md` 获取全部技能列表及分类
2. **遍历技能目录**：按 `maxhub-{platform}/` 目录逐个进入
3. **读取技能入口**：解析每个目录下的 `SKILL.md`，提取 frontmatter 元数据和路由表
4. **加载引用文件**：根据路由表中 `Reference file` 字段，加载 `references/` 下对应的 API 引用
5. **提取元数据**：读取 `_meta.json` 获取版本和发布信息

### 关键标识

- **目录命名**：`maxhub-{platform}` 为技能唯一标识
- **frontmatter.name**：与目录名一致
- **frontmatter.metadata.openclaw.primaryEnv**：统一为 `MAXHUB_API_KEY`
- **_meta.json.slug**：与目录名一致
- **_meta.json.ownerId**：统一为 `maxhub-skills`

### 技能发现规则

```
技能根目录 = 本文件所在目录
技能列表 = 子目录名匹配 maxhub-*/ 的所有目录
技能入口 = {技能根目录}/{技能目录名}/SKILL.md
技能元数据 = {技能根目录}/{技能目录名}/_meta.json
技能引用 = {技能根目录}/{技能目录名}/references/*.md
```
