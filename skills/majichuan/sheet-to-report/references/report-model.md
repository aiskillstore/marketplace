# 请求与 report_model v2

> 本文是已实现接口参考，用于调用和核验当前行为；不替代已批准的技术规格或验收计划。

## 请求 JSON

```json
{
  "source_path": "business-detail.xlsx",
  "mode": "professional",
  "sheet_name": "经营明细",
  "period_type": "monthly",
  "audience": "经营管理层",
  "objective": "判断经营变化、定位结构驱动并形成下一周期动作",
  "analysis_intent": "business_review",
  "analysis_profile": "transactional_commerce",
  "semantic_contract": {
    "domain": "transactional_commerce",
    "table_grain": "order_line",
    "confirmation_status": "confirmed",
    "field_mappings": {
      "order": {"source_field": "订单号", "confidence": "high"},
      "product": {"source_field": "商品编码", "confidence": "high"},
      "customer": {"source_field": "客户编码", "confidence": "high"},
      "time": {"source_field": "下单时间", "confidence": "high"},
      "geography": {"source_field": "区域", "confidence": "high"},
      "quantity": {"source_field": "数量", "confidence": "high"},
      "unit_price": {"source_field": "单价", "confidence": "high"},
      "status": {"source_field": "订单状态", "confidence": "high"}
    },
    "cancellation_rule": {"values": ["已取消"]},
    "return_rule": {"values": ["已退货"]}
  },
  "date_column": "下单时间",
  "primary_metrics": ["销售额", "订单数"],
  "dimensions": ["区域", "商品编码"],
  "metric_contracts": [
    {"name": "销售额", "aggregation": "sum", "unit": "元", "role": "outcome", "direction": "higher_is_better"}
  ],
  "comparisons": ["period_over_period", "year_over_year"],
  "week_start": "monday",
  "timezone": "Asia/Shanghai",
  "incomplete_period_policy": "exclude",
  "theme": "corporate",
  "ppt_refinement": "offer_slideviber",
  "output_mode": "report+pptx"
}
```

相对 `source_path` 以请求 JSON 所在目录为基准。

| 字段 | 必填 | 允许值或约束 |
| --- | ---: | --- |
| `source_path` | 是 | `.csv` 或 `.xlsx` |
| `mode` | 否 | `quick / professional`，默认 `quick` |
| `sheet_name` | 否 | Excel 工作表名；CSV 忽略 |
| `period_type` | 是 | `weekly / monthly` |
| `audience` | 是 | 汇报受众 |
| `objective` | 是 | 本次要回答的问题 |
| `analysis_intent` | 否 | `business_review / exploration / engineering_regression`，默认 `business_review` |
| `analysis_profile` | 否 | `auto / general / retail_growth / transactional_commerce / content_operations / project_operations`，默认 `auto` |
| `semantic_contract` | 视场景 | 交易画像必须提供表粒度、字段映射和显式业务规则；`content_operations` 与 `project_operations` 为 experimental，必须显式 `confirmation_status=confirmed`，且固定使用 general 执行层 |
| `analysis_questions` | 否 | 专业模式可指定镜头、问题、优先级和所需字段；仍需通过证据门禁 |
| `date_column` | 是 | 可解析为日期的字段 |
| `primary_metrics` | 是 | 数值指标 1–6 个 |
| `dimensions` | 否 | 分类字段，建议不超过 4 个 |
| `metric_contracts` | 视指标 | `sum / ratio / average / last`；非加总指标必须提供 |
| `comparisons` | 否 | `period_over_period / year_over_year` |
| `week_start` | 否 | `monday / sunday` |
| `timezone` | 否 | 默认 `Asia/Shanghai` |
| `incomplete_period_policy` | 否 | `exclude / keep`，默认 `exclude` |
| `theme` | 否 | `corporate / clean / warm` |
| `ppt_refinement` | 否 | `standard / offer_slideviber` |
| `output_mode` | 否 | `report / report+pptx` |

## 一键与两阶段接口

默认一键生成：

```bash
python scripts/sheet_to_report.py --request request.json --output output
```

专业或内部流程可把确定性分析与叙事排序拆开：

```bash
python scripts/sheet_to_report.py --request request.json --output output --analyse-only
python scripts/sheet_to_report.py --output output --finalize story_plan.json
```

- `analysis_evidence.json` 保存来源 SHA、请求指纹、分析合同、质量决定、分析镜头、evidence catalog 和确定性 report seed。
- 默认 story plan 只保存已有 `slide_id / layout_id / evidence_ids / chart_ids / content_refs` 的选择与顺序；不能修改页面文案、数字、公式或 evidence。证据后的新判断走下方显式提案入口，不能解锁旧页面进行任意编辑。
- `--finalize` 会重新核对来源 SHA、请求指纹、页面身份、内容引用和证据范围。计划无效、越权或证据不足时返回结构化失败，不覆盖上一版已通过产物。
- 本地请求指纹与内容锁可检测任一未同步篡改；若攻击者能同步替换所有本地请求、seed、锁和哈希，则必须依赖外部不可变摘要或签名证明原始来源。

### 证据后判断提案

当已有结构比较但缺少经营判断时，由当前运行环境中的 AI 阅读 `analysis_evidence.json`，提交 `decisions.json` 数组；不连接新模型 API，不在代码里按行业或案例生成固定结论。

```bash
python scripts/sheet_to_report.py --output output --compose-decisions decisions.json
python scripts/sheet_to_report.py --output output --finalize output/story_plan.json
```

第一条只编译并创建 `story_plan.json`，已有文件拒绝覆盖，校验失败不创建计划；第二条重放原证据和提案后再执行原内容／模型／HTML门禁。`output` 中须已有分析阶段产出的 `analysis_evidence.json`。Python 调用为 `build_story_plan(evidence, decision_proposals=proposals)`。

每条提案严格使用以下字段，额外字段与自报 `achieved_depth / evidence 数值 / 章节归属` 拒绝：

- `proposal_id / question_id`：唯一提案 ID、受支持且已选择的真实问题 ID。
- `headline / operating_implication`：AI 形成的判断标题与资源、风险或验证意义；不是数字复述。
- `claim_type=diagnostic|inference`、`signal_type=risk|opportunity`、非空 `limitations[]`：只在表内证据范围作诊断／受限推断；没有因果证据不写因果保证。
- `proofs[]`：目前白名单为 `{"evidence_id": "已有证据ID", "view": "period_change"}`。单个期间细分证据自行固定其实际两期；完整趋势还需 `current_period / baseline_period`，必须在已计算序列与声明问题范围内。值、单位、对象和比较期由编译器读取；风险／机会必须至少有一个与指标方向相符的实际变化。其他证明形态不会被强转为期间证明。
- `action`：严格包含 `action_type / target / headline / rationale / steps[] / success_signal / guardrails[] / limitations[]`。`target` 必须精确等于一个已证明对象，不能拼接未观测对象；风险／机会方向也须由该对象的证明支持。步骤、成功信号与止损条件由 AI 明确填写，不得只写“继续关注”。数值事实由 proof 投影，提案业务语言不接受游离数值常量，包括中文百分数、倍数等数量表达；已观测对象名称里的数字不当作事实常量。该校验不替代实际经营判断的人工语义审查。

分析阶段用实际行成员登记 `decision_context[]` 的每问题完整证据组合及范围；编译阶段只引用该已计算组合，不能凭哈希猜测并集行数、重读源表或新增补查。证明本身必须具备真实驱动／细分，提案不能通过给普通趋势增加 risk/opportunity 标签升级深度。所附上下文证据也不替代提案实际引用的结构证明。

原 evidence、源／请求指纹、静态问题要求、指标与 scope 不改。派生故事保存 proposals 和 `base_content_hash`，重新计算真实深度、组合选择、摘要、章节、行动及内容锁；finalize 从原 evidence＋提案确定性重建，再校验计划，不接受自行重签的派生页面。最终选择仍可能删除提案或撤销其行动深度；阶段6的五案例与视觉验收尚未因此完成。

## report_model v2 顶层契约

```text
schema_version
source
request
data_profile
metric_contracts
analysis_profile
analysis_contract
quality_decisions
analysis_brief
candidate_question_graph
analysis_lenses
analysis_chapters
periods
period_overview
latest_snapshot
kpis
insights
actions
levers
charts
slide_plan
evidence_index
value_selection
content_validation
validation
```

### `analysis_contract`

