---
name: autopilot
description: Use when the user dictates an app, site, bot, or feature to build end-to-end and expects a finished result without reviewing specs, tickets, or code — vibecoding sessions, non-technical users, "собери под ключ", "build it for me", "не задавай лишних вопросов" requests. Also use when the user invokes /autopilot, or asks for a build in a named mode, depth or finish — «полный автомат», «режим интервью», «погриль меня», «ручной режим», «строго по брифу», «проработай глубоко», «вылижи до эталона».
argument-hint: "[full|semi|interview|manual] [strict|deep] [polish] что нужно построить или путь к brief.md"
---

# Autopilot

## Overview

Autopilot flies a dictated idea from words to a working project **in one dialogue**, without making the user approve each stage. It is self-contained: every rule it needs lives in `phases/`. No other skill has to be installed.

Two ideas carry the whole design.

**The order is the product.** Code is written in the second-to-last phase. Everything before it exists to decide *what* to build, and everything after it exists to prove the right thing got built.

**The brief is the contract, not the design.** Two obligations follow from it, and they pull in opposite directions on purpose.

*Nothing may quietly vanish.* The user's original words become a numbered manifest before anything else happens, and every phase is gated on it. What breaks naive vibecoding is not bad code — it is a requirement that stopped existing somewhere around the third rewrite.

*The brief is not the design.* It is a silhouette: it describes the happy path and nothing underneath — no empty states, no failures, no interruptions, no limits. Working those out is legitimate work, not scope creep, and it is where much of the value of this process comes from. **How far to take it is the user's dial**, set by the [depth](#depth) parameter. What is never allowed at any setting is depth that **detaches** from the brief.

## Reading this skill

This file is the orchestrator: modes, phase order, gates. The rules for each phase live in `phases/` and are **read at the moment that phase starts, not before** — that is what keeps the working context small.

**The unit of loading is the file, not the section.** «Read only the block at the top» is not a mechanism — a read pulls in the whole file — so anything needed by one phase and not another is its own file. That is why Phase 0's share of the instruments and of the project memory sit in `phases/0-instruments.md` and `phases/0-memory.md` rather than at the top of the phase-7 and phase-9 files: taking the whole of both would cost thirty-eight thousand characters in the one context that is never refreshed, to answer questions that arrive four phases later.

| Phase | Read | Produces |
|---|---|---|
| 0 Preflight | `phases/0-preflight.md`, then `0-instruments.md` and `0-memory.md` | repo configured, `.autopilot/` created |
| 1 Manifest | `phases/1-manifest.md` | `brief.md`, `manifest.md` |
| 2 Briefing | `phases/2-briefing.md` | answers recorded into the manifest |
| 3 Spec | `phases/3-spec.md` | `spec.md` |
| 4 Plan | `phases/4-plan.md` | `tickets/NN-*.md` (or none — see tiers), `interfaces.md` seeded |
| 5 Subagents | `phases/5-subagents.md` | code, commits, `interfaces.md` grown |
| 6 Review | `phases/6-review.md` | per-ticket review |
| 7 Instruments | `phases/7-instruments.md` — **in Phase 4**, when the tickets are cut | `state.js`, `dashboard.html` (opened for the user) |
| 8 Final | `phases/8-final.md` | blind acceptance, final report |
| 9 Memory | `phases/9-memory.md` — **in Phase 5 and Phase 8** | `CLAUDE.md` / `AGENTS.md`, `docs/adr/` — the project as the next session will find it |

## The words the user sees

The phases have English names in this file and the user never sees them. In the chat, on the dashboard and in the final report there is **exactly one Russian word per stage**, and it is this one. Two vocabularies for one process is how a person reads the README and then cannot find any of it on the screen.

| Phase | `stages[].id` | Пользователю |
|---|---|---|
| 0 Preflight | `preflight` | Подготовка |
| 1 Manifest | `manifest` | Требования |
| 2 Briefing | `briefing` | Брифинг |
| 3 Spec | `spec` | Спецификация |
| 4 Plan | `plan` | План |
| 5 Subagents | `build` | Разработка |
| 6 Review | `review` | Код-ревью |
| 8 Final | `final` | Приёмка |

Two rules hold this together:

- **«Сборка» — это весь прогон, а не один этап.** «Сборка идёт», «сборка прервалась», «продолжи сборку» — про процесс целиком. Поэтому пятый этап называется «Разработка»: иначе одно слово означает и часть, и целое. И «сборка» в смысле `npm run build` — тоже не он.
- **Единица работы — «таск».** Не «задача», не «тикет», не «issue». «Задача» — это то, что поставил пользователь (бриф); одно слово на две разные вещи ломает и отчёт, и дашборд.

Phases 7 and 9 are not sequential, and each is split in two along the line where it is read. The instruments are raised in Phase 0 from `phases/0-instruments.md` — template, starting state, the update ritual — and `phases/7-instruments.md` is opened only when the tickets are cut. The project memory is raised in Phase 0 from `phases/0-memory.md` — which file, and the skeleton — and `phases/9-memory.md` is opened when the build discovers something and again in Phase 8, where a subagent writes the full description from the finished code.

## Modes

Everything typed after `/autopilot` splits into four parts: **the mode** (optional bare word — `full`, `semi`, `interview`, `manual`), **the depth** (optional bare word — `strict`, `deep`), **the finish** (optional bare word — `polish`), and **the brief** (everything else). No dashes on any parameter. Text that is not a recognised parameter is always brief.

`/autopilot full deep интернет-магазин керамики` — full mode, deep elaboration. Order does not matter; all three parameters are optional and independent.

| Mode | Triggers | Human gates |
|---|---|---|
| **full** — полный автомат | `/autopilot full`, «полный автомат», «полностью сам», «ничего не спрашивай», "fully automatic", "don't ask me anything" | none |
| **semi** — полуавтомат **(default)** | `/autopilot semi`, «полуавтомат», nothing specified | questions, on genuine forks only |
| **interview** — режим интервью | `/autopilot interview`, «режим интервью», «погриль меня», «допроси», «задай все вопросы», «разбери задачу со мной», "grill me", "interview me", "ask me everything" | questions, all of them |
| **manual** — ручной | `/autopilot manual`, «ручной режим», «согласовывай каждый шаг», "approve every step" | the same questions + spec + tickets |

**Why four and not three.** A mode decides two separate things: how much the user is asked about the *product*, and how much of the *process* they approve. Those are different kinds of their time — answering questions is the work, approving artifacts is control over how the work runs — and wanting one without the other is the ordinary case, not an exotic one. `interview` is that case: take the задачу apart with me question by question, then build the rest yourself. `manual` is `interview` plus the two artifact gates, and nothing else.

- **Announce the resolved mode and offer the others, once, before Phase 1.** The user must never discover the mode by noticing questions that did or did not arrive — and they cannot ask for a mode they do not know exists. In a chat client there is no `--help` to read: this block is the only place the dials are ever named, so it is not optional.

  ```
  Режим: полуавтомат · глубина: обычная — спрошу только то, что в задаче не определено, дальше соберу сам.
  Дашборд открыл — обновляется сам.
  Память проекта — AGENTS.md (+ CLAUDE.md со ссылкой). Скажи, если нужен другой.

  Можно переключить в любой момент, просто скажи:
  • «полный автомат» — не спрашиваю вообще ничего
  • «погриль меня» — разберу задачу вопросами до конца, дальше соберу сам
  • «ручной режим» — то же плюс согласуешь спецификацию и список тасков
  • «строго по брифу» / «проработай глубоко» — меньше или больше проработки сверх сказанного
  • «вылижи» — в конце сравню с эталоном и доведу; дольше и дороже
  ```

  With `polish` on, the first line names it and its ceiling: «Режим: полуавтомат · глубина: обычная · доводка: до трёх кругов».

  One short block, once, at the start. **It is a hint, not a question** — say it and go straight into Phase 1; waiting for a reply to it is exactly the pause this skill exists to remove. Do not repeat it later, do not restate it after a mid-run switch (one line is enough there: «Понял, дальше ручной режим»).
- **Ambiguity resolves to semi.** A mode word contradicting the rest of the sentence («ручной режим, но не спрашивай») → the explicit mode word wins; two mode words → ask which one, in one line.
- **The mode can be switched mid-run** («переключись в ручной») — it applies from the next phase onward. Phases already passed are not replayed.
- **Extra instructions in the brief** (stack, language, budget, «без базы данных», deadline) are manifest requirements like any other. They constrain the build; they never replace a phase.
- **No mode removes the manifest gates or the safety gates.** Irreversible or outward-facing actions — deploy, publish, pay, send messages to third parties, delete data, rewrite git history — stay a question in **all four** modes, including full.

## Depth

How far past the brief's own words the spec is allowed to go. The mode decides *how much the user is asked*; depth decides *how much is worked out for them*. They are independent.

| Depth | Triggers | Deepening a requirement (`R##.n`) | New capabilities (`A##`) |
|---|---|---|---|
| **strict** | `/autopilot strict`, «строго по брифу», «только то, что сказал», «ничего не добавляй», "strictly as written", "nothing extra" | only what the requirement cannot work without | **not allowed** |
| **normal** **(default)** | nothing specified | freely, by judgement — as much as the feature warrants | allowed, with a parent, within proportion |
| **deep** | `/autopilot deep`, «проработай глубоко», «максимальная глубина», «продумай за меня», "go deep", "think it through" | the full depth pass, every dimension, every requirement | actively encouraged, same two limits |

- **Default is normal, and normal means permitted.** The agent elaborates where elaboration obviously helps and does not chase every edge of every requirement. This is the setting most briefs should run on.
- **`strict` does not mean careless.** Errors and empty states are still handled — a build that crashes on bad input does not satisfy the requirement it was written for. What `strict` removes is anything the user did not ask for: no extra capabilities, no anticipating needs, no "пока я тут, добавлю".
- **`deep` does not lift the attachment rules.** Every `A##` still names its parent requirement; the proportion limit still holds. `deep` buys thoroughness, never a different project.
- **`deep` also turns on the adversarial pass** — the premortem over the brief in `phases/2-briefing.md`, which asks where the idea itself comes apart rather than where a requirement is underspecified. It runs at `deep` in **every** mode, and in `interview` and `manual` at every depth, because taking the задачу apart is what those modes are for. The mode then decides what happens to what it finds: a question, or an `ASSUMPTION` decided for the user.
- **Depth is announced with the mode**, in the same opening block: «Режим: полуавтомат · глубина: максимальная».
- **Depth can be changed mid-run** («поменьше отсебятины», «продумай глубже») — applies from the next phase. Already-written spec sections are not retroactively trimmed unless the user asks.

The rules for each level live in `phases/3-spec.md`.

## Polish — доводка

**Off by default.** One bare word turns it on, and it is the only parameter that costs the user real money and real time rather than just attention.

| | Triggers | What it adds |
|---|---|---|
| **polish** | `/autopilot polish`, «вылижи», «доведи до идеала», «сравни с эталоном», «не останавливайся, пока не будет как надо», «бюджет не важен, важен результат» | after the blind acceptance, up to three rounds of comparing the running build against the user's own reference and fixing the differences |

**Why this is a third dial and not a value of `depth`.** Depth decides how much is worked out *before* the code exists; polish decides how much is corrected *after* it does. A `strict` brief can deserve a flawless finish, and a `deep` spec can be right the first time. Folding one into the other would tie two independent decisions to one word, which is the same argument that gives this skill four modes instead of three.

Two things are decided here; everything else — the critic's prompt, the filter, the stop conditions, the bookkeeping — is in `phases/polish.md`, **read only when the parameter is on.**

- **It measures against a reference, never against taste.** No `reference.md` with something comparable in it → the loop says so in one line and does not run. A critic with nothing to compare against invents a standard, and the run then pays for chasing it.
- **Its findings become tickets**, cut and flown and reviewed and committed like any others. Nothing about доводка bypasses Phase 6 or the green suite; it is more work of the same kind, not a different kind of work.

Announced with the mode and depth in the opening block, ceiling named: «доводка: до трёх кругов».

## When to Use

- User dictates what to build and expects the finished thing, not a collaboration on process.
- User is non-technical: will not read specs, judge ticket granularity, or review code.
- "Собери под ключ", "just build it", "не задавай лишних вопросов".
- User wants the idea taken apart with them question by question, and the build done without them — that is **interview** mode, still Autopilot.
- User wants to approve the spec and the tickets but not to run the pipeline by hand — that is **manual** mode, still Autopilot.

**When NOT to use:** the user wants to co-author the code itself line by line (work with them directly); the task is a small single-file change (just do it); the idea is bigger than one project and its destination is unclear (settle the destination first, then return here).

## The flight

| Phase | full | semi (default) | interview | manual |
|---|---|---|---|---|
| 0 Preflight | auto | auto | auto | auto |
| 1 Manifest | auto | auto | auto | auto |
| 2 Briefing | skipped → self-briefing | only what the brief leaves open — sometimes none | the adversarial pass, then every fork it opens | the same |
| 3 Spec | auto | auto | auto | show → wait for explicit «ок» |
| 4 Plan | auto, notify only | auto, stoppable | auto, stoppable | discuss → wait for explicit «ок» |
| 5 Subagents | auto | auto | auto | auto |
| 6 Review | auto | auto | auto | auto |
| 8 Final | report + Assumptions | report | report | report |

**`polish` adds a step inside Phase 8, in every mode** — the доводка loop, between the blind acceptance and the report. It changes no cell above: it asks the user nothing, and it approves nothing with them.

**`interview` and `manual` differ in exactly two cells** — the spec gate and the plan gate. If you find yourself treating them differently anywhere else, one of them is wrong.

**The manifest gates run in every mode.** They are checks against the user's own words, not requests for the user's time — no mode buys the right to skip them.

| Gate | After phase | Condition to pass |
|---|---|---|
| **G1** | 2 Briefing | every requirement has a status; none left `open` without a reason recorded |
| **G2** | 3 Spec | every live requirement is `in-spec`, `deferred`, or `dropped`, zero `open` — **and an independent reader given only the brief and the spec finds nothing missing** |
| **G3** | 4 Plan | every `in-spec` maps to ≥1 ticket, **and every ticket traces back to ≥1 requirement** |
| **G4** | 8 Final | blind acceptance run against the brief, spec withheld; every disagreement with the manifest reported |

**G2 and G4 are the same check at the two ends of the flight, and both are needed.** They measure the build against the user's own words, with your paraphrase of them taken away — G2 while the answer is a paragraph of spec, G4 when it is the last chance to know. Everything in between measures against the spec, because that is the contract the executors were actually given; judging a subagent by words it never saw produces findings nobody can act on.

A failed gate is not a warning. It sends the phase back to be redone — see `phases/1-manifest.md`.

**The plan may be corrected; the brief may not.** When the build proves the plan wrong — a data model that does not hold, an assumed interface that cannot exist — the spec is amended and a `D##` row records what the code demonstrated and when. That is the one thing allowed into the manifest after the briefing, it never retires a requirement, and it is never a route for an idea you had. Rules in `phases/5-subagents.md`.

## Secrets

Credentials are the user's to hold, not the agent's to handle. This section binds every phase; the phases do not restate it.

- **Never request one.** No key, token, password, connection string, or card number is ever a question. *Which* provider is a question. *Whether* an account exists is a question. The credential is not.
- **Redact at ingest, before anything is written.** The brief, every user answer, and every pasted fragment pass the redaction gate in `phases/1-manifest.md` *before* they reach a file. A detected secret becomes `[REDACTED:<VAR_NAME>]` — the variable name survives, the value does not.
- **"Verbatim" always means "verbatim after redaction."** Wherever this skill asks for the user's exact words, it asks for them redacted. The two rules are one rule.
- **Refer to it by name.** `STRIPE_SECRET_KEY`, not the value. The user puts the value in `.env` themselves; `.env` is in `.gitignore` before the first commit; the final report lists which names are still empty.
- **A leaked secret is a stop condition.** A secret that reached a file or a commit is reported immediately, in plain language, with the advice to rotate it. Before the first commit, run the redaction gate over the whole of `.autopilot/`.

## Files this skill owns

```
.autopilot/
├── <feature-slug>/
│   ├── <YYYY-MM-DD>-brief.md   the user's original words, redacted, never edited again
│   ├── manifest.md      R01…Rnn — requirements and their status
│   ├── reference.md     what the result should be like — the user's comparables, never yours
│   ├── spec.md          the specification
│   ├── interfaces.md    the boundaries from the spec, then what finished tickets built
│   └── tickets/NN-<slug>.md
├── README.md            how to read this folder — for the human, written once in Phase 0
├── state.js             the run state, and the only file you update: stages, tickets, timings, debt
└── dashboard.html       the human view — copied once in Phase 0, then reads state.js by itself

CLAUDE.md | AGENTS.md   the project memory — what the next session reads first
docs/adr/               decisions worth outliving the run — written in Phase 9, tier T2+
```

