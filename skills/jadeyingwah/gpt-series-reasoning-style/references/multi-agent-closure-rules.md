# Multi-Agent Closure Rules / 多 Agent 闭环规则

These rules make Commander Multi-Agent Mode reliable when independent roles, models, or sessions work on the same task. They are distilled from production multi-agent collaboration experience and are intentionally project-neutral.

这些规则用于让指挥官多 Agent 模式在多个独立角色、模型或会话协作时保持可靠。它们来自真实多 Agent 协作经验，已去掉项目专属内容。

## Identity Declaration / 身份声明硬规则

- Declaration cadence: declare on first entry into the project or task, on role change, on formal handoff, or whenever identity could be confused — one concise line is enough. Once the role is established and unambiguous, per-response repetition is not required.
- Format: `身份：<角色名> / 任务 ID <ID>。`
- Roles are decoupled from the carrying model: changing the model, platform, or session does not change a role's duties, permissions, or handoffs. The declaration states who is speaking (role + task); routing metadata (role + platform/window, underlying model optional) belongs to the task package and the project AI identity registry, not to the identity itself.
- At the declaration moments above, a role may not respond with `收到`, `明白`, `开始`, or another identity-less reply.
- Use an existing task ID when present; a routine task without one is not blocked by it and must not be force-numbered.
- When returning from another role, re-declare the current identity and report the previous role's unfinished or overreach state.
- If the task is unclear after the declaration, request the task ID or task package instead of guessing.
- Role identities are mutually exclusive. A role may not switch identity to take over another role's responsibilities. Mutual exclusion binds behavior, not just the declared label: a role that never switches its declared identity may not perform another role's actions (e.g. an executor issuing a final acceptance verdict). Overreach is detected by the commander's evidence review, not by self-reporting.
- Before declaring identity, cross-check it against the task package's Recipient identity field. If they differ, stop and report both (任务包 = X / 声明 = Y) and mark work in flight UNVERIFIED until resolved.
- If the user corrects a role's identity, that role must stop current work and re-declare the correct identity.
- If the host already injects identity automatically, the duplicate declaration may be omitted — but only when the injected value is the role + task ID. A bare model or session name (e.g. “You are <model>”) does not qualify, because roles are decoupled from the carrying model; treat per-host injection content as UNVERIFIED until tested with that host.

规则：

- 声明节奏：首次进入项目或任务、角色变化、正式交接、或身份可能混淆时声明——一行简洁说明即可；角色已确立且无歧义时，不要求每条回复重复声明。
- 格式：`身份：<角色名> / 任务 ID <ID>。`
- 角色与承载模型解耦：更换模型、平台或会话，不改变角色职责、权限和交接关系。身份声明标识"谁在说话"（角色+任务）；路由元数据（角色+平台/窗口，底层模型可选）属于任务包与项目 AI 身份登记表，不属于身份本身。
- 在上述声明时点，不得输出“收到/明白/开始”等省略身份的回应。
- 已有任务 ID 时沿用；普通任务没有 ID 不得因此阻塞，也不必强行编号。
- 从其他角色切回时，必须重新声明当前身份，并报告旧角色的未完成状态或越权状态。
- 身份声明后任务仍不明确时，请求任务 ID 或任务包，不得自行猜测。
- 角色身份互斥；不得通过切换身份接管其他角色的职责。互斥约束的是行为而不只是声明标签：一个从未切换声明身份的 AI，也不得执行其他角色的动作（例如执行者给出最终验收判定）。越权由指挥官的证据核验发现，不依赖越权者自我举报。
- 声明前必须先对照任务包的 Recipient 身份字段自检；不一致时停止并同时报告（任务包 = X / 声明 = Y），挂起中的产物标 UNVERIFIED，解决前不得继续。
- 用户纠正身份时，立即停止当前动作并重新声明正确身份。
- 宿主已自动注入身份时才能省略重复声明，但仅当注入的是「角色 + 任务 ID」；只注入模型名/会话名（如 You are <model>）不构成豁免——角色与承载模型解耦。各宿主注入内容在逐宿主实测登记前一律按 UNVERIFIED 对待。

## Command Succession / 指挥权接管

