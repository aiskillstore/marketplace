---
name: aimpact-crypto
description: AIMPACT Crypto 技能提供 Crypto 领域早报、晚报、热点新闻和精选内容，基于 AI 评分智能排序，支持定时推送。当用户说"查询 AIMPACT Crypto 早报"、"查询 AIMPACT Crypto 晚报"、"查询 Crypto 24H 热点榜"或"查询 Crypto 精选内容"时调用。
version: 0.8.1
metadata:
  openclaw:
    requires:
      bins: [curl]
    optional:
      tools: [web_fetch, message]
---

# AIMPACT Crypto - Crypto 资讯助手

## 何时调用此技能

当用户说以下任一指令时，自动调用此技能：
- "查询 AIMPACT Crypto 早报"
- "查询 AIMPACT Crypto 晚报"
- "查询 Crypto 24H 热点榜"
- "查询 Crypto 精选内容"
- "生成 Crypto 日报"

提供 Crypto 领域早报、晚报、热点新闻和精选内容，基于 AI 评分智能排序后推送。

## 安装后提示

✅ 安装成功！你可以通过以下方式获取 Crypto 资讯：

- 📰 **查询 AIMPACT Crypto 早报** - 每日上午精选（前一天 00:00 - 当天 12:00）
- 🌙 **查询 AIMPACT Crypto 晚报** - 每日晚间总结（当天 12:00 - 24:00）
- 🔥 **查询 Crypto 24H 热点榜** - 最近 24 小时影响力最高内容
- 💎 **查询 Crypto 精选内容** - Crypto 领域高质量资讯

你也可以直接说：**"帮我查询 AIMPACT Crypto 早报"**

## 功能
- 提供 AIMPACT Crypto 早报、晚报、热点新闻榜
- 基于 AI 评分智能排序，优先展示高价值内容
- 按分类整理（DeFi/NFT/Layer2/监管/项目/市场）
- 可选推送：基于 OpenClaw 已配置的 `message` 工具与渠道凭据，提供已配置渠道的推送能力
- 去重：默认基于当前批次结果去重（标题或 ID）

## 使用方式

### 快捷指令（推荐）

告诉你的 AI 助手以下任一指令：

- **"查询 AIMPACT Crypto 早报"**
  - 获取每日上午精选内容（前一天 00:00 - 当天 12:00，最多 10 条）
  
- **"查询 AIMPACT Crypto 晚报"**
  - 获取每日晚间总结（当天 12:00 - 24:00，最多 10 条）
  
- **"查询 Crypto 24H 热点榜"**
  - 获取最近 24 小时影响力最高内容（按 AI 评分降序，最多 10 条）
  
- **"查询 Crypto 精选内容"**
  - 获取 Crypto 领域高质量资讯（最近 24 小时，最多 10 条）

### 定时推送（可选）

在 OpenClaw 外部配置 cron 任务：

前提说明：
- 本技能不内置、不存储任何渠道凭据。
- 如需推送，需在 OpenClaw 中预先配置 `message` 工具及渠道凭据。
- 若未配置 `message` 或渠道凭据，则仅输出报告，不执行推送。

**推荐时间**:
- 早报: 每日 12:00
- 晚报: 每日 22:00
- 热点: 每日 18:00

**示例配置**:
```bash
# Linux/macOS crontab
0 12 * * * openclaw agent --message "查询 AIMPACT Crypto 早报"
0 18 * * * openclaw agent --message "查询 Crypto 24H 热点榜"
0 22 * * * openclaw agent --message "查询 AIMPACT Crypto 晚报"
```

**Windows 任务计划程序**:
```powershell
# 创建每日 12:00 早报任务
schtasks /create /tn "AIMPACT-Crypto早报" /tr "openclaw agent --message '查询 AIMPACT Crypto 早报'" /sc daily /st 12:00
```

## 🎯 数据源配置

### 当前启用信源

