---
name: linkedin-messages
description: "Writes LinkedIn invitation notes, first messages and follow-ups: one template per persona, then per lead a real fact framing its offer. Use when messages sound generic or repeat the title."
---

# LinkedIn messages

Each message type has one recommended framework, written whole in the user's voice. Show
the method on their own leads, never explain it. Each step ends on a page (`references/artifacts.md`).
Starts from the Persona cards (linkedin-personas) and the Voice card (linkedin-voice), even provisional. A rule in Claude's memory that
contradicts the Voice card loses (cleanup: bereach-setup).

## Hard rules (only these hold a message)

1. Nothing invented: no fact, date, tense, proof, figure, guessed feeling, claim about the user's work,
   or offer the user never made. A proof only from the user's own words about a real customer. A
   reply states no product, price or work fact the user did not give: ask the user. Never a placeholder
   in a draft.
2. The right person: `bereach_brief` for every person before every message, every option on (Step 3).
   A draft only for a lead sure on Who is who; never someone already talking to the user, a customer or
   a past client. Any reply from them or a colleague at their firm stops the sequence, except to a
   colleague a reply names.
3. Nothing is sent without the user's yes.

The user's rules: the craft upgrades every weak part of their message and keeps their voice: greeting
and sign-off word for word, address form, pronoun, punctuation, words, Never list. Never a word on credits or cost, even when the
user raised them. French: "vous" and "Bonjour Prénom," unless the Voice card says tu; in a reply, the
form they wrote in. No em or en dash. No third party's data; no client named without consent. No legal,
opt-out or data-source line (how they were found, where a fact came from); a referral the lead made is
a tie, not one.

## One framework per message type

| Type | Framework | Why | Size |
|---|---|---|---|
| Invitation | Premise note (Holland) when a real fact exists, else no note | Accepted for a reason about them; asks nothing, so never a pitch | 200 characters or `notes.maxLength` |
| First message | Premise first with the user's real offer (Holland; reciprocity) | A real reason about them, then what the user really offers, with an easy no | 2 to 4 full sentences |
| Follow-up 1 | One real peer (Cialdini). No real customer result: poke the bear (Braun) | Something new; a similar peer is the best-supported lever | 1 to 3 full sentences |
| Follow-up 2, the last | Detach: the offer again with a plain way out (Braun; Voss) | Makes no easy and closes the loop with respect | 2 short sentences |
| Reply | FAB through "So what?", tied to their words (Rackham) | They already gave their attention; only a benefit tied to what they said moves it | Follows theirs |

Before writing or judging, read `references/frameworks.md` (the type's card; Levels of
awareness for the persona's Awareness line) and the type's file (`references/invitation-note.md`,
`first-dm.md`, `follow-ups.md`, replies included). A draft names its framework, and why it fits, only when
it visibly applies it. Sequence: invitation, first message, two follow-ups, stop at the first reply (five
messages: `references/sequence-5.md`).

## Size: a range the parts fill, never a target to pad or squeeze to

Write the framework whole in full, native sentences. Cut a whole idea, never the grammar: no verbless
opener, no colon joining two clauses, no statement that turns into a question, no clipped sentence. Past about 500
characters a message reads long. Under a hard limit (the note), say the full framework does not fit and
send no note. Characters are counted only for the note, as the prospect gets it
(`{Prénom}` as 10, a line break as 1).

## The offer

The offer is one the user already made in a message, or one a prospect asked for in a reply. None exists:
ask the user once; meanwhile the message ends on their proven ask, else one plain question tied to their
fact. Never propose a study, estimate, audit or map the user has not offered. Never a case study, demo,
call or discount.

## Judge, then upgrade

Judge every part of the chosen framework, the user's own words included. Rewrite every failing part in
ONE recommended version in their voice; each change names its principle. No "keep as is".
Read aloud: a sentence read twice is rewritten. Asked for best practice: the same verdict and version.

## Step 1. Read what exists

- `bereach_memory_list`, `fullContent: true`: type `offering` (Persona cards, validated templates) and
  type `playbook` (the Voice card per language; several: ask which).
- What got replies (linkedin-outreach-method): evidence, never a template to keep.
- `bereach_status`: `connections.trend` (null under ten sent: "not enough yet"), each account's `notes`.

## Step 2. One template per persona and type

Fill the type file's parts from the persona card. Fixed words plus
two slots: `{fait}` and the offer's object it frames. Each persona carries ONE moment line, a situation of
their work they would recognise, for leads with no fact under 6 months; a slot reads right whatever
fills it. Deliver "Message templates", then `bereach_memory_save` type `offering`.

## Step 3. The fact per lead

`bereach_brief` for every person before every message: it settles who is who, the current
company and past conversations. No `include`, `campaignId` of the list, `historyVerbatim` 200,
`maxAgeDays` left at its default: the brief reads the conversation anew every call. The type is decided BEFORE the brief, from `bereach_inbox`
and the user's samples: anyone already written to gets a reply or follow-up. No word of a reply exists
before the brief has returned their last message; it answers what they wrote, and a politeness reply
gets one short real next step chosen after reading.
A whole list: `bereach_add_signals`, then `start: false` (its `list_url` in the page footer), then
`bereach_contacts` (`campaignId`, `sortBy: "whyNowAt_desc"`).

Pick ONE fact: something they wrote or said, then something
they shared, then another dated fact under 6 months, else the moment line. Use it only if it ties, as
they meant it, to why the user writes, and add one clause on why it matters to them. The tense matches
the date. After a note, the first message opens on a second fact, the consequence
or the offer's reason, never the note's line.

## Step 4. Show

**Deliver: "Drafts for review"**: 3 real rendered examples, then only rows that need a decision (TO FIX
only for what only the user knows). Every draft is created with `bereach_draft_dm`. The 3 previews on
Plan and personas (linkedin-outreach-method) pass Steps 3 and 4; never drafted, queued or sent.

## Step 5. Put the approved drafts in BeReach

- Approve no message naming an offer the user never made.
- **Invitations** (`references/invitation-note.md` read first): `bereach_connect`. With no note, one call
  per half. With a note, one call per lead, because a call's note is one text for everyone in it. A
  note left off: tell the user word for word.
- **First messages**: the Step 4 drafts (`contactId` from the contacts or the brief; `null`: save first with
  `bereach_get_profile`), then `bereach_approve_drafts` (edits in `editedMessages`) once the person reads `connected`
  in `bereach_contacts` (`campaignId` of the list, `outreachStatus: "connected"`) (`references/first-dm.md`,
  When). Never promise a send time.
- **Follow-ups and replies are not queued**: `bereach_inbox` each working day, **Follow-ups to send**
  (`references/follow-ups.md`), `bereach_send_dm` on the yes, never two in one visit.