指挥官失联、超载或不可用时，指挥权可以移交，但**不是自动发生的**：

1. **授权**：接替必须由用户明确授权（副总指挥/备份指挥官身份是候选，不是许可）。未获授权前，任何角色都不得以"总指挥不在"为由自行派发或验收。
2. **接管声明**：接管时声明接管范围、期限与已接手任务清单（未闭环项、待授权项、已派发未返回项）。
3. **记录**：接管与交回都写入派发台账，状态可追溯。
4. **交回**：原指挥官恢复后，交回指挥权并做状态交接；不得出现两个同时生效的指挥权。
5. **不越权**：接管只转移指挥权，不转移其他角色的 DRI 职责；执行者仍不能自任最终验收审计员。

指挥权接管 ≠ 角色身份切换：前者是用户授权的指挥权移交，后者是被禁止的越权行为。

**Command succession (EN)**

Command may be transferred when the commander is unreachable, overloaded, or unavailable, but it is **not automatic**:

1. **Authorization**: the succession must be explicitly authorized by the user (a deputy or backup commander identity is a candidacy, not a permission). Without authorization, no role may dispatch or accept on the grounds that "the commander is away".
2. **Succession declaration**: when taking over, declare the scope, the duration, and the list of tasks taken over (unclosed items, items pending authorization, items dispatched but not yet returned).
3. **Record**: both taking over and handing back are written into the dispatch ledger so the state stays traceable.
4. **Hand back**: once the original commander returns, hand command back and perform a state handover; two simultaneously effective commands must never exist.
5. **No overreach**: succession transfers command only, not another role's DRI responsibility — an executor still may not appoint itself the final acceptance auditor.

Command succession ≠ role identity switching: the former is a user-authorized transfer of command, the latter is prohibited overreach.

## Responsibility Closure / DRI 责任闭环

- The user is the final approver. The commander is the default DRI and final closure owner.
- Delegation does not transfer final responsibility.
- One task has one DRI. Auditors and contributors cannot use their role to bounce the task back.
- If a delegated role returns an objection or blocker, the commander must choose one path:
  1. Supplement the task package and continue with the same DRI.
  2. Reassign to a new unique DRI.
  3. Take over directly.
  4. Confirm a genuine user-only blocker with evidence.
- The fix-loop counter is anchored to the logical deliverable and shared across all roles and forms: reassigning the DRI, switching form, or taking over directly does NOT reset it. Any takeover path must declare the inherited round count (继承已用轮数：N). Round N+1 after a takeover is still round N+1 of the same deliverable.
- Never end a response with only `等待某角色处理`. State DRI, deliverable, completion condition, review duty, and next action.
- Audit opinions are input, not responsibility transfer. The commander deduplicates, verifies, prioritizes, and converts them into an executable fix list.
- If a plan revision is delegated, the commander provides complete context, immutable decisions, unresolved gaps, and acceptance criteria, then reviews the result.

规则：

- 用户是最终批准人；总指挥是默认 DRI 和最终闭环负责人。
- 委派不转移最终责任。
- 一个任务只有一个 DRI；审计或建议角色不能借此把任务弹回。
- 接收方退回或提出异议时，总指挥必须选择：补齐任务包继续、改派唯一 DRI、亲自接管、或确认必须由用户决定的真实阻塞。
- 修复循环计数器锚定逻辑交付物、全形态共享：改派 DRI、切换形态或亲自接管都不重置计数。任何接管路径必须声明继承的已用轮数（继承已用轮数：N）；接管后的第 N+1 轮仍是同一交付物的第 N+1 轮。
- 不能只回复“等待某角色处理”，必须给出 DRI、交付物、完成条件、复核责任和下一步。
- 审计意见是输入，不是责任转移；总指挥负责去重、核验、定级并形成可执行修整清单。
- 委派计划修订时，总指挥必须提供完整前因后果、不可变决策、待解缺口和验收标准，并在修订后亲自复审。

## Task Package / 强制任务包

A complete task package must include (23 fields — the authoritative count; do not cite 24):

