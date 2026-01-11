# Command Template with Arguments

Use for commands that accept user input.

## Single Argument ($ARGUMENTS)

```markdown
---
description: "{Brief description}"
allowed-tools:
  - WebFetch(domain:github.com)
argument-hint: "{parameter_name}"
---

# {Command Name}

{Instructions using $ARGUMENTS for the input.}

Target: $ARGUMENTS

1. {First step using the argument}
2. {Process the input}
3. {Return results}
```

## Multiple Arguments ($1, $2)

```markdown
---
description: "{Brief description}"
allowed-tools:
  - Bash(bash:*)
argument-hint: "{param1} {param2}"
---

# {Command Name}

Create $1 in $2:

1. Validate inputs
2. Generate using $1 as name
3. Save to $2 location
4. Confirm completion
```

## Example: Fix Issue

```markdown
---
description: "Find and fix a GitHub issue by number"
allowed-tools:
  - WebFetch(domain:github.com)
argument-hint: "issue_number"
---

# Fix Issue

Fix issue #$ARGUMENTS:

1. Fetch issue details from GitHub
2. Understand requirements and context
3. Locate relevant code files
4. Implement the fix
5. Add tests if applicable
6. Prepare commit message
```

## Example: Create Component

```markdown
---
description: "Generate a new React component"
allowed-tools:
  - Read
  - Write
argument-hint: "ComponentName type"
---

# Create Component

Create a $2 component named $1:

1. Check existing patterns in src/components/
2. Generate $1.tsx following conventions
3. Add tests in $1.test.tsx
4. Export from index.ts
```

## Usage

Save as `.claude/commands/{command-name}.md`

Run with args: `/{command-name} value1 value2`
