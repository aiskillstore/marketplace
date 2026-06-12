---
name: zach-feature-demand-validator
description: |
  功能需求真伪验证器。用三维数据（Review/关键词/社区）验证微创新是否真实需求。
  使用时机：品类选定后评估微创新、竞品分析发现差异点后判断要不要跟进。
  触发词：/zach-feature-demand-validator
benefits-from: [zach-product-research]
user-invocable: true
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep, WebSearch, WebFetch, mcp__sorftime__product_reviews, mcp__sorftime__keyword_detail, mcp__sorftime__keyword_extends]
risk-level: low
---

## 前置建议

本公开版 Skill 是自包含的，不依赖任何私有工作区文件、内部参考库或品牌专属协议。

开始执行前，建议先阅读本 Skill 自带的参考材料：

- `references/judgment_criteria.md` — 三维需求判断标准
- `references/report_template.md` — 报告结构
- `references/csv_schema.md` — 交付 CSV 结构
- `references/review_fallback_pack.md` — 无 Sorftime 时的评论证据包格式

## 定位

亚马逊卖家的产品开发，大多数时候不是做颠覆式创新，而是在现有供给上做微创新：

- 加一个小功能
- 补一个小结构
- 优化一个小体验

危险点也恰好在这里。很多功能看起来合理，但很可能只是卖家自己的想象，不是消费者真实在意的点。

这个 Skill 的定位，不是帮你发明新物种，而是判断：

**这个微创新，到底是不是用户真的在意。**

它通过三个独立维度交叉验证，避免“感觉有需求就开模”。

| 维度 | 首选数据源 | 无 Sorftime 时的替代方案 |
|------|-----------|----------------------|
| Review 信号 | Sorftime `product_reviews` | WebSearch + WebFetch 主动抓取 Amazon Review 页面，或用户提供 `review_source_pack` |
| 关键词信号 | Sorftime `keyword_detail` / `keyword_trend` / `keyword_extends` | Google Trends（WebFetch）+ Amazon Autocomplete（WebSearch）+ 第三方搜索量估算 |
| 社区信号 | WebSearch（Reddit + Quora） | 继续可执行（不依赖 Sorftime） |

## 上游 / 下游

- **上游**：`zach-product-research`、`zach-competitor-deep-dive`
- **下游**：`zach-new-product-listing-writer`

---

## 执行优先级

### 路线 A：Sorftime 完整版

适用条件：当前环境可调用 Sorftime MCP。

1. Review 维度走 Sorftime `product_reviews`
2. 关键词维度走 Sorftime 关键词工具
3. 社区维度走 WebSearch

### 路线 B：无 Sorftime 替代版

适用条件：当前环境没有 Sorftime MCP。

1. Review 维度：优先用 WebSearch + WebFetch 主动抓取 Amazon Review；若抓取失败，再降级到用户提供的 `review_source_pack`
2. 关键词维度：用 Google Trends + Amazon Autocomplete + 第三方工具获取免费搜索数据
3. 社区维度：继续走 WebSearch

**注意**：替代版的数据精度不如 Sorftime（无法拿到精确周搜索量和 CPC），但三个维度都有真实数据支撑，不存在”空白维度”。报告中需标注数据来源差异。

---

## 输入方式

### 业务输入

支持两类：

| 输入方式 | 示例 | 处理逻辑 |
|---------|------|---------|
| 品类 + 功能描述 | `air fryer + steam feature` | 先找市场上是否已有带该功能的产品 |
| ASIN + 功能描述 | `B0XXXX + self-cleaning` | 直接围绕指定产品和相邻竞品验证 |

默认站点：`US`

### Review fallback 输入

当 Sorftime 不可用时，用户需要提供本地评论证据包：

```text
review_source_pack/
├── source_manifest.json
└── raw/
    ├── reviews.csv
    ├── reviews.txt
    └── reviews.html
```

详细格式见 `references/review_fallback_pack.md`。

---

## 执行流程

### Step 0：解析任务与构造关键词

