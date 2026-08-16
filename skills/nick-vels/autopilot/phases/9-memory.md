# Phase 9 — Project memory

The file the **next** session reads. Not a phase in sequence — started in Phase 0, topped up during the build, finished in Phase 8.

Four files describe this project and they are not interchangeable. Confusing them is how documentation rots.

| File | Question it answers | Lifetime |
|---|---|---|
| `.autopilot/<slug>/` | what was promised and what was delivered **in this run** | forever, but it is history |
| `.autopilot/<slug>/interfaces.md` | what the previous tickets built, for the tickets still to come | **dies with the run** |
| `CLAUDE.md` / `AGENTS.md` | what an agent needs to work in this repo **tomorrow** | forever, and it is the present tense |
| `docs/adr/` | **why** it is the way it is, and what was considered instead | forever, and it is past tense on purpose |

The last two are what this file is about. Everything in the memory file must be true of the repository *as it stands* — not of the plan, not of the run that produced it. Everything in an ADR is true of the moment it was decided, and stays written even when it is later reversed; that is what makes it a record rather than a second, staler copy of the memory file.

**Phase 0's share of this file is not here — it is `phases/0-memory.md`**: which file to write, and the skeleton to put in it. That is Moment 1, which is why the moments below start at two. This file is read **inside Phase 5** for what may be appended during the build, and **in Phase 8** for the full description and the ADRs. Nothing below applies until there is code to describe.

## Where the content lives — the markers

Everything Autopilot writes sits between two markers, in every case, including a file it created itself:

```markdown
<!-- autopilot:start -->
...
<!-- autopilot:end -->
```

One rule, and it buys two things: updating is «replace what is between the markers», and **anything the user wrote outside them is untouchable**. A brownfield repo whose CLAUDE.md carries a team's hard-won rules must come out of an Autopilot run with those rules intact.

If the markers are missing on a later run but Autopilot's sections are recognisably there, wrap them — do not append a second copy.

## Moment 2 — during the build

Append only **facts that were discovered and cost something to discover**. One line each, no rewrite of the file:

- the real test command, once it is known — and how to run a single file;
- a gotcha that ate time: an ordering dependency, a version pin, a platform quirk;
- a new variable in `.env.example`;
- a decision a subagent had to make that the next one must not re-litigate.

That is the whole list. What must **not** go in, from the CLAUDE.md quality rules:

- generic advice («пиши тесты», «используй понятные имена») — true everywhere, useful nowhere;
- restatements of the obvious («класс `UserService` работает с пользователями») — the name already said it;
- one-off fixes and commit-by-commit history — that is what `.autopilot/` and git are for;
- long explanations of a standard technology — a link or one clause, never a paragraph;
- anything that duplicates `interfaces.md` while the run is still going. Interfaces are folded in **once**, at the end.

If nothing was discovered during a ticket, nothing is written. Most tickets write nothing, and that is the correct rate.

## Moment 3 — the full description (Phase 8)

Now the code exists, so now the architecture can be described from the code instead of from the plan.

**Spawn a subagent.** It runs in parallel with the blind-acceptance agent — they read the same finished repo and never see each other's output.

It receives: the repository, the current memory file, `interfaces.md`, the tier, and the commands to run and test the project.

**It must not receive `spec.md` or the tickets.** A memory written from the spec documents intentions; the next session trusts it and gets lied to by a file whose whole job is to be trusted. Same reasoning as the blind acceptance — different purpose, identical mechanism.

Its brief:

> Опиши проект так, чтобы агент, впервые открывший этот репозиторий, начал
> работать без разведки. Источник — только код, который ты видишь.
>
> Пиши плотно: одна строка на мысль. Не пересказывай очевидное из имён,
> не давай общих советов, не объясняй, что такое известные технологии.
> Каждая команда должна запускаться копипастом, каждый путь — существовать.
>
> Если чего-то в коде нет — раздела нет. Пустой раздел хуже отсутствующего.

### What the sections are, by tier

The file scales with the project, exactly like the ticket tiers do.

**T0–T1 — короткий файл:**

| Раздел | Что внутри |
|---|---|
| Заголовок и строка | что это и для кого |
| Команды | установка, запуск, тесты, сборка — проверенные |
| Структура | дерево на 5–15 строк, у каждой папки — назначение |
| Подводные камни | то, что неочевидно и уже кого-то укусило |
| Как здесь работает Autopilot | из скелета, без изменений |

**T2–T3 — плюс к этому:**

| Раздел | Что внутри |
|---|---|
| Ключевые файлы | точки входа и модули, которые придётся трогать чаще всего |
| Архитектура | как части связаны: поток данных, кто кого вызывает, где границы |
| Соглашения кода | принятые в этом проекте, а не в мире вообще |
| Окружение | имена переменных и зачем каждая — **никогда значения** |
| Тесты | чем и как; где лежат; как гонять один файл |

