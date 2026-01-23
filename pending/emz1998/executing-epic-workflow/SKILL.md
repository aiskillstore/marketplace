---
name: executing-epic-workflow
description: Execute systematic feature development using EPIC methodology (Explore, Research, Plan, Validate, Implement, Review, Iterate). Use when building features, implementing complex tasks, or following structured development workflows. Delegates exploration, research, planning, validation, and review to specialized agents.
---

# Executing EPIC Workflow

## 1. Context

- Main Objective: Execute feature development using the EPIC methodology (Explore, Research, Plan, Validate, Implement, Review, Iterate)
- Secondary Objective: Ensure proper delegation to specialized subagents for each phase
- User Input: Feature description, requirements, or task specification
- Workflow: Explore → Research → Plan → Validate Plan → Implement → Review → Iterate (main agent only implements)

### CRITICAL: Session Directory Initialization

**BEFORE starting any EPIC phase, the main agent MUST:**
1. Create session directory: `.claude/sessions/[NN]-[session-description]/`
   - `[NN]`: Two-digit sequential number (01, 02, 03, etc.)
   - `[session-description]`: Short hyphenated description (e.g., user-auth-feature, payment-integration)
2. Store the session directory path for use throughout the workflow
3. **ALWAYS instruct ALL subagents to save their reports to this session directory**

**Example:**
- Session directory: `.claude/sessions/01-user-auth-feature/`
- When delegating to any subagent, ALWAYS include: "Save your report to `.claude/sessions/01-user-auth-feature/[required-filename].md`"

## 2. Workflow

### Phase 1: Explore

**Objective:** Gather comprehensive context about the codebase and existing implementations

- T001: Initialize session directory [P0]
  - Determine next sequential number by checking existing `.claude/sessions/` directories
  - Create new session directory: `.claude/sessions/[NN]-[session-description]/`
  - Example: `.claude/sessions/01-user-auth-feature/`
  - Store this path as `SESSION_DIR` for use in all subsequent phases

- T002: Delegate exploration to `codebase-explorer` agent [P0]
  - **CRITICAL: Include explicit save instruction in delegation prompt:**
    ```
    "Please analyze the current project status, identify relevant files and components,
    assess recent changes and technical dependencies, and document the current state
    of related features.

    IMPORTANT: Save your complete exploration report to:
    [SESSION_DIR]/codebase-status.md

    The report must be saved to this exact location for workflow validation."
    ```
  - Request analysis of current project status
  - Identify relevant files and components
  - Assess recent changes and technical dependencies
  - Document current state of related features
  - **Agent MUST save report to: `[SESSION_DIR]/codebase-status.md`**

- T003: Review exploration findings [P0]
  - Read the generated report: `[SESSION_DIR]/codebase-status.md`
  - Synthesize discovered information
  - Identify gaps or areas needing clarification
  - Prepare context for research phase

- T004: Validate phase completion [P0]
  - Run: `python .claude/skills/epic/scripts/validate-phase.py explore [SESSION_DIR]`
  - **ITERATIVE COMPLIANCE FLOW:**
    - If validation PASSES: Proceed to Phase 2 (Research)
    - If validation FAILS:
      1. Reinvoke `codebase-explorer` agent with EXPLICIT instruction: "Save your report to `[SESSION_DIR]/codebase-status.md`"
      2. Re-run validation script
      3. Repeat steps 1-2 until validation passes
    - **CRITICAL:** Do NOT proceed to next phase until validation passes

### Phase 2: Research

**Objective:** Conduct comprehensive research on complex topics and validate approaches

- T005: Delegate research tasks to `research-specialist` agent [P0]
  - **CRITICAL: Include explicit save instruction in delegation prompt:**
    ```
    "Please conduct comprehensive research on [specific topics], validate approaches
    across multiple sources, perform deep web investigations if needed, and synthesize
    findings into actionable insights.

    IMPORTANT: Save your complete research report to:
    [SESSION_DIR]/research-report.md

    The report must be saved to this exact location for workflow validation."
    ```
  - Conduct research on complex topics
  - Validate approaches across multiple sources
  - Perform deep web investigations if needed
  - Synthesize findings into actionable insights
  - **Agent MUST save report to: `[SESSION_DIR]/research-report.md`**

- T006: Review research findings [P0]
  - Read the generated report: `[SESSION_DIR]/research-report.md`
  - Identify best practices and patterns
  - Document technical recommendations
  - Prepare foundation for planning phase

