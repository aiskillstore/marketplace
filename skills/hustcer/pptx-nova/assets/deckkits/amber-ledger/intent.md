# Amber Ledger

暖象牙纸底、炭黑无衬线观点、正体衬线解释、鼠尾草证据色和蜂蜜琥珀焦点构成这套年度报告语言。
颜色、字号、区域、容量和规则以 [design.json](design.json) 为唯一数值事实源。标题、判断、单位、
来源、日期、状态、目标口径及阈值全部来自 content；套件不定义业务政策。

参考为 Warm Jade Annual Report 的设计规范及八页纵向合成图。八个面板均为 16:9，采用默认宽屏。
规范的通用摄影要求与实际双圆封面冲突，以具体画面为身份依据，不提供摄影或活动页能力。
具体年度报告章节覆盖通用限制，保留衬线解释与开放证据布局；不迁移参考中的红绿阈值、
交通实体或金融政策。原稿的小字、低对比及拥挤布局已调整，双圆收进画布以满足边界门禁。
0.2 版基于完整八页示例的设计审查继续减轻视觉重量：封面使用琥珀空心环、鼠尾草圆盘与同色边轨，
保留原生椭圆；数据图形使用独立证据色，炭黑用于文字与细线，不再铺成整列或大扇区。

## 标准工作流

从 [明确标注为合成数据的示例](../amber-ledger/examples/content.json) 开始，无需手写坐标：

```sh
node pptx-nova/scripts/cli/deckkits/design.mjs --deckkit amber-ledger
node pptx-nova/assets/deckkits/validate-content.mjs content.json --deckkit amber-ledger --mode delivery --json
node pptx-nova/scripts/cli/create/build.mjs --deckkit amber-ledger content.json -o patch.json
```

使用标准 Create runner 完成锁定、机器检查、对象回读、canonical 逐页审查和同一候选交付绑定。
production 可参与自动交付选择。完整报告声明 `meta.designScope: "complete"`，以封面开场、决策收束；
单页及节选声明 `"excerpt"`。`auto` 确定性选择能容纳内容的合法构图；显式选择仍执行容量检查。

| type                | 职责                         | layoutId                       |
| ------------------- | ---------------------------- | ------------------------------ |
| amberCoverSlide     | 双圆封面与元数据登记栏       | circleRight / circleLeft       |
| amberSummarySlide   | 四项指标、衬线判断、琥珀焦点 | verdictCenter / verdictBand    |
| amberMixSlide       | 历史柱图、构成环图与背景指标 | evidenceRail / evidenceBand    |
| amberTrendSlide     | 点线趋势、区间注释与解释     | chartRail / chartBand          |
| amberBridgeSlide    | 可核对的差异桥与基准表       | bridgeRail / bridgeBand        |
| amberProjectsSlide  | 实际条、计划刻度与责任行动   | progressRows / progressColumns |
| amberMatrixSlide    | 重点列原生矩阵及假设         | matrixWide / matrixRail        |
| amberDecisionsSlide | 决策登记与衬线收束           | decisionTable / decisionLedger |

保持纸底、颜色职责、正体字体层级、横线分组及克制的琥珀焦点。允许证据区左右移动、解释区
改为下方带、项目由行改列、矩阵附注侧置、决策由表格改为开放列表。双圆大小、浅色重点列、
标题换行和证据顺序是有界构图选择，不要求逐像素一致。没有为凑页数添加无用途页型。

## 颜色与证据职责

- `ink` 保留给标题、数值和文字；差异桥总计、实际进度和趋势线使用 `sage`，历史柱与普通驱动使用 `history`。
- 构成环图与图例读取同一 `amber.evidence.categorical` 色序，不继承共享执行器的黑色默认值。
  这些颜色在环图中只区分类别；不代表状态或风险等级。琥珀在其他图中标记当前观察或讨论焦点。
- 进度底轨使用浅鼠尾草色，计划刻度使用更深的暖金色；长度、位置仍从原始 actual/plan 数值推导。
- 矩阵 `focusTone: "sage"` 或 `"amber"` 表达浅底深字的重点列。旧值 `"ink"` / `"history"`
  继续接受，均映射为浅鼠尾草底，不恢复黑底反白。`focusColumn` 与逐格内容保持原意。
- 趋势图纵轴按原始数值推导 1/2/5 系列的整齐主刻度与上下留白；不四舍五入或改写输入观察值。

所有色值、角色映射、封面轮廓线宽仍由 design.json 提供；未修改共享执行器或 core-primitives。

## 容量与编辑边界

- 数组上限和每个字段预算见 schema 与发现报告；最大数组数目不承诺所有字段同时取最长文本。
  实例容量不足会失败，须选择其他合法布局、重组或拆页；不删字段、不改数值、不无限缩字。
- 常规历史柱图、直线点图、环图为原生单系列图表；矩阵、基准表、决策表为原生表格。
  文字、形状、表格、图表可在 PowerPoint 编辑，不使用整页截图或栅格图表。
- 最大绝对值非零且小于 `1e-5` 的柱图/点线图使用注册的原生数值派生形状，保留原始数值，
  标签显示科学记数；点线为可编辑 freeform。此分支避免本次 runtime 极小轴刻度挤压，
  不属于原生 chart 对象。未来 runtime 改善后应重新探测，不能将它解释为永久能力禁令。
- 差异桥及实际/计划进度由同一数值来源推导；差异桥要求显式 baseline 且起点加驱动等于终点。
  支持负数、零和跨零；零值不伪造最小条长。baseline 必须低于所有累计值，图中明确标出刻度。
- 独立图例、环内合计、解释、差异桥、进度和微量图形不会随手工图表数据编辑自动同步。
  数值更新应修改 content 并重新生成。原生 Excel 数值编辑及 chart cache 更新已在本机验证，
  不能据此承诺所有宿主、所有组合的自动同步。
- 字体 Tahoma / Noto Sans SC / Georgia / Songti SC 不嵌入；中文、英文、混排常规/粗体已经实际
  canonical 与本机 PowerPoint 检查，其他平台需复核。正文与小字受合同下限约束。
- 不宣称 native-skinning、任意图片输入、已有 PPTX 保留、动画、Windows 宿主或全像素一致性。

## 0.2 验证范围

完整八页示例、十六个注册布局、最大条目数及中英混排样例均通过机器检查与实际 PNG 审查。
八页全部文字序列、三个原生图表的类别和数值缓存、三个嵌入工作簿保持一致；三个表格仍为原生对象。
ZIP/XML、完整包语义及兼容检查通过，本机 PowerPoint clean-open 通过。
本轮未新增交互编辑、跨平台或像素等价认证，readiness 为 production。
