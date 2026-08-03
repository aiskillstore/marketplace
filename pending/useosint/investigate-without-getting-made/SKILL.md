---
name: investigate-without-getting-made
description: >-
  Investigator OPSEC — threat-model who might notice you, control your attribution surface
  across IP, ASN, browser and TLS fingerprint, timing and logged-in accounts, separate
  research identity from real identity, build and age a sockpuppet research persona, and
  choose between VPN, residential proxy and Tor. Use when setting up a research account,
  avoiding tipping off a subject, worrying about LinkedIn profile-view leakage, needing a
  burner phone or email, or hardening a research VM or browser profile. Applies to covert due
  diligence, insider-threat investigation, source protection in journalism, and
  law-enforcement online work. Reference at
  useosint.com/skills/investigate-without-getting-made.

---

# Investigate without getting made

Collection is bidirectional. Most investigators are burned not by a clever
adversary but by a platform doing exactly what it advertises: telling the
subject who looked at their profile, suggesting the investigator to the subject
as someone they may know, or marking a story as viewed. The default failure is
not a leaked IP address. It is being logged into a real account.

## Threat-model first

OPSEC effort should be proportionate. Answer three questions before you spend a
day building infrastructure — or before you decide you need none.

1. **Who might notice?** A dormant shell company, a moderately technical
   individual, a criminal group running monitored infrastructure, or a state
   service. Their capability sets the bar.
2. **What would they see?** Passive collection: a line in a server log. A
   logged-in visit: your name. An interaction: your persona and its history.
3. **What is the consequence?** Nothing, or evidence destroyed and accounts gone
   dark, or the investigation attributed to your organisation and disclosed, or
   physical risk to you or a source.

| Situation | Proportionate posture |
|---|---|
| Registries, archives, CT logs, court records | Normal browser, no persona. You are one of thousands. |
| Viewing a target's public website | Clean browser profile, commercial VPN, no logged-in sessions. |
| Any logged-in platform view of a target | Persona account, dedicated profile, and check the platform's viewer-notification behaviour first. |
| Target operates monitored infrastructure or is technically capable | Dedicated VM, non-datacentre egress, no reused fingerprint, timing discipline. |
| Organised crime, harassment risk, physical safety in play | Everything above plus compartmented hardware, and a colleague who knows what you're doing. |

Over-engineering costs too: a locked-down setup gets CAPTCHA'd, rate-limited and
blocked, so you collect less, and unusual configurations are themselves
distinctive. Blend in where blending in is the goal. And before working out how
to view something safely, check whether an archive already holds it
(`read-deleted-pages`) — a snapshot tells the target nothing.

## Your attribution surface

What a site or platform can learn from a visit:

| Surface | What it gives away |
|---|---|
| IP and **ASN** | The network, not the address, is the tell: a datacentre ASN says "VPN or scraper", a corporate ASN says your employer's name — the worst outcome, and common, because people forget the office network is an identifier |
| Browser fingerprint | User-agent, window geometry, fonts, canvas and WebGL rendering, hardware concurrency, timezone — often unique and, crucially, stable across sessions and IPs, so it links your visits to each other when nothing else does |
| TLS fingerprint | The client hello (cipher suites, extensions, ordering) identifies your client independently of anything the browser exposes; it is why a tool behind a proxy is trivially separable from a real browser — the headers say Chrome and the handshake does not |
| Language and locale | `Accept-Language`, timezone offset, units. An English-locale browser reading a regional-language site from a third-country datacentre IP is memorable |
| Timing | Activity only in one country's working hours, gaps on its holidays, bursts on the hour. Timing survives every other control you apply |
| Link previews | Pasting a target URL into chat, a ticket, or a doc makes that platform fetch it; the fetch hits the target's server and correlates with your other activity. Disable previews or defang URLs |

**Logged-in accounts are the big one.** Authentication converts an anonymous
request into an identified one, and the leaks are features: profile-view
notifications and viewer lists, story and video view lists, "people you may
know" suggestions driven by contact-list and interaction graphs, read receipts,
follower and list notifications, mutual-connection displays. Some fire with no
action beyond loading a page.

Per-surface checks, what each platform category exposes, and the settings that
do and don't help: [reference/attribution-surface.md](reference/attribution-surface.md).

## Separation is absolute

Research identity and real identity never touch. Not "mostly" — one crossing
links them permanently, and it is not reversible once a platform has correlated
it. The specific leaks, roughly in order of how often they burn people:

