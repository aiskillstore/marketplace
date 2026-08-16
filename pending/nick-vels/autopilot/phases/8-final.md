# Phase 8 — Touchdown

Landing. Two things happen here, and the first one is the reason this framework exists. A third — the доводка loop — happens between them, and only when the `polish` parameter is on.

## 1. Blind acceptance — gate G4

Every check so far has measured the build against the **spec**. But the spec is your own paraphrase of the brief, written several phases ago. If a requirement was lost on the way into it, everything downstream has been faithfully confirming that loss.

So the last check does not use the spec.

**Spawn a subagent that receives:**

- `.autopilot/<slug>/<дата>-brief.md` — the user's own words (the path is `briefFile` in `state.js`)
- the repository as it now stands
- how to run the project and its tests

**It must not receive:** `spec.md`, `manifest.md`, the tickets, or any summary of them. A checker given the spec inherits the spec's blind spots and will confirm them. Independence is the entire mechanism — take it away and this phase is theatre.

Its brief:

> Прочитай приложенный файл брифа — это задача, которую поставил заказчик. Затем изучи
> репозиторий и определи, что из этого действительно реализовано.
>
> **Запусти проект** — команды в приложенном описании — и пройди основной сценарий так,
> как прошёл бы его заказчик. Чтение кода показывает намерение, запуск показывает результат.
> Если проект не поднимается или сценарий обрывается — это и есть главная находка
> проверки, поставь её первым пунктом. Если запустить нельзя вообще (нужен аккаунт,
> ключ, внешний сервис) — скажи прямо, что именно помешало, и не выдавай чтение кода
> за проверку работоспособности.
>
> По каждому требованию из брифа: реализовано / частично / нет — и одна строка,
> где именно это видно (что ты увидел при запуске, или где это в коде,
> или почему ты решил, что этого нет).
>
> Не оценивай качество кода. Не предлагай улучшений. Не ищи оправданий
> отсутствию — просто зафиксируй факт. Если требование выполнено формально,
> но по сути не работает (данные сохраняются, но пользователю не показываются) —
> это «частично», а не «реализовано».

**Then compare its verdict with `manifest.md`:**

| Manifest says | Blind says | Meaning |
|---|---|---|
| `done` | реализовано | agreed |
| `done` | **частично / нет** | 🔴 **drift** — the manifest is wrong. Report it, and fix it if it is small |
| `placeholder` | частично | expected — confirm the placeholder is visible, not an invented fact |
| `dropped` / `deferred` | нет | expected — must appear in the report as not built |
| — | реализовано, но не из брифа | scope that grew without a parent; report it |

Every 🔴 goes in the report **and** in `state.js` under `blind`. A drift found here is not a failure of the run — it is the run working. Hiding it is the failure.

If there are no tickets (tier T0), this check still runs. Small builds drift too, and it is one subagent.

**A build that was never run is a build nobody has seen work.** The tests were written by the same process that wrote the code, so they agree with it by construction; the first time this project meets a user must not be the first time it is launched. If it genuinely cannot be run here — no credentials, a service that needs an account, a platform this machine is not — that goes in the report as an open item under «что нужно от тебя», not silently into the accepted column.

## 2. What outlives the run — memory and decisions

**Launch these at the same time as the blind acceptance.** Up to three subagents in one slot, no contact between them, each answering a different question:

| Agent | Question | Receives | Never receives |
|---|---|---|---|
| blind checker | что из брифа сделано | the brief, the repo | `spec.md`, `manifest.md`, tickets |
| memory | как этим пользоваться завтра | the repo, `interfaces.md`, the memory file, the tier | `spec.md`, tickets |
| ADR *(tier T2+)* | почему сделано именно так | `spec.md`, `manifest.md` | the repo — it documents decisions, not code |

The memory agent writes the full description of the project into `CLAUDE.md` or `AGENTS.md` — architecture, key files, conventions, environment, tests, gotchas — scaled to the tier, folding in what `interfaces.md` accumulated. Like the blind checker, **it does not receive `spec.md` or the tickets**: a memory written from the plan documents intentions, and the next session has no way to tell the difference.