- T007: Validate phase completion [P0]
  - Run: `python .claude/skills/epic/scripts/validate-phase.py research [SESSION_DIR]`
  - **ITERATIVE COMPLIANCE FLOW:**
    - If validation PASSES: Proceed to Phase 3 (Plan)
    - If validation FAILS:
      1. Reinvoke `research-specialist` agent with EXPLICIT instruction: "Save your report to `[SESSION_DIR]/research-report.md`"
      2. Re-run validation script
      3. Repeat steps 1-2 until validation passes
    - **CRITICAL:** Do NOT proceed to next phase until validation passes

### Phase 3: Plan

**Objective:** Develop comprehensive implementation strategy

- T008: Delegate strategic planning to `strategic-planner` agent [P0]
  - **CRITICAL: Include explicit save instruction in delegation prompt:**
    ```
    "Please analyze the problem comprehensively using the exploration and research
    findings from [SESSION_DIR]/codebase-status.md and [SESSION_DIR]/research-report.md.
    Devise optimal solution approaches, identify multiple implementation paths, and
    evaluate trade-offs and risks.

    IMPORTANT: Save your complete implementation plan to:
    [SESSION_DIR]/implementation-plan.md

    The plan must be saved to this exact location for workflow validation."
    ```
  - Provide paths to exploration and research reports for context
  - Analyze problem comprehensively using exploration and research findings
  - Devise optimal solution approaches
  - Identify multiple implementation paths
  - Evaluate trade-offs and risks
  - **Agent MUST save report to: `[SESSION_DIR]/implementation-plan.md`**

- T009: Review and consolidate plan [P0]
  - Read the generated plan: `[SESSION_DIR]/implementation-plan.md`
  - Integrate insights from exploration and research
  - Verify comprehensive implementation roadmap exists
  - Confirm success criteria and validation steps are defined

- T010: Validate phase completion [P0]
  - Run: `python .claude/skills/epic/scripts/validate-phase.py plan [SESSION_DIR]`
  - **ITERATIVE COMPLIANCE FLOW:**
    - If validation PASSES: Proceed to Phase 4 (Validate Plan)
    - If validation FAILS:
      1. Reinvoke `strategic-planner` agent with EXPLICIT instruction: "Save your plan to `[SESSION_DIR]/implementation-plan.md`"
      2. Re-run validation script
      3. Repeat steps 1-2 until validation passes
    - **CRITICAL:** Do NOT proceed to next phase until validation passes

### Phase 4: Validate Plan

**Objective:** Critical review and validation of proposed approach

- T011: Delegate plan validation to `consulting-expert` agent [P0]
  - **CRITICAL: Include explicit save instruction in delegation prompt:**
    ```
    "Please review the implementation plan at [SESSION_DIR]/implementation-plan.md
    objectively. Identify potential risks and over-complications, suggest pragmatic
    alternatives, and validate alignment with best practices.

    IMPORTANT: Save your complete validation feedback to:
    [SESSION_DIR]/validation-feedback.md

    The feedback must be saved to this exact location for workflow validation."
    ```
  - Provide path to implementation plan for review
  - Review proposed approaches objectively
  - Identify potential risks and over-complications
  - Suggest pragmatic alternatives
  - Validate alignment with best practices
  - **Agent MUST save report to: `[SESSION_DIR]/validation-feedback.md`**

- T012: Refine plan based on validation feedback [P0]
  - Read the validation feedback: `[SESSION_DIR]/validation-feedback.md`
  - Address identified concerns
  - Simplify over-complicated approaches
  - Update `[SESSION_DIR]/implementation-plan.md` with refinements if needed
  - Finalize implementation strategy

- T013: Validate phase completion [P0]
  - Run: `python .claude/skills/epic/scripts/validate-phase.py validate [SESSION_DIR]`
  - **ITERATIVE COMPLIANCE FLOW:**
    - If validation PASSES: Proceed to Phase 5 (Implement)
    - If validation FAILS:
      1. Reinvoke `consulting-expert` agent with EXPLICIT instruction: "Save your feedback to `[SESSION_DIR]/validation-feedback.md`"
      2. Re-run validation script
      3. Repeat steps 1-2 until validation passes
    - **CRITICAL:** Do NOT proceed to next phase until validation passes

### Phase 5: Implement

**Objective:** Execute the implementation directly as the main agent

- T014: Set up implementation tracking with TodoWrite tool [P0]
  - Read the finalized plan: `[SESSION_DIR]/implementation-plan.md`
  - Break down plan into actionable tasks
  - Create todo list with clear status tracking
  - Mark tasks as in_progress when working on them

- T015: Execute implementation following the plan [P0]
  - Write code according to specifications from `[SESSION_DIR]/implementation-plan.md`
  - Follow established patterns from `[SESSION_DIR]/codebase-status.md`
  - Implement one task at a time
  - Mark todos as completed immediately after finishing

