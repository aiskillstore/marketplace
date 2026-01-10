---
name: Documentation Fundamentals
description: Auto-invoke when reviewing README files, JSDoc comments, or inline documentation. Enforces "WHY not WHAT" principle.
---

# Documentation Fundamentals Review

> "Code tells you HOW, comments tell you WHY. If you only explain what the code does, you're wasting everyone's time."

## When to Apply

Activate this skill when:
- Reviewing or creating README files
- Writing JSDoc/docstring comments
- Inline code comments
- API documentation
- Architecture decision records

---

## The Golden Rule: WHY, Not WHAT

```typescript
// ❌ BAD: Explains what (code already says this)
// Increment counter by 1
counter++;

// ✅ GOOD: Explains why (context the code can't provide)
// Counter must be incremented before validation runs
// to account for the edge case where initial value is 0
counter++;
```

---

## README Structure (The 5 Essentials)

Every README must answer these questions:

### 1. What Is This? (1 sentence)

> "What problem does this solve in one sentence?"

```markdown
## What

A CLI tool that converts Figma designs to React components.
```

### 2. Why Does It Exist?

> "What pain point motivated this project?"

```markdown
## Why

Manually converting designs to code takes hours and introduces inconsistencies.
This tool automates the process, ensuring pixel-perfect components.
```

### 3. How to Install

> "Copy-paste instructions that work."

```markdown
## Installation

npm install your-package
```

### 4. How to Use

> "The simplest possible example that works."

```markdown
## Quick Start

npx your-tool --input design.fig --output ./components
```

### 5. How to Contribute (Optional)

> "For open source projects."

```markdown
## Contributing

1. Fork the repo
2. Create your feature branch
3. Submit a pull request
```

---

## Comment Types & When to Use Them

### Function/Method Documentation (JSDoc)

```typescript
/**
 * Validates email format and checks domain against blocklist.
 *
 * @param email - The email address to validate
 * @returns ValidationResult with success status and error message
 *
 * @example
 * const result = validateEmail('user@example.com');
 * if (!result.success) {
 *   showError(result.error);
 * }
 *
 * Note: This uses the RFC 5322 regex pattern, which is intentionally
 * strict to prevent disposable email addresses.
 */
function validateEmail(email: string): ValidationResult {
  // Implementation
}
```

### Inline Comments (Only for WHY)

```typescript
// Rate limit is 100/min but we use 80 to leave headroom for retries
const RATE_LIMIT = 80;

// Sort descending because newest items should appear first
// (business requirement from PM - see ticket #1234)
items.sort((a, b) => b.date - a.date);

// HACK: API returns dates as strings, need to parse manually
// TODO: Remove after backend migration (Q2 2026)
const date = new Date(response.dateString);
```

### Block Comments (Complex Logic)

```typescript
/*
 * Authentication Flow:
 * 1. Check local token cache
 * 2. If expired, attempt silent refresh
 * 3. If refresh fails, redirect to login
 *
 * We use refresh tokens instead of re-authentication to avoid
 * disrupting the user experience during long sessions.
 */
```

---

## Common Mistakes (Anti-Patterns)

### 1. Commenting the Obvious

```typescript
// ❌ BAD: Useless comment
// Set name to "John"
const name = "John";

// Get the user's age
const age = user.age;

// Loop through items
for (const item of items) { ... }

// ✅ GOOD: No comment needed (code is self-explanatory)
const name = "John";
```

### 2. Outdated Comments

```typescript
// ❌ BAD: Comment doesn't match code (dangerous!)
// Filter out inactive users
const users = data.filter(u => u.role === 'admin');

// ✅ GOOD: Comment matches reality
// Only show admin users in management view
const users = data.filter(u => u.role === 'admin');
```

### 3. No Context on Magic Numbers

```typescript
// ❌ BAD: What is 86400?
const expiresIn = 86400;

// ✅ GOOD: Explains the magic
const SECONDS_PER_DAY = 86400;
const expiresIn = SECONDS_PER_DAY; // Tokens expire after 24 hours
```

### 4. Commented-Out Code

```typescript
// ❌ BAD: Dead code polluting the file
// const oldImplementation = () => { ... };
// function deprecatedHelper() { ... }

// ✅ GOOD: Delete it! Git remembers everything
```

### 5. Empty README

```markdown
<!-- ❌ BAD: Auto-generated, never updated -->
# my-project

This project was bootstrapped with Create React App.
```

---

## Socratic Questions

Ask these instead of giving answers:

1. **WHY not WHAT**: "Does this comment tell me something the code doesn't?"
2. **Audience**: "Would a developer joining tomorrow understand this?"
3. **Maintenance**: "If you change the code, would you remember to update this comment?"
4. **README**: "Can someone run this project with just the README instructions?"
5. **JSDoc**: "What would a developer need to know to use this function correctly?"
6. **Necessity**: "If you delete this comment, is anything lost?"

---

## README Template

```markdown
# Project Name

One-sentence description of what this does.

## Why

The problem this solves and why it matters.

## Installation

npm install project-name

## Quick Start

Minimal code example that works.

## API

### functionName(param)

Description of what it does.

**Parameters:**
- `param` (string): What this parameter is for

**Returns:** What gets returned

**Example:**
```js
// Usage example
```

## Configuration

Available options and their defaults.

## Contributing

How to contribute (if applicable).

## License

MIT (or your license)
```

---

## JSDoc Essentials

```typescript
/**
 * Brief description of what this function does.
 *
 * @param paramName - Description of parameter
 * @returns Description of return value
 * @throws {ErrorType} When this error occurs
 * @example
 * // Show how to use it
 * const result = myFunction('input');
 *
 * @see RelatedFunction for similar functionality
 * @deprecated Use newFunction instead (v2.0+)
 */
```

---

## Red Flags to Call Out

| Flag | Question |
|------|----------|
| Empty README | "Can a new developer run this project right now?" |
| `// Set x to 5` | "Does this comment add value? The code already says this." |
| Outdated comments | "Does this comment still match what the code does?" |
| No JSDoc on exports | "How would someone know how to use this function?" |
| Commented-out code | "Why is this here? Git has history if you need it back." |
| Magic numbers | "What does 3600 mean? Why this number?" |

---

## Interview Connection

> "I maintain comprehensive documentation including READMEs, JSDoc comments, and architecture decision records, ensuring code is maintainable by the entire team."

Documentation habits demonstrate:
- Communication skills
- Long-term thinking
- Team player mentality
- Senior-level maturity

---

## MCP Usage

### Context7 - Framework Docs
```
Fetch: JSDoc documentation
Fetch: Markdown best practices
```

### Octocode - Real Examples
```
Search: README.md patterns in popular repos
Search: JSDoc examples in TypeScript projects
```