- `analysis_intent`：业务复盘、探索或工程回归。
- `semantic_contract`：已确认的业务对象、表粒度、字段映射、置信度、过滤和状态规则。
- `adapter_id`、`adapter_maturity`、`execution_profile`：最终选定的适配器及其执行层。verified 可按已确认边界运行；experimental 只在确认分析计划后运行且使用 general 执行层；unavailable 明确失败。
- `available_objects`：本次可支持的问题对象；未确认对象不得进入正式叙事。

Quick 只能自动采用 high 置信度字段映射。Professional 使用 medium 前必须有 `confirmation_status=confirmed`；low 始终返回 `needs_input`。

### `quality_decisions`

通用层记录问题选择与缺失条件。`transactional_commerce` 另保存：

- 销售、客户、商品、地域等分域口径；缺客户 ID 不影响销售域，但不进入客户域。
- 负数量、取消、退货、零价、异常价格分别记录规则、数量与影响金额。
- 已确认过滤器的输入、保留、排除行数与影响金额；未确认候选规则不执行。
- 工程回归是否关闭业务镜头。

### `analysis_lenses`

每个镜头保存业务问题、优先级、所需对象／指标、图表要求、选择理由、状态与缺失条件；还记录 `required_depth`、`achieved_depth`、`answer_status`、`evidence_ids`、`followup_trace` 与 `stop_reason`。高优先问题未达到规定深度时只能继续补查或降级；`followup_trace` 仅记录白名单聚合路径、真实信息增量与停止信息，不含行级原始数据。

深度由 `analysis_depth.assess_depth` 根据实际证据形状复算：排名不自动成为驱动，计划用途／证据 ID／工具名／自报深度不构成证明；结构证据和同问题的实际经营判断须同时存在才可达到 4。`depth_gaps` 是运行结果，进入根请求重放白名单。联合指标必须具有相同实际样本指纹和时间／过滤上下文；旧证据复用不计新增信息。阶段 6 联调尚未完成，不能据局部探针通过声明全部深度门禁通过。

自定义问题和系统候选使用同一规划字段与真实前置条件检查；缺失字段、对象或指标时不能借已有事实宣称已回答。没有显式深度时，结果问题默认为 1、高优先问题为 4、其余为 3；显式值保留并接受严格类型校验。执行后停止原因来自受控执行器，不接受请求自行伪报终态。

`comparison_scope` 可省略，或声明严格的 `{period_field, baseline, current}`（两侧均为非空、不重复且互不重叠的周期字符串列表）；未知键、任意字符串和非法类型在入口失败。兼容两个明确名称：`latest_complete_period_vs_prior_period` 与 `latest_complete_vs_previous_and_year_over_year`。受控执行器从主分析已计算的完整周期窗口解析名称，使用已确认日期字段和相同周历；“前期”指上一实际保留周期，双比较生成独立环比／同比路径，绝不拼接基准分母。没有完整周期证明（例如keep策略）、缺日期授权或缺对应基期时明确停止；已成功比较保留。根请求的符号合同不改写，实际范围保存在各证据scope及执行轨迹中，finalize不重新解析日期或读取源表。

聚合信息身份比较实际样本指纹、指标合同、分组轴和比较角色；不因无效筛选的写法变化计作新信息。完整分组可证明集中度，集中度摘要不能反向证明完整分组；截断排名也不能冒充完整分组。主趋势按每个实际周期登记 `scope_bindings.periods`，可复用为同一样本的两期比较证明，但不能覆盖新子集。跨问题重复路径仍按批准的重复哈希停止策略处理。

已有期间证据可绑定到具体受支持的自定义 `question_id`，须匹配指标合同、声明维度、实际窗口与比较角色；指标 ID 别名可用，证据 ID 的文本没有业务含义。非期间问题与原始日期字段的显式比较继续交由既有补查执行器核对实际计算身份，不能仅凭指标或月份标签相同借证据。绑定不生成新证据、不增加深度，经营判断仍须独立成立。

洞察和行动的 `question_id` 进入正式共享字段与内容锁；行动从真实来源洞察／章节解析归属。内容 QA 按具体问题检查状态、页面归属及覆盖，不能用同镜头或同显示问题文本覆盖兄弟问题；缺少 ID 的旧记录仅在镜头唯一对应一个问题时回退。单问题业务页不得重标其他问题的判断；总览基线可引用支持性趋势事实，但这不算趋势问题已覆盖。

