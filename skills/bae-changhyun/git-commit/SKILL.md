---
name: git-commit
description: MUST use this skill when user asks to commit, create commit, save work, or mentions "커밋". This skill OVERRIDES default git commit behavior. Creates commits following Conventional Commits format with emoji + type/scope/subject (✨ feat, 🐛 fix, ♻️ refactor, etc).
---

# Git Commit Guide

Creates commits using the Conventional Commits format with type, scope, and subject components.

## Quick Start

```bash
# 1. Check project conventions
cat CLAUDE.md 2>/dev/null | head -30

# 2. Review staged changes
git diff --staged --stat
git diff --staged

# 3. Stage files if needed
git add <files>

# 4. Create commit with emoji
git commit -m "✨ feat(scope): add new feature"
```

## Commit Structure

Format: `emoji type(scope): subject`

| Component | Description | Example |
|-----------|-------------|---------|
| **emoji** | Visual indicator | ✨, 🐛, ♻️ |
| **type** | Change category | `feat`, `fix`, `refactor` |
| **scope** | Affected area (kebab-case) | `auth`, `api-client` |
| **subject** | What changed (imperative mood) | `add login validation` |

**Rules:**
- First line ≤ 72 characters
- Use imperative mood ("add", not "added" or "adding")
- No period at end

## Commit Types with Emoji

### Core Types

| Emoji | Type | Purpose |
|-------|------|---------|
| ✨ | `feat` | New feature |
| 🐛 | `fix` | Bug fix |
| 📝 | `docs` | Documentation |
| 💄 | `style` | Formatting/style (no logic change) |
| ♻️ | `refactor` | Code refactoring |
| ⚡️ | `perf` | Performance improvement |
| ✅ | `test` | Add/update tests |
| 🔧 | `chore` | Tooling, config |
| 🚀 | `ci` | CI/CD improvements |
| ⏪️ | `revert` | Revert changes |

### Detailed Types

**Features (feat):**
| Emoji | Usage |
|-------|-------|
| 🧵 | Multithreading/concurrency |
| 🔍️ | SEO improvements |
| 🏷️ | Add/update types |
| 💬 | Text and literals |
| 🌐 | Internationalization/localization |
| 👔 | Business logic |
| 📱 | Responsive design |
| 🚸 | UX/usability improvements |
| 📈 | Analytics/tracking |
| 🚩 | Feature flags |
| 💫 | Animations/transitions |
| ♿️ | Accessibility |
| 🦺 | Validation |
| 🔊 | Add/update logs |
| 🥚 | Easter eggs |
| 💥 | Breaking changes |
| ✈️ | Offline support |

**Fixes (fix):**
| Emoji | Usage |
|-------|-------|
| 🚨 | Compiler/linter warnings |
| 🔒️ | Security issues |
| 🩹 | Simple fix for non-critical issue |
| 🥅 | Catch errors |
| 👽️ | External API changes |
| 🔥 | Remove code/files |
| 🚑️ | Critical hotfix |
| ✏️ | Typos |
| 💚 | CI build |
| 🔇 | Remove logs |

**Refactor:**
| Emoji | Usage |
|-------|-------|
| 🚚 | Move/rename resources |
| 🏗️ | Architectural changes |
| 🎨 | Improve structure/format |
| ⚰️ | Remove dead code |

**Chore:**
| Emoji | Usage |
|-------|-------|
| 👥 | Add/update contributors |
| 🔀 | Merge branches |
| 📦️ | Compiled files/packages |
| ➕ | Add dependency |
| ➖ | Remove dependency |
| 🌱 | Seed files |
| 🧑‍💻 | Developer experience |
| 🙈 | .gitignore |
| 📌 | Pin dependencies |
| 👷 | CI build system |
| 📄 | License |
| 🎉 | Begin project |
| 🔖 | Release/version tags |
| 🚧 | Work in progress |

**Database/Assets:**
| Emoji | Usage |
|-------|-------|
| 🗃️ | Database changes |
| 🍱 | Assets |

**Test:**
| Emoji | Usage |
|-------|-------|
| 🧪 | Add failing test |
| 🤡 | Mock things |
| 📸 | Snapshots |
| ⚗️ | Experiments |

## Commit Scope (Task/Request Unit)

**MUST FOLLOW:** Default to **one commit per task/request**, not per file and not per work unit.

- **Principle:** When the user asks for one thing, the result is normally **one commit**, even if it touched many files or went through several internal steps. If you modified `main.py`, `utils.py`, `config.yaml` to deliver the request, these **MUST be in a single commit**.
- **Combine when in doubt.** A clean log of a few meaningful commits beats many micro-commits.
- **Split only for genuinely unrelated concerns** (e.g. an unrelated bugfix landed alongside the feature) — and even then aim for 2–3 commits max, never one-per-file.
- **Reason:** When reverting to a specific commit, that delivered request should work completely.

**❌ Bad Example** (파일별로 분리 커밋 - 기능 단위가 아님)
```bash
git add search.py
git commit -m "✨ feat: create search module"
git add api.py
git commit -m "🐛 fix: fix api connection"
```

**✅ Good Example**
```bash
git add search.py api.py
git commit -m "✨ feat(search): implement keyword search with API endpoint"
```

## Result-Oriented Messages

**MUST FOLLOW:** Do not write conversation history (process). Write only the **final code changes (result)**.

Even if there were 10 modifications during development (error fixes, typo fixes, etc.), the commit message should only state the finally implemented feature.

