# Phase 3 — Flightplan

Turn the manifest and the briefing answers into a specification. **This phase does not reopen the interview** — what is still unresolved becomes a `placeholder` row, not another round of questions.

One exception, and it is narrow: a genuine fork the briefing missed, where the two branches are different projects and a placeholder would only defer the same question to the build. Ask it, once, in one line, with a recommended answer. In **full** mode there is no exception — decide it and record the `ASSUMPTION`.

Write to `.autopilot/<slug>/spec.md`. What the user sees in the dialogue is a two-line summary; the file is the spec.

## Depth

**The brief is a silhouette.** The user describes what happens when everything goes right, at the level of «принимает заявки и складывает в таблицу». They do not describe what the third screen says when the network drops, what an empty list looks like, what happens on a double submit, or what the very first launch shows before any data exists. They are not withholding those answers — they do not have them, and they are not supposed to.

Working them out is the most valuable thing this phase can do. A spec that merely restates the brief in tidier words has produced nothing, and it guarantees the gaps get filled during implementation by whichever subagent hits them first, differently each time.

Where the adversarial pass ran in Phase 2, its craft findings land here — the ones nobody needed to be asked about. They arrive as `R##.n` stories like anything else; what makes them worth their own mention is that they are usually the ones the depth pass below would not have produced, because they came from asking where the idea breaks rather than where a requirement is thin.

**How far to take it is the user's setting, not yours.** Read it from the announced depth:

| Depth | The depth pass below | `A##` new capabilities |
|---|---|---|
| **strict** | not run. Only *Wrong input* and *Failure*, and only where the requirement plainly breaks without them | **forbidden** — cut them, do not write them |
| **normal** *(default)* | run by judgement — the dimensions that plainly matter for that requirement, skipping the ones that do not | allowed, with parent and proportion |
| **deep** | run in full — every dimension, every requirement, or an explicit «не применимо» | encouraged, same parent and proportion |

At **strict**, an idea you had that the brief did not ask for does not become a spec section and does not become a note. It is simply not written. The user chose this setting to get exactly what they asked for, and a spec that argues with that choice has ignored an instruction.

At **normal**, use judgement rather than a checklist. Elaborate where the gap would obviously cause a bad build; do not chase every edge of every requirement. Most briefs belong here.

At **deep**, the pass is mechanical and exhaustive — that is what was asked for.

### The depth pass

Run at **normal** and **deep** (see the table above for how completely). Every `R##` requirement goes through this list.

At **deep**, skipping a dimension because a requirement «и так понятная» is exactly the mistake this pass exists to prevent — write «не применимо» instead of skipping silently.

| Dimension | The question the brief never answered |
|---|---|
| **First run** | what does this look like before any data exists? |
| **Empty** | zero items, zero results, zero history — what is on screen, and what invites the next step? |
| **Wrong input** | what does the user see, in their language, and what survives of what they typed? |
| **Failure** | the network, the service, the disk — what breaks, what is said, what is retried, what is lost |
| **Interruption** | closed halfway, refreshed, sent twice — does it resume, restart, or duplicate? |
| **Growth** | ten items versus ten thousand — what has to change, and does it now or later? |
| **Boundaries** | who may do this, and what happens to someone who may not? |
| **Aftermath** | where does the result go, who learns about it, can it be undone? |

Each answer becomes an `R##.n` story with its own acceptance line. `R##.n` never counts against any limit — it is the requirement the user actually made, worked out properly.

**The number of stories is an output, not a target.** A requirement that genuinely has seven dimensions gets seven stories; one that has two gets two, and padding it to look thorough is the same defect as skipping it. What is always wrong is twelve requirements producing twelve stories — that is the brief copied out rather than worked through.

### Two roads for depth

**Propose it** — when the answer is genuinely the user's to give (which of two behaviours they want, what tone the messages take, whether something is worth its cost). That is a briefing question, and one of the best a briefing can spend itself on.

**Decide it** — when the answer is craft, not preference. Error text, retry policy, empty-state copy, sensible limits, sane defaults. Decide, write it into the spec, and say so plainly in the summary. Asking the user which HTTP status to return is a wasted question; asking whether a cancelled order should refund automatically is not.

In **full** mode both roads collapse into the second — decide everything, and list what you decided in the final report. At **strict** depth, the first road narrows too: a question exists to clarify what the user asked for, never to sell them something extra.

### Keeping depth attached

The one failure mode worth guarding: depth that **floats free of the brief** — a beautiful subsystem grows while a plain requirement from line 2 quietly never gets a section. So every story carries a mark saying where it came from.