The brief is dated in its filename because a slug directory outlives one sitting. The dashboard is opened for the user, not described to them: it shows the eight stages of the cycle, where the run is now, and a live clock on the run, the current stage and the current ticket.

`.autopilot/` is the record of **this** run; the memory file at the root is the project as it stands, for whoever opens the repo next; `docs/adr/` is why it stands that way. Autopilot's content in the memory file lives between `<!-- autopilot:start -->` markers — everything the user wrote outside them is untouchable. See `phases/9-memory.md`.

The three are not interchangeable, and the split is what keeps the spec throwaway. `spec.md` is worth nothing the day the work ships; the reasoning inside it — why this data model, what the build proved wrong, which word means which thing — is worth something for years, and it dies with `.autopilot/` unless something routes it out. That is what the ADRs are for.

`.autopilot/` is committed, not ignored — it is the user's record of what was promised and what was delivered. A run that leaves nothing under `.autopilot/` did not happen.

## Judgement

This skill describes a process, not the product. Its numbers — tiers, question counts, story counts, wave widths — are **calibration for a first guess, never targets to hit.** A spec written to reach a story count, or a plan cut to land inside a tier, has optimised for the rule instead of for the person who asked.

The rules below are the same kind of thing. Each one is here because it was paid for, and each is an argument — arguments can lose. Where following one would make the result worse for the user, break it deliberately, say so in one line, and carry on. That is a decision, and decisions get recorded. What is never acceptable is breaking one quietly, or keeping one because it is written down.

**Five rules are not calibration and do not lose.** They hold in every mode, at every depth, at every tier:

1. **A requirement is removed only by the user**, in their own words, quoted into the manifest.
2. **A secret is never requested, echoed, or written** — not into a file, a prompt, a commit, or a report.
3. **A fact about the user is never invented.** Prices, texts, addresses, accounts stay visible placeholders until they supply them.
4. **An irreversible or outward-facing action is a question** — deploy, publish, pay, message a third party, delete data, rewrite history.
5. **The orchestrator does not write the project's code.** Its keyboard reaches `.autopilot/`, the memory file and git. Everything else — a fix worth two lines, a red test, a review finding — travels down to a subagent. Rules in `phases/5-subagents.md`.

Everything else is argument.

## Rationalizations — the ones that cost the user the product

Phase-specific mechanics are not here; they live in the phase that owns them. What follows is the short list of excuses that end with the user getting something other than what they asked for.

