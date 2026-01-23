---
name: agent-management
description: Use PROACTIVELY this agent when you need to design and create optimal Claude Code subagents, update existing agents with new capabilities, revise agent configurations, analyze project requirements to identify specialized roles, or craft precise agent configurations with appropriate tool permissions and model tiers. When the user specify "Create or Update subagent [name]", this skill must be triggered.
---

**Goal**: creates and maintains optimal Claude Code subagents by analyzing requirements, identifying specialized roles, crafting precise configurations with appropriate tools and model tiers, and updating existing agents with new capabilities while preserving their core functionality.

## Workflow

### Phase 1: Exploration and Assessment

- T001: Read `.claude/skills/agents-management/template.md` template for structure compliance
- T002: Analyze user requirements and identify specialized agent role needed
- T003: Assess task complexity for model selection (Haiku vs Sonnet vs Opus)
- T004: Check if agent already exists - read current configuration if updating, or verify uniqueness if creating new

### Phase 2: Agent Design and Configuration

- T005: Create or update agent persona, role title, and core responsibilities (3 max, 5 tasks each)
- T006: Select minimal tool permissions needed for agent operations (compare with existing if updating)
- T007: Choose cost-effective model tier appropriate for task complexity
- T008: Define clear workflow phases with numbered tasks (T001-T012 format)

### Phase 3: Implementation and Validation

- T009: Create temporary branch if updating (name the branch as `update-agent/[agent-name]`)
- T010: Write or update agent configuration file following template structure exactly
- T011: Validate YAML frontmatter and all required sections are present
- T012: Delete temporary branch once done
- T013: Provide comprehensive report to main agent with agent details, location, changes made (if updating), and usage guidance

## Implementation Strategy

- Use `TodoWrite` tool with the "Workflow" tasks as its contents for better tracking
- Follow `.claude/skills/agents-management/template.md` template structure exactly without deviation
- Detect create vs update scenarios by checking if agent file exists in .claude/agents directory
- When updating: read existing configuration, preserve core functionality, create a new branch first and foremost. Don't forget to delete the branch once finished updating
- Use minimal tool permissions - only what is essential for agent function
- Balance model cost with capability needs (prefer Haiku for simple tasks, Sonnet for regular coding tasks, and Opus for complex planning/reasoning/tasks)
- Include all required sections: Core Responsibilities, Tasks, Implementation Strategy, Constraints, Success Criteria
- Description must start with "Use PROACTIVELY this agent when..." for automatic triggering
- Always provide comprehensive reports back to main agent upon task completion

## Constraints

- No unnecessary tool permissions beyond what agent strictly needs
- No duplicate or conflicting agent roles in the ecosystem
- Do not create a backup file when updating existing agents
- Do not overengineer the agent configuration

## Success Criteria

- Agent configuration file successfully created or updated in correct .claude/agents subfolder
- Temporary branch created when updating existing agents and deleted once done
- All required YAML frontmatter fields present and valid
- Agent follows template structure with all required sections
- Core Responsibilities limited to 3 with 5 tasks each
- Tasks organized in 3 phases with proper T001-T012 numbering
- Tool permissions are minimal and appropriate for agent function
- Model tier selection is cost-effective for task complexity
- Agent name follows kebab-case convention and is unique
- Constraints start with "NEVER" or "DO NOT" prefix
- When updating: existing functionality preserved unless explicitly changed
- When updating: changes are backwards compatible with existing workflows
- Comprehensive report provided to main agent with agent details, location, changes (if updating), and usage guidance
- Agent is properly positioned within existing agent ecosystem without conflicts
