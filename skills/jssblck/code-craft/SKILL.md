---
name: code-craft
description: Use when writing, reviewing, or refactoring code, or scaffolding a new project. Language-agnostic principles (types encode invariants, parse don't validate, errors as values, no mocks, earn abstractions) with dialects for Rust, TypeScript, Go, and Python.
user-invocable: true
argument-hint: "[rust|typescript|go|python] [target]"
---

# Code Craft

A small set of durable, language-agnostic engineering principles, plus a router
to the dialect of whatever language you are actually editing. The principles are
the same everywhere; only the spelling changes.

## How to use this skill

1. **Apply the universal core below.** These hold in every language. They are
   the decisions that survive a rewrite into another language.
2. **Detect the language(s) in scope** from the files being touched (see the
   detection guide), then **read `languages/<lang>.md`**. That file shows how
   each universal principle is spelled in that language, plus the idioms and
   tooling unique to it. Load only the language(s) you are working in.
3. **Read `principles/<name>.md` for depth** when a principle is the crux of the
   change (a boundary redesign, an error-model decision, a test strategy). The
   core below is the summary; the principle file is the workflow and the nuance.
4. Run the project's own formatter, type-check, linter, and tests before
   claiming done. The language file names the concrete commands.

## Universal core

Each principle links to a deeper file and maps into every language file.

### 1. Make illegal states unrepresentable

Encode invariants in the type system so the bad case cannot be constructed, not
in a name, comment, or convention that a caller can ignore. A wrapper that only
renames a value buys nothing; a type whose only constructor enforces the
invariant buys everything. Prefer enums/unions for mutually exclusive states
over flag soup, and structured data over a string that has to be re-parsed.
Depth: [`principles/illegal-states.md`](principles/illegal-states.md).

### 2. Parse, don't validate

At every boundary where weak external data enters (config, JSON/TOML, CLI/env,
network, user edits), convert it once into a proof-carrying type and pass that
type inward. Do not write `validate(x) -> bool/void` and then keep passing the
raw value; return the refined value. If a caller can skip the parse and still
type-check, the design is not done. Depth:
[`principles/parse-dont-validate.md`](principles/parse-dont-validate.md).

### 3. Errors are values; gates fail closed

Handle expected failure through the language's value channel (Result, error
return, typed exception), not by crashing on recoverable conditions. Add context
as the error propagates so the message is a chain, not a single line. Never
silently swallow an error. A gate or check that cannot produce a valid answer is
a block, never a quiet pass. Depth:
[`principles/errors-as-values.md`](principles/errors-as-values.md).

### 4. No stringly-typed data; newtypes over primitives

A `String`/`string`/`str` that is really an email, a user id, a path, or a state
is a bug waiting to happen. Wrap distinct domain values in distinct types so the
compiler stops you from passing a `UserId` where an `OrderId` belongs, and so
parsing happens once. This is the everyday form of principle 1. Depth:
[`principles/illegal-states.md`](principles/illegal-states.md).

### 5. Mind ownership and copies, but clarity first

Avoid copying or allocating when borrowing or referencing is correct and clear,
especially in loops and hot paths. Accept the most general input type (a view,
not an owned container). This matters most in Rust and C-family code and least
in GC'd languages, but unnecessary deep copies and re-allocations are a smell
everywhere. Do not contort readable code for a copy you have not measured.

### 6. Test behavior, not implementation; avoid mocks

Test at real boundaries with real data. Prefer pure functions, real temp files,
and throwaway fixtures over mocking frameworks that assert on internal calls.
Name tests for the behavior they pin. Use property-based tests where the input
space is large. Keep tests deterministic: no sleeps for synchronization, expose
a join/observe channel instead. Depth:
[`principles/testing.md`](principles/testing.md).

### 7. Architecture docs are a stable map

Keep a short, durable description of module boundaries, invariants, and
cross-cutting concerns. Name the important modules and the deliberate absences
("X stays out of layer Y"). When code moves, update the map rather than adding a
migration note. Keep churny detail in code comments, not the map. Depth:
[`principles/architecture-docs.md`](principles/architecture-docs.md).

### 8. Earn your abstractions; profile before optimizing

Prefer the smallest correct thing. Do not add generics, traits/interfaces,
layers, or indirection before there are two real callers that need them. Do not
optimize on a hunch: measure first, then optimize the proven hot path, then
measure again. Premature abstraction and premature optimization are the same
mistake (acting on a future that has not arrived). Depth:
[`principles/simplicity.md`](principles/simplicity.md).

### 9. New projects: take the defaults

When starting a new project (or hardening a young one), do not re-litigate
tooling. Lock in one opinionated auto-formatter and one linter per language and
run the full check suite from one recipe in both CI and a pre-commit hook (so
they never drift), add a deterministic agent-rules layer that also gates in CI
and an agentic review gate over each changeset, ship CLI binaries via
tag-triggered releases with checksummed install scripts, and scaffold the
community/governance files. License is the one
decision the agent must ask about: AGPL-3.0-or-later or Apache-2.0, nothing else.
The picks and the full checklist are in
[`principles/new-project-defaults.md`](principles/new-project-defaults.md).

## Language router

Detect the language, then read its file. Each maps the principles into the
dialect and adds what is unique to that language (tooling, concurrency model,
naming, project layout, idioms to reach for, anti-patterns to refuse).

| Language | File | Detect by |
|---|---|---|
| Rust | [`languages/rust.md`](languages/rust.md) | `*.rs`, `Cargo.toml` |
| TypeScript / JavaScript | [`languages/typescript.md`](languages/typescript.md) | `*.ts`, `*.tsx`, `*.js`, `tsconfig.json`, `package.json` |
| Go | [`languages/go.md`](languages/go.md) | `*.go`, `go.mod` |
| Python | [`languages/python.md`](languages/python.md) | `*.py`, `pyproject.toml`, `requirements.txt` |

For a language not listed, apply the universal core directly and follow the
project's existing conventions; the principles are designed to transfer.

## Precedence

Project instructions and existing code conventions win over this skill. If a
repo's `AGENTS.md`/`CLAUDE.md` or its established patterns conflict with a
principle here, follow the repo and say so. This skill is the default, not an
override.

## Provenance

Distilled from `leonardomso/rust-skills` (MIT), Matklad's Rust100k series, and
Alexis King's "Parse, don't validate" and "Names are not type safety", then
generalized beyond Rust.
