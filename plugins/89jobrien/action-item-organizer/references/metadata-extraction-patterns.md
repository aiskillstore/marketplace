---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: reference
parent: action-item-organizer
---

# Metadata Extraction Patterns

This document provides detailed patterns and strategies for extracting metadata from various document formats when converting them into actionable TODO lists.

## Core Metadata Types

### 1. Task Description

The primary action to be completed.

**Extraction Strategies:**

**From Prose:**

- Look for imperative verbs: "Add", "Remove", "Fix", "Implement", "Refactor"
- Extract sentences starting with "Should", "Must", "Need to"
- Convert recommendations into action statements

**Examples:**

```
Source: "The authentication system should be updated to use OAuth2."
Extracted: "Update authentication system to use OAuth2"

Source: "Consider refactoring the user service for better maintainability."
Extracted: "Refactor user service for better maintainability"

Source: "It would be good to add caching here."
Extracted: "Add caching to improve performance"
```

**From Lists:**

- Already in action format, extract directly
- Add context if the list item is terse

**Examples:**

```
Source: "- Add tests"
Extracted: "Add unit tests for user service"

Source: "- Fix bug"
Extracted: "Fix null pointer exception in data processing"
```

### 2. Priority Level

The urgency and importance of the task.

**Extraction Strategies:**

**Explicit Markers:**

- "P0", "P1", "P2", "P3"
- "Critical", "High", "Medium", "Low"
- "Blocker", "Major", "Minor", "Trivial"
- "Must", "Should", "Could", "Won't" (MoSCoW)

**Implicit Signals:**

- Section headings: "Critical Issues", "Immediate Actions"
- Language intensity: "MUST fix", "Should consider"
- Context clues: "blocking deployment", "nice to have"

**Examples:**

```
Source: "CRITICAL: Fix authentication bypass"
Extracted Priority: P0

Source: "Consider adding pagination for better UX"
Extracted Priority: P3

Source: "Security Issue: SQL injection in user query"
Extracted Priority: P0 or P1 (based on exposure)

Source: "Code smell: Large function could be split"
Extracted Priority: P2
```

**Priority Inference Table:**

| Keyword/Phrase | Likely Priority |
|----------------|-----------------|
| "MUST fix before deploy" | P0 |
| "Blocking", "Critical", "Blocker" | P0 |
| "Security vulnerability" | P0-P1 |
| "Should fix", "Important" | P1 |
| "Recommended", "Consider" | P2 |
| "Nice to have", "Future" | P3 |
| "Code smell", "Minor issue" | P2-P3 |

### 3. File Paths and Line Numbers

Location in the codebase where action is needed.

**Extraction Patterns:**

**Standard Formats:**

```
path/to/file.ext:line
path/to/file.ext:startLine-endLine
path/to/file.ext:line:column
/absolute/path/to/file.ext:line
```

**Common Variations:**

```
"in file.ext at line 123"
"file.ext (line 123)"
"See path/to/file.ext"
"path/to/file.ext, lines 10-20"
```

**Regex Patterns:**

```regex
# Standard colon format
[\w/.-]+\.(js|ts|py|java|go|rb|php|cs|cpp|h):\d+(-\d+)?

# Prose format
(?:in|at|see)\s+[\w/.-]+\.(ext)(?:\s+at\s+)?(?:line|lines)?\s*\d+

# Parenthetical format
[\w/.-]+\.(ext)\s*\(line\s*\d+\)
```

**Examples:**

```
Source: "Add validation in app/api/user/route.ts:45"
Extracted: app/api/user/route.ts:45

Source: "The calculateTotal function (utils/math.js, line 89) needs error handling"
Extracted: utils/math.js:89

Source: "See authentication middleware for details"
Extracted: (Note: File path not specified, mark as TBD)
```

**Handling Missing Paths:**

When file paths are not specified:

- Mark as "**File**: TBD" in output
- Add note to investigate and add path
- Try to infer from context or section headings

### 4. Owner/Responsible Party

Who should complete the task.

