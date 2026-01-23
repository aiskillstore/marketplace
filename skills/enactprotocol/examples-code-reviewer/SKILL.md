---
enact: "2.0.0"
name: "examples/code-reviewer"
version: "1.0.0"
description: "AI-powered code review tool that analyzes code for bugs, style issues, and improvements"
license: "MIT"
author:
  name: "Enact Examples"
tags:
  - ai
  - code-review
  - analysis

inputSchema:
  type: object
  properties:
    code:
      type: string
      description: "The code to review"
    language:
      type: string
      description: "Programming language of the code"
      default: "auto"
    focus:
      type: string
      enum: ["bugs", "style", "performance", "security", "all"]
      description: "What aspect to focus the review on"
      default: "all"
  required:
    - code

outputSchema:
  type: object
  properties:
    issues:
      type: array
      items:
        type: object
        properties:
          severity:
            type: string
            enum: ["error", "warning", "info"]
          line:
            type: number
          message:
            type: string
          suggestion:
            type: string
    summary:
      type: string
    score:
      type: number
      description: "Code quality score from 0-100"

annotations:
  title: "Code Reviewer"
  readOnlyHint: true
  openWorldHint: false
---

# Code Reviewer

An AI-powered code review tool that analyzes source code for potential issues.

## Instructions

You are a senior software engineer performing a code review. Analyze the provided code and identify:

1. **Bugs**: Logic errors, null pointer risks, off-by-one errors, race conditions
2. **Style Issues**: Naming conventions, code organization, readability
3. **Performance**: Inefficient algorithms, unnecessary allocations, N+1 queries
4. **Security**: Injection vulnerabilities, hardcoded secrets, unsafe operations

## Review Process

1. First, identify the programming language if not specified
2. Read through the code to understand its purpose
3. Analyze based on the requested focus area (or all areas if "all")
4. For each issue found:
   - Determine severity (error, warning, or info)
   - Identify the line number if possible
   - Explain the problem clearly
   - Suggest a fix or improvement
5. Provide a summary and overall quality score (0-100)

## Output Format

Return a JSON object matching the outputSchema with:
- `issues`: Array of identified problems
- `summary`: Brief overview of the code quality
- `score`: Numeric score from 0 (terrible) to 100 (excellent)

## Example

For input:
```javascript
function getUser(id) {
  var user = users.find(u => u.id = id);
  return user.name;
}
```

Expected output:
```json
{
  "issues": [
    {
      "severity": "error",
      "line": 2,
      "message": "Assignment operator (=) used instead of comparison (===) in find callback",
      "suggestion": "Change 'u.id = id' to 'u.id === id'"
    },
    {
      "severity": "error", 
      "line": 3,
      "message": "Accessing .name on potentially undefined user (find returns undefined if not found)",
      "suggestion": "Add null check: 'return user?.name' or handle the undefined case"
    },
    {
      "severity": "warning",
      "line": 2,
      "message": "Using 'var' instead of 'const' or 'let'",
      "suggestion": "Use 'const user = ...' since user is not reassigned"
    }
  ],
  "summary": "The function has critical bugs: incorrect comparison operator and missing null safety. Also uses outdated var declaration.",
  "score": 35
}
```
