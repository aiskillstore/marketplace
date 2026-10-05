---
name: nestjs-code-audit
description: 'Audits an existing NestJS repository with bundled semantic guidance and optional specialist skills and returns one prioritized, evidence-backed code-quality report. Use when asked to check a whole NestJS codebase or a scoped folder for syntax, TypeScript, lint, module-boundary, dependency, design-smell, security, testing, performance, reliability, or production-readiness problems. This is a read-only review workflow: it does not fix code, install dependencies, run migrations, or deploy. When other skills also apply, reconcile ownership before mutation.'
license: MIT
compatibility: 'Requires Node.js 20+ and a NestJS repository. Sibling skills are optional.'
metadata:
  author: amirtaherkhani
  version: '1.0.3'
---

# NestJS Code Audit

Inspect the current user's NestJS project and return one consolidated report of verified code problems and evidence-backed risks. Audit only; do not modify the target project.

## Pre-execution conflict guard

Before editing files or running any state-changing command, reconcile active instructions. Read-only inspection may continue.

### Prerequisites

Confirm root, scope, instructions, Git state, installed versions/dependencies, and safe checks. Preserve user changes. Load [semantic-review.md](references/semantic-review.md) for the requested semantic lanes; sibling skills are optional deeper guidance, not installation prerequisites. Read other active skills only when their decisions overlap.

### Primary ownership

This skill owns read-only quality evidence, finding deduplication, severity, and report assembly. When installed and relevant, coordinate with:

- `nestjs-architecture-principles`: module, dependency, data, and transaction boundaries.
- `nestjs-oop-design-patterns`: object responsibilities, invariants, and patterns.
- `nestjs-features-performance`: lifecycle, API/security, testing, runtime, and performance.
- `nestjs-professional-software-engineering`: implementation and verification.
- `nestjs-feature-audit`: branch-specific roadmap gate and feature reporting.
- `nestjs-git-commit-pr-message`: authorized Git publication and CI follow-up.

These are decision boundaries, not required dependencies. Retain domain ownership when handing work to another workflow.

### Conflict test

Resolve incompatible findings, unsafe checks, or missing evidence using explicit user intent, repository contracts, verified runtime constraints, then the narrowest owner. Keep one finding per root cause; unresolved claims belong in **Needs verification**. If an action crosses the audit boundary, stop before mutation. An audit alone never authorizes fixes; if the user explicitly requested both, finish the read-only audit first, then enter the authorized implementation phase without asking for the same approval again.

## Invocation

Preferred portable invocation:

```text
$nestjs-code-audit
$nestjs-code-audit full src/payments
$nestjs-code-audit static
$nestjs-code-audit security src/auth
```

Codex CLI/IDE custom-prompt alias, when installed:

```text
/prompts:nestjs-audit
/prompts:nestjs-audit full src/payments
```

Codex does not provide arbitrary bare user-defined commands such as `/Nestjs audit`; keep the supported alias explicit.

### Actions

| Action | Coverage |
| --- | --- |
| `full` (default) | Safe static gates plus architecture, object design, runtime, security, testing, and delivery review |
| `static` | Syntax, TypeScript, lint, configuration, and directly related toolchain failures |
| `architecture` | Modules, dependencies, data/write ownership, transactions, events, ports, and service boundaries |
| `design` | Responsibilities, invariants, coupling, abstractions, patterns, and refactoring risks |
| `runtime` | Nest lifecycle, API/errors, reliability, performance evidence, health, shutdown, and delivery |
| `security` | Input, identity/access, tenant isolation, secrets, output, abuse controls, and security tests |
| `tests` | Test-layer choice, missing boundary coverage, flaky lifecycle risks, and safely runnable checks |

An optional repository-relative scope follows the action. If the first argument is not a recognized action, treat all arguments as the scope/focus and use `full`. For focused actions, load only the relevant lanes in the bundled semantic reference, plus any available specialist guidance needed for a cross-lane blocker. Report only the requested scope.

## Audit workflow

### 1. Establish eligibility and scope

1. Resolve the current working directory and optional user scope without escaping the repository root.
2. Read `AGENTS.md` and other repository instructions, `package.json`, lockfiles, `nest-cli.json`, TypeScript and lint configuration, bootstrap files, module files, tests, and deployment manifests that affect the scope.
3. Verify that `@nestjs/core` is declared or that the repository is clearly a NestJS workspace. If not, stop and report that this audit is not applicable.
4. Record the current branch and dirty state. Do not alter or discard existing changes.
5. State a one-sentence baseline of the observed architecture. Do not infer Clean Architecture, DDD, CQRS, or microservices from folder names.

