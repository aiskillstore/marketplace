# Feature Audit Evidence Classification

Classify roadmap items from observed evidence, not intent, filenames, or optimistic status labels.

## Evidence hierarchy

Prefer stronger, directly relevant evidence:

1. Verified runtime or generated-contract evidence from the audited revision and authorized target environment.
2. Passing tests that exercise the roadmap acceptance condition.
3. Executable source plus module wiring, configuration, schema/migration, and caller evidence.
4. Static source or configuration without execution proof.
5. Comments, TODOs, issue text, commit messages, or conversation context.

Lower evidence may locate work but cannot overrule a contradictory higher-level observation. Record missing runtime access rather than simulating production proof.

## Primary category rules

### ✅ Implemented

Use only when the roadmap item is present, wired into the expected path, consistent with current standards, and supported by the strongest safely available validation. State any unverified rollout or environment boundary.

Source existence alone is insufficient when the roadmap requires migration, activation, rollout, or live behavior.

### ❌ Missing/Not Implemented

Use when a required item or necessary integration point is absent, only a stub/TODO exists, or the observed work is partial and the unfinished sub-item can be named. Support absence with searched symbols, paths, callers, wiring, tests, configuration, and expected integration points.

Do not classify an unavailable external check as missing code unless the roadmap specifically requires evidence that should exist in the repository.

### ⚠️ Legacy Code

Use when an older implementation remains active and the roadmap or current project standard explicitly requires migration, replacement, or retirement. Identify both the legacy path and the target path.

Old-looking syntax, age, or a deprecated library is not enough without project/version evidence and feature impact.

### 🛑 Bugs & Blockers

Use for verified incorrect behavior, broken wiring, contradictory contracts, failing relevant checks, or a prerequisite that prevents completion or reliable validation. Distinguish:

- **Bug:** implemented behavior contradicts the roadmap, contract, or verified runtime expectation.
- **Blocker:** missing authorization, dependency, credential, environment, decision, rollout, or external state prevents the next roadmap outcome.

Include the smallest reproduction or observation and explicit exit evidence.

## Avoid double-counting

- Assign one primary category per normalized item.
- Split compound roadmap items when implementation and rollout have different states.
- Put an implemented source change under **Implemented** and its unperformed production rollout under **Bugs & Blockers** as a separate rollout sub-item.
- Do not list the same missing item again as a blocker unless the blocker is a distinct prerequisite.
- Do not promote a suspicion to a bug. Record it in the item's evidence as `not verifiable` and state the next safe check.

## Claim contract

Every entry must answer:

- **Requirement:** What exact roadmap target is being evaluated?
- **Observed:** What state exists at the audited revision?
- **Evidence:** Which path/line, command/result, contract, or runtime observation proves the claim?
- **Impact:** What roadmap outcome is satisfied, delayed, unsafe, or incorrect?
- **Next proof:** What validation confirms completion or clears the blocker?
