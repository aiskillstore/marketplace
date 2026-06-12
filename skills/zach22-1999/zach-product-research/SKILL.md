---
name: zach-product-research
description: |
  基于Sorftime MCP的选品分析，发现高潜力市场机会、多维度属性标注与交叉分析、验证竞争格局、测算投入产出、输出Go/No-Go决策与选品报告。
  使用时机：选品立项前的市场调研。新品上架工作流第一步。
  触发词：/zach-product-research
benefits-from: []
user-invocable: true
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep, mcp__sorftime__category_search_from_product_name, mcp__sorftime__category_search_from_top_node, mcp__sorftime__search_categories_broadly, mcp__sorftime__category_name_search, mcp__sorftime__category_report, mcp__sorftime__category_report_from_history, mcp__sorftime__category_trend, mcp__sorftime__category_keywords, mcp__sorftime__keyword_search_results, mcp__sorftime__keyword_detail, mcp__sorftime__keyword_extends, mcp__sorftime__keyword_trend, mcp__sorftime__product_search, mcp__sorftime__product_detail, mcp__sorftime__product_trend, mcp__sorftime__product_reviews, mcp__sorftime__product_traffic_terms, mcp__sorftime__product_variations, mcp__sorftime__potential_product, mcp__sorftime__competitor_product_keywords, mcp__sorftime__ali1688_similar_product]
risk-level: low
---

## 前置建议

本公开版 Skill 是自包含的，不依赖任何私有工作区文件、内部参考库或品牌专属协议。

开始分析前，优先阅读本 Skill 自带的参考材料：

- `references/payload_schema_v2.md` — v2 数据包结构与必填字段
- `references/payload_schema.md` — v1 兼容格式
- `references/html_report_spec.md` — HTML 精简报告结构要求
- `references/analysis_patterns.md` — 分析模式与洞察写法模板

如果你已有自己的市场研究资料，可以作为补充背景使用；但本 Skill 的执行、交付和校验不依赖外部私有资料。

# 选品分析器（Product Research - Sorftime MCP）

## 定位

基于 **Sorftime MCP** 的选品分析，帮助你在有利润前提下，用最短时间、最低风险发现高潜力市场机会。

**数据来源**：全部通过 Sorftime MCP 工具获取，不捏造、不估算。

**下游输出**：选品报告（MD + HTML精简 + Dashboard看板 + Excel）→ 新品上架工作流的后续步骤：`zach-competitor-deep-dive`（Listing 级竞品拆解）→ `zach-pricing-strategy`（定价精算）→ …

> **注**：本 Skill 已吸收原 `zach-market-intelligence` 的 Go/No-Go 决策框架与进入壁垒评估能力（见 Step 2.4 / Step 3.5），以及 `zach-report-dashboard-renderer` 的 Dashboard 可视化看板能力。两者均已标记为 deprecated。

## Script Directory

- `scripts/render_deliverables.py`
  - 用途：把统一 JSON 数据包渲染为 `md + html精简 + dashboard看板 + xlsx + json`，并执行交付校验
  - **v2 模式**（推荐）：payload 含 `schema_version: “2.0”` + `chapters`，渲染器从结构化数据生成表格 + 插入 LLM 洞察段落
  - **v1 兼容模式**：payload 含 `report_markdown` / `report_html`，直接写入（旧流程）
  - 命令：
    - `python skills/zach-product-research/scripts/render_deliverables.py generate --input <payload.json>`
    - `python skills/zach-product-research/scripts/render_deliverables.py validate --input <payload.json>`
    - `python skills/zach-product-research/scripts/render_deliverables.py all --input <payload.json>`
  - 适用时机：Step 5 交付阶段，禁止手工只补单个文件后直接结束任务
- `scripts/parse_top100_dimensions.py`
  - 用途：按规则文件解析 Top100 标题维度，输出 `top100_parsed.json` 与 `uncertain_products.json`
- `scripts/cross_analysis.py`
  - 用途：基于解析后的产品 JSON 生成交叉矩阵和机会空白点

## References

- `references/payload_schema_v2.md`
  - 用途：v2 payload 结构定义（10 章 chapters + excel_sheets），准备 `render_deliverables.py` 输入数据包时查看
- `references/payload_schema.md`
  - 用途：v1 payload 结构定义（向后兼容参考）
- `references/html_report_spec.md`
  - 用途：HTML 精简报告区块定义参考
- `references/analysis_patterns.md`
  - 用途：四种分析模式的模板与示例，报告写作时必须引用（至少使用 3 种）

## Assets

- `assets/html_report_template.html`
  - 用途：HTML 精简报告模板（v1 使用，v2 由 render_deliverables.py 内置渲染）
- `assets/dashboard_template.html`
  - 用途：Dashboard 可视化看板模板（从 zach-report-dashboard-renderer 迁入），v2 由 render_deliverables.py 自动注入数据

## Agents

- `agents/data-pipeline.md`
  - 用途：负责 Sorftime 原始数据 → 中间 JSON / Excel Sheet 数据
- `agents/insight-writer.md`（v2 新增，替代 report-writer.md）
  - 用途：负责在固定 10 章结构中撰写分析洞察段落（不写表格格式/HTML）

## Evals

- `evals/evals.json`
  - 用途：最小自测套件
- `evals/files/sample_payload_minimal.json`
  - 用途：交付链路最小样本

---

## 核心原则

1. **权重优先**：权重越大，免费流量越多
2. **盈利监控**：利润覆盖广告成本，保持健康ROI
3. **战场优先**：先选好市场，再打磨产品
4. **数据驱动**：用可量化指标判断市场与竞品
5. **差异化竞争**：通过优化设计、卖点、包装提升转化

---

## 硬性规则（⛔ 不可省略）

以下规则适用于所有场景，不论模型能力或用户是否明确要求：

1. ⛔ 类目 Top100 明细必须输出完整 100 条，不得以"代表产品"缩写
2. ⛔ 竞品差评分析必须附"竞品选择逻辑表"（ASIN + 选择理由 + 竞品类型 + 覆盖维度），竞品总数 6-10 个，覆盖量级标杆/功能差异/价格带/痛点
3. ⛔ 关键词分析必须覆盖至少 3 个维度对比（如：品类大词 vs 属性词 vs 规格/场景词）
4. ⛔ MD 报告中出现的每个数据表/统计结论，必须在 Excel 中有对应 Sheet
5. ⛔ 每个 Step 完成后进行数据完整性检查，再进入下一步
6. ⛔ 输出前执行 Step 5 交付自检清单
7. ⛔ 定向品类分析（场景 4）必须执行 Step 1.5 产品属性标注
8. ⛔ 差评痛点必须按属性维度归类（而非仅按产品归类）

### 报告写作硬性规则（⛔ 不可省略）

以下规则确保每份报告达到「充电宝 v2」级别的分析深度，而非纯数据堆砌：

9. ⛔ **禁止纯数据呈现**：每个数据表格后必须紧跟「**关键洞察**」段落（2-4 条 bullet），说明数据的业务含义，不得只放表格不做解读
10. ⛔ **必须有 Executive Summary**：报告开头必须有 3-5 条核心结论，每条结构为：`数据点 → 含义 → 行动建议`
11. ⛔ **交叉分析必须解释原因**：每个"空白"/"薄供给"标签必须附带原因分析（技术限制？需求不存在？被市场忽视？供应链难度？），不得只标注状态
12. ⛔ **差评痛点必须映射品牌机会**：每个维度的差评痛点必须完成 `痛点 → 品牌能力 → 产品方案` 的映射，不得只列痛点不给方案
13. ⛔ **策略建议必须有产品矩阵**：至少给出 Tier 1 产品的完整规格（维度规格表 + 决策理由 + 目标定价 + 差异化主张 + 对标竞品 + 预估月销潜力），绝不允许"待确认"占位
14. ⛔ **供需缺口必须排优先级**：按三维评估（市场规模 40% + 技术可行性 30% + 品牌匹配 30%）排序，不得平铺罗列
15. ⛔ **必须使用分析模式**：每份报告至少使用以下 4 种分析模式中的 3 种（详见 `references/analysis_patterns.md`）：

| 模式 | 核心逻辑 | 最低使用次数 |
|------|----------|-------------|
| 数据→空白→机会 | 从分布数据中发现供给空白，评估机会价值 | 1 次 |
| 痛点→优势映射 | 将差评痛点映射到品牌能力和产品方案 | 1 次 |
| 交叉维度→结构性空白 | 多维度交叉发现结构性市场缺口 | 1 次 |
| 多维评估→优先级矩阵 | 多因素加权评估排出优先级 | 1 次 |

---

## Sorftime MCP 工具清单

执行选品分析时，调用以下 Sorftime MCP 工具（⛔ = 必调，📋 = 按需）：

