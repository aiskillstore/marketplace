---
name: code-reviewer
description: |
  Provides thorough code review guidance when users ask for code reviews,
  PR reviews, or feedback on their code. Activates when users mention
  reviewing code, checking for issues, or want feedback on implementations.
---

# Code Reviewer

## Purpose
Provides comprehensive code review following industry best practices, focusing on code quality, security, performance, and maintainability.

## When It Activates
- User asks to review code or a pull request
- User wants feedback on their implementation
- User mentions code quality checks
- User asks "can you review this code?"

## Instructions

When reviewing code, systematically analyze:

### 1. Code Quality
- **Readability**: Is the code clear and self-documenting?
- **Naming**: Are variables, functions, and classes well-named?
- **Complexity**: Are there overly complex sections that need refactoring?
- **DRY Principle**: Is there unnecessary code duplication?

### 2. Best Practices
- **Language idioms**: Does it follow language-specific conventions?
- **Design patterns**: Are appropriate patterns used correctly?
- **Error handling**: Are errors properly caught and handled?
- **Logging**: Is there adequate logging for debugging?

### 3. Security
- **Input validation**: Are all inputs properly validated?
- **SQL injection**: Are database queries parameterized?
- **XSS vulnerabilities**: Is output properly escaped?
- **Authentication/Authorization**: Are permissions checked?
- **Sensitive data**: Are secrets properly protected?

### 4. Performance
- **Algorithmic complexity**: Can performance be improved?
- **Database queries**: Are they efficient (N+1 queries)?
- **Memory usage**: Are there potential memory leaks?
- **Caching**: Could caching improve performance?

### 5. Testing
- **Test coverage**: Are there tests for new functionality?
- **Edge cases**: Are edge cases covered?
- **Test quality**: Are tests meaningful and maintainable?

### 6. Documentation
- **Comments**: Are complex sections explained?
- **API docs**: Are public interfaces documented?
- **README updates**: Does documentation need updating?

## Review Format

Present findings as:

1. **Summary**: Quick overview of the review
2. **Strengths**: What's done well
3. **Issues Found**: Organized by severity (Critical, Major, Minor)
4. **Recommendations**: Specific, actionable improvements
5. **Code Suggestions**: Example code for improvements

## Tone
- Be constructive and encouraging
- Explain the "why" behind suggestions
- Offer alternatives when pointing out issues
- Acknowledge good practices

## Examples

### Example 1: Security Issue
**Issue**: SQL query using string concatenation
**Severity**: Critical
**Why**: Vulnerable to SQL injection attacks
**Fix**: Use parameterized queries
```python
# Bad
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

# Good
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
```

### Example 2: Code Quality
**Issue**: Nested if statements creating high complexity
**Severity**: Minor
**Why**: Reduces readability and maintainability
**Fix**: Use guard clauses or extract to functions
