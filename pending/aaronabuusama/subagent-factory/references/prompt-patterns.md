# Prompt Patterns for Effective Agents

This document provides proven patterns for writing effective agent system prompts based on Anthropic's prompt engineering best practices.

## Core Principles

### The "Right Altitude" Principle

Agent prompts should be at the sweet spot between:

**Too Low (Over-Constrained)**:
```markdown
If user asks about pricing, say "Our pricing starts at $10/month"
If user asks about features, say "We have features A, B, C"
```
**Problem**: Brittle, maintenance-heavy, limits agent flexibility

**Too High (Too Vague)**:
```markdown
Be helpful and answer questions.
```
**Problem**: No guidance, unpredictable behavior

**Just Right**:
```markdown
You are a product expert. When discussing pricing:
- Start with value proposition
- Present tier options with key differentiators
- Offer to schedule demo for complex needs

When discussing features:
- Ask about user's specific use case
- Highlight relevant features
- Provide concrete examples
```
**Benefit**: Clear guidance that allows reasoning

### Minimalism with Completeness

**Goal**: Minimal set of information that fully outlines expected behavior

**Not**:
- Shortest possible prompt (may be incomplete)
- Exhaustive documentation (too noisy)

**But**:
- Essential information only
- Complete coverage of key scenarios
- High signal-to-noise ratio

### Clarity Over Complexity

**Be Clear, Direct, and Detailed**:
- Don't assume AI reads minds
- Specificity reduces ambiguity
- Small details matter (typos throw off model)
- Use your native/strongest language

## Prompt Structure

### Recommended Component Order

1. **Identity/Role** - Who the agent is
2. **Responsibilities** - What the agent does
3. **Context** - Background information needed
4. **Workflow** - Step-by-step process
5. **Checklists** - Concrete items to verify
6. **Examples** - Demonstrate desired patterns
7. **Output Format** - Structure of results
8. **Boundaries** - DO/DO NOT guidelines

### Clear Delineation

Use headers, lists, and structure:

```markdown
## Responsibilities

When invoked, you will:
1. [First responsibility]
2. [Second responsibility]
3. [Third responsibility]

## Workflow

### Step 1: [Action]
[Details and guidance]

### Step 2: [Action]
[Details and guidance]
```

## Pattern 1: Identity and Role Definition

### Purpose
Sets persona, expertise level, and domain focus.

### Structure

```markdown
You are a [role] with [expertise/experience].

Your specializations include:
- [Domain 1]
- [Domain 2]
- [Domain 3]
```

### Examples

**Security Reviewer**:
```markdown
You are a senior security engineer with 15+ years of experience in authentication
systems and vulnerability assessment. Your expertise includes:
- OWASP Top 10 vulnerabilities
- Authentication and authorization protocols (OAuth, JWT, SAML)
- Cryptography and secure key management
- Threat modeling and attack vector analysis
- Security compliance (SOC2, GDPR, HIPAA)
```

**Test Runner**:
```markdown
You are a test automation specialist with deep knowledge of:
- Test-driven development (TDD) and behavior-driven development (BDD)
- Common testing frameworks (Jest, Pytest, Go testing)
- Debugging test failures and flaky tests
- CI/CD best practices
- Code coverage analysis
```

**Tech Researcher**:
```markdown
You are a technology researcher skilled in evaluating frameworks, libraries,
and architectural patterns. Your expertise includes:
- API design and evaluation
- Performance benchmarking
- Security and compliance analysis
- License compatibility assessment
- Community health indicators (activity, maintenance, support)
```

### Why It Works
- Primes model with relevant domain knowledge
- Sets appropriate tone and vocabulary
- Establishes authority and confidence

## Pattern 2: Clear Responsibilities

### Purpose
Define what the agent does when invoked.

### Structure

```markdown
When invoked:
1. [Primary action]
2. [Secondary action]
3. [Result delivery]
```

### Examples

**Code Reviewer**:
```markdown
When invoked to review code:
1. Run `git diff --cached` to see staged changes (or `git diff main` for branch comparison)
2. For each modified file:
   - Read full file for context
   - Understand purpose of changes
   - Check against quality checklists
3. Generate findings report in specified format
```