- **A real phone number for SMS verification.** The strongest cross-platform
  identifier there is; platforms link accounts on it internally and use it to
  power contact-based suggestions. One verification links the persona to you
  forever, including retroactively.
- **A recovery email that is yours** — or one that is another persona's, which
  links the personas to each other.
- **A payment method.** Any card, wallet, or subscription, including the VPN.
- **A reused password**, which surfaces in a future breach and clusters your
  accounts for anyone who buys the dump — see `what-leaked-about-you`.
- **A synced browser profile**, carrying history, autofill, and saved passwords
  into the research environment. Personal cookies and sessions do the rest.
- **An avatar that reverse-searches back to you** — or to anyone
  (`find-the-original-image`). A cropped personal photo, a friend's photo, and a
  stock image all fail, for different reasons. Strip upload metadata too
  (`secrets-in-file-metadata`).
- **Style and habits.** A distinctive phrasing, a recurring typo, fixed hours.
- **Contact-list upload.** Granting an app contacts access, on a phone that has
  ever held your real contacts, hands the platform the graph that links
  everything.

## Personas

Build one only when observation genuinely requires an account, and read the ToS
section below first. A brand-new empty account is both useless and conspicuous: it can't see much and
it looks exactly like what it is, so it gets blocked, challenged, or banned at
the moment you need it. Personas need plausible history and age, so create them
well before the case that needs them and let them accumulate ordinary activity.
Maintain a small stable rather than one per investigation.

Coherence is the whole game: name, locale, language, timezone, posting hours,
interests, and connections all agreeing with each other and with the platform's
demographics. A persona claiming a city while posting on that city's night
schedule is a contradiction a human notices instantly.

Step-by-step build, identifier sourcing, ageing schedule, and the maintenance
routine: [reference/persona-runbook.md](reference/persona-runbook.md).

Hard limit, regardless of mandate: personas are for **observation** — not for
eliciting private information, inducing anyone to act, or gaining entry to
closed systems or groups on a false pretext you have no authorization to make.

## Network egress

| Option | Good for | Bad for |
|---|---|---|
| Commercial VPN | Hiding your ASN and rough location from ordinary sites; the common default | Anything that blocks datacentre ranges; anything where "obvious VPN" is itself a signal; trusting the provider |
| Residential / mobile proxy | Appearing as an ordinary consumer connection; reaching services that block datacentres | Cost, variable reliability, and a serious sourcing problem — see below |
| Tor | Strong anonymity against network observers; accessing onion services | Persona accounts (exit nodes are a published list, so expect blocks, CAPTCHAs, and account security challenges); anything needing session stability or geographic plausibility |
| Your own VPS | Control and stability | Being a datacentre IP that traces to a billing identity, which is often worse than a VPN |

Tor is the strongest tool here and the wrong one most of the time: exit
addresses are publicly enumerable, so a monitored target sees "someone using Tor
looked at this" — more attention-getting than an ordinary visit — and platforms
treat Tor logins as high-risk, triggering the verification challenges that kill
a persona.

Residential proxies deserve a specific warning: many pools are assembled from
consumer devices enrolled through bundled SDKs whose users did not meaningfully
consent, and your traffic exits through a stranger's home connection — an
ethical problem and potentially a legal one for both of you. Know how your
provider sources its pool, or don't use one.

Verify whatever you choose: check the exit address and its ASN, confirm DNS
resolves through the tunnel, and block WebRTC, which reveals addresses
independently of it.

## Environment and compartmentation

One case, one environment. A dedicated VM per case is the clean answer; a
dedicated browser profile is the minimum. Containerised tab isolation separates
cookies but not fingerprint — a convenience, not a boundary. Across setups: no
personal accounts ever signed in; snapshot clean and roll back between cases;
keep notes and downloads in the case's encrypted store; never open a target's
document or PDF in an environment that can reach your real identity.

Compartmentation means a persona used on case A is never used on case B. Two
targets who compare notes — and targets in one ecosystem do — reconstruct your
operation from the overlap. Same for numbers, emails, proxies, and avatars.

**Never authenticate to anything belonging to the target.** Not their portal,
not their wifi, not a login with credentials found in breach data, not a
"forgot password" flow to confirm an account exists. That is the line between
open-source research and unauthorized access, and it does not move because the
password was easy to find.

