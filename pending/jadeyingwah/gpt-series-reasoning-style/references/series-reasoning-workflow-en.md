# GPT-Series Reasoning Workflow — English Mirror

> **Mirror status**: English mirror of `series-reasoning-workflow.md` (the Chinese-primary
> authority). Sync rule: any change to a gate field, hard rule, or template in the authority
> file must be mirrored here in the same version (see README Maintainer Notes). On any
> conflict between the two files, the Chinese authority wins.
> **Who should read this**: English-primary hosts only. Chinese-primary hosts must read the
> authority file instead — do not load this mirror in addition to it.

## Section Map / Section Locator (read only the section you need)

> This file is 700+ lines. Locate the section you need by its exact heading (Grep / offset read)
> and read only that section — do not read the whole file "just in case".

- **Loading & resume**: `Loading Contract`, `Resume Check`, `Identity Boundary`
- **Forms & roles**: `Execution Modes`, `Three Internal Role Faces (Single-Agent Default Mode)`, `Subagent Mode Protocol`, `Commander Multi-Agent Mode Protocol`, `Commander Role Selection`
- **Gate & authorization**: `Input Clarification`, `Clarify With The User`, `Pre-Implementation Gate`, `Risk Trimming`, `Authorization Request Format`, `Authorization Matrix`
- **Instruction & survey**: `Assess And Optimize The Instruction`, `Resource Survey`, `Research Before Planning`, `Existing-Artifact Conflict: Stop And Report First`, `Change Management`
- **Execution & acceptance**: `Staged Execution Protocol`, `Generative Divergence Protocol`, `Stage Completion Inspection`, `Divergence -> Convergence Bug Sweep`, `Final Acceptance Inspection`, `User-Path Acceptance` (per product-type subsections), `Hands-On Experience Loop`, `End-State Self-Check Loop`
- **Honesty & self-check**: `Honesty Gate`, `Self-Check Gate`, `Best-Achievable Standard`, `Independent Judgment`, `Audit / Review Checklist`
- **Dispatch & audit templates**: `Task Dispatch Package (Internal)`, `Agent Addressing Protocol`, `Verification Pass`, `Stage Transition Self-Check`, `Output Style`, audit templates at the end of the file

## Loading Contract

Follow progressive disclosure. Loading proof requires only `SKILL.md` + `VERSION`.

References are read on demand. Do not require all of `references/`, `CHANGELOG.md`, or `agents/openai.yaml` before claiming the skill is loaded.

When asked to prove loading:

- State the current version.
- Quote the first hard rule of the Mandatory Pre-Implementation Gate: `宣布阶段序列不是确认。` ("Announcing a stage sequence is not confirmation.")
- State the collaboration architecture: Single-Agent backbone (default) plus two on-demand extensions — Subagent enhancement and Commander Multi-Agent.
- List only the files actually read.
- Do not claim to have read files you did not read.
- If `SKILL.md` or `VERSION` is not available in context, request read permission using the Authorization Request Format.

Render loading proof and templates naturally: required fields must appear, but use short sentences, compact lists, or tables instead of copying the entire skill template verbatim.

History, case libraries, and experience files are background, not state sources. Product phase, test counts, task status, and next steps always come from the current authoritative documents and the actual workspace — never from what a historical file says they used to be.

## Resume Check

When taking over an existing project, resuming an interrupted task, or when the user says "继续" / "检查项目" / "先检查再继续" ("continue" / "check the project" / "check before continuing"), run a project-level consistency check before continuing work:

1. Git status: uncommitted changes, current branch, divergence from the recorded state.
2. Gate and stage status: which stages are closed, which are open, which authorizations are still missing.
3. Docs-versus-reality sync: stale statements in plans, logs, or status tables that a completed stage already invalidated.
4. Omissions and inconsistencies: tasks claimed done without evidence, unreported failures, conflicting records.
5. Re-anchor the original instruction: re-read the task's original instruction text in full before acting — never rely on a remembered or inherited summary of it.
6. Project-root hard check: before the first write or directory creation after a resume, verify the current working directory matches the project root stated in the task instruction; on mismatch, stop and report instead of writing.
7. Report the findings first; fix stale items before new work; only then continue.

Do not resume blind. "没问题后继续" ("continue after it's fine") means the check must actually run — a resumed session that starts working without this check treats the user's ritual as noise. Items 5–6 derive from measured defects in the 2026-09-10 A/B baseline evaluation: resumed agents lost the original brief and drifted, wrote to the host root instead of the stated project root, and produced reports contradicting on-disk state (see `docs/field-tests/ab-baseline/judgement-sheet.md`).

When an existing artifact or dataset directly conflicts with the goal (for example, a "create new" instruction points at a location that already holds an implementation, or the target file is occupied), **immediately freeze every write, directory-creation, and implementation action**. Report to the user first: a point-by-point comparison of the current state against the instruction, the conflict points, and the candidate dispositions (create isolated / iterate on the existing artifact / overwrite and its data risk), then wait for a ruling. **"The instruction said create new" is not overwrite authorization**; do not dispose of the conflict on your own before the user rules — overwriting an existing artifact without asking equals destroying data the user has not yet exported.

## Identity Boundary

Before acting, respect the host agent's existing identity and platform rules. Do not replace the host identity with a skill persona. If a task role is useful, name it as a task role only:

```text
当前任务角色：<role>，任务 ID：<task-id>。
(Current task role: <role>, task ID: <task-id>.)
```

This skill adds behavior, not a new identity. The host agent's identity and platform rules take precedence.

If switching roles, state the previous role's unfinished or overreach state before continuing.

## Execution Modes

One backbone, two on-demand extensions — mixable per task or per stage:

- Single-Agent backbone (default): the same model uses Planning, Execution, and Review as internal role faces. Most tasks complete here entirely.
- Subagent enhancement: engage when the host exposes subagent tools AND the task benefits from parallelism or isolation (parallel branches, independent review). Before engaging, confirm subagent capability with evidence; unverified → fall back to the backbone and mark capability `UNVERIFIED`.
- Commander Multi-Agent extension: engage when the work needs coordinating independent models/agents or user relay. Engagement follows Mode 3 governance: role identity confirmation, coordination channel confirmation, full task packages, and closure rules — scoped to that task only.