**Test Runner**:
```markdown
When invoked:
1. Identify and execute project test command (from package.json, Makefile, etc.)
2. Capture full test output
3. If failures occur:
   - Read failing test files
   - Analyze root cause (code bug vs test bug)
   - Propose minimal fix with rationale
4. Report results with actionable recommendations
```

### Why It Works
- Creates predictable workflow
- Sets clear expectations
- Reduces ambiguity about agent's role

## Pattern 3: Concrete Checklists

### Purpose
Provide specific items to verify, preventing oversight.

### Structure

```markdown
## [Domain] Checklist

- [ ] Item 1 with specific criterion
- [ ] Item 2 with specific criterion
- [ ] Item 3 with specific criterion
```

### Examples

**Security Checklist**:
```markdown
## Security Checklist

Authentication & Authorization:
- [ ] Authentication checks before all sensitive operations
- [ ] Proper authorization (user can only access their own data)
- [ ] Session management (timeouts, secure cookies, regeneration)
- [ ] Password handling (hashing, complexity requirements, no plaintext)

Input Validation:
- [ ] Validation on all user-supplied data
- [ ] Parameterized queries (no SQL injection)
- [ ] Output encoding (no XSS vulnerabilities)
- [ ] File upload restrictions (type, size, location)

Secrets Management:
- [ ] No hardcoded secrets, API keys, or passwords
- [ ] Secrets loaded from environment variables or secret managers
- [ ] No secrets in logs or error messages
- [ ] Proper key rotation mechanisms
```

**Code Quality Checklist**:
```markdown
## Code Quality Checklist

Readability:
- [ ] Functions and variables have clear, descriptive names
- [ ] Functions are small and focused (< 50 lines)
- [ ] Complex logic has explanatory comments
- [ ] No commented-out code

Maintainability:
- [ ] No code duplication (DRY principle applied)
- [ ] Proper error handling throughout
- [ ] Appropriate logging at key points
- [ ] Consistent code formatting

Testing:
- [ ] Critical paths have test coverage
- [ ] Edge cases are tested
- [ ] Error conditions are tested
- [ ] Tests are independent (no shared state)
```

### Why It Works
- Systematic coverage
- Nothing forgotten
- Concrete evaluation criteria
- Consistent quality

## Pattern 4: Examples (Multishot Prompting)

### Purpose
Show exactly what you want, not just describe it.

### Structure

```markdown
## Example [Scenario]

### Input
[What agent receives]

### Analysis
[How agent should think]

### Output
[What agent should produce]
```

### Examples

**Security Finding Example**:
```markdown
## Example Security Finding

### Input
```python
def login(email):
    query = "SELECT * FROM users WHERE email = '" + email + "'"
    return db.execute(query)
```

### Analysis
Direct string concatenation in SQL query creates SQL injection vulnerability.
Attacker could input: `admin@example.com' OR '1'='1` to bypass authentication.

### Output
**HIGH SEVERITY: SQL Injection Vulnerability**
- **File**: `auth/login.py:45`
- **Issue**: Direct string concatenation in SQL query
- **Risk**: Authentication bypass, data exfiltration
- **Code**:
  ```python
  query = "SELECT * FROM users WHERE email = '" + email + "'"
  ```
- **Fix**:
  ```python
  query = "SELECT * FROM users WHERE email = ?"
  return db.execute(query, [email])
  ```
- **Why**: Parameterized queries prevent SQL injection by separating query structure from data
```

**Test Failure Analysis Example**:
```markdown
## Example Test Failure

### Input
```
FAIL: test_user_creation (tests/test_auth.py)
AssertionError: Expected 201, got 400
```

### Analysis
Test expects successful user creation (201) but receives validation error (400).
Need to check:
1. What validation is failing?
2. Is test input invalid, or is validation too strict?
3. Recent changes to user model or validation logic?

### Output
**Test Failure Analysis: test_user_creation**

**Root Cause**: Recent commit added email format validation. Test uses invalid email format.

**Evidence**:
- Test input: `email='testuser'` (missing domain)
- New validation: Email must match regex `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`
- Error response: `{"error": "Invalid email format"}`

**Proposed Fix**:
```python
# Change this:
response = client.post('/users', {'email': 'testuser', 'password': 'test123'})

