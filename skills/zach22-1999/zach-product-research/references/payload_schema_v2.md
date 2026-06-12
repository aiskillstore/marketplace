# 统一数据包 Schema v2

`render_deliverables.py` 使用统一 JSON 数据包作为输入。v2 引入 `chapters` 结构，作为唯一事实来源。

## 设计原则

**混合模式**：数据表格由渲染模板从 `chapters` 结构化数据生成（保证一致性），分析洞察由 LLM 在固定"槽位"中自由撰写（保持深度）。

| 内容类型 | 谁负责 | 为什么 |
|---------|--------|--------|
| 章节结构/标题/编号 | 渲染模板固定 | 保证每次都是 10 章，标题一致 |
| 数据表格（KPI、分布、竞品表等） | 渲染模板从 JSON 生成 | 保证数据准确，格式统一 |
| 分析洞察/结论段落 | LLM 自由撰写（不限长度） | 保持分析深度和商业判断质量 |

## 顶层结构

```json
{
  "schema_version": "2.0",
  "metadata": { ... },
  "chapters": { ... },
  "excel_sheets": { ... },
  "artifacts": { ... }
}
```

### 与 v1 的区别

| 字段 | v1 | v2 |
|------|----|----|
| `schema_version` | 不存在 | `"2.0"`（必填） |
| `report_markdown` | LLM 整篇写入 | **不再需要**，由渲染器从 chapters 生成 |
| `report_html` | LLM 整篇写入 | **不再需要**，由渲染器从 chapters 生成 |
| `chapters` | 不存在 | **核心新增**，10 章结构化数据+洞察 |
| `excel_sheets` | 保留 | 保留（不变） |
| `artifacts` | 保留 | 保留（不变） |

**向后兼容**：渲染器检测到 `schema_version != "2.0"` 或存在 `report_markdown` 字段时，走 v1 旧路径。

---

## metadata（不变）

```json
{
  "brand": "string",
  "category": "string",
  "version": "string (v1_YYYYMMDD)",
  "date": "string (YYYYMMDD)",
  "site": "string (US/GB/DE/...)",
  "keyword": "string",
  "created": "string (YYYY-MM-DD HH:MM)",
  "topic": "string",
  "type": "string (选品报告)",
  "data_sources": ["string"]
}
```

---

## chapters（v2 核心）

固定 10 个 key，每个对应一章。LLM 填写每章的结构化数据字段和 `insight` / `findings` / `conclusions` 自由文本字段。

### ch01_executive_summary