| Excuse | Reality |
|--------|---------|
| «Пользователь сказал не задавать вопросов» | Он сказал не задавать ЛИШНИХ. Решающие вопросы — часть работы, не обсуждение процесса. |
| «KISS — просто собери» | Простой результат даёт порядок, а не пропуск этапов. Без спецификации каждая правка — «а я имел в виду другое». |
| «Бриф весь в диалоге, зачем его переписывать в файл» | Диалог сжимается, и бриф в нём — самое старое. Через три фазы ты будешь синтезировать по пересказу пересказа. |
| «Это требование явно неважное, пропущу» | Важность требований определяет пользователь. Ты можешь предложить `deferred` — вычеркнуть может только он. |
| «Пользователь про это больше не вспоминал — значит, отменил» | Молчание не отменяет. Отмена — это его слова, записанные в манифест цитатой. |
| «Сделаю заглушку, уточнит потом» | Блокирующие неизвестные (оплата, хостинг, аккаунты) решаются в брифинге — в полном автомате в self-briefing, — но всегда до билда. |
| «Пусть пришлёт ключ, я вставлю в код» | Ключи вставляет пользователь и только в `.env`. Ты работаешь с именем переменной. |
| «Ключ уже в контексте, значит, можно записать» | Наоборот: значит, надо отредактировать и предупредить. Контекст — не разрешение. |
| «Быстрее всё сделать в одном контексте» | Быстрее в первый час. Дальше модель ходит кругами и ломает работавшее. |
| «Исполнитель написал, что не смог, — доделаю сам, я же в контексте» | Ты в контексте всего прогона — поэтому и нельзя. Каждая правка твоими руками оставляет у тебя дифф до конца сборки и ухудшает каждый следующий таск. Не смог — значит, дозапрос ему или свежий контекст, но не твои руки. |
| «Тут правки на две строки — гонять субагента дороже» | Дороже этому таску. Платят все следующие: контекст оркестратора тратится один раз и не возвращается. К восьмому таску разница — между «собрал» и «сломал работавшее». |
| «Бриф краткий — значит, и спецификация краткая» | Бриф — силуэт: пользователь описал happy path и не описал ни пустых состояний, ни ошибок, ни обрывов. На нормальной и максимальной глубине продумать их — твоя работа. |
| «Это и так очевидно, писать не буду» | Очевидное тебе — не зафиксировано, и каждый субагент додумает его по-своему: три исполнителя — три разные «очевидности». Манифест и спецификация — единственные точки сверки. |
| «Придумал полезную фичу, добавлю» | Углубление заказанного (`R##.n`) — да. Новая возможность (`A`) — только с родительским требованием, в пределах пропорции и в отчёт. На `strict` — нельзя вообще. |
| «Полный автомат — значит можно и задеплоить» | Автомат снимает вопросы о продукте, а не право на необратимое. Деплой, оплата, рассылка, удаление — гейт во всех режимах. |
| «В полном автомате можно додумать за пользователя всё» | Решения — да, и все в ASSUMPTIONS. Факты о пользователе (цены, тексты, аккаунты) — нет: заглушка и строка в отчёте. |
| «Напишу "запускаю через 60 секунд"» | Ты не умеешь ждать — обещанной паузы не будет. Честная формулировка: «начинаю, скажи стоп». |
| «В ручном режиме тоже начну и подожду возражений» | В ручном согласование — это явное «ок». Молчание им не является, начатая работа тем более. |
| «Сверю результат со спецификацией, этого хватит» | Спецификация может уже потерять требование. Финальная сверка идёт с брифом и без спецификации — иначе она подтвердит собственную ошибку. |
| «Покрытие проверю сам — я же только что писал спецификацию» | Тот, кто писал, не видит, чего не написал. На G2 бриф и спецификацию читает субагент, которому не дают ни манифеста, ни разговора. |
| «Правило про тесты записано в фазе — значит, оно действует» | Действует только то, что доехало в промпт исполнителя. Фазовый файл читает оркестратор, а код пишет не он. |
| «Интерфейсы устаканятся по ходу — первый таск задаст» | Тогда их задаст тот, кто видел одну восьмую задачи. Границы модулей решаются до нарезки, иначе восемь контекстов договариваются задним числом. |
| «Отчёт напишу по памяти — я же всё это и делал» | К восьмой фазе твой контекст самый загрязнённый за весь прогон. Отчёт собирается из `manifest.md` и `state.js`, перечитанных с диска. |
| «Обоснования решений останутся в спецификации» | Спецификация умирает вместе с прогоном. То, что должно пережить его, уходит в ADR — иначе следующая сессия переоткроет те же решения. |
| «Пользователь сказал "погриль меня" — покажу и спецификацию» | Режим интервью покупает вопросы, а не гейты. Гейты — это «ручной режим», и это отдельное слово, которое он не сказал. |
| «Таски и спецификация видны в чате — зачем файлы» | Файл в `.autopilot/` и есть артефакт; чат — только его пересказ. Диалог умрёт, файлы останутся. |
| «Пользователь не спрашивал про режимы — не буду грузить» | Он и не спросит: в чате нет `--help`. Пять строк в начале — единственное место, где он вообще узнаёт, что у сборки есть ручки. |
| «Просил вылизать — критик разберётся, с чем сравнивать» | Не разберётся: он придумает эталон и погонит сборку к нему. Нет эталона от пользователя — доводка не запускается, и это ответ, а не отказ. |
| «Круг доводки нашёл мелочь — поправлю сам, это же не таск» | Тогда правка идёт без ревью, без зелёного прогона и без точки отката. Доводка — это ещё таски, а не право взять клавиатуру. |
| «Критик всё ещё недоволен — значит, рано останавливаться» | Он будет недоволен всегда: ему за это и платят. Остановка — это отсутствие находок, потолок кругов или слово пользователя. |
| «Проект собран, тесты зелёные — значит, работает» | Тесты писал тот же процесс, что и код. Пока проект никто не запустил, «работает» — это гипотеза, а первым его запустит пользователь. |

