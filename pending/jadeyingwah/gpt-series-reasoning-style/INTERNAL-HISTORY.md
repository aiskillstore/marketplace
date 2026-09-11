# Internal Release History / 内部版本历史

公开发布线见 [CHANGELOG.md](CHANGELOG.md)。本文件归档**发布前的内部迭代**（`0.1.x`–`3.3.x`，含重定位前那条 `2.4.0`→`3.2.2` 长线及分支末端的 `3.3.0` 实验记录）以及更早的旧公开线，一律**按史实原样保留、仅用于追溯**；对外版本从当前 `1.1.0` 起算，不在此文件计数。

The public release line lives in CHANGELOG.md. This file archives the pre-publication internal iterations (`0.1.x`–`3.x`, incl. the pre-rebase `2.4.0`→`3.2.2` line) and the earlier public line, preserved verbatim for traceability. Public releases number from `1.1.0` and are not counted here.

---

## 3.2.2 - 2026-09-08

External review pass (full-file read) — three fixes, two explicitly rejected as over-optimization:

- **Off-by-one fixed**: task package is **23 fields** (verified against the authoritative list in multi-agent-closure-rules.md), not 24. Corrected 3 spots in agent-modes.md + the SKILL.md description; the authoritative list is now annotated "(23 fields — the authoritative count; do not cite 24)".
- **Template-not-literal clarification** added at the point of use (workflow gate template): the template is a field checklist — render naturally, never wrap 角色身份确认/协调通道确认 in code blocks (was only stated in self-test/README before).
- **Maintainer Notes added to README**: the six sync surfaces for gate fields and hard rules (from the three rule-desync field tests) — a rule change must sync all of them in one version.
- Rejected as over-optimization (documented here so they are not re-proposed): ① an extra "task ≤ single-window small change → light tier" shortcut — the light tier and mode self-selection already cover this, and 3.2.0 just tightened this exact boundary the other way; ② splitting README into two audiences and slimming self-test/CHANGELOG — runtime only loads SKILL.md + VERSION, references are on-demand; repo weight is not a runtime cost.

## 3.2.1 - 2026-09-08

The third probe exposed a **rule self-contradiction** (not a bypass): the tested model correctly cited real skill text to justify defaulting to the backbone instead of proposing Subagent mode. Three conflicting sources, all authored during 3.1.0-3.2.0, fixed:

1. **SKILL.md leftover**: "用户不选形态时默认主干" — a pre-3.1.0 default rule that survived the mode self-selection rewrite. Replaced with the self-selection wording (AI selects by task facts, declares in the gate, user-named wins).
2. **Misleading exclusion wording** (SKILL.md + workflow): the light-tier exclusion said "形态须由用户指定——AI 自行选定的不算指令已指定". That sentence was meant to explain why new products skip the light tier (bypassing the gate), but as written it generalized into "the user must always specify the form" — the exact opposite of self-selection. Rewritten: new products default to medium tier because they involve multi-file and product decisions and must not bypass the gate; the form choice is proposed by the AI in the gate and ruled by the user.
3. **Cost judgment made explicit**: when a parallelism signal ("同时/一起做") is present, the benefit-vs-briefing-cost judgment must be written into the form-selection reason — hitting the signal but choosing not to parallelize requires a stated cost basis, never a silent default.

- Synchronized version references to 3.2.1.

## 3.2.0 - 2026-09-08

Second field-test fix from the same subagent probe: the model applied the **light tier** to "同时做三个互不相关的小工具…放在桌面" — every light-tier adjective was literally satisfied (specific, small, reversible, no side effects), so it skipped the gate entirely and built all three serially, never declaring a mode choice.

- Root cause layered on 3.1.2: the 3.1.2 fix added 形态选择 to the full-flow gate template, but the **light-tier path bypasses the whole template**, and the tier boundary was written as adjectives (specific / small / reversible / no side effects) which a three-deliverable task can satisfy by enumeration. SKILL.md already said 全新产物默认中档, but nothing cross-locked the light-tier clause to it, and "the AI chose the form itself" was silently counted as "the instruction fully specified the form".
- Fixed: explicit **light-tier exclusions** in both `SKILL.md` and `references/sol-reasoning-workflow.md`: ① new-from-scratch products default to medium tier, and the form must be specified by the USER (an AI-chosen form never counts as "instruction-specified"); ② multi-deliverable tasks (≥2 independent products); ③ parallelism signals (同时/并行/一起做 → full gate with the 形态选择 field, and per self-selection this should propose the Subagent enhancement).
- Added self-test Test 56 third case: the exact probe prompt, expected to fail the light tier and run the full gate with a declared form choice.
- Lesson added: tier boundaries written as adjectives get gamed by enumeration — boundaries need explicit exclusion lists.
- Synchronized version references to 3.2.0.

## 3.1.2 - 2026-09-08

Field-test fix from the subagent-mode probe (three desktop tools). The model ran an otherwise excellent gate — risk tier, resource survey, one focused question, honest UNVERIFIED, node syntax evidence — but **silently skipped the mode choice**: the user's "同时做三个互不相关的小工具" is a textbook Subagent signal, and the gate output contained no form selection or de-escalation reason at all.

- **Root cause: rule–template desync.** The 3.1.0 self-selection rule lived only in `references/agent-modes.md` (loaded on demand); the 【实现前确认】 template in `references/sol-reasoning-workflow.md` and the field list in `SKILL.md` had no matching field. The model completed every templated field and skipped the undeclared one. (Contrast: the 2.5.0 risk-tier rule was added to both rule and template together, and every field test since has shown the tier line.)
- Fixed: gate template and SKILL.md field list now carry **形态选择：单 Agent 主干 / 子 Agent 增强 / 指挥官扩展 — 一行理由** (light tier exempt; "同时/并行/多任务" flagged as a Subagent signal that must be explicitly evaluated).
- Lesson added: a rule added to a reference file does not change behavior unless the gate template and field list carry it — rule and template must ship in the same version.
- Synchronized version references to 3.1.2.

## 3.1.1 - 2026-09-08

- Consistency pass after 3.1.0: updated self-test Test 21, whose expectation ("treats this as Default Mode unless the user explicitly chooses") contradicted the new mode self-selection — rewritten to expect task-fact-based self-selection with a declared one-line reason, plus "a user-named form wins subject to capability gates". Also aligned the Single-Agent description in `references/agent-modes.md` (both languages).
- Synchronized version references to 3.1.1.

## 3.1.0 - 2026-09-08

**Mode self-selection**: the AI now chooses its own form based on task facts, instead of waiting for the user to name one.

- Decision order (first hit wins): light tier → Commander extension (user signals cross-AI / capability gap with another AI available / explicit independent-audit request) → Subagent enhancement (tools present + genuinely independent parallel branches + benefit outweighs briefing cost + no external model needed) → otherwise Single-Agent backbone.
- The self-selection is a **recommendation declared at the gate with a one-line reason** — the user can override with one sentence; a user-named form always wins (except when the capability gate fails → fall back to Single-Agent and mark `UNVERIFIED`).
- Mode choice ≠ implementation authorization: every form still runs its own confirmations and gates.
- Escalation requires a task-based reason; de-escalation does not — no form upgrading just to showcase multi-agent capability.
- Updated `references/agent-modes.md` (new Mode Self-Selection section) and `SKILL.md`.
- Added self-tests 65-67 (capability-gap proposes Commander without being asked; simple task stays on the backbone; independent parallel branches propose Subagent). Self-test count: 64 → 67.
- Synchronized version references to 3.1.0.

## 3.0.1 - 2026-09-08

- Absorbed the one new lesson from the v3.0.0 field test (T-POMODORO-01, scored 16/16): **a DOM state change is not rendered evidence**. The executor's probe saw `flash` in classList and reported "border turned tomato-red + flash animation" as passing, while the CSS selector (`.card.flash`) never matched the actual element (`class="app"`) — the effect had never rendered. The commander caught it only by reading the computed style during independent re-verification. Visual acceptance must verify the rendered result (computed style or screenshot pixels), not the DOM state.
- Added to lessons + extended self-test Test 54 with the rendered-result expectation. Self-tests remain 64.
- Field-test validation summary for 3.0.0: risk tier explicit ✓, governance under project root incl. per-member identity file ✓, evidence landing path + existence check ✓, no model interrogation ✓ — all four post-2.5.0 rules observed working in one run for the first time.

## 3.0.0 - 2026-09-08

Breaking rename and registry restructure, per user decision:

1. **Renamed**: `gpt-5-6-sol-multi-agent-style` / "GPT-5.6 Sol Multi-Agent Style" → `gpt-series-reasoning-style` / "GPT系列推理风格（GPT-Series Reasoning Style）". The old name pinned a specific model version; the series name survives model churn. Repository directory renamed accordingly; all in-repo references updated.
2. **Never ask for underlying models**: the skill no longer asks the user what underlying model any AI member uses. A model is recorded only when the user volunteers it or it is publicly evident — optional reference metadata that never blocks a registry record or task package.
3. **Per-member identity files**: the project registry layout is now a README index plus **one standalone identity markdown file per AI member** (`<项目根>/docs/agents/<member>.md`), carrying role, responsibilities, platform/channel, trust tier, status, and current task.
4. **Read-before-dispatch**: the commander reads a member's identity file before the first relay and adapts communication and task-package framing to it.
5. **Recipients read their own file first**: every activation prompt instructs the recipient to read its own identity file and declare its identity before executing the task package.