| 类别 | 工具 | 用途 | 优先级 |
|------|------|------|--------|
| **类目** | `category_search_from_product_name` | 按产品名搜索相关细分类目 | ⛔ 必调 |
| | `category_search_from_top_node` | 按大品类搜索细分类目 | 📋 按需 |
| | `search_categories_broadly` | 多维度广泛搜索类目 | 📋 按需 |
| | `category_name_search` | 按类目名称查询NodeId | 📋 按需 |
| | `category_report` | 类目实时Top100报告 | ⛔ 必调 |
| | `category_report_from_history` | 类目历史Top100报告 | 📋 按需 |
| | `category_trend` | 类目趋势数据（⛔ NewProductSalesAmountShare 必调） | ⛔ 必调（Step 1.7） |
| | `category_keywords` | 类目核心关键词 | 📋 按需 |
| **关键词** | `keyword_search_results` | 关键词搜索结果自然位产品 | 📋 按需 |
| | `keyword_detail` | 关键词详情 | ⛔ 必调 |
| | `keyword_extends` | 关键词延伸词 | 📋 按需 |
| | `keyword_trend` | 关键词历史趋势 | 📋 按需 |
| **产品** | `product_search` | 产品搜索 | 📋 按需 |
| | `product_detail` | 产品详情（属性标注补充验证） | ⛔ 必调（Step 1.5） |
| | `product_trend` | 产品趋势 | 📋 按需 |
| | `product_reviews` | 产品评论 | ⛔ 必调（Negative） |
| | `product_traffic_terms` | 产品反查关键词 | 📋 按需 |
| | `product_variations` | 产品变体 | 📋 按需 |
| **选品** | `potential_product` | 潜力产品搜索 | 📋 按需 |
| | `competitor_product_keywords` | 竞品关键词曝光 | 📋 按需 |
| **供应链** | `ali1688_similar_product` | 1688相似产品（采购成本） | 📋 按需 |

**⛔ 必调说明**：无论场景如何，这 6 个工具必须调用，其输出是报告核心数据的来源。📋 按需工具根据场景和用户需求选择性调用。

---

## Gotchas（执行中最容易踩坑）

1. **Skill 本地存在，不等于当前会话已加载**
   - 如果仓库里已经有 `skills/zach-product-research/`，但当前会话仍提示 skill 不可用，先检查：
     - 当前 IDE 或 Agent 是否已经重新加载工作区配置
     - 是否存在历史别名（如 `product-research`）与正式名不一致的问题
   - **重要**：即使你修好了磁盘文件，当前会话的 skill 列表也可能不会热更新；必要时要明确提示“当前会话需重开/新会话重载 skill”。

2. **Sorftime MCP 在桌面端可能有逐次授权摩擦**
   - 大批量并发调用前，优先做“最小闭环”：先拿类目、关键词、Top100 核心数据，再决定是否继续深挖。
   - 批量补调时默认按 `<= 8` 一批，避免一口气铺太多工具调用，导致中途被用户逐个确认打断。
   - 如果环境允许网络访问，且本机 `~/.cursor/mcp.json` 已配置 Sorftime，可考虑走**本地直连 HTTP MCP** 作为非交互式 fallback；**严禁回显真实 key**。

3. **泛关键词经常混池，先清词池再估市场**
   - 不要默认把用户给的词直接当“机器本体市场”。
   - 典型案例：`essential oil diffuser` 会混入精油本体、humidifier、reed diffuser、耗材生态。
   - 必须先用 `category_name_search` / `keyword_search_results` / 标题样本检查，确认结果池到底是不是同一竞争单元，再做市场规模判断。

4. **Top100 大体量数据不要直接硬读**
   - 默认先走标题解析，再对未知项补调 `product_detail`。
   - 如果 Top100 / 评论 / 明细返回很大，先落中间文件，再用脚本抽取字段；不要靠手工读大 JSON。

5. **只产出 Markdown 不算完成**
   - 只要用户要正式交付，必须跑 `render_deliverables.py all`，同时产出 `MD + HTML精简 + Dashboard + XLSX`。
   - 如果目录里只有 `.md`，无论分析写得多完整，都视为**未完成**。

6. **render_deliverables.py 有严格校验门槛**
   - `excel_sheets` 第一张必须是 `数据来源说明`
   - 必选 Sheet 不全会校验失败
   - v2 payload 必须含 10 个 `chapters`
   - Markdown 洞察深度不足、缺少 Tier 产品矩阵、缺少 Go/No-Go 评分卡，也会在校验阶段暴露出来

---

## 执行流程

### Step 0: 信息收集（交互式）

收到调用后，首先确认以下关键信息：

```
📋 选品分析 - 信息确认

1. 目标站点：[US/UK/DE/FR/IT/ES/CA/JP，默认US]
2. 选品场景：[新手入门/蓝海发现/季节性/品牌打造/定向品类分析]
3. 约束条件（可选）：
   - 价格区间：如 $10-40
   - 月销量：如 > 1000
   - 品类偏好：如 家居/电子/宠物
   - 预算：如 10万人民币
4. 产业带优势（可选）：如有特定供应链优势
```

**如果用户未提供信息**：默认按「新手入门」场景，美国站，价格 $10-40，无特定产业带。

### Step 1: 发现机会市场

**1.1 类目市场扫描**

调用 `search_categories_broadly` 或 `category_search_from_product_name` 筛选符合以下条件的类目：

- 新品销量占比 > 15%
- 品牌数 > 80（分散市场）
- Top3销量占比 < 40%（低垄断）
- 平均价格 $10-40（新手友好）
- 月销量规模适中（视预算而定）

**1.2 关键词机会挖掘（⛔ 必须多维度对比）**

对候选类目，调用 `keyword_search_results` + `keyword_detail`：

- 搜索量 > 10000/月
- 自然位月销量 > 50000
- 首页竞品review数 < 500（门槛可追赶）
- CPC价格（广告成本）可接受

**⛔ 多维度关键词对比表**：关键词分析必须覆盖至少 3 个层级/维度，不得只分析用户提到的单一维度。

维度示例（根据品类调整）：

| 维度 | 示例关键词 | 说明 |
|------|-----------|------|
| 品类大词 | power bank, portable charger | 最大流量入口 |
| 属性词 | fast charging power bank, wireless power bank | 功能/特性细分 |
| 规格/参数词 | 65W power bank, 20000mAh portable charger | 具体规格参数 |
| 场景词 | laptop portable charger, camping power bank | 使用场景细分 |

每个维度的关键词必须调用 `keyword_detail` 获取以下数据，输出对比表：

| 关键词 | 维度 | 月搜索量 | CPC | 自然位产品数 | 首页平均评论数 | 数据来源 |
|--------|------|----------|-----|-------------|--------------|----------|

**检查点**：确认至少 3 个维度的关键词都有 `keyword_detail` 数据后，再进入 Step 1.3。

**1.3 潜力产品初筛**

调用 `potential_product` + `product_search`：

- 月销量 > 1000
- 价格 $10-30
- 评分 > 4.0
- 上架时间 < 6个月（新品有机会）

### Step 1.4: 分析维度自发现（用户未指定维度时执行）

> 当用户不熟悉目标品类、无法指定分析维度时，模型需要自主发现该品类的关键差异化维度。本步骤在 Step 1.5（属性标注）之前执行，输出为属性标注的维度定义。

**触发条件**：用户未明确指定分析维度，或指定维度 ≤ 2 个。

**执行方法**（四路并行，结果综合）：

**路径 1：Top100 标题高频词聚类**
- 对 `category_report` 返回的 100 条产品标题做词频统计
- 过滤掉通用词（brand, portable, charger 等品类通用词）
- 保留出现频率 ≥ 10% 的属性词作为候选维度
- 示例输出：`slim` 出现 23 次 → 候选维度「外观形态」

**路径 2：关键词延伸词分析**
- 对品类核心词调用 `keyword_extends`，分析消费者用什么修饰词搜索
- 高搜索量的修饰词 = 消费者关注的差异化维度
- 示例：`keyword_extends("power bank")` → "65W power bank", "slim power bank" → 候选维度「功率」「形态」

**路径 3：`product_detail` 属性字段 Key 提取**
- 对 Top5 销量产品调用 `product_detail`
- 从返回的「属性」字段中提取 **key 名称**（非 value），作为结构化维度候选
- 示例：属性含 `Battery Capacity`, `Connector Type` → 候选维度「容量」「接口类型」

**路径 4：WebSearch 品类评测文章（可选）**
- 搜索 "[品类] buying guide" 或 "[品类] how to choose"
- 从评测文章中提取消费者决策的关键参数
- 示例：Wirecutter 评测关注 "capacity, charging speed, size, ports" → 候选维度确认

**输出**：候选维度列表（5-8 个），每个维度含：
- 维度名称
- 发现来源（标题词频/延伸词/属性Key/评测文章）
- 候选分类值（如：功率 → ≤15W / 15-22.5W / 30W / 45W / 65W / 100W+）

**⛔ 必须让用户确认**：输出候选维度后，请用户确认/删减/补充，再进入 Step 1.5。用户可能有品类知识补充模型发现不了的维度。

**检查点**：至少确认 3 个分析维度后，进入 Step 1.5。

---

### Step 1.5: Top100 产品属性标注（P0 - 多维度分析必需）

> 本步骤将 `category_report` 返回的 Top100 基础数据升级为结构化多维度属性数据，是后续交叉分析与差异化建议的基础。

**输入**：Step 2.1 `category_report` 返回的 Top100 产品列表（本步骤可在获取 Top100 后立即执行，与 Step 1 并行推进）

**⛔ 必须提取的基础字段**（所有品类通用，`category_report` 直接返回）：

