# Measuring: is B really better than A?

## Contents
- The 7-day rule
- How many people a test needs
- The noise band (quick check)
- Past messages (the one threshold)
- The two-proportion check (exact check)
- Honest comparison rules
- Reading `connections.trend`
- Choosing the next test
- Results artifact layout

## The 7-day rule

Most acceptances arrive in the first days (in vendor data, about 88% within 7 days). Replies are slower (in
vendor data, about 60% in the first week), so the 7-day reply rate undercounts: fine for comparing two arms,
but it is not the final rate. A raw "accepted / sent" always makes the newest week look worst. So every period is read at
the same age: what went out in it, and what of that was accepted or answered **within 7 days**. A period
younger than that is `counting`: show it, never compare it.

## How many people a test needs

Per arm, to have an 80% chance of seeing a real gap (5% risk of a false alarm):

| Now | Hoping for | People per arm |
|---|---|---|
| 30% accepted | 45% | about 165 |
| 30% accepted | 40% | about 360 |
| 30% accepted | 35% | about 1,400 |
| 10% replied | 20% | about 200 |
| 10% replied | 15% | about 690 |

So test big changes only. A one-word tweak needs thousands of people.
A message test (first message, ask, offer) is sized on **first messages sent**, the people who accepted,
not on invitations: invitations to plan = first messages wanted / expected acceptance rate. Show both counts
and read the noise band off the first messages.
Quick formula (Evan Miller): people per arm = 16 x p x (1 - p) / gap^2, with p the average rate and the gap
as a share (0.10 for 10 points).

## The noise band (quick check)

A gap smaller than this (percentage points) is noise. Any other size: 1.96 x sqrt(2 x p x (1 - p) / n).
Under 10 first messages in an arm: verdict `trop tôt`, counts only, no band. The band is Claude's check,
never on a page: the page says `direction` or `prouvé` and the counts.

| Sent per arm | Rates near 10% | near 20% | near 30% | near 40% |
|---|---|---|---|---|
| 10 | 26 | 35 | 40 | 43 |
| 25 | 17 | 22 | 25 | 27 |
| 50 | 12 | 16 | 18 | 19 |
| 100 | 8 | 11 | 13 | 14 |
| 200 | 6 | 8 | 9 | 10 |
| 400 | 4 | 6 | 6 | 7 |

## Past messages (the one threshold)

Every skill points here for what the user's own sent messages (What got replies, a saved playbook, the Voice
card) can say. They were never split at random, so whatever the count they are a hint, said `piste, pas
preuve`, never a verdict and never a reason to keep a slot that fails the expert shape (SKILL step 4). Under 10
messages of a kind: counts only, no claim at all ("3 sur 3" against "4 sur 12" says nothing). Never "this works
because" read off them. Counted on interested answers only (below); a politeness reply ("avec plaisir", "au
plaisir", a thumbs up) or a no is never counted as a message working. Only a test between two passing versions,
read at `prouvé`, says what works.

## The two-proportion check (exact check)

```
pA = wonA / sentA        pB = wonB / sentB
p  = (wonA + wonB) / (sentA + sentB)
SE = sqrt( p * (1 - p) * (1/sentA + 1/sentB) )
z  = (pB - pA) / SE
```