- Updated `identities/deputy-commander.md`, `references/identity-library.md`, `references/multi-agent-closure-rules.md`.
- Synchronized version references to 3.0.0.

- 破坏性重命名与登记结构重构（用户决定）：
  1. **改名**：`gpt-5-6-sol-multi-agent-style` / "GPT-5.6 Sol Multi-Agent Style" → `gpt-series-reasoning-style` / "GPT系列推理风格（GPT-Series Reasoning Style）"。旧名锁死具体型号；系列名可穿越型号更替。仓库目录同步更名，库内引用全部更新。
  2. **从不询问底层模型**：skill 不再询问用户任何 AI 成员的底层大模型。仅在用户主动告知或公开可得时记录——可选参考元数据，绝不阻塞登记记录或任务包。
  3. **每成员一个身份文件**：项目登记目录结构改为 README 索引 + **每个 AI 成员独立的身份 md**（`<项目根>/docs/agents/<成员>.md`），承载角色、职责、平台/通道、信任层级、状态与当前任务。
  4. **派发前先读**：指挥官在首次传话前读取该成员的身份文件，并据此适配沟通方式与任务包表述。
  5. **接收方先读自己的文件**：每份启动提示词都指示接收方先读取自己的身份文件、声明身份后再执行任务包。
- 更新 `identities/deputy-commander.md`、`references/identity-library.md`、`references/multi-agent-closure-rules.md`。
- 版本号同步到 3.0.0。

## 2.9.1 - 2026-09-08

- De-branded all positive examples in the normative files (agent-modes / identity-library / multi-agent-closure-rules) and the self-test expectations: recipient examples now use neutral, platform-class names (`IDE 内置 AI 窗口执行者` / `网页对话窗口执行者`) instead of `TRAE 主执行者` / `智谱对话窗口执行者` / `豆包窗口执行者`. Rationale: the tested commander offered `TRAE 窗口` / `Codex CLI` as recipient options because it learned them from the skill's own examples — examples teach behavior, so they must not hard-code a specific toolchain.
- Kept intentionally: brand names inside self-test **prompts** (adversarial stimuli testing that brand-only recipients are rejected) and the rule text describing that rejection.
- Verified: zero brand hits in the three normative rule files; no private-project-name leakage anywhere outside CHANGELOG history.
- Synchronized version references to 2.9.1.

## 2.9.0 - 2026-09-08

Extracted from newly organized commander-session transcripts and from the v2.8.1 live test. Five rules added, all evidence-backed:

1. **Existing-artifact conflict: stop and report first** (from the 9-04 live test, where the commander found an existing app and froze all writes before reporting). Freeze → report against each hard requirement → offer dispositions → wait. "The instruction said create new" is never overwrite authorization; an unrequested backup is still unauthorized action.
2. **Command succession** (from a real project event: the deputy commander dispatched the R3 rework package "with user authorization while the commander was temporarily unreachable"). Takeover requires explicit user authorization; declare scope/duration/taken-over tasks; record in the ledger; hand back with a status handover; never two live commands at once; succession moves command only, not other roles' DRI.
3. **Change management**: impact analysis → frozen scope → regression scope with re-verification → whole-plan re-evaluation → surface conflicts with approved decisions.
4. **Registry scoping clarified**: the identity registry belongs to the project being worked on; reusing another project's identity directory is not an acceptable option even if the user proposes it — offering it is itself a governance defect.
5. **Verification conveniences are scope**: debug switches, shortened-duration test modes, extra buttons, and mock toggles must be listed in the gate as explicit user decisions, not adopted silently as "fixed decisions".

- Added self-tests 62-64 (existing-artifact conflict, command succession, change management + verification conveniences). Self-test count: 61 → 64.
- Also updated `identities/deputy-commander.md` with the succession process and anti-patterns (it previously never mentioned takeover at all).
- Synchronized version references to 2.9.0.

- 从新整理的指挥官会话实录与 v2.8.1 实测中提炼，五条规则全部有实证支撑：
  1. **既有产物冲突先报告**（9-04 实测中总指挥发现既有应用后冻结一切写动作再报告）：冻结 → 逐条比对报告 → 给处置选项 → 等裁决；"指令说新建"绝不构成覆盖授权，未经请求的备份同样越权。
  2. **指挥权接管**（项目真实事件：副总指挥"经用户授权、总指挥暂时失联期间"派发 R3 退回任务包）：接管须用户明确授权；声明范围/期限/接手清单；入台账；恢复后交回并交接；不得两个指挥权并存；接管只转移指挥权，不转移其他角色 DRI。
  3. **变更管理**：影响分析 → 冻结范围 → 回归范围并复验 → 整体重评 → 挑明与既有决策的冲突。
  4. **登记目录边界澄清**：身份登记属于当前项目，复用其他项目的身份目录不可接受（即使用户提出），把它列为选项本身就是治理缺陷。
  5. **验收便利设施属范围变更**：调试开关、缩短时长测试模式、额外按钮、mock 开关必须在门禁中作为显式决策列出，不得静默当作"固定决策"采纳。
- 新增自测 62-64，自测题数 61 → 64；补充 `identities/deputy-commander.md` 的接管流程（此前该文件完全未提接管）。
- 版本号同步到 2.9.0。

## 2.8.1 - 2026-09-07

- Static self-test pass over all 61 checks found one internal contradiction and two stale paths; all three are fixed.
  - **P0 contradiction:** Test 48 ("Model Names Must Use Official Identifiers") still required an official model identifier and blocked task-package finalization until the model/session was precise — directly contradicting the 2.6.0 model decoupling. A model behaving per 2.8.0 would fail this check, and the check itself taught the wrong behavior. Rewritten as "Recipient Must Be Concrete, Model Is Optional": recipient = role + platform/window; model = optional reference metadata, never blocking.
  - Test 46: registry path is now project-root scoped (`<项目根>/docs/agents/`), not a bare `docs/agents/`.
  - Test 59: dispatch ledger path aligned to `<项目根>/docs/agents/dispatch-ledger.md`.
- Also verified and cleared: the suspected conflict between 2.7.0 ("create the project root after gate approval") and the gate rule ("no directories before user confirmation") is **not** a conflict — gate approval *is* the user confirmation, so no rule change is needed.
- Synchronized version references to 2.8.1.

- 静态自测（61 题逐条扮演核验）发现一处内部矛盾与两处过期路径，均已修复。
  - **P0 矛盾**：Test 48 仍要求官方模型标识、并以"模型不精确就不许定稿任务包"为阻断条件，与 2.6.0 的模型解耦正面冲突——按 2.8.0 行为的模型会考不过这题，且该题本身会教错行为。已改写为"接收方必须具体、模型可选"。
  - Test 46：身份目录路径改为以项目根为基准。
  - Test 59：台账路径对齐项目根。
  - 另核验并排除一处疑似冲突：2.7.0"门禁获批后创建项目根"与"确认前不建目录"并不矛盾（门禁批准即用户确认），无需改规则。
- 版本号同步到 2.8.1。

## 2.8.0 - 2026-09-04

