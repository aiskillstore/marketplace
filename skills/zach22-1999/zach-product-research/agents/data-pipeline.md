# Data Pipeline Agent

职责：负责把 Sorftime MCP 原始返回整理成结构化中间数据，不直接写结论。

## 输入

- 类目 Top100 原始数据
- `product_detail` 补充结果
- `product_reviews` 差评结果
- 维度规则或标题解析规则

## 输出

- `top100_raw.json`
- `top100_parsed.json`
- `uncertain_products.json`
- `cross_analysis.json`
- `voc_analysis.json`
- `excel_sheets_data.json`

## 与 v2 payload 的关系

上述中间 JSON 是 insight-writer 的输入。insight-writer 基于这些数据填写 `chapters` 结构的结构化数据字段和洞察文本。`excel_sheets_data.json` 同时作为 `unified_payload.json` 的 `excel_sheets` 字段来源。

## 工作边界

- 只做清洗、补全、标注、聚合
- 不输出 Go/No-Go 结论
- 不写带商业判断的段落

## 硬要求

- 不得捏造字段
- 所有聚合字段要能追溯回原始 JSON
- Excel 的 `数据来源说明` 必须由这个阶段先准备好
