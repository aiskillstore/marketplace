# 图表（Chart）创建与编辑

当前 `add-chart` schema 发布 **27 种 chart kind**，每种支持若干 variant。把
`xdoc schema --mode ops --ops add-chart` 当作当前可写契约；操作名存在不等于内置 PDF/Viewer
拥有 PowerPoint 渲染等价性，尤其是 3D 和 ChartEx。

## 专项语义验证

chart 页的目标是原生、可编辑、语义正确，不做 SVG 像素坐标校准。写 chart 前先在
`deck_lock.slides[].chart` 记录 kind、数据来源和验证点；生成 `patch.json` 后由
`cli/create/check-lock.mjs` 做静态语义检查，再交给 xdoc dry-run / vision-check / PNG
复核。

最小检查清单：

- `categories.length` 必须和每个普通 series 的 `values.length` 一致。
- 每个 series 要有可读 `name`；多系列图尤其不能留空，否则 legend 失去语义。
- `combo` 必须真的是组合：至少两种 series kind，或至少一个 `secondaryAxis: true`。
- legend、data label、axis tick label 使用 schema 全名，不用 `b`、`r`、`outEnd` 之类简写。
- 图表要能证明 slide 的 `claimTitle` / `proofObject`，不要只因为有数据就塞图。
- PNG/contact-sheet 复核负责判断 legend、axis、data label、callout 是否遮挡；静态语义检查
  不替代视觉复核。

既有图表的显示差异先走 [fidelity diagnosis](../review/fidelity-diagnosis.md)，保留 category slot、
point index 和缺失值语义。遇到 `resource_chart_slots_exceeded`，按
[错误排查](../runtime/troubleshooting.md) 检查逻辑槽位；压缩 PPTX 不会缩小图表投影。

普通二维图表也要区分 inspect 的 chart 外框与渲染后的绘图区、轴和 legend。
外框回读正确、原生 PNG 门禁通过，不证明 PowerPoint 使用相同的内部布局或文字换行。
精确版式任务应核对同一候选的独立 PowerPoint 导出；未归因的差异保留为观察结果，
不要移动外框、缩字号或重建原生 chart 来补偿单个 renderer 的显示。

核对升级后的图表显示时，保留以下继承差别：

- data label 的删除状态有省略、显式 true、显式 false 三种。point override 先于
  最终隐藏判定：局部 false 可恢复上层隐藏的标签；局部 true 应隐藏，包括自定义文本。
  不要把省略变成 false，也不要把 parser 模型字段直接当作 patch 可写字段。
- pie/doughnut 标签未指定位置时可自动放置，不代表关闭标签。doughnut 的自动环内
  标签应位于内外半径之间；按实际 hole size 核对位置、数值与数量，不追加重复文本框。
- 显式 no-fill 图表线不会因继承线宽而重新可见；省略 paint 则可能采用自动系列色。
  同时保留 dash、category rotation（包括零）、大小写重置、语言和层级字体覆盖。
- 自动 label/legend fitting 与作者显式字号不同；检查小图、末端 category、overlay
  legend、treemap 下缘，不要为匹配旧预览统一缩小字号或改数据。

这些是源文件和渲染的诊断语义；能否写入仍以该操作的实时 schema 与 dry-run 为准。

升级后也要核对这些具体边界，先以当前 runtime 重渲染原始文件：

- 二维 bar/column 的错误值标签（如 `#N/A`）可以可见而没有有限数值柱体；保留
  error、blank、zero 的区别，以及 point 隐藏/自定义标签，不把错误改成 0 来消除显示差异。
- treemap 的行分区评分依赖实际方向与宽高；数据比例、输入身份和稳定等值次序须保持。
  分区修正不证明 legend 换行或 plot 边界已与 Office 等价，不通过排序/改值复刻旧像素。
- surface 的自动值带间隔、投影标签与 legend 容量共同规划；显式范围、间隔、log 和
  反转轴保持作者语义。轮廓应包含网格边和真实值带边界，不应暴露仅用于着色的三角剖分线；
  真实斜向刻度边界和 wireframe 仍可能可见。
- 顶视 surface/contour 的长宽来自 category/series 比例及作者 depth，再应用 manual layout；
  Web 坐标只解析一次。位置移动不应改变法线或光照，着色法线不应带入柱槽间距，自动高度
  与 fit 后尺寸也不是同一事实。核对空间轴 ticks、显式隐藏/无 outline、反转高度下的标签侧。
  当前连续高光仍是有界材质近似；网格、轮廓更准确不证明 Office 光照一致，勿改数据或相机
  去追旧颜色。精确保真仍需同候选的独立 PowerPoint 对照。
- 显式 `heightPercent` 的 3D 高度基于 category/series 数据网格及有效轴间距，水平 bar
  与竖向图表的方向处理不同；自动高度是另一策略。不要套用固定 4:3 倍率，或为了匹配旧
  预览改写高度、网格/轴参数。整体 fit、材质和相机差异仍须独立 PowerPoint 证据。

自动水平 legend 当前可在 frame 内换行，布局留白与实际绘制应使用同样的行数；
长标签、overlay 和显式 manual box 仍须单独复核。category label 位于反转/交叉轴的
另一侧时，应检查其实际物理侧与另一侧数值端点，不能靠移动 chart 外框补偿旧 renderer。

### 横向分类标签、交叉轴与裁剪

当前运行时的普通二维 bar 分类标签会按最终绘图区的可用宽度、作者字号和行密度进行
换行、字素安全缩略及自动抽样。先完成轴标题、数值刻度、边框、共享表格表头等留白后
再适配；初始外框宽度不是最终标签预算。显式 tick-label skip 仍是作者设置，manual、
combo、date 和 3D 路径也不能套用同一自动规则。保留完整 category cache、数据点位置及
显式间隔，不把图上省略号或少画的标签写回原始数据，不通过缩字号复刻旧截图。
SVG 可访问文本与 PDF ActualText 可保留完整源标签，因此 PDF 提取到长文本而 PNG
显示缩略是可能的；提取结果不能证明所有分类文字都已绘出或没有溢出。

普通二维数值轴穿过分类轴时，核对分类序号、类别间距、反转方向与内部交叉位置；
轴线、ticks、标签、display units 的锚点可以独立。显式 `crosses=max` 不等同于刚好位于
最大分类坐标的自定义 crossing。不要把轴一律推到外边缘，或按数值 X 轴解释分类序号。

面积填充/渐变/轮廓按 resolved plot 边界裁剪，但标签独立绘制；line/stock markers 按
实际累计值判断是否在域内。边界附近的浮点误差不应吞掉合法堆叠 marker，真正越界的
marker 则不应被夹到轴上。测试反转/log/百分比轴及大偏移窄域，不改值或放宽显式 bounds
来“找回”本应隐藏的图形。

### 曲面图的独立坐标轴与 paint

category/depth 轴分别解析自己的 crossing、log/linear origin 与 reversal；不要用一个
“顶轴”开关解释两者。面片投影为零面积时可不填色，但真实 mesh/wireframe 轮廓仍可能
可见。核对显式 no-fill、隐藏线、dash、alpha，以及带 `spPr` 的高度色带对整套 paint
的所有权；自动 wireframe 笔色和空心 legend key 与面填色独立，不能补成实心色块。
旧灰阶 surface palette 还依赖有效 DK1/theme override，不能按默认 accent 色强行重涂。
这些改进不证明整体拟合、legend 密度、材质和 Office 光照已完全一致。

### 3D 相机、曲面材质与轴框诊断

本节描述已有对象的解析/渲染语义，不能把模型字段直接塞进 patch。
`chart-3d/pdf-rendering` 与 `chart-3d/viewer-rendering` 仍按实时 capability truth 的
`partial` 边界处理；精确视觉验收保留同候选的独立 PowerPoint 对照。
当前两条渲染合同均披露 surface/surface3D 的高度区间图例、contour 坡度光照和有界
连续渐变/alpha；不要再把“3D surface 图例只列系列”或“渐变只取首 stop”当作固定限制。
作者 bounds、隐藏/删除项与 paint 所有权仍须核对；字体、自动布局及纹理/高光采样的
差异仍按当前 limits 和实际输出诊断，分别保留 PDF 与 Viewer 证据。

- 自动 3D fit 先预留标题、非 overlay legend、轴标题和投影文字空间，再整体等比拟合。
  折线/曲面的缺省高度还依赖有效 category/series 网格；`midCat`、`between` 与堆叠
  方式会改变比例。显式高度、inner/outer manual layout、字号和 rotation（包括 0）
  仍独立。斜排标签、深度标签侧、水平 bar 刻度密度变化不授权改写这些声明。
  强透视以固定光学中心拟合，不用移动外框去补偿旧预览的消失点或峰值角度。
- `surface` 不一律是平面等高图：非顶视相机可投影为高度网格；缺省相机与只写部分
  `view3D` 不等价。分类/深度反转须同时作用于顶点、ticks、标签和物理坡度光照。
  平面 `between` 把网格列/标签放在槽中心、两端留半槽，主刻度在槽边；`midCat`
  或省略时首末点铺满，深度轴仍走端点。勿通过倒排数据、删高度区间或改相机修画面。
- 连续渐变共用整张曲面的作者坐标，不按三角形/色带重新起算；`between` 的半槽留白
  不属于实际网格色场。带格式的 paint 所有权、no-fill、透明度和矢量轮廓仍独立。
  真实相机的连续高光按相机空间光照及透视位置求值，右角轴使用独立光照路径。
  有界填充纹理可能在资源预算不足时整图回退为矢量面光照；这不是 PPTX 被扁平化，
  也不证明无限缩放保真。不要为掩盖接缝重复叠加半透明面或合并缺失高度的洞。
  Web 纹理的同位置渐变 stops 保留两侧颜色/alpha 跳变，恰在断点时由最后一个 stop
  拥有；包括首尾断点，不能去重或改成平滑过渡。共享纹理和单面纹理在像素尺寸分别
  取整后仍映射到完整采样边界，不能通过改 chart 外框补偿旧版拉伸/留缝。
  这项 Web 修复不证明原生 PDF 对相同渐变的支持；分别保留两条链路的实际证据。
