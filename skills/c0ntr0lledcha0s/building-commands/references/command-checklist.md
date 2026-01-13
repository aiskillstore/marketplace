# Command Quality Checklist

Comprehensive quality review checklist for Claude Code slash commands.

---

## How to Use This Checklist

1. **Before Creating**: Review requirements
2. **During Development**: Check off items as you implement
3. **Before Committing**: Final quality gate
4. **During Review**: Use for PR reviews
5. **When Updating**: Re-validate existing commands

**Quick Check**: Run `/agent-builder:commands:enhance <command-name>` for automated scoring against many of these criteria.

---

## Schema Compliance

### File Structure

- [ ] File is markdown with `.md` extension
- [ ] Contains YAML frontmatter (between `---` markers)
- [ ] YAML is syntactically valid
- [ ] Frontmatter comes before body content

### Naming

- [ ] Filename uses lowercase only (`a-z`)
- [ ] Numbers allowed if needed (`0-9`)
- [ ] Hyphens for word separation (`my-command.md`)
- [ ] No underscores (`my_command` ❌)
- [ ] No spaces or special characters
- [ ] Name is 64 characters or less
- [ ] Name is action-oriented (starts with verb)
  - Examples: `create-`, `run-`, `check-`, `update-`

### Required Fields

- [ ] Has `description` field
- [ ] Description is clear and concise
- [ ] Description is 10-200 characters
- [ ] Description explains what command does (not how)

---

## Model Configuration

### Model Field (If Present)

- [ ] Uses **version alias** or **full ID** (NOT short alias)
  - ✅ `claude-haiku-4-5` (version alias)
  - ✅ `claude-haiku-4-5-20251001` (full ID)
  - ❌ `haiku` (short alias - causes errors)
  - ❌ `sonnet` (short alias - causes errors)
  - ❌ `opus` (short alias - causes errors)
- [ ] Starts with `claude-`
- [ ] Model choice appropriate for task complexity:
  - Simple/quick tasks → `claude-haiku-4-5`
  - Balanced tasks → `claude-sonnet-4-5`
  - Complex reasoning → `claude-opus-4-5`

### Model Field Omission

- [ ] If no model field, intentionally inheriting from conversation ✅
- [ ] Not using `model: inherit` (just omit field)

---

## Tool Permissions

### Allowed Tools Field

- [ ] `allowed-tools` field present (recommended) OR intentionally omitted
- [ ] Tools are comma-separated if multiple
- [ ] All tool names are valid:
  - `Read`, `Write`, `Edit`, `Grep`, `Glob`, `Bash`
  - `WebFetch`, `WebSearch`, `NotebookEdit`
  - `Task`, `TodoWrite`, `BashOutput`, `KillShell`

### Tool Minimalism

- [ ] Only includes necessary tools (principle of least privilege)
- [ ] Typically 6 or fewer tools
- [ ] Doesn't include both `Write` and `Edit` unless truly needed
  - `Edit`: for modifying existing files
  - `Write`: for creating new files
  - Usually need only one

### Bash Security (If `Bash` in tools)

- [ ] Body documents input validation approach
- [ ] Mentions sanitization or escaping
- [ ] Shows examples of safe usage
- [ ] Avoids dangerous patterns:
  - ❌ `eval $var`
  - ❌ `rm -rf $var` without validation
  - ❌ Unquoted variables in commands
  - ❌ `$ARGUMENTS` directly in pipes/chains

---

## Argument Handling

### Argument Hint

- [ ] Has `argument-hint` if command uses `$1`, `$2`, or `$ARGUMENTS`
- [ ] Hint uses bracket notation: `[param1] [param2]`
- [ ] Hint clearly describes parameters
- [ ] Optional parameters indicated (e.g., `[required] [optional?]`)

### Argument Documentation

- [ ] Body has `## Arguments` section if command uses arguments
- [ ] Each argument documented:
  - What it is
  - Required or optional
  - Expected format or values
  - Default value (if optional)
- [ ] Examples show argument usage

### Argument Validation

- [ ] If using Bash with arguments, shows validation
- [ ] Checks for required arguments
- [ ] Validates argument format
- [ ] Provides helpful error messages for invalid args