| 字段 | 来源 | 用途 |
|------|------|------|
| `上线日期` | category_report 原始字段 | Step 1.7 新品分析 |
| `上线天数` | category_report 原始字段 | Step 1.7 新品分析 |

这两个字段在 `category_report` 返回数据中已有，解析时必须一起提取，不要丢弃。

**标注维度**（按品类定制，以下为充电宝示例；其他品类需根据品类特征自定义维度）：

| 维度 | 解析方法 | 示例规则（充电宝） |
|------|----------|-------------------|
| 功率 | 正则 `(\d+\.?\d*)\s*[Ww]` + V/A 推算（V×A=W） | 22.5W, 65W, 5V/3A=15W |
| 容量 | 正则 `(\d[\d,]*)\s*[Mm][Aa][Hh]` （忽略大小写、处理逗号） | 10000mAh, 20,000 mAh |
| 线材 | 关键词 "built-in cable", "built in", "with cable", "integrated cable" | 内置线/外置线/无 |
| 数显 | 关键词 "LED display", "digital display", "LCD", "battery indicator" | 有/无 |
| 磁吸/无线充 | 关键词 "MagSafe", "magnetic", "Qi2", "wireless charging", "Qi" | MagSafe/Qi2/Qi/无 |
| 外观形态 | 关键词 "slim", "thin", "mini", "compact", "small", "lightweight" | slim/mini/standard |

**执行方法**（三阶段）：

1. **标题正则 + 关键词自动标注**（覆盖率约 70-80%）
   - 遍历 Top100 产品标题，按上表规则逐维度提取
   - 每条产品标注置信度：高（明确匹配）/ 低（模糊或缺失）

2. **⛔ `product_detail` 补充验证**（针对置信度低的约 20-30% 产品）
   - 对标题无法确认的产品，调用 `product_detail` 获取 bullet points / 产品描述
   - 从描述中提取缺失的属性信息
   - 每批最多 8 个并行调用以提高效率

3. **手动 override 记录**
   - 记录所有手动修正的产品及修正原因
   - 便于后续复查与经验积累

**⚠️ 标题解析注意事项**（参见文末「标题解析经验库」章节）

**输出**：

| 文件 | 内容 |
|------|------|
| `top100_parsed.json` | 每条产品增加 N 个属性列 + 置信度标注 |
| `uncertain_products.json` | 需要 `product_detail` 验证的产品列表及验证结果 |

**检查点**：确认 100 条产品均已完成属性标注（允许部分维度为"未知"，但不允许跳过标注步骤），再进入下一步。

### Step 1.6: 多维度交叉分析（P1 - 属性标注完成后执行）

> 基于 Step 1.5 的结构化属性数据，生成交叉分析矩阵，发现供需缺口与市场机会空白点。

**适用条件**：
- 产品已完成多维度属性标注（Step 1.5）
- 需要找到供需缺口（搜索需求有但供给少的维度组合）
- 需要发现产品组合机会空白点

**标准交叉表**：

对所有有意义的维度对（dimension pair）生成交叉矩阵：

| 交叉维度 | 分析指标 | 说明 |
|----------|----------|------|
| 维度A x 维度B | 产品数 | 该组合下有多少产品 |
| 维度A x 维度B | 月总销量 | 该组合的市场需求量 |
| 维度A x 维度B | 月总销额 | 该组合的市场价值 |
| 维度A x 维度B | 平均价格 | 该组合的价格水平 |

示例（充电宝）：功率 x 容量、功率 x 磁吸、容量 x 线材、功率 x 外观形态 等

**自动识别供需缺口**：

- **空白点**：产品数 = 0 的维度组合 → 潜在蓝海机会（需验证需求是否真实存在）
- **薄供给**：产品数 ≤ 2 的组合 → 低竞争机会（少量在售，竞争小）
- **高需求低供给**：月销量高但产品数少的组合 → 最优机会

**品牌集中度分析**：

- 每个主要维度组合中，Top3 品牌的销量占比
- 识别品牌垄断严重的组合（避开）vs 品牌分散的组合（机会）

**输出**：

| 文件 | 内容 |
|------|------|
| `cross_analysis.json` | 所有交叉分析矩阵数据 |
| 机会空白点列表 | 纳入最终报告的"市场机会"章节 |

**⛔ 交叉分析输出格式要求**：

每对交叉维度的输出不得只有表格，必须包含以下结构：

1. **交叉矩阵表格**（产品数 / 月销量 / 月销额 / 均价）
2. **关键发现段落**（2-4 条 bullet），必须回答：
   - 哪些组合是市场主力？（高供给 + 高需求）
   - 哪些组合存在供需缺口？（高需求 + 低供给）
   - 哪些组合是伪机会？（低供给 + 低需求，实际无需求）
3. **空白/薄供给标签定义与分析要求**：

| 标签 | 定义 | 必须补充的分析 |
|------|------|--------------|
| 空白 | 产品数 = 0 | 原因分析（技术不可行？需求不存在？被忽视？）+ 需求验证方法 |
| 薄供给 | 产品数 ≤ 2 | 现有产品表现如何？（销量/评分）+ 竞争进入难度 |
| 高需求低供给 | 月销量 Top30% 但产品数 Bottom30% | 为什么供给少？+ 进入可行性评估 |

**检查点**：确认至少 3 对维度组合完成交叉分析，且每对都有「关键发现」段落（不只表格），空白点/薄供给列表已生成且附原因分析，再进入 Step 1.7。

### Step 1.7: 新品分析（⛔ 必做）

> 基于 Step 1.5 已提取的 `上线日期` 字段，分析 Top100 中新品的占比、表现和趋势，判断类目对新品的友好程度。这是选品决策的关键输入——新品占比高的类目意味着新进入者有机会，反之则门槛高。

**数据来源**：
- `category_report` 返回的 `上线日期`/`上线天数` 字段（Step 1.5 已提取，零额外 API 成本）
- `category_trend`（trendIndex=NewProductSalesAmountShare）→ 1 次 API 调用

**执行步骤**：

**1. 上架时间分桶统计**

对 Top100 按上架时间分桶，统计每桶的产品数和销量占比：

| 时间段 | 产品数 | 月销量 | 销量占比 |
|--------|--------|--------|----------|
| ≤3 个月 | | | |
| 3-6 个月 | | | |
| 6-12 个月 | | | |
| 1-2 年 | | | |
| 2-3 年 | | | |
| 3 年+ | | | |

**2. 半年内新品明细表**

列出所有上架 ≤6 个月的产品，按月销量降序：

| ASIN | 品牌 | 价格 | 月销量 | 上线日期 | 天数 | 评论数 | [各属性维度] |

关注：
- 新品中有哪些品牌？（全是大品牌 vs 有白牌突围）
- 新品进入 Top50 了吗？（能否打进头部）
- 新品的属性组合是什么？（市场供给方向验证）

**3. 新品销量占比趋势**

调用 `category_trend`（trendIndex=`NewProductSalesAmountShare`），获取近 2 年每月的新品销量占比趋势：
- 趋势上升 → 类目活跃，对新品友好
- 趋势平稳低位（<5%）→ 类目成熟，老品主导，新品难突围
- 趋势下降 → 类目固化，不建议新品进入

**4. 新品友好度判断**

综合以上数据，给出类目的新品友好度评级：

| 指标 | 友好（绿灯） | 中等（黄灯） | 不友好（红灯） |
|------|------------|------------|--------------|
| 半年内新品占 Top100 数量 | ≥10% | 5-10% | <5% |
| 半年内新品销量占比 | ≥10% | 5-10% | <5% |
| 新品进入 Top50 数量 | ≥3 个 | 1-2 个 | 0 |
| 新品中是否有非头部品牌 | 有白牌/新品牌 | 仅 2-3 线品牌 | 全是头部品牌 |
| 新品销量占比趋势 | 上升 | 平稳 | 下降 |

**输出**：纳入报告的「市场概况」章节，含上架时间分布表、新品明细、趋势图数据、新品友好度评级。

**检查点**：新品分析完成且新品友好度评级已给出，再进入 Step 2。

### Step 2: 验证竞争格局

**2.1 类目深度分析**

调用 `category_report` 获取 Top 100，分析：

- 品牌集中度（品牌垄断系数）
- 卖家类型分布（FBA/FBM/亚马逊自营比例）
- 新品比例（半年内上架产品占比）

**检查点**：确认 `category_report` 返回的产品数 = 100 条（⛔ 硬性规则第 1 条）。不足则重新调用或说明原因。

**2.2 竞品详细分析（⛔ 差评分析须附选择逻辑）**

对重点产品，调用 `product_detail` + `product_reviews`：

- 销量排名、价格趋势、评分评论数
- 好评关键词（用户重视什么）
- 差评痛点（改进机会）

**⛔ 竞品选择逻辑表**：做差评分析前，必须先输出竞品选择逻辑表，说明为什么选这些竞品：

| ASIN | 品牌 | 选择理由 | 竞品类型 | 覆盖维度 |
|------|------|----------|----------|----------|
| B0XXXXXXXX | BrandA | 类目销量 Top3 | 量级标杆 | 价格带-中 |
| B0YYYYYYYY | BrandB | 高功率段销量第一 | 功能差异代表 | 功率-高 |
| B0ZZZZZZZZ | BrandC | 差评率最高（4.0以下） | 痛点参考 | 痛点密集 |
| B0WWWWWWWW | BrandD | 磁吸品类入门款 | 功能差异代表 | 磁吸-入门 |
| B0VVVVVVVV | BrandE | 高端价格带代表 | 价格带覆盖 | 价格带-高 |
| B0UUUUUUUU | BrandF | 低价走量代表 | 价格带覆盖 | 价格带-低 |