- T016: Handle errors and blockers [P1]
  - Keep tasks as in_progress if encountering issues
  - Create new tasks for blockers that need resolution
  - Never mark incomplete work as completed

- T017: Document implementation completion [P0]
  - Add inline comments where logic isn't self-evident
  - Update relevant documentation files if needed
  - Note any deviations from original plan
  - **CRITICAL: Main agent creates implementation summary:**
    ```
    Save a summary of what was implemented, key decisions made, and any
    deviations from the plan to:
    [SESSION_DIR]/implementation-complete.md

    This file is required for workflow validation.
    ```

- T018: Validate phase completion [P0]
  - Run: `python .claude/skills/epic/scripts/validate-phase.py implement [SESSION_DIR]`
  - **ITERATIVE COMPLIANCE FLOW:**
    - If validation PASSES: Proceed to Phase 6 (Review)
    - If validation FAILS (missing implementation-complete.md):
      1. Main agent creates `[SESSION_DIR]/implementation-complete.md` with summary
      2. Re-run validation script
      3. Repeat until validation passes
    - **CRITICAL:** Do NOT proceed to next phase until validation passes

### Phase 6: Review

**Objective:** Validate implementation quality through specialized review

- T019: Delegate code review to appropriate review agent [P0]
  - **CRITICAL: Include explicit save instruction in delegation prompt:**
    ```
    "Please review the implementation comprehensively. Review the code changes,
    check for code quality, performance, and security issues. Reference the
    implementation summary at [SESSION_DIR]/implementation-complete.md.

    IMPORTANT: Save your complete quality review to:
    [SESSION_DIR]/quality-report.md

    The report must be saved to this exact location for workflow validation.
    Include all findings, recommendations, and severity levels."
    ```
  - For code quality: Use general review processes
  - For security: Consider security-expert agent
  - Request comprehensive feedback on implementation
  - **Agent MUST save report to: `[SESSION_DIR]/quality-report.md`**

- T020: Delegate testing validation to `test-engineer` agent if tests exist [P1]
  - **CRITICAL: Include save instruction in delegation prompt**
  - Ensure tests pass for critical business logic
  - Validate test coverage
  - Review test data and mocking patterns
  - **Results should be appended to: `[SESSION_DIR]/quality-report.md`**

- T021: Compile review findings [P0]
  - Read the quality report: `[SESSION_DIR]/quality-report.md`
  - Document all feedback from review agents
  - Prioritize issues by severity
  - Prepare for iteration phase if needed

- T022: Validate phase completion [P0]
  - Run: `python .claude/skills/epic/scripts/validate-phase.py review [SESSION_DIR]`
  - **ITERATIVE COMPLIANCE FLOW:**
    - If validation PASSES: Proceed to Phase 7 (Iterate) if issues found, or complete workflow if no issues
    - If validation FAILS:
      1. Reinvoke review agents with EXPLICIT instruction: "Save your report to `[SESSION_DIR]/quality-report.md`"
      2. Re-run validation script
      3. Repeat steps 1-2 until validation passes
    - **CRITICAL:** Do NOT proceed to next phase until validation passes

### Phase 7: Iterate

**Objective:** Address feedback and resolve issues until quality standards are met

- T023: Delegate troubleshooting to `troubleshooter` agent if issues found [P0]
  - **CRITICAL: Include explicit save instruction in delegation prompt if issues exist:**
    ```
    "Please diagnose and resolve the errors/bugs/build failures found in the
    quality report at [SESSION_DIR]/quality-report.md.

    OPTIONAL: If troubleshooting is performed, save your troubleshooting report to:
    [SESSION_DIR]/troubleshooting-report.md

    This file is optional but helpful for documentation."
    ```
  - Diagnose errors, bugs, or build failures
  - Resolve runtime exceptions
  - Fix configuration problems
  - **Agent MAY save report to: `[SESSION_DIR]/troubleshooting-report.md` (optional)**

- T024: Address review feedback (main agent) [P0]
  - Read the quality report: `[SESSION_DIR]/quality-report.md`
  - Implement suggested improvements
  - Fix identified issues
  - Update `[SESSION_DIR]/implementation-complete.md` with changes made

- T025: Repeat review phase if significant changes made [P1]
  - If major modifications were implemented, return to Phase 6
  - Ensure changes don't introduce regressions
  - This creates an iteration loop: Review → Iterate → Review until quality passes