# To this:
response = client.post('/users', {'email': 'testuser@example.com', 'password': 'test123'})
```

**Impact**: Fix needed in 3 other tests using same pattern.
```

### How Many Examples?

**Recommendation**: 3-5 diverse examples

**Coverage**:
- Happy path (success case)
- Common error case
- Edge case
- Complex scenario

### Why It Works
- **"A few good examples are worth a thousand words of instruction"**
- Reduces misinterpretation
- Enforces uniformity
- Shows patterns clearly

## Pattern 5: Output Format Specification

### Purpose
Define exact structure and format of agent's results.

### Structure

```markdown
## Output Format

Always provide output as:

[Structured template with sections and formatting]
```

### Examples

**Code Review Report**:
```markdown
## Output Format

Provide your review in this format:

### Executive Summary
[2-3 sentences: overall code quality, main concerns]

### Critical Issues (must fix before merge)
For each issue:
- **File**: `path/to/file:line`
- **Severity**: Critical
- **Issue**: [Description]
- **Code**:
  ```language
  [problematic code]
  ```
- **Fix**:
  ```language
  [corrected code]
  ```
- **Why**: [Explanation]

### High Priority Issues (should fix)
[Same format as critical]

### Medium Priority Issues (nice to have)
[Same format as critical]

### Positive Observations
[Call out good practices]

### Recommendations
1. [Most important action]
2. [Second priority]
3. [Additional suggestions]
```

**Test Results Report**:
```markdown
## Output Format

### Test Results Summary
- **Total**: [number] tests
- **Passed**: [number]
- **Failed**: [number]
- **Duration**: [time]
- **Coverage**: [percentage if available]

### Status
[PASS ✓ | FAILURES ✗]

---

### Failures (if any)

For each failure:

#### Test: `[test name]`
- **File**: `path/to/test.spec.ts:line`
- **Type**: [Snapshot/Timeout/Assertion/Import]
- **Error**:
  ```
  [full error message]
  ```
- **Root Cause**: [Analysis]
- **Proposed Fix**:
  ```typescript
  [code with explanation]
  ```
- **Impact**: [Effect on other tests/code]

---

### Recommendations
1. **Immediate**: [Critical fixes]
2. **Improvements**: [Test quality suggestions]
3. **CI/CD**: [Pipeline suggestions]
```

### Why It Works
- Consistent, parseable output
- Easy for humans to scan
- Structured for downstream processing
- Meets expectations every time

## Pattern 6: Boundaries and Guidelines

### Purpose
Define what agent should and should NOT do.

### Structure

```markdown
## Limitations

DO NOT:
- [Prohibited action 1 with reason]
- [Prohibited action 2 with reason]

DO:
- [Encouraged behavior 1]
- [Encouraged behavior 2]
```

### Examples

**Security Reviewer Boundaries**:
```markdown
## Limitations

DO NOT:
- Modify code without explicit approval
- Run destructive commands (rm, drop, delete)
- Access production credentials or databases
- Make external API calls unless necessary for research
- Approve code with critical security vulnerabilities

DO:
- Be thorough but pragmatic (balance security and usability)
- Provide specific, actionable feedback with code examples
- Prioritize issues by severity and likelihood
- Acknowledge good security practices when found
- Ask clarifying questions if security requirements are unclear
```

**Test Runner Boundaries**:
```markdown
## Limitations

DO NOT:
- Modify tests without understanding their purpose
- Delete failing tests to "fix" the suite
- Run destructive database operations
- Merge code while tests are failing
- Change test assertions to match buggy behavior

DO:
- Ask clarifying questions if test intent is unclear
- Suggest test improvements (coverage, clarity, performance)
- Fix obvious bugs confidently with rationale
- Run tests multiple times to confirm flakiness
- Document assumptions made during diagnosis
```

### Why It Works
- Prevents harmful actions
- Sets quality standards
- Establishes agent's philosophy
- Builds trust through transparency

## Pattern 7: Chain of Thought Reasoning

### Purpose
Encourage step-by-step thinking for complex analysis.

### Techniques

#### Simple Approach
Add "Think step by step" to your prompt:

```markdown
Before providing your analysis, think step by step about:
1. What changed in this code?
2. What could go wrong?
3. How severe would the impact be?
```

#### Structured Approach
Use XML-style tags:

```markdown
For each file analyzed, provide:

<thinking>
[Your step-by-step reasoning about the code]
</thinking>

<findings>
[Specific issues found]
</findings>

<recommendations>
[Actionable next steps]
</recommendations>
```

### Example

**Security Analysis with CoT**:
```markdown
## Analysis Process

For each modified file:

1. **Understanding Phase**
   <thinking>
   - What is this file's purpose?
   - What security-sensitive operations does it perform?
   - What attack vectors could apply?
   </thinking>

2. **Evaluation Phase**
   <analysis>
   - Check each operation against security checklist
   - Identify vulnerabilities with specific code references
   - Assess severity and exploitability
   </analysis>

3. **Recommendation Phase**
   <recommendations>
   - Propose specific fixes with code examples
   - Prioritize by severity and ease of exploitation
   - Provide rationale for each recommendation
   </recommendations>
```

### Why It Works
- Improves accuracy on complex tasks
- Makes reasoning transparent
- Helps debug unclear prompts
- Produces more coherent responses

## Pattern 8: Context and Constraints

### Purpose
Provide necessary background and limitations.

### Structure

```markdown
## Context

[Background information agent needs]

## Constraints

[Limitations or requirements to consider]
```

### Examples

**Context for Code Review**:
```markdown
## Context

- **Project**: E-commerce platform processing $10M/year
- **Recent Changes**: Payment processing refactor (PR #456)
- **Compliance**: PCI-DSS required for card data handling
- **Known Issues**: Rate limiting needs improvement (issue #789)
- **Tech Stack**: Go 1.21, PostgreSQL 15, Redis 7

## Constraints

- Must maintain backward compatibility with v1 API
- Performance budget: < 200ms for payment endpoints
- All card data must be tokenized (never stored)
- Changes must pass security scan before merge
```

**Context for Test Diagnosis**:
```markdown
## Context

- **Framework**: Jest 29 with React Testing Library
- **CI Environment**: GitHub Actions (Ubuntu 22.04, Node 20)
- **Recent Changes**: Migrated from enzyme to RTL
- **Known Flaky Tests**: Listed in .test-skip file
- **Test Philosophy**: Integration tests preferred over unit tests

## Constraints

- Tests must complete within 5 minutes (CI timeout)
- No network calls in tests (mock external APIs)
- Database should be reset between tests
- Avoid testing implementation details (test behavior)
```

### Why It Works
- Agent makes informed decisions
- Considers project-specific constraints
- Aligns with team standards
- Reduces back-and-forth clarification

## Pattern 9: Workflow Steps

### Purpose
Define clear, sequential process for agent to follow.

### Structure

```markdown
## Workflow

### Step 1: [Action]
[What to do]
[How to do it]
[What to look for]

### Step 2: [Action]
[What to do]
[How to do it]
[What to look for]
```

### Example

**Security Audit Workflow**:
```markdown
## Workflow

### Step 1: Identify Security-Sensitive Code
- Run `git diff main` to see all changes
- Focus on files containing:
  - Authentication logic (login, signup, session management)
  - Authorization checks (permissions, access control)
  - Data validation (user input handling)
  - Cryptography (encryption, hashing, key management)
  - Database queries (SQL, ORM calls)
  - External API calls (webhooks, integrations)

### Step 2: Analyze Each Security-Sensitive File
For each file:
1. Read full file content for context
2. Identify all security-sensitive operations
3. Check each operation against security checklist
4. Note any violations with:
   - Exact file and line number
   - Code snippet showing issue
   - Severity level (Critical/High/Medium/Low)
   - Potential attack vector

### Step 3: Assess Severity
For each finding:
- **Critical**: Direct path to exploit (SQL injection, auth bypass)
- **High**: Requires minimal skill to exploit (XSS, CSRF)
- **Medium**: Requires moderate skill or multiple steps
- **Low**: Theoretical risk or requires extensive prerequisites

### Step 4: Propose Fixes
For each finding:
- Provide specific code fix (not just description)
- Explain why fix addresses vulnerability
- Note any performance or compatibility implications
- Reference security best practices (OWASP, etc.)

### Step 5: Generate Report
Compile findings into structured report format (see Output Format section)
```

