# Deliverability: what a sender must know

Cold email lands in the inbox when it is authenticated, sent in small numbers, to the right people, and nobody
marks it as spam. Everything else is detail.

## The checklist

| Item | Rule | Why |
|---|---|---|
| Mailbox | A real person's mailbox on the work domain | Free webmail gets about half the replies of a work domain (one large dataset) |
| SPF | Set on the domain | Gmail and Yahoo require SPF or DKIM from every sender; both (plus DMARC) for bulk senders and above 5,000 a day at Outlook.com. Set both anyway |
| DKIM | Set on the domain | Same as SPF |
| DMARC | Published, `p=none` at least, aligned with SPF or DKIM | Required above 5,000 a day; free, and rules keep tightening |
| Volume | 20 to 50 a day per mailbox at most | Small batches reply better; spikes look like spam |
| New mailbox or domain | Start with a handful a day, grow over weeks | Google: "start with a low sending volume... slowly increase" |
| Spam complaints | Under 0.1%, never 0.3% | Above 0.3% Gmail stops helping you |
| Bounces | Under 2% | A high bounce rate says "bought or guessed list" |
| Tracking | Off (no open pixel, no wrapped links) | Tracking-off emails got more replies in a 31M-email dataset |
| Format | Plain text, no image, no attachment, no link in email 1 | Looks like a person, not a campaign |
| Opt-out | A plain line in every email; honor within 2 days | Yahoo: 2 days; US law: 10 business days at most |

## How to check SPF, DKIM, DMARC

- Send yourself an email to a Gmail address, open it, "Show original": SPF, DKIM and DMARC each say PASS.
- Not passing: the domain admin adds the records their email provider gives (Google Workspace and Microsoft 365
  both have a setup page).

## The thresholds that matter (official)

| Provider | Since | Who | Must |
|---|---|---|---|
| Gmail | Feb 2024, stricter from Nov 2025 | Everyone | SPF or DKIM, spam under 0.3%, valid DNS, TLS |
| Gmail | same | Close to 5,000 a day from one domain (forever after) | SPF and DKIM and DMARC, alignment, one-click unsubscribe on marketing mail |
| Yahoo | Feb 2024 | Same split | Same, plus unsubscribes honored in 2 days |
| Outlook.com | May 2025 | Over 5,000 a day | SPF, DKIM, DMARC aligned; else junk, then rejected (550 5.7.515) |

One person sending 30 a day is far below the bulk lines. Build to them anyway.

## Myths to drop

- **Warm-up networks** (tools where inboxes mail each other and fake opens): no independent proof they work;
  one large tool shut its warm-up network in 2023, saying Google told it the
  network broke Gmail's terms. Real warm-up is real email, growing slowly.
- **Spam trigger words:** filters learn from complaints and engagement, not a word list.
- **Open rates:** open counts are unreliable (many are automatic loads, not reads). Count replies.
- **A second lookalike domain fixes everything:** industry best practice discourages lookalike domains, and a
  second domain does not fix bad targeting. Good targeting at low volume does.

## List hygiene

- Send only to emails marked verified; skip the rest.
- Remove hard bounces at once; never retry them.
- Do not re-mail people who never answered a full sequence for at least a few months.