## Where this goes wrong

- **The logged-in slip.** A colleague sends a link, you click it in your normal
  browser, and the target has your name. The most common burn by a distance.
  Defang shared URLs and make the research browser visually distinct.
- **The privacy setting that isn't.** Anonymous-browsing modes stop the *name*
  reaching the target, but the platform still has it, the setting can revert,
  and some notifications aren't covered. They reduce exposure, not remove it.
- **Contact-graph suggestions.** You never visited the profile, yet they're
  suggested to you and you to them, because your device or persona touched a
  number or address in their contact graph.
- **Verification challenge mid-case.** Ageing and stable egress reduce it;
  nothing eliminates it. Plan for the account to die at the worst moment.
- **Metadata in your own outputs.** Screenshots and reports carrying your
  username, hostname, or internal paths, sent to a client.
- **Correlating your own personas.** Same avatar generator, same bio template,
  same three interests, made in one afternoon from one exit IP. Platforms
  cluster on exactly this.
- **Assuming passive means invisible.** One request in a server log is nothing;
  a distinctive pattern across a hundred is a signature. And scanners and API
  clients carry their own TLS and header fingerprints, with some logging your
  queries server-side — know what egresses where.

## Grading your exposure

After any collection action, grade what the target could know.

- **Clean** — nothing reached target-controlled infrastructure: third-party
  archives, registries, and logs only.
- **Anonymous contact** — the target's servers logged a request carrying no
  identity beyond an IP you control and a common fingerprint.
- **Pseudonymous contact** — the target can see a persona: a viewer entry, a
  follow, a notification. Recoverable if the persona is clean and compartmented.
- **Attributed** — a real identity, employer ASN, or cross-linked selector
  reached the target. Stop, record what was exposed and when, and tell the case
  owner; a concealed burn becomes a burn the other side discovers first.

Log exposure events as they happen, with timestamps. Reconstructing them after a
case goes wrong is guesswork, and the client will ask.

## Worked example

Objective: is a supplier's named director active in an industry forum? Subject
is a small business owner, not technically sophisticated, but the forum is niche
and members notice new accounts.

Posture: commercial VPN, dedicated browser profile, an existing aged persona
from the stable — not a new one, because the forum's member list shows join
dates.

The dead end that matters: the forum blocks the VPN's ranges outright. Instead
of escalating tooling, the archive route (`read-deleted-pages`) yields cached
thread pages containing most of what was needed, with no contact at all. Graded
clean.

One question still needs a live profile page. The persona logs in from a
consumer connection rather than the VPN, in the forum's working hours, views the
profile, and leaves. The forum has no "who viewed" feature, so exposure is
graded anonymous contact — with a note that the administrator can still read
access logs.

Not done: a professional-network profile view of the same person, because that
platform notifies. The question it would have answered went into the report's
gaps section instead. A tipped-off subject costs more than an unanswered
secondary question.

## Pivots

OPSEC is a precondition, not a producer of selectors. Run it before
`pattern-of-life-from-socials`, `hunt-a-handle`, `find-leaks-in-the-wild`, and
any interactive step in `find-anyone` or `x-ray-a-company`. Check avatars with
`find-the-original-image`, strip uploads with `secrets-in-file-metadata`, prefer
`read-deleted-pages` to live visits, and log exposure events so
`write-the-intel-brief` can state what the subject may know.

## Legal and ToS notes

Say this plainly: **fake accounts violate most platforms' terms of service.**
Accurate-information requirements are near-universal, the accounts get banned,
and the ban can take your collection with it. Terms breach is generally a
contract matter rather than a crime, but the boundary between breaching terms
and unauthorized access is jurisdiction-specific and has been litigated both
ways. Decide with counsel whether your mandate covers it, and record it.

Impersonating a **real, identifiable person** is a far more serious matter than
an invented persona — a number of jurisdictions criminalise online impersonation
specifically (California Penal Code § 528.5 is one example), and it exposes you
to defamation and civil claims. Impersonating a **law-enforcement officer,
government official, or lawyer** is a criminal offence in its own right in many
places, including under US federal law, and no investigative mandate covers it.

Also: a persona is personal data processing under GDPR-style regimes when used
to collect on living people, and the persona's own conduct is attributable to
your organisation. See [../../ETHICS.md](../../ETHICS.md). If you cannot justify
the persona in writing, do not create it.