---

## Content Quality

### Structure

- [ ] Body is well-organized with clear sections
- [ ] Uses heading levels appropriately (`##`, `###`)
- [ ] Has at least 3-4 major sections
- [ ] Sections flow logically

### Required Sections

- [ ] **Purpose/Overview**: What the command does
- [ ] **Arguments** (if applicable): Parameter documentation
- [ ] **Workflow/Steps**: How command executes
- [ ] **Examples/Usage**: Concrete usage examples

### Recommended Sections

- [ ] **Prerequisites**: What must exist before running
- [ ] **Important Notes**: Caveats, warnings, tips
- [ ] **Error Handling**: What to do if command fails
- [ ] **Related Commands**: Links to similar commands

### Examples

- [ ] Has at least 1-2 concrete examples
- [ ] Examples show realistic usage
- [ ] Examples demonstrate different scenarios:
  - Basic usage
  - With options
  - Edge cases
- [ ] Examples use code blocks for commands
- [ ] Examples explain what happens

### Writing Quality

- [ ] Clear, concise language
- [ ] Free of typos and grammatical errors
- [ ] Technical terms explained or linked
- [ ] Active voice preferred
- [ ] Consistent terminology

---

## Formatting

### Markdown

- [ ] Proper markdown syntax
- [ ] Code blocks use triple backticks with language
- [ ] Inline code uses single backticks
- [ ] Bold for emphasis: `**important**`
- [ ] Lists for steps or items

### Lists

- [ ] Uses lists for step-by-step instructions
- [ ] Numbered lists for sequential steps
- [ ] Bullet lists for unordered items
- [ ] List items are concise and parallel structure

### Code Blocks

- [ ] Commands shown in code blocks
- [ ] Language specified (bash, yaml, markdown, etc.)
- [ ] Long lines broken appropriately
- [ ] Proper indentation

### Line Length

- [ ] Most lines under 120 characters
- [ ] Long lines broken for readability
- [ ] No excessively long paragraphs

---

## Security

### Input Handling

- [ ] User input validated before use
- [ ] File paths sanitized (no `../` attacks)
- [ ] Shell metacharacters escaped
- [ ] Whitelist approach when possible

### Dangerous Operations

- [ ] Destructive operations (delete, rm) have safeguards
- [ ] User confirmation for irreversible actions
- [ ] Clear warnings for dangerous operations
- [ ] Validation before destructive operations

### Secrets

- [ ] No hardcoded secrets (API keys, passwords, tokens)
- [ ] Sensitive data mentioned only as placeholders/examples
- [ ] Environment variables recommended for secrets
- [ ] Clear examples show placeholder format

### Error Messages

- [ ] Error messages don't reveal sensitive information
- [ ] Errors guide user to fix (not just fail silently)
- [ ] Stack traces sanitized if shown

---

## Usability

### Discoverability

- [ ] Description helps users find command
- [ ] Command name reflects purpose
- [ ] Examples show common use cases
- [ ] Related commands linked

### User Experience

- [ ] Command provides feedback during execution
- [ ] Progress shown for long operations
- [ ] Success/failure clearly indicated
- [ ] Helpful error messages

### Documentation

- [ ] All features documented
- [ ] Edge cases mentioned
- [ ] Limitations explained
- [ ] Prerequisites listed

---

## Maintainability

### Code Quality

- [ ] References to files use relative paths
- [ ] `{baseDir}` variable used for skill resources
- [ ] No hardcoded absolute paths
- [ ] Workflow is clear and logical

### Comments

- [ ] Complex logic explained
- [ ] Why, not just what
- [ ] Links to external docs when relevant

### Versioning

- [ ] Breaking changes noted
- [ ] Deprecations documented
- [ ] Migration path provided

---

## Testing

### Manual Testing

- [ ] Command executes successfully
- [ ] With valid arguments
- [ ] With invalid arguments (fails gracefully)
- [ ] Edge cases handled

### Validation

- [ ] Passes schema validation
  ```bash
  python3 validate-command.py my-command.md
  ```
- [ ] No critical errors
- [ ] Warnings addressed or documented

### Quality Score

