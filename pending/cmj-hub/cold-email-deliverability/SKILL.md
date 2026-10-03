---
name: cold-email-deliverability
description: 15-point pre-campaign domain health check across DNS (SPF, DKIM, DMARC, MX, BIMI), reputation (SNDS, Postmaster, blacklists), warm-up status (mailbox age, send volume ramp, reply ratio), and content (spam-trigger lint, link-to-text ratio, image-to-text ratio). Returns a 0-100 deliverability score and a fix-order. Uses native DNS lookups + public blacklist APIs — no paid tools required. Loaded by the main cold-email skill when the user asks about deliverability, domain health, SPF/DKIM/DMARC, or pre-launch readiness.
user-invocable: false
allowed-tools: Read Write Bash
  - WebFetch
license: MIT

---

# Cold Email Deliverability — 15-point pre-campaign domain health

Loaded by `cold-email` when the user asks about deliverability,
SPF/DKIM/DMARC, domain health, or "are we ready to send."

## Activation triggers

- "Check deliverability"
- "Domain health"
- "SPF / DKIM / DMARC"
- "Are we ready to send"
- "Pre-campaign check"
- "Why are we landing in spam"
- "Inbox placement"

## Workflow

### 1. Inputs

Ask for:

- `sending_domain` — e.g. `outreach.jmc.com`
- `from_address` — full address used in the From: header
- `inbox_provider` — GSuite / O365 / Smartlead / Instantly / custom
- `mailbox_age_days` — how long this address has been sending
- `current_daily_send_volume` — emails/day
- `recent_reply_ratio` — % over the last 14 days (skip if first campaign)

### 2. Run the 15 checks

The 15 checks span four categories:

| # | Category | Check | How |
|---|---|---|---|
| 1 | DNS | SPF record exists | `dig TXT <domain>` for `v=spf1` |
| 2 | DNS | SPF includes inbox provider | Lookup includes match provider |
| 3 | DNS | SPF lookup count ≤10 | Resolve all includes recursively |
| 4 | DNS | DKIM selector resolves | `dig TXT <selector>._domainkey.<domain>` |
| 5 | DNS | DKIM key ≥1024 bits | Decode the p= value |
| 6 | DNS | DMARC record exists | `dig TXT _dmarc.<domain>` |
| 7 | DNS | DMARC policy ≠ none for cold outreach | `p=quarantine` or `p=reject` required for bulk senders post-Feb 2024 |
| 8 | DNS | DMARC has `rua=` reporting | Aggregate report URI configured |
| 9 | Reputation | Domain not on Spamhaus / SURBL | Lookup against public blacklist APIs |
| 10 | Reputation | rDNS / PTR record matches sending IP | `dig -x <sending-ip>` matches forward |
| 11 | Warm-up | Mailbox age ≥21 days | Compare `mailbox_age_days` to threshold |
| 12 | Warm-up | Daily send ramp ≤30/day for first 14 days | Compare `current_daily_send_volume` |
| 13 | Warm-up | Reply ratio ≥3% over 14 days | (Hard threshold for B2B cold) |
| 14 | Content | TLS support on MX | Confirm STARTTLS advertised |
| 15 | Content | DKIM signs the body, not just headers | Test message via test tool (mxtoolbox) |

### 3. Run the lookups

Use `Bash` for `dig`, `host`, `nslookup`. Use `WebFetch` for blacklist
lookups against public APIs (Spamhaus DBL, MultiRBL.valli.org).

**Never** call paid APIs. Never ask for an API key. If a check requires
a tool the user doesn't have, fall back to telling the user the
manual lookup command + expected output.

Example fallback:

> Check 9 (Spamhaus / SURBL) requires `multirbl.valli.org` or
> `mxtoolbox.com` — copy-paste this URL:
> `https://multirbl.valli.org/lookup/<sending-domain>.html`
> Look for any red flags in the response.

### 4. Score

Each of the 15 checks is binary (pass / fail). Score:

```
Deliverability = (passingChecks / 15) * 100
```

### 5. Output the fix-order

Failing checks get ranked by:

1. **Fail-blocker severity**: SPF / DKIM / DMARC failures and blacklist
   hits are blockers — fix BEFORE sending anything.
2. **Compounding impact**: a DNS fix compounds across all campaigns
   forever.
3. **Ease**: TXT record changes are 1 hour; warm-up is days.

Output:

```markdown
# Deliverability check — <domain>

## Score: <0-100>/100 — <grade>

| # | Check | Status |
|---|---|---|
| 1 | SPF record | ✓ / ✗ |
| 2 | SPF includes provider | ✓ / ✗ |
... (all 15) ...

## Fix order

### CRITICAL (do not send until fixed)
- Check N: <description> — <fix>

### IMPORTANT (fix in next 7 days)
- ...

### NICE-TO-HAVE
- ...
```

## Grade thresholds

| Score | Grade | Verdict |
|---|---|---|
| 95-100 | A | Ready. Ship. |
| 85-94 | B | Ship but fix the B-list within 30 days |
| 70-84 | C | Don't scale spend. Fix top 3 first. |
| 50-69 | D | Hold campaign. Fix critical-tier items. |
| 0-49 | F | Pause everything. Rebuild infra. |

## References

- The **Pre-Campaign Domain Health Checklist** (15-point PDF) ships in
  [the free Cold Email Linter](https://jaymountconsulting.com/tools/cold-email-linter).
- DMARC + Feb-2024 bulk-sender rules (Google / Yahoo / Microsoft) —
  see `../../cold-email/references/bulk-sender-rules.md`.
- The full **Cold Email & Outreach Craft** course covers deliverability
  forensics in 4 lessons:
