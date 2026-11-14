---
name: linkedin-outreach-method
description: "Runs the whole LinkedIn outreach loop: find, sort by persona, voice, one template per persona, send, measure acceptance and replies at 7 days. Start here for any LinkedIn outreach."
---

# Outreach method

Goal: **acceptance rate and reply rate go up, week after week.** Each step ends on one artifact. Only a page that
sends, runs searches or sets the words sent in the user's name waits for a yes (a brief never does); any other is shown and Claude goes on, saying in one line what it adds
later.

Check first: `bereach_status` answers; if not, the bereach-setup skill, while the cards and voice go on. LinkedIn
signed out: no `bereach_connect` or `bereach_draft_dm` (both refuse); the pages show the words, a reconnect asked once. Read saved
rules once (memory, pasted instructions): an old ICP, role or size rule is a Plan and personas chip; any other that
fights a skill or a card goes to What Claude knows, after the first invitations.

## The artifacts

Same names in every skill. Before drawing a page, read its wireframe in `references/artifacts.md` and its row in
`references/frameworks.md` (Step to framework); ICP and persona words: `references/icp.md`.

| Order | Artifact | Drawn by | Waits for a yes |
|---|---|---|---|
| before | One question round (a message) | this skill | the answers; a blank becomes a `(guess)` |
| 1 | Plan and personas (cards v1, people in the account, searches, 3 message previews) | this skill, cards by linkedin-personas | yes: the searches spend credits |
| 2 | Invitations to send | this skill | yes: it sends |
| 3 | Voice and messages (Voice card, What got replies folded, Message templates) | linkedin-voice, linkedin-messages | yes: the words go out in the user's name |
| 4 | Drafts for review, Follow-ups to send, per batch | this skill | each send |
| 5 | Results, then Persona cards v2 (their words from replies) | this skill, linkedin-personas | the decision, the changed lines |
| 6 | Next test | this skill | the one change |
| after 2 | Go further (what improves next, which skill) | this skill | nothing |
| after 2 | What Claude knows, only when a saved rule fights a skill or a card | bereach-setup | the deletes |
| on | Overview, only when nothing waits elsewhere | this skill | nothing |

## Where things are kept

- Persona cards and templates: `offering`, `## Personas` (saving replaces it: read it whole, keep the rest). Voice
  card: `playbook`, one per language. Persona, half, day-7 read: contact tags, `bereach_contact_update` `tags: { add }`, never `set` (it wipes the other tags).
- Credits (every skill): said only where a search spends them (its page asks before spending; a contacts offer
  costs a search per yes). Never on the message side: no credit word in a chat line, page, choice, test or craft answer
  about briefs, profile reads, drafts, invitations or messages, even when the user raised them (answer the craft
  only), and never a reason to skip a brief or a read.

## 1. Read, ask once, then Plan and personas

The question round is the first message: only step 1 is read before it; briefs run as one batch.

1. `bereach_status`, BeReach memory and ONE count of the untouched people (`references/search-doors.md`, one call,
   its total).
2. At once ONE question round (one message): their website and documents, the linkedin-personas questions, may Claude read
   their conversations, 3 to 5 messages that got replies, their languages, anything they would never write.
   Unanswered ends in `(guess)`; an answer is one chip on the page.
3. With the answers: their website, CRM and documents (linkedin-personas, Step 1; customers and open deals leave
   the list), `bereach_plan_searches` (free), the untouched people split per persona (`references/search-doors.md`).
4. Deliver **Plan and personas**: Persona cards v1 (linkedin-personas), the untouched people split per persona,
   searches only for a persona short of a first week of invitations (read first: `references/search-doors.md`,
   The doors; `references/icp.md`, From ICP to search),
   then the band **3 premiers messages**: previews to 3 real leads, each fully briefed and checked (linkedin-messages, The fact per lead and Show). On the yes (no
   search: at once): `bereach_run_searches`, the cards saved, sure rows tagged; the page is republished with what was found.
5. Every filter answered (place AND size) applied; out of scope (student, own profile, side project, own team,
   outside the ICP) leaves with one grey line and never comes back.
6. A repeat search short of new people: one widening proposed, never waited on. A title that changes the role, or a
   country where the card's busy months or Why now do not hold, is a new card (linkedin-personas), never in a running
   test; a new range goes in the card's Found by. Run it at most a week before the invitations it feeds.

## 2. What got replies

Once per pack, with the round's yes (`references/conversation-review.md`): it feeds the cards v1 and shows folded
on Voice and messages.

## 3. Voice: the linkedin-voice skill's Voice card, first block of Voice and messages