- 值恰在色带边界时，填充归属上方物理区间；最高平面的 cap paint 是绘制规则，
  不新增数值区间或 legend 项。反转轴不改变区间身份，不能按颜色数反推数据或加假区间。
  surface/contour 自动水平 legend 共用紧凑、按列对齐的换行和高度预留；核对窄框、
  不同长度标签、末行起点、factor layout，保留 authored box、侧边及混合族的独立策略。
- 普通 3D line/column 的数值轴跟随物理 category origin，不固定在屏幕左侧；
  category crossing 按拟合后的值域解析，交叉平面、depth 边与标签侧独立。
  对 line/column/area 分别核对 auto、显式 min/max、自定义交点和反转值域；有限
  `crossesAt` 优先于 `crosses`，超域交点夹到有效边界。自定义交点恰在上界不等于
  `crosses=max` 的远侧语义。远侧交叉平面边先于不透明数据绘制，不能穿透前景实体。
  删除轴会隐藏其主框线、ticks 和标签，但不等于删除 floor/wall 或独立交叉平面。
  核对各轴自己的 color/width/dash/alpha；显式 no-fill/透明与省略不同，正线宽而
  未指定 paint 可以解析为自动黑色。不要把保留源轴线误判为新建图表配色违规。
  分类平面的平行边仍受分类轴画笔控制，depth/floor 几何边有独立归属；轴删除、
  no-fill/零宽画笔、透明画笔及隐藏标签不是同一种操作。仅隐藏画笔不应删掉标签或
  独立 floor。自动斜排的上侧分类标签向外起锚，下侧沿另一端向外；显式角度仍保留。
- 已导入的 stacked/percent-stacked 3D line ribbon 按系列顺序累积带符号端点，
  自动值域也使用累计值；percent 以绝对值总和归一，极大有限输入仍需有限结果。
  blank/error 的 ribbon 缺口不沿用普通二维 stacked line 的 error-slot 连续规则。
  这不扩大 `line-3d` writer 的 variant 集合；保留已有 grouping 和源数值。
- 3D bar 的负值 paint 需核对 point override、显式 inversion 与 no-fill 优先级，
  透明箱体的完整边线和正值面光照独立。signed area 穿越基线的前面、遮挡和反转
  仍须视觉复核。面积 profile 按基线交点拆凸单元，但端盖只属于完整 profile 或缺失
  数据分段的真实两端，内部分类截面不能重复叠加，尤其要查半透明面上的暗条。
  反向相机、反转值域与缺失数据各自核对；不要改正负号、补洞、拆系列或改成 2D。
  原生部件保留 fill alpha 不证明 PDF/PNG 已按相同透明度合成；半透明面积页需分别核对
  源 alpha、当前输出与 PowerPoint，对差异保留证据，不通过改色或去透明度掩盖。

按问题选择最小回归，不必为所有图表任务运行整套矩阵：

| 症状                 | 保留源语义的对照                               | 核对证据                                               |
| -------------------- | ---------------------------------------------- | ------------------------------------------------------ |
| 交叉轴、前后遮挡     | auto/min/max/custom、值域反转、deleted/no-fill | 交点位置、平面远边遮挡、标签与独立 floor；PDF/Web 分开 |
| 面积暗条、缺面       | 跨零值、连续半透明 profile、缺失分段、反向相机 | 正负前面、内部无重复端盖、真实分段端盖与源数据         |
| 自动斜排标签侵入数据 | high/low 物理侧、自动与显式 rotation           | 文字向外包络；不要靠移动 chart 或改字号复刻旧预览      |
| 曲面断色、透明接缝   | 重复 stops（含端点）、窄色带、共享/单面纹理    | Web 颜色/alpha 断点和完整采样边界；原生 PDF 单独判定   |

使用同一 PPTX 字节、当前运行时、相同字体/日期/比例重渲染。已有真实文件可作最小
复现；缺少触发条件时才另建合成探针，标注合成数据且不改用户源文件。机器检查与
PNG 复核之后，精确 Office 保真仍须独立 PowerPoint 证据；clean-open 只证明可打开。

读取/渲染已有 ChartEx 多层 category cache 时按连续 run 建树，分隔开的同名路径不能全局合并；
连续重复完整路径保留首条观测，不擅自求和。sunburst 的值排序、等值次序、颜色身份及
长径向标签换行与 treemap 不同。保留输入顺序与节点身份，升级后先重渲染源文件，
不要排序原始数据去复刻旧截图；原生 Office 复核要求仍然适用。

在 Studio、data-driven、结构编辑、模板跟随或手工 refurbish 路线中，只要 patch 含
add-chart / set-chart / set-chart-data / set-chart-text，apply 后保存 final-inspect.json，并运行
<skill-root>/scripts/cli/review/semantic-audit.mjs 输出 semantic-audit.json。该审计只做轻量语义门禁：
数据维度、数值类型、source/claim 披露和最终原生 chart 对象存在性；它不是完整 OOXML
chart 等价检查。semantic-audit.json 若为 fail，最终 evidence-summary 必须阻塞；warn
可以披露后继续视觉复核。

`cli/review/semantic-audit.mjs` 与 `cli/create/check-lock.mjs` 共用同一个 chart
semantic normalizer：经典 Chart 读取 `data`，ChartEx 读取 `dataEx`，并按 chart kind
检查 points/stages/values/nodes/series 等最小语义。数据来源优先读取 op 自身，再读取
`deck_lock.slides[].chart.semanticSource` / `source` / `dataSource`；不要为了消除假警告而
给 `add-chart` 伪造 schema 不存在的 `source` 字段。

## 数值精度、格式回退与区间验证

区分原始数据、PPTX 保存的数据、显示标签。`inspect` 的 chart 类型/外框和轻量语义审计
不能证明全部数值一致；精度敏感任务可用 `xdoc convert <candidate.pptx> --to json
--output <run-dir>/chart-data.json` 回读已披露的 series/points，与原始输入逐项核对。
该导出是数据投影，不是完整 chart XML、轴声明或 embedded workbook 等价证明；未披露的
属性仍需针对原生部件检查。不要把 PDF 提取的格式化标签当作原始数据。

- 当前 Web/PDF 的普通数值回退保留有限 binary64 值，不再为缩短标签截掉有效数字。
  `General`、空格式和不支持的格式可能走该回退；例如 `1234567890123` 与
  `1.23456789012345` 应保留，而显式 `0.00` 仍可显示为 `1.23`。格式回退不是完整
  Excel 格式支持，也不保证保留输入的十进制拼写。超过 binary64 精度的数据应在进入
  JSON number 前保留原始文本并明确转换限制，不能宣称已经丢失的位数可被渲染器恢复。
- 对升级后变长的标签，先核对数值与格式，再检查实际渲染的遮挡。只有任务允许改变
  显示格式时才设置 `numberFormat` 或轴 `displayUnits`；保留底层数据，不做预先舍入。
- 线性轴 ticks 在极小/极大域和窄区间应保持可区分、有限且有序；浮点清理不能吞掉
  作者显式 origin/bounds 或真实尾区间。全负数据的自动上界不总是零，窄负域也不应被
  强制拉到零；按实际数据域检查，勿用旧截图反推固定 min/max。非法 log domain 或
  冲突的显式 bounds 不能靠伪造 ticks/gridline 掩盖，需回到数据与作者意图处理。
- 直方图保留原始重复样本和区间闭合规则。有限样本的跨度/偏移也可能在中间运算溢出，
  如 `[-1e308, 1e308]`；当前渲染器可保持有限区间端点。检查标签没有 `NaN`/`Infinity`，
  并核对每箱计数与总和，不能仅因图像存在就判定通过。不要手工缩放或截断观测值。
  自动边界标签可作有界六位有效数字显示舍入，但精确边界、闭合方向和样本归属不变；
  窄域仍须保留能区分边界的精度，显式格式独立。别把短标签写回 bin edges。
- 曲面图的 legend 表示高度区间，不是空间系列名。自动边界可消除浮点噪声造成的多余
  色带，例如范围 `0..0.3`、`majorUnit=0.1` 应有三个区间；作者显式设置的
  `max=0.30000000000000004` 则保留最后的极小区间。大数偏移下的窄区间、包含真实
  观测值的尾区间也不能按相对容差合并。反转轴时同时核对区间顺序与颜色对应，勿倒排
  原始数据来修复图例；数值不同的边界即使格式化后同名，也仍是不同边界。

仅对任务相关的边界制作小型验证页：大整数、长小数与固定格式对照；跨正负极值的
直方图；自动/显式/反转轴的 surface 与 surface-3d。用同一运行时、字体和冻结日期生成
canonical PDF/PNG，提取 PDF 标签作辅助断言，再检查实际图像。保留数据回读、区间/计数
核对与渲染证据；按既有 ChartEx/3D 规则补 PowerPoint 证据。这些改进不扩大 authoring
能力，也不把 xdoc 自身的 PDF/JSON 交叉检查升级为 Office 保真认证。

## 自动轴、标签适配与正负百分比堆叠

升级后先重渲染同一源文件；自动布局可能改变 ticks、换行、斜排或缩写，而原始数据不变。
作者显式 major unit、rotation（包括 0）和 manual layout 优先，不能把自动策略当作
覆盖作者声明的理由。当前 Web/PDF 的适配仍是 Office 布局近似，需分别记录消费者。

- 显式 min 或 max 是刻度锚点；自动间隔不能移动该边界。窄正值域不应被一律拉到零，
  自动 logarithmic surface 需核对正值域、数量级、有限 ticks 和高度色带；非法非正 log
  数据仍需处理，不能靠造刻度掩盖。不要从旧预览抄 min/max 来抵消升级变化。
