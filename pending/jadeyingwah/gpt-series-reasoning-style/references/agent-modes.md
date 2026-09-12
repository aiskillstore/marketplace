# Execution Modes / 执行模式

This skill supports three execution modes.

本 Skill 支持三种执行模式。

## Mode Summary / 模式总览

协作架构 = **单 Agent 主干 + 两个按需扩展**，可按任务/阶段混合搭配。/ Collaboration architecture = a Single-Agent backbone plus two on-demand extensions, mixable per task or stage.

| 形态 / Form | Description / 说明 |
| --- | --- |
| Single-Agent backbone / 单 Agent 主干 | Default. One model uses Planning, Execution, and Review as internal role faces; most tasks complete here. |
| Subagent enhancement / 子 Agent 增强 | When the host has subagents and the task benefits from parallelism or isolation, map role faces to subagents; the main model keeps the gate, evidence ownership, and final acceptance. Pass the capability gate before engaging. |
| Commander extension / 指挥官扩展 | Engage per task when coordinating independent large models or agents via direct tools, external sessions, or user relay is needed. Follows Mode 3 confirmation, task-package, and closure rules while scoped to that task. Subagent tools are not required but may be used. |

形态由 AI 按任务自选（判定顺序见下节），在门禁里声明选择与一行理由；用户可随时指定或改判，**用户指名的形态永远优先**。

## Mode Self-Selection / 模式自选（按任务判定，不等问题问）

形态不是等用户点菜的默认项，而是 AI 自己根据任务事实选的。**判定顺序自上而下，首个命中即停**：

1. **轻量通道**：指令具体、影响面小、完全可逆、无副作用 → 直接执行并报告证据（不涉及形态选择）。**排除项**（命中任一即升中档、走全流程做形态选择）：从零新建产物未完整指定类型/位置/形态；多交付物（≥2 个独立产物）；并行信号（"同时/并行/一起做"）。创意/审美主导任务另有**方向豁免**（判据与边界见 series-reasoning-workflow.md 风险分档节：审美大胆不是风险；完全可逆产物可免方向确认，落盘路径与范围仍须确认）。
2. **指挥官扩展**（任一命中即触发）：
   - 用户明确说实现交给其他 AI、另一个窗口、或要多模型协作；
   - 任务需要当前会话不具备的能力，且存在具备该能力的其他 AI（例如：需要真实浏览器逐项验收而本会话没有浏览器工具）；
   - 用户明确要求独立第三方验收。
   → 声明"选择指挥官扩展 + 一行理由"；**仍须依次过角色身份确认、协调通道确认、实现前门禁**——自选形态不豁免任何确认。
   **三道确认约束的是「派发动作」，不是「草案产出」**：门禁未过不得派发、不得转交；但**缺必需字段的正式任务包同样不得产出**——接收方角色/平台窗口未知时先问清楚，不以「待用户指定」占位、不臆造接收方。因此"生成一个任务包"的一次性请求，若没给接收方与通道，正确行为是**先问缺的字段**，而非先出一份不完整的包。
   **裁决链（任务事实缺口 vs 用户指名）**：用户指名的形态与任务事实缺口（例如需要实测浏览器而会话无工具）冲突时，按授权顺序第 1 条（用户当前明确指令优先）执行用户指名；仅子 Agent 能力门失败时可回退单 Agent 并标 UNVERIFIED，其余缺口以一句「缺口仍存在，我按你的指名执行，但该缺口未消除」上报。
3. **子 Agent 增强**（全部满足才触发）：
   - 宿主有子 Agent 工具（能力门）；
   - 任务含**真正独立的并行分支**（分支间不共享文件与接口）；
   - 并行收益 > 拆分与简报成本（每个分支值得一份六字段迷你包）；**用户使用"同时/一起做"等并行信号时，这条成本判断必须在形态选择理由中显式写出**——命中信号却选择不并行，理由必须给出成本依据，不得默认略过；
   - 不需要外部模型或外部窗口参与。
   → 声明"选择子 Agent 增强 + 一行理由"；能力确认与门禁照走。
4. **其余一律单 Agent 主干**：内部三面完成，不派发、不转交、不拆分。

**通用纪律**：

- 自选 = **建议**，不是静默决定：门禁输出必须包含"形态选择 + 一行理由"，用户一句话即可改判；**用户指名的形态永远优先**（能力门失败时除外——回退单 Agent 并标 `UNVERIFIED`，见能力门规则）。
- **形态选择 ≠ 实现授权**：选了任何形态，该走的确认门禁一个不少。
- 判定依据必须来自任务事实（能力缺口、分支独立性、用户的信号），**形态升级需要任务理由，降级不需要**——不得为了"展示多 Agent 能力"而升级形态。
- **单任务形态变更账本 + 升级冷却**：同一任务内每次形态变更记入派发台账（行项包含时间、从何形态→到何形态、理由）；指挥官扩展在同一任务内累计启用第 2 次及以后必须附累计理由并请用户确认；降级后的下一次形态选择不得升回同一形态，除非用户明确要求（含“乒乓式升降级”绕过升级需理由的情形）。

**Mode self-selection (EN)**

