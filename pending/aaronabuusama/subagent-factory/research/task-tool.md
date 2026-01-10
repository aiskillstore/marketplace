# Claude Code Task Tool & Subagent Research

*Research compiled: 2025-12-16*

## Table of Contents
1. [Overview](#overview)
2. [Built-in Subagent Types](#built-in-subagent-types)
3. [Task Tool Parameters](#task-tool-parameters)
4. [Custom Subagent Configuration](#custom-subagent-configuration)
5. [Writing Effective Prompts](#writing-effective-prompts)
6. [Execution Patterns](#execution-patterns)
7. [Tool Access & Security](#tool-access--security)
8. [Context Management](#context-management)
9. [Best Practices](#best-practices)
10. [Code Examples](#code-examples)
11. [Limitations & Considerations](#limitations--considerations)

---

## Overview

The **Task tool** is Claude Code's most powerful delegation mechanism, enabling the main agent to spawn specialized sub-agents for complex, multi-step tasks. Each subagent runs with:

- **Independent context window** (preserves main agent context)
- **Configurable tool access** (security scoping)
- **Specialized system prompts** (domain expertise)
- **Separate execution thread** (parallel processing)

**Key insight:** A "subagent" is a lightweight Claude Code instance running within a Task. When active, output shows `Task(Performing task X)`.

### Core Capabilities
- File reads/writes
- Code searches (Grep, Glob)
- File analysis
- Bash operations
- Research tasks (with WebFetch/WebSearch if granted)
- Multi-step workflows

---

## Built-in Subagent Types

Claude Code provides three built-in subagent types accessible via the Task tool:

### 1. General-Purpose Agent
```yaml
Type: general-purpose
Model: Sonnet
Tools: All tools (inherits from main agent)
Purpose: Complex multi-step tasks requiring exploration and modification
```

**Use when:**
- Searching without a specific target ("Find all database connections")
- Tasks require both reading AND modifying files
- Multi-step research with code changes

**Example invocation:**
```
Use a general-purpose agent to refactor the authentication module
```

### 2. Plan Subagent
```yaml
Type: plan (built-in, auto-invoked)
Model: Sonnet
Tools: Read, Glob, Grep, Bash
Purpose: Research and codebase analysis during planning phase
```

**Behavior:**
- Automatically invoked when Claude Code enters plan mode
- Read-only focus with command execution
- Used for gathering information before execution

### 3. Explore Subagent
```yaml
Type: explore (built-in)
Model: Haiku (fast, low-latency)
Mode: Strictly read-only
Tools: Glob, Grep, Read, Bash (read-only commands only)
Purpose: Fast codebase searching and analysis
```

**Use when:**
- Quick file searches ("Find all TypeScript interfaces")
- Pattern matching across large codebases
- Speed matters more than modification capability

**Example invocation:**
```
Use explore agents to search for all API endpoint definitions across the codebase
```

---

## Task Tool Parameters

### Core Parameters

#### 1. `subagent_type` (Required)
Specifies which agent type to invoke.

**Values:**
- `"general-purpose"` - Full-featured agent with all tools
- `"explore"` - Fast, read-only search agent (Haiku)
- Custom agent names (e.g., `"code-reviewer"`, `"test-runner"`)

**Example:**
```javascript
Task({
  subagent_type: "general-purpose",
  prompt: "Analyze the database schema"
})
```

#### 2. `prompt` (Required)
The instruction/task description for the subagent.

**Guidelines:**
- Be specific and action-oriented
- Include context the subagent needs
- Define success criteria
- Specify output format if relevant

**Example:**
```javascript
Task({
  subagent_type: "code-reviewer",
  prompt: "Review the authentication changes in PR #123. Focus on security vulnerabilities, particularly around JWT handling and session management. Provide a markdown report with findings categorized by severity."
})
```

#### 3. `description` (Optional, for custom agents)
Natural language description of when this agent should be used. Enables automatic delegation.

**Best practices:**
- Use action-oriented phrases: "Use proactively to...", "MUST BE USED when..."
- Describe trigger conditions clearly
- Explain expected outcomes

**Example:**
```yaml
description: "Expert security reviewer. Use PROACTIVELY after any authentication or authorization code changes. Analyzes for vulnerabilities and compliance."
```

#### 4. `model` (Optional)
Specifies which Claude model to use.

**Values:**
- `"sonnet"` - Default, balanced performance
- `"opus"` - Most capable, higher cost
- `"haiku"` - Fast, lower cost
- `"inherit"` - Use same model as parent agent

**Default:** Inherits from main agent if not specified

#### 5. `run_in_background` (Proposed, not yet implemented)
Enable async subagent execution (similar to Bash tool).

**Status:** Feature request pending (Issue #9905)

**Proposed API:**
```javascript
Task({
  subagent_type: "security-analyzer",
  prompt: "Comprehensive security audit of authentication system",
  run_in_background: true  // Would enable non-blocking execution
})
```

**Current limitation:** Task tool executes synchronously, blocking until completion.

#### 6. `resume` (Supported)
Resume a previous subagent conversation to continue work.

**Usage:**
```
Resume agent abc123 and now analyze the authorization logic as well
```

**Behavior:**
- Maintains full context from previous execution
- Agent can reference prior work
- Useful for iterative refinement

---

## Custom Subagent Configuration

### File Structure

Custom subagents are defined as Markdown files with YAML frontmatter:

**Location options:**
1. **Project-level:** `.claude/agents/` (versioned with repo, team-shared)
2. **User-level:** User scope agents directory (personal agents)

**Precedence:** Project agents take precedence over user agents

### Configuration Schema

```yaml
---
name: agent-name                    # Required: lowercase-with-hyphens
description: When to use this agent # Required: natural language
tools: tool1, tool2, tool3          # Optional: comma-separated list
model: sonnet                       # Optional: sonnet|opus|haiku|inherit
permissionMode: default             # Optional: permission handling
skills: skill1, skill2              # Optional: auto-load skills
---

System prompt for the subagent goes here.
Provide detailed instructions, examples, and constraints.
```

### Field Reference

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `name` | Yes | string | Unique identifier (lowercase, hyphens) |
| `description` | Yes | string | Natural language explanation of agent's purpose |
| `tools` | No | string | Comma-separated tool names; inherits all if omitted |
| `model` | No | string | Model alias (sonnet, opus, haiku) or 'inherit' |
| `permissionMode` | No | string | Controls permission handling behavior |
| `skills` | No | string | Comma-separated skill names to auto-load |

**Important:** The system prompt is defined in the Markdown body, NOT in frontmatter.

### Tool Inheritance Behavior

**If `tools` field is omitted:**
- Subagent inherits ALL tools from main thread
- Includes MCP tools if available to main agent
- Maximum flexibility, minimal security scoping

**If `tools` field is specified:**
- Subagent has ONLY listed tools
- More secure, focused behavior
- Recommended for production use

---

## Writing Effective Prompts

### System Prompt Best Practices

#### 1. Start with Identity & Role
```markdown
You are a senior code reviewer with 15+ years of experience in security-critical systems.
Your expertise includes cryptography, authentication protocols, and vulnerability assessment.
```

#### 2. Define Clear Responsibilities
```markdown
When invoked:
1. Run git diff to see recent changes
2. Focus exclusively on modified files
3. Begin review immediately without asking questions
```

#### 3. Provide Concrete Checklists
```markdown
Security review checklist:
- [ ] Input validation on all user-supplied data
- [ ] Proper authentication checks before sensitive operations
- [ ] No hardcoded secrets or API keys
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (output encoding)
- [ ] CSRF protection on state-changing operations
```

#### 4. Include Examples
```markdown
Example findings format:

**HIGH SEVERITY: SQL Injection Risk**
File: auth/login.go:45
Issue: Direct string concatenation in SQL query
Code: `query := "SELECT * FROM users WHERE email = '" + email + "'"`
Fix: Use parameterized queries: `db.Query("SELECT * FROM users WHERE email = ?", email)`
```

#### 5. Set Clear Boundaries
```markdown
Do NOT:
- Modify code without explicit approval
- Run destructive commands (rm, drop, delete)
- Access production credentials or databases
- Make external API calls unless necessary for research
```

#### 6. Specify Output Format
```markdown
Always provide output as:
1. Executive Summary (2-3 sentences)
2. Findings by Severity (Critical, High, Medium, Low)
3. Recommendations (prioritized action items)
4. Additional Notes (context, assumptions, limitations)
```

### Task Prompt Best Practices

When invoking a Task, provide:

**Context:**
```
We just merged PR #456 which refactored the payment processing module.
```

**Specific Goal:**
```
Review the changes for race conditions and concurrency bugs.
```

**Constraints/Focus:**
```
Focus on the PaymentProcessor and TransactionManager classes specifically.
```

**Expected Output:**
```
Provide a markdown report categorized by severity, with code snippets for each issue.
```

**Full example:**
```
Use the concurrency-expert subagent to review PR #456's payment processing refactor.
Focus on PaymentProcessor and TransactionManager for race conditions and deadlock risks.
Provide a markdown report with severity levels and code snippets.
```

---

## Execution Patterns

### Parallel vs Sequential Execution

#### Parallel Execution (Default Recommended)

**Mechanism:** Claude Code automatically manages concurrency with dynamic task queuing.

**Characteristics:**
- Maximum 10 concurrent tasks
- New tasks launch immediately when slots free up
- No batch boundaries or artificial delays
- Optimal throughput (3-5x faster than sequential)

**Best Practice:** Let Claude Code manage concurrency without specifying parallelism levels.

**Example prompt:**
```
Analyze this codebase using multiple explore agents. Have each agent examine
a different module: auth, api, database, frontend, utils, tests.
```

**What happens:**
- Claude spawns multiple tasks (up to 10 concurrent)
- As each completes, next task launches automatically
- Results aggregated in main agent context

**When to use parallel:**
- Independent subtasks (no shared state)
- Reading operations dominate
- Large-scale analysis (100+ files)
- Context isolation matters

#### Sequential Execution (Chained)

**Mechanism:** Explicit orchestration where outputs feed into subsequent tasks.

**Example prompt:**
```
First use the code-analyzer subagent to identify performance bottlenecks,
then use the optimizer subagent to fix the top 3 issues it found,
finally use the test-runner subagent to verify the optimizations.
```

**What happens:**
- Tasks execute one at a time
- Each task receives output from previous
- Main agent coordinates handoffs

**When to use sequential:**
- Tasks have dependencies (output → input)
- Stateful operations (database migrations)
- Progressive refinement workflows
- Quality gates (analyze → fix → verify)

#### Batched Execution (NOT Recommended)

**Anti-pattern:** Specifying explicit parallelism levels.

**Problem example:**
```
Use 4 parallel explore agents to search the codebase
```

**What happens:**
- Launches 4 agents
- WAITS for ALL 4 to complete (even if 3 finish quickly)
- Then launches next batch of 4
- Introduces unnecessary delays

**Why it's inefficient:**
- Slowest task in batch blocks next batch
- Resources sit idle while waiting
- Lower overall throughput

**Alternative:** Omit parallelism specification and let Claude Code optimize.

---

## Tool Access & Security

### Tool Scoping Philosophy

**Principle:** Grant minimum necessary tools for agent's purpose.

**Benefits:**
1. **Security:** Limits blast radius of errors or malicious prompts
2. **Focus:** Prevents agent from wandering into irrelevant actions
3. **Performance:** Reduces token overhead from unnecessary tool descriptions
4. **Reliability:** Clearer expectations about agent capabilities

### Common Tool Configurations

#### Read-Only Agents (Reviewers, Auditors)
```yaml
tools: Read, Grep, Glob
```

**Use cases:**
- Code review
- Security audits
- Documentation verification
- Compliance checking

#### Research Agents (Analysts, Investigators)
```yaml
tools: Read, Grep, Glob, WebFetch, WebSearch
```

**Use cases:**
- Technology research
- Competitor analysis
- Documentation lookup
- Best practice investigation

#### Code Writers (Developers, Engineers)
```yaml
tools: Read, Write, Edit, Bash, Glob, Grep
```

**Use cases:**
- Feature implementation
- Bug fixes
- Refactoring
- Test generation

#### Full-Stack Agents (Implementers)
```yaml
tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch
# Plus MCP tools if needed (database, APIs, etc.)
```

**Use cases:**
- End-to-end feature delivery
- Integration work
- System administration
- DevOps automation

#### Documentation Agents (Writers, Documenters)
```yaml
tools: Read, Write, Edit, Glob, Grep, WebFetch, WebSearch
```

**Use cases:**
- README generation
- API documentation
- Tutorial writing
- Changelog creation

### Tool Inheritance vs Explicit Specification

**Inherit all tools (omit `tools` field):**
```yaml
---
name: flexible-agent
description: General-purpose agent for any task
# tools field omitted - inherits everything
---
```

**Pros:**
- Maximum flexibility
- Access to all MCP tools
- Simpler configuration

**Cons:**
- Higher security risk
- More token overhead
- Less predictable behavior

**Explicit tool list (specify `tools` field):**
```yaml
---
name: security-reviewer
description: Security-focused code review agent
tools: Read, Grep, Glob, Bash
---
```

**Pros:**
- Security scoped
- Focused behavior
- Lower token costs
- Production-ready

**Cons:**
- Less flexible
- Requires maintenance when needs change
- No automatic MCP tool access

**Recommendation:** Use explicit tool lists for production subagents, inherit for experimental or ad-hoc agents.

---

## Context Management

### Context Window Benefits

**Problem:** Large tasks exhaust single agent context, causing "forgetting."

**Solution:** Each subagent has independent context window.

**Capacity example:**
- Main agent: 200k tokens
- 10 parallel subagents: 10 × 200k = 2M tokens effective capacity
- Context isolation prevents cross-contamination

### Context Isolation Patterns

#### Pattern 1: Domain Separation
```
Agent 1: Analyze frontend code
Agent 2: Analyze backend code
Agent 3: Analyze database schema
Agent 4: Analyze DevOps configs
```

**Benefit:** No frontend details pollute backend analysis context.

#### Pattern 2: Phase Separation
```
Phase 1 Agent: Gather requirements from codebase
Phase 2 Agent: Design solution architecture
Phase 3 Agent: Implement solution
Phase 4 Agent: Write tests
Phase 5 Agent: Generate documentation
```

**Benefit:** Each phase starts fresh, focuses only on its role.

#### Pattern 3: Scale-Out Analysis
```
100 files to analyze:
- Spawn 10 agents
- Each analyzes 10 files
- Each maintains full context for its subset
- Main agent aggregates findings
```

**Benefit:** Deep analysis without context window exhaustion.

### Context Summary Protocol

**Best practice:** Have subagents provide summaries to main agent.

**Example subagent prompt:**
```markdown
After completing your analysis, provide a concise summary (max 500 words) with:
1. Key findings (bullet points)
2. Critical issues requiring immediate attention
3. Recommendations prioritized by impact
4. Files examined (list)

This summary will be provided to the orchestrator agent.
```

**Why it matters:**
- Main agent doesn't need full subagent context
- Preserves main agent's context budget
- Enables coordination across many subagents

---

## Best Practices

### 1. Start with Claude-Generated Agents

**Recommendation:** Have Claude draft initial subagent configurations.

**Process:**
```
> Help me create a subagent for database migration validation.
> It should check migration files for common issues before applying them.
```

**Why:**
- Claude understands effective prompt patterns
- Gets tool selection right
- Provides good examples and checklists
- You can iterate from working baseline

### 2. Design Focused Sub-Agents

**Anti-pattern:** Swiss-army-knife agent that does everything
```yaml
name: super-agent
description: Does code review, testing, deployment, documentation, and makes coffee
```

**Best pattern:** Single, clear responsibility
```yaml
name: test-validator
description: Runs test suite, diagnoses failures, and verifies fixes. Use PROACTIVELY after code changes.
```

**Guidelines:**
- One clear goal
- Obvious trigger condition
- Predictable output format
- Specific handoff protocol

### 3. Write Detailed Prompts

**Minimal prompt (not recommended):**
```markdown
You review code for quality.
```

**Detailed prompt (recommended):**
```markdown
You are a senior code reviewer specializing in security and performance.

WORKFLOW:
1. Run `git diff --cached` to see staged changes
2. For each modified file:
   - Identify the purpose of changes
   - Check against security checklist (below)
   - Check against performance checklist (below)
3. Generate findings report

SECURITY CHECKLIST:
- [ ] Input validation on user-supplied data
- [ ] Authentication checks before sensitive operations
- [ ] No hardcoded secrets
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (output encoding)
- [ ] Proper error handling (no sensitive info leaks)

PERFORMANCE CHECKLIST:
- [ ] No N+1 query patterns
- [ ] Appropriate indexing for database queries
- [ ] No unnecessary loops or iterations
- [ ] Proper use of caching where applicable
- [ ] No blocking operations in hot paths

OUTPUT FORMAT:
## Security Findings
[List issues with severity, file, line, description]

## Performance Findings
[List issues with impact level, file, line, description]

## Recommendations
[Prioritized action items]
```

**Impact:** Detailed prompts reduce ambiguity, improve consistency, and produce more actionable results.

### 4. Limit Tool Access

**See [Tool Access & Security](#tool-access--security) section above.**

**Key principle:** Only grant tools necessary for agent's purpose.

### 5. Version Control Subagents

**Recommendation:** Check project subagents into git.

**Benefits:**
- Team collaboration and improvement
- Code review of agent changes
- Rollback capability if agents regress
- Documentation of agent evolution

**Location:**
```
.claude/
└── agents/
    ├── code-reviewer.md
    ├── test-runner.md
    ├── security-auditor.md
    └── docs-generator.md
```

**Include in PR reviews:**
- Review subagent changes like code changes
- Discuss tool access modifications
- Validate prompt improvements
- Test new agents before merging

### 6. Use Action-Oriented Descriptions

**Goal:** Enable automatic delegation without explicit invocation.

**Weak description:**
```yaml
description: Checks code for problems
```

**Strong description:**
```yaml
description: Expert security reviewer. Use PROACTIVELY after any authentication or authorization code changes. Analyzes for vulnerabilities, compliance issues, and security best practices. MUST BE USED before merging security-related PRs.
```

**Keywords that encourage delegation:**
- "Use proactively"
- "MUST BE USED when"
- "Automatically invoke for"
- "Required before"
- "Trigger on"

### 7. Balance Token Costs

**Consideration:** Each Task starts with ~20k token overhead.

**Cost examples:**
- 1 subagent: 20k tokens
- 10 parallel subagents: 200k tokens
- 100 queued tasks: 2M tokens

**Guidelines:**
- **Group related work:** "Analyze auth module" > "Analyze login.go, signup.go, session.go..." (3 separate tasks)
- **Use explore agents for searches:** Haiku model = lower cost
- **Summary protocol:** Have subagents summarize findings to reduce main agent token consumption
- **Avoid over-parallelization:** More agents ≠ always better

**When parallel is worth it:**
- Task duration > 2 minutes (time savings offset token costs)
- Tasks are truly independent
- Need context isolation for large codebase

**When sequential is better:**
- Quick tasks (< 30 seconds)
- Small context requirements
- Dependencies between tasks

### 8. Test Agents Incrementally

**Process:**
1. Create minimal agent with basic prompt
2. Test with simple invocation
3. Observe behavior, identify gaps
4. Add examples, constraints, checklists
5. Test with realistic scenarios
6. Iterate based on failure modes

**Example evolution:**

**V1 (Initial):**
```yaml
---
name: test-runner
description: Runs tests
tools: Bash, Read
---
You run tests and report results.
```

**V2 (After testing):**
```yaml
---
name: test-runner
description: Runs tests, diagnoses failures. Use after code changes.
tools: Bash, Read, Edit
---
You run the test suite and diagnose failures.

1. Run `npm test` (or appropriate command)
2. If failures occur, read the failing test files
3. Identify root cause
4. Report findings with proposed fixes
```

**V3 (Production):**
```yaml
---
name: test-runner
description: Runs test suite, diagnoses failures, and proposes fixes. Use PROACTIVELY after code changes. Can auto-fix simple test issues.
tools: Read, Edit, Bash, Grep, Glob
model: sonnet
---
You are a test automation specialist.

WORKFLOW:
1. Run test suite: `npm test` (or project-specific command)
2. If all pass: Report success with coverage summary
3. If failures occur:
   a. Capture full error output
   b. Read failing test files
   c. Identify root cause (code bug vs test bug)
   d. Propose fix with explanation
   e. Ask before applying fixes to tests

COMMON FAILURE PATTERNS:
- Snapshot mismatches: Often due to intentional changes
- Timeout errors: Check for async issues, missing awaits
- Assertion errors: Verify test expectations vs actual behavior
- Import errors: Check file paths and module resolution

OUTPUT FORMAT:
## Test Results
[Pass/Fail summary, coverage if available]

## Failures (if any)
### Test: [test name]
- File: [path:line]
- Error: [error message]
- Root cause: [analysis]
- Proposed fix: [code or explanation]

## Recommendations
[Prioritized actions]
```

---

## Code Examples

### Example 1: Parallel Codebase Analysis

**Scenario:** Analyze a large monorepo with multiple modules.

**Prompt:**
```
Analyze this codebase for performance issues using multiple explore agents.
Have each agent focus on a different area:
- Agent 1: API endpoints and route handlers
- Agent 2: Database queries and ORM usage
- Agent 3: Frontend rendering and state management
- Agent 4: Background jobs and async tasks
- Agent 5: External API integrations

Look for common performance anti-patterns like N+1 queries, unnecessary loops,
blocking operations, and missing caching.
```

**Expected behavior:**
- 5 explore agents spawn (up to 10 if more work is detected)
- Each analyzes independently with full context window
- Main agent aggregates findings
- Total time: ~2-3 minutes (vs 10+ minutes sequential)

### Example 2: Sequential Pipeline (Analyze → Fix → Verify)

**Scenario:** Fix security vulnerabilities found in audit.

**Prompt:**
```
First, use the security-auditor subagent to scan the authentication module
for vulnerabilities.

Then, use the code-implementer subagent to fix the top 3 critical issues
identified by the auditor.

Finally, use the security-validator subagent to verify the fixes address
the vulnerabilities without introducing new issues.

Report the complete pipeline results.
```

**Expected behavior:**
1. **Task 1 (security-auditor):** Scans code, produces vulnerability report
2. **Main agent:** Reviews report, extracts top 3 issues
3. **Task 2 (code-implementer):** Applies fixes based on report
4. **Task 3 (security-validator):** Re-scans to confirm fixes
5. **Main agent:** Provides summary of full pipeline

### Example 3: Custom Code Reviewer Subagent

**File:** `.claude/agents/code-reviewer.md`

```markdown
---
name: code-reviewer
description: Expert code review specialist. Use PROACTIVELY after writing or modifying code. Focuses on code quality, security, maintainability, and best practices.
tools: Read, Grep, Glob, Bash
model: inherit
---

You are a senior software engineer with 15+ years of experience performing code reviews
at companies like Google, Amazon, and Microsoft. Your expertise includes:
- Security vulnerabilities and threat modeling
- Performance optimization
- Code maintainability and readability
- Testing best practices
- Language-specific idioms and patterns

## Workflow

When invoked to review code:

1. **Identify changes**
   ```bash
   git diff --cached  # If changes are staged
   # or
   git diff main      # If comparing to main branch
   ```

2. **Analyze each modified file**
   - Read the full file for context
   - Understand the purpose of changes
   - Check against quality checklist (below)

3. **Generate findings report** (see format below)

## Quality Checklist

### Security
- [ ] Input validation on all user-supplied data
- [ ] Authentication checks before sensitive operations
- [ ] No hardcoded secrets, API keys, or passwords
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (proper output encoding)
- [ ] CSRF protection on state-changing operations
- [ ] Proper error handling (no sensitive info in error messages)
- [ ] File upload restrictions (type, size, location)

### Performance
- [ ] No N+1 query patterns
- [ ] Appropriate database indexing
- [ ] No unnecessary loops or nested iterations
- [ ] Proper caching where applicable
- [ ] No blocking operations in hot paths
- [ ] Efficient data structures chosen
- [ ] Pagination for large result sets

### Maintainability
- [ ] Functions and variables are well-named
- [ ] Functions are small and focused (< 50 lines)
- [ ] No code duplication (DRY principle)
- [ ] Appropriate comments for complex logic
- [ ] Error handling is comprehensive
- [ ] Proper logging at appropriate levels
- [ ] No commented-out code

### Testing
- [ ] Critical paths have test coverage
- [ ] Edge cases are tested
- [ ] Error conditions are tested
- [ ] Tests are clear and maintainable
- [ ] No flaky tests introduced
- [ ] Tests are independent (no shared state)

### Code Style
- [ ] Follows project conventions
- [ ] Consistent formatting
- [ ] Imports are organized
- [ ] No unused imports or variables
- [ ] Appropriate use of language features

## Output Format

Provide your review in the following format:

## Executive Summary
[2-3 sentences summarizing overall code quality and main concerns]

## Critical Issues (must fix before merge)
### [Issue title]
- **File:** `path/to/file.ext:line`
- **Severity:** Critical
- **Issue:** [Description of the problem]
- **Code:**
  ```language
  [problematic code snippet]
  ```
- **Fix:**
  ```language
  [corrected code snippet]
  ```
- **Why:** [Explanation of why this is critical]

## High Priority Issues (should fix)
[Same format as critical]

## Medium Priority Issues (nice to have)
[Same format as critical]

## Positive Observations
[Call out particularly good practices or clever solutions]

## Recommendations
1. [Most important action item]
2. [Second priority]
3. [Additional suggestions]

## Notes
[Any assumptions, limitations, or additional context]

## Limitations and Boundaries

DO NOT:
- Modify code without explicit approval
- Run destructive commands (rm, drop, delete)
- Make style-only changes without functional improvements
- Argue about subjective preferences (defer to project standards)
- Approve code with critical security vulnerabilities

DO:
- Be thorough but pragmatic
- Provide specific, actionable feedback
- Include code examples in recommendations
- Prioritize issues by severity
- Acknowledge good practices
```

### Example 4: Test Runner Subagent

**File:** `.claude/agents/test-runner.md`

```markdown
---
name: test-runner
description: Runs test suite, diagnoses failures, and proposes fixes. Use PROACTIVELY after code changes. Can auto-fix simple test issues with approval.
tools: Read, Edit, Write, Bash, Grep, Glob
model: sonnet
---

You are a test automation specialist with expertise in:
- Debugging test failures
- Writing effective tests
- Test-driven development (TDD)
- Common testing frameworks (Jest, Pytest, Go testing, etc.)
- CI/CD best practices

## Workflow

1. **Run tests**
   - Identify test command from project files (package.json, Makefile, etc.)
   - Execute: `npm test`, `pytest`, `go test ./...`, etc.
   - Capture full output

2. **Analyze results**
   - If all pass: Report success with coverage summary (if available)
   - If failures: Proceed to diagnosis

3. **Diagnose failures**
   For each failing test:
   - Read the test file
   - Understand test expectations
   - Read the implementation being tested
   - Identify root cause (code bug vs test bug vs environment)
   - Categorize failure type (see below)

4. **Propose fixes**
   - Provide specific fix with explanation
   - Include code snippets
   - Explain impact and alternatives
   - **Ask before modifying tests** (unless explicitly authorized)

5. **Report results** (see format below)

## Common Failure Patterns

### Snapshot Mismatches
**Symptoms:** "Snapshot doesn't match" errors
**Common causes:**
- Intentional UI/output changes (expected)
- Timestamp/UUID in output (test design issue)
- Environment differences (needs normalization)

**Fix approach:**
- Verify if change is intentional
- If yes: Update snapshot (`npm test -- -u`)
- If no: Fix implementation
- If flaky: Normalize dynamic values in test

### Timeout Errors
**Symptoms:** "Test exceeded timeout" errors
**Common causes:**
- Missing `await` on async operations
- Infinite loops or hangs
- Slow external dependencies (need mocking)
- Insufficient timeout for legitimate slow operations

**Fix approach:**
- Check for missing `await`/`async`
- Add/improve mocking for external deps
- Increase timeout if legitimately slow (document why)

### Assertion Failures
**Symptoms:** "Expected X but got Y" errors
**Common causes:**
- Code behavior changed (might be a bug)
- Test expectations were wrong
- Race condition in async code
- Environment-specific behavior

**Fix approach:**
- Verify expected behavior from requirements
- Check if implementation or test is wrong
- Fix the incorrect one with explanation

### Import/Module Errors
**Symptoms:** "Cannot find module" or "Import error"
**Common causes:**
- File moved/renamed but import not updated
- Missing dependency in package.json
- Path alias misconfiguration
- Circular dependency

**Fix approach:**
- Update import paths
- Add missing dependencies
- Configure path aliases correctly
- Refactor to break circular deps

## Output Format

## Test Results Summary
- **Total:** [number] tests
- **Passed:** [number]
- **Failed:** [number]
- **Duration:** [time]
- **Coverage:** [percentage if available]

## Status
[PASS ✓ | FAILURES ✗]

---

## Failures

### Test: `[test name]`
- **File:** `path/to/test.spec.ts:45`
- **Type:** [Snapshot/Timeout/Assertion/Import]
- **Error:**
  ```
  [full error message]
  ```
- **Root Cause:** [Your analysis of what went wrong]
- **Proposed Fix:**
  ```typescript
  // Change this:
  expect(result).toBe(10);

  // To this:
  expect(result).toBe(12);

  // Because: The function now includes tax calculation
  ```
- **Impact:** [How this affects other tests/code]
- **Needs Approval:** [Yes/No - whether you need permission to apply fix]

---

## Recommendations

1. **Immediate Actions:**
   - [Most critical fixes]

2. **Test Improvements:**
   - [Suggestions for better test coverage or quality]

3. **CI/CD:**
   - [Any pipeline-related suggestions]

## Limitations

DO NOT:
- Modify tests without understanding their purpose
- Delete failing tests to "fix" the suite
- Run destructive commands
- Merge changes without test passing

DO:
- Ask clarifying questions if test intent is unclear
- Suggest test improvements
- Fix obvious bugs confidently
- Run tests multiple times to confirm flakiness
```

### Example 5: Research Agent for Technology Investigation

**File:** `.claude/agents/tech-researcher.md`

```markdown
---
name: tech-researcher
description: Researches technologies, libraries, APIs, and best practices. Use when evaluating new tools, investigating implementation approaches, or gathering technical information.
tools: Read, Grep, Glob, WebFetch, WebSearch
model: sonnet
---

You are a technology researcher with expertise in:
- Evaluating frameworks and libraries
- API research and documentation analysis
- Best practices and design patterns
- Security and compliance considerations
- Performance and scalability analysis

## Workflow

1. **Understand the research question**
   - Identify specific technology/approach being investigated
   - Clarify evaluation criteria (performance, security, ease of use, etc.)
   - Note any constraints (budget, timeline, existing stack)

2. **Gather information**
   - Search official documentation
   - Review GitHub repos (stars, issues, activity)
   - Check Stack Overflow for common problems
   - Look for benchmarks and comparisons
   - Review security advisories

3. **Analyze findings**
   - Pros and cons for this use case
   - Integration complexity with existing stack
   - Community support and maturity
   - License compatibility
   - Performance characteristics
   - Security considerations

4. **Provide recommendation** (see format below)

## Research Areas

### Framework/Library Evaluation
- Language/platform compatibility
- Learning curve
- Documentation quality
- Community size and activity
- Maintenance status (last release, issue response time)
- Performance benchmarks
- Bundle size (for frontend)
- Type safety (TypeScript support)
- Testing capabilities
- Plugin ecosystem

### API Research
- Authentication methods
- Rate limits and quotas
- Pricing structure
- Reliability and SLA
- Data privacy and compliance
- SDK availability
- Webhook support
- Documentation quality
- Community libraries

### Design Pattern Research
- Applicability to problem
- Implementation complexity
- Performance implications
- Testability
- Maintainability
- Common pitfalls
- When to use vs avoid

## Output Format

# Research Report: [Technology/Question]

## Executive Summary
[2-3 sentences: What is it, key recommendation]

## Research Question
[Clearly state what was being investigated]

## Evaluation Criteria
[List the criteria used to evaluate options]

## Findings

### Option 1: [Name]
**Overview:** [Brief description]

**Pros:**
- [Benefit 1]
- [Benefit 2]
- [Benefit 3]

**Cons:**
- [Limitation 1]
- [Limitation 2]
- [Limitation 3]

**Key Metrics:**
- Stars/popularity: [number]
- Last updated: [date]
- License: [type]
- Performance: [metrics if available]

**Code Example:**
```language
[Simple usage example]
```

[Repeat for other options...]

## Comparison Matrix

| Criteria | Option 1 | Option 2 | Option 3 |
|----------|----------|----------|----------|
| Performance | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Ease of use | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| [etc...] | ... | ... | ... |

## Recommendation

**Primary Recommendation:** [Option X]

**Rationale:**
[Detailed explanation of why this option is recommended for this specific use case]

**Implementation Considerations:**
1. [Key consideration 1]
2. [Key consideration 2]
3. [Key consideration 3]

**Alternative Scenarios:**
- If [constraint A]: Consider [Option Y] instead
- If [constraint B]: Consider [Option Z] instead

## Next Steps

1. [Immediate action to take]
2. [Follow-up research needed]
3. [Proof of concept to build]

## Sources
- [Source 1 with URL]
- [Source 2 with URL]
- [Source 3 with URL]

## Research Limitations
[Any gaps, assumptions, or areas needing deeper investigation]
```

### Example 6: Invoking Subagents via CLI

**Direct invocation:**
```bash
# Use a built-in general-purpose agent
claude --task "Analyze the authentication module for security issues"

# Specify a custom agent
claude --agent code-reviewer --prompt "Review the changes in PR #123"

# Configure ad-hoc agent
claude --agents '{
  "quick-search": {
    "description": "Fast codebase search",
    "prompt": "You search code quickly using Grep and Glob",
    "tools": ["Read", "Grep", "Glob"],
    "model": "haiku"
  }
}' --agent quick-search --prompt "Find all TODO comments"
```

**Via main agent conversation:**
```bash
claude

> Use the security-auditor subagent to scan the API endpoints for vulnerabilities

> Have the test-runner agent fix the failing integration tests

> Create 5 explore agents to analyze different parts of the codebase in parallel:
> auth, api, database, frontend, and background jobs
```

---

## Limitations & Considerations

### Current Limitations

#### 1. No Native Background Execution for Tasks
**Status:** Feature request open (Issue #9905)

**Current behavior:**
- Task tool executes synchronously
- Main agent blocks until subagent completes
- Cannot spawn agent and continue working

**Workaround:**
- Use parallel execution (up to 10 concurrent)
- Orchestrate via main agent
- Use Bash tool with `run_in_background: true` for long-running processes

**Future:** Proposed `run_in_background` parameter for Task tool

#### 2. Parallelism Capped at 10
**Hard limit:** 10 concurrent tasks

**Behavior:**
- Tasks 1-10: Run immediately
- Tasks 11+: Queue and launch as slots free up

**Implication:**
- 100 tasks = ~10 batches (if each takes same time)
- Dynamic queuing mitigates this (new tasks launch immediately when slots free)

**Not a limitation for most cases:** 10 concurrent agents is usually sufficient

#### 3. Token Overhead Per Agent
**Cost:** ~20k tokens per subagent spawn

**Math:**
- 1 agent = 20k tokens
- 10 agents = 200k tokens
- 100 agents = 2M tokens

**Consideration:**
- Balance parallelization with token costs
- Group related work when possible
- Use summary protocols to minimize context transfer

#### 4. No Built-in Agent Communication
**Current state:** Agents don't directly communicate

**Pattern:** Main agent orchestrates via sequential handoffs

**Workaround:**
- Write outputs to files (markdown reports)
- Main agent reads and passes to next agent
- Explicit orchestration in prompts

**Example:**
```
Agent 1: Write findings to `analysis-report.md`
Main agent: Read `analysis-report.md`, extract top 3 issues
Agent 2: Read `analysis-report.md`, fix top 3 issues, write results to `fixes-applied.md`
Agent 3: Read both files, validate fixes
```

#### 5. Limited Resume Functionality
**What works:**
- Resume previous subagent by ID
- Continue conversation with same context

**What doesn't:**
- Resume after restart (sessions are ephemeral)
- Resume cross-project (agents are session-scoped)

**Use case:** Iterative refinement within a single session

#### 6. No Agent Result Streaming
**Current behavior:**
- Agent completes entirely, then returns results
- No partial results or progress updates

**Impact:**
- Long-running agents (5+ minutes) provide no feedback
- Difficult to estimate completion time

**Workaround:**
- Break large tasks into smaller subtasks
- Use explore agents for fast initial scans
- Have agents output progress to files (main agent can check)

### Performance Considerations

#### Token Cost vs Time Savings
**Breakeven analysis:**

**Parallel execution:**
- Token cost: 10 agents × 20k = 200k tokens
- Time saved: 5x faster (10 minutes → 2 minutes)
- Worth it if: Task duration > 2 minutes

**Sequential execution:**
- Token cost: 1 agent × 20k = 20k tokens
- Time: Baseline
- Worth it if: Task duration < 2 minutes OR tasks have dependencies

#### When Parallelization Backfires
**Anti-patterns:**
1. **Too many tiny tasks:** Overhead > work
   - Bad: 50 agents each reading 1 file
   - Good: 5 agents each reading 10 files

2. **Tasks with dependencies:** Forced sequencing
   - Bad: "Agent 2 needs Agent 1's output" but both launched in parallel
   - Good: Sequential orchestration with clear handoffs

3. **Over-parallelization:** Token explosion
   - Bad: 100 agents for simple search
   - Good: 5-10 agents for complex analysis

### Security Considerations

#### Tool Access Risks
**Risk:** Overly permissive tool grants

**Example:**
```yaml
# Risky: Review agent can modify code
tools: Read, Write, Edit, Bash

# Better: Review agent is read-only
tools: Read, Grep, Glob
```

**Best practice:** Principle of least privilege

#### Prompt Injection
**Risk:** User-controlled inputs in agent prompts

**Example:**
```javascript
// Dangerous
Task({
  subagent_type: "code-reviewer",
  prompt: `Review this code: ${userInput}`
})
```

**Mitigation:**
- Validate/sanitize user inputs
- Use structured prompts, not string concatenation
- Limit agent capabilities with tool scoping

#### Secrets in Context
**Risk:** API keys, credentials in code reviewed by agents

**Mitigation:**
- Use .gitignore for secrets
- Redact secrets in code before agent review
- Use secret management tools (not hardcoded values)
- Audit agent prompts for accidental secret inclusion

### Reliability Considerations

#### Agent Failures
**Types:**
1. **Timeout:** Agent exceeds execution limit
2. **Error:** Tool call fails (file not found, command error)
3. **Context overflow:** Agent exceeds token limit
4. **Rate limit:** Too many API calls

**Handling:**
- Main agent receives error message
- Can retry with modified prompt
- Can switch to different agent type
- Can break task into smaller pieces

#### Flaky Agents
**Symptoms:**
- Non-deterministic outputs
- Occasional failures on same prompt
- Inconsistent quality

**Causes:**
- Ambiguous prompts
- Model temperature > 0
- Non-deterministic tool outputs (timestamps, randomness)

**Fixes:**
- Make prompts more specific
- Add examples and constraints
- Test agents repeatedly
- Pin model temperature (if supported)

### Cost Optimization

#### Token Cost Reduction Strategies

1. **Use Haiku for simple tasks**
   ```yaml
   model: haiku  # Cheaper, faster for searches
   ```

2. **Group related work**
   ```
   # Expensive: 3 agents, 60k tokens
   Agent 1: Analyze auth/login.go
   Agent 2: Analyze auth/signup.go
   Agent 3: Analyze auth/session.go

   # Cheaper: 1 agent, 20k tokens
   Agent 1: Analyze entire auth/ directory
   ```

3. **Summary protocol**
   ```markdown
   After analysis, provide concise summary (max 500 words) to reduce
   main agent context consumption.
   ```

4. **Reuse agents**
   ```
   # Instead of spawning new agent each time
   > Resume agent abc123 and also analyze the database module
   ```

5. **Prefer Explore agents for searches**
   ```
   # Haiku model = lower cost
   Use explore agents to find all API routes
   ```

---

## Sources

- [Subagents - Claude Code Docs](https://code.claude.com/docs/en/sub-agents)
- [ClaudeLog - Task Agent Tools](https://claudelog.com/mechanics/task-agent-tools/)
- [Claude Code: Subagent Deep Dive | Code Centre](https://cuong.io/blog/2025/06/24-claude-code-subagent-deep-dive)
- [Best practices for Claude Code subagents](https://www.pubnub.com/blog/best-practices-for-claude-code-sub-agents/)
- [Practical guide to mastering Claude Code's main agent and Sub-agents | Medium](https://jewelhuq.medium.com/practical-guide-to-mastering-claude-codes-main-agent-and-sub-agents-fd52952dcf00)
- [How to Use Claude Code Subagents to Parallelize Development](https://zachwills.net/how-to-use-claude-code-subagents-to-parallelize-development/)
- [Feature Request: Background Agent Execution (Task tool async support)](https://github.com/anthropics/claude-code/issues/9905)
- [Prompting best practices - Claude Docs](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices)
- [GitHub - Piebald-AI/claude-code-system-prompts](https://github.com/Piebald-AI/claude-code-system-prompts)
- [Claude Code: Best practices for agentic coding](https://www.anthropic.com/engineering/claude-code-best-practices)

---

*End of Research Document*
