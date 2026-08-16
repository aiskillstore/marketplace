# Phase 1 — Manifest

The brief is the only thing in this whole process the user actually authored. Everything downstream is your paraphrase of it. This phase turns it into an artifact that survives every later rewrite, so that nothing can quietly stop existing.

Runs **before** the briefing questions. The questions are themselves a re-encoding of the brief — the anchor has to be dropped first.

## 1. Redaction gate — runs before anything is written

Every piece of user text — the brief, every answer, every pasted fragment — passes this gate on its way to a file, a prompt, or the dashboard. Nothing bypasses it.

Scan for:

| Kind | Shape |
|---|---|
| Stripe / OpenAI-style | `sk-…`, `sk_live_…`, `sk_test_…`, `rk_live_…`, `pk_live_…` |
| GitHub | `ghp_…`, `gho_…`, `ghs_…`, `github_pat_…` |
| AWS | `AKIA…`, `ASIA…` |
| Google | `AIza…`, `ya29.…` |
| Slack | `xoxb-…`, `xoxp-…`, `xoxa-…` |
| Telegram bot | 8–10 digits, colon, 35 chars of `[A-Za-z0-9_-]` |
| JWT | `eyJ…` followed by a dot and more base64 |
| Connection string | `<scheme>://<user>:<something>@<host>` |
| Private key | `-----BEGIN … PRIVATE KEY-----` |
| Generic | ≥32 chars of hex or base64 sitting next to `key`, `token`, `secret`, `password`, `ключ`, `токен`, `пароль`, `доступ` |

On a hit:

1. Replace the value with `[REDACTED:<VAR_NAME>]`, inventing the conventional variable name for that provider (`STRIPE_SECRET_KEY`, `TELEGRAM_BOT_TOKEN`, `DATABASE_URL`). The name is what the build needs; the value never was.
2. Add the name to `.env.example` with an empty value.
3. Tell the user immediately, in one line, in plain language: «Ты прислал ключ Stripe — я его не сохранил. Впиши его сам в `.env`, а этот лучше отзови и выпусти новый: он уже побывал в переписке.»
4. Carry on. A redacted secret does not block the flight.

**Never echo the value back**, not even to confirm what you found. Naming the provider is enough.

Before the first commit, run this gate over everything under `.autopilot/`. A secret that got in through some path nobody predicted still must not reach git history.

## 2. Write the brief file

The redacted brief, **word for word**, into `.autopilot/<slug>/<YYYY-MM-DD>-brief.md` — today's date, then `-brief.md`: `2026-08-07-brief.md`. The date is part of the name because a slug directory outlives one sitting; a month later «доделай ещё вот это» arrives, and the files have to say which brief came when. Record the chosen name in `state.js` as `briefFile`, so nothing downstream has to guess it.

```markdown
# Изначальная задача

> Записано <дата>. Этот файл не редактируется — он эталон, с которым
> сверяется готовый результат.

<весь текст пользователя, дословно, после редактирования секретов>
```

Rules that make this file worth having:

- **No paraphrase, no cleanup, no reordering.** Bad grammar, contradictions, half-sentences and duplicated thoughts all stay. A tidied brief is already a spec, and a spec is the thing you cannot check against.
- **Everything counts as brief** — the idea, the asides, the constraints, the "и ещё хорошо бы", the stack preference, the deadline mentioned in passing.
- **Never edited again.** Later thoughts from the same sitting are appended under `## Дополнения`, dated, never merged into the original text. A brief dictated on a **later day** is a new file with that day's date — appending it to an older one erases the fact that the project was asked for twice.

## 3. Atomise into requirements

Split the brief into the smallest units that can independently be true or false about the finished product. Write `.autopilot/<slug>/manifest.md`.

Every requirement is a row, and every row carries the **exact words it came from**. The quote is the point — a paraphrased requirement drifts exactly like a paraphrased brief.

```markdown
# Манифест требований

Источник: `<дата>-brief.md`. Строку из этого списка может снять **только пользователь**.

| ID | Из брифа (дословно) | Статус | Основание | Где |
|----|---------------------|--------|-----------|-----|
| R01 | «принимает заявки на ремонт техники» | in-ticket | — | spec §2 → T02 |
| R02 | «складывает их в Google-таблицу» | in-ticket | — | spec §4 → T05 |
| R03 | «чтобы клиент видел статус» | in-spec | — | spec §6 |
| R04 | «и дублировать на SMS» | dropped | пользователь: «SMS не надо, только телега» | — |
| R05 | «фирменные цвета студии» | placeholder | цвета не переданы | отчёт |
| R06i | *(подразумевается)* кто-то должен читать заявки | deferred | Out of Scope §9: админки в брифе не было | отчёт |
```

