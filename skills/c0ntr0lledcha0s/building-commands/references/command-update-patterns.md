# Command Update Patterns

Common scenarios and solutions for updating Claude Code slash commands.

---

## Pattern Categories

1. [Model Field Issues](#model-field-issues)
2. [Security Hardening](#security-hardening)
3. [Argument Handling](#argument-handling)
4. [Documentation Improvement](#documentation-improvement)
5. [Schema Compliance](#schema-compliance)
6. [Tool Permissions](#tool-permissions)

---

## Model Field Issues

### Pattern: Short Alias in Model Field

**Problem**: Command uses short alias causing API errors

**Symptoms**:
- Error: "model not found" or 404 errors
- `model: haiku`, `model: sonnet`, or `model: opus` in frontmatter
- Command fails to execute

**Solution**:
```bash
/agent-builder:commands:migrate my-command --apply
# OR
/agent-builder:commands:update my-command
> What to update? 3 (model)
> Select model: 1 (claude-haiku-4-5)
```

**Example**:
```yaml
# Before (BROKEN)
---
description: Quick file search
model: haiku  # ❌ Causes "model not found" error
---

# After (FIXED)
---
description: Quick file search
model: claude-haiku-4-5  # ✅ Version alias works correctly
---
```

**Impact**: Command executes successfully, no API errors

**Why This Happens**: Commands require version aliases or full IDs. Short aliases (haiku/sonnet/opus) only work for agents, not commands.

---

### Pattern: Inherit Model Value

**Problem**: Using `model: inherit` instead of omitting field

**Symptoms**:
- `model: inherit` in frontmatter
- Validation warning about field format

**Solution**:
```yaml
# Before
---
model: inherit
---

# After (remove field entirely)
---
# No model field - inherits from conversation
---
```

**Impact**: Cleaner config, follows best practices

---

### Pattern: Wrong Model for Task Complexity

**Problem**: Using expensive model for simple tasks or cheap model for complex tasks

**Symptoms**:
- Command description mentions "quick", "simple" but uses `claude-opus-4-5`
- Command involves complex reasoning but uses `claude-haiku-4-5`
- High costs for simple operations

**Solution**:
```yaml
# Before (over-powered)
---
description: Quick file listing
model: claude-opus-4-5  # Too expensive for simple task
---

# After (right-sized)
---
description: Quick file listing
model: claude-haiku-4-5  # Fast and cheap for simple tasks
---
```

**Guidelines**:
- `claude-haiku-4-5`: Simple, quick operations (file search, formatting)
- `claude-sonnet-4-5`: Balanced tasks (code review, documentation)
- `claude-opus-4-5`: Complex reasoning (architecture decisions, security audits)

---

## Security Hardening

### Pattern: Unnecessary Bash Access

**Problem**: Command has Bash but doesn't need it

**Symptoms**:
- `allowed-tools` includes `Bash`
- Command body doesn't execute shell commands
- Primary tasks are read/write/analysis

**Solution**:
```bash
/agent-builder:commands:update my-command
> What to update? 2 (allowed-tools)
> Select preset: 2 (Read, Write, Edit, Grep, Glob)
```

**Example**:
```yaml
# Before
---
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
---

# After (if Bash not needed)
---
allowed-tools: Read, Write, Edit, Grep, Glob
---
```

**Impact**: Reduced attack surface, safer command

---

### Pattern: Missing Input Validation Documentation

**Problem**: Command has Bash but no validation documentation

**Symptoms**:
- `allowed-tools` includes `Bash`
- Command uses `$1`, `$2`, or `$ARGUMENTS` in bash commands
- No mention of "validate", "sanitize", or "escape"
- Enhancement score flags security issues

**Solution**:

Add validation section to command body:

```markdown
## Input Validation

Before executing bash commands with user input:

1. **Validate arguments**: Check format and allowed values
2. **Sanitize paths**: Prevent path traversal (../)
3. **Escape shell metacharacters**: Use proper quoting
4. **Whitelist patterns**: Only allow expected formats

Example:
\`\`\`bash
# Bad - command injection risk
bash -c "cat $1"

# Good - proper quoting
bash -c "cat \"$1\""

# Better - validation first
if [[ "$1" =~ ^[a-zA-Z0-9/_.-]+$ ]]; then
  bash -c "cat \"$1\""
else
  echo "Invalid filename"
fi
\`\`\`
```

**Impact**: Prevents command injection attacks

---

### Pattern: Dangerous Command Patterns

**Problem**: Command uses dangerous bash patterns

**Symptoms**:
- Enhancement flags: "Dangerous rm -rf with variable"
- Uses `eval $var`, `rm -rf $var`, or unquoted variables in pipes
- Potential for unintended data loss

**Solution**:

Add safeguards:

```bash
# Before (DANGEROUS)
bash -c "rm -rf $1"
bash -c "eval $1"

# After (SAFER)
# Add validation before destructive operations
if [[ "$1" == "target-dir" ]]; then
  bash -c "rm -rf \"$1\""
else
  echo "Error: Can only delete 'target-dir'"
fi

# Never use eval with user input
# Refactor to use safer alternatives
```

**Impact**: Prevents accidental data loss and code injection

---

## Argument Handling

### Pattern: Missing Argument Hint

**Problem**: Command uses arguments but no hint for users

**Symptoms**:
- Command body references `$1`, `$2`, or `$ARGUMENTS`
- No `argument-hint` field in frontmatter
- Users unsure what parameters to provide

**Solution**:
```bash
/agent-builder:commands:update my-command
> What to update? 4 (argument-hint)
> Enter new argument-hint: [filename] [options]
```

**Example**:
```yaml
# Before
---
description: Process a file
---

# Body uses $1 but no hint

# After
---
description: Process a file
argument-hint: [filename]
---
```

**Impact**: Better user experience, clear parameter expectations

---

### Pattern: Argument Hint Without Brackets

**Problem**: Argument hint doesn't use bracket convention

**Symptoms**:
- `argument-hint: filename options` instead of `[filename] [options]`
- Validation warning about format

**Solution**:
```yaml
# Before
---
argument-hint: filename options
---

# After
---
argument-hint: [filename] [options]
---
```

**Auto-fix**: Run `/agent-builder:commands:migrate my-command --apply`

---

### Pattern: Undocumented Arguments

**Problem**: Command uses arguments but doesn't document them

**Symptoms**:
- Uses `$1`, `$2`, `$ARGUMENTS` in body
- No `## Arguments` section explaining what they are
- Enhancement flags missing documentation

**Solution**:

Add arguments section:

```markdown
## Arguments

- `$1` - Filename to process (required)
- `$2` - Output format: json, yaml, or csv (optional, defaults to json)

Example: `/mycommand data.txt yaml`
```

**Impact**: Users understand what to provide

---

### Pattern: Inconsistent Argument Usage

**Problem**: Mixes positional ($1, $2) and all arguments ($ARGUMENTS)

**Symptoms**:
- Body uses both `$1` and `$ARGUMENTS`
- Unclear which to use
- Potential for bugs

**Solution**:

Choose one approach:

```markdown
# Approach 1: Positional (for known, structured arguments)
Use $1 for first argument, $2 for second, etc.

# Approach 2: All arguments (for variable or unknown count)
Use $ARGUMENTS for everything

# Don't mix both unless you have a clear reason
```

**Guideline**:
- Use positional ($1, $2) when you have 1-3 specific parameters
- Use $ARGUMENTS when you have many or variable parameters

---

## Documentation Improvement

### Pattern: Missing Workflow Section

**Problem**: Command doesn't explain execution steps

**Symptoms**:
- No `## Workflow` or `## Steps` section
- Users don't know what command will do
- Enhancement flags missing workflow

**Solution**:

Add workflow section:

```markdown
## Workflow

1. **Parse Arguments**: Extract filename from $1
2. **Validate Input**: Check file exists and is readable
3. **Process File**:
   - Read contents
   - Transform data
   - Format output
4. **Write Results**: Save to output file or display
5. **Confirm**: Show success message
```

**Impact**: Clear expectations, better user understanding

---

### Pattern: No Examples

**Problem**: Command lacks concrete usage examples

**Symptoms**:
- No `## Example` or `## Usage` section
- Abstract description without specifics
- Enhancement flags missing examples

**Solution**:

Add examples section:

```markdown
## Example Usage

### Example 1: Basic usage
\`\`\`
/mycommand input.txt
\`\`\`

Processes `input.txt` with default settings.

### Example 2: With options
\`\`\`
/mycommand input.txt --format=json
\`\`\`

Processes file and outputs JSON format.

### Example 3: Complex case
\`\`\`
/mycommand large-dataset.csv --filter=active --sort=date
\`\`\`

Filters and sorts large dataset before processing.
```

**Impact**: Users can copy-paste and adapt examples

---

### Pattern: Vague Description

**Problem**: Description doesn't clearly explain what command does

**Symptoms**:
- Generic description: "Helpful command"
- Doesn't specify action or purpose
- Users confused about when to use

**Solution**:

Improve description specificity:

```yaml
# Before (vague)
---
description: Process files
---

# After (specific)
---
description: Convert CSV files to JSON format with schema validation
---
```

**Template**: `[Action] [what] [how/with what features]`

**Examples**:
- "Create a new React component with TypeScript and tests"
- "Review pull request for security vulnerabilities and code quality"
- "Generate API documentation from OpenAPI spec with examples"

---

## Schema Compliance

### Pattern: Missing Description Field

**Problem**: Command lacks required description

**Symptoms**:
- Validation error: "Missing required 'description' field"
- Command won't load

**Solution**:
```bash
/agent-builder:commands:update my-command
> What to update? 1 (description)
> Enter new description: <clear one-liner>
```

**Required**: Every command must have a description field

---

### Pattern: Description Too Long/Short

**Problem**: Description doesn't meet length guidelines

**Symptoms**:
- Too short (< 10 chars): Not descriptive enough
- Too long (> 200 chars): Should be concise one-liner

**Solution**:
```yaml
# Too short
description: Fix code  # Only 8 chars

# Too long
description: This command will analyze your codebase and identify potential issues including security vulnerabilities, code smells, performance problems, and suggest improvements with detailed explanations  # 198 chars, still too verbose

# Just right
description: Analyze code for security issues, code smells, and performance problems  # Clear, concise, informative
```

**Guideline**: 20-120 characters is ideal

---

### Pattern: Invalid Filename

**Problem**: Command filename violates conventions

**Symptoms**:
- Uppercase letters: `MyCommand.md`
- Underscores: `my_command.md`
- Special chars: `my.command.md`
- Too long (> 64 chars)

**Solution**:

Rename file to follow conventions:

```bash
# Before (invalid)
my_command.md
MyCommand.md
my.command.md

# After (valid)
my-command.md
```

**Rules**:
- Lowercase only: `a-z`
- Numbers allowed: `0-9`
- Hyphens allowed: `-`
- Max 64 characters
- No underscores, spaces, or special characters

---

## Tool Permissions

### Pattern: Over-Permissioned

**Problem**: Command requests more tools than needed

**Symptoms**:
- `allowed-tools` lists 6+ tools
- Command only uses 2-3
- Enhancement warns about over-permissioning

**Solution**:

Review and minimize:

```yaml
# Before (over-permissioned)
---
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, WebFetch, WebSearch
---

# After (minimal necessary)
---
allowed-tools: Read, Grep, Glob
---
```

**Principle**: Start minimal, only add tools as truly needed

---

### Pattern: Both Write and Edit

**Problem**: Command has both Write and Edit (usually redundant)

**Symptoms**:
- `allowed-tools` includes both `Write` and `Edit`
- Command typically does one or the other

**Solution**:

Choose appropriate tool:

```yaml
# Before (redundant)
---
allowed-tools: Read, Write, Edit, Grep, Glob
---

# After (choose one)
---
allowed-tools: Read, Edit, Grep, Glob    # For modifying existing files
---
# OR
---
allowed-tools: Read, Write, Grep, Glob   # For creating new files
---
```

**Guideline**:
- `Edit`: Modify existing files (most common)
- `Write`: Create new files from scratch
- Rarely need both in same command

---

## Quick Reference

### Common Update Commands

```bash
# Interactive update
/agent-builder:commands:update my-command

# Get quality score and recommendations
/agent-builder:commands:enhance my-command

# Migrate schema (e.g., fix model field)
/agent-builder:commands:migrate my-command --apply

# Audit all commands
/agent-builder:commands:audit

# Compare two commands
/agent-builder:commands:compare command-a command-b
```

### Common Scripts

```bash
# Interactive update
python3 update-command.py my-command

# Quality analysis
python3 enhance-command.py my-command

# Schema migration
python3 migrate-command.py --dry-run
python3 migrate-command.py my-command --apply

# Bulk validation
python3 audit-commands.py --verbose

# Compare commands
python3 compare-commands.py command-a command-b
```

---

## Pattern Template

When documenting new patterns, use this template:

```markdown
### Pattern: [Pattern Name]

**Problem**: [What's wrong]

**Symptoms**:
- [Symptom 1]
- [Symptom 2]

**Solution**:
[How to fix]

**Example**:
[Before/after code]

**Impact**: [Benefits of fix]
```

---

## Related Resources

- [Migration Guide](./command-migration-guide.md) - Schema version migrations
- [Command Checklist](./command-checklist.md) - Quality review checklist
- [SKILL.md](../SKILL.md) - Complete command building guide