- 水平轴按真实文字 advance 估算容量；line/area 数值轴还考虑字号与可读间距。
  column 的数值刻度密度和 category fitting 是不同决策：category 可能先换行，再斜排，
  最后按绘图区、轴交叉和标题空间缩写。不要为增加 category 空间而强制改变数值间隔。
  普通水平数值轴与 3D/百分比/垂直轴的密度策略不同；水平 bar 轴标题按物理侧预留和
  绘制，不能只按 XML 中的轴角色猜位置。category 标签侧与数值轴 crossing 也独立。
- 普通 smooth categorical line 的自动值域采用端点和曲线内部采样，保留真实极值、
  gap/error 连续性与显式 bounds；不要只取源点范围，也不要改点值来恢复旧的自动轴。
  signed area 沿源顺序使用同一带符号基线，bar 正负分开；窄负域和百分比端点不应
  被强制添加正值空间。二维 logarithmic contour 的自动指数步长也不同于 3D 或显式 unit。
- 缩写只改变绘制文字。Web 可访问标签/title 与 PDF 文本提取可保留完整 category，
  所以提取到全文不证明 PNG 上显示全文，也不能因此报告重复或漏字。分别核对原始
  category 顺序、数据回读和实际 PNG；不能截短源 category 去匹配画面。
- signed percentage area 与 3D bar 堆叠以每个 category 的绝对值总和为共同分母，
  但累积规则不同。对按源系列顺序的 `[30, -10]`，贡献分别为 `+75%/-25%`：
  area 沿同一带符号基线累积，边界为 `0 → 75% → 50%`；3D bar 正负各自累积，
  两段为 `0 → 75%` 和 `0 → -25%`。不能跨图表家族套用基线、重排系列，或使用
  代数和得到 `150%/-50%`，也不把正负两侧各自归一到 100%。核对段基线、边界、
  反转方向及原始数值；百分比坐标不意味着底层值已经改成百分数。

针对实际任务选择控制页：自动/显式单边界、窄正值域、长 category/大字号/轴交叉、
正负混合百分比。对 3D 和精确 Office 布局沿用专项审计与独立 PowerPoint 证据，
不要以 xdoc PDF 与自身 PNG 一致代替 Office 验证。

## Native diagram/table presets

常见商务图示优先用 `add-slide.recipe` preset，而不是手算几十个 `add-shape` 坐标。
这些 preset 会编译成原生可编辑 PPTX 对象，支持 `theme` 字段随 themePack 改色：

| preset           | `recipe.kind`      | 输入字段                       | 适用场景                     |
| ---------------- | ------------------ | ------------------------------ | ---------------------------- |
| Timeline         | `timeline`         | `title`, `items[]`             | 里程碑、发布节奏、历史演进   |
| Roadmap          | `roadmap`          | `title`, `phases[]`            | 产品规划、季度计划、阶段目标 |
| 2x2 Matrix       | `matrix-2x2`       | `title`, `quadrants[4]`        | 优先级、定位、风险收益       |
| Process Flow     | `process-flow`     | `title`, `steps[]`             | 流程、操作步骤、转化前段     |
| Funnel           | `funnel`           | `title`, `stages[]`            | 销售漏斗、转化分析、pipeline |
| SWOT Matrix      | `swot`             | `title`, 四个象限列表          | 战略评估、市场分析、工作坊   |
| Pyramid          | `pyramid`          | `title`, `levels[]`            | 层级、成熟度、运营模型       |
| Hub Spoke        | `hub-spoke`        | `title`, `hub`, `spokes[]`     | 平台生态、能力地图、干系人   |
| Cycle            | `cycle`            | `title`, `steps[]`             | 反馈闭环、运营节奏、复盘流程 |
| Gantt            | `gantt`            | `title`, `tasks[]`             | 交付计划、项目排期、里程碑   |
| Scorecard Table  | `scorecard-table`  | `title`, `headers[]`, `rows[]` | 评分卡、供应商评估、就绪度   |
| Comparison Cards | `comparison-cards` | `title`, `cards[]`             | 方案比较、功能分组、场景权衡 |

### Timeline

```json
{
  "op": "add-slide",
  "recipe": {
    "kind": "timeline",
    "title": "Launch timeline",
    "items": [
      { "date": "Q1", "label": "Design", "text": "Prototype" },
      { "date": "Q2", "label": "Beta", "text": "Pilot customers" },
      { "date": "Q3", "label": "GA", "text": "Launch" }
    ],
    "theme": { "accent": "0A6BFF", "text": "111827", "muted": "667085", "background": "FFFFFF" }
  }
}
```

### Roadmap

```json
{
  "op": "add-slide",
  "recipe": {
    "kind": "roadmap",
    "title": "Product roadmap",
    "phases": [
      { "label": "Now", "period": "Q1", "items": ["Stabilize core", "Instrument usage"] },
      { "label": "Next", "period": "Q2", "items": ["Self-serve onboarding", "Partner API"] },
      { "label": "Later", "period": "Q3", "items": ["Enterprise controls"] }
    ]
  }
}
```

### 2x2 matrix

`quadrants` 必须正好 4 项，按左上、右上、左下、右下顺序填。

```json
{
  "op": "add-slide",
  "recipe": {
    "kind": "matrix-2x2",
    "title": "Prioritization matrix",
    "xAxis": "Impact",
    "yAxis": "Effort",
    "quadrants": [
      { "label": "Quick wins", "text": "Ship now" },
      { "label": "Big bets", "text": "Sequence carefully" },
      { "label": "Fill-ins", "text": "Batch work" },
      { "label": "Avoid", "text": "Revisit later" }
    ]
  }
}
```

### Process flow

```json
{
  "op": "add-slide",
  "recipe": {
    "kind": "process-flow",
    "title": "Sales process",
    "steps": [
      { "label": "Lead", "text": "Inbound capture" },
      { "label": "Qualify", "text": "Score fit" },
      { "label": "Close", "text": "Contract" }
    ]
  }
}
```

### Funnel

```json
{
  "op": "add-slide",
  "recipe": {
    "kind": "funnel",
    "title": "Conversion funnel",
    "stages": [
      { "label": "Visitors", "value": "120k" },
      { "label": "Trials", "value": "18k" },
      { "label": "Paid", "value": "3.2k" }
    ]
  }
}
```

### SWOT matrix

```json
{
  "op": "add-slide",
  "recipe": {
    "kind": "swot",
    "title": "Market view",
    "strengths": ["Brand", "Retention"],
    "weaknesses": ["Long sales cycle"],
    "opportunities": ["New segment"],
    "threats": ["Price pressure"]
  }
}
```

### Pyramid

```json
{
  "op": "add-slide",
  "recipe": {
    "kind": "pyramid",
    "title": "Operating model",
    "levels": [
      { "label": "Strategy" },
      { "label": "Programs", "text": "Cross-functional bets" },
      { "label": "Execution" }
    ]
  }
}
```

### Hub spoke

```json
{
  "op": "add-slide",
  "recipe": {
    "kind": "hub-spoke",
    "title": "Platform ecosystem",
    "hub": "Core API",
    "spokes": [
      { "label": "Partners" },
      { "label": "Apps" },
      { "label": "Data" },
      { "label": "Automation" }
    ]
  }
}
```

### Cycle

```json
{
  "op": "add-slide",
  "recipe": {
    "kind": "cycle",
    "title": "Learning loop",
    "steps": [
      { "label": "Plan" },
      { "label": "Build" },
      { "label": "Measure" },
      { "label": "Learn" }
    ]
  }
}
```

### Gantt

`date` 和 `value` 分别作为开始/结束标签；当前 preset 生成可编辑的任务条，不依赖图表对象。

```json
{
  "op": "add-slide",
  "recipe": {
    "kind": "gantt",
    "title": "Delivery plan",
    "tasks": [
      { "label": "Design", "date": "Jan", "value": "Feb" },
      { "label": "Build", "date": "Feb", "value": "Apr" },
      { "label": "Launch", "date": "May", "value": "Jun" }
    ]
  }
}
```

### Scorecard table

```json
{
  "op": "add-slide",
  "recipe": {
    "kind": "scorecard-table",
    "title": "Vendor scorecard",
    "headers": ["Vendor", "Score", "Risk"],
    "rows": [
      ["A", "92", "Low"],
      ["B", "84", "Medium"]
    ]
  }
}
```

### Comparison cards

```json
{
  "op": "add-slide",
  "recipe": {
    "kind": "comparison-cards",
    "title": "Options",
    "cards": [
      { "label": "Fast", "text": "Ship now" },
      { "label": "Balanced", "text": "Stage rollout" },
      { "label": "Deep", "text": "Invest more" }
    ]
  }
}
```

## chart kind × variant 速记

| kind                                                  | 推荐 variant                                                              | 备注                                                                                                             |
| ----------------------------------------------------- | ------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| `column` / `bar`                                      | `clustered` / `stacked` / `percent-stacked`                               | 最常用                                                                                                           |
| `column-3d` / `bar-3d`                                | `clustered` / `stacked` / `percent-stacked`                               | 3D 版本                                                                                                          |
| `line`                                                | `standard` / `markers` / `stacked` / `percent-stacked`                    | 加 marker 用 `markers`                                                                                           |
| `line-3d`                                             | `standard`                                                                | 仅一种                                                                                                           |
| `area` / `area-3d`                                    | `standard` / `stacked` / `percent-stacked`                                |                                                                                                                  |
| `pie` / `pie-3d`                                      | `standard` / `exploded`                                                   | exploded 拉开扇区                                                                                                |
| `doughnut`                                            | `standard` / `exploded`                                                   | 圈饼图                                                                                                           |
| `radar`                                               | `standard`                                                                | 雷达                                                                                                             |
| `scatter`                                             | `markers` / `lines` / `lines-no-markers` / `smooth` / `smooth-no-markers` | XY 散点                                                                                                          |
| `bubble` / `bubble-3d`                                | `standard`                                                                | 气泡（含 size 维度）                                                                                             |
| `stock`                                               | `standard`                                                                | HLC/OHLC K 线                                                                                                    |
| `surface` / `surface-3d`                              | `standard` / `wireframe`                                                  | 曲面                                                                                                             |
| `combo`                                               | `standard`                                                                | 组合图；支持每个 series 加 `secondaryAxis: true`                                                                 |
| `waterfall` / `funnel` / `histogram` / `pareto`       | `standard`                                                                | chartEx 系列（写到 `ppt/charts/chartExN.xml`）；前三者用 `dataEx`，`pareto` 用普通 `data`                        |
| `treemap` / `sunburst` / `box-whisker` / `region-map` | `standard`                                                                | chartEx 系列；treemap/sunburst 用 `dataEx.nodes[]`，box-whisker 用 `dataEx.series[]`，`region-map` 用普通 `data` |

