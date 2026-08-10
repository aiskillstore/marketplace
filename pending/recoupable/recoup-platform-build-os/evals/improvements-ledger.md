# workspace-os improvements ledger

The compounding output of the eval harness. Each run appends grounded, evidence-backed edits to the
`workspace-os` skill — this is `{domain}-reflect` applied to the scaffolder itself. Only log
improvements tied to an **observed** failure in a run (cite the run + agent), never generic advice.

Row format:

| # | Pri | Finding (observed) | Evidence (run / agent / file) | Proposed change in workspace-os | Status |
|---|-----|--------------------|-------------------------------|---------------------------------|--------|

Status: `proposed` → `applied` (edited the skill) → `verified` (a later run shows it fixed) → `rejected` (with reason).

---

## Findings

### Run 2026-06-22-1657 (research-lab + consulting; builds ~98–99/100, uses 100/100)

_Findings 1–5 applied to `workspace-os` v0.10.0 (2026-06-22) and **verified** in run `2026-06-22-1814`
(fresh build + use on v0.10.0; package-freshness loop confirmed end-to-end). That verification surfaced
+ fixed F6. H1 (a harness improvement) is still proposed._

| # | Pri | Finding (observed) | Evidence | Proposed change in workspace-os | Status |
|---|-----|--------------------|----------|---------------------------------|--------|
| 1 | HIGH | The doctor's mechanical checks get **reinvented at use-time** instead of shipping with the build. An operator built `operations/doctor.py` mid-session to stop recomputing counts by hand; the eval's own `validate.py` converged on the same script independently. | research-lab user agent (task 5) built `operations/doctor.py` and wired it into `lab-doctor`/`lab-janitor`; harness `validate.py` is the same idea. | Add `assets/doctor.py.tmpl` — generic, dependency-free: recompute pipeline/entity/skill counts, cross-check `_board.md` + `dashboard.html` + manifests + root hygiene + dark-skill reachability + draft-confirm count; exit non-zero on findings. Reference it from `assets/doctor-SKILL.md.tmpl` as the fast path. | **verified** (run 1814) |
| 2 | HIGH | After in-place skill edits the packaged `.plugin` **silently drifts**, and there's no clean home to re-zip into (a new `outputs/` would trip the doctor's root-hygiene check). Both operators changed `plugin/skills/` + bumped manifests; neither could cleanly repackage. | consulting bumped manifests to v0.2.0 (build `.plugin` now stale); research-lab's `reflect` explicitly skipped re-zipping to avoid a stray top-level folder. | (a) `references/packaging.md` + `blueprint.md`: declare the repackaged artifact transient/external and **exempt it from hygiene**; (b) add a doctor check "manifest version / skills changed since last package" (package freshness); (c) make `skillify`/`janitor`'s "re-zip plugin/" step state the exact location. | **verified** (run 1814) |
| 3 | MED | The never-stale **safety net is never actually armed**: no scheduler existed in either environment, so the weekly janitor stayed a documented "one step later," never on. The core "self-reconciles when no one's looking" promise is off by default. | Both builds recorded the cadence in `operations/routines.md`; neither could wire it. | Ship a scheduling asset (`assets/janitor-workflow.yml.tmpl` for CI and/or a `launchd`/cron snippet) so enabling is literally one copy. Promote "janitor schedule unwired" to a standing low doctor finding in the template (both doctors added it ad hoc). | **verified** (run 1814) |
| 4 | MED | `skillify`'s "ask before publishing" gate **blocks autonomous compounding**. Both operators needed an explicit "go ahead without approval" to finish skillifying in one unattended pass; a scheduled janitor could never publish. | Both user-agent task 5 prompts had to grant approval for the skill to be published to `plugin/skills/`. | In `assets/skillify-SKILL.md.tmpl` + `references/self-management.md`, define the unattended policy: without a human, stage + verify + **propose** (draft + `operations/improvements.md` entry) but don't publish; publishing needs approval or an explicit "autonomous publish" setting. | **verified** (run 1814) |
| 5 | LOW | `draft — confirm` debt **accumulates with no burn-down ritual** on sparse builds. The doctor surfaces the count but nothing drives confirmation. | research-lab draft-confirm markers 28 (build) → 44 (after use); only surfaced, never reduced. | Add a tiny "confirm predictions" routine to the `operations/routines.md` template and an intake nudge (offer to confirm draft items when a folder with them is touched). | **verified** (run 1814) |
| H1 | harness | The harness auto-scores only 56/100 of the build rubric; the 44 judgment pts were scored by the parent this run. | This run. | Add an optional evaluator-subagent step (readonly) to score judgment + use-time rubric at scale, so larger runs don't bottleneck on the parent. | proposed |
| 6 | LOW | `doctor.py.tmpl` entity-freshness heuristic matched the word "follow", so a *filed* "follow-up" note with a past date raised a false freshness finding. | run 2026-06-22-1814 (verify-operate agent renamed the note to dodge the gauge, then logged it). | Tighten the cue from `next/due/follow` to `next action / due / overdue` so history doesn't trip it. | **applied** |