### Statuses

| Status | Meaning | Who may set it |
|---|---|---|
| `open` | not yet resolved anywhere | initial state |
| `in-spec` | landed in the spec, section noted | you |
| `in-ticket` | a ticket exists that delivers it | you |
| `done` | built and reviewed, commit noted | you |
| `placeholder` | in the build, but with a stub where a user fact belongs | you |
| `deferred` | consciously postponed, listed in the spec's Out of Scope with a reason | you |
| `dropped` | **cancelled by the user** | **the user, never you** |

Three rules bind these, and they are the reason this file exists:

- **`dropped` requires a quote.** The Основание column holds the user's own words cancelling it. No quote, no drop. You may *propose* dropping something — that is a briefing question, not a status change.
- **`deferred` is not `dropped`.** Postponing is yours to decide; cancelling is not. Every `deferred` row appears in the final report under «что не вошло», so the user learns about it while the project is still fresh.
- **Silence never cancels anything.** A requirement the user stopped mentioning is still live. Forgetting and deciding must not look alike.

### Implicit requirements

Mark with a trailing `i` (`R06i`) anything the brief clearly *implies* but never says — «принимает заявки» implies somewhere to read them; «интернет-магазин» implies a way to pay.

These are the most dangerous items in the whole flight: too obvious to state, too big to skip. Route them to the briefing as questions rather than inventing or ignoring them. In **full** mode they become explicit `ASSUMPTION` decisions and appear in the report.

### Discovered constraints

Mark with `D` (`D01`, `D02`) anything the **build** proved that the plan did not know — a data model that does not hold, an assumed interface that cannot exist, two requirements that collide in practice. Its Основание is the finding itself, and it names the requirement it serves.

A `D##` row is the only thing allowed to enter the manifest after the briefing, and only from `phases/5-subagents.md`. It is not a requirement the user made and it never replaces one: a requirement the code proves impossible is a question for the user, not a `D##` that quietly retires it. An idea you had while building is not a discovery either — that is an `A##`, and it lives in the spec under the usual parent-and-proportion rules.

### How fine to cut

One requirement = one thing that can be independently true or false.

- «телеграм-бот, который принимает заявки и складывает их в таблицу» → **two** requirements. One can work while the other doesn't.
- «красивый современный дизайн» → **one**, and it is inherently untestable — mark it and let the briefing turn it into something checkable, or let it stay a stated matter of taste.
- A 2000-word brief usually yields 25–50 rows. Under 10 from a long brief means you summarised instead of atomising — redo it.

## 4. Report the manifest in one line

«Разобрал задачу на 23 требования — держу их под контролем до самого конца.» No table in the chat. The file is the artifact; the chat is a mention of it.

## The gates

Recorded here because they all read this file. A failed gate is not a warning — the phase is redone.

**G1 — after the briefing.** Every requirement has a status. Anything still `open` must have a recorded reason (unreachable user, question deferred). In **full** mode nothing may be `open`: the self-briefing answers everything or marks it `placeholder`.

**G2 — after the spec.** Two halves, both mandatory, per `phases/3-spec.md`.

- *Your own pass* — zero `open`. Every live requirement is `in-spec`, `deferred`, or `dropped`, with its spec section noted. **An `open` row means the spec is incomplete** — rewrite the spec, do not proceed.
- *The independent pass* — a subagent given the brief and the spec, and **not** this file, reports what the spec fails to cover. You wrote the spec, so you cannot see what you did not write; this file makes the loss findable, not you the one who finds it.

This is the gate that would have caught every drift you have ever seen, and the second half is why.

**G3 — after the plan.** Two directions, both mandatory:

- *Forward* — every `in-spec` requirement maps to at least one ticket. A requirement with no ticket will not get built.
- *Backward* — every ticket traces to at least one requirement or to a spec decision that traces to one. **A ticket tracing to nothing is work nobody ordered** — cut it or attach it to the requirement it actually serves.

**G4 — at the final phase.** Blind acceptance, per `phases/8-final.md`. Every disagreement between the manifest and the blind verdict goes in the report.

## Keeping it current

The manifest is updated at exactly five moments, never continuously:

| When | What changes |
|---|---|
| after each briefing answer | `open` → `dropped` / clarified / confirmed |
| after the spec is written | `open` → `in-spec` / `deferred`, section noted |
| after tickets are cut | `in-spec` → `in-ticket`, ticket number noted |
| after each ticket lands | `in-ticket` → `done` / `placeholder`, commit noted |
| when the build contradicts the plan | a new `D##` row, and the affected rows re-pointed at the amended spec section |

Each update is an edit of the affected rows, never a rewrite of the table. The table is short-lived context and long-lived truth; treat it as data, not prose.