### `analysis_brief`、`candidate_question_graph` 与 `analysis_chapters`

- `analysis_brief` 固化受众、目标、决策节奏、交互模式和最小必要确认状态。
- `candidate_question_graph` 保存字段能力生成的候选问题、初扫信号、可回答性、价值评分、选择／拒绝理由和稳定问题 ID。
- `analysis_chapters[]` 是正式正文选择单位。每章至少包含 `chapter_id / question_id / decision_question / judgement / answer_status / required_depth / achieved_depth / fact_evidence_ids / driver_evidence_ids / segment_evidence_ids / operating_implication / report_language / chart_ids / action_ids / limitations / selection_status / claim_chart_alignment`。
- 核心章节必须 `answer_status=answered` 且达到深度门槛；否则只能降级。管理摘要通过 `key_conclusion_chapter_ids` 引用已选章节，正式行动通过 `source_chapter_ids` 回链来源章节。
- 核心章节下限独立为 4，不因问题把 required_depth 写低而降低。`judgement_insight_id` 绑定实际合格判断，`judgement` 和 `operating_implication` 从同一洞察投影，不得拿兄弟洞察最大深度授予浅标题。

### `value_selection` 与 `narrative_validation`

- `value_selection.selection_unit=analysis_chapter`；`analysis_chapters` 决定整章进入正文、附录或删除。旧的 `featured / appendix / dropped` 洞察分组保留兼容和章内追溯，但不再单独决定正文故事。
- `presentation_role=supporting` 的普通 KPI 事实最高只能进入 `appendix`；高优先问题覆盖不得把它提升为 `featured`。单一问题下自然达到正文门槛、证据独立且风险／机会信号互补的洞察可以同时保留；管理摘要按“lens＋signal_type”选择最多 3 条结论。
- 正式行动若声明 `source_insight_ids`，这些来源必须全部属于 `featured_insight_ids`；附录或删除项不得绕过中央选择直接升级为关键决策建议。
- `content_validation.narrative_validation` 记录页面故事顺序是否有效及相关阻断；未通过时不得输出正式叙事。

## 证据与内容审计

### 计算范围合同

- 新内核模型及分析证据产物必须包含 `scope_contract_version=analysis-scope-v1` 和顶层 `scope_catalog`；删除目录不能退出范围校验。
- 计算点用源表内部唯一行索引登记实际参与行集。持久化仅包含规则、父范围、时间／筛选／指标契约和行数，不包含原始行或行号。原子 `scope_id` 由规则及父范围生成，完整目录另外受内容锁保护。
- source／atomic／comparison 范围包含不透明 `population_sha256`，只用于同一源表内实际参与样本的等同性证明；不导出成员位图。不同指标恰好行数相同不等于同样本。非零售投影可复用完整主分析分组，真实 rows 进入摘要锁；含“其他”的截断排名不能证明全部对象排序。
- `source.loaded_row_count` 保留原始加载行数，独立于显式过滤后的 `data_profile.row_count`。主分析窗口统一日期、去重、完整周期及数值策略。交易排名进一步要求订单、金额及对应对象有效；客户覆盖不冒用销售总盘。质量影响分别绑定基准／受影响行与金额范围，绝对金额分母保存为 `baseline_absolute_amount`。
- `evidence_index[*].scope_id` 与 `sample_count` 必须对应；周期、质量和多指标比较用 `scope_bindings`／`metric_scope_bindings` 标明各自分母。补查路径身份包含有效分析窗口范围，不能跨窗口复用同一证据身份。
- 洞察、章节、图表和行动通过证据引用绑定 `scope_id / scope_disclosure`。章节合并校验 `fact_evidence_ids / driver_evidence_ids / segment_evidence_ids`；引用不同范围时生成显式 `comparison`，精确列出成员并按真实行集并集计数，声明分母分别计算。无证据且未入选的章节只能声明未作业务判断，不能冒领数字范围。
- 交易预处理原有 whole-source 质量目录保持原义，与新计算窗口范围并列，不用全源计数替换窗口计数。分析证据顶层与两个 seed 的范围／质量决定镜像必须一致；范围目录、各对象绑定及真实图表 payload 一并进入内容锁。所有补查的结果内层范围／行数必须与 evidence 顶层一致，完整结果及其 `result_hash` 受通用锁保护，不仅由某个适配器验证。