不合法的 kind/variant 组合在写之前就会被 schema 拒绝；apply 前用 `--dry-run` 兜底。

## 数据结构（关键）

### 直角坐标系（column / bar / line / area / radar / pie / doughnut）

```json
{
  "categories": ["Q1", "Q2", "Q3", "Q4"],
  "series": [
    { "name": "2025", "values": [10, 12, 14, 16] },
    { "name": "2026", "values": [15, 18, 21, 24] }
  ]
}
```

### XY 散点 / 气泡

```json
{
  "series": [
    {
      "name": "Region A",
      "points": [
        { "x": 1.0, "y": 2.0 },
        { "x": 1.5, "y": 3.2 }
      ]
    }
  ]
}
```

bubble 多一个 `size`：

```json
{ "x": 1.0, "y": 2.0, "size": 0.5 }
```

### Stock（K 线）

```json
{
  "categories": ["2025-01", "2025-02"],
  "open": [10, 12],
  "high": [15, 17],
  "low": [8, 9],
  "close": [12, 14]
}
```

`open` 可省略 → HLC；含 `open` → OHLC。volume stock 暂未支持。

Stock 数据必须先做语义不变量检查，再写入或交付：

- HLC：每个 category 上必须满足 `low[i] <= close[i] <= high[i]`。
- OHLC：每个 category 上必须满足
  `low[i] <= min(open[i], close[i], high[i])` 且
  `high[i] >= max(open[i], close[i], low[i])`。
- 修复单个异常点时，优先做最小数据改动，保持趋势、类别、系列名称和图表样式不变。
- 用 `set-chart-data` 修改既有 stock chart 时，xdoc 会同步 chart XML 和 embedded
  workbook；不要用 raw XML 只改 `ppt/charts/chartN.xml`，否则 PowerPoint 刷新图表时
  可能从 workbook 恢复旧数据。

### Combo

`combo` 的 `data.series` 每个元素可加 `kind`（覆盖 chart kind）；要把某个系列
挂到次坐标轴上,加 `secondaryAxis: true`:

```json
{
  "kind": "combo",
  "data": {
    "categories": ["Q1", "Q2", "Q3", "Q4"],
    "series": [
      { "name": "Revenue", "kind": "column", "values": [10, 12, 14, 16] },
      { "name": "Growth %", "kind": "line", "values": [5, 8, 12, 15], "secondaryAxis": true }
    ]
  }
}
```

校验规则:同一个 combo **要么** 包含 ≥2 种 plot kind(column/line/area 任意两个),
**要么** 至少有一个 `secondaryAxis: true` 的系列;两者满足其一即可通过。换句话说,
单 plot kind + 二轴(经典"柱+折线但都是 column"的伪二轴)现在合法。

### ChartEx（waterfall / funnel / histogram / pareto / treemap / sunburst / box-whisker / region-map）

走同样的 `add-chart`,kind 选对即可;内部会写入 `ppt/charts/chartExN.xml`(modern
chart 部件),并自动建立 `chartEx` 关系类型。`variant` 必须是 `standard`。
`dataEx` 只接受 6 种 kind：waterfall(`points[]`) / funnel(`stages[]`) / histogram(`values[]`) /
treemap、sunburst(`nodes[]`) / box-whisker(`series[]`)；`pareto` 与 `region-map` 不接受 `dataEx`
（schema 直接 union-no-match），必须用普通 `data.categories` / `data.series`，xdoc 仍会写成 chartEx 部件。
这里的 kind 是图表类别，不是每种 `dataEx` 都能带 `kind` 字段。hierarchy 的可选
`dataEx.kind` 用于 treemap/sunburst；histogram 等载荷按自己的 schema 写 `values[]`
等字段，不追加该 discriminator。
其余 PowerPoint-only 图表必须使用 ChartEx 专用 `dataEx` 载荷，不要把普通
`data.categories` / `data.series` 当作等价输入，除非当前 xdoc schema 明确说明支持自动
lowering。对照参考 deck 时，以 PowerPoint 生成的 `chartEx*.xml` 语义为准，而不是用
普通 chart 经验猜维度、axis、dataLabels 或 layoutPr。

```json
{
  "op": "add-chart",
  "slide": 0,
  "kind": "waterfall",
  "variant": "standard",
  "x": "1in",
  "y": "1.5in",
  "w": "10in",
  "h": "5in",
  "title": "现金流桥接",
  "dataEx": {
    "points": [
      { "label": "起始", "value": 100, "kind": "total" },
      { "label": "Q1", "value": -20, "kind": "decrease" },
      { "label": "Q2", "value": 35, "kind": "increase" },
      { "label": "Q3", "value": 50, "kind": "increase" },
      { "label": "结束", "value": 165, "kind": "total" }
    ]
  }
}
```

ChartEx 语义要点：

- 非空 `title` 会写入原生 `cx:title/cx:tx/cx:txData/cx:v`。省略或传空白标题时
  不写空 `cx:title`，避免 PowerPoint 合成 “Chart Title”；后续
  `set-chart-data.dataEx` 会保留既有标题。
- ChartEx 目前不支持用 `add-chart.legend` 显式控制 legend 位置。显式传入会
  fail closed，而不是被静默忽略；需要自定义 legend 时省略该字段并使用独立的
  可编辑文本/形状，或保留当前 PowerPoint 默认 legend 语义。
- `waterfall`：`points[].kind` 使用 `increase` / `decrease` / `subtotal` / `total`；
  subtotal/total 应映射到 `<cx:subtotals>`，不要凭空写 `<cx:aggregation/>`。
- `funnel`：`stages[]` 的数值维度应是 `numDim type="val"`，不是 `size`；通常需要
  value data labels 和 funnel 自己的 category axis gapWidth。
- `histogram`：用原始样本 `values[]`，PowerPoint 语义通常是
  `layoutId="clusteredColumn"` + `<cx:binning intervalClosed="r">`，不是自造普通柱图。
  保留重复样本和原始数值精度；不要预聚合为普通柱图、去重或先四舍五入。核对每个区间的
  左/右闭合规则、边界值与计数总和，尤其是小数箱宽、大数偏移和极小间隔。已有 OOXML
  的 binSize/binCount/underflow/overflow 等设置属于需要检查的输入语义；可写字段仍以
  当前 `add-chart` / `set-chart-data` schema 为准，不能把 renderer 的内部字段当 patch 字段。
  检查新生成的包时，Office 的 `cx:binSize` / `cx:binCount` 数值写在 `val` 属性中，
  不要改成元素文本以迎合名义 simple-content schema。优先让原生 chart op 生成，
  保留缓存/嵌入工作簿一致性检查，并通过 PowerPoint clean-open 验证；静态图像正常
  或 schema 单独通过都不能排除 Repair。导入图表的既有 binning 声明仍需按源证据处理。
- `sunburst` / `treemap`：层级输入可用 `nodes[]`，但写入 ChartEx 时通常只输出叶子行；
  多级 category cache 按 PowerPoint 的 leaf-to-root 层级顺序写入，不能把中间节点也当成
  独立 data point。
- `box-whisker`：每个 series 可带 `categories[]`，长度必须等于 `values[]`；重复的
  `Day1` / `Day2` / `Day3` 等 category label 用来形成分组轴，不能退化成单一 category。
- 参考 deck 复刻时，优先复用同类型既有 ChartEx 的 `chartStyle` / `chartColorStyle`
  关系，并补 parser/generator 回归测试固定上述语义。
- 修改既有 chart（经典或 ChartEx）的系列配色时，优先用 `set-chart.colorStyle`
  重写 colorStyle part（见下节），不要对 `colors*.xml` 写 raw OOXML。

### 系列配色：`set-chart.colorStyle`（经典 + ChartEx 通用）

chart 的系列默认颜色来自 chart part 关联的 colorStyle part（`ppt/charts/colors*.xml`，
`cs:colorStyle` 颜色循环）：系列 i 在无内联 fill override 时取 `colors[i % n]`。
`set-chart.colorStyle` 是编辑该循环的高层 op，经典 `c:` 与 ChartEx `cx:` 图表通用：

```json
{
  "op": "set-chart",
  "slide": 42,
  "shape": { "id": 22 },
  "colorStyle": { "method": "cycle", "colors": ["1B2566", "C9563B", { "scheme": "accent3" }] }
}
```

- `colors` 是完整替换的颜色循环（hex 字符串或 `{"scheme": ...}` 主题色）；
  既有 `cs:variation` 与 style-family `id` 保留。
- `method` 映射 `meth` 属性（`cycle` / `withinLinear` / `acrossLinear` /
  `withinLinearReversed` / `acrossLinearReversed`），省略时保留原值。
- chart 没有 colorStyle part 时会自动创建并注册 rels / Content-Types。
- dry-run 的 `semanticChanges` 会输出 `before -> after` 颜色 token diff，
  可在 apply 前确认改动命中的 part 与颜色。
