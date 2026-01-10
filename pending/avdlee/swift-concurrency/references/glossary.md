# Glossary

Concise definitions of key Swift Concurrency terms used throughout this skill.

## Actor isolation

A rule enforced by the compiler: actor-isolated state can only be accessed from the actor's executor. Cross-actor access requires `await`.

## Global actor

A shared isolation domain applied via attributes like `@MainActor` or a custom `@globalActor`. Types/functions isolated to the same global actor can interact without crossing isolation.

## Default actor isolation

A module/target-level setting that changes the default isolation of declarations. App targets often choose `@MainActor` as the default to reduce migration noise, but it changes behavior and diagnostics.

## Strict concurrency checking

Compiler enforcement levels for Sendable and isolation diagnostics (minimal/targeted/complete). Raising the level typically reveals more issues and can trigger the “concurrency rabbit hole” unless migrated incrementally.

## Sendable

A marker protocol that indicates a type is safe to transfer across isolation boundaries. The compiler verifies stored properties and captured values for thread-safety.

## @Sendable

An annotation for function types/closures that can be executed concurrently. It tightens capture rules (captured values must be Sendable or safely transferred).

## Suspension point

An `await` site where a task may suspend and later resume. After a suspension point, you must assume other work may have run and (for actors) state may have changed (reentrancy).

## Reentrancy (actors)

While an actor is suspended at an `await`, other tasks can enter the actor and mutate state. Code after `await` must not assume actor state is unchanged.

## nonisolated

Marks a declaration as not isolated to the surrounding actor/global actor. Use only when it truly does not touch isolated mutable state (typically immutable Sendable data).

## nonisolated(nonsending) (Swift 6.2+ behavior)

An opt-out to prevent “sending” non-Sendable values across isolation while still allowing an async function to run in the caller’s isolation. Used to reduce Sendable friction when you do not need to hop executors.

## @concurrent (Swift 6.2+ behavior)

An attribute used to explicitly opt a nonisolated async function into concurrent execution (i.e., not inheriting the caller’s actor). It is used during migration when enabling `NonisolatedNonsendingByDefault`.

## @preconcurrency

An annotation used to suppress Sendable-related diagnostics from a module that predates concurrency annotations. It reduces noise but shifts safety responsibility to you.

## Region-based isolation / sending

Mechanisms that model ownership transfer so certain non-Sendable values can be moved between regions safely. The `sending` keyword enforces that a value is no longer used after transfer.


