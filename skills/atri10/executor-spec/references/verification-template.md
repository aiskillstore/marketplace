# Verification Strategy Template

Path: `<initiative>/verification/INIT-NNNN-VRFY-nn-<topic-slug>.md`

`executor-verification` executes this document row by row and can only
report what a row told it to observe. Every vague cell here becomes an
unverifiable claim there.

## Skeleton

````markdown
---
id: INIT-0004-VRFY-01
initiative: INIT-0004
kind: verification
title: Cell placement acceptance strategy
status: draft
created_at: <UTC from an executed command>
updated_at: <same>
supersedes: null
superseded_by: null
spec: INIT-0004-SPEC-01
criteria_count: 9
evidence_types: [unit, integration, manual, smoke, static]
---

# Cell placement — verification strategy

## How to run this

<Anything the executor needs once, before any row: the working directory,
how to start dependencies, which fixture data to load. Name real commands.
If a row needs a running service, the command that starts it goes here,
not repeated in every row.>

```bash
cd services/placement
docker compose up -d postgres      # placement rows land here
npm ci
```

## Criteria

| ID | Criterion | Method | Procedure | Evidence | Status |
|---|---|---|---|---|---|
| V01 | R01 deterministic placement | unit | `npx vitest run test/placement/deterministic.test.ts` | `3 passed`, exit 0 | pending |
| V02 | R02 unknown cell rejected | integration | `curl -s -o /tmp/b -w '%{http_code}' localhost:8080/place -d '{"tenant":"t1","cell":"cell-9999"}'` then `jq -r .error /tmp/b` | `422` then `unknown_cell` | pending |
| V03 | R02 no placement recorded on rejection | integration | `psql -Atc "select count(*) from placement where tenant='t1'"` after V02 | `0` | pending |
| V04 | R09 isolation enforced in service | unit | `npx vitest run test/placement/isolation.test.ts` | `5 passed`, exit 0 | pending |
| V05 | R11 latency at 10k tenants | integration | `node scripts/loadgen.js --tenants 10000 --report p99` | p99 `<= 50` ms printed | pending |
| V06 | C01 Node floor | smoke | `node --version` | a version string `>= 20.11.0` | pending |
| V07 | C02 no runtime dependency outside `@platform/*` | smoke | `jq -r '.dependencies\|keys[]' package.json` | every line begins `@platform/` | pending |
| V08 | C03 cell identifier pattern | unit | `npx vitest run test/placement/cell-id.test.ts` | `4 passed`, exit 0 | pending |

`Status` stays `pending` until `executor-verification` runs the row. This
document does not claim results; it defines how results get produced.

## Manual criteria

Manual rows carry numbered steps with one observation each, in full,
because a manual row a stranger cannot perform cold is a vague row.

### V09 — R14 operator can evict a cell from the console

**Method:** manual

**Procedure:**

1. Open `http://localhost:3000/cells` — the table lists `cell-1` … `cell-4`.
2. Click **Evict** on the `cell-3` row — a confirm dialog appears naming
   `cell-3`.
3. Confirm — within 2 seconds the `cell-3` row's status reads `draining`.
4. Reload the page — the status still reads `draining`.
5. Run `psql -Atc "select action,target from audit order by id desc limit 1"`
   — output is `cell.evict|cell-3`.

**Evidence:** step 3 shows `draining`, step 4 confirms it persisted, step
5 prints `cell.evict|cell-3`.

**Status:** pending

## Coverage

Every `R<nn>` and every `C<nn>` in the spec appears at least once. This
table is how the human confirms that at the gate.

| Spec item | Criteria |
|---|---|
| R01 | V01 |
| R02 | V02, V03 |
| R09 | V04 |
| R11 | V05 |
| R14 | V09 |
| C01 | V06 |
| C02 | V07 |
| C03 | V08 |

A spec item with no criterion is a hole: the requirement exists, and
nothing will ever prove it. Fix it here, before the gate.
````

## Row rules

| Column | Rule |
|---|---|
| ID | `V<nn>`, sequential, never renumbered — plans and verdicts cite them |
| Criterion | The `R<nn>` or `C<nn>` proven, plus its short name |
| Method | `unit` \| `integration` \| `manual` \| `smoke` \| `static`, matching `evidence_types` |
| Procedure | The exact command, or numbered manual steps. Copy-paste correct |
| Evidence | The observed output that counts as proof |
| Status | `pending` until executed |

**One row per requirement, minimum.** A requirement needing two methods —
a unit test for the calculation and a manual check of the rendered result
— gets two rows. **Every global constraint gets a row too:** a version
floor nobody checks is a version floor nobody meets.

## Evidence rules

Acceptable evidence names something a second person could observe
independently: an exit code, a specific count, a named field value, a
named log line, a named on-screen state.

| Disqualified | Replace with |
|---|---|
| "tested thoroughly" | The command and its expected output |
| "works" / "behaves correctly" | The specific assertion that holds |
| "tests pass" | Which test file, which test name, how many assertions |
| "verified manually" | Numbered steps and the expected state after each |
| "no errors" | Exit code 0 plus the named absence you checked for |
| "looks right" | The named field value or rendered string |
| "the API returns success" | The exact status code and the exact body field |

## Negative and boundary rows

A requirement stating a rejection, a limit, or an error response needs a
row proving the *failure* path.

| Requirement shape | Required row |
|---|---|
| Rejects X with status S | Send X, observe S — not "valid requests still work" |
| Up to N items | Observe behaviour at N and at N+1 |
| Times out after T | Observe the timeout firing, and observe it not firing under T |
| Emits log line L | Observe L present after the trigger, and absent without it |

V02 and V03 above are one requirement split across two rows for exactly
this reason: the status code and the absence of a side effect are two
separate observations, and a rejection that still writes a row is a bug
that a single row would miss.

## Choosing a method

| Method | Use when | Evidence looks like |
|---|---|---|
| `unit` | The behaviour is a function of inputs, no I/O | Test file, test count, exit 0 |
| `integration` | The behaviour crosses a boundary — HTTP, DB, filesystem, process | Status code, row count, file content |
| `manual` | A human must observe a rendered state or perform a real interaction | Numbered steps, one observation per step |
| `smoke` | Proving the thing runs at all, or a constraint on the environment | Command output, version string, exit 0 |
| `static` | The requirement is a property of the artifact itself — a signature, a config value, a schema — provable without running it | The cited file:line, or the linter/type-checker command output |

Prefer the cheapest method that actually observes the requirement. A unit
test that mocks the boundary the requirement is about proves nothing —
that requirement is `integration`.

## Before writing the file

1. `spec` names the current, non-superseded spec ID.
2. `criteria_count` equals the number of rows plus manual criteria blocks.
3. `evidence_types` lists only methods actually used.
4. Every `R<nn>` and `C<nn>` in the spec appears in the coverage table.
5. Every procedure is copy-paste correct against the real repository —
   paths, commands, and flags checked, not assumed.
6. No row's evidence column contains a phrase from the disqualified list.