## 4. One template per persona (the rule the other skills point to)

The linkedin-messages skill writes per persona ONE first message and two follow-ups (and the note: its Invitation row), each
in its type's framework and through its Judge, then upgrade (its `references/frameworks.md`
and the type's file read first). The user's messages give the voice; the craft
always comes from the pack, pro or novice.

- **The upgraded message is the baseline at once**, proposed for validation (the user may correct words), never
  beside a "keep as is". A reply never proves a slot (`references/measuring.md`, Past messages).
- **A test compares two versions that both pass** (two offers, two angles), one slot changed. Never a test or a
  choice framed by cost, never fact against no fact.
- The offer: only one the user made (an answered message, their words) or a prospect asked for; none: Claude asks
  once, meanwhile their proven ask, never a placeholder. Nothing invented about the user.

Deliver **Voice and messages** after the invitations go; the user's yes to every fixed word saves both. The previews on
Plan and personas need no yes; a draft put in BeReach waits for this one.

## 5. Send

Invitations, per persona, the account's untouched people first, found people only to fill the batch:
1. Take out every held lead, every unsure one, a brief showing a role outside the ICP (one grey line), everyone already in a conversation or a past client (`bereach_inbox`,
   `bereach_contacts`, the cards' Proof), matched on the profile in every spelling of its address. Settled minus set
   aside (each lead once) equals invited; Claude recounts until it does.
2. Split or not: expected first messages per half = (the persona's invited total x the acceptance of all accounts together) / 2
   (`connections.trend`, the baseline, at 10 or more sent in 6 weeks, else 1 in 3). 30 or more: two halves, the pair of step 4; under the hoped gap's size (`references/measuring.md`): a
   direction only, nothing asked. Under 30: the baseline alone.
3. Halves: shuffle, alternate, tag `arm:<persona>:a` and `arm:<persona>:b`.
4. A headline that does not say the trade in this persona's words: one proposal, never waited on.
5. `bereach_connect` with `dryRun` true per half, then deliver **Invitations to send** with its two computed dates
   (last batch, Results); a note test: each invitee briefed first (linkedin-messages `references/invitation-note.md`); no fact, no note. On the yes: halves interleaved; a half with notes is sent one call per lead, because a call's note is one text for everyone in it. A later accept joins the next period, outside the test.

First messages, for each new batch of accepts (both halves, drafted and approved the same day):
1. `bereach_brief` for every lead, every part on (linkedin-messages, The fact per lead). No fact under 6 months: the validated
   moment line, the lead stays in its half. A signal lead gets its signal, both halves.
2. `bereach_draft_dm` with the persona's template (linkedin-messages `references/first-dm.md` read first); deliver **Drafts for review**.
3. On the yes: `bereach_approve_drafts` on READY rows, never for someone the connect skipped; track with
   `bereach_outbox` and `bereach_invitations` direction `sent`.

Day 7 of each batch: tag who answered, per half and persona, `read7:<batch>`; only then follow-up 1.
Every working day `bereach_inbox` (free): an answer stops the sequence for that person and every colleague at the
same firm, except a colleague the answer names (linkedin-messages `references/follow-ups.md`). Deliver **Follow-ups to send** each day something is due or an interested reply arrives: replies on top
(linkedin-messages `references/follow-ups.md` read first), one block per batch, each person's `bereach_brief` read first, read again before each message (`maxAgeDays` left at its default, the conversation is read anew). `bereach_send_dm` on the yes.

## 6. Measure at 7 days

`bereach_status` `connections.trend` for all accounts together; per half or persona the `read7` tags only, never a count to
date or a rate from `bereach_invitations` (`references/measuring.md`, The 7-day rule, The noise band). **Results** is drawn ONCE, on its date from
Invitations to send; before, one Overview line, and Persona cards v2 and Next test wait (a fill-in search does not).
One decision row per persona; later pages copy its figures, never a sum across personas.

## 7. Decide, then change one thing

Read `references/measuring.md` before calling a winner. A persona without halves gets a plain change or a pause
(a new period, not a test); a pause stops new invitations and first messages, follow-ups already due still go. The
user's stated busy months move the dates; a `(guess)` moves nothing.

**Next test**: the first that applies in `references/measuring.md` (Choosing the next test), after Persona cards v2 has its yes; the winner
is the new template; every new message passes the linkedin-messages chips.

## Never

- Never send a message, first, follow-up or reply, without the user's yes on that send's artifact.
- Never import an industry benchmark as a target rate: beat your own baseline. Voice notes, video:
  `references/advanced.md`.
