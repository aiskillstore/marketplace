# Clear Impact

白底、深绿文字层级、鲜绿主体和开放的细线结构，适合影响报告与工作复盘。
它迁移的是证据报告的设计语言，标题、结论、单位、日期、来源、状态及阈值全部来自 content。
精确 token、字号、区域、容量及构图以 [design.json](design.json) 为唯一事实源。

源资料的实际图片包含八张无摄影的数据报告页；文档中的“38 页、摄影占主导”描述与其冲突。
本套件采用实图和规范共同支持的颜色、留白、细线与证据层级，不注册摄影输入或固定摄影比例。
画布保持 16:9。常见的 Arial / Arial Unicode MS 替代无法确认的 Liter / MiSans；不嵌入字体。
本机 Arial 有 Regular/Bold 字体文件；Arial Unicode MS 只有 Regular，中文粗体由宿主合成，已检查正体显示。
原图的浅灰绿小字加深、表格衬线改为正体无衬线、黑色收束统一为深绿。
鲜绿用于主要数据填色和深色指标带；白底小字采用更深的可读绿色。

## 标准工作流

从 [完整合成示例](../clear-impact/examples/content.json) 开始，只填写内容，无需手写页面坐标：

```sh
node pptx-nova/scripts/cli/deckkits/design.mjs --deckkit clear-impact
node pptx-nova/assets/deckkits/validate-content.mjs content.json --deckkit clear-impact --mode delivery --json
node pptx-nova/scripts/cli/create/build.mjs --deckkit clear-impact content.json -o patch.json
```

标准 Create runner 使用相同合同，保存计划、规则检查、原生图表/表格回读与交付绑定。
当前为 production，可参与自动交付选择。

## 页面职责与构图

| type                   | 职责                         | layoutId               |
| ---------------------- | ---------------------------- | ---------------------- |
| impactOverviewSlide    | 观点、索引和深色指标带       | verdict / bandFirst    |
| impactReviewSlide      | 指标与编号发现               | rail / band            |
| impactChartSlide       | 单系列原生柱图与解释         | chartLeft / chartRight |
| impactComparisonSlide  | 原生比较表、指标、证据       | side / stacked         |
| impactProcessSlide     | 指标、处理链和反馈           | chain / vertical       |
| impactCapacitySlide    | 容量指标与解释               | strip / rail           |
| impactScorecardSlide   | 原生责任清单与状态单元格     | wide / inset           |
| impactCommitmentsSlide | 基线、目标和行动             | columns / ledger       |
| impactProgressSlide    | 实际值、目标、比例及派生条形 | rows / columns         |
| impactVarianceSlide    | 有符号差异归因与精确合计校验 | wide / split           |
| impactMilestonesSlide  | 日期、里程碑、证据与责任     | horizontal / vertical  |
| impactDecisionsSlide   | 请求、影响、责任和时限       | ledger / split         |

`auto` 在能够容纳当前实例的构图中确定性选择，并避免连续重复；显式构图也必须通过容量检查。
容量是字段组合的上限，不代表每个布局可以同时容纳所有字段的最长文字。细节看 schema、
槽位发现和解析结果；较长内容须换合法变体、重组或拆页，不能靠删字段或无限缩字。
例如容量页的竖排适合少量详细指标，横向指标带可以容纳更多简短指标；纵向流程适合较短节点。
`inset` 责任表在完整清单需要更聚焦的左右留白时使用，数据及单元格不变。

## 内容与编辑边界

- 每页的 document、section、source 均为内容字段。所有示例数据明确标记为合成/示意。
- 图表需要数值、类别、系列名及单位。保留负数、零和极小值；负数采用明确描边。
  数值标签格式独立于原始数值；极小值可用科学记数。单页最多一个 `focus`。
  PowerPoint 按标签格式显示科学记数；当前 xdoc canonical 渲染器可能显示等值十进制数，
  两者保留相同原始数值，不承诺逐像素一致。
- 表格逐格原生可编辑；列宽由权重计算，数值列右对齐。责任表必须恰有一个 status 列，
  明暗状态来自 rows[].status，状态文案来自对应单元格，不按业务数值推断达成情况。
- KPI 和承诺中的 value / baseline / target 是显示字符串，不自动推导商业结论。
  KPI 单位与小号标签同组，避免将长单位挤入大数字行。
- 达成页要求非负 actual 和正 target。条长、目标刻度和比例来自同一数据；超过目标不截断数值。
  比例采用显示精度，实际值和目标值原样保留。该组件表达 actual / target，不预设越大越好。
- 差异页要求 start + drivers[].value 与 end 在浮点容差内一致。浮动柱、正负号与标签由同一来源生成；
  零变化没有伪造的最小柱高。数值在顶端对齐，类别在底端对齐。
- 达成条、差异桥、流程反馈及里程碑是原生形状/文字，不是原生图表数据模型。
  手工编辑图表、表格、形状或标签不会自动同步旁注、派生几何和比例；应修改 content 重新生成。
- 不注册照片、图标、组合图、多系列图、动画、原生翻新或任意 customOps。
  不承诺其他 Office 平台的字体与显示一致性。

复用了主题、规则、容量选择、槽位投影、原生回读和标准 Create 交付能力。
新增 `impact-evidence/v1` 只负责开放式报告的组件计划及执行；没有修改 core-primitives。
