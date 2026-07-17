---
name: code-review-preferences
description: Use when reviewing code, PRs, or discussing code quality standards. Applies team coding standards and review methodology.
---

<essential_principles>
## Code Review Philosophy

Reviews exist to:
1. **Catch bugs** before production
2. **Share knowledge** across the team
3. **Maintain consistency** in the codebase

Reviews do NOT exist to:
- Show off knowledge
- Enforce personal style preferences
- Block progress unnecessarily

## The 3-Pass Method

### Pass 1: Understand (don't comment yet)
- What is this change trying to do?
- What files are affected?
- What's the scope?

### Pass 2: Correctness
- Are there bugs?
- Are edge cases handled?
- Are there security issues?

### Pass 3: Improvements (max 5 comments)
- Is it readable?
- Is it maintainable?
- Are there better patterns?

## Review Checklist

### Must Check
- [ ] Tests pass
- [ ] No obvious bugs
- [ ] Edge cases handled
- [ ] No security vulnerabilities
- [ ] No secrets in code

### Should Check
- [ ] Code is readable
- [ ] Functions < 50 lines
- [ ] Clear naming
- [ ] Helpful error messages

### Nice to Check
- [ ] Performance considerations
- [ ] Documentation updated
- [ ] Consistent patterns

## Feedback Style

**DO:**
- Ask questions: "What happens if X is null?"
- Be specific: "Line 42: Consider guard clause"
- Acknowledge good work: "Nice refactor"
- Limit comments: Max 5 per review

**DON'T:**
- Dictate: "You must do X"
- Be vague: "This could be better"
- Nitpick style: "I prefer single quotes"
</essential_principles>

<intake>
What would you like me to review?

1. **Paste code/diff** - I'll review inline
2. **Reference file** - Use @filename
3. **Describe PR** - I'll ask questions

**Context:**
- Bug fix / New feature / Refactor / Performance

**Specific concerns?** (Security, breaking changes, etc.)
</intake>
