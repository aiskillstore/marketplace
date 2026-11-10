# McKinsey Blue 2.0

白底咨询分析语言：观点标题、深蓝结论带、细规则、直接数据标签、渐进蓝色支柱、语义图标与清晰责任链。
第一手依据为 Kimsoong 客户忠诚度原稿全部八页，旧版仅作缺陷对照。合同数值以 design.json 为准。

日常使用 discover → content → validate/build → standard Create；无需手写页面坐标。
八类职责保留既有 mck 页型名；构图用注册 layoutId 选择，auto 按容量和节奏确定性选择。
所有正文/标签/来源遵守 10pt 底线，关键正文为 11pt；源稿低对比小字已适配。
Arial / Arial Unicode MS 是明确替代字体，不嵌入、不保证跨平台一致。中英常规/粗体须按最终证据验收。

业务实体、观点、指标、日期、单位、来源、责任方、保密文字和资金政策均来自 content。
随附演示源于未验证的参考材料，不能作为真实事实引用。源收入 82/16/5 合计 103% 被保留并披露口径问题。
红/橙/绿表示内容选定的语义，不能由皮肤自行判断业务结论。图标须为离线 Tabler pack 中的合法名称。

人口画像和损失条为原生图表；cohort 宽度和矩阵圆面积从数值推导。数值、显示标签和几何不能分别手填。
Tabler 为 SVG 矢量图片，不承诺图标路径节点可编辑。文字、形状及原生数据对象可独立编辑；
在 PowerPoint 内手工改图表数据、面积圆或旁注不会同步相关注释，应从 content 重新生成。
不支持任意自由坐标、整页截图背景、未知图表种类或未注册布局。容量不足会失败，应改用合法变体、重组或拆页。

## 0.1 → 2.0 字段迁移

- 保留八个 mck 页型入口；封面 title 从两元素数组改为可换行字符串，details 从 tuple 改为 label/value 对象。
- 年龄/收入/职业百分比 tuple 改为 label/value 的数值记录；原数值不归一化，单位和来源显式输入。
- 原 accent/color/bg 自由色改为语义 tone 枚举；样例相近旧色按实际职责映射，任意 hex 不再接受。
- 优先矩阵 size 改为 weight，直径按 sqrt(weight/maxWeight) 推导，面积才表示相对权重；x/y 为 0..1。
  原 size 按直径语义平方转换；图例、轴名和四象限标签均由 content 提供。
- interests、governance.items 和 phases.items 从位置 tuple 改为命名对象；图标字段保留并校验。
- 新增显式 detailsLabel、metricLabel、unit、labels、ownerDetail、finding.action 和可选 confidentiality；固定保密 footer 退役。
- 不提供永久旧输入转换器；修改后的 content 必须通过 2.0 schema 和实例容量检查。独立 nativeSkinning/refurbishProfile 保留，创建证据不代表源稿无损翻新。

## 验收状态

2.0.0 / production，于 2026-10-24 经维护者明确授权、三项 live benchmark 和 delivery readiness
复核后晋级；资格依据当前合同与验收记录，不继承旧版登记状态。
七组共 56 页最终 canonical PNG 已逐张检查，覆盖十六个注册布局、同内容替代构图、中英混排、异领域和密度边界。
七份 PowerPoint for Mac 16.114 保存关闭重开与完整回读通过；标题、形状持有编号、图表数据、表格单元格实际编辑后保留。
窄 rail 的五条 cohort 应使用短标签；五项 ledger 单元格最多 80 字符，中文标点可能自然换行，较长内容应改用 columns 或重组拆页。
字体不嵌入，其他系统/Office 版本及跨宿主像素一致性未验证；独立翻新路线未重做源稿保真验收。
机器、逐页视觉和原生宿主的历史证据记录于迁移报告（未随本仓库发布：
`mckinsey-blue-v2-migration-results.md`）；当前选型状态以 [catalog](../catalog.json) 为准。
