# 🚀 MaxHub API Skills：一站式多平台数据采集利器

> 让 AI 助手轻松获取抖音、TikTok、B站、小红书等 20 个平台的数据，987 个 API 端点，ClawHub 一键安装

---

## 📖 项目简介

**MaxHub API Skills** 是一套专为 OpenClaw 平台设计的技能集合，通过简单的自然语言指令，即可让 AI 助手获取各大主流平台的公开数据。所有端点严格对齐官方 API 文档，路径精确、参数完整。

- **GitHub**: https://github.com/XieWxx/maxhub-api-skills
- **官网**: https://www.aconfig.cn
- **版本**: v3.2.0
- **协议**: MIT License

### 📦 下载地址

| 平台 | 地址 | 说明 |
|------|------|------|
| GitHub | https://github.com/XieWxx/maxhub-api-skills | 源码仓库 |
| ClawHub | https://clawhub.ai/u/xiewxx | OpenClaw 技能市场 |

---

## ✨ 核心优势

### 🎯 一站式多平台支持

支持 **20 个主流平台**，覆盖国内外主流社交媒体、视频平台、知识社区：

| 平台类型 | 支持平台 |
|---------|---------|
| 短视频 | 抖音（271 API）、TikTok（189 API）、快手（9 API）、西瓜视频（7 API）、皮皮虾（16 API） |
| 长视频 | B站、YouTube |
| 社交媒体 | 微博、Twitter/X、Instagram、Threads、Reddit、LinkedIn |
| 知识社区 | 知乎、小红书、微信 |
| 其他 | Lemon8、Sora2、临时邮箱 |

### 🔒 安全合规

- ✅ 仅获取公开数据，不触碰用户隐私
- ✅ 通过 HTTPS 加密传输，保障数据安全
- ✅ 不存储、不转发用户凭证
- ✅ 不执行任何平台操纵操作（刷量、刷播放等）
- ✅ 已移除所有指标操纵端点
- ✅ 需要 Cookie 的端点已添加安全警告和最小权限说明
- ✅ 所有数据传输目标已明确披露
- ✅ 已通过 ClawHub 安全审核

### 🌍 国际化支持

所有 Skill 文档支持 **中英双语**，方便国内外用户使用。

### ⚡ 智能调度

- 自动识别用户意图，选择最合适的 API
- 支持链式调用，自动填充参数
- 内置调用限制，防止意外产生高额费用

### 📐 端点精确性

- 所有端点路径严格来源于官方 API 文档
- 路径精确到具体子分类版本（如 `/api/v1/douyin/web/fetch_one_video`）
- 参数表包含名称、类型、必填状态、描述和示例值
- 废弃端点已过滤

---

## 🎪 热门 Skill 推荐

### 1️⃣ maxhub-douyin（抖音）

**API 数量**: 271

**核心功能**:
- 🔥 实时热搜榜单获取
- 📹 视频详情、评论、弹幕数据
- 👤 用户信息、粉丝列表、作品列表
- 🔍 关键词搜索（视频、用户、话题）
- 🎵 创作者中心、星图数据、指数分析

**使用场景**:
```
用户: 帮我看看今天抖音热搜第一是什么
AI: 正在获取抖音热搜榜...
    今天的热搜第一是：[话题名称]，热度 1234.5万
```

---

### 2️⃣ maxhub-tiktok（TikTok）

**API 数量**: 189

**核心功能**:
- 🌍 支持多地区（美国、日本、东南亚等）
- 📹 视频、用户、评论、直播数据
- 📊 广告分析、创作者数据
- 🛒 店铺商品、热卖列表

---

### 3️⃣ maxhub-bilibili（B站）

**API 数量**: 41

**核心功能**:
- 📺 视频、番剧、影视信息
- 💬 评论、弹幕数据
- 👤 UP主信息、投稿列表
- 🔥 热门视频、排行榜

---

### 4️⃣ maxhub-xiaohongshu（小红书）

**API 数量**: 77

**核心功能**:
- 📝 笔记详情、评论数据
- 👤 用户信息、粉丝列表
- 🔍 关键词搜索
- 🛍️ 商品信息、话题数据

---

### 5️⃣ maxhub-weibo（微博）

**API 数量**: 64

**核心功能**:
- 🔥 实时热搜榜
- 👤 用户信息、微博列表
- 💬 评论数据
- 🔍 AI搜索、高级搜索

---

## 🛠️ 快速开始

### 第一步：获取 API Key

