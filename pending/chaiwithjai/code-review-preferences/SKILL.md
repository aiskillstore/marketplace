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

## Review Standards

### Must Check
- [ ] Tests pass
- [ ] No obvious bugs
- [ ] Edge cases from PR description handled
- [ ] No security vulnerabilities
- [ ] No secrets in code

### Should Check
- [ ] Code is readable
- [ ] Functions are reasonably sized (<50 lines)
- [ ] Names are clear and descriptive
- [ ] Error messages are helpful

### Nice to Check
- [ ] Performance considerations
- [ ] Documentation updated
- [ ] Consistent with existing patterns

## Feedback Style

**DO:**
- Ask questions: "What happens if X is null?"
- Be specific: "Line 42: Consider using a guard clause"
- Acknowledge good work: "Nice refactor here"
- Limit comments: Max 5 per review

**DON'T:**
- Dictate: "You must do X"
- Be vague: "This could be better"
- Nitpick style: "I prefer single quotes"
- Pile on: 20 comments is overwhelming
</essential_principles>

<intake>
What would you like me to review?

1. **Format**
   - Paste the code/diff here
   - Reference a file with @filename
   - Describe the PR and I'll ask questions

2. **Context**
   - Bug fix
   - New feature
   - Refactor
   - Performance optimization
   - Other: ___

3. **Specific concerns?**
   (Security, performance, breaking changes, etc.)

**I'll wait for your answers before starting the review.**
</intake>
