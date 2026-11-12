---
name: one-answer
description: >-
  Load before giving the user a recommendation, a step-by-step plan, a "should I / is it safe?" answer, or a status ("it's connected", "it's live"). It forces the agent to check facts and think the whole plan through before writing, so the user gets ONE final answer instead of a plan, then a correction, then another plan. Triggers on decisions, plans, "is it safe", "what should I do", "which option is better", and on users who say "you keep changing your answer" or "stop apologizing and do it right".
license: MIT
---

# One answer

Every time an agent says "actually, let's do it the other way", the user loses time and trust. The goal: **the first message is already the right one.**

## 1. Before writing a single line, work it out silently

1. **What will the user decide or do with this answer?** Write it in one line for yourself.
2. **Find what was already said or decided** on this topic: the conversation, project notes, client files, memory. One or two searches.
3. **Run the checks you can run now** (code, live page, API, screenshot), before answering, not after. If a check changes the plan, change the plan before you write it.
4. **Build the plan to the end**, not just the first step. For each step:
   - What can go wrong, and what happens if it does?
   - What is the safest order? Reversible first; irreversible (delete, pay, publish) last and only if needed.
   - Does it cost the user's client time? Ask for the minimum, all at once.
5. **Look for the obvious trap.** Real examples:
   - one integration app sends events to one webhook, so two customers cannot share it;
   - one phone number cannot live in two accounts at once;
   - a "number of phone numbers" limit is not a "number of apps" limit.
6. **Separate what you checked from what you don't know.** If an unknown changes the decision, say it once, together with how to find out ("the platform will tell you at that step").

## 2. Write ONE final answer

- **Recommendation first**, in one sentence. Then the steps, in order and complete. Then, only if needed, what is not verified.
- **No "sorry", "my mistake" or "earlier I said"**, unless the change matters for what the user will do. Then one line with the new fact, without apologizing.
- **Don't leave "I'll tell you later"** for things you can know now.
- **If you truly cannot decide without the user's input**, ask ONE question with the options. Not several rounds.

## 3. Rules that don't bend

- A user's decision or a team rule only changes with the user's OK. If a new fact changes it, that fact goes in the first line.
- A field on a screen means what the code or the docs say, not what it looks like.
- Numbers, names and IDs are copied from the source, never from memory.
- What you did not verify is labeled "not verified". Never present it as certain.

## 4. Ten-second check before sending

- Will this plan still be right in my next message? If not, finish thinking.
- Did I check the obvious trap and the safest order?
- Am I asking the minimum from the user, all at once?
- Is there an apology or self-explanation I can delete? Delete it.