1. 确认输入是“品类 + 功能”还是“ASIN + 功能”
2. 确认站点，默认 `US`
3. 基于 `references/keyword_construction_guide.md` 构造 3-5 个英文关键词变体
4. 判断当前走 Sorftime 完整版还是 Review fallback 降级版

### Step 1：Review 信号采集

#### 1.1 Sorftime 完整版

1. 若用户给的是品类：
   - 调 `product_search` 找含该功能的产品
   - 优先选 3-5 个月销高、评论多、标题明确带功能词的 ASIN
2. 若用户给的是 ASIN：
   - 直接用该 ASIN
   - 必要时调 `product_detail` 确认功能是否真实存在
3. 对每个目标 ASIN 调 `product_reviews`
4. 把返回结果保存为 JSON，再调用脚本：

macOS / Linux:
```bash
python3 skills/zach-feature-demand-validator/scripts/parse_reviews.py \
  --input <reviews.json> \
  --asin <ASIN> \
  --keywords "steam,steamer,steaming" \
  --source-url "sorftime://product_reviews/<ASIN>" \
  --output <数据源目录>/01_review_信号_原始数据.csv
```

Windows:
```powershell
py -3 skills/zach-feature-demand-validator/scripts/parse_reviews.py `
  --input <reviews.json> `
  --asin <ASIN> `
  --keywords "steam,steamer,steaming" `
  --source-url "sorftime://product_reviews/<ASIN>" `
  --output <数据源目录>\01_review_信号_原始数据.csv
```

#### 1.2 无 Sorftime 时的 Review 采集

**核心原则：按功能关键词定向选 ASIN，不随机抓。**

Review 采集的意义在于验证"用户有没有在意这个功能"，所以必须定向找两类产品：
- **A 类：已带该功能的产品** → 看用户对这个功能的真实评价（好评提到了？差评说没用？）
- **B 类：同品类但不带该功能的竞品** → 看用户有没有抱怨"缺了这个功能"

随机抓高销量产品的 review 不会命中功能相关内容，没有分析价值。

**第一步：用功能关键词定向搜索 ASIN**

1. 用 WebSearch 搜索 `amazon.com [品类] [功能关键词]`
   - 例：验证"空气炸锅+蒸汽"→ 搜索 `amazon.com air fryer steam`
   - 从结果中提取 2-3 个**已带该功能**的真实 ASIN（A 类）
2. 再搜索 `amazon.com [品类] best seller`，提取 2-3 个**不带该功能但销量高**的 ASIN（B 类）
   - 这些是对照组，看主流产品的 review 里有没有人提到"希望有这个功能"
3. ⛔ 严禁使用 `B0XXXXX` 等占位符，必须拿到真实可验证的 10 位 ASIN
4. 确认每个 ASIN 的产品名、是否带目标功能，记录到报告中

**第二步：抓取 Review**

对每个 ASIN：
- 用 WebFetch 尝试访问 `https://www.amazon.com/product-reviews/<ASIN>/ref=cm_cr_dp_d_show_all_btm?reviewerType=all_reviews&sortBy=recent&pageNumber=1`
- 如果 Amazon 页面可访问，提取评论内容（标题、正文、星级、日期）
- 如果被反爬拦截，用 WebSearch 搜索 `site:amazon.com "<ASIN>" reviews` 获取评论摘要
- 还可搜索第三方评论聚合站（reviewmeta.com、fakespot.com）

**第三步：数据量要求**

- A 类（带功能）：每个 ASIN 至少 15-30 条 review
- B 类（不带功能）：每个 ASIN 至少 15-30 条 review
- 总量目标不低于 80 条
- 如果单个 ASIN 返回不足，增加同类 ASIN 补足
- 实际采集量和 A/B 分类写入报告

**第四步：脚本解析**

将采集到的 review 整理为标准 JSON，再调用 parse_reviews.py 脚本（同 1.1）

**降级路径：用户提供 review_source_pack**

仅当 WebSearch + WebFetch 均无法获取足够 review 数据时，才要求用户手动提供证据包：

