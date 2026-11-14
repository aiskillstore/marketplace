---
name: linkedin-voice
description: "Learns the user's voice from 3 to 5 messages they sent, upgrades the craft with the pack's expertise, saves it as the BeReach playbook, checks drafts against it. Use before writing outreach."
---

# Voice card

Goal: every message Claude writes reads like the user wrote it on their best day: their voice, a pro's
craft. Their messages give the voice; the pack gives the craft and upgrades every failing slot, whoever
wrote it, pro or novice (Step 2b). The voice card is the one source of truth.

On the card: the **voice** (how they always write) and the **tone per message type** (note, first message,
follow-up, reply). Not on it: the offer (the `offering` memory), the ICP and personas (the search plan,
the persona cards).

## Step 1. Collect real writing, not adjectives

Never ask "how would you describe your tone?". Ask for messages they sent.

1. Saved voice first: `bereach_memory_list` type `playbook`. Several: ask which one. Read it with
   `fullContent: true` and its `scope`. Its identity fields are kept; its samples and guidelines go through
   Step 2b like pasted messages (being saved is not a pass).
2. Rules elsewhere (Claude memory, project instructions, other playbooks) stay off the card; one that
   conflicts goes to the bereach-setup skill's What Claude knows page.
3. Take the **3 to 5 messages that got a reply** asked in the linkedin-outreach-method skill's one question
   round, varied (people, topics, lengths), first messages to prospects if they have them: pasted text, a
   screenshot or a file.
4. Nothing to paste: the answered messages the user confirmed in "What got replies" (linkedin-outreach-method)
   when it ran. Otherwise, with the round's yes: `bereach_inbox`, up to 8 answered conversations,
   `bereach_brief` with every part on, the list's `campaignId` when there is one and `historyVerbatim` 200.
   Keep only word-for-word messages, each with a grey chip `écrit par vous ?`, kept unless the user says no.
5. No answered message: unanswered ones they wrote may be read for FORM only (greeting, sign-off, address
   form, contractions, punctuation), each `à confirmer`, never for content or length. Then write one test
   message; their corrections become the first sample. The card stays `provisoire` until a reply.

Only text the person wrote, never tool text they did not rewrite or validate word for word. The
**reference message** is their best hand-written one after the upgrade, the example the writer copies first.

## Step 2. Read the voice by counting

Before filling it, read `references/frameworks.md` (Summary, and T/V distinction for a language with a
formal "you"). Fill `references/voice-card-template.md`: count each field (I/we/you share, vous or tu,
! and ?, sentence length, greeting, sign-off) and put the quoted fragment next to the number; samples verbatim.

