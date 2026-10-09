# Optional tracker CLI

## Purpose and limits

`python3 <skill-root>/scripts/gauntlet.py --help` lists commands. Python 3.10+ with the standard-library `sqlite3` module is required; there are no third-party dependencies. The helper writes only its specified SQLite ledger. It never runs project code, installs packages, contacts the network, or spawns agents. All evidence and approvals are **attestations supplied by the caller**, not authenticated facts.

Use one orchestrator as ledger owner. SQLite transactions serialize accidental concurrent record requests, and an invalid event rolls back its whole batch. State belongs in a private, trusted directory outside the installed skill. Existing directories are not permission-hardened automatically; do not use an attacker-writable path. The database file cannot be a symlink, but this is not full filesystem TOCTOU hardening. Do not open a ledger supplied by an untrusted party.

## Initialize

```sh
python3 /path/to/gauntlet/scripts/gauntlet.py init \
  --db /private/review/run.sqlite3 \
  --scope 'The requested change and its direct consumers' \
  --revision 'actual-commit-plus-scoped-worktree-digest' \
  --mode repair --tier standard \
  --lenses correctness-api,reliability-data \
  --checks baseline,regression --verification execution
```

Use your actual private path and snapshot. Mode defaults to **review**, tier to **standard**, verification to **execution**, required checks to **baseline**, and the core lens is always present. `--max-rounds N` can set an explicit initial cap from 1 to 20. A cap too small to meet the tier's clean-pass requirement intentionally results in a partial outcome; the helper does not silently lower the standard.

## Record events

Write a UTF-8 JSON event, or an array of events, to a file and run:

```sh
python3 /path/to/gauntlet/scripts/gauntlet.py record \
  --db /private/review/run.sqlite3 --input event.json
```

Alternatively use `--input -` for stdin or `--event '<JSON>'` with correct shell quoting. Files/stdin are safer for long text or untrusted characters. Input is capped at 1 MiB and batches at 100 events. Unknown event fields, duplicate JSON keys, non-finite JSON numbers, and invalid transitions are rejected. Keep long logs outside the ledger and store their paths plus concise results.

### Tasks and review-contract expansion

```json
{"type":"task","id":"core","status":"done","evidence":"Requirements traced to file:line; evidence/path.md"}
```

A task can be `pending`, `done`, `blocked`, or `not_applicable`. Done requires evidence. Blocked/excluded requires `reason`. Core cannot be excluded. Every initial lens has a task with the same ID.

```json
{"type":"add_task","id":"cancel-after-commit","title":"Inspect cancellation after commit","lens":"reliability-data"}
```

```json
{"type":"add_lens","id":"security-privacy","reason":"Discovered a cross-tenant authorization boundary"}
```

```json
{"type":"require_check","id":"tenant-isolation"}
```

Additions expand the acceptance contract, require corresponding work, and make the current round non-clean. There is no command to remove required checks or quietly downgrade the verification method/risk tier. Get the initial plan roughly right rather than using the helper as a log of every tiny step. For ordinary investigative notes use `note`.

### Findings

```json
{"type":"finding","id":"F001","status":"confirmed","severity":"medium","title":"Duplicate durable effect","location":"src/worker.py:84","claim":"A repeated operation ID must not write twice","evidence":"Actual reproduction and evidence path"}
```

New findings start as `candidate` or `confirmed`. Candidates may lack evidence; confirmed findings require it. Every finding needs a stable ID, title, severity, location, and claim. The repair flow is `confirmed → patched → verified`. Candidate findings cannot jump directly to repaired. Substantiate them first.

After applying an authorized fix, record its actual new snapshot **before** claiming a repair:

```json
{"type":"target","revision":"actual-new-snapshot-digest","reason":"Applied F001 invariant fix"}
```

This invalidates all checks and task completions and reopens previously verified fixes as patched. Previously accepted risks reopen as confirmed with the old approval cleared; read-only confirmed findings reopen as candidates for substantiation against the new snapshot. A target change cannot count as a clean re-attack. Re-run required checks and repeat affected review work.

```json
{"type":"finding","id":"F001","status":"patched","root_cause":"Specific missing invariant at its owner","fix":"Actual change and affected sites","regression":"Original failure evidence, post-fix test, and neighboring case"}
```

Record a genuinely executed check before verifying:

```json
{"type":"check","id":"regression","kind":"execution","result":"pass","command":"The exact command actually executed","exit_code":0,"evidence":"Observed result and log path"}
```

```json
{"type":"finding","id":"F001","status":"verified","verification":["regression"]}
```

Verification references named passing checks from the current round and snapshot. Review-only mode rejects patched/verified repair records. A template JSON event does not establish that a check happened; replace its prose with actual observations.

Dismiss a false positive with `status: dismissed`, fresh counterevidence in `evidence`, and a `reason`. Accept a confirmed low/medium residual finding only with `status: accepted`, an explicit external `approval` reference, and `reason`. High/critical findings cannot be waived here. Severity changes require a reason. Accepted/dismissed findings can be reopened, with a reason, to confirmed/candidate respectively. Approval text is not authenticated by the script; the host and orchestrator must verify it.

### Checks

`kind` is `execution` or `inspection`; `result` is `pass`, `fail`, or `blocked`. Every check requires `command` (or inspection procedure) and observed `evidence`. Executed pass/fail checks require an integer `exit_code`; a pass must use 0. Blocked/inspection checks omit `exit_code`. Inspection does not satisfy execution-required gates. Report pre-existing failures in notes and keep the acceptance decision explicit; do not record a fake pass to get around one.

Checks are automatically bound to the current snapshot and round. Required checks must be current to close cleanly. A relevant failing additional check also blocks closure. Re-recording a check replaces its latest result but preserves the previous event in the audit history.

### Close and continue

```json
{"type":"close_round","angle":"A distinct counterexample family actually investigated","independence":"solo-role-pass","summary":"Coverage, outcome, limitations, and evidence references"}
```

Independence is `subagent`, `solo-role-pass`, or `human`; choose the truth. Closing a round records it even when incomplete; it does not turn blockers into a pass. The helper derives clean/non-clean, rather than accepting a caller's `clean: true` assertion.

```json
{"type":"next_round","reason":"Unresolved mechanism plus the concrete next attack strategy"}
```

A round must close before the next can begin. Repeated angle strings do not count as distinct consecutive clean passes; semantically duplicate strategies also must not count, though the helper can only compare normalized text. Round budgets cannot silently grow.

```json
{"type":"budget","max_rounds":8,"approval":"Specific user approval reference","reason":"New strategy and scope of the extension"}
```

```json
{"type":"note","text":"Known limitation, authorization reference, or next action"}
```

## Inspect and export

`status --db ...` emits a compact JSON summary. `snapshot --db ...` emits the full current state (not the append-only event history). `report --db ...` emits Markdown to stdout; redirect to an approved path when desired. `gate --db ...` computes completion. State format is versioned at schema 1; unsupported schemas are rejected, not migrated silently.

Exit codes: **0** successful command / completed gate; **2** invalid input, invalid state, I/O or database error; **3** gate blocked; **4** gate budget exhausted. `record` succeeding means the event was stored, **not** that the review passed. `status` can show blocked while returning 0 because reading status succeeded.

The helper does not enforce wall-clock, token, tool-call, or sub-agent budgets; the orchestrator must track those separately. It does not prove the supplied target identifier covers the real worktree. It is a guard against bookkeeping mistakes, not a replacement for host controls or honest verification.
