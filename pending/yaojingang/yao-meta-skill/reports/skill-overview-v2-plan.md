# Skill Overview v2 报告升级方案

## 结论

建议把 `reports/skill-overview.html` 从“Skill 概览页”升级为“Skill 生成审计报告”。它不只说明新 Skill 是什么，还要解释它为什么这样设计、质量如何、风险在哪里、后续怎么升级。

本版方案在上一版基础上做了三点修正：

1. 在最前面新增“技能概述”模块，让用户先读懂这个 Skill 的一句话定位、核心价值、适用对象和交付结果，再看指标和图表。
2. 将“总览指标”后移为第二模块，避免用户一打开页面就看到抽象分数，却还不知道这个 Skill 是什么。
3. 将报告定位从“好看的说明页”收紧为“可解释、可评估、可复盘的生成报告”，所有图表和分数都必须能从本地 Skill 文件或已有 reports 推导出来。

## 目标

每次创建一个全新 Skill 后，同时生成一份双语 HTML 报告：

- 默认中文简体，右上角可以切换英文。
- 白色背景，沿用 Kami 的长文档排版节奏。
- 顶部吸顶导航，每个一级模块保持四个汉字。
- 模块足够细，既能让普通用户理解 Skill，也能让维护者评估质量。
- 包含图表、矩阵、数字化指标和后续升级建议。
- 静态 HTML 可离线打开，不依赖外部图表库或在线资源。

## 非目标

- 不把报告做成复杂 Web App。
- 不引入外部 JS 图表库。
- 不让报告替代 `SKILL.md`、`README.md`、`agents/interface.yaml` 等源文件。
- 不用模型主观打分冒充事实评分；所有分数必须可解释。
- 不在报告里暴露用户私密原文，除非这些内容已经存在于 Skill 包体内且适合展示。

## 报告模块

顶部导航建议保留 9 个一级模块，全部四字：

1. 技能概述
2. 总览指标
3. 能力画像
4. 原理结构
5. 契约边界
6. 质量评估
7. 风险治理
8. 包体资产
9. 迭代路线

### 1. 技能概述

作用：让用户先用一分钟读懂这个新 Skill。

内容：

- Skill 名称、显示名称、创建时间、成熟度。
- 一句话定位：这个 Skill 主要解决什么重复任务。
- 核心价值：它能帮用户少做什么、稳定什么、交付什么。
- 适用对象：个人使用、团队复用、平台迁移或库级能力。
- 交付结果：最终生成哪些文件和报告。
- 使用提醒：最应该打开的文件和下一步建议。

图表：

- “Skill 名片”信息块。
- “从输入到交付”的三段式流程条：输入材料 -> Skill 包体 -> 可复用能力。

数据来源：

- `SKILL.md` frontmatter
- `README.md`
- `manifest.json`
- `agents/interface.yaml`
- `reports/intent-context.json`
- `reports/skill-overview.json`

### 2. 总览指标

作用：用数字化方式快速判断这个 Skill 的当前状态。

内容：

- 完整度分数
- 触发清晰度分数
- 证据充分度分数
- 可维护性分数
- 可迁移性分数
- 上下文成本估算

图表：

- 5 维雷达图。
- 指标卡片。
- “当前成熟度”状态条。

评分原则：

- 分数必须来自结构化规则，而不是主观判断。
- 每个分数旁边必须显示 1 到 3 条原因。
- 缺失数据时显示“未生成 / 证据不足”，而不是编造结论。

### 3. 能力画像

作用：说明这个 Skill 在能力地图中的位置。

内容：

- 它属于创建型、评审型、执行型、研究型、写作型还是工具型 Skill。
- 使用模式：Scaffold / Production / Library。
- 触发强度：显式调用、自然语言匹配、上下文辅助。
- 复用范围：个人、团队、跨项目、跨平台。

图表：

- 能力定位矩阵：横轴为“执行确定性”，纵轴为“知识密度”。
- 使用对象标签组。

数据来源：

- `manifest.json`
- `agents/interface.yaml`
- `reports/prompt-quality-profile.json`
- `reports/system-model.json`

### 4. 原理结构

作用：解释这个 Skill 为什么这样组织。

内容：

- 意图澄清
- 边界路由
- 资产分层
- 证据回路
- 漂移观察
- 杠杆升级

图表：

- 闭环流程图。
- 分层架构图：入口层、参考层、脚本层、评估层、报告层。
- 如果存在 system model，展示反馈回路。

数据来源：