1. 要求用户提供 `review_source_pack/`
2. 检查 `source_manifest.json` 是否包含 ASIN、站点、导出时间、来源 URL、导出方式
3. 调脚本统一解析原始证据：

```bash
python3 skills/zach-feature-demand-validator/scripts/parse_review_source_pack.py \
  --pack <review_source_pack> \
  --keywords "steam,steamer,steaming" \
  --output <数据源目录>/01_review_信号_原始数据.csv
```

支持的原始文件格式：CSV、TXT / Markdown、HTML

#### 1.3 Review 判定

判定标准见 `references/judgment_criteria.md`，核心仍是：

- 功能提及率
- 需求表达数（如 `wish it had`）
- 正负反馈分布

### Step 2：关键词信号采集

#### 2.1 有 Sorftime 时

对关键词变体依次调用：

- `keyword_detail`
- `keyword_trend`
- `keyword_extends`

再用脚本导出标准 CSV：

```bash
python3 skills/zach-feature-demand-validator/scripts/generate_keyword_csv.py \
  --type detail \
  --data <detail.json> \
  --source-ref "keyword_detail:steam air fryer" \
  --output <数据源目录>/02_keyword_信号_搜索量数据.csv
```

#### 2.2 无 Sorftime 时的替代采集

关键词维度不能留空。没有 Sorftime 时，通过以下免费数据源获取替代数据：

**搜索量估算（替代 keyword_detail）：**

1. 用 WebSearch 搜索 `"[功能关键词]" amazon search volume` 或 `"[功能关键词]" keyword search volume`
2. 从 SEO 工具页面（如 Ahrefs 免费版、Ubersuggest、Keywords Everywhere 公开数据）获取大致搜索量级
3. 用 WebFetch 尝试访问 `https://trends.google.com/trends/explore?q=[关键词]&geo=US` 获取 Google Trends 相对热度
4. 在报告中标注数据来源为"第三方估算"，精度不如 Sorftime

**趋势数据（替代 keyword_trend）：**

1. Google Trends 是核心替代源：用 WebFetch 获取过去 12 个月的趋势曲线
2. 对每个关键词变体都查 Google Trends，记录趋势方向（上升/平稳/下降）
3. 用 WebSearch 搜索 `"[功能关键词]" trend 2025 2026` 获取行业讨论中的趋势判断

**延伸词（替代 keyword_extends）：**

1. 用 WebSearch 搜索 `amazon autocomplete [功能关键词]`，或直接搜索 `[功能关键词]` 观察搜索引擎的自动补全建议
2. 用 WebSearch 搜索 `"[功能关键词]" related searches` 获取相关搜索词
3. 用 WebFetch 尝试访问 Amazon 搜索页，观察搜索建议下拉框

**CSV 输出要求不变**：三个 CSV（02/03/04）仍需生成，来源类型标为 `google_trends` / `web_search_estimate` / `amazon_autocomplete`，不标为 Sorftime。

⛔ 关键词数据不得伪造。如果某个数据源确实无法访问，该字段标为"采集失败 + 原因"，不填 N/A 了事。

### Step 3：社区信号采集

1. 用 WebSearch 搜索 Reddit / Quora
2. 保留标题、URL、发布日期、态度摘要、查询词
3. 用脚本导出标准 CSV：

```bash
python3 skills/zach-feature-demand-validator/scripts/generate_community_csv.py \
  --data <community.json> \
  --source-ref 'site:reddit.com "air fryer steam"' \
  --output <数据源目录>/05_社区_信号_讨论摘要.csv
```

### Step 4：综合判定

| 判定 | 条件 | 建议 |
|------|------|------|
| ✅ 强真需求 | 三个维度均有正面信号 | 值得投入开发 |
| ⚠️ 弱真需求 | 两个维度有信号，一个维度缺失 | 可考虑，但要承认风险 |
| ❓ 待验证 | 只有一个维度有信号 | 先别上大投入 |
| ❌ 伪需求 | 没有正面信号，或已有明显负面信号 | 不建议投入 |

