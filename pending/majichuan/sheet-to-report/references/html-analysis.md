# 宿主驱动的 HTML 分析合同

当前章节合同 `html-chapters/1`；新运行图表合同 `chart-spec/1`。本文件负责HTML阶段；已完成模型通过[章节演示投影](chapter-presentation.md)接续PPT，不能直接调用旧PPT消费者。

## 必须按顺序执行

1. 先读本文件、`report-model.md` 和 [共享图表规格](chart-spec.md)。显式使用已确认版本的 Skill 绝对根目录，核对安装版或待验版的真实文件清单；不误用旧版。本地初扫记录根目录和既定 Skill/参考文件/Python脚本清单的文件哈希。Git仅为可选开发元数据：本Skill自身仓库可读取时记录Commit与已跟踪改动，否则二者为null并记录不可用原因，不要求普通用户安装Git。文件读取或指纹失败仍阻断；补查及最终化仍禁止混用不同文件版本。更新Skill后不得续算旧运行或手改旧快照指纹，已完成模型可按既有来源合同继续用于PPT。
2. 使用已确认请求，`output_mode=report`，输出为新目录。运行 `python <绝对根>/scripts/sheet_to_report.py --html-analysis --analyse-only --request <请求> --output <新运行目录>`。此路径仅计算基本盘、周期和主要对象分布，不调用旧自动补查，不写正式故事。
3. 阅读 `snapshot-000.json` 的证据目录、小聚合、口径与能力。针对重点问题记录已有证据是否充分；有可回答的真实缺口时提交批次。不得用既有示例结论或预设答案替代当前输入的证据分析。
4. `--html-analysis --followup <批次.json> --output <同一目录>`。批次含 `run_id/snapshot_version/snapshot_sha256`（从当前快照取得）、`batch_id`、`paths`。每条路径包含 `question_id/decision_use/gap/basis_evidence/operation/metrics/dimension`；可选 `periods` 与 `filters:[{field,values}]`。当前算子 `period_breakdown` 按已确认维度和周期对读指标。基础维度总计没有提供联合期间拆解时，这是一条真实新信息路径。
5. 阅读新快照后修正或停止。新批次占一轮；最多四轮、总十二路径、同计算问题族三路径。问题改名、改期或改筛选不重置问题族预算。拒绝/重复不扣路径但占轮，失败计算扣路径；同批次原样重放不重新计数。源变化需显式新运行及原因，不能借新运行绕过预算。中断预留文件阻止未核实重算。
6. 基于最终快照提交故事；`--html-analysis --compose-decisions <提案.json> --output <运行>`。提案含三个绑定字段以及 `title/summary/chapters/actions/sufficiency`。`title` 和所有文案使用片段数组：普通字符串不能包含游离阿拉伯数字；需要数字/对象/日期时引用 `{evidence_id,row,column}`。引用由程序解析并携带单位，不能修改计算值。
7. 章节含 `id/role/claim_type/title/body/meaning/limitations/evidence_ids/charts`，可选 `nav_title` 使用一至十二字符的业务短名片段数组。role 可为 background/diagnostic/supporting；claim_type 可为 fact/structural/hypothesis。背景无需行动。图表含 `evidence_id/kind/x/y/title/limit`（limit不超过24），kind 支持 line/bar/paired/contribution。可选 `order=source/descending/absolute`、`emphasis=primary/supporting`；paired 额外指定 `y2`，同一对象同序显示两指标，各用独立标尺和单位。contribution 使用全部证据行显示首要拉动对象、其余对象合计与全体净变动，limit 不裁掉尾部抵减；仅用于可加总的金额/数量变化，禁止对去重人数、单均和比例求和。不接受自行提供图数据。summary 项含 `chapter_ids/headline/text`；action 项含 `chapter_ids/title/target/basis/steps/success_signal/boundary`。`sufficiency` 每项含 `question/evidence_ids/decision/reason`，decision 区分 sufficient/followed_up/data_limit/implementation_gap/budget_stop。
8. `--html-analysis --finalize <生成的story文件> --output <运行>`。只读冻结证据和提案，不读原表、不补算；生成新最终目录。不编辑 report_model 或 HTML。修复计算/提案/渲染后重新生成，旧结果保留。