- 一个 colors part 可能被多个同类 ChartEx 共享（创建时按 kind 复用关系）；
  共享时 apply 会报 `chart-color-style:` warning 并给出引用数——确认是否
  有意让全部引用图表同步换色。
- ChartEx 数据标签文字颜色走 `set-chart.dataLabels[].font`（写
  `cx:dataLabels/cx:txPr`），不再需要 raw XML；`numberFormat` / `separator` /
  `showPercentage` / `showLegendKey` 在 ChartEx 上仍会明确拒绝。
- xdoc 预览对 colorStyle 的还原不保证与 PowerPoint 一致；最终视觉仍按下文
  ChartEx PowerPoint baseline 规则复核。

### 系列配色对比度指引

选择 `colorStyle.colors` / 系列色时，按以下通用规则减少人工试色与返工：

- 创建图表或在本次获授权范围内重新配色时，文字、线条可使用黑色，但不要让
  数据系列、柱体、面积、饼片、层级区域、曲面色带或图表背景出现大面积黑色／近黑色填充。
  可用不同明度的灰色替代，也可选有足够对比度的主题色；不必为了避黑而统一换成浅灰。
  3D 图表还要检查挤出侧壁与阴影面，避免正面已经换色、侧面仍成为大片近黑色。
  在 PNG／Web 视觉复核时检查实际填充、相邻区域区分度及标签可读性，不能只检查色值配置。
  保留源稿的编辑任务不因此自动获得重配色授权。
- 浅色背景（paper/白）配深色系列（如 navy/deep coral/teal 系），保证
  柱/线与背景对比度 ≥ 3:1；数据标签文字与其所在填充色对比度 ≥ 4.5:1。
- 数据标签压在系列填充上时，标签颜色相对填充色取深色（深底白字/浅底深字），
  不要沿用主题 accent 亮色（亮黄标签压珊瑚填充是本条的反例）。
- 系列数超过调色板长度时颜色会循环；相邻系列避免只靠亮度区分，
  优先给出 ≥ 系列数的颜色数组而不是依赖 `withinLinear` 自动变体。
- 色盲可区分性：避免仅红/绿对比，优先蓝-橙、蓝-棕等组合。

> ⚠️ chartEx 部件在 PowerPoint 2016+ 才完整支持;部分老旧渲染器(WPS 旧版、
> LibreOffice <7.4) 会忽略 chartEx 节点回退到 fallback 图。要 100% 兼容时优先
> 用经典 chart(column 模拟 waterfall、bar 模拟 funnel)。

## 创建图表

```json
{
  "op": "add-chart",
  "slide": 0,
  "kind": "column",
  "variant": "clustered",
  "x": "1in",
  "y": "1.5in",
  "w": "8in",
  "h": "5in",
  "name": "Revenue Chart",
  "title": "营收趋势",
  "legend": "bottom",
  "data": {
    "categories": ["Q1", "Q2", "Q3", "Q4"],
    "series": [
      { "name": "2025", "values": [10, 12, 14, 16] },
      { "name": "2026", "values": [15, 18, 21, 24] }
    ]
  }
}
```

`legend` 位置（**必须用全名**，shorthand 不接受）：
`right / left / top / bottom / top-right`。没有 `none` / `corner`；不要 legend 时省略该字段，
再用 `set-chart.legend` 或视觉复核处理。

> ⚠️ schema 严格匹配 — `"b"` / `"r"` / `"tr"` 之类的简写都会被拒绝。

### 创建原生日期轴（`c:dateAx`）

日期轴创建必须显式写 `categoryAxis.type: "date"`；xdoc 不会根据
`data.categories` 的字符串外观猜测日期语义。类别必须是严格 Gregorian
`YYYY-MM-DD`，范围 `1900-01-01..9999-12-31`。写出时 chart cache 和 embedded
workbook 都使用 Excel 1900 日期系统数值，并显式写入 `c:date1904 val="0"` 与
`workbookPr date1904="0"`，避免 PowerPoint for Mac 按 1904 系统偏移 1462 天；`1900-02-29`
是 Excel 的虚构日期，输入会被拒绝，而 `1900-02-28` / `1900-03-01` 分别写为 59 / 61。

```json
{
  "op": "add-chart",
  "slide": 0,
  "kind": "line",
  "variant": "markers",
  "x": "1in",
  "y": "1.5in",
  "w": "10in",
  "h": "5in",
  "name": "Monthly Revenue",
  "categoryAxis": {
    "type": "date",
    "formatCode": "mmm yyyy",
    "baseTimeUnit": "days",
    "majorUnit": 1,
    "majorTimeUnit": "months",
    "minorUnit": 7,
    "minorTimeUnit": "days"
  },
  "data": {
    "categories": ["2026-01-01", "2026-02-01", "2026-03-01"],
    "series": [{ "name": "Revenue", "values": [10, 14, 18] }]
  }
}
```

支持 column/bar/line/area/radar/surface 及其 3D 对应类型。pie/doughnut、
scatter/bubble、stock/combo 和所有 ChartEx `dataEx` kind 都会 fail closed。
`formatCode` 默认 `yyyy-mm-dd`；时间单位只接受 `days / months / years`，
`majorUnit` / `minorUnit` 必须为正数。生成器会保留正确的 axId、position、scaling、
delete 和 crossAx 配对，并把 series category cache 写成带格式码的 `c:numRef/c:numCache`。

## 编辑图表

### 只改文本 / 翻译 label

翻译 chart title、category labels、series names、data labels 时，优先用 top-level
安全命令：

```bash
xdoc pptx replace-chart-text \
  --source source.pptx \
  --data chart-replacements.json \
  --output translated.pptx \
  --visible-cache-only \
  --dry-run \
  --json > replace-chart-text-dry-run.json
```

输入 JSON 使用 role + sourceText/sourceHash + targetText 定位已有可见 cache
文本；`index` 是同一 chart part 内该 role 的 0-based 序号：

```json
{
  "schemaVersion": "pptx-chart-text-replacements/v1",
  "replacements": [
    {
      "part": "ppt/charts/chart1.xml",
      "role": "category",
      "index": 0,
      "sourceText": "产品",
      "targetText": "Product"
    }
  ]
}
```

经典 Chart 和 ChartEx 的应用默认标题 `Chart Title` 可能不是普通可见文本节点。
翻译模式下不要搜索这个字面量，也不要手工构造标题 selector；应直接使用
`i18n-scan` inventory 经 `i18n-plan.replaceChartText` 生成的 replacement。此类
replacement 会额外携带 `sourceState=generated-default-title`、`chartDialect` 和
`structureSignature`，三个守卫字段必须原样保留。`replace-chart-text` 会在写入前
重新验证状态，并只物化对应 dialect 的最小标题文本子树，保留已有 layout、overlay、
shape properties 和 text properties。

该 generated-title 路径只适用于标题容器中完全没有对应 dialect `tx` 子节点的情况。
只要已经存在任何 `tx`（包括空的 rich-text 容器），就必须 preserve/manual-review；
不要自动补文本，也不要用临时 OOXML fallback 绕过这个安全边界。

只有 dry-run 报告满足 `agentGate.passed=true`、`changedNodes[]` 符合预期、
`structureChecks[]` 全部通过时，才去掉 `--dry-run` 写候选文件。该命令只写
OPC 声明为 Chart/ChartEx 的部件中的可见文本节点，不依赖路径或扩展名；不会修改 external workbook path、chart
relationship target、embedded workbook 数据/sharedStrings 或 `formatCode`。

普通 chart 编辑仍可用 patch op `set-chart-text`。它会改已有 chart 文本缓存和
embedded workbook 中对应标签，不重建 chart data XML，适合需要保持 workbook-backed
chart 标签同步的非翻译场景。

```json
{
  "op": "set-chart-text",
  "slide": 1,
  "shape": { "name": "Revenue Chart" },
  "title": "Revenue Trend",
  "categories": [
    { "index": 0, "text": "Q1" },
    { "index": 1, "text": "Q2" }
  ],
  "series": [{ "index": 0, "name": "Actual" }]
}
```

不要把 `set-chart-data` 当作 chart 文本翻译工具：它会重建 chart XML / workbook
数据区域，适合真的替换数据集，但可能丢失或重排既有标题、layout、样式和扩展节点。
patch op `set-chart-text` 目前只覆盖经典 chart part。翻译模式下，top-level
`xdoc pptx replace-chart-text --visible-cache-only` 已原生支持经典 chart 与 ChartEx，
并通过 namespace-aware 定位处理 ChartEx direct/nested point text，以及两种 dialect
的 generated default title。ChartEx 翻译应优先使用该 helper；未知扩展结构和任何
已有 `tx` 的标题默认 preserve-only。只有不涉及上述安全边界、helper 明确报告不支持、
且确实需要修改时，才使用带完整报告、ZIP/XML 校验与 clean-open 验证的定向 OOXML
fallback。

### 改数据

```json
{
  "op": "set-chart-data",
  "slide": 1,
  "shape": { "name": "Revenue Chart" },
  "data": { "categories": [...], "series": [...] }
}
```

ChartEx 使用同一个 `set-chart-data` op，但载荷仍是 `dataEx`。它只替换 ChartEx
数据维度并保留已有 native title；不要把普通 `data` 当作 ChartEx 的等价输入：

图表判别只用 `kind`。创建时以 `add-chart.kind` 为准，层级 `dataEx.kind` 若提供必须
一致；更新 treemap/sunburst 的 `nodes[]` 时必须显式提供 `dataEx.kind`，执行器会核对
目标的现有类型，不会靠数据提示换成另一种图表。组合系列的 `kind` 使用 `column`、
`line` 或 `area`；`chartKind`、`type` 判别和 `columnChart` 等同义值均不可用。

```json
{
  "op": "set-chart-data",
  "slide": 1,
  "shape": { "name": "Conversion Funnel" },
  "dataEx": {
    "stages": [
      { "label": "Visitors", "value": 120000 },
      { "label": "Trials", "value": 18000 },
      { "label": "Paid", "value": 3200 }
    ]
  }
}
```