**⛔ 竞品选择必须满足以下覆盖要求**：

| 覆盖维度 | 要求 | 说明 |
|----------|------|------|
| 量级标杆 | 至少 1-2 个 | 类目 Top5 销量产品，代表市场标准 |
| 功能差异代表 | 每个主要功能维度至少 1 个 | 如：高功率代表、磁吸代表、内置线代表 |
| 价格带覆盖 | 高/中/低各至少 1 个 | 确保分析覆盖全价格段 |
| 痛点参考 | 至少 1-2 个 | 差评率高或星级低的产品，挖掘改进机会 |

- **总数**：6-10 个竞品
- **每个主要属性维度**（来自 Step 1.5 标注）至少有 1 个代表产品

**选择建议**：按细分段（如价格带、功率段、使用场景）各选 1-2 个代表，覆盖头部竞品 + 痛点竞品。

**检查点**：竞品选择逻辑表完成后，再逐一调用 `product_reviews`（reviewType=Negative）做差评分析。每批最多 8 个并行调用。

**⛔ 差评分析按维度分类**：差评痛点必须按属性维度归类（如功率相关、线材相关、数显相关、容量相关、磁吸相关、外观形态相关、通用质量问题），而非仅按产品归类。这样才能直接映射到产品设计决策。

**2.3 关键词竞争分析**

调用 `competitor_product_keywords` + `product_traffic_terms`：

- 核心关键词排名
- 流量词数量和分布
- 自然流量 vs 广告流量占比

**2.4 进入壁垒评估（⛔ 必做，原 market-intelligence Step 4）**

> 适用场景：所有正式交付版本必须输出。本节用于把“能不能做”的风险讲清楚，避免只给机会不讲门槛。

评估以下壁垒维度，每个维度给出等级（低/中/高）：

| 壁垒类型 | 评估内容 | 数据来源 |
|----------|----------|----------|
| Review 壁垒 | 达到首页需要多少 Review | `category_report` Top100 评论数分布 |
| 资金壁垒 | 首批备货 + 广告 + 头程 | `ali1688_similar_product` + 估算 |
| 技术壁垒 | 是否需要认证/专利/模具 | WebSearch + 品类知识 |
| 合规壁垒 | FDA/UL/CE/FCC 等认证 | WebSearch（见下方站点合规表） |
| 供应链壁垒 | 供应商门槛/MOQ | `ali1688_similar_product` |
| 品牌壁垒 | 是否需要品牌故事/忠诚度 | 竞争格局分析结果 |

**站点合规速查**：

| 站点 | 常见认证要求 |
|------|-------------|
| US | FDA（食品/化妆品）、UL（电子）、FCC（无线）、CPSC（儿童产品）、EPA（杀虫）|
| UK | UKCA、WEEE |
| DE | CE、WEEE、EPR、VerpackG（包装法）|
| FR | CE、EPR、Triman 标志 |
| IT/ES | CE、EPR |

**输出**：壁垒汇总表（类型 + 等级 + 预估成本 + 预估时间）+ 预估启动投入合计

### Step 3: 投入产出测算

**财务公式**：

```
毛利 = 售价 - 采购成本 - FBA费用 - 物流成本
净利润 = 毛利 - 广告成本 - 退货损耗 - 平台佣金(约15%)
毛利率 = 净利润 / 售价 * 100%

预估CPC：从 keyword_detail 获取
目标ACOS = 毛利率 * 50%（保守）
净利率 = 净利润 / 售价 * 100%
```

**物流成本参考**：

- 价格 $10-20：物流成本控制在售价 15% 以内
- 价格 $20-40：可承担更高物流成本

**采购成本**：可调用 `ali1688_similar_product` 获取1688货源参考价。

### Step 3.5: Go/No-Go 综合评分（⛔ 必做，原 market-intelligence Step 6）

> 适用场景：所有正式交付版本必须输出。即便用户已经倾向进入，也必须把“进入条件、前提风险、最终判断”显式写出来。

**评分体系（加权计算）**：

| 维度 | 权重 | 评分(1-10) | 数据来源 |
|------|------|-----------|----------|
| 市场规模 | 20% | X | Step 1.1 `category_report` |
| 竞争格局 | 25% | X | Step 2.1 品牌集中度/新品占比 |
| 需求清晰度 | 15% | X | Step 1.2 关键词 + Step 1.6 交叉分析 |
| 进入壁垒（反向） | 20% | X | Step 2.4 壁垒评估 |
| 盈利能力 | 20% | X | Step 3 投入产出测算 |

**决策矩阵**：

| 加权总分 | 决策 | 建议 |
|----------|------|------|
| 7.5-10 | **GO** | 强烈建议进入，优先推进 |
| 6.0-7.4 | **CONDITIONAL GO** | 有条件进入，需解决关键风险 |
| 4.0-5.9 | **HOLD** | 暂缓，需更多数据验证或等待时机 |
| 0-3.9 | **NO-GO** | 不建议进入，风险大于机会 |

**输出**：评分卡 + 决策建议 + Top3 机会 + Top3 风险 + 缓解方案

**注意**：如果决策为 NO-GO，流程终止，不进入 Step 4。

### Step 4: 差异化建议与产品矩阵（⛔ 必须具体到规格）

> 本步骤是报告的核心价值输出——从数据分析转化为可执行的产品策略。绝不允许"待确认"占位或只列方向不给规格。

**4.1 VOC 痛点维度映射**

基于 Step 2.2 的差评分析（已按维度归类），对每个维度执行四要素映射：

| 要素 | 说明 | 示例（充电宝-功率维度） |
|------|------|----------------------|
| **痛点描述** | 该维度下消费者最高频的不满 | "充电速度慢，标称快充实际只有 10W" |
| **数据支撑** | 差评频次/占比 + 涉及竞品 | 23% 差评提及充电慢，涉及 Brand A/B/C |
| **品牌机会** | 品牌在该维度的能力优势 | 目标品牌具备快充或供应链优势，可做真实 65W |
| **产品方案** | 具体的产品设计方向 | 标配 65W GaN + LED 实时功率显示，消除信任疑虑 |

⛔ 每个属性维度（来自 Step 1.5）都必须完成此映射表，不得遗漏。

**4.2 机会空白优先级排序**

汇总 Step 1.6 交叉分析发现的所有空白/薄供给/高需求低供给机会，按三维评估排序：

| 评估维度 | 权重 | 评分标准（1-5 分） |
|----------|------|-------------------|
| 市场规模 | 40% | 1=月销额<$50K, 2=50-200K, 3=200-500K, 4=500K-1M, 5=>1M |
| 技术可行性 | 30% | 1=需要重大研发, 2=需要新模具, 3=改良现有方案, 4=成熟方案, 5=现有产品线可覆盖 |
| 品牌匹配 | 30% | 1=完全不匹配, 2=需要新品牌定位, 3=部分匹配, 4=高度匹配, 5=核心优势领域 |

**输出格式**：

| 排名 | 机会描述 | 维度组合 | 市场规模(40%) | 技术可行性(30%) | 品牌匹配(30%) | 加权总分 | 建议行动 |
|------|----------|----------|-------------|----------------|-------------|---------|---------|
| 1 | [具体描述] | [维度A×维度B] | X | X | X | X.X | [具体行动] |

**4.3 产品矩阵规划**

基于优先级排序，规划具体产品矩阵。至少完成 Tier 1（最优先进入的产品），Tier 2/3 视数据充分度而定：

**Tier 模板**（每个 Tier 必须包含以下所有字段）：

```
### Tier [N]: [产品定位一句话]

**目标市场**：[对应的维度组合空白/机会]
**决策理由**：[为什么优先做这个——引用 4.2 的优先级排序数据]

| 维度 | 规格 | 决策依据 |
|------|------|----------|
| [维度1] | [具体规格值] | [为什么选这个值] |
| [维度2] | [具体规格值] | [为什么选这个值] |
| ... | ... | ... |

**目标定价**：$XX.XX（基于 Step 3 测算，毛利率 XX%）
**差异化主张**：[一句话核心卖点，区别于竞品的关键]
**对标竞品**：[ASIN] [品牌] [价格] — 我们的优势：[具体差异]
**预估月销潜力**：XX-XX 件/月（基于同维度组合现有产品表现推算）
```

⛔ **禁止事项**：
- 不允许"待 Zach 确认"、"待定"、"建议进一步调研"等占位语
- 不允许只列方向不给具体规格（如"建议做大容量"必须改为"建议做 20000mAh"）
- 不允许不标对标竞品（必须有具体 ASIN）
- 不允许不给目标定价（必须基于 Step 3 测算）
- 如果数据确实不足以支撑某个 Tier，明确标注"数据不足：缺少 XX 数据，建议补充 XX 后再定"，但不得用"待确认"含糊带过

### Step 5: 交付前自检（⛔ 必做）

### ⛔ 交付硬性规则

16. ⛔ **禁止分步输出**：不得先手工输出 MD 报告再调用 render_deliverables.py；
    所有交付物必须由 `render_deliverables.py all` 一次性生成
