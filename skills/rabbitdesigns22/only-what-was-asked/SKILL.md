---
name: only-what-was-asked
description: >-
  Load before changing anything LIVE for a client or a business: pausing or turning on ads, campaigns or ad sets, changing budgets, turning off an app, bot, number or automation, cancelling a scheduled post, editing a live site, or any rule or script that can switch things off by itself. Use it for "only pause X", "just turn off Google Ads", "don't touch anything else", "solo le pausas", "solo eso", "no le apagues nada", "ni lo demás", "no toques lo demás", "sin tocar nada más", "que no apague nada". It pins the exact target (which client, which account, which channel, which object), writes the list of what must stay as it is, takes a before snapshot of both, changes only the target, then reads back the target AND the neighbours to prove nothing else moved, and checks that no automation will do more later. Not for code refactors in a repo (use a code blast-radius skill) and not for deciding whether to pause something.
license: MIT
---

# Only what was asked

The owner says "pause only Google Ads for this client" and the agent pauses Google Ads, then also the Meta ads "to be consistent", or turns off the client's app because "they haven't paid". Or a script written last week starts switching clients off after a few days. Each extra change costs the business money or a client, and the owner learns about it from the client.

One rule: **change exactly the named thing, prove the rest did not move, and make sure nothing will move it later.**

## When to use

- Any change to something live that customers or a client depend on: ads, campaigns, budgets, apps, chat bots, phone numbers, scheduled posts, websites, automations.
- The request names one thing and leaves others implied ("only", "just", "solo", "nada más").
- You are writing or changing a rule, cron job or script that can pause, turn off, delete or charge on its own.

## The method

### 1. Pin the target in one line

Write it before touching anything:

> Target: **[client] · [platform] · [account id or name] · [object: campaign / ad set / app / number] · [action: pause / resume / budget to X]**

- If the request is ambiguous on any field (two accounts, two campaigns, "his ads" could be Google or Meta), ask one short question that lists the options. Do not pick.
- Same client name in two systems is two targets. "Pause Google Ads" never includes Meta.

### 2. Write the do-not-touch list

List what sits next to the target and must stay as it is, by name:

| Keep as is | Current state |
|---|---|
| Meta ads, same client | active, 3 ad sets |
| Client's app / bot | on |
| Other Google Ads campaigns, other clients | as they are |

Include anything the owner named ("not Facebook, nothing else") and anything a reasonable person might "tidy up" while there. Unpaid bills, low results or "it would be consistent" are never reasons to touch an item on this list. Raise them as a note to the owner instead.

### 3. Snapshot before

Record the current state of the target and of every row on the do-not-touch list: status, budget, schedule, last change time. Screenshots or the platform's own list view. You will compare against this.

### 4. Do only the target

- One change, the smallest that does what was asked (pause, not delete; pause the campaign that was named, not the whole account).
- If the platform offers "apply to all" or bundles other changes, decline them.
- If the change needs money information first (spend so far, balance), read it and report it before or with the change, as asked.

### 5. Read back the target and the neighbours

After the change, open the platform's list again (not the confirmation toast):

- Target: new state as asked, with time.
- Every row on the do-not-touch list: same as the snapshot. Any difference is a stop: say it, undo it if it was you, and report.

### 6. Check nothing will do more later

Look for automations that could act on the same client or object: scheduled rules, cron jobs, "auto-pause after N days unpaid" logic in an admin console, platform automated rules, billing auto-suspension.

- If one exists that would go beyond the owner's order, report it, and switch it off only if the owner's order covers it ("the console must not turn anything off" covers it).
- List what such an automation already changed (clients it already turned off, posts it already cancelled) and give the list to the owner. Do not undo those by yourself; the owner decides.
- When you write such logic yourself, the default is **notify, never act**: it lists who is overdue and tells the owner; a human decides what to pause.

### 7. Report in one block

> Done 10:42 (UTC-6). Paused: Client A · Google Ads · campaign "Search MX" (was active, spent MX$318 this month).
> Untouched, checked after: Meta ads (active, 3 ad sets), app (on), other campaigns (unchanged).
> Automations: admin console has an auto-off after 6 days unpaid → disabled per your order, now notifies only.

## Words

- "Only X changed" only after step 5 checked every neighbour.
- Never "paused everything for this client" unless the order said everything.
- If you could not check a neighbour (no access), write "not checked" and why.

## Limits

- It controls scope, not judgement: it will not tell you whether pausing is the right business call.
- Some platforms apply changes with delay or cascade (pausing an account pauses all its campaigns). Read the platform's own rule before acting, and if the cascade would hit a do-not-touch row, ask first.
