---
name: ddd-check-incremental
description: Incremental DDD compliance check — scans only changed/new Java files in git diff and validates against DDD layer rules. Use before every commit.
model: claude-sonnet-4-20250514
allowed-tools: Read, Grep, Glob, Bash
user-invocable: true
---

# DDD Incremental Compliance Check

Check only **new or modified** Java files against DDD layer rules. Fast, pre-commit focused.

## Trigger

Run when user says "check my changes", "DDD check", "review this code", or before committing.

## Workflow

### Step 1: Find Changed Files

```bash
# Staged changes (pre-commit)
git diff --cached --name-only --diff-filter=ACMR | grep '\.java$'

# Unstaged changes (working tree)
git diff --name-only --diff-filter=ACMR | grep '\.java$'

# Both
git diff HEAD --name-only --diff-filter=ACMR | grep '\.java$'
```

If no Java files changed, report: "No Java files changed — nothing to check."

### Step 2: Classify Each File by Layer

Map file path to DDD layer:

| Package Pattern | Layer | Rule File |
|---|---|---|
| `**/ddd/common/**` | Common | (structural rules only) |
| `**/ddd/domain/**` | Domain | `rules/domain-layer.md` |
| `**/ddd/application/**` | Application | `rules/application-layer.md` |
| `**/ddd/adaptor/**` | Adaptor | `rules/adaptor-layer.md` |
| `**/ddd/infrastructure/**` | Infrastructure | `rules/infrastructure-layer.md` |
| `**/ddd/client/**` | Client | `rules/client-layer.md` |
| `**/ddd/model/**` | Model | `rules/model-layer.md` |

### Step 3: Read Relevant Rule Files

Load only the rule files matching the changed layers. Plus always load `rules/anti-patterns.md`.

### Step 4: Check Each Changed File

For each changed file, read it and validate against:

1. **Structural rules** — correct base class, correct package, correct naming
2. **Dependency rules** — no forbidden imports (e.g. domain must not import infrastructure)
3. **Anti-patterns** — cross-check against `rules/anti-patterns.md`

### Step 5: Report

Format output as:

```
## DDD Check: {branch} → {n} files changed

### {FilePath}.java — {Layer}
🔴 CRITICAL: {problem}. {fix}.
🟡 HIGH: {problem}. {fix}.

### Summary
- {n} files checked
- {x} violations (C: {a}, H: {b}, M: {c}, L: {d})
```

## Severity

| Level | Criteria |
|---|---|
| **CRITICAL** | Architecture violation — wrong layer dependency, missing base class, domain depends on infrastructure |
| **HIGH** | Rule violation — wrong naming, public setter on aggregate, wrong exception mode |
| **MEDIUM** | Convention deviation — missing JavaDoc, wrong file location |
| **LOW** | Style suggestion |

## Key Checks

**Domain Layer (MOST CRITICAL):**
- [ ] All aggregates extend `BaseAggregate<ID>`
- [ ] All entities extend `BaseEntity<ID>`
- [ ] All value objects extend `BaseValue`
- [ ] `setId()` is `protected`, not `public`
- [ ] No infrastructure imports (no Mapper, no JPA, no SQL)
- [ ] Repository interfaces extend `AggregateRepository<T, ID, Q>`
- [ ] External calls go through `GatewayI` interfaces
- [ ] Aggregate methods = business behaviors, not CRUD
- [ ] Design patterns FORBIDDEN in domain (Strategy, Factory, etc.)
- [ ] 阻断型 throws exception, 分支型 returns ResultDO (see `references/exception-handling.md`)

**Application Layer:**
- [ ] Cmd services extend `ApplicationCmdService`
- [ ] Qry services extend `ApplicationQueryService`
- [ ] APP catches Domain/Adaptor exceptions, converts to ResultDO
- [ ] APP never throws exceptions to Adaptor

**Infrastructure Layer:**
- [ ] Repository impls in correct package
- [ ] PO classes separate from domain objects
- [ ] Converter/Assembler between PO and domain
- [ ] All GatewayI implementations here, not in domain

**Client Layer:**
- [ ] All DTOs extend `BaseDTO`
- [ ] No domain classes exposed in DTOs

## Important

- Do NOT check unchanged files — incremental only
- Reference the specific rule section when flagging violations (e.g. "rules/domain-layer.md Section A.3")
- Suggest the exact fix, not just the problem
- If a violation is intentional, note it but don't flag as CRITICAL
- Only report real problems — don't report "looks good" for files with zero issues
