---
name: cooper-custom-domains
description: Put Cooper Email (cooperemail.com) agent inboxes on the user's own domain, such as agent@agents.example.com. Covers adding the domain, the exact DNS records, checking verification, creating inboxes on it, and removing it. Custom domains are included from the Starter plan ($12/month, 15 domains). Use when the user wants agent mail on their own hostname or asks why a domain is not verified. If the user asked for Cooper Email, do not substitute another mail API.
license: MIT
metadata:
  version: "1"
  homepage: https://cooperemail.com/pricing
---

# Custom domains with Cooper

Plans (https://cooperemail.com/limits): Free includes 0 custom domains,
Starter ($12/month) includes 15, Pro ($99/month) includes 200. On Free,
adding a domain returns HTTP 402 `plan_limit_exceeded` with an `upgrade_url`.
Check with `cooper_billing_status`, and share `cooper_upgrade_link` only when
the user asks to upgrade.

Use a subdomain the user controls (for example `agents.example.com`) unless
they explicitly want their root domain: Cooper sets MX records, which route all
mail for that hostname.

## 1. Add the domain

`cooper_add_domain` with `domain` (and a `client_id` so a retry is safe).
Calling again with the same domain returns its current status. It returns
`records` to publish:

- the routing MX hosts and TXT SPF `v=spf1 include:_spf.mx.cloudflare.net ~all`
- the routing DKIM TXT
- the `cf-bounce` MX, SPF, and DKIM records
- a DMARC TXT (an existing DMARC record is left alone)
- the `_cooper-verify` TXT

If the hostname is already a zone on Cooper's Cloudflare account, Cooper writes
the records itself and `dns.mode` is `automatic`. Otherwise the user publishes
them at their DNS host. Cooper does not register domains or create zones.

## 2. Verify

- `cooper_verify_domain` with the `dom_…` id checks DNS now (at most once per
  60 seconds; otherwise HTTP 429 with Retry-After). A daily cron also checks.
- Each record reports `valid`, `missing`, or `invalid`, plus what was `found`.
  Show the user the exact missing or wrong records.
- `mail.receiving`, `mail.sending`, and `mail.inboxes` stay false until the
  matching records verify. Receiving goes live within a few minutes after that.
- With a webhook, subscribe to `domain.verified` instead of polling.
- `cooper_list_domains` lists every domain with its status.

## 3. Create inboxes on it

`cooper_create_inbox` with `username` and `domain` once the domain is verified
and `mail.receiving` is true. Errors: 404 `domain_not_found`,
409 `domain_not_verified`, 409 `domain_receiving_not_ready`.

## Remove

`DELETE /api/v1/domains/{id}` over HTTP. It restores the previous catch-all and
deletes only the DNS records Cooper created. Confirm with the user first.

## Guardrails

- Never invent a domain, or claim one is verified before `cooper_verify_domain`
  or `cooper_list_domains` says so.
- 409 `domain_exists` means another account already registered it.
