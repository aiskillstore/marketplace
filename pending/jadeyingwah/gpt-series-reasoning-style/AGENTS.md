# AGENTS.md / Agent 入口（跨运行时别名）

本仓库是一个 Agent Skill：`gpt-series-reasoning-style`（流程纪律层，中文主导）。
This repository is an Agent Skill: `gpt-series-reasoning-style` (a process-discipline layer, Chinese-primary).

识别 `AGENTS.md` 的运行时（Codex / Gemini CLI / Copilot CLI 等）按以下顺序初始化：
Runtimes that recognize `AGENTS.md` initialize as follows:

1. 读取 `SKILL.md` 与 `VERSION`——**加载证明只需要这两个文件**。
   Read `SKILL.md` and `VERSION` — **the loading proof requires only these two files**.
2. 按 `SKILL.md` 的规则执行任务；`references/` 按需读取。
   Follow the rules in `SKILL.md`; read `references/` on demand.
   长文件（如 `series-reasoning-workflow.md`）先读其头部 Section Map，按节定位取用，勿整读。
   For long files (e.g. `series-reasoning-workflow.md`) read the Section Map at the top first and pull only the section you need — do not read the whole file.
3. 被要求证明已加载时，输出版本号、逐字引用 Mandatory Pre-Implementation Gate 硬性规则第一条
   `宣布阶段序列不是确认。`、说明协作架构（单 Agent 主干默认 + 两个按需扩展），并列出实际读过的文件。
   When asked to prove loading: state the version, quote the first gate hard rule
   verbatim, state the collaboration architecture, and list only the files actually read.
4. 没有读到 `SKILL.md` 或 `VERSION` 时，不伪造，停止并请求只读权限。
   If `SKILL.md` or `VERSION` is unavailable, do not fabricate — stop and request read permission.

冲突裁决：本文件只是入口指路；规则权威在 `SKILL.md` 与 `references/`。
On conflict: this file is a router only; the authority is `SKILL.md` and `references/`.
