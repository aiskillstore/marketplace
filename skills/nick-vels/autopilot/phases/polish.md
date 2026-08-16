# Доводка — the polish loop

**Read only when the `polish` parameter is on.** It is off by default, and on a run without it this file does not exist.

Not a phase in sequence. It runs **inside Phase 8, between the blind acceptance and the final report**, and it is the only part of Autopilot that repeats itself deliberately.

Everything up to here measures the build against what was *asked for*. This measures it against what it should *be like* — and those are different questions with different answers. A landing page can satisfy every requirement in the manifest and still look like a form with a background colour.

## The one thing that makes this work

**A comparison needs something to compare against.** Give a critic a product and no reference and it will invent one, then drive the build toward a standard nobody chose — expensively, and for as many rounds as you let it. That is the failure this whole file is arranged around, and it is the same one the manifest axis of `phases/6-review.md` exists to prevent: a reviewer judges what it was handed, and what it was not handed it makes up.

So the loop has a precondition, and it is hard:

> **No `reference.md` with at least one comparable, no loop.** Say so in one line and go to the report.

```
Доводка просила эталон — с чем сравнивать. В задаче его нет и добыть неоткуда,
поэтому сравнивать было бы не с чем: пропускаю, отчёт ниже.
```

`reference.md` is collected in Phase 2 (`phases/2-briefing.md`). If the parameter was switched on mid-run, after the briefing, collect it now: **one question, in every mode including full.** The user asked for доводка explicitly, so the question that makes доводка possible is not an extra question — it is the request being carried out.

### What counts as a comparable

Anything the critic can put beside the build and read a difference off. The form changes with the kind of work; the requirement that it be **external to this run** never does.

| Kind of work | The comparable | How the critic uses it |
|---|---|---|
| interface, landing, app | reference screenshots or live URLs the user named | its own screenshot of the running build, side by side |
| behaviour, flows | the scenario, in the user's words: what a person does, in order | run it as that person would, note where it stops feeling right |
| API, calculations, data | input→output pairs derived by hand or from a source | run them, compare, no tolerance for «близко» |
| copy, tone | sample text the user considers right | its own text beside it, the difference named |
| speed, weight | a number: milliseconds, kilobytes | measure |

**Your own spec is never a comparable.** Neither is «best practice», «modern design», or anything else the critic supplies from itself. Those are the failure mode wearing a plausible hat.

## One round

Four steps, and the shape of them is the same as an ordinary ticket's — because that is exactly what a finding becomes.

**1. The critic.** One subagent, fresh, per round. It receives:

- `.autopilot/<slug>/<дата>-brief.md` — the user's own words
- `.autopilot/<slug>/reference.md` — the comparables
- the repository, and how to run it
- what previous rounds already fixed — titles only, so it does not re-report them

**It must not receive** `spec.md`, `manifest.md`, the tickets, or the previous critics' full reports. Same rule as the blind checker, same reason: a critic given the plan reviews the plan.

> Приложен бриф — что заказывали, и эталон — на что это должно быть похоже.
> Запусти проект и пройди его так, как прошёл бы заказчик.
>
> Поставь результат рядом с эталоном и назови конкретные различия. Не оценку
> «хуже/лучше», а различия: что именно отличается и что нужно изменить,
> чтобы это различие исчезло.
>
> Каждая находка — одним предложением, как проверяемое условие: что должно
> стать верным. «Выглядит недостаточно дорого» — не находка. «Заголовок
> и текст набраны одним размером, в эталоне разница вдвое» — находка.
>
> Ничего не чини сам. Не предлагай новых возможностей: ты сравниваешь
> с эталоном, а не придумываешь продукт. Если различий нет — так и скажи,
> это нормальный ответ.
>
> Не больше 12 находок, отсортированы по тому, насколько заметно различие.

**2. The filter — yours, and it is the expensive step to skip.** A finding survives only if all three hold:

- it is stated as a **checkable condition**, not a preference;
- it points at a **difference from the reference** or at a requirement in the manifest — not at an idea the critic had;
- fixing it does not require a decision only the user can make. If it does, it is a line in the report, not a ticket.

Everything else is dropped, silently, and the drop is not an argument with the critic. **A round that yields nothing after the filter is a round that found nothing** — count it as such.

