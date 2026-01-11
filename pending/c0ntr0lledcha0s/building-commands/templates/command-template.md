---
description: Brief description of what this command does
allowed-tools: Read, Grep, Glob, Bash
argument-hint: "[arg1] [arg2]"
# model: claude-haiku-4-5  # Optional: version alias (recommended) or full ID
# NOTE: If using model, must be version alias (claude-haiku-4-5) or full ID, NOT short alias (haiku)
---

# Command Name

Brief description of the command's purpose and what it accomplishes.

## Arguments

- **`$1`**: Description of first argument (e.g., file path, PR number, search term)
- **`$2`**: Description of second argument (optional)
- **`$ARGUMENTS`**: Use this to capture all arguments as a single string (for commit messages, etc.)

**Required Arguments**: [List which are required]
**Optional Arguments**: [List which are optional and their defaults]

## Workflow

When this command is invoked with `/command-name arg1 arg2`:

1. **Validate Arguments**: Check that required arguments are provided and valid
2. **Gather Context**: Read relevant files or fetch necessary information
3. **Perform Action**: Execute the main command logic
4. **Report Results**: Provide clear feedback about what was done

## Examples

### Example Usage 1: Basic Usage
```
/command-name value1 value2
```

**What happens:**
1. Validates value1 and value2
2. Performs [specific action]
3. Reports completion status

**Expected output:**
```
✅ [Action] completed successfully
   - [Result detail 1]
   - [Result detail 2]
```

### Example Usage 2: With Quoted Arguments
```
/command-name "argument with spaces"
```

**What happens:**
1. Handles argument with proper quoting
2. Performs [specific action]
3. Returns results

### Example Usage 3: Error Case
```
/command-name
```

**What happens:**
1. Detects missing required argument
2. Displays error message with usage example

## Error Handling

### Missing Arguments
```
❌ Error: Missing required argument [arg1]

Usage: /command-name [arg1] [arg2]

Example: /command-name my-file.txt --option
```

### Invalid Arguments
```
❌ Error: Invalid [arg1]: "[value]"

Expected: [description of valid format]
Example: /command-name valid-value
```

### Execution Failures
- If [specific failure condition]: [How to handle]
- If [another failure]: [Recovery action]

## Important Constraints

### DO:
- ✅ [What the command should always do]
- ✅ [What the command should always do]
- ✅ [What the command should always do]

### DON'T:
- ❌ [What the command should never do]
- ❌ [What the command should never do]
- ❌ [What the command should never do]

## Important Notes

- Note about required setup or context
- Note about side effects or state changes
- Note about permissions needed

## Security Considerations

[If this command involves file operations, bash, or sensitive data]

- Validate file paths before operations
- Sanitize arguments used in bash commands
- [Other security notes as relevant]

## Maintenance Notes

**Critical Rule**: If using the `model` field, must use version alias (`claude-haiku-4-5`) or full ID (`claude-haiku-4-5-20251001`), NOT short alias (`haiku`). Short aliases cause "model not found" errors.

- Templates are starting points - expand with specific details
- Document all arguments clearly
- Provide multiple examples covering common and edge cases
