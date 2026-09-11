---
name: sheet-to-report
description: Use when a user wants to turn one structured Excel or CSV table into an evidence-traceable weekly or monthly HTML analysis report and, optionally, an editable business PPTX. Suitable for Excel 数据分析、周报、月报、阶段复盘、数据简报 或汇报 PPT; not for medical, investment, employee-rating, or other high-stakes advice.
license: MIT
compatibility: Requires Python 3.10+; standard PPT export also requires Node.js 18+ and python-pptx 1.0+; optional SlideViber is installed separately.
metadata:
  version: "0.2.2"
---

# 数据分析&汇报小助手

将单张结构清晰的 `.xlsx` 或 `.csv` 转成可追溯的 HTML 决策简报，并按需生成达到职场汇报标准的可编辑 PPTX。

## 30 秒了解

- **适合谁：** 需要做周报、月报、活动复盘或阶段经营汇报的运营、销售、产品及业务负责人。
- **能得到什么：** 一份可离线阅读的 HTML 分析简报；按需生成可编辑标准 PPT；还可选择单独安装 SlideViber 继续制作美化版。
- **怎样开始：** 用户只需提供一张结构清晰的 Excel／CSV，并说明汇报对象与想解决的问题。Agent 先检查字段和口径，只在歧义会改变结论时提问。
- **实际效果：** [在线查看完整合成案例](https://majichuan.github.io/sheet-to-report/)，包括 HTML、标准 PPT 与 SlideViber 美化版的同源对照。

## 为什么选择 sheet-to-report

**帮你看懂业务变化，串起汇报主线，也把下一步讲清楚。**

- **抓住值得关注的问题——找问题**

  围绕你的汇报目标，从表中寻找重要变化、机会和风险。发现异常后，在数据支持的范围内继续按时间、渠道、人群或商品细分核查，并选择合适的图表说明。
- **结论有依据，判断有边界——核依据**

  先核对指标含义和比较范围，再组织结论。关键数字可以追溯到计算依据；数据不足时说明哪些还无法判断，避免把猜测当成事实。
- **把零散发现串成清楚的汇报主线——串主线**

  将整体表现、关键变化、细分证据和经营含义逐层展开，让读者顺着“发生了什么—哪些因素值得关注—依据是什么—下一步怎么做”理解整份报告。图表与文字前后呼应，汇报时更容易让听众跟上。
- **建议具体到行动和验证——落行动**

  说明针对哪个业务环节、建议怎么做、观察什么指标，以及什么情况下需要调整，帮助你把分析结果转成下一步工作安排。
- **一份分析，衔接阅读与汇报——出报告**

  按需生成离线 HTML、可编辑标准 PPT，并可另行安装 SlideViber 进一步美化。三类产物沿用同一套分析依据，并校验关键数字、口径与结论的一致性。

第一次使用可以直接说：

> 请用 sheet-to-report 分析这份 Excel，面向业务负责人做月度复盘。先检查字段和数据范围，只向我确认会改变结论的口径；先生成 HTML，如需 PPT 再按主题选择流程继续。

Agent 执行时先运行与目标对应的环境预检；失败时保留已经通过的产物，并按[快速帮助与故障定位](references/quick-help.md)用普通用户能理解的语言说明“卡在哪一步、影响什么、下一步做什么”。

## 开始前确认

先明确分析意图，避免把工程测试包装成业务结论：

- `business_review`：回答经营变化、结构驱动、风险与行动；正式 HTML 按有证据的业务问题组织章节，不预设页数。
- `exploration`：在已确认语义范围内探索可验证线索；证据不足的内容降级为带限制的假设。
- `engineering_regression`：只输出计算合同、数据质量与回归核验 dossier，不生成经营洞察或行动建议。

仅向用户呈现两种选择：

- **直接分析**：自动扫描字段与少量预览；只采用高置信语义，存在歧义时返回结构化待确认问题。
- **确认分析计划**：确认语义合同、分析问题、指标契约、受众、目标、维度、比较方式和主题后再执行。中置信字段只有在确认后才可使用，低置信字段始终需要确认。

无论哪种模式，不能可靠判断时都要询问用户，不猜口径：

- 汇报目标、受众和 `analysis_intent`
- 周报或月报、日期字段、未完成周期策略
- 1–6 个核心指标及其单位、聚合方式、分子分母
- 0–4 个拆解维度
- 只要数据简报，还是同时需要可编辑 PPTX

先查看字段名和少量预览。可运行 `python scripts/sheet_to_report.py --inspect path/to/data.xlsx` 获取机器可读的候选字段与待确认问题。若发现姓名、手机号、邮箱、证件号、详细地址等个人信息，提示用户先删除、脱敏或改用合成数据。脚本本身不调用外部 API；运行它的 AI 平台仍可能读取用户提供的文件，应遵循所在平台的隐私政策。

## 受控混合分析链路

执行顺序固定为：

`分析意图 → 语义能力与质量决定 → 分析简报 → 候选问题图 → 确定性计算与受控补查 → 决策章节 → 行动合同 → 内容 QA → HTML/PPT`

- `analysis_profile=auto` 是默认入口。`general`、`retail_growth` 与 `transactional_commerce` 为 verified；`content_operations` 与 `project_operations` 为 experimental，必须经“确认分析计划”后在 `general` 执行层运行；unavailable 必须明确失败，不能伪装为通用分析成功。
- 交易表必须声明表粒度与订单、数量、单价等字段映射。销售域与客户域分开：缺客户 ID 的交易仍可保留在销售口径，但不得伪造匿名客户。
- 负数量、取消、退货、零价和异常价格分别记录数量、影响金额、规则与范围；任何排除都必须来自已确认的白名单规则，不能静默清洗。
- 新比率请求明确单行分母为零的处理。全量投入除以全量产出等总量比率使用 `zero_denominator_policy=include_in_totals`，保留零产出行的投入；仅汇总分母为零时不可计算。旧请求未指定时保留 `exclude_row` 兼容口径，不能把其数值当作全量成本效率。
- 分析问题只能从已确认的业务对象、字段、指标和时间覆盖中选择。确定性计算负责数字与公式，叙事层只能选择、排序和压缩证据，不得自创数字、公式、因果或行业基准。
- 高优先问题按“事实—驱动—细分—经营含义”记录 `required_depth / achieved_depth`。深度不足且仍有合法表内路径时必须继续受控补查；没有真实信息增量时降级，不能用非空文本冒充回答。
- 正文选择单位是业务章节，不是孤立指标或单条洞察。核心诊断应说明问题、判断、证据与经营含义；行动可由多个章节共同支持，背景章节无需制造行动。
- `report_model.json` 是一次生成的内容真相源，洞察、行动、图表均引用可解析的 evidence ID。新版 `html-chapters/1` 通过独立 `chapter-presentation/1` 接续标准PPT或SlideViber，不交给旧PPT消费者；旧模型只保留原兼容路径。

## 执行流程

1. 要求 Python 3.10 或更高版本。先运行环境预检：

   ```bash
   python scripts/environment_check.py --target html
   ```

   PPT阶段另运行 `python scripts/environment_check.py --target standard`；美化版改为 `--target slideviber --slideviber-dir <已单独安装的SlideViber目录>`。Node不在PATH时传 `--node <Node可执行文件>`。检查按目标区分：HTML不要求PPT/Node；标准完整稿及主题小样使用公开python-pptx与Node，不需要Codex私有工具。预检通过不代表字体、浏览器或实际视觉已验。

2. 预检提示缺少依赖时，再运行 `python -m pip install -r requirements.txt`；不要把依赖或生成文件打包进 Skill。普通安装不要求Git；版本追溯保留文件指纹，Git信息只在本Skill自身仓库可读取时补充，缺失不冒充已知版本或干净工作区。
3. 读取 [请求与报告模型](references/report-model.md)，确定意图、分析画像与语义合同。选择“直接分析”时可先执行：

   ```bash
   python scripts/sheet_to_report.py --inspect path/to/data.xlsx
   ```

4. **正式 HTML 默认由宿主 AI 驱动**。先读 [宿主 HTML 分析合同](references/html-analysis.md)，显式使用本 Skill 绝对目录。初扫 → 阅读证据并逐问题判断充分性 → 必要时受控补查 → 绑定最终快照提交故事 → compose → finalize。无需用户手写问题或提案；脚本只做确定性计算，不会独立调用模型。不允许手修最终模型或 HTML。`html-chapters/1` 与旧 PPT 页型解耦；背景无需制造行动，数字仍必须绑定证据。以下一键入口保留为旧分析/兼容用途，不代表完成新版宿主 AI 分析：

   ```bash
   python scripts/sheet_to_report.py --request path/to/request.json --output path/to/output
   ```

5. **以下为旧模型兼容入口，不接续上面的新版 HTML 流程。** 经确认的旧分析流程可分两阶段运行。`--analyse-only` 只生成确定性 `analysis_evidence.json`；`--finalize` 只接受与来源哈希、请求指纹和 evidence 严格绑定的 story plan：

   ```bash
   python scripts/sheet_to_report.py --request path/to/request.json --output path/to/output --analyse-only
   python scripts/sheet_to_report.py --output path/to/output --finalize path/to/story_plan.json
   ```

   默认 story plan 只能重排已有内容。若表内已有结构证据却缺经营判断，先由当前 AI 阅读冻结证据，按 [证据后判断提案](references/report-model.md#证据后判断提案) 提交结构化 proposals，再用 `--compose-decisions` 编译故事计划。数字、范围、深度和章节归属仍由脚本生成与校验；不得直接改 seed 或内容锁。来源不匹配、引用越权、缺少必需页面角色或内容证据不足时必须失败，不能静默生成。
6. 新版 HTML 在组织提案前读取 [共享图表规格](references/chart-spec.md)。按判断任务与数据条件选图，用 `chart-spec/1` 记录选择理由、限制、尺度和重点；新运行不能退回旧细横条合同。柱图、分布、构成、关系和贡献图各有数据约束，不按行业名或固定图型配额选择。图中分箱、比例和累计坐标只消费已计算证据；能力不足须说明原因，不能交给渲染器临时计算。检查 `report_model.json`、`report.html`、`html_qa.json` 和数据质量提示。实际审核关键图能否支持判断，优先桌面；手机只查基础可用性。机器 QA 通过不等于实际阅读验收完成。
7. 若用户选择 PPTX，新版 HTML 先读取 [章节到演示投影](references/chapter-presentation.md)，使用独立 `chapter-presentation/1` 及对应新消费者，不把模型直接送入旧 `build_pptx.py`。按当前已验证能力执行，显式拒绝尚未支持的布局或图形条件。交付 `report.pptx` 与 `ppt_qa.json`；标准版必须先独立通过字号、边界、重叠、占位符、标题—图表证据一致性、内容锁定与中文排版门禁。
8. 生成任何PPT前读取 [主题选择](references/ppt-theme-selection.md)。用户明确说“你决定、直接生成”且无已确认偏好时，使用默认清晰商务；已明确指定或已确认沿用的风格优先。正常情况下若没有指定风格、也未授权代选，先给候选方向及每个方向的封面＋真实图表两页PPT小样，等待用户选择，不限重要汇报。标准版通过后，若用户尚未表态，简短说明可通过 SlideViber 继续生成美化版，是否安装与继续由用户选择；已拒绝时不重复询问。美化版继承同一已确认选择，保留标准稿、完整内容和来源校验；新版章节模型使用 [章节到演示投影](references/chapter-presentation.md) 的独立构图消费者，旧模型使用 `slideviber_handoff.md`。预览及实际PPT核验后另存 `report-polished.pptx`，不重复审批。
9. 美化稿在同一显示尺寸下对照标准稿，检查视觉焦点、图文对应、图表可读性及整稿节奏；只换颜色、分辨率或导出器不算美化完成。精修版导出后运行对应合同的一致性检查；缺少日期、关键数值、判断标题或 evidence 对应关系时不得交付。新版章节投影使用 `chapter_presentation_qa.py` 并传入绑定的 `--scene`；以下命令仅用于旧模型：

   ```bash
   python scripts/slideviber_consistency.py --model report_model.json --pptx report-polished.pptx --output slideviber_qa.json
   ```

## 自适应叙事与内容门禁

本节页数、旧字段与 featured 限制描述旧模型兼容行为。新版 `html-chapters/1` 以宿主 HTML 合同为准，背景可进正文、无需制造行动；主图设计与正文事实选择相互独立。

- 6–10 页只适用于证据充足的 `business_review`；页面由已选择的分析镜头和直接证据决定，不凑固定页数。证据不足返回 `needs_input / insufficient_evidence`，并保留上一版已通过产物。
- `engineering_regression` 使用明确的 QA dossier，允许少于 6 页；不得出现经营复盘、管理摘要、经营杠杆或行动路线等业务包装。
- `analysis_brief` 固化受众、目标、节奏与最小必要确认；`candidate_question_graph` 保留问题来源、初扫信号、选择／拒绝理由和字段支持。
- `analysis_lenses` 记录问题、优先级、所需对象、指标、深度缺口、补查轨迹和停止原因。未选择、不可用或深度不足的问题不得伪装成核心回答。
- `analysis_chapters` 以问题为单位组合事实、驱动、细分、经营含义、图表和行动；管理摘要只引用已入选章节。
- evidence 必须记录公式、过滤范围、样本数、受影响行数／金额、业务对象和限制；事实、诊断、推断、假设分别声明 `claim_type`、`evidence_strength` 和限制。
- 行动必须包含类型、对象、依据、解释、步骤、成功信号、止损护栏、限制、来源章节和 evidence ID；缺任一项不得进入正式输出。行动对象回答“针对谁或哪个业务环节采取措施”，必须与来源证据相连；不可用负责人替代。执行分工仅在有依据时单列“建议协同角色”，未知时省略，不编造组织安排。
- `content_validation` 阻断原始字段泄漏、数字复述、无证据因果、重复结论、套话、空槽、悬空 evidence 和未解析占位符。

## HTML 业务呈现规则

- 图表先按本页要证明的关系和数据语义选择，再核对目标输出能力；保留候选取舍理由，不以图型数量作为质量指标。HTML、标准PPT与SlideViber复用同一来源投影。十类图型的选择依据见[共享图表合同](references/chart-spec.md)，实际容量、原生图表与可编辑形状的区别见[跨格式能力](references/chapter-presentation.md#图表跨格式能力)。换数据后重新选型，不能照搬既有案例图表清单。
- HTML 只生成一套统一的标准商务样式；主题选择只作用于标准 PPT 与可选的 SlideViber 美化版，不作用于 HTML，也不因换 PPT 主题生成多份 HTML。
- 主标题是报告身份与分析主题，不得使用 Skill 产品名。`report_subtitle` 只承载周期或范围，`judgement_headline` 承载最重要判断。
- `period_overview` 展示分析期累计或整体口径；`latest_snapshot` 展示最新完整周期及实际对比周期。禁止把最新一个周期冒充整个分析期。
- HTML 正文按已选业务问题章节递进；KPI、趋势与经营杠杆只作为上下文或证明材料，不能形成孤立单指标堆叠。没有核心章节时不得把浅层模块包装为合格经营简报。
- 章节标题使用业务判断，正文明确对应问题、经营含义、证明图表、行动和边界。原始 `chapter_id / question_id / evidence_id` 只留在模型与 QA，不进入观众可见正文。
- `featured` 继续作为旧接口兼容和章节内部候选记录；最终正文选择以 `value_selection.selection_unit=analysis_chapter` 与 `analysis_chapters[].selection_status` 为准。
- 新版 HTML 可用 supporting 表达必要背景，但不能把浅排名包装为强诊断。旧模型的 supporting 附录规则只用于旧接口兼容。管理摘要不能用普通 KPI 事实挤掉有证据的诊断。
- 采用证据优先规则：现有字段能够回答的问题必须完成趋势、结构或交叉分析；只有确实缺少字段、周期或业务事件证据时，才准确说明无法验证。
- 核心结论逐条采用“简短判断标题＋解释与证据”：标题由宿主根据正文和所引章节概括，HTML加粗，PPT复用为同条判断的标题；不能只写分类标签或机械截取首句，不能遗漏关键范围、比较条件与不确定性。正文保留证据和边界，详见宿主HTML合同。
- PPT按“核心判断→整体概况→判断依据→行动安排→口径附录”组织，保留分析期基本盘；通过独立演示编排把图表标题、结论编号和各页用途连起来。正文眉题说明对应哪项结论或属于全局背景，行动区区分执行、验证与边界，页码提供整体进度。标准版与美化版复用同一映射，不能只按字数机械切页；见[章节到演示投影](references/chapter-presentation.md)。
- 设计表达根据本页已有内容关系选择构图，不能用大小、顺序或颜色制造未经支持的优先级与因果；图表重点须绑定图中类别及本页判断，强调区不能只重复原读数。美化可将正文无损分段或呈现有原文依据的步骤，必须逐字拼回且全段可见，不转移到备注；主指标需声明与汇报目的有关的理由。长内容或密集图回退到可读布局，SVG预览与最终PPT重导入都要核验，不缩字、不溢出、不丢信息。新正式任务由宿主按当前数据提供`presentation-visual/2`，不得复用旧案例编排；主指标、短标注和步骤关系按证据选用，无依据保留同级或并列。字段规则与内部设计评审入口见[有来源的设计表达](references/chapter-presentation.md#有来源的设计表达)；内部小样不改变普通用户的主题选择流程。
- 强制“摘要—章节—行动闭环”：每条摘要判断引用已选章节；正式行动引用来源章节并按最终筛选结果连续编号，再同步回管理摘要。
- 同比同时写明实际最新周期与实际同比周期；子集与整体同页时明确范围，必要时给出同期全渠道基准。
- “贡献最高”等结构判断必须继续调用可用的成本、质量、转化或效率证据完成交叉分析。
- evidence ID、来源哈希、原始字段名与渲染提示不进入观众页面，但完整保留在模型、交接和 QA 中。

## 标准 PPT 规则

- 页面从九类候选构图中按证据选择：封面、管理摘要、KPI、趋势、结构、经营杠杆、机会风险、行动路线、数据与口径。缺证据的可选页必须消失。
- `visual_spec.eyebrow` 使用中文功能眉题；`tone`、`density`、`focus_evidence_ids`、`display_claim`、可选比较口径和图表焦点控制视觉表达。无法可靠确定时留空，不得猜测。
- 主题入口为 clean、corporate、editorial、warm，配置与适用路径见主题选择参考。旧PPT布局只支持前三个旧ID clean/corporate/warm，不将editorial静默降级为换色。正文对比度不低于4.5:1，大字和装饰性元信息不低于3:1。
- 趋势和结构优先使用原生可编辑图表；每页只保留一个视觉焦点，内容超容量时精简、换低密度布局、拆页或失败，不缩小字号硬塞。
- 所有中文运行使用 `lang=zh-CN`，段落启用东亚换行与悬挂标点；PPT QA 必须检查孤立标点、字号、边界、重叠、对比度、布局角色、视觉焦点、密度和重复口径。
- SlideViber 是可选精修层，不是标准版依赖。它只能提升视觉表现，不得改变页 ID、日期、数字、指标口径、结论或行动含义。

## 快速体验与公开样例

公开体验只使用内置脚本自生成模拟数据，不冒充真实企业数据：

```bash
python scripts/generate_sample.py --output-dir generated
```

生成后，把 `generated/synthetic-business.xlsx` 交给当前 Agent，并说：

> 请用 sheet-to-report 直接分析这份模拟业务表，先生成 HTML；如果继续生成 PPT，请按主题选择流程执行。

生成约 10 万行、18 个月、带已知业务信号的正式体验案例：

```bash
python scripts/generate_sample.py --output-dir main-case --main-case --rows 100000 --write-xlsx
```

生成后，把 `main-case/retail-omnichannel-main.xlsx` 交给当前 Agent；分析仍按本 Skill 的宿主 AI 链路执行，不把旧兼容命令当成新版完整分析。

## 边界

- v0.2 只支持一张结构清晰的数据表；可用 `sheet_name` 选择工作表。多 Sheet 联合、多层表头和合并单元格进入后续版本。
- 先完成表内可验证的趋势、结构和交叉分析；只有确实缺字段、周期或业务事件证据时，才请求补充数据或口径。
- 支持 `sum`、`ratio`、`average`、`last`。比率必须声明分子、分母与 `scale`；余额取期末值。
- 默认 `Asia/Shanghai`、周一为周起点、排除未完成周期并提示；只接受 `weekly` 或 `monthly`。
- HTML固定为一套标准商务样式；PPT四方向共享选择记录，主题不改变内容或分析结论；新版完整链路及实际已验主题以章节演示合同为准。公司母版或原生数据编辑要求不可因选主题而降级。
- 示例仅用于体验和说明；每次以用户当前输入与问题重新分析，不绑定任何内置数据或预设结论。
- 未获得单独发布授权时，不打包、上传、推送或更新公开站点。
- 输出是描述性分析、证据受控的诊断与复核建议，不用于医疗、投资、人事评价、授信等高风险决策。
- 任何高层级结论都要保留数据范围、缺失、重复、过滤、字段口径、证据强度与限制。