```text
Recipient:
Recipient identity (role + platform/window — underlying model optional reference):
Why this recipient:
Identity declaration format:
Recipient activation prompt:
Task ID:
Command / instruction:
Goal:
Background / root cause:
Current facts:
Scope:
Non-goals:
Fixed decisions:
Open questions:
Allowed scope:
Forbidden scope:
Acceptance criteria:
Evidence required:
Return format:
Return conditions:
Closure path:
Authorization:
Trust tier:
```

If any required field is missing, the handoff is not complete.

任务包必须包含以上字段；信息不完整时不得宣称已完成交接。

`Evidence required` must name a concrete landing path under the project root (e.g., `<项目根>/evidence/`); the commander creates the evidence directory in the project skeleton when it creates the root, or the package's Scope explicitly assigns its creation to the executor. Evidence without a designated landing path invites phantom files — claims of screenshots that exist nowhere on disk.

`Evidence required` 必须给出项目根之下的具体落盘路径（如 `<项目根>/evidence/`）；总指挥创建项目骨架时一并建证据目录，或在任务包 Scope 里显式把该目录的创建指派给执行者。没有指定落盘位置的证据，就是在邀请"幽灵文件"——声称存在、盘上没有的截图。

For user relay, `Recipient activation prompt` must tell the receiving model to load the Skill, use Commander Multi-Agent Mode, adopt the assigned identity, and then execute the task package. Without this prompt, a new receiving session may not know which Skill, mode, or identity to use.

用户转交时，“接收方启动提示词”必须告诉接收模型：加载本 Skill、使用指挥官多 Agent 模式、采用指定身份，然后再执行任务包。缺少这个提示词，新会话可能不知道使用哪个 Skill、模式或身份。

**Manual multi-window relay / 手动多窗口转交的低门槛入口**：没有子 Agent 工具、需要人在窗口间粘贴时，允许先用**五字段降级简化包**（目标 / 范围 / 验收标准 / 返回格式 / 信任层级，见 agent-modes「Recipient Downgrade」）启动接收方，正式 23 字段任务包在登记接收方后补齐——降级只减 briefing 复杂度，不减验收标准。

`Recipient` must be concrete before the task package is complete: name the role and platform/window (e.g., `IDE 内置 AI 窗口执行者` / `网页对话窗口执行者`). Values such as `待用户指定`, `待确认`, or a bare "另一个 AI" make the handoff incomplete. The underlying LLM model/version is optional reference metadata — record it if known, never require it, and never let a model change invalidate a package or ledger row.

`Recipient activation prompt` must be a self-contained copy-paste text: include the exact Skill version, the mode, the identity, and the identity declaration format.

任务包生成前必须确定接收方：写清角色与平台/窗口（如 `IDE 内置 AI 窗口执行者` / `网页对话窗口执行者`）；"待用户指定"、"待确认"或笼统的"另一个 AI"属于任务包不完整。底层大模型/版本为可选参考元数据——知道就记，不强制，模型变动不使任务包或台账失效。

接收方启动提示词必须是可直接粘贴的完整文本，包含具体 Skill 版本、模式、身份和身份声明格式。

**Brief file / 简报文件化（推荐默认）**：23 字段任务包一经用户确认，指挥官把它**落盘为简报文件**（默认 `<项目根>/docs/plans/<task-id>-brief.md`，与派发台账同批留档）；接收方启动提示词只带三样东西——加载指令、身份声明格式、简报文件路径。接收方一次 Read 读到完整任务包，任务文本**不再经控制器/用户上下文逐字中转**。收益：①长任务包不占对话轮次，省中转 token；②简报文件即派发留档，append-only 可审计；③接收方丢上下文/续会时重读文件即可恢复。用户明确要求直接粘贴任务包全文时，从其指令。/ **Brief file (recommended default)**: once the 23-field package is confirmed, the commander writes it to a brief file (default `<项目根>/docs/plans/<task-id>-brief.md`, archived with the dispatch ledger); the activation prompt carries only the loading instruction, the identity declaration format, and the brief file path — the recipient reads the full package in one Read, and the task text never transits the controller/user context verbatim. Saves relay tokens, doubles as an append-only dispatch record, and survives context loss. If the user explicitly asks for the full package pasted inline, follow the user.