改完 chart 数据后，至少做三步验证：

1. dry-run 中确认 `resolvedSelectors[]` 命中目标 chart，`changedParts[]` 包含 chart
   part；若是 embedded workbook-backed chart，也应看到 workbook part 变化。
2. 对关键业务语义做轻量审计，例如 stock 的 low/high 不变量、series/category 长度一致、
   legend 系列名不为空。把结果保存到 run 目录（如 `semantic-audit.json`）。
3. 做视觉复核。优先用 `xdoc pptx preview` 生成预览；若某类复杂/长尾 chart 没有渲染完整图体，
   不要把空白预览当作 deck 内容缺失；改用 PowerPoint、LibreOffice、PDF 渲染或用户提供的
   权威预览作为视觉依据，并在 `visual_review.json` 中记录 fallback 原因。

### 一键换 PowerPoint 内置 style（1-48）

```json
{ "op": "set-chart", "slide": 1, "shape": {...}, "style": 6 }
```

清掉：

```json
{ "op": "set-chart", "slide": 1, "shape": {...}, "style": null }
```

PowerPoint 内置 1-48 covers warm/cool/mono/contrast 各种预设，比手动调色快。

### 修改 3D 视角

```json
{
  "op": "set-chart",
  "slide": 1,
  "shape": { "name": "Revenue 3D" },
  "view3D": {
    "rotX": 20,
    "rotY": 35,
    "rightAngleAxes": false,
    "perspective": 60,
    "depthPercent": 120,
    "heightPercent": 90
  }
}
```

`view3D` 仅能写入含原生 3D chart group 的图表；对 2D 或 ChartEx 目标会在 mutation
前 fail closed。每个字段设 `null` 会移除对应 OOXML 元素，省略则保留。
`rightAngleAxes: true` 时 perspective 不生效。apply 后通过 inspect 的
`chart.supportsView3D`、`chart.kind`、`chart.view3D` 回读场景值。

原生 OOXML authoring 是 supported，但 PDF 和 bundled Viewer 的 3D rendering 分别是
partial：投影、遮挡和默认着色有覆盖，不保证 bevel、material、custom lightRig 或所有
surface/legend 细节与 PowerPoint 相同。验收精确 Office 视觉保真时，必须对照同一候选的
PowerPoint 原生渲染；clean-open 只证明没有观察到打开/修复问题，不能代替像素复核。
原生证据不可用时如实标记未验证，按用户的实际验收要求处理，不能用 xdoc PNG/PDF
单独证明 Office parity。

### 改标题

标题文本和标题样式是两个 op：`set-chart-text` 改文字，`set-chart` 改样式：

```json
{ "op": "set-chart-text", "slide": 1, "shape": {...}, "title": "2026 vs 2025 营收" }

{
  "op": "set-chart",
  "slide": 1,
  "shape": {...},
  "title": { "font": { "name": "Inter", "size": "16pt", "bold": true, "color": "1F1F1F" } }
}
```

标题 font 的稀疏更新会作用于实际显示的 rich runs/fields/breaks 及已有段落默认值；
只改 color 不应擅自补 bold。标题替换应保留显式字体默认值，formula cache 与相邻
title/axis 样式另行核对。验证真实显示文字及源 run 属性，不只检查外层 `txPr`。

### 改图例

```json
{
  "op": "set-chart",
  "slide": 1,
  "shape": {...},
  "legend": {
    "position": "bottom",
    "includeInLayout": false,
    "font": { "name": "Inter", "size": "10pt" }
  }
}
```

`legend` 还支持 `horizontalOffset`（数值，水平偏移，取值 -1..1，超出会报
`legend horizontal offset must be between -1 and 1`）。

### 改坐标轴

```json
{
  "op": "set-chart",
  "slide": 1,
  "shape": {...},
  "axes": [
    {
      "axis": "value",
      "scale": { "min": 0, "max": 30, "majorUnit": 5, "minorUnit": 1 }
    }
  ]
}
```

`axes[].axis` 是严格 enum，只收 canonical 全名：`category` / `value` / `x` / `y`
（直角坐标图用 category/value；scatter / bubble 用 x/y）。`scale` 还支持
`reverseOrder` / `crosses`（`auto / custom / max / min`）/ `crossesAt`，以及
`logBase`（2..1000，仅 value 轴，对数刻度）和 `crossBetween`
（`between / mid-category`，仅 value 轴）。

不要把 patch 选轴与 parser 的 crossing 字段位置混为一谈：`min/max/reverseOrder`
作用于所选轴本身，`crosses/crossesAt` 则沿 `crossAx` 写到对轴声明。当前普通 3D
图中，要把分类交叉平面置于数值 25，使用 `axis:"value"`、
`scale:{"crosses":"custom","crossesAt":25}`（写到 `c:catAx`）；误用
`axis:"category"` 会写入 `c:valAx`，dry-run 仍可能成功，却没有改变目标平面。
需要精确交点时核对实际 chart part 的 `crossAx` 配对、`crossesAt` 所属轴，再检查
当前渲染；inspect 的外框/相机回读不能证明交点正确。不要根据显示截图猜轴或重写数据。

日期轴时间单位（仅当 deck 里已有 `c:dateAx` 时可用；它可以来自 PowerPoint，或由
上面的 `add-chart.categoryAxis.type=date` 创建）：`scale` 支持
`baseTimeUnit` / `majorTimeUnit` / `minorTimeUnit`
（`days / months / years`，`null` 恢复自动），用 `axis: "category"` 定位日期轴；
`majorUnit`/`minorUnit` 此时是"每 N 个时间单位"的计数（如 `majorUnit: 2` +
`majorTimeUnit: "months"` = 每 2 个月一个主刻度）。典型场景：日粒度数据的
X 轴标签挤成一团 → 设 `majorTimeUnit: "months"`。普通 `c:catAx` 对这些时间单位
仍会 fail closed（含 `null` 清除）；需要日期语义时必须在创建阶段显式选择日期轴，
不能用 `set-chart` 猜测或转换既有分类轴。

轴条目还支持（xdoc ≥0.3.1，方案 7 长尾补齐）：

```json
{ "op": "set-chart", "slide": 1, "shape": {...},
  "axes": [
    { "axis": "value",
      "title": { "text": "USD (thousands)", "font": { "bold": true }, "rotation": -90 },
      "displayUnits": { "unit": "thousands", "showLabel": true } },
    { "axis": "category", "title": null }
  ] }
```

- `title`：轴标题。`text` / `font` / `rotation`（-90..90 度）；`null` 删除轴标题。
- `displayUnits`：仅 value 轴。`unit` 取内置档位
  `hundreds / thousands / ten-thousands / hundred-thousands / millions /
ten-millions / hundred-millions / billions / trillions`，或直接给正数作自定义
  除数（写 `c:custUnit`）；`showLabel: true` 同时显示单位标签；`null` 移除。
  金额类轴强烈建议用它代替手改数据（"以千为单位"的正确语义表达）。

> ⚠️ `cat` / `val` / `categoryAxis` / `valueAxis` / `valueX` / `xAxis` 之类的旧简写，
> 以及 `ser`、`secondaryVal`、`date`，**都不在** enum 内。axis 定位当前只能针对
> **主轴**；combo 图的次坐标轴(通过 `data.series[i].secondaryAxis: true` 创建,
> 见 §数据结构 → Combo)暂不能用 `set-chart` 的 `axes` 条目单独设样式 — 需要时
> 只能用 `patch-ooxml`(`--allow-raw-xml`)直改第二个 `c:valAx` 节点（OOXML 没有
> `c:secondaryValAx` 元素，次坐标轴就是 chart part 里另一个 axId 的 `c:valAx`）。

### 改轴线 / 网格线 / 刻度标签

```json
{ "op": "set-chart", "slide": 1, "shape": {...},
  "axes": [{ "axis": "value", "line": { "width": "0.75pt", "color": "BFBFBF" } }] }

{ "op": "set-chart", "slide": 1, "shape": {...},
  "axes": [{ "axis": "value", "gridlines": { "width": "0.5pt", "color": "EEEEEE" },
             "minorGridlines": { "width": "0.25pt", "color": "F5F5F5" } }] }

{ "op": "set-chart", "slide": 1, "shape": {...},
  "axes": [{ "axis": "value", "gridlines": null }] }

{ "op": "set-chart", "slide": 1, "shape": {...},
  "axes": [{ "axis": "value",
             "ticks": { "major": "outside", "minor": "none",
                        "labelPosition": "next-to-axis", "numberFormat": "0.0%" } }] }

{ "op": "set-chart", "slide": 1, "shape": {...},
  "axes": [{ "axis": "category",
             "ticks": { "rotation": -45, "labelSkip": 2, "font": { "size": "9pt" } } }] }
```

`ticks.major` / `ticks.minor` 取值：`cross / inside / none / outside`（**不接受**
`out` / `in` 等简写）。`ticks.labelPosition` 取值：`high / low / next-to-axis / none`。
`gridlines` / `minorGridlines` 都接受 `null` 表示删除该组网格线。

`ticks` 还支持刻度标签排版（拥挤类目轴的首选修复手段，优先于缩字号）：

- `rotation`：-90..90 度，写入轴 `txPr` 的 bodyPr rot（**PNG 预览可见**）；
- `font`：刻度标签字体（同通用 font 对象）；
- `labelSkip` / `markSkip`：每 N 个类目显示一个标签 / 刻度线（≥1，仅类目轴）；
- `labelOffset`：0..1000，标签与轴的距离百分比（100 = 默认，仅类目轴）；
- `labelAlignment`：`center / left / right`（仅类目轴）。

