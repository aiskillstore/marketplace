# Phase 2 — Briefing

The phase the user is actually needed for — the only one in `semi` and `interview`, the first of three in `manual`. Its job is not to collect wishes: it is to **close what cannot be built as written**, and, where the mode or the depth asks for it, to find out what the brief got wrong while changing it is still free.

The manifest already exists. Every question here exists to move a row in it.

Two dials meet in this phase and they do different jobs. **Depth decides how much gets opened up; the mode decides who closes it.** A fork found at `deep` is the same fork in every mode — in `full` you settle it yourself and label the decision, in `interview` you put it to the user. Confusing the two is how `full deep` turns into a contradiction.

## The adversarial pass

**Runs when:** the mode is `interview` or `manual`, at any depth · **or** the depth is `deep`, in any mode. Otherwise skip this section entirely and go straight to the interview.

Everything else in this phase asks *what the brief left undefined*. This asks something different and harder: **where the idea itself comes apart.** A brief can be complete, unambiguous and internally consistent, and still describe a thing that will not work — and nothing downstream of here will ever notice, because every check after this one measures the build against what was asked for.

Run it against `brief.md` and `manifest.md`, before you ask anything. Seven questions, and the answers are yours to find, not the user's to supply:

| | The question you put to the задача, not to the user |
|---|---|
| **1. Провал** | Проект сдан, работает, и им никто не пользуется. Что произошло? |
| **2. Столкновение** | Какие два требования не могут быть верны одновременно? Не внутри одного — между разными строками манифеста |
| **3. Непроверенное** | Что пользователь считает решённым, а оно не решено? «Люди этим будут пользоваться», «данные откуда-то возьмутся», «у меня есть аудитория» |
| **4. Цена** | Какое требование съест половину сборки ради малой доли ценности — и знает ли он об этом? |
| **5. Условие** | Чего в брифе нет, но без чего результат бессмысленен? Не подразумеваемое требование (это `R##i`), а условие успеха: кто это наполнит, кто будет обслуживать, откуда первые данные |
| **6. Вторая неделя** | Что случится, когда это перестанет быть новым: рост, дубликаты, модерация, поддержка, чужие руки |
| **7. Второй актор** | Кто ещё будет этим пользоваться, кроме описанного? Про него в брифе обычно нет ни строчки |

Five to seven findings is the normal yield. Fewer than three on a real project means the pass was run for form's sake.

### What a finding may become — and what it may never become

Route each one, and route it by **mode**, not by how alarming it looks:

| Kind of finding | full | semi | interview / manual |
|---|---|---|---|
| only the user can settle it | `ASSUMPTION` in the manifest, in the report | asked **only if** the two branches give a visibly different product | **asked** |
| craft — you can settle it | decided, into the spec | decided, into the spec | decided, into the spec |
| it is a whole capability | `A##` under its parent, or Out of Scope | same | same, or offered as a question |
| it is outside the задача | one line in Out of Scope | same | same |

**The pass has no power to remove anything.** It produces questions, `A##` stories, Out of Scope lines and `ASSUMPTION` rows — never a `dropped` row, never a quietly narrowed requirement. A requirement the pass thinks is a bad idea is still the user's requirement: the most it earns is one question naming the cost.

And it is **a grilling of the задача, not of the person.** «Заявки будут приходить — а кто их читает в субботу?» is the pass working. «Ты уверен, что это вообще кому-то нужно?» is not a finding, it is an opinion, and it buys nothing that can be built.

## The rules of the interview

**One question at a time.** Wait for the answer before asking the next. A wall of questions is bewildering and gets answered badly, which is worse than not asking.

**Every question names its requirement.** Internally, each question is «this asks about R07». A question that closes no row is a question you invented for your own comfort — drop it.

**Recommend an answer with every question.** «Заявки складывать в Google-таблицу или сразу в базу? Я бы взял таблицу — тебе её видно и не нужен сервер.» The user can accept in one word. Never ask an open question where a recommended default would do.

**Look facts up, ask only decisions.** Anything discoverable in the filesystem, the repo, or a tool is not a question. What stack the repo already uses is a fact. What payment provider the user has an account with is a decision.

**Blocking unknowns go first.** Payment, hosting, which accounts already exist, where data lives, who the user is authenticated as — these decide the shape of everything. In the first three questions, never at the finish line. A payment question asked at the end costs half the project.

**Decisions, never secrets.** *Which* provider, *whether* an account exists — yes. The key, the token, the password, the connection string — never. If the user volunteers one anyway, the redaction gate in `phases/1-manifest.md` handles it.

**Never answer for the user.** No silent assumptions, no invented content. Forced past an unknown → mark the row `placeholder` and move on. In **full** mode decisions do get made for the user — labelled, never silent. See below.

**Ask what the brief actually leaves open — however many that is, including none.**

The count is an outcome of the brief, not a number you were handed. The mode moves the *line* — which forks reach the user — and the brief decides how many things fall on each side of it. A two-line brief about a marketplace can leave eight real forks; a careful brief for a landing page, with the copy already written and the stack named, can leave zero even in `interview`. Both are correct interviews. What is never correct is producing a question because a mode implied there should be more: a manufactured question is answered badly, teaches the user that the interview is a formality, and spends the attention you will need for the one question that matters.

