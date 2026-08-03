# Research persona runbook

Read the ToS and legal section of the parent skill before building anything.
Personas breach most platforms' terms; that is a decision to make deliberately,
in writing, with whoever owns the risk.

Build personas **before** you need them. A persona created for today's case is
a persona that is too young for today's case.

## 0. Authorization record

Write, and keep with the case file: why an account is necessary, what it will
and will not do, which platforms, who approved it, and the retirement date.
One paragraph. If it can't be written, don't build the persona.

## 1. Legend

Decide the whole story before creating anything, and write it down — you will
need to answer questions consistently months later.

- Name: common in the claimed locale, unremarkable, and — check this — not a
  real identifiable person with a public presence. Invented persona: acceptable.
  Impersonating a real individual: a different legal category entirely.
- Location, and a plausible reason to be there.
- Age bracket, occupation, employer type (never a specific real small employer
  whose staff know each other).
- Interests that justify following the accounts and joining the groups the case
  requires — the persona's plausibility comes from the coherence of its
  interests, not from its biography text.
- Language register: the persona's writing should match its claimed background.
  Machine-translated text in a claimed native language is obvious.
- What the persona will never do: contact anyone, request access, comment,
  elicit.

## 2. Identifiers

Establish these in this order, each isolated from you and from every other
persona.

| Identifier | Guidance |
|---|---|
| Environment | Build the persona from the same environment and egress it will always be used from. Creation-time IP and fingerprint are recorded and later compared. |
| Email | Provider that does not demand a phone number to register. One address per persona. Never a recovery address for another persona. |
| Phone | The hardest problem. Free online SMS-receive numbers are shared, are already registered on major platforms, and are widely blocklisted. VoIP numbers are frequently rejected. A dedicated prepaid SIM in a device that has never held your real SIM or contacts is the reliable option — and never your real number, not once, not "just to get through verification". |
| Payment | Only where unavoidable. Prepaid instrument, never a personal card, never a card shared between personas. |
| Avatar | Do not use a real person's photo — that is impersonation and it harms an uninvolved person. Synthetic faces avoid reverse-image hits but carry generator artefacts (fixed eye placement, distorted backgrounds, mangled jewellery and teeth) and are increasingly detected. Where the platform permits it, a non-face image is safer and less interesting to everyone. Whatever you choose, reverse-search it first with `find-the-original-image`, and strip its metadata with `secrets-in-file-metadata`. |
| Password | Unique, generated, stored in the case's vault. Reuse across personas clusters them the moment any one appears in a dump. |

Every identifier gets recorded in the persona's file with its creation date and
where it was used. An untracked persona is one you cannot safely retire.

## 3. Registration

- Register from the persona's normal egress. Registering over Tor or a flagged
  datacentre range invites immediate verification.
- Complete the profile the way a real, slightly lazy user would: some fields
  filled, some blank. Fully populated profiles look manufactured.
- Set locale, language, and timezone to match the legend.
- Turn off contact syncing and contact upload. Never grant contacts access.
- Where the platform offers visibility controls, restrict the persona's own
  profile — a persona with a bare public profile draws less scrutiny than one
  that appears to be nothing at all.
- Do not create several personas in one session from one address. Platforms
  cluster on registration-time signals, and one ban then takes the whole batch.

## 4. Ageing

A persona becomes usable through unremarkable activity over time, not through
volume. There is no minimum-days rule worth trusting — what matters is that the
account has a history that predates its purpose, and that the history looks like
a person's.

- Log in irregularly, in the persona's claimed waking hours, from the same
  egress and device fingerprint.
- Follow mainstream, high-follower accounts consistent with the legend, then
  gradually narrower ones. Following only accounts relevant to your case is the
  clearest possible signal of purpose.
- Accumulate a small amount of low-risk activity: saved posts, joined public
  groups, an occasional innocuous reaction.
- Let it acquire a few incidental connections organically. Do not solicit them.
- Keep a log of every session, so the persona's own pattern-of-life stays
  consistent when a different analyst uses it.

Maintain a small stable of aged personas across the platforms you routinely
work. This is a standing cost, not per-case work.

## 5. Operating

- One persona, one case. Compartmentation is what limits the damage of a burn.
- Same environment, same egress, every session. Consistency beats concealment
  for account survival — the security systems you are up against are looking for
  *change*.
- Observe only. No messages, no follows of the target, no comments, no reactions
  on target content. Reactions are notifications.
- Before viewing anything the target controls, run the pre-action check in the
  attribution-surface reference.
- Never use a persona to access closed systems, request access on a false
  pretext you have no authorization to make, or elicit information from people.
- Log what the persona did, when, and what it saw, and archive the pages via
  `read-deleted-pages` — the persona's access may not survive to be re-checked.

## 6. Failure modes

| Symptom | Meaning | Response |
|---|---|---|
| Verification challenge (phone, ID, selfie) | The account is flagged | Do not feed it real identifiers. Assume the account is finished. |
| Sudden CAPTCHA on every action | Egress reputation or behaviour flagged | Stop for the session. Do not switch IPs mid-session to escape it — that confirms the pattern. |
| Shadow restrictions (content not visible to others) | Partially actioned | Fine for observation; note that the account's own visibility is unreliable. |
| Suspension | Burned | Do not appeal with real identity or documents. Retire it. |
| Target reacts to the persona | Noticed | Stop all persona activity on the case, log the exposure, tell the case owner. |

## 7. Retirement

Retire personas that were challenged, that touched a case that went adversarial,
or that were used across cases by mistake. Retirement means: stop using it,
record the retirement date and reason, keep the identifier record so a future
analyst does not reuse a burned number or address, and delete the persona's
collected data under the case's retention rules in `write-the-intel-brief`.

Do not resurrect a retired persona because it is conveniently aged. That is how
one burn becomes two.
