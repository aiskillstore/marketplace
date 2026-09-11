# Built-in Identities / 内置身份定位

These files define generic role identities for Commander Multi-Agent Mode.

这些文件为指挥官多 Agent 模式提供通用角色身份定位。

Universal role contract: `references/identity-library.md`.

通用身份契约：`references/identity-library.md`。

## Quick Reference / 身份速查

Use this table when presenting built-in identities to the user. Do not show only role names.

向用户出示内置身份时使用下表，不能只列角色名。

| Identity / 身份 | Responsibility / 职责 |
| --- | --- |
| `commander` / 总指挥 | Owns user communication, whole-plan control, dispatch, evidence verification, and final acceptance. |
| `deputy-commander` / 副总指挥 | Keeps continuity when the commander is unavailable or overloaded. |
| `executor` / 执行者 | Implements only the approved task package and returns real artifacts and evidence. |
| `planner` / 计划者 | Produces a complete plan before implementation. |
| `deputy-planner` / 副计划者 | Audits plans and risks before execution. |
| `requirements-analyst` / 需求分析师 | Clarifies goals, scope, and testable acceptance criteria. |
| `architect` / 架构师 | Chooses technology, boundaries, data models, and extension points. |
| `qa-engineer` / 测试工程师 | Designs test strategy, cases, coverage, and real verification evidence. |
| `reviewer` / 审查者 | Reviews actual artifacts and returns P0 / P1 / P2 / UNVERIFIED findings. |
| `code-reviewer` / 代码审查员 | Reviews code for correctness, readability, architecture, security, and performance. |
| `security-tester` / 安全测试员 | Attacks trust boundaries, auth, injection, secrets, permissions, and AI/LLM risks. |
| `acceptance-auditor` / 验收审计员 | Independently validates the real user path in the real target environment. |
| `documentation-consistency-reviewer` / 文档一致性审查员 | Checks specs, code, tests, docs, and status consistency. |
| `user-representative` / 用户代表 | Represents real user needs, usability, accessibility, and edge cases. |
| `performance-engineer` / 性能优化员 | Finds performance risks and validates them with measured evidence. |
| `deployment-release-engineer` / 部署发布工程师 | Plans build, package, release, rollback, and environment switching. |
| `privacy-compliance-reviewer` / 隐私合规审查员 | Checks data flow, retention, consent, and regulatory boundaries. |
| `legal-reviewer` / 专利法律审查员 | Checks license, patent, legal, and external-submission risks. |
| `integration-coordinator` / 集成协调员 | Manages shared interfaces, merge order, and dependency flow. |
| `risk-manager` / 风险管理员 | Maintains a persistent risk and escalation register. |
| `documentation-writer` / 文档编写员 | Writes documentation that matches real behavior and includes runnable examples. |
| `_template` / 身份模板 | Base template for creating custom identities. |

## Files / 文件

- `commander.md` - Commander / 总指挥
- `executor.md` - Executor / 执行者
- `reviewer.md` - Reviewer / 审查者
- `code-reviewer.md` - Code Reviewer / 代码审查员
- `planner.md` - Planner / 计划者
- `deputy-planner.md` - Deputy Planner / 副计划者
- `requirements-analyst.md` - Requirements Analyst / 需求分析师
- `architect.md` - Architect / 架构师
- `qa-engineer.md` - QA / Test Engineer / 测试工程师
- `security-tester.md` - Security Tester / 安全测试员
- `acceptance-auditor.md` - Acceptance Auditor / 验收审计员
- `documentation-consistency-reviewer.md` - Documentation Consistency Reviewer / 文档一致性审查员
- `user-representative.md` - User Representative / 用户代表
- `performance-engineer.md` - Performance Engineer / 性能优化员
- `deployment-release-engineer.md` - Deployment / Release Engineer / 部署发布工程师
- `privacy-compliance-reviewer.md` - Privacy / Compliance Reviewer / 隐私合规审查员
- `legal-reviewer.md` - Patent / Legal Reviewer / 专利法律审查员
- `integration-coordinator.md` - Integration Coordinator / 集成协调员
- `risk-manager.md` - Risk Manager / 风险管理员
- `deputy-commander.md` - Deputy Commander / 副总指挥
- `documentation-writer.md` - Documentation Writer / 文档编写员
- `_template.md` - Template / 身份模板

If the user provides another identity file, place it in `custom-identities/` (Chinese: 其他身份) and read it before adopting the role.

如果用户提供其他身份文件，请放入 `custom-identities/`（中文名：其他身份），并在采用该角色前读取。