In priority order:

- **Every blocking unknown is asked, always.** Payment, hosting, accounts, where the data lives, an existing system to fit into. No count and no mode makes one of these skippable — an unasked blocking question costs the project far more than an extra question ever costs the user.
- **A fork only the user can settle is asked.** How many of them, and that is the whole difference between the modes:

  | | Which forks reach the user |
  |---|---|
  | **semi** | the ones where the two branches lead to a visibly different product. The rest you settle and record |
  | **interview** · **manual** | **all of them**, plus everything the adversarial pass opened. A fork whose branches look alike from here may not look alike from where the user sits, and in these modes that judgement is theirs |

  This is not «more patience» — it is a different line in the same place. In `semi` you decide a borderline fork and note it; in `interview` you ask it.
- **Everything else you decide yourself** and record it. Error wording, retry policy, sane defaults, naming, layout — that is craft, and Phase 3 is where it belongs. This line does **not** move with the mode: `interview` buys the user every decision that is genuinely theirs, not the right to be asked which HTTP status to return.

  «Everything else» is narrower than it sounds, and getting the line wrong in this direction is the expensive mistake. A decision belongs back in the interview, not in your hands, if it **costs the user money or ties them to a vendor**, if it **changes what they see or what they can do**, if **undoing it later means rebuilding rather than editing**, or if it **encodes a rule about their business** — prices, deadlines, who may do what, what happens to someone's data. None of those are craft, however obvious the answer looks from here. When you cannot tell which side a decision falls on, that uncertainty *is* the signal: ask.
- **Nothing left open? Say so and go.** «Вопросов нет — в задаче всё однозначно, пишу спецификацию.» Mark the `briefing` stage `skipped` in `state.js` with the note «вопросов не потребовалось», so the user sees a decision rather than a step that quietly did not happen.

In **semi**, most briefs land somewhere between two and eight questions. That is an observation about briefs, not a target for you — **and there is no ceiling any more than there is a floor.** A three-line brief for a marketplace, a project that has to fit into someone's existing system, a business with rules you cannot guess: fifteen questions there is not an interrogation, it is the cheapest part of the whole build. Ask them, and say once why there are so many — «задача большая и многое не определено, вопросов будет больше обычного». What makes a long interview bad is padding, never length.

In **interview** and **manual** the range is simply higher, for the same reason: the user asked for the задача to be taken apart, so the forks that `semi` would have settled quietly all reach them. Ten to twenty-five on a real project is ordinary. Say once at the start what they are in for — «разбираю задачу подробно, вопросов будет много; каждый закрывает что-то, что иначе я решу за тебя» — and then just work. **Do not apologise for the count as you go**: a mode the user chose does not need excusing, and «извини, ещё один вопрос» every third turn teaches them that they picked wrong.

## What to ask about

In priority order. Ask only what is actually unresolved for *this* brief; skip anything the brief already settled.

1. **Blocking externals** — payment, hosting, domain, third-party accounts, existing data to import.
2. **What the adversarial pass found**, where it ran. These come second and never last, because they are the only questions in the list capable of changing what gets built rather than how. Each is asked the same way as any other — one at a time, with a recommended answer, naming its cost: «Заявки будут приходить круглосуточно, а мастер один. Ставим очередь и обещаем ответ в рабочие часы, или принимаем только с 9 до 18? Я бы взял первое — клиент не упирается в закрытую дверь.»
3. **Implicit requirements** (`R##i` rows) — the things the brief assumed. «Заявки будут падать в таблицу — тебе нужен ещё экран, чтобы их смотреть, или таблицы хватит?» These are the rows most likely to sink the project silently.
4. **Depth the user alone can settle.** The brief describes the happy path; the interesting decisions live under it. Some of those are craft and you decide them yourself in Phase 3 — error wording, retry policy, defaults. Others are genuinely the user's preference, and those are among the best questions you can spend a slot on: «Клиент отменил заявку через час — деньги возвращаем сами или мастер решает?» A question like this buys a whole branch of the spec that would otherwise be guessed.

   At **strict** these narrow to clarifying what the user already said — never to offering them something extra.
5. **Untestable requirements** — «красиво», «удобно», «быстро». Turn one into something checkable, or accept it as a matter of taste and record that. Do not spend three questions here.

   The cheapest way to turn one into something checkable is to ask what it should be **like**: «Есть сайты, на которые это должно быть похоже? Скинь два-три». An answer here is worth more than three rounds of guessing what «современно» meant — see *Эталон* below.
6. **Contradictions inside the brief** — quote both halves and ask which wins.
7. **Scope edges** — what is explicitly *not* needed. Answers here become `dropped` rows and save whole tickets.

## Эталон — what the result should be like

The manifest records *what* to build. Nothing yet records **what it should be like**, and for anything with a surface — a page, an app, a piece of copy — that gap is where «сделал по требованиям, а выглядит не так» comes from. The brief almost never says it, and the user almost always has it in their head.

