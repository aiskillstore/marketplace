---
name: anyviz
description: >-
  Use when 用户请求选择、创建、改进或统一数据可视化，并需按数据与意图选择图表、主题及
  D3.js、ECharts、Mapbox、Three.js、Matplotlib、Plotly 或 ggplot2 技术栈。
---

# anyviz

为数据与意图选图，应用统一美学，生成目标环境可运行代码。只加载当前任务所需资源。

## 流程

### 1. 分析

- 数据：变量数量、数值/类别/时间/地理/层次类型、规模、分布、缺失、异常。
- 意图：比较、分布、关系、组成、趋势、地理、层次、流程。

### 2. 选图与主题

1. 读 `guides/chart-selection.md`；单图不足时用组合图或多视图。
2. 读对应模板：`templates/charts/`、`maps/`、`graphs/`、`3d/`。新增或修改模板遵循 `templates/TEMPLATE-SPEC.md`。
3. 按场景加载主题：

| 场景 | 主题 |
|---|---|
| 报告、PPT、PDF、邮件、商业汇报 | `analytics` |
| 大屏、监控、实时看板、深色仪表盘 | `dashboard` |
| 论文、期刊、学位论文、印刷 | `academic` |
| 网页、交互产品、社交媒体、通用 | `modern` |

场景模糊且风格影响结果时询问；否则默认 `modern`。同一输出只用一个主题。

### 3. 应用美学

- 先读权威配置 `aesthetics/default.json` 与所选 `aesthetics/themes/*.json`。
- 按需读：色彩 `aesthetics/color.md`、排版 `aesthetics/typography.md`、布局 `aesthetics/layout.md`。
- 色板选择读 `guides/color-guide.md`；自然语言定制读 `guides/customization-guide.md`。
- 用户明确值覆盖主题；主题覆盖默认值。覆盖项传递到同一输出全部图表。
- 主标题按完整画布居中。顶部图例独占安全带；静态导出检查可见内容中心。

### 4. 选技术栈

| 环境/条件 | 选择 | 适配器 |
|---|---|---|
| Web 已装 ECharts；或要求快速开箱 | ECharts | `adapters/web/echarts.md` |
| Web 已装 Mapbox；地理交互 | Mapbox | `adapters/web/mapbox.md` |
| Web 已装 Three.js；3D | Three.js | `adapters/web/three.md` |
| Web 无已知依赖；高定制 | D3.js | `adapters/web/d3.md` |
| Python 交互/Jupyter | Plotly | `adapters/python/plotly.md` |
| Python 论文/出版 | Matplotlib | `adapters/python/matplotlib.md` |
| R/统计 | ggplot2 | `adapters/r/ggplot2.md` |

地理优先 Mapbox（Web）或 Plotly Mapbox（Python）；3D 优先 Three.js 或 Plotly 3D。先检查项目依赖，不凭空引入库。

#### HTML 大屏硬约束

- `init` 前根容器必须可见、非零，并有明确 `width` 与 `height`/`min-height`；`flex: 1` 不算显式高度。
- 地图使用本地注册资产或已验证降级，不只依赖远程脚本。
- 密集标签启用 `hideOverlap`、截断、抽稀或重排。
- 卡片圆角、内边距、边框、阴影一致。

### 5. 校验

多图表读 `guides/consistency-rules.md`：统一字体角色、实体颜色、间距、线点样式、数值格式、标注、图表语义、交互。图例 ≥4 项用 2×N 网格；细则见 `guides/legend-layout.md`。

论文/报告另读 `guides/academic-publication.md`：检查题注、来源、图例间距、时间轴节点、导出居中。

全部输出读 `guides/accessibility.md`：

- 文本/背景对比度 ≥4.5:1；大字与数据元素 ≥3:1。
- 关键区分至少两种编码；红绿语义加 ▲▼/＋−，或改蓝橙。
- 提供 alt text（类型、趋势、数据出口）；复杂图附表或 CSV。
- 交互支持键盘、可见焦点、≥44px 触摸目标、非 hover 信息入口、`prefers-reduced-motion`。

可选运行 `scripts/theme_validator.py` 校验输出 JSON。

## 输出契约

1. 用 1–2 句说明选图理由。
2. 给出主题、配色与关键设计决策。
3. 给出含数据转换和显式美学参数的完整可运行代码；不依赖库默认值。
4. 多图表列出已核验的共同属性。

## 资源

- 图表选择：`guides/chart-selection.md`
- 美学：`aesthetics/default.json`、`aesthetics/themes/*.json`、`aesthetics/*.md`
- 定制与校验：`guides/color-guide.md`、`guides/customization-guide.md`、`guides/consistency-rules.md`、`guides/legend-layout.md`、`guides/academic-publication.md`、`guides/accessibility.md`
- 34 个模板：`templates/charts/` 20、`maps/` 3、`graphs/` 8、`3d/` 3
- 适配器：`adapters/web/`、`adapters/python/`、`adapters/r/`
