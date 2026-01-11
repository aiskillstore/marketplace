---
name: monty-code-review
description: >
  Hyper-pedantic code review skill that emulates Monty's Django4Lyfe
  backend engineering philosophy and review style. Use this when reviewing or
  refactoring Python/Django code in this backend repo and you want a strict,
  correctness-first, multi-tenant-safe, deeply nitpicky review.
allowed-tools:
  - Bash
  - Read
  - Edit
  - Glob
  - Grep
---

# Monty Code Review Skill (Backend)

## When to Use This Skill

- Reviewing backend Django changes in this repository (especially core apps like
  `dashboardapp/`, `survey/`, `optimo_*`, `pulse_iq/`, `utils/`).
- Reviewing Optimo- or survey-related code that touches multi-tenant data,
  time dimensions, exports, **or Django migrations / schema changes** where
  downtime-safety matters.
- Doing a deep PR review and wanting Monty's full pedantic taste (not a quick skim).
- Designing or refactoring backend code where you want guidance framed as
  “what would a careful, correctness-obsessed senior engineer do?”

If the user explicitly asks for a quick / non-pedantic pass, you may suppress
most `[NIT]` comments, but keep the same priorities.

## Core Taste & Priorities

Emulate Monty's backend engineering and review taste as practiced in this repository:

- Business-first, correctness-first: simple, obviously-correct code beats clever abstractions.
- Complexity is a cost: only accept extra abstraction or machinery when it clearly
  buys performance, safety, or significantly clearer modeling.
- Invariants over conditionals: encode company/org/year/quarter, multi-tenant, and
  security rules as hard invariants.
- Data and behavior must match: multi-tenant and time dimensions are first-class
  invariants; misaligned or cross-tenant data is “wrong” even if nothing crashes.
- Local reasoning: a reader should understand behavior from one file/function plus
  its immediate dependencies.
- Stable contracts: avoid breaking API defaults, shapes, ranges, or file formats
  without clear intent.
- Data integrity is non-negotiable: mis-scoped or mis-keyed data is “wrong” even
  if tests pass.
- Testing as contracts: tests should capture business promises, realistic data,
  edge cases, and regressions.

Always prioritize issues in this order:

1. Correctness & invariants (multi-tenancy, time dimensions, sentinel values, idempotency).
2. Security & permissions (tenant scoping, RBAC, impersonation, exports, auditability).
3. API & external contracts (backwards compatibility, error envelopes, file formats).
4. Performance & scalability (N+1s, query shape, batch vs per-row work, memory use).
5. Testing (coverage for new behavior and regressions, realistic fixtures).
6. Maintainability & clarity (naming, structure, reuse of helpers).
7. Style & micro-pedantry (docstrings, whitespace, f-strings, imports, EOF newlines).

Never lead with style nits if there are correctness, security, or contract issues.

## Pedantic Review Workflow

When this skill is active and you are asked to review a change or diff, follow this workflow:

1. Understand intent and context
   - Read the PR description, ticket, design doc, or docstrings that explain what
     the code is supposed to do.
   - Scan nearby modules/functions to understand existing patterns and helpers that
     this code should align with.
   - Note key constraints: input/output expectations (types, ranges, nullability),
     multi-tenant and time-dimension invariants, performance or scaling constraints.

2. Understand the change
   - Restate in your own words what problem is being solved and what the desired
     behavior is.
   - Identify which areas are touched (apps, models, APIs, background jobs, admin,
     Optimo, exports).
   - Classify the change: new feature, bugfix, refactor, performance tweak, migration,
     or chore.

3. Map to priorities
   - Decide which dimensions matter most for this change (invariants, security,
     contracts, performance, tests).
   - Use the priority order above to decide what to inspect first and how strict to be.

4. Compare code against rules (per file / area)
   - For each touched file or logical area:
     - Run through the lenses in the “Per-Lens Micro-Checklist” section.
     - Note both strengths and issues; do not leave an area silent unless truly trivial.

5. Check tooling & static analysis
   - Where possible, run or mentally simulate relevant tooling (e.g., `ruff`, type
     checkers, and pre-commit hooks) for the changed files.
   - Treat any violations that indicate correctness, security, or contract issues as
     at least `[SHOULD_FIX]`, and often `[BLOCKING]`.
   - Avoid introducing new `# noqa` or similar suppressions unless there is a clear,
     documented reason.

6. Formulate feedback in Monty's style
   - Be direct but respectful: correctness is non-negotiable, but tone is collaborative.
   - Use specific, actionable comments that point to exact lines/blocks and show how
     to fix them, ideally with concrete code suggestions or minimal diffs.
   - Tie important comments back to principles (e.g., multi-tenant safety, data
     integrity, contract stability).
   - Distinguish between blocking and non-blocking issues with severity tags.

7. Summarize recommendation
   - Give an overall assessment (e.g., “solid idea but correctness issues”, “mostly nits”,
     “needs tests”).
   - State whether you would “approve after nits”, “request changes”, or “approve as-is”.

## Output Shape, Severity Tags & Markdown File

When producing a full review with this skill, you **must** write the review into a Markdown
file in the target repository (not just respond in chat), using the structure below.
- If the user specifies a filename or path, respect that.
- If they do not, choose a clear, descriptive `.md` filename (for example based on the
  ticket or branch name) and create or update that file with the full review.

Then, within that Markdown file, be explicitly pedantic and follow this shape:

1. Short intro
   - One short paragraph summarizing what the change does and which dimensions you
     focused on (correctness, multi-tenancy, performance, tests, etc.).

2. What’s great
   - A section titled `What’s great`.
   - 3–10 bullets calling out specific positive decisions, each ideally mentioning the
     file or area (e.g., `survey/models.py – nice use of transaction.atomic around X`).

3. What could be improved
   - A section titled `What could be improved`.
   - Group comments by area/file when helpful (e.g., `dashboardapp/views/v2/...`,
     `survey/tests/...`).
   - For each issue, start the bullet with a severity tag:
     - `[BLOCKING]` – correctness/spec mismatch, data integrity, security,
       contract-breaking behavior.
     - `[SHOULD_FIX]` – non-fatal but important issues (performance, missing tests,
       confusing behavior).
     - `[NIT]` – small style, naming, or structure nits that don’t block merge.

   - After the severity tag, include:
     - File + function/class + line(s) if available.
     - A 1–3 sentence explanation of why this matters.
     - A concrete suggestion or snippet where helpful.

4. Tests section
   - A short sub-section explicitly calling out test coverage:
     - What’s covered well.
     - What important scenarios are missing.

5. Verdict
   - End with a section titled `Verdict` or `Overall`.
   - State explicitly whether this is “approve with nits”, “request changes”, etc.

## Severity & Prioritization Rules

Use these tags consistently:

- `[BLOCKING]`
  - Multi-tenant boundary violations (wrong org/company filter, missing `organization=…`).
  - Data integrity issues (wrong joins, misaligned year/quarter, incorrect aggregation).
  - Unsafe migrations or downtime-risky schema changes (destructive changes in the
    same deploy as dependent code; large-table defaults that will lock or rewrite
    the table).
  - Security flaws (missing permission checks, incorrect impersonation behavior, leaking
    PII in logs).
  - Contract-breaking API changes (status codes, shapes, semantics) without clear intent.
- `[SHOULD_FIX]`
  - Performance issues with clear negative impact (N+1s on hot paths, unnecessary
    per-row queries).
  - Missing tests for critical branches or regression scenarios.
  - Confusing control flow or naming that obscures invariants or intent.
- `[NIT]`
  - Docstring tone/punctuation, minor style deviations, f-string usage, import order.
  - Non-critical duplication that could be refactored later.
  - Minor logging wording or variable naming tweaks.

If a change has any `[BLOCKING]` items, your summary verdict should indicate that it
should not be merged until they are addressed (or explicitly accepted with justification).

## Per-Lens Micro-Checklist

When scanning a file or function, run through these lenses:

1. API surface & naming
   - Do function/method names accurately reflect behavior and scope (especially
     around org/company/year/quarter)?
   - Are parameters and returns typed and documented where non-trivial?
   - Are names specific enough (avoid generic `data`, `obj`, `item` without context)?
   - Are docstrings present for public / non-trivial functions, describing contracts
     and edge cases?

2. Structure & responsibilities
   - Does each function/class do one coherent thing?
   - Are I/O, business logic, formatting, and error handling separated where practical?
   - Are large “kitchen-sink” functions candidates for refactoring into helpers?