**3. The work.** Surviving findings become tickets and go the ordinary way: `phases/5-subagents.md` for the cut and the crew, `phases/6-review.md` for the review, one commit each, full suite after each.

**This is the rule the loop lives or dies by.** A finding fixed by your own hand, or by the critic, or by a subagent that skips review, costs the run everything the framework was built to protect: the rollback point, the independent check, the green suite between changes. Доводка is not a licence to touch the code directly — it is more tickets, held to the same standard as the first ones.

- Group them: two findings in the same file are one ticket. Findings in different zones are a wave, launched together like any other.
- A finding whose fix would touch a requirement — anything that changes *what the product does* rather than how it looks or reads — is not a доводка ticket. It is either an `A##` with a parent or a question, per the depth rules in `phases/3-spec.md`.

**4. The books.** Append a round to `state.js` → `polish` (shape below), tell the user one plain line, and go to the next round.

> Круг 2: нашлось 4 различия с эталоном, 3 поправил — типографика, отступы, состояние пустого списка.

## When it stops

Three exits. **Whichever comes first ends the loop** — this is not a list of things to satisfy.

1. **Dry.** A round yields nothing that survives the filter. One such round is enough: the previous round's fixes have already been through review, and a second empty round buys a repetition, not a check.
2. **The ceiling.** Three rounds. Announced at the start, and not raised because the last round was productive — a loop that extends itself on its own results has no ceiling at all.
3. **The user says stop.** In any form, at any point, including «хватит», «достаточно», «оставь как есть». Ends the loop immediately, mid-round if need be.

**There is no fourth exit, and in particular there is no «критик доволен».** A critic that has to declare itself satisfied will find something to be dissatisfied about, indefinitely, because that is what it was asked to do. Satisfaction is not a stop condition — absence of findings is.

## The regression rule

**A round that breaks something is rolled back whole, not repaired.**

If, after a round's tickets are in, the full suite is red, or the blind acceptance's verdict on any requirement has moved backwards — `реализовано` that is now `частично` — revert that round's commits, record it, and stop the loop. Do not spend a round fixing a round.

This is stricter than the repair path in Phase 5, on purpose. There, a red test means one ticket is unfinished. Here it means the polish itself is doing damage — and the second-most expensive thing this loop can do is degrade a build that was already accepted while everyone watches the numbers go up. (The most expensive is to do it invisibly, which is why the round goes in the report either way.)

Cheap insurance, and it costs one line: **note the commit the loop starts from**, before round 1.

## state.js

```json
"polish": {
  "reference": "reference.md",
  "startedAt": "2026-08-07T16:02:11+03:00",
  "baseCommit": "a1b2c3d",
  "rounds": [
    { "n": 1, "found": 7, "accepted": 5, "tickets": ["P1", "P2"], "finishedAt": "…" },
    { "n": 2, "found": 4, "accepted": 3, "tickets": ["P3"], "finishedAt": "…" },
    { "n": 3, "found": 2, "accepted": 0, "tickets": [], "finishedAt": "…" }
  ],
  "stoppedBy": "dry"
}
```

`stoppedBy`: `dry` · `ceiling` · `user` · `regression`. Polish tickets are ordinary rows in `tickets` with a `P`-prefixed id, so the dashboard shows them, times them and counts them like everything else — the `final` stage stays `active` for the duration, and nothing new has to be taught to the page.

`found` minus `accepted` is the filter doing its job. A run where those two numbers are always equal means the filter was not applied, and a critic was allowed to define the product.

## The report

Доводка gets its own section in the Phase 8 report, before «Что нужно от тебя»:

```markdown
## Доводка

Сравнивал с эталоном — <что именно>. Три круга, 8 различий устранено.

| Что стало лучше | Круг |
|---|---|
| Типографика: заголовки и текст теперь различаются по размеру, как в эталоне | 1 |
| Пустой список больше не пустой экран — есть подсказка, что делать | 2 |

Остались отличия, которые я не трогал:

| Отличие | Почему |
|---|---|
| Фотографии товаров | нужны твои — сейчас видимые заглушки |
```

Two rules for it. **What the loop declined to fix is listed, not omitted** — a доводка section that shows only wins is an advertisement. And **a round that was rolled back appears with its reason**, in the same plain language as everything else: «Четвёртый круг сломал оформление заказа — откатил, оставил как было».