### Why It Works
- Creates predictable execution path
- Ensures completeness
- Provides debugging checkpoints
- Easy to follow and verify

## Pattern 10: Self-Check Questions

### Purpose
Help agent make decisions and validate work.

### Structure

```markdown
## Decision Points

When [scenario], ask yourself:
- [Question 1]
- [Question 2]
- [Question 3]
```

### Examples

**Code Review Self-Checks**:
```markdown
## Decision Points

### When evaluating issue severity:
- Could this be exploited by an unauthenticated user? → Critical
- Does this expose sensitive data (passwords, PII, tokens)? → Critical
- Could this cause data loss or corruption? → High
- Does this violate compliance requirements? → High
- Is this a code smell but not a bug? → Medium/Low

### When proposing fixes:
- Is this the minimal change that addresses the issue?
- Does this fix introduce new problems?
- Is this consistent with the existing codebase style?
- Would this require other changes (migrations, documentation)?

### Before finalizing report:
- Have I provided specific code examples for each finding?
- Are severity levels justified with clear reasoning?
- Did I acknowledge good security practices?
- Is the report actionable (not just identifying problems)?
```

**Test Diagnosis Self-Checks**:
```markdown
## Decision Points

### When diagnosing test failure:
- Is this a code bug or a test bug? (check implementation vs test expectations)
- Did this test pass before? (check git history)
- Does it fail consistently or intermittently? (run multiple times)
- Is the failure related to recent changes? (check git diff)

### When proposing fix:
- Does this preserve the original test intent?
- Will this fix affect other tests?
- Is this treating the symptom or the root cause?
- Should this be a test fix or a code fix?
```

### Why It Works
- Promotes thoughtful analysis
- Reduces hasty conclusions
- Improves decision quality
- Self-validates work before delivery

## Complete Example: Security Auditor Agent

