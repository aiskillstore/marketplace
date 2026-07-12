---
name: ddd-check-full
description: Full-project DDD compliance audit — scans ALL Java files against every DDD layer rule. Use for architecture reviews, onboarding, and pre-release checks.
model: claude-sonnet-4-20250514
allowed-tools: Read, Grep, Glob, Bash
user-invocable: true
---

# DDD Full-Project Compliance Audit

Deep scan of **every** Java file against all DDD rules. Use for architecture review, refactoring assessment, or pre-release audit.

## Trigger

Run when user says "full DDD audit", "check entire project", "architecture review", or "DDD compliance report".

## Workflow

### Step 1: Discover All Java Files

```bash
find . -name "*.java" -not -path "*/target/*" -not -path "*/test/*" | sort
```

Count files and estimate: "Scanning {N} files across {M} layers..."

### Step 2: Load All Rule Files

Read EVERY rule file at `rules/`:
- `rules/domain-layer.md`
- `rules/application-layer.md`
- `rules/adaptor-layer.md`
- `rules/infrastructure-layer.md`
- `rules/client-layer.md`
- `rules/model-layer.md`
- `rules/anti-patterns.md`

Plus reference files if needed:
- `references/base-classes-reference.md`
- `references/exception-handling.md`

### Step 3: Layer-by-Layer Audit

Group files by layer. For each layer:

1. **Package check** — all files in correct package?
2. **Base class check** — all classes extend correct base?
3. **Naming check** — classes/methods follow DDD naming conventions?
4. **Dependency check** — no illegal cross-layer imports?
5. **Structural check** — aggregates, entities, value objects structured correctly?
6. **Exception mode check** — 阻断型 throws, 分支型 returns ResultDO?

### Step 4: Cross-Layer Checks

- **Dependency direction**: Run `grep -r "import org\.bookiosk\.ddd\."` on each layer, verify no reverse dependencies
- **Missing patterns**: Are there layers with zero classes? Missing base classes?
- **Anemic model detection**: Any domain class with only getters/setters and no behavior methods?
- **Exception boundary**: Is APP catching Domain/Adaptor exceptions? Is any layer throwing across boundaries?

### Step 5: Report

Format as comprehensive report:

```
# DDD Full Compliance Audit
Project: {name} | Files: {N} | Layers: {M} | Date: {date}

## Executive Summary
- Total violations: {X} (CRITICAL: {a}, HIGH: {b}, MEDIUM: {c}, LOW: {d})
- Compliance score: {Y}%
- Worst layer: {layer}

## By Layer

### Domain Layer (N files, X violations)
| File | Severity | Issue | Fix |
|------|----------|-------|-----|
| Order.java | CRITICAL | setId public | Change to protected |
| ... | | | |

### Application Layer (N files, X violations)
...

## Anti-Patterns Found
{list of anti-patterns detected with file locations}

## Dependency Graph (ascii)
common
  ↑
domain ← infrastructure
  ↑
application
  ↑
client

## Recommendations
1. {Top priority fix}
2. {Second priority fix}
...
```

## Severity

| Level | Criteria |
|---|---|
| **CRITICAL** | Architecture violation — wrong layer dependency, missing required base class, domain depends on infrastructure |
| **HIGH** | Rule violation — wrong naming, public identity setter, domain service with no behavior |
| **MEDIUM** | Convention deviation — anemic entity, missing Field wrapper, no JavaDoc on public API |
| **LOW** | Style — inconsistent formatting, missing @Override |

## Key Checks by Layer

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
- [ ] `LevelLock` implementations are concrete (extend abstract class)
- [ ] All `GatewayI` implementations here, not in domain

**Client Layer:**
- [ ] All DTOs extend `BaseDTO`
- [ ] No domain classes exposed in DTOs
- [ ] Client module is deployable standalone (no domain imports)

## Important

- Always reference the specific rule section when flagging violations (e.g. "rules/domain-layer.md Section A.3")
- Suggest the exact fix, not just the problem
- Prioritize CRITICAL issues — architecture decay is harder to fix later
- A perfect score is rare — focus on actionable items
