# Agent Quality Checklist

Use this checklist to review agent quality before deployment or during maintenance reviews.

---

## Quick Assessment

**Agent Name**: ________________
**Review Date**: ________________
**Reviewer**: ________________
**Overall Score**: _____ / 10

---

## 1. Schema Compliance (10 points)

### Required Fields
- [ ] **Name** present and valid (2 pts)
  - [ ] Lowercase letters, numbers, hyphens only
  - [ ] Max 64 characters
  - [ ] Descriptive and unique

- [ ] **Description** present and clear (3 pts)
  - [ ] Under 1024 characters
  - [ ] Explains what agent does
  - [ ] Specifies when to invoke
  - [ ] Actionable and specific

### Optional Fields
- [ ] **Tools** specified appropriately (3 pts)
  - [ ] Minimal necessary permissions
  - [ ] No unnecessary tools
  - [ ] Properly comma-separated

- [ ] **Model** selection is appropriate (2 pts)
  - [ ] Uses version alias (haiku/sonnet/opus) OR specific version
  - [ ] Matches task complexity
  - [ ] Cost-effective choice

### Format
- [ ] **YAML frontmatter** valid
  - [ ] Starts with `---`
  - [ ] Valid YAML syntax
  - [ ] Ends with `---`
  - [ ] Followed by markdown body

**Schema Score**: _____ / 10

---

## 2. Security (10 points)

### Tool Permissions
- [ ] **Minimal permissions** (3 pts)
  - [ ] Only grants necessary tools
  - [ ] No over-permissioning
  - [ ] Removes unused tools

- [ ] **Bash access** (if applicable) (3 pts)
  - [ ] Justified need for Bash
  - [ ] Input validation documented
  - [ ] Command injection prevention
  - [ ] Proper escaping/quoting

- [ ] **Write permissions** (if applicable) (2 pts)
  - [ ] Justified need for Write/Edit
  - [ ] File validation documented
  - [ ] No arbitrary file writes

### Security Patterns
- [ ] **No hardcoded secrets** (2 pts)
  - [ ] No API keys in agent body
  - [ ] No passwords or tokens
  - [ ] Uses environment variables

**Security Score**: _____ / 10

**Critical Issues** (must fix before deployment):
- [ ] None identified
- [ ] Issues listed below:

---

## 3. Content Quality (10 points)

### Core Sections
- [ ] **Role definition** clear (2 pts)
  - [ ] "You are..." statement present
  - [ ] Expertise area specified
  - [ ] Boundaries defined

- [ ] **Capabilities** documented (2 pts)
  - [ ] Lists what agent can do
  - [ ] Specific and concrete
  - [ ] 3-5 key capabilities

- [ ] **Workflow** documented (2 pts)
  - [ ] Step-by-step process
  - [ ] Actionable steps
  - [ ] Logical flow

- [ ] **Examples** provided (2 pts)
  - [ ] 2-3 concrete examples
  - [ ] Real-world scenarios
  - [ ] Expected outputs shown

- [ ] **Best practices** listed (1 pt)
  - [ ] Guidelines present
  - [ ] Standards specified
  - [ ] Quality expectations

- [ ] **Error handling** documented (1 pt)
  - [ ] Common errors listed
  - [ ] Graceful degradation
  - [ ] User-friendly messages

**Content Quality Score**: _____ / 10

**Missing Sections**:
- [ ] _______________________
- [ ] _______________________

---

## 4. Maintainability (10 points)

### Structure & Organization
- [ ] **Clear headings** (2 pts)
  - [ ] 5+ section headings
  - [ ] Logical organization
  - [ ] Easy navigation

- [ ] **Formatting** (2 pts)
  - [ ] Uses lists where appropriate
  - [ ] Code blocks for examples
  - [ ] Bold/italic for emphasis

- [ ] **Readability** (2 pts)
  - [ ] Clear, concise writing
  - [ ] No overly long lines
  - [ ] Good use of whitespace

### Documentation
- [ ] **Comments** (if needed) (1 pt)
  - [ ] Complex sections explained
  - [ ] Changelog present (if versioned)
  - [ ] TODOs documented

- [ ] **Consistency** (2 pts)
  - [ ] Consistent terminology
  - [ ] Consistent formatting
  - [ ] Follows conventions

- [ ] **Length** appropriate (1 pt)
  - [ ] Not too brief (>100 words)
  - [ ] Not too verbose (<2000 words)
  - [ ] Balanced detail

**Maintainability Score**: _____ / 10

---

## 5. Functionality (Qualitative)

### Does it work?
- [ ] **Agent invokes successfully**
  - [ ] No loading errors
  - [ ] Appears in agent list

- [ ] **Produces expected output**
  - [ ] Follows documented workflow
  - [ ] Quality meets standards
  - [ ] Handles edge cases

- [ ] **Performance acceptable**
  - [ ] Completes in reasonable time
  - [ ] Model choice is appropriate
  - [ ] Resource usage is acceptable

