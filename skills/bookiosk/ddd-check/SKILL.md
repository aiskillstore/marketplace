---
name: ddd-check
description: DDD compliance check for Java projects. Incremental mode scans git diff changes — fast, pre-commit. Full mode audits every Java file — architecture review. Validates layer isolation, base class usage, naming conventions, dependency direction, and anti-patterns.
model: claude-sonnet-4-20250514
allowed-tools: Read, Grep, Glob, Bash
user-invocable: true
---

# DDD Compliance Check

Validate Java projects against Domain-Driven Design layer rules. Supports two modes:

- **Incremental** (`ddd-check`, "check my changes") — scans only changed/new Java files via git diff
- **Full** (`ddd-check-full`, "full audit") — audits every Java file in the project

## DDD Layer Rules

Rules are in `rules/` directory. Each file defines structural, naming, and dependency constraints for one layer:

| Rule File | Layer |
|---|---|
| `rules/domain-layer.md` | Domain — aggregate, entity, value object, repository, domain service |
| `rules/application-layer.md` | Application — command/query services, executors, DTOs |
| `rules/adaptor-layer.md` | Adaptor — controllers, converters, gateways |
| `rules/infrastructure-layer.md` | Infrastructure — repository impls, PO, mapper, RPC clients |
| `rules/client-layer.md` | Client — public API DTOs, facades |
| `rules/model-layer.md` | Model — shared enums, constants, shared types |
| `rules/anti-patterns.md` | Anti-patterns — anemic model, service overuse, wrong dependencies |

Reference docs in `references/` are educational, not checked against code.

## Workflow

### Determine Mode

Ask user: "Incremental check or full audit?"

If user says "incremental", "check changes", "pre-commit", "my code" → **Incremental mode**.
If user says "full", "audit", "architecture review", "entire project" → **Full mode**.

Default to incremental if unclear.

### Incremental Mode

1. Find changed Java files:
   ```bash
   git diff HEAD --name-only --diff-filter=ACMR | grep '\.java$'
   ```
2. If no Java files changed: "No Java files changed — nothing to check."
3. Classify each file by layer (match package path to layer name).
4. Read only the rule files matching changed layers + always `anti-patterns.md`.
5. Check each file: correct package → correct base class → naming conventions → forbidden imports → anti-patterns.
6. Report:

```
## DDD Check: {branch} → {n} files changed

### {FilePath}.java — {Layer}
🔴 CRITICAL: {problem}. {fix}.
🟡 HIGH: {problem}. {fix}.

### Summary
- {n} files checked, {x} violations (C: {a}, H: {b}, M: {c}, L: {d})
```

### Full Mode

1. Discover all Java files:
   ```bash
   find . -name "*.java" -not -path "*/target/*" -not -path "*/test/*" | sort
   ```
2. Load all 7 rule files + `base-classes-reference.md`.
3. Group files by layer. For each layer: package check → base class check → naming check → dependency check → structural check.
4. Cross-layer: verify dependency direction via import grep, detect anemic models, find empty layers.
5. Report with executive summary, per-layer tables, dependency graph, anti-patterns list, prioritized recommendations.

## Severity

| Level | Criteria |
|---|---|
| **CRITICAL** | Architecture violation — wrong layer dependency, missing base class, domain depends on infrastructure |
| **HIGH** | Rule violation — wrong naming, public identity setter, domain service with no behavior |
| **MEDIUM** | Convention deviation — anemic entity, missing Field wrapper, no JavaDoc on public API |
| **LOW** | Style — inconsistent formatting, missing @Override |

## Key Checks by Layer

**Domain (MOST CRITICAL):**
- Aggregates extend `BaseAggregate<ID>`, entities extend `BaseEntity<ID>`, value objects extend `BaseValue`
- `setId()` is `protected`, not `public`
- No infrastructure imports (no Mapper, JPA, SQL)
- Repository interfaces extend `AggregateRepository<T, ID, Q>`
- External calls through `GatewayI` interfaces
- Design patterns FORBIDDEN in domain (Strategy, Factory, etc.)

**Application:**
- Cmd services extend `ApplicationCmdService`, Qry services extend `ApplicationQueryService`
- Each use case has dedicated Executor

**Infrastructure:**
- Repository impls in correct package, PO classes separate from domain objects

**Client:**
- All DTOs extend `BaseDTO`, no domain classes exposed

## Important

- Reference specific rule sections when flagging violations (e.g. "domain-layer.md Section A.3")
- Suggest exact fix, not just problem
- Do NOT check unchanged files in incremental mode
- Only report real problems — no "looks good" padding
