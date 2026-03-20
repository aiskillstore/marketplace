---
name: req-change-workflow
description: >
  Standardize requirement/feature changes in an existing codebase (especially Chrome extensions) by turning
  "改需求/需求变更/调整交互/改功能/重构流程" into a repeatable loop: clarify acceptance criteria, confirm current
  behavior from code, assess impact/risk, design the new logic, implement with small diffs, run a fixed
  regression checklist, and update docs/decision log. Use when the user feels the change process is chaotic,
  when edits tend to sprawl across files, or when changes touch manifest/service worker/OAuth/storage/UI and
  need reliable verification + rollback planning.
---

# Req Change Workflow

## Overview

Use a lightweight, repeatable workflow to modify an existing requirement without scope creep or “边改边炸”. Produce clear artifacts at each gate so the user can approve before the implementation starts.

## Workflow (gated loop)

Follow the steps in order. Do not implement code changes until the user approves Step 4.

### Step 0: Set the plan (optional but recommended)

- Use `update_plan` to create 5–7 short steps: clarify → baseline → impact → design → implement → validate → document.
- Keep exactly one step `in_progress` at a time and advance as you finish.

### Step 1: Clarify the change (lock scope first)

Ask the user for the minimal inputs, then rewrite them into a clear “change brief”:

- Target (1 sentence): what outcome changes.
- Out of scope (1 sentence): explicitly what must NOT change.
- Acceptance criteria (3–6 bullets): observable behaviors that can be verified.
- “Must keep” constraints: compatibility, performance, security, no new dependencies, no network, etc.
- Rollback expectation: can we revert by reverting a diff, or does it require data migration/backfill?

Use the template in `references/change-brief-template.md`.

### Step 2: Confirm current behavior from code (baseline)

Do not trust memory or assumptions. Locate the real entrypoints + current data flow and summarize it in 5–10 lines:

- UI entrypoints (e.g., `sidepanel/`, `options/`) and where user actions are wired.
- Background orchestration (e.g., `service_worker.js`).
- Core modules (e.g., `src/core/...`) and storage (`src/core/local/...`).
- Config/permissions changes (e.g., `manifest.json`).

Use `scripts/impact_scan.sh` to quickly find likely files, then read only the necessary ones.

Output artifact: “Current behavior summary” + a short file list (with why each file matters).

### Step 3: Impact + risk assessment (change budget)

Before proposing a new design, list:

- Files/modules that must change and why.
- Risks: auth/session, storage migration, concurrency, caching, permission scopes, UX regressions.
- Testing checkpoints: what to verify manually (use `references/regression-checklist.md`).
- Rollback plan: what is safe to revert; what needs cleanup.

If changes touch `manifest.json` or `service_worker.js`, require a manual reload step in the validation plan (Chrome extensions cache aggressively).

Output artifact: “Impact & risk list” + “Rollback plan (1–3 bullets)”.

### Step 4: Propose the new design (get approval)

Describe the new behavior using:

- New flow (bullet sequence) including edge cases.
- State model: key states, transitions, and failure recovery.
- Change boundaries: what stays unchanged.
- Observability: logs/events/UI hints for debugging.

Then ask the user to approve:

- The acceptance criteria (Step 1) as final.
- The file list (Step 2/3) as the change budget.
- The proposed design (this step).

Do not start editing code until the user says “同意/OK/按这个做”.

### Step 5: Implement with minimal, localized diffs

Implementation rules:

- Prefer root-cause fixes over patches, but keep diffs small and focused.
- Avoid scattering logic across multiple entrypoints; centralize in one module when possible.
- Keep ES module imports explicit; avoid implicit globals.
- Add short JSDoc for exported functions when introducing new exports.
- User-visible logs: actionable Chinese messages (explain what to do next).

If the change involves async flows/cross-module calls/fallbacks, add Chinese comments explaining assumptions and failure handling.

### Step 6: Validate (fixed regression loop)

- Run the manual pages referenced in `references/regression-checklist.md`.
- If `manifest.json` or `service_worker.js` changed: reload the extension before retesting.
- Record what you tested and the observed outcome (even if it is manual).

### Step 7: Maintain (docs + decision log)

- Update project docs or inline notes for future maintainers.
- Add a short “Decision log” entry: why this design, what alternatives were rejected, and how to roll back.

Use the template in `references/decision-log-template.md`.

## Resources

### scripts/
- `scripts/impact_scan.sh`: fast file candidate scan via `rg` for keywords + common extension entrypoints.

### references/
- `references/change-brief-template.md`: input template to lock scope + acceptance criteria.
- `references/regression-checklist.md`: manual regression checklist for this repo’s Chrome extension.
- `references/decision-log-template.md`: lightweight decision record template.