```json
{
  "conclusions": [
    {
      "data_point": "Top100月销额 $5.2M，Q4 环比 +180%",
      "meaning": "强季节性礼物驱动型市场",
      "action": "建议 Q3 备货，锚定 11-12 月旺季窗口"
    }
  ],
  "go_nogo_verdict": "CONDITIONAL GO",
  "one_line_summary": "一句话总结市场机会与决策"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `conclusions` | array | ✅ | ≥ 3 条，每条含 data_point / meaning / action |
| `go_nogo_verdict` | string | ✅ | GO / CONDITIONAL GO / HOLD / NO-GO |
| `one_line_summary` | string | ✅ | 一句话总结 |

### ch02_market_overview

```json
{
  "kpis": [
    {
      "name": "Top100月销量",
      "value": "55,497件",
      "source": "category_report",
      "note": "可选补充说明"
    }
  ],
  "keyword_comparison": [
    {
      "keyword": "karaoke machine",
      "search_volume_rank": 1234,
      "search_volume_change": "+15%",
      "top3_asin": ["B0xxx", "B0yyy", "B0zzz"],
      "segment": "品类大词"
    }
  ],
  "insight": "这个市场呈现典型的「礼物驱动+强季节性」特征..."
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `kpis` | array | ✅ | ≥ 5 个 KPI 指标 |
| `keyword_comparison` | array | ✅ | 关键词多维度对比 |
| `insight` | string (Markdown) | ✅ | LLM 自由撰写的市场特征解读，不限长度 |

### ch03_dimension_distribution

```json
{
  "dimensions": [
    {
      "name": "价格带",
      "distribution": [
        {
          "value": "$20-30",
          "product_count": 25,
          "product_share": "25%",
          "monthly_sales": 12000,
          "sales_share": "22%",
          "monthly_revenue": 300000,
          "avg_price": 25.5
        }
      ],
      "insight": "20-30 美元是主力价格带，但 50+ 美元段虽然只有 8% 的产品..."
    }
  ]
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `dimensions` | array | ✅ | ≥ 2 个维度 |
| `dimensions[].name` | string | ✅ | 维度名称 |
| `dimensions[].distribution` | array | ✅ | 分布数据行 |
| `dimensions[].insight` | string (Markdown) | ✅ | 该维度的关键洞察 |

### ch04_cross_analysis

```json
{
  "matrices": [
    {
      "dim1": "价格带",
      "dim2": "功率",
      "data": [
        {
          "dim1_value": "$20-30",
          "dim2_value": "65W",
          "count": 3,
          "sales": 1500,
          "revenue": 45000
        }
      ],
      "gaps": [
        {
          "dim1_value": "$30-40",
          "dim2_value": "100W",
          "count": 0,
          "reason": "供给空白：技术可行但被忽视"
        }
      ],
      "findings": "65W + $20-30 是主力组合，但 100W + $30-40 存在明显空白..."
    }
  ]
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `matrices` | array | ✅ | ≥ 1 对交叉分析 |
| `matrices[].data` | array | ✅ | 交叉矩阵数据 |
| `matrices[].gaps` | array | ✅ | 供需缺口（可为空数组） |
| `matrices[].findings` | string (Markdown) | ✅ | 关键发现 |

### ch05_competitor_brands

```json
{
  "competitor_selection_logic": [
    {
      "asin": "B0XXXXX",
      "brand": "BrandA",
      "reason": "品类 Top1，覆盖 65W+数显 主力组合",
      "type": "标杆型",
      "covered_dimensions": "功率/数显/线材",
      "price": 29.99,
      "monthly_sales": 5000,
      "reviews": 1200
    }
  ],
  "brand_landscape": [
    {
      "brand": "BrandA",
      "market_share": "18%",
      "product_count": 12,
      "avg_price": 35.5,
      "strategy": "高功率+性价比打法",
      "role": "品类领导者",
      "implication_for_us": "不正面竞争，从差异化细分切入"
    }
  ],
  "insight": "市场品牌集中度中等（CR3=35%），头部品牌以性价比为主..."
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `competitor_selection_logic` | array | ✅ | 竞品选择逻辑表 |
| `competitor_selection_logic[].price` | number | 推荐 | 竞品价格（从 product_detail 获取） |
| `competitor_selection_logic[].monthly_sales` | number | 推荐 | 竞品月销量 |
| `competitor_selection_logic[].reviews` | number | 推荐 | 竞品评论数 |
| `brand_landscape` | array | ✅ | 品牌格局分析 |
| `insight` | string (Markdown) | ✅ | 品牌竞争格局洞察 |

### ch06_voc_pain_points

```json
{
  "by_dimension": [
    {
      "dimension": "电池/续航",
      "pain_points": [
        {
          "description": "电池容量虚标，实际续航不足标称 50%",
          "frequency": 45,
          "share": "32%",
          "related_competitors": ["B0xxx (BrandA)", "B0yyy (BrandB)"]
        }
      ],
      "support_data": "涉及 45 条差评，主要集中在 $20 以下产品",
      "opportunity": "使用高密度电芯+实测续航标注，切中核心痛点",
      "solution": "4000mAh 实标电池 + 包装标注实测续航时长"
    }
  ]
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `by_dimension` | array | ✅ | 按维度归类的痛点 |
| `by_dimension[].pain_points` | array | ✅ | 痛点列表 |
| `by_dimension[].opportunity` | string | ✅ | 品牌机会 |
| `by_dimension[].solution` | string | ✅ | 产品方案 |

### ch07_opportunity_gaps

```json
{
  "opportunities": [
    {
      "rank": 1,
      "description": "65W + 数显 + $25-35 价格带，仅 3 个竞品",
      "market_size_score": 8,
      "feasibility_score": 7,
      "brand_fit_score": 9,
      "weighted_score": 8.1,
      "source": "交叉分析 ch04 + 痛点 ch06",
      "action": "优先进入，Tier 1 产品锚定此组合"
    }
  ],
  "scoring_method": "市场规模 40% + 技术可行性 30% + 品牌匹配 30%",
  "insight": "最高优先级机会集中在高功率+中价位段..."
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `opportunities` | array | ✅ | ≥ 1 个机会 |
| `opportunities[].weighted_score` | number | ✅ | 加权评分 |
| `scoring_method` | string | ✅ | 评分方法说明 |
| `insight` | string (Markdown) | ✅ | 机会分析洞察 |

### ch08_strategic_recommendations

```json
{
  "tiers": [
    {
      "tier": "Tier 1",
      "name": "主力冲锋款",
      "specs": {
        "功率": "65W",
        "容量": "10000mAh",
        "数显": "有",
        "线材": "Type-C 内置"
      },
      "target_price": "$29.99",
      "differentiation": "同价位唯一 65W+数显组合",
      "benchmark_asin": "B0XXXXX",
      "benchmark_advantage": "数显+内置线 vs 竞品无数显",
      "estimated_monthly_sales": "800-1200 件",
      "decision_rationale": "基于 ch04 交叉分析空白 + ch06 续航痛点"
    }
  ],
  "procurement_reference": [
    {
      "label": "基础款（10000mAh/22.5W）",
      "min": 3.5,
      "median": 5.0,
      "max": 7.0
    }
  ],
  "brand_strategy": "定位科技实用派，视觉风格简洁+数据可视化...",
  "timeline": "Tier 1 优先 Q3 上架，Tier 2 验证后 Q4 跟进..."
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `tiers` | array | ✅ | ≥ 1 个 Tier 完整规格 |
| `tiers[].specs` | object | ✅ | 维度规格键值对 |
| `tiers[].target_price` | string | ✅ | 目标定价 |
| `tiers[].differentiation` | string | ✅ | 差异化主张 |
| `procurement_reference` | array | 推荐 | 1688 采购价参考，每项含 label/min/median/max |
| `brand_strategy` | string | ✅ | 统一品牌策略 |
| `timeline` | string | ✅ | 时间线建议 |

### ch09_barriers_go_nogo

```json
{
  "barriers": [
    {
      "type": "Review 壁垒",
      "level": "中",
      "detail": "Top10 均值 2,500+ 评论，但新品通过 Vine 可快速积累",
      "mitigation": "Vine + 早期 PPC 引流策略"
    }
  ],
  "go_nogo_scorecard": [
    {
      "dimension": "市场容量",
      "weight": 25,
      "score": 8,
      "weighted_score": 2.0,
      "rationale": "月销额 $5.2M，增长稳定"
    }
  ],
  "total_score": 7.2,
  "verdict": "CONDITIONAL GO",
  "verdict_detail": "市场容量和机会空间评分高，但 Review 壁垒和季节性风险需关注",
  "risks": [
    {
      "risk": "Q1-Q2 淡季月销量可能下降 60%",
      "probability": "高",
      "impact": "中",
      "mitigation": "控制首批 MOQ，淡季转广告投放积累评论"
    }
  ]
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `barriers` | array | ✅ | 6 类壁垒评估 |
| `go_nogo_scorecard` | array | ✅ | 5 维度评分卡 |
| `total_score` | number | ✅ | 总分 |
| `verdict` | string | ✅ | GO / CONDITIONAL GO / HOLD / NO-GO |
| `risks` | array | ✅ | 风险列表 |

### ch10_appendix

```json
{
  "tool_calls": [
    {
      "tool": "category_report",
      "params": "amzSite=US, nodeId=xxx",
      "date": "2026-03-15",
      "purpose": "获取 Top100 产品数据"
    }
  ],
  "data_date": "2026-03-15",
  "data_freshness_note": "数据有效期建议 30 天内",
  "files": [
    {
      "filename": "20260315_US_karaoke_市场调研报告_v1_20260315.md",
      "type": "Markdown 正式报告",
      "description": "完整分析报告"
    }
  ]
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `tool_calls` | array | ✅ | MCP 工具调用清单 |
| `data_date` | string | ✅ | 数据获取日期 |
| `files` | array | ✅ | 完整文件清单 |

---

## excel_sheets（不变）

与 v1 完全兼容。第一个 key 必须是 `数据来源说明`。

必选 Sheet（11 个）：
- `数据来源说明`（首 Sheet）
- `市场概况`
- `类目销量Top100_明细`
- `关键词对比_分段`
- `新品分析`
- `竞品选择逻辑`
- `竞品差评摘要`
- `品牌_竞品格局`
- `属性标注_Top100`
- `进入壁垒评估`
- `Go-NoGo评分卡`

## artifacts（不变）

至少保留 `top100_raw.json`。推荐包含 `cross_analysis.json`、`voc_analysis.json`、`top100_parsed.json`。

---

## 校验规则（render_deliverables.py validate）

v2 payload 必须通过以下检查：

1. `schema_version == "2.0"`
2. `chapters` 包含全部 10 个 key（ch01 ~ ch10）
3. `ch01_executive_summary.conclusions` 长度 ≥ 3
4. `ch02_market_overview.kpis` 长度 ≥ 5
5. `ch03_dimension_distribution.dimensions` 长度 ≥ 2
6. 每章的必填 `insight` / `findings` / `conclusions` 字段非空
7. `ch09_barriers_go_nogo.verdict` 为合法值
8. `excel_sheets` 包含 11 个必选 Sheet
9. `metadata` 包含全部 9 个必填字段
