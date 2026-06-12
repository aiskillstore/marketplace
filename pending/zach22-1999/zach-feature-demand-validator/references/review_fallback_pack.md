# Review Fallback Pack 规范

当 Sorftime MCP 不可用时，Review 维度改用本地 `review_source_pack`。

## 目录结构

```text
review_source_pack/
├── source_manifest.json
└── raw/
    ├── reviews.csv
    ├── reviews.txt
    └── reviews.html
```

## `source_manifest.json` 最小字段

```json
{
  "asin": "B0XXXXXXX",
  "site": "US",
  "product_title": "Air Fryer with Steam Feature",
  "captured_at": "2026-03-19 14:30:00",
  "source_url": "https://www.amazon.com/product-reviews/B0XXXXXXX",
  "export_method": "manual_export_csv",
  "raw_files": ["reviews.csv"]
}
```

### 字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| `asin` | 是 | 对应产品 ASIN |
| `site` | 是 | 站点，如 `US` |
| `product_title` | 否 | 产品标题 |
| `captured_at` | 是 | 导出时间 |
| `source_url` | 是 | Amazon 评论页 URL |
| `export_method` | 是 | `manual_export_csv` / `manual_export_html` / `manual_export_txt` |
| `raw_files` | 否 | 原始文件列表，不填则默认扫描 `raw/` 目录 |

## 支持的原始文件格式

### 1. CSV

支持常见列名变体，以下列至少要能映射出正文和星级：

- `title` / `review_title` / `标题`
- `body` / `review_body` / `评论`
- `rating` / `stars` / `评星`
- `date` / `review_date` / `评论日期`

### 2. TXT / Markdown

推荐格式：

```text
title: Great idea but not enough steam
rating: 3
date: 2026-01-12
body: I wish it had a stronger steam mode for reheating leftovers.

---

title: Nice feature
rating: 5
date: 2026-01-09
body: Steam helps food stay moist.
```

### 3. HTML

适合保存 Amazon 评论页源码后直接解析。脚本会优先识别：

- `data-hook="review"`
- `data-hook="review-title"`
- `data-hook="review-body"`
- `data-hook="review-date"`
- `data-hook="review-star-rating"`

## 推荐工作流

1. 保存原始评论文件到 `raw/`
2. 填好 `source_manifest.json`
3. 运行：

macOS / Linux:
```bash
python3 skills/zach-feature-demand-validator/scripts/parse_review_source_pack.py \
  --pack ./review_source_pack \
  --keywords "steam,steamer,steaming" \
  --output ./01_review_信号_原始数据.csv
```

Windows:
```powershell
py -3 skills/zach-feature-demand-validator/scripts/parse_review_source_pack.py `
  --pack .\review_source_pack `
  --keywords "steam,steamer,steaming" `
  --output .\01_review_信号_原始数据.csv
```

## 数据诚信要求

1. 原始文件必须保留，不允许只保留二次整理结果
2. `source_url` 必须可回溯到具体 Amazon 评论页
3. 如果文本是人工复制出来的，`export_method` 要明确写 `manual_export_txt`
4. fallback 只解决 Review 维度，不代表整个需求验证已经完整
