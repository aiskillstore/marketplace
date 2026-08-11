# Scoring rubric

Two rubrics, each /100. Every item traces to a contract in `workspace-os` (the SKILL phases or the
`references/`), so a low score points at a specific place in the skill to fix.

Severity for findings: **broken** (contradictory/invalid state), **gap** (missing expected thing),
**polish** (works but weak). `validate.py` auto-scores the items marked `[auto]`; the rest are scored
by inspection or by an evaluator subagent.

---

## A. Build-time rubric (is the workspace well-formed?) — /100

### Structure & taxonomy — 20
- **5** `[auto]` Lean core present: a flowing `{pipeline}/` + an `{entities}/` folder, plus
  `knowledge/`, `library/`, `work/`, `artifacts/`, `plugin/`, `operations/`.
- **5** `[auto]` Every top-level folder name is a single lowercase word.
- **5** No unjustified empty optional top-level folders (`reference/ proof/ content/ business/` only
  when they hold real material). Over-preparation lives in subfolders/stubs, not extra root dirs.
- **5** Domain fit: pipeline stages are numbered (`01-`,`02-`) and match the archetype; entity folder
  matches the core unit.

### The brain — 20
- **8** `[auto]` `CLAUDE.md` exists, has no leftover `{DOMAIN}`/`{PIPELINE}`/`{ENTITY}` placeholders,
  and contains all four contracts: auto-manage loop, never-stale, compound-learning, filing tree.
- **4** `[auto]` `AGENTS.md` mirrors `CLAUDE.md` (symlink preferred; a "See CLAUDE.md" file is partial).
- **4** `[auto]` `artifacts/dashboard.html` exists, is HTML, and is domain-customized (no placeholders).
- **4** `[auto]` `operations/health.md` and `operations/improvements.md` are seeded.

### Skills & plugin — 30
- **10** `[auto]` All six organs exist under `plugin/skills/`: `*-intake`, `*-doctor`, `*-janitor`,
  `*-learn`, `*-reflect`, `*-skillify` — plus at least one domain-specific skill.
- **6** `[auto]` Each `SKILL.md` is valid: `name` matches its folder, has a `description`, no angle
  brackets in the description.
- **6** `[auto]` Manifests valid + parity: both exist, same kebab `name` (defaults to `{slug}-os`),
  Codex manifest has `"skills": "./skills/"`.
- **4** `[auto]` `.agents/skills` adapter resolves to / mirrors `plugin/skills`.
- **4** Doctor reads as read-only; janitor explicitly runs the doctor first (by content inspection).

### Compounding assets — 15
- **8** `knowledge/` seeded sensibly (faqs / insights / decisions / sops). For rich input, real
  material was extracted into it (not empty).
- **7** `library/` seeded with reusable, domain-relevant instruments (templates/checklists/scripts).

### Hygiene & honesty — 15
- **5** Inferred facts are marked "draft — confirm"; no invented hard facts the user must own.
- **5** No one-off work promoted to a top-level folder; `validate.py` packaging checks pass.
- **5** A packaged `{slug}-os.plugin` was produced (or the attempt + outputs noted); intended janitor
  cadence recorded in `operations/routines.md` if no scheduler was available.

---

## B. Use-time rubric (does it manage & improve itself?) — /100

Scored from the `git diff` between the post-build baseline and the post-use state, plus the user
agent's own report. **This is the headline score.**

### Intake & filing — 20
- **10** New input placed in its correct home, dated `YYYY-MM-DD`.
- **10** Input actually read and reconciled against the right entity/pipeline folder (not just dropped).

### Never-stale — 30  *(the defining property)*
- **10** The affected entity `README.md` / `{pipeline}/_board.md` was updated to match the new reality
  **in the same turn**.
- **10** `artifacts/dashboard.html` was regenerated so its counts/KPIs match the folders.
- **10** No contradiction left behind: a post-hoc doctor run comes back clean (or only flags things
  outside this task).

### Compound learning — 20
- **10** At least one durable learning was deposited (`knowledge/decisions|faqs|insights/`).
- **10** A repeated question/decision was written once and reused — evidence of "never solve twice"
  (e.g. the knowledge index updated, or the agent cited an existing entry instead of re-deriving).

### Self-improvement machinery — 20
- **7** The **doctor** runs read-only and writes a sensible score + punch list to
  `operations/health.md` (it changed nothing else).
- **7** The **janitor** fixed safe drift and reported a before/after score.
- **6** Repeated/maintainable work triggered a **skillify** proposal, or **reflect** logged a grounded
  system improvement to `operations/improvements.md` (citing a real friction, not generic advice).

### Autonomy & evidence — 10
- **5** Loops fired **without being told** — given only "here's new material," the agent still updated
  the dashboard/board/knowledge because `CLAUDE.md` told it to. (If it only acted when explicitly
  instructed, score 0 — that's the key failure mode.)
- **5** "Done / consistent" was claimed against a doctor run, not asserted by feel.

---

## Reading the scores

- **Build high, Use low** → the scaffold is pretty but inert. The fix is almost always in the
  generated `CLAUDE.md` (`assets/CLAUDE.md.tmpl`) or the organ skill templates — the brain isn't
  compelling the loops. This is the most important failure to hunt.
- **Build low** → the fix is in the SKILL phases / references the builder followed (taxonomy,
  packaging, skill-authoring). Often the skill is ambiguous or too heavy to finish in one context.
- **Both low** → the kickoff was too sparse for the skill's inference rules, or a phase is
  underspecified. Check whether the builder even finished all 7 phases.

Every finding becomes a row in `improvements-ledger.md`: *finding → evidence (run/agent) → the exact
file in `workspace-os/` to change → status.*
