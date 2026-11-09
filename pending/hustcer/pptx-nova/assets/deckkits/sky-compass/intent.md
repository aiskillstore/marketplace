# Sky Compass

白底、天空蓝观点标题、海军蓝强调、浅蓝证据栏和开放式细线表格组成这套运营复盘语言。
数值事实以 [design.json](design.json) 为准；标题、判断、指标、日期、单位、来源、状态、
阈值与责任链全部来自 content。颜色不定义业务政策，负数也不自动等于红色。

参考设计规范与八页合成图存在冲突：规范要求摄影、左上横导航，实际八页采用无摄影白底、
右上浅蓝章节标签。以具体画面保持身份，不新增摄影能力。八个面板均为 16:9。
0.2 版以开放式天空蓝同心弧线替换封面灰色实心扇形，弧线止于海军蓝底栏上缘，
不覆盖文字或来源。保留蓝点页眉、短蓝下划线、海军蓝底栏、状态圆点与红色侧线、
条图基准刻线、环图中心值与图例、流程虚线引线、按日期分布的圆形编号和月份刻度。
这些细节是执行组件的一部分，换文案和构图时也不能被通用简化抹掉。

说明区使用更轻的冰蓝底色及加粗海军蓝小标题，避免与数据争夺视觉重量。
表格主要数据和证据正文为 11.5pt，表头、合并责任人/日期及辅助标签保留 10.5pt。
横向流程的虚线括线覆盖全流程，不能把总周期目标指向某个阶段。
差异桥保持真实零基线与数值比例；稀疏布局直接突出驱动数值，密集布局使用明确的 12pt 样式。
`unit` 表示驱动的变化单位，可选 `levelUnit` 表示起终值的水平单位；未提供时沿用 `unit`。
百分比水平与百分点变化应分别填写 `%` / `pp`。独立标注不会让细小增量柱变成假最小高度。
示例结论按当页证据编写，不将跨页重复口号固化为组件默认文案。

## 使用

从 [合成数据完整示例](../sky-compass/examples/content.json) 开始，通过标准工作流生成，无需手写坐标：

```sh
node pptx-nova/scripts/cli/deckkits/design.mjs --deckkit sky-compass
node pptx-nova/assets/deckkits/validate-content.mjs content.json --deckkit sky-compass --mode delivery --json
node pptx-nova/scripts/cli/create/build.mjs --deckkit sky-compass content.json -o patch.json
```

按标准 Create runner 完成 deck lock、机器检查、原生对象回读、canonical PNG 逐页检查和同一候选
交付绑定。当前为 default，作为默认 DeckKit 参与自动交付选择。完整报告使用 `meta.designScope: "complete"`，封面开场、
决策收束；节选使用 `"excerpt"`。`auto` 确定性选择能容纳内容的合法布局；显式选择仍检查容量。

| type                | 表达职责                   | layoutId              |
| ------------------- | -------------------------- | --------------------- |
| skyCoverSlide       | 观点封面、元数据与指标     | verdict / rail        |
| skyPerformanceSlide | 目标、实绩、达成率与状态   | wide / rail           |
| skyCoverageSlide    | 构成环图、合计与数据轨道   | plotLeft / plotRight  |
| skyRankingSlide     | 当期条图、基准刻线与变化   | plotLeft / plotRight  |
| skyProcessSlide     | 时间比例链或纵向处理链     | horizontal / vertical |
| skyDiagnosisSlide   | 原因、证据、归因与责任     | wide / compact        |
| skyActionsSlide     | 日期轴或纵向行动登记       | horizontal / vertical |
| skyProjectSlide     | 同心弧线、元数据与三项叙述 | arcLeft / arcRight    |
| skyTrendSlide       | 实绩与计划边界柱图         | plotLeft / plotRight  |
| skyBridgeSlide      | 可核对的差异桥             | plotLeft / plotRight  |
| skyAppendixSlide    | 多期原生数据附表           | wide / inset          |
| skyDecisionsSlide   | 决策、依据与延误成本       | wide / compact        |

## 容量与编辑边界

- 数组上限与字段预算见 schema 和发现报告。最大数量不承诺所有字段同时取最长文本；超容量会失败，
  须选其他合法布局、重组或拆页。正文及标签下限 10.5pt，不靠静默删字段、改数值或缩字放行。
- 环图与趋势柱图是原生 chart，四种登记表是原生 table；其余为可编辑文字与形状，无整页图片或栅格图表。
  原生表格单元格使用单段落和自动换行，不接受显式换行。
- 条图、轨道、时间位置、差异桥从同一数值来源推导。差异桥必须起点加驱动等于终点；
  归因必须加总为 gap。零值保留标签和连接，不画假最小柱；混合尺度中不足 1 EMU 的条省略图形，
  保留原始数值与科学记数标签。百分比构成必须加总为 100。
- 独立图例、中心值、解释、数值派生形状与月份标记不会随手工图表编辑自动同步。
  更新数据应改 content 并重新生成，不能把可编辑性解释成所有对象联动。
- Arial / Noto Sans SC 不嵌入。常规、粗体、中文、英文及混排有实际渲染覆盖；其他平台需重查字体与换行。
- 不宣称任意已有 PPTX 翻新、无损保留、native-skinning、摄影、动画或跨平台像素一致。

实际验收覆盖、主要设计差异与原生宿主结果见 [验收记录](../../../benchmarks/visual/cases/sky-compass/golden-operations/review.md)。
