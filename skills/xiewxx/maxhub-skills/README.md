# MaxHub API Skills / MaxHub API 技能集合

[English](#english) | [中文](#中文)

---

<a name="中文"></a>
## 📋 Skill 列表

MaxHub API 平台的 OpenClaw Skill 集合，提供多平台数据采集和分析能力。所有端点严格对齐官方 API 文档，确保路径精确、参数完整。

| Skill | 平台 | 功能 | API数量 |
|-------|------|------|---------|
| [maxhub-douyin](./maxhub-douyin) | 抖音 | 视频/用户/搜索/热榜/创作者/星图/指数 | 271 |
| [maxhub-tiktok](./maxhub-tiktok) | TikTok | 视频/用户/搜索/广告分析/创作者/店铺 | 189 |
| [maxhub-linkedin](./maxhub-linkedin) | LinkedIn | 公司/用户/内容广告/搜索职位 | 85 |
| [maxhub-xiaohongshu](./maxhub-xiaohongshu) | 小红书 | 笔记/用户/搜索/商品话题 | 77 |
| [maxhub-instagram](./maxhub-instagram) | Instagram | 帖子/用户/搜索/工具转换 | 68 |
| [maxhub-weibo](./maxhub-weibo) | 微博 | 微博/用户/搜索/热搜/视频推荐 | 64 |
| [maxhub-bilibili](./maxhub-bilibili) | B站 | 视频/用户/搜索/直播评论 | 41 |
| [maxhub-youtube](./maxhub-youtube) | YouTube | 视频/频道/搜索评论 | 37 |
| [maxhub-zhihu](./maxhub-zhihu) | 知乎 | 内容/用户/搜索热门 | 31 |
| [maxhub-wechat](./maxhub-wechat) | 微信 | 视频号/公众号 | 24 |
| [maxhub-lemon8](./maxhub-lemon8) | Lemon8 | 帖子用户/搜索发现 | 16 |
| [maxhub-pipixia](./maxhub-pipixia) | 皮皮虾 | 帖子用户/搜索热门 | 16 |
| [maxhub-reddit](./maxhub-reddit) | Reddit | 帖子/版块/用户搜索 | 13 |
| [maxhub-sora2](./maxhub-sora2) | Sora2 | 出镜秀/帖子用户/工具 | 14 |
| [maxhub-twitter](./maxhub-twitter) | Twitter/X | 推文/用户/搜索热门 | 12 |
| [maxhub-kuaishou](./maxhub-kuaishou) | 快手 | 视频/用户/热榜 | 9 |
| [maxhub-xigua](./maxhub-xigua) | 西瓜视频 | 视频用户 | 7 |
| [maxhub-toutiao](./maxhub-toutiao) | 今日头条 | 内容用户 | 7 |
| [maxhub-threads](./maxhub-threads) | Threads | 帖子用户/搜索 | 3 |
| [maxhub-temp-mail](./maxhub-temp-mail) | 临时邮箱 | 临时邮箱服务 | 3 |

**端点总数：987**

## 🚀 快速开始

### 1. 获取 API Key

访问 [MaxHub 官网](https://www.aconfig.cn) 注册账号并获取 API Key。

### 2. 配置环境变量

```bash
export MAXHUB_API_KEY=mh_sk_your_api_key_here
export MAXHUB_BASE_URL=https://www.aconfig.cn
```

### 3. 安装 Skill

```bash
# 安装单个 Skill
clawhub skill install maxhub-douyin

# 批量安装
for skill in maxhub-douyin maxhub-tiktok maxhub-bilibili maxhub-xiaohongshu maxhub-weibo; do
  clawhub skill install "$skill"
done
```

## 🔒 安全声明

所有 Skill 均遵循以下安全原则：

- ✅ 仅通过 HTTPS 调用 MaxHub API
- ✅ 不存储、不转发用户凭证
- ✅ 不访问本地文件系统
- ✅ 不执行任何平台操纵操作（刷量、刷播放等）
- ✅ 不生成平台安全绕过签名
- ✅ 已移除所有指标操纵端点（如 `add_video_play_count`）
- ✅ 需要 Cookie 的端点已添加安全警告和最小权限说明
- ✅ 所有数据传输目标已明确披露（`https://www.aconfig.cn`）

## ⚡ 调用限制

为保护用户账户安全和控制费用，所有 Skill 遵循以下限制：

| 限制项 | 默认值 |
|--------|--------|
| 单次最大翻页数 | 5页 |
| 单次最大返回条数 | 50条 |
| 链式调用最大深度 | 3层 |
| 批量操作最大数量 | 10条 |

## 📖 文档结构

每个 Skill 目录包含：

- `SKILL.md` - Skill 说明文档（含意图路由表）
- `references/api-*.md` - 按功能分组的 API 参考文件
- `references/param-mappings.md` - 参数映射
- `_meta.json` - 元数据（版本、标签、依赖）

## 🔗 相关链接

- [MaxHub 官网](https://www.aconfig.cn)
- [API 文档](https://www.aconfig.cn/docs)
- [GitHub 仓库](https://github.com/XieWxx/maxhub-api-skills)

## 📝 版本历史

### v3.2.0 (2026-05-20)

- 将所有端点路径中的 `...` 通配符替换为真实子分类路径
- 端点路径精确到具体版本（如 `/api/v1/douyin/web/fetch_one_video`）

### v3.1.0 (2026-05-19)

- 修复 ClawHub 安全审计问题（ASI02/ASI03/ASI07/ASI04）
- 移除指标操纵端点（`add_video_play_count`、`fetch_increase_post_view_count`）
- 为需要 Cookie 的端点添加安全警告和最小权限说明
- 添加数据传输披露和源信息可追溯
- 添加 `homepage` 和 `repository` 到 `_meta.json`

### v3.0.0 (2026-05-18)

- 基于 `docs/` 唯一数据源重新生成所有 references 文件
- 端点覆盖率从 ~50% 提升至 99.9%
- 移除所有臆想的接口地址
- 清除所有接口调用定价信息
- 修正通配符使用

### v2.0.0 (2026-05-10)

- 统一 API 域名到 `https://www.aconfig.cn`
- 合并 weibo 和 weibo-v2
- 所有 skill 添加 `maxhub-` 前缀
- 过滤废弃端点

### v1.1.1 (2026-05-09)

- 修复 YAML 元数据格式
- repository 地址从 gitee 改为 GitHub

### v1.0.0 (2026-05-08)

- 初始版本发布

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

---

<a name="english"></a>
## 📋 Skill List

OpenClaw Skill collection for MaxHub API platform. All endpoints strictly align with official API documentation.

| Skill | Platform | Features | APIs |
|-------|----------|----------|------|
| [maxhub-douyin](./maxhub-douyin) | Douyin | Video/User/Search/Trending/Creator/Xingtu/Index | 271 |
| [maxhub-tiktok](./maxhub-tiktok) | TikTok | Video/User/Search/Ads Analytics/Creator/Shop | 189 |
| [maxhub-linkedin](./maxhub-linkedin) | LinkedIn | Company/User/Content Ads/Search Jobs | 85 |
| [maxhub-xiaohongshu](./maxhub-xiaohongshu) | Xiaohongshu | Note/User/Search/Product Topic | 77 |
| [maxhub-instagram](./maxhub-instagram) | Instagram | Post/User/Search/Tools | 68 |
| [maxhub-weibo](./maxhub-weibo) | Weibo | Post/User/Search/Trending/Video Feed | 64 |
| [maxhub-bilibili](./maxhub-bilibili) | Bilibili | Video/User/Search/Live Comment | 41 |
| [maxhub-youtube](./maxhub-youtube) | YouTube | Video/Channel/Search Comment | 37 |
| [maxhub-zhihu](./maxhub-zhihu) | Zhihu | Content/User/Search Trending | 31 |
| [maxhub-wechat](./maxhub-wechat) | WeChat | Channels/Media Platform | 24 |
| [maxhub-lemon8](./maxhub-lemon8) | Lemon8 | Post User/Search Discover | 16 |
| [maxhub-pipixia](./maxhub-pipixia) | Pipixia | Post User/Search Trending | 16 |
| [maxhub-reddit](./maxhub-reddit) | Reddit | Post/Subreddit/User Search | 13 |
| [maxhub-sora2](./maxhub-sora2) | Sora2 | Cameo/Post User/Tools | 14 |
| [maxhub-twitter](./maxhub-twitter) | Twitter/X | Tweet/User/Search Trending | 12 |
| [maxhub-kuaishou](./maxhub-kuaishou) | Kuaishou | Video/User/Trending | 9 |
| [maxhub-xigua](./maxhub-xigua) | Xigua Video | Video User | 7 |
| [maxhub-toutiao](./maxhub-toutiao) | Toutiao | Content User | 7 |
| [maxhub-threads](./maxhub-threads) | Threads | Post User/Search | 3 |
| [maxhub-temp-mail](./maxhub-temp-mail) | Temp Mail | Temporary email service | 3 |

**Total endpoints: 987**

## 🚀 Quick Start

### 1. Get API Key

Visit [MaxHub Official Site](https://www.aconfig.cn) to register and get your API Key.

### 2. Configure Environment Variables

```bash
export MAXHUB_API_KEY=mh_sk_your_api_key_here
export MAXHUB_BASE_URL=https://www.aconfig.cn
```

### 3. Install Skills

```bash
# Install a single Skill
clawhub skill install maxhub-douyin

# Batch install
for skill in maxhub-douyin maxhub-tiktok maxhub-bilibili maxhub-xiaohongshu maxhub-weibo; do
  clawhub skill install "$skill"
done
```

## 🔒 Security Statement

All Skills follow these security principles:

- ✅ Only call MaxHub API via HTTPS
- ✅ Do not store or forward user credentials
- ✅ Do not access local file system
- ✅ Do not perform any platform manipulation (fake views, likes, etc.)
- ✅ Do not generate platform security bypass signatures
- ✅ Removed all metric manipulation endpoints (e.g., `add_video_play_count`)
- ✅ Cookie-requiring endpoints include security warnings and least-privilege guidance
- ✅ All data transmission targets explicitly disclosed (`https://www.aconfig.cn`)

## ⚡ Rate Limits

| Limit Item | Default Value |
|------------|---------------|
| Max pages per request | 5 pages |
| Max results per request | 50 items |
| Max chain call depth | 3 layers |
| Max batch operation size | 10 items |

## 📖 Documentation Structure

Each Skill directory contains:

- `SKILL.md` - Skill documentation with intent routing table
- `references/api-*.md` - API reference files grouped by function
- `references/param-mappings.md` - Parameter mappings
- `_meta.json` - Metadata (version, tags, dependencies)

## 🔗 Related Links

- [MaxHub Official Site](https://www.aconfig.cn)
- [API Documentation](https://www.aconfig.cn/docs)
- [GitHub Repository](https://github.com/XieWxx/maxhub-api-skills)

## 📝 Version History

### v3.2.0 (2026-05-20)

- Replaced all `...` wildcards with real sub-category paths from docs
- Endpoint paths now precise to specific version

### v3.1.0 (2026-05-19)

- Fixed ClawHub security audit issues (ASI02/ASI03/ASI07/ASI04)
- Removed metric manipulation endpoints
- Added Cookie security warnings and data transmission disclosure
- Added `homepage` and `repository` to `_meta.json`

### v3.0.0 (2026-05-18)

- Rebuilt all references from docs as single source of truth
- Endpoint coverage increased from ~50% to 99.9%
- Removed all fabricated endpoint addresses
- Cleared all pricing information

### v2.0.0 (2026-05-10)

- Unified API domain to `https://www.aconfig.cn`
- Merged weibo and weibo-v2
- Added `maxhub-` prefix to all skills
- Filtered deprecated endpoints

### v1.0.0 (2026-05-08)

- Initial release

## 📄 License

MIT License

## 🤝 Contributing

Issues and Pull Requests are welcome!

---

**MaxHub API** - Making Data Collection Easier / 让数据采集更简单
