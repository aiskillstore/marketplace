# Breach source catalogue

Sources differ along four axes that actually change your answer: what you can
search *by*, what you get *back*, how the corpus is curated, and what the access
and licence terms permit. Pick on those, not on marketing.

Services and their terms change. Verify access model and licensing before you
rely on a result in a deliverable.

## The axes

**Searchable selectors.** Email-only lookup answers "was this address exposed".
Multi-selector search — username, phone, name, IP, domain — is what lets you
pivot *into* records from something other than an email, and that is usually
where the investigative value is.

**Returned detail.** Membership-only sources tell you which breach an identity
appears in and which data classes it contained. Record-level sources return
field values. Membership is enough for service enumeration; record-level is
needed for identity attribute recovery.

**Curation.** Curated corpora verify and attribute breaches before loading them,
which makes a hit meaningful and a miss more informative. Aggregating corpora
ingest anything, including combolists with no provenance — higher recall, much
lower precision, and often no reliable answer to "which service did this come
from".

**Access and licence.** Free web lookup, keyed API, subscription, or
purpose-restricted licence. Some licences prohibit use in employment,
tenancy, or credit decisions, or require you to be an accredited investigator.
Read them before results reach a client.

## Have I Been Pwned

The default first stop, and the only source in wide use that is deliberately
conservative about what it returns.

- Verifies and attributes breaches before loading them, and labels each with the
  **data classes** it contained (email addresses, passwords, IP addresses, dates
  of birth, and so on). Data classes are the single most useful metadata field
  in breach work: they tell you what to look for before you go looking.
- Distinguishes fully public breaches from **sensitive** ones (where mere
  membership is damaging) and from **unverified** dumps, which are flagged as
  such. Respect that distinction in reporting.
- Free web lookup for a single email. The API is keyed, and supports
  programmatic lookup and verified domain-wide searches by the domain owner —
  the correct route for an organisational self-audit.
- Does **not** return passwords or record field values. That is a design choice,
  not a gap.
- Also indexes pastes, which surfaces exposure that never became a named breach.

## Pwned Passwords and k-anonymity

A separate service, and the mechanism deserves understanding because it is the
model for how this kind of lookup should be built.

You hash the password with SHA-1 locally and send only the **first five hex
characters** of the hash to the range endpoint. The service returns every hash
suffix in its corpus beginning with that prefix, along with how many times each
has been seen. You compare locally.

The service therefore never learns the password, never learns the full hash, and
cannot tell which of the returned candidates you were interested in — the
"k-anonymity" property. Consequences for practice:

- It is safe to run against credentials you legitimately hold. This is the right
  tool for self-audit and client remediation.
- The occurrence count is a usefulness signal: a password seen many times is
  common and links nothing; a password seen once or twice is distinctive.
- It answers "is this password in circulation", not "is this password on this
  account". It is not an account check.
- No credential is transmitted, but you are still handling a live password
  locally. Do not log it, and do not keep it.

## Commercial record-level services

Used across the industry; keyed and paid. Named here as current implementations
of a capability, not as endorsements.

| Service | Characteristic strength |
|---|---|
| DeHashed | Broad multi-selector record search — email, username, name, phone, IP, address, hash — returning field values. The usual choice when you need to pivot from a non-email selector into records |
| IntelX | Indexes leaked *material* rather than only parsed user tables: documents, pastes, darkweb pages, historical captures. Closer to a search engine over leaked and obscure sources, with a selector-based query model |
| Snusbase | Fast search across an aggregated breach corpus with hash and password-field querying, oriented toward record retrieval |

Practical cautions for all of them:

- **Overlap is not corroboration.** Vendors ingest the same public dumps. Two
  services agreeing usually means one upstream source.
- **Provenance quality varies per record**, not per vendor. A single service
  will hold both well-attributed breaches and anonymous combolists. Check the
  attribution on the specific record.
- **Query logging.** Your searches are logged by the vendor. Assume every
  selector you look up is retained, and consider what that means for a sensitive
  case.
- **Licence restrictions** frequently prohibit exactly the downstream uses
  clients want. Check before promising anything.

## Adjacent sources

- Paste sites, forums, and messaging channels carry dumps before any indexer has
  them, and carry material that never becomes a named breach — use
  `find-leaks-in-the-wild`.
- Data-broker aggregators are a *different* thing entirely: compiled from public
  records and commercial data, not from a compromise. Useful, but never report
  them as breach exposure. Use `dig-through-data-brokers`.
- Some national CERTs and regulators publish breach notifications naming the
  incident, date, and affected data categories. Authoritative attribution when
  it exists, and worth checking before believing a dump's claimed origin.

## Choosing quickly

- Need a service list from an email: HIBP.
- Need to know if a password you hold is circulating: Pwned Passwords range API.
- Need to search by username, phone, or name: a commercial record-level service.
- Need to know whether a claimed breach is real: the alleged victim's own
  disclosure, then a regulator notification, then curated-source attribution —
  in that order.
- Need something circulating right now: `find-leaks-in-the-wild`.