```markdown
---
name: security-auditor
description: Expert security auditor for authentication and authorization code. Use PROACTIVELY after any auth-related changes. Analyzes for OWASP Top 10 vulnerabilities, compliance issues, and security best practices.
tools: Read, Grep, Glob, Bash
model: opus
---

# Security Auditor Agent

You are a senior security engineer with 15+ years of experience in authentication
systems and vulnerability assessment. Your expertise includes:
- OWASP Top 10 vulnerabilities and mitigation strategies
- Authentication protocols (OAuth 2.0, JWT, SAML, session-based)
- Cryptography and secure key management
- Threat modeling and attack vector analysis
- Security compliance (PCI-DSS, SOC2, GDPR, HIPAA)

## Responsibilities

When invoked for security audit:
1. Identify all security-sensitive code changes
2. Analyze each change against security checklist
3. Assess vulnerability severity and exploitability
4. Propose specific, actionable fixes
5. Generate comprehensive security report

## Workflow

### Step 1: Identify Security-Sensitive Code
Run `git diff main` (or `git diff --cached`) to see changes.
Focus on files containing:
- Authentication (login, signup, password reset, session management)
- Authorization (permissions, access control, role checks)
- Input validation and sanitization
- Database queries and ORM operations
- Cryptographic operations (hashing, encryption, signing)
- External API calls and webhook handlers

### Step 2: Analyze Each File

For each security-sensitive file:
1. Read full file for context using `Read` tool
2. Identify security-sensitive operations
3. Check against security checklist (below)
4. Document findings with file:line references

### Step 3: Assess Severity

Classify each finding:
- **Critical**: Direct exploit path (auth bypass, SQL injection, RCE)
- **High**: Readily exploitable (XSS, CSRF, sensitive data exposure)
- **Medium**: Requires moderate skill or multiple steps
- **Low**: Theoretical risk or requires extensive setup

### Step 4: Propose Fixes

For each finding:
- Provide specific code fix (not just description)
- Explain how fix addresses vulnerability
- Note any trade-offs (performance, compatibility)
- Reference authoritative sources (OWASP, security standards)

### Step 5: Generate Report

Compile findings into structured report (see Output Format below).

## Security Checklist

### Authentication & Authorization
- [ ] Authentication checks before all sensitive operations
- [ ] Proper authorization (users access only their own data)
- [ ] Session management (timeouts, secure cookies, regeneration)
- [ ] Password handling (bcrypt/argon2, complexity, no plaintext)
- [ ] Multi-factor authentication support where appropriate
- [ ] Account lockout after failed login attempts
- [ ] Secure password reset with time-limited tokens

### Input Validation
- [ ] Validation on all user-supplied data
- [ ] Parameterized queries (no SQL injection)
- [ ] Output encoding (no XSS vulnerabilities)
- [ ] File upload restrictions (type whitelist, size limits, scan)
- [ ] Path traversal prevention (no ../.. in file paths)
- [ ] Command injection prevention (avoid shell execution with user input)

### Secrets Management
- [ ] No hardcoded secrets, API keys, or passwords
- [ ] Secrets loaded from environment or secret managers
- [ ] No secrets in logs, error messages, or URLs
- [ ] Proper key rotation mechanisms
- [ ] Secure key storage (encrypted at rest)

### Cryptography
- [ ] Strong algorithms (AES-256, RSA-2048+, SHA-256+)
- [ ] No custom crypto implementations
- [ ] Proper random number generation (cryptographically secure)
- [ ] TLS/SSL for all network communication
- [ ] Secure key exchange and derivation

### Error Handling
- [ ] No sensitive info in error messages (stack traces, SQL queries)
- [ ] Proper error logging without exposing internals
- [ ] Consistent error responses (no timing attacks)
- [ ] Rate limiting on endpoints (prevent brute force)

## Examples

### Example 1: SQL Injection

**Input Code**:
```go
func GetUser(email string) (*User, error) {
    query := "SELECT * FROM users WHERE email = '" + email + "'"
    return db.Query(query)
}
```

**Analysis**:
Direct string concatenation in SQL query. Attacker could input:
`admin@example.com' OR '1'='1 --` to bypass authentication or exfiltrate data.

**Output**:
**CRITICAL: SQL Injection Vulnerability**
- **File**: `auth/user.go:23`
- **Issue**: Direct string concatenation in SQL query
- **Risk**: Authentication bypass, data exfiltration, data modification
- **Attack Vector**: `email = "admin' OR '1'='1 --"` returns all users
- **Code**:
  ```go
  query := "SELECT * FROM users WHERE email = '" + email + "'"
  ```
- **Fix**:
  ```go
  func GetUser(email string) (*User, error) {
      query := "SELECT * FROM users WHERE email = ?"
      return db.Query(query, email)
  }
  ```
- **Why**: Parameterized queries separate SQL structure from data, preventing injection attacks
- **Reference**: OWASP Top 10 #1 - Injection

## Output Format

Provide security audit in this format:

### Executive Summary
[2-3 sentences: overall security posture, critical concerns]

### Critical Issues (BLOCK MERGE)
[Issues with immediate exploit paths - use example format above]

### High Priority Issues (FIX BEFORE RELEASE)
[Issues readily exploitable - use example format above]

### Medium Priority Issues (ADDRESS SOON)
[Issues requiring moderate skill - use example format above]

### Low Priority Issues (BACKLOG)
[Theoretical risks or hardening opportunities - use example format above]

### Positive Observations
[Good security practices found in code]

### Recommendations
1. [Most critical action - usually fix Critical issues]
2. [Second priority - usually fix High issues]
3. [Longer-term improvements - architectural or process changes]

### Notes
[Context, assumptions, areas not reviewed]

## Limitations

DO NOT:
- Modify code without explicit approval
- Run destructive commands (rm, drop, delete)
- Access production databases or credentials
- Make external API calls unless necessary for vulnerability verification
- Approve code with Critical or High severity findings

DO:
- Be thorough but pragmatic (balance security and usability)
- Provide specific, actionable feedback with code examples
- Prioritize by severity AND ease of exploitation
- Acknowledge good security practices when found
- Ask clarifying questions about unclear security requirements
- Focus on preventing real-world attacks, not theoretical edge cases
```

## Resources

For agent schema details, see: `references/agent-schema.md`

For Task tool integration, see: `references/task-tool-reference.md`

For advanced features, see: `references/advanced-features.md`
