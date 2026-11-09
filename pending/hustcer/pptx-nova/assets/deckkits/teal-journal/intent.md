# Teal Journal：青绿手记

1.0.0 是 default 创建型 DeckKit，可参与默认及自动交付选择。暖纸底、河蓝结构、珊瑚强调、叙事衬线、方角色域与开放细线共同构成身份；数值事实以同目录 `design.json` 为唯一来源。

八类职责、十六个执行构图：

| 页型                 | 构图                  | 内容用途与边界                                       |
| -------------------- | --------------------- | ---------------------------------------------------- |
| journalCoverSlide    | angular / inset       | 大观点、切角资产外壳、强调条、摘要、3–4 个短标记     |
| journalOutlookSlide  | leadLeft / leadRight  | 焦点指标、原生横条图、2–3 组解释                     |
| journalAudienceSlide | leadLeft / leadBottom | 3–5 列、2–5 行的原生开放表格；导语与附注分区         |
| journalCalendarSlide | horizontal / vertical | 3–4 个有序时间区间、实绩/计划标记、2–4 项分配        |
| journalJourneySlide  | arc / linear          | 3–4 个时段；由同一开始/结束数值计算半环或直线        |
| journalAnatomySlide  | center / offset       | 可编辑样本、恰好六项说明、比较条；中置引线或侧置规则 |
| journalResultsSlide  | rail / band           | 2–3 个成果、2–4 个产出、2–3 个重点指标               |
| journalRoadmapSlide  | rail / stacked        | 分配、2–3 个基线/目标、2–3 项负责人/日期/衡量        |

`layoutId: "auto"` 按实际文字容量与近期构图确定性选择，显式布局也必须通过同一检查。预算只是发现提示；合法容量最终由实际输入、canonical PDF/PNG 决定。过长内容应换合法构图、重组或拆页；不删字段、不改数值、不缩到字号下限以下。相同构图连续超过合同上限会报错；不同内容仍应人工检查跨页节奏。

标题大小写原样保留。结构与大数使用 Arial / Arial Unicode MS，叙事使用 Georgia / Songti SC，均为正体替代；字体不嵌入。带底色标签由形状持有文字，内边距与字框共享事实源；相关说明、KPI 与行动使用单一段落对象保留不同字号、字重及字段绑定。

所有观点、单位、来源、期间、实体、阈值和政策来自 content。示例是明确标识的合成验证资料；`community-content.json` 是社区维修的混排跨主题示例。表格单元格完整写入原生表格；图表保留原始数值，整数、常规小数与极小值使用分离的显示格式。正负值均用河蓝与显式符号表达，没有固化的红绿政策。

分配项必须非负且总和为正；零项保留文字但不绘制有面积的段。日历与旅程的区间必须有序、互不重叠且在轴范围内。比较条允许零或负值，但不能全零。图表支持有限数值，包含零、负数与极小量；原生回读只证明注册的单系列横条组合，不外推其他图表种类。

图表、表格、文字、色域、时间区间、分配段、引线与端点均可编辑。手工改图表/表格数据不会自动更新独立标题、注记、派生形状、区间或分配段；要同步这些对象，修改 content 后重新生成。形状不是内嵌电子表格公式。

参考的照片只迁移为显式资产外壳，不复制原图，也不伪装成插画替代。1.0.0 没有注册外部图片输入或自由 customOps，不宣称照片摄入、原生换肤、已有源稿无损保留、动画或其他比例验证。若真实交付需要照片，先扩展可验证的资产合同再使用；不能把外壳示例称作完整摄影主题复刻。

标准流程为 `slots → validate-content → create/build → create/run → exact-candidate PNG review → finalize`。验证范围与环境未验证项见 [验收记录](../../../benchmarks/visual/cases/teal-journal/golden-handbook/review.md)。