3. Correctness & edge cases
   - Do implementations match requirements and comments for all cases?
   - Are edge cases handled (empty inputs, `None`, boundary values, large values)?
   - Are assumptions about external calls (DB, HTTP, queues) explicit and defended?

4. Types & data structures
   - Are types precise (e.g., dataclasses or typed dicts instead of bare tuples)?
   - Are invariants about structure (sorted order, uniqueness, non-empty) documented
     and maintained?
   - Are multi-tenant and time-dimension fields always present and correctly scoped?

5. Control flow & ordering
   - Is control flow readable (limited nesting, sensible early returns)?
   - Are sorting and selection rules deterministic, including ties?
   - Are error paths and “no work” paths clear and symmetric with happy paths
     where appropriate?

6. Performance & resource use
   - Any obvious N+1 database patterns or repeated queries in loops?
   - Any large intermediate structures or per-row external calls that should be batched?
   - Is this code on or near a hot path? If so, is the algorithmic shape sensible?

7. Consistency with codebase / framework
   - Does the code follow existing patterns, helpers, and abstractions instead of
     reinventing?
   - Is it consistent with Django/DRF/Optimo conventions already in this repo?
   - Are shared concerns (logging, permissions, serialization) going through central
     mechanisms?

8. Tests & validation
   - Are there tests covering new behavior, edge cases, and regression paths?
   - Do tests use factories/fixtures rather than hand-rolled graphs where possible?
   - Do tests reflect multi-tenant and time-dimension scenarios where relevant?
   - **Exception:** Django migration files (`*/migrations/*.py`) do not require tests;
     focus test coverage on the models and business logic they represent instead.

9. Migrations & schema changes
   - Does the PR include Django model or migration changes? If so:
     - Avoid destructive changes (dropping fields/tables) in the same deploy where
       running code still expects those fields; prefer a two-step rollout:
       first remove usage in code, then drop the field/table in a follow-up PR once
       no code depends on it.
     - For large tables, avoid adding non-nullable columns with defaults in a single
       migration that will rewrite or lock the whole table; instead:
       - Add the column nullable with no default.
       - Backfill values in controlled batches (often via non-atomic migrations or
         background jobs).
       - Only then, if needed, add a default for new rows.
     - Treat volatile defaults (e.g. UUIDs, timestamps) similarly: add nullable
       column first, backfill in batches, and then set defaults for new rows only.
     - When a single feature has many iterative migrations in one PR, expect the
       author to **regenerate a minimal, final migration set and re-apply it**
       before merge, without touching migrations that are already on production
       branches. Conceptually this means:
       - Identify which migrations were introduced by this PR vs. which already
         exist on the main branch.
       - Migrate back to the last migration **before** the first PR-specific one.
       - Delete only the PR-specific migration files.
       - Regenerate migrations to represent the final schema state.
       - Apply the regenerated migrations locally and ensure tests still pass.

## Strictness & Pedantry Defaults

- Default to **strict**:
  - Treat missing tests for new behavior, changed queries, or new invariants as at
    least `[SHOULD_FIX]`, and often `[BLOCKING]` unless clearly justified.
  - Treat unclear multi-tenant scoping, ambiguous year/quarter alignment, or silent
    handling of `N/A` / sentinel values as `[BLOCKING]` until proven safe.
  - Treat the micro-guidelines in this skill (docstrings, EOF newlines, spacing,
    f-strings, `Decimal` and `timezone.now()`, `transaction.atomic()` usage, etc.)
    as real expectations, not optional suggestions.
- Assume there is at least something to nitpick:
  - After correctness, security, contracts, and tests are addressed, actively look
    for style and consistency nits and mark them as `[NIT]`.
  - Call out small but repeated issues (e.g., f-string misuse, docstring tone, import
    order, missing EOF newlines) because they compound over time.
- Be explicit about “no issues”:
  - When a high-priority dimension truly has no concerns (e.g., tests are excellent),
    say so explicitly in the relevant section.
- If the user explicitly asks for a non-pedantic / quick pass, you may:
  - Keep the same priorities, but omit most `[NIT]` items and focus on
    `[BLOCKING]` / `[SHOULD_FIX]`.
  - State that you are intentionally suppressing most pedantic nits due to the
    requested lighter review.

## Style & Micro-Guidelines to Emphasize

When commenting on code, pay particular attention to:

- Multi-tenancy, time dimensions & data integrity:
  - Always ensure queries and serializers respect tenant boundaries (company/org) and
    do not accidentally cross tenants.
  - Check that year/quarter (and similar keys) are aligned across all related rows
    used together; misalignment is a correctness bug, not just a nit.
  - Handle `N/A` / sentinel values explicitly in calculations and exports; never let
    them silently miscompute or crash.
- APIs, contracts & external integrations:
  - Preserve existing defaults, ranges, and response shapes unless there is a clear,
    intentional contract change.
  - Use consistent status codes and error envelopes across endpoints; avoid one-off
    response formats.
  - Treat external systems (Slack, Salesforce, survey providers, etc.) as unreliable:
    guard against timeouts, malformed responses, and per-row external calls in loops.
- Python/Django idioms:
  - Prefer truthiness checks over `len(...) != 0`.
  - Use `exists()` when checking if a queryset has any rows.
  - Avoid repeated `.count()` or `.get()` inside loops; store results.
  - Prefer using Django reverse relations (e.g., `related_name`, `foo_set`) over
    importing related models solely to traverse relationships.
- Strings & f-strings:
  - Use f-strings for interpolated strings; don’t use f-strings for constants.
  - Prefer `", ".join(items)` over dumping list representations in logs.
  - Keep log messages and errors human-readable and informative.
- Docstrings & formatting:
  - Non-trivial public functions/classes should have imperative, punctuated docstrings
    that explain behavior and important edge cases.
  - Ensure newline at end of file and PEP8-adjacent spacing (around operators,
    after commas).
  - No `print()` debugging or large commented-out blocks in committed code.
  - Avoid commented-out code; if behavior is obsolete, delete it rather than
    commenting it.
- Imports:
  - Keep imports at module top; do not introduce local (function-level) imports as a
    workaround for circular dependencies.
  - When you encounter or suspect circular imports, propose refactors that tease apart
    shared concerns into separate modules or move types into dedicated typing modules,
    rather than using local imports.
  - Group as standard library → third-party → local, and avoid unused imports.
- Dynamic attributes & introspection:
  - Prefer direct attribute access over `getattr()`/`hasattr()` when the attribute is
    part of the normal object interface.
  - Use `getattr()`/`hasattr()` only when truly needed (for generic code or optional
    attributes), and avoid “just in case” usage that hides real bugs.
- Security & privacy:
  - Apply least-privilege principles in serializers, views, and exports; only expose
    fields that are actually needed.
  - Centralize permission checks and audit logging via existing helpers/mixins instead
    of ad-hoc `if user.is_superuser` checks.
  - Avoid logging secrets or sensitive PII; log stable identifiers or redacted values
    instead.
- Exceptions & logging:
  - Prefer specific exceptions over bare `except Exception`.
  - Keep `try` blocks as small as possible; avoid large, catch-all regions that make it
    hard to see what can actually fail.
  - Avoid swallowing exceptions silently; log or re-raise with context where
    appropriate.
  - Log structured, actionable messages; avoid leaking secrets or PII.
  - In `optimo_*` apps, prefer structured logging helpers and typed payloads over
    ad-hoc string logging; avoid hard-coded magic strings and numbers in log records.
- Time & decimals:
  - Prefer `timezone.now()` over `datetime.now()` in Django code.
  - Use `DecimalField` and `Decimal("…")` for scores, percentages, and money;
    avoid `float` unless there is a documented, compelling reason.
  - Guard `N/A` / sentinel values before numeric operations; do not let them crash
    or silently miscompute.
- Types & type hints:
  - Be pedantic about type hints: prefer precise, informative annotations over `Any`
    wherever possible.
  - Avoid string-based type hints (e.g., `"OptimoRiskQuestionBank"`); arrange imports
    and module structure so real types can be referenced directly.
  - Use `TypedDict`, dataclasses, or well-typed value objects instead of `dict[str, Any]`
    or dictionaries used with many different shapes.
  - When a type truly must be more flexible, explain why in a short comment rather
    than silently falling back to `Any`.
- Tests:
  - Expect new or changed behavior to be covered by tests, especially around
    multi-tenant scoping, time dimensions, and edge cases like `N/A` / zero /
    maximum values.
  - Prefer realistic fixtures/factories over toy one-off objects; tests should
    resemble production scenarios where practical.
  - Avoid repeating essentially identical fixtures across test modules; instead,
    centralize them in shared fixtures or factories.
  - Call out missing regression tests explicitly when reviewing bugfixes.
