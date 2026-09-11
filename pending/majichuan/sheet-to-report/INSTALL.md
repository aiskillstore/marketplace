# 安装与使用说明

> 按目标安装所需依赖：HTML、标准PPT、可选美化PPT。优先使用当前发布版本；不同AI工具的导入方式以对应平台说明为准。

只想快速判断问题时，先看[常见问题](FAQ.md)；本页保留完整安装与环境边界。

## 1. 先确认你的工具能执行什么

| 目标 | 所需条件 | 当前已知状态 |
| --- | --- | --- |
| HTML 分析简报 | 能读取 Skill 和 Excel/CSV、执行 Python 脚本、阅读证据并组织叙事的 AI 工具 | 已有本机多案例交付；未逐一验证其他 Agent |
| 新版标准 PPT | 上述条件，以及Node.js 18+与公开python-pptx 1.0+ | 当前整稿/主题小样及本机安装重放已验；不需要Codex私有库 |
| SlideViber 美化 PPT | Python、Node及本Skill构图代码，另需单独安装SlideViber和其公开依赖 | 私有变量耦合已移除，已有纯矢量整稿验证；浏览器回退及其他环境须实际核查 |

PowerPoint 或 WPS 用于查看、播放和编辑成品，不是当前计算分析入口的替代。AI 工具如果没有本地脚本执行能力，应说明能力缺口，不能承诺仅通过对话完成同一链路。

## 2. 基础安装

取得最终发布的 Skill 文件后，按所用 AI 工具支持的方式导入或放置，保持 `SKILL.md`、`references/`、`scripts/` 及运行资源的相对目录结构完整。不同工具的 Skill 目录可能不同，不使用作者电脑的绝对路径。

让 Agent 定位实际安装根目录，并在该目录执行：

```bash
python --version
python scripts/environment_check.py --target html
```

要求 Python 3.10 或更高。当前 `requirements.txt` 声明：

```text
pandas>=2.2
numpy>=1.26
openpyxl>=3.1
python-pptx>=1.0
```

缺依赖或版本不满足时，使用目标 Python 环境安装：

```bash
python -m pip install -r requirements.txt
```

**预检的实际范围：**按目标检查Python和公开依赖最低版本。HTML不要求PPT或Node；标准PPT检查Node和python-pptx；SlideViber另检查其目录和声明模块。`passed`不代表字体、浏览器启动、实际视觉或原生编辑已验。

**版本记录与更新：**普通安装不要求Git。每次初扫保留既定文件清单的指纹；Git只补充开发版本，无法读取时明确记录未知和原因。升级Skill后不要续算旧运行或手改快照指纹，应使用新运行目录；已完成模型仍可按既有来源合同继续制作PPT。独立无Git副本的最小入口验证已通过，但不等同于全新机器pip安装或所有Agent验收。

## 3. 开始分析

向 Agent 提供文件和目标，例如：

> 请使用 sheet-to-report 分析这份 Excel，面向业务负责人做阶段复盘。先检查字段与数据范围，确认影响结论的口径，再生成有图表、判断和下一步建议的 HTML；无法回答的部分请说明原因。

必要时，Agent先执行字段检查：

```bash
python scripts/sheet_to_report.py --inspect "你的数据.xlsx"
```

随后由 Agent 按 `references/html-analysis.md` 完成初扫、阅读证据、必要补查、故事编排、校验和最终生成。用户无需手写 JSON。仅执行旧的 `--request ... --output ...` 命令，不代表完成新版 AI 驱动分析。

有歧义的指标定义、分母或字段需要确认；“直接分析”不意味着可以猜测。内容运营、项目运营画像当前仍需“确认分析计划”。每次生成使用新输出目录，保留已有文件。

## 4. 继续生成 PPT

先确认演示环境，再按 `references/chapter-presentation.md` 使用新版章节到演示投影。不要将新版 HTML 模型直接交给旧 `build_pptx.py`。

先执行与本次输出目标一致的预检：