|z| above 1.96: `prouvé` (95%). Below: `direction`, keep sending. Never a z or a p-value on a page.
Valid only with at least 10 wins and 10 non-wins in each arm; below that, wait (or use Fisher's exact test).
Calculator for users: https://www.evanmiller.org/ab-testing/chi-squared.html

Examples: 30/100 against 40/100 gives z = 1.48, not proven. 60/200 against 80/200 gives z = 2.10, B wins.
Same 10-point gap; only the size changed.

## Honest comparison rules

- Same persona, same send days. Shuffle the list, then alternate down it (an ordered list, by rank, fit score or
  company, makes two halves that differ before anything is sent). When pacing spreads the sends over many
  days, interleave the halves so every day carries both.
- Fix the size before you start and read once. Checking after every result and stopping at the first
  good-looking gap turned a 5% false alarm rate into 26% in one worked example; checking every day also
  inflates it.
- Each batch carries both halves, sent the same day, and is read at the same age: on its own day 7 the
  answered people per half are tagged `read7:<batch>`. Results counts those tags only, once, when the last
  planned batch is 7 days old. Arm sizes come from the Invitations to send page, never restated.
- One change at a time, compared within one persona and the same batches. Every later page (Persona cards
  v2, the Voice card's promotion, Next test, Overview) copies the Results figure per persona and version
  with its label, never a recount or a sum across personas. A voice's count covers the messages written
  in it: in a note test the first message is the same on both sides, so both sides count.
- A lead stays in the half it was drawn into, whatever line it gets (no fact under 6 months: the
  validated moment line); nobody is taken out of one side after the split, no subset counted apart.
- A first-message test counts replies within 7 days of the first message. Follow-up 1 goes after that
  batch's day-7 tags, or earlier only when it is the same in both halves and names nothing tested.
- Both sides pass the expert shape (SKILL step 4); a version that fails it is never a side, so never
  kept on a tie.
- `direction` keeps the arm ahead for now ("on garde X pour l'instant"), the baseline on a tie. Ahead
  means more interested answers, not more no's. A message arm kept on direction goes back to the baseline
  when the next test changes the message, unless `prouvé`. A note kept on direction is an invitation
  lever: it stays on every invitation of that persona's next test, both sides alike (a Next test that drops it
  undoes a Results decision: Claude fixes it before drawing). A direction is never carried to another persona.
  An acceptance gap inside the band gets no chip.
- A draft the user edited is counted per half from its edited tag per batch (amber `modifié par vous :
  N`); a voice edit applied to both halves alike is not a test variable.
- A gap found by slicing afterwards is an idea for the next test, not a result.
- Four verdict words, nothing else: `trop tôt` (a batch under 7 days old or under 10 first messages in an
  arm), `direction` (which side leads, gap under the band), `prouvé` (gap above it), `base seule` (grey:
  nothing was paired, so there is nothing to compare).
- Note against no note: read acceptance and replies per invitation sent. The note ahead on both keeps it
  for now, under the `direction` rule above; behind on either, no note.
- Repeat a win once before rebuilding everything on it.
- Sanity check: two halves with the SAME template usually differ by less than the noise band. One crossing
  in 20 is chance; a crossing that repeats means the split is biased.

## Reading `connections.trend` (from `bereach_status`)

| Field | Meaning |
|---|---|
| `withinDays` | 7: the age every period is read at |
| `weeks[]`, `days[]` | 6 weeks (Monday start) and 14 days, oldest first |
| `counting` | true = younger than 7 days after its end: do not compare |
| `invitations.sent / won / rate` | invitations sent in the period, accepted within 7 days, whole percent |
| `invitations.withNote`, `withoutNote` | same, split by note |
| `firstMessages.sent / won / rate` | first messages sent, answered within 7 days |

`rate` is missing under 10 sent. The trend covers all the user's accounts together; split by persona or arm
with tagged contacts: `bereach_contacts` with `tag`, `engaged` false, `limit` 100, follow `nextPage` until it is
absent, and count `outreachStatus` yourself. Accepted = connected, dm_sent, followed_up, replied, in_conversation,
meeting_booked, not_interested. Answered = replied, in_conversation, meeting_booked, not_interested; interested =
in_conversation, meeting_booked, or a reply that engages (a question, a yes, a request); no = not_interested; a
politeness reply (a thanks, an emoji, "avec plaisir") or a deferral ("not now", "later", a vague request for
information) is answered, never interested; a request for the offer by name is interested. Every claim about what works
counts interested answers only. These counts are to date:
they only set a batch's `read7` tags on its day 7, never Results directly.

## Choosing the next test

Next test, in order (the first that applies):
1. a card line changed from replies (pain, objection answer): a premise the replies refuted is changed
   before anything else, never carried forward (red `contredit les réponses`);
2. a persona at 0 replies on 8 or more first messages: (a) check the card's Why now against when the user
   is hired, and list every template line that fights the card (a who-writes clause claiming what the
   objection answer says someone else does), (b) one plain change or a pause, the user picks;
3. acceptance below the saved baseline by more than the noise band: an acceptance lever before any
   message test (the headline, a premise note when the account can add notes, or the card's Signal slice).
   An invitation change the same on both sides (the headline, a note kept) may always run beside a
   message test;
4. another angle: another pain or premise row of the card, never the same one reworded;
5. the offer: two of the user's real offers they keep, both passing the shape (the offer swapped, nothing else); what replies
   asked to receive is the first candidate.

Size it before drawing, from the table above: expected first messages per arm under what the hoped gap
needs is amber `trop petit pour se voir`, and Claude picks one way out, said in one grey line: the same
pair over two periods, read pooled, only when the expected new leads per period (SKILL.md step 1, point 6) cover it;
else a bigger lever.
A new offer is one the user made or a reply asked for, never one Claude proposes. Need new leads: its own Plan and personas page and its own yes,
widened and timed as SKILL.md step 1, point 6 says.

A voice edit the user made twice is offered on the next Drafts for review and, on the yes, applied to every
saved template, follow-up and offer carrying that word or its family, both sides alike, in one
decision; the Message checks run again on each changed template.

## Results artifact layout

The wireframe, fields and flags are in `references/artifacts.md`, section "Results".