- T026: Final verification [P0]
  - Confirm all success criteria from `[SESSION_DIR]/implementation-plan.md` are met
  - Verify no regressions introduced
  - **CRITICAL: Main agent creates final verification summary:**
    ```
    Save a summary confirming all criteria are met, no regressions exist,
    and the implementation is complete to:
    [SESSION_DIR]/final-verification.md

    This file is required for workflow validation.
    ```

- T027: Validate phase completion [P0]
  - Run: `python .claude/skills/epic/scripts/validate-phase.py iterate [SESSION_DIR]`
  - **ITERATIVE COMPLIANCE FLOW:**
    - If validation PASSES: EPIC workflow complete ✅
    - If validation FAILS:
      1. Main agent creates `[SESSION_DIR]/final-verification.md` with summary
      2. Re-run validation script
      3. Repeat until validation passes
    - **CRITICAL:** Do NOT mark workflow complete until validation passes

## 3. Implementation Strategy

### Agent Delegation Pattern

**CRITICAL: ALL delegation prompts MUST include explicit save instructions to SESSION_DIR**

**Phase 1 - Explore:**

- Use `Task` tool with `subagent_type="codebase-explorer"`
- **MUST include in prompt:** "Save your report to `[SESSION_DIR]/codebase-status.md`"
- Provide specific investigation goals
- Request comprehensive analysis of current state

**Phase 2 - Research:**

- Use `Task` tool with `subagent_type="research-specialist"`
- **MUST include in prompt:** "Save your report to `[SESSION_DIR]/research-report.md`"
- Conduct research on complex topics
- Validate approaches across multiple sources

**Phase 3 - Plan:**

- Use `Task` tool with `subagent_type="strategic-planner"`
- **MUST include in prompt:** "Save your plan to `[SESSION_DIR]/implementation-plan.md`"
- Provide paths to previous reports for context
- Analyze problem using exploration and research findings
- Devise optimal solution approaches

**Phase 4 - Validate Plan:**

- Use `Task` tool with `subagent_type="consulting-expert"`
- **MUST include in prompt:** "Save your feedback to `[SESSION_DIR]/validation-feedback.md`"
- Provide path to implementation plan for review
- Review proposed approaches objectively
- Identify risks and suggest alternatives

**Phase 5 - Implement:**

- Main agent executes directly (NO delegation)
- Read plan from `[SESSION_DIR]/implementation-plan.md`
- Use TodoWrite tool to track progress
- Follow plan strictly without deviation
- **Main agent MUST save:** `[SESSION_DIR]/implementation-complete.md`
- Ask clarifying questions via AskUserQuestion tool when needed

**Phase 6 - Review:**

- Use `Task` tool with appropriate review agent for code review
- **MUST include in prompt:** "Save your report to `[SESSION_DIR]/quality-report.md`"
- Provide path to implementation summary
- Use `Task` tool with `subagent_type="test-engineer"` for testing validation
- Compile all feedback from review agents

**Phase 7 - Iterate:**

- Use `Task` tool with `subagent_type="troubleshooter"` if issues found (optional)
- Provide path to quality report
- Address review feedback (main agent)
- Return to Phase 6 if significant changes made
- **Main agent MUST save:** `[SESSION_DIR]/final-verification.md`
- Final verification when all checks pass

### Progressive Task Tracking

- Create todo list at start of implementation phase
- Update task status in real-time
- Exactly ONE task in_progress at any time
- Mark tasks completed immediately upon finishing
- Never batch completion updates

### Iterative Compliance Validation

**CRITICAL Pattern: Validate → If Fail → Reinvoke → Repeat**

After EVERY phase, run the validation script:
- `python .claude/skills/epic/scripts/validate-phase.py <phase> <session-dir>`

If validation FAILS:
1. Identify which required file(s) are missing
2. Reinvoke the responsible subagent with explicit instruction to create missing file(s)
3. Re-run validation script
4. Repeat steps 1-3 until validation PASSES
5. **Do NOT proceed to next phase until validation passes**

This iterative flow ensures:
- Subagents complete their assigned tasks
- All required documentation is created
- Compliance is enforced at every phase
- No phase can be skipped or incomplete

### Session Directory Structure

All subagent reports MUST be saved to: `.claude/sessions/[NN]-[session-description]/`

Required files by phase:
- Phase 1 (Explore): `codebase-status.md`
- Phase 2 (Research): `research-report.md`
- Phase 3 (Plan): `implementation-plan.md`
- Phase 4 (Validate): `validation-feedback.md`
- Phase 5 (Implement): `implementation-complete.md`
- Phase 6 (Review): `quality-report.md`
- Phase 7 (Iterate): `final-verification.md`

### Strict Plan Adherence