**Commander capability gate / 指挥官能力门**：升级/启用指挥官扩展声明「能力缺口」时，必须附两条证据，缺一不启动：① 缺什么能力、当前会话有什么反证（如需要真实浏览器而会话无浏览器工具）；② 目标接收方身份文件路径。无证据时拒绝启动扩展，标 UNVERIFIED 并回退单 Agent 主干。子 Agent 模式与指挥官扩展的证据要求对称，避免「能力缺口」涉为展示多 Agent 的自我声明。

## Project AI Identity Registry / 项目 AI 身份登记

Commander Multi-Agent Mode is not a solo mode. Before generating a user-relay task package, the commander must confirm that actual recipient AIs exist.

Registry location is project-scoped: `<项目根>/docs/agents/`, the Mode 3 plan `<项目根>/docs/plans/`, and the dispatch ledger `<项目根>/docs/agents/dispatch-ledger.md` all live under the project root — never in the commander's own workspace. If the project root does not exist yet at gate time, create it (and `docs/agents/`) after gate approval, or have the executor create the root first and write governance files immediately after; state which path was chosen.

身份目录与治理产物以项目为根：`<项目根>/docs/agents/`、模式三计划 `<项目根>/docs/plans/`、派发台账 `<项目根>/docs/agents/dispatch-ledger.md` 一律放在项目根之下，绝不放进总指挥自己的工作区——项目找不到的治理文件等于不存在。若门禁时项目根尚未创建：门禁获批后由总指挥先建项目根与 `docs/agents/`，或让执行者先建根、总指挥随后立即写入，并向用户说明选了哪条路。

## Mode 3 Direct Execution Shortcut / 模式三直接执行短路

If the user confirms that only the current model is available and chooses direct tools, skip the project AI identity registry and recipient activation prompts. The model still follows Mode 3 confirmation and implementation gate rules, but it does not create `docs/agents/`, does not select recipient roles, and does not generate prompts for new conversation windows.

如果用户确认当前只有当前模型可用，并选择直接工具，则跳过项目 AI 身份目录和接收方启动提示词。模型仍按模式三的确认和实现前门禁执行，但不创建 `docs/agents/`、不选择接收方角色、不生成新对话窗口提示词。

Rules:

1. Ask the user where the project AI identity directory is located.
2. If the user provides a path, use it even if it is not the default.
3. If the user does not know or says there is no such directory, propose creating one with the default ASCII path `docs/agents/` and ask for authorization.
4. If the user authorizes creation, the registry is a **per-member identity file layout**: a registry README (index) plus **one standalone identity markdown file per AI member** (e.g., `docs/agents/executor.md`). Each member file must include role identity, responsibilities, current platform/channel, trust tier, task status, DRI ownership, and whether it is available for this task. The underlying LLM model is **never asked for** — record it only when the user volunteers it or it is publicly evident; it churns and must never invalidate a record. A bare brand or product name alone is not enough; name the role and platform/window.
5. **Commander reads before dispatching**: before the first relay to any member, the commander reads that member's identity file and adapts communication and task-package framing to it.
6. **Recipients read their own file first**: every activation prompt instructs the recipient to read its own identity file under `<项目根>/docs/agents/` and declare its identity before executing the task package.
7. If the user denies authorization, explain why Mode 3 needs the registry and return `BLOCKED`; do not create the directory and do not generate a placeholder task package.
8. If no other AI is registered, ask the user what project or task to work on first.
9. Assess task difficulty and select the smallest suitable role set, such as:
   - Simple task: executor.
   - Medium task: executor + reviewer + acceptance-auditor.
   - Complex or high-risk task: add architect, QA/test engineer, security tester, or documentation consistency reviewer as needed.
10. Register the selected roles in the AI identity directory with role identity, platform/channel, current model (optional reference), task status, and availability.
11. For each registered recipient, generate a standalone activation prompt that loads the Skill, selects Mode 3, assigns the identity, and includes the task package. The user opens a new conversation window for each recipient and pastes that prompt.
12. Do not treat the task as dispatched until the user confirms the recipient windows are created and the prompts have been relayed. If the user cannot create them, return `BLOCKED`.
13. Persist Mode 3 plans in the project docs, such as `docs/plans/`, before dispatch. A plan only in chat is not a project plan.

规则：

- 指挥官多 Agent 模式不是单人模式。生成用户转交任务包前，必须确认实际接收方存在。
1. 先问用户项目 AI 身份目录在哪里。
2. 用户指定路径时，即使不是默认路径也沿用。
3. 用户不知道或说没有时，先提出创建默认 ASCII 路径 `docs/agents/`，并请求授权。
4. 用户授权创建后，登记目录采用**每个 AI 成员一个身份 md 文件**的结构：登记 README（索引）+ **每个成员独立的身份 md**（如 `docs/agents/executor.md`）。成员文件包含角色身份、职责、平台/通道、信任层级、任务状态、DRI 归属和是否可承接本次任务。底层大模型**从不主动询问**——仅在用户主动告知或公开可得时记录；它容易变动，且绝不使记录失效。只写品牌名或产品名不够，应写清角色与平台/窗口。
5. **指挥官派发前先读**：对任一成员的首次传话前，指挥官先读取该成员的身份 md，并据此适配沟通方式与任务包表述。
6. **接收方先读自己的文件**：每份启动提示词都指示接收方先读取自己在 `<项目根>/docs/agents/` 下的身份 md、声明身份，然后再执行任务包。
7. 用户拒绝授权时，说明模式三为什么需要身份目录，并返回 `BLOCKED`；不创建目录，不生成占位任务包。
8. 没有其他已登记 AI 时，先问用户本次要做什么项目或任务。
9. 评估任务难度，并选择最小且合适的角色集，例如：
   - 简单任务：执行者。
   - 中等任务：执行者 + 审查者 + 验收审计员。
   - 复杂或高风险任务：按需增加架构师、测试工程师、安全测试员或文档一致性审查员。
10. 在 AI 身份目录中登记所选角色，记录角色身份、平台/通道、当前模型（可选参考）、任务状态和是否可承接。
11. 为每个登记接收方生成独立启动提示词：加载 Skill、选择模式三、分配身份，并包含任务包。用户为每个接收方新建一个对话窗口并粘贴该提示词。
12. 用户确认接收方窗口已创建且提示词已转述后，才可视为已派发；用户无法创建时返回 `BLOCKED`。
13. 模式三计划应写入项目根之下的 `docs/plans/`（不是总指挥自己的工作区）；只在对话里出现不算项目计划。

## File Ownership and Access / 文件所有权与访问隔离

- Each role reads only its own identity file and the task package assigned to it.
- A role must not enumerate other role files or infer access from file names.
- One file can have only one writable DRI at a time.
- When multiple roles touch the same artifact, state who reads, who writes, and who does final review.
- Reviewers are read-only by default. If a reviewer sees overreach, preserve the output and hand it to the correct DRI; do not blindly roll back.

规则：

- 每个角色只读取自己的身份文件和分配给自己的任务包。
- 不得通过枚举其他角色文件或文件名推断来扩大权限。
- 同一文件同一时间只能有一个可写 DRI。
- 多角色涉及同一产物时，明确谁读、谁写、谁最终复核。
- 审查者默认只读；发现越权时保留产物并交正确 DRI 接管，不贸然回滚。

## Pre-Dispatch Conflict Ledger / 派发前冲突账本

Before dispatching parallel agents, scan which tasks share the same file, interface, or module. Emit a ledger table instead of claiming "no conflict":

| Task pair / Task | Shared file/interface | Writable DRI | Ruling |
| --- | --- | --- | --- |
| T-A ↔ T-B | src/auth.py | T-A only / conflict | ... |
| T-C (self) | src/db.py | T-C only | OK |

- One row per task pair that shares a file/interface, and one row for each task's self-consistency.
- If two tasks need write access to the same file, assign one writable DRI and make the other read-only or sequential.
- The ledger is an artifact; "scan is clean" without the table is not evidence.

派发并行 Agent 前，先扫描哪些任务共享同一文件/接口/模块，输出账本表而非口头声称"无冲突"：每对共享文件的任务一行，每个任务自洽性一行。若两个任务都要写同一文件，只分配一个可写 DRI，另一个改为只读或串行。账本是产物；没有表的"扫描干净"不算证据。

## Authorization Separation / 授权分离

