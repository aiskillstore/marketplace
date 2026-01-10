---
name: copilot-flow
description: AI collaboration workflow plugin - Implements automated collaborative development process between Claude and Copilot through structured 5-stage workflow
license: MIT
---

# Copilot Flow Integration

When to use this skill:
- When you need a structured AI-assisted development workflow
- When you want to leverage both Claude and Copilot's strengths
- When you require end-to-end task management from analysis to delivery

**Triggering conditions:**
- When user mentions "請 Copilot 協助" (Please ask Copilot to assist)
- When user says "詢問 Copilot" (Ask Copilot)
- When user requests "執行 copilot-flow" (Execute copilot-flow)
- When user starts with "copilot-flow:" or "c-flow:" prefix

## Core Features

This skill orchestrates a complete 5-stage AI collaboration workflow:
1. **Analyze** (Claude) - Requirements analysis and structuring
2. **Design** (Copilot) - Architecture design and planning
3. **Implement** (Claude) - Code implementation based on design
4. **Review** (Copilot) - Code quality assessment
5. **Deliver** (Claude) - Final integration and documentation

## Workflow Commands

The workflow is managed through specialized slash commands in the `/commands` directory:

### /copilot-flow:analyze [task description]
- Executes the analysis phase
- Claude analyzes requirements and prepares structured prompts
- Output: `analysis-result.md`

### /copilot-flow:design [goals]
- Executes the design phase using Copilot MCP
- Creates architecture design based on analysis
- Output: `architecture-design.md`

### /copilot-flow:implement [target]
- Executes implementation phase
- Claude implements code following Copilot's design
- Output: Source code files and `implementation-report.md`

### /copilot-flow:review [scope]
- Executes review phase using Copilot MCP
- Professional code review with focus areas
- Output: `code-review-report.md`

### /copilot-flow:deliver [objectives]
- Executes final delivery phase
- Claude integrates all results and documentation
- Output: Complete delivery package

## Usage Patterns

### Full Workflow Execution
For complete task execution, use the workflow orchestrator:

```
執行 copilot-flow 實現用戶認證系統
```

This will:
1. Show preview of all stages
2. Wait for confirmation
3. Execute each stage in sequence
4. Manage state between stages
5. Provide final delivery package

### Individual Stage Execution
Execute specific stages independently:

```
/copilot-flow:analyze 分析現有代碼庫並提出改進建議
/copilot-flow:review 審查 auth.js 檔案的安全性
/copilot-flow:implement 根據設計文檔實現 API 端點
```

## State Management

The workflow maintains state through:
- `.claude/workflow-state.json` - Current stage and progress
- Stage output files - Results from each phase
- claude-mem integration - Complete interaction history

## AI Model Collaboration

### Claude Responsibilities
- Requirements analysis and structuring
- Code implementation and modifications
- Final integration and delivery
- File system operations

### Copilot Responsibilities (via MCP)
- Architecture design recommendations
- Code quality review and feedback
- Security and performance assessment
- Best practices guidance

## Example Workflow

### User Request
```
執行 copilot-flow 實現一個 REST API 進行用戶認證，支持 JWT token
```

### Workflow Execution
1. **Preview Mode** - Shows planned stages and estimated time
2. **Analysis** - Claude breaks down requirements
3. **Design** - Copilot suggests architecture
4. **Implementation** - Claude writes code
5. **Review** - Copilot reviews implementation
6. **Delivery** - Claude prepares final package

### Outputs
- `analysis-result.md` - Structured requirements
- `architecture-design.md` - System design
- Source code files - Implementation
- `code-review-report.md` - Quality assessment
- `delivery/` - Complete package with docs

## Best Practices

### Do
- Start with clear requirements
- Let the workflow handle stage transitions
- Review each stage output before proceeding
- Use full workflow for complex tasks
- Execute individual stages for specific needs

### Don't
- Skip stages in full workflow mode
- Modify intermediate files manually
- Run stages out of sequence
- Ignore review recommendations

## Error Recovery

If workflow is interrupted:
1. Check `.claude/workflow-state.json` for current state
2. Resume from last completed stage
3. Or restart from specific stage
4. All progress is preserved

## Integration with Other Skills

- **copilot-mcp-server**: Used internally by design and review stages
- **claude-mem**: Records all workflow interactions
- File system tools: Used by Claude for implementation

## Keywords
AI collaboration, workflow, automation, Claude, Copilot, structured development, end-to-end, project management, code review, architecture design