# Quality Standards for Claude Code Components

Comprehensive quality standards for agents, skills, commands, and hooks.

## General Principles

1. **Clarity over Cleverness**: Components should be immediately understandable
2. **Security by Default**: Minimal permissions, validate inputs
3. **Single Responsibility**: Each component does one thing well
4. **User-Centric**: Design from the user's perspective
5. **Well-Documented**: Examples and clear explanations

## Quality Dimensions

### 1. Description Clarity

**Excellent (5/5)**:
- 100+ characters, specific and detailed
- Clear statement of purpose
- Specific auto-invoke triggers (for skills)
- Concrete examples included
- No vague words (helps, manages, handles)

**Example**:
```yaml
description: Expert at writing Jest unit tests for JavaScript/TypeScript. Auto-invokes when user writes new functions or classes, or asks "test this code". Generates comprehensive test suites with mocks, assertions, and edge cases following AAA pattern.
```

**Poor (1/5)**:
```yaml
description: Helps with testing
```

**Checklist**:
- [ ] Description is 100+ characters
- [ ] Purpose is specific and clear
- [ ] Auto-invoke triggers are explicit (skills only)
- [ ] Includes example use case
- [ ] Avoids vague words

### 2. Tool Permissions

**Excellent (5/5)**:
- Minimal necessary tools
- Read-only when possible
- Each tool justified
- No dangerous combinations

**Tool Guidelines**:

| Tool | When Justified | Red Flags |
|------|---------------|-----------|
| Read | Almost always needed | - |
| Grep | Searching codebases | Using with Write |
| Glob | Finding files | Using alone without Read |
| Write | Creating new files | Used for editing existing |
| Edit | Modifying files | Used with Bash unsafely |
| Bash | Running commands | With user input, with Write |
| Task | Delegating to agents | In agents (circular), overused |
| WebSearch | Current information | For local codebase |
| WebFetch | Fetching docs | Without WebSearch |

**Safe Combinations**:
- `Read, Grep, Glob` - Research/analysis
- `Read, Write` - File creation
- `Read, Edit` - File modification
- `Read, Grep, Glob, WebSearch, WebFetch` - Research with web

**Dangerous Combinations**:
- `Bash, Write, Edit` - Command injection + file access
- `Bash, Task` - Complex delegation chains
- All tools - Almost never justified

**Checklist**:
- [ ] Uses minimal necessary tools
- [ ] No unjustified Bash access
- [ ] No dangerous combinations
- [ ] Each tool has clear purpose
- [ ] Prefers Read over Bash for reading

### 3. Auto-Invoke Triggers (Skills Only)

**Excellent (5/5)**:
- Specific quoted phrases
- Clear activation criteria
- Low false positive rate
- Comprehensive coverage

**Effective Triggers**:
```yaml
Auto-invokes when user asks "how does X work?", "where is Y implemented?",
or "explain the Z component". Also activates when exploring unfamiliar code.
```

**Ineffective Triggers**:
```yaml
Use when user needs help understanding code
```

**Checklist**:
- [ ] Includes specific quoted phrases
- [ ] Activation criteria are unambiguous
- [ ] Won't trigger on irrelevant queries
- [ ] Covers all intended use cases
- [ ] No overlap with other skills

### 4. Security

**Excellent (5/5)**:
- Minimal permissions
- Input validation mentioned (if Bash)
- No security vulnerabilities
- Safe defaults
- Follows principle of least privilege

**Security Checklist**:
- [ ] No unnecessary Bash access
- [ ] Input validation if Bash used
- [ ] No command injection risks
- [ ] No hardcoded secrets
- [ ] Safe file operations
- [ ] No dangerous combinations

**Red Flags**:
- ❌ Bash with user input without validation
- ❌ Write + Bash combination
- ❌ All tools allowed
- ❌ No mention of input validation with Bash

### 5. Usability

**Excellent (5/5)**:
- Clear documentation
- Multiple usage examples
- Code examples with explanations
- Helpful error messages
- Intuitive behavior

**Documentation Standards**:
- Overview section
- Capabilities list
- Usage examples (3+)
- When to use / when not to use
- Integration examples

**Checklist**:
- [ ] Has overview/introduction
- [ ] Lists capabilities
- [ ] Includes 3+ usage examples
- [ ] Has code examples
- [ ] Explains when to use
- [ ] Clear section structure
- [ ] Uses markdown formatting effectively

## Component-Specific Standards

### Agents

**Required Elements**:
```yaml
---
name: component-name
description: [100+ chars with clear invocation criteria]
tools: [minimal list]
model: sonnet  # or haiku for simple tasks
---

# Agent Name

Clear mission statement and capabilities.

## When to Invoke This Agent

[Specific criteria - when to use agent vs. skills directly]

## Capabilities

- [Capability 1]
- [Capability 2]

## Examples

### Example 1: [Scenario]
[Usage example]
```

**Quality Standards**:
- Description clarifies when to invoke vs. using skills
- Tools list excludes Task (no circular delegation)
- Model choice is appropriate (haiku for simple, sonnet for complex)
- Examples show clear value proposition

### Skills

**Required Elements**:
```yaml
---
name: skill-name
description: [150+ chars with specific auto-invoke triggers]
version: 1.0.0
allowed-tools: [minimal list]
---

# Skill Name

Detailed explanation of skill's expertise.

## When to Use This Skill

[Auto-invoke triggers - must be specific]

## Capabilities

[Detailed list]

## Resources Available

Scripts in {baseDir}/scripts/:
- script-name.py: [description]

References in {baseDir}/references/:
- reference.md: [description]

## Examples

[Multiple usage examples]
```

**Quality Standards**:
- Auto-invoke triggers are specific and quoted
- Uses `{baseDir}` for resource references
- Has scripts/references/assets directories if needed
- Examples demonstrate auto-activation
- Version follows semver

### Commands

**Required Elements**:
```yaml
---
description: [Clear one-line description of what command does]
allowed-tools: [minimal list]
argument-hint: "[arg1] [arg2]"  # optional
model: haiku  # or sonnet if complex
---

# Command Documentation

What this command does and why to use it.

## Usage

```bash
/command-name arg1 arg2
```

## Examples

### Example 1: [Scenario]
```bash
/command-name example-arg
```

[What happens]

## Arguments

- $1: [description]
- $2: [description]
```

**Quality Standards**:
- Description is clear and action-oriented
- Argument hint matches actual arguments used
- Model choice is appropriate
- Examples show real-world usage
- Explains output/result

### Hooks

**Required Elements**:
```json
{
  "hooks": [
    {
      "name": "descriptive-name",
      "event": "PreToolUse|PostToolUse|UserPromptSubmit",
      "matchers": {
        "toolName": "ToolName",
        "toolParameters": { "param": "pattern" }
      },
      "type": "prompt|command",
      "prompt": "Clear instruction" // or "command": "script.sh"
    }
  ]
}
```

**Quality Standards**:
- Matchers are specific (not overly broad)
- Hook name clearly indicates purpose
- Type choice is appropriate (prompt for guidance, command for validation)
- No security risks in commands
- Clear purpose and benefit

## Quality Scoring

### Overall Quality Levels

**5.0 - Excellent**: Marketplace-ready, best practices throughout
**4.5 - Very Good**: Minor improvements would help
**4.0 - Good**: Solid component, some enhancements recommended
**3.5 - Adequate**: Works but important improvements needed
**3.0 - Fair**: Significant issues to address
**2.5 - Poor**: Major problems, not recommended for use
**2.0 - Very Poor**: Substantial rework required
**1.0 - Critical**: Unusable in current state

### Dimension Scoring

Each dimension (Description, Tools, Triggers, Security, Usability) scored 1-5:

**5/5**: Exemplary, no improvements needed
**4/5**: Good, minor improvements possible
**3/5**: Adequate, important improvements recommended
**2/5**: Poor, significant issues
**1/5**: Critical problems

## Common Issues and Fixes

### Issue: Vague Description

**Bad**:
```yaml
description: Helps with code quality
```

**Good**:
```yaml
description: Expert at analyzing code quality using ESLint, Prettier, and static analysis. Auto-invokes when user finishes writing code or asks "is this code good?" Provides actionable improvement suggestions.
```

### Issue: Excessive Tools

**Bad**:
```yaml
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, Task, WebSearch, WebFetch
```

**Good**:
```yaml
allowed-tools: Read, Grep, Glob  # Research skill only needs to read and search
```

### Issue: Vague Triggers

**Bad**:
```yaml
description: Use when user needs testing help
```

**Good**:
```yaml
description: Auto-invokes when user writes new functions or asks "test this code", "write tests", or "add unit tests"
```

### Issue: Security Risk

**Bad**:
```yaml
allowed-tools: Bash, Write
# No input validation mentioned
```

**Good**:
```yaml
allowed-tools: Read, Grep
# Or if Bash needed:
# Validates all user input before execution. Never directly interpolates user input into bash commands.
```

### Issue: Poor Documentation

**Bad**:
```markdown
# My Skill

This skill does things.
```

**Good**:
```markdown
# My Skill

Expert at analyzing code patterns and identifying design patterns.

## Capabilities

- Gang of Four pattern recognition
- Architectural pattern analysis
- Anti-pattern detection
- Code duplication analysis

## When to Use This Skill

Auto-invokes when user asks "what patterns are used?", "find repeated code",
or "analyze the architecture"

## Examples

### Example 1: Finding Design Patterns
```
User: "What design patterns are in this codebase?"
Skill activates → Searches for Factory, Singleton, Observer patterns → Reports findings
```

[More examples...]
```

## Review Checklist

Before publishing or using a component:

### All Components
- [ ] Name follows lowercase-hyphen convention
- [ ] Description is 100+ characters
- [ ] Description is specific, not vague
- [ ] Tools are minimal and justified
- [ ] No security vulnerabilities
- [ ] Documentation is comprehensive
- [ ] Examples are included
- [ ] Version follows semver (skills/agents)

### Skills Specifically
- [ ] Auto-invoke triggers are specific
- [ ] Triggers include quoted phrases
- [ ] Uses {baseDir} for resources
- [ ] Has appropriate directories (scripts/references/assets)

### Agents Specifically
- [ ] Clarifies when to invoke vs. using skills
- [ ] No Task tool (no circular delegation)
- [ ] Model choice is appropriate
- [ ] Clear value proposition

### Commands Specifically
- [ ] argument-hint matches usage
- [ ] Uses $ARGUMENTS or $1, $2 correctly
- [ ] Clear examples provided
- [ ] Model choice is appropriate

### Hooks Specifically
- [ ] Matchers are specific, not overly broad
- [ ] No security risks in commands
- [ ] Clear purpose documented
- [ ] Event type is appropriate

## Marketplace Standards

Components intended for marketplace should meet higher standards:

**Minimum Requirements**:
- Overall quality score: 4.0+
- No critical security issues
- Comprehensive documentation
- Multiple examples
- Clear use cases

**Recommended**:
- Overall quality score: 4.5+
- All dimensions score 4+
- README with screenshots/demos
- Test coverage for scripts
- Contribution guidelines

## References

- [Claude Code Plugin Documentation](https://code.claude.com/docs)
- [Security Best Practices](./security-checklist.md)
- [Usability Guidelines](./usability-guidelines.md)