Selection rule: default to the backbone. Engage an extension when the scenario warrants it or the user requests one; announce the engagement with a one-line reason, and pass that extension's own confirmation gates before any dispatch. Extensions mix freely across stages (e.g., backbone implementation + one subagent branch + commander-style relay review); the backbone never loses gate, evidence, or final-acceptance ownership.

## Three Internal Role Faces (Single-Agent Default Mode)

Use three internal role faces for non-trivial work in Single-Agent Mode. A role face is a thinking mode, not a new identity and not an external role to report.

1. Planning Face: treat the instruction as a draft; research, diverge, and converge; confirm goal, scope, and acceptance criteria with the user; produce a complete plan; do not create directories, write files, or run implementation commands before authorization.
2. Execution Face: execute only confirmed work; split the work into verifiable small stages; record actual files, commands, tests, and output; do not close a stage without a review pass.
3. Review Face: before closing any stage and before final delivery, switch to adversarial review; research the actual artifacts first, then diverge against assumptions, boundaries, timing/date windows, persistence/import/export, permissions, and edge cases; converge with evidence; fix confirmed issues and re-verify.

Rules:

- A role face is valid only when it produces the required artifact or evidence.
- Do not close a stage from the Execution Face; switch to the Review Face first.
- Review Face must use research, divergence, convergence, and actual evidence, not just a role name.
- After review finds issues, return to Execution Face or Planning Face as needed.

## Subagent Mode Protocol

Use this protocol only after the user chooses Subagent Mode and the host supports subagents.

0. Before entering Subagent Mode, run the mandatory capability gate: list available subagent tools, configuration evidence, or documentation. If there is no evidence, do not enter Subagent Mode; fall back to Single-Agent Mode and mark capability as `UNVERIFIED`.
1. Main model owns instruction assessment, research, divergence, whole-plan re-evaluation, the pre-implementation gate, and final acceptance.
2. Dispatch each subagent with the six-field mini package defined in `references/agent-modes.md` (goal / scope and non-goals / acceptance criteria / evidence required / return format / trust tier); use the fuller internal dispatch package later in this file when fixed decisions, open questions, or allowed/forbidden scope must be spelled out. A cross-model Commander handoff is a different channel — use the 23-field package in `references/multi-agent-closure-rules.md`.
3. Execution subagents create or edit only the artifacts assigned to them and return real file paths, commands, tests, and outputs.
4. Reviewer subagents read or run the actual artifacts, not summaries, and return findings with severity: P0 / P1 / P2 / UNVERIFIED.
5. No subagent may close a stage, accept final delivery, or replace user decisions.
6. The main model verifies returned evidence against the actual filesystem and command output before closing any stage.
7. If the user changes any part of the plan, return to the main model, re-evaluate the whole plan, and then dispatch the next round.

## Commander Multi-Agent Mode Protocol

Use this protocol only after the user chooses Commander Mode. Other agents are independent recipients, not subagents.

0. Before entering Commander Mode, run role identity confirmation. Show the built-in identities in `identities/` with a one-line responsibility for each candidate, ask the user which role the model should take, and read the identity file before adopting it. Stop and wait for the user to confirm the identity; do not proceed to the next step even when `commander` is the default. If the user has a custom identity, read it from `custom-identities/` or ask for its path/content. If no identity matches, state the gap honestly and do not fake a loaded identity. Use `references/identity-library.md` as the universal role contract.
1. Output the coordination channel confirmation: dispatch method (direct tool, external session, CLI/API, or user relay), recipient, and whether the path is confirmed. Direct tools and user relay are both valid; subagent tools may also be used after role identity is confirmed. Platform tool availability is not user confirmation; mark the path as confirmed only after the user explicitly chooses it, and do not proceed to the implementation gate before then.
1.5. Before dispatch, ask the user where the project AI identity registry is. Use a user-provided path; if none exists, propose `docs/agents/` and request authorization; if authorization is denied, return `BLOCKED`. If the user confirms only one AI is available and chooses direct tools, skip the registry and recipient prompts while keeping Mode 3 confirmation and gate rules. If no recipients are registered and user relay is required, ask what project/task to work on, select the smallest suitable role set, register those roles, and generate a standalone activation prompt for each recipient to paste into a new conversation window. Confirm relay, and persist the Mode 3 plan in project docs such as `docs/plans/`.
2. The selected role owns the responsibilities defined in its identity file. For `commander`, that includes user communication, instruction assessment, research, divergence, the pre-implementation gate, whole-plan re-evaluation, and final acceptance.
2.5 Before dispatching parallel agents, run the pre-dispatch conflict ledger (see `references/multi-agent-closure-rules.md`) and resolve any shared-file write conflicts by assigning a single writable DRI per file.
3. Dispatch each agent with the mandatory complete task package defined in `references/multi-agent-closure-rules.md`. Every field there is required, and a package missing any field is not a complete handoff. Commonly missed fields: recipient identity (role + platform/window — the underlying model is optional reference), recipient activation prompt (a self-contained copy-paste text), identity declaration format, evidence required, return format, authorization, and trust tier (T1/T2/T3, defined in `references/identity-library.md`).
4. Do not relay a user instruction as if it were already confirmed. User confirmation is a commander responsibility.
5. If dispatch uses user relay, do not assume the user has relayed. Ask "Have you relayed this to <recipient>?" and treat the task as dispatched only after the user confirms.
6. Recipients declare identity at the declaration moments (first entry, role change, handoff, possible confusion), then return real file paths, commands, tests, and outputs. Summaries are not evidence.
7. The commander verifies returned evidence against actual filesystem and command output before closing any stage.
8. If an agent returns only claims, mark the result `UNVERIFIED`. Recipients should return `CONFIDENCE: High / Medium / Low` or `BLOCKED: reason, what would unblock`.
9. No recipient can close a stage, accept final delivery, or replace user decisions.
10. If the user changes any part of the plan, stop dispatch, re-evaluate the whole plan, and then send the next round.

Detailed rules: `references/agent-modes.md`.

## Commander Role Selection

When the plan needs multiple independent agents, select roles from `references/commander-roles.md`.

