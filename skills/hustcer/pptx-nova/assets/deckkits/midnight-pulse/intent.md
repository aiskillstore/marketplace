# Midnight Pulse

深夜运营指挥室式的证据报告：近黑蓝底、青蓝仪表、冰蓝数字、琥珀异常，以及交叠并裁切到画布边缘的深海军蓝／深青薄雾。**背景叠层是身份必需项**，不能为追求通用极简而删除。只有注册的背景薄雾可使用渐变，图表、表格与其他形状保持平面表达。

通过标准 `content.json → validate-content → build → create runner` 使用。本套件为 production，可参与自动交付选择。发现字段、可用布局和容量时运行 `<skill-root>/scripts/cli/deckkits/design.mjs --deckkit midnight-pulse` 与 slots 命令。数值事实以同目录 design.json 和投影 schema 为准。

## 页面职责与构图

| 页型                  | 职责                                       | 合法构图                     |
| --------------------- | ------------------------------------------ | ---------------------------- |
| pulseCoverSlide       | 观点、三项实际／目标／达成率、封面图片槽位 | widePhoto / photoRail        |
| pulseOverviewSlide    | 判断与达成仪表                             | gaugeRail / gaugeBand        |
| pulseAuditSlide       | 无竖线衬线诊断表及追溯                     | auditWide / auditRail        |
| pulseTrendSlide       | 单系列趋势、阶段边界与编号事件             | trendRail / trendBand        |
| pulseAttributionSlide | 分组差异归因和双环汇聚                     | targetRight / targetLeft     |
| pulseComparisonSlide  | 相同口径的开放式比较                       | compareColumns / compareRows |
| pulseStatusSlide      | 状态、进度、证据、阻塞、纠正及责任期限     | statusRows / statusColumns   |
| pulseCloseSlide       | 路线、门槛与需批准的事项                   | routeTop / routeLeft         |

`auto` 根据实际内容容量及最近构图确定性选择；显式 layoutId 也必须通过容量检查。完整 deck 以观点封面开始、路线决策结束，节选使用 `meta.designScope: "excerpt"`。不接受手写坐标或 customOps。过量或过长内容须换合法构图、重组或拆页，不能静默删除或缩字。

## 内容与颜色职责

所有业务标题、判断、来源、日期、单位、目标、状态文字、门槛及责任信息均来自 content。`emphasis` 是标题中需要加粗的实际子串，不根据领域词汇自动猜测。输入大小写原样保留。

青蓝是数据与进度；冰蓝是数字、刻度和结构；琥珀用于未达标与延迟后果。绿色与珊瑚红只进入项目状态圆点及对应状态文字。达成率由 `direction` 决定为实际／目标或目标／实际；无定义的除法明确失败。显示数值不被修改，环的图形在满环处饱和。各因素必须合计为实际减目标；汇聚射线不编码比例。

## 原生对象与编辑同步边界

趋势柱图、仪表环图及诊断表为原生对象。文字、进度、刻度、编号、汇聚线、空心路线节点和决策轮廓均可编辑。背景是经过画布裁切的原生 freeform 椭圆轮廓与限定渐变，不是全页图片；节点路径可编辑，但不承诺保留 PowerPoint 的椭圆预设类型。

生成时的图表 cache、嵌入工作表与输入同源。本次 macOS PowerPoint 原生探针中，Excel 内嵌工作表改值并保存成功，但图表 cache 与重新导出的画面仍为旧值，因此不承诺宿主手工数据编辑的自动同步。独立文字、目标、达成环、事件标记、阶段线、进度条及表格顶线也不随手工数据或几何编辑自动更新；须修改 content 并重新生成以保持同步。柱图使用共同线性轴，极小观测可能低于可辨像素；零值不伪造最小柱高。JSON/原生回读不代表完整 Office 像素等价。

封面的 `cover.photo` 是可选的内容资产，通过 `--assets assets_manifest.json` 注入，支持共享的 cover/contain 裁切。未绑定时保留明确标识的可编辑外壳；正文禁止图片。照片、来源和 caption 不能回退到参考素材。示例照片为独立生成的虚构场景，业务数据明确为合成。

## 字体与验证

无衬线文字使用 Arial / Noto Sans SC；诊断表使用 Georgia / Songti SC。文字保持正体，粗体显式设置；字体不嵌入，另一机器须重新核验实际匹配、中文粗体和换行。机器检查、逐页 canonical PNG 复核和 PowerPoint 原生结果分别记录于迁移验收报告，不互相替代。
