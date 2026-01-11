---
name: code-review
description: This skill should be used when the user requests a code review of changed files. Use this to review git-diffed files for security vulnerabilities (OWASP Top 10), performance issues (O(N) complexity, ORM optimization), bugs, and adherence to project coding standards defined in agents.md and claude.md.
---

# Code Review Skill

## Purpose

Perform comprehensive code reviews on files that have been modified in the current git working directory. Review code for:
- Security vulnerabilities (OWASP Top 10)
- Performance issues (algorithmic complexity, ORM N+1 queries)
- Logic bugs and unintended behavior
- Adherence to project coding standards
- Code quality and maintainability

## When to Use

Invoke this skill when:
- User explicitly requests code review
- User asks to review changes before committing
- User wants feedback on modified files
- User mentions checking for bugs, security issues, or performance problems

## Code Review Process

### Step 1: Identify Changed Files

Use git plumbing commands to get a list of files that have been modified:

```bash
# Get all files with uncommitted changes (staged and unstaged)
git diff --name-only HEAD

# Alternative: Get only staged files
git diff --cached --name-only

# Alternative: Get files changed in recent commits
git diff --name-only HEAD~1..HEAD
```

Store the list of changed files for systematic review.

### Step 2: Read Project Standards

Before reviewing code, load the project's coding standards to understand expectations:

- **Python/Backend code**: Read `/Users/daviddworetzky/Documents/repos/Geist/docs/agents.md` for agent architecture patterns and best practices
- **General standards**: Read `/Users/daviddworetzky/Documents/repos/Geist/claude.md` (or `CLAUDE.md`) for SQLAlchemy patterns, dependency preferences, SDLC process, and general coding preferences

Key standards to check:
- SQLAlchemy models should follow the pattern in claude.md (proper imports, Base inheritance, relationships)
- Prefer minimal inline implementations over extra dependency imports
- Core libraries are better than PyPI packages
- Models must be added to `scripts/copy_weights.py`
- Classes should inherit from appropriate base classes (e.g., `BaseAgent`)
- Database models should be in `app/models/database/`

### Step 3: Review Each File Systematically

For each changed file, perform the following checks:

#### Security Review (OWASP Top 10)

Check for common security vulnerabilities:

1. **Injection Flaws** (SQL, Command, LDAP, etc.)
   - Look for string concatenation in SQL queries
   - Check for unsanitized user input in shell commands
   - Verify parameterized queries are used with SQLAlchemy

2. **Broken Authentication**
   - Check for weak password validation
   - Verify proper session management
   - Look for exposed credentials or API keys

3. **Sensitive Data Exposure**
   - Check for unencrypted sensitive data storage
   - Verify HTTPS/TLS usage for data transmission
   - Look for logging of sensitive information

4. **XML External Entities (XXE)**
   - Check XML parsing for external entity processing
   - Verify XML parsers are configured securely

5. **Broken Access Control**
   - Check for missing authorization checks
   - Verify proper user permission validation
   - Look for insecure direct object references

6. **Security Misconfiguration**
   - Check for default credentials
   - Verify error messages don't expose sensitive info
   - Look for overly permissive CORS settings

7. **Cross-Site Scripting (XSS)**
   - Check for unescaped user input in templates
   - Verify proper output encoding
   - Look for dangerous innerHTML usage

8. **Insecure Deserialization**
   - Check for pickle/eval usage with untrusted data
   - Verify proper input validation

9. **Using Components with Known Vulnerabilities**
   - Check for outdated dependencies
   - Verify no known vulnerable libraries

10. **Insufficient Logging & Monitoring**
    - Check for proper error logging
    - Verify security events are logged

#### Performance Review

Check for performance issues:

1. **Algorithmic Complexity**
   - Look for nested loops that could be O(N²) or worse
   - Check for repeated calculations that could be cached
   - Verify efficient data structure usage

2. **ORM Optimization**
   - Check for N+1 query problems (missing eager loading)
   - Look for queries inside loops
   - Verify proper use of `joinedload()` or `selectinload()`
   - Check for loading entire tables when only a few fields needed
   - Verify proper indexing on foreign keys

3. **Database Issues**
   - Look for missing indexes on frequently queried columns
   - Check for inefficient WHERE clauses
   - Verify proper transaction boundaries