**Extraction Patterns:**

**Direct Assignment:**

```
"@username"
"Assigned to: Team Name"
"Owner: Sarah"
"Responsibility: Backend team"
```

**Implicit Assignment:**

- Section headings: "Backend Tasks", "Frontend Items"
- Context clues: "security team should review"
- Component ownership: "API gateway team"

**Examples:**

```
Source: "@sarah: Update user model schema"
Extracted Owner: Sarah

Source: "Frontend team needs to add loading states"
Extracted Owner: Frontend Team

Source: "Security audit required"
Extracted Owner: Security Team (or TBD if unclear)
```

**Owner Normalization:**

- Convert handles to names if known
- Use consistent team names
- Default to "TBD" if unspecified

### 5. Time Estimates

Expected effort to complete the task.

**Extraction Patterns:**

**Standard Formats:**

```
"2 hours"
"4h"
"1 day"
"3-5 hours"
"2-4d"
"30 minutes"
```

**Conversion Rules:**

- Standardize to hours when possible
- "days" → multiply by 8 (1 day = 8 hours)
- "minutes" → keep as-is or convert to decimal hours
- Ranges → keep as range or use upper bound

**Examples:**

```
Source: "Should take about 2 hours"
Extracted: 2 hours

Source: "Est: 1-2 days"
Extracted: 8-16 hours (or "1-2 days")

Source: "Quick fix, 30 min"
Extracted: 0.5 hours (or "30 minutes")

Source: "Complex refactor, at least a week"
Extracted: 40+ hours (or "1+ weeks")
```

**Inference When Missing:**

- Mark as "Estimate: TBD"
- Consider task complexity for rough estimate
- Don't guess without reasonable basis

**Estimate Complexity Factors:**

```
Simple (1-2 hours):
- Small bug fixes
- Minor text changes
- Simple configuration updates

Medium (4-8 hours):
- New small features
- Moderate refactoring
- Integration of existing components

Complex (16+ hours):
- New major features
- Architectural changes
- Complex security implementations
```

### 6. Tracking IDs

Issue, ticket, or tracking numbers.

**Extraction Patterns:**

**Common Formats:**

```
"#123"
"JIRA-456"
"GH-789"
"Issue #123"
"Ticket: 456"
```

**Regex Patterns:**

```regex
# Hash format
#\d+

# Prefix format
[A-Z]+-\d+

# Full text format
(?:Issue|Ticket|Bug|Task)\s*[:#]?\s*\d+
```

**Examples:**

```
Source: "Fix caching issue #234"
Extracted ID: #234

Source: "JIRA-1234: Implement user roles"
Extracted ID: JIRA-1234

Source: "Related to GitHub issue 567"
Extracted ID: GH-567 (or #567)
```

**Multiple IDs:**

```
Source: "Fixes #123, relates to #456"
Extracted: (#123, #456)

Source: "Implements JIRA-789 and JIRA-790"
Extracted: (JIRA-789, JIRA-790)
```

### 7. Categories/Tags

Domain or type classification.

**Common Categories:**

- Security
- Performance
- Bug Fix
- Feature
- Refactoring
- Testing
- Documentation
- DevOps
- UI/UX
- Database
- API
- Accessibility

**Extraction Strategies:**

**From Section Headers:**

```
Source: Under "Security Issues" heading
Extracted Category: Security

Source: Under "Performance Optimizations"
Extracted Category: Performance
```

**From Keywords:**

```
Source: "Add authentication to endpoint"
Extracted Category: Security

Source: "Optimize database query"
Extracted Category: Performance

Source: "Add unit tests for user service"
Extracted Category: Testing
```

**From Tags:**

```
Source: "[security] Fix XSS vulnerability"
Extracted Category: Security

Source: "(perf) Reduce bundle size"
Extracted Category: Performance
```

### 8. Context and Rationale

Why the task matters.

**Extraction Strategies:**

**From Explanatory Text:**

