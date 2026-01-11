# Basic Command Template

Use for simple commands without arguments.

```markdown
---
description: "{Brief description of what this command does}"
allowed-tools:
  - Bash(npm:*)  # Add tools as needed
---

# {Command Name}

{Clear, step-by-step instructions for Claude to follow.}

1. {First step}
2. {Second step}
3. {Final step with expected output}
```

## Example

```markdown
---
description: "Check code quality and report issues"
allowed-tools:
  - Bash(npm:*)
---

# Lint Check

Run the linter and summarize findings:

1. Execute `npm run lint`
2. Group issues by severity (error, warning)
3. Suggest quick fixes for common issues
4. Report total count and affected files
```

## Usage

Save as `.claude/commands/{command-name}.md`

Then run: `/{command-name}`
