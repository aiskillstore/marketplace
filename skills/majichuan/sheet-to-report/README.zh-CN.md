# 数据分析&汇报小助手

[English](README.md)

**把一张业务表，变成有依据、讲得清、能行动的经营简报。**

![从业务表到证据、图表与行动](assets/brand/github-social-preview.png)

`sheet-to-report` 面向运营、销售、产品及业务负责人。提供一张结构清晰的 Excel／CSV 和汇报目标，由 AI 检查口径、寻找重点、补查依据、组织结论与行动建议，适合周报、月报、活动复盘和阶段经营汇报。

[在线看完整案例](https://majichuan.github.io/sheet-to-report/) · [三步开始](QUICKSTART.zh-CN.md) · [常见问题](FAQ.md) · [安装与环境](INSTALL.md)

## 先看实际效果

公开演示采用完全合成的 10 万行全渠道经营数据，覆盖 18 个月、11 个字段，不包含真实企业或个人信息。

**[在线查看完整案例展示](https://majichuan.github.io/sheet-to-report/)** · [阅读完整 HTML 分析简报](https://majichuan.github.io/sheet-to-report/report.html) · [查看案例说明](DEMO.zh-CN.md)

下面两张图使用同一条结论和同一组数据。标准版保留直接可编辑的图表与文字；可选的 SlideViber 美化版在不遗漏重要信息的前提下，重新组织构图和视觉层级。

| 可编辑标准版 | 可选 SlideViber 美化版 |
| --- | --- |
| ![标准版：整页原生图表显示付费广告投入产出低于去年同期](assets/screenshots/standard-ppt-chart.png) | ![SlideViber 美化版：左侧解释业务含义，右侧保留同一组图表证据](assets/screenshots/slideviber-ppt-chart.png) |

在线案例增加了四组同页对照，并提供两套完整23页样例：[下载可编辑标准版 PPTX](https://majichuan.github.io/sheet-to-report/downloads/sheet-to-report-demo-standard.pptx)，或[下载 SlideViber 美化版 PPTX](https://majichuan.github.io/sheet-to-report/downloads/sheet-to-report-demo-slideviber.pptx)。

## 30 秒了解

- **适合谁：** 需要做周报、月报、活动复盘或阶段经营汇报的运营、销售、产品及业务负责人。
- **准备什么：** 一张结构清晰的 Excel／CSV、汇报对象，以及希望解决的问题。
- **能得到什么：** 可离线阅读的 HTML 分析简报；按需生成可编辑标准 PPT；还可选择单独安装 SlideViber 继续制作美化版。
- **怎样配合：** 你负责提供数据和业务目标、确认必要口径；AI 负责检查、分析、组织结论和生成报告。

## 为什么选择 sheet-to-report

**帮你看懂业务变化，串起汇报主线，也把下一步讲清楚。**

- **抓住值得关注的问题——找问题**

  围绕你的汇报目标，从表中寻找重要变化、机会和风险。发现异常后，在数据支持的范围内继续按时间、渠道、人群或商品细分核查，并选择合适的图表说明。
- **结论有依据，判断有边界——核依据**

  先核对指标含义和比较范围，再组织结论。关键数字可以追溯到计算依据；数据不足时说明哪些还无法判断，避免把猜测当成事实。
- **把零散发现串成清楚的汇报主线——串主线**

  将整体表现、关键变化、细分证据和经营含义逐层展开，让读者顺着“发生了什么—哪些因素值得关注—依据是什么—下一步怎么做”理解整份报告。图表与文字前后呼应，汇报时更容易让听众跟上。
- **建议具体到行动和验证——落行动**

  说明针对哪个业务环节、建议怎么做、观察什么指标，以及什么情况下需要调整，帮助你把分析结果转成下一步工作安排。
- **一份分析，衔接阅读与汇报——出报告**

  按需生成离线 HTML、可编辑标准 PPT，并可另行安装 SlideViber 进一步美化。三类产物沿用同一套分析依据，并校验关键数字、口径与结论的一致性。

## 开始前准备

先准备三样东西：能读取文件并运行本地代码的 AI 工具、一张结构清晰的 Excel／CSV、你的汇报对象和希望解决的问题。你不需要编写代码或配置 JSON；让 AI 先检查环境即可。

HTML 需要 Python 3.10+ 和项目依赖；标准 PPT 还需要 Node.js 18+、`python-pptx` 及可用的预览工具；SlideViber 单独安装。完整说明见[安装与环境](INSTALL.md)。当前一次分析一张结构化表；个人和敏感信息请先删除或脱敏。单纯把 Skill 上传到平台，不代表该平台已经具备运行模型、读取文件和生成产物的完整条件。

## 从 Excel 到报告

| 阶段 | AI 会做什么 | 你怎样参与 | 可见结果 |
| --- | --- | --- | --- |
| 1. 明确分析范围 | 检查文件、字段和时间范围；展示简短方案或开始分析 | 提供目标；需要时确认口径或调整方案 | 知道要分析什么、是否还需补充 |
| 2. 生成 HTML 简报 | 寻找业务问题、补查证据、串联结论与行动，生成并检查 HTML | 阅读报告；只要 HTML 可在此结束 | 可打开的 HTML 及检查状态 |
| 3. 制作标准 PPT（可选） | 在可预览环境展示主题小样，选定后生成完整稿 | 回复“生成 PPT”，再选主题 | 主题预览、整稿阅读入口、可编辑 PPTX |
| 4. 继续美化（可选） | 检查 SlideViber 依赖，在同源分析基础上优化版式 | 回复“制作美化版” | 单独保存的美化稿及预览，标准稿保留 |

实际确认次数取决于数据口径、开始方式、已有偏好和运行环境，不会为了走流程反复询问已经确认的内容。

## 两种开始方式

**首次推荐：先确认分析方案。** 适合第一次使用，希望先确认分析方向和口径。复制下面这句话：

> 请用 sheet-to-report 分析这份 Excel，面向业务负责人做月度复盘。先检查数据，用简短的方案告诉我：建议分析哪个时间范围、重点回答哪些业务问题、有哪些需要我确认的口径。等我确认后再生成 HTML 分析简报。完成后，请告诉我如何继续制作可编辑 PPT。

AI 会先给出分析范围、重点问题、必要待确认项和预计交付。你可以这样回答：“按这个方案分析。重点看渠道效率；收入使用退款后的净收入。先只生成 HTML。”这只是回答形式示例，不是所有数据的默认口径。

**已熟悉时：直接分析。** 适合目标和口径已经清楚，希望尽快得到结果：

> 请用 sheet-to-report 直接分析这份 Excel，面向业务负责人做月度复盘。先检查字段和时间范围；遇到影响结论的口径不清时再向我确认。先生成 HTML，完成后告诉我如何继续制作可编辑 PPT。

两种方式都会询问真正影响结论的歧义。某些尚未完整验证的业务场景还会要求先确认方案，避免直接运行后得到误导性结论。

## 安装

### Claude Code Plugin

本仓库同时按单 Skill Claude Code Plugin 组织。根目录 `SKILL.md` 仍是唯一能力入口；`.claude-plugin/plugin.json` 只提供插件目录所需的元数据，因此 Claude 渠道不会复制或改写分析流程。

在 Claude Code 内依次运行下面两条命令，即可添加作者自托管市场并安装：

```text
/plugin marketplace add majichuan/sheet-to-report
/plugin install sheet-to-report@majichuan-skills
```

这是作者通过 GitHub 维护的安装入口，不代表已经通过 Anthropic 社区目录审核或收录。

如需校验或预览本地克隆：

```bash
claude plugin validate . --strict
claude --plugin-dir .
```

### Agent Skills 安装器

可用兼容 Agent Skills 的安装器直接从 GitHub 安装：

```bash
npx skills add https://github.com/majichuan/sheet-to-report --skill sheet-to-report
```

也可以在 [skills.sh 公开详情页](https://skills.sh/majichuan/sheet-to-report/sheet-to-report)查看安装入口和累计安装量。

也可以下载 GitHub Release 的 ZIP，或把仓库复制到所用 AI 工具支持的 Skill 目录。请保持 `SKILL.md`、`references/`、`scripts/` 和 `assets/` 的相对结构完整。

在 Skill 根目录检查基础环境：

```bash
python --version
python scripts/environment_check.py --target html
```

完整依赖和 PPT 说明见[安装与使用说明](INSTALL.md)。

## 生成之后怎么继续

HTML 完成后，AI 应提供可打开的报告入口并说明已完成、尚未验证的检查。需要用于会议汇报时，回复“生成 PPT”；无偏好时先推荐“清晰商务”，并在宿主支持渲染时直接展示真实 PPT 页面图片。无法渲染时应提前说明，让你按文字选择主题或明确授权使用推荐主题。

标准稿完成后，应同时提供完整稿阅读入口和独立可编辑 PPTX。需要继续优化视觉排版时，回复“制作美化版”，再使用 [SlideViber](https://github.com/tf71991/slideviber-skill)。SlideViber 需单独安装，标准稿会保留，图表编辑方式可能与标准版不同。

遇到环境、工作表、指标口径或平台模型错误时，先看[常见问题](FAQ.md)。HTML、标准 PPT 与美化版按阶段生成，后续阶段失败时应保留已经通过的产物。

## 本地试用合成数据

```bash
python scripts/generate_sample.py --output-dir generated-sample --write-xlsx
python scripts/sheet_to_report.py --inspect generated-sample/synthetic-business.xlsx
```

检查命令只负责生成样例和读取字段；正式结论、HTML 与 PPT 仍由 Agent 按 `SKILL.md` 的分析链路生成。

## 当前边界

- 当前版本以中文业务场景为主；英文产出尚未完成同等验收。
- 每次处理一张结构清晰的 Excel／CSV；多表联合、数据库接入和后台定时运行不属于 v0.2。
- AI 工具须能读取文件并运行本地 Python；PPT 另需 Node.js 与 `python-pptx`，详见安装说明。
- 不绑定任何案例，不套用模拟案例的结论；样例数据由脚本本地生成。
- 不用于医疗、投资、授信、人事评价等高风险决策。

提交问题前，请先删除或替换真实业务与个人数据。参与方式见 [CONTRIBUTING.md](CONTRIBUTING.md)，安全问题见 [SECURITY.md](SECURITY.md)。

## 隐私、条款与支持

- [隐私政策（英文）](PRIVACY.md)
- [使用条款（英文）](TERMS.md)
- [问题支持（英文）](SUPPORT.md)
- [安全问题报告](SECURITY.md)

## 许可

本项目采用 [MIT License](LICENSE)。第三方与合成数据说明见 [NOTICE.md](NOTICE.md)。