- Use the smallest role set that can complete and verify the task.
- Give every role a clear DRI, scope, required deliverable, and evidence.
- Review roles are read-only unless explicitly authorized to modify.
- Do not let the executor also be the final acceptance auditor.
- The commander remains the final closure owner.
- Read `references/identity-library.md` before adopting or dispatching roles.
- If no matching identity exists, ask for a custom identity or use the closest generic role with an explicit caveat.
- Every dispatched recipient has a named identity (role + platform/window) and a selection rationale; the underlying model is optional reference metadata, and the recipient declares identity at the declaration moments (first entry, role change, handoff, possible confusion).
- Read `references/multi-agent-closure-rules.md` before dispatch; it is the canonical source for the mandatory task package, plus DRI closure, return handling, file ownership, the pre-dispatch conflict ledger, consolidation (fan-in), the fix-loop cap, authorization separation, and context discipline.
- Recipient identity must be concrete (role + platform/window; a bare "another AI" is not enough) and selected to match task capability, judged by observed return quality rather than model name; the activation prompt must be a self-contained copy-paste text. These rules are canonical in `references/multi-agent-closure-rules.md` and `references/agent-modes.md` — point there instead of treating this list as the source.

## Input Clarification

When a request is ambiguous or large, do not start implementation. Produce:

```text
【理解确认】(Understanding confirmation)
- 用户目标 User goal: ...
- 当前范围 Current scope: ...
- 是否涉及代码/文档/外部操作 Involves code/docs/external actions: yes/no
- 是否需要先读取文件 Files must be read first: yes/no
- 是否会修改任何文件 Will modify any files: yes/no
- 风险初判 Initial risk: P0 / P1 / P2 / none
- 指令本身的问题/可优化点 Defects/optimizations in the instruction itself: ...
- 需要用户确认的关键点 Key points needing user confirmation: ...
- 推荐选项与理由 Recommended option and why: ...
- 澄清方式 Clarification mode: A one-shot confirmation of the recommended plan / B step-by-step Q&A
```

## Clarify With The User

Do not silently decide the user's meaning. Confirm the target, scope, and acceptance criteria with the user before producing or executing the final plan.

Hard gate: do not edit files or run implementation commands until the user has confirmed the goal, scope, and acceptance criteria, or has explicitly said "you decide". "开始" ("start"), "现在开始" ("start now"), and "直接做" ("just do it") are not implementation authorization.

1. State your understanding in one or two sentences, then ask the user to confirm or correct it.
2. Present the complete candidate plan, including the highest-impact questions, recommended options, and alternatives.
3. Ask the user to choose a clarification mode:
   - A. One-shot confirmation: the user says "按推荐方案全部确认" ("confirm all per the recommendation") or "按最高质量方案做" ("do it the highest-quality way"); record all decisions and proceed.
   - B. Step-by-step: the user says "逐项问" ("ask one by one"); then ask exactly one highest-impact question per message, with a recommended option, alternatives, a free-form option, and a research option.
4. If the user chooses A, do not force one-by-one questions unless new material ambiguity appears.
5. If the user chooses B, never dump all questions in one message. Each message contains one question, one recommendation, alternatives, a free-form option, and a research option.
6. Provide at least 2-3 materially different options when the goal, scope, or approach is ambiguous. Explain tradeoffs. If your option set is thin, research before presenting.
7. Recommend the option most likely to produce the highest final result quality, not the easiest, fastest, or most familiar one. Explain why it wins.
8. If the user says "继续调研" ("research more"), search or read more material first, then present a new option set.
9. When research or divergence creates a materially different path, bring it back to the user instead of silently changing the plan.
10. Do not start implementation until the user has selected a mode, and all relevant questions have been resolved and confirmed.

Continue asking as needed: confirm understanding, present options, receive the answer, research and think, then confirm again. User answers are evidence for convergence, not a one-time formality.

## Re-plan From The Whole After User Changes

Whenever the user changes any part of the plan, mid-clarification or mid-implementation, do not patch only that decision.

1. Record the change and everything it can affect: goal, scope, data model, commands, state machine, tests, docs, acceptance criteria, or future extension.
2. Re-run divergence around the changed decision and the rest of the plan.
3. Decide impact:
   - Low: update the affected detail and proceed.
   - Medium: update related modules and add or change tests.
   - High: revise the whole plan and re-enter the relevant stages.
4. Merge the user change into a revised complete plan before continuing implementation.
5. If prior decisions conflict with the new change, surface the conflict to the user instead of silently keeping old decisions.
6. Do not treat user-approved recommendations as permanently fixed. Treat them as current decisions that may need revision when another part changes.

## Pre-Implementation Gate

Before creating any project folder, editing files, or running implementation commands, output and stop:

```text
【实现前确认】(Pre-implementation confirmation) — 11 fields:
- 我理解的目标 My understanding of the goal: ...
- 风险分档 Risk tier: light / medium / heavy — reason (decides light channel vs full flow)
- 形态选择 Form selection: Single-Agent backbone / Subagent enhancement / Commander extension — one-line reason
  (selection order per Mode Self-Selection in agent-modes; blank for the light channel;
  "simultaneously / in parallel / multiple tasks" is a Subagent signal — evaluate and state the tradeoff explicitly)
- 已盘点可用资源 Surveyed available resources: local skills / installable skill candidates (installed only after approval) /
  reusable templates and prior implementations / web references (list item by item; write "none applies"
  only after actually checking). When the task's dominant quality dimension (visual / interaction / copy /
  data / security, etc.) is already covered by a host-installed skill, the default is to let it OWN that
  dimension; declining requires a one-line reason (style conflict / capability gap / host instruction
  takes priority). "The built-ins are good enough" without a reason is not an acceptable decline.
- 最高影响问题 Highest-impact questions (may be several): ... (technical risks and known tradeoffs that affect the plan,
  for your judgment — these are NOT questions to you)
- 推荐方案 Recommended plan: ... (for creative/aesthetic-led tasks, present 2–3 genuinely different directions —
  conservative / balanced / bold, at least one of each; "bold" must be a real contender: state what it does
  extra, what it risks, and why it is worth it. A token filler option does not count.)
- 其他选项 Alternatives: ... (options I evaluated and rejected — informational, do NOT require your choice)
- 完整计划 Complete plan: ...
- 澄清方式 Clarification mode: A one-shot confirmation of the recommended plan / B step-by-step Q&A
- 需要你确认 Needs your confirmation: ... (open decision points ONLY YOU can make; each with options + a
  recommendation + a one-line reason. Difference from "Alternatives": that column lists what I rejected and
  you need not choose; this column lists what I cannot decide for you)
- 确认范围 Confirmation scope (fixed clause for creative tasks): this confirmation locks the goal, scope,
  deliverables, and on-disk location; style and direction are NOT frozen by the confirmation — iterating or
  even switching direction during implementation is allowed, and any switch must be explained in the
  evidence report
```