| Mark | Origin | Rule |
|---|---|---|
| `R##` | straight from the brief | untouchable |
| `R##.n` | **deepening** a brief requirement | uncapped — this is the main work of the phase |
| `G##` | decided in the briefing | the user confirmed it |
| `A##` | a **new capability** the brief never implied | must name a parent `R##` |
| `D##` | a constraint the **build** proved, added mid-flight | only from `phases/5-subagents.md`, never from an idea |

Note the line between the last two, because it is the one that gets blurred: elaborating «принимает заявки» into retry, resume and validation is `R01.n` — the same requirement, understood properly. Adding a loyalty programme is `A`. Depth is not scope creep, and treating it as if it were is how specs end up thin.

Three rules keep additions attached. They hold at **every** depth — `deep` relaxes none of them, and `strict` removes `A##` entirely:

- **Parenthood.** An `A##` story names the `R##` it serves. A free-floating invention gets cut — not because inventions are bad, but because one with no parent is a different project.
- **Proportion.** `A` stories may not outnumber `R` + `G` combined. `R##.n` never counts toward this — deepening what was ordered is unlimited by construction.
- **Precedence.** Recorded here, enforced in Phase 4: tickets closing `R` come before tickets closing only `A`. If time or patience runs out, what goes unfinished is your addition, never the user's request.

Every `A##` that survives into the build is listed in the final report under «что я добавил сверх заказанного», so the user learns about it from the report rather than from the code.

## Boundaries — decided here, not by whichever ticket reaches them first

Phase 5 runs several subagents in fresh contexts, each seeing one ticket and `interfaces.md`. What makes them build one project instead of several incompatible halves is that the **boundaries between modules were already decided** — the units, what each one owns, and the signatures they expose to each other.

Leave that undecided and it still gets decided: by ticket 01, which has seen an eighth of the задача, in whatever shape made ticket 01 easy. Everything after it either obeys that shape or quietly builds a second version of it. Reinvention is the most expensive defect a parallel crew produces, and this is where it is actually prevented — `interfaces.md` only records the decision, it cannot make it.

So this phase names, for every unit the build will have:

- **What it owns** — the data, the rule, the surface. One unit, one reason to change.
- **What it exposes** — the public signatures other units call. Names and shapes, not implementations.
- **What it hides** — the part nobody else may reach into. If nothing is hidden, it is not a module, it is a folder.

Then the **test seams**, which are a subset of the above and not a separate exercise: behaviour is checked through those same public boundaries. Prefer seams that already exist in the repo. **The fewer the better — the ideal is one.** A seam is a promise to keep something stable, and every extra one is another thing that cannot move.

Three rules keep this from becoming architecture for its own sake:

- **Boundaries follow the depth pass, not the requirement list.** One requirement can live inside one module; three requirements that all read the same data belong behind one boundary, not three.
- **A boundary that no ticket crosses is not a boundary.** If the whole thing is built by one subagent, it needs no public signature — say so and move on. At tier T0 this section is two lines.
- **Deep modules over many shallow ones.** A narrow interface hiding real work beats a wide one hiding none. Every signature written here is something eight contexts have to agree about, and the cheapest agreement is the one there is least of.

In **manual** this is part of what the spec gate covers, and it is the part worth actually discussing — it is the only decision in the spec that is expensive to change later.

Phase 4 seeds `interfaces.md` from this section before the first ticket flies. Write it so that is a copy, not a re-derivation.

## The template

```markdown
# Спецификация: <название>

## Задача

Проблема пользователя своими словами — от лица того, кто ей страдает,
не от лица кода.

## Решение

Что появится у пользователя, когда всё будет готово. Тоже без техники.

## Пользовательские истории

| # | Метка | История | Приёмка |
|---|-------|---------|---------|
| 1 | R01 | Как клиент, я оставляю заявку боту, чтобы не звонить | бот принял и подтвердил |
| 2 | R01.1 | …и вижу понятную ошибку, если связь отвалилась | текст ошибки, не молчание |
| 3 | A01 → R01 | …и получаю номер заявки, чтобы на него ссылаться | номер в подтверждении |

Каждая история — «Как <кто>, я <что>, чтобы <зачем>» плюс то,
по чему видно, что она работает.

## Решения по реализации

Стек, модули и их границы, схема данных, контракты API, внешние сервисы.
Каждое решение — с одной строкой «почему так».
Без путей к файлам и без кода: они устареют раньше спецификации.

Исключение: если структура (схема, тип, конечный автомат) выражается
точнее кодом, чем прозой — вставь только её, без обвязки.

## Границы и швы

Единицы, из которых состоит проект. По одной строке на каждую:
что владеет, что выставляет наружу, что прячет.

| Модуль | Владеет | Выставляет | Прячет |
|---|---|---|---|
| `intake` | заявки клиентов | `createRequest({phone, address, problem}) -> {id, createdAt}` | нормализацию телефона, генерацию номера |

Швы для тестов — подмножество этих же границ, названное явно:
поведение проверяется через них, Phase 5 тестирует только здесь.
Предпочитай существующие швы новым. Чем меньше швов, тем лучше; идеал — один.

Это единственный раздел спецификации, который Phase 4 копирует в `interfaces.md`
дословно. Пиши его так, чтобы копировать было нечего додумывать.

## Вне рамок

Что осознанно НЕ строим. Каждая строка ссылается на требование манифеста,
которое она откладывает, и говорит почему.

| Требование | Почему не сейчас |
|---|---|
| R06i — админка для заявок | заявки видны в таблице; отдельный экран — следующий заход |

## Открытые места

Каждый `placeholder` из манифеста: что стоит заглушкой, где именно в коде,
и что от пользователя нужно, чтобы её закрыть.

## Покрытие манифеста

| Требование | Раздел спецификации |
|---|---|
| R01 | Истории 1–3, Решения §2 |
| R02 | Истории 4–5, Решения §4 |

Строк ровно столько, сколько живых требований в манифесте. Ни одной пропущенной.
```

