# Deliverability check, in detail

Load this when running step 3 of the skill. Work the layers in order and stop
at the first hard failure: no amount of copy editing gets unauthenticated
mail delivered. Every provider rule below carries a source in
[sources.md](sources.md), checked as of 2026-11-05. Providers change these
pages; re-read them before quoting a rule as current.

Each claim here is marked:

- **[provider]**: stated by the mailbox provider or a standard.
- **[law]**: stated by a regulator.
- **[industry body]**: a published position of M3AAWG, the industry
  anti-abuse working group. Not law and not a provider rule.
- **[convention]**: common practitioner practice, not a published rule. Say
  so when passing it on.

## Layer 1: authentication

### What to look up

Use `scripts/check-sending-domain.sh <domain> [selector]`, or by hand:

```sh
dig +short MX  example.com                      # can it receive replies and bounces?
dig +short TXT example.com | grep -i spf1        # SPF: exactly one v=spf1 record
dig +short TXT _dmarc.example.com                # DMARC record
dig +short TXT <selector>._domainkey.example.com # DKIM public key for that selector
```

No `dig`? `nslookup -type=TXT _dmarc.example.com` works on macOS, Linux and
Windows. A shell-less host can use a public DNS-over-HTTPS JSON endpoint, e.g.
`https://dns.google/resolve?name=_dmarc.example.com&type=TXT`.

### How to read it

- **SPF** [provider, RFC 7208]: one TXT record starting `v=spf1` at the
  domain in the envelope sender. Two records is a permanent error. It must
  `include:` every service that sends as the domain (Google Workspace uses
  `include:_spf.google.com`). End with `~all` or `-all`; `+all` authorises
  anyone. At most 10 DNS-lookup terms (`include`, `a`, `mx`, `ptr`, `exists`,
  `redirect`) counting nested includes.
- **DKIM** [provider, RFC 6376]: a public key at `<selector>._domainkey.<domain>`.
  DNS can't list selectors. Find the real one in the `s=` tag of the
  `DKIM-Signature` header on a sent message. Google Workspace's default
  selector is `google`. Gmail requires keys of 1024 bits or more and
  recommends 2048.
- **DMARC** [provider, RFC 9989, which replaced RFC 7489 in May 2026]: a TXT
  record at `_dmarc.<domain>` starting `v=DMARC1`. `p=none` is the minimum
  Gmail, Yahoo and Outlook.com accept from bulk senders. It satisfies the rule
  but blocks no spoofing; move to `quarantine` then `reject` once reports show
  only your own services. Add `rua=` to receive aggregate reports. A
  subdomain with no record inherits the parent's policy (`sp=` if set).
- **Alignment** [provider]: the visible From domain must match the SPF domain
  or the DKIM `d=` domain (relaxed alignment allows subdomains). Sending
  through a tool that signs with its own domain fails alignment until you add
  its DKIM record on your domain.
- **Reverse DNS and TLS** [provider]: Gmail requires the sending IP's PTR
  record to resolve back to it, and TLS in transit. Hosted mailbox providers
  (Google Workspace, Microsoft 365) handle both; check only for your own
  servers.

### Prove it on a real message

DNS shows what is published. Send one message to a personal Gmail address
and open "Show original": SPF, DKIM and DMARC each read PASS or FAIL, with
the domain that passed. That's the result that counts.

### Hard failures

- No SPF and no DKIM: rejected or spam-foldered at Gmail and Yahoo for every
  sender [provider].
- Bulk sender without DMARC or alignment: since November 2025 Gmail applies
  temporary and permanent rejections to non-compliant traffic [provider];
  Outlook.com has rejected non-compliant high-volume domains with
  `550 5.7.515` since 5 May 2025 [provider].

## Layer 2: reputation, volume and warm-up

### Thresholds that are published

