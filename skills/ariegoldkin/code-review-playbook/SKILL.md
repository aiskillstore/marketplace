---
name: code-review-playbook
description: Use this skill when conducting or improving code reviews. Provides structured review processes, conventional comments patterns, language-specific checklists, and feedback templates. Ensures consistent, constructive, and thorough code reviews across teams.
version: 1.0.0
author: AI Agent Hub
tags: [code-review, quality, collaboration, best-practices]
---

# Code Review Playbook

## Overview

This skill provides a comprehensive framework for effective code reviews that improve code quality, share knowledge, and foster collaboration. Whether you're a reviewer giving feedback or an author preparing code for review, this playbook ensures reviews are thorough, consistent, and constructive.

**When to use this skill:**
- Reviewing pull requests or merge requests
- Preparing code for review (self-review)
- Establishing code review standards for teams
- Training new developers on review best practices
- Resolving disagreements about code quality
- Improving review processes and efficiency

## Code Review Philosophy

### Purpose of Code Reviews

Code reviews serve multiple purposes:

1. **Quality Assurance**: Catch bugs, logic errors, and edge cases
2. **Knowledge Sharing**: Spread domain knowledge across the team
3. **Consistency**: Ensure codebase follows conventions and patterns
4. **Mentorship**: Help developers improve their skills
5. **Collective Ownership**: Build shared responsibility for code
6. **Documentation**: Create discussion history for future reference

### Principles

**Be Kind and Respectful:**
- Review the code, not the person
- Assume positive intent
- Praise good solutions
- Frame feedback constructively

**Be Specific and Actionable:**
- Point to specific lines of code
- Explain *why* something should change
- Suggest concrete improvements
- Provide examples when helpful

**Balance Speed with Thoroughness:**
- Aim for timely feedback (< 24 hours)
- Don't rush critical reviews
- Use automation for routine checks
- Focus human review on logic and design

**Distinguish Must-Fix from Nice-to-Have:**
- Use conventional comments to indicate severity
- Block merges only for critical issues
- Allow authors to defer minor improvements
- Capture deferred work in follow-up tickets

---

## Conventional Comments

A standardized format for review comments that makes intent clear.

### Format

```
<label> [decorations]: <subject>

[discussion]
```

### Labels

| Label | Meaning | Blocks Merge? |
|-------|---------|---------------|
| **praise** | Highlight something positive | No |
| **nitpick** | Minor, optional suggestion | No |
| **suggestion** | Propose an improvement | No |
| **issue** | Problem that should be addressed | Usually |
| **question** | Request clarification | No |
| **thought** | Idea to consider | No |
| **chore** | Routine task (formatting, deps) | No |
| **note** | Informational comment | No |
| **todo** | Follow-up work needed | Maybe |
| **security** | Security concern | **Yes** |
| **bug** | Potential bug | **Yes** |
| **breaking** | Breaking change | **Yes** |

### Decorations

Optional modifiers in square brackets:

| Decoration | Meaning |
|------------|---------|
| **[blocking]** | Must be addressed before merge |
| **[non-blocking]** | Optional, can be deferred |
| **[if-minor]** | Only if it's a quick fix |

### Examples

```typescript
// ✅ Good: Clear, specific, actionable

praise: Excellent use of TypeScript generics here!

This makes the function much more reusable while maintaining type safety.

---

nitpick [non-blocking]: Consider using const instead of let

This variable is never reassigned, so `const` would be more appropriate:
```typescript
const MAX_RETRIES = 3;
```

---

issue: Missing error handling for API call

If the API returns a 500 error, this will crash the application.
Add a try/catch block:
```typescript
try {
  const data = await fetchUser(userId);
  // ...
} catch (error) {
  logger.error('Failed to fetch user', { userId, error });
  throw new UserNotFoundError(userId);
}
```

---

question: Why use a Map instead of an object here?

Is there a specific reason for this data structure choice?
If it's for performance, could you add a comment explaining?

---

security [blocking]: API endpoint is not authenticated

The `/api/admin/users` endpoint is missing authentication middleware.
This allows unauthenticated access to sensitive user data.

Add the auth middleware:
```typescript
router.get('/api/admin/users', requireAdmin, getUsers);
```

---

suggestion [if-minor]: Extract magic number to named constant

Consider extracting this value:
```typescript
const CACHE_TTL_SECONDS = 3600;
cache.set(key, value, CACHE_TTL_SECONDS);
```
```