```
Source: "Add rate limiting to prevent DDoS attacks and ensure service availability"
Extracted Context: Prevents DDoS attacks and ensures service availability

Source: "Refactor UserService because the current implementation is tightly coupled and hard to test"
Extracted Context: Current implementation is tightly coupled and hard to test
```

**From Impact Statements:**

```
Source: "Missing input validation allows SQL injection, potentially exposing user data"
Extracted Context: Allows SQL injection, potentially exposing user data

Source: "N+1 query causing 5-second page load times for users"
Extracted Context: Causing 5-second page load times
```

**Context Signals:**

- "because", "since", "in order to"
- "This will", "This prevents", "This enables"
- "Currently", "The problem is"
- "Impact:", "Risk:", "Benefit:"

## Document Format Patterns

### Code Review Reports

**Structure Recognition:**

```
# Code Review Report

## Critical Issues
- Issue 1
- Issue 2

## Warnings
- Warning 1

## Suggestions
- Suggestion 1
```

**Extraction Pattern:**

1. Map sections to priorities (Critical → P0, Warnings → P1, Suggestions → P2-P3)
2. Extract file paths from issue descriptions
3. Infer owner from file/module structure
4. Extract context from explanatory paragraphs

**Example:**

```
Source Section: "## Critical Issues"
Source Item: "**Security**: Remove hardcoded API key in auth.js:23. This exposes credentials in version control."

Extracted:
- Priority: P0
- Category: Security
- Task: Remove hardcoded API key
- File: auth.js:23
- Context: Exposes credentials in version control
```

### Meeting Notes

**Structure Recognition:**

```
# Team Meeting - 2024-12-09

Discussion topics...

## Action Items
- @sarah will implement feature X by Friday
- Backend team to investigate performance issue
- Everyone: review PR #123 before next meeting
```

**Extraction Pattern:**

1. Focus on "Action Items", "Next Steps", "TODO" sections
2. Extract owner from @mentions or "X will Y" patterns
3. Extract deadlines from temporal phrases
4. Infer priority from urgency language

**Example:**

```
Source: "@sarah will implement OAuth2 authentication ASAP due to security concerns"

Extracted:
- Owner: Sarah
- Task: Implement OAuth2 authentication
- Priority: P0 or P1 (ASAP + security)
- Context: Security concerns
```

### Audit Reports

**Structure Recognition:**

```
# Security Audit Report

## High Risk Findings
1. SQL Injection vulnerability in user search
   - File: search.php, line 45
   - Impact: Database compromise
   - Recommendation: Use parameterized queries

## Medium Risk Findings
...
```

**Extraction Pattern:**

1. Map risk levels to priorities (High → P0/P1, Medium → P2, Low → P3)
2. Extract recommendations as tasks
3. Extract file paths from "File:" or "Location:" fields
4. Extract impact as context

**Example:**

```
Source Finding: "SQL Injection vulnerability in user search"
Source File: "search.php, line 45"
Source Recommendation: "Use parameterized queries"
Source Impact: "Database compromise"

Extracted:
- Priority: P0
- Category: Security
- Task: Fix SQL injection in user search
- Sub-task: Use parameterized queries
- File: search.php:45
- Context: Risk of database compromise
```

### Issue Trackers

**Structure Recognition:**

```
Issue #123: Add user authentication

Priority: High
Assignee: @backend-team
Labels: security, enhancement
Estimated: 8 hours

Description:
Current system lacks authentication...

Acceptance Criteria:
- [ ] Implement login endpoint
- [ ] Add session management
- [ ] Add logout endpoint
```

**Extraction Pattern:**

1. Issue title becomes main task
2. Acceptance criteria become sub-tasks
3. Priority maps directly
4. Assignee becomes owner
5. Description provides context

### Project Plans

**Structure Recognition:**

```
# Q4 2024 Roadmap

## Phase 1: Foundation (High Priority)
- Set up CI/CD pipeline (DevOps, 2 weeks)
- Implement user authentication (Backend, 1 week)

## Phase 2: Features (Medium Priority)
- Add dashboard views (Frontend, 3 weeks)
```