- **Gmail bulk sender** [provider]: close to 5,000 messages a day to personal
  Gmail accounts (the page says "5,000 or more" in one place and "more than
  5,000" in another). Mail from the primary domain and its subdomains counts
  together, and once reached the status is permanent. The rules do not cover
  mail sent to Google Workspace business addresses.
- **Outlook.com high-volume sender** [provider]: more than 5,000 a day to
  outlook.com, hotmail.com and live.com.
- **Yahoo** [provider]: requires bulk-sender measures but its best-practice
  page gives no volume threshold.
- **Spam rate** [provider]: Gmail asks for under 0.10% and never 0.30% or
  more; Yahoo asks for under 0.3%. Above 0.3% Gmail withholds mitigation
  support.
- **Google Workspace sending cap** [provider]: 2,000 messages a day per paid
  user (500 on trial accounts), on a rolling 24 hours. It is an account limit,
  separate from the bulk-sender classification; hitting it does not make the
  domain a bulk sender.

### Practice that is not published [convention]

- A new domain or mailbox has no reputation. Start with a small daily number
  of cold emails per mailbox (low tens at most), raise it gradually over two
  to four weeks while bounces and complaints stay low, and keep a fixed cap
  after that. Write the ramp down in the stop rules.
- Real replies help reputation. Automated "warm-up networks" that send and
  reply between member inboxes manufacture engagement, which M3AAWG names as
  unacceptable. Don't recommend them.
- Verify addresses before sending and re-verify a list that has sat for
  weeks. Hard bounces are the fastest way to lose a new domain.
- Enrol the sending domain in Google Postmaster Tools
  (https://postmaster.google.com) to see Gmail's spam rate and reputation.
  It only shows data once volume to Gmail is large enough.

### The separate-domain question

- Sending cold mail from the company's main domain puts invoices, password
  resets and every employee's mail at risk if a campaign goes badly
  [convention]. A separate, clearly owned sending domain contains that risk.
- It is honest only if the sender name, signature and the domain itself
  identify the real company (the domain redirects to or names the main
  site). M3AAWG's November 2025 position defines a deceptive lookalike as a
  domain that resembles a legitimate one but is unrelated, and calls it
  abusive to use extra domains or mailboxes to bypass volume limits, avoid
  filters or mask sending domains [industry body]. The line is identity and
  intent: one clearly owned domain to protect the main one is fine; a fleet
  of domains to stay under limits or hide volume is not.
- Subdomains don't reset Gmail's bulk count, because volume is counted at the
  primary domain [provider].

## Layer 3: unsubscribe and identity

- **One-click unsubscribe** [provider]: Gmail requires bulk senders to
  include both headers on marketing and promotional mail, plus a visible
  unsubscribe link in the body:

  ```
  List-Unsubscribe: <https://example.com/unsub?id=...>
  List-Unsubscribe-Post: List-Unsubscribe=One-Click
  ```

  (RFC 2369 and RFC 8058). Yahoo requires a working one-click
  `List-Unsubscribe` header for bulk senders, prefers the RFC 8058 POST
  method and accepts `mailto:`. Google notes that recipients, not Google,
  decide what is promotional, so treat cold email as promotional. Missing
  one-click doesn't trigger automatic rejection at Gmail, but it removes
  mitigation support.
- **Honor opt-outs**: Yahoo requires within 2 days; Google recommends within
  48 hours [provider]. CAN-SPAM's legal maximum is 10 business days, and the
  opt-out must keep working for at least 30 days after sending [law].
- **CAN-SPAM (US)** [law]: covers B2B commercial email. Truthful headers and
  From identity, a subject that matches the content, a clear opt-out, a valid
  physical postal address, and disclosure that the message is an
  advertisement. Penalties are per email.
- **UK PECR** [law]: companies and LLPs can be emailed without prior consent;
  sole traders and some partnerships are treated as individuals and need
  consent. Never disguise who is sending, and give a valid opt-out address.
  The ICO says this guidance is under review.
- **Elsewhere**: rules differ by country (Germany and Canada, for example,
  are much stricter for B2B cold email). Say the recipient's country decides,
  that this isn't legal advice, and suggest the founder check before
  emailing those regions.
- **Identity** [law and provider]: the From name is a real person at the real
  company; no fake `Re:`/`Fwd:`; nothing that impersonates Gmail or another
  brand in the From header.

## Layer 4: content, last

Weakest lever; check it only once the layers above pass.

- Plain text or minimal HTML with a text part [convention].
- No images, attachments or link shorteners; at most one link, none in the
  first email [convention].
- Open-tracking pixels add a remote image to a plain email and the open
  numbers they produce are unreliable (mail apps prefetch images). Prefer
  measuring replies [convention].
- Message format must follow RFC 5322 [provider].
- "Spam trigger word" lists have no published provider backing. If the user
  asks for one, say that, and put the effort into layers 1-3.