### Folding in interfaces.md

`interfaces.md` is a working contract between tickets, and its life ends with the run. Its durable content — public signatures, schemas, event formats, module ownership — becomes the Архитектура and Ключевые файлы sections. What does not survive: the per-ticket framing («Из таска 03…»), anything already obvious from the code, and any instruction addressed to a subagent.

The file itself stays in `.autopilot/<slug>/` as the run's record. It is not deleted and it is not maintained.

### Before writing — verify

Currency is the criterion this file fails first and most quietly. So, before the block is written:

1. **Run the commands** it documents — at minimum install, test, and build. A command that fails does not go in.
2. **Check every path** exists.
3. **Grep the block for secret values** — the redaction gate from `phases/1-manifest.md` applies here as it does everywhere. Variable names, never values.
4. **Check the length against the tier.** A landing page with a two-page memory file has been padded, and padding is how a reader learns to skim.

Then write the block between the markers, commit it with the final commit, and note the chosen file in the Phase 8 report under «Где что лежит».

## Moment 4 — the ADRs (Phase 8, tier T2+)

**Runs at tier T2 and above.** Below that there is not enough decided to be worth a folder, and what little there is goes in the memory file's Подводные камни.

The memory file answers «как этим пользоваться». It deliberately does not answer «почему так» — a file that tries to be both grows past the length at which anyone reads it, and the reasoning is what gets skimmed. But the reasoning is exactly what the next session needs in order not to undo this one: code shows what was chosen and is silent about what was rejected and why, so an agent reading only the code will cheerfully re-open a settled question and pick the option that was already tried.

`spec.md` holds all of it right now and is worthless the day the work ships. So this is the routing step: **what deserves to survive comes out of the spec and into `docs/adr/`, and the spec stays throwaway.**

### What earns an ADR

Three sources, and nothing else:

| Source | Why it qualifies |
|---|---|
| every `D##` row | the build proved the plan wrong. This is the highest-value kind: it records a road already walked and found closed |
| load-bearing entries from **Решения по реализации** | the data model, the module boundaries, an external service, a schema — anything whose reversal means rebuilding rather than editing |
| a term the project uses in its own way | one ADR for the vocabulary, if the spec introduced any. This is what makes the next spec speak the same language instead of inventing synonyms |

What does **not** earn one: a decision with no alternative (there was one library and you used it), anything a linter or the framework decided, and anything that is simply the obvious default. An ADR asserting that you chose the standard option for the standard reason teaches nothing and dilutes the ones that do.

Three to six files on a T2 build, five to twelve on T3. More than that means the filter was not applied.

### Spawn it in parallel with the other two

It receives **`spec.md` and `manifest.md`, and not the repository** — it documents decisions, not code, and giving it the repo turns it into a second memory agent writing a worse version of the same file.

> По приложенным спецификации и манифесту напиши по одному ADR на каждое решение,
> которое дорого отменять, и на каждую строку `D##`.
>
> Формат — `docs/adr/NNNN-<краткое-название>.md`, нумерация с `0001`, по файлу
> на решение. Внутри четыре раздела и больше ничего:
>
> **Контекст** — что было известно на момент решения. Одна-две строки.
> **Решение** — что решили, в настоящем времени: «Заявки хранятся в SQLite».
> **Почему** — и, главное, что рассмотрели и отвергли. Отвергнутый вариант
> без причины бесполезен: пиши, чем именно он не подошёл.
> **Последствия** — с чем теперь придётся жить, включая неприятное.
>
> Для `D##` контекст — это то, что план предполагал, а решение — то, что
> код доказал. Такой ADR ценнее остальных: он закрывает дорогу, по которой
> кто-то иначе пойдёт заново.
>
> Не пиши ADR на решение, у которого не было альтернативы. Не пересказывай
> спецификацию. Не описывай код — ты его не видел, и это не твоя работа.

If `docs/adr/` already exists, **continue its numbering and its format** — an existing convention in the repo beats this one, exactly as `CONTEXT.md` beats invented vocabulary in Phase 3. Never renumber what is already there.

The ADRs go in with the final commit, alongside the memory file, and get one line in the report under «Где что лежит».

## On resume

The memory file is the **first** thing to read on resume, before `state.js` — it is the cheapest possible re-entry into a project. If it is missing or plainly stale against the code, that is a defect of the previous run: fix it as part of the current one, do not work around it.

`docs/adr/` is **not** read on resume — it is for the session after this one, and reading a folder of past reasoning is exactly the kind of re-orientation the memory file exists to make unnecessary. Read one only when a decision is about to be reversed.
