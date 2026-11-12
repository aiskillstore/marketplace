---
name: sort-me-out
description: >-
  Load when the user says "sort me out", "what am I missing", "what did I forget", "what's pending", "I'm all over the place", "ordéname", "qué me falta", "qué se me pasó", or asks for a full picture of everything open across projects, chats, clients and notes. The agent studies every source it can reach (notes, logs, task lists, memory, recent conversations, project files, live systems), then gives ONE ordered list: what is pending, what was promised and never done, what fell through the cracks, what is blocked and on whom, ranked by urgency and money at stake. For people who juggle many things and lose track.
license: MIT
---

# Sort me out

The user is juggling too much and things fall through the cracks between conversations: a promise made on Tuesday, a "send me that later" nobody sent, a task blocked on a third person who was never reminded. Your job is to be their memory and hand back **one clear, ordered list**, not a pile of notes.

## 1. Gather: read everything you can reach (silently)

Look in every source available to you, newest first:
- project notes, logs, changelogs, to-do files, decision records;
- the agent's memory and the user's own instructions file;
- recent conversations and other agents' reports you can access;
- task lists, issue trackers, calendars, inboxes you are allowed to read;
- live systems when a check is cheap (is the service up, did the payment arrive, is the item still "pending").

For each open item, write one line for yourself: **what, for whom, who must act, since when, what happens if it waits.** Mark the source.

## 2. Verify before listing

- If a note says "pending" but you can check it now (status page, API, file), check it. Done items do not go on the list; items that broke since do.
- Merge duplicates (the same task written three ways in three places).
- Separate what you **checked** from what you only **read** in a note.

## 3. Hunt for what was forgotten

Explicitly look for:
- promises the user (or the agent) made: "I'll send it", "tomorrow", "after lunch";
- things started and never finished: half-done setups, drafts, unpublished work;
- items waiting on another person with no reminder sent;
- deadlines and recurring duties (renewals, weekly reviews, payments due);
- money left on the table: unpaid invoices, quotes never followed up, clients who went quiet;
- small risks that grow: expiring keys, full disks, accounts under review.

## 4. Deliver one ordered answer

Format, in the user's language:

1. **Today, urgent** (money, a client waiting, something broken): max 5 items.
2. **This week.**
3. **Waiting on someone else**: who, since when, and the one-line nudge to send them.
4. **Forgotten / slipped through**: the items found in step 3.
5. **Done since last time**: one line, so the user sees progress.

Each item is one line: what, why it matters, the next action, and who does it. Mark the ones **you** can do right now and do them (or offer to, if they are irreversible or cost money). Mark clearly what you could not verify.

No essays, no repeating the sources back. If the list is long, keep the top of each section and say how many more there are.

## 5. Keep the memory

Save the list (with date and time) where the project keeps notes, so the next "sort me out" can show what changed. Never store secrets in it.
