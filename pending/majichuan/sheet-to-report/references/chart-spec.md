---
updated: 2026-09-09
version: chart-spec/1
---

# 共享图表合同 chart-spec/1

本合同提供共享图表设计。旧无 version 合同仍由旧模块显式处理；新合同失败不得降级成旧横条。`scripts/chart_contract.py` 的 `validate_chart(chart, record)` 抛出 ValueError 阻断非法组合；`project_chart(chart, record)` 返回与屏幕无关的确定性投影。HTML与新版章节PPT消费同一投影；各消费者的实际容量与编辑能力见[跨格式能力](chapter-presentation.md#图表跨格式能力)。

## 宿主选型

先明确本页要让观众理解的关系：趋势、对象比较、完整构成、分布、两指标关系或变化贡献。结合粒度、单位、分母、完整性、负值、缺失及长尾比较适用候选，再检查输出能力。`task/reason/constraints`保留选择依据；不能因PPT入口尚不支持某图，就把现有柱形说成业务最优。没有需要时保留清楚的原图，不设置图型数量配额，也不将不同分母的占比堆叠成一个总体。

能力不足时：只有仍能表达同一主要关系且不丢对象、数值、范围的替代才可使用，并说明理由；否则明确报告缺口。正式任务不得在渲染器新增占比、分箱或分解。已冻结报告仅调整图表时，可用`scripts/revise_charts.py --model 原模型 --proposal 原提案 --correction 修订.json --output 新目录`；修订为`{source_model_sha256,charts:{章节ID:[完整图表提案]}}`，只复用该章已绑定证据，重组与封印新模型，原模型和正文保持不变。宿主须另行核验候选是否更合适，代码通过不代替业务判断。

## 图表提案

必需字段：`version` 固定 `chart-spec/1`；`id` 稳定标识；`task` 为 trend/comparison/composition/distribution/relationship/contribution；`reason` 非空选择理由；`constraints` 字符串数组；`evidence_id`；`kind`；`x`、`y` 列 key；`title` 非空现有文本片段数组；`limit` 为 1–500 整数。

kind：line/bar/column/grouped/paired/stacked/donut/scatter/waterfall/histogram。可选字段只有：`series`（grouped/stacked 的 2–6 个列 key，首项必须是 y）、`y2`（仅 paired）、`x_scale`（category/time/linear）、`order`（source/descending/absolute）、`emphasis`（primary/supporting）、`highlight`（已有对象标签字符串数组）、`label`（仅 scatter 的对象标识列）。新值或多余字段均拒绝。允许任务与图型的合理重叠；理由不能替代数值与语义校验。

默认 x_scale：scatter 为 linear，其余 category；默认 order：line/waterfall/histogram/scatter 为 source，其余 descending。time 或 linear 必须 source。累计曲线采用 line + linear。柱/条/构成/瀑布图必须保留零起点；投影以 axes.zero_baseline 声明，消费者不得擅自截轴。可读对象上限为 bar/paired 30、column/grouped/stacked/waterfall 24、donut 6、histogram 40、line/scatter 500；超出需明确截取（若允许）或计算合适的聚合证据。

## 计算端证据语义

证据仍包含 `columns`、`rows`、`scope`，由原证据快照和哈希绑定，宿主提案不得提供以下语义。`chart_semantics` 必须由受控计算构造，不能从任意宿主布尔标记推导事实。

- `partition={mutually_exclusive:true,complete:true}`：跨行构成，仅供 donut。y 必须是已计算百分比，列 unit 为 `%`，有非空 denominator 标识；全部行非负、合计 100，2–6 类，全部展示。
- `series_partition={mutually_exclusive:true,complete:true}`：同一行内跨 series 构成，供 stacked；每列 additive=true、单位一致；百分比时列 denominator 一致且每行合计100。普通 grouped 只要求单位一致；百分比指标可以各自使用明确的不同 denominator，但必须在投影保留分母供消费者说明。
- `time={frequency:'day'|'week'|'month',expected_values:[完整有序 ISO 日期或 YYYY-MM]}`：时间域由计算端生成，必须是连续周期。实际行顺序严格递增、不可超域；缺期投影为 null 与 gap_indices，不补零、不无提示连线。
- `cumulative={x_key,y_key,total:100,order:'descending'}`：x 是已计算的实体累计百分比，严格递增、0–100、终点100；y 有限且终点100。负值、下降和超过100保留，并投影 signed_cumulative 与警示；不得强制裁剪为漂亮曲线。
- `histogram={lower_key,upper_key,count_key,sample_count}`：行提供已计算箱边界和人数/对象数，x 是箱标签，y 必须 count_key。连续等宽不重叠边界，计数为非负整数、合计 sample_count；最后一箱闭右侧，其他左闭右开。不等宽需要另行计算密度证据，本版本拒绝直接以计数作高度。分箱与实体聚合只能发生在计算端。
- `waterfall={role_key,base_key,end_key}`：行 role 为 start/delta/end，首尾为 start/end，中间为 delta。y 是已算金额，base/end 是已算图形坐标。start/end 均 base=0、end=y；每个 delta 的 base=前一行 end，end=base+y；终点 y=前一行 end。y 列必须 additive=true。图形不重新计算新业务量。

任何被 limit 隐藏的行仍校验缺失、非有限数、对象重复等。line/donut/stacked/waterfall/histogram 禁止裁尾；排名和散点允许显式截取，并投影 shown/source/omitted 和尾部说明。scatter 仅允许 source 截取，不宣称随机抽样或完整总体。

## 投影接口

统一字段：version/id/task/kind/title/reason/constraints/evidence_id/scope；labels（展示字符串）、x_values（category 字符串、linear 原数值、time Unix UTC 毫秒）；series（key/label/unit/values，如有 denominator 同时保留）；source_count/shown_count/omitted_count/truncated/tail_note；order/emphasis/highlight；axes={x:{key,label,unit,scale},y:{independent:boolean},zero_baseline:boolean}。

可选字段：time 提供 gap_indices；累计曲线提供 signed_cumulative/warnings；waterfall 提供 roles/bases/ends；histogram 提供 bin_lower/bin_upper；scatter label 用于 labels，x_values 始终为数值。highlight_indices 传递重点对象的展示位置；stacked 的 series[].bases/ends 仅是已有分量的几何位置。贡献任务的全部图型要求可加总并禁止截尾。投影不生成 SVG、不读取原表、不计算比例、分箱或新聚合，不改变输入对象。