| 源 | URL | 类型 | 说明 |
|---|---|---|---|
| MetaEra AI 快讯 | https://agent.me.news/skill/flash/list?page=1&size=20 | API | 全量快讯（需筛选 Crypto 相关新闻） |
| Aimpact Crypto 新闻 | https://agent.me.news/skill/aimpact/articles?page=1&size=20&category=crypto | API | AIMPACT 自有 Crypto 新闻流 |

**信源策略：**
- 优先读取 MetaEra 全量快讯，并从结果中筛选 Crypto 相关新闻
- 同步使用 AIMPACT Crypto 新闻作为主信源补充
- 所有可用信源以 `sources.md` 为准
- 新增信源时统一维护到 `sources.md`

## 分类体系

- 💰 DeFi — 去中心化金融、协议、收益
- 🎨 NFT — NFT 项目、市场、艺术品
- 🔗 Layer2 — 扩容方案、Rollup、侧链
- 🛡️ 监管/合规 — 政策法规、监管动态
- 🚀 项目/融资 — 新项目、融资、合作
- 📊 市场/数据 — 价格走势、链上数据、分析

## 配置

可在你的 TOOLS.md 中添加：
```markdown
### AIMPACT Crypto 资讯
- 早报推送：12:00 (Asia/Shanghai)
- 晚报推送：22:00 (Asia/Shanghai)
- 热点推送：18:00 (Asia/Shanghai)
- 推送渠道：已配置渠道
- 内容数量：最多 10 条/次
- 排序规则：按 AI 评分降序
```

## 采集流程

1. **读取配置**：执行前先读取 `sources.md`，确认本次采集数据源清单
2. **调用 API（优先 `curl`，`web_fetch` 兜底）**：按 `sources.md` 配置，优先使用 `curl` 调用 AIMPACT Crypto 数据源 API
   - MetaEra AI 快讯（`curl`，不带分类参数）
   - 从 MetaEra 全量快讯中筛选 Crypto 相关新闻
   - AIMPACT Crypto 新闻（`curl`）
   - 仅当 `curl` 不可用或请求失败时，才使用 `web_fetch` 对同一 URL 兜底重试
3. **提取字段**：从 API 响应提取标题、摘要、链接、发布时间、AI 评分
4. **时间过滤**：根据查询类型过滤时间范围
   - 早报：前一天 00:00 - 当天 12:00
   - 晚报：当天 12:00 - 24:00
   - 热点：最近 24 小时
5. **去重过滤**：基于本次采集结果去重（按标题或 ID）
6. **智能排序**：按 AI 评分降序排序（如 API 提供）
7. **分类标注**：根据内容关键词补充分类标签（DeFi/NFT/Layer2 等）
8. **筛选数量**：选出 Top 10 条
9. **格式化输出**：严格按 `format.md` 格式化生成报告
10. **推送分发**：通过 message 工具推送到指定渠道（可选）

### API 抓取规则（强约束）
- `sources.md` 中所有 URL 均为 API endpoint，必须优先使用 `curl` 获取数据。
- 仅当 `curl` 不可用或请求失败时，才允许使用 `web_fetch` 对同一 URL 兜底重试。
- 仅允许请求 `sources.md` 白名单 URL，禁止改走公开网页搜索替代。
- 失败时需返回 HTTP 状态码与错误摘要，不得直接改走公开网页搜索替代。

## 注意事项
- 建议优先使用 `curl` 调用 API endpoint
- `web_fetch` 仅作为兜底手段（`curl` 不可用或失败时）
- 执行前必须读取 `sources.md`，并严格按其配置进行采集
- 所有内容基于 AI 评分智能排序，优先展示高价值资讯
- 输出格式以 `format.md` 为唯一标准，不得自行变更结构
- 首次使用建议先手动触发，确认输出格式与推送渠道
- 本技能不负责管理任何第三方渠道密钥，也不要求写入本地持久化存储
