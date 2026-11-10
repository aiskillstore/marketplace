# Paper Scholar

Paper Scholar 把暖纸底、橄榄绿层级、珊瑚标记、开放式证据和研究课件节奏组织成标准 DeckKit。
通过 `content.json → validate-content → build → Create` 使用，无须手写坐标。
版本与 readiness 以 [catalog](../catalog.json) 为准；当前为 default，可参与自动交付选择。

## 身份、构图与内容

身份不变量包括封面拱形等高线与平滑研究路径、短珊瑚下划线、居中的编号圆点、细箭头、
十点比例示意、珊瑚原生柱图、浅绿机制图、带圆形标识的分组表、粉色案例标题带和功能性行动条。
数字、来源、日期、结论、行配色含义、行动理由与复核条件均来自 content。
等高线是封面身份图案，不表达未经提供的地理或研究数据。

| 页型                    | 职责                                   | 合法构图                  |
| ----------------------- | -------------------------------------- | ------------------------- |
| `scholarCoverSlide`     | 观点、研究范围、元数据与等高线         | `contour`、`inset`        |
| `scholarMethodsSlide`   | 方法步骤与多来源交叉核对               | `horizontal`、`vertical`  |
| `scholarFindingSlide`   | 百分比、比较组、数值派生差异与十点示意 | `leadLeft`、`leadRight`   |
| `scholarChartSlide`     | 单系列原生柱图与两段解释               | `plotLeft`、`plotRight`   |
| `scholarMechanismSlide` | 两条半衰期曲线、公式、参数与刻度       | `center`、`plotLeft`      |
| `scholarSegmentsSlide`  | 原生分组表、汇总、口径和结论           | `full`、`rail`            |
| `scholarCaseSlide`      | 三段案例、图片外壳与前后对比           | `portrait`、`resultFirst` |
| `scholarClosingSlide`   | 行动、依据、执行方式与下一次复核       | `bands`、`ledger`         |

`auto` 按实际容量与近期构图确定性选择；显式 layoutId 同样须满足容量。
完整 deck 以封面开始、行动页结束；片段用 `meta.designScope: "excerpt"`。
重复构图超过合同节奏会失败。没有合法构图时重组或拆页，不静默删除字段、不缩字。

## 容量与数据语义

方法支持 2–4 步、2–3 类来源；图表支持 2–5 个有限数值，保留负数、零和极小数。
表格支持 3–5 列、2–5 行；`rows[].cells` 必须比 headers 少一格，首格由 `label` 提供。
`emphasisColumn` 为从 1 开始的值列索引；不得指向不存在的列。
`tone` 显式选择 `pale` 或 `blush`，不自动推断优劣。
`icon` 只接受 schema 注册的语义 Tabler 名称，须与内容相符。

百分比发现页与案例页使用 0–100 的原始百分数和 `%` 单位。
发现页差异与十个圆的扇区从 metric/comparator 数值计算；0 没有填充，100 全填充。
机制页明确选择半衰期模型 `R(t) = 2^(-t/h)`，不是任意曲线编辑器。
两组 halfLife 必须为正；2–4 个刻度须严格递增且处于 `[0, maxTime]` 内。
平滑曲线不因复核刻度自动跳变；模型选择、参数和解释由内容作者负责。
行动页支持 2–3 项、2–4 个复核字段。所有独立可见字符串拒绝纯空白。
发现页、柱图、机制和案例分别具有不同 schema，不能互换字段。

## 原生编辑与同步边界

文字、形状、曲线、表格和柱图均为原生对象。图表保留全部类别、系列名称和原始数值；
表格保留每格文字。图表显示格式与源数值分别处理，极小量不添加虚假的最小柱高。
小柱触发整组柱外标签，避免当前 runtime 的逐点覆盖继承差异；不足一单位的数值范围增加
轴域留白。派生轴域无法用有限数表示时拒绝生成，要求调整计量单位，绝不改原始数值。
手工编辑数据后，独立单位说明、差异文字、扇区、模型曲线、图例及表格图标不会自动同步；
须从 content 重新生成。原生数据回读不证明全部 OOXML 样式或跨宿主像素一致。

案例图片为带交叉线和可编辑说明的 shape 外壳，不接受实际图片输入。
参考照片、品牌和原始业务事实均不分发。Tabler 图标为内联 SVG 图片，尺寸可编辑，
不承诺其路径节点具有 PowerPoint 原生形状编辑能力。
本套件不注册现有 PPTX 翻新、动画、任意图片输入或无损保留能力。

## 字体与设计裁决

使用正体 Arial / Arial Unicode MS 的常规与粗体，替代未安装的 Liter / MiSans；不嵌入字体。
默认画布为 16:9。原图的绿／珊瑚身份优先于冲突的蓝／黄文字规范；末尾禁通用卡片规则
用于开放版面，原图行动条仍保留功能性分组与圆角。加深小字和编号，提高对比；
表格去掉竖线、保留墨绿标签、浅绿／粉色证据与重点值。公式修正为与半衰期一致的数学语义。
英文大小写和中英换行保留作者意图，不自动改写专名。

样例均为明确标识的合成数据；[完整示例](examples/content.json)、
[同内容替代构图](examples/alternate-content.json)、[混排水务主题](examples/water-content.json)
展示字段填写。机器、实际逐页视觉和 PowerPoint 宿主结果记录在
[golden 审查](../../../benchmarks/visual/cases/paper-scholar/golden-learning/review.md)。