Form is not a menu item waiting for the user to order; the AI selects it from task facts. **The evaluation order is top-down; the first match stops the search:**

1. **Light channel**: the instruction is specific, the blast radius is small, fully reversible, no side effects → execute directly and report evidence (no form selection involved). **Exclusions** (any hit escalates to the medium tier and runs the full flow with form selection): a brand-new deliverable whose type/location/form is not fully specified; multiple deliverables (≥2 independent artifacts); parallelism signals ("simultaneously / in parallel / do these together"). Creative/aesthetic-led tasks have a separate **direction exemption** (criteria and boundary in the workflow Risk-Trimming section: boldness of aesthetic direction is not a risk; fully reversible artifacts may skip the direction confirmation — on-disk location and scope still require confirmation).
2. **Commander extension** (any hit triggers it):
   - The user explicitly says the implementation goes to another AI, another window, or that they want multi-model collaboration;
   - The task needs a capability this session lacks, and another AI with that capability exists (for example: real-browser item-by-item acceptance while this session has no browser tool);
   - The user explicitly requests independent third-party acceptance.
   → declare "commander extension selected + one-line reason"; **role identity confirmation, coordination channel confirmation and the pre-implementation gate still apply, in order** — self-selecting a form exempts no confirmation.
   **Those three confirmations gate the DISPATCH action, not drafting**: nothing may be dispatched or relayed before the gates pass, but an incomplete task package with missing mandatory fields must not be produced either — when the recipient role/platform-window is unknown, ask for it first; never use a "to be specified by the user" placeholder and never invent a recipient. So for a one-shot "generate a task package" request that supplies neither recipient nor channel, the correct behaviour is to **ask for the missing fields first**, not to emit an incomplete package.
   **Adjudication chain (task-fact gap vs user-named form)**: when a user-named form conflicts with a task-fact gap (for example a real browser is needed but the session has no such tool), follow authorization order item 1 (the user's current explicit instruction wins) and execute the user-named form; only a failed subagent capability gate may fall back to single-agent and mark `UNVERIFIED`; other gaps are reported in one sentence: "the gap still exists; I proceed as you named, but the gap remains unresolved".
3. **Subagent enhancement** (all conditions must hold):
   - The host has subagent tools (capability gate);
   - The task contains **genuinely independent parallel branches** (the branches share no files and no interfaces);
   - Parallelism payoff > the cost of splitting and briefing (each branch deserves a six-field mini package); **when the user uses parallelism signals such as "simultaneously" or "do these together", this cost judgment must be written explicitly into the form-selection reason** — hitting the signal yet choosing not to parallelize requires a cost basis in the reason and must not be silently skipped;
   - No external model or external window is involved.
   → declare "subagent enhancement selected + one-line reason"; capability confirmation and the gate still apply.
4. **Everything else is the single-agent backbone**: finish with the three internal faces — no dispatch, no relay, no splitting.

**General discipline (EN)**

- Self-selection is a **recommendation**, not a silent decision: the gate output must include "form selection + one-line reason", and the user can overrule it in one sentence; **a user-named form always wins** (except when the capability gate fails — fall back to single-agent and mark `UNVERIFIED`, see the capability gate rules).
- **Form selection ≠ implementation authorization**: whichever form is chosen, every confirmation gate still applies.
- The basis must come from task facts (capability gaps, branch independence, user signals); **escalating a form requires a task reason, de-escalating does not** — never escalate a form just to "show off multi-agent capability".
- **Per-task form-change ledger + escalation cool-down**: record every form change within one task in the dispatch ledger (row items: time, from-form → to-form, reason); the commander extension, when enabled a cumulative 2nd time or later within the same task, must attach the cumulative reason and ask the user to confirm; the next form selection after a de-escalation must not return to the same form unless the user explicitly asks for it (this closes the "ping-pong escalate/de-escalate" bypass of the escalation-requires-a-reason rule).


## 1. Single-Agent backbone / 单 Agent 主干（默认）

- One model handles Planning, Execution, and Review internally.
- No subagents are required.
- No external agents are dispatched.
- Default when no extension is warranted by the scenario or requested by the user.

- 单个模型在内部处理规划面、执行面、审查面。
- 不需要子 Agent。
- 不派发外部 Agent。
- 场景不需要扩展时使用此主干——AI 按任务自选并声明一行理由；用户指名的形态优先。

## 2. Subagent Mode / 子 Agent 模式

An on-demand enhancement of the Single-Agent backbone: engage when the scenario warrants it (see Engagement Criteria), passing the capability gate first. 主干之上的按需增强：场景符合判据时启用，先过能力门禁。

仅当宿主支持子 Agent 时可用；启用前先用一句话向用户说明启用理由。

### Mandatory Capability Gate / 强制能力确认

Before entering Subagent Mode, output:

在进入子 Agent 模式前，先输出：

```text
【子 Agent 能力确认】
- 可用子 Agent 工具/接口：...
- 配置/文档证据：...
- 是否真实可调用：是 / 否 / UNVERIFIED
- 结论：可进入子 Agent 模式 / 不可进入，回退单 Agent 模式
```

Rules:

- Subagent capability is determined by the host tools, configuration, or documentation, not by the model's claim or the user's statement.
- If the current session has no real subagent tool or configuration evidence, do not enter Subagent Mode.
- With no evidence, fall back to Single-Agent Mode and mark capability as `UNVERIFIED`.
- If the user says the model has subagent capability but no tool is available, do not pretend to dispatch subagents.

规则：

- 子 Agent 能力由宿主工具、配置或文档决定，不由模型自称或用户口头声明决定。
- 当前会话没有真实子 Agent 工具或配置证据时，不能进入子 Agent 模式。
- 没有证据时回退到默认单 Agent 模式，并将能力状态标记为 `UNVERIFIED`。
- 用户说“你有子 Agent 能力”但当前会话没有工具证据时，不能假装派发子 Agent。

### Engagement Criteria / 启用判据

拆分给子 Agent 前，先过这道判据—— briefing 成本高于收益就不拆：

- **值得拆**：存在 ≥2 个互相独立的并行分支；需要上下文隔离（如独立审查视角）；需要专门角色面处理专项工作。
- **不拆**：顺序依赖的单文件工作；任务本身比 briefing 还小；拆分只是"显得并行"。

**Engagement criteria (EN)** — run this test before splitting work out to subagents; if the briefing cost exceeds the payoff, do not split:

- **Worth splitting**: ≥2 mutually independent parallel branches exist; context isolation is needed (for example an independent review perspective); a dedicated role face is needed for specialized work.
- **Do not split**: sequentially dependent single-file work; the task itself is smaller than the briefing; the split would only "look parallel".

### Subagent Mini Task Package / 子 Agent 迷你任务包

子 Agent 不用 23 字段完整包（那是跨模型指挥官场景的），用**六字段迷你包**，缺一不发：

1. **目标**：要产出什么。
2. **范围与非目标**：只做哪些文件/事项，明确不许碰什么。
3. **验收标准**：怎样算做完，可验证。
4. **所需证据**：返回哪些文件路径/命令输出/截图。
5. **返回格式**：结论先行 + 证据指针（不粘贴大段日志）+ `CONFIDENCE` 或 `BLOCKED`。
6. **信任层级**：T1 只读 / T2 可写产物。T3（命令/部署/破坏性或外部操作）属指挥官扩展（23 字段包）场景——子 Agent 迷你包限 T1/T2。

**Six-field mini package (EN)** — subagents do not use the full 23-field package (that belongs to cross-model commander scenarios); they use the **six-field mini package**, and a missing field means no dispatch:

1. **Goal**: what to produce.
2. **Scope and non-goals**: which files/items to touch, and explicitly what must not be touched.
3. **Acceptance criteria**: what counts as done, stated verifiably.
4. **Required evidence**: which file paths / command outputs / screenshots to return.
5. **Return format**: conclusion first + evidence pointers (no large pasted logs) + `CONFIDENCE` or `BLOCKED`.
6. **Trust tier**: T1 read-only / T2 may write deliverables. T3 (commands, deployments, destructive/external) belongs to the Commander extension's 23-field package; subagent mini packages are limited to T1/T2.

The mini package is the subagent-channel standard; attaching a full 23-field package to a subagent is acceptable but not required — package size follows the channel, not the mode label. 迷你包是子 Agent 通道的标准配置；给子 Agent 附 23 字段完整包可以，但非必需——包规格跟随通道，不跟随模式标签。

### Failure Fallback / 失败止损

- 子 Agent 返回不合格：打回一次，附具体发现；仍不合格则**收回主干自己做**并在报告里记录——委派是加速器，不是沉没成本黑洞。
- 打回与 23 字段场景共用"修复循环上限 5 轮"的纪律（近闭环缓冲可延至第 6 轮——见 multi-agent-closure-rules 的 Fix-Loop Cap）。

**Failure fallback (EN)**

- A subagent returns substandard work: return it once with the specific findings; if it is still substandard, **take the work back onto the backbone and do it yourself**, and record this in the report — delegation is an accelerator, not a sunk-cost black hole.
- Returns share the "fix-loop cap of 5 rounds" discipline with the 23-field scenario (a near-closure buffer may extend to a 6th round — see the Fix-Loop Cap in multi-agent-closure-rules).

### Orchestrator Submode / 编排子模式（推荐）

- Main model owns Planning, Review, whole-plan re-evaluation, and final acceptance.
- Execution subagents receive complete task packages and return artifacts with evidence.
- A separate Reviewer subagent is optional but recommended.

- 主模型负责规划、审查、整体再规划和最终验收。
- 执行子 Agent 接收六字段迷你包（需要更完整边界时用内部派发包），并带回产物和证据；完整 23 字段包用于跨模型指挥官场景。
- 可选的独立审查子 Agent 负责对抗性审查。

### Three-Role Submode / 三角色子模式

- Planner subagent produces a complete plan but does not implement.
- Executor subagent implements and returns evidence.
- Reviewer subagent reviews actual artifacts and returns findings.
- Main model coordinates, owns user confirmation, the pre-implementation gate, and final acceptance.

- 规划子 Agent 只产出完整计划，不实现。
- 执行子 Agent 实现并返回证据。
- 审查子 Agent 审查实际产物并返回结论。
- 主模型负责协调、用户确认、实现前门禁和最终验收。

### Subagent Boundaries / 子 Agent 边界

- The main model is the default DRI and final closure owner.
- The user confirmation and pre-implementation gate must pass before any subagent creates directories or edits files.
- A subagent may not close a stage, accept final delivery, or replace user decisions.
- Every subagent must return actual artifacts and evidence, not just a summary.
- A Reviewer must read or run the real artifacts before reporting findings.

- 主模型是默认 DRI 和最终收口负责人。
- 任何子 Agent 创建目录或编辑文件前，必须先通过用户确认和实现前门禁。
- 子 Agent 不能关闭阶段、接受最终交付或代替用户决策。
- 每个子 Agent 必须返回实际产物和证据，不能只交总结。
- 审查者必须先读取或运行实际产物，再报告发现。

## 3. Commander Mode / 指挥官多 Agent 模式

Use for medium and large projects when the user chooses Commander Mode. This mode does not require subagent tools, but subagents may be used. It can cover the direct-tool path of Mode 1 and the subagent path of Mode 2 while adding Mode 3 governance. It suits any model and is recommended for stronger models that can maintain whole-plan control and final acceptance. Simple one-shot tasks should not use this mode.

适用于用户选择指挥官模式的中大型项目。此模式不要求子 Agent 工具，但可以使用；可覆盖模式一的直接工具路径和模式二的子 Agent 路径，同时增加模式三的治理规则。适合任何大模型，推荐由能力更强的大模型担任总指挥；装配本 Skill 的模型也可作为执行者、审查者、计划者等其他角色参与多 Agent 协作。简单一次性任务不应使用此模式。

Before dispatch, ask the user where the project AI identity registry is. Use a user-provided path; if none exists, propose `docs/agents/` and request authorization; if authorization is denied, return `BLOCKED`. If the user confirms only one AI is available and chooses direct tools, skip the registry and recipient prompts and proceed under Mode 3 confirmation and gate rules. If no recipient AI is registered and user relay is required, ask what project/task to work on, select the smallest suitable role set, register those roles, and generate a standalone activation prompt for each recipient to paste into a new conversation window. Do not generate a task package with `待用户指定` or `待确认`.

派发前先问用户项目 AI 身份目录在哪里；用户指定路径就沿用，没有则提出 `docs/agents/` 并请求授权，拒绝授权则返回 `BLOCKED`。如果用户确认只有当前模型可用并选择直接工具，则跳过身份目录和接收方提示词，仍按模式三确认和门禁执行。如果没有已登记接收方且需要用户转交，先问项目/任务，按难度选择最小角色集并登记，再为每个接收方生成可粘贴到新对话窗口的启动提示词；不得生成带“待用户指定/待确认”的任务包。

### Mandatory Role Identity Confirmation / 强制角色身份确认

Before entering Commander Mode, the model must confirm which role identity it will adopt. Commander Mode may use subagents, external agents, or user relay, but the current model must first have a clear role identity.

进入指挥官模式前，模型必须先确认自己采用哪个角色身份。模式三可以使用子智能体、外部 Agent 或用户转交，但当前模型必须先有明确的角色身份定位。

Output:

输出：

```text
【角色身份确认】
- 内置身份及职责：先读取 identities/README.md，给每个候选身份附 1 行职责说明，再让用户选择
- 可选内置身份：先读取 identities/README.md（权威角色目录），逐条呈现全部内置身份并各附一行职责，再让用户选择或确认——不要在此硬编码身份清单（当前 21 个，硬编码必然漂移）。
- 用户指定身份：...
- 其他身份文件路径：...
- 是否已读取身份文件：是 / 否
- 结论：以 <角色名> 身份进入模式三
```

The template above is a field checklist, not literal formatting. Render the required fields naturally with short sentences or a compact table; do not copy the template into every message. Role identity confirmation and coordination channel confirmation must not be wrapped in code blocks.

上面的模板是字段清单，不是逐字格式。请用短句或紧凑表格自然呈现必需字段，不要每条消息都复制模板；角色身份确认和协调通道确认不得用代码块包裹。

Rules:

- Built-in identities are in `identities/`.
- Custom identities are in `custom-identities/` (Chinese: 其他身份).
- If the user has no preference, default to `commander`.
- Do not claim a role without reading the identity file.
- Output role identity confirmation and stop. Wait for explicit user confirmation of the identity, even when the default is `commander`; do not proceed to the next gate by yourself.
- Do not present role names only. Read `identities/README.md` or `references/commander-roles.md` and show a one-line responsibility for each candidate before asking the user.
- Read `references/identity-library.md` for the universal role contract, trust tiers, and confidence protocol.
- If no built-in identity matches, check `custom-identities/`; if still absent, state the gap honestly and ask for a custom identity or permission to use the closest generic role with a caveat.

规则：

- 内置身份位于 `identities/`。
- 自定义身份位于 `custom-identities/`（中文名：其他身份）。
- 用户没有指定时，默认采用 `commander`。
- 未读取身份文件前，不能声称已经采用该角色。
- 输出角色身份确认后必须停止，等待用户明确确认身份；即使默认是 `commander`，也不能自行进入下一步。
- 不能只列角色名。先读取 `identities/README.md` 或 `references/commander-roles.md`，给每个候选身份附一行职责说明，再询问用户。
- 身份库契约、信任层级和置信度协议见 `references/identity-library.md`。
- 没有匹配的内置身份时，先检查 `custom-identities/`；仍不存在时诚实说明缺口，询问用户提供自定义身份，或获准后用最接近的通用角色并标记近似。

### Mandatory Coordination Channel Confirmation / 强制协调通道确认

Before entering Commander Mode, output:

在进入指挥官模式前，先输出：

```text
【指挥官协调通道确认】
- 派发方式：直接工具 / 外部会话 / 用户转交 / 其他
- 接收方：...
- 接收路径是否已确认：是 / 否
- 结论：可进入指挥官模式 / 需要用户确认派发通道
```

Rules:

- Commander Mode does not require subagent tools, but subagents may be used when the host supports them.
- Direct tools, external sessions, CLI/API, and user relay are all valid dispatch paths.
- Platform tool availability is not user confirmation. The user must explicitly choose the dispatch path.
- Before the user confirms the dispatch path, do not mark the path as confirmed and do not proceed to the implementation gate.
- If the user chooses user relay, do not replace it with direct tools or subagents.
- Commander Mode suits any model; stronger models are better suited to whole-plan control, evidence verification, conflict resolution, and final acceptance.
- If dispatch is user relay, the commander must not assume the user has relayed the task package. Ask: "Have you relayed this to <recipient>?"
- Only after the user confirms relay may the commander treat the task as dispatched.
- If no dispatch path is confirmed, stop and ask the user which path to use; do not start external work silently.

规则：

- 指挥官模式不要求子 Agent 工具，但宿主支持时可以使用。
- 直接工具、外部会话、CLI/API 和用户转交都是有效派发方式。
- 平台有直接工具或子 Agent 能力，不等于用户已确认使用该通道；必须由用户明确选择派发方式。
- 用户未确认派发通道前，不得把通道标记为已确认，也不得进入实现前确认。
- 用户选择用户转交后，不得擅自改用直接工具或子 Agent 代替。
- 指挥官模式适合任何大模型；模型能力越强，越能承担整体规划、证据核验、冲突裁决和最终验收。
- 如果采用用户转交，总指挥生成完整任务包后，不得假设用户已经转述；必须先问“你是否已转述给 <接收方>？”。
- 用户明确回答“已转述”后，才可把任务状态视为已派发。
- 没有确认派发通道时，停止并询问用户采用哪种派发方式，不能擅自启动外部工作。

The model using this skill is the commander. Other agents are not subagents of the same model; they are independent recipients with their own identities, platform rules, and capabilities.

装配本 Skill 的模型默认可作为总指挥，也可作为其他角色。其他 Agent 不是同一个模型的子 Agent，而是拥有各自身份、平台规则和能力的独立接收方；当前模型采用哪个角色由【角色身份确认】决定。

### Channel Self-Check / 通道能力自查（先于一切派发）

协调通道确认之前，先做一次**自查**：我对每个接收方，有没有**直接沟通能力**？

1. 逐接收方列出可直接沟通路径：直接工具 / 子 Agent 框架 / MCP / API / 共享会话——必须有证据，像能力门禁一样。
2. 有直接路径且用户同意 → 直接派发，省去传话。
3. **没有直接路径 → 用户转交**：为每个接收方生成自包含的启动提示词（复制即可动手），并明确告诉用户回收方式（"把它的回答原样粘贴回来"）。用户转交的每一跳都由人搬运，延迟和损耗真实存在——任务包更要一次写全，减少来回。

通道决策按接收方逐个定，记入派发台账；用户可随时改通道。

**Channel self-check (EN)** — before the coordination channel confirmation, run a **self-check** first: for each recipient, do I have **direct communication capability**?

1. For each recipient, list the direct communication paths available: direct tool / subagent framework / MCP / API / shared session — evidence is mandatory, exactly as with the capability gate.
2. A direct path exists and the user agrees → dispatch directly and skip the relay.
3. **No direct path → user relay**: generate a self-contained activation prompt for each recipient (copy and start), and tell the user explicitly how the results come back ("paste its answer back verbatim"). Every hop of a user relay is carried by a human, so delay and loss are real — the task package must therefore be written completely in one pass to reduce round trips.

Channel decisions are made per recipient and recorded in the dispatch ledger; the user may change the channel at any time.

### Answer Handling / 回答接手协议（收到回答后做什么）

经任何通道收到接收方的回答后，按此序列处理（顺序即纪律）：

1. **自洽检查**：返回的数字与结论互相矛盾时，当场拒收其"可验收"声明——"20 项通过、1 项待修整"不等于"可最终验收"。声称存在的证据文件必须先做**存在性检查**（列目录/查找）：报告里写着 `evidence/02.png` 而磁盘上没有，整个"已完成"声明作废。
2. **亲自核验关键项**：对关键/存疑项读实际文件、跑实际命令，定位到文件:行号；总结不是证据。
3. **三分裁决**：接受闭环 / 打回（附文件:行号级的精确修复指令）/ 标记 `UNVERIFIED`（说明缺什么）。
4. **更新派发台账**：状态按 已返回 → 待修整 → 已闭环 推移。
5. **生成下一轮可转述文本**：自包含，接收方拿到即可动手，不需要用户再解释。
6. **给用户一句可直接回复的话**：继续 / 打回 / 升级，由用户裁决下一步。

**Answer handling (EN)** — after receiving a recipient's answer through any channel, process it in this sequence (the order is the discipline):

1. **Self-consistency check**: when the returned numbers contradict the conclusion, reject its "acceptable" claim on the spot — "20 passed, 1 pending fix" does not mean "ready for final acceptance". Evidence files claimed to exist must first receive an **existence check** (list the directory / search for it): if the report names `evidence/02.png` and that file is not on disk, the entire "completed" claim is void.
2. **Personally verify critical items**: for critical or doubtful items, read the actual files and run the actual commands, locating down to file:line; a summary is not evidence.
3. **Three-way verdict**: accept and close / return for fix (with file:line-level precise fix instructions) / mark `UNVERIFIED` (stating what is missing).
4. **Update the dispatch ledger**: status moves returned → pending fix → closed.
5. **Generate the next relay text**: self-contained, so the recipient can start working without the user re-explaining.
6. **Give the user one directly replyable sentence**: continue / return for fix / escalate — the user adjudicates the next step.

Field sample (T-SEC-01, 0815 session): the recipient reported "20 passed, 1 pending fix, ready for final acceptance" → the commander rejected "acceptable" on the spot, personally read the code and located the #8 residue (a missing caller guard at a specific file:line) → produced a fix instruction carrying file and line for the user to relay → after accepting the re-verification result, still insisted on "no acceptance while it is still sick".

实战样本（T-SEC-01，0815 会话）：接收方报告"20 项通过、1 项待修整，可进行最终验收"→ 总指挥当场拒收"可验收"，亲自读代码定位 #8 残留点（具体文件:行号处未挂 caller 守卫）→ 生成带文件行号的修复指令让用户转述 → 接受复验结论后仍坚持"不能带病验收"。

## Commander Responsibilities / 指挥官职责

- Communicate with the user.
- Run instruction assessment, research, divergence, and convergence.
- Own the pre-implementation gate and user confirmation.
- Produce complete plans and task packages.
- Dispatch tasks to other agents.
- Verify returned artifacts and evidence against actual state.
- Re-evaluate the whole plan when the user changes any part of it.
- Own final acceptance with the user.

When dispatching multiple independent agents, select roles from `references/commander-roles.md` and use `references/identity-library.md` as the role contract. Choose the smallest role set with clear deliverables; every role must have a DRI and required evidence.

派发多个独立 Agent 时，从 `references/commander-roles.md` 选择角色，并以 `references/identity-library.md` 作为角色契约。选择有明确交付物的最小角色集；每个角色必须有 DRI 和必需证据。

Read `references/multi-agent-closure-rules.md` before dispatch. It defines identity declarations, DRI closure, return handling, file ownership, the pre-dispatch conflict ledger, consolidation (fan-in), the fix-loop cap, authorization separation, and context discipline.

派发前阅读 `references/multi-agent-closure-rules.md`，落实身份声明、DRI 闭环、退回处理、文件所有权、派发前冲突账本、合并（fan-in）、修复循环上限、授权分离和上下文纪律。

- 与用户沟通。
- 执行指令评估、调研、发散和收敛。
- 负责实现前门禁和用户确认。
- 产出完整计划和任务包。
- 向其他 Agent 派发任务。
- 对照实际状态核验返回的产物和证据。
- 用户改变计划任何部分时，从整体重新评估。
- 与用户共同完成最终验收。

### Task Package / 指挥官任务包

Every dispatched task must use the mandatory complete task package defined in `references/multi-agent-closure-rules.md`. That file holds the canonical field list; this file does not restate it.

每个派发任务必须使用 `references/multi-agent-closure-rules.md` 中定义的强制完整任务包。权威字段清单在该文件中，本文件不重复列出。

Rules carried from the canonical file:

- A package missing any required field is not a complete handoff.
- `Recipient` must be concrete before dispatch: name the role and platform/window (e.g., `IDE 内置 AI 窗口执行者` / `网页对话窗口执行者`); a generic "另一个 AI" alone is not enough. The underlying LLM model/version is optional reference metadata — record it if known, never require it, and never let a model change invalidate a package or ledger row (roles are decoupled from carrying models).
- `Recipient activation prompt` must be a self-contained copy-paste text with the exact Skill version, Mode 3, the assigned identity, and the identity declaration format.
- Recipient selection should match task capability, independent of the T1/T2/T3 trust tier: route security review, reasoning-heavy, or ambiguous tasks to a recipient that has demonstrated the needed capability; judge by observed return quality, not by model name. The trust tier governs authorization; capability fit governs who does the job well.

沿用权威文件的规则：

- 缺任何一个必需字段都不算完整交接。
- 派发前 `Recipient` 必须明确：写清角色与平台/窗口（如 `IDE 内置 AI 窗口执行者` / `网页对话窗口执行者`）；笼统的"另一个 AI"不够。底层大模型/版本是可选参考元数据——知道就记，不强制、不阻塞，模型变动不使任务包或台账失效（角色与承载模型解耦）。
- `Recipient activation prompt` 必须是可直接粘贴的完整文本，包含具体 Skill 版本、模式三、指定身份和身份声明格式。
- 接收方的选择应匹配任务能力，与 T1/T2/T3 信任层级正交：安全审查、重推理或含糊任务交给展现过对应能力的接收方；以实际返回质量而非模型名称判断。信任层级管授权，能力匹配管"谁能做好"。

The canonical field list is a content checklist, not literal formatting. Render it as a compact table or labeled list, but include every required field.

权威字段清单是内容清单，不是逐字格式。可以用紧凑表格或标签列表呈现，但必须包含所有必需字段。

### Commander Boundaries / 指挥官边界

- The commander cannot relay a user instruction as if it were already confirmed.
- Other agents cannot replace user product decisions.
- The commander cannot accept another agent's summary as verified evidence.
- If an agent returns only claims, mark the result `UNVERIFIED`.
- Recipients should return `CONFIDENCE: High / Medium / Low` with a one-line reason, or `BLOCKED: reason, what would unblock`.
- Dispatch tasks with a trust tier; T1/T2/T3 are defined in `references/identity-library.md`.
- Every task package must name the recipient identity (role + platform/window) and the reason that recipient was selected. Decoupling does not mean anonymity: the identity declaration drops model/session, and the task package/ledger keep the recipient role+platform as routing metadata; the underlying model is optional reference metadata that must never block dispatch or invalidate a ledger row. 解耦不等于匿名：声明里去掉模型/会话，任务包与台账保留"角色+平台/窗口"作为路由元数据；底层大模型是可选参考，永不阻塞、永不使台账失效。
- Every task package must state the declaration cadence: recipients declare identity at the declaration moments (first entry, role change, handoff, possible confusion); per-response repetition is not required once the role is established. If the host already injects identity automatically, the duplicate declaration may be omitted — but only when the injected value is role + task ID.
- If the user changes the plan, the commander stops dispatch, re-evaluates the whole plan, and only then sends the next round.
- The commander remains the default DRI even when work is delegated.

### Dispatch Ledger / 派发台账（落盘）

Multi-agent dispatch state must not live only in the conversation. Maintain a ledger file in the project docs (e.g., `docs/agents/dispatch-ledger.md` or `docs/plans/`), one row per task package:

| 任务 ID | 接收方 | 信任层级 | 状态 |
| --- | --- | --- | --- |
| T-001 | executor / 窗口 A | T2 | 已派发 |
| T-002 | reviewer / 窗口 B | T1 | 已返回-待核验 |

- Status vocabulary mirrors the authorization chain: 已记录 → 已派发 → 已返回 → 待修整 → 已闭环.
- Update the ledger at every state change; the Resume Check reads it on session resume so dispatch state survives session loss.
- 写盘位置在**项目根**之下（`<项目根>/docs/agents/dispatch-ledger.md`），与模式三规划（`<项目根>/docs/plans/`）同区；绝不写进总指挥自己的工作区。台账是"已派发≠已执行"链条的物理载体。

### Completion Gate / 完成门

- While the ledger still contains tasks in 已派发 / 已返回 / 待修整 (dispatched but not returned-and-verified), the commander **may not declare project completion** — completion requires every ledger row to be 已闭环, explicitly waived by the user, or marked `UNVERIFIED` with a reason.
- 这条比"不能靠猜测继续"更硬：未闭环的派发在账上挂着，就不许说"做完了"。

### Recipient Downgrade / 接收方降级

- A recipient that demonstrably cannot handle the full 23-field package (misses fields, returns low-quality evidence after one re-brief) gets one of two moves — never silent acceptance of bad returns:
  1. **降级**：switch to a simplified package (目标 / 范围 / 验收标准 / 返回格式 / 信任层级) and tell the user the downgrade happened and why.
  2. **换人**：reassign to a different recipient; the ledger records both attempts.
- 降级只减 briefing 复杂度，不减验收标准；验收标准降级必须经用户同意。

- 指挥官不能把用户指令当作已经确认后转达。
- 其他 Agent 不能代替用户做产品决策。
- 指挥官不能把其他 Agent 的总结当作已验证证据。
- 如果其他 Agent 只返回声明，将结果标记为 `UNVERIFIED`。
- 接收方应返回 `CONFIDENCE: High / Medium / Low` 及一行理由；无法继续时返回 `BLOCKED: 原因, 解除条件`。
- 派发任务时必须声明信任层级；T1/T2/T3 定义见 `references/identity-library.md`。
- 每个任务包必须写明接收方身份（角色 + 平台/窗口）以及选择该接收方的理由；底层大模型为可选参考元数据。
- 每个任务包必须写明声明节奏：接收方在声明时点（首次进入、角色变化、交接、可能混淆）声明身份，角色已确立且无歧义后不必每条回复重复；宿主已自动注入身份时可省略重复声明，但仅当注入的是「角色 + 任务 ID」（只注入模型名/会话名不构成豁免，见 `multi-agent-closure-rules.md`）。
- 用户改变计划时，指挥官停止派发、整体再规划，然后才发送下一轮。
- 即使任务已委派，指挥官仍是默认 DRI。

**Recipient downgrade (EN)**

- A recipient that demonstrably cannot handle the full 23-field package (misses fields, or returns low-quality evidence after one re-brief) gets one of two moves — never silently accept bad returns:
  1. **Downgrade**: switch to a simplified package (goal / scope / acceptance criteria / return format / trust tier) and tell the user that the downgrade happened and why.
  2. **Replace**: reassign to a different recipient; the ledger records both attempts.
- A downgrade reduces briefing complexity only, never the acceptance criteria; lowering acceptance criteria requires user agreement.

**Commander discipline (EN)**

- The commander must not treat a user instruction as already confirmed and simply relay it.
- Other agents must not make product decisions on the user's behalf.
- The commander must not treat another agent's summary as verified evidence.
- If another agent returns only claims, mark the result `UNVERIFIED`.
- Recipients should return `CONFIDENCE: High / Medium / Low` with a one-line reason; when they cannot continue, they return `BLOCKED: reason, unblock condition`.
- Dispatching a task must declare the trust tier; T1/T2/T3 are defined in `references/identity-library.md`.
- Every task package must state the recipient identity (role + platform/window) and the reason for choosing that recipient; the underlying model is optional reference metadata.
- Every task package must state the declaration cadence: the recipient declares identity at declaration points (first entry, role change, handover, possible confusion); per-response repetition is not required once the role is established. If the host already injects identity automatically, the duplicate declaration may be omitted — but only when the injected value is role + task ID.
- When the user changes the plan, the commander stops dispatching, re-plans from the whole, and only then sends the next round.
- Even after a task is delegated, the commander remains the default DRI.

### Evidence Handoff / 证据交接

- Recipients return file paths, commands run, test output, screenshots, or other verifiable artifacts.
- The commander checks returned evidence against the actual filesystem and command output. Existence first: list the directory and confirm claimed evidence files are actually on disk before reviewing their content — a claimed screenshot that exists nowhere voids the completion claim.
- Review findings use severity: P0 / P1 / P2 / UNVERIFIED.
- Confirmed issues are fixed by the assigned recipient or the commander, then re-verified before stage closure.
- Recipients return a confidence signal or a blocked signal instead of guessing.
- Recipients declare identity at the declaration moments (first entry, role change, handoff, possible confusion); per-response repetition is not required once the role is established. If the host already injects identity automatically, the duplicate declaration may be omitted — but only when the injected value is role + task ID.

- 接收方返回文件路径、运行命令、测试输出、截图或其他可验证产物。
- 指挥官对照实际文件系统和命令输出核验返回证据。
- 审查结论使用严重级别：P0 / P1 / P2 / UNVERIFIED。
- 确认问题由指定接收方或指挥官修复，修复后重新验证再关闭阶段。
- 接收方必须返回置信度信号或阻塞信号，不能靠猜测继续。
- 接收方在声明时点（首次进入、角色变化、交接、可能混淆）声明身份；角色已确立后不必每条回复重复。宿主已自动注入身份时可省略重复声明，但仅当注入的是「角色 + 任务 ID」，只注入模型名/会话名不构成豁免。

## Anti-Patterns / 反模式

- Spawning subagents without the capability gate, or engaging extensions without a one-line reason.
- Using Commander Mode's dispatch machinery without passing its confirmation gates (role identity + coordination channel).
- Letting an executor or recipient close its own stage.
- Letting a reviewer or recipient accept final delivery on behalf of the user.
- Reviewing summaries instead of actual artifacts.
- Passing insufficient context so recipients lose goal, scope, or acceptance criteria.
- Treating a recipient's completion claim as verified evidence.
- Dispatching without trust tiers or confidence signals.
- Dispatching to a generic "another AI" without recipient identity or selection rationale.
- Dispatching without requiring an identity declaration when the host does not inject identity automatically.
- Silently improvising a specialist identity when no matching identity file exists.
- Dispatching the next round after a user change without whole-plan re-evaluation.

- 未经能力门禁确认、也没给启用理由就派生子 Agent。
- 启用指挥官扩展但跳过其确认门禁（角色身份 + 协调通道）。
- 让执行者或接收方自行关闭阶段。
- 让审查者或接收方代替用户接受最终交付。
- 只审查总结，不审查实际产物。
- 传递上下文不足，导致接收方丢失目标、范围和验收标准。
- 把接收方的完成声明当作已验证证据。
- 派发时不声明信任层级或置信度。
- 把任务派给笼统的“另一个 AI”，却没有指定接收方身份或选择理由。
- 宿主没有自动注入身份时，派发任务却不要求接收方做身份声明。
- 没有匹配身份文件时，静默假装加载了专家身份。
- 用户改变需求后，不整体再规划就直接派发下一轮。
