# Phase 4 — Waypoints

Cut the spec into units of work, each built by its own subagent in its own fresh context.

Before cutting anything, understand what a cut costs.

## The cost of a boundary

Every ticket boundary is a fresh context that has to fly in from nothing: read the interfaces, explore the code, work out the stack, find the test command. Call it 20–40k tokens of pure re-orientation before a single line gets written. And the subagent runs a review at the end, which is more contexts again.

So a ticket is worth creating **only when the work inside it is bigger than its own boundary**. A ticket carrying eighty words of instruction pays full price for a boundary and delivers a fraction of the value.

This is the mistake to avoid, and it is not the obvious one. Cutting too fine feels careful. It is the opposite: each extra boundary is another chance for two subagents to disagree about an interface, and another whole context spent re-learning the project. **Fewer, denser tickets beat more, thinner ones** — every time.

## The tier budget

Decide the tier from **what has to be built**, then cut to it. State the tier and the count in one line to the user.

| Tier | The product looks like | Tickets |
|---|---|---|
| **T0** | one surface, one layer, no external service — a page, a form, a script, a single endpoint | **none — build straight from the spec in one context** |
| **T1** | one coherent feature: a few surfaces over one data shape, at most one external service | 2–3 |
| **T2** | several features, or one feature reaching across several layers — store, logic, interface, integration | 4–8 |
| **T3** | ≥ 3 genuinely independent subsystems, each with its own data and its own reason to change | 9–16 |
| **>16** | — | **not allowed.** Either justify it in a line in the spec, or split the work into two Autopilot runs |

**The tier is read from the product, never from the length of `spec.md`.** Depth decides how thoroughly each requirement is written up; it has nothing to say about how much there is to build. A `deep` spec for a landing page is a long document about one page — still T0, still one context, still no tickets. Sizing by word count quietly turns the depth dial into a ticket multiplier, which is the opposite of what it is for.

**T0 is real and it is common.** A landing page, a form, a script, a single endpoint — cut nothing, build it in one pass, review once, done. Skipping tickets here is not a shortcut; creating them would be the waste. Say so plainly: «Задача небольшая — собираю сразу, без разбивки».

At T0 the `plan` stage in `state.js` is marked `skipped` with the reason as its note — «ярус T0 — без разбивки на таски» — not left `pending`. A stage that never moves reads as a stuck build, and the whole point of the dashboard is that it does not have to be explained.

Crossing a tier upward needs a reason written into the spec, not a feeling.

## How to cut

Each ticket is a **narrow but complete path through every layer** it touches — data, logic, interface, tests. Not a horizontal slice of one layer. When it is done, something works end to end that did not work before, and you can show it.

- Anything that has to exist before the rest — the shell, the shared primitives, the schema — is ticket 01, alone. Nothing parallelises with it.
- Groundwork that makes later tickets easy goes early. Make the change easy, then make the easy change.
- Give each ticket its **blocking edges** — the tickets that must finish before it can start. No blockers means it can start immediately.
- Number from `01` in dependency order, blockers first.
- **Tickets closing `R` requirements come before tickets closing only `A`.** If the run is cut short, what is missing must be your additions, never the user's request.

## The floor — two tests every ticket must pass

**The payback test.** Would its subagent spend more effort flying in than building? Then it is not a ticket. Merge it into the neighbour it depends on.

**The neighbour test.** Fewer than three acceptance criteria, touching the same files as an adjacent ticket, and not separated from it by a wave boundary? Then it is a checklist item inside that neighbour, not a ticket of its own.

## The merge pass — mandatory

After the draft, before writing any files, go through the list once more and merge:

- adjacent tickets touching the same files with no wave between them;
- any ticket under three acceptance criteria that has a natural parent;
- chains where B is blocked by A, nothing else is blocked by A, and A alone demos nothing.

Then re-check the tier. A draft that lands at 14 and merges to 7 was a T2 job pretending to be T3 — normal, and the reason this pass exists.

## Waves — what may fly together

Blocking edges say what cannot start yet. **Waves say what may start at the same time**, and computing them is not optional: without waves the crew flies one ticket at a time, and a plan whose tickets are genuinely independent takes two or three times longer than it needs to — for no reason anybody chose.

Work them out once, right after the merge pass, from two things you already have:

1. **`wave = 1 + max(wave of its blockers)`** — everything with no blockers is wave 1.
2. **Then split each wave by zones.** Two tickets in one wave that would write the same files cannot run together: move the later one into the next wave. Same files → serialise, always. Two subagents editing one file overwrite each other and the loss is silent.

Step 2 needs to know what each ticket owns, so every ticket names its zone:

**Зона:** `src/bot/` · `migrations/`

Directories and modules — a boundary of ownership, not a file list. This is the one exception to "avoid paths": here the path *is* the decision being made, and it goes stale only if the ticket itself is re-cut.

A wave of one is a normal answer. Ticket 01 — the shell, the schema, the shared primitives — is a wave of its own by definition.

**Do not manufacture parallelism.** Splitting a ticket in two so a wave looks wider spends two contexts to save one, and the merge pass exists to undo exactly that. Waves are *discovered* in the dependency graph, never designed into it. If everything genuinely depends on everything, the answer is N waves of one — say so and fly it.

**A wave number is assigned once, here, and is not recomputed later.** It describes the plan, not the frontier: when a ticket finishes and the next one becomes launchable, that is the build moving through the plan, not the plan changing. Renumbering waves as the run progresses makes rows jump between groups on the dashboard, and the user — who has no way to know the numbers were rewritten — reads it as the agent losing the plan.

If a wave genuinely has to change, that is a re-cut and it follows the rules for a plan that moved: the reason goes in one line to the user, and if the code forced it, a `D##` row records why. Silent renumbering is the thing to avoid, not renumbering.