## The vocabulary rule

If `CONTEXT.md` or `docs/adr/` exist, the spec speaks the project's language — the terms already defined there, not synonyms. A concept you need that the glossary lacks is a signal: either you are inventing language the project does not use, or there is a real gap worth noting. If a decision here contradicts a recorded one, say so out loud in the spec rather than overriding it silently.

## Gate G2 — before leaving this phase

This is the single most valuable check in the whole flight. Everything downstream trusts the spec; this is the last moment the spec is still cheap to compare against the words the user actually said. It has two halves, and the second is the one that works.

### 1. Your own pass — zero `open` rows

Update every manifest row: `open` → `in-spec` with its section, or → `deferred` with its Out of Scope line.

Then check: **zero `open` rows.** An `open` row means the spec does not cover something the user asked for. That is not a note for later — it is an incomplete spec. Go back and write the missing section.

### 2. The independent coverage check

The first half cannot catch its own blind spot. **You wrote the spec, so you cannot see what you did not write** — a requirement you misread as covered gets marked `in-spec` by the same reading that lost it, and every check from here to the end inherits that. The manifest makes the loss *findable*; it does not make you the one who can find it.

So spawn a subagent. It receives **exactly two files** — `<дата>-brief.md` and `spec.md` — and nothing else.

**It must not receive:** `manifest.md`, the conversation, the briefing answers, or any summary of them. The manifest is your reading of the brief; hand it over and you have asked someone to check your reading against itself.

Its brief:

> Прочитай два файла. Первый — задача, как её поставил заказчик своими словами.
> Второй — спецификация, написанная по этой задаче.
>
> Найди всё, что заказчик просил, а спецификация не покрывает. По каждому: цитата
> из брифа и одна строка, чего именно нет.
>
> Отдельно — то, что покрыто наполовину: требование названо, но описано так, что
> по нему нельзя собрать. «Складывает в таблицу» без указания, что именно
> складывается, — это половина.
>
> И отдельно — то, чего в брифе не было, а в спецификации есть.
>
> Не оценивай качество, не предлагай улучшений, не объясняй, почему чего-то могло
> не быть. Только факт расхождения. Если расхождений нет — так и скажи.

Then act on it, before leaving the phase:

| Finding | What it means |
|---|---|
| missing | the spec is incomplete — **write the section**, then update the row |
| half-covered | the executor will guess — write what was missing |
| in the spec, not in the brief | an `A##` with no parent, or a `D##` written too early. Attach it or cut it |
| «расхождений нет» | pass |

Record the result in `state.js` under `coverage` — the count of findings and what was done with each — so the Phase 8 report can say whether this gate ever caught anything. A gate whose findings are never visible is a gate nobody will keep running.

**A finding here is the gate working, not a failure of the spec phase.** It costs a paragraph now. The same finding at G4 costs the build.

## Showing it

**full, semi and interview** — two lines in the chat: what will be built, and what deliberately will not. Then move on.

In **interview** that is easy to get wrong, because the user has just spent twenty answers on this and it feels like they are owed the document. They are not — they chose the mode that buys questions, not gates, and stopping here to wait for approval is the pause the mode was picked to avoid. Two lines, plus one saying where it is: «Спецификация — `.autopilot/<slug>/spec.md`, если захочешь посмотреть. Начинаю.» Then start.

**manual** — the spec is a gate. Show it in full, stop, wait for an explicit «ок». Rewrite on every objection and ask again. Silence is not agreement, and neither is work already started.