17. ⛔ **unified_payload.json 必须包含产品级明细**：
    - `excel_sheets["类目销量Top100_明细"]` 必须包含 100 条产品数据
    - `excel_sheets["属性标注_Top100"]` 必须包含属性标注结果
    - 两个 Sheet 的数据来源是 `top100_raw.json` 和 `top100_parsed.json`
18. ⛔ **竞品选择逻辑必须包含价格和销量**：`competitor_selection_logic` 每条记录
    必须含 price/monthly_sales/reviews 字段（从 product_detail 获取）

在输出报告和数据文件之前，逐项检查以下清单。**全部通过后才可输出**，未通过项必须修正后再输出：

- [ ] 类目 Top100 明细 = 100 条？（不足 100 条说明数据获取不完整，需重新调用 `category_report`）
- [ ] Top100 产品已完成属性标注？（Step 1.5，每条产品至少标注了定义的维度）
- [ ] 交叉分析已完成至少 3 对维度组合？（Step 1.6，含空白点/薄供给列表）
- [ ] 每个分析维度的关键词都有 `keyword_detail` 数据？（至少 3 个维度）
- [ ] 竞品差评分析附有"竞品选择逻辑表"？（含 ASIN + 选择理由 + 竞品类型 + 覆盖维度）
- [ ] 竞品选择覆盖了量级标杆、功能差异代表、价格带高中低、痛点参考？（6-10 个）
- [ ] 差评痛点已按属性维度归类？（而非仅按产品归类）
- [ ] MD 报告中的每个数据表在 Excel 中有对应 Sheet？
- [ ] Excel 中的数据条数 >= MD 报告中的数据条数？（Excel 不得少于 MD）
- [ ] 所有数据点标注了 Sorftime MCP 来源工具名？
- [ ] JSON 第一个 key 为"数据来源说明"？
- [ ] Excel Sheet 列表包含"竞品选择逻辑"和"关键词对比_分段"？（若有对应分析）
- [ ] Excel 包含"属性标注_Top100"和"交叉分析"Sheet？（若执行了 Step 1.5/1.6）
- [ ] 新品分析（Step 1.7）已完成？（含新品数量/占比/时间分桶 + 新品友好度评级）
- [ ] HTML 精简报告已生成？（⛔ 三件套：MD + Excel + HTML）
- [ ] 若执行了 Step 2.4 进入壁垒评估，壁垒汇总表完整？（6 类壁垒 + 等级 + 成本 + 时间）
- [ ] 若执行了 Step 3.5 Go/No-Go 评分，5 维度评分 + 加权总分 + 决策建议完整？
- [ ] 「类目销量Top100_明细」Sheet 包含 ≥100 条数据？
- [ ] 「属性标注_Top100」Sheet 属性标注完整？
- [ ] 竞品选择逻辑表每条含 price/monthly_sales/reviews？
- [ ] 调用 `render_deliverables.py all` 一次性生成（非分步）？

**洞察质量检查（⛔ 必须全部通过）**：

- [ ] 有 Executive Summary（≥ 4 条核心结论，每条含数据点+含义+行动建议）？
- [ ] 每个维度分布表后有「关键洞察」段落（2-4 条 bullet）？
- [ ] 交叉分析每对维度有「关键发现」段落（不只表格）？
- [ ] 所有「空白」/「薄供给」标签都有原因解释（技术/需求/被忽视/供应链）？
- [ ] 差评按维度归类后，每个维度有「品牌机会」映射（痛点→能力→方案）？
- [ ] 有产品矩阵（至少 Tier 1 含完整规格表+定价+差异化+对标竞品）？
- [ ] 机会空白点有优先级排序（三维加权评估）？
- [ ] 报告至少使用了 3 种分析模式（见 `references/analysis_patterns.md`）？

---

## "6合1"隐赚指数标准

隐赚指数（潜力指数）评估以下6项，得分越高越好：

| 指标 | 理想状态 |
|------|----------|
| 排名趋势 | 稳定或上升 |
| 销量趋势 | 稳定或增长 |
| 价格趋势 | 稳定或上涨 |
| 评价门槛 | 评论数少、易追赶（<500） |
| 广告成本 | CPC低或自然流量高 |
| 上架时间 | 半年内新品 |

`potential_product` 可按潜力指数排序，优先筛选高分产品。

---

## "好市场"评判标准

| 维度 | 理想指标 |
|------|----------|
| 流量垄断 | 垄断系数 < 30% |
| 品牌分散 | 品牌数 > 80 |
| 新品活跃 | 新品占比 > 30%，新品销量占比 > 15% |
| 评价门槛 | 平均评论数 < 500 |
| 价格区间 | $10-40 |
| 售后风险 | 退货率 < 10% |

---

## 选品输出模板

每个推荐产品必须包含以下结构：

```markdown
## 【产品名称】

### 一、市场概况
- **所属类目**：[类目名称 + NodeId]
- **目标关键词**：[核心关键词]
- **月销量规模**：[市场规模]
- **平均价格**：[价格区间]
- **数据来源**：[Sorftime MCP 工具名]

### 二、"6合1"验证
- [ ] 排名趋势：[稳定/上升/下降]
- [ ] 销量趋势：[稳定/增长/下降]
- [ ] 价格趋势：[稳定/上涨/下跌]
- [ ] 评价门槛：评论数[XXX]，可追赶
- [ ] 广告成本：CPC $[XXX]
- [ ] 上架时间：[XXX]个月内

### 三、竞争分析
- **品牌垄断系数**：[XX%]
- **Top3销量占比**：[XX%]
- **新品活跃度**：[高/中/低]
- **主要竞品**：[竞品ASIN及特点]

### 四、财务测算（USD）
| 项目 | 金额 |
|------|------|
| 售价建议 | $XX.XX |
| 采购成本 | $X.XX |
| FBA费用 | $X.XX |
| 平台佣金(15%) | $X.XX |
| 物流成本 | $X.XX |
| 预估毛利 | $X.XX |
| 毛利率 | XX% |
| 预估CPC | $X.XX |
| 目标ACOS | XX% |
| 净利率 | XX% |

### 五、差异化建议
- **痛点改进**：[具体改进方向]
- **卖点提炼**：[差异化卖点]
- **定价策略**：[价格方案]

### 六、风险提示
- [ ] 季节性风险：[是/否]
- [ ] 认证要求：[是/否]
- [ ] 专利风险：[是/否]
- [ ] 供应链风险：[注意事项]
```

---

## 常见场景策略

### 场景1：新手入门（预算<15万）

- 价格 $10-20
- 轻小件（降低FBA成本）
- 无售后风险品类
- 中国卖家占比 > 70% 的类目
- 推荐：厨房收纳、宠物用品、头巾面罩

### 场景2：蓝海发现（低竞争）

- 筛选低垄断类目（`search_categories_broadly` 设 `top3Product_sales_share` < 0.4）
- 关注新品出单明显的细分市场
- 寻找 Top400 长尾机会
- 验证关键词竞争强度（`keyword_detail`）

### 场景3：季节性产品

- 使用 `keyword_trend` 验证季节性
- 提前 2-3 个月备货
- 关注搜索量变化趋势
- 评估淡季库存风险

### 场景4：定向品类/产品分析（用户已指定品类）

适用于用户已确定要分析的产品/品类（如"分析美国站充电宝市场"、"分析某品类竞争格局"），与场景 1-3 的"发现未知机会"不同。

**与发现型场景的区别**：

| 步骤 | 发现型（场景1-3） | 定向型（场景4） |
|------|-------------------|----------------|
| Step 1.1 类目扫描 | 广泛搜索候选类目 | **跳过**——用户已指定类目，直接用 `category_search_from_product_name` 定位 NodeId |
| Step 1.2 关键词 | 筛选高潜力词 | **⛔ 多维度对比**——必须覆盖品类大词、属性词、规格词、场景词（至少 3 维度） |
| Step 1.4 维度发现 | 📋 按需 | **⛔ 推荐**——用户未指定维度时必做；用户已指定维度时跳过 |
| Step 1.5 属性标注 | 📋 按需 | **⛔ 必做**——定向分析需要多维度结构化数据，属性标注是核心步骤 |
| Step 1.6 交叉分析 | 📋 按需 | **⛔ 推荐**——发现维度组合空白点，直接指导产品定义 |
| Step 2.2 竞品选择 | 按潜力指数选 | **按细分段选**——按价格带/功能段/使用场景各选 1-2 个代表，覆盖市场全貌 |
| Step 2.4 进入壁垒 | **⛔ 必做** | **⛔ 必做**——正式交付版本必须明确六类壁垒与启动前提 |
| Step 3.5 Go/No-Go | **⛔ 必做** | **⛔ 必做**——正式交付版本必须给出量化结论，而不是只给方向 |
| Step 1.7 新品分析 | 📋 按需 | **⛔ 必做**——定向分析需评估新品可进入性 |
| Step 1.3 潜力产品 | 核心步骤 | 📋 按需——用户更关心已有市场格局而非新品机会 |

**执行要点**：

