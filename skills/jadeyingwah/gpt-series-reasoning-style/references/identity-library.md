# Identity Library / 身份库契约

This reference defines how role identities are stored, selected, adopted, and maintained in Commander Multi-Agent Mode. It is a behavior contract, not a list of job titles.

本参考文件定义指挥官多 Agent 模式下角色身份如何存储、选择、采用和维护。它是行为契约，不是岗位列表。

## Role Presentation / 身份出示

Before outputting 【角色身份确认】, read `identities/README.md` and present each candidate role with a one-line responsibility. A list of role names is not enough for the user to make an informed choice.

输出【角色身份确认】前，先读取 `identities/README.md`，并给每个候选身份附上一行职责说明。只列角色名不足以让用户做出选择。

Use a compact table or short list. Do not dump all role names inside a code block or repeat the same headings across every message.

使用紧凑表格或短列表。不要把所有角色名放进代码块，也不要在每条消息里重复相同标题。

The role identity confirmation itself must not be wrapped in a code block. Use a plain Markdown table, labels, or short bullets.

角色身份确认本身不得用代码块包裹；使用普通 Markdown 表格、标签或短列表呈现。

## Built-in Role Quick Reference / 内置身份速查

`identities/README.md` is the canonical catalog. Role names, file names, and one-line responsibilities are maintained only there, so the list cannot drift across references.

`identities/README.md` 是权威目录。角色名、文件名和一行职责只在该文件维护，避免清单在多个参考文件之间漂移。

Read it before presenting, selecting, or dispatching roles, and point to it instead of restating the catalog here.

出示、选择或派发角色前先读取它，并指向该文件，不要在这里重复列出角色清单。

Custom user identities are stored in `custom-identities/` (Chinese: 其他身份) and must be read before adoption.

用户自定义身份存放在 `custom-identities/`（中文名：其他身份），采用前必须读取。

## Role File Contract / 身份文件契约

Every identity file under `identities/` should contain these sections:

```text
Identity
Mission
Responsibilities
Process
Required Output
Handoff
Boundaries
Anti-Patterns
```

Rules:

- A role is valid only when it has a required deliverable and a verifiable output.
- A role name is not proof that the role was performed. The model must read the identity file before claiming the role.
- The host agent's identity, platform rules, and permission boundaries take precedence over any task role.
- Custom identities are stored in `custom-identities/` (Chinese: 其他身份) and must be read before adoption.
- If no matching identity exists, the model must state the gap honestly instead of faking a loaded role.

规则：

- 角色只有在拥有必需交付物和可验证输出时才有效。
- 角色名不能证明角色已执行；模型必须先读取身份文件，才能声称采用该角色。
- 宿主模型的身份、平台规则和权限边界优先于任何任务角色。
- 自定义身份存放在 `custom-identities/`（中文名：其他身份），采用前必须读取。
- 没有匹配身份时，必须诚实说明缺口，不能伪造已加载身份。

## Role Selection / 角色选择

1. Read `references/commander-roles.md` before selecting roles.
2. Start from the smallest role set that can complete and verify the task.
3. Name one DRI per task; the commander remains the default closure owner.
4. Every role must have a clear deliverable, evidence requirement, and boundary.
5. Review roles are read-only unless explicitly authorized to modify.
6. Do not add a role just because it sounds useful. A role without a required output is role bloat.
7. For every dispatched recipient, specify the recipient identity (role + platform/window) and why that recipient was selected; the underlying LLM model is optional reference metadata.
8. Read `references/multi-agent-closure-rules.md` before dispatching work; it defines identity declarations, DRI closure, file ownership, authorization, and context discipline.

## Dispatch Role Assignment / 派发角色分配

Before generating a task package:

- Decide which role set is needed: for example, executor for implementation, reviewer for review, acceptance-auditor for final validation.
- Assign one identity to each recipient.
- Name the recipient by role and platform/window (e.g., `IDE 内置 AI 窗口执行者` / `网页对话窗口执行者`); a generic "另一个 AI" alone is not enough. The underlying LLM model/version is optional reference metadata — record it if known, never require it, and never let a model change invalidate a package.
- Do not leave the recipient identity pending; if it is unknown, ask the user before generating the task package.
- Ask the user for the project AI identity registry path before dispatch; use a user-provided path, propose `<项目根>/docs/agents/` if none exists, and return `BLOCKED` if creation is denied.
- Governance artifacts are project-scoped: registry `<项目根>/docs/agents/`, Mode 3 plan `<项目根>/docs/plans/`, dispatch ledger `<项目根>/docs/agents/dispatch-ledger.md`. Never place them in the commander's own workspace — a governance file the project cannot find does not exist. **The registry belongs to the project being worked on: reusing another project's identity directory (for example a different project's `docs/项目AI身份/`) is not an acceptable option**, even if the user proposes it — governance must sit beside the work it governs, and offering that as an option is itself a governance defect.
- When the task package requires file-based evidence (screenshots, exports, logs), the project skeleton includes the evidence directory (`<项目根>/evidence/`) — created by the commander with the root, or explicitly assigned to the executor in the package Scope. Evidence must land somewhere before it can be verified.
- If the project root does not exist yet at gate time: after gate approval, either create the project root and `docs/agents/` yourself (authorized by the approval) or assign the executor to create the project root first and write governance files immediately after — state which path you chose.
- Registry layout is **one standalone identity markdown file per AI member** (e.g., `docs/agents/executor.md`) plus a registry README index; each member file carries role, responsibilities, platform/channel, trust tier, DRI ownership, availability for this task, status, and current task.
- Before the first relay to any member, the commander reads that member's identity file and adapts communication and task-package framing to it.
- Every activation prompt instructs the recipient to read its own identity file under `<项目根>/docs/agents/` and declare its identity before executing the task package.
- **Never ask the user what underlying model an AI member uses.** Record a model only when the user volunteers it or it is publicly evident; it is optional reference metadata that must never block or invalidate a registry record or task package.
- If the user confirms only one AI is available and chooses direct tools, skip the registry and recipient activation prompts; Mode 3 confirmation and gate rules still apply.
- If no recipient AI is registered, ask what project/task to work on, select the smallest suitable role set, register those roles, and generate a standalone activation prompt for each recipient to open a new conversation window.
- Explain why that recipient is best suited for the task, such as tool access, demonstrated capability, or independence from the implementer.
- Require the recipient to read its identity file before adopting the assigned role.
- Include a self-contained recipient activation prompt so a new session knows to load the Skill version, use Mode 3, adopt the assigned identity, and then execute the task package.

- 决定需要哪些角色，例如执行者负责实现、审查者负责审查、验收审计员负责最终验收。
- 给每个接收方分配一个明确身份。
- 接收方按"角色 + 平台/窗口"命名（如 `IDE 内置 AI 窗口执行者` / `网页对话窗口执行者`）；笼统的"另一个 AI"不够。底层大模型/版本是可选参考元数据——知道就记，不强制，模型变动不使任务包失效。
- 接收方身份不得留空或写"待确认"；不知道时先问用户，再生成任务包。
- 派发前先问用户项目 AI 身份目录路径；用户提供就沿用，没有则提出 `docs/agents/`，拒绝创建则返回 `BLOCKED`。
- 用户确认只有当前模型可用并选择直接工具时，跳过身份目录和接收方提示词；模式三确认和门禁规则仍然适用。
- 没有已登记接收方时，先问项目/任务，按难度选择最小角色集并登记，再为每个接收方生成可粘贴到新对话窗口的启动提示词。
- 说明为什么选择该接收方，例如工具能力、模型能力或与实现者保持独立。
- 要求接收方在采用角色前读取对应身份文件。
- 包含可直接粘贴的接收方启动提示词，明确 Skill 版本、模式三、指定身份，再执行任务包。

## Universal Output Protocol / 通用输出协议

Every adopted role should return:

- An identity declaration at the declaration moments (first entry into the task, role change, formal handoff, or possible confusion): role and task ID, unless the host already injects this information automatically. Roles are decoupled from the carrying model; the model/session lives in the task package and the identity registry, not in the declaration. Once the role is established and unambiguous, per-response repetition is not required.
- Actual artifacts: file paths, commands run, test output, screenshots, API responses, or logs.
- A confidence signal:
  - `CONFIDENCE: High, <one-line reason>` when output is complete and evidence-backed.
  - `CONFIDENCE: Medium, <assumption>` when output is reasonable but has a stated assumption or gap.
  - `CONFIDENCE: Low, <reason>` when context is insufficient for a reliable result.
- A blocked signal instead of a guess:
  - `BLOCKED: <reason>, <what would unblock>`

Claims without artifacts are not evidence. A summary is not evidence. Unverified conclusions are marked `UNVERIFIED`.

每个采用角色的回复在声明时点（首次进入、角色变化、交接、可能混淆）声明：角色、任务 ID；角色已确立后不必每条回复重复，模型/会话不属于声明内容。

## Trust Tiers / 信任层级

When dispatching work, assign a trust tier to every task:

| Tier / 层级 | Type / 类型 | Required Before Acting / 执行前要求 |
| --- | --- | --- |
| T1 | Research and analysis / 调研分析 | Use directly after evidence review; no separate confirmation needed. |
| T2 | Artifacts and file writes / 产物与文件写入 | Show the plan or output to the user and obtain confirmation before writing. |
| T3 | Commands, deployments, destructive or external actions / 命令、部署、破坏性或外部操作 | Explicit per-action user authorization. |

## Finding Severity / 发现严重度（P0/P1/P2）

Review- and audit-type findings are graded with these definitions (used by `reviewer`, `code-reviewer`, `documentation-consistency-reviewer`, and the fix-loop). This table is the single authority for severity labels.

| Severity / 严重度 | Definition / 定义 | Handling / 处置 |
| --- | --- | --- |
| P0 | Would cause wrong execution, data/credential leakage, security incidents, or irreversible damage. / 会导致错误执行、数据或凭据泄露、安全事故或不可逆损坏。 | Fix immediately; block delivery until resolved. / 立即修复，修复前不得交付。 |
| P1 | Violates the skill's discipline or produces wrong results, without security or irreversible impact. / 违反本 skill 纪律或产生错误结果，但不涉及安全与不可逆。 | Fix before delivery. / 交付前修复。 |
| P2 | Quality, consistency, or maintainability improvement. / 质量、一致性或可维护性改进。 | Record as backlog; non-blocking. / 记入 backlog，不阻塞交付。 |

If a task produces both T1 and T2 output, classify it as the higher tier.

## No-Match Identity / 无匹配身份

If the user asks for a role not in `identities/`:

1. State clearly that no matching built-in identity exists.
2. Check `custom-identities/`; if a custom identity exists, read it.
3. Ask whether the user wants to provide a custom identity file or content.
4. If the user wants to proceed without a custom identity, use the closest generic role and mark it as improvised or approximate.
5. Never present a generic role as a loaded specialist identity.

## Identity Drift / 身份漂移

If a role's observed behavior starts to diverge from its identity file, the task output is invalid until resolved:

- Re-read the identity file and compare it with the actual behavior.
- Identify whether the issue is missing context, missing evidence, or scope overreach.
- Correct the behavior or ask the user for a custom identity update.
- Record the drift only if it changes a deliverable, evidence, or boundary.

## Anti-Patterns / 反模式

- Claiming a role without reading its identity file.
- Choosing all roles for every task.
- Making reviewers also the final acceptance auditor.
- Accepting a recipient's summary as verified evidence.
- Treating `CONFIDENCE: High` as a substitute for actual artifacts.
- Silently improvising a specialist identity when no matching identity exists.
- Allowing role bloat to hide missing responsibilities.
- Using role names as a perspective-rotation log in final review.

## Related Files / 相关文件

- `references/commander-roles.md`: role tables and smallest role set by project size.
- `references/agent-modes.md`: mode rules and task package format.
- `references/multi-agent-closure-rules.md`: identity mutual exclusion, DRI closure, file ownership, the pre-dispatch conflict ledger, consolidation (fan-in), the fix-loop cap, authorization separation, and context discipline.
- `identities/`: built-in identity files.
- `custom-identities/`: user-provided identity files.