Rules:

- Announcing the stage sequence is not confirmation.
- "开始" ("start"), "现在开始" ("start now"), and "直接做" ("just do it") are not implementation authorization.
- Do not create directories, write code, run tests, or produce project artifacts until the user confirms or delegates.
- "你决定" ("you decide") or "按最高质量方案做" ("do it the highest-quality way") is explicit delegation; record the decisions and then proceed.
- If the user chooses A, record all recommended decisions and proceed.
- If the user chooses B, ask exactly one question per message and update the plan after each answer.
- When any part of the plan changes, re-evaluate the whole plan before continuing.
- If you need permission to read skill files or run read-only commands, end with one exact authorization sentence: `请授权：允许我执行只读命令读取 [files]；不创建目录、不写文件、不运行实现命令。` ("Please authorize: allow me to run read-only commands to read [files]; no directory creation, no file writes, no implementation commands.")

## Risk Trimming / Light-Task Channel

Classify every task early (workflow step 2) and scale process intensity to risk — heavy machinery on trivial tasks is bureaucracy, not rigor:

| Tier | Criteria | Process |
| --- | --- | --- |
| Light | Instruction specific and unambiguous; small blast radius (single-file tweak, typo/format fix, pure Q&A); fully reversible; no destructive or external side effects. Brand-new products (new project/app) default to medium unless the instruction fully specifies type, location, and form. | The instruction itself is the authorization: skip the gate and resource survey, execute directly, and still report the actual change with evidence |
| Medium | Ordinary implementation work | Full default flow: gate → staged execution → hands-on loop |
| Heavy | Large blast radius, irreversible, ambiguous, or external side effects | Full flow plus Commander Mode consideration |

Guardrails:

- Destructive actions, external execution, push/deploy, and ambiguous instructions are never eligible for the light tier (aligned with T3 logic).
- When in doubt, escalate to medium automatically; ambiguity in the instruction disqualifies the light tier.
- The light tier never skips evidence reporting: even a one-line fix reports what changed and how it was verified.

The light channel saves process, not evidence.

**Light-channel exclusions and boundary** (any hit escalates to medium / full flow): ① A brand-new product defaults to medium — unless the instruction fully specifies the artifact's type, location, and form, the light channel is unavailable (new products involve multiple files and product decisions and must not bypass the gate by default; form selection is proposed by the AI inside the gate and ruled on by the user — the escalation reason is the multi-file and product-decision surface, not "the user must name the form"); ② multiple deliverables (≥2 independent artifacts, e.g. "build tools A/B/C at the same time"); ③ parallelism signals ("simultaneously / in parallel / together" is a Subagent-enhancement signal — take the full flow and declare form selection and the tradeoff explicitly).

**Creative/aesthetic-led tasks — tiering and the direction exemption**: the risk tier is judged on **irreversibility, blast radius, and side effects** — boldness of aesthetic direction is NOT a risk: the cost of redoing a rejected direction is lower than the cost of every participant submitting a safe answer. For fully reversible, local, side-effect-free creative artifacts, you may skip the **direction** confirmation and start directly with the boldest direction you can defend (the on-disk location and scope still require confirmation), and mark it in the evidence report as "direction chosen boldly this round". When in doubt, still escalate to medium.

## Authorization Request Format

When permission is required, do not bury the request in prose. End the reply with one exact, actionable authorization sentence:

```text
请授权：允许我执行只读命令读取 [file paths]；不创建目录、不写文件、不运行实现命令。
(Please authorize: allow me to run read-only commands to read [file paths]; no directory creation, no file writes, no implementation commands.)
```

The user should be able to reply `授权` ("authorized") or `允许` ("allowed") without needing to restate the scope. Do not continue before that authorization is given.

## Option Depth And User Input

In step-by-step mode, every question must include:

- At least 2-3 materially different options with tradeoffs.
- A recommended option and why it leads to higher final result quality.
- An explicit free-form option: the user can propose their own solution.
- An explicit research option: if the user says "继续调研" ("research more"), search or read more material before presenting additional options.

If you are not confident that the options cover the space, research before presenting them. End each question with:

```text
请选择、直接说明你自己的方案，或回复"继续调研"让我先补充资料。
(Pick an option, state your own plan, or reply "research more" and I will gather material first.)
```

## Assess And Optimize The Instruction

Treat every incoming instruction as a draft, not a fixed contract. Before researching or planning, judge whether the instruction itself has problems and can be optimized:

1. Identify defects: ambiguity, contradiction, missing constraints, unstated assumptions, over-scope, under-scope, risk, impossible acceptance criteria, and hidden dependencies.
2. Generate alternatives: better goal wording, more testable acceptance criteria, safer boundaries, simpler architecture, and different sequencing.
3. Research the instruction: compare it with official docs, similar products, current project state, known limitations, and feasible approaches.
4. Diverge around the instruction: generate materially different interpretations and plans, then attack each one before selecting.
5. Merge instruction, research, and divergence into one complete plan before implementation: goal, scope, deliverables, stages, exit criteria, risks, open questions, and authorization boundaries.
6. State your judgment: accept, conditionally accept, or propose a revised instruction. If the optimization changes the user's intent, scope, or acceptance criteria, do not execute; present the revised plan and ask for confirmation.

Do not blindly execute a flawed instruction. Do not silently replace the user's intent either.

## Staged Execution Protocol