- `SKILL.md`
- `references/`
- `scripts/`
- `evals/`
- `reports/system-model.json`

### 5. 契约边界

作用：说明什么时候该触发，输入输出是什么，边界在哪里。

内容：

- 触发描述
- 应触发场景
- 不应触发场景
- 输入材料
- 输出结果
- 排除项
- 失败或缺资料时的处理方式

图表：

- 输入输出矩阵。
- should-trigger / should-not-trigger 对照表。
- 边界卡片：Owned / Adjacent / Excluded。

数据来源：

- `SKILL.md` frontmatter
- `reports/intent-dialogue.json`
- `reports/intent-confidence.json`
- `evals/`
- `agents/interface.yaml`

### 6. 质量评估

作用：评估这个 Skill 是否可靠、清晰、可维护。

内容：

- `description` 是否清楚。
- `SKILL.md` 是否过重。
- `references/` 是否承担了长指导。
- `scripts/` 是否承担了确定性逻辑。
- `evals/` 是否覆盖触发和质量。
- prompt quality、artifact design、system model 摘要。

图表：

- 条形评分图。
- 质量证据表。
- “强项 / 缺口 / 建议”三列分析。

数据来源：

- `reports/prompt-quality-profile.json`
- `reports/artifact-design-profile.json`
- `reports/system-model.json`
- `reports/output-risk-profile.json`
- 包体文件统计

### 7. 风险治理

作用：让用户看到这个 Skill 当前最可能失败在哪里。

内容：

- 误触发风险
- 输出漂移风险
- 证据不足风险
- 包体膨胀风险
- 跨平台迁移风险
- 人工判断边界

图表：

- 风险热力图：影响程度 x 发生概率。
- 风险清单：风险、信号、应对方式、证据来源。

数据来源：

- `reports/output-risk-profile.json`
- `reports/system-model.json`
- `reports/intent-confidence.json`
- `reports/portability_score.json`

### 8. 包体资产

作用：让 reviewer 快速确认这个 Skill 的文件结构是否合理。

内容：

- `SKILL.md`
- `README.md`
- `agents/interface.yaml`
- `manifest.json`
- `references/`
- `scripts/`
- `evals/`
- `reports/`

图表：

- 包体树状图。
- 文件类型分布 donut。
- 资产状态表：存在、缺失、可选、过重、建议补充。

数据来源：

- 本地文件系统扫描
- `manifest.json`
- `agents/interface.yaml`

### 9. 迭代路线

作用：把下一步升级方向讲清楚，避免无序扩张。

内容：

- Top 3 下一步升级方向。
- 每个方向的原因、动作、收益和暂缓项。
- 哪些内容现在不应该做。
- 哪些前置条件满足后再升级。

图表：

- 优先级矩阵：价值 x 成本。
- 迭代时间线。

数据来源：

- `reports/iteration-directions.json`
- `reports/system-model.json`
- `reports/intent-confidence.json`

## 指标设计

### completeness_score

衡量关键资产是否齐全。

参考规则：

- `SKILL.md` 存在：基础分
- `agents/interface.yaml` 存在：加分
- `README.md` 存在：加分
- `manifest.json` 存在：加分
- `references/`、`scripts/`、`evals/`、`reports/` 根据成熟度判断是否加分

### trigger_score

衡量触发是否清晰。

参考规则：

- frontmatter `description` 是否存在
- 是否说明任务、输入、输出和非目标
- 是否有 should-trigger / should-not-trigger 样例
- 是否有 route eval

### evidence_score

衡量报告证据是否充分。

参考规则：

- 是否有 intent 报告
- 是否有 artifact design 报告
- 是否有 prompt quality 报告
- 是否有 system model 报告
- 是否有 iteration directions 报告

### maintainability_score

衡量是否容易维护。

参考规则：

- `SKILL.md` 不过长
- 长指导进入 `references/`
- 确定性逻辑进入 `scripts/`
- 测试或 eval 可随包体迁移
- 报告和 manifest 保持同步

### portability_score

衡量跨环境复用能力。

参考规则：

- `agents/interface.yaml` 是否完整
- `manifest.json` 是否声明目标平台
- 是否有降级策略
- 是否避免硬编码私有路径

### context_cost

估算上下文成本。

参考规则：

- `SKILL.md` 字数
- references 文件数量和总字数
- reports 是否只在需要时读取
- 是否把长说明放到入口文件

## 数据模型建议

建议生成一个中间报告模型：