- [ ] Enhancement score ≥ 6 (good)
  ```bash
  /agent-builder:commands:enhance my-command
  ```
- [ ] Ideally ≥ 8 (excellent)
- [ ] Critical recommendations addressed

---

## Pre-Commit Checklist

Before committing a new or updated command:

- [ ] All required fields present and valid
- [ ] Model field uses version alias (not short alias)
- [ ] Tool permissions minimal and justified
- [ ] Arguments documented if used
- [ ] Has usage examples
- [ ] Passes validation: `python3 validate-command.py my-command.md`
- [ ] Quality score ≥ 6: `/agent-builder:commands:enhance my-command`
- [ ] Tested with valid inputs
- [ ] Tested with invalid inputs (fails gracefully)
- [ ] Security reviewed (if uses Bash or handles input)
- [ ] Documentation complete
- [ ] No typos or grammatical errors
- [ ] Follows naming conventions

---

## PR Review Checklist

When reviewing someone else's command:

### Automated Checks

- [ ] Run validation: `/agent-builder:commands:audit`
- [ ] Run enhancement: `/agent-builder:commands:enhance <command-name>`
- [ ] Review quality score and recommendations

### Manual Review

- [ ] Command name is clear and follows conventions
- [ ] Description accurately describes functionality
- [ ] Model field correct (version alias, not short alias)
- [ ] Tool permissions justified
- [ ] Security reviewed (especially Bash access)
- [ ] Arguments documented
- [ ] Examples are realistic and helpful
- [ ] Code is readable and maintainable
- [ ] No hardcoded secrets or sensitive data

### Testing

- [ ] Test command with valid inputs
- [ ] Test with invalid inputs
- [ ] Test edge cases mentioned in docs
- [ ] Verify error messages are helpful

---

## Common Issues Checklist

Quick check for common problems:

- [ ] ❌ NOT using short alias in model field (`haiku`/`sonnet`/`opus`)
- [ ] ❌ NOT missing description field
- [ ] ❌ NOT using underscores in filename
- [ ] ❌ NOT including Bash without validation docs
- [ ] ❌ NOT using `eval $var` or `rm -rf $var`
- [ ] ❌ NOT mixing both Write and Edit unnecessarily
- [ ] ❌ NOT using `$1` without argument-hint
- [ ] ❌ NOT using argument-hint without brackets
- [ ] ❌ NOT missing examples
- [ ] ❌ NOT having overly long description (> 200 chars)

---

## Quality Tiers

### Tier 1: Valid (Minimum Acceptable)

- ✅ Passes validation
- ✅ No critical errors
- ✅ Required fields present
- ✅ Model field correct (if present)
- ✅ Basic functionality works

**Score**: ≥ 6/10

### Tier 2: Good (Recommended)

- ✅ All Tier 1 criteria
- ✅ Has examples
- ✅ Arguments documented
- ✅ Clear workflow
- ✅ Security reviewed
- ✅ Few or no warnings

**Score**: ≥ 8/10

### Tier 3: Excellent (Best Practice)

- ✅ All Tier 2 criteria
- ✅ Multiple detailed examples
- ✅ Comprehensive documentation
- ✅ Error handling documented
- ✅ Related commands linked
- ✅ Follows all best practices
- ✅ No warnings or recommendations

**Score**: ≥ 9/10

---

## Related Tools

### Automated Checks

```bash
# Schema validation
python3 validate-command.py my-command.md

# Quality analysis
/agent-builder:commands:enhance my-command

# Bulk audit
/agent-builder:commands:audit --verbose

# Compare with template
/agent-builder:commands:compare my-command template-command
```

### Interactive Updates

```bash
# Update configuration
/agent-builder:commands:update my-command

# Migrate schema
/agent-builder:commands:migrate my-command --apply
```

---

## Resources

- [Command Update Patterns](./command-update-patterns.md) - Common update scenarios
- [Command Migration Guide](./command-migration-guide.md) - Schema migration help
- [Building Commands Skill](../SKILL.md) - Complete command creation guide
- [Validation Script](../scripts/validate-command.py) - Schema validation tool
- [Enhancement Script](../scripts/enhance-command.py) - Quality analysis tool