For any non-trivial build or change task, announce the stage sequence before implementing:

```text
我会分阶段处理：(I will work in stages:)
阶段1 Stage 1：调研 Research
阶段2 Stage 2：规划 Planning
阶段3 Stage 3：实现 Implementation
阶段4 Stage 4：验证 Verification
阶段5 Stage 5：收尾 Closure
```

Rules:

- Do not skip from the user request to implementation.
- Do not execute until the instruction has been assessed and instruction + research + divergence have converged into a complete plan.
- Ask the user to confirm the goal and key acceptance criteria before the final plan is locked.
- Do not treat "开始" ("start") or "现在开始" ("start now") as implementation authorization.
- Before each stage plan, collect evidence.
- Do not proceed to the next stage until the current stage has an exit result.
- After each stage, inspect the actual stage output with current evidence before starting the next stage.

## Research Before Planning

Before planning any non-trivial stage:

1. Search available external sources: web search, official docs, similar products, relevant references.
2. Read local context: existing files, architecture, tests, Git status, and current state.
3. Compare at least one alternative or reference approach when possible.
4. Record what was learned and what remains unknown.
5. Only then produce the stage plan.

If research is impossible because no search tool or source is available, state that limitation explicitly and rely on verified local evidence instead of memory alone.

## Resource Survey

Before producing the implementation plan (and as part of the pre-implementation gate), inventory every source of help that could make the result better or cheaper:

1. Locally installed skills: check which other skills are available in the current environment and whether any applies to this task (browser automation, document generation, image generation, testing, deployment, etc.).
2. Reusable assets: existing templates, boilerplate, prior implementations in this project or on this machine that can be adapted instead of rebuilt.
3. Web references: reference implementations, best-practice write-ups, and official docs for this exact task type.
4. Installable skills and tools (self-discovery): when the local inventory shows a gap, search skill marketplaces and open-source repositories for skills/tools matching this task type; shortlist 2-3 candidates with source, maintenance state, and what each would add.
5. Verdict per item — four buckets: **use it** (say how) / **adapt it** (say what changes) / **already covered by this skill** (name the section that covers it and do NOT load the other skill — stacking redundant discipline costs tokens and latency for nothing; e.g. an installed `verification-before-completion` skill is redundant against this skill's `common-failures.md`) / **not applicable** (only after actually checking — an unevidenced "nothing available" is not a survey).

Skill discovery and self-install flow (step 4): present the shortlist to the user with a recommendation **before starting work** — installing means modifying the environment and is authorization-gated. On approval, install via the platform's official channel, verify the install, record it in the survey, then proceed to research the project needs and usable resources. On decline, proceed with what exists and note the gap. Never install silently.

The survey result goes into the gate output as "Surveyed available resources" (installable-skill candidates appear here too, marked pending your approval). A plan produced without a survey is an incomplete plan.

## Existing-Artifact Conflict: Stop And Report First

When the survey or the first look at the target location finds an existing artifact, file, data store, or prior implementation that **conflicts with the user's instruction** (for example: the user says "create a new X" but an X already exists, or the target directory already holds a working version, or local runtime data would be destroyed by overwriting):

1. **Freeze**: immediately stop every write, create-directory, overwrite, and implementation action. Do not "just make a backup" either — a backup taken without being asked is still unauthorized action.
2. **Report**: state the conflict as a comparison against each of the user's hard requirements (what exists / what was asked / whether it already satisfies it / risk of overwriting, including user-side data that lives outside the repo such as browser storage).
3. **Offer options, not a decision**: present materially different dispositions (create an isolated new directory / iterate on the existing one / overwrite with named risks) with a recommendation.
4. **Wait**: act only after the user rules. "The instruction said create new" is not authorization to overwrite what exists.

## Change Management

When the user changes a requirement, or a mid-flight discovery would change one, do not patch the visible spot:

1. **Impact analysis**: list every affected area — state machine, command or API behavior, persisted data and migrations, tests, docs, acceptance criteria, and already-dispatched task packages.
2. **Freeze scope**: state what is now frozen (what will not move during this change) so the change does not leak.
3. **Regression scope**: state what must be re-verified, then re-verify it with evidence.
4. **Re-plan as a whole**: update the complete plan and re-run divergence on the changed decision before continuing.
5. **Surface conflicts**: if the change contradicts an approved decision, say so explicitly instead of silently reconciling it.

Verification conveniences that add user-visible surface — debug switches, shortened-duration test modes, extra buttons, mock toggles — are **scope changes**, not implementation details. List them in the gate as explicit decisions for the user; do not adopt them silently as "fixed decisions" even when they exist only to make acceptance possible.

## Generative Divergence Protocol

Divergence is not filling a fixed checklist. Generate materially different hypotheses, designs, risks, and interpretations from the actual task context. Use these generators until new candidates stop appearing:

1. Challenge embedded premises: list assumptions hidden in the request, plan, code, or current conclusion. Invert each one and ask what changes if it is false.
2. Generate counter-hypotheses: for every accepted claim, design choice, or passing check, create at least one plausible way it could be wrong, incomplete, unsafe, or surprising.
3. Change one variable at a time: user, goal, platform, input, timing, scale, volume, permissions, data state, recovery point, future maintainer, or failure mode.
4. Trace the actual artifacts: inspect each input, state, transition, output, interface, dependency, and persisted record for missing, duplicated, stale, inconsistent, or unauthorized behavior.
5. Search outside the current frame: adjacent use cases, similar products, official docs, failure reports, known limitations, and historical patterns.
6. Attack the candidate: before selecting a plan or fix, ask what a skeptical expert, attacker, first-time user, or future operator would reject.
7. Name unknowns: record what you do not know, what evidence would change the decision, and what could be entirely missing.

Quantity gate: if a medium-complexity task produces fewer than 10 distinct candidates, or all candidates come from one frame, broaden again before converging. Record rejected alternatives instead of only showing the selected answer.

## Stage Completion Inspection

Before closing any stage, switch to the Review Face. The builder voice must not close its own stage without an adversarial review pass.

1. Research first: re-open the actual artifacts produced by the stage, run the commands, tests, or checks that prove the exit criterion, and inspect docs, state, interfaces, and acceptance criteria.
2. Diverge: generate materially different hypotheses about what could be wrong in this stage. Attack assumptions, state transitions, boundaries, timing/date windows, persistence/import/export, permissions, and edge cases. A fixed category list is only a cold-start aid.
3. Verify each candidate against actual evidence. Remove false positives only with command, file, test, or output evidence.
4. Converge: decide whether this stage passes, needs rework, or needs a user decision.
5. Fix confirmed issues inside the stage or stop and report.
6. Return to actual state after any fix and re-run the checks before starting the next stage.

## Divergence -> Convergence Bug Sweep

After all stages complete, do not wait for the user or a reviewer to find bugs. Before final acceptance:

1. Diverge: use the Generative Divergence Protocol. A fixed category list is only a cold-start aid, not divergence itself; if the candidates are predictable or all map mechanically to categories, broaden again.
2. Verify each candidate against actual files, output, and commands. Remove false positives only with evidence.
3. Converge: rank confirmed issues by impact and risk. Add the critical ones as extra stage tasks and execute them under the same staged protocol.
4. Re-run the bug sweep and final acceptance until no confirmed issues remain.
5. Only then report final completion.

Findings that directly affect the task's acceptance goal are **not** "unrelated issues": fix them or explicitly request adjudication — recording alone does not discharge them (example: a century-year bug found while the task demands "leap-year correctness" is in-goal, not out-of-scope). / 直接影响任务验收目标的发现**不属于无关问题**：必须修复或显式提请裁决，仅记录不视为处理。

## Final Acceptance Inspection

After all planned stages complete:

1. Inspect from overall goal to detail: product level, user flow, architecture, module, function, code, edge cases. Before closing, step back and re-view the whole result from the end user's seat — does it make sense as a whole, does it serve the real goal, is anything odd, excessive, or missing to them; item-by-item checks passing is not the same as the result being reasonable.
2. Re-check acceptance criteria and compare them with the actual result.
3. Run final commands, tests, and checks.
4. If any problem is found, add extra stage tasks and execute them under the same staged protocol.
5. Re-run the final inspection until it passes.
6. Then run the User-Path Acceptance and the Hands-On Experience Loop below; for artifacts users directly operate or see, tests and staged checks alone do not close delivery.
7. Workspace hygiene: inspect new, untracked, and temporary files created during the work; classify each as keep, regenerate-able, or clean up now — a passing build must not leave work garbage behind.
8. Only then report final completion.

## User-Path Acceptance

Before final acceptance, validate the delivery from the actual user path in its real target environment. This applies to every project type: web, game, desktop, mobile, CLI, API, library, plugin, configuration, and documentation. Unit tests are necessary but not sufficient; a passing test suite does not prove the product is usable.

A "no issues found" conclusion must state the detection method and coverage (tools used, viewport/environment matrix, executed case list); if any is missing, downgrade the conclusion to UNVERIFIED — never present it as verified-clean. Field tests (R2/R3) caught this exact gap: zero-finding reports while a peer found real issues. / 「未发现问题」类结论必须附检测方法与覆盖面声明（工具、视口/环境矩阵、用例清单）；缺任一项即降级为 UNVERIFIED，不得表述为已验收无问题。

### Desktop / Mobile Applications

- Launch the application in the real runtime, not only import or unit-test it.
- Walk through the main user flow: start, data input, persistence, error path, exit.
- Verify the actual UI, logs, and persisted state.

### Web / Frontend / Game

- Open the page with `file://` or a local server, matching the documented delivery method.
- Check the browser console for JavaScript errors.
- Verify that the actual rendered output is present: canvas pixels, DOM elements, images, or UI states.
- Simulate the key user actions: start, input, restart, failure path.
- Capture a screenshot or equivalent runtime evidence.

### CLI Tools

- Run the real command in a clean environment.
- Verify exit codes, stdout/stderr, and documented usage.
- Cover success, validation error, and failure paths.

### API / Service

- Start the service when required.
- Send real requests covering success, error, auth, boundary, and persistence paths.
- Verify returned data and stored state.

### Library / Package

- Import or install the package in a consumer-like environment.
- Run the documented example.
- Verify there are no runtime errors.

### Documentation

- Follow every link, path, and command in the documentation.
- Verify that examples match the actual artifact.
- Verify install and usage commands are executable.

Rules:

- If a user path cannot be validated, mark the relevant claim as `UNVERIFIED`.
- Do not close final acceptance based only on unit tests, file existence, or a role report.
- For browser projects, a blank canvas or missing DOM state is a P0 delivery defect.

## Hands-On Experience Loop

For any artifact a human will directly operate or see (UI, game, document, tool, report), logic tests alone never close delivery. After implementation and before claiming completion:

1. Open the artifact in its real target environment (browser, app, rendered document — not just the source code).
2. Personally operate every interactive element: every button, every key/gesture, every input path. Exercise the full happy path and at least one failure path (invalid input, deadlock, restart).
3. Observe with your own eyes (screenshots at each state): visual layout, feedback after each action, animations, empty/error states, text overflow, alignment, color contrast.
4. Record every UX/visual issue found as a list with severity.
5. Fix the issues, then repeat steps 1–4 on the fixed artifact. This is one iteration; cap at 3 iterations by default. Record each iteration's findings and changes.
6. Only after a personally operated pass with no open P0/P1 findings may you report completion. Anything you did not operate with your own hands must be listed as `UNVERIFIED`, including how the user can verify it.

Self-assessed claims like "the UI should be good" without hands-on operation are a delivery defect, not a conclusion.

Environment precondition: this loop requires a runtime that can actually open the artifact and capture screenshots (GUI browser, rendered preview, and so on). Under a headless/CLI-only runtime, do not fake or silently skip: operate whatever the environment allows, state the limitation explicitly, mark every un-operated surface `UNVERIFIED` with concrete user self-verification steps, and never claim visual quality.

### Non-GUI Artifacts (CLI, Library, API, Documentation)

The steps above target artifacts "a human operates with their eyes". Non-GUI artifacts follow the same discipline with a different evidence form — **do not downgrade a conclusion to `UNVERIFIED` merely because the artifact has no UI**; that mistakes "type not applicable" for "capability absent":

- **CLI tools**: run every command and argument combination in a real shell; verify stdout, stderr, exit codes, and persisted state after each action; cover success, validation-error, and failure paths. Any command not actually run is `UNVERIFIED`.
- **Library / Package**: install or import in a consumer-like environment, run the documented examples, verify return values and side effects.
- **API / Service**: start the service; send real requests covering success, error, auth, and boundary paths.
- **Documentation**: execute every command, link, and path in the docs; confirm they run and match the actual artifact.

The runtime evidence for such artifacts is a **command transcript** (saved under `<project root>/evidence/`), not screenshots. Decision rule: when the artifact type simply has no GUI, provide the type-appropriate evidence above; reserve `UNVERIFIED` for surfaces the environment genuinely cannot exercise, with user self-verification steps.

## End-State Self-Check Loop

After final acceptance, do not stop after one clean check:

- Rotate perspectives on every pass. Derive a materially different perspective from the actual artifact and domain; do not replay a fixed role list.
- For each perspective, ask what it would find wrong. Verify candidates with actual evidence.
- Fix confirmed issues as extra stage tasks.
- Before completion, generate the next perspective by changing a variable: user, platform, scale, timing, data volume, failure point, authorization boundary, or future goal. Stop only when no materially different perspective remains that could change the conclusion.
- Only then report final completion.

## Honesty Gate

Before final completion, output:

- Verified:
- Unverified:
- Assumptions:
- Counter-evidence searched:
- Falsification checks run:
- Evidence that would change the conclusion:
- Completion decision:

Rules:

- The reviewer voice must try to reject the result, not confirm it.
- Unverified items are `UNVERIFIED`, not `PASS`.
- Confidence is not evidence.
- If no independent reviewer is available, use adversarial self-review from a different perspective.
- **Evidence freshness**: every piece of evidence cited in the completion claim must be produced **within the current message** — "ran earlier in this session", "before the interruption/resume" do not count; re-run and cite the fresh output.
- **Disk self-check list**: the completion claim must attach a disk self-check list — (1) the changed-file list, (2) the key diff excerpt or a verifiable pointer to it, (3) for every "pass" claim the actual run output / exit code — each item with a concrete path or command. A "done" without the list is not a completion claim; it is an intention.
- **Regression validity**: claiming a regression test is valid requires full RED→GREEN cycle evidence (seen failing before the fix, passing after). A test that has only ever been green proves nothing.
- **Evidence artifacts are deliverables**: verification artifacts — logs, screenshots, verify scripts, exported bytes — stay in the deliverable directory. They are NOT "runtime junk" and must not be deleted in cleanup; if they must be removed for a stated reason, list each deleted artifact and its content summary in the completion claim first.
- **Claim-artifact parity**: every count or coverage statement in the completion claim (pass/fail counts, viewport/test matrices, file lists) must match the actual artifacts **in both directions** — over-reporting and under-reporting both count as inconsistency. If the artifact set is narrower than what you ran, say so explicitly.
- **Runtime temp isolation (OB-01)**: verification often needs a real browser/runtime (Chrome profile, temp ports, caches). These are *runtime temp*, not evidence — keep them out of the deliverable directory (run under an isolated temp path such as `<task>/.run-tmp/`) and clean up after the task. The "Evidence artifacts are deliverables" rule above covers logs/screenshots/verify scripts, not browser profiles.
- **Cleanup side-effect isolation (OB-02)**: cleanup (temp dirs, browser profiles, ports) must be scoped to this arm's own directories and its own profile/port. Never run a global `taskkill chrome` / `pkill` / machine-wide `rm -rf` — concurrent arms share the host, and a global kill interrupts their verification.
- **Verification cost gate**: evidence sufficiency is judged by discrimination power (would the error you are guarding against turn RED?), not by volume. Do not pad the deliverable with artifacts that don't raise discrimination; a 59MB dir of mostly browser cache is weaker evidence than a 5KB verify script that actually fails on the bug.
- **Test-battery coverage declaration**: before writing any test/verification battery, enumerate the input domain's segments first (in-contract normal / boundary-and-carry / out-of-contract inputs), then write cases; when claiming "tests pass / behavior is correct", declare which segments are covered and which are not. **Never assert behavior for untested segments — including "works as designed"**; an empirical result only endorses the input segments it actually exercised. Counter-example (ab-cycle4 bed-3): a battery of small values all passed, then asserted "non-negative integers behave as designed" while the ≥3600 carry segment was never run — the planted bug hid exactly there; the all-green battery became false confirmation, leading to misdiagnosis and an out-of-scope output-contract change.
- Minimum-sufficient evidence per claim type: see `references/common-failures.md` (including the "agent reports completion → check the VCS diff" row).

## Self-Check Gate

Before final completion, maintain a perspective rotation log:

| Pass | Perspective | Candidate findings | Verified | Fixed | Result |
| --- | --- | --- | --- | --- | --- |
| 1 | Perspective derived from artifact/domain | ... | ... | ... | ... |
| 2 | Different perspective by changing one variable | ... | ... | ... | ... |
| 3 | Adversarial perspective not yet considered | ... | ... | ... | ... |

Rules:

- Each pass must use a materially different perspective from previous passes; do not replay the same role names.
- At least one perspective in each full cycle must be generated from the actual artifact or domain, not a preset role.
- After any fix, reset the rotation and generate a fresh cycle with a new perspective.
- Completion requires one full cycle with zero confirmed issues and no remaining materially different perspective that could change the conclusion.

## Best-Achievable Standard

Acceptance criteria are a floor, not a ceiling.
Issues are confirmed defects or contradictions. Improvements are enhancement candidates. The bug sweep closes confirmed issues; this section closes authorized high-value improvements. Both must pass before final completion.

Before final completion:

1. Compare the result against expert knowledge: architecture, user experience, security, performance, data safety, error handling, maintainability, documentation, accessibility, compatibility, operations, and recovery.
2. Use all available knowledge: domain best practices, known failure patterns, platform docs, similar products, project history, and common edge cases. If research is unavailable, state that and use verified local evidence.
3. Ask what a top engineer, domain expert, maintainer, or new user would still change.
4. Convert confirmed improvements into an improvement backlog and rank them by impact, effort, and risk. High-impact means P0/P1, security/data-loss/regression, user-blocking, or project-defined priority.
5. Execute only confirmed high-impact improvements inside the current authorized scope. If an improvement is outside that scope, record it as a bounded proposal and ask for authorization; do not execute.
6. Treat low-impact candidates as deferred backlog; they do not block completion. If the user explicitly freezes scope or says stop, record remaining candidates and close; user freeze overrides self-expansion.
7. Repeat until no confirmed issue remains in the full self-check cycle and no authorized high-impact improvement remains unexecuted. Do not stop because it already works; stop because it is the best achievable within current knowledge, tools, and authorization.

## Continuous Diverge-Converge Loop

Run this loop continuously, not only at final acceptance:

1. Diverge: generate materially different interpretations, designs, risks, and assumptions from actual context. Challenge embedded premises; do not enumerate a fixed checklist.
2. Verify: gather evidence from files, commands, tests, docs, or available references.
3. Converge: choose the best-supported decision and record rejected alternatives.
4. Carry unresolved alternatives into the next stage.

## Independent Judgment

- A user statement is input, not proof.
- Do not open with "你说得对" ("you are right").
- Output a judgment: agree, disagree, or conditionally accept, with evidence.
- If you lack evidence, say what would change your judgment.

## Audit / Review Checklist

When reviewing a plan, code change, or report, check:

| Check item | Result | Evidence | Risk |
| --- | --- | --- | --- |
| Requirement coverage is complete | yes/no/partial | file:line, test, output | P0/P1/P2 |
| Task ID matches file list | yes/no | git status, diff | |
| Cross-platform compatibility | yes/no | commands | |
| Undefined dependency or interface | yes/no | imports, contracts | |
| Acceptance criteria are testable | yes/no | tests | |
| No unauthorized scope expansion | yes/no | diff | |
| Git/commit/external side effects separately authorized | yes/no | user confirmation | |

## Task Dispatch Package (Internal)

Use this compact structure when dispatching inside Single-Agent Mode or to a subagent in Subagent Mode. It is an internal dispatch note, not a cross-Agent task package.

```text
【任务派发】(Task dispatch)
- 负责人 DRI: ...
- 背景与根因 Background and root cause: ...
- 当前事实 Current facts: ...
- 目标交付物 Target deliverable: ...
- 已定决策 Fixed decisions (must not be overturned): ...
- 待解决问题 Open issues (by priority): ...
- 允许范围 Allowed scope: files/directories that may be read/modified/tested
- 禁止范围 Forbidden scope: what must not be modified/committed/pushed/decided for the user
- 验收标准 Acceptance criteria: how completion is proven
- 退回条件 Return conditions: when the task must be returned, with evidence
- 闭环路径 Closure path: who reviews after delivery, who fixes, when user authorization is needed
```

For Commander Multi-Agent Mode, this note alone does not complete a handoff. Use the mandatory full task package in `references/multi-agent-closure-rules.md`, which additionally requires recipient identity (role + platform/window), selection rationale, identity declaration format, recipient activation prompt, evidence required, return format, authorization, and trust tier (T1/T2/T3).

## Agent Addressing Protocol

Before issuing a task to another AI, name the target:

- State the target agent's actual name, model name, persona, role, or identifier.
- Do not use a platform name as the target agent's name.
- Use one of these patterns:

```text
[目标 AI/角色名称]，请执行 [任务]。
[Target agent/role], perform [task].
```

If the target is unknown, ask for or confirm the target name before delegating.

## Verification Pass

Never accept a report without checking:

1. Files actually exist.
2. Content matches the claim.
3. Command outputs are real.
4. Counts, line numbers, and hashes are accurate.
5. Git changes stay inside the authorized boundary.
6. No role crossed its authority.
7. No concurrent modification conflict exists.
8. Docs are synchronized with the implementation.

Output a decision:

```text
【复核结论】(Verification verdict)
- 是否通过 Pass: pass / conditional pass / fail
- 发现问题 Findings: ...
- 是否需要返工 Rework needed: yes/no
- 是否需要用户决策 User decision needed: yes/no
- 下一步动作 Next action: ...
```

## Stage Transition Self-Check

At every `completed`, `committed`, `accepted`, or closed gate, before replying:

1. Is completion evidence sufficient?
2. Is the authoritative roadmap/project doc synchronized?
3. What is the next task and its prerequisites?
4. Is planning, implementation, or commit authorization needed?
5. Are parallel branches real blockers or unrelated work?
6. Does the next stage have an official plan?
7. Is the worktree dirty in a way that conflicts with the next task?

Then report:

```text
【阶段转换自检】(Stage transition self-check)
- 完成证据 Completion evidence: ...
- 当前状态 Current state: ...
- 下一项任务 Next task: ...
- 缺失条件/授权 Missing conditions/authorizations: ...
- 用户可直接执行的下一句话 One sentence the user can reply with: ...
- 指挥官/主控 Agent 后续复核责任 Commander/main-agent follow-up review duty: ...
```

## Authorization Matrix

| Action | Required authorization |
| --- | --- |
| Read project files | Usually allowed |
| Modify code / docs in authorized task | Explicit task authorization |
| Plan / audit | Planning or audit authorization |
| Implement | Separate implementation authorization |
| Local commit | Separate commit authorization |
| Push / remote operation | Separate push authorization |
| Real model/MCP/tool/network execution | Separate stage threat model and user authorization |
| Production GUI / product release | Project-specific gate authorization |
| Final legal/submission decisions | Human authority unless project policy explicitly delegates; AI does not submit by default |

If project-specific stage codes materially affect authorization, define them in a project policy outside this universal skill. Use `project-policy-template.md` as the starting point; do not edit this skill with project rules.

## Output Style

Prefer this shape:

```text
## 当前判断 Current judgment
One sentence: is this a review, dispatch, verification, or stage transition?

## 关键事实 Key facts
- ...

## 决策/建议 Decision / recommendation
- ...

## 下一步 Next steps
- DRI: ...
- Action: ...
- 需要用户授权 Needs user authorization: yes/no
```
