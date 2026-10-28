# lava-mcp · 熔岩消息面热度监测

[![Listed on HookMCP](https://hookmcp.com/badge.svg)](https://hookmcp.com)

[熔岩（Lava）](https://lava.ai-dolphin.com/subscribe) 提供 **A 股股票和概念板块的消息面热度监测** 结构化只读数据——支持 **量化交易工具** 与 **AI Agent 股市研究** 接入，通过远程 MCP / REST 调用。

> 只读 · 结构化要点 + 机构/大V ID（`agency_id`）· 新闻命中不含标题与正文

## 新手 3 步

① 开通并复制 API Key（登录熔岩 → 左侧「AI数据服务」→ API Key → 新建；首次登录通常已自动生成「默认」Key）

② 装 Skill，或在豆包办公 / WorkBuddy / 千问办公填 MCP 地址 https://lava.ai-dolphin.com/subscribe/v1/mcp

③ 用中文问「某某股票最近消息面热不热」，或「最近 24 小时全市场哪些股票消息面最热」

## 远程 MCP（推荐）

| 项 | 值 |
| --- | --- |
| 传输 | Streamable HTTP |
| Endpoint | `https://lava.ai-dolphin.com/subscribe/v1/mcp` |
| 鉴权 | 请求头 `Authorization: Bearer <API Key>`（或 `X-API-Key`）；亦支持 OAuth 2.1（PKCE S256 + DCR） |
| 客户端 | 豆包办公、WorkBuddy（BUDDY）、千问办公（QwenWork）等支持自定义 HTTP MCP 的客户端 |

开通与计费见 [落地页](https://lava.ai-dolphin.com/subscribe)：开通赠 100 元代金券；约 1000 次 = 5 元。

## Skill 模板

仓库内 [`SKILL.md`](./SKILL.md) 与线上官方模板对齐（含全市场热榜、加权、首提、多时间窗、加速榜、日频面板、机构覆盖度与新闻点名）。官方模板：

https://lava.ai-dolphin.com/subscribe/v1/skill

## 文档与机器可读规范

- 产品落地页：https://lava.ai-dolphin.com/subscribe
- API 文档（canonical）：https://lava.ai-dolphin.com/subscribe/docs
- OpenAPI 3.0：https://lava.ai-dolphin.com/subscribe/v1/openapi.json
- llms.txt：https://lava.ai-dolphin.com/llms.txt
- MCP Registry：[`server.json`](./server.json)
- Glama：[`glama.json`](./glama.json) · 线上 `/.well-known/glama.json`

## 主要工具（MCP）

| Tool | 用途 |
| --- | --- |
| `get_stock_news_heat` | 个股消息面热度与结构化观点列表 |
| `search_news_flow` | 关键词检索消息面结构化记录 |
| `get_concept_stock_heat` | 概念 → 个股提及排行 |
| `get_stock_concept_heat` | 个股 → 概念提及排行 |
| `get_market_hot_stocks` | 全市场个股热榜；窗口内会附带 heat_chg_1d / heat_chg_3d / heat_z20 |
| `get_market_hot_concepts` | 全市场概念热榜；时间窗最长 `3d` |
| `get_weighted_hot_stocks` | 高分机构/大V加权热榜；默认 `min_score` 1050、`order=weighted` |
| `get_first_mention_stocks` | 首提流：此前 7 天无提及、窗口内第一次被提到的 A 股 |
| `get_stock_heat_windows` | 单股多时间窗热度 + 逐小时 + 来源拆分 |
| `get_accelerating_hot_stocks` | **热度加速榜**：按 heat_chg_1d / heat_chg_3d / heat_z20 动量排序 |
| `get_stock_heat_panel` | **日频历史面板**：日频 mentions / agencies / weighted_heat，适合回测与导出 |
| `get_agency_coverage` | **机构覆盖度**：覆盖机构数时序与 7/30 日去重、新增覆盖（只给计数） |
| `get_news_stock_hits` | 新闻命中个股：`news_id`、发布时间、媒体、命中股票；不含标题与正文 |
| `get_agency_ranking` / `get_agency_pit` / `get_agency_history` / `list_agency_pit_dates` | 机构/大V评分（当前 / PIT / 时序） |
| `get_account` | 余额与用量（不计费） |

参数名与线上 MCP / OpenAPI 一致。机构/大V分大约 450~1500，1000 左右为中等，1050 约前 10%。

### `get_accelerating_hot_stocks`

在全市场热榜候选上计算动量，并按变化降序。字段为纯统计量，便于量化因子与监控。

| 参数 | 说明 |
| --- | --- |
| `window` | `1h` / `4h` / `18h` / `24h` / `3d` / `7d`，默认 `24h` |
| `order` | `chg1d`（默认）/ `chg3d` / `z20` |
| `min_mentions` | 最低提及门槛，默认 3 |
| `market` | `ashare`（默认）/ `all` |
| `limit` | 返回条数，默认 50，最大 200 |

### `get_stock_heat_panel`

按自然日聚合个股或概念的 mentions、agencies、weighted_heat、is_first_mention_day。区间最长 92 天，单次最多 20 个标的。

| 参数 | 说明 |
| --- | --- |
| `type` | `stock`（默认）/ `concept` |
| `stock_name` / `ts_code` / `concept` / `codes` | 标的选择（见 OpenAPI） |
| `days` 或 `start_date`/`end_date` | 回看区间 |

### `get_agency_coverage`

返回每日滚动 7/30 日去重机构/大V数、区间累计新增覆盖、30 日高分占比。只给计数，不返回机构 ID 列表。

| 参数 | 说明 |
| --- | --- |
| `stock_name` 或 `ts_code` | 必填其一 |
| `days` | 时序天数，默认 30，范围 7~90 |
| `min_score` | 可选；高分占比计算用 |

### 其他热榜 / 首提 / 新闻点名

详见线上文档与 OpenAPI：`get_market_hot_stocks`、`get_weighted_hot_stocks`、`get_first_mention_stocks`、`get_stock_heat_windows`、`get_news_stock_hits`。

## 口径说明（对外）

- 全部工具只读；输出为结构化字段与统计量，供量化与 Agent 研究接入
- 机构/大V使用返回的 `agency_id` 指代
- `get_news_stock_hits` 只有 `news_id`、发布时间、媒体来源与命中股票，不含标题与正文
- 勿外推控制台路径（`/subscribe/v1/console` 为 noindex）

## License

本仓库采用 [MIT License](./LICENSE)。

文档与 Skill 模板以站点公开内容为准（线上 SVN **r10407** 口径）；本仓库仅作接入说明与分发入口。