第七步中的四类无 version 图只供旧快照兼容。新快照声明 `capabilities.chart_spec_version=chart-spec/1`，每张图必须遵循该版本规格；错误版本或非法图型组合直接失败，不静默回退。章节、摘要、行动、范围和数值插值的合同不变。

## 新版图表的宿主决策

先明确每个关键判断希望读者看到的关系：趋势、比较、构成、分布、两指标关系或变化贡献。核对证据目录中的粒度、单位、分母、负值、长尾、缺失和 `chart_semantics`，再选最适合的图；理由和约束保存于图表提案内部，不铺正文。新图必填 version/id/task/reason/constraints 及既有引用字段，具体白名单和例子以共享规格为准。图型种类和张数不作配额；必要时保留表格或准确说明缺口。

新图数据只引用快照中的计算记录。预声明的 `chart_evidence.enrich` 从已有聚合生成：各已分组对象指标的直方分布、互斥分组占比、购买频次人数占比、客户实际累计比例、客户身份销售覆盖，以及已有分解分量的起终点桥接。动态期间×对象证据在既有补查预算内产生；其已计算结果可派生完整类别系列和贡献桥接，不重新查询原表。派生记录保留公式、源记录指纹与口径；histogram 箱宽可能因长尾而不适合重点展示，宿主应检查分布实际解释力，不能只因为已生成就放进正文。

`bridge_period_components` 表示前期净销售经交易单/单均数学分量到本期净销售；`bridge_components_*` 表示从零到总增量的分量对账；`bridge_change_*` 含首要对象、其余对象合计和净变动。上述是通用计算角色而非默认故事顺序。直方图证据 `hist_dimension_*` 的样本是维度聚合后的对象，不是原表每一行；累计曲线 `customer_curve` 的横轴是实际客户人数比例，不能当等间距类别。

compose 将投影冻结为模型 `chart_views`，保留章节、快照和 scope 绑定；HTML 仅将它们映射到几何和标签。PPT已通过独立chapter-presentation投影消费相同图表语义；HTML渲染不依赖PPT导出器。正式检查以桌面为主，移动端只需基础可读与无页面横溢，不逐章精修。图形及注释不能把结构关联升级为因果。

## 审核与失败处理

每章额外声明 `scope_bindings:{evidence_id: scope的canonical_sha256}` 与 `scope_relation`。同一总体用 `same_population`，独立范围必须用 `separate_scopes` 并在文案披露分母，不能以全期/客户域/单期数值互相冒充。程序按快照核对范围指纹。补查默认复用初扫冻结周期，不能随日历自动扩大范围；补查及最终化核对 Skill/scripts/references 文件哈希，版本变化不得混进旧运行。任一未提交批次预留阻断改名重算；须先核对恢复记录。

交易表预声明基础覆盖还包括多指标月度、最新期规模/单均数学分解、地域/条目总盘、客户累计贡献与正向购买频次、质量与原表对账；这些计算在初扫前声明。期间×对象的联合变化仍为动态补查。两期补查产生对象并集变化；商品字段和数量/金额合同支持时，追加逐条目数量/单位净金额/新增退出分解。单位净金额含交易组合及调整，不宣称挂牌价或因果。费用文字线索只是候选视图，不能冒充已批准分类或清洗；费用候选继续进入全体总额。

快照指纹、运行/版本、数值引用、章节/行动来源、图表列、内容锁失败均阻止输出。背景允许无行动，诊断不能靠加动作冒充强证据。逐项审阅数值、比较范围、完整覆盖、故事与行动、桌面手机和打印；机器通过不替代宿主阅读或用户校准。需要新增算子时标记实现能力缺口，不写成数据不足。正式生成必须由宿主读证据并组织提案；单独确定性脚本不代表完成 AI 分析。

## 阅读与图表校准

