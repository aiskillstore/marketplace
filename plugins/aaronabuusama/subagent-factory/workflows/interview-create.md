# Interview Create Workflow - Guided Agent Creation

Interactive workflow with questions and customization at each step. Ideal for learning the process or creating complex agents.

## When to Use This Workflow

- First time creating an agent
- Learning agent design principles
- Creating complex multi-responsibility agents
- Want guidance on best practices
- Uncertain about configuration options

## Interview Process

The assistant will ask you questions to gather requirements and guide you through agent creation. You can customize at each step.

---

## Phase 1: Agent Identity

### Question 1: What is the agent's primary purpose?

**Prompt**: Describe in one sentence what this agent should do.

**Examples**:
- "Review code for security vulnerabilities"
- "Run tests and diagnose failures"
- "Research and compare technology options"
- "Implement features following specifications"

**Your answer**: [Agent will capture]

---

### Question 2: What should we name this agent?

**Guidelines**:
- Use kebab-case (lowercase with hyphens)
- Be descriptive and specific
- Action-oriented or domain-focused

**Examples**:
- `security-reviewer` (not `code-checker`)
- `test-runner` (not `testing-agent`)
- `tech-researcher` (not `research-helper`)

**Suggested based on purpose**: [Agent will suggest]

**Your choice**: [Agent will capture]

---

### Question 3: What trigger phrases should invoke this agent?

**Prompt**: List keywords or phrases that indicate this agent should be used.

**Examples**:
- Security reviewer: "security audit", "vulnerability scan", "auth review"
- Test runner: "run tests", "diagnose failures", "fix broken tests"
- Tech researcher: "research", "compare", "evaluate", "investigate"

**Your phrases**: [Agent will capture]

---

## Phase 2: Tool Selection

### Question 4: What type of operations will this agent perform?

**Options**:

**A. Read-Only Operations** (reviewing, analyzing, auditing)
```yaml
tools: Read, Grep, Glob
```
- Can read files and search
- Cannot modify code
- Cannot execute commands
**Use for**: Reviewers, auditors, analyzers

**B. Research Operations** (investigating, comparing, gathering info)
```yaml
tools: Read, Grep, Glob, WebFetch, WebSearch
```
- Can read files and search
- Can fetch web content
- Cannot modify code
**Use for**: Researchers, analysts, evaluators

**C. Code Modification** (implementing, fixing, refactoring)
```yaml
tools: Read, Write, Edit, Bash, Grep, Glob
```
- Can read and modify files
- Can execute commands
- Can create new files
**Use for**: Implementers, fixers, builders

**D. Full Access** (end-to-end workflows)
```yaml
# Omit tools field to inherit all
```
- All built-in tools
- All MCP tools
- Maximum flexibility
**Use for**: Complex workflows, orchestration

**Your choice**: [Agent will capture]

**Custom tool list** (optional): [Agent will ask if you want to customize]

---

### Question 5: Which model should this agent use?

**Options**:

| Model | Use When | Cost | Speed |
|-------|----------|------|-------|
| **haiku** | Fast searches, simple tasks | Lowest | Fastest |
| **sonnet** | Most tasks, balanced | Medium | Medium |
| **opus** | Complex reasoning, critical decisions | Highest | Slower |
| **inherit** | Match parent agent's model | Varies | Varies |

**Default recommendation**: sonnet (balanced for most tasks)

**Your choice**: [Agent will capture]

---

## Phase 3: Workflow Design

### Question 6: What are the main steps in this agent's workflow?

**Prompt**: Describe the agent's process from invocation to completion.

**Template**:
```
1. [First action - usually gathering info]
2. [Second action - usually analysis]
3. [Third action - usually output generation]
```

**Examples**:

**Security Reviewer**:
1. Run git diff to see changes
2. For each file, check against security checklist
3. Generate findings report

**Test Runner**:
1. Execute project test command
2. For failures, read test files and diagnose
3. Propose fixes with rationale

**Your workflow**: [Agent will capture multi-line]

---

### Question 7: What checklist items should the agent verify?

