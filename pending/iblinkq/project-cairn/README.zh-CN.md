[English](README.md) | [中文](README.zh-CN.md)

# Project Cairn

**把做过的事情，沉淀成可复用的知识。**

[打开交互说明页面，了解 Skill 详情](https://iblinkq.github.io/project-cairn/)

[![Project Cairn 中文交互式可视化概览](docs/assets/screenshots/project-cairn-overview-zh-CN.png)](https://iblinkq.github.io/project-cairn/)

## 这些情况，你是不是也遇到过？

- 同一个坑，换个项目又踩一遍。
- 会话一断、Agent 一换，背景和规则又得从头解释。
- 计划、进度和结论散落各处，AI 在新旧方案之间反复横跳。
- 明明解决过，真正需要时却只剩一堆翻不完的聊天记录。

## Project Cairn 会做什么

Project Cairn 是一个 Agent Skill。它让 Agent 在正常推进项目时，把已经验证的踩坑经验、关键决策、探索成果和灵感洞见留在项目里。真正值得跨项目复用的内容，再由你确认后进入长期知识库。

![Project Cairn 与 AI Agent、知识库及相关生态的关系图](docs/assets/screenshots/project-cairn-ecosystem-zh-CN.png)

它提供一套稳定的文档分工和流转规则：

- `AGENTS.md` 保存 Agent 每次进入项目都要遵守的规则。
- `cairn/LOG.md` 记录事情发生的顺序，只留摘要和指针。
- `cairn/ROADMAP.md` 保存总体目标、计划和当前进度。
- `cairn/<主题>.md` 保存某个主题目前成立的结论。
- `cairn/Cited.md` 记录真正影响过当前项目的外部知识，只挂指针，不复制正文。

Cairn 是旅人留下的路标石堆。这个名字想表达的也很简单：前一个项目走通过的路，应该让后一个项目看得见。

## 适合谁

如果你同时推进多个 AI 协作项目，或者会在 Claude Code、Codex、OpenClaw、WorkBuddy 等兼容 Skill 的 Agent 之间切换，Project Cairn 可以帮你保留项目共同认可的结论，而不是把它们留在某个 Agent 的私有记忆或一段旧对话里。

## 安装

**Claude Code**，用户级安装：

```bash
git clone https://github.com/iBlinkQ/project-cairn.git ~/.claude/skills/project-cairn
```

**Codex**，用户级 direct skill 路径：

```bash
git clone https://github.com/iBlinkQ/project-cairn.git ~/.agents/skills/project-cairn
```

**WorkBuddy**，通过本地 Skill 包安装：

1. 下载 [Project Cairn ZIP](https://github.com/iBlinkQ/project-cairn/archive/refs/heads/main.zip)。
2. 在 WorkBuddy 侧边栏打开“技能”，点击“添加技能”，再选择“上传技能”。
3. 选择下载的 ZIP 文件。导入完成后，WorkBuddy 会自动配置，无需手动复制目录。

操作入口见 [WorkBuddy 官方 Skill 文档](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Skills-Market)。

其他兼容 Skill 的 Agent，把仓库 clone 到该 Agent 读取 Skill 的目录即可。安装后，`SKILL.md` 应直接位于 `project-cairn/` 根目录，不要再多嵌套一层。

前置依赖是 `git`。`scripts/*.sh` 需要 `bash`，已在 macOS 和 Linux 上验证，Windows 需要 WSL 或 Git Bash；`scripts/*.py` 需要 Python 3。目前没有包管理器版本。

## 三步开始使用

1. 在项目里对 Agent 说“初始化 Project Cairn”。它会询问项目定位、git 策略和历史迁移方式，再生成项目规则与配置。初始化时可以暂不连接知识库，等第一次真正需要毕业知识时再配置。
2. 照常推进项目。Agent 根据 `AGENTS.md`，在正常协作回合里维护进展和当前结论，不需要单独运行一个记录服务。
3. 当某条经验对其他项目也有用时，让 Agent 提出毕业候选。你确认范围后，它才会写入知识库。以后遇到相近问题，新项目先检索，再把真正用到的知识指针记进 `cairn/Cited.md`。

## 两侧如何配合

Project Cairn 把信息分在两侧，而不是把所有内容塞进一个不断膨胀的文件。

| 两侧 | 保存什么 | 典型载体 | 什么时候读取 |
|---|---|---|---|
| **项目侧** | 当前项目的规则、进展、结论和案例 | 根目录 `AGENTS.md` 与 `cairn/` | 进入项目和推进工作时 |
| **知识库侧** | 已经抽象完成、能跨项目复用的知识 | Obsidian、Notion、飞书 / Lark wiki | 新工作需要旧经验时 |

项目侧先把事实和结论留稳。知识具备复用价值后，再经过人工确认进入知识库侧。两侧承担不同生命周期，所以项目里的局部结论和跨项目的通用知识不会互相覆盖。

## 一条经验如何走到下一个项目

以这个消息机器人问题为例：

1. 项目启动时，Cairn 把规则和配置写入项目。
2. Agent 正常推进排查，并把关键进展记入 `LOG.md`。
3. 问题解决并验证后，当前结论写入对应的主题文档。
4. 如果 spec、plan、评审或复盘里还有稳定结论，Agent 只提取结论，不搬运过程文档。
5. Agent 判断这条经验可能跨项目复用，向你提出毕业候选。
6. 你确认后，Agent 去除项目偶然细节，补齐背景、适用条件和来源，再写入知识库并更新索引。
7. 新项目遇到相近问题时，先检索知识库。只有真正影响了产出的笔记，才在 `Cited.md` 留下指针。

交互式页面把完整过程展开为 T0 到 T8 九个步骤，包括路线图维护、定期审查和再次毕业：[查看完整流程](https://iblinkq.github.io/project-cairn/)。

## 它会留下什么

Project Cairn 不预建一堆空模板。除了初始化所需的核心文件，其他文档都等真实信号出现时再创建。

| 文件 | 负责的事情 |
|---|---|
| `AGENTS.md` | 规则与导航 |
| `.cairn/config.yaml` | 机器可读配置 |
| `cairn/LOG.md` | 倒序时序记录 |
| `cairn/ROADMAP.md` | 总体目标、计划和当前进度 |
| `cairn/<主题>.md` | 按主题维护的当前真相 |
| `cairn/Reference/` | 项目自己持有的外部原始材料 |
| `cairn/Cited.md` | 实际使用过的知识库指针 |

被代码或工作流直接消费的 schema、配置和工程契约仍留在代码树里。Cairn 保存的是关于它们的知识，比如为什么这样设计、比较过哪些方案、实施时踩过什么坑。

主题文档使用 Markdown 与 YAML frontmatter，至少包含一个 `type` 字段，对齐 Google [Open Knowledge Format](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing) 的最小约定。这不等于完整实现 OKF bundle。

每篇毕业笔记还会记录来源和参与者，包括 `graduated_from`、`contributors`、`graduated_by` 与 `authoring_mode`，方便回到形成结论的项目和材料。

## 自动化边界

- Project Cairn 不在后台监听，也不会在会话结束后自行运行。
- 日常记录发生在你和 Agent 正常协作的回合中，由项目里的 `AGENTS.md` 规则驱动。
- Agent 可以提出知识毕业候选，但没有你的确认，不会写入长期知识库。
- 初始化时可以暂不连接 Obsidian、Notion 或飞书 / Lark，等第一次真正需要毕业知识时再配置。
- 审查负责发现矛盾、过期结论和遗漏，不会替你擅自修改重要判断。

毕业的写入方向是项目侧到知识库侧。新项目复用知识时先检索，再在 `Cited.md` 留指针，不复制知识库正文。这是显式消费，不是两个存储之间的后台同步。

## 已验证的知识库

Project Cairn 已验证三种毕业目标：

- **Obsidian**：写入 vault 相对路径，以 `INDEX.md` 维护入口，用 WikiLink 连接笔记。
- **Notion**：写入数据库，数据库同时承担容器和索引，属性列承接结构化元数据。
- **飞书 / Lark wiki**：写入知识空间的节点树，并保留可回查的文档链接。

每种 provider 都遵守 `references/provider-interface.md` 中的行为契约，同时保留平台自己的链接和索引方式。各 provider 的具体执行路径位于 `references/graduation/`。真正写入前，可以先运行对应的只读检查：

```text
scripts/obsidian-preflight.sh
scripts/notion-preflight.sh
scripts/lark-preflight.sh
```

## 深入了解

Project Cairn 不是用来替代所有相关工具的：

| 工具或方法 | 它主要解决什么 | 与 Cairn 的关系 |
|---|---|---|
| [LLM Wiki](https://github.com/karpathy) | 把读过的原始资料整理成 wiki | LLM Wiki 偏资料知识化，Cairn 偏项目经验知识化 |
| [Open Knowledge Format](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing) | 让知识文件可以被人和机器交换 | OKF 是格式方向，Cairn 管形成、维护、毕业和复用 |
| Agent Memory | 延续某个 Agent 的偏好和工作上下文 | Memory 管 Agent 的连续性，Cairn 管项目知识的连续性 |
| [superpowers](https://github.com/obra/superpowers) | 用 spec、plan、测试和评审把工作做稳 | superpowers 管过程，Cairn 从过程中留下稳定结论 |

一句话区分：Agent 记住了，不等于项目学会了。

## 文档地图

| Reference | 用途 |
|---|---|
| `references/init.md` | 初始化或补建 Project Cairn |
| `references/maintenance.md` | 维护 `LOG.md`、`ROADMAP.md` 和主题文档 |
| `references/graduation.md` | 判断、蒸馏并写入可复用知识 |
| `references/graduation/` | 每个 provider 一份的毕业执行路径（Lark wiki、Notion、Obsidian） |
| `references/provider-interface.md` | provider adapter 的行为契约 |
| `references/consume.md` | 检索、使用并引用外部知识 |
| `references/audit.md` | 找出漂移、矛盾和缺失记录 |
| `references/upgrade.md` | 检查并升级已初始化项目的规范版本 |
| `references/frontmatter.md` | 项目笔记与知识库笔记的字段规范 |
| `references/branch-closure.md` | 关闭探索分支前收拢知识 |
| `references/zh-glossary.md` | 中文项目文档的固定术语对照 |

## 贡献

欢迎 Issue 和 PR。Project Cairn 以文档规则为主，贡献通常会落在 `SKILL.md`、`references/*.md`、`assets/templates/*` 或 `scripts/`。如果改动了行为，请在 PR 里说明原因和影响范围。

## License

[MIT](LICENSE)