每个 `evidence_index` 记录至少包含：

- 唯一 evidence ID、证据类型和指标／维度对象；
- `formula / calculation`；
- `filter_scope`；
- `sample_count`、`affected_rows`、可用时的 `affected_amount`；
- `business_objects` 与 `limitations`；
- `quality_managed=true`。

洞察额外声明 `claim_type=fact|diagnostic|inference|hypothesis`、`evidence_strength=high|medium|low`、`value_score` 和限制。诊断／推断缺少交叉证据时必须降级为假设。

行动必须包含 `action_type / target / basis / rationale / steps / success_signal / guardrails / limitations / source_chapter_ids / evidence_ids / verification_signal / formal`。缺少来源章节、对象、依据、步骤、证据、成功信号或止损护栏时不得进入正式输出。

深度 5 由“真实 4 级判断 + 合格且最终保留的行动”证明，不以请求深度或空 action_ids 授予。生产顺序先准备缺省行动字段，再评估候选，最后在只保留／不新增行动的有界收敛中重算问题与章节；过滤掉行动必须撤回其深度贡献，不重新补查或改低 required_depth。finalize 只使用锁定模型，不读源或补查。

`formal` 必须严格为布尔 true；action_id 唯一且非空，步骤／护栏为非空字符串列表，限制为字符串列表，成功信号为非空字符串，不能把当前观测直接重复为试验成功条件。标准化只补真正缺省字段，显式空值或错误类型不得字符串化洗白。这些内容合同对深度 4 的正式行动同样有效。每个 source_insight_id 必须有同问题的所属章节；source_chapter_ids 与章节 action_ids 双向一致。最终问题仅评估归属本问题章节的行动，章节仅评估自己的行动和代表判断。

`content_validation` 阻断：

- 原始字段泄漏、纯数字复述、无证据因果或目标值；
- 不受支持镜头、重复结论、套话、空槽和未解析占位符；
- 悬空 evidence、非封面内容页无证据、标题与证据没有信息锚点。

## 分析意图与页面规则

- `business_review`：只有证据充足时生成 6–10 页自适应叙事；缺失镜头的可选页直接消失，不凑页数。
- `exploration`：允许输出带限制的可验证假设，不把相关性写成因果。
- `engineering_regression`：输出明确 QA dossier；允许少于 6 页，不生成经营洞察、经营杠杆或行动路线。
- `needs_input / insufficient_evidence` 是正常结构化结果，不是空报告。业务复盘不足 6 个有证据页面时停止渲染并列出补充问题。

`slide_plan[]` 将页面角色分别绑定到管理摘要、KPI、洞察、行动、图表或质量数据的确定路径，并记录 `slide_id`、`layout_id`、`story_role`、`evidence_ids`、`chart_ids`、`content_refs` 和 `visual_spec`。渲染器只能读取这些引用，不得从页面标题猜内容。

### `slide_plan[].visual_spec`

```json
{
  "eyebrow": "关键趋势",
  "tone": "data",
  "density": "standard",
  "display_claim": "收入变化与主要结构线索",
  "comparison_contexts": [
    {"kind": "yoy", "label": "同比", "current_label": "2025年6月", "baseline_label": "2024年6月"}
  ],
  "focus_evidence_ids": ["metric:收入:trend"],
  "chart_focus": {"series_name": "收入", "category_name": null}
}
```

- `eyebrow` 使用中文功能眉题。
- `focus_evidence_ids` 必须属于本页 evidence。
- `comparison_contexts` 只显示模型中实际存在的比较周期。
- 无法可靠确定视觉焦点或图表强调时留空，不得猜测。

## 时间、指标与业务阅读层

- `period_overview` 是分析期累计／整体 KPI；`latest_snapshot` 是最新完整周期 KPI 及实际比较周期，两者不得混用。
- 比率使用分子合计 ÷ 分母合计；均值遵守确认的权重；余额按日期取期末值。
- 同比结论同时显示实际最新周期与实际同比周期；子集与整体同页时明确范围，必要时保存同期全渠道基准。
- 证据优先：表内可回答的问题直接完成趋势、结构和交叉分析；只有确实缺字段、周期或业务事件证据时才说明无法验证。
- 常规趋势与结构优先使用 PowerPoint 原生可编辑图表；复杂图像必须标记不可编辑。

