---
name: cc-devflow-orchestrator
description: CC-DevFlow workflow router and agent recommender. Use when starting requirements, running flow commands, or asking about devflow processes.
---

# CC-DevFlow Orchestrator

## Purpose
Guide users to the correct agent/command WITHOUT duplicating their detailed standards.

## Workflow Map

### 🏢 项目级工作流（Project-Level, 项目初期执行一次）

```
/core-roadmap → ROADMAP.md + BACKLOG.md (产品路线图)
/core-architecture → ARCHITECTURE.md (系统架构设计)
/core-guidelines → frontend-guidelines.md / backend-guidelines.md (项目规范)
/core-style → STYLE.md (设计风格指南) 
```

### 📦 需求级工作流（Requirement-Level, 每个需求执行一次）

```
/flow-init → research.md + tasks.json + BRAINSTORM.md (研究初始化 + 头脑风暴)
     ↓
/flow-clarify → clarifications/*.md (11 维度歧义扫描, 可选)
     ↓
/flow-prd → PRD.md (invoke prd-writer agent, 需 BRAINSTORM.md 对齐)
     ↓
/flow-checklist → checklists/*.md (需求质量检查, 可选)
     ↓
/flow-tech → TECH_DESIGN.md + data-model + contracts (invoke tech-architect agent)
     ↓
/flow-ui → UI_PROTOTYPE.html (invoke ui-designer agent, 可选, 引用 STYLE.md)
     ↓
/flow-epic → EPIC.md + TASKS.md (invoke planner, bite-sized tasks)
     ↓
/flow-dev → TASKS.md execution (TDD + Autonomous mode default)
     ↓
/flow-review → SPEC_REVIEW.md + CODE_QUALITY_REVIEW.md (Two-Stage Review) 
     ↓
/flow-qa → QA reports (invoke qa-tester + security-reviewer agents)
     ↓
/flow-release → PR creation + deployment (分支完成决策)
     ↓
/flow-verify → consistency check (invoke consistency-checker agent, 任意阶段可调用)
```

### 🐛 Bug 修复工作流

```
/flow-fix "BUG-123|描述" → 系统化调试 (4阶段: Root Cause → Pattern → Hypothesis → TDD Fix)
```

**说明**:
- 项目级命令建立全局标准（SSOT），需求级命令引用这些标准
- `/flow-init` 包含 Brainstorming 阶段，生成 BRAINSTORM.md 作为需求「北极星」
- `/flow-prd` 需要 BRAINSTORM.md 对齐检查
- `/flow-clarify` 在 PRD 前可选执行，消除 research.md 中的歧义
- `/flow-epic` 使用 bite-sized tasks 原则 (2-5分钟/任务)
- `/flow-dev` 默认 Autonomous 模式（自动重试），使用 `--manual` 退出到 Manual 模式 
- `/flow-review` 是新增的两阶段审查 (Spec Compliance → Code Quality)
- `/flow-ui` 和 `/flow-dev` 自动加载 `devflow/STYLE.md`（如存在）
- 项目级命令可按需执行，无严格顺序要求

## Agent Delegation Guide

### When User Asks About Requirements Clarification
- **DO**: Recommend `/flow-clarify` command → invokes clarify-analyst agent
- **DON'T**: Duplicate clarification logic (flow-clarify.md has ~128 lines)
- **Link**: See [.claude/commands/flow-clarify.md](.claude/commands/flow-clarify.md) for details
- **Outputs**: clarifications/[timestamp]-flow-clarify.md (澄清报告)
- **Features**: 11-dimension scan, ≤5 prioritized questions, session recovery

### When User Asks About PRD
- **DO**: Recommend `/flow-prd` command → invokes prd-writer agent
- **DON'T**: Duplicate PRD standards (prd-writer agent has ~300 lines)
- **Link**: See [.claude/agents/prd-writer.md](.claude/agents/prd-writer.md) for PRD details
- **Standards**: INVEST principles, Anti-Expansion mandate, Given-When-Then criteria

