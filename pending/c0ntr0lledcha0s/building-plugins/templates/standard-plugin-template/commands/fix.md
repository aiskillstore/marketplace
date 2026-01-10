---
description: Fix identified issues in the specified component
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
argument-hint: [component-name]
---

# Fix Command

Automatically fix common issues in a component.

## Usage

```bash
/my-standard-plugin:fix [component-name]
```

## What This Command Does

1. **Analyze Component**: Identify fixable issues
2. **Confirm Changes**: Ask user for approval
3. **Apply Fixes**: Automatically resolve issues
4. **Verify**: Confirm fixes applied successfully

## Parameters

- **component-name**: (Required) The component to fix

## Implementation

### Step 1: Analyze for Issues

Run analysis to identify fixable issues.

### Step 2: List Proposed Fixes

Show user what will be changed:
```
Found 3 fixable issues:
1. Add input validation (login.ts:45)
2. Update deprecated method (auth.ts:78)
3. Add error handling (utils.ts:102)

Apply these fixes? (y/n)
```

### Step 3: Apply Fixes

If user confirms, apply each fix:
- Use Edit tool for targeted changes
- Validate changes
- Report progress

### Step 4: Verification

Confirm all fixes applied:
```
✅ Applied 3 fixes successfully
```

## Safety Features

- Always ask for confirmation before making changes
- Create backup before modifying files
- Validate changes before saving
- Provide rollback option if needed

## Example

```bash
/my-standard-plugin:fix authentication
```

## Notes

- This command modifies files
- Always review changes carefully
- Consider running tests after applying fixes