如果走无 Sorftime 替代版，综合结论必须标注”关键词数据来源为 Google Trends / 第三方估算，精度低于 Sorftime”。

### Step 5：生成报告

交付固定包括：

1. `[日期]_[品类]_[功能]_功能需求验证报告.md`
2. 五个标准 CSV
3. 若走 Review fallback，还要附上：
   - `review_source_pack/source_manifest.json`
   - `review_source_pack/raw/*`

### Step 6：交付校验

```bash
python3 skills/zach-feature-demand-validator/scripts/validate_deliverables.py --dir <output_dir>
```

只有返回 `validate_ok` 才算完成。

---

## 标准输出

```text
outputs/feature-validation/
├── YYYY-MM-DD_[品类]_[功能]_功能需求验证报告.md
└── YYYY-MM-DD_[品类]_[功能]_数据源/
    ├── 01_review_信号_原始数据.csv
    ├── 02_keyword_信号_搜索量数据.csv
    ├── 03_keyword_信号_趋势数据.csv
    ├── 04_keyword_信号_延伸词.csv
    ├── 05_社区_信号_讨论摘要.csv
    └── review_source_pack/               # 仅 fallback 场景需要
        ├── source_manifest.json
        └── raw/
```

所有 CSV 都必须包含：

- `数据来源`
- `来源类型`
- `来源链接/查询词`
- `原始文件名`
- `采集时间`

---

## Script Directory

| 脚本 | 用途 |
|------|------|
| `scripts/parse_reviews.py` | 解析 Sorftime `product_reviews` JSON |
| `scripts/parse_review_source_pack.py` | 解析手动导出的 Amazon Review 证据包 |
| `scripts/generate_keyword_csv.py` | 关键词数据导出为标准 CSV |
| `scripts/generate_community_csv.py` | 社区讨论导出为标准 CSV |
| `scripts/validate_deliverables.py` | 校验 MD、CSV 和 fallback 证据包是否完整 |
| `scripts/WINDOWS_USAGE.md` | Windows 运行说明 |

---

## 硬性规则

1. ⛔ Sorftime 可用时，Review 和关键词维度优先走 Sorftime
2. ⛔ 无 Sorftime 时，三个维度都必须有真实数据采集，不允许任何维度留空或填 N/A
3. ⛔ **ASIN 必须是真实可验证的 10 位编号**（如 B0PUBLIC01），严禁使用 MULTI、UNKNOWN、B0XXXXX 等占位符或品牌名。`parse_reviews.py` 和 `validate_deliverables.py` 均会强制校验 ASIN 格式，非法值将导致脚本报错退出
4. ⛔ **多 ASIN 场景必须按 ASIN 分组处理**：每个 ASIN 单独调用 `parse_reviews.py --asin <真实ASIN>`，或在 JSON 中为每条 review 添加 `ASIN` / `__asin` 字段。禁止用一个占位符覆盖所有行
5. ⛔ Review 采集目标不低于 80 条（跨 3-5 个 ASIN），实际采集量写入报告
6. ⛔ Review 原始数据必须走 Python 脚本解析，不能把大段原始 JSON / HTML 直接塞进报告
7. ⛔ 每个 CSV 必须保留可核查来源字段，来源类型必须真实反映数据来源（sorftime_mcp / google_trends / web_search_estimate 等）
8. ⛔ 负面信号必须写入报告
9. ⛔ 所有结论都要引用具体数据，不允许空泛判断

---

## 参考文档

- `references/csv_schema.md`
- `references/report_template.md`
- `references/judgment_criteria.md`
- `references/keyword_construction_guide.md`
- `references/review_fallback_pack.md`

## 风险与边界

- **本 Skill 不做**：不做产品开发决策，只验证需求真伪
- **risk-level: low** — 纯分析/信息收集

## 上游 / 下游

- **上游**：`zach-product-research` — 提供品类方向
- **下游**：→ 产品开发决策（人工）→ `/zach-new-product-listing-writer`

## 完成后

报告完成状态：DONE / DONE_WITH_CONCERNS / BLOCKED / NEEDS_CONTEXT
