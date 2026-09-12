# Commander Mode Role Library / 指挥官多 Agent 角色库

## Role Selection Principle / 选角原则

- One task has one DRI.
- A role is useful only when it has a required deliverable or evidence.
- The acceptance auditor must validate the actual user path in the real target environment, not only unit tests or file existence.
- Review roles are read-only unless explicitly authorized to modify.
- The user is the final approver; the commander remains the final closure owner.
- A role may be an internal thinking mode, a subagent, or an external independent agent.
- Choose the smallest role set that can complete and verify the task; avoid role bloat.
- Read `references/identity-library.md` for the universal role contract, confidence protocol, and trust tiers.

- 一个任务只有一个 DRI。
- 角色只有在有明确交付物或证据时才有意义。
- 审查类角色默认只读，除非被明确授权修改。
- 用户是最终批准人；总指挥是最终收口负责人。
- 角色可以是内部思考模式、子 Agent 或外部独立 Agent。
- 选择能完成任务和验证的最小角色集，避免角色冗余。
- 统一身份契约、置信度协议和信任层级见 `references/identity-library.md`。

## Core Roles / 核心角色

| Role / 角色 | Responsibility / 职责 | Required Output / 必需交付物 |
| --- | --- | --- |
| Commander / 总指挥 | User communication, plan, gate, dispatch, evidence verification, conflict resolution, final acceptance. | Complete plan, task packages, acceptance verdict. |
| Requirements Analyst / 需求分析师 | Clarify intent, define scope and acceptance criteria. | Requirements document, acceptance criteria. |
| Architect / 架构师 | Choose technology, define boundaries, data model, and extension points. | Architecture decision, interface contract. |
| Planner / 计划者 | Produces a researched, stage-explicit, confirmable plan before implementation. | Complete plan with stages, risks, and exit criteria. |
| Deputy Planner / 副计划者 | Audit plans and risks before execution. | Plan review, risk list. |
| Executor / 执行者 | Implement the approved scope only. | Files, commands, tests, docs, evidence. |
| QA / Test Engineer / 测试工程师 | Define test strategy, regression, edge cases, and evidence. | Test plan, test results. |
| Reviewer / 审查者 | Reads or runs the actual artifacts and returns adversarial findings. | P0 / P1 / P2 / UNVERIFIED findings with file:line. |
| Code Reviewer / 代码审查员 | Review the diff for bugs, security, performance, and maintainability. | Review report with P0 / P1 / P2. |
| Acceptance Auditor / 验收审计员 | Independently validate against acceptance criteria, including the actual user path in the real target environment. | ACCEPTED / REJECTED / NEEDS REVIEW with user-path evidence. |
| Security Tester / 安全测试员 | Attack surfaces, authorization, injection, secrets, permissions. | Security report. |
| Documentation Consistency Reviewer / 文档一致性审查员 | Check specs, code, tests, docs, and status consistency. | Mismatch list. |
| User Representative / 用户代表 | Represent user perspective, usability, and edge cases. | Feedback report. |

## Optional Roles / 可选角色

| Role / 角色 | When to Include / 何时加入 |
| --- | --- |
| Performance Engineer / 性能优化员 | Response time, concurrency, memory, or resource usage matters. |
| Deployment / Release Engineer / 部署发布工程师 | Build, package, release, rollback, or environment switching is required. |
| Privacy / Compliance Reviewer / 隐私合规审查员 | User data, logs, retention, or regulatory boundaries are involved. |
| Patent / Legal Reviewer / 专利法律审查员 | Patent, license, legal, or external submission decisions are involved. |
| Integration Coordinator / 集成协调员 | Multiple parallel tasks touch shared interfaces or need merge ordering. |
| Risk Manager / 风险管理员 | High-risk decisions need a persistent risk and escalation register. |
| Deputy Commander / 副总指挥 | The commander may be unavailable or overloaded, or continuity is critical. |
| Documentation Writer / 文档编写员 | A separate writer is needed while reviewers remain independent. |

## Role Identity Files / 身份文件

Built-in identity files live in `identities/`. The file name is the canonical role name.

内置身份文件位于 `identities/`，文件名即规范角色名。

The complete file-to-role catalog is maintained only in `identities/README.md`; that is the canonical list. Read it before presenting, selecting, or dispatching roles, and point to it instead of duplicating the mapping here.

完整的文件与角色对照目录只在 `identities/README.md` 中维护，那是权威清单。出示、选择或派发角色前先读取它，并指向该文件，不要在此重复对照表。

