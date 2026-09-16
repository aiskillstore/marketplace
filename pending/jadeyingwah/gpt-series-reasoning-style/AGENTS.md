# AGENTS.md / Agent 入口（跨运行时别名）

本仓库是一个 Agent Skill：`gpt-series-reasoning-style`（交付验收纪律层，中文主导）。
This repository is an Agent Skill: `gpt-series-reasoning-style` (a delivery-discipline layer, Chinese-primary).

识别 `AGENTS.md` 的运行时（Codex / Gemini CLI / Copilot CLI 等）按以下顺序初始化：
Runtimes that recognize `AGENTS.md` initialize as follows:

1. 读取 `SKILL.md` 与 `VERSION`——**加载证明只需要这两个文件**。
   Read `SKILL.md` and `VERSION` — **the loading proof requires only these two files**.
2. 按 `SKILL.md` 的**五阶段流程**执行任务；规则文件**按阶段**读取——阶段2 读
   `references/plan-rules.md`，阶段5 读 `references/review-rules.md`；叠加形态二三
   （子智能体 / 多智能体）时读 `references/multi-agent.md` 与模板。
   Follow the five-stage flow in `SKILL.md`; rule files load **by stage** — read
   `references/plan-rules.md` at stage 2 and `references/review-rules.md` at stage 5;
   read `references/multi-agent.md` and the templates only when stacking mode 2/3
   (sub-agent / multi-agent).
3. 被要求证明已加载时：输出版本号；说明**五阶段时序**（阶段1 自由构想 → 阶段2 规则规划 →
   阶段3 执行 → 阶段4 直觉检查 → 阶段5 纪律检查）；
   逐字引用纪律第 1 条「真打开看一眼：产物在真实环境打开、真用一遍，不许只看代码或心算就宣布完成。」；
   说明协作形态（默认形态一；形态二有明显增益就自觉开；形态三命中后先与用户确认）；列出实际读过的文件。
   When asked to prove loading: state the version; describe the five-stage sequence (stage-1 free ideation →
   stage-2 ruled planning → stage-3 execution → stage-4 intuition check → stage-5 discipline check); quote
   rule 1 verbatim ("真打开看一眼：产物在真实环境打开、真用一遍，不许只看代码或心算就宣布完成。"); state the
   collaboration modes (mode-1 default; mode-2 self-initiated when clearly beneficial; mode-3 confirmed with
   the user first); and list only the files actually read.
4. 没有读到 `SKILL.md` 或 `VERSION` 时，不伪造，停止并请求只读权限。
   If `SKILL.md` or `VERSION` is unavailable, do not fabricate — stop and request read permission.

冲突裁决：本文件只是入口指路；规则权威在 `SKILL.md`（需跨运行时同步改动时，一并更新本文件）。
On conflict: this file is a router only; the authority is `SKILL.md` (when a change must be mirrored across
runtimes, update this file in the same pass).
