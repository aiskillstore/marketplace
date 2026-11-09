# Session Rules

Use this reference only when the user explicitly states that a rule should carry
forward within the current deck, for example “后续新增页面的标题继续使用蓝色”.
Do not create a session rule from a one-off experiment, an implicit preference,
or an ambiguous phrase.

`session-rules.json` is a current-deck working-memory artifact. It is not an
author profile, does not cross projects, and never overrides DeckKit hard
constraints or delivery gates.

## Deterministic Scope

Version `pptx-nova-session-rules/v1` deliberately supports only rules that can
be compiled and verified without free-form interpretation:

| Rule kind              | Supported action                                        | Verification                                     |
| ---------------------- | ------------------------------------------------------- | ------------------------------------------------ |
| `preserve-invariant`   | `slide-count`, `non-target-shapes`, `target-text-style` | Existing Edit Contract diff/style gates          |
| `future-element-style` | `slide-title.fontColor`, `summary-box.fillColor`        | Produced-object identity plus candidate PPTX XML |

The executable event vocabulary is limited to `any-edit`, `slide-added`, and
`element-added`. Human-readable explanations may be stored beside a rule, but
free text must not drive applicability.

## Lifecycle

1. Write `session-rules-draft.json` only from an explicit user quote or an
   auditable artifact.
2. Normalize it against the current PPTX revision:

   ```bash
   node <skill-root>/scripts/cli/edit/session-rules.mjs \
     --draft <run-dir>/session-rules-draft.json \
     --source current.pptx \
     --output <run-dir>/session-rules.json \
     --json
   ```

3. Add the optional relative pointer to `deck_lock.json`:

   ```json
   {
     "sessionRulesPath": "session-rules.json"
   }
   ```

4. Before an edit, write a structured `session-operation.json`, resolve active
   rules, and consume the generated contract overlay.
5. After the candidate passes every gate and is accepted, advance the rule file
   to the new revision. Do not advance after a failed or abandoned candidate.

   ```bash
   node <skill-root>/scripts/cli/edit/session-rules.mjs \
     --rules <previous-run>/session-rules.json \
     --source <accepted-candidate.pptx> \
     --output <next-run>/session-rules.json \
     --json
   ```

The stable `deckId` identifies the logical deck. `currentRevisionSha256` and
`parentRevisionSha256` form an auditable revision chain; a hash is never used as
the logical deck identity.

## Rule Shape

```json
{
  "schemaVersion": "pptx-nova-session-rules/v1",
  "deckIdentity": {
    "deckId": "customer-loyalty-deck"
  },
  "rules": [
    {
      "id": "rule-future-title-blue",
      "kind": "future-element-style",
      "status": "active",
      "lifetime": "current-deck",
      "trigger": { "event": "slide-added" },
      "target": {
        "slideScope": "future",
        "elementKind": "slide-title"
      },
      "action": { "fontColor": "0076A8" },
      "source": {
        "kind": "user-feedback",
        "turn": 3,
        "quote": "后续新增页面的标题继续使用蓝色"
      },
      "supersedes": []
    }
  ]
}
```

Only `active` rules execute. `candidate` rules preserve ambiguous observations
without affecting output. A replaced rule remains in history with
`status: "superseded"`; the new active rule lists its id in `supersedes[]`.
Two active style rules that set different values for the same event and element
kind are invalid and must be resolved explicitly.

## Operation Plan And Resolver

The operation plan declares facts the agent already knows while authoring the
patch. It must not ask the resolver to infer semantic roles from arbitrary shape
names or natural language.

```json
{
  "schemaVersion": "pptx-nova-session-operation/v1",
  "event": "slide-added",
  "slideCountDelta": 1,
  "targets": [
    {
      "id": "new-slide-title",
      "kind": "produced-object",
      "slide": 8,
      "elementKind": "slide-title",
      "shapeName": "S8_Title",
      "opIndexes": [1, 2],
      "changeCategories": ["shape", "text"]
    }
  ],
  "explicitOverrides": []
}
```

Use stable names for produced objects. DeckKit primitives already follow the
`S<slide>_<role>` convention; manual structural patches should do the same.

```bash
node <skill-root>/scripts/cli/edit/session-rules-resolve.mjs \
  --rules <run-dir>/session-rules.json \
  --operation <run-dir>/session-operation.json \
  --source current.pptx \
  --output <run-dir>/session-rules-resolution.json \
  --strict --json
```

Read `agentGate.nextAction`:

| Value                             | Meaning                                                   |
| --------------------------------- | --------------------------------------------------------- |
| `continue-without-session-rules`  | No active rule applies; continue with the normal workflow |
| `continue-with-contract-overlay`  | Only preserve rules apply; merge the overlay              |
| `write-rule-compliant-patch`      | Produced-object style targets must be implemented         |
| `refresh-session-rules-revision`  | The rules are bound to stale source bytes                 |
| `block-and-request-user-decision` | A rule conflicts with the requested operation             |

A `slide-count` preserve rule conflicts deterministically with non-zero
`slideCountDelta` and blocks before patch execution.

## Explicit Current-Request Override

The current explicit user request has higher priority than a session rule, but
the override must remain auditable:

```json
{
  "explicitOverrides": [
    {
      "ruleId": "rule-future-title-blue",
      "source": {
        "kind": "current-user-request",
        "quote": "这次新增页标题改用红色"
      }
    }
  ]
}
```

Do not suppress a rule without the current user quote.

## Edit Contract Integration

Pass the successful resolution to the contract normalizer:

```bash
node <skill-root>/scripts/cli/edit/contract.mjs \
  --draft <run-dir>/edit-contract-draft.json \
  --source current.pptx \
  --session-rules-resolution <run-dir>/session-rules-resolution.json \
  --output <run-dir>/edit-contract.json \
  --json
```

The normalizer:

- merges rule-owned produced-object targets;
- merges preserve, allowed-change, and evidence requirements;
- binds the rules, operation, and resolution SHA-256 values;
- increases required target coverage instead of treating rule work as optional.

The ordinary `<skill-root>/scripts/cli/edit/contract-gate.mjs --strict` then verifies:

- the three bound session artifacts are unchanged;
- the rules still match the contract source revision and deck id;
- dry-run ops resolve the produced object identity;
- final inspect contains the declared object on the declared slide;
- candidate PPTX bytes contain the required font/fill value.

Candidate-byte checks follow the resolved numeric shape ID from final inspect;
an ID lookup never falls back to another object with the same name. Name-only
targets must resolve uniquely on the declared slide. Bind an inspected ID when
names collide; ambiguous identity blocks the gate instead of accepting the
first matching object.

Every applicable rule is reported in `sessionRuleResults[]` as `satisfied` or
`blocked`. A failed style postcondition returns
`nextAction: "apply-session-rules"`; stale bindings return
`nextAction: "refresh-session-rules-resolution"`.

## Zero-Friction Rule

If no `sessionRulesPath` exists, do not create placeholder session artifacts.
If a rule file exists but no active rule applies, the resolver must return
`continue-without-session-rules`; do not add targets, evidence, confirmation, or
user-visible ceremony.