- 直接从 Step 0 收集的品类/产品名进入 Step 1.2 关键词分析
- 关键词维度覆盖必须全面（⛔ 硬性规则第 3 条）
- ⛔ 必须执行 Step 1.5 属性标注 + Step 1.6 交叉分析（定向分析的核心价值）
- 竞品选择必须附选择逻辑表（⛔ 硬性规则第 2 条），覆盖量级标杆/功能差异/价格带/痛点
- 差评分析必须按属性维度归类
- 类目 Top100 仍需完整 100 条（⛔ 硬性规则第 1 条）

---

## 输出规范

1. **数据来源标注**：每个数据点必须标注来源 Sorftime MCP 工具名
2. **量化指标优先**：用具体数字而非模糊描述
3. **逻辑链完整**：从市场发现 → 竞争验证 → 财务测算 → 差异化建议
4. **风险提示**：必须包含潜在风险和应对方案
5. **可执行性**：建议必须具体可落地

---

## 数据诚信规则（必须遵守）

- **绝不捏造数据**：所有数据必须来自 Sorftime MCP 调用结果，不得编造
- **标注数据来源**：每个数据点标注来源工具（如 `mcp_sorftime_product_search`）
- **区分事实与推测**：事实用数据支撑，推测必须标注「⚠️ 推测」
- **标注数据时效**：注明数据的获取时间或适用时间范围

---

## `product_detail` 返回字段与可信度指南

> Sorftime `product_detail` 返回的字段来源不同，可信度差异大。标注属性时需按可信度优先级使用。

| 字段 | 对应亚马逊位置 | 可信度 | 使用建议 |
|------|--------------|--------|----------|
| **标题** | 前台产品标题 | **高** | 主要解析来源，消费者可见，虚标会被投诉 |
| **产品描述** | 五点描述 / A+ 文字 | **中高** | 补充验证，营销文案但含具体参数 |
| **属性** | 后台 Item Specifics | **中低** | 结构化但卖家可能乱填，需交叉验证 |
| **外包装尺寸** | 物流属性 | **高** | 可推算产品实际大小，辅助判断形态 |
| 价格/销量/评论/排名 | 前台公开数据 | **高** | 基础信息，直接使用 |
| 主图 URL | 产品图片链接 | — | 当前无法 OCR，仅供人工查看 |

**使用优先级**：标题 > 产品描述（五点） > 属性字段（后台）

**属性字段常见问题**：
- `Special Feature`：卖家经常堆砌不相关关键词，**不可作为属性判断依据**
- `Battery Capacity`：通常准确（亚马逊有格式要求），可直接使用
- `Connector Type`：格式不统一（有的写 "USB-C"，有的写 "Output: USB-C*2+USB-A*1"），需解析
- `Color` / `Style`：通常准确，可直接使用
- **空字段**：`特征` 字段经常为空 `{}`，不要依赖

---

## 中间数据持久化规则

> 多维度分析流程通常需要 2-3 小时甚至跨 session 完成。为防止上下文压缩或 session 中断导致数据丢失，必须在关键节点持久化中间结果。

**⛔ 持久化检查点**：

| 完成步骤后 | 必须保存的文件 | 说明 |
|-----------|--------------|------|
| Step 1.1 category_report | `top100_raw.json` | 原始 Top100 数据，后续所有分析的基础 |
| Step 1.4 维度自发现 | 记录在 session 中或追加到报告 | 用户确认的维度列表 |
| Step 1.5 属性标注 | `top100_parsed.json` + `uncertain_products.json` | 标注后数据 + 待验证列表 |
| Step 1.6 交叉分析 | `cross_analysis.json` | 交叉矩阵 + 空白点 |
| Step 2.2 VOC 分析 | `voc_analysis.json` | 竞品选择逻辑 + 差评分类 |

**原则**：
- 每个 Step 完成后，将结果写入文件再进入下一步
- 如果 session 中断，下次可从最后保存的文件恢复，避免重新调用 API
- JSON 文件命名与标准输出目录一致（见「标准输出目录结构」）

---

## Sorftime 返回数据处理规则（⛔ 必须用 Python 脚本）

> Sorftime MCP 返回的数据量通常较大（Top100 约 50KB+），直接用 Read 工具读取会超出 token 限制导致失败。所有 Sorftime 大数据返回**一律用 Python 脚本解析**，不要尝试 Read 工具直读。

### 哪些工具的返回需要 Python 脚本处理

| 工具 | 返回大小 | 处理方式 |
|------|----------|----------|
| `category_report` | ~50KB（100 条产品） | ⛔ 必须用 Python 脚本解析 |
| `product_detail`（批量） | 每个 ~2-5KB，批量 ≥5 个时总量大 | ⛔ 必须用 Python 脚本解析 |
| `keyword_detail` | 每个 ~0.5KB | 单次可直读，批量用脚本 |
| `product_reviews` | ~5-20KB（按产品） | 建议用 Python 脚本解析 |
| 其他单次调用 | <5KB | 可直读 |

### category_report 数据结构与解析模板

Sorftime `category_report` 返回数据的结构**不是标准 JSON**，而是包裹在 `list[0]['text']` 中，前面带有一行指令文本。必须用以下方式解析：

```python
import json

# raw_data 是 category_report 的返回值（保存为文件后读取）
with open('top100_raw.json', 'r') as f:
    raw = json.load(f)

# 结构：list[0]['text'] 包含 JSON，前面有指令前缀
text_content = raw[0]['text']
json_start = text_content.index('{')  # 找到第一个 { 的位置
data = json.loads(text_content[json_start:])

# data 现在是标准 dict，包含 Top100 产品列表
products = data.get('products', [])  # 具体 key 视返回格式而定
```

**⛔ 不要**：
- 不要用 Read 工具直接读取 category_report 的返回文件（会超 token 限制）
- 不要假设返回是标准 JSON（有指令前缀）

### product_detail 批量调用规则

| 规则 | 说明 |
|------|------|
| 每批最多 **8 个**并行调用 | 超过 8 个可能触发限流 |
| 返回结果用 Python 脚本解析 | 批量结果合并处理，提取需要的字段 |
| 先标题解析，再对"未知"项补调 | 标题覆盖率约 70-80%，仅对缺失项调 product_detail，节省 API 调用 |

**标准两步流程**（Step 1.5 细化）：

```
Step 1: 标题正则解析 100 个产品 → 标注已知/未知
Step 2: 对"未知"产品批量调 product_detail（每批 ≤8 并行）→ 从描述/属性中提取缺失值
```

这比对全部 100 个产品调 product_detail 节省约 70-80% 的 API 调用量。

### product_reviews 处理建议

- 每个竞品的差评数据量约 5-20KB
- **可批量并行调用**：与 `product_detail` 一致，每批最多 8 个 ASIN 并行调用，再合并解析，以减少总耗时
- 批量获取 6-10 个竞品的差评后，用 Python 脚本按维度归类
- 归类结果保存为 `voc_analysis.json`

---

## 标题解析经验库（P1 - 按品类持续积累）

> 本节记录标题正则解析中的常见陷阱与经验规则，供 Step 1.5 执行时参考，避免重复踩坑。按品类积累，新品类调研后应补充新的经验条目。

### 通用陷阱

| 陷阱类型 | 示例 | 错误理解 | 正确处理 |
|----------|------|----------|----------|
| 相似词混淆 | "Lighting Input" | Lightning 线材 | 这是输入端口描述，不是内置 Lightning 线 |
| V/A 功率推算 | "5V/3A" | 不知道功率 | V x A = W，即 5V/3A = 15W，5V/2.4A = 12W |
| PD 功率推断不可靠 | "PD Fast Charging" | 等于 20W | PD 可能是 15W/18W/20W/30W 中任何一个，需 `product_detail` 确认 |
| "Fast Charging" 含义模糊 | "Fast Charging Power Bank" | 高功率快充 | 实际可能是 12W-20W 任何功率，需 `product_detail` 确认 |
| 容量格式多样 | "10000mah", "10,000 mAh" | 解析失败 | 正则需忽略大小写 `[Mm][Aa][Hh]`，处理逗号 `\d[\d,]*` |
| 标题营销夸大 | "Super Fast", "Ultra Quick" | 高功率 | 营销用词无标准含义，不可作为属性值 |
| 多功能合并描述 | "3-in-1 Charger Cable" | 三条线 | 可能是一条三合一线，需验证 |

### 品类特定经验：充电宝（Portable Charger / Power Bank）

| 维度 | 解析要点 | 正则/规则 |
|------|----------|-----------|
| 功率 | 优先匹配明确 W 值；无 W 值时用 V*A 推算；仅有 "PD"/"Fast Charging" 标记为"待确认" | `(\d+\.?\d*)\s*[Ww]` 优先；`(\d+\.?\d*)\s*[Vv]\s*/?\s*(\d+\.?\d*)\s*[Aa]` 次之 |
| 容量 | 忽略大小写、处理逗号分隔符 | `(\d[\d,]*)\s*[Mm][Aa][Hh]` |
| 线材 | 区分"内置线"和"输入端口"；"Lighting Input" 不是内置线 | 关键词匹配 + 排除 "input"/"port" 后缀 |
| 磁吸 | MagSafe/Qi2 属于磁吸无线充；普通 Qi/wireless 属于无线充但非磁吸 | 分层标注：MagSafe > Qi2 > Qi > 无 |
| 数显 | "LED" 单独出现可能是指示灯而非数显屏 | 需匹配 "LED display"/"LED screen" 而非仅 "LED" |