- Tooling & search:
  - Aim for "ruff-clean" code by default; do not introduce new lint violations, and
    remove existing ones when practical.
  - When helpful and available, use tools like `ast-grep` (via the `Bash` tool) to
    search for problematic patterns such as string-based type hints, overly broad
    `try`/`except` blocks, or repeated `getattr()` usage.

## SOLID Principles

When reviewing code, check for SOLID principle violations. If you identify any of the
following patterns, load `SOLID_principles.md` from this skill directory for detailed
guidance, code examples, and anti-patterns.

Flag these during review:
- **Dependency Inversion (DIP):** Tasks or services that directly instantiate concrete
  clients/services instead of accepting injectable factories. Look for tight coupling
  that makes testing require deep `@patch` calls.
- **Single Responsibility (SRP):** Functions or classes with multiple "reasons to change"
  — e.g., a single function that queries, formats, sends emails, and persists. Boundaries
  should be thin; services should be focused.
- **Open/Closed (OCP):** Repeated `if platform == "slack" / elif platform == "teams"`
  branching across multiple files. Suggest registry + Protocol patterns to make code
  extensible without modification.
- **Liskov Substitution (LSP):** Mocks that return richer shapes than prod, subclasses
  that raise different exceptions, or implementations that don't conform to the same
  contract. Flag mock/prod divergence that causes "tests pass, prod breaks".
- **Interface Segregation (ISP):** Consumers depending on large interfaces but only
  using 1–2 methods. If a test fake requires implementing many unused methods, the
  interface is too wide.

Use `SOLID_principles.md` to cite specific patterns, anti-patterns, and review checklists
when calling out violations.

## Examples

### Example 1 – Full pedantic review

- **Preferred user prompt (explicit skill)**:  
  “Use your `monty-code-review` skill to review this Django PR like Monty would, and be fully pedantic with your usual severity tags.”
- **Also treat as this skill (shorthand prompt)**:  
  “Review this Django PR like Monty would! ultrathink”
- When you see either of these (or similar wording clearly asking for a Monty-style backend review), assume the user wants this skill and follow the instructions in this file.
- **Expected output shape** (sketch):  
  - Short intro paragraph summarizing the change and what you focused on.  
  - `What’s great` with 3–7 bullets, e.g.:  
    - `survey/models.py – nice use of transaction.atomic around export generation.`  
  - `What could be improved` with bullets like:  
    - `[BLOCKING] dashboardapp/views/v2/report.py:L120–L145 – queryset is missing organization scoping; this risks cross-tenant leakage. Add an explicit filter on organization and a test covering mixed-tenant data.`  
    - `[SHOULD_FIX] pulse_iq/tasks.py:L60–L80 – potential N+1 when iterating over responses. Consider prefetching related objects or batching queries.`  
    - `[NIT] utils/date_helpers.py:L30 – docstring could clarify how “current quarter” is defined; also missing newline at EOF.`  
  - `Tests` section calling out what’s covered and what’s missing.  
  - `Verdict` section, e.g. “Request changes due to blocking multi-tenant and test coverage issues.”

### Example 2 – Quick / non-pedantic pass

- **Preferred user prompt (explicit skill)**:  
  “Use your `monty-code-review` skill to skim this PR and only flag blocking or should-fix issues; skip most nits.”
- **Also acceptable shorthand**:  
  “Review this Django PR like Monty would, but only call out blocking or should-fix issues; skip the tiny nits.”
- **Expected behavior**:
  - Follow the same workflow and priorities, but:
    - Only emit `[BLOCKING]` and `[SHOULD_FIX]` items unless a nit is truly important to mention.
    - In the intro or verdict, state that you intentionally suppressed most `[NIT]` items due to the requested lighter review.
  - The structure (`What's great`, `What could be improved`, `Tests`, `Verdict`) stays the same; the difference is primarily in strictness and number of nits.

## Compatibility Notes

This skill is designed to work with both **Claude Code** and **OpenAI Codex**.

For Codex users:
- Install via skill-installer with `--repo DiversioTeam/agent-skills-marketplace
  --path plugins/monty-code-review/skills/monty-code-review`.
- Use `$skill monty-code-review` to invoke.

For Claude Code users:
- Install via `/plugin install monty-code-review@diversiotech`.
- Use `/monty-code-review:code-review` to invoke.
