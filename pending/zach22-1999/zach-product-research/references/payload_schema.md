# 统一数据包 Schema

`render_deliverables.py` 使用统一 JSON 数据包作为输入。

## 最小结构

```json
{
  "metadata": {
    "brand": "AORYVIC",
    "category": "wood-furniture-legs",
    "version": "v1_20260311",
    "date": "20260311",
    "site": "US",
    "keyword": "wood-furniture-legs",
    "created": "2026-03-11 16:35",
    "topic": "AORYVIC Wood Furniture Legs Sofa Legs",
    "type": "选品报告",
    "data_sources": [
      "sorftime MCP: category_report",
      "sorftime MCP: keyword_detail"
    ]
  },
  "report_markdown": "# 正式报告正文",
  "report_html": "<!doctype html>...</html>",
  "excel_sheets": {
    "数据来源说明": [],
    "市场概况": []
  },
  "artifacts": {
    "top100_raw.json": [],
    "cross_analysis.json": {}
  }
}
```

## 强制规则

- `metadata` 不可缺
- `data_sources` 必须是非空数组
- `excel_sheets` 第一个 key 必须是 `数据来源说明`
- 输出目录由 metadata 计算，不允许 payload 中自定义任意路径

## 必选扩展

- `excel_sheets` 必须包含 `关键词对比_分段`、`新品分析`、`竞品选择逻辑`、`竞品差评摘要`
- `excel_sheets` 必须包含 `品牌_竞品格局`、`进入壁垒评估`、`Go-NoGo评分卡`
- `artifacts` 至少保留 `top100_raw.json` 与一个分析类 JSON

## 推荐扩展

- `excel_sheets` 可按实际调用补充 `1688参考`
- `artifacts` 可追加 `voc_analysis.json`、`keyword_details.json`、`new_product_analysis.json`