- Planning, implementation, local commit, push, real network/model/MCP execution, production deployment, and legal/submission decisions are separate authorizations.
- No destructive or external action may run without explicit user authorization.
- Tool availability is not user authorization. A platform having direct tools or subagent capability does not confirm a dispatch path.
- The user's latest explicit decision takes precedence over approved documents, plans, implementation, and history.
- Authority order when sources conflict: 1. the user's current explicit instructions, authorizations, and prohibitions; 2. role permission boundaries; 3. the project's authoritative specs, roadmap, confirmed decisions, and actual artifacts; 4. other role files and approved task packages; 5. historical conversations, old plans, old states, style files, and case libraries.
- Contradiction triage: when authoritative documents conflict, verify facts first and give a recommendation; fix what can be fixed within the authorized scope directly; escalate to the user only for product direction, high-risk external actions, or substantive ambiguity.
- `已记录` is not `已派发`; `已派发` is not `已转述`; `已转述` is not `已执行`.

规则：

- 规划、实现、本地提交、推送、真实网络/模型/MCP 执行、生产部署和法律/提交决定是独立授权。
- 未获用户明确授权，不得执行破坏性或外部操作。
- 工具可用不等于用户授权；平台有直接工具或子 Agent 能力，不代表派发通道已被确认。
- 用户最新明确决定优先于已批准文档、计划、实现和历史记录。
- 权威来源冲突时的优先级：1. 用户当前明确指令、授权和禁止事项；2. 角色权限边界；3. 项目权威规格、路线图、已确认决策与实际产物；4. 其他角色档案与已批准任务包；5. 历史对话、旧计划、旧状态、风格文件与案例库。
- 矛盾分流：权威文档相互矛盾时，先核验事实并给出推荐处理；授权范围内能消除的直接消除；只有涉及产品方向、高风险外部动作或实质歧义时才请求用户裁决。
- “已记录”不等于“已派发”，“已派发”不等于“已转述”，“已转述”不等于“已执行”。

## Context Discipline / 上下文纪律

- Send each recipient only the context relevant to its role.
- Do not dump the full repository, full history, or all identity files into every agent.
- Use indexes, search, and minimal call chains to reduce unnecessary context.
- A task package must be self-contained enough for the recipient to act, but not bloated with unrelated material.
- Evidence by pointer, not by paste: full tool outputs and long logs go to disk or artifact files; returns carry paths, key excerpts, and verdicts. Trimming machine-generated bulk (logs, JSON, search dumps) is allowed; trimming user decisions, task packages, and human content is never allowed. When in doubt, keep the original — lost savings are acceptable, lost correctness is not.

规则：

- 只给接收方与其角色相关的上下文。
- 不要把整个仓库、全部历史或所有身份文件灌给每个 Agent。
- 使用索引、搜索和最小调用链减少无关上下文。
- 任务包应足够自包含，但不堆入无关材料。
- 证据用指针不用粘贴：完整工具输出与长日志落盘（或产物文件），返回只带路径、关键摘录和结论。允许裁剪机器生成的批量内容（日志、JSON、搜索转储）；用户决策、任务包与人的内容永不裁剪。拿不准就保留原文——可省 token，不可省正确性。

## Stage Transition Closure / 阶段转换闭环

After a stage closes, report:

- Completion evidence.
- Current status.
- Next task and its prerequisites.
- Missing condition or authorization.
- The exact sentence the user can reply with.
- The commander's review responsibility for the next handoff.

Do not silently wait after declaring completion. Distinguish a true blocker from an independent parallel branch.

规则：

- 阶段结束后必须报告：完成证据、当前状态、下一任务、缺失条件/授权、用户可直接回复的句子、总指挥后续复核责任。
- 不能声明完成后静默等待；必须区分真实阻塞和无关并行支线。

## Consolidation (Fan-In) / 合并与冲突裁决

After parallel recipients return, the commander consolidates before closure:
- Collect each recipient's return (file paths, commands, test output, screenshots).
- Validate deliverables against each task's acceptance criteria from the task package.
- Merge outputs; if multiple recipients touched shared concerns, reconcile conflicts using the pre-dispatch conflict ledger and the single writable DRI per file.
- Generate a consolidation summary: what each recipient delivered, conflicts found and how resolved, remaining gaps.

