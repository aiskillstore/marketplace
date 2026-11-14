---
name: cold-email
description: "Writes cold emails and follow-ups for people in a BeReach list: finds work emails, one sequence per persona, drafts the user sends. Use for any cold email or email outreach."
---

# Cold email

BeReach finds the work email; Claude writes the drafts. **The user sends them from their own mailbox or
email tool.** Nothing here sends or reads an email. `bereach_draft_dm`, `bereach_send_dm` and
`bereach_schedule_drafts` are for LinkedIn messages: never use them for an email.

Each step ends with a **Deliver**: a page drawn as in `references/artifacts.md`. **Only a page that spends email credits or hands over emails to send waits for the user's yes; the
Sending check is shown and Claude goes on.**

Refused with a trial link: give it to the user and stop, no retry.

The web only teaches the user's trade; a vendor statistic never decides. Asked for best practice: a
verdict per slot, then the upgraded email to validate.

## Step 1. Sending check (once per user)

Five questions only:

1. Which mailbox sends (work domain, not a free webmail)?
2. Are SPF, DKIM and DMARC set? If unsure, say how to check (`references/deliverability.md`).
3. How many cold emails a day? Over 50 per mailbox: too many.
4. Which countries are the people in (sets the footer, `references/legal.md`)? Germany: left out unless the
   user says otherwise. An EU country legal.md does not name: amber, check.
5. Is tracking off (no open pixel, no wrapped links)?

**Deliver: "Sending check".**

## Step 2. Who, and why them

1. Read the list: `bereach_contacts` with the list's `campaignId`, `engaged: false` (a found `whyNow` is
   a free dated reason). Drop do-not-contact people and anyone tagged `cold-email`,
   silently (count only).
2. Read what they sell: `bereach_memory_list`, type `offering`, `fullContent: true`. Its `## Personas`
   holds the persona cards (each with Offer and Why now window).
3. Read the voice card: `bereach_memory_list`, type `playbook`, `fullContent: true`, the one place for
   writing rules (it wins on voice, the self-check on craft).
4. Persona cards or voice card missing: build them first (linkedin-personas or linkedin-voice skill).
5. Before sorting, read linkedin-personas `references/persona-card.md` (ICP, plan groups and cards).
   Put each person in one persona, tag `persona:<short-name>` (`bereach_contact_update`, `tags.add`).
   READY: title matches one card, company inside its ICP. CHECK: two cards fit or the company is outside;
   no email lookup, brief or draft until the user decides. Out of scope (not this persona,
   outside the ICP): left at the search step; found later: HOLD, no email. Batches of 25 at most, 2
   per company.

**Deliver: "Who is who"**, cost for READY people only, plus the whole-list signals ceiling (`bereach_add_signals` `start: false`). Nothing is spent before the yes.

## Step 3. One sequence per persona

1. Open `references/frameworks.md` now, before writing a word (Default, Which shape when). Baseline: its
   default (self-check, opening and ask) in the user's voice unless a row fits better, opening on a dated
   fact from their brief, else a moment of their work. The user's own emails give the voice (address form,
   greeting, sign-off, words), never the slots: keep a slot of theirs only where it passes the self-check,
   rewrite every failing one with a framework named on the page, replies included. **The offer comes from
   the user's own trade**, is kept by the reader (a sheet, a plan, a sample of their work; software: a free
   audit or estimate of THEIR case, never a case study), exists before the send (no blank); an object a
   past reply asked for works as the offer. Never offer to find contacts unless that is the user's trade.
2. 3 or 4 emails (`references/sequence.md`), days 1, 4, 8, 14, step 2 a reply in the thread, each ending on
   one yes/no question naming its object, the last offering the way out. ONE offer per sequence.
3. Proof only in a follow-up, from a real customer of the user, else none. Never a claim about
   the user's work, customers or results they did not give: ask.
4. A `{why now}` slot in every template that reads right whatever fills it. No fact under 6 months: a
   moment line. Two languages: same offer, same ask.

