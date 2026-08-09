---
name: universal-audit
description: 'Audit software releases with unforgiving standards. Use when soft approvals or incomplete scope could create deployment risk. Execute a full-lifecycle audit across fifteen core domains, including security, architecture, UX, and privacy. Apply deterministic scoring, evaluate hard evidence, and enforce release gates with hard-stop rules regardless of the overall score.'
license: MIT
metadata:
  version: 1.0.3
---

# Universal Audit - Formal Production Assurance

This skill executes the **Universal Software Engineering Audit Specification v2.2** (bundled at `spec/Universal_Software_Engineering_Audit_Specification.md`). The spec is normative. This file is the execution procedure. When they conflict, the spec wins.

Core discipline, non-negotiable:

- Every conclusion traces to evidence. PASS requires affirmative evidence, never scanner silence.
- Insufficient evidence is **UNVERIFIED**, stated plainly, with what would verify it.
- Never invent defects, never soften verified risk, never pad findings to look thorough.
- The numeric score never overrides release gates.

## Phase 0 - Engagement Setup (blocking)

1. Confirm the target: repo path, running URL, or both. Read `package.json` / `requirements.txt` / `wrangler.toml` / equivalent before anything else.
2. Fill the intake from `references/templates/intake-template.md`. Ask the operator only for items you cannot establish yourself. Missing inputs go to **Audit Limitations**, never silently assumed.
3. Declare: audit type, depth tier (rapid / standard / deep), environment, access level, assurance objective, and risk profile (P1–P6, see `references/depth-and-profiles.md`). If the operator did not specify depth, propose one with rationale and wait.
4. Assign the audit ID: `AUD-[PRODUCT]-[YYYYMMDD]-[SEQ]`.
5. Rules of Engagement: this skill defaults to **passive, read-only inspection**. No load tests, no destructive actions, no auth bypass attempts, no tests against systems the operator does not own. Active testing requires the RoE template completed and explicit operator authorization recorded in the manifest.
6. Gate controls: evaluate `GOV-SCOPE-001` and `GOV-ROE-001` first. If either cannot PASS, the engagement is advisory only - say so now, not in the report.
7. Create the artifact directory: `audits/<audit-id>/` in the project root (or an operator-specified location). Run `scripts/init_audit_artifacts.py --audit-id <audit-id> --output audits/<audit-id>` to create the initial manifest from `assets/audit-manifest-template.json`. It refuses to overwrite an existing directory.

## Phase 1 - Control Selection

1. Load the catalog: spec Appendix A. Select every control at or below the declared tier (Rapid = R; Standard = R+S; Deep = R+S+D). Profile-critical controls are mandatory regardless of tier.
2. Mark NOT APPLICABLE controls with recorded justification. NA without justification is invalid.
3. Assign each selected control its scoring category from spec A.0. A control without a category is a validation failure.
4. Write `selected-controls.json` (schema in `references/schemas/`). This freezes the coverage denominator before any evidence is gathered - selection cannot be trimmed later to inflate coverage.

## Phase 2 - Evidence Collection

Work the spec Section 12 order. For each selected control, gather the minimum PASS evidence listed in the catalog or stronger. Practical guidance per family is in `references/control-procedures.md`. Read `references/release-evidence-catalog.md` when choosing evidence for a release gate. Read `docs/evidence-ledger-guide.md` before recording evidence for the first time.

- Record every material observation in `evidence-ledger.json`: ID, class, timestamp, location (file:line, endpoint, config key), method, sanitized excerpt, limitations.
- Repository unavailable: source-dependent claims are `UNVERIFIED - Runtime inference only`.
- Tool output (linters, SCA, scanners) is evidence to assess, not a verdict. Validate before accepting severity.
- Sanitize as you go: no secrets, tokens, personal data, or working exploit payloads in the ledger.
- For large targets, fan evidence collection out to subagents by control family, one ledger merged afterward. Deduplicate observations across families before Phase 3.

## Phase 3 - Findings and Status

1. Assign each selected control exactly one status: PASS / FAIL / WARN / NOTE / UNVERIFIED / NOT APPLICABLE.
2. Every FAIL and WARN becomes a finding using the twenty-field standard (spec Section 9), written to `findings.json`. Severity is impact, likelihood is separate, confidence is separate. Low-confidence concerns normally stay UNVERIFIED.
3. Consolidate duplicates around root causes. Apply the systemic-risk rule (spec 13.5) only when all four conditions hold.
4. WARN may not carry Critical severity. A WARN - High on a C3 control must survive the Phase 5 challenge or be reclassified FAIL - High.

## Phase 4 - Scoring and Verdict

1. Run `scripts/score.py`:

   ```
   python scripts/score.py audits/<audit-id>/selected-controls.json \
       --profile P4 --tier standard --out audits/<audit-id>/score-sheet.json
   ```

It computes per-category provisional scores, applies the mandatory caps, computes tier-relative coverage (and the Standard-denominator figure for Rapid audits), validates category mapping, and evaluates the release gates. Do not hand-calculate scores; the script is the single source of arithmetic.
2. Select exactly one verdict - APPROVED / APPROVED WITH CONDITIONS / REQUIRES REWORK / DO NOT SHIP - from the script's gate evaluation plus the qualitative gates the script cannot check (critical-workflow verification, interim-control ownership). Justify the verdict against the gates line by line.

## Phase 5 - Independent Challenge

Standard tier: run a separate contradiction pass - a fresh subagent that did not author the findings attempts to refute every Critical/High finding, every release-significant Medium/WARN, and every C3 PASS supporting approval, and recalculates the score sheet. Deep tier: the challenge must be a genuinely independent agent or human review.

Record each challenge outcome: UPHELD / MODIFIED / REJECTED / NEEDS MORE EVIDENCE, with rationale, in `verification-log.json`. Resolve differences transparently.

## Phase 6 - Report and Release

1. Render `report.md` from `references/templates/report-template.md`. Executive summary is seven sentences maximum.
2. Confirm the twelve-point quality gate (spec 19.2). Any failure means the report is not ready - fix it, do not ship it annotated.
3. Final artifact set in `audits/<audit-id>/`: `audit-manifest.json`, `selected-controls.json`, `evidence-ledger.json`, `findings.json`, `score-sheet.json`, `risk-register.json`, `verification-log.json`, `report.md`.
4. Deliver the verdict, the top risks, and the coverage figures in the final message. Plain language, no alarmism, no softening.

## Re-Audit Mode

If the operator supplies a prior audit ID or report, run spec Section 16 instead of a fresh Phase 1–3: verify each prior FAIL/WARN against its original reproduction, classify (OPEN / PARTIALLY REMEDIATED / REMEDIATED / ACCEPTED / REGRESSED / NOT REPRODUCIBLE), re-run all applicable C3 controls, recalculate from current evidence, and produce the delta table. Never carry a PASS forward without confirming its evidence still holds.

## Scope Control

- A time box changes coverage, not truth standards. Out of time: remaining controls are UNVERIFIED and reported as such.
- Never present a limited audit as full production assurance.
- Stop immediately if authorization is exceeded, a test risks material harm, or the audited version cannot be established.