So: **whatever the user hands you that a finished result could be measured against goes into `.autopilot/<slug>/reference.md`.** Reference sites, a competitor, screenshots, a text whose tone they like, a number they want beaten, «как в приложении банка». One line each, verbatim after redaction, with where it came from.

```markdown
# Эталон

На что это должно быть похоже. Собрано со слов пользователя — не выдумано.

## Внешний вид
- linear.app — «вот такая чистота, ничего лишнего» (ответ на вопрос 3)
- скриншот в брифе — раскладка карточек

## Как должно ощущаться
- «заявка отправляется в два клика, без регистрации»

## Тексты
- пример письма, который прислал пользователь — короткий, на «ты»

## Чего быть не должно
- «не хочу как на госуслугах»
```

Three rules, and they are what keep this from becoming a second spec:

- **Only what the user gave.** A comparable you chose yourself is your taste with a citation, and it will later be used to judge the build as though the user had asked for it. If they named nothing, the file has the sections that do have content and no others — an empty `reference.md` is a truthful one.
- **A comparable is not a requirement.** It never becomes an `R##`, never gets a status, never gates anything. «Похоже на linear.app» is a direction; «должна быть тёмная тема» is a requirement, and if the user said that, it belongs in the manifest.
- **Ask for it once, cheaply, and only where it can matter.** One question in the interview, folded into an existing one where possible. A backend integration with no surface does not need this question, and asking it there is exactly the manufactured question this phase warns against.

In **full** mode there is no interview, so `reference.md` gets only what the brief itself carries — and that is correct. Do not self-brief a reference: an invented comparable is an invented fact about the user's taste, and the rule against those does not have an exception here.

**One case makes this a required question in every mode, including full:** the run has `polish` on. Доводка is a comparison, a comparison needs a comparable, and a user who explicitly asked for it has already agreed to the one question that makes it possible. If they have nothing to name, record that — the loop will decline to run, per `phases/polish.md`, and that is a better outcome than a critic inventing the standard.

## Recording answers

After each answer, update the manifest row immediately — not at the end of the interview.

- Answer resolves a requirement → note the decision in Основание.
- Answer **cancels** a requirement → `dropped`, with the user's own words quoted. This is the only path to `dropped`, and it is why the answers are recorded verbatim (after redaction).
- Answer raises something new → **a new row**, `G##`, quoting the user's phrasing. This is the only phase where the manifest grows on the user's words. Afterwards it grows for exactly one reason — a `D##` row for something the build proved, per `phases/5-subagents.md` — and never for an idea of yours.
- Answer is «не знаю» → `placeholder`, and the build gets a stub with a visible label.

## Full mode — the self-briefing

**No interview happens.** The `briefing` stage in `state.js` is marked `skipped` with the note «полный автомат — самобрифинг», not left `pending`: the user has to see that the step was a decision, not a stall.

Run the same checklist against yourself and write the answers into the manifest, each labelled by kind. At **`full deep`** the adversarial pass runs too, and every finding it produces that only the user could have settled becomes an `ASSUMPTION` — that is what «полный автомат» means here, not that the question was never worth asking. Each of them is a line in the Phase 8 report, and on a `deep` run that section is the longest one in it.

The line between the two kinds is the whole discipline of this mode:

**Decisions are yours to make.** Stack, structure, provider, data model, layout. Pick the option that runs on the user's own machine **without a third-party account and without money**, and record it as `ASSUMPTION — принято за пользователя: …` in the manifest's Основание column. Every one of these is a required line in the Phase 8 report — the user never asked for them and has the right to see all of them in one place.

**Facts about the user are not yours to invent.** Their prices, texts, addresses, business rules, accounts, brand colours. These become `placeholder` in the manifest, visibly labelled filler in the code (`[ЦЕНА — впиши]`, not `4990 ₽`), and a line in the final report. A plausible invented price is worse than an obvious blank: the blank gets fixed, the price gets shipped.

**A paid or account-bound service becomes an adapter, not a guess.** One interface, a local stub behind it, the real credential an empty variable name in `.env.example`. The user swaps the stub for the real thing when they have the account — the build does not wait for it and does not pretend to have it.

## Interview and manual

Identical here — the two modes part company only at the spec and the plan, two phases later. Same rules as `semi`, no cap, and the wider line on which forks reach the user. Keep going while genuine forks remain, then say so plainly: «Вопросов больше нет, пишу спецификацию».

The thing to guard against in these two is not length, it is **drift into process**. «Какой стек берём?», «нарезать на таски помельче?», «показать спецификацию?» are not interview questions — they are the questions Autopilot exists to answer itself, and asking them is how a mode the user chose for its thoroughness turns into the meeting they were avoiding. Every question still names its manifest row.

## Closing

Before leaving this phase, check **gate G1**: every manifest row has a status; nothing is `open` without a recorded reason. Then announce the transition in one line — «Понял. Пишу спецификацию» — and go to Phase 3.

Do not summarise the interview back to the user. The manifest holds it, and the spec is about to say it better.
