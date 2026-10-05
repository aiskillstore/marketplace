---
name: nestjs-professional-software-engineering
description: 'Designs, implements, refactors, debugs, reviews, and verifies production-quality NestJS and TypeScript software. Use for NestJS feature development, bug fixes, APIs, libraries, testing, maintainability, developer experience, idiomatic syntax, or syntactic sugar. It inspects the current project and official version-appropriate documentation before selecting syntax, preserves public behavior, and tests the result. When other skills also apply, reconcile ownership before mutation.'
license: MIT
metadata:
  author: amirtaherkhani
  version: '2.0.2'
---

# Professional Software Engineering

Produce correct, idiomatic, secure, readable, maintainable, testable, and extensible NestJS software while respecting the existing project.

## Pre-execution conflict guard

Before editing files or running any state-changing command, reconcile active instructions. Read-only inspection may continue.

### Prerequisites

Inspect repository instructions, working tree, manifests, installed versions, source/callers, contracts, conventions, and checks. Preserve unrelated changes. Verify uncertain or version-sensitive syntax against installed types/source and official documentation; never invent an API. Read other active skills only when their decisions overlap.

### Primary ownership

This skill owns project inspection, minimal implementation, version-compatible syntax, API ergonomics, testing, and verification. When installed and relevant, coordinate with:

- `nestjs-architecture-principles`: module, dependency, data, and transaction boundaries.
- `nestjs-oop-design-patterns`: object responsibilities, invariants, and patterns.
- `nestjs-features-performance`: lifecycle, API/security, testing, runtime, and performance.
- `nestjs-code-audit`: read-only quality evidence and deduplicated reporting.
- `nestjs-feature-audit`: branch-specific roadmap gate and feature reporting.
- `nestjs-git-commit-pr-message`: authorized Git publication and CI follow-up.

These are decision boundaries, not required dependencies. Retain domain ownership when handing work to another workflow.

### Conflict test

Check for incompatible edits/contracts, command order or side effects, competing owners, and unmet version, evidence, authorization, or repository prerequisites. Resolve using explicit user intent, repository contracts, verified runtime constraints, then the narrowest owner. Assign one lead per decision; do not create parallel designs to satisfy incompatible advice. If a material conflict remains, stop before mutation and ask for the smallest missing decision. Audits stay read-only; explicit fix authorization applies in a distinct implementation phase.

## Required workflow

For implementation requests, complete the workflow through mutation and verification. For review or diagnosis requests, inspect and report evidence without modifying files unless the user also authorizes implementation.

### 1. Inspect

1. Establish repository scope and applicable instructions.
2. Identify the language, framework, runtime, package manager, and exact relevant versions.
3. Read relevant implementation, callers, tests, configuration, manifests, and public contracts.
4. Search for analogous features and naming, error, test, and API conventions.
5. Determine focused and broader test, type-check, lint, format, build, and smoke-test commands.

Do not begin with a broad rewrite. Establish current behavior before changing it.

### 2. Understand

Define:

- requested outcome and observable acceptance criteria;
- affected boundaries and consumers;
- compatibility, security, data, performance, deployment, and migration implications;
- assumptions that would materially change the solution.

Ask only when a missing decision materially affects architecture, public behavior, security, data, cost, or compatibility.

### 3. Select the clearest valid syntax

Use this evidence order:

1. Existing repository conventions and compatible public behavior.
2. Installed compiler, runtime, package versions, types, and source.
3. Official version-appropriate language or framework documentation.
4. A minimal local experiment or type-check when documentation leaves ambiguity.
5. Community examples only as discovery evidence, never as the API contract.

Compare at least the direct, explicit form with any convenient syntax. Prefer modern idioms when they are supported, familiar in the project, and clearer at the call site and implementation site.

Load [syntax-and-idioms.md](references/syntax-and-idioms.md) when selecting language or framework syntax.

### 4. Design the smallest coherent change

The design must be:

- idiomatic for the detected language and framework;
- consistent with existing architecture and conventions;
- cohesive, testable, secure by default, and backward-compatible unless a break is authorized;
- explicit about meaningful state changes, effects, failure modes, cost, and control.

For public APIs, make common operations obvious and invalid usage difficult. Prefer progressive disclosure: a convenient path for common cases and a lower-level path only when callers need meaningful control.

Load [syntactic-sugar.md](references/syntactic-sugar.md) for the decision test and API examples.

### 5. Implement

- Use valid, modern syntax supported by the detected toolchain.
- Keep functions, classes, modules, components, and services focused.
- Follow established naming, formatting, organization, validation, and error conventions.
- Validate untrusted input at boundaries and protect sensitive information.
- Handle failures explicitly with actionable, non-leaking errors.
- Consider concurrency, transactions, idempotency, retries, timeouts, cancellation, cleanup, and observability when relevant.
- Avoid unnecessary dependencies, speculative abstractions, clever one-liners, hidden global state, implicit side effects, and unrelated cleanup.
- Comment intent and constraints, not self-explanatory syntax.

### 6. Test and verify

Add or update deterministic tests for observable behavior, relevant edge cases, invalid input, failure paths, security-sensitive behavior, regressions, and public compatibility.

Run the checks appropriate to the change:

1. Focused tests.
2. Broader tests when the risk warrants them.
3. Type checking or compilation.
4. Lint and formatting verification.
5. Build or packaging.
6. Runtime, generated-contract, or migration smoke checks when practical.

Do not weaken tests or controls to obtain a pass. Do not claim a check passed unless it ran successfully.

Load [implementation-verification.md](references/implementation-verification.md) for risk-based verification.

### 7. Report

Lead with the completed outcome, then state:

- important design and syntax decisions;
- files or areas changed;
- checks executed and their results;
- remaining limitations, risks, migrations, or follow-up.

Keep the report concise and distinguish verified facts from assumptions or unrun checks.

## Syntactic sugar rule

Use syntactic sugar only when it:

- reduces meaningful ceremony or repeated misuse;
- improves readability for the repository's actual maintainers;
- preserves predictable behavior, typing, debugging, and composability;
- does not conceal meaningful cost, I/O, state changes, network activity, authorization, transactions, error behavior, or lifecycle;
- preserves an explicit path when advanced callers need control; and
- can be documented and tested with realistic examples.

Reject sugar that merely shortens code, creates a private mini-language, overloads ambiguous inputs, relies on surprising coercion, or makes stack traces and errors harder to understand.

## Expected response

For implementation work, report the delivered behavior and verification. When syntax choice is central, also state:

- **Observed convention:** the relevant repository pattern.
- **Options considered:** explicit and convenient forms.
- **Selected syntax:** why it is supported and clearest.
- **Hidden-behavior check:** effects, cost, failures, and control that remain visible.
- **Compatibility:** affected callers and migration, if any.

Do not return only a proposed snippet when the user requested implementation.

## Reference routing

| Task | Load |
| --- | --- |
| Choose idiomatic, version-compatible syntax | [syntax-and-idioms.md](references/syntax-and-idioms.md) |
| Design or review syntactic sugar and public API ergonomics | [syntactic-sugar.md](references/syntactic-sugar.md) |
| Scope implementation and select verification depth | [implementation-verification.md](references/implementation-verification.md) |
