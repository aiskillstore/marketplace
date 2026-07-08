---
name: tavily-search-free
description: Web search, online search, real-time search, internet search, Google alternative, Bing alternative, DuckDuckGo alternative, search the web, lookup online, find information, research,查询,搜索,搜索结果,网页搜索,联网搜索,实时搜索,网络查询,资料查找,信息检索,最新资讯,新闻搜索, Tavily Search API for optimized, real-time web search results for RAG. A pre-configured, cost-effective search tool.
---

# Tavily Search Skill (MCP-based)

This skill utilizes the Tavily MCP server, providing clean, real-time web search results optimized for LLMs and RAG pipelines.

## 执行环境

| 路径类型 | 路径 | 基准目录 |
|---------|------|---------|
| **技能目录** | `~/.pi/agent/skills/tavily-search-free/` | 固定位置 |
| **主脚本** | `~/.pi/agent/skills/tavily-search-free/executor.py` | 技能目录 |
| **使用方式** | `pi` 自动调用或手动执行 | 无需手动执行 |

## API Key 配置

支持多 Key 轮询，提高请求并发能力。

**配置方式**：在 `.env` 文件中用逗号分隔多个 Key：
```
TAVILY_API_KEY=key1,key2,key3
```

**查看 Key 状态**：
```bash
uv run executor.py --key-status
```

## 可用工具

| 工具 | 描述 |
|------|------|
| `tavily_search` | 网络搜索（新闻、事实、数据） |
| `tavily_extract` | 从 URL 提取内容（markdown/text） |
| `tavily_crawl` | 爬取网站（可配置深度） |
| `tavily_map` | 映射网站结构 |
| `tavily_research` | 综合研究（多来源） |

## 使用方式

### 方式 1：通过 pi 自动调用（推荐）

`pi` 会自动调用此技能进行网络搜索，无需手动执行命令。

### 方式 2：手动执行

```bash
# 从技能目录执行
cd ~/.pi/agent/skills/tavily-search-free

# 列出所有工具
uv run executor.py --list

# 搜索
uv run executor.py --call '{"tool": "tavily_search", "arguments": {"query": "搜索内容"}}'

# 提取 URL 内容
uv run executor.py --call '{"tool": "tavily_extract", "arguments": {"urls": ["https://example.com"]}}'

# 爬取网站
uv run executor.py --call '{"tool": "tavily_crawl", "arguments": {"url": "https://example.com", "max_depth": 2}}'

# 映射网站
uv run executor.py --call '{"tool": "tavily_map", "arguments": {"url": "https://example.com"}}'

# 综合研究
uv run executor.py --call '{"tool": "tavily_research", "arguments": {"input": "研究主题"}}'
```

## 参数说明

### tavily_search
| 参数 | 必填 | 默认值 | 说明 |
|-----|------|--------|------|
| `query` | 是 | - | 搜索查询内容 |
| `max_results` | 否 | 5 | 最大返回结果数量 |
| `search_depth` | 否 | basic | 搜索深度：`basic`/`advanced`/`fast`/`ultra-fast` |
| `time_range` | 否 | null | 时间范围：`day`/`week`/`month`/`year` |

### tavily_extract
| 参数 | 必填 | 默认值 | 说明 |
|-----|------|--------|------|
| `urls` | 是 | - | URL 列表 |
| `extract_depth` | 否 | basic | 提取深度：`basic`/`advanced` |
| `format` | 否 | markdown | 输出格式：`markdown`/`text` |

## 输出格式

脚本输出 JSON 格式，包含搜索结果或提取内容。

## 监控与统计

```bash
# 查看状态
uv run executor.py --status

# 查看统计
uv run executor.py --stats

# 查看日志
uv run executor.py --logs 100
```

## 路径说明

- **脚本位置**：`~/.pi/agent/skills/tavily-search-free/executor.py`
- **配置位置**：`~/.pi/agent/skills/tavily-search-free/mcp-config.json`
- **环境变量**：`~/.pi/agent/skills/tavily-search-free/.env`
- **依赖安装**：使用 `uv sync` 自动管理

---

*基于 Tavily MCP 服务器，支持 5 个工具，渐进式加载节省上下文*
