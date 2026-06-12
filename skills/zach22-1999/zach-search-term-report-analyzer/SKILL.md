---
name: zach-search-term-report-analyzer
description: |
  分析 Amazon Ads search term report（SP / SB / SD），识别候选 ASIN、报告类型、低效词、放量词、属性词、场景词和趋势变化。
  使用时机：用户上传广告搜索词报告，想判断哪些 search term 应该观察、控 bid、否定候选、继续放量，或想把搜索词里的用户需求反馈到 Listing 与投放策略时调用。
  触发词：/zach-search-term-report-analyzer
benefits-from: []
user-invocable: true
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep]
risk-level: medium
---

## 前置建议

本公开版 Skill 是自包含的，不依赖私有工作区文件、内部知识库、店铺配置或团队数据源。

开始执行前，建议先读取本 Skill 自带材料：

- `references/field_mapping.md` — SP / SB / SD 字段映射
- `references/decision_rules.md` — 搜索词决策规则
- `references/term_classification.md` — 品牌词、竞品词、属性词、场景词分类口径
- `references/output_template.md` — 报告与 CSV 输出模板
- `scripts/clean_search_term_report.py` — 原始报表清洗与标准化脚本
- `scripts/analyze_search_term_decisions.py` — 单 ASIN 决策分析脚本
- `scripts/fetch_listing_context.py` — 可选的 Amazon 前台 Listing 上下文抓取脚本

## 定位

广告搜索词报告不只用来找否词。它同时承担三件事：

1. 找出持续消耗预算但转化弱的词
2. 找出 CVR、ACOS 或趋势表现更好的放量候选
3. 从用户真实搜索语言里提炼属性词、场景词和 Listing 反馈线索

本 Skill 输出的是分析建议和行动候选，不会替用户直接修改广告、预算、出价或否词设置。

## 输入参数

| 参数 | 必须 | 默认值 | 说明 |
|------|------|--------|------|
| 搜索词报告文件 | 是 | - | CSV / XLSX / XLSM / XLS，优先使用 Amazon Ads 官方导出文件 |
| 品牌 | 否 | 报表字段或文件名识别 | 也可用 `--brand` 显式指定 |
| ASIN | 否 | 自动识别单一候选 | 多个候选时必须让用户选择一个 |
| 站点 | 否 | `US` | 用于可选 Listing 抓取 |
| 报告类型 | 否 | 自动识别 | SP / SB / SD；识别失败时标记 `UNKNOWN` |
| 目标 ACOS | 否 | 报表自身基准 | 用 `--target-acos 0.20` 显式传入更稳 |
| Listing 上下文 | 否 | 默认尝试 live fetch | 可用 `--listing-context-file` 提供本地标题/卖点文本 |

## 执行流程

### Step 1: 识别输入文件与分析对象

1. 读取用户上传或指定的搜索词报告。
2. 运行清洗脚本识别字段、报告类型、品牌候选和 ASIN 候选：

```bash
python3 skills/zach-search-term-report-analyzer/scripts/clean_search_term_report.py <input_file>
```

3. 如果识别到多个 ASIN，先列候选给用户选择，不要混合分析。
4. 如果品牌无法识别，允许用户用 `--brand` 显式传入；品牌只用于分组、文件命名和品牌词识别。

### Step 2: 标准化字段

按 `references/field_mapping.md` 将原始字段统一为内部字段：

- `date`
- `brand`
- `asin`
- `campaign_name`
- `ad_group_name`
- `targeting`
- `match_type`
- `search_term`
- `impressions`
- `clicks`
- `spend`
- `orders`
- `sales`
- `cvr`
- `acos`
- `roas`

缺失字段按“有就用，没有就跳过”处理；但核心字段 `date + search_term + clicks + spend` 缺失时必须停止。

### Step 3: 建立 ASIN 基准与时间窗

1. 默认以单个 ASIN 为分析单位。
2. 建立该 ASIN 近 30 天广告 CVR 基准：`orders / clicks`。
3. 分别聚合 7 / 14 / 30 天窗口的点击、花费、订单、CVR、ACOS 和趋势变化。
4. 如果用户提供 `--target-acos`，用它判断成本压力；否则使用该 ASIN 报表自身 ACOS 作参考。

