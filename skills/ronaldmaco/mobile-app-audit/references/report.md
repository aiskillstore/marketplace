# Findings, report and audit log

## Finding format
```
[ID] [Severity] Title
Status: Verified | Suspected
Where: file:line (endpoint, config, CMS data, CDN rule if any)
What the user sees: one sentence, user terms
Cause: concrete mechanism
Trigger: exact conditions (state, network, timing, data, region, OS, build)
Evidence: files / log lines / requests / oracle output
Impact map: rows checked, rows failing, rows not tested (reason)
Fix: smallest change, what stays the same visually, what the review gate found
Test: regression tests added or manual case id
Also in: sibling apps / platforms / screens with the same pattern
Delivery: what must ship (app build, OTA, backend deploy, CMS data, cache purge) and who owns it
```
Before a finding is reported as **Critical** or **High**, write one "Try to refute" paragraph: the strongest reason it might not be a bug (handled elsewhere, unreachable, the library or server already enforces it, debug-only) and the check that ruled that out. If it is not ruled out, the finding stays Suspected or its severity drops.

Severity: **Critical** (crash, data loss, security exposure, cannot sign in/use, store rejection), **High** (feature broken or wrong data), **Medium** (fails under realistic conditions, silent failures, notable performance/accessibility gaps), **Low** (cosmetic, copy, edge case).

## Report
1. Summary: mode, scope, how it was checked (static/backend/oracle/device/telemetry), what was not covered and why.
2. Findings, most severe first.
3. Coverage table: every inventory item or impact map row -> OK / finding id / not tested (reason) / not measured (reason). "Not tested" and "not measured" are never counted as OK.
4. Fix order and what each fix needs to reach users.
5. Open questions and actions for other owners (backend, CMS, store).
6. When a previous audit log exists: each finding marked **new**, **fixed** or **persistent since <date>**, with before/after screenshots for visual changes (agent-device `diff screenshot --baseline <file>`, or ImageMagick `compare -metric AE before.png after.png diff.png`).
7. Mode D and G: the future-risk table (`references/future-risk.md`). Mode F: the autopsy block (`references/autopsy.md`).

Write to the user in their language, short: what was wrong, what changed, how it was proven, what is pending.

## Audit log (resume without re-auditing)
Keep `docs/audit/<YYYY-MM-DD>-<scope>.md` in the app repo (or the work folder if writing to the repo is not allowed): mode, build audited, inventory, impact maps, coverage table, findings with status, evidence paths, oracle scripts, next steps. At the start of any audit, read the latest log first and continue from it. Ask before committing it.