**Prompt**: List specific items the agent should check or validate.

**Examples**:

**Security Checklist**:
- [ ] Input validation on user data
- [ ] Authentication before sensitive operations
- [ ] No hardcoded secrets
- [ ] SQL injection prevention

**Code Quality Checklist**:
- [ ] Clear function names
- [ ] Functions under 50 lines
- [ ] No code duplication
- [ ] Proper error handling

**Your checklist**: [Agent will capture items]

---

## Phase 4: Examples and Guidance

### Question 8: Can you provide an example scenario?

**Prompt**: Describe a typical input and expected output for this agent.

**Template**:
```
**Scenario**: [What situation triggers this]
**Input**: [What the agent receives]
**Expected Output**: [What the agent should produce]
```

**Example**:

**Scenario**: Reviewing authentication changes
**Input**: Modified login.go file with SQL query
**Expected Output**:
```
HIGH SEVERITY: SQL Injection
File: auth/login.go:45
Issue: String concatenation in SQL
Fix: Use parameterized queries
```

**Your example**: [Agent will capture]

---

### Question 9: What should the agent's output format be?

**Prompt**: Describe the structure of results.

**Common formats**:

**Report Format**:
```
# Executive Summary
[Brief overview]

# Findings
[Detailed issues]

# Recommendations
[Action items]
```

**Test Results Format**:
```
## Summary
- Total: X tests
- Passed: Y
- Failed: Z

## Failures
[Details for each]
```

**Research Format**:
```
# [Topic]
## Options
[Comparison]

## Recommendation
[Choice with rationale]
```

**Your format**: [Agent will capture]

---

## Phase 5: Boundaries and Constraints

### Question 10: What should the agent NOT do?

**Prompt**: List prohibited actions or behaviors.

**Common boundaries**:
- Don't modify code without approval
- Don't run destructive commands
- Don't access production systems
- Don't skip critical checks

**Your boundaries**: [Agent will capture]

---

### Question 11: What guidelines should the agent follow?

**Prompt**: List encouraged behaviors or principles.

**Common guidelines**:
- Be thorough but pragmatic
- Provide specific, actionable feedback
- Include code examples
- Prioritize by impact

**Your guidelines**: [Agent will capture]

---

## Phase 6: File Location and Creation

### Question 12: Where should this agent be stored?

**Options**:

**A. Project-level** (`.claude/agents/`)
- Shared with team
- Version controlled
- Project-specific tasks

**B. User-level** (`~/.claude/agents/`)
- Personal workflow
- Used across projects
- Not shared with team

**Your choice**: [Agent will capture]

---

### Confirmation: Review Generated Agent

[Agent will display the complete generated file]

```markdown
# .claude/agents/[name].md
---
name: [captured]
description: [captured]
tools: [captured]
model: [captured]
---

# [Name]

You are [role based on purpose].

## Responsibilities

When invoked:
[Generated from workflow]

## Workflow

[Generated from steps]

## Checklist

[Generated from items]

## Output Format

[Generated from format spec]

## Examples

[Generated from scenarios]

## Limitations

DO NOT:
[Generated from boundaries]

DO:
[Generated from guidelines]
```

**Options**:
1. **Accept and create** - Write file to specified location
2. **Customize** - Make adjustments before creating
3. **Start over** - Return to beginning

---

## Phase 7: Testing and Iteration

### After creation, the agent will guide you through testing:

1. **Initial test**:
   ```
   Use the [agent-name] agent to [realistic scenario]
   ```

2. **Evaluate results**:
   - Did agent follow workflow?
   - Was output format correct?
   - Were boundaries respected?
   - Quality of analysis/output?

3. **Iterate if needed**:
   - Identify specific failure mode
   - Suggest prompt adjustments
   - Update and re-test

---

## Example Interview Session

### Complete Example: Creating Test Runner Agent

**Q1: Purpose?**
> "Run tests, diagnose failures, and propose fixes"

**Q2: Name?**
> Suggested: `test-runner`
> Accepted