### When User Asks About Requirement Quality Checklist
- **DO**: Recommend `/flow-checklist` command → invokes checklist-agent
- **DON'T**: Duplicate checklist standards (checklist-agent has ~180 lines)
- **Link**: See [.claude/commands/flow-checklist.md](.claude/commands/flow-checklist.md) for details
- **Outputs**: checklists/*.md (ux, api, security, performance, data, general)
- **Features**: 5 quality dimensions, Anti-Example rules, 80% gate threshold
- **Level**: Requirement-level (optional, before /flow-epic)

### When User Asks About Tech Design
- **DO**: Recommend `/flow-tech` command → invokes tech-architect agent
- **DON'T**: Duplicate tech standards (tech-architect agent has ~516 lines)
- **Link**: See [.claude/agents/tech-architect.md](.claude/agents/tech-architect.md) for design details
- **Outputs**: TECH_DESIGN.md, data-model.md, contracts/, quickstart.md

### When User Asks About Design Style Guide
- **DO**: Recommend `/core-style` command → invokes style-guide-generator agent
- **DON'T**: Duplicate style guide standards (style-guide-generator agent has ~400 lines)
- **Link**: See [.claude/agents/style-guide-generator.md](.claude/agents/style-guide-generator.md) for details
- **Outputs**: STYLE.md (project-level SSOT for visual consistency)
- **Level**: Project-level (execute once per project)

### When User Asks About UI Prototype
- **DO**: Recommend `/flow-ui` command → invokes ui-designer agent
- **DON'T**: Duplicate UI standards (ui-designer agent has ~485 lines)
- **Link**: See [.claude/agents/ui-designer.md](.claude/agents/ui-designer.md) for UI details
- **Features**: 80+ design masters sampling, responsive design, NO PLACEHOLDER, references STYLE.md

### When User Asks About Task Planning
- **DO**: Recommend `/flow-epic` command → invokes planner agent
- **DON'T**: Duplicate planning logic (planner agent has ~400 lines)
- **Link**: See [.claude/agents/planner.md](.claude/agents/planner.md) for task breakdown rules
- **Enforces**: Phase -1 Gates (Articles VII, VIII, IX), TDD sequence

### When User Asks About QA/Security
- **DO**: Recommend `/flow-qa` command → invokes qa-tester + security-reviewer agents
- **DON'T**: Duplicate QA standards (qa-tester agent has ~300 lines)
- **Link**: See [.claude/agents/qa-tester.md](.claude/agents/qa-tester.md) for QA details

### When User Asks About Code Review (v2.1.0 新增)
- **DO**: Recommend `/flow-review` command → invokes spec-reviewer + code-quality-reviewer agents
- **DON'T**: Duplicate review standards (Two-Stage Review)
- **Link**: See [.claude/commands/flow-review.md](.claude/commands/flow-review.md) for details
- **Features**: Stage 1 (Spec Compliance) → Stage 2 (Code Quality), 不信任实现者报告

### When User Asks About Bug Fix (v2.1.0 新增)
- **DO**: Recommend `/flow-fix` command → 4-phase systematic debugging
- **DON'T**: Guess and fix without investigation
- **Link**: See [.claude/commands/flow-fix.md](.claude/commands/flow-fix.md) for details
- **Features**: Root Cause → Pattern → Hypothesis → TDD Fix, Iron Law enforcement

## Phase Gates (Quick Reference Only)

### Entry Gates
- **flow-init Entry**: Git 工作区干净, main 分支
- **flow-clarify Entry**: research.md 存在, phase0_complete == true
- **flow-prd Entry**: BRAINSTORM.md 存在, research.md 无 TODO placeholder 
- **flow-checklist Entry**: PRD.md 必须完成 (prd_complete == true)
- **flow-tech Entry**: PRD.md 必须完成
- **flow-ui Entry**: PRD.md 必须完成（可与 tech 并行）
- **flow-epic Entry**: PRD 完成，tech/ui 推荐但可选，Checklist Gate (如存在 checklists/)
- **flow-dev Entry**: EPIC.md + TASKS.md 存在
- **flow-review Entry**: development_complete == true 
- **flow-qa Entry**: review_complete == true (或 development_complete)
- **flow-release Entry**: qa_complete == true

### Exit Gates
- **flow-init Exit**: research.md 5-level quality check, BRAINSTORM.md 完整
- **flow-clarify Exit**: clarification report 完整, orchestration_status.clarify_complete == true
- **flow-prd Exit**: PRD.md 无 placeholder, Constitution 合规, BRAINSTORM 对齐
- **flow-tech Exit**: TECH_DESIGN.md + data-model + contracts 完整
- **flow-epic Exit**: TASKS.md TDD 顺序正确, bite-sized tasks, Phase -1 Gates 通过
- **flow-dev Exit**: 所有 TASKS 完成, TDD Checkpoint 通过, 测试通过
- **flow-review Exit**: SPEC_REVIEW.md + CODE_QUALITY_REVIEW.md 均 PASS 
- **flow-qa Exit**: 无 high-severity 漏洞
- **flow-release Exit**: PR 创建成功, 分支决策完成 

**For Details**: See [orchestration_status.json](devflow/requirements/REQ-XXX/orchestration_status.json) and [EXECUTION_LOG.md](devflow/requirements/REQ-XXX/EXECUTION_LOG.md)

## State Machine: Status → Recommended Command

Read `orchestration_status.json` to determine current phase:

```yaml
status: "initialized"
  → Recommend: /flow-clarify (optional, clarify ambiguities)
  → Alternative: /flow-prd (skip clarification, generate PRD directly)
  → Note: BRAINSTORM.md 已在 /flow-init 生成 

status: "clarify_complete" OR "clarify_skipped"
  → Recommend: /flow-prd (generate PRD)

status: "prd_complete"
  → Recommend: /flow-tech (generate technical design)
  → Alternative: /flow-ui (generate UI prototype, optional)

status: "tech_design_complete"
  → If UI not done: /flow-ui (optional)
  → Else: /flow-epic (generate EPIC and TASKS)

status: "epic_complete"
  → Recommend: /flow-dev (TDD development, Autonomous mode default)
  → Alternative: /flow-dev --manual (Manual mode for complex requirements) 

status: "development_complete"
  → Recommend: /flow-review (Two-Stage Code Review) 
  → Alternative: /flow-qa (skip review, go directly to QA)

status: "review_complete"
  → Recommend: /flow-qa (quality assurance and security review)

status: "qa_complete"
  → Recommend: /flow-release (create PR and release)

status: "released"
  → Recommend: /flow-verify (final consistency check)
```

## Troubleshooting Quick Routing

### Phase gate blocked?
- **Action**: Check `orchestration_status.json` for current status
- **Script**: Run `.claude/scripts/check-prerequisites.sh --json`

### Document missing?
- **Action**: Check which phase is incomplete
- **Script**: Run `.claude/scripts/generate-status-report.sh`

### Need detailed standards?
- **Clarify**: See flow-clarify.md command + clarify-analyst agent
- **PRD**: Consult prd-writer agent
- **Tech**: Consult tech-architect agent
- **UI**: Consult ui-designer agent
- **Tasks**: Consult planner agent
- **QA**: Consult qa-tester agent

### Constitution violation?
- **Real-time check**: constitution-guardian guardrail (PreToolUse hook)
- **Batch validation**: Run `.claude/scripts/validate-constitution.sh`
- **Reference**: See `.claude/rules/project-constitution.md` 
- **Rationalization Library**: See `.claude/rules/rationalization-library.md` 

### TDD order violated?
- **Real-time check**: devflow-tdd-enforcer guardrail (PreToolUse hook)
- **Manual check**: See TASKS.md, tests MUST be marked [x] before implementation
- **TDD Skill**: See `.claude/skills/flow-tdd/SKILL.md` 

## Auxiliary Commands

### Status and Progress
- `/flow-status` - Query requirement progress
- `/flow-update "REQ-123" "T012"` - Update task completion
- `/flow-restart "REQ-123" --from=epic` - Resume interrupted workflow

### Upgrade and Analysis
- `/flow-upgrade "REQ-123" --analyze` - PRD version upgrade impact analysis
- `/flow-constitution` - Constitution management
- `/flow-verify "REQ-123"` - Comprehensive consistency verification

### Bug Fix
- `/flow-fix "BUG-123|登录超时"` - 系统化 BUG 修复 (4阶段调试法)
- `/problem-analyzer "<issue>"` - Problem diagnosis

### Code Review
- `/flow-review "REQ-123"` - Two-Stage Code Review (Spec → Quality)
- `/code-review-high "<diff>"` - High-rigor code review

## Integration with Other Skills

### Guardrails (实时阻断)
- **devflow-tdd-enforcer**: Enforces TDD order in TASKS.md
- **constitution-guardian**: Enforces Constitution compliance

### Workflow Skills
- **flow-brainstorming**: 需求头脑风暴，生成 BRAINSTORM.md
- **flow-tdd**: TDD Iron Law 执行
- **flow-debugging**: 4阶段系统化调试
- **flow-receiving-review**: 处理代码审查反馈
- **flow-finishing-branch**: 分支完成决策
- **verification-before-completion**: 验证闸门

### Reference Skills
- **devflow-file-standards**: File naming and directory structure reference
- **devflow-constitution-quick-ref**: Constitution quick reference

## Design Principle

**This skill does NOT contain**:
- ❌ Detailed agent execution standards (those are in agent files)
- ❌ Full Phase Gate validation logic (those are in flow command files)
- ❌ Complete Constitution articles (those are in project-constitution.md)

**This skill ONLY contains**:
- ✅ Workflow routing (which command to run next)
- ✅ Agent delegation (which agent handles what)
- ✅ Quick reference (Phase Gates summary, not full details)
- ✅ Links to detailed documentation

**Rationale**: Avoid duplication ("不重不漏" principle). Agents and Commands own detailed standards.
