<p align="center">
  <img src="assets/banner.svg" alt="anyviz — 面向 AI 时代的数据可视化" width="100%">
</p>

<p align="center">
  <a href="https://www.npmjs.com/package/anyviz"><img src="https://img.shields.io/npm/v/anyviz?style=flat-square&color=4269d0" alt="npm"></a>
  <a href="https://anyviz.aiware.store"><img src="https://img.shields.io/badge/website-anyviz.aiware.store-111827?style=flat-square" alt="Website"></a>
  <a href="https://github.com/TseringYuu/anyviz"><img src="https://img.shields.io/badge/anyviz-v1.0.2-4269d0?style=flat-square" alt="Version"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-3ca951?style=flat-square" alt="License"></a>
  <a href="SKILL.md"><img src="https://img.shields.io/badge/AI%20ready-workflow-a463f2?style=flat-square" alt="AI-ready workflow"></a>
  <a href="aesthetics/default.json"><img src="https://img.shields.io/badge/design-Observable_Plot-ff725c?style=flat-square" alt="Design System"></a>
  <a href="adapters/web/d3.md"><img src="https://img.shields.io/badge/engine-D3.js-efb118?style=flat-square" alt="Default Engine"></a>
  <img src="https://img.shields.io/badge/platform-Web%20%7C%20Python%20%7C%20R-6cc5b0?style=flat-square" alt="Platforms">
</p>

<p align="center">
  <b>简体中文</b> · <a href="README.en.md">English</a>
</p>

> **anyviz** 是一个面向 AI 时代的数据可视化规范与工作流库。
> 它为 AI 工具提供专业数据设计师级别的判断：图表选择、美学系统、
> 多技术栈渲染，以及同一画布下多图表的设计一致性。

<p align="center">
  <a href="https://anyviz.aiware.store"><b>官网</b></a> ·
  <a href="https://www.npmjs.com/package/anyviz">npm</a> ·
  <a href="SKILL.md">AI 工作流入口</a> ·
  <a href="examples">示例</a>
</p>

---

## 安装与使用

### 在 AI 编程工具中使用

把 anyviz 作为 AI 助手的可视化工作流上下文使用。AI 需要优先读取 [`SKILL.md`](SKILL.md)，
并按需查阅 `guides/`、`templates/`、`adapters/` 与 `aesthetics/`。

macOS / Linux 一键安装到当前用户的所有已检测 Agent：

```bash
curl -fsSL https://raw.githubusercontent.com/TseringYuu/anyviz/main/install.sh | sh
```

Windows PowerShell：

```powershell
irm https://raw.githubusercontent.com/TseringYuu/anyviz/main/install.ps1 | iex
```

安装器不依赖 Node.js 或 Python。通用 Agent Skills 目录覆盖 Codex、Cursor、OpenCode、
OpenClaw、Cline、Kimi Code CLI、Warp、Zed 等工具，并自动检测 Claude Code、Hermes Agent、
Gemini CLI、GitHub Copilot、Windsurf、Goose 等使用独立目录的工具。重复执行同一命令即可更新；
若目标位置已有非安装器管理的同名 Skill，原目录会先保留为带时间戳的备份。

```text
请使用 anyviz 工作流，帮我可视化这份销售数据
用地图展示各省的人口分布，并保持适合报告的浅色主题
制作一个 1920×1080 的业务仪表盘，展示关键运营指标
把这些图表统一改成深色大屏风格
```

如果你的工具支持通过仓库或目录加入上下文，也可直接添加本仓库；如果支持自定义 Skill，
将 [`SKILL.md`](SKILL.md) 与相关资源目录一起加入工具上下文。

### 在项目中安装

通过 npm 安装后，可以在脚本或应用中读取 anyviz 的主题、模板与规范路径。

```bash
npm install anyviz
```

```js
const anyviz = require('anyviz');

const theme = anyviz.defaultTheme();
const dashboardTheme = anyviz.themes.dashboard();

console.log(anyviz.skillPath);
console.log(anyviz.guides.academicPublication);
console.log(theme.color.categorical.palette);
console.log(dashboardTheme.name);
```