---

## Review Process

### 1. Before Reviewing

**Check Context:**
- Read the PR/MR description
- Understand the purpose and scope
- Review linked tickets or issues
- Check CI/CD pipeline status

**Verify Automated Checks:**
- [ ] Tests are passing
- [ ] Linting has no errors
- [ ] Type checking passes
- [ ] Code coverage meets targets
- [ ] No merge conflicts

**Set Aside Time:**
- Small PR (< 200 lines): 15-30 minutes
- Medium PR (200-500 lines): 30-60 minutes
- Large PR (> 500 lines): 1-2 hours (or ask to split)

### 2. During Review

**Follow a Pattern:**

1. **High-Level Review** (5-10 minutes)
   - Read PR description and understand intent
   - Skim all changed files to get overview
   - Verify approach makes sense architecturally
   - Check that changes align with stated purpose

2. **Detailed Review** (20-45 minutes)
   - Line-by-line code review
   - Check logic, edge cases, error handling
   - Verify tests cover new code
   - Look for security vulnerabilities
   - Ensure code follows team conventions

3. **Testing Considerations** (5-10 minutes)
   - Are tests comprehensive?
   - Do tests test the right things?
   - Are edge cases covered?
   - Is test data realistic?

4. **Documentation Check** (5 minutes)
   - Are complex sections commented?
   - Is public API documented?
   - Are breaking changes noted?
   - Is README updated if needed?

### 3. After Reviewing

**Provide Clear Decision:**
- ✅ **Approve**: Code is ready to merge
- 💬 **Comment**: Feedback provided, no action required
- 🔄 **Request Changes**: Issues must be addressed before merge

**Respond to Author:**
- Answer questions promptly
- Re-review after changes made
- Approve when issues resolved
- Thank author for addressing feedback

---

## Review Checklists

### General Code Quality

- [ ] **Readability**: Code is easy to understand
- [ ] **Naming**: Variables and functions have clear, descriptive names
- [ ] **Comments**: Complex logic is explained
- [ ] **Formatting**: Code follows team style guide
- [ ] **DRY**: No unnecessary duplication
- [ ] **SOLID Principles**: Code follows SOLID where applicable
- [ ] **Function Size**: Functions are focused and < 50 lines
- [ ] **Cyclomatic Complexity**: Functions have complexity < 10

### Functionality

- [ ] **Correctness**: Code does what it's supposed to do
- [ ] **Edge Cases**: Boundary conditions handled (null, empty, min/max)
- [ ] **Error Handling**: Errors caught and handled appropriately
- [ ] **Logging**: Appropriate log levels and messages
- [ ] **Input Validation**: User input is validated and sanitized
- [ ] **Output Validation**: Responses match expected schema

### Testing

- [ ] **Test Coverage**: New code has tests
- [ ] **Test Quality**: Tests actually test the right things
- [ ] **Edge Cases Tested**: Tests cover boundary conditions
- [ ] **Error Paths Tested**: Error handling is tested
- [ ] **Test Isolation**: Tests don't depend on each other
- [ ] **Test Naming**: Test names describe what's being tested

### Performance

- [ ] **Database Queries**: N+1 queries avoided
- [ ] **Caching**: Appropriate caching used
- [ ] **Algorithm Efficiency**: No unnecessarily slow algorithms (O(n²) when O(n) possible)
- [ ] **Resource Cleanup**: Files, connections, memory released
- [ ] **Lazy Loading**: Heavy operations deferred when possible

### Security

- [ ] **Authentication**: Protected endpoints require auth
- [ ] **Authorization**: Users can only access their own data
- [ ] **Input Sanitization**: SQL injection, XSS prevented
- [ ] **Secrets Management**: No hardcoded credentials or API keys
- [ ] **Encryption**: Sensitive data encrypted at rest and in transit
- [ ] **HTTPS Only**: Production traffic uses HTTPS
- [ ] **Rate Limiting**: Endpoints protected from abuse

### Language-Specific (JavaScript/TypeScript)

- [ ] **Async/Await**: Promises handled correctly
- [ ] **Type Safety**: TypeScript types are specific (not `any`)
- [ ] **Nullability**: Null checks where needed (`?.` operator)
- [ ] **Array Methods**: Using map/filter/reduce appropriately
- [ ] **Const vs Let**: Using const for immutable values
- [ ] **Arrow Functions**: Appropriate use of arrow vs regular functions

