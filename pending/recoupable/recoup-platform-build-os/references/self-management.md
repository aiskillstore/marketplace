# The Self-Management Contract (what CLAUDE.md must enforce)

A workspace OS is only alive if the agent keeps it current. The generated `CLAUDE.md` must encode
the contracts below. (`AGENTS.md` is a symlink to `CLAUDE.md`, so this governs every agent runner.)

## 1. The auto-manage loop (run on every new input, without being asked)
When the user adds material (file, transcript, note, result) OR asks for work, run end to end:
1. **Place** the raw file in its correct home, dated `YYYY-MM-DD`.
2. **Read** it.
3. **Extract** reusable value (insights, answers, decisions) into `knowledge/`.
4. **Scan** the related entity/pipeline folder; read its README; reconcile against the new info.
5. **Update everything affected** in the same turn: entity `README.md` dashboards, `_board.md`,
   `artifacts/dashboard.html`, metrics. This is the never-stale rule.
6. **Move** folders to match reality (stage changes); update any external system of record.
7. **Mine** for compounding assets (templates, proof, FAQs).
8. **Report** what changed.

## 2. The never-stale contract (state management is the agent's job)
- "Touched the project" = "left it consistent." Never end a turn with a dashboard, board, or README
  that contradicts what just happened.
- After any change, ask: *which other files now disagree with reality?* Update them all.
- **Consistency is checked, not felt.** The read-only `{DOMAIN}-doctor` is the verification surface —
  it scores the workspace and writes a punch list to `operations/health.md`. "Left it consistent"
  means a clean doctor run, not a confident summary.
- The **janitor skill** is the backstop: it runs the doctor, fixes what's safe, and is wired to a
  scheduled task (default weekly) so drift is caught even when no one is looking.
- Staleness signals the doctor hunts: entity READMEs whose "next action" is in the past; items in the
  wrong pipeline stage; un-ingested files in inbox/raw; dashboards that don't match the folders;
  recurring answers not yet in the knowledge base; repeated tasks not yet skills; one-off work left at
  the root instead of `work/`; **dark skills** (built but unreachable by any trigger); manifests out of
  version/name parity.

## 3. The compound-learning + self-improvement contract (get smarter every session)
- Every work session must deposit at least one durable learning: a decision (`knowledge/decisions/`),
  a canonical answer (`knowledge/faqs/`), an insight (`knowledge/insights/`), or an improved
  template/skill.
- Never solve the same problem twice — search the knowledge base first; if the answer exists, reuse it;
  if it doesn't and the question is recurring, write it down.
- **Ask "skillify this?"** After finishing work, ask whether it will repeat, need upkeep, or prevent a
  failure from recurring. If yes, run the `{DOMAIN}-skillify` skill; it stages the draft under
  `work/`, verifies it, asks for approval, then moves it into `plugin/skills/` and repackages. One-off
  work stays in `work/` (dated) — it never becomes its own top-level folder. **Unattended** (a scheduled
  janitor with no human present): skillify stops at staged + verified + *proposed* (logged to
  `operations/improvements.md`); publishing to `plugin/skills/` waits for approval unless the workspace
  sets an explicit autonomous-publish policy.
- **Improve the system, not just its contents.** `knowledge/` and `plugin/skills/` compound *content*
  and *capabilities*; `{DOMAIN}-reflect` compounds the *machinery* — when the same friction recurs,
  turn it into a new skill, routing row, doctor check, template, or `CLAUDE.md` rule, logged to
  `operations/improvements.md`. Spend ~half the effort on the system that does the work (50/50).
- Keep `operations/routines.md` with the cadences (e.g. weekly review, periodic value review)
  and prefer wiring the recurring ones as scheduled tasks.
- **Burn down draft-debt.** When you touch a file/folder carrying "draft — confirm" markers, confirm or
  correct them in the same turn. Sparse-input builds start with many predictions; the doctor counts
  them, and normal work should retire them rather than let them pile up.
- Keep `plugin/skills/` as the source of truth for skills. `.agents/skills` is only the Cursor/Codex
  discovery adapter and should point to or mirror `plugin/skills/`.

## Filing decision tree (customize labels per domain)
1. Reusable instrument (template/script/checklist)? -> `library/`
2. A task that will repeat or need upkeep? -> run `{DOMAIN}-skillify`
3. A finalized output you regenerate/keep current (dashboard, recurring report/export)? -> `artifacts/`
4. A one-off / ad-hoc build (won't repeat)? -> `work/{project}/YYYY-MM-DD-…/` (not a new top-level folder)
5. Reusable answer/insight/decision/SOP? -> `knowledge/`
6. A flowing item not yet "done"? -> the staged `{pipeline}/` folder
7. Tied to a core entity? -> `{entities}/{name}/`
8. Outcome/proof? -> `proof/`
9. Raw/idea/draft/published content? -> `content/`
10. Canon/source/spec/brand? -> `reference/`
11. Legal/finance/metrics? -> `business/`