4. **Memory Issues**
   - Check for memory leaks (unclosed files, connections)
   - Look for loading large datasets into memory
   - Verify generators are used for large iterations

#### Logic and Bug Review

Check for logical errors:

1. **Type Safety**
   - Verify proper type handling
   - Check for None/null handling
   - Look for type coercion issues

2. **Error Handling**
   - Verify proper exception handling
   - Check for caught-but-ignored exceptions
   - Look for overly broad exception catches

3. **Business Logic**
   - Verify code matches intended behavior
   - Check for off-by-one errors
   - Look for race conditions or concurrency issues
   - Verify proper state management

4. **Edge Cases**
   - Check for empty list/array handling
   - Verify boundary condition handling
   - Look for division by zero possibilities

#### Project Standards Review

Verify adherence to project standards based on file type:

**Python Files:**
- Imports follow the pattern in claude.md
- SQLAlchemy models inherit from Base
- Proper use of relationships and foreign keys
- Models are in correct directory (`app/models/database/`)
- Agent classes inherit from `BaseAgent` or appropriate base class
- Minimal dependencies, prefer core libraries

**General:**
- Code follows existing patterns in the codebase
- Proper documentation and docstrings
- Consistent naming conventions
- Appropriate separation of concerns

### Step 4: Categorize and Report Issues

Categorize issues into severity levels:

**Critical (Fix Immediately):**
- Security vulnerabilities that could lead to data breach or system compromise
- Logic bugs that would cause data corruption or system failure
- Performance issues that would cause severe degradation (e.g., O(N³) in hot path)
- ORM issues causing catastrophic N+1 queries
- Moderate security issues (information disclosure, weak validation)
- Significant performance problems (O(N²) where N could be large)
- Logic bugs that affect core functionality
- Violations of critical project standards

**Recommended (Prompt for Approval):**
- Minor performance improvements
- Code style issues
- Non-critical standard violations
- Suggestions for better maintainability

### Step 5: Take Action

**For Critical and Important Issues:**
1. Fix the issue immediately
2. Explain what was wrong and why it was fixed
3. Show the before/after code
4. Reference relevant standards or security principles

**For Recommended Issues:**
1. List the issues clearly
2. Explain the potential benefit of fixing
3. Ask user if they want these fixed
4. Let user decide priority

## Example Review Output

When presenting findings, use this format:

```
## Code Review Results

### Files Reviewed
- app/services/user_service.py
- app/models/database/user.py

### Critical Issues Fixed

#### 1. SQL Injection in user_service.py:42
**Issue:** Raw string concatenation in SQL query allows SQL injection
**Before:**
```python
query = f"SELECT * FROM users WHERE email = '{email}'"
```
**After:**
```python
query = session.query(User).filter(User.email == email)
```
**Why:** Parameterized queries prevent SQL injection attacks (OWASP #1)

#### 2. N+1 Query in user_service.py:78
**Issue:** Loading related data in loop causes N+1 queries
**Before:**
```python
for user in users:
    posts = user.posts  # Lazy load triggers query
```
**After:**
```python
users = session.query(User).options(joinedload(User.posts)).all()
for user in users:
    posts = user.posts  # Already loaded
```
**Why:** Reduces database round trips from N+1 to 1 query

### Recommended Improvements

#### 1. Import Optimization (user_service.py:1)
- Consider using built-in `datetime` instead of `arrow` library
- Aligns with project preference for core libraries over PyPI packages
- Would you like me to refactor this?

#### 2. Code Style (user.py:15)
- Consider adding docstring to `User` class
- Would improve code documentation
- Should I add this?
```

## Tips for Effective Reviews

1. **Be Thorough**: Check every changed line, not just the obvious parts
2. **Context Matters**: Understand the purpose of the code before critiquing
3. **Prioritize Severity**: Fix security and correctness issues before style
4. **Explain Reasoning**: Always explain why something is a problem
5. **Provide Solutions**: Don't just identify issues, show how to fix them
6. **Respect Intent**: Understand what the developer was trying to achieve
7. **Check Imports**: Verify all necessary imports are present after fixes
8. **Test Compatibility**: Ensure fixes don't break existing functionality