### Language-Specific (Python)

- [ ] **PEP 8**: Follows Python style guide
- [ ] **Type Hints**: Functions have type annotations
- [ ] **List Comprehensions**: Used where appropriate (not overused)
- [ ] **Context Managers**: Using `with` for file/connection handling
- [ ] **Exception Handling**: Specific exceptions caught (not bare `except:`)
- [ ] **F-Strings**: Modern string formatting used

### API Design

- [ ] **RESTful**: Follows REST conventions (if REST API)
- [ ] **Consistent Naming**: Endpoints follow naming patterns
- [ ] **HTTP Methods**: Correct methods used (GET, POST, PUT, DELETE)
- [ ] **Status Codes**: Appropriate HTTP status codes returned
- [ ] **Error Responses**: Consistent error format
- [ ] **Pagination**: Large lists are paginated
- [ ] **Versioning**: API version strategy followed

### Database

- [ ] **Migrations**: Database changes have migrations
- [ ] **Indexes**: Appropriate indexes created
- [ ] **Transactions**: ACID properties maintained
- [ ] **Cascades**: Delete cascades handled correctly
- [ ] **Constraints**: Foreign keys, unique constraints defined
- [ ] **N+1 Queries**: Eager loading used where needed

### Documentation

- [ ] **PR Description**: Clear explanation of changes
- [ ] **Code Comments**: Complex logic explained
- [ ] **API Docs**: Public API documented (JSDoc, docstrings)
- [ ] **README**: Updated if functionality changed
- [ ] **CHANGELOG**: Breaking changes documented

---

## Review Feedback Patterns

### How to Give Constructive Feedback

#### ✅ Good Feedback

```
issue: This function doesn't handle the case where the user is null

If `getUserById()` returns null (user not found), this will throw:
`Cannot read property 'email' of null`

Add a null check:
```typescript
const user = await getUserById(userId);
if (!user) {
  throw new UserNotFoundError(userId);
}
return user.email;
```
```

**Why it's good:**
- Specific (points to exact problem)
- Explains the impact (what will happen)
- Suggests a concrete solution
- Provides example code

#### ❌ Bad Feedback

```
This is wrong. Fix it.
```