也可以直接从仓库引用核心规范：

```bash
git clone https://github.com/TseringYuu/anyviz.git
```

官网与示例入口：[https://anyviz.aiware.store](https://anyviz.aiware.store)

---

## 为什么需要 anyviz

大模型早已能写出绘图代码，缺的是**品味**与**一致性**，也就是把“默认样式的图”与“专业作品”
区分开的那些细小但关键的决策。anyviz 把这些决策沉淀为一套可复用的规范：选哪种图、用什么色板、
字号如何分级、标签放在哪里，以及多张图如何保持视觉连贯。

- **图表智能**——将数据形态与分析意图（比较、分布、关系、组成、趋势、地理、层次、流程）映射到
  **34 种生产级模板**中最合适的一种。
- **黄金美学**——植根于 Tufte 的数据墨水比与 ColorBrewer / Viridis 色彩科学，提供感知均衡、
  色盲友好的默认主题。
- **环境感知渲染**——同一套规范在 Web（D3.js、ECharts、Mapbox、Three.js）、Python（Plotly、
  Matplotlib）与 R（ggplot2）上产出视觉一致的结果。
- **一致性即默认**——任何未显式指定的属性都从全局规范继承，并由校验器在多图布局中强制执行。
- **内建无障碍**——对比度、冗余编码与替代文本指导是流水线的一部分，而非事后补救。

---

下面的展示图呈现了 anyviz 适用的多种输出形态：分析报告、运营仪表盘、地理可视化与监控大屏。
这些场景都不是孤立图表，而是在同一画布中组织多种可视化，形成清晰、统一、可落地的业务视图。

<p align="center">
  <img src="assets/showcase.gif" alt="使用 anyviz 设计的多种整屏数据大屏示例" width="100%">
</p>

## 工作流水线

anyviz 通过五阶段工作流处理每一个请求，确保从原始数据到生成代码的每一步都符合专业标准：

**分析 → 美学 → 适配 → 一致性 → 无障碍**

1. **分析** — 根据数据形态与意图，从 34 种模板中选择图表
2. **美学** — 应用统一色彩与字号分级（Tufte）
3. **适配** — 检测项目技术栈，输出 D3 / ECharts 等代码
4. **一致性** — 同步实体颜色、数值格式与间距
5. **无障碍** — 对比度、色盲友好与替代文本

---

## 作为独立美学库

规范以纯 JSON 定义，任何工具或脚本都可直接引用。

```python
import json

# 加载 anyviz 权威美学规范
with open('aesthetics/default.json', encoding='utf-8') as f:
    theme = json.load(f)

# 分类色板
palette = theme['color']['categorical']['palette']
print(f"分类色板: {palette}")

# 排版层级
h1 = theme['typography']['scale']['h1']
print(f"主标题: {h1['size_px']}px / 字重 {h1['weight']}")
```

---

## 模板库（34 种）

| 类目 | 数量 | 模板 |
| :--- | :---: | :--- |
| [`templates/charts/`](templates/charts) | 20 | 柱状、折线、散点、面积、饼图/环形、直方图、箱线、热力、雷达、瀑布、密度、华夫、点图、坡度、小倍数、日历热力、烛台、六边形分箱、平行坐标、矩阵散点 |
| [`templates/maps/`](templates/maps) | 3 | 面量图、气泡地图、流向地图 |
| [`templates/graphs/`](templates/graphs) | 8 | 桑基、和弦、力导向、树图、旭日、树形图、弧形图、冲积图 |
| [`templates/3d/`](templates/3d) | 3 | 3D 地球、3D 散点、3D 曲面 |

每个模板都遵循 [`templates/TEMPLATE-SPEC.md`](templates/TEMPLATE-SPEC.md) 定义的统一五段式结构：
*适用场景、数据格式、美学参数、设计要点、变体。*

---

## 核心设计原则

**1. 美学优先。** 最大化数据墨水比，消除图表垃圾。优先直接标注而非图例，倡导小倍数图而非动画，
让数据本身成为焦点。

**2. 一致性优于个性化。** 任何未指定的属性都从全局规范继承。即使调用者仅覆盖一种颜色，字体、
间距、网格线依然严格统一。

**3. 环境感知自适应。** anyviz 感知运行环境与依赖，在 Web、Python、R 上产出视觉一致的输出，
无需调用者操心技术栈。

**4. 可解释、可修改。** 每次输出都附带图表选择理由与美学决策说明。没有黑盒，任何参数都可被
理解和调整。

---

## 默认色板

默认 `modern` 主题受 Observable Plot 现代设计语言启发——明亮、克制、色盲友好。

| | 色值 | 语义 |
| :---: | :--- | :--- |
| 🔵 | `#4269d0` | 主要系列——稳定、信任 |
| 🟢 | `#3ca951` | 次要——增长、正面、达标 |
| 🔴 | `#ff725c` | 对比——警告、负面、亏损 |
| 🟣 | `#a463f2` | 辅助——高亮、特殊对比 |
| 🟡 | `#efb118` | 辅助——注意、预警 |
| 🩵 | `#6cc5b0` | 辅助——青色、中性对比 |
| ⚪ | `#9696a0` | 中性灰——参考线、"其他" |
| 🟠 | `#f5a623` | 橙色——高对比高亮 |
| 🩷 | `#ca5bb8` | 洋红——特殊类别 |
| 🌸 | `#ff8ab7` | 粉色——辅助类别 |

完整色板原理与色盲说明：[`guides/color-guide.md`](guides/color-guide.md) 与
[`guides/accessibility.md`](guides/accessibility.md)。

---

## 技术栈自适应

anyviz 解析调用场景与依赖，自动选择最合适的引擎：

| 环境 | 默认 | 触发条件 | 优势 |
| :--- | :--- | :--- | :--- |
| **Web** | **D3.js** | 默认——零依赖、完全自定义 | 像素级控制、无依赖 |
| **Web** | **ECharts** | 项目已装 `echarts`，或需开箱即用图表 | 性能高、交互丰富 |
| **Web** | **Mapbox** | 地理空间数据、高精度地图 | 专业地图渲染、海量数据 |
| **Web** | **Three.js** | 三维空间、曲面、沉浸式场景 | 原生 3D、硬件加速 |
| **Python** | **Plotly** | Jupyter、交互式分析、仪表盘 | 交互强、可导出 HTML |
| **Python** | **Matplotlib** | 论文、出版、静态高清 | 打印友好、符合学术规范 |
| **R** | **ggplot2** | R 生态下的统计分析 | 声明式图形语法 |

---

## 自然语言定制

anyviz 将自然语言指令映射到美学参数，同时保持一致性：

| 维度 | 你说 | 映射到 | 效果 |
| :--- | :--- | :--- | :--- |
| **主题** | "深色模式" | 页面 `#1A1A1A`、文本 `#E8E8E8`、色板提亮 15% | 沉浸式深色大屏，高对比 |
| **风格** | "学术/论文风格" | 衬线字体、隐藏 Y 网格线、保留外边框 | 克制、出版就绪 |
| **风格** | "高校研究项目/论文图表" | 启用 academic publication 规则、外置题注与资料来源、禁用图内重复来源 | 适配装订文档、研究报告与正式评审材料 |
| **风格** | "极简" | 去除网格线与边框，仅保留核心轴线 | 最大化数据墨水比 |
| **颜色** | "暖色调" | 限制色相 0°–60° | 充满活力的暖色感受 |
| **颜色** | "冷色调" | 限制色相 180°–270° | 冷静、科技感 |
| **排版** | "字体大一些" | 所有层级（H1–H6）×1.15 | 大屏可读性更好 |
| **布局** | "图表居中 / 标题居中" | 标题以画布为锚点居中，导出后执行视觉内容居中检查 | 避免 Word、论文或报告中出现视觉偏移 |
| **布局** | "图例离图远一点" | 图例启用安全带与最小间距，优先避让标题、轴标签与数据标签 | 防止图例与图表元素过近或互相挤压 |
| **布局** | "适合手机看" | 应用 mobile 断点、1:1 宽高比 | 适配窄屏，防标签重叠 |
| **元素** | "显示数据标签" | 开启数据标签（9px、`#888888`） | 无需悬停即读精确值 |

完整映射：[`guides/customization-guide.md`](guides/customization-guide.md)。

---

## 目录结构

```text
anyviz/
├── SKILL.md                  # AI 工作流入口（流水线 + 核心规则）
├── README.md                 # 中文主文档
├── README.en.md              # 英文备用文档
├── aesthetics/               # 权威美学规范
│   ├── default.json          # 默认主题（颜色、排版、间距、线条、响应式）
│   ├── color.md              # 色彩规则与色盲友好色板
│   ├── typography.md         # 排版规则与多语言字体
│   ├── layout.md             # 布局规则与数据墨水比标准
│   └── themes/               # modern · analytics · dashboard · academic
├── guides/                   # 决策、定制与出版指南
│   ├── academic-publication.md# 论文、研究报告与装订文档图表规则
│   ├── chart-selection.md    # 图表选择决策树（数据 + 意图 → 图表）
│   ├── color-guide.md        # 用色原则与语义约定
│   ├── consistency-rules.md  # 多图表一致性规则
│   ├── customization-guide.md# 自然语言 → 美学参数
│   ├── legend-layout.md      # 图例布局规则（边界检查、避让、居中、网格）
│   └── accessibility.md      # 对比度、色盲友好、冗余编码、替代文本
├── templates/                # 34 种图表模板
│   ├── TEMPLATE-SPEC.md       # 统一模板规范
│   ├── charts/               # 20 种统计图表
│   ├── maps/                 # 3 种地图
│   ├── graphs/               # 8 种关系与层次图
│   └── 3d/                   # 3 种三维图
├── adapters/                 # 技术栈适配器（web / python / r）
├── assets/                   # README 横幅、字标与展示素材
├── examples/                 # 可运行示例 + 各自 README
└── scripts/
    ├── theme_validator.py    # 主题一致性自动校验器
    └── make_*.py             # 品牌素材的可复现生成脚本
```

---

## 示例

[`examples/`](examples) 里的每个示例都是一块完整、可直接运行的**行业数据大屏**——不是单一图表，
而是一整块画布上协同组织的多种可视化，统一采用 anyviz 深色大屏美学。它们展示了同一套规范如何
适配金融监控、电商运营、能源物联与城市地理分析等不同需求。

- [`finance-trading`](examples/finance-trading) —— 金融实时监控：K 线 + 均线、实时分时、资金流向、板块热力
- [`ecommerce-retail`](examples/ecommerce-retail) —— 电商运营：GMV 趋势、品类占比、区域销售地图、转化漏斗
- [`iot-energy`](examples/iot-energy) —— 智慧能源物联：实时功率曲线、能源结构、设备仪表盘、拓扑图、告警
- [`city-geo`](examples/city-geo) —— 城市大数据：地图飞线 + 涟漪、城市排名、客流趋势、24h 热力

四个示例均为单文件 `index.html`（ECharts 5.5.1），面向 1920×1080 设计并做了响应式适配。

---

## 参与贡献

欢迎贡献——尤其是新模板、适配器与指南改进。模板结构、校验步骤与 PR 流程见
[CONTRIBUTING.md](CONTRIBUTING.md)，社区规范见 [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)。

```bash
# 本地校验主题配置
python3 scripts/theme_validator.py -c examples/test_config_valid.json
```

---

## 社区与友链

- [LINUX DO](https://linux.do) — 新一代综合社区，讨论、分享、共建

---

## 许可

[MIT](LICENSE)

---

## 学术与理论参考

anyviz 的设计植根于信息可视化领域的经典著作：

- **Edward Tufte** —— *The Visual Display of Quantitative Information*（数据墨水比、消除图表垃圾）
- **Nathan Yau** —— *Data Points: Visualization That Means Something*（感知设计、数据叙事）
- **ColorBrewer 2.0** —— *Color Advice for Cartography*（感知均衡、色盲友好色板）
- **Viridis** —— *Perceptually Uniform Colormaps*（高感知分辨率、打印与色盲友好）