### Step 4: 抓取或读取 Listing 上下文

默认行为：脚本会尝试按 ASIN 和站点访问 Amazon 前台页面，提取 title / bullets / description / breadcrumb。

稳定测试或网络受限时使用：

```bash
--skip-live-listing-fetch
--listing-context-file skills/zach-search-term-report-analyzer/examples/listing-context-sample.md
```

Listing 上下文只用于增强“相关词、属性词、场景词、弱相关词”的判断；抓取失败不能阻断基础广告分析。

### Step 5: 做搜索词决策分析

读取 `references/decision_rules.md` 和 `references/term_classification.md`，为每个 search term 输出：

- 主分类：`brand_term` / `competitor_term` / `asin_term` / `core_category_term` / `attribute_term` / `scenario_term` / `irrelevant_term` / `uncertain_term`
- 动作标签：`scale_up` / `hold_test` / `reduce_bid` / `negative_candidate` / `observe` / `listing_feedback` / `manual_review`
- 置信度：`high` / `medium` / `low`
- 解释：说明点击、花费、CVR、ACOS、趋势和 Listing 相关性如何共同支持该判断

### Step 6: 输出报告与明细

默认输出到：

```text
outputs/search-term-report-analyzer/{brand_or_unknown}/
```

脚本命令示例：

```bash
python3 skills/zach-search-term-report-analyzer/scripts/analyze_search_term_decisions.py \
  <input_file> \
  --brand ExampleBrand \
  --asin B0PUBLIC01 \
  --target-acos 0.20 \
  --listing-context-file skills/zach-search-term-report-analyzer/examples/listing-context-sample.md \
  --skip-live-listing-fetch
```

## 输出文件清单

| 文件 | 格式 | 路径 |
|------|------|------|
| 主报告 | `.md` | `outputs/search-term-report-analyzer/{brand}/{YYYY-MM-DD}_{brand}_{asin}_7-14-30天_搜索词报告分析.md` |
| 明细表 | `.csv` | `outputs/search-term-report-analyzer/{brand}/{YYYY-MM-DD}_{brand}_{asin}_7-14-30天_搜索词分析明细.csv` |
| 异常清单 | `.csv` | `outputs/search-term-report-analyzer/{brand}/{YYYY-MM-DD}_{brand}_{asin}_7-14-30天_异常清单.csv` |
| 运行摘要 | `.json` | `outputs/search-term-report-analyzer/{brand}/{YYYY-MM-DD}_{brand}_{asin}_7-14-30天_run_summary.json` |

## 风险与边界

- **本 Skill 不做**：
  - 不直接修改广告出价、预算、否词或广告结构
  - 不上传用户报表、不沉淀真实销售数据
  - 不依赖私有店铺配置或内部知识库
  - 字段不足时不强行给出 CVR / ACOS 结论
- **需要人工复核**：
  - 多个 ASIN 混在同一份报告里
  - 品牌词、竞品词或 ASIN 型搜索词策略不明确
  - Listing 抓取失败且词义相关性高度依赖产品卖点
  - 点击量低、花费低或 7 / 14 / 30 天信号互相冲突
- **risk-level = medium**：
  - 本 Skill 会给出广告动作建议，但任何出价、预算、否词执行都需要用户确认后手动完成。

## 上游 / 下游

- **上游**：
  - 用户提供的 Amazon Ads search term report
  - 可选 Listing 上下文文件
- **下游**：
  - 人工广告操作：复核否词候选、控 bid 候选、放量候选
  - Listing 优化：把属性词、场景词、需求词反馈到标题、卖点、A+ 或素材

## 完成后

报告完成状态：

- **DONE** — 报告、明细、异常清单和摘要均已生成
- **DONE_WITH_CONCERNS** — 已生成，但存在需人工复核的高影响项
- **BLOCKED** — 核心字段缺失、文件不可读或 ASIN 无法确定
- **NEEDS_CONTEXT** — 需要用户补充品牌、ASIN、站点、目标 ACOS 或 Listing 上下文

告知用户：

1. 分析对象：品牌、ASIN、站点、报告类型
2. 结果摘要：否词候选、控成本候选、放量候选、Listing 反馈词数量
3. 文件路径：主报告、明细表、异常清单和运行摘要