- Follow the plan exactly as designed
- Do not implement beyond defined scope
- Do not improvise or add unplanned features
- Stop and ask if uncertain about any task
- Simple/lean approach over complex solutions

## 4. Constraints

- **CRITICAL:** Main agent ONLY implements - MUST delegate all other phases (Explore, Research, Plan, Validate, Review, Iterate)
- **CRITICAL:** Follow EXACT phase sequence - Explore → Research → Plan → Validate Plan → Implement → Review → Iterate
- **CRITICAL:** Run validation script after EVERY phase - do NOT proceed until validation PASSES
- **CRITICAL:** If validation fails, MUST reinvoke subagents until they create required files
- **CRITICAL:** Iterative compliance flow is MANDATORY - cannot skip or bypass validation
- **CRITICAL:** All subagent reports MUST be saved to session directory: `.claude/sessions/[NN]-[session-description]/`
- **CRITICAL:** Use TodoWrite tool throughout implementation to track progress
- **CRITICAL:** Follow plan strictly - no deviation or improvisation
- **CRITICAL:** Do not implement tasks beyond the defined scope
- **CRITICAL:** Mark exactly ONE task as in_progress at a time
- **CRITICAL:** Complete tasks immediately upon finishing (no batching)
- Do NOT skip exploration phase - comprehensive context gathering is required
- Do NOT skip research phase - research must happen BEFORE planning
- Do NOT skip planning phase - thorough strategy development is mandatory
- Do NOT skip validation phase - plan must be validated before implementation
- Do NOT skip review phase - validation and code review are essential
- Do NOT skip iteration phase - feedback must be addressed
- Do NOT proceed to next phase if validation fails - reinvoke subagents iteratively
- Do NOT create documentation files unless explicitly requested (except required phase reports)
- Do NOT add emojis unless user explicitly requests them
- Do NOT over-engineer - build for MVP with simple/lean approach
- Do NOT implement features, refactoring, or improvements beyond what was asked
- Only add comments where logic isn't self-evident
- Only validate at system boundaries (user input, external APIs)
- Delete unused code completely - no backwards-compatibility hacks
- Ask clarifying questions via AskUserQuestion tool when uncertain

## 5. Success Criteria

### Phase 1 - Exploration Success

- [ ] Comprehensive codebase context gathered via codebase-explorer agent
- [ ] Relevant files and components identified
- [ ] Current state and dependencies documented
- [ ] Exploration findings reviewed and synthesized

### Phase 2 - Research Success

- [ ] Research conducted via research-specialist agent
- [ ] Complex topics investigated thoroughly
- [ ] Approaches validated across multiple sources
- [ ] Best practices and patterns identified
- [ ] Technical recommendations documented

### Phase 3 - Planning Success

- [ ] Strategic plan developed via strategic-planner agent
- [ ] Problem analyzed comprehensively using exploration and research
- [ ] Multiple implementation paths identified
- [ ] Trade-offs and risks evaluated
- [ ] Consolidated implementation roadmap created
- [ ] Success criteria defined

### Phase 4 - Validation Success

- [ ] Plan reviewed via consulting-expert agent
- [ ] Potential risks and over-complications identified
- [ ] Pragmatic alternatives suggested where needed
- [ ] Plan refined based on validation feedback
- [ ] Final implementation strategy approved

### Phase 5 - Implementation Success

- [ ] Todo list created with all implementation tasks
- [ ] All planned tasks executed following specifications
- [ ] Code follows established patterns from exploration
- [ ] Todos marked as completed immediately after finishing
- [ ] No tasks left as in_progress if actually completed
- [ ] Implementation decisions documented appropriately
- [ ] No features or improvements added beyond scope

### Phase 6 - Review Success

- [ ] Code review completed via appropriate review agent
- [ ] Testing validation performed if tests exist
- [ ] All review findings documented
- [ ] Issues prioritized by severity
- [ ] Feedback compiled for iteration phase

### Phase 7 - Iteration Success

- [ ] Troubleshooting completed via troubleshooter agent (if needed)
- [ ] All review feedback addressed and implemented
- [ ] Issues and bugs resolved
- [ ] Re-review performed if significant changes made
- [ ] No regressions introduced
- [ ] Final verification confirms completion

### Overall Success

- [ ] All seven EPIC phases completed in correct sequence
- [ ] Proper delegation to specialized agents for all phases except Implementation
- [ ] Main agent handled implementation phase directly
- [ ] Research completed BEFORE planning
- [ ] Plan validated BEFORE implementation
- [ ] Plan followed strictly without deviation
- [ ] User requirements fully satisfied
- [ ] Code quality validated through review and iteration
- [ ] Documentation updated where required