**Why it's bad:**
- Not specific (what's wrong?)
- Not helpful (how to fix?)
- Sounds harsh (not constructive)

---

### How to Receive Feedback

**As an Author:**

1. **Assume Good Intent**: Reviewers are trying to help
2. **Ask Questions**: If feedback is unclear, ask for clarification
3. **Acknowledge Valid Points**: Accept feedback graciously
4. **Explain Your Reasoning**: If you disagree, explain why
5. **Make Changes Promptly**: Address feedback quickly
6. **Say Thank You**: Appreciate the reviewer's time

**Responding to Feedback:**

```markdown
✅ Good Response:
> Good catch! I didn't consider the null case.
> I've added the null check in commit abc123.

✅ Good Response (Disagreement):
> I chose a Map here because we need O(1) lookups on a large dataset.
> An object would work but performs worse at scale (n > 10,000).
> I added a comment explaining this tradeoff.

❌ Bad Response:
> This works fine. Not changing it.
```

---

## Code Review Anti-Patterns

### For Reviewers

❌ **Nitpicking Without Clear Value**
```
nitpick: Add a space here
nitpick: Rename this variable to `userInfo` instead of `userData`
nitpick: Move this import to the top
```
**Better:** Use automated tools (Prettier, linters) for formatting.

❌ **Reviewing Line-by-Line Without Understanding Context**
**Better:** Read PR description first, understand the big picture.

❌ **Blocking on Personal Preferences**
```
This should be a class instead of functions.
```
**Better:** Only block on objective issues (bugs, security). Discuss preferences separately.

❌ **Rewriting Code in Comments**
**Better:** Suggest improvements, don't provide full implementations (unless very helpful).

❌ **Review Fatigue (Approving Without Reading)**
**Better:** If you don't have time, say so. Don't rubber-stamp.

### For Authors

❌ **Giant Pull Requests (> 1000 lines)**
**Better:** Break into smaller, focused PRs.

❌ **No Description**
**Better:** Write clear PR description with context and testing notes.

❌ **Submitting Failing Tests**
**Better:** Ensure all automated checks pass before requesting review.

❌ **Getting Defensive About Feedback**
**Better:** Accept feedback gracefully, discuss respectfully.

❌ **Force-Pushing After Review**
**Better:** Add new commits so reviewers can see what changed.

---

## Review Templates

### Standard PR Template

```markdown
## Description

Brief summary of what changed and why.

Fixes #[issue number]

## Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Refactoring (no functional changes)
- [ ] Documentation update

## How Has This Been Tested?

- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Tested manually in local environment
- [ ] Tested in staging environment

## Checklist

- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published

## Screenshots (if applicable)

[Add screenshots for UI changes]

## Additional Notes

[Any additional context or notes for reviewers]
```

### Security Review Template

```markdown
## Security Review Checklist

### Authentication & Authorization
- [ ] Endpoints require appropriate authentication
- [ ] User permissions are checked before actions
- [ ] JWT tokens are validated and not expired
- [ ] Session management is secure

### Input Validation
- [ ] All user inputs are validated
- [ ] SQL injection prevented (parameterized queries)
- [ ] XSS prevented (input sanitization, CSP headers)
- [ ] CSRF protection in place for state-changing operations

### Data Protection
- [ ] Sensitive data is encrypted at rest
- [ ] TLS/HTTPS used for data in transit
- [ ] API keys and secrets not hardcoded
- [ ] PII is properly handled (GDPR/CCPA compliance)

### Dependencies
- [ ] No known vulnerabilities in dependencies (npm audit / pip-audit)
- [ ] Dependencies from trusted sources
- [ ] Dependency versions pinned

### Logging & Monitoring
- [ ] Sensitive data not logged (passwords, tokens)
- [ ] Security events logged (failed auth attempts)
- [ ] Rate limiting in place for public endpoints

**Security Concerns Identified:**
[List any security issues found]

**Reviewer Signature:**
[Name, Date]
```

---

## Review Metrics and Goals

### Healthy Review Metrics

| Metric | Target | Purpose |
|--------|--------|---------|
| **Review Time** | < 24 hours | Fast feedback loop |
| **PR Size** | < 400 lines | Manageable reviews |
| **Approval Rate (first review)** | 20-30% | Balance speed vs quality |
| **Comments per PR** | 3-10 | Engaged but not overwhelming |
| **Back-and-Forth Rounds** | 1-2 | Efficient communication |
| **Time to Merge (after approval)** | < 2 hours | Avoid stale branches |

### Warning Signs

- ⚠️ PRs sitting unreviewed for > 3 days (review capacity issue)
- ⚠️ 90%+ approval rate on first review (rubber-stamping)
- ⚠️ Average PR size > 800 lines (PRs too large)
- ⚠️ 15+ comments per PR (overly nitpicky or unclear requirements)
- ⚠️ 5+ review rounds (poor communication or unclear standards)

---

## Integration with Agents

### Code Quality Reviewer Agent
- Uses this playbook when reviewing code
- Applies conventional comments format
- Follows language-specific checklists
- Provides structured, actionable feedback

### Backend System Architect
- Reviews for architectural soundness
- Checks design patterns and scalability
- Validates API design against best practices

### Frontend UI Developer
- Reviews component structure and patterns
- Checks accessibility and responsive design
- Validates UI/UX implementation

### Security Reviewer (Future Agent)
- Focuses on security checklist
- Identifies vulnerabilities
- Validates compliance requirements

---

## Advanced Pattern Detection (Opus 4.5)

### Extended Thinking for Complex Reviews

For large PRs or systemic analysis, leverage Opus 4.5's extended thinking to perform deep pattern detection:

**When to Use Extended Thinking:**
- PR touches > 10 files across multiple modules
- Reviewing security-critical code paths
- Analyzing architectural consistency
- Detecting cross-file code smells
- Evaluating breaking change impact

**Extended Thinking Review Pattern:**

Based on [Anthropic's Extended Thinking API](https://docs.anthropic.com/en/docs/build-with-claude/extended-thinking):

```typescript
import Anthropic from '@anthropic-ai/sdk';

interface ReviewResult {
  issues: ReviewIssue[];
  patterns: DetectedPattern[];
  recommendations: string[];
  riskScore: number;
}

async function performDeepCodeReview(
  prDiff: string,
  codebaseContext: string
): Promise<ReviewResult> {
  const anthropic = new Anthropic();

  // Extended thinking requires budget_tokens < max_tokens
  // Minimum budget: 1,024 tokens
  const response = await anthropic.messages.create({
    model: 'claude-opus-4-5-20251101',
    max_tokens: 16000,
    thinking: {
      type: 'enabled',
      budget_tokens: 8000 // Deep analysis for complex reviews
    },
    messages: [{
      role: 'user',
      content: `
        Perform a comprehensive code review analyzing:

        ## PR Changes
        ${prDiff}

        ## Codebase Context
        ${codebaseContext}

        ## Analysis Requirements
        1. **Systemic Pattern Detection**: Identify recurring patterns (good and bad)
        2. **Cross-File Impact**: Trace how changes affect other modules
        3. **Security Analysis**: Deep scan for vulnerabilities (OWASP Top 10)
        4. **Architectural Consistency**: Verify alignment with existing patterns
        5. **Technical Debt Assessment**: Identify debt being added or resolved

        Provide structured output with:
        - Critical issues (must fix)
        - Warnings (should fix)
        - Suggestions (nice to have)
        - Detected patterns (positive and negative)
        - Risk score (1-10)
      `
    }]
  });

  // Response contains thinking blocks followed by text blocks
  // content: [{ type: 'thinking', thinking: '...' }, { type: 'text', text: '...' }]
  return parseReviewResponse(response);
}
```

### Systemic Code Smell Detection

Detect patterns that span multiple files:

```typescript
interface CodeSmellPattern {
  type: 'duplication' | 'coupling' | 'complexity' | 'naming' | 'architecture';
  severity: 'critical' | 'warning' | 'info';
  locations: FileLocation[];
  description: string;
  suggestion: string;
}

const SMELL_PATTERNS = {
  // Cross-file duplication
  duplication: {
    triggers: ['similar logic in 3+ files', 'copy-paste patterns', 'repeated error handling'],
    action: 'Extract to shared utility or base class'
  },

  // Tight coupling
  coupling: {
    triggers: ['circular imports', 'god objects', 'feature envy'],
    action: 'Apply dependency injection or interface segregation'
  },

  // Complexity creep
  complexity: {
    triggers: ['nested callbacks > 3 levels', 'functions > 50 lines', 'cyclomatic complexity > 10'],
    action: 'Decompose into smaller, focused functions'
  },

  // Inconsistent naming
  naming: {
    triggers: ['mixed conventions', 'unclear abbreviations', 'inconsistent pluralization'],
    action: 'Align with codebase naming conventions'
  },

  // Architectural drift
  architecture: {
    triggers: ['layer violations', 'missing abstractions', 'inappropriate intimacy'],
    action: 'Refactor to follow established architectural patterns'
  }
};
```

### Security Deep Analysis

Extended thinking enables comprehensive security review:

```typescript
interface SecurityFinding {
  category: 'injection' | 'auth' | 'crypto' | 'exposure' | 'config';
  severity: 'critical' | 'high' | 'medium' | 'low';
  cwe: string; // CWE ID
  location: FileLocation;
  description: string;
  remediation: string;
}

async function performSecurityReview(
  code: string,
  context: SecurityContext
): Promise<SecurityFinding[]> {
  const anthropic = new Anthropic();

  const response = await anthropic.messages.create({
    model: 'claude-opus-4-5-20251101',
    max_tokens: 12000,
    thinking: {
      type: 'enabled',
      budget_tokens: 6000 // Security analysis needs deep reasoning
    },
    messages: [{
      role: 'user',
      content: `
        Perform security analysis on this code:

        ${code}

        Context:
        - Language: ${context.language}
        - Framework: ${context.framework}
        - Exposure: ${context.isPublicFacing ? 'Public' : 'Internal'}

        Check for:
        1. Injection vulnerabilities (SQL, XSS, command)
        2. Authentication/Authorization flaws
        3. Cryptographic weaknesses
        4. Sensitive data exposure
        5. Security misconfiguration

        For each finding, provide CWE ID and specific remediation.
      `
    }]
  });

  return parseSecurityFindings(response);
}
```

### Cross-File Impact Analysis

Trace how changes ripple through the codebase:

```typescript
interface ImpactAnalysis {
  directImpact: FileImpact[];
  indirectImpact: FileImpact[];
  breakingChanges: BreakingChange[];
  testCoverage: TestCoverageGap[];
}

async function analyzeChangeImpact(
  changedFiles: string[],
  dependencyGraph: DependencyGraph
): Promise<ImpactAnalysis> {
  // Build impact graph
  const directlyAffected = new Set<string>();
  const indirectlyAffected = new Set<string>();

  for (const file of changedFiles) {
    // Files that import this file
    const dependents = dependencyGraph.getDependents(file);
    dependents.forEach(d => directlyAffected.add(d));

    // Second-level dependents
    for (const dependent of dependents) {
      const secondLevel = dependencyGraph.getDependents(dependent);
      secondLevel.forEach(d => {
        if (!directlyAffected.has(d)) {
          indirectlyAffected.add(d);
        }
      });
    }
  }

  // Use extended thinking for breaking change analysis
  const breakingAnalysis = await analyzeBreakingChanges(
    changedFiles,
    Array.from(directlyAffected)
  );

  return {
    directImpact: Array.from(directlyAffected).map(f => ({ file: f, type: 'direct' })),
    indirectImpact: Array.from(indirectlyAffected).map(f => ({ file: f, type: 'indirect' })),
    breakingChanges: breakingAnalysis.breaking,
    testCoverage: breakingAnalysis.gaps
  };
}
```

### Review Automation with Model Tiering

Optimize review costs with intelligent model selection:

```typescript
type ModelTier = 'opus' | 'sonnet' | 'haiku';

interface ReviewConfig {
  model: ModelTier;
  thinkingBudget?: number;
  focus: string[];
}

function selectReviewModel(pr: PullRequest): ReviewConfig {
  // Critical path - use Opus with extended thinking
  if (pr.touchesCriticalPath || pr.isSecurityRelated) {
    return {
      model: 'opus',
      thinkingBudget: 8000,
      focus: ['security', 'architecture', 'breaking-changes']
    };
  }

  // Large PRs - use Opus for systemic analysis
  if (pr.filesChanged > 10 || pr.linesChanged > 500) {
    return {
      model: 'opus',
      thinkingBudget: 5000,
      focus: ['patterns', 'impact', 'consistency']
    };
  }

  // Standard PRs - Sonnet for thorough review
  if (pr.linesChanged > 100) {
    return {
      model: 'sonnet',
      focus: ['correctness', 'style', 'tests']
    };
  }

  // Small changes - Haiku for quick review
  return {
    model: 'haiku',
    focus: ['correctness', 'style']
  };
}
```

### Review Comment Generation

Generate conventional comments automatically:

```typescript
interface GeneratedComment {
  label: 'praise' | 'nitpick' | 'suggestion' | 'issue' | 'question' | 'security' | 'bug';
  decoration?: 'blocking' | 'non-blocking' | 'if-minor';
  subject: string;
  discussion: string;
  location: { file: string; line: number };
}

function formatConventionalComment(comment: GeneratedComment): string {
  const decoration = comment.decoration ? ` [${comment.decoration}]` : '';
  return `${comment.label}${decoration}: ${comment.subject}\n\n${comment.discussion}`;
}

// Example output:
// security [blocking]: SQL injection vulnerability in user search
//
// The search query is constructed using string concatenation:
// ```typescript
// const query = `SELECT * FROM users WHERE name = '${searchTerm}'`;
// ```
//
// Use parameterized queries instead:
// ```typescript
// const query = 'SELECT * FROM users WHERE name = $1';
// const result = await db.query(query, [searchTerm]);
// ```
```

---

## Quick Start Guide

**For Reviewers:**
1. Read PR description and understand intent
2. Check that automated checks pass
3. Do high-level review (architecture, approach)
4. Do detailed review (logic, edge cases, tests)
5. Use conventional comments for clear communication
6. Provide decision: Approve, Comment, or Request Changes

**For Authors:**
1. Write clear PR description
2. Perform self-review before requesting review
3. Ensure all automated checks pass
4. Keep PR focused and reasonably sized (< 400 lines)
5. Respond to feedback promptly and respectfully
6. Make requested changes or explain reasoning

---

**Skill Version**: 2.0.0
**Last Updated**: 2025-11-27
**Maintained by**: AI Agent Hub Team