**Extraction Pattern:**

1. Phase indicates priority grouping
2. Task description includes category and estimate
3. Owner often in parentheses
4. Timeline provides deadline context

## Edge Cases and Special Handling

### Ambiguous Priorities

When priority is unclear:

1. Use context clues (security → higher, cosmetic → lower)
2. Default to P2 (medium) and flag for review
3. Note: "Priority needs review" in context

### Nested Action Items

When items have sub-items:

```
Source:
"Implement authentication:
  - Add login endpoint
  - Add session management
  - Add logout endpoint"

Extracted:
- [ ] Implement authentication
  - [ ] Add login endpoint
  - [ ] Add session management
  - [ ] Add logout endpoint
```

### Duplicate Items

When same item appears multiple times:

1. Consolidate into single item
2. Combine context from all occurrences
3. Note multiple sources if from different documents

### Completed Items

When item is marked complete in source:

1. Skip if creating new TODO list
2. Include with [x] if tracking existing progress
3. Note completion in context

### Vague or Unclear Items

When item lacks specificity:

1. Extract as-is but flag for clarification
2. Add note: "Needs clarification" in context
3. Mark metadata as TBD where appropriate

## Validation Checklist

After extraction, verify:

- [ ] All actionable items from source are included
- [ ] Priorities are consistently applied
- [ ] File paths are accurate and complete
- [ ] Owners are assigned or marked TBD
- [ ] Context explains why each task matters
- [ ] Nested relationships are preserved
- [ ] Tracking IDs are included where available
- [ ] Estimates are included or marked TBD

## Examples by Document Type

### Example 1: Dense Code Review Report

**Source:**

```
app/api/auth.ts:45 - Critical: Hardcoded credentials found. Remove immediately.
The SECRET_KEY variable contains production credentials. This poses severe
security risk if committed to version control. Estimate: 30 minutes.

app/utils/db.ts:89-102 - Warning: N+1 query in getUserPosts. This causes
performance issues when users have many posts. Consider using JOIN or eager
loading. Owner: backend team. Estimate: 2 hours.
```

**Extracted:**

```markdown
- [ ] **Security: Remove hardcoded credentials** (#1)
  - [ ] Remove SECRET_KEY variable from code
  - [ ] Move to environment variables
  - [ ] Verify not in git history
  - **File**: `app/api/auth.ts:45`
  - **Owner**: TBD
  - **Estimate**: 0.5 hours
  - **Priority**: P0
  - **Context**: Production credentials in code pose severe security risk

- [ ] **Performance: Fix N+1 query in getUserPosts** (#2)
  - [ ] Refactor to use JOIN or eager loading
  - **File**: `app/utils/db.ts:89-102`
  - **Owner**: Backend Team
  - **Estimate**: 2 hours
  - **Priority**: P1
  - **Context**: Causes performance issues when users have many posts
```

### Example 2: Unstructured Meeting Notes

**Source:**

```
Sarah mentioned we need to update the docs before launch. Mike said
the deployment script is broken and needs fixing urgently. Let's also
consider adding dark mode at some point.
```

**Extracted:**

```markdown
- [ ] **DevOps: Fix broken deployment script**
  - **Owner**: Mike
  - **Estimate**: TBD
  - **Priority**: P0
  - **Context**: Blocking deployment (urgently needed before launch)

- [ ] **Documentation: Update docs before launch**
  - **Owner**: Sarah
  - **Estimate**: TBD
  - **Priority**: P1
  - **Context**: Required before launch

- [ ] **UI: Add dark mode**
  - **Owner**: TBD
  - **Estimate**: TBD
  - **Priority**: P3
  - **Context**: Future enhancement to consider
```

## Conclusion

Effective metadata extraction requires:

1. Pattern recognition across document formats
2. Contextual inference when explicit data is missing
3. Consistent normalization of extracted data
4. Validation to ensure completeness
5. Clear marking of TBD items for follow-up

Use these patterns as a guide, but always apply judgment based on the specific document structure and domain context.
