# Blue Research

白底、海军蓝结论、青蓝证据、开放细线矩阵与浅灰解释带构成研究报告身份。套件为 production，
可参与自动交付选择，创建可编辑原生对象；不承担行业政策、投资建议或任意已有 PPTX 的无损翻新。
所有标题、观点、数值、单位、时间、来源、解释、阈值、角色和行动均来自 content。

通过标准 `slots`、`design`、`validate-content`、`create/build`、`create/run` 使用；无需手写坐标。
容量与几何的唯一事实源为 [design.json](design.json)，每页 schema 提供字段预算，解析器按实际
组合检查，不缩字、不静默删除。`layoutId: "auto"` 按容量和近期构图确定选择；显式布局同样须适配。
完整 deck 以封面开场、读者行动结尾；摘录须设置 `meta.designScope: "excerpt"`。

| 页面职责       | type                      | 注册构图              |
| -------------- | ------------------------- | --------------------- |
| 封面           | researchCoverSlide        | spine / split         |
| 概览与页码目录 | researchOverviewSlide     | rail / reverse        |
| 原生图表证据   | researchEvidenceSlide     | rail / band           |
| 蓝阶矩阵与引文 | researchMatrixSlide       | rail / reverse        |
| 调和差异桥     | researchBridgeSlide       | rail / reverse        |
| 分层表与短条   | researchTiersSlide        | rail / reverse        |
| 时间与门槛     | researchTimelineSlide     | horizontal / vertical |
| 共享目标与阶段 | researchScorecardSlide    | steps / register      |
| 编号结论       | researchFindingsSlide     | register / leadRail   |
| 读者行动       | researchImplicationsSlide | matrix / ledger       |

证据图支持单系列 column/line、双系列非负 stacked column。数值与显示格式分离；整数、小数、
科学记数由源数值选择。`chart.phaseLabel` 必填，说明观测/计划范围或“全部为观测”；
`forecastFrom` 是最后一个观测类别的零基索引，仅单系列 column 可用，其后柱为蓝色虚线轮廓。
所有类别、系列和数值均回读；同一线性轴上的极小量可能只有数字可读而图形不足一像素。

矩阵支持四至六列、三至六行，列权重及各 cell 的 paper/pale/history/deep 由内容明确提供。
不根据某业务指标擅自推导强弱。深蓝单元格使用白字。实际可容纳字数取决于行数、列宽和语言，
超限须重组或拆页。表格每格是一个原生段落，禁止手动换行，允许原生自动换行。

桥图要求 `opening + sum(drivers.value) = closing`；正负差异、零值均保留，不制造最小柱长。
短条宽度来自非负值/当前表最大值；全零时不绘制非零条。时间线 horizontal 以提供的数值位置
编码时间，事件须严格有序、不同且位于 start/end 内；过近事件会因实际容量被拒绝。
vertical 为等高的有序事件登记栏，保留原始日期数值，不声明长度编码。阶段框的高度是顺序结构，
不编码业绩；每个阶段的标题、责任人与行动随框顶递升，共用底部基线、上方依赖轴和右侧验收端点。
steps 最多四条行动；register 最多两条行动。字长仍须通过真实容量检查，不能按条数保证适配。

封面保留开放刊头、青色竖线、眉题、42pt 两行大标题与较浅年份；支持 content 自主换行。
内页刊头和右侧章节标签来自 reportTitle/eyebrow；封面不显示页码。结论页保留编号、说明、
证据注记及短黄色强调；读者页保留约束、行动、责任人、指标、时限、依赖链与共同验收。

原生图表和表格的数据可编辑；桥柱、短条、胶囊、引用、独立标签和预测样式是从 content 生成的
独立对象。在 PowerPoint 手工修改图表/表格/日期后，它们不会自动联动，须从同一 content 重建。
不要用编辑过的独立图形反推原始数值。字体为 Arial / Songti SC 正体常规和粗体替代，不嵌入字体，
其他机器需安装并重新验证字体。中文保留研究式衬线语气，未冒充 STKaiti / LXGW Bright。
本机 PowerPoint 图表编辑曾暂留旧缓存，重新进入“编辑数据”再返回后同步；修改工作簿后须核对
图表标签及保存回读，不能把工作簿修改成功当成图表同步证明。

参考为 marine-blue-research 设计规范及八页合成图。Part B 覆盖 Part A 的持续导航及字体要求。
实际八页没有摄影，因此不引入无来源照片，也不注册摄影/地图/任意图片输入。小号青文字加深，
字号提高，页脚移入安全边距，阶梯保留明显递升并为验收栏预留空间。黄色强调为独立、原生可编辑的内容短语，
不声称任意行内文字背景功能；橙色只用于小型事件编号，不编码好坏。参考业务词和金融政策不进入实现。

机器、逐页 canonical PNG 与原生宿主事实见
[benchmark review](../../../benchmarks/visual/cases/blue-research/golden-learning/review.md)。
本说明只声明实际覆盖的能力，不推断跨平台像素一致或无损保留能力。