### 品类特定经验：充电器（Wall Charger / Charger Block）

| 维度 | 解析要点 | 正则/规则 |
|------|----------|-----------|
| 功率 | 优先匹配明确 W 值；无 W 值时 USB-A 单口默认 ≤12W；仅标 "PD"/"Fast Charging" 需 product_detail 确认 | `(\d+\.?\d*)\s*[Ww]` |
| 接口数 | 区分"端口数"和"装数"：`2 port` = 2口，`2 pack` = 2装 | "dual"=2口, "3 port"=3口, 数字+port |
| 接口类型 | 仅标注 USB-C / USB-C+USB-A 两类；纯 USB-A 产品极少（已退出主流） | 默认 USB-C，含 "USB-A"/"USB A" 标为混合型 |
| 带线 | "with cable"/"with cord"/"built-in cable" = 带线；注意区分"带线充电器"和"充电线单品" | 关键词匹配 |
| 装数(Pack) | `(\d+)\s*-?\s*[Pp]ack` 提取；无 Pack 标注默认 1装 | 正则提取 |
| GaN | 标题含 "GaN"/"Gallium Nitride" = 是 | 大小写不敏感 |
| 折叠插脚 | "foldable"/"fold"/"foldable plug" = 是 | 关键词匹配 |
| **陷阱** | "2 Pack" vs "2 Port" 最常混淆；"USB C Charger Block **2 Pack**" = 2装单口，不是2口 | 需组合上下文判断 |
| **陷阱** | 标题无 W 值的 USB-A 产品通常是 5V/2.1A=10W 或 5V/2.4A=12W，需 product_detail 确认 | V×A 推算 |
| **陷阱** | "40W" 标题可能是 "20W × 2 port" 总功率，也可能是单口 40W，需看接口数 | 结合接口数判断 |

### 经验库使用规则

1. **执行 Step 1.5 前**，先查阅本节对应品类的经验条目
2. **发现新陷阱时**，在调研报告末尾记录，后续合并回本节
3. **品类首次调研**，经验库可能为空，调研结束后必须补充至少 3 条经验
4. **置信度标注**：凡命中上述陷阱条目的产品，自动标注为"低置信度"，进入 `product_detail` 验证队列

---

## 标准输出目录结构（P2）

定向品类分析（场景 4）的标准输出文件结构：

```
outputs/market-research/{brand}/{品类}/{version}/
├── top100_raw.json              # 原始 Top100 数据（category_report 直接输出）
├── top100_parsed.json           # 属性标注后的 Top100 数据（Step 1.5 输出）
├── uncertain_products.json      # 需 product_detail 验证的产品列表
├── cross_analysis.json          # 交叉分析结果（Step 1.6 输出）
├── voc_analysis.json            # VOC 差评分析结果
├── {date}_{site}_{品类}_市场调研报告_{version}.md     # 完整 MD 报告
├── {date}_{site}_{品类}_市场调研_数据_{version}.xlsx   # Excel 数据（多 Sheet）
├── {date}_{site}_{品类}_精简报告_{version}.html        # ⛔ HTML 精简报告（三件套必出）
├── parse_top100_dimensions.py   # 标题解析脚本（可选，复杂品类用）
├── apply_overrides.py           # 手动修正脚本（可选）
├── cross_analysis.py            # 交叉分析脚本（可选）
└── export_to_excel.py           # Excel 导出脚本
```

其中 `{version}` 格式为 `v{N}_{YYYYMMDD}`（如 `v2_20260228`），便于同品类多次调研的版本管理。

---

## 报告与数据文件存储

**必须同时输出三类文件（⛔ 三件套必出）**（与 market-comparison 及「外部数据调用规范」一致）：MD 报告 + Excel 多 Sheet + **HTML 精简报告**，便于负责人逐项、逐 ASIN 验证且**来源可追溯**。

| 类型 | 格式 | 文件命名 | 用途 |
|------|------|----------|------|
| 报告 | .md | `[日期]_[站点]_[关键词]_选品报告.md` | 可读结论与建议 |
| 数据 | .xlsx（多 Sheet） | `[日期]_[站点]_[关键词]_选品数据.xlsx` | 可验证、可透视、可逐条核对；每个 Sheet 含义与来源明确 |
| ⛔ 精简 | .html | `[日期]_[站点]_[关键词]_精简报告.html` | 快速浏览关键结论，可直接在浏览器打开分享 |

**HTML 精简报告输出规范**（⛔ 所有品类统一，参考充电宝 v2 / 充电器水准）：

HTML 精简报告须与 MD/Excel 同源数据一致，且**结构、样式、区块完整**，禁止仅「一段话 + 简单表格」的简陋版。必须包含以下区块与样式约定：

| 区块 | 必选 | 内容要求 | 样式/组件 |
|------|------|----------|-----------|
| **Header** | ⛔ | 主标题（品类+市场调研）+ 副标题（品牌 · 站点 · 日期 · 版本） | 居中；主标题 28px；副标题灰色 14px |
| **市场大盘** | ⛔ | 4–8 个核心 KPI（Top100 月销量、月销额、均价、中国卖家占比、Top3 集中度、新品占比、平均评分等） | **KPI 卡片网格**（kpi-grid + kpi-card）：每卡 label + value + note；具体数字，禁止「约」「少量」 |
| **多维产品分布** | ⛔ | 该品类 3–6 个属性维度，每维「主力段 / 销量占比」+「次要段 / 占比」+「关键洞察」一栏 | **表格**：表头维度、主力段、销量占比、次要段、占比、关键洞察；数字为具体值 |
| **消费者痛点** | ⛔ | 差评按维度归类的 Top 5–6 条，每条：标题 + 频率/占比（可选）+ 简短描述 | **痛点卡片网格**（pain-grid + pain-card）：排名圆标 + 标题 + 频率 + desc；可加 insight 框总结品牌机会 |
| **供需缺口/机会空白** | ⛔ | 交叉分析得出的 3–5 个高价值空白或薄供给组合；维度组合、状态（空白/薄供给）、竞品数、为什么值得关注 | **表格** + **gap-tag**（empty/scarce）标注状态 |
| **品牌/竞品格局** | ⛔ | Top 5–10 品牌：品牌、SKU 数、月销量、份额、定位、对我方含义 | 表格；必须有明确结论，不得只抄品牌名单 |
| **进入壁垒评估** | ⛔ | Review / 资金 / 技术 / 合规 / 供应链 / 品牌 六类壁垒，含等级、成本/时间、前置条件 | 表格 + 结论段落 |
| **Go / No-Go评分卡** | ⛔ | 5 维度评分、加权总分、结论、进入前提、Top3 风险与缓解 | 评分表 + 结论框 |
| **品牌建议** | ⛔ | 产品矩阵或策略建议（可按 Tier1/Tier2 或统一策略表）；规格、价格带、差异化一句 | **策略卡片**（tier-card）或**表格**；与 MD 报告建议一致 |
| **Footer** | ⛔ | 数据来源（Sorftime MCP）、采集日期、完整报告 .md 与 .xlsx 文件名 | 居中、小字、灰色、border-top |

**样式约定**：使用 CSS 变量统一主色与灰度（如 --blue, --gray-100）；容器 max-width 960px、padding 40px 24px；表格带圆角、斑马悬停、表头背景；响应式：小屏 KPI 两列、痛点单列。**参考实现**：使用当前任务输出的公开示例 HTML 结构作为基准，不引用品牌专属历史案例路径。

**自检**：交付前确认 HTML 含上述 6 个必选区块且无「少量」「约」等模糊表述；与同目录 MD 报告数据一致。

**存储位置**：统一为 `outputs/market-research/[品牌名]/[品类slug]/[version]/`；品牌未指定时建议使用 `outputs/market-research/_draft/[品类slug]/[version]/`。不要把正式交付文件直接散落在仓库根目录。

**Excel 多 Sheet 结构**（必须包含**数据来源说明**、**总结**与**明细**；凡「Top100」等须在数据来源说明中区分含义）：