```bash
python scripts/environment_check.py --target standard
python scripts/environment_check.py --target slideviber --slideviber-dir "SlideViber目录"
```

Node不在PATH时给预检传`--node "Node可执行文件"`。作者命令也使用该实际Node程序运行。`RUNTIME_PYTHON`可指定Python解释器，否则Windows使用python、其他系统使用python3。标准稿与标准主题小样均由公开python-pptx写入，不再要求`RUNTIME_NODE_MODULES`或`PRESENTATIONS_SKILL_DIR`。

完整稿使用冻结模型、已确认选择和故事投影，作者自动完成来源/数值/几何校验；用户不需要安装Codex插件或复制私有缓存。随后仍须由实际PPT渲染器检查整稿，保留有问题的候选并修作者，不手修最终文件。环境缺失时具体报告缺哪项，已完成HTML保留。

主题交互遵循本 Skill 的统一规则：

- 已明确指定或已确认沿用的主题优先。
- 未指定且未授权代选：提供候选方向和每方向真实封面＋图表两页小样，用户选择后生成整稿。
- 明确说“你决定、直接生成”，且无已有偏好：使用清晰商务。
- 美化版继承所选方向。当前通用章节整稿支持清晰商务、沉稳管理和温暖亲和所对应的 `clean/corporate/warm` 配置；`editorial` 整稿未验证并拒绝执行，不能把四个方向的小样能力宣传成四种整稿全部通过。

## 5. 可选 SlideViber

标准PPT完成后，Agent会告知可继续制作美化版。是否安装、是否继续由用户选择；不安装仍可交付HTML和标准PPT，已拒绝不重复询问。通过[SlideViber项目说明](https://github.com/tf71991/slideviber-skill)了解安装及许可，本Skill不捆绑其源码，也不自动安装。

用户选择继续时，沿用同一分析内容与已确认主题，重新设计演示构图，另存美化PPT并做完整内容、数值及溢出校验；不得覆盖标准稿。

SlideViber 单独安装，读取其当前版本说明与许可证。当前本机版本的依赖清单包括 `python-pptx`、`defusedxml`、`playwright` 和 `lxml`，复杂 SVG 元素的图片回退还需 Chromium。使用其版本自带的依赖清单，不把以下准备误认为完整跨环境安装已验证：

```bash
python -m pip install -r "SlideViber目录/requirements.txt"
python -m playwright install chromium
```

使用 SlideViber 的 `scripts/build.py` 导出前，仍需完成本 Skill 的独立演示构图和来源校验。美化不能删正文、数字或限制条件。不能转换的复杂元素可能变成图片；有严格原生编辑要求时应先说明边界，不静默降级。

## 6. 遇到问题时

| 情况 | 应如何处理 |
| --- | --- |
| Python 找不到／包缺失 | 核对实际解释器与其安装环境，不要求用户修改业务数据来绕过环境问题 |
| HTML预检通过，PPT仍失败 | 运行对应standard/slideviber预检，核对实际Python与Node、字体及渲染工具，不能把HTML通过当作PPT已验 |
| 运行期间提示执行版本改变 | 保留旧目录；确认是否升级了Skill，不手改快照哈希或强行续算；需要重新分析时使用新目录 |
| 语义不清或证据不够 | 询问影响结论的问题，或明确缩小结论范围；不编造数据 |
| 当前图型或容量不能完整呈现 | 合法重排、拆页或说明能力缺口，不截字删信息 |
| 美化版本缺少内容或不一致 | 保留标准版和失败记录，修正生成环节后重新导出，不手改最终文件掩盖问题 |
| 办公软件中字体替换或编辑异常 | 记录软件版本及受影响页面；检查对应字体或对象，不要求重跑全部案例 |

已完成多类模拟案例与代表性PPT的WPS检查；不等同于所有对象、所有软件版本或所有AI宿主均已验收。输入用于描述与证据受控的诊断，不适用于医疗、投资、人事评价或授信等高风险决策；脚本不调用外部模型API，但宿主AI平台可能读取用户文件，使用前应了解其数据处理政策。