## Red Flags — start the phase over

Every line here means something the user asked for is at risk. Phase mechanics — instruments, timestamps, wave bookkeeping, memory-file detection — are checked in the phase files that own them, not here.

- Writing code before the spec exists.
- The brief was never written to its file — the run is anchored to nothing.
- A requirement left the manifest without a status, or was marked `dropped` without a quote of the user saying so.
- Past gate G3: a ticket that traces to no requirement, or a requirement that traces to no ticket.
- Spec or tickets that exist only in the dialogue — nothing written under `.autopilot/`.
- Instruments that disagree with the chat: a stage still `active` after you moved on, a ticket running while the dashboard calls it `pending`, a ticket carrying the run's `startedAt` instead of its own, timestamps filled in afterwards from memory. The user believes the screen over your sentences, which is the whole reason it exists.
- The announced depth and the actual spec diverge: a bare restatement of the brief at normal or deep, or an invented capability — any `A##` — at strict.
- Gate G2 passed on your own reading of your own spec — the independent coverage check skipped, or its checker handed the manifest.
- Final acceptance measured against the spec instead of blind against the brief.
- The blind checker, the coverage checker or the memory subagent handed `spec.md`, the manifest or the tickets — whichever of those it was supposed to be blind to. Independence is the entire mechanism; without it each of them confirms the plan instead of the thing.
- The final report composed from memory instead of from `manifest.md`, `state.js` and the two subagents' returns, re-read from disk.
- A T2+ run that ended with no ADR: every `D##` and every load-bearing implementation decision left to die with `.autopilot/`.
- The finished project was never actually run — accepted on green tests and a reading of the code.
- Starting without announcing mode and depth, or announcing one and behaving as another: questions in full, a spec put up for approval in interview, a start-and-see instead of «ок» in manual.
- With `polish` on: a доводка round run against no reference, its findings applied outside the ticket path, a fourth round, or a round that broke something and was patched instead of reverted.
- A comparable in `reference.md` that the user never named — your taste entered as though it were theirs, and everything downstream now judges the build against it.
- The adversarial pass skipped in `interview` because the brief «выглядел продуманным» — or used to argue the user out of a requirement instead of into a decision.
- A blocking unknown — payment, hosting, an account, where the data lives — left unasked in semi, interview or manual because the brief «выглядел понятным». Asking nothing is legitimate only when nothing is open; a manufactured question and a skipped blocking one are both defects, in opposite directions.
- Promising the user a wait — a countdown, «через минуту», «если не ответишь за N секунд» — that you have no way to honour.
- In full: an invented fact about the user standing where an ASSUMPTION, a stub, or a PLACEHOLDER belongs.
- Asking the user a process question — which tracker, which doc file, which memory file, ticket granularity, code review — outside manual, where spec and tickets are gates by design.
- A requirement quietly narrowed to whatever happened to work, or the spec amended mid-build with no `D##` row recording why.
- Two tickets in one subagent context, or two tickets in one commit.
- The orchestrator editing a file outside `.autopilot/`: a fix «на две строки», a red test, a review finding applied by hand instead of sent down. One such edit is the whole failure — the diff stays in its context for the rest of the run.
- A ticket's diff, or the raw output of a full test run, read into the orchestrator's context. It needs a verdict and the names of what failed, not the material.
- A repair started from an empty context when the ticket's own executor was still reachable — or the mirror failure, a third дозапрос into an executor that has already failed to do it twice.
- Parallel subagents editing the same files — or the mirror failure, independent tickets flown one at a time with the plan's parallelism thrown away in the delivery.
- A subagent launched without `interfaces.md`, or finishing without returning the contract block.
- The first wave launched with `interfaces.md` still empty — module boundaries left for whichever ticket happens to reach them first.
- A subagent prompt with no testing rules in it: the discipline written in the phase file the orchestrator reads, and absent from the handoff to the one who writes the code.
- Payment, hosting, or accounts first mentioned at the finish line.
- A secret value asked for, repeated back, or written into any file, prompt, commit, or report.
- Installing a package or fetching remote code without the user asking for it.
- Text outside the `autopilot` markers edited, moved or dropped, or the run ending with no project memory file at all.
