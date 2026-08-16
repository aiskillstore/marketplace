# Phase 0 — Preflight

Configure the repo and raise the instruments. What runs here depends on what is already on disk, and there are exactly three cases. Decide which one you are in **before** doing anything else.

| On disk | Case | What Phase 0 does |
|---|---|---|
| no `.autopilot/` | **new repo** | everything below, in order |
| `.autopilot/state.js` with `finishedAt: null` | **resume** | none of the steps — go to *Resuming an interrupted flight* at the end of this file |
| `.autopilot/` exists, last run has `finishedAt` set | **new feature in a configured repo** | steps 1, 3, 5, 7 only |

**The third case is the one that gets missed**, and missing it is silent. The repo is configured, so the settings work is done — but this flight still needs its own slug directory, its own dated brief, its own manifest and its own fresh instruments. Reuse the previous run's `state.js` and the user spends this build watching a dashboard that describes a project which already shipped.

In that case: derive a new slug (step 1) and create its directory (step 3); **archive the finished run** — move `state.js` to `.autopilot/<previous-slug>/state.js`, write a fresh one for this flight and re-open the dashboard (step 3, rules in `phases/0-instruments.md`); top up the memory file rather than rewriting it (step 5); close the stage (step 7). Skip the conventions note and the git setup — they are already there, and `.autopilot/README.md` describes the folder, not the run.

**Nothing here is a question for the user.** These are process decisions, not product ones. No mode buys the user a say in where ticket files live; asking about it is exactly the kind of question Autopilot exists to remove.

## 1. Name the flight

Derive a **feature-slug** from the dictated idea — short, kebab-case, latin (`telegram-repair-bot`, `nail-studio-landing`). It names `.autopilot/<feature-slug>/` for the whole run and never changes mid-flight.

## 2. Look before writing

Read what is already here; assume nothing:

- `git rev-parse --git-dir` — is this a repo at all?
- `CLAUDE.md`, `AGENTS.md` at the root — does either exist?
- `.autopilot/` — a previous run? Then this is a **resume**, see below.
- `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml` — is there an existing stack to respect?
- `CONTEXT.md`, `docs/adr/` — existing domain vocabulary and decisions. If present, the spec and the tickets must use that vocabulary rather than inventing synonyms, and must flag anything that contradicts a recorded decision instead of silently overriding it.

## 3. Create the flight directory

```
.autopilot/
├── <feature-slug>/
│   ├── <YYYY-MM-DD>-brief.md
│   ├── manifest.md
│   ├── reference.md        (only if the briefing collects one — `phases/2-briefing.md`)
│   ├── spec.md
│   ├── interfaces.md
│   └── tickets/
├── state.js
└── dashboard.html
```

The brief carries **the date it was dictated in its filename** — `2026-08-07-brief.md`. A slug directory outlives one conversation: the user comes back a month later with «доделай», a second brief gets appended, and a file called `brief.md` gives no way to tell which sitting is which. The date is the cheapest possible answer, and it sorts.

`state.js` and `dashboard.html` are written now, empty-but-valid, per `phases/0-instruments.md`. The initial `stages` array lists all eight stages — `preflight` as `active`, the rest `pending` — so the dashboard shows the whole road from the first minute instead of a blank page.

## 3a. Raise the instruments

Copy the template, write the starting `state.js`, open the page once. **Read `phases/0-instruments.md`** — it is Phase 0's whole share of the dashboard, including the update ritual you will use for the rest of the run.

Do **not** read `phases/7-instruments.md` here. It answers questions that arrive in Phase 4, and reading it now spends six thousand characters of the one context that is never refreshed.

## 4. Record the conventions

Write `.autopilot/README.md` — a short note for the human, not for the agent:

```markdown
# Как читать эту папку

- `dashboard.html` — открывается сам в начале сборки; можно и двойным кликом.
  Этапы, прогресс, время, что осталось. Обновляется сам, пока сборка идёт.
- `<проект>/<дата>-brief.md` — твоя изначальная задача, слово в слово. Не редактируется.
- `<проект>/manifest.md` — список требований и что с каждым стало.
- `<проект>/spec.md` — спецификация.
- `<проект>/tickets/` — таски, на которые разбита сборка (если сборка мелкая, их нет).

Если сборка прервалась — скажи агенту «продолжи автопилот», он поднимет состояние отсюда.
```

## 5. Raise the project memory

The repo needs a file that tells the **next** session what this project is — `CLAUDE.md` or `AGENTS.md`. Which one is decided by detection, never by a question; the skeleton is written now and finished in Phase 8. **Read `phases/0-memory.md`** — the detection table and the skeleton, and nothing else applies until the build is over.

Two things happen here: pick the file, write the skeleton between the `<!-- autopilot:start -->` markers. Announce the choice in one line inside the opening block, together with the mode — and do not wait for a reply.

Record the chosen file in `state.js` as `memoryFile`, and note it in the Phase 8 report. Do **not** read `phases/9-memory.md` here — everything in it belongs to Phase 5 and Phase 8.

## 6. Git

If there is no git repo, `git init` **now**, not in Phase 5 — the first commit must be able to happen the moment the first ticket lands. Write `.gitignore` before anything else is created, with at least:

```
.env
.env.*
!.env.example
node_modules/
__pycache__/
.DS_Store
```

`.autopilot/` is **not** ignored. It is the record of what was promised.

If a repo already exists and its working tree is dirty, say so in one line and continue — do not stash, reset, or clean the user's uncommitted work.

## 7. Close the stage

Leaving any phase means the same two marks, here and everywhere after: the stage you are leaving goes `done` with `finishedAt`, the stage you are entering goes `active` with `startedAt`, `updatedAt` moves, and the dashboard line is replaced. Two edits, per `phases/0-instruments.md`. **A run whose stage list never moves is a run the user cannot see** — and that is the same as no dashboard at all.

## Resuming an interrupted flight

`.autopilot/state.js` exists with `finishedAt` still `null` → this is a resume, not a new flight. (A run that finished is the third case at the top of this file, not this one — and at tier T0 there are no tickets to be unfinished, so `finishedAt` is the only reliable test.)

1. Read the project memory file first (`memoryFile` in `state.js` — `CLAUDE.md` or `AGENTS.md`), then `state.js`, `manifest.md`, `interfaces.md`. Do **not** re-read the whole dialogue; the files are the memory. The brief is `<slug>/*-brief.md` — the newest one if there is more than one.
2. Tell the user in one line where things stand: «Продолжаю: 7 из 12 тасков готовы, следующий — корзина».
   Reopen the dashboard only if the previous run had finished (`finishedAt` set) — mid-flight, assume the tab is still open and just say the path.
3. A ticket marked `in-progress` in `state.js` with no commit behind it was interrupted mid-flight. Reset it to `pending` and run it again from scratch — a half-applied ticket is worse than a fresh one.
4. Re-run the Phase 6 checklist over the whole diff since the last green commit before continuing. Something may have been left broken.
5. Continue from the frontier. Do not redo finished phases; do not re-ask answered questions.