### 2. Collect deterministic evidence

Use the bundled collector from this skill's directory:

```bash
node scripts/collect-quality-evidence.mjs --root "$PWD" --run
```

Add `--scope <relative-path>` when the user requested a narrower audit. The collector:

- reads manifests and source files without changing them;
- identifies the package manager and available quality scripts;
- runs only allow-listed, non-fixing ESLint and `tsc --noEmit` commands when `--run` is present;
- never installs dependencies, runs builds, updates snapshots, writes coverage, or invokes arbitrary package scripts;
- returns JSON containing command results and heuristic review candidates.

If dependencies are missing or a command is unsafe, unavailable, timed out, or outside scope, record it as **not run**. Do not reinterpret a missing check as a pass. Never run `lint --fix`, format/write commands, migrations, deployment commands, live integration tests, or tests that may reach shared infrastructure during this audit.

### 3. Review four evidence lanes

#### Toolchain correctness

- Report parser, TypeScript, and lint diagnostics exactly enough to locate the problem.
- Deduplicate cascaded compiler errors when they share one root cause.
- Separate command failure from a code finding, such as missing dependencies or broken configuration.

#### Architecture

Trace bootstrap entry points, module imports/exports, provider visibility, request/message paths, persistence ownership, transactions, events, and external adapters. Confirm cycles or boundary leaks from real imports and call paths. Do not report architectural preference as a defect.

#### Object design and maintainability

Inspect responsibilities, dependency clusters, invariant placement, repeated conditional variation, framework/vendor leakage, hidden service location, speculative abstractions, and risky refactor seams. File length or a regex signal alone is not a finding.

#### Runtime, security, and verification

Inspect lifecycle placement, validation, authentication/authorization, tenant/resource ownership, public error and response contracts, secrets/logging, query and resource bounds, timeouts/retries/idempotency, health/shutdown, test boundaries, and deployment evidence when present. Do not claim performance problems without measurements.

### 4. Verify and deduplicate findings

A confirmed finding needs:

- a stable ID: `TOOL`, `ARCH`, `OOP`, `RUN`, `SEC`, or `TEST` plus a number;
- severity: critical, high, medium, or low;
- primary owning skill;
- file and line evidence plus the relevant import, call path, diagnostic, or configuration;
- concrete impact, not only a rule name;
- the smallest safe remedy;
- a validation step that could prove the remedy.

Use critical only for a present security, data-loss, tenant-isolation, or severe availability risk. High requires likely incorrect behavior or a boundary flaw blocking a known change. Medium requires a credible maintainability, correctness, or operability cost. Low is a localized improvement with limited risk.

Move unverified regex signals, suspected dead code, possible performance issues, and checks blocked by missing dependencies to **Needs verification**. Do not inflate the report with style preferences or multiple findings for one root cause.

## Required report

Return Markdown in this order:

1. **Audit verdict:** pass, pass with risks, or fail; audited scope; one-sentence baseline.
2. **Quality gates:** syntax/TypeScript, lint, tests if safely available, and audit coverage, each marked pass, fail, or not run with the exact command or reason.
3. **Finding summary:** counts by severity and owner.
4. **Confirmed findings:** ordered by severity and impact, using the evidence/remedy/validation contract above.
5. **Needs verification:** candidate, missing evidence, and smallest next check.
6. **Healthy patterns:** only notable controls actually verified in the repository.
7. **Recommended order:** a short, dependency-aware remediation sequence; implement only in a distinct phase if the user explicitly authorized those fixes.

If there are no confirmed problems, say so and list the checks that were not run. A clean lint result is not proof of sound architecture, security, runtime behavior, or test coverage.

## Reference routing

| Need | Load |
| --- | --- |
| Review architecture, objects, runtime, and healthy controls without sibling skills | [semantic-review.md](references/semantic-review.md) |
| Decide which checks may run without modifying the project | [check-policy.md](references/check-policy.md) |
| Assign and deduplicate findings across the three domain skills | [finding-ownership.md](references/finding-ownership.md) |
| Format the final audit consistently | [report-template.md](references/report-template.md) |
