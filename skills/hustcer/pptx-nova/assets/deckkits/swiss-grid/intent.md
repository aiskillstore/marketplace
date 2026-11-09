# Swiss Grid 2.0

白纸、黑字、克制的红色与无衬线字体构成身份；对齐和留白建立阅读顺序。
网格首先是组织信息的工具。封面与收束不显示灰色施工网格；仅在解释网格本身的示意页使用可见结构。
采用非对称构图、齐左不齐右、开放名录、功能性细线和明确的大小字对比，避免圆角卡片、阴影、渐变与装饰性图标。

## 来源与裁决

以 `67-swiss-grid-systems.pptx` 的十四页第一手视觉素材为主，保留全部页面职责；
原有套件补入的评分表是第十五类职责。原稿图标、字体样张字重和列末注释均纳入检查。
不要求像素一致：放大原稿的小字、重排密集正文、移走压线的标注，并撤去封面/收束的灰色网格。
这些取舍让秩序来自文字与空间关系，保留原稿的编辑语气。

博物馆资料作为设计背景：[Poster House 的 The Swiss Grid](https://swissgrid.posterhouse.org/)
展示网格的灵活应用；[MoMA 的 Helvetica 展览](https://www.moma.org/calendar/exhibitions/38)
讨论字体的中性和比例。套件的具体规则是对本次资料与用户目标的设计裁决。

## 内容与构图

十五个页型保留 `swiss*Slide` 名称；所有页面经 `swiss-typographic/v1` 注册族解析。
使用 `layoutId: auto` 或发现输出中的显式布局，不在 content 中写页面坐标。
标题、引文、人物、年份、示例、单位和来源都由 content 提供。完整稿使用
`meta.designScope: complete`，须以 cover 开始并以 closing 结束；片段用 `excerpt`。
容量不足时切换合法构图、重组内容或拆页；解析失败会给出页/字段诊断，不删字段或无限缩字。

身份和容量的机器事实以 design.json 为准；本文件解释用途，不构成第二份数值合同。
常规内容页共享标题/副题/短红线；引文、宣言和封面承担停顿。不要连续使用密集名录。

## 原生对象和同步边界

- 文字、标记、四种网格图、计量示意为原生文字/形状；示意标签由形状自身持有并双向居中。
- 表格为原生表格，逐格保留；`columns[].weight` 是相对列宽，`rows` 是与列数一致的字符串数组。
  `rowTones` 可将指定行强调为红色；业务阈值和状态判断由 content 决定。
- 系统页的 baseUnit、columnUnits、gapUnits、rowUnits 和列/行数量共同推导几何与数值标注。
  单位来自 content；显示最多四位小数。手工编辑一个标注或形状不会同步其余对象，须重新生成。
- 品牌/实体图标来自离线 Tabler 包，SVG 保持矢量图片；它们不等于可逐节点编辑的原生形状。
  示例以 Apple/Google/Spotify/Airbnb 图标及 building/plane 语义替代原始商标，不分发原稿图片。
- 不提供照片/截图槽位、图表、源稿动画保留或任意业务内容自动换肤保证。

## 字体

Helvetica 与 Arial Black 是已安装的相近替代；中文采用正体 Arial Unicode MS，粗体显式指定。
字体样张的 `specimenStyle: heavy | bold | regular` 决定实际字重；名称和说明保持 content 原文。
这不是 Akzidenz-Grotesk / Univers 原字体的精确标本。字体不打包、不嵌入，其他平台须重新检查替代、换行和字重。

## 从 0.1 迁移

- `accent: <hex>` 改为 `focus: true`；颜色职责由合同控制。
- 旧 cover `footer` 可作为独立附注继续显示；页码始终由位置/总页数生成。
- 内页 eyebrow 是真实内容并完整显示，不再按 `P · NN` 静默抑制。
- 字体卡片增加 `specimenStyle`、`lead`；根 sampleText 可被每张卡片的 sampleText 覆盖。
- column 条目支持独立 `note`，不再丢失原稿列末注释。
- system 的独立 baseValue、measureLabels、body 改为 `model + labels`；不得把旧展示字符串猜作数值。
  示例将旧 264 的不一致列宽修正为由 16×16 得到的 256，间距仍由 2×16 得到 32。
- table 的记录/状态对象改为 `rows[][]` 字符串，column key/kind 删除，width 改为相对 weight。
  旧状态 label 迁入单元格，业务强调单独放入 rowTones；不内置红黄绿评分政策。
- closing 不再接受 `dots` 页面坐标；点阵由注册布局产生。statement 使用 title，不再接受 statement 别名。
- 多行输入统一为字符串中的换行，旧数组文本须先合并；未知字段、未知布局和超容量输入明确失败。

旧固定渲染器不作为 fallback 分发。翻新配置保持独立审查路线，不从新建样例推导源稿无损能力。

## 验证状态

2.0.0 于 2026-10-24 经维护者明确授权晋级，在当时登记为唯一的 default；当前 readiness
以 [catalog](../catalog.json) 为准，现登记为 production。迁移验收时，最终源码对应的
57 页 canonical 已逐张检查，五组文件均通过 PowerPoint
for Mac 16.114 原生打开、保存、关闭重开及对象回读；标题、形状内文字和表格单元格实际编辑也已回读。
本次晋级重跑三项 live benchmark，并通过 default readiness；原生宿主证据沿用迁移验收的范围。
机器、视觉、原生宿主的范围和未验证项见
迁移报告（未随本仓库发布：`swiss-grid-v2-migration-results.md`）。新生成的每份 PPTX 仍须完成其交付检查。