> ⚠️ **刻度线默认是画出来的（xdoc ≥0.3.4）**：`c:majorTickMark` /
> `c:minorTickMark` 元素**缺失**时按 OOXML 默认值 `cross` 渲染 —— 轴线两侧
> 各伸出一小段，PowerPoint 也是这样。`add-chart` 不写这两个元素，所以**新建
> 图表默认两条轴都带 cross 刻度线**。要走极简风格（多数咨询版式的做法），必须
> 显式关掉：
>
> ```json
> { "op": "set-chart", "slide": 1, "shape": {...},
>   "axes": [{ "axis": "category", "ticks": { "major": "none", "minor": "none" } },
>            { "axis": "value",    "ticks": { "major": "none", "minor": "none" } }] }
> ```
>
> 另外三条相关事实，做视觉复核时会用到：
>
> - 刻度线用**轴线本身**的颜色与线宽；把轴线设成无线条（`line` 删除/无填充）
>   会连刻度线一起去掉，这与 PowerPoint 一致。
> - 长度按**轴标签字号**成比例（major ≈ 0.32 字号，minor ≈ 0.24 字号），
>   所以缩小刻度标签字号也会让刻度线变短；不存在单独调长度的开关。
> - 类目轴的 major 落在**类目带边界**（N 个类目 = N+1 条），minor 落在中点；
>   数值轴 major 落在主刻度、minor 落在次刻度。雷达图与饼图不画刻度线。

### 改某系列样式

```json
{
  "op": "set-chart",
  "slide": 1,
  "shape": {...},
  "series": [
    {
      "series": 0,
      "fill": { "type": "solid", "color": "1A73E8" },
      "line": { "width": "2pt", "color": "1A73E8" },
      "marker": { "symbol": "circle", "size": 6, "fill": "FFFFFF" },
      "smooth": false,
      "invertIfNegative": true
    }
  ]
}
```

`series` 是 0-based 索引；同一个 `series` 数组里可以给不同系列各写一条（同一系列
重复出现且字段冲突会被拒绝）。

> ⚠️ marker 用 `symbol`（不是 `kind`）：严格 enum，只收
> `auto / circle / dash / diamond / dot / none / picture / plus / square / star /
triangle / x`（其它值直接被 schema 拒绝）。marker 的 `fill` /
> `line` 取颜色字符串（如 `"FFFFFF"`），不是对象。

### 趋势线 / 误差线（系列级分析装饰）

```json
{ "op": "set-chart", "slide": 1, "shape": {...},
  "series": [
    { "series": 0,
      "trendlines": [
        { "type": "linear", "forward": 2,
          "displayEquation": true, "displayRSquared": true,
          "label": {
            "numberFormat": "0.0000",
            "font": { "name": "Aptos", "size": "9pt", "bold": false,
                      "color": "336699" },
            "rotation": -15
          } },
        { "type": "moving-average", "period": 3 }
      ] },
    { "series": 1,
      "errorBars": { "valueType": "percentage", "value": 5 } }
  ] }
```

- 使用 `trendlines` 数组按顺序**完整替换**同一系列的趋势线集合；数组顺序是
  唯一稳定 identity，不要假设可按 index 增删。`trendlines: []` 清空全部趋势线，
  省略字段保持原集合。单数 `trendline` 和 `trendlines: null` 均被拒绝。
- 每条趋势线的 `type`：`exponential / linear / logarithmic / moving-average /
polynomial / power`；`order`（2..6）仅 polynomial，`period`（2..255）仅
  moving-average，`intercept` 仅 exponential/linear/polynomial（组合错会被
  dry-run 拒绝并说明）；还支持 `forward` / `backward`（外推期数）、`name`、
  `line`（线样式）。pie/doughnut/radar 等不支持趋势线的 series 会拒绝非空集合，
  但仍允许清空。
- `label` 只负责 PowerPoint 自动生成的方程/R² 标签格式，首版安全字段为
  `numberFormat`、`font.name/size/bold/color` 和 `rotation`（-90..90）。只要提供
  `label`，同一趋势线必须显式设置 `displayEquation: true` 或
  `displayRSquared: true`；`label: null` 表示不写格式容器。当前不承诺自定义
  `<c:tx>` 文本或 manual layout，不能用 `label` 替换 PowerPoint 生成的公式内容。
- `label.font.size` 对齐 DrawingML `a:defRPr/@sz` 的 100..400000 centipoint
  边界，只接受带显式 `pt` 后缀的 1pt..4000pt 字符串，小数最多 4 位。其他
  单位、数字裸值和越界值会 fail-closed。
- `errorBars.valueType`：`fixed / percentage / std-dev`（需配 `value`）、
  `std-err`（不带 value）、`custom`（需 `plus` + `minus` 两个数值数组，长度=
  点数）；可选 `type`（`both / minus / plus`，默认 both）、`direction`
  （`x / y`，scatter/bubble 用）、`noEndCap`、`line`。`errorBars: null` 删除。

趋势线集合与标签属于高风险 chart XML 改动：先 dry-run 确认 selector、changedParts、
semantic/structure gate，再 apply；随后用 inspect/parse 回读确认趋势线数量、顺序、类型、
方程/R² 开关和 label 格式，最后执行 ZIP/XML 校验、预览复核，并在可用时跑 PowerPoint
clean-open。只看到 patch 成功不足以证明数组顺序和 `bold: false` 等显式值被保留。

> ✅ **当前预览支持（xdoc ≥0.3.1）**：PNG/PDF 预览链会渲染
> `trendlines` / `errorBars` / `dataTable` /
> `displayUnits` / 轴标题 /
> `minorGridlines`，包括趋势线方程与 R²、单位标签以及图下数据表布局。
> 刻度标签 `rotation` 也可见。若 capability probe 显示当前 runtime 不支持某项，
> 再按 [故障排查](../runtime/troubleshooting.md) 中的 XML/Office fallback 复核；不要把旧
> runtime 的能力差异误判为写出失败。

### 数据标签

```json
{
  "op": "set-chart",
  "slide": 1,
  "shape": {...},
  "dataLabels": [
    {
      "scope": { "series": 0 },
      "showValue": true,
      "showPercentage": false,
      "showCategoryName": false,
      "showSeriesName": false,
      "position": "outside-end",
      "numberFormat": "#,##0"
    }
  ]
}
```

`scope` 是 **对象**（不是字符串）：

- 省略 `scope` → plot 0（组合图不等于全部 plot）
- `{ "series": 0 }` → 第 0 个系列
- `{ "series": 0, "point": 2 }` → 第 0 系列的第 2 个点
- 想同时给 plot 显式指定：`{ "plot": 0 }`

`position` 必须用全名（**shorthand 不接受**）：
`above / below / best-fit / center / inside-base / inside-end / left / outside-end / right`。

这些值不是所有 chart kind 的通用可写集合。`area` / `area-3d` / `doughnut` 在 plot、series、point
范围均拒绝显式 `position`，包括 `center`；省略以保留默认/导入位置，其他标签字段
仍按 scope 校验。组合图按实际所属 plot 判断，不能按系列输入顺序猜 plot index。
库层的 clear 能力不代表 patch 接受 `position:null`；必须以当前字段 schema 为准。
新建 doughnut 使用默认 Center 放置，不应为了居中而写 `position: "center"`。
若旧文件含显式位置且需要清理，先查询当前 patch schema；不要反复换位置枚举重试，
也不要把错误回退成 raw XML 写入。只改字号、格式或可见性时省略位置字段即可。

> ⚠️ 老版本里见过的 `"all"` / `"ctr"` / `"l"` / `"r"` / `"t"` / `"b"` / `"inBase"` /
> `"inEnd"` / `"outEnd"` 全部被 schema 拒绝。

`dataLabels[]` 还支持 `separator`（多字段标签的分隔符字符串，如 `"; "`）与
`font`（标签字体对象）；`separator` 与 `show*` / `numberFormat` 仅 plot / series 作用域，
point 作用域目前只收 `position` 和 `font`（带 `showValue` 等会报
`point data labels currently support position and font only`）。

### Plot 区域（gap / overlap / vary）

```json
{
  "op": "set-chart",
  "slide": 1,
  "shape": {...},
  "plot": {
    "gapWidth": 150,
    "overlap": -10,
    "varyByCategories": true,
    "bubbleScale": 100
  }
}
```

- `index` 多 plot 图表用来选 plot（非负整数，默认 0）
- `gapWidth` 0-500（柱间距百分比）
- `overlap` -100 to 100（柱重叠）
- `varyByCategories` 单系列时每类目不同颜色
- `bubbleScale` bubble 缩放
- `firstSliceAngle` 0-360（pie / doughnut 首片起始角，**预览可见**）
- `holeSize` 1-90（仅 doughnut 环孔大小百分比，**预览可见**；数值越小环越粗）。
  新建 `standard` / `exploded` doughnut 会显式写入一个 `c:holeSize val="50"`；
  50 是 xdoc 的创建默认值，不是 Office 强制的数值。需要其他孔径时通过
  `set-chart.plot.holeSize` 覆盖；编辑时省略保留既有值，不能假定默认值会修复导入图表。
  这里的保留指 `set-chart` 局部编辑。经典 `set-chart-data` 会重建 chart XML/workbook，
  实测 doughnut 的既有 62 会重置为 50，标题/标签样式等也不能假定保留。
  换数据前记录所需声明，在重建之后重新应用孔径及所需样式，回读最终 chart 部件并复核 PNG；
  仅改标题/系列名/category 文本时优先用前述安全文本编辑路线。
- `sizeRepresents` `area / width`（仅 bubble：气泡大小映射面积还是直径）

### 图表级选项（displayBlanksAs / roundedCorners / dataTable）

```json
{ "op": "set-chart", "slide": 1, "shape": {...},
  "displayBlanksAs": "span",
  "roundedCorners": false,
  "dataTable": { "showHorizontalBorder": true, "showVerticalBorder": true,
                 "showOutline": true, "showKeys": true } }
```