- Evidence landing path and existence check (from the live relay test's second finding): the executor claimed four screenshots in `flashcard-evidence/` that did not exist on disk — the commander's consistency check caught it, but the root cause was upstream: no designated landing path for evidence.
  - `Evidence required` must name a concrete landing path under the project root (e.g., `<项目根>/evidence/`); the commander creates the evidence directory in the project skeleton or explicitly assigns its creation to the executor in the package Scope.
  - Answer Handling step 1 (consistency check) now includes an existence check: claimed evidence files listed but missing on disk void the completion claim.
  - Evidence Handoff: existence before content — list the directory first.
- Added the matching lesson failure pattern and a self-test 60 expectation; synchronized version references to 2.8.0.

- 证据落盘路径与存在性检查（来自转交实测的第二个发现）：执行者声称 `flashcard-evidence/` 里有四张截图，磁盘上并不存在——总指挥的自洽检查拦住了它，但根因在上游：证据没有预先指定的落盘位置。
  - `Evidence required` 必须给出项目根之下的具体落盘路径（如 `<项目根>/evidence/`）；总指挥建项目骨架时一并建证据目录，或在任务包 Scope 里显式把创建指派给执行者。
  - 回答接手协议第 1 步（自洽检查）加入存在性检查：声称的证据文件列了名但盘上没有，"已完成"声明整体作废。
  - 证据交接：先存在后内容——先列目录再审内容。
- 新增对应 lessons 失败模式与自测 60 断言；版本号同步到 2.8.0。

## 2.7.0 - 2026-09-04

- Governance artifacts are now project-scoped (user-reported defect from the live relay test: the commander wrote the registry and plan into its own workspace instead of the project folder): the identity registry `<项目根>/docs/agents/`, the Mode 3 plan `<项目根>/docs/plans/`, and the dispatch ledger `<项目根>/docs/agents/dispatch-ledger.md` all live under the project root, never in the commander's own workspace — a governance file the project cannot find does not exist.
- Root-cause fix for the ambiguity: `docs/agents/` proposals now state the base root explicitly. If the project root does not exist yet at gate time, the commander either creates the root + docs skeleton itself (authorized by gate approval) or has the executor create it first and writes governance files immediately after — stating which path was chosen.
- Updated identity-library (registry path rules), closure-rules (registry section, plan-persistence rule), agent-modes (ledger location), lessons; added the expectation to the recipient-identity self-test.
- Synchronized version references to 2.7.0.

- 治理产物改为以项目为根（用户在转交实测中发现：总指挥把身份登记与计划写进了自己的工作区而非项目文件夹）：身份登记 `<项目根>/docs/agents/`、模式三计划 `<项目根>/docs/plans/`、派发台账 `<项目根>/docs/agents/dispatch-ledger.md` 一律放在项目根之下，绝不放进总指挥自己的工作区——项目找不到的治理文件等于不存在。
- 根因修复：`docs/agents/` 提案现在显式声明基准根。若门禁时项目根尚未创建，总指挥可自行创建项目根与 docs 骨架（门禁批准即授权），或让执行者先建根、总指挥随后立即写入治理文件——并向用户说明选了哪条路。
- 更新 identity-library（登记路径规则）、closure-rules（登记节、计划落盘规则）、agent-modes（台账位置）、lessons；接收方身份自测加断言。
- 版本号同步到 2.7.0。

## 2.6.0 - 2026-09-04

- Completed the recipient decoupling (user decision): task packages no longer require the recipient's underlying LLM model/version. The recipient is named by role + platform/window (e.g., `TRAE 主执行者` / `智谱对话窗口执行者`); the model is optional reference metadata — record it if known, never require it, never let a model change invalidate a package or ledger row. Capability fit is judged by observed return quality, not model name. The anti-vagueness rule survives with a new object: a bare "另一个 AI" is still not a recipient.
- Supersedes the model/session part of 2.5.1's clarification; the "decoupling ≠ anonymity" line now means role+platform routing metadata. The declaration (v1.10.0), the task package, and the registry are now consistently model-agnostic.
- Updated agent-modes (capability-fit rule, task-package fields, boundaries), commander-roles, identity-library (including a stale ZH declaration line that still mentioned 目标模型/会话), workflow, lessons, README, and self-test.
- Synchronized version references to 2.6.0.

- 完成接收方解耦（用户拍板）：任务包不再要求接收方的底层大模型/版本。接收方按"角色 + 平台/窗口"命名（如 `TRAE 主执行者` / `智谱对话窗口执行者`）；大模型是可选参考元数据——知道就记，不强制，模型变动不使任务包或台账失效。能力匹配以实际返回质量判断，不以模型名称判断。反模糊规则保留但对象改变：笼统的"另一个 AI"仍不是合格接收方。
- 取代 2.5.1 澄清中关于模型/会话的部分；"解耦不等于匿名"现在指"角色+平台"路由元数据。身份声明（v1.10.0）、任务包、身份登记表三者现已完全模型无关。
- 更新 agent-modes（能力匹配规则、任务包字段、边界）、commander-roles、identity-library（含一处仍写"目标模型/会话"的中文声明残留）、workflow、lessons、README、self-test。
- 版本号同步到 2.6.0。

## 2.5.0 - 2026-09-04

- Field test follow-up (commander run on a flashcard web app, 11/12):
  - The gate output now includes an explicit risk-tier line (轻 / 中 / 重 with the reason) — the run classified correctly but never stated the tier.
  - Light-tier boundary clarified: brand-new products (new project/app) default to medium unless the instruction fully specifies type, location, and form — codifies the two runs' correct behavior (plane game = fully specified light tier; flashcard = medium full flow).
  - Package size follows the channel, not the mode label: the mini package is the subagent standard; attaching a 24-field package to a subagent is acceptable but not required (the run over-complied harmlessly).
- Updated the gate templates in SKILL.md and workflow, the Risk Trimming table, the mini-package section, and self-test 56; synchronized version references to 2.5.0.

- 实测跟进（指挥官模式跑单词卡片应用，11/12）：
  - 门禁确认单新增显式"风险分档"行（轻/中/重 + 理由）——实测中分档判对了但没说出来。
  - 轻通道边界写死：全新产物（新项目/新应用）默认中档，除非指令完整指定类型、位置与形态——把两次实测的正确行为（飞机游戏=完整指定的轻档；卡片应用=中档全流程）成文化。
  - 包规格跟随通道、不跟随模式标签：迷你包是子 Agent 标准配置；给子 Agent 附 24 字段包可以但非必需（实测无害地超标）。
- 更新 SKILL.md 与 workflow 的门禁模板、风险分档表、迷你任务包节、自测 56；版本号同步到 2.5.0。

## 2.4.0 - 2026-09-04

- Completion of the private prototype project distillation — six remaining Sol thinking patterns adopted from the evolved commander identity file (2026-08-15):
  - Authority order for conflicting sources: user's current explicit instructions > role permission boundaries > authoritative specs/confirmed decisions/artifacts > other role files and task packages > historical conversations and case libraries; contradiction triage verifies facts first, fixes within scope directly, and escalates only product-direction/high-risk/substantively-ambiguous conflicts.
  - Scope discipline: changes required by the user's goal are handled proactively; discovered unrelated issues are recorded and reported, never fixed opportunistically (no drive-by refactors).
  - Declaration cadence relaxed per the prototype's evolution: identity is declared at first entry, role change, formal handoff, or possible confusion — one concise line; per-response repetition is no longer required. Task IDs are reused when present, but a routine task without one is never blocked or force-numbered.
  - History/case libraries are background, not state sources: current phase, counts, and status always come from current authoritative documents and the actual workspace.
  - Workspace hygiene at final acceptance: new/untracked/temporary files are classified as keep, regenerate-able, or clean-up-now — a passing build must not leave work garbage behind.
- Updated declaration-cadence wording across agent-modes, commander-roles, identity-library, workflow, lessons, and self-test; added self-test 61 (authority chain, scope discipline, and workspace hygiene).
- Synchronized version references to 2.4.0.

- 完成私有原型项目蒸馏的最后六条——源自 2026-08-15 版总指挥身份档案的行动思维：
  - 权威优先级链：用户当前明确指令 > 角色权限边界 > 权威规格/已确认决策/实际产物 > 其他角色档案与任务包 > 历史对话与案例库；矛盾分流——先核验事实给推荐，授权范围内直接消除，仅产品方向/高风险/实质歧义才请用户裁决。
  - 范围克制：用户目标所需的改动主动处理；发现的无关问题只记录并报告，绝不顺手扩大重构。
  - 声明节奏按原型进化放宽：首次进入、角色变化、正式交接、可能混淆时声明一行即可；不再要求每条回复重复。任务 ID 沿用即可，普通任务无 ID 不阻塞、不强行编号。
  - 历史/案例库是背景不是状态源：产品阶段、数量、状态永远以当前权威文档和实际工作区为准。
  - 终验新增工作区卫生：检查新增/未跟踪/临时文件并分类（保留/可再生/立即清理），通过构建不得遗留工作垃圾。
- 同步更新 agent-modes、commander-roles、identity-library、workflow、lessons、self-test 中的声明节奏表述；新增自测 61（权威链、范围克制与工作区卫生）。
- 版本号同步到 2.4.0。

## 2.3.0 - 2026-09-04

- Added the Channel Self-Check to Commander Mode: before any coordination confirmation, the agent enumerates its direct communication paths to each recipient (direct tools / subagent framework / MCP / API) with evidence; a direct path plus user approval means direct dispatch; no direct path means user relay with self-contained activation prompts and explicit return-collection instructions. Per-recipient decision, recorded in the ledger.
- Added the Answer Handling protocol — what the commander does after receiving a recipient's answer, in order: consistency check (a report claiming "20 passed, 1 pending-rework, ready for acceptance" is rejected on the spot), personal verification of flagged items down to file:line, three-way ruling (close / send back with precise fix instructions / mark UNVERIFIED), ledger update, next self-contained relay text, and one user-replyable closing sentence.
- Both protocols are distilled from the real commander sessions (the T-SEC-01 exchange: Sol rejected TRAE's acceptance-ready claim, personally located the residual guard gap down to a specific file:line, relayed precise fix instructions, and still refused acceptance until re-verified).
- Added self-test 60 (channel self-check and answer handling).
- Synchronized version references to 2.3.0.

- 指挥官模式新增"通道能力自查"：任何协调确认之前，先逐接收方列出直接沟通路径（直接工具/子 Agent 框架/MCP/API）并附证据；有直接路径且用户同意 → 直接派发；没有 → 用户转交，生成自包含启动提示词并明确回收方式（"原样粘贴回来"）。按接收方逐个决策并记入台账。
- 新增"回答接手协议"——收到接收方回答后的动作序列：自洽检查（"20 项通过、1 项待修整、可最终验收"当场拒收）→ 亲自核验关键项到文件:行号 → 三分裁决（闭环/打回附精确修复指令/标记 UNVERIFIED）→ 更新派发台账 → 生成下一轮自包含转述文本 → 给用户一句可直接回复的话。
- 两条协议均蒸馏自真实指挥官会话（T-SEC-01 交换：Sol 拒收 TRAE 的"可验收"声明、亲自把守卫缺失定位到具体文件:行号、转述精确修复指令、复验通过前拒绝验收）。
- 新增自测 60（通道自查与回答接手）。
- 版本号同步到 2.3.0。

## 2.2.0 - 2026-09-04

- Hardened Subagent Mode (extension A): fixed a stale pre-2.0.0 selection rule that survived the architecture refactor; added concrete engagement criteria (worth splitting vs briefing-cost-dominant); introduced the six-field Subagent Mini Task Package (目标/范围与非目标/验收标准/所需证据/返回格式/信任层级) so subagents never receive under-specified briefs; added the failure fallback — one specific rework round, then absorb the task back into the backbone (delegation is an accelerator, not a sunk-cost trap).
- Hardened Commander Mode (extension B): added the Dispatch Ledger — dispatch state persisted to project docs, one row per task (任务 ID/接收方/信任层级/状态: 已记录→已派发→已返回→待修整→已闭环), read by Resume Check so dispatch state survives session loss (distilled from planning-with-files); added the Completion Gate — project completion is blocked while any ledger row is dispatched/returned-unverified/pending-rework; added Recipient Downgrade — simplified package or reassignment with user notification, acceptance criteria never silently lowered.
- Added self-test 58 (mini package and failure fallback) and 59 (dispatch ledger and completion gate); added two matching failure patterns to lessons.
- Synchronized version references to 2.2.0.

- 强化子 Agent 模式（扩展A）：修掉架构重构中漏网的旧选择规则；新增具体启用判据（值得拆 vs 拆分成本大于收益）；新增六字段"子 Agent 迷你任务包"（目标/范围与非目标/验收标准/所需证据/返回格式/信任层级），杜绝欠规格 briefing；新增失败止损——一次具体打回，仍不合格就收回主干自己做（委派是加速器，不是沉没成本黑洞）。
- 强化指挥官模式（扩展B）：新增派发台账——派发状态落盘到项目文档，每任务一行（任务 ID/接收方/信任层级/状态：已记录→已派发→已返回→待修整→已闭环），续会体检读取，派发状态可存活于会话丢失（蒸馏自 planning-with-files）；新增完成门——台账上还有已派发/已返回未核验/待修整的任务时，禁止宣布项目完成；新增接收方降级——简化任务包或换人并告知用户，验收标准永不静默降低。
- 新增自测 58（迷你任务包与失败止损）与 59（派发台账与完成门）；lessons 新增两条对应失败模式。
- 版本号同步到 2.2.0。

## 2.1.0 - 2026-09-04

- Extended the resource survey with skill discovery and self-install: when the local inventory shows a gap, the agent searches marketplaces and repositories for matching skills/tools, shortlists 2-3 candidates with source and maintenance state, and presents them for approval **before starting work**. Installing is authorization-gated — on approval, install via the official channel, verify, record in the survey; on decline, proceed with the gap noted.
- Borrowed from Headroom (chopratejas/headroom) into Context Discipline: evidence by pointer, not by paste — full outputs to disk, returns carry paths/key excerpts/verdicts; machine bulk may be trimmed, user decisions/task packages/human content never; lost savings are acceptable, lost correctness is not.
- Updated the core style line and the gate field「已盘点可用资源」to include installable-skill candidates (approval required).
- Added self-test 57 (skill discovery and self-install needs approval).
- Synchronized version references to 2.1.0.

- 资源盘点扩展"技能自发现与自装"：本地盘点出缺口时，主动搜索技能市场与开源仓库的匹配候选，给 2-3 个候选（含来源与维护状态），**开工前征求用户批准**。安装属授权门内动作——同意后走官方渠道安装并验证、记入盘点；不同意则带缺口开工并注明。
- 从 Headroom（chopratejas/headroom）借鉴进上下文纪律：证据用指针不用粘贴——完整输出落盘，返回只带路径/关键摘录/结论；机器批量内容可裁剪，用户决策/任务包/人的内容永不裁剪；可省 token，不可省正确性。
- 更新核心风格行与门禁字段「已盘点可用资源」，纳入可装技能候选（需批准）。
- 新增自测 57（技能自发现与自装需批准）。
- 版本号同步到 2.1.0。

## 2.0.0 - 2026-09-04

- Restructured the collaboration architecture: a Single-Agent backbone (default) plus two on-demand, mixable extensions — Subagent enhancement and Commander Multi-Agent. All three names are preserved (模式1/2/3 → 主干/扩展A/扩展B), but the extensions are no longer "alternate modes" the user must pre-select: the agent engages them by scenario (parallel/isolation work → Subagent; cross-model coordination or user relay → Commander) or on user request, announcing a one-line reason and passing each extension's own confirmation gates.
- The old selection guards were reframed, not removed: "only when the user chooses" became "engage by scenario with the extension's own gates" — the Subagent capability gate, the Commander role identity and coordination channel confirmations, and user-relay confirmation all still apply before any dispatch. The backbone never loses gate, evidence, or final-acceptance ownership.
- Updated the loading proof (collaboration architecture instead of three parallel modes), `agents/openai.yaml`, the agent-modes Mode Summary and anti-patterns, lessons, and self-test 28.
- Motivated by a live v1.10.0 field run where a reviewer agent fairly noted the Commander half was dead weight for single-user work; the architecture now keeps the rigor while letting the backbone carry everyday tasks.
- Synchronized version references to 2.0.0. Major version bump: the mode system's framing changed.

- 重构协作架构：**单 Agent 主干（默认）+ 两个按需可混合扩展**——子 Agent 增强与指挥官多 Agent。三个名称全部保留（模式1/2/3 → 主干/扩展A/扩展B），但两个扩展不再是"用户必须预先选择的可选模式"：智能体按场景启用（并行/隔离工作→子 Agent；跨模型协调或用户转交→指挥官）或应用户请求启用，启用前一句话说明理由，并各过各的确认门禁。
- 旧的选择守卫被重新表述而非删除："仅当用户选择时"改为"按场景启用且必须过扩展自身的门禁"——子 Agent 能力门禁、指挥官的角色身份与协调通道确认、用户转交确认在任何派发前仍然全部适用。主干永远不失守门禁、证据与最终验收的所有权。
- 同步更新加载证明（协作架构取代三并行模式）、`agents/openai.yaml`、agent-modes 模式总览与反模式、lessons、自测 28。
- 缘起：v1.10.0 的一次实测中，评审智能体公正指出指挥官半本是单人场景的死重——新架构保留严谨性的同时让主干承载日常任务。
- 版本号同步到 2.0.0。主版本号升级：模式系统的表述框架已改变。

## 1.10.0 - 2026-09-04

- Decoupled identity declarations from the carrying model (distilled from a private prototype, where roles survived model changes): the declaration format is now `身份：<角色名> / 任务 ID <ID>`; the model/session is dispatch metadata belonging to the task package (`Recipient model / session`) and the project AI identity registry. The task-package requirement for a concrete official model identifier is unchanged.
- Added the risk-trimming tiers and the lightweight task channel: light tasks (specific instruction, small blast radius, reversible, no side effects) execute directly on the instruction itself — skipping the gate and resource survey but never the evidence report; destructive, external, push/deploy, or ambiguous work always takes the full flow; when in doubt, escalate to medium automatically.
- Added self-test 56 (lightweight channel boundaries: typo fix executes directly; "refactor everything, 直接干" still requires the gate) and Example 26 (light channel versus full gate, side by side).
- Updated `agents/openai.yaml` default_prompt with the risk-trimming clause and added the risk-tier step to the SKILL.md workflow; lessons gained the risk-scaling principle.
- Synchronized version references to 1.10.0.

- 身份声明与承载模型解耦（蒸馏自私有原型项目——角色在换模型后职责不变）：声明格式改为 `身份：<角色名> / 任务 ID <ID>`；模型/会话属于派发元数据，归任务包（`Recipient model / session`）与项目 AI 身份登记表。任务包"接收方模型/会话必须具体"的要求不变。
- 新增风险分档与轻量任务通道：轻档任务（指令具体、影响面小、可逆、无副作用）凭指令本身直接执行——跳过门禁与资源盘点，但绝不省略证据报告；破坏性、外部、推送部署或含糊任务永远走全流程；拿不准自动升中档。
- 新增自测 56（轻通道边界：改错字直接执行；"重构一切，直接干"仍需门禁）与示例 26（轻通道与全流程门禁对照）。
- 更新 `agents/openai.yaml` default_prompt 风险分档条款；SKILL.md 工作流加入分档步骤；lessons 收录风险裁剪原则。
- 版本号同步到 1.10.0。

## 1.9.1 - 2026-09-04

- Removed the long-operation progress-visibility guidance introduced in 1.9.0, per user decision: long thinking time usually means the model is considering more, not less; it is not a defect and should not be regulated. The Resume Check rule itself is unaffected.

- 依用户裁定移除 1.9.0 引入的"长操作过程可见性"指引：思考时间长通常意味着考虑得更多，不是缺陷，不应立规约束。续会全面体检规则本身不受影响。

## 1.9.0 - 2026-09-04

- Added the Resume Check rule (distilled from 37 real occurrences of the user's "检查项目" ritual in the production commander session): on session resume, "继续", or "检查项目", run a project-level consistency check first — Git status, gate/stage status, docs-versus-reality sync, omissions and inconsistencies — report findings, fix stale items, then continue (SKILL.md workflow step 1; new `Resume Check` section in `sol-reasoning-workflow.md`).
- Added progress-visibility guidance: during long tool chains or deep reasoning, give short progress lines instead of staying silent (real user pain: "怎么样了，我看你一直在思考").
- Added the independent-gatekeeper principle to lessons: a verification role does not decide, execute, or push closure; it personally verifies what everyone else missed.
- Added self-test 55 (resume check) and Example 25 (a completion-oriented resume-check report that still stops at the gate for implementation authorization).
- Synchronized version references to 1.9.0. Full evidence chain: a dedicated internal distillation-session record (kept outside this repository).

- 新增续会全面体检规则（蒸馏自生产指挥官会话中 37 次真实的"检查项目"仪式）：接手既有会话、恢复中断任务或用户说"继续/检查项目"时，先做项目级一致性检查——Git 状态、门禁与阶段状态、文档与实现同步、遗漏与不一致——报告发现、先修过期项再继续（SKILL.md 工作流步骤1；`sol-reasoning-workflow.md` 新增 `Resume Check` 章节）。
- 新增长操作过程可见性指引：长工具链/深度推理期间给出简短进度行，不让用户面对静默思考（真实痛点："怎么样了，我看你一直在思考"）。
- 教训库新增独立守门人原则：核验角色不做决策、不执行、不推动闭环，但亲自核验其他人都会漏掉的问题。
- 新增自测 55（续会体检）与示例 25（面向完成的续会体检报告——实现本身仍停在门禁等授权）。
- 版本号同步到 1.9.0。完整证据链见内部蒸馏会话记录（存于仓库之外的内部存档）。

## 1.8.0 - 2026-09-04

- Enriched the frontmatter description with v1.7+ trigger keywords (pre-implementation gate, resource survey, hands-on UX verification, plus Chinese trigger phrases) to improve automatic activation recall — the description is the primary discovery signal.
- Added Example 24: a completion report demonstrating the hands-on UX loop with per-round findings, screenshot evidence, bounded fix iterations, and `UNVERIFIED` surfaces with user self-verification steps.
- Added distilled lessons for the two v1.7.0 rules: resource inventory before planning, and the hands-on experience loop including its headless degradation; added two matching failure patterns ("planning from scratch without checking available resources" and the "tests green, UI broken" trap).
- Synchronized version references to 1.8.0 across `VERSION`, `SKILL.md`, the README badge, `self-test.md`, and `examples.md`.

- 丰富 frontmatter description 的触发词：补入 v1.7+ 的关键机制（实现前门禁、资源盘点、实操验收）及中文触发短语，提升自动激活命中率——description 是发现的唯一信号。
- 新增示例 24：一份完成报告，示范实操体验闭环的写法——逐轮发现、截图证据、有界修复迭代、`UNVERIFIED` 项与用户自验步骤。
- 教训库补齐 v1.7.0 两条规则的对应条目：规划前资源盘点、实操体验闭环（含 headless 降级）；并新增两条失败模式（"不查现有资源就从零造轮子"与"测试全绿但界面是坏的"陷阱）。
- 版本号同步到 1.8.0，覆盖 `VERSION`、`SKILL.md`、README 徽章、`self-test.md` 与 `examples.md`。

## 1.7.1 - 2026-09-04

- Clarified the hands-on experience loop's environment precondition: under headless/CLI-only runtimes, operate whatever is possible, state the limitation explicitly, and mark un-operated surfaces `UNVERIFIED` with user self-verification steps instead of claiming visual quality (SKILL.md workflow step 8, `sol-reasoning-workflow.md` Hands-On Experience Loop, self-test 54).
- Added host-level guidance: enable platform write/command confirmation switches as a machine-level backstop for the instruction-level gate.
- Adopted from an independent third-party acceptance test of v1.7.0 (10/10 PASS); no behavioral rules changed, documentation clarifications only.

- 明确实操体验闭环的环境前置：纯 headless/CLI 运行时下，能操作的操作、明说限制，未操作部分标 `UNVERIFIED` 并给用户自验步骤，绝不宣称视觉良好（SKILL.md 工作流步骤8、`sol-reasoning-workflow.md` 实操体验闭环章节、自测 54）。
- 新增宿主级指引：建议开启平台的写文件/运行命令二次确认开关，作为指令级门禁的机器级兜底。
- 采纳自 v1.7.0 的独立第三方验收测试（10/10 通过）；未改变任何行为规则，仅为文档澄清。

## 1.7.0 - 2026-09-04

- Added a mandatory resource survey before implementation: the agent must inventory locally installed skills, reusable templates and existing implementations, and web references for the task type, with a use/adapt/not-applicable verdict per item; the inventory is part of the pre-implementation gate (`已盘点可用资源`).
- Added a mandatory hands-on experience loop before completion: for any artifact a human directly operates or sees, the agent must open it in the real target environment, personally operate every button/key/gesture and at least one failure path, capture screenshots as evidence, record UX/visual issues, fix them, and re-operate to verify (bounded at 3 iterations by default). Un-operated surfaces must be marked `UNVERIFIED`.
- Strengthened the core style and workflow: research now explicitly covers skill/resource inventory; logic tests alone no longer close delivery for operable artifacts.
- Added self-test 53 (resource survey before implementation) and self-test 54 (hands-on UX loop before completion).
- Motivated by a real 2048 delivery where logic tests passed 20/20 while the agent never operated the UI it claimed was good.

- 新增强制资源盘点前置：动手前必须盘点本地已装 skills、可复用模板与现成实现、网络参考实现，逐项给出"用/改造用/不适用"结论；盘点结果写入门禁确认单「已盘点可用资源」。
- 新增强制实操体验闭环：凡人要直接操作或观看的产物，完成前必须在真实目标环境亲自操作每个按钮/按键/手势及至少一条失败路径，截图留证，记录 UX/视觉问题并修复复验（默认封顶 3 轮）；没亲手操作过的部分标 `UNVERIFIED`。
- 强化核心风格与工作流：调研明确覆盖 skills/资源盘点；对可操作产物，仅逻辑测试通过不再构成完成。
- 新增自测 53（实现前资源盘点）与自测 54（完成前实操体验闭环）。
- 缘起：一次 2048 实测交付中逻辑测试 20/20 通过，但智能体从未亲自操作过自己声称"体验良好"的界面。

## 1.6.0 - 2026-09-04

- Added a pre-dispatch conflict ledger: before handing off parallel agents, the commander scans shared files/interfaces and emits a ledger table, turning the "no conflict" claim into a verifiable artifact (prevents two writable DRIs on the same file).
- Added capability-fit guidance for recipient model/session selection, orthogonal to the T1/T2/T3 trust tier: route security review, reasoning-heavy, or ambiguous tasks to a stronger model; route mechanical file-write or formatting tasks to a faster model.
- Added a Consolidation (fan-in) phase and a fix-loop cap: after parallel recipients return, the commander merges outputs and reconciles conflicts before closure; review-fix loops are bounded at 5 rounds per task, escalating to the user at the cap instead of looping silently.
- Added self-test 51 (pre-dispatch conflict ledger) and self-test 52 (fix-loop cap), removed the dead `update-readme.py` migration script, and replaced a restated rule in `sol-reasoning-workflow.md` with a pointer to the canonical sources.
- Synchronized version references to 1.6.0 across `VERSION`, `SKILL.md`, the README badge, `self-test.md`, and `examples.md`.

- 新增派发前冲突账本：派发并行 Agent 前，总指挥扫描共享文件/接口并输出账本表，把"无冲突"从口头声称变成可核验产物（从源头防止同一文件出现两个可写 DRI）。
- 新增接收方模型/会话的"能力匹配"指引，与 T1/T2/T3 信任层级正交：安全审查、重推理或含糊任务用更强模型；机械写文件/格式化任务用更快模型。
- 新增合并（fan-in）阶段与修复循环上限：并行接收方返回后，总指挥先合并输出并裁决冲突再闭环；审查-修复循环每任务封顶 5 轮，到顶升级用户而非静默空转。
- 新增自测 51（派发前冲突账本）与自测 52（修复循环上限），删除已失效的 `update-readme.py` 迁移脚本，并将 `sol-reasoning-workflow.md` 里一处复述规则改为指向权威来源。
- 版本号同步到 1.6.0，覆盖 `VERSION`、`SKILL.md`、README 徽章、`self-test.md` 与 `examples.md`。

## 1.5.0 - 2026-09-04

- Resolved the task-package schema conflict. The compact 【任务派发】 note in `sol-reasoning-workflow.md` is now explicitly scoped as "Task Dispatch Package (Internal)" for Single-Agent / Subagent dispatch, and Commander Multi-Agent cross-Agent handoff must use the mandatory full task package in `references/multi-agent-closure-rules.md`.
- Trimmed `agents/openai.yaml` `default_prompt` to a pointer. It still carries the loading proof, three modes, the mandatory pre-implementation gate, and A/B clarification into the first invocation, but no longer duplicates rule bodies that live in SKILL.md and references.
- Made `identities/README.md` the single canonical role catalog. `identity-library.md` and `commander-roles.md` now point to it instead of restating the role list, removing the triple-listing drift.
- Synchronized version references to 1.5.0 across `VERSION`, `SKILL.md`, the README badge, `self-test.md`, and `examples.md`.
- De-duplicated the task package and trust tiers. `multi-agent-closure-rules.md` is now the sole canonical field list for the mandatory task package; `agent-modes.md` and `sol-reasoning-workflow.md` point to it instead of restating ~24 fields. `identity-library.md` is now the sole canonical T1/T2/T3 definition; the inline glosses in `agent-modes.md` and `sol-reasoning-workflow.md` were replaced with pointers. No rule was removed, only the duplicate copies.
- Verified by running self-test 33 (task package + trust tiers) against the canonical files; all expected fields resolve through the new pointer chain.

- 修复任务包 schema 冲突。`sol-reasoning-workflow.md` 中的精简【任务派发】说明已明确限定为“内部任务派发包”，仅用于单 Agent / 子 Agent 派发；指挥官多 Agent 模式的跨 Agent 交接必须使用 `references/multi-agent-closure-rules.md` 中的强制完整任务包。
- 精简 `agents/openai.yaml` 的 `default_prompt` 为指针式。它仍把加载证明、三种模式、实现前门禁和 A/B 澄清带进首次调用，但不再重复 SKILL.md 与 references 中已有的规则正文。
- 将 `identities/README.md` 确立为唯一的权威角色目录。`identity-library.md` 与 `commander-roles.md` 改为指向它，不再各自重列角色清单，消除三处重复导致的漂移。
- 版本号同步到 1.5.0，覆盖 `VERSION`、`SKILL.md`、README 徽章、`self-test.md` 与 `examples.md`。
- 去重任务包与信任层级。`multi-agent-closure-rules.md` 成为强制任务包字段清单的唯一权威来源，`agent-modes.md` 与 `sol-reasoning-workflow.md` 改为指向它，不再各列约 24 个字段；`identity-library.md` 成为 T1/T2/T3 的唯一权威定义，另两处的内联释义替换为指针。没有删除任何规则，只删除重复副本。
- 已跑自测 33（任务包 + 信任层级）对照权威文件验证，所有期望字段都能通过新的指针链解析到。

## 1.4.0 - 2026-08-08

- Renamed this skill from `gpt-5-6-sol-reasoning-style` to `gpt-5-6-sol-multi-agent-style` as a new multi-agent orchestration concept.
- Added a Mode 3 direct execution shortcut: if only one AI is available and direct tools are chosen, skip the project AI identity registry and recipient activation prompts while keeping Mode 3 confirmation and gate rules.
- This reduces first-use overhead for users who do not need multi-agent relay.
- Added self-test 50.
- Updated SKILL.md, README, agent-modes, identity-library, multi-agent closure rules, workflow, lessons, self-test, examples, and `agents/openai.yaml`.

- 新增模式三直接执行短路：如果只有当前模型可用且选择直接工具，则跳过项目 AI 身份目录和接收方启动提示词，但仍保留模式三确认和门禁规则。
- 降低不需要多 Agent 转交时的首次使用负担。
- 新增自测 50。
- 更新 SKILL.md、README、agent-modes、identity-library、multi-agent closure rules、workflow、lessons、self-test、examples 和 `agents/openai.yaml`。

## 1.3.9 - 2026-08-08

- When no recipients are registered in Mode 3, the commander must first ask what project/task to work on.
- It must assess difficulty, select the smallest suitable role set, register those roles, and generate a standalone activation prompt for each recipient to paste into a new conversation window.
- Added self-test 49.
- Updated SKILL.md, README, agent-modes, identity-library, multi-agent closure rules, workflow, lessons, self-test, examples, and `agents/openai.yaml`.

- 模式三没有已登记接收方时，总指挥必须先问用户要做什么项目/任务。
- 必须评估难度、选择最小合适的角色集、登记角色，并为每个接收方生成可粘贴到新对话窗口的启动提示词。
- 新增自测 49。
- 更新 SKILL.md、README、agent-modes、identity-library、multi-agent closure rules、workflow、lessons、self-test、examples 和 `agents/openai.yaml`。

## 1.3.8 - 2026-08-08

- Required AI identity registry and task packages to use official model identifiers/versions or exact configured sessions.
- Rejected Chinese brand names such as `豆包` alone; use names like `Doubao Seed`, `GPT-5`, or the exact configured identifier.
- Added self-test 48.
- Updated SKILL.md, README, identity-library, agent-modes, multi-agent closure rules, workflow, lessons, self-test, examples, and `agents/openai.yaml`.

- 要求 AI 身份登记和任务包使用官方模型标识/版本或精确配置会话。
- 禁止只写“豆包”等中文品牌名；应写 `Doubao Seed`、`GPT-5` 或精确配置名。
- 新增自测 48。
- 更新 SKILL.md、README、identity-library、agent-modes、multi-agent closure rules、workflow、lessons、self-test、examples 和 `agents/openai.yaml`。

## 1.3.7 - 2026-08-08

- Clarified that Mode 3 can cover the direct-tool path of Mode 1 and the subagent path of Mode 2, while adding Mode 3 governance rules.
- Updated SKILL.md, README, agent-modes, workflow, lessons, examples, and `agents/openai.yaml`.

- 明确模式三可覆盖模式一的直接工具路径和模式二的子 Agent 路径，同时增加模式三治理规则。
- 更新 SKILL.md、README、agent-modes、workflow、lessons、examples 和 `agents/openai.yaml`。

## 1.3.6 - 2026-08-08

- Refined the Mode 3 description: subagent tools are not required but may be used, and stronger models are recommended as commander.
- Updated SKILL.md, README, agent-modes, workflow, lessons, examples, and `agents/openai.yaml`.

- 优化模式三描述：不要求子 Agent 工具，但可以使用；推荐由强模型担任总指挥。
- 更新 SKILL.md、README、agent-modes、workflow、lessons、examples 和 `agents/openai.yaml`。

## 1.3.5 - 2026-08-08

- Changed first Mode 3 registry setup from "check/create by default" to "ask the user for the path first".
- If the user provides a path, use it; if none exists, propose `docs/agents/` and request authorization; if authorization is denied, return `BLOCKED`.
- Added self-test 47 for denial handling.
- Updated SKILL.md, README, agent-modes, identity-library, multi-agent closure rules, workflow, lessons, self-test, examples, and `agents/openai.yaml`.

- 模式三首次建立 AI 身份目录从“默认检查/创建”改为“先问用户路径”。
- 用户提供路径就沿用；没有则提出 `docs/agents/` 并请求授权；拒绝授权则返回 `BLOCKED`。
- 新增自测 47，覆盖拒绝创建时的处理。
- 更新 SKILL.md、README、agent-modes、identity-library、multi-agent closure rules、workflow、lessons、self-test、examples 和 `agents/openai.yaml`。

## 1.3.4 - 2026-08-08

- Changed the generic project AI identity directory default to ASCII `docs/agents/`.
- Chinese paths such as `docs/项目AI身份/` are accepted only when the project already established them.
- Updated SKILL.md, README, multi-agent closure rules, and self-test.

- 通用项目 AI 身份目录默认改为 ASCII 路径 `docs/agents/`。
- 中文路径如 `docs/项目AI身份/` 仅在项目已经使用时才沿用。
- 更新 SKILL.md、README、multi-agent closure rules 和 self-test。

## 1.3.3 - 2026-08-08

- Added mandatory project AI identity registry for first Mode 3 use.
- Before user-relay dispatch, the commander must check or create `docs/agents/` or the project's AI identity directory, register actual recipients, and confirm they exist.
- Prohibited placeholder task packages when no recipient AI is registered.
- Mode 3 plans must be persisted in project docs such as `docs/plans/`, not only in chat.
- Added self-test 46.
- Updated SKILL.md, README, agent-modes, identity-library, multi-agent closure rules, workflow, lessons, self-test, examples, and `agents/openai.yaml`.

- 模式三首次使用新增强制项目 AI 身份登记。
- 用户转交前，总指挥必须检查或创建 `docs/agents/` 或项目 AI 身份目录，登记实际接收方并确认其存在。
- 没有已登记接收方时，禁止生成带占位符的任务包。
- 模式三计划必须写入项目 docs，例如 `docs/plans/`，不能只在对话里出现。
- 新增自测 46。
- 更新 SKILL.md、README、agent-modes、identity-library、multi-agent closure rules、workflow、lessons、self-test、examples 和 `agents/openai.yaml`。

## 1.3.2 - 2026-08-08

- Required `Recipient model / session` to be concrete before dispatch; `待用户指定` or `待确认` is incomplete.
- Required `Recipient activation prompt` to be a self-contained copy-paste text with Skill version, mode, identity, and identity declaration format.
- Added self-test 45.
- Updated SKILL.md, README, identity-library, agent-modes, multi-agent closure rules, workflow, lessons, self-test, examples, and `agents/openai.yaml`.

- 强制派发前接收方模型/会话必须明确；“待用户指定”或“待确认”属于任务包不完整。
- 强制接收方启动提示词必须可直接复制粘贴，包含 Skill 版本、模式、身份和身份声明格式。
- 新增自测 45。
- 更新 SKILL.md、README、identity-library、agent-modes、multi-agent closure rules、workflow、lessons、self-test、examples 和 `agents/openai.yaml`。

## 1.3.1 - 2026-08-08

- Added mandatory `Recipient activation prompt` to task packages.
- For user relay, the activation prompt must tell the receiving model to load the Skill, use Commander Multi-Agent Mode, adopt the assigned identity, and then execute the task package.
- Added self-test 44.
- Updated SKILL.md, README, identity-library, agent-modes, multi-agent closure rules, workflow, lessons, examples, self-test, and `agents/openai.yaml`.

- 任务包新增必填字段“接收方启动提示词”。
- 用户转交时，启动提示词必须告诉接收模型：加载本 Skill、使用指挥官多 Agent 模式、采用指定身份，再执行任务包。
- 新增自测 44。
- 更新 SKILL.md、README、identity-library、agent-modes、multi-agent closure rules、workflow、lessons、examples、self-test 和 `agents/openai.yaml`。

## 1.3.0 - 2026-08-08

- Simplified `SKILL.md` for lower first-load token usage.
- Kept only loading proof, mode introductions, the implementation gate, clarification modes, concise execution rules, and on-demand reference pointers.
- Moved detailed Mode 3 templates, role confirmation rules, closure rules, and workflow details into references loaded only when needed.
- Simplified `agents/openai.yaml` default_prompt while retaining the hard gate, mode requirements, and final acceptance rule.

- 精简 `SKILL.md`，降低首次加载 Token 消耗。
- 只保留加载证明、模式简介、实现前门禁、澄清模式、精简执行规则和按需引用入口。
- 模式三确认模板、角色确认规则、闭环规则和完整工作流移到 references，按需读取。
- 精简 `agents/openai.yaml` 的 default_prompt，同时保留硬门禁、模式要求和最终验收规则。

## 1.2.9 - 2026-08-08

- Made the no-code-block rule explicit for role identity confirmation, coordination channel confirmation, and implementation gate output.
- These outputs must now use plain Markdown tables, labels, or short bullets instead of code blocks.
- Added self-test 43.
- Updated SKILL.md, README, identity-library, agent-modes, lessons, self-test, examples, and `agents/openai.yaml`.

- 明确禁止角色身份确认、协调通道确认和实现前确认使用代码块。
- 这些输出必须使用普通 Markdown 表格、标签或短列表呈现。
- 新增自测 43。
- 更新 SKILL.md、README、identity-library、agent-modes、lessons、self-test、examples 和 `agents/openai.yaml`。

## 1.2.8 - 2026-08-08

- Added hard rule: role identity confirmation must stop and wait for explicit user confirmation, even when `commander` is the default.
- Added hard rule: platform tool availability is not dispatch confirmation; the user must choose the dispatch path before it is marked confirmed or the implementation gate starts.
- Added hard rule: if the user chooses user relay, the commander must not replace it with direct tools or subagents.
- Added self-tests 41-42.
- Updated SKILL.md, README, agent-modes, workflow, multi-agent closure rules, self-test, examples, and `agents/openai.yaml`.

- 新增硬规则：角色身份确认后必须停止并等待用户明确确认，即使默认是 `commander`。
- 新增硬规则：平台工具可用不等于派发通道已确认；用户选择派发方式后才能标记为确认，才能进入实现前确认。
- 新增硬规则：用户选择用户转交后，不得改用直接工具或子 Agent 代替。
- 新增自测 41-42。
- 更新 SKILL.md、README、agent-modes、workflow、multi-agent closure rules、self-test、examples 和 `agents/openai.yaml`。

## 1.2.7 - 2026-08-08

- Clarified Commander Multi-Agent Mode: the current model may act as a commander or another role, not only as the commander.
- Updated all mode descriptions, role-library naming, examples, self-test, and `agents/openai.yaml`.
- Added self-test 40 to verify Mode 3 can adopt a non-commander identity such as `executor`.

- 明确指挥官多 Agent 模式：当前模型可作为总指挥或其他角色，不只是总指挥。
- 更新所有模式说明、角色库命名、示例、自测和 `agents/openai.yaml`。
- 新增自测 40，验证模式三可以采用 `executor` 等非总指挥身份。

## 1.2.6 - 2026-08-08

- Added `references/multi-agent-closure-rules.md`, distilling production multi-agent collaboration rules into a project-neutral contract.
- Added identity mutual exclusion, DRI responsibility closure, no task bouncing, one writable DRI per file, role-file access isolation, authorization separation, role-scoped context, and stage transition closure.
- Added self-tests 38-39 for DRI closure and file ownership/context discipline.
- Updated SKILL.md, README, identity-library, commander-roles, agent-modes, workflow, lessons, examples, self-test, and `agents/openai.yaml`.

- 新增 `references/multi-agent-closure-rules.md`，把真实多 Agent 协作经验蒸馏为项目无关的闭环契约。
- 新增身份互斥、DRI 责任闭环、禁止任务弹跳、每文件唯一可写 DRI、角色文件访问隔离、授权分离、角色化上下文和阶段转换闭环。
- 新增自测 38-39，覆盖 DRI 闭环和文件所有权/上下文纪律。
- 更新 SKILL.md、README、identity-library、commander-roles、agent-modes、workflow、lessons、examples、self-test 和 `agents/openai.yaml`。

## 1.2.5 - 2026-08-08

- Added mandatory identity declarations in Commander Mode: each role must start its response with role, target model/session, and task ID unless the host already injects identity automatically.
- Added identity declaration format to task packages.
- Added self-test 37.
- Updated SKILL.md, README, identity-library, commander-roles, agent-modes, workflow, lessons, examples, self-test, and `agents/openai.yaml`.

- 模式三新增强制身份声明：除非宿主已自动注入身份，每个角色回复前必须声明角色、目标模型/会话和任务 ID。
- 任务包新增身份声明格式。
- 新增自测 37。
- 更新 SKILL.md、README、identity-library、commander-roles、agent-modes、workflow、lessons、examples、self-test 和 `agents/openai.yaml`。

## 1.2.4 - 2026-08-08

- Added natural presentation rules: templates are content checklists, not literal formatting.
- Models must render required fields with natural language, short sentences, or compact tables; no more full-template code dumps or boilerplate decoration such as "已读取 N 个文件" and "✅".
- Added self-test 36 to verify templates can be rendered naturally without losing required fields.
- Updated SKILL.md, README, workflow, lessons, agent-modes, self-test, examples, and `agents/openai.yaml`.

- 新增自然呈现规则：模板是内容清单，不是逐字格式。
- 模型必须用自然语言、短句或紧凑表格呈现必需字段；不再整段复制模板，也不再使用“已读取 N 个文件”“✅”等装饰。
- 新增自测 36，验证模板可以自然呈现且不丢失必需字段。
- 更新 SKILL.md、README、workflow、lessons、agent-modes、self-test、examples 和 `agents/openai.yaml`。

## 1.2.3 - 2026-08-08

- Clarified the loading proof requirement: the model must quote the first hard rule of Mandatory Pre-Implementation Gate exactly: `宣布阶段序列不是确认。`
- Updated examples and self-test so future loading proofs do not quote the gate preamble instead of the first hard rule.

- 明确加载证明要求：模型必须逐字引用 Mandatory Pre-Implementation Gate 硬性规则第一条：`宣布阶段序列不是确认。`
- 更新示例和自测，避免以后把门禁前置说明误当成第一条规则。

## 1.2.2 - 2026-08-08

- Required every dispatched task package to name the recipient identity, recipient model/session, and why that recipient was selected.
- Prohibited dispatching to a generic "another AI" without role and rationale.
- Added dispatch role assignment rules to SKILL.md, identity-library, commander-roles, agent-modes, workflow, lessons, examples, self-test, README, and `agents/openai.yaml`.
- Added self-test 35 for recipient identity and selection rationale.

- 强制每个派发任务包写明接收方身份、目标模型/会话，以及选择该接收方的理由。
- 禁止把任务派给笼统的“另一个 AI”，却不指定角色和选择理由。
- 将派发角色分配规则加入 SKILL.md、identity-library、commander-roles、agent-modes、workflow、lessons、examples、self-test、README 和 `agents/openai.yaml`。
- 新增自测 35，验证任务包必须包含接收方身份和选择理由。

## 1.2.1 - 2026-08-08

- Fixed role identity confirmation usability: the model must now read `identities/README.md` or `references/commander-roles.md` and show a one-line responsibility for every candidate identity before asking the user to choose.
- Added a bilingual built-in identity quick-reference table in `identities/README.md` and `references/identity-library.md`.
- Added self-test 34 to verify that role confirmation explains each identity instead of only listing role names.
- Updated SKILL.md, README, agent-modes, workflow, lessons, examples, and self-test.

- 修复角色身份确认的可用性：模型必须先读取 `identities/README.md` 或 `references/commander-roles.md`，在询问用户前给每个候选身份附一行职责说明。
- 在 `identities/README.md` 和 `references/identity-library.md` 增加内置身份中英对照速查表。
- 新增自测 34，验证角色确认必须解释每个身份，而不是只列角色名。
- 更新 SKILL.md、README、agent-modes、workflow、lessons、examples 和 self-test。

## 1.2.0 - 2026-08-08

- Expanded the built-in identity library: added architect, deputy planner, QA/test engineer, code reviewer, security tester, documentation consistency reviewer, user representative, and optional roles for performance, release, compliance, legal, integration, risk, deputy commander, and documentation writing.
- Standardized every identity file around Identity, Mission, Responsibilities, Process, Required Output, Handoff, Boundaries, and Anti-Patterns.
- Added `references/identity-library.md` as the universal role contract: role selection, no-match identity handling, confidence signals, trust tiers, and identity drift.
- Commander task packages now include trust tiers: T1 research, T2 artifacts/file writes, T3 commands or external/destructive actions.
- Dispatched recipients must return `CONFIDENCE: High / Medium / Low` or `BLOCKED` instead of guessing.
- Added self-tests 30-33 for role selection, no-match handling, confidence/BLOCKED, and trust tiers.
- Updated SKILL.md, README, workflow, lessons, examples, self-test, and `agents/openai.yaml`.

- 扩展内置身份库：新增架构师、副计划者、测试工程师、代码审查员、安全测试员、文档一致性审查员、用户代表，以及性能、发布、合规、法律、集成、风险、副总指挥和文档编写等可选角色。
- 统一所有身份文件结构：身份定位、使命、职责、流程、必需输出、交接、边界、反模式。
- 新增 `references/identity-library.md` 作为统一身份契约，覆盖角色选择、无匹配身份处理、置信度信号、信任层级和身份漂移。
- 指挥官任务包新增信任层级：T1 调研分析、T2 产物/文件写入、T3 命令/部署/破坏性或外部操作。
- 被派发的接收方必须返回 `CONFIDENCE: High / Medium / Low` 或 `BLOCKED`，不能靠猜测继续。
- 自测新增 30-33，覆盖角色选择、无匹配身份、置信度/阻塞信号和信任层级。
- 更新 SKILL.md、README、workflow、lessons、examples、self-test 和 `agents/openai.yaml`。

## 1.1.0 - 2026-08-08

- Added three execution modes: default single-agent mode, subagent mode, and commander multi-agent mode.
- Default mode keeps Planning, Execution, and Review as internal role faces for models without subagents.
- Subagent mode lets a host with subagents map the role faces to Planner, Executor, and Reviewer subagents while the main model retains the gate, evidence ownership, and final acceptance.
- Subagent mode now requires a mandatory capability confirmation before every use; without real subagent tool or configuration evidence, the model falls back to single-agent mode and marks capability as `UNVERIFIED`.
- Commander mode is now defined as a universal commander mode: it does not require subagent tools, suits any model, and is recommended for stronger models. Direct tools, external sessions, CLI/API, and user relay are all valid dispatch paths. Before every use, the commander outputs a coordination channel confirmation and must not assume a user-relayed task has been dispatched.
- Added `references/commander-roles.md` with core roles, optional roles, boundaries, and the smallest role set by project size.
- Added mandatory real-environment acceptance for every project type: web pages must be opened, apps launched, CLIs run, APIs requested, libraries imported, plugins installed, and docs followed before final completion; unit tests are not sufficient.
- On initial loading, the model must state the three execution modes: Single-Agent Mode, Subagent Mode, and Commander Multi-Agent Mode.
- Commander Multi-Agent Mode is explicitly suited to medium and large projects; simple one-shot tasks should not use it.
- Commander Mode now requires role identity confirmation before dispatch. Built-in identities are in `identities/`; user custom identities are in `custom-identities/` (Chinese: 其他身份).
- Commander multi-agent mode lets the model using this skill act as a commander and dispatch work to other independent models or agents while retaining user confirmation, whole-plan control, evidence verification, and final acceptance.
- Added `references/agent-modes.md` with mode boundaries, task package format, evidence handoff, and anti-patterns.
- Updated SKILL.md, workflow, lessons, self-test, examples, README, and `agents/openai.yaml`.

- 新增三种执行模式：默认单 Agent 模式、子 Agent 模式和指挥官多 Agent 模式。
- 默认模式为没有子 Agent 的模型保留“规划面、执行面、审查面”的内部思考模式。
- 子 Agent 模式允许支持子 Agent 的宿主把三个角色面映射为 Planner、Executor、Reviewer 子 Agent，同时主模型保留门禁、证据归属和最终验收。
- 子 Agent 模式每次使用前必须先做能力确认；没有真实子 Agent 工具或配置证据时，回退单 Agent 模式并标记 `UNVERIFIED`。
- 指挥官模式重写为通用总指挥模式：不要求子 Agent 工具，适合任何大模型，推荐由能力更强的大模型担任总指挥。直接工具、外部会话、CLI/API 和用户转交都是有效派发方式。每次使用前先输出协调通道确认，并不得假设用户转交的任务已经派发。
- 新增 `references/commander-roles.md`，包含核心角色、可选角色、角色边界，以及按项目规模选择的最小角色集。
- 新增所有项目类型的强制真实环境验收：Web 必须打开、应用必须启动、CLI 必须运行、API 必须请求、库必须导入、插件必须安装、文档必须按示例执行后才能最终完成；单元测试通过不充分。
- 刚加载时必须先说明三种执行模式：单 Agent 模式、子 Agent 模式、指挥官多 Agent 模式。
- 指挥官多 Agent 模式明确适用于中大型项目；简单一次性任务不应使用该模式。
- 指挥官多 Agent 模式派发前必须先完成角色身份确认。内置身份位于 `identities/`，用户自定义身份位于 `custom-identities/`（中文名：其他身份）。
- 指挥官多 Agent 模式让装配本 Skill 的模型作为总指挥，向其他独立大模型或 Agent 派发任务，同时保留用户确认、整体规划、证据核验和最终验收。
- 新增 `references/agent-modes.md`，包含模式边界、任务包格式、证据交接和反模式。
- 更新 SKILL.md、workflow、lessons、self-test、examples、README 和 `agents/openai.yaml`。

## 1.0.0 - 2026-08-07

- Initial public release.
- Added three internal role faces: planning, execution, and review.
- Role faces are thinking modes, not identity replacement or external personas.
- Before closing any stage, the model must switch to the review face and verify actual output through research, divergence, convergence, and evidence.
- Updated SKILL.md, workflow, lessons, self-test, examples, and `agents/openai.yaml`.

- 正式公开发布。
- 新增三个内部角色面：规划面、执行面、审查面。
- 角色面是思考模式，不是身份替换，也不是外部人格。
- 关闭任意阶段前，模型必须切换到审查面，并通过调研、发散、收敛和证据核验实际产出。
- 更新 SKILL.md、workflow、lessons、self-test、examples 和 `agents/openai.yaml`。

## Development History / 发布前内部历史

The `0.1.x` to `3.x` sequence below was internal iteration work before this public release. It is preserved for traceability; public releases start at `1.0.0`, and the current public version is `1.1.0`.

下面的 `0.1.x` 到 `3.x` 版本是公开发布前的内部迭代历史，仅用于追溯；公开版本从 `1.0.0` 开始，当前公开版本为 `1.1.0`。

### 0.1.0 - 2026-08-06

- Initial commander workflow distilled from GPT-5.6 Sol conversations.
- 初始“指挥官”工作流，从 GPT-5.6 Sol 对话中蒸馏而来。

### 1.1.0-internal - 2026-08-06

- Removed project-specific content and made the skill platform-neutral.
- 移除项目特定内容，使 Skill 保持平台中立。

### 1.2.x - 2026-08-06

- Added a neutral `project-policy-template.md` and kept product names only as install targets.
- 新增中立的 `project-policy-template.md`；产品名仅作为安装目标保留。

### 1.3.0 - 2026-08-06

- Added the Agent Addressing Protocol.
- 新增 Agent 指代协议：下达指令前先指明目标 AI 或角色。

### 1.4.0 - 2026-08-07

- Added stage announcement and research-before-planning defaults.
- 新增阶段声明默认值，以及“规划前先调研”的强制步骤。

### 2.0.0 - 2026-08-07

- Renamed the skill and refocused it on high-reasoning behavior.
- 更名为 `gpt-5-6-sol-reasoning-style`，聚焦高推理行为风格。

### 2.1.0 - 2026-08-07

- Added mandatory stage completion inspection.
- 新增每个阶段的完成审查：实际输出被重新打开并对照证据核验后，阶段才算完成。

### 2.2.0 - 2026-08-07

- Added final acceptance inspection from overall goal to detail.
- 新增从整体目标到细节的最终验收检查；发现问题会追加阶段任务并执行。

### 2.3.x - 2026-08-07

- Added divergence-to-convergence bug sweep, self-check gate, best-achievable standard, honesty gate, identity boundary, and independent judgment.
- 新增发散到收敛缺陷扫描、自检门禁、最好可达标准、诚实门禁、身份边界和独立判断。

### 2.4.0 - 2026-08-07

- Replaced checklist divergence with a generative divergence protocol.
- 将清单式发散替换为生成式发散协议，并增加候选数量门限。

### 2.5.0 - 2026-08-07

- Added mandatory instruction assessment before planning.
- 新增规划前的指令评估：把用户指令视为草案，识别歧义、矛盾、缺失约束和风险。

### 2.6.x - 2026-08-07

- Added mandatory user-guided convergence and iterative clarification.
- 新增用户引导收敛和迭代澄清：歧义问题必须返回用户确认，而不是自行决定。

### 2.7.0 - 2026-08-07

- Added the hard pre-implementation gate.
- 新增硬性实现前门禁；“开始”和“现在开始”不再被视为实现授权。

### 2.8.x - 2026-08-07

- Moved the gate to the top of SKILL.md and added the exact `【实现前确认】` template.
- 将门禁移到 SKILL.md 顶部，并增加精确的 `【实现前确认】` 输出模板。

### 2.9.0 - 2026-08-07

- Added the gate to the execution-layer `default_prompt`.
- 将门禁加入执行层 `agents/openai.yaml` 的 `default_prompt`。

### 3.0.x - 2026-08-07

- Added one-shot and step-by-step clarification modes, exact authorization request format, full loading contract, and option depth rules.
- 新增一次性确认/逐项问答模式、精确授权请求格式、完整加载契约和选项深度规则。

### 3.1.0 - 2026-08-07

- Added whole-plan re-evaluation after any user change.
- 新增整体计划再评估：用户改变任意计划部分时，评估数据模型、命令、状态机、测试、文档和验收标准的影响。

### 3.2.0 - 2026-08-07

- Rewrote SKILL.md with progressive disclosure.
- 重写 SKILL.md，采用渐进式加载；加载证明只需要 `SKILL.md` 和 `VERSION`。

### 3.3.0 - 2026-08-07

- Added mandatory reviewer-perspective closure before every stage.
- 新增每个阶段结束前的审查面收口：审查必须按调研 -> 发散 -> 收敛 -> 回到实际证据执行。
