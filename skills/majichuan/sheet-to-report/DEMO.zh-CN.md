# 10 万行合成数据演示

[English](DEMO.md)

这个案例用于展示 `sheet-to-report` 如何把一张结构化业务表转成完整简报。数据、业务背景与分析结论均为自主合成内容。

## 输入概况

| 项目 | 演示范围 |
| --- | --- |
| 数据量 | 100,000 行 |
| 周期 | 2024 年 1 月至 2025 年 6 月 |
| 主要维度 | 渠道、区域、品类、用户层级 |
| 主要指标 | 访问量、订单数、收入、退款、营销成本 |
| 汇报目标 | 复盘增长、效率、退款压力与下一步验证 |

公开案例提供完整 HTML、四组两版 PPT 同页对照，以及两套完整23页样例。5 MB 源表不放进公开仓库；需要本地试用时，可运行 `scripts/generate_sample.py` 生成一份更轻量的合成表。

## 本案例的核心判断

1. **收入增长但投入产出回落。** 先核验付费广告效率，内容种草的增长需要进一步验证。
2. **服饰扩量需同步处理退款压力。** 增长与售后问题应进入同一条决策路径。
3. **分层优势不等于可复制增量。** 用户层级的平均差异只能提供验证方向，不能直接视为因果回报。

## 查看产物

**[在线查看完整案例展示](https://majichuan.github.io/sheet-to-report/)** · [阅读完整 HTML 分析简报](https://majichuan.github.io/sheet-to-report/report.html)

HTML 按“核心判断、经营基本盘、图表依据、行动路线、指标口径”组织阅读主线。主要结论可跳转到对应证据，并保留会影响解释的限制条件。

| 可编辑标准版 | 可选 SlideViber 美化版 |
| --- | --- |
| ![标准版图表页](assets/screenshots/standard-ppt-chart.png) | ![SlideViber 美化版图表页](assets/screenshots/slideviber-ppt-chart.png) |

两张图使用同一组源数据与同一条结论。标准版侧重直接编辑和汇报结构；SlideViber 美化版使用独立构图，加强结论、业务解释与图表之间的关系。美化环节为可选能力，需要用户单独安装 SlideViber。

[下载完整可编辑标准版 PPTX](https://majichuan.github.io/sheet-to-report/downloads/sheet-to-report-demo-standard.pptx) · [下载完整 SlideViber 美化版 PPTX](https://majichuan.github.io/sheet-to-report/downloads/sheet-to-report-demo-slideviber.pptx)

## 这个案例证明了什么

- 分析从指标含义与业务问题出发。
- 结论保留周期、分母、筛选与证据关系。
- HTML、标准 PPT 与美化 PPT 共用同一份分析模型，美化不能悄悄改结论或漏信息。
- 行动建议写清调整对象、具体做法、验证信号与停止边界。

本案例只用于展示产品能力，不是基准测试，也不代表任何真实企业表现。
