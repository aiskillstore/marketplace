---
name: model-per-chat
description: >-
  Load when someone runs many Claude Code / Claude desktop chats, agents, subagents or scheduled tasks and wants to decide which model each one should use (Fable, Opus, Sonnet, Haiku, or no model at all) to save plan limits or money without adding mistakes. Use it when a new model comes out ("Fable 5.2 just came out, who gets it?"), when limits run out too fast, or for "which model for each chat", "assign models to my agents", "save tokens across sessions", "qué modelo le pongo a cada chat", "a quién le pongo Fable", "Opus o Sonnet", "ahorrar límites", "se me acaba el plan", "que suba el esfuerzo solo", "Opus también es caro", "lo mejor pagando poco". It sets a cheap base (mid model, low effort) with a written rule to climb to the top model only for the hard or irreversible step and come back down. It reads the live plan meters and each session's current model, checks today's prices and plan rules on the official pages, scores every chat 1-10 by what a mistake there costs, maps the score and the run frequency to a model, flags plan traps (models billed outside the limits, launch windows that end, extra usage switched off), and only downgrades a chat after a check on its real recent work. Not for choosing a model inside API code (use claude-api) and not for one single task.
license: MIT
---

# Model per chat

A fleet of chats all on the same top model burns the plan on the cheap work: a watcher that runs every 20 minutes to say "nothing new" costs the same per turn as the supervisor that approves client work. Moving everything to a cheap model fails the other way: the chats where a mistake costs money or a client start making them.

One rule: **pay for intelligence where a mistake is expensive, and pay for volume nowhere.**

## 1. Read the facts live, never from memory

Models, prices and plan rules change every few weeks. Before recommending anything, collect and write down with the time:

- **Plan and meters now:** plan name, % used of each limit window and when it resets, per-model meters, and whether extra usage / usage credits are on and with what monthly cap. (Claude desktop: the usage card or the session-usage tool. Claude Code: `/status`.)
- **Each chat's current model and effort.** Read it from the session metadata, not from what you assume. Someone may have already switched one.
- **Today's model facts from the official pages** (the vendor's model announcement, pricing page, and the help-center article on how each model counts against the plan): which models the plan includes, which are billed outside the limits, any launch window and its exact end time with time zone, and the official advice on which model fits which work. Third-party posts are leads, not sources. If the official page doesn't state a fact, write "not stated" instead of filling the gap from a blog.

## 2. Inventory every chat and job

One row each, including scheduled tasks and the sessions they spawn:

| Chat / job | What it does | Runs how often | Touches what (money, clients, live system, public post, only files) | Who checks its output after |
|---|---|---|---|---|

Scheduled jobs that fire many times a day are usually the biggest hidden cost even when each run is tiny.

## 3. Score importance 1-10 by the cost of a mistake

Add up:

| Factor | Points |
|---|---|
| A mistake costs money or a client directly (ads spend, payments, messages to customers, live sales bot) | 0-4 |
| It acts on something live or hard to undo (publishes, sends, pauses, deploys) | 0-2 |
| The work needs judgment or taste, not just steps (supervising, design, debugging, writing to people) | 0-2 |
| Other chats depend on its decisions (it gives orders or approves) | 0-2 |
| Someone strong reviews every output before it matters | −1 |

Frequency does not raise importance. It decides how much a wrong pick costs.

## 4. Map score and frequency to a model

| Score | Default |
|---|---|
| 9-10 | The vendor's recommended daily driver at the top (today usually the current Opus), at low effort, with the climb rules of 4b. The newest flagship (e.g. Fable) only for the 1-2 hardest chats, and only while the plan includes it or the owner agreed to pay for it. |
| 6-8 | If the owner wants to save: mid model (Sonnet) at medium effort **plus the escalation rule of 4b** (top-model check before anything irreversible, top-model subagent for hard steps). Without the escalation rule in place, keep the daily driver. |
| 4-5 | Mid model. |
| 1-3 | Small model (Haiku), or **no model**: a plain script that wakes a chat only when there is something to do. |

Volume rules:
- Anything that runs more than ~10 times a day gets the cheapest option that passes the check in step 6, and its "nothing new" path should exit after one command.
- Effort is the second lever: lower effort on routine chats before downgrading the model; keep higher effort only where the score is 9-10.
- A chat that is mostly idle costs nothing. Don't spend the owner's attention moving it.

## 4b. Cheap by default, climb by itself only when the step needs it

Most turns in most chats are routine: reading, searching, small edits, status. Paying the top model for all of them is where the plan goes. The better default for a cost-conscious owner is **the mid model at low or medium effort for every chat that is not a supervisor, plus an escalation rule written into the chat's own instructions**, so it climbs for the hard step and comes back down.

