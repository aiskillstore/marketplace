# anyviz 示例库

本目录是 anyviz 的「整屏大屏」示例集。每个示例都不是单一图表，而是一个**完整的、可直接在浏览器打开运行的行业数据大屏**，演示如何用 anyviz 的设计系统把多种图表协同组织成一块专业级可视化大屏。

所有示例共享同一套 anyviz 深色大屏美学：底色 `#03050C`、品牌分类色板（`#4269d0` `#3ca951` `#ff725c` `#a463f2` `#efb118` `#6cc5b0`）、统一的排版与卡片规范。
其中涉及中国地图的示例会复用 `examples/common/china.js` 本地地图注册脚本，减少对远程资源的依赖。

## 大屏示例（4 个行业场景）

| 示例 | 目录 | 技术栈 | 场景 |
|------|------|--------|------|
| **金融市场实时监控中心** | [`finance-trading/`](finance-trading/) | ECharts 5.5.1 | K 线 + 均线、实时分时、资金流向、板块热力图、北向资金、涨跌停 |
| **电商运营数据中心** | [`ecommerce-retail/`](ecommerce-retail/) | ECharts 5.5.1 | GMV 趋势、品类占比、区域销售地图、转化漏斗、渠道分布、热销榜 |
| **智慧能源物联监控中心** | [`iot-energy/`](iot-energy/) | ECharts 5.5.1 | 实时功率曲线、能源结构、设备仪表盘、能耗热力、设备拓扑、告警分布 |
| **城市大数据可视化中心** | [`city-geo/`](city-geo/) | ECharts 5.5.1 | 中国地图飞线 + 涟漪、城市排名、客流趋势、年龄结构、24h 热力 |

每个目录内含 `index.html`（可直接运行）和 `README.md`（设计说明、图表清单、品牌色决策、一致性检查清单）。

## 运行方式

```bash
# 任意大屏：直接在浏览器打开
open examples/finance-trading/index.html

# 或启动本地服务器（部分浏览器对本地地图资源更友好）
cd examples/finance-trading
python3 -m http.server 8000
```

设计面向 1920×1080 大屏，并做了响应式适配（CSS Grid + `chart.resize()`），可在普通屏幕上正常查看。所有数据均为前端生成的模拟数据，生产环境替换为真实数据源（API / CSV）即可。

## 文件结构

```
examples/
├── README.md                       ← 本文件（总索引）
├── test_config_valid.json          ← theme_validator 测试夹具（勿动）
├── test_config_invalid.json        ← theme_validator 测试夹具（勿动）
├── common/china.js                 ← 本地中国地图注册脚本（供地图示例使用）
├── finance-trading/                ← 金融/交易大屏
│   ├── index.html
│   └── README.md
├── ecommerce-retail/               ← 电商/零售运营大屏
│   ├── index.html
│   └── README.md
├── iot-energy/                     ← 物联网/能源监控大屏
│   ├── index.html
│   └── README.md
└── city-geo/                       ← 城市/地理大屏
    ├── index.html
    └── README.md
```

## 这些示例演示了什么

每个大屏都遵循 anyviz 的核心原则，可作为构建你自己大屏的参考：

1. **多图表协同，而非孤立图表**：KPI 卡、主图、辅助图、地图、列表在一块画布上协同表达一个完整的业务视角。
2. **美学参数明确写死**：颜色、字号、间距、网格全部显式配置，不依赖 ECharts 默认主题。
3. **跨图表一致性**：同一实体在不同图表中颜色一致；标题、轴、网格、边距规则统一。
4. **深色大屏语言**：克制的辉光与渐变、等宽数字、实时时钟与 LIVE 指示，营造指挥中心质感。
5. **无障碍**：文字对比度达标，颜色编码外附加冗余编码（↑↓、形状），地图含降级方案防白屏。

## 与指南文档的关联

创建或修改大屏时，请参考：

| 文档 | 用途 |
|------|------|
| `guides/chart-selection.md` | 根据数据类型和意图选择图表 |
| `aesthetics/default.json` | 加载默认美学参数（颜色、排版、间距） |
| `guides/legend-layout.md` | 检查图例边界、避让、居中与安全距离 |
| `guides/academic-publication.md` | 论文、研究报告与装订文档图表规则 |
| `guides/consistency-rules.md` | 多图表一致性规则 |
| `guides/accessibility.md` | 无障碍检查清单 |
| `templates/TEMPLATE-SPEC.md` | 图表模板统一结构规范 |

## 测试夹具

`test_config_valid.json` 与 `test_config_invalid.json` 是 `scripts/theme_validator.py` 的测试夹具，CI 会用到，**请勿修改或删除**。

## 许可证

所有示例代码遵循 anyviz 主项目许可证。参见 [`LICENSE`](../LICENSE)。
