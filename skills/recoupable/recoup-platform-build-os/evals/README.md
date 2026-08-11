# recoup-platform-build-os evals

A repeatable harness for answering one question: **does `recoup-platform-build-os` actually produce a workspace
that manages itself and improves itself?** — and, every time we run it, **what should change in the
skill to scaffold a better system next time?**

The harness is built on one principle borrowed from the skill itself: *evidence over confidence.*
We don't ask "does this feel like a good workspace." We build workspaces with fresh-context agents,
operate them with other fresh-context agents, and score the result against the skill's own contracts.

## Why fresh-context subagents

The skill is supposed to be self-sufficient: a `CLAUDE.md` it writes should drive an agent that has
never read `recoup-platform-build-os`. So every stage uses a subagent with a clean context window:

- **Builder agents** never see this evaluation or the chat that launched it. They only get a kickoff
  input and the path to `recoup-platform-build-os/SKILL.md`. This tests whether the *skill* is followable.
- **User agents** never see `recoup-platform-build-os` at all. They are dropped into a finished workspace and told
  only "you operate here, here's some new material." This tests whether the *generated brain*
  (`CLAUDE.md` + the skills it authored) actually fires the never-stale and compounding loops.
- **Evaluator agents** score against `rubric.md` from a clean read of the resulting files + diffs.

If a loop only fires when a human reminds the agent, that's a finding — the generated `CLAUDE.md`
isn't pulling its weight.

## The pipeline

```
scenario kickoff ─▶ [builder agent] ─▶ built workspace ─▶ git snapshot
                                              │
                                       [static eval]  validate.py + rubric (build-time)
                                              │
                          new input + asks ─▶ [user agent] ─▶ operated workspace
                                              │
                                        git diff (before/after)
                                              │
                                     [behavioral eval]  rubric (use-time)
                                              │
                                        [synthesis] ─▶ improvements-ledger.md + a dated report
```

## Layout

```
evals/
├── README.md               # this file — the methodology
├── rubric.md               # build-time + use-time scoring (tied to the skill's contracts)
├── validate.py             # automated static checks on a built workspace (the mechanical subset)
├── improvements-ledger.md  # accumulating, dated findings → concrete edits to recoup-platform-build-os
├── scenarios/              # the test cases (inputs are committed; outputs are not)
│   ├── research-lab/       #   SPARSE input → tests Phase 0 prediction + "lean root"
│   ├── consulting-firm/    #   RICH input → tests extraction into knowledge/entities/library
│   └── record-label/       #   RICH input → tests the Recoup music-locked path (artists/ + RECOUP.md, no pipeline)
└── runs/                   # GITIGNORED generated artifacts: one dir per run
    └── YYYY-MM-DD-HHMM/
        ├── research-lab/workspace/      # what the builder produced
        ├── consulting-firm/workspace/
        └── report.md                    # scores + findings for this run
```

A scenario folder contains:

- `kickoff.md` — what the **builder** receives (a prompt, or a pointer to a `kickoff/` input packet).
- `kickoff/` — (rich scenarios only) the input files the builder ingests.
- `use-script.md` — the natural-language tasks the **user agent** performs after the build.
- `use-input/` — new material dropped into the workspace during the use phase (tests never-stale on
  genuinely new input the builder never saw).

## How to run it

1. **Snapshot a run dir:** `runs/<timestamp>/<domain>/workspace/`.
2. **Build:** dispatch a builder subagent per scenario — fresh context, given only the kickoff and the
   absolute path to `recoup-platform-build-os/SKILL.md`, told to build *only* inside its workspace dir.
3. **Static eval:** `python3 recoup-platform-build-os/evals/validate.py <workspace_dir>` → JSON score + findings.
   Score the judgment items in `rubric.md` by inspection.
4. **Freeze:** `git -C <workspace_dir> init -q && git -C <workspace_dir> add -A && git -C <workspace_dir> commit -qm baseline`.
5. **Use:** dispatch a user subagent per workspace — fresh context, given the workspace path and the
   `use-script.md`, **never** told about `recoup-platform-build-os` or the words "never-stale"/"doctor".
6. **Behavioral eval:** `git -C <workspace_dir> diff baseline` is the evidence. Score the use-time
   rubric (an evaluator subagent reads the diff + the user agent's report).
7. **Synthesize:** write `runs/<timestamp>/report.md` and append the cross-run patterns to
   `improvements-ledger.md` as concrete, grounded edits to `recoup-platform-build-os`.

## What a result looks like

Each run yields, per domain, a **build score /100** and a **use score /100**, plus a punch list. The
*use* score is the headline: a workspace can be built perfectly and still be dead if nothing fires
when a real agent works in it. The ledger turns the lowest, most-repeated failures into specific
changes to the skill — that's the compounding loop applied to the scaffolder itself.