What climbs on its own already: on current models, adaptive thinking decides per turn how much to think, so a routine turn is cheap and a hard turn thinks more even at the same effort setting. What does not happen by itself: a session does not change its own model or effort setting. So the climb is done by delegation, which the chat can do without anyone touching settings:

| Step in front of the chat | What it does |
|---|---|
| Routine: read, search, list, summarize, rename, small edit with a test | Stays on its base (mid model, low/medium). Bulk reading of long logs, transcripts or folders goes to a **small-model subagent** that returns only the lines that matter. |
| Hard: the plan for a change across many files, a bug that survived 2 tries, a design or copy that will go to a paying client, a decision another chat will act on | Hands **that one step** to a **top-model subagent** at high effort (in Claude Code: the Agent tool with `model: "opus"` and `effort: "high"`, or a subagent file with `model: opus`). The brief carries only what that step needs, so the strong model reads little. Then back to base. |
| Irreversible: send to a customer, pause/spend on ads, deploy a live app, publish, delete | Before doing it, a **top-model check** of the exact action (what, where, the do-not-touch list) at medium/high effort. Cheap, because it is short. The chat acts only if the check passes. |
| Second failure on the same thing | Stop retrying on the base model. Escalate as "hard". Two cheap failed tries plus one strong try costs less than five cheap ones. |
| The owner or a reviewer sends work back | The redo goes to the top model, and the chat notes why so the next similar piece starts there. |

Rules for the climb:
- Climb for the step, not for the chat. After the strong step, the chat goes back to its base.
- Say it in the report in a few words ("plan checked with the strong model") so the owner sees where money went.
- If the owner types the one-turn keyword their tool offers for deeper thinking (in Claude Code: `ultrathink`), respect it for that turn only.
- Supervisors and approvers keep the top model as base, but at **low effort** by default, with bulk reading delegated to the small model. Adaptive thinking still goes deep on the turns that need it.
- Write the escalation rule into each chat's instructions (its project instructions file or its standing order), not only in this skill, so it works when the skill is not loaded.

Paste-ready rule for a chat's instructions:

> Base: mid model, low/medium effort. Bulk reading goes to a small-model subagent. Before anything irreversible (customer message, ad spend, deploy, publish, delete), get a top-model check of the exact action. A plan across many files, a bug after 2 failed tries, or work for a paying client goes to a top-model subagent at high effort for that step only, then back to base. Say in the report when you climbed and why.

## 5. Check the plan traps before switching anyone

- **Model billed outside the limits.** Some plans include a flagship only during a launch window or up to a share of the weekly limit, then bill it to usage credits. Write the exact end moment in the owner's time zone and set a reminder a day before to move those chats back. If usage credits are off, that model stops working for that chat at the end of the window, which can strand a supervisor mid-task.
- **Separate meters.** A per-model meter (e.g. "Fable 1%") filling up does not stop the others, but the shared weekly meter does. Check which one is close to full.
- **Scheduled tasks may have no model setting of their own.** They often start on the app's default model. Say so instead of claiming they were switched; the fix is a cheaper default model (in Claude Code the `model` and `effortLevel` keys of the user settings set the default for new sessions; whether scheduled runs honor them must be checked by reading the model of the next run), or making the task a script that starts a chat only when needed.
- **A cheap default changes every new session.** If the default model goes down, the chats that must stay strong need their model set on purpose, and the change needs the owner's ok because it is a settings change.
- **Cascade cost.** A supervisor on a cheap model that approves bad work makes every chat under it redo pieces. Redo turns cost more than the savings.

## 6. Downgrade only after a real check

For each chat you plan to move down:
1. Take 2-3 of its real recent tasks (from its transcript).
2. Run them, or watch its next 2 real runs, on the cheaper model.
3. Compare with what the current model did, on that chat's own bar: same facts, nothing broken, nothing the reviewer would send back.
4. Worse on any → keep the stronger model and write why. Same → switch.
5. Rollback rule written in the table: "if the reviewer sends back 2 pieces from this chat in a week, move it back up."

## 7. Apply and report

- Switching another session's model changes the owner's setup and spending: show the table and get one ok for the batch, then switch, then read each session's model back to confirm it changed.
- Report one table:

| Chat | Score | Now | Recommended | Why (one line) | Check done | Rollback rule |
|---|---|---|---|---|---|---|

Then three lines: what is switched and confirmed, what is not switchable (and the workaround), and the dates to remember (window end, limit reset).

## Words

- "Saves X" only with a number you measured (meter before and after a day) or "estimated" plus how.
- Never "the new model is better for everything". The vendor's own advice is usually "flagship for the hardest work, daily driver for the rest"; quote it.

## Limits

- It does not measure exact per-turn cost on subscription plans; vendors don't publish multipliers. It ranks by relative cost and by measured meter movement.
- Scores are judgment. The owner knows which client matters most; their word overrides the table.
