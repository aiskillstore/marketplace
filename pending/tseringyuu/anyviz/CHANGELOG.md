# Changelog

All notable changes to anyviz are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

本变更日志遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 格式与
[语义化版本](https://semver.org/lang/zh-CN/) 规范。

## [Unreleased]

## [1.0.3] - 2026-08-06

### Added 新增

- Native shell installers for macOS, Linux, and Windows install the complete anyviz Agent
  Skill into the shared Agent Skills directory and every detected agent-specific skill root,
  without requiring Node.js or Python.
  新增 macOS、Linux 与 Windows 原生安装脚本，无需 Node.js 或 Python，即可把完整 anyviz
  Agent Skill 安装到通用目录与检测到的各 Agent 独立目录。
- Installer regression coverage verifies initial installation, supporting resources,
  agent detection, and idempotent updates.
  新增安装器回归测试，覆盖首次安装、配套资源、Agent 检测与幂等更新。

### Changed 变更

- All 53 runtime prompt files were compressed while preserving chart-selection behavior,
  hard constraints, accessibility rules, adapter code, and template data contracts.
  精简全部 53 个运行时提示文件，保留选图行为、硬约束、无障碍规则、适配器代码与模板数据契约。
- The main skill now uses progressive disclosure, and all 34 chart templates share shorter,
  consistent section names for faster scanning and lower context usage.
  主技能改用渐进式加载；34 个图表模板统一短章节名，降低上下文占用并提升检索效率。

## [1.0.2] - 2026-07-08

### Added 新增

- `guides/academic-publication.md` — publication rules for academic papers, university
  research projects, bound Word/PDF documents, captions, source notes, legend clearance,
  visual centering after export, and timeline marker aspect preservation.
  新增学术论文与研究报告图表规则，覆盖题注、资料来源、装订文档、导出后视觉居中、图例安全距离与时间轴节点防变形。
- `aesthetics/default.json` now defines canvas-anchored title alignment, legend clearance
  safe areas, export visual-centering policy, and default embedded-source policy.
  默认美学规范新增画布级标题居中、图例安全区、导出视觉居中与图内资料来源策略。
- `aesthetics/themes/academic.json` now includes a `publication` section for formal
  research-report and thesis contexts.
  Academic 主题新增 `publication` 区块，面向高校研究项目、论文、研究报告与装订文档。
- Package entry points now expose core guide paths through `anyviz.guides.*`, with matching
  npm export-map entries for all core guides.
  npm 入口新增 `anyviz.guides.*`，并在 export map 中公开全部核心指南路径。
- `scripts/check_package_exports.js` validates that published guide APIs resolve to files
  present in the package.
  新增包导出校验脚本，确保指南 API 与实际文件一致。

### Changed 变更

- Matplotlib, D3, ECharts, and ggplot2 adapters now document canvas-level titles, dedicated
  legend bands, safer legend-to-plot spacing, and publication-friendly export behavior.
  各技术栈适配指南统一补充画布级标题、图例安全带、图例与绘图区间距、出版型导出规则。
- README, README.en, SKILL, layout, consistency, and legend guides now include explicit
  references to chart centering, title centering, legend clearance, and academic publication
  behavior.
  主文档、工作流入口与相关指南补充图表居中、标题居中、图例间距与论文出版场景规则。
- `npm run validate` now runs both theme validation and package-export validation.
  主验证命令同时覆盖主题规范与包入口导出一致性。

### Fixed 修复

- Theme validation now rejects charts that disable export visual centering, use axis-centered
  titles where canvas-centered titles are required, or place legends too close to titles,
  axes, data labels, or plot areas.
  主题校验器现在会拦截导出视觉居中关闭、标题以坐标轴而非画布居中、图例与标题/轴/标签/绘图区过近等问题。
- Academic source-note rules now prevent duplicate source notes inside chart images when
  the document layer already renders captions and source paragraphs.
  学术场景下避免图像内部与文档层重复绘制资料来源说明。
- Timeline guidance now avoids aspect distortion caused by axis-transform circles, favoring
  scatter/symbol markers that preserve circular geometry.
  时间轴规则避免使用易被拉伸的坐标轴变换圆形，优先采用保持圆形比例的 scatter/symbol 节点。

## [1.0.1] - 2026-06-17

### Added 新增

- `guides/legend-layout.md` — legend positioning rules covering viewBox bounds checking,
  label collision avoidance, 2×N grid layout for ≥4 items, horizontal centering, and
  academic theme line-style differentiation. Based on real-world layout bugs encountered
  in multi-chart document generation.
  图例布局规则：viewBox 边界检查、标签避让、4 项以上 2×N 网格、水平居中、学术主题线型冗余。
  基于多图表文档生成中遇到的实际布局 bug 总结。
- `aesthetics/themes/academic.json` — added `line_style_differentiation` section defining
  stroke-dasharray mapping for series 0-4+ (solid / long-dash / short-dash / dotted / cycle).
  Academic 主题新增线型差异化配置，定义系列 0-4+ 的 stroke-dasharray 映射。
- `templates/charts/bar-chart.md` — added design points 6-7 (negative bar label clearance,
  horizontal diverging bar label separation) and expanded Diverging Bar variant with
  concrete layout diagrams and common-error callouts.
  柱状图模板新增负值标签避让规则和横向双向条形图标签分侧规则。
- `templates/charts/radar-chart.md` — added design points 7-8 (legend vs dimension label
  avoidance, academic theme multi-entity line-style differentiation).
  雷达图模板新增图例与维度标签避让规则和学术主题多实体线型区分规则。
- `templates/charts/line-chart.md` — added design points 6-7 (legend bounds checking,
  dual-axis legend annotation).
  折线图模板新增图例边界检查和双轴图例标注规则。

## [1.0.0] - 2026-05-28

### Added 新增

- Initial public release. 初始公开发布。
- **Chart template library: 34 templates** / 图表模板库 34 种:
  - `charts/` (20): bar, line, scatter, area, pie/donut, histogram, box plot, heatmap,
    radar, waterfall, density, waffle, dot, slope, small multiples, calendar heatmap,
    candlestick, hexbin, parallel coordinates, scatter matrix
    （柱状、折线、散点、面积、饼/环、直方图、箱线、热力、雷达、瀑布、密度、华夫、点图、
    坡度、小倍数、日历热力、烛台、六边形分箱、平行坐标、矩阵散点）
  - `maps/` (3): choropleth, bubble map, flow map（面量图、气泡地图、流向地图）
  - `graphs/` (8): sankey, chord, force-directed, treemap, sunburst, dendrogram,
    arc diagram, alluvial（桑基、和弦、力导向、树图、旭日、树形、弧形、冲积）
  - `3d/` (3): globe, scatter 3D, surface（3D 地球、3D 散点、曲面）
- `templates/TEMPLATE-SPEC.md` — unified five-section template specification.
  统一五段式模板规范。
- Four built-in themes: `modern`, `analytics`, `dashboard`, `academic`.
  四套内置主题。
- Five-stage visualization pipeline: analysis → aesthetics → adaptation → consistency → accessibility.
  五阶段可视化流水线。
- Multi-stack adapters: D3.js, ECharts, Mapbox, Three.js (web); Plotly, Matplotlib (Python);
  ggplot2 (R). 多技术栈适配器。
- Authoritative aesthetic spec in `aesthetics/default.json` plus `color.md`, `typography.md`,
  `layout.md`. 权威美学规范。
- Decision guides: `chart-selection.md`, `color-guide.md`, `consistency-rules.md`,
  `customization-guide.md`, `accessibility.md`. 决策、定制与无障碍指南。
- `scripts/theme_validator.py` for automated theme-consistency validation.
  主题一致性校验脚本。
- Open-source community files: `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`,
  GitHub issue/PR templates, and CI workflow. 开源社区配套与 CI。
- SVG brand assets: `assets/banner.svg`, `assets/wordmark.svg`.
  纯 SVG 品牌视觉资产。
- npm package entry (`package.json`, `index.js`). npm 程序化入口。

### Changed 变更

- All templates completed to the five-section structure.
  所有模板补齐五段式结构。
- Aesthetic guides expanded: palette generation, dark themes, number typography, label de-overlap,
  multi-chart grid layout, responsive design, interaction consistency.
  审美指南扩充：色板生成、深色主题、数字排版、标签防重叠、多图布局、响应式、交互一致性。
- `examples/` restructured into runnable `.html` files with per-scenario READMEs.
  示例重构为可运行 HTML + 场景 README。
- `README.md` / `README.en.md` rewritten with SVG banner and corrected figures.
  README 重写，更新横幅与事实数据。

### Fixed 修复

- `scripts/theme_validator.py`: per-chart validation for top-level `charts` arrays;
  default-palette prefixes no longer flagged as customizations.
  修复多图表校验漏检；默认色板前缀不再误报为定制。

### Removed 移除

- Legacy raster logo and pre-rendered promo media, replaced by SVG assets.
  移除旧位图 logo 与预渲染宣传素材。

[Unreleased]: https://github.com/TseringYuu/anyviz/compare/v1.0.3...HEAD
[1.0.3]: https://github.com/TseringYuu/anyviz/compare/v1.0.2...v1.0.3
[1.0.2]: https://github.com/TseringYuu/anyviz/compare/v1.0.1...v1.0.2
[1.0.1]: https://github.com/TseringYuu/anyviz/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/TseringYuu/anyviz/releases/tag/v1.0.0
