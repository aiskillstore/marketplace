# Agent Memory

Every InsForge project has built-in agent memory: a platform-managed store of durable facts, decisions, preferences, and references that survive across sessions. It exists to solve the forgetting problem - the next session (or another agent) should not have to rediscover what this one already learned.

## Commands

```bash
npx -y @insforge/cli memory list                  # title index of stored memories (cheap - no AI call)
npx -y @insforge/cli memory recall "<query>"      # semantic + keyword recall; --scope, --limit, --threshold
npx -y @insforge/cli memory remember "<content>"  # store a memory; --kind, --title, --scope, --source
npx -y @insforge/cli memory remember --file <f>   # extract durable memories from a transcript/notes file
```

All commands honor `--json`.

## The workflow

**At the start of every non-trivial task** - check what past sessions already learned:

```bash
npx -y @insforge/cli memory list
```

This is cheap (no LLM or embedding call). Scan the titles; if any look relevant, recall the details before designing or debugging:

```bash
npx -y @insforge/cli memory recall "how are snippet tags filtered"
```

**When you make a decision, hit a gotcha, or change something** - record it at the moment it happens, not at the end of the session:

```bash
npx -y @insforge/cli memory remember \
  --kind decision --title "Tags as text[] not join table" \
  "Snippet tags are a text[] column with a GIN index, not a join table. Chosen because tags are free-form per owner with no shared vocabulary; revisit if tag analytics are needed."
```

## Kinds

| Kind | Use for | Example title |
|------|---------|---------------|
| `fact` | How something is | "Webhook retries are capped at 3" |
| `decision` | What was chosen and **why** | "Tags as text[] not join table" |
| `preference` | How the user wants things done | "Migrations only, never raw DDL in prod" |
| `reference` | Where something lives | "Stripe staging secret location" |

These four are the only valid `--kind` values. There is no `gotcha` kind: a gotcha is content, not a kind - store it as `fact` (or `decision` when it records a choice you made because of it).

## What to store

- Decisions **with their rationale** - the "why" exists nowhere in the code and is the highest-value recall.
- Non-obvious gotchas and behaviors you had to discover (cascade semantics, insert-format quirks, which key to use where) - store these as `--kind fact`.
- Where secrets, dashboards, and external resources live.
- Reversals: "we changed X to Y after Z" - memory keeps the current truth plus the history of why it changed.

Write one atomic memory per fact. A well-titled, self-contained sentence or two recalls far better than a paragraph of mixed notes.

## What NOT to store

- Anything derivable from the code or schema itself (recall returns nothing useful that `db tables` wouldn't).
- Transient task state - a failing test you are about to fix, scratch values, in-progress TODOs.
- Things the user merely asked about. Store what is true about the project, not what was discussed.

Memory is for what the next session cannot reconstruct.

## Behavior notes

- **Idempotent by design**: re-remembering a known fact reconciles to a no-op; a contradicting fact updates the existing memory in place (no duplicates). When the truth changes, just `remember` the new truth.
- **Transcript mode** (`--file`): the server extracts only durable facts and skips transient chatter; you do not need to pre-clean the file.
- **Scopes** (`--scope`): memories are partitioned logically (default project scope). Use a scope per agent or per feature area when memories should not cross-contaminate, e.g. `--scope build:snippet-vault`.
- **Empty recall is a feature**: if nothing relevant is stored, recall returns nothing rather than a forced low-confidence match. Do not lower `--threshold` to make results appear.
