# Attribution surface checklist

Run the setup section once per environment and the pre-action section before
every action that touches something the target controls. Platform behaviour
changes; the mechanisms below do not, so verify the current behaviour of any
specific platform before relying on it.

## Environment setup

- [ ] Dedicated VM or, at minimum, a dedicated browser profile for this case
- [ ] No personal accounts signed in anywhere in the environment, including the
      browser itself (browser sync carries history, autofill, and passwords)
- [ ] Cookies, storage, and cache cleared or snapshot-restored from clean
- [ ] Password manager scoped to this case, not the personal vault
- [ ] Extensions minimised — each one is a fingerprint contributor, and some
      exfiltrate browsing history by design
- [ ] Timezone, locale, and `Accept-Language` set to something consistent with
      the persona's claimed location, not your own
- [ ] Link previews disabled in every tool where you paste target URLs (chat,
      ticketing, notes, docs)
- [ ] Screenshot and export tooling checked for embedded usernames and paths

## Network

- [ ] Exit IP verified, and its **ASN** checked — datacentre, residential, or
      corporate. The ASN is the giveaway, not the address.
- [ ] Corporate network confirmed *not* in use. An employer's ASN names your
      organisation.
- [ ] DNS resolving through the tunnel, not the local resolver
- [ ] WebRTC disabled or blocked
- [ ] IPv6 either tunnelled or disabled — a tunnel that only covers IPv4 leaks
- [ ] Egress stable for the session: mid-session IP or country changes trigger
      security challenges on persona accounts
- [ ] Kill-switch behaviour known: what happens to in-flight requests if the
      tunnel drops

## Browser and client fingerprint

- [ ] Stock, common browser and a common window size. Rare configurations are
      more identifying than default ones.
- [ ] Not simultaneously using a fingerprint-randomising setup and a persona
      account — randomisation between sessions looks like account compromise
- [ ] Automated tooling understood: HTTP client libraries and scanners have
      distinctive TLS handshakes and header ordering that do not match the
      user-agent they claim
- [ ] Anything with server-side components (hosted scanners, cloud transforms,
      URL-preview services) identified — those queries leave your control and
      may be logged or resold

## Timing

- [ ] Collection not confined to your own working hours, if that matters
- [ ] No obvious cadence (top of the hour, every weekday, never on your
      country's holidays)
- [ ] Bulk enumeration rate-limited and spread out; a burst is a signature and
      also gets you blocked

## Logged-in platform leakage

The category that burns people. Mechanisms, with the platform types where each
is common:

| Mechanism | Where it appears | What the target sees |
|---|---|---|
| Profile-view notification / viewer list | Professional networking, some dating and forum platforms | Your name and account, often with your job title |
| Story / status / ephemeral-post viewer list | Mainstream social, messaging status features | Your account in the viewer list |
| Live-video viewer list | Social video, streaming | Your account while watching |
| Read receipts and typing indicators | Messaging and DMs | That you read it and when |
| Online / last-seen presence | Messaging | Your activity pattern over time |
| Contact-graph suggestions | Social, messaging | You suggested to them as someone they may know |
| "Joined" notifications from phone-number matching | Messaging apps | Your new account announced to everyone holding that number |
| Follow / connection / list-add notification | Most social platforms | Direct and unambiguous |
| Mutual-connection display | Professional and social networks | Which of their contacts you share |
| Reaction, save, and bookmark events | Most social platforms | Accidental taps are notifications |
| Group-membership visibility | Forums, chat platforms, professional groups | Your persona in the member list |

Before any logged-in view, answer: does this platform notify on view; does it
list viewers; can the account holder see analytics that include me; will my
persona be suggested to them afterwards. If you cannot answer, test on an
account you control before touching the target.

Privacy or anonymous-browsing settings reduce the *name* shown, not the fact of
the visit or the platform's own record. They are also easy to lose — a session
reset or a client update can revert them, and they usually cost you the
equivalent feature in return. Never treat one as a boundary.

## Contact-list and identifier hygiene

- [ ] No mobile app in the research environment has been granted contacts access
- [ ] The persona's phone number has never been in your real contacts, or in the
      contacts of anyone connected to you
- [ ] Persona email addresses never used as recovery addresses for each other
- [ ] Persona numbers never used to verify a second persona
- [ ] No payment instrument shared between personas, or with you
- [ ] Persona avatar checked with `find-the-original-image` and confirmed not to
      match a real person or a stock library
- [ ] Uploaded files stripped of metadata (`secrets-in-file-metadata`)

## Pre-action check

Run these four before every action that touches target infrastructure:

1. Is there a passive route? Archive, cache, registry, log, third-party copy.
2. What identity does this action carry — none, persona, or real?
3. What will the target be able to see, and when?
4. If this burns, what is lost, and who needs to know?

## Post-action

- [ ] Exposure event logged: what, when, from which identity, what the target
      could observe
- [ ] Exposure graded clean / anonymous contact / pseudonymous contact /
      attributed
- [ ] If attributed: stop, notify the case owner, and record it for the report
- [ ] Persona state noted (challenged, restricted, healthy)