- `displayBlanksAs`：`gap / span / zero` — 折线图有缺失数据时的语义选择
  （`span` 连线跨过空值，`zero` 按 0 画；创建时默认 `gap`）。
- `roundedCorners`：图表外框圆角开关。
- `dataTable`：图下数据表（四个 show* 开关至少给一个；`null` 移除整个数据表）。
  xdoc ≥0.3.1 的 PNG/PDF 预览会显示数据表布局。

### 单点样式

```json
{
  "op": "set-chart",
  "slide": 1,
  "shape": {...},
  "series": [
    {
      "series": 0,
      "points": [
        {
          "point": 2,
          "fill": { "type": "solid", "color": "EA4335" },
          "marker": { "symbol": "diamond", "size": 10 }
        }
      ]
    }
  ]
}
```

适合"高亮某个数据点"。

### 只改 marker（标记符号）

```json
{
  "op": "set-chart",
  "slide": 1,
  "shape": {...},
  "series": [
    {
      "series": 0,
      "marker": { "symbol": "square", "size": 6, "fill": "FFFFFF", "line": "1A73E8" }
    }
  ]
}
```

## 完整示例：营收图

```json
{
  "schemaVersion": "pptx-patch/v1",
  "ops": [
    { "op": "add-slide" },
    {
      "op": "add-text-box",
      "slide": 0,
      "name": "Title",
      "x": "1in",
      "y": "0.5in",
      "w": "11in",
      "h": "0.8in",
      "text": "营收分析"
    },
    {
      "op": "add-chart",
      "slide": 0,
      "kind": "column",
      "variant": "clustered",
      "x": "1in",
      "y": "2in",
      "w": "11in",
      "h": "4.5in",
      "name": "Revenue",
      "title": "季度营收（万元）",
      "legend": "bottom",
      "data": {
        "categories": ["Q1", "Q2", "Q3", "Q4"],
        "series": [
          { "name": "2025", "values": [1000, 1200, 1400, 1600] },
          { "name": "2026", "values": [1500, 1800, 2100, 2400] }
        ]
      }
    },
    {
      "op": "set-chart",
      "slide": 0,
      "shape": { "name": "Revenue" },
      "style": 6,
      "dataLabels": [{ "showValue": true, "position": "outside-end", "numberFormat": "#,##0" }]
    }
  ]
}
```

> ⚠️ 上例 `dataLabels` 条目省略了 `scope` —— 这等价于 plot 0（覆盖所有系列）。要只标
> 某一个系列，加 `"scope": { "series": 1 }`。

## 升级后图表渲染变化的诊断

先用当前 xdoc 对同一源文件重渲染，不为恢复旧像素改数据或固定自动轴：

- 折线自动 domain 包含实际绘制的误差棒端点；累计/统计误差须按系列语义解释，显式
  min/max 仍优先。不要缩减误差值或截断轴来掩盖旧 domain 的问题。
- 柱/条形的 overlap 与 stacking 是独立因素；类目轴方向还影响 horizontal bar 的系列
  槽位和 legend 身份。检查 category/series 索引、正负累计与顺序，不靠交换数据数组修预览。
- Bubble 自动轴使用有效 x/y/正 size 点及 bubbleScale 对应留白，窄的同号范围可不含零。
  显式范围和 major unit 仍优先，且可裁切气泡；轴留白不等于气泡直径。散点 spline、精确
  bubble 直径或 plot layout 仍须独立证据，不从本次自动轴改进推导保真。
- 3D horizontal bar 同时检查 `barDir`、类目/数值反转、投影 geometry、刻度、gridline 与
  depth 标题；轴与柱体不能分别转向。保留 view3D 与真实数据，勿改成竖柱或 2D 补偿。
- 字体取证应包含实际可见 title、axis/depth title、display-unit label、legend 与 data label，
  包括 combo 分组和 point override；隐藏或已删除的 label 不该强迫修改作者字体。

这些是 Web/PDF 诊断边界，不扩大 chart authoring 或 Office playback 支持。按
`../review/fidelity-diagnosis.md` 记录消费者与字体；静态预览不能证明 Office 逐帧/逐像素一致。

## 时间序列 / 预测的视觉陷阱

按时间序列画 column / bar 时，如果只填了上半年实际数据、下半年用 `0` 占位，
渲染出来就像业务突然崩盘。处理方式：

1. **补预测值**：把 Q3 / Q4 用估算值填上，类目轴标注 `"Q3 (预测)"` / `"Q4 (预测)"`
2. **改用部分类目**：只展示已有数据的 `Q1 / Q2`，下半年单独做 callout
3. **添加 highlight 区**：用 `set-chart` 的 `series[].points` 把预测点改成虚线/不同色

不要把"暂无数据"和"业务断崖"留给观众自己分辨。

## Unsupported 时怎么办

下列 Office `XlChartType` / 高级特性当前 xdoc 标为 unsupported 或 partial（完整状态表见
`xdoc schema` 的 `commands.pptx.catalogs.xlChartTypeMap.entries[]`）：

- 3D series-axis，以及日期轴的高级手工 layout/多轴变体（显式单 category
  `c:dateAx` 创建和时间单位已支持）
- volume stock（`xlStockVHLC` / `xlStockVOHLC`，partial：回退为不带 volume 的 HLC/OHLC）
- 经典图表的 chartEx 新式变体（`xlAreaEx` / `xlBarClusteredEx` / `xlColumnClusteredEx` /
  `xlLineEx` / `xlPieEx` / `xlDoughnutEx` / `xlXYScatterEx` / `xlBubbleEx` 等，unsupported）
- cone / cylinder / pyramid 3D 柱形、pie-of-pie / bar-of-pie、filled radar / radar markers、
  `xlLineMarkersStacked`（partial：回退为普通 3D 柱 / pie / radar / stacked line）
- `pareto` 与 `region-map` 本身是 supported，走普通 `data` 输入，见上文

遇到时：

1. 告诉用户 "这种图表 xdoc 当前不支持，可以用..." 给出替代方案
2. 备选方案：
   - volume stock → 拆成 stock + bar 两张图
   - 高级 secondary-axis 之外的多轴 → 用 `combo` 的 `secondaryAxis` 加单轴方案
3. 不要假装做了 — 一定要让用户知道

## 不要做的事

- ❌ 不要把 `categories` 当成 `series`（categories 是 X 轴标签，series 才是数据线）
- ❌ scatter / bubble 用了 `categories + values` 会失败 — 用 `points: [{x,y}]`
- ❌ stock 的 high/low/close 数组长度必须等于 categories
- ❌ 不要假定 chart 内部坐标系跟 slide 一样 — `set-chart` 的 `axes[].scale` 是 chart-local

## ChartEx creation and verification notes

For PowerPoint-only chart types such as `waterfall`, `sunburst`, `treemap`,
`histogram`, `box-whisker`, and `funnel`, do not assume that a successful
`xdoc pptx apply --dry-run` means the object will render in PowerPoint.

- Use the ChartEx-specific `dataEx` payload shape. Do not pass the ordinary
  chart `data.categories` / `data.series` shape for these kinds unless the
  current xdoc schema explicitly documents that mapping.
- `add-chart.title` is ChartEx-aware: non-empty text writes native `cx:title`,
  blank text omits the container, and `set-chart-data.dataEx` preserves it.
  Never write classic `<c:title>` into `chartEx*.xml`. Explicit
  `add-chart.legend` control remains unsupported and is rejected instead of
  ignored; use the default ChartEx legend semantics or separate editable
  labels when a custom legend is required.
- `xdoc convert` is not sufficient evidence for ChartEx rendering. Always
  use a non-interactive PowerPoint baseline render when the optional macOS +
  scriptable PowerPoint + Nushell + xdoc PDFium evidence route is available:
  `nu <skill-root>/scripts/cli/office/powerpoint-snapshot.nu deck.pptx --slides N-M --out <run-dir>/powerpoint/slide-%d.png --method pdf-render --json > <run-dir>/powerpoint-native-render.json`.
  Then run the high-risk finalizer with `--candidate deck.pptx
--powerpoint-native-render <run-dir>/powerpoint-native-render.json`. It reads
  the final ZIP, identifies ChartEx by OPC Content Type, and maps relationships
  through slide/layout/master ownership to one-based presentation order. Renamed
  parts and inherited charts are included; a filename alone is not chart identity.
  It requires candidate/hash/image-bound coverage for all mapped slides and keeps
  unreferenced ChartEx parts unresolved rather than guessing a slide.
  PDF exports can omit hidden slides: retain `pdf_page_count` and `pdf_pages` from
  the snapshot report. The helper maps logical slides to physical PDF pages and
  rejects an omitted requested slide or an unexplained page count. Do not label a
  different PDF page as the requested slide; keep the failure and choose a disclosed
  alternative if native proof is required.
  When the complete optional route is available, absence or staleness is a hard
  failure. When any prerequisite is unavailable, the baseline workflow remains
  usable but the result is an explicit unverified warning rather than a pass;
  stop if the user or delivery policy explicitly requires PowerPoint-native proof.
  Treat user phrases such as "PowerPoint 截图" or "用 PowerPoint 显示效果对比" as
  PowerPoint render verification, not as permission to use window-mode screenshots.
  Use `--method window` only if `pdf-render` fails; keep the failed pdf-render
  report and record the fallback reason. Window mode now fails closed unless
  the frontmost process, staged presentation path/name, window title, current
  slide, canvas rectangle, and PNG/Retina scale remain consistent before and
  after capture. It is still a fallback and does not satisfy the ChartEx
  `pdf-render` gate. Scope it to the minimum suspect slides.
- If PowerPoint displays `This chart isn't available in your version.`, the
  candidate is not shippable as a ChartEx object even if the OOXML is
  well-formed and xdoc inspect succeeds.
- When a deadline requires a PowerPoint-renderable deliverable before ChartEx
  OOXML support is fixed, use native editable shapes/text to recreate the
  visual chart and document that it is not a native chart object.