并行接收方返回后，总指挥在闭环前先合并：收集各自产物；对照任务包验收标准校验；合并输出，若多接收方涉及同一关切，依据派发前冲突账本与"每文件单一可写 DRI"裁决冲突；产出合并小结（各方交付、冲突与解法、残留缺口）。

## Findings Ledger / 发现账本

A findings ledger is the escalation artifact required when a fix loop reaches its cap. It is a first-class governance file, sibling to the dispatch ledger under the project root (e.g. `<project root>/docs/agents/findings-ledger.md`). Required fields per round:

- Round number / 轮次编号
- What changed and why / 本轮改动与原因
- Unresolved items / 未解项
- Evidence pointer (path + key excerpt) / 证据指针（路径 + 关键摘录）

An empty or field-less ledger does not satisfy an escalation.

发现账本是修复循环耗尽时的升级产物，与派发台账同级、放在项目根下（如 `<project root>/docs/agents/findings-ledger.md`）。每轮必填字段：轮次编号、本轮改动与原因、未解项、证据指针（路径 + 关键摘录）。空账本或无字段清单不视为合规升级。

**All ledgers live in one place / 三本账一处安家**：all governance ledgers live under `<项目根>/docs/agents/` — the dispatch ledger and the form-change ledger share **one file** (`dispatch-ledger.md`，形态变更记入派发台账的行项)；the findings ledger is a **sibling file** in the same directory (`findings-ledger.md`)，只在修复循环触顶时创建。治理心智成本 = 一个目录、两个文件。

## Fix-Loop Cap / 修复循环上限

A review-fix loop (recipient returns, commander verifies, returns for fix) is bounded:
- Cap at 5 rounds per logical deliverable. On the 5th unresolved round, escalate to the user with the findings ledger; do not loop silently.
- One near-closure buffer: if the 5th round has a real fix but one acceptance item is still missing, the commander may request round 6 with the findings ledger; a user approval resets the counter to a buffer round (max once per deliverable).
- Each round records what changed and why. Rounds are judged by an observable delta, not by someone's internal act of reading: each return must state this round's material changes (file diff / command output / line numbers) plus what changed since last round. A return with no delta is invalid and counts against the cap. Exception: a return that explicitly states "reviewed, no change needed" and attaches review evidence is exempt from the delta requirement, does not count against the cap, but must still be recorded. The commander verifies only delta existence, never the unobservable read-or-not.

审查-修复循环（接收方返回→总指挥核验→打回修复）设上限：每逻辑交付物最多 5 轮，全形态共享、接管继承已用轮数；第 5 轮仍未解则升级给用户并附发现账本，不得静默空转。
- 近闭环缓冲（每交付物最多一次）：第 5 轮已给出真实修复、仅差一项验收时，指挥官可凭发现账本请求第 6 轮，用户批准后改为缓冲轮。
- 每轮记录改动与原因。轮次有效性以可观测的 delta 判定，不依赖某人内部的读没读：每轮返回必须陈述本轮实质变化（文件 diff / 命令输出 / 行号）以及相对上一轮的差异；无 delta 的返回无效且计入上限；例外：返回明确声明「复核后确认无需改动」并附复核证据时，不受 delta 要求约束、不计入上限，但仍须记录。指挥官只做 delta 存在性检查，不做不可观测的读没读判定。

## Anti-Patterns / 反模式

- Responding without an identity declaration.
- Switching identity to take over another role.
- Bouncing tasks between roles.
- Ending with `等待某角色处理` without DRI and next action.
- Allowing multiple writable roles to modify the same file.
- Sending full context to every recipient.
- Treating audit opinions as responsibility transfer.
- Treating one authorization as permission for all later actions.
- Recording a task as dispatched before the user confirms relay.

规则：

- 不声明身份就回复。
- 切换身份接管其他角色。
- 任务在角色之间反复弹跳。
- 只用“等待某角色处理”结束回复。
- 多个可写角色同时修改同一文件。
- 给每个接收方灌入完整上下文。
- 把审计意见当作责任转移。
- 把一次授权当作后续所有操作的授权。
- 用户确认转述前就记为已派发。