- 先用一句简短判断说明每章问题，数字优先放在主图和必要依据中；不删掉改变结论的范围或限制。数字引用已带单位，不再接“位”等重复量词。
- 页面用暖白底、深灰正文、深蓝主色；青绿突出正向贡献，橙红表示负向贡献，琥珀色标示待确认事项。颜色与符号、标签并用，不靠整页浅色底或彩虹排名区分内容。
- 每章按问题选择主图，必要时以 `emphasis=primary` 突出一图；辅助图保留必要比较，避免连续同类排名充数。频次/分层对读用 source 顺序；累计贡献组相互重叠，使用有明确标签的顺序曲线，不能相加或冒充互斥分层。
- 导航使用短业务名，与正文完整判断标题分开；只保留一个锚点偏移来源。被动滚动高亮只更新选中状态，不触发页面纵向滚动。
- 收到用户对完整候选的体验校准后，可以在已审核的自有提案基础上聚合修订；必须在新证据上重新核对引用、重绑快照并记录来源。这属于同一候选修订，不得声称隔离生成。隔离验收依然只提供 Skill、原表和已确认请求。

## 行动对象与协同角色

新快照声明 action_target_version=action-target/1。每条行动的 target 必须具体描述干预的人群、渠道、商品、任务记录或流程环节；target_refs 为非空证据单元格引用数组（evidence_id/row/column），来自行动所属章节，且引用的业务对象必须出现在 target 文本。不能仅用数字、日期或负责人作为对象。

suggested_role 是可选文本片段数组，含义固定为“建议协同角色”；没有真实分工依据时省略。不能将角色建议写成已确定的责任分配。宿主还须阅读对象、证据、步骤三者是否一致：字符串匹配与黑名单不能替代语义判断。旧快照没有绑定标记时保留具体对象的兼容路径，但新 compose 也拒绝明显的负责人占位。

仅修订既有行动对象时，可使用 scripts/revise_action_targets.py --model 源模型 --proposal 原始提案 --correction 修訂提案 --output 新目录。修订提案只含 source_model_sha256 与完整 actions，且只允许变动 target/target_refs/suggested_role。程序复用原冻结快照、预算和计算版本，单列本次生成版本及来源指纹；不回读数据、不补查、不改变其他文案或图表。输出由正常 compose 与渲染器生成，不手修最终模型或文件。
## 核心结论的简短判断标题

新快照以 `capabilities.summary_headline_version=summary-headline/1` 要求每条摘要提供 `headline` 片段数组。与 `text` 使用相同的章节证据引用范围及数字解析规则，不能生成游离数值。通常用约8–22个中文字符；结构上限40字符，保留准确性所需的范围及不确定性，不为凑字数改变含义。

宿主先阅读完整正文和所引章节，再概括“哪个对象有什么变化／差异／值得注意的判断”。不要机械截取第一句、照搬某个案例、仅写“增长分析”等分类名、把结构关联加强成因果，或将试验方向写成已证明的结果。标题和正文合读应保持原结论含义；限定词需要出现在标题时不得移到正文后声称标题仍准确。结构校验无法证明语义蕴含，宿主须逐条核对。

HTML以加粗短标题开头，正文和证据链接继续保留。标准PPT与SlideViber复用同一个标题，分别调整展示层级，完整正文超容量时拆页，不隐藏或缩小硬塞。旧快照未声明能力时可兼容无标题报告，不自动猜标题。

既有冻结报告仅补充或修订摘要标题时，使用：
`python scripts/revise_summary_headlines.py --model OLD_MODEL --proposal ORIGINAL_PROPOSAL --correction CORRECTION --output NEW_DIR`。
CORRECTION仅含 `source_model_sha256` 与按原摘要顺序排列的 `headlines`（每项为片段数组）。入口验证原提案和源模型封印，只更新headline并重新compose/render；摘要正文、章节引用、行动、图表、快照及计算预算不变，保留既有行动修订记录。本次修订版本与原计算版本分别记录，不声称重新分析。