**Deliver: "Message templates"**, one per persona, email 1 filled for one real person. After the yes, save it
under that persona: `bereach_memory_save` type `offering` replaces the whole entry, so resend the Step 2
offering whole.

## Step 4. Emails, then the reasons

1. `bereach_find_emails` with every READY `contactId` in ONE call (25 at most). One email credit per email
   found; none found is free. Quote `emailCreditsUsed` from the reply, never a sum.
2. Only `verified: true` is sendable; else "unverified, skip".
3. Email credits run out: give `buyCreditsUrl` and the `note`, stop for the people left.
4. `bereach_brief` (`contactId`, `campaignId`, no `include`, `historyVerbatim` 200; `maxAgeDays` left at its
   default, the conversation is read anew) for every READY person before each email to them,
   batches included. For a whole list, `bereach_add_signals`, within the Who is who yes. Nothing usable:
   a moment line, marked.
5. Fill `{why now}`: one sentence giving the fact AND why it made the user write (the tie to the offer),
   tense per its date (`references/frameworks.md`, Personal line rules). **Never invent a fact.**

## Step 5. Drafts and review

Open `references/frameworks.md` again, then write each READY person's email 1 from the approved sequence
plus their line. Self-check and fix every draft. An offer not deliverable now: block those rows.

**Deliver: "Drafts for review"**. The user approves, edits or removes rows.

## Step 6. Hand over

**Deliver: "Ready to send"**, then:
- `bereach_contact_update` on everyone handed over: `tags.add` `["cold-email", "cold-email-YYYY-MM-DD"]`.
  Never `tags.set`; leave `notes` alone.
- One line: own mailbox, 20 to 50 a day at most, tracking off, found addresses not emailed deleted
  (`references/deliverability.md`, `legal.md`).

## Step 7. Replies and results

- Stop, unsubscribe, not interested: `bereach_contact_update` with `doNotContact: true`; the user removes
  them from any running sequence the same day.
- A positive reply (pasted by the user): `bereach_brief` first (`maxAgeDays` left at its default, the conversation is read anew); answer what they asked with one next step,
  the same working day; a fact only the user knows is a blank, never invented.
- Results: the user's own counts (mailbox, tool, CSV, pasted replies), never estimated. A rate counts only
  batches 7 days past their first email; younger ones show "counting". No rate under 10 sent. One change per batch between two passing versions, within one persona. While a test runs, send
  the version with more interested replies; a tie keeps the baseline.

**Deliver: "Results"**.

## Self-check (every draft)

- [ ] No title, tenure, headline or company description recited; the fact is tied to why the user writes.
- [ ] Fact in their row or brief, tense matching its date, under 6 months. Nothing invented, no figure
      without a source, no guess in quotation marks.
- [ ] Line one names their situation, not us; then who writes (name + trade noun, one clause); one offer from the user's trade, no
      proof in email 1, one yes/no question naming it. No call, slot, meeting or vague wish.
- [ ] No hedge, no guessed feeling, no thank-you or line that says nothing about them.
- [ ] Email 1 body 50 to 90 words, follow-ups under 50 (footer not counted), personal line 240 characters at most.
- [ ] Subject 1 to 5 words, no fake "Re:"/"Fwd:"; no buzzword; no link, image, attachment or tracking in email 1.
- [ ] Native-grade language per the voice card. French: vous unless the card says tu or the person wrote tu
      first; "Bonjour" capitalised with vous.
- [ ] Country footer on email 1 (`references/legal.md`); follow-ups carry the opt-out line only (US: full
      footer on every email).
- [ ] 4 emails at most per person; never the same email to one company in the same week; no 3 drafts
      share opening or shape (rotate the moment lines).

## What not to do

- Promise reply rates or quote open rates.
- Send to a guessed or unverified address.
- Write to anyone who asked to stop, on any channel, or anyone on HOLD.