- **Size**: linkedin-messages (the user's lengths are information, never a target).
- **Address form**: as the samples, never mixed in one message. Not decided: formal for a first contact,
  then mirror the prospect.
- 2 to 5 verbatim **signature phrases**, each from a slot that passes the framework; one from a failing
  slot (thank-you, wish, "n'hésitez pas", an ending) is never voice.
- The **Never list** (ask "anything you would never write?"), **tone per type** (types the samples show,
  else empty).

## Step 2b. Expert upgrade: judge every slot, upgrade every failing one

Before judging any sample, read the linkedin-messages skill's `SKILL.md` (Judge, then upgrade; One
framework per message type), its `references/frameworks.md` (the card for that sample's type) and its
type file (`invitation-note.md`, `first-dm.md` or `follow-ups.md`, Parts): judge each slot against those parts.

Every sample at once, saved or pasted: upgrade every failing part into ONE recommended version, the
principle per change in plain words; replies are a hint, never proof. What this skill adds:

- **Identity, always kept** (the only thing the samples give): their greeting and sign-off word for word
  (none added when they never sign, never a "Cordialement" they do not use), address form, punctuation,
  contractions, pronoun, their vocabulary, Never list, language. **Craft, always judged**:
  everything else, the line after the greeting included.
- The upgraded version is a sendable message to a real lead, on that lead's real fact, never a template
  with blanks or `[ ]`. A thank-you or politeness opener always fails.
- Who writes, always kept: one short clause, name or "we" and the trade, said as what the user does for
  THAT reader, never a verb about connecting tools. A clause about the sender's own project or place is a
  pivot to the sender; the same sentence gets the same verdict in every message of the session.
- The offer: only one the user already made in a message, or one a prospect asked for in a reply, with the
  user's gift verb kept as written ("j'ai trouvé"). None: the user is asked once; meanwhile their proven ask,
  else one plain question tied to the lead's fact. Never a study, estimate, audit or map they have not
  offered, never a placeholder.
- Never a grade said to the user, never a claim about what works from a handful of messages.

## Step 3. Deliver the Voice card

Before drawing it, read `references/artifacts.md` (Voice card). **Deliver: "Voice card"**, the first block
of Voice and messages (its own page only when this skill runs alone), one per language, state draft, with
one **test message** to one real person in a sure persona never written to (rules in artifacts.md), briefed
with every part on, on a new fact, and ONE decision validating the upgraded versions, never "keep as is".

A correction goes on the card (a "never" becomes a Never item). That one yes saves the card.

## Step 4. Save it as the playbook

`bereach_memory_save` with `type: "playbook"`, a `label` of 2 to 4 words (what the message is for), and
`content` as one JSON document:

```json
{
  "version": 1,
  "writeMode": "guidelines",
  "language": "fr",
  "addressForm": "vous",
  "tone": "one line per message type",
  "guidelines": "the card, written as one writer briefing another",
  "hardRules": "only rules the user stated, in their words, each marked (stated, not counted)",
  "samples": ["validated upgraded message 1", "validated upgraded message 2", "validated test message"]
}
```

- `samples` hold the versions the user validated after the upgrade, never an original with a failing
  slot; `guidelines` carry the identity fields and the craft from the framework, never a failing habit.
- `writeMode`: `guidelines` for different messages; `strict` with a `skeleton` only for one exact template
  sent to everyone (drops `tone`, `guidelines`, `hardRules`: the never list goes in the skeleton); `hybrid`
  for both.
- Adjust: the existing `scope`, only the changed fields; a field left out is kept, `null` removes it.
  Start again: same scope, `null` for every old field the new card does not set (`skeleton`, `steps`,
  `variables`).
- One playbook per language; a second label only when the user asks. One voice, one place: never also in
  Claude memory or project instructions.
- Saving draws no page: one line on the next one. It never turns an `à confirmer` chip green.
- **Promote it** after the first Results, and **a change** (the same edit made twice): rules in
  `references/artifacts.md` (Promote and change). Neither keeps a version that fails a Step 2b slot.

## Step 5. Check every draft against the card

Count before showing a draft; fix what fails, then show it. Open the linkedin-messages skill's `SKILL.md`
(Hard rules; Size) and run both in full; on top of them, from the card:

- [ ] Greeting, sign-off, casing and contractions as on the card; full sentences as long as the framework needs.
- [ ] Reads in one pass aloud: no verbless opener, no colon joining two clauses, no statement that turns
      into a question, no run-on; a part that does not fit is dropped whole, never shrunk.
- [ ] Address form as the card; French with no form on it: vous, "Bonjour Prénom,".
- [ ] Punctuation habits kept (no ! or emoji if they never use one).
- [ ] No Never word; at most one signature phrase; unless their samples do it, no "not (only) X but (also)
      Y", no list of three, and in English none of crucial, delve, seamless, robust, pivotal, leverage.
- [ ] No em or en dash, no invented fact, number or offer, no `[ ]`.

Counting is reliable, a model's sense of "sounds like them" is not. Then ask: **"Would you have sent
this?"** A "no" is a card update, not just a draft fix.

## Rules

- Who they are comes from their messages only, the craft from the frameworks and the pack. Never ask again for
  a voice already given.
- Credits never shape a message, a choice or a test: every person is briefed. A craft answer never
  mentions credits or cost, even when the user raised them: it starts on the verdict.
- Language: the one the recipient reads; a second language gets its own samples and card.
- The card decides greeting, casing and address form over the linkedin-messages defaults, except a
  lowercase casual opener never carries into French with vous.