| Sheet 名 | 类型 | 数据含义（须在「数据来源说明」中写明） | 主要字段 |
|----------|------|----------------------------------------|----------|
| **数据来源说明** | 必选 | 本文件所有 Sheet 的来源与含义 | Sheet名、数据来源工具、数据含义、关键参数、数据获取日期 |
| **市场概况** | 总结 | 类目+关键词汇总指标（category_search + keyword_detail） | 类目名称、NodeId、Top100月销量、Top100月销额、平均价格、…、数据获取日期 |
| **类目销量Top100_明细** | 明细 | **类目销量 Top100 榜单**（category_report，该类目按销量前 100 产品） | ASIN、标题、品牌、卖家、价格、月销量、月销额、评论数、星级、…、数据来源_工具、数据来源_含义 |
| **属性标注_Top100** | 明细（Step 1.5） | Top100 产品的结构化属性标注结果 | ASIN、标题、品牌、[各属性维度列]、置信度、验证方式（标题/product_detail/override）、数据来源_工具 |
| **交叉分析_矩阵** | 分析（Step 1.6） | 维度交叉表矩阵数据 | 维度A、维度B、产品数、月总销量、月总销额、平均价格 |
| **交叉分析_机会空白** | 分析（Step 1.6） | 供需缺口与机会空白点 | 维度A值、维度B值、产品数、判定（空白/薄供给/高需求低供给）、Top3品牌占比 |
| **关键词自然位产品_明细** | 明细 | **某关键词搜索自然位前 N 产品**（keyword_search_results，非类目榜） | ASIN、标题、品牌、价格、月销量、评论数、…、数据来源_工具、关键词、数据来源_含义 |
| **潜力产品_明细** | 明细 | 潜力产品列表（potential_product） | ASIN、标题、品牌、价格、月销量、评论数、潜力指数、数据来源_工具、数据来源_含义 |
| **竞品差评摘要** | 明细 | 某 ASIN 差评摘要（product_reviews, reviewType=Negative） | ASIN、评论类型、痛点维度、摘要或高频词、数据来源_工具、数据来源_含义 |
| **品牌_竞品格局** | 必选 | Top 品牌与竞品角色格局 | 品牌、SKU数、月销量、份额、角色定位、对目标品牌含义 |
| **竞品选择逻辑** | 必选（若有差评分析） | 差评分析所选竞品及选择理由 | ASIN、品牌、选择理由、竞品类型（量级标杆/功能差异代表/价格带覆盖/痛点参考）、覆盖维度、数据来源_工具 |
| **关键词对比_分段** | 必选 | 多维度关键词对比（大词/属性词/规格词/场景词） | 关键词、维度、月搜索量、CPC、自然位产品数、首页平均评论数、数据来源_工具 |
| **新品分析** | 必选（Step 1.7） | Top100 中新品（≤6个月）分布与趋势 | ASIN、标题、品牌、上线日期、上线天数、月销量、月销额、价格、[属性维度列]、新品友好度评级、数据来源_工具 |
| **进入壁垒评估** | 必选 | 六类进入壁垒汇总与启动前提 | 壁垒类型、等级、数据锚点、预估成本、预估时间、对目标品牌含义 |
| **Go-NoGo评分卡** | 必选 | 五维加权评分与结论 | 维度、权重、评分、依据、加权分、总分、决策 |
| **1688参考** | 明细 | 1688 相似品（ali1688_similar_product） | 标题、价格、链接、数据来源_工具、数据来源_含义 |

**数据来源说明示例行**：

| Sheet名 | 数据来源工具 | 数据含义 | 关键参数 | 数据获取日期 |
|---------|--------------|----------|----------|--------------|
| 类目销量Top100_明细 | mcp_sorftime_category_report | 类目销量 Top100 榜单（该类目实时销量前 100 产品） | amzSite=US, nodeId=xxx | 2026-02-12 |
| 关键词自然位产品_明细 | mcp_sorftime_keyword_search_results | 关键词「portable charger」搜索自然位前 50 产品 | amzSite=US, searchKeyword=portable charger | 2026-02-12 |

**命名与含义**：  
- 「类目销量 Top100」= category_report 返回的**该类目按销量排序的前 100 个产品**。  
- 「关键词 XXX 自然位」= keyword_search_results 返回的**该关键词搜索下的自然位产品**。二者不得混用；报告与 Excel 中凡出现 Top100/自然位等，须与数据来源说明一致。  
- 每个明细 Sheet 建议含列「数据来源_工具」「数据来源_含义」，或至少在「数据来源说明」中有一行对应。

**生成方式**：默认使用 skill 自带脚本，不再要求手工分别拼 MD / HTML / Excel。  

### 统一数据包格式（供 `render_deliverables.py` 使用）

#### v2 格式（推荐）

```json
{
  "schema_version": "2.0",
  "metadata": {
    "brand": "AORYVIC",
    "category": "wood-furniture-legs",
    "version": "v1_20260311",
    "date": "20260311",
    "site": "US",
    "keyword": "wood-furniture-legs",
    "created": "2026-03-11 16:20",
    "topic": "AORYVIC Wood Furniture Legs Sofa Legs",
    "type": "选品报告",
    "data_sources": [
      "sorftime MCP: category_report",
      "sorftime MCP: keyword_detail"
    ]
  },
  "chapters": {
    "ch01_executive_summary": { "conclusions": [...], "go_nogo_verdict": "GO", "one_line_summary": "..." },
    "ch02_market_overview": { "kpis": [...], "keyword_comparison": [...], "insight": "..." },
    "ch03_dimension_distribution": { "dimensions": [...] },
    "ch04_cross_analysis": { "matrices": [...] },
    "ch05_competitor_brands": { "competitor_selection_logic": [...], "brand_landscape": [...], "insight": "..." },
    "ch06_voc_pain_points": { "by_dimension": [...] },
    "ch07_opportunity_gaps": { "opportunities": [...], "scoring_method": "...", "insight": "..." },
    "ch08_strategic_recommendations": { "tiers": [...], "brand_strategy": "...", "timeline": "..." },
    "ch09_barriers_go_nogo": { "barriers": [...], "go_nogo_scorecard": [...], "verdict": "GO", "risks": [...] },
    "ch10_appendix": { "tool_calls": [...], "data_date": "...", "files": [...] }
  },
  "excel_sheets": {
    "数据来源说明": [{ "...": "..." }],
    "市场概况": [{ "...": "..." }]
  },
  "artifacts": {
    "top100_raw.json": [],
    "cross_analysis.json": []
  }
}
```

**完整 v2 Schema 详见** `references/payload_schema_v2.md`

#### v1 格式（向后兼容）

v1 payload 含 `report_markdown` / `report_html` 字段，无 `schema_version` 和 `chapters`。渲染器自动检测并走旧路径。

### 脚本职责

`render_deliverables.py` 会自动：

1. 按规范目录写入 `outputs/market-research/{brand}/{category}/{version}/`
2. v2 生成（4 个交付文件）：
   - `{date}_{site}_{keyword}_市场调研报告_{version}.md`（从 chapters 模板渲染）
   - `{date}_{site}_{keyword}_精简报告_{version}.html`（从 chapters 模板渲染）
   - `{date}_{site}_{keyword}_可视化看板_{version}.html`（Dashboard，从 chapters 构建 view-model）
   - `{date}_{site}_{keyword}_市场调研_数据_{version}.xlsx`
   - `excel_sheets_data.json`、`unified_payload.json` 与 `artifacts` 中声明的原始/中间 JSON
3. 校验：
   - v2: 四件套齐全 + chapters 10 章完整性 + 各章必填字段校验
   - Markdown 含 YAML 头
   - HTML 含 10 个必选区块
   - Excel 首 Sheet 为 `数据来源说明`
   - 文件名、目录结构符合 skill 规范

### 交付完成定义（DoD）

执行 `python skills/zach-product-research/scripts/render_deliverables.py all --input <payload.json>` 后，必须同时满足：

- 命令返回 `validate_ok`
- 正式交付文件位于 `outputs/market-research/...`
- v2: MD / HTML精简 / Dashboard看板 / XLSX 四件套都存在
- Excel 首 Sheet 为 `数据来源说明`
- 报告中引用的关键结论在 Excel 对应 Sheet 中可追溯

未调用的工具对应 Sheet 可省略或留空列表，不得用估算填充。

- 报告中的每个关键数字都应在对应 Sheet 中有对应行/列；所有结论可逐条或逐 ASIN 核对，且通过「数据来源说明」可确认来源与含义。

### 自测命令

每次修改脚本或模板后，至少运行一次：

```bash
python skills/zach-product-research/scripts/render_deliverables.py all --input skills/zach-product-research/evals/files/sample_payload_minimal.json --root .
```

只有返回 `validate_ok`，才说明交付链路没有被改坏。

## 风险与边界

- **本 Skill 不做**：不执行采购、不下单、不修改 Listing、不操作广告
- **以下情况升级人工**：
  - Go/No-Go 评分落在 CONDITIONAL GO 区间时，必须人工决策
  - 数据异常（如 Top100 返回不足 50 条）时标注数据缺失
  - 涉及合规/认证门槛高的品类，提醒用户确认
- **risk-level: low** — 纯分析/信息收集，不影响资金或账号

## 上游 / 下游

- **上游**（benefits-from）：无，本 Skill 是链路起点
- **下游**（建议后续）：
  - → `/zach-competitor-deep-dive` — 竞品深度拆解
  - → `/zach-pricing-strategy` — 定价策略
  - → `/zach-keyword-expansion` — 关键词拓展

## 可选的下游集成

本公开版只负责产出和校验四件套交付物，不内置任何私有系统写回逻辑。

如果你有自己的工作流系统，可以在交付完成后自行把这些字段接到：

- 飞书、多维表格或内部数据库
- Notion、Airtable、Google Sheets
- 自己的项目看板或选品归档系统

建议同步的最小字段包括：

- 调研关键词
- 站点
- 调研日期
- 月搜索量估算
- 主流售价区间
- 预估毛利率
- Go / No-Go
- 交付目录
- 报告文件名
- Excel 文件名
- Dashboard 文件名

## 完成后

报告完成状态（四选一）：
- **DONE** — 四件套全部通过 `validate_ok`
- **DONE_WITH_CONCERNS** — 交付完成但数据有缺失（如 Top100 不满 100 条）
- **BLOCKED** — Sorftime MCP 不可用或品类 ID 无法定位
- **NEEDS_CONTEXT** — 用户未提供关键词/品类/站点