**Issues Found** (during testing):
- [ ] _______________________
- [ ] _______________________

---

## 6. Alignment & Overlap

### Purpose Clarity
- [ ] **Unique purpose**
  - [ ] Not redundant with other agents
  - [ ] Clear differentiation
  - [ ] Fills specific need

- [ ] **Appropriate scope**
  - [ ] Not too broad (does too much)
  - [ ] Not too narrow (too trivial)
  - [ ] Focused on one domain

### Comparison (if similar agents exist)
- [ ] **Compared with**: _______________________
- [ ] **Key differences**: _______________________
- [ ] **Recommendation**:
  - [ ] Keep both (different purposes)
  - [ ] Merge into one
  - [ ] Specialize further
  - [ ] Deprecate one

---

## Overall Assessment

### Scores Summary

| Category | Score | Weight | Weighted |
|----------|-------|--------|----------|
| Schema Compliance | ___ / 10 | 1.0 | ___ |
| Security | ___ / 10 | 1.0 | ___ |
| Content Quality | ___ / 10 | 1.0 | ___ |
| Maintainability | ___ / 10 | 1.0 | ___ |
| **Total** | | | **___ / 10** |

### Rating

- **9-10**: Excellent - Ready for production
- **7-8**: Good - Minor improvements recommended
- **5-6**: Fair - Significant improvements needed
- **0-4**: Poor - Major revision required

**Agent Rating**: _______________

---

## Action Items

### Critical (Must Fix)
1. _______________________
2. _______________________

### High Priority (Should Fix)
1. _______________________
2. _______________________

### Medium Priority (Nice to Have)
1. _______________________
2. _______________________

### Low Priority (Optional)
1. _______________________
2. _______________________

---

## Automated Assessment

### Run These Commands

```bash
# Validation
python3 agent-builder/skills/building-agents/scripts/validate-agent.py path/to/agent.md

# Enhancement analysis
python3 agent-builder/skills/building-agents/scripts/enhance-agent.py agent-name

# Comparison (if similar agents exist)
/agent-builder:agents:compare agent-name similar-agent
```

### Automated Scores

| Tool | Score | Notes |
|------|-------|-------|
| validate-agent.py | PASS / FAIL | _____________ |
| enhance-agent.py | ___ / 10 | _____________ |
| compare similarity | ___ % | _____________ |

---

## Review Notes

### Strengths
- _______________________
- _______________________
- _______________________

### Weaknesses
- _______________________
- _______________________
- _______________________

### Recommendations
- _______________________
- _______________________
- _______________________

---

## Decision

- [ ] **Approve** - Ready to use
- [ ] **Approve with conditions** - Minor fixes needed
- [ ] **Revise** - Significant changes required
- [ ] **Reject** - Not viable, start over

**Reviewer Signature**: ________________
**Date**: ________________

---

## Follow-Up

### Next Review Date
Recommended: ________________

### Tracking
- **Issue/Ticket**: ________________
- **Git Commit**: ________________
- **Documentation Updated**: Yes / No

---

## Appendix: Scoring Guidelines

### Schema Compliance Scoring

**10/10** - Perfect schema
- All required fields present and valid
- Optional fields used appropriately
- Follows all conventions

**7-9/10** - Good schema
- Required fields present
- Minor improvements possible

**4-6/10** - Needs work
- Some fields missing or invalid
- Doesn't fully follow conventions

**0-3/10** - Poor schema
- Missing critical fields
- Invalid format
- Won't load properly

### Security Scoring

**10/10** - Excellent security
- Minimal necessary permissions
- All risks addressed
- Best practices followed

**7-9/10** - Good security
- Reasonable permissions
- Most risks addressed
- Minor improvements possible

**4-6/10** - Security concerns
- Over-permissioned
- Some risks unaddressed
- Needs hardening

**0-3/10** - Security issues
- Dangerous permissions
- No input validation
- Critical vulnerabilities

### Content Quality Scoring

**10/10** - Comprehensive documentation
- All sections present
- Excellent examples
- Clear and thorough

**7-9/10** - Good documentation
- Most sections present
- Some examples
- Generally clear

**4-6/10** - Incomplete documentation
- Missing key sections
- Few/no examples
- Unclear in places

**0-3/10** - Poor documentation
- Most sections missing
- No examples
- Confusing or vague

### Maintainability Scoring

**10/10** - Highly maintainable
- Well-structured
- Excellent formatting
- Very readable

**7-9/10** - Maintainable
- Good structure
- Decent formatting
- Readable

**4-6/10** - Needs improvement
- Poor structure
- Inconsistent formatting
- Hard to read

**0-3/10** - Unmaintainable
- No structure
- No formatting
- Unreadable

---

## Related Resources

- [Update Patterns](../references/agent-update-patterns.md) - Common update scenarios
- [Migration Guide](../references/migration-guide.md) - Schema migrations
- [SKILL.md](../SKILL.md) - Complete building guide
- [Agent Template](./agent-template.md) - Standard template