```text
reports/skill-overview.json
```

核心结构：

```json
{
  "skill_summary": {},
  "scorecard": {},
  "capability_profile": {},
  "principle_model": {},
  "contract_boundary": {},
  "quality_review": {},
  "risk_governance": {},
  "package_assets": {},
  "iteration_roadmap": {},
  "report_contract": {}
}
```

HTML 只负责渲染这个模型，不直接到处读取文件。

## 实现拆分

建议把现有报告渲染器拆成四层：

```text
Skill package
  -> report model builder
  -> metrics calculator
  -> chart renderer
  -> HTML renderer
```

建议文件：

- `scripts/render_skill_overview.py`：保留 CLI 入口和编排。
- `scripts/skill_report_model.py`：汇总 Skill 数据和各模块内容。
- `scripts/skill_report_metrics.py`：计算分数和原因。
- `scripts/skill_report_charts.py`：生成内联 SVG 图表。
- `tests/verify_skill_overview.py`：验收 HTML 主结构。
- `tests/verify_skill_report_metrics.py`：验收分数规则。
- `tests/verify_skill_report_charts.py`：验收 SVG 图表和无外部依赖。

## 排版约束

- 背景保持纯白。
- 使用 ink-blue 作为强调色。
- 采用 Kami 式长文档节奏：先结论，再证据，再解释。
- 图表必须有 caption，caption 要说洞察，不只说图表名称。
- 不使用外部字体、外部图片或外部图表库。
- 顶部导航吸顶。
- 一级菜单全部四字。
- 默认中文简体，英文作为切换视图。
- 每个模块要能独立扫描，不依赖读者从头读到尾。

## 生成完成后的用户文案

创建 Skill 后，CLI / 输出摘要建议显示：

```text
Skill 已创建完成。

建议先打开总结报告：
<absolute-path>/reports/skill-overview.html

这份报告默认使用中文简体，右上角可切换英文。它会展示这个 Skill 的概述、指标、原理、触发边界、输入输出、质量评估、风险治理、包体资产和后续升级路线。
```

## 验收标准

功能验收：

- 新建 Skill 后自动生成 `reports/skill-overview.html` 和 `reports/skill-overview.json`。
- HTML 默认中文简体。
- 右上角可以切换英文。
- 顶部导航吸顶，一级菜单均为四字。
- 页面至少包含 9 个一级模块。
- 页面至少包含 4 类 SVG 图表：雷达图、流程图、风险热力图、资产分布图。
- 每个数字分数都有原因说明。
- 缺失数据时显示证据不足，不编造结论。

测试验收：

- `python3 tests/verify_skill_overview.py`
- `python3 tests/verify_yao_cli.py`
- `python3 tests/verify_skill_report_metrics.py`
- `python3 tests/verify_skill_report_charts.py`
- `make ci-test`

视觉验收：

- 桌面端顶部导航不遮挡正文。
- 移动端导航可以换行或紧凑展示，不溢出。
- 图表在白底上清晰可读。
- 中文默认视图没有大段英文占位。
- 报告可直接用浏览器打开。

## 风险与应对

### 风险一：报告变得过重

应对：模块多，但数据来源要轻。没有证据的模块显示“暂无证据”，不要额外生成大量报告。

### 风险二：分数看起来像主观评价

应对：每个分数绑定规则和原因，报告展示“为什么得这个分”。

### 风险三：渲染器继续膨胀

应对：先拆 model、metrics、charts，再扩 HTML。不要继续把所有逻辑塞进 `render_skill_overview.py`。

### 风险四：英文切换质量不足

应对：默认中文必须完整；英文可以先作为解释层，不要求每个用户原文都翻译，但不能影响中文体验。

## 推荐实施顺序

1. 定义 v2 `skill-overview.json` 数据结构。
2. 新增 metrics 计算器，先产出 scorecard 和原因。
3. 新增 chart renderer，生成内联 SVG。
4. 重构 HTML 为 9 个一级模块。
5. 更新 `init_skill.py` 和 `yao.py` 的报告输出文案。
6. 生成示例 Skill 报告，做视觉检查。
7. 跑专项测试和完整 CI。

## 最小可行版本

如果希望先小步迭代，第一版只做：

- 新增“技能概述”模块。
- 新增“总览指标”模块。
- 新增 5 维雷达图。
- 新增分数原因说明。
- 保留现有其他模块结构。

这能最快提升报告的第一屏价值，同时为后续 9 模块完整版本铺好数据结构。
