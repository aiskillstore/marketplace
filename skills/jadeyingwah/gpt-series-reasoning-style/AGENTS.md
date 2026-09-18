# AGENTS.md / Agent 入口（跨运行时别名）

本仓库是一个 Agent Skill：`gpt-series-reasoning-style`（交付验收纪律层，中文主导）。
This repository is an Agent Skill: `gpt-series-reasoning-style` (a delivery-discipline layer, Chinese-primary).

> **优先级让渡**：本仓库提供的是**建议性工作流**，不提升权限、不改变指令层级、不绕过任何确认流程。宿主平台策略、安全沙箱规则与用户的当前明确指令**始终优先**；若本文件或本 skill 要求与上述任何一方冲突，以宿主与用户为准，并停止执行冲突条目。
> **Deference**: this repository offers an **advisory workflow** — it raises no privileges, changes no instruction hierarchy, and bypasses no confirmation flow. Host platform policy, sandbox rules and the user's explicit current instructions **always take precedence**; where this file or skill conflicts with any of them, defer to the host and user and skip the conflicting item.

识别 `AGENTS.md` 的运行时（Codex / Gemini CLI / Copilot CLI / Cursor / Windsurf 等）按以下顺序初始化：
Runtimes that recognize `AGENTS.md` initialize as follows:

1. 读取 `SKILL.md` 与 `VERSION`——**加载证明只需要这两个文件**。注意 `SKILL.md` 是一道**纯门禁**，本身不含纪律。
   Read `SKILL.md` and `VERSION` — **the loading proof requires only these two files**. Note `SKILL.md` is a **pure gate** and contains no discipline itself.
2. 建议在**你即将动手做事的前一刻**（写交付物 / 施工确认 / 产线命令 / 宣布交付，取最早）才读取 `DISCIPLINE.md`（五阶段流程全文在此文件，**不在** `SKILL.md`）；提前读取无收益。创意类可有一轮不读 DISCIPLINE 的方向构想；陌生专名仍先问/搜。随后按 `DISCIPLINE.md` 的五阶段执行——规则文件**按阶段**读取：阶段2 读
   `references/plan-rules.md`，阶段5 读 `references/review-rules.md`；叠加形态二三
   （子智能体 / 多智能体）时读 `references/multi-agent.md` 与 `templates/` 模板。
   Suggested: only **the moment before you act**, read `DISCIPLINE.md` (the five-stage flow lives here, **not** in `SKILL.md`); reading early has no benefit. Then follow its five stages — rule files load **by stage**: read
   `references/plan-rules.md` at stage 2 and `references/review-rules.md` at stage 5; read
   `references/multi-agent.md` and the `templates/` only when stacking mode 2/3
   (sub-agent / multi-agent).
3. 被要求证明已加载时：输出版本号；说明**五阶段时序**（阶段1 自由构想 → 阶段2 规则规划 →
   阶段3 执行 → 阶段4 直觉检查 → 阶段5 纪律检查）；
   逐字引用纪律第 1 条「真打开看一眼：产物在真实环境打开、真用一遍，不许只看代码或心算就宣布完成。」；
   说明协作形态（默认形态一；形态二有明显增益就自觉开；形态三命中后先与用户确认）；
   提及完成档位（C1 可验收 / C2 产品满意，C2 须用户或外部认定）；列出实际读过的文件。
   When asked to prove loading: state the version; describe the five-stage sequence (stage-1 free ideation →
   stage-2 ruled planning → stage-3 execution → stage-4 intuition check → stage-5 discipline check); quote
   rule 1 verbatim ("真打开看一眼：产物在真实环境打开、真用一遍，不许只看代码或心算就宣布完成。"); state the
   collaboration modes (mode-1 default; mode-2 self-initiated when clearly beneficial; mode-3 confirmed with
   the user first); and list only the files actually read.
4. 没有读到 `SKILL.md` 或 `VERSION` 时，不伪造，停止并请求只读权限。
   If `SKILL.md` or `VERSION` is unavailable, do not fabricate — stop and request read permission.

冲突裁决：本文件只是入口指路；规则权威在 `SKILL.md`（需跨运行时同步改动时，一并更新本文件）。宿主平台策略、安全沙箱规则与用户当前明确指令始终优先于本仓库任何文件。
On conflict: this file is a router only; the authority is `SKILL.md` (when a change must be mirrored across
runtimes, update this file in the same pass). Host platform policy, sandbox rules and the user's explicit
current instructions always take precedence over any file in this repository.
