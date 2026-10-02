---
name: troubleshooting-motoko-migrations
description: >-
  Deep reference for when the migration chain misbehaves — upgrade
  compatibility errors you cannot explain, migration files you cannot write,
  a project converted from legacy persistence, or a request to remove the
  chain. Load only when the rules in migrating-motoko-actors do not explain what
  you are seeing.
version: 0.1.5
compatibility:
  toolchain:
    moc: ">=1.11.2"
  mops:
    core: ">=2.5.0"
caffeineai-subscription: [none]
---

# Troubleshooting Motoko Migrations

Reference for the failure modes of the mops-managed migration chain (`migrations/`).

**Do not load this for routine work.** Writing a migration, deciding implicit vs explicit, or naming a new file is covered by `migrating-motoko-actors` — that skill's rules are sufficient for the normal path. Come here when:

- a compatibility or migration diagnostic does not match what you see in `main.mo`
- a write to a migration file fails, or you are tempted to rename/delete one
- the first file in the chain has a non-empty `OldActor` and you are unsure whether that is a bug
- the task asks you to remove migrations, restore inline initializers, or go back to `(with migration = ...)`
- `mops check` complains about a state shape that is not in the current source

## How the runtime decides what to run

- The whole chain is compiled **into** the backend wasm. There are no separate migration artifacts — changing any migration file changes the wasm.
- Applied migrations are tracked **by module name** (the filename without `.mo`) in the canister's persistent metadata.
- On **upgrade**, the runtime replays only the migrations that module name says have not been applied yet. Deploying onto a canister several versions behind replays all the missing steps in one upgrade — you never need intermediate deploys to "catch up".
- On **fresh install**, every file in the chain replays in lexicographic order. Every migration ever added runs on every fresh install of the project, forever.

Two consequences drive most of the rules in this skill:

- **Renaming a migration changes its identity.** The runtime would treat the renamed file as never applied and replay it against state that no longer matches — or skip the work the old name recorded. Filenames are permanent.
- **Editing an applied migration is invisible to a canister that already ran it.** The runtime skips it by name, so an edited body never executes. A stable field you add there is never initialized, and the canister traps at runtime reaching for it (`IC0503`, "missing migration var" class). Fix forward with a new migration instead.

## What the checker compares against

`mops check` validates your chain against the **deployed** canister's stable signature (its `.most` snapshot), not against local git history. So:

- Diagnostics can name fields that are no longer anywhere in your source — they come from the deployed version.
- The one-pending-migration limit counts migrations **not yet deployed**. Files that are already live do not count toward it.
- The stable-signature major in a `.most` header identifies the persistence model: `1` classic, `3` legacy inline `(with migration = ...)`, `4` enhanced migration chain. Once a project reaches `4` it never goes back (see [EM is one-way](#em-is-one-way)).

## Diagnostics you may hit

| Diagnostic                                                | What it actually means                                                                                       | Action                                                                                                     |
| --------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------- |
| `M0250` initialized stable field                          | A stable actor field has an inline initializer, which the chain (not the actor body) must supply              | Reduce it to a typed declaration; move the initializer expression into the pending migration's `NewActor`   |
| `M0254` / `M0267` initial actor requires field            | `main.mo` declares a stable field that no migration supplies. `M0267` is the same problem when the deployed signature cannot account for it either | Add the field to the pending migration's `NewActor` with a value computed from `OldActor` or a well-defined default |
| `M0170` compatibility error                               | The new actor is not stable-compatible with the deployed signature                                           | Add (or extend) the pending migration so the transformation is explicit                                     |
| `M0255` stable signature downgrade                        | The build would move the canister from an enhanced chain back to an older persistence model — usually because the chain or the mops migrations config was removed | Restore what was removed; there is no supported downgrade                                                   |
| Chain start does not match the baseline                   | The first migration's `OldActor` does not describe the state the canister actually holds — the classic case is a converted project where the chain starts from the legacy shape, not `{}` | See [Converted projects](#converted-legacy--enhanced-projects); do not rewrite `OldActor` to `{}`           |
| `M0268` migration directory disagrees with deployed history | An already-applied migration was edited, deleted, or reordered, so the chain no longer matches the history recorded by the stable baseline. Surfaces at `mops build` (which folds the deployed baseline via `--stable-baseline`) and can pass `mops check` when `check-limit` trims that migration out | Restore the applied migration to exactly what was deployed and express further changes as a new migration. Only the oldest migrations may be trimmed; an applied migration in the middle cannot be removed |
| `M0014` effectful actor body (older toolchains)           | Initialization work sitting in the actor body                                                                | Keep the actor body static — see [Static actor body](#static-actor-body)                                    |
| `IC0503` missing migration var (runtime, after deploy)    | A stable field never received a value — typically an edited or renamed applied migration, or a field added without a migration | Add a new migration that supplies the field; never repair by editing the old file                          |
| `IC0505` invalid custom section (install only, build and check pass) | The chain's stable-type history has outgrown the platform's custom-section limit | Nothing local fixes it — stop adding migrations and report it; see [Why chains must stay short](#why-chains-must-stay-short) |

Write failures on a migration file are not a tooling bug — see the next section.

## Frozen migration files

On platforms that freeze deployed migrations, each one is made read-only after a successful deploy and write tools reject it by its mode bits.

- **Do not** `chmod` it, delete it, rename it, or route around the write failure. The freeze encodes a runtime invariant, not a policy preference.
- A migration that is still **pending** (not yet applied) is not frozen: edit that one rather than adding a second file for the same change.
- If the change you need belongs conceptually in a frozen migration, express it as a new migration that transforms the current state into the shape you want. History is append-only.

## Converted (legacy → enhanced) projects

Some enhanced-migration projects were not created that way — they were converted in place from legacy inline-migration persistence, with live data preserved. In such a project:

- The **first file in the chain is typically an identity migration** whose `OldActor` is the pre-conversion stable shape and whose `NewActor` passes the same data through unchanged. This is correct. Do not "simplify" it to `OldActor = {}` and do not re-seed the fields — that would discard live state.
- `OldActor = {}` is only right when the chain genuinely starts from an empty canister, i.e. the project used the chain from creation.
- The pre-conversion history stays load-bearing: fresh installs of a converted project replay from the last legacy schema, not from `{}`. Never try to prune, flatten, or "clean up" the chain to make it start at `{}`.
- Diagnostics about a field that exists only in the pre-conversion shape are expected on the first migration and are handled by the platform's build configuration. Do not restructure the chain to silence them.

A project can also inherit such a chain without having been converted itself — forking or remixing a converted project copies the chain as-is, first migration included. The rule is the same either way, and it is readable straight off the chain: **a non-empty `OldActor` in the earliest file means state predates the chain, so that file is correct as written.**

## Protected configuration

Where a hosting platform owns the mops migrations config — the `[canisters.<name>.migrations]` section, its `chain` path, and `check-limit` — you cannot add, remove, or alter it, and the tooling will reject attempts.

- **Never raise or drop `check-limit` to clear a "too many pending migrations" error.** The fix is always to fold the extra changes into a single pending migration. Every file the error lists has not been applied yet, so any of them can be edited.
- **The chain directory is whatever `chain = ...` says.** It is normally `src/backend/migrations`, but a project imported under a non-default canister name can differ. Read the mops config rather than assuming the path.
- If the migrations section appears to be missing from a project that has a chain, do not re-add it yourself; report the inconsistency.

## EM is one-way

Once a project uses the migration chain there is no supported path back to legacy persistence. Independent mechanisms enforce this:

1. The persistence model is decided per project and is sticky — nothing re-evaluates it later.
2. The compiler rejects a signature downgrade (`M0255`), and a legacy wasm deployed over an enhanced canister traps at runtime. Signature versions only move forward.
3. Applied migrations are identified by module name, so history cannot be rewritten by editing or renaming files — and on platforms that freeze deployed migrations, it cannot be rewritten at all.
4. Fresh installs of a converted project permanently depend on the pre-conversion history.

So if a task asks you to delete the `migrations/` directory, restore inline initializers on stable fields, or reintroduce `(with migration = ...)`, say plainly that it is not possible for this project and offer the forward-only equivalent: a new migration that reshapes state toward what the user actually wants.

## Why chains must stay short

The one-migration-per-deployed-version rule is not bureaucratic. A long chain eventually becomes **undeployable, and the failure is unrecoverable**:

- The compiled wasm carries a custom section encoding the entire stable-type history. It grows with every migration **and** with the size of the stable types themselves, until it crosses the platform's 1 MiB limit on those sections. With modest stable types that happens in the high hundreds of files; with richer types, proportionally sooner.
- **`mops build` and `mops check` still succeed at that point** — only the install is rejected (`IC0505`, invalid custom section). A green check is not evidence that the chain is deployable, and no redeploy or retry recovers it: the oversized section is baked into the artifact.
- Every file replays on every fresh install, forever, inside a **single message**. Garbage collection only runs at message boundaries, so every intermediate state stays live for the whole replay — a data-heavy migration can exhaust the memory limit at a far smaller chain length than the section cap implies.
- Fresh installs recurse once per step, so call-stack depth is proportional to chain length.
- Wasm size and compile time grow with every step, and the `.most` signature serializes the whole chain.

Nothing in the toolchain caps chain length, so the one-migration-per-version discipline is the only thing keeping a project away from that cliff: fold changes into the pending migration, keep stable types lean, and never add a migration whose body would just be `old`.

## Static actor body

The actor body must not do work. Stable fields are typed declarations; their values come from the chain.

Older toolchains rejected any effectful actor body outright, and that compiler check has since been relaxed for transient bindings — but the rule stands regardless of whether the compiler complains, because **top-level seeding re-runs on every upgrade** and would overwrite live state.

Initialization belongs in exactly two places:

- a migration function, which runs once per canister at install/upgrade time, or
- idempotent logic invoked lazily during normal operation (e.g. inside an update method that checks whether the work is already done).

## When you cannot resolve it

Do not create room to proceed by relaxing protected configuration, deleting or renaming history, or rewriting a frozen file. Those turn a build failure into data loss. If the chain and the deployed signature genuinely disagree in a way none of the above explains, stop and report the mismatch: which fields the checker names, what the latest migration's `NewActor` declares, and what `main.mo` declares.

## Related skills

- `migrating-motoko-actors` — how to author migrations (the normal path)
- `writing-motoko` — language reference, actor and mixin rules, core library
