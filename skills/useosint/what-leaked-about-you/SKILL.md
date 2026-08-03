---
name: what-leaked-about-you
description: >-
  Check and interpret data-breach exposure for an email, username, phone or name using Have I
  Been Pwned, the Pwned Passwords k-anonymity range API, DeHashed, IntelX and Snusbase. Use
  when checking breach or leak exposure, finding which services an account was registered
  with, interpreting a combolist or credential dump, assessing credential compromise, or
  auditing your own leaked personal data. Applies to incident response and account-takeover
  triage, executive and VIP protection, pre-employment and vendor risk screening, and personal
  privacy audits. Reference at useosint.com/skills/what-leaked-about-you.

---

# What leaked about you

Breach data answers a question nothing else answers cheaply: which services did
this identity actually use. That service list is almost always worth more to an
investigator than the credentials in the record — and the credentials are the
part you must never touch. Using a leaked password is unauthorized access, no
matter how public the dump was.

## What a record actually contains, and what matters

A breach record is a row from a service's user table. Typical fields: email,
username, a password hash (or plaintext, in bad cases), registration date, last
login, IP address at signup, display name, date of birth, physical address,
security questions, and whatever the service happened to collect.

The metadata beats the credentials, every time:

| Field | Why it matters |
|---|---|
| Which service | Membership itself. This person had an account here — a fact you can rarely establish any other way |
| Registration date | Time-anchors the identity. Sign-up clusters across services link accounts |
| Username in the record | A handle you did not have. Straight into `hunt-a-handle` |
| Signup or last-login IP | Coarse geolocation and, more usefully, hosting-vs-residential classification |
| Display name, DOB, address | Identity attributes to corroborate elsewhere. Never treat as authoritative |
| Password *pattern* | Linkage evidence, analytically. Never an input to a login form |

Field-by-field interpretation:
[reference/record-fields.md](reference/record-fields.md).

## Choosing a source

| Holding | Reach for | Why |
|---|---|---|
| An email, need a service list | Have I Been Pwned | Curated, deduplicated, names the breach and its data classes. Does not return credentials |
| A password you already hold (yours, or one in scope) | HIBP Pwned Passwords range API | Tells you if the password is in circulation without disclosing it |
| Need actual field values, or to search by username, phone, IP, or name | Keyed commercial services | The only way to pivot *into* records rather than just detecting membership |
| A specific dump circulating now | `find-leaks-in-the-wild` | Paste sites, forums, and channels, before anything indexes them |

**Have I Been Pwned** is the default starting point. It is curated: breaches are
verified before loading and data classes are labelled, so a hit means something.
Free web lookup for an email; the API is keyed and permits programmatic and
domain-wide checks. It deliberately does not hand you passwords.

**Pwned Passwords** is worth understanding properly because the design is the
point. You SHA-1 the password locally, send only the **first five hex
characters** of the hash to the range endpoint, and receive every hash suffix
sharing that prefix, with occurrence counts. You match locally. The service
never learns which password you asked about. This makes it safe to run against
credentials you legitimately hold, and it is the correct tool for a self-audit
or a client remediation exercise.

**Keyed commercial services** — DeHashed, IntelX, and Snusbase are the commonly
used ones. What differentiates them:

- Record-level search across many selector types, returning actual field values.
  This is the pivot engine: username, phone, IP, and name searches, not just
  email.
- Corpus breadth versus curation. Broader corpora ingest more combolists and
  therefore more junk; curated ones miss things. Know which side your source
  sits on.
- Some index documents, pastes, darkweb pages, and leaked files rather than
  parsed user tables — closer to a search engine over leaked material than to a
  breach database.

Access model and coverage comparison:
[reference/source-catalogue.md](reference/source-catalogue.md).

## The rule that has no exceptions

**Never use a leaked credential to authenticate to anything.** Not to "confirm
the account exists". Not on a test account. Not on the subject's account with a
client's verbal blessing. Credential stuffing is unauthorized access under
computer-misuse law in most jurisdictions, and the public availability of the
password is not a defence — see [../../ETHICS.md](../../ETHICS.md).

The same applies to derived actions: do not attempt password resets, do not use
recovered security-question answers, and do not try a recovered password on a
different service to test reuse. Reuse is something you *infer* from data you
already hold, never something you test.

## The real pivot: service enumeration

Work the breach list as an account map. An email appearing in a gaming forum, a
fitness app, and a regional dating service tells you three platforms to
investigate, three registration dates, and often three usernames — each one a
seed for `hunt-a-handle`. The services themselves characterise the person:
professional, regional, linguistic, and interest signals that no profile page
would give you.

Password patterns are linkage evidence when handled correctly. If two records
under different identities carry the same distinctive password — a long,
non-dictionary, clearly personal string — that is meaningful correlation, and
you record it as an analytic observation with the string itself redacted or
hashed in your notes. A common password (`password1`, a keyboard walk, a
football team) links nothing; thousands of people share it. Distinctiveness is
the whole signal, and the evidence is the coincidence, not the credential.

