# 统一学术搜索 MCP 服务器

这是统一的学术搜索 MCP 服务器，整合 CrossRef、PubMed、arXiv、Scopus 和 ScienceDirect 数据源。

## 工具

| 工具 | 功能 |
|------|------|
| `search_papers` | 统一搜索，支持多数据源并发 |
| `get_paper_by_id` | 按 DOI、PMID 或 arXiv ID 获取详情 |
| `get_citation` | 格式化引用，支持 APA、Nature、IEEE 等风格 |
| `lookup_mesh` | MeSH 词表查询 |
| `search_scopus` | Scopus 高级检索 |
| `get_scopus_abstract` | Scopus 摘要与详情元数据 |
| `get_scopus_citation_overview` | Scopus 引用概览 |
| `search_scopus_authors` / `get_scopus_author` | 作者检索与详情 |
| `search_scopus_affiliations` / `get_scopus_affiliation` | 机构检索与详情 |
| `search_scopus_serial_titles` / `get_scopus_serial_title` | 期刊与连续出版物检索和详情 |
| `get_scopus_plumx_metrics` | PlumX 指标 |
| `search_sciencedirect` | ScienceDirect 检索 |
| `get_sciencedirect_article_metadata` | ScienceDirect 文章元数据 |

## 配置

环境变量：

- `PUBMED_EMAIL`：必填，NCBI 要求。
- `NCBI_API_KEY`：可选，用于提升速率限制。
- Elsevier / Scopus / ScienceDirect：复用 `pybliometrics` 配置文件，默认位置为 `~/.config/pybliometrics.cfg`。

`search_papers` 默认检索 CrossRef、PubMed 和 arXiv。Scopus / ScienceDirect 是可选 provider：只有在 `sources` 显式传入 `scopus` / `sciencedirect`，或调用专用 Scopus / ScienceDirect 工具时，才会访问 Elsevier API。

这样可以避免默认搜索无意消耗 Elsevier API 配额；若本机缺少 `pybliometrics` 配置，会在返回 JSON 的 `errors` 字段中给出对应数据源错误。

配置文件：`config.toml`

## 使用

插件会通过以下形式启动隔离运行环境：

```bash
uv run --no-project --directory <mcp-server> --with ... python academic_search_server.py
```

这些工具由 `academic-search` skill 调用。