Custom user identities go in `custom-identities/` (Chinese: 其他身份) and must be read before adoption.

用户自定义身份放在 `custom-identities/`（中文名：其他身份）。

## Identity Matching / 身份匹配

- A role must be selected only when it has a required deliverable.
- Read the identity file before claiming the role.
- If the user requests a role not in `identities/`, check `custom-identities/` first.
- If no identity file exists, state the gap honestly and ask whether the user wants to provide one.
- If the user proceeds without a custom identity, use the closest generic role and mark the result as improvised or approximate.
- Never present a generic role as a loaded specialist identity.

- 只有当角色有必需交付物时才选择它。
- 声称采用角色前必须读取身份文件。
- 用户请求的身份不在 `identities/` 时，先检查 `custom-identities/`。
- 没有身份文件时，诚实说明缺口，并询问用户是否提供自定义身份。
- 用户没有自定义身份仍要继续时，使用最接近的通用角色，并标记为临时近似，不能冒充已加载专家身份。

## Recipient Identity Assignment / 接收方身份分配

- Every dispatched task must name the recipient identity (role + platform/window) and why that recipient was selected; the underlying LLM model is optional reference metadata.
- The recipient must read its identity file before adopting the assigned role.
- Every recipient declares its identity at the declaration moments (first entry, role change, handoff, possible confusion) unless the host injects identity automatically; per-response repetition is not required once the role is established.
- Do not dispatch to a generic "another AI" without a role and rationale.
- The commander decides the smallest role set before generating task packages.
- Read `references/multi-agent-closure-rules.md` before dispatch; it defines DRI closure, task returns, file ownership, authorization separation, and context discipline.

- 每个派发任务必须写明接收方身份（角色 + 平台/窗口）以及选择理由；底层大模型为可选参考元数据。
- 接收方采用角色前必须读取对应身份文件。
- 接收方在声明时点（首次进入、角色变化、交接、可能混淆）声明身份；角色已确立后不必每条回复重复。
- 不能把任务派给笼统的“另一个 AI”，却不指定角色和选择理由。
- 总指挥先生成最小角色集，再生成任务包。
- 派发前阅读 `references/multi-agent-closure-rules.md`，落实 DRI 闭环、退回处理、文件所有权、授权分离和上下文纪律。

## Role Set By Project Size / 按项目规模选择

| Project Size / 项目规模 | Recommended Core Set / 推荐核心角色 |
| --- | --- |
| Small / 小型任务 | Commander, Executor, Acceptance Auditor. |
| Medium / 中等任务 | Above plus Requirements Analyst, Architect, QA, Code Reviewer. |
| Large / 大型任务 | Above plus Security Tester, Documentation Consistency Reviewer, User Representative. |
| High-Risk / 高风险任务 | Add Privacy/Compliance Reviewer, Patent/Legal Reviewer, Risk Manager, Integration Coordinator. |

## Role Boundaries / 角色边界

- The commander is the default DRI and final closure owner.
- The user is the final approver for scope, commit, push, release, and external decisions.
- Reviewer roles do not implement unless explicitly assigned as the implementer.
- Executor only modifies files inside the allowed scope.
- No role may accept final delivery on behalf of the user.
- Role names are task roles, not identity replacements; the host agent's identity and platform rules take precedence.

- 总指挥是默认 DRI 和最终收口负责人。
- 用户是范围、提交、推送、发布和外部决策的最终批准人。
- 审查类角色不实现，除非被明确指定为实现者。
- 执行者只修改允许范围内的文件。
- 任何角色都不能代替用户接受最终交付。
- 角色名是任务角色，不是身份替换；宿主模型的身份和平台规则优先。

## Anti-Patterns / 反模式

- Adding a role that has no required deliverable.
- Adding multiple reviewers with overlapping scope but no clear owner.
- Letting the executor also be the final acceptance auditor.
- Treating a role name as proof that the role was actually performed.
- Using all roles for every task.
- Claiming a role without reading its identity file.
- Silently improvising a specialist identity when no matching identity exists.
- Dispatching to a generic recipient without identity (role + platform/window) or rationale.
- Responding without an identity declaration when the host does not inject identity automatically.

- 加入没有必需交付物的角色。
- 加入多个范围重叠但责任不清的审查者。
- 让执行者同时担任最终验收审计员。
- 把角色名当作角色已经执行的证据。
- 每个任务都套用全部角色。
- 把任务派给笼统接收方，却没有指定角色/平台身份或选择理由。
- 宿主没有自动注入身份时，回复却不声明自己是谁。