Write `wave` into every ticket file and into `state.js`. The dashboard groups the build by waves and marks the parallel ones («Волна 3 — 2 таска параллельно»); Phase 5 launches each wave in one go.

## Seeding interfaces.md — before any ticket flies

Phase 3 decided the boundaries: what each unit owns, what it exposes, what it hides. **Copy that section into `interfaces.md` now**, under «Границы, решённые в спецификации», together with the project rules a subagent cannot derive — stack and versions, the run and test commands, what must not be touched, and the rule that a missing dependency comes back as `BLOCKED` rather than an install.

This is a copy, not a design exercise. If it turns into one, Phase 3 left the boundaries undecided and the right move is to go back and decide them — not to invent them here, where the plan is already cut around them.

Why it cannot wait for ticket 01 to return: the first subagent reads this file before it writes anything, and what it reads is the only thing standing between it and inventing its own version of every boundary. A file that says nothing until the first ticket has finished means the first ticket *is* the design, chosen by whoever saw one eighth of the задача.

Zones follow from the same section. A ticket's **Зона** is the part of the boundary map it owns — which is why two tickets in one wave with disjoint zones can be trusted not to collide: they were separated in the spec, not guessed at here.

At tier T0 there is one context and no wave, so the file gets the project rules and the seams, and nothing more. It is still written: Phase 5 checks its own work against those seams, and Phase 9 folds it into the memory file.

## Publishing the plan to the instruments

The moment the ticket files exist, **every ticket goes into `state.js` and into the dashboard** — not when the first one starts, not after the first one lands:

```json
{ "id": "04", "title": "Панель мастера: очередь заявок", "requirements": ["R04", "R04.1"],
  "blockedBy": ["02"], "wave": 3, "zone": ["src/admin/"], "status": "pending", "retries": 0 }
```

`status: "pending"`, no timestamps yet — they come when the ticket launches. This is one edit, and it is what turns the dashboard from «таски ещё не нарезаны» into the whole plan with its waves, visible before a line of code is written.

**A build running while the dashboard still says the tickets were never cut is broken instruments**, and it breaks them at the exact moment the user is most likely to look. The count, the waves, the «ход сборки» block and the honest progress bar all read from this array — nothing on the dashboard can show what was never written. See `phases/7-instruments.md`.

## Density — the other half of the rule

Cutting fewer tickets only helps if each one carries what its subagent needs. The failure mode is a ticket so thin that the executor fills the gaps by guessing.

Every ticket file:

```markdown
# 03 — Приём заявки от клиента

**Требования:** R01, R01.1, A01
**Blocked by:** 01, 02
**Зона:** `src/bot/`
**Волна:** 2
**Status:** ready

## Что должно заработать

Клиент пишет боту, отвечает на три вопроса — что сломалось, адрес, телефон —
и получает подтверждение с номером заявки. Если сеть отвалилась на середине,
следующее сообщение продолжает с того же места, а не начинает заново.

## Из брифа, дословно

> «принимает заявки на ремонт техники»
> «чтобы клиент видел статус»

## Разделы спецификации

Истории 1–5, Решения §2 и §4, Швы §1.

## Критерии приёмки

- [ ] Диалог из трёх шагов доходит до подтверждения
- [ ] Номер заявки уникален и виден клиенту
- [ ] Прерванный диалог продолжается, а не сбрасывается
- [ ] Незаполненный телефон даёт понятную ошибку, а не падение
- [ ] Тест на шве §1 покрывает полный путь и обрыв
```

The verbatim brief quotes are not decoration. They are the last thing standing between a fresh context and a plausible reinterpretation of what was ordered — and they cost about forty tokens.

Avoid file paths and code snippets: they go stale faster than the ticket does. The exception is a structure that prose states worse than code — a schema, a state machine, a type shape. Then inline just that.

## Gate G3 — before publishing

**Forward:** every `in-spec` requirement appears in at least one ticket's Требования line. A requirement in no ticket does not get built.

**Backward:** every ticket names at least one requirement, or a spec decision that itself traces to one. **A ticket tracing to nothing is work nobody ordered** — cut it, or attach it to what it actually serves. This direction catches the invented subsystem that would otherwise consume three contexts and confuse the acceptance run.

**Complete:** every ticket has a zone and a wave, no two tickets in one wave share a zone, and **`interfaces.md` already carries the boundaries from the spec**. A missing wave means Phase 5 has to guess the order, and it will guess "one at a time"; an empty `interfaces.md` means the first subagent guesses the architecture.

Then update the manifest: `in-spec` → `in-ticket`, with the ticket number, and publish the tickets to the instruments (above).

## Showing the plan

Write the files first. **A ticket that exists only in the dialogue is not a ticket** — what the user sees is a summary of files already on disk.

**Parallelism gets one line, and only if it is true**: «Часть тасков пойдёт параллельно — 6 тасков в 4 волны». It is the one piece of process the user actually feels, because it changes how long they wait. Never claim it for a plan that is one long chain.

**semi and interview** — one screen, plain language, no technical detail, one line per ticket saying what the user will be able to do when it lands. Then: «Показываю план и начинаю. Скажи "стоп", если что-то не так». Then start. Do not wait for approval — waiting is the failure mode this skill exists to remove. **Never promise a countdown:** you cannot hold a pause, so a stated delay is a promise you will break. The user's window to object is their own reaction, and saying so plainly is the honest version of it.

`interview` is `semi` here, and deliberately: the questions were the point of that mode, the ticket list was not. A user who wants to argue about granularity said «ручной режим», which is a different word.

**full** — the same screen as a notification. No pause.

**manual** — the plan is a gate. Show it with technical detail, discuss granularity and order, adjust on request, wait for an explicit «ок». Phase 5 starts only on agreed tickets.
