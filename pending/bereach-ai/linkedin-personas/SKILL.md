---
name: linkedin-personas
description: "Builds 2 to 4 persona cards with the user and puts each lead in one. Use before writing to a new list, or when messages sound generic or repeat the job title."
---

# Personas

The ICP (in the search plan) says which companies. A persona says which person inside them and what to say
to them: a role in a situation, never a person with a life. The title finds the card; the card writes the
message, never "I saw you are Head of X".

Blocks: **Persona cards v1** and **Who is who** on linkedin-outreach-method's Plan and personas
page (its "3 premiers messages" band comes from the v1 cards at once, via linkedin-messages), Who is who
again on Invitations to send; each its own page only when this skill runs alone. Before drawing a block,
read `references/artifacts.md` (its section).

## Step 1. Read what exists

- `bereach_memory_list`, `fullContent: true`, for `offering` and `user-profile`; the offering's "Personas"
  section is the starting point.
- Their website, CRM (if a connector is there) and documents (`references/sources.md`); inside
  linkedin-outreach-method, after its question round.
- The search plan, if `bereach_plan_searches` ran here: each group (a role in one segment) goes
  into the Found by of its card; groups that would get the same first message share one card, even across
  segments; roles the plan guessed end in `(guess)`.
- The account's untouched people, as linkedin-outreach-method split them (a few hundred per persona,
  never every row): their real titles shape Found by.
- What got replies, from linkedin-outreach-method (only with the user's yes): its "Their words" list seeds
  Pain, Objection and Their words. Never read the same conversations twice.

## Step 2. Draft the cards with the user

Asked in linkedin-outreach-method's one question round, only what Step 1 left empty or `(guess)`:
1. Your best 3 customers: who signed, their title, what happened just before the yes?
2. The "no" you hear most, and your answer to it?
3. What have you already offered a prospect (a sheet, a plan, a sample of your work), and from what price?

Before drafting, read `references/persona-card.md` (Core, Rules) and `references/frameworks.md` (Which card
field comes from which framework); the band names only a framework the cards visibly apply.

Draft 2 to 4 cards. Cards are short: a seller writes a message from them in one read. A line that is not the
user's words or a reply ends in `(guess)`. Get right:

- Proof: a real case in the user's words. Unnamed, it needs no consent; a named client waits for the yes.
  None given: "None yet", never a case Claude wrote, never a site or deck figure.
- Offer: only one the user really made (a message, their own words) or a prospect asked for. None: empty,
  the user is asked once; never a study, estimate, audit or map they have not offered.
- The objection answer and price: the user's words only (no service, speed or result they never stated),
  else an empty text field.

**Deliver: Persona cards v1**, provisional by design; an answer given later is saved and the block
republished in place.

## Step 3. Save the cards

- `bereach_memory_save`, `type: "offering"`, only on a change. It replaces the whole entry: the full
  existing text (or what they sell, from the question round) plus a `## Personas` section with every card
  and any validated templates.
- New titles or roles go to the next `bereach_plan_searches`; a Why now, Signal or Proof picks its door in
  linkedin-outreach-method's `references/search-doors.md`.

## Step 4. Put each lead in one persona

Before sorting, read `references/persona-card.md` (ICP, plan groups and cards; More: Not this persona).

Untouched people first, then each search's, from the row (title, company, `whyNow`); no profile data:
amber `pas de profil : N`. Keep on the row any fact settling the persona, dated (month and year).

- One persona per lead. Two fit: the one whose Why now window the dated `whyNow` falls in, or whose ICP the
  company is in, else `CHECK`. A batch rule for titles outside a card's Found by adds them to it on the
  same rule row; else they stay `CHECK`.
- `sure`: the title matches exactly one card's Found by and nothing puts the company outside its ICP. Enough to tag.
- `CHECK`: two cards fit with nothing to split them, or the company is outside the ICP. No tag, no message
  until the user picks; the others go on.
- Out of scope (student, intern, side project, the sender's own profile, team or company, too big) stays
  at the search step, never reappears. One added later: `HOLD`, no message; on the user's yes,
  `bereach_contact_update` with the list's `campaignId` and `lifecycleStage: "rejected"`.
- Tag: `bereach_contact_update`, all `contactIds` of one persona, `tags: { add: ["persona:<short-name>"] }`,
  one short name per persona everywhere.

Only when the user asks for a score: `bereach_check_fit` with the `campaignId`, `icp` as the plan's ICPs in
their words, `personas` as `"<short-name> (title, title, title)"` (3 titles at most). Tag from
`fit.persona`; it hides and blocks nobody; say its cost before and what it spent after.

**Deliver: Who is who**. Sure rows need no yes; open rows are held and asked on Invitations to send, never
a stop of their own. Its total is the count every later page reads.

## Step 5. Hand over to the messages

linkedin-messages writes one template per persona from Why now, Pain, Proof, Objection and Offer,
line 1 from the lead's brief (every person briefed before every message), else the moment
line, never their title or headline. A reply asking for something is evidence for the Offer.

## Step 6. Learn from results

After 7 days linkedin-outreach-method draws **Results** per persona (tag `persona:<short-name>`,
`bereach_inbox` for replies). Then, with the user, never on a partial read:

- A line changes only when 2 or more replies say the same, quoted; every change names its source (a reply,
  or "votre idée"). A new offer with no source is a question, never filled in.
- Confirmed lines become `seen in N replies`; contradicted ones are rewritten; an answer is asked again only
  when replies contradict it, and a new objection's answer is the user's.
- Nothing confirmed, fixed or merged under 10 invited.
- A change to Pain, Offer or the objection answer is queued as that persona's next test
  (linkedin-outreach-method's measuring order), never edited live.
- 0 replies on 8 or more first messages: the Why now check, then one plain change or a `pause`; the user picks.
- After a rename or merge: one `bereach_contact_update` per persona, `tags: { add: [new], remove: [old] }`,
  then save again (Step 3).

**Deliver: Persona cards v2**, only the changed lines, one decision.

## Never

- Invent a pain, quote, proof, offer, tool, date or answer the user did not give and no reply or brief shows.
- Quote a named customer before the user says they may be cited.
- Use age, gender, hobbies, school, personality type or a photo to sort or to write.
- Say where the data comes from or how people were found.
