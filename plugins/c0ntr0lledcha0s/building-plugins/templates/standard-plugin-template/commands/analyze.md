---
description: Analyze the specified component and provide recommendations
allowed-tools: Read, Grep, Glob, Bash
argument-hint: [component-name]
---

# Analyze Command

Perform comprehensive analysis of a component and provide actionable recommendations.

## Usage

```bash
/my-standard-plugin:analyze [component-name]
```

## What This Command Does

1. **Locate Component**: Find the specified component in the codebase
2. **Analyze Structure**: Examine code structure and patterns
3. **Check Quality**: Assess code quality and best practices
4. **Generate Report**: Provide detailed findings and recommendations

## Parameters

- **component-name**: (Required) The name of the component to analyze

## Implementation Steps

### Step 1: Validate Input

Check if component-name is provided:
```
If $1 is empty:
  Ask user: "Which component would you like to analyze?"
  Exit
```

### Step 2: Find Component

Search for the component in the codebase:
```
Use Grep to find files matching the component name
Verify the component exists
```

### Step 3: Analyze Component

Read and analyze relevant files:
- Check code structure
- Identify patterns
- Assess quality
- Find potential issues

### Step 4: Generate Report

Provide comprehensive findings:
- **Summary**: Brief overview
- **Findings**: Detailed analysis
- **Issues**: Problems identified
- **Recommendations**: Actionable improvements

## Example

```bash
/my-standard-plugin:analyze authentication
```

**Expected Output:**
```
🔍 Analyzing 'authentication' component...

📊 ANALYSIS RESULTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Strengths:
- Well-structured code
- Good test coverage

⚠️  Issues Found:
- Missing input validation in login.ts:45
- Deprecated method used in auth.ts:78

💡 Recommendations:
1. Add input validation for user credentials
2. Update to use new authentication API
3. Consider adding rate limiting

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Error Handling

- If component not found: Suggest similar component names
- If access denied: Check permissions
- If analysis fails: Provide error details

## Notes

- Analysis is read-only (no modifications)
- Results are displayed in terminal
- Consider using the example-agent for deeper analysis