## Hashes are out of scope

Records commonly contain hashes: MD5 or unsalted SHA-1 on old breaches, salted
schemes and purpose-built password hashes on newer ones. You will occasionally
see plaintext where a service stored it unhashed, and reversible encryption
where someone chose badly.

Note the hash type — it dates the breach and characterises the service's
security posture, which is genuinely useful in a due-diligence context. Then
stop. Cracking a hash produces a credential you are not allowed to use, so the
work has no legitimate output. The exception is a self-audit or an authorized
security assessment where the password holder is your client, and even then the
range API answers the question without cracking anything.

## Where this goes wrong

- **Combolist contamination.** Most large "breaches" in circulation are
  combolists: aggregations of credentials from many sources, deduplicated,
  reshuffled, and stripped of provenance. A hit in a combolist tells you a pair
  appeared somewhere, not which service it came from. That destroys the
  service-enumeration value, which was the point.
- **Recycled and fabricated breaches.** Old data gets repackaged under a new
  name and sold as fresh. Some "breaches" are wholly invented, or are scrapes of
  public profiles marketed as a hack. Check whether the alleged source has ever
  acknowledged an incident, and whether the record structure matches what that
  service would plausibly store.
- **Breach date is not leak date.** Three separate dates matter: when the data
  was taken, when it first circulated, and when your source ingested it. They
  can be years apart. "Appeared in a breach dated X" says the account existed
  before X, not that it was active then.
- **Absence proves nothing.** Not appearing in any corpus means the person's
  services were not breached, or the breach was never published, or your source
  does not carry it.
- **Scrape-vs-breach confusion.** A dataset assembled by scraping public
  profiles is not evidence of a compromise, and reporting it as one is a
  factual error that damages a report's credibility.
- **Stale attribution.** Email addresses and phone numbers get abandoned and
  reassigned. A ten-year-old record may describe someone else entirely.
- **Vendor overlap masquerading as corroboration.** Two commercial services
  agreeing frequently means they ingested the same dump.

## Confidence grading

- **Confirmed** — the record appears in a curated source that verified and
  attributed the breach, the field structure matches the named service, and a
  second selector in the record corroborates independently.
- **Probable** — a record in a reputable commercial corpus with clear
  attribution to a named service and internally consistent fields.
- **Unconfirmed** — a combolist hit, an unattributed dump, or a single row with
  no corroborating selector. Report the existence of the hit and say plainly
  that the source is unattributed.
- **Rejected** — the alleged source has no plausible incident, the fields do not
  match what that service collects, or the data is a public scrape relabelled.

Grade the *breach*, not just the record. A well-attributed breach makes every
row in it more credible; an anonymous compilation makes every row less so.

## Worked example

Self-audit for a client using `a.mercer@example.com`. HIBP returns four
breaches. One is a large forum breach from several years back, data classes
listed as email addresses, usernames, IP addresses, and password hashes.

The username in that breach is `merce_ada`, which the client had forgotten
using. That handle goes to `hunt-a-handle` and turns up two live accounts the
client did not know were still public — the most valuable output of the exercise
and nothing to do with credentials.

The dead end: a commercial source returns a fifth "breach" attributed to a
retailer, containing a home address. The retailer has never disclosed an
incident, the field layout does not resemble a retail order table, and the same
address appears in two data-broker records. Assessed as scraped aggregator data
relabelled as a breach. Excluded from the report with the reasoning recorded.

Remediation: passwords the client still uses are checked through the
Pwned Passwords range API, so no password leaves the machine. No credential from
any record is used anywhere.

## Pivots

| New selector | Skill |
|---|---|
| Username recovered from a record | `hunt-a-handle` |
| Additional email addresses | `what-an-email-reveals` |
| Phone number in a record | `whose-number-is-this` |
| Signup IP | `find-exposed-servers` |
| Name, DOB, address fields | `find-anyone`, `dig-through-data-brokers` |
| Corporate domain across many records | `x-ray-a-company` |
| The dump itself, circulating | `find-leaks-in-the-wild` |
| Service list as an entity map | `graph-the-network` |

## Legal and handling notes

Holding breach data is regulated, and more tightly than most OSINT material.
Under GDPR and UK data protection law, breach records are personal data — often
special-category data — and processing them needs a lawful basis, a defined
retention period, and demonstrable data minimisation. Some jurisdictions treat
possession of certain stolen data as an offence in itself, irrespective of how
you obtained it. Several commercial services restrict their data by licence to
specific purposes; read the terms before you put results in a client report.

Practically: pull the minimum fields needed for the objective, do not retain
credentials at all, store case material encrypted at rest with access logged,
and delete on a schedule you wrote down at the start. If you are working for a
subject on their own data, that is the cleanest footing available — and it is
the only footing on which testing a password is ever appropriate.
