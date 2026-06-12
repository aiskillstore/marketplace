# CSV Schema — 功能需求验证的标准数据文件

## 目录结构

```text
YYYY-MM-DD_[品类slug]_[功能slug]_数据源/
├── 01_review_信号_原始数据.csv
├── 02_keyword_信号_搜索量数据.csv
├── 03_keyword_信号_趋势数据.csv
├── 04_keyword_信号_延伸词.csv
├── 05_社区_信号_讨论摘要.csv
└── review_source_pack/              # 仅 Review fallback 场景需要
    ├── source_manifest.json
    └── raw/
```

## 全 CSV 通用要求

所有 CSV 都必须使用 UTF-8，并保留以下核查字段：

| 列名 | 说明 |
|------|------|
| `数据来源` | 具体工具或证据包名称，如 `mcp_sorftime_product_reviews`、`web_search`、`amazon_review_source_pack` |
| `来源类型` | 来源类别，如 `sorftime_mcp`、`public_web_search`、`manual_export_csv` |
| `来源链接/查询词` | 来源 URL、Query，或内部调用标识 |
| `原始文件名` | JSON / CSV / HTML / TXT 的原始文件名 |
| `采集时间` | `YYYY-MM-DD HH:MM:SS` |

---

## CSV 01：Review 信号原始数据

来源：

- Sorftime `product_reviews` + `scripts/parse_reviews.py`
- 或本地 `review_source_pack` + `scripts/parse_review_source_pack.py`

| 列名 | 说明 |
|------|------|
| `ASIN` | 产品 ASIN |
| `评论日期` | 原始评论日期，保留原始格式 |
| `星级` | 1.0 - 5.0 |
| `评论内容` | 标题 + 正文，截断到 300 字符 |
| `功能相关(Y/N)` | 是否与目标功能有关 |
| `情感(正/负/中)` | 按星级粗分：≥4 正，3 中，≤2 负 |
| `功能直接提及` | 是否直接提到功能关键词 |
| `水分/干燥提及` | 是否命中辅助场景词 |
| `需求信号` | 是否命中 `wish it had` 等表达 |
| `数据来源` | `mcp_sorftime_product_reviews` 或 `amazon_review_source_pack` |
| `来源类型` | `sorftime_mcp`、`manual_export_csv`、`manual_export_html`、`manual_export_txt` 等 |
| `来源链接/查询词` | Sorftime 调用标识或 Amazon 评论页 URL |
| `原始文件名` | `reviews.json` / `reviews.csv` / `reviews.html` 等 |
| `采集时间` | 评论包导出或抓取时间 |

---

## CSV 02：关键词搜索量数据

来源：`scripts/generate_keyword_csv.py --type detail`

| 列名 | 说明 |
|------|------|
| `关键词` | 查询词 |
| `周搜索量` | 周搜索量，或 `N/A(未验证)` |
| `搜索排名` | 搜索排名，或 `N/A` |
| `变化率` | 变化情况 |
| `CPC` | CPC |
| `数据来源` | 一般为 `mcp_sorftime_keyword_detail` |
| `来源类型` | 一般为 `sorftime_mcp`；无 Sorftime 时可标 `data_gap_placeholder` |
| `来源链接/查询词` | 如 `keyword_detail:steam air fryer` |
| `原始文件名` | 原始 JSON 名称 |
| `采集时间` | 采集时间 |

---

## CSV 03：关键词趋势数据

来源：`scripts/generate_keyword_csv.py --type trend`

| 列名 | 说明 |
|------|------|
| `关键词` | 查询词 |
| `日期` | 原始时间点 |
| `月搜索量` | 月搜索量，或 `N/A(未验证)` |
| `搜索排名` | 搜索排名 |
| `趋势方向` | 上升 / 平稳 / 下降 / 波动 / 数据缺口 |
| `数据来源` | 一般为 `mcp_sorftime_keyword_trend` |
| `来源类型` | 一般为 `sorftime_mcp` |
| `来源链接/查询词` | 如 `keyword_trend:steam air fryer` |
| `原始文件名` | 原始 JSON 名称 |
| `采集时间` | 采集时间 |

---

## CSV 04：关键词延伸词

来源：`scripts/generate_keyword_csv.py --type extends`

| 列名 | 说明 |
|------|------|
| `延伸词` | 延伸词 |
| `周搜索量` | 周搜索量，或 `N/A(未验证)` |
| `搜索排名` | 搜索排名 |
| `关联度(高/中/低)` | 与目标功能的相关度 |
| `数据来源` | 一般为 `mcp_sorftime_keyword_extends` |
| `来源类型` | 一般为 `sorftime_mcp` |
| `来源链接/查询词` | 如 `keyword_extends:steam air fryer` |
| `原始文件名` | 原始 JSON 名称 |
| `采集时间` | 采集时间 |

---

## CSV 05：社区讨论摘要

来源：`scripts/generate_community_csv.py`

| 列名 | 说明 |
|------|------|
| `来源(Reddit/Quora)` | 讨论来源 |
| `帖子标题` | 帖子或问题标题 |
| `URL` | 原始链接 |
| `发布日期` | 原始发布时间 |
| `讨论热度` | 高 / 中 / 低 / 无结果 |
| `用户态度摘要` | 期待 / 推荐 / 质疑 / 吐槽 |
| `WebSearch查询词` | 具体搜索词 |
| `数据来源` | `web_search` |
| `来源类型` | `public_web_search` |
| `来源链接/查询词` | 通常与 `WebSearch查询词` 一致，必要时可写 URL |
| `原始文件名` | 社区原始 JSON 文件名 |
| `采集时间` | 采集时间 |

---

## Review fallback 额外要求

如果 `01_review_信号_原始数据.csv` 中的 `来源类型` 含有 `manual` 或 `amazon`，则交付目录必须额外包含：

- `review_source_pack/source_manifest.json`
- `review_source_pack/raw/` 下至少 1 个原始文件

`source_manifest.json` 必须包含：

- `asin`
- `site`
- `captured_at`
- `source_url`
- `export_method`