**Q3: Trigger phrases?**
> "run tests", "diagnose test failures", "fix broken tests"

**Q4: Operation type?**
> Choice: C (Code Modification)
> Tools: Read, Edit, Write, Bash, Grep, Glob

**Q5: Model?**
> Choice: sonnet (default)

**Q6: Workflow?**
> 1. Execute project test command
> 2. Capture output, diagnose failures
> 3. Propose minimal fixes with rationale
> 4. Re-run to verify

**Q7: Checklist?**
> - [ ] Identify test command from package.json
> - [ ] Capture full error output
> - [ ] Read failing test files
> - [ ] Determine if code bug or test bug
> - [ ] Verify fix doesn't break other tests

**Q8: Example scenario?**
> **Scenario**: Test failing after code change
> **Input**: AssertionError in test_user_creation
> **Output**: Root cause analysis with specific fix

**Q9: Output format?**
> ```
> ## Test Results
> - Total: X, Passed: Y, Failed: Z
>
> ## Failures
> For each: test name, file, error, root cause, fix
>
> ## Recommendations
> Prioritized actions
> ```

**Q10: Boundaries?**
> - Don't modify tests without understanding intent
> - Don't delete failing tests to "fix" suite
> - Don't merge while tests failing

**Q11: Guidelines?**
> - Ask if test intent unclear
> - Run tests multiple times to check for flakiness
> - Fix obvious bugs confidently with rationale

**Q12: Location?**
> Choice: A (Project-level: .claude/agents/)

**[Agent displays generated file]**

**Confirmation**: Accept and create

**[File created, ready for testing]**

---

## Tips for Effective Interviews

### Be Specific
❌ "Check for problems"
✅ "Check for SQL injection, XSS, and authentication bypasses"

### Think Step-by-Step
Break complex tasks into clear sequential steps.

### Provide Concrete Examples
Show actual code snippets and expected outputs.

### Define Clear Boundaries
Specify both what to do AND what not to do.

### Start Simple, Iterate
First version doesn't need to be perfect. Test and refine.

---

## After Interview: Next Steps

1. **Test agent immediately**
   ```
   Use the [agent-name] agent to [realistic task]
   ```

2. **Document usage** (if project agent)
   ```markdown
   ## [Agent Name]

   **Purpose**: [What it does]
   **Invoke**: [Trigger phrases]
   **Example**: [Usage example]
   ```

3. **Version control** (if project agent)
   ```bash
   git add .claude/agents/[name].md
   git commit -m "Add [name] agent"
   ```

4. **Share with team**
   - Demo the agent
   - Gather feedback
   - Iterate based on real usage

5. **Monitor and improve**
   - Track invocation patterns
   - Note failure modes
   - Refine prompts over time

---

## Interview Customization Options

At any point, you can:

### Skip Questions
"I already know the [X], let's skip to [Y]"

### Provide Multiple at Once
"The name is X, it should use tools Y, and trigger on phrases Z"

### Request More Guidance
"What are common patterns for [agent type]?"

### See Examples
"Show me examples of [security/test/research] agents"

### Start Over
"Let's start fresh with a different approach"

---

## Advantages of Interview Mode

1. **Guided learning** - Understand agent design principles
2. **Complete coverage** - Questions ensure nothing is forgotten
3. **Best practices** - Suggestions based on proven patterns
4. **Customization** - Adjust at each decision point
5. **Immediate testing** - Validate as you build

## When to Switch to Quick Mode

After creating 2-3 agents via interview:
- You understand the schema
- You know tool selection patterns
- You can write effective prompts
- You want faster iteration

Switch to: `workflows/quick-create.md`

---

## Resources

For schema reference, see: `references/agent-schema.md`

For prompt patterns, see: `references/prompt-patterns.md`

For quick creation, see: `workflows/quick-create.md`

---

## Ready to Start?

Tell the assistant:

> "Let's create an agent using the interview workflow"

Or be more specific:

> "I want to create a [type] agent that [purpose]. Let's use the interview process."

The assistant will guide you through all questions, provide suggestions, and create your agent.
