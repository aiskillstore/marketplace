# Interpreting a breach record, field by field

A record is a row from someone's user table, dumped and possibly mangled several
times since. Read it as a database row with unknown provenance, not as a
statement of fact.

## Identity fields

**Email address.** The join key for most breach work. Normalise before comparing
— lowercase, and for providers that ignore them, strip dots and `+tags`, so
variants collapse to one mailbox. Two records that look like different people
are often one. A corporate address in a record also dates an employment
relationship, which is frequently more useful than the account itself.

**Username.** Often the highest-value field in the row, because it is a selector
you did not have. Feed it to `hunt-a-handle`. A username from an old breach is
particularly good: it predates the subject's current opsec habits.

**Display name / real name.** Self-declared at signup, unverified, and sometimes
deliberately false. Corroborate before using. Consistency of a distinctive name
across several unrelated breaches is a genuine signal.

**Date of birth.** Frequently fake, especially where the service had an age gate
— January 1st and round years are heavily over-represented. A consistent DOB
across independent breaches is worth more than any single instance.

**Physical address and phone.** Treat as historical. Both go stale fast; addresses
change and numbers get recycled. Pivot the phone to `whose-number-is-this`, but
carry the date forward with it.

## Temporal fields

**Registration / signup date.** The most under-used field in breach data. It
places the identity in time, bounds when the person first used that service, and
— across several breaches — reveals sign-up clusters. People create accounts in
bursts: a new job, a new device, a new interest. Clusters across services are
correlation evidence for the accounts belonging to one person.

**Last login / last activity.** Tells you whether the account was live at the
time of the breach, which distinguishes an abandoned account from an active one.

**The three dates you must not conflate:**

| Date | Meaning |
|---|---|
| Breach date | When the data was taken from the service |
| Disclosure / leak date | When it first circulated publicly |
| Ingestion date | When your source loaded it |

They are often years apart. A record from a breach dated X proves the account
existed before X. It does not prove activity at X, and it says nothing about
today.

## Network fields

**Signup IP / last-login IP.** Coarse geolocation at best, and often wrong for
mobile and corporate networks. The higher-value read is classification: is this
a residential ISP, a mobile carrier, a hosting provider, or a known VPN or Tor
exit? A hosting-provider IP at signup suggests automation or deliberate
concealment. Infrastructure detail via `find-exposed-servers`.

Two accounts sharing an unusual IP in the same time window is meaningful
correlation. Two accounts sharing a carrier-grade NAT address is not.

## Credential fields

Note the type, then leave them alone.

| Storage seen | What it tells you |
|---|---|
| Plaintext | The service stored passwords unhashed. Severe negligence, and a strong signal about the service's era and engineering quality |
| Unsalted MD5 or SHA-1 | Old, weak, and trivially attacked at scale. Common in older breaches |
| Salted MD5 / SHA-family | Better, still not password-appropriate |
| Purpose-built password hashing (bcrypt, scrypt, Argon2 family, PBKDF2) | The service did it correctly. Practically, the passwords in that breach did not enter circulation en masse |
| Reversible encryption | Someone chose encryption where they needed hashing. Everything is recoverable by whoever holds the key |

The hash type is legitimate reporting content: it characterises the breached
service's security posture, and it explains why a given breach did or did not
produce a usable credential corpus.

Cracking is out of scope. It produces a credential you may not use, so there is
no lawful output — except in an authorized assessment where the password holder
is your client, and even then the k-anonymity range API answers the question
without recovering anything.

**Password patterns as analysis, never as input.** Where plaintext is present in
material you legitimately hold, the *shape* of a password is evidence: a
distinctive non-dictionary string reused across two records under different
identities is real linkage. Record the observation, redact or hash the string in
your notes, and never type it into a login form. A common password links
nothing — the signal is entirely in its distinctiveness.

**Security questions and answers** are, in practice, permanent personal facts:
mother's maiden name, first school, first pet. They frequently corroborate
identity attributes found elsewhere, and they are exactly the data an attacker
needs. Handle as the most sensitive field in the row, and do not use them for
account recovery under any circumstances.

## Structural and provenance fields

**Source / breach name.** The most important field in the whole record. If the
row cannot be attributed to a named service, you have a credential pair and
nothing else — no registration fact, no date, no pivot. Combolist rows are
exactly this, which is why they are worth so much less than they appear.

**Field layout.** A quick authenticity check: does the column set match what
that service would plausibly collect? A retailer's dump with no order data, or
a forum dump carrying home addresses, is a reason to doubt the attribution.

**Duplicates and near-duplicates.** The same identity recurring across dumps
usually means one leak reprocessed, not several incidents. Deduplicate before
counting anything, and never report a count of "breaches" without checking for
this.

## Recording

Extract only the fields the objective requires. Do not copy credential fields
into case notes at all. Record, for every row: source name, source's claimed
breach date, the service it is attributed to, which vendor you retrieved it
from, and retrieval date. Without provenance, a record is not evidence — and
without provenance you cannot defend holding it.