1. 访问 [MaxHub 官网](https://www.aconfig.cn)
2. 注册账号并登录
3. 在控制台创建 API Key

### 第二步：配置环境变量

```bash
export MAXHUB_API_KEY=mh_sk_your_api_key_here
export MAXHUB_BASE_URL=https://www.aconfig.cn
```

### 第三步：安装 Skill

```bash
# 安装单个 Skill
clawhub skill install maxhub-douyin

# 批量安装
for skill in maxhub-douyin maxhub-tiktok maxhub-bilibili maxhub-xiaohongshu maxhub-weibo; do
  clawhub skill install "$skill"
done
```

### 第四步：开始使用

直接用自然语言与 AI 对话即可：

```
用户: 帮我看看抖音今天的热搜
AI: [自动调用 maxhub-douyin 获取数据并展示]

用户: 分析一下这个 TikTok 视频的评论情感
AI: [自动获取评论并进行情感分析]
```

---

## 📊 平台覆盖统计

| Skill | API 数量 | 主要用途 |
|-------|---------|---------|
| maxhub-douyin | 271 | 抖音数据分析、热搜监控、创作者分析 |
| maxhub-tiktok | 189 | TikTok 海外数据分析、广告分析 |
| maxhub-linkedin | 85 | 商业情报、公司分析 |
| maxhub-xiaohongshu | 77 | 小红书种草分析、笔记研究 |
| maxhub-instagram | 68 | Instagram 帖子与用户分析 |
| maxhub-weibo | 64 | 微博舆情监控 |
| maxhub-bilibili | 41 | B站内容分析、UP主研究 |
| maxhub-youtube | 37 | YouTube 视频/频道分析 |
| maxhub-zhihu | 31 | 知乎内容分析 |
| maxhub-wechat | 24 | 微信视频号/公众号数据 |
| maxhub-lemon8 | 16 | Lemon8 帖子分析 |
| maxhub-pipixia | 16 | 皮皮虾内容分析 |
| maxhub-reddit | 13 | Reddit 帖子与版块分析 |
| maxhub-sora2 | 14 | Sora2 AI视频平台 |
| maxhub-twitter | 12 | Twitter/X 推文分析 |
| maxhub-kuaishou | 9 | 快手视频分析 |
| maxhub-xigua | 7 | 西瓜视频分析 |
| maxhub-toutiao | 7 | 今日头条分析 |
| maxhub-threads | 3 | Threads 帖子分析 |
| maxhub-temp-mail | 3 | 临时邮箱服务 |

---

## 🎯 典型应用场景

### 📈 市场研究

```
用户: 帮我分析一下最近一周抖音上"新能源汽车"相关话题的热度趋势
AI: [调用多个 API 获取数据并生成趋势报告]
```

### 📝 内容创作

```
用户: 给我找 10 个小红书上关于"减脂餐"的高赞笔记，分析它们的共同特点
AI: [获取笔记数据并分析内容特点]
```

### 🔍 竞品分析

```
用户: 对比分析 @品牌A 和 @品牌B 在抖音上的粉丝画像和互动数据
AI: [获取双方数据并生成对比报告]
```

### 📊 数据监控

```
用户: 每天早上帮我获取抖音、微博、B站的热搜榜并发送到邮箱
AI: [设置定时任务，自动获取并发送]
```

---

## 🔧 技术特点

### 智能意图识别

系统会自动理解用户意图，选择最合适的 API：

```
用户: 看看这个视频有多少点赞
AI: [识别到需要获取视频详情，自动调用对应 API]
```

### 链式调用

支持自动串联多个 API 调用：

```
用户: 找到抖音上粉丝最多的 10 个美食博主，并分析他们的最新视频
AI:
  1. 搜索美食博主 → 获取列表
  2. 按粉丝数排序 → 筛选 Top 10
  3. 获取每位博主的最新视频 → 汇总分析
```

### 参数智能填充

系统会自动从上下文中提取参数：

```
用户: 分析 @某博主 的粉丝数据
AI: [自动提取博主 ID，调用粉丝分析 API]
```

---

## 📚 文档资源

- **GitHub 仓库**: https://github.com/XieWxx/maxhub-api-skills
- **API 文档**: https://www.aconfig.cn/docs
- **问题反馈**: https://github.com/XieWxx/maxhub-api-skills/issues

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

---

## 📄 开源协议

本项目采用 [MIT License](./LICENSE) 开源协议。

---

## 🌟 Star History

如果这个项目对你有帮助，欢迎 Star ⭐️ 支持！

[![Star History Chart](https://api.star-history.com/svg?repos=XieWxx/maxhub-api-skills&type=Date)](https://star-history.com/#XieWxx/maxhub-api-skills&Date)

---

## 📮 联系我们

- **官网**: https://www.aconfig.cn
- **GitHub**: https://github.com/XieWxx/maxhub-api-skills

---

**MaxHub API Skills** - 让数据采集更简单，让 AI 助手更强大！🚀