The ADR agent is the mirror image and that is why it cannot be the same one. **`spec.md` dies with the run**, and with it every «почему так» in it — the reason for the data model, what the build proved wrong at ticket four, which word the project uses for which thing. Six months later the next session reads working code and no reason for any of it, and re-opens decisions that were settled here. At tier T2+ that is worth three files in `docs/adr/`; below it, the memory file carries what little there is.

Everything about all of this — which memory file, the markers, the sections per tier, what an ADR contains, and the verification pass over the commands — is in `phases/9-memory.md`. Read it before spawning.

This is the artifact that decides what the *next* run costs. A project whose second session begins by re-reading the whole codebase paid for that in the first session and got nothing.

## 2a. Доводка — only with `polish` on

If the run has the `polish` parameter, the loop goes **here**: after the blind acceptance has said what is and is not built, and before the report describes the result. Both halves of that matter. The blind verdict is the baseline the regression rule compares against, and a report written before the loop describes a build that no longer exists.

Read `phases/polish.md` now — and only now. On a run without the parameter, skip this section entirely and do not read the file.

Without `polish`, nothing changes: the blind checker's findings go into the report as open items, exactly as below.

## 3. The final report

Run the full test suite once more first — truncated, `2>&1 | tail -30`, for the same reason as after every ticket — and wait for both subagents. Then write in the user's language, plain, no jargon.

### Where every line of it comes from

**Re-read the files. Do not write this from memory.**

By the time you reach this phase your context is the most polluted it has been all run — the brief, the manifest, the briefing, the spec, every phase file, and the returns of every subagent, most of it compacted at least once. The report is the one artifact the user actually reads, and writing it from that is how a `deferred` requirement gets reported as done, a placeholder disappears, and an `A##` nobody ordered turns up in the summary as if they had asked for it.

So build each section from its source, opened now:

| Section | Read from |
|---|---|
| Решения, принятые за вас | `manifest.md` — every `ASSUMPTION` in Основание |
| Готово | the blind checker's return, not the manifest's `done` rows |
| Доводка *(only with `polish`)* | `state.js` → `polish`, and `reference.md` for what was compared against |
| Что нужно от тебя | `manifest.md` `placeholder` rows + `state.js` → `debt` |
| Что не вошло | `manifest.md` `deferred` and `dropped` rows, with their quotes |
| Что я добавил сверх заказанного | `state.js` → `additions`, cross-checked against `A##` in the spec |
| Что пошло не по плану | every `D##` row in `manifest.md` |
| Открытые вопросы | `state.js` → `blind`, plus anything in `coverage` that ended up not built |
| Запустить / Где что лежит | `state.js` → `memoryFile`, `briefFile`, and the commands the memory agent verified |

Two of these are worth naming, because memory gets them wrong in a specific direction. **«Готово» comes from the blind checker, not from your own bookkeeping** — the manifest says what you believe was delivered, and the whole point of the previous section is that those two can disagree. And **«Что не вошло» comes from the rows, not from recollection**: a requirement dropped in the first ten minutes of a three-hour run is exactly the one you will not remember, and it is quoted in the file.

Order matters — the user reads the top and skims the rest.

**In full mode, the report opens with «Решения, принятые за вас»** — every `ASSUMPTION` from the self-briefing, in plain language, each with the one-line reason. They never asked for these; they have the right to see all of them in one place, first.

```markdown
## Готово

<Что теперь работает — 3–6 строк обычным языком, от лица пользователя.>

**Запустить:**
```
npm install && npm run dev
```
Открыть http://localhost:3000

## Что нужно от тебя

1. Впиши в `.env` — `TELEGRAM_BOT_TOKEN`, `GOOGLE_SHEETS_ID`.
   Файл `.env.example` уже лежит рядом, скопируй и заполни.
2. Замени заглушки: цены в `src/data/prices.ts`, тексты писем
   в `src/emails/`. Сейчас там видимые метки `[ВПИШИ]`, не выдуманные значения.

## Что не вошло

| Что | Почему |
|---|---|
| Уведомления на SMS | ты сказал «SMS не надо, только телега» |
| Админка для заявок | отложено: заявки видно в таблице, отдельный экран — следующий заход |

## Что я добавил сверх заказанного

<Каждая `A##`-история, дошедшая до кода, — обычным языком, с требованием,
ради которого добавлена. Раздел опускается только если добавлений не было
(на глубине `strict` — всегда). Пользователь должен узнать о них отсюда,
а не наткнувшись в коде.>

| Что добавил | Ради чего |
|---|---|
| Номер заявки в подтверждении | чтобы клиент мог на неё сослаться — R01 |

## Что пошло не по плану

<Каждая строка `D##` из манифеста — обычным языком: что задумывалось,
что этому помешало и как сделано вместо. Раздел опускается, только если
`D##` не было. Требование при этом то же — меняется способ, а не заказ.>

| Что не сработало | Как сделано |
|---|---|
| Одна заявка на один адрес — у половины клиентов адресов два | Адреса вынесены в список, форма принимает несколько |

## Открытые вопросы

<Расхождения слепой приёмки, если есть. Прямо, без смягчения:
«Требование "клиент видит статус" я считал готовым, независимая проверка
показала, что статус сохраняется, но нигде не отображается. Исправлено /
требует отдельного таска.»

Сюда же — то, что нашла сверка покрытия на спецификации и что в итоге
НЕ построено. Найденное и построенное здесь не упоминается: гейт
отработал, пользователю нечего с этим делать.>

## Где что лежит

- Описание проекта для следующего раза — `AGENTS.md` в корне
- Почему сделано именно так — `docs/adr/` (если проект крупный)
- Прогресс и цифры — `.autopilot/dashboard.html`
- Твоя изначальная задача — `.autopilot/<slug>/<дата>-brief.md`
- Требования и их судьба — `.autopilot/<slug>/manifest.md`
- Спецификация — `.autopilot/<slug>/spec.md`
```

## Rules for the report

- **Плейсхолдеры и пустые переменные — обязательный раздел**, даже если их ноль (тогда одной строкой: «всё заполнено»). Это то, что отделяет «работает» от «работает у тебя».
- **Секреты — только именами.** Никогда значениями, включая те, что пользователь присылал сам.
- **«Что не вошло» пишется всегда**, даже когда всё вошло. Пустой раздел с одной строкой честнее отсутствующего: он показывает, что вопрос задавался.
- **Не приукрашивать.** Упавший тест, невыполненный таск, найденное расхождение — называются прямо, с тем, что именно сломано и что для починки нужно. Отчёт, скрывающий дефект, стоит дороже дефекта.
- **Никаких диффов, имён файлов кода, названий тестов** — они в инструментах, для тех, кому нужны.

## Closing the instruments

The memory file goes in with the final commit, before this. Then, in `state.js` and nowhere else: set `finishedAt`, write the `blind` block, refresh the counts, close every stage — `final` to `done`, and anything still `active` or `pending` to `done`, `skipped` (with a note) or `failed`, whichever is true. A run whose dashboard says «в работе» a day after it landed is lying to the person who trusted it.

The open page picks this up by itself within ten seconds — this is the picture the user is left with, and it arrives without you doing anything more.

`finishedAt` also stops the clocks and the ten-second polling: the page freezes on the final numbers instead of counting time nobody is spending. Leave it `null` on a finished run and the user's total keeps growing overnight.

**Then, and only then, put out the server** — the one Phase 0 started for the pane (`phases/0-instruments.md`). It goes last because the page has to fetch the final state first, and it goes at all because a run that ends leaving an HTTP server on the user's machine has left something running that nobody will ever think to stop:

```bash
[ -f .autopilot/serve.pid ] && kill "$(cut -d' ' -f2 .autopilot/serve.pid)" 2>/dev/null; rm -f .autopilot/serve.pid
```

The pane keeps the final picture on screen — it is already rendered and no longer polling. Nothing is lost with the port: `dashboard.html` is a static file, and a double-click reopens it in a real browser with every number intact. Say nothing about any of this; the shutdown is not news. If доводка is running (`phases/polish.md`), the run is not over — the server stays up until the доводка closes too.