| ❌ Bad (Process) | ✅ Good (Result) |
|------------------|------------------|
| "Fixed typo, fixed A function error, added library to implement login" | `✨ feat(auth): implement JWT-based login` |
| "fix api connection and variable name errors and import errors" | `✨ feat(search): implement keyword search` |

## Core Workflow

### 1. Check Project Conventions

```bash
cat CLAUDE.md 2>/dev/null | head -30
```

Always check for project-specific commit rules.

### 2. Review Staged Changes

```bash
git diff --staged --stat
git diff --staged
```

Understand what's being committed.

### 3. Analyze Changes

Identify:
- Primary type (feat > fix > refactor)
- Scope (module/component affected)
- Summary (what changed, in imperative mood)

### 4. Create Commit

```bash
git commit -m "emoji type(scope): subject"
# Example: git commit -m "✨ feat(auth): add login validation"
```

### 5. Add Body (if needed)

For complex changes:

```bash
git commit -m "$(cat <<'EOF'
✨ feat(scope): subject

Body explaining WHY and HOW.
Wrap at 72 characters.

Refs: #123
EOF
)"
```

## Breaking Changes

Add exclamation mark (!) after type/scope for breaking changes:

```bash
git commit -m "💥 feat(api)!: change response format"
```

Or use footer:

```bash
git commit -m "$(cat <<'EOF'
💥 feat(api): change response format

BREAKING CHANGE: Response now returns array instead of object.
EOF
)"
```

## Subject Line Rules

- **DO**: Use imperative mood ("add", "fix", "change")
- **DO**: Keep under 50 characters
- **DO**: Start lowercase after colon
- **DON'T**: End with period
- **DON'T**: Use vague words ("update", "improve", "change stuff")

## Review Fix Commits

When addressing PR review comments:

```bash
git commit -m "$(cat <<'EOF'
🐛 fix(scope): address review comment #ID

Brief explanation of what was wrong and how it's fixed.
Addresses review comment #123456789.
EOF
)"
```

## Commit Split Guidelines

**Default is NOT to split.** One task/request → one commit (see "Commit Scope" above). Do **not** split by change-type, file-pattern, or "easier to review" — that produces over-splitting (20+ commits/day) and is explicitly discouraged.

Split into a SEPARATE commit **only** when genuinely **unrelated concerns** ended up mixed in one batch — e.g. an unrelated bugfix or dependency bump landed alongside the requested feature. Even then aim for **2–3 commits max**, never one-per-file and never one-per-change-type.

**Example — keep together (DON'T over-split):** a feature plus its docs, types, tests, and the lint fixes it required are **all one commit** — they deliver a single request.

```
✨ feat(solc): add new solc version support with types, docs, and tests
```

Only carve out a second commit if something truly unrelated rode along:

```
1st: ✨ feat(solc): add new solc version support with types, docs, and tests
2nd: 🔒️ fix(deps): patch unrelated security vulnerability in lockfile
```

## Pre-Commit Checklist

Before creating a commit, ask yourself:

1. **Are all related files included?** (Are all dependency files modified for the feature `git add`ed?)
2. **Is the message clean?** (Does it contain only the core implementation without repetitive "fix", "modify"?)
3. **Is it the diff from previous commit?** (Did you summarize `git diff` content, not conversation log?)

## Good Commit Examples

```
✨ feat: add user authentication system
🐛 fix: resolve memory leak in rendering process
📝 docs: update API documentation with new endpoints
♻️ refactor: simplify error handling logic in parser
🚨 fix: resolve linter warnings in component files
🧑‍💻 chore: improve developer tools setup process
👔 feat: implement business logic for transaction validation
🩹 fix: resolve minor style inconsistency in header
🚑️ fix: patch critical security vulnerability in auth flow
🎨 style: restructure component for better readability
🔥 fix: remove deprecated legacy code
🦺 feat: add input validation for user registration form
💚 fix: resolve CI pipeline test failures
📈 feat: implement tracking for user engagement analytics
🔒️ fix: strengthen authentication password requirements
♿️ feat: improve form accessibility for screen readers
```

## Language Rule

**MUST FOLLOW:** The commit message language should match the repository's existing commit history.

Before writing a commit message:
1. Run `git log --oneline -5` to check recent commit messages
2. Use the same language as the existing commits
3. If commits are in Korean, write in Korean. If in English, write in English.

```bash
# Check recent commit language
git log --oneline -5
```

**Examples:**
- If recent commits are `"✨ feat: 로그인 기능 추가"` → Write in Korean
- If recent commits are `"✨ feat: add login feature"` → Write in English

## Important Rules

- **ALWAYS** check recent commit history to determine commit message language
- **ALWAYS** check project conventions (CLAUDE.md) before committing
- **ALWAYS** review staged changes before committing
- **ALWAYS** commit per task/request (one commit), not per file or per change-type; combine when in doubt
- **ALWAYS** set local git email by remote host before committing: GitLab/`gcsc.co.kr` → `chbae@gcsc.co.kr`, `github.com` → `chbae624@gmail.com` (only if it doesn't already match)
- **ALWAYS** write result-oriented messages (final changes only)
- **ALWAYS** use imperative mood in subject ("add", not "added")
- **ALWAYS** include appropriate emoji at the start
- **ALWAYS** keep first line ≤ 72 characters
- **ALWAYS** use HEREDOC for multi-line messages
- **NEVER** stage secrets, credentials, or large binaries
- **NEVER** use vague subjects ("fix bug", "update code")
- **NEVER** list process steps in commit message
- **NEVER** end subject with period