## 输出与一致性

- `report_model.json`：跨格式唯一语义真相源。
- `report.html` 与 `html_qa.json`：按问题章节组织的自包含业务简报，以及结构、资源、章节数量、单指标堆叠、编码型对象和内容检查。
- `report.pptx` 与 `ppt_qa.json`：标准可编辑汇报及字号、边界、重叠、正文对比度、角色、焦点、东亚换行和孤立标点检查。
- `slideviber_handoff.md`：可选精修交接；SlideViber 是可选精修层，不能改变结论。
- `run_result.json`：运行状态、产物清单和失败阶段。

HTML、PPTX 与 SlideViber 必须读取同一 `report_model.json`，且使用同一 `slide_id`、日期、数字、结论、行动与 evidence ID。美化只能改变视觉表达。

主题边界：HTML 使用唯一的标准商务样式，便于稳定阅读、复核与证据追溯；请求中的 `clean / corporate / warm` 只改变标准 PPT 与 SlideViber 的视觉主题，不改变 HTML。HTML 正文按已选 `analysis_chapters` 递进，普通 KPI 与 supporting 事实不得由渲染器自行升级；摘要与正式行动必须分别通过章节 ID 完成双向闭环，技术 ID 不显示给业务读者。

章节的 fact／driver／segment 证据必须有实际可读证明。`chart.evidence_ids` 仅是引用，不等于该图实际展示了证据；只有对象、指标和数值匹配的直接趋势／简单排名可以免表。期间或季节比较、交易驱动、质量诊断、带额外订单数／单均金额／占比的排名保留类型化数值证明表；共享表只渲染一次，并链接到前文唯一锚点。不能可靠投影的证据在写 HTML 前失败，不回读源表或重新计算。

摘要、章节、图表及行动的范围披露读取 `scope_catalog` 的结构化规则及分项绑定，不直接输出带工具／字段 ID 的原始定义。保留实际不连续期间、筛选含义、上级排除量、指标聚合与质量规则；输入行数不是订单／客户数或比率分母，组合范围不共用分母，质量绝对金额与净金额分开，季节性月均不得称为期间合计。确认的英文指标展示名保留，禁止多个不同指标统一改称“指标”。

HTML QA 按逐行单元格矩阵核对证明表对象、期间、单位和数值，并检查范围披露、唯一锚点及静态隐藏属性／行内样式。该静态检查不声称覆盖任意 CSS 级联、布局或阅读体验；浏览器逐章验收仍是独立门禁。

有合格核心章节但仍有未完成问题时，`narrative_selection.status=partial_coverage`，`unresolved_questions[]` 从真实问题与页面重新派生，记录问题 ID、业务问题、证据、回答状态、所需／实际深度、缺口、停止原因、说明及后续处理。HTML 必须明确展示问题、实际缺口与后续处理，不能把这类报告显示为全部问题已回答。附录保留事实不等于问题达到所需深度；这类处置也不计作已回答覆盖。处置元数据进入内容锁；删除、改写或伪装为 complete 均须被 QA 阻断。

## 失败与人工确认

- 缺日期字段、指标契约分子分母或交易必需字段：停止并列出缺项。
- 交易表粒度不清、字段映射低置信或 medium 未确认：返回 `needs_input`。
- 负向、取消、零价或异常交易没有已确认处理规则：保留并显式登记质量决定，不静默剔除。
- 未知聚合、布局、缺图、悬空 evidence、未解析占位符或标题—图表证据不一致：明确失败。
- 业务复盘证据不足：返回 `needs_input / insufficient_evidence`；工程回归改用 QA dossier，不伪装成经营分析。
- 多工作表联合、多层表头、合并单元格：先整理为单张单层表。
- 机器 QA 通过不等于人工视觉验收；正式发布前仍需逐页检查。

## 公开样例边界

快速体验和公开示例只使用 `scripts/generate_sample.py` 生成的固定种子模拟数据，并在产物中声明 synthetic provenance。真实或内部压力数据不进入 Skill 文案、示例和发布包。
