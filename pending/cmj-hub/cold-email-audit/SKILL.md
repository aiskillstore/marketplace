---
name: cold-email-audit
description: 30-point audit of a B2B outbound program across four dimensions — infrastructure (8 points), targeting (8 points), messaging (8 points), and operations (6 points). Produces a 0-100 score, the top 3 levers, and a 90-day remediation order. Loaded by the main cold-email skill when the user asks to audit or grade their outbound. Based on the JMC 30-Point Outbound Audit framework.
user-invocable: false
allowed-tools: Read Write Grep
  - WebFetch
license: MIT

---

# Cold Email Audit — 30-Point Outbound Program Review

Loaded by `cold-email` when the user asks to "audit our outbound",
"why isn't this working", "grade our cold email program", or similar.
Scores a B2B outbound program against 30 points across 4 dimensions
and surfaces the top 3 levers.

## Activation triggers

- "Audit our outbound"
- "Why isn't our cold email working"
- "Grade our outbound program"
- "Outbound audit"
- "What's wrong with our cold email"
- "Score our outbound"

## Workflow

### 1. Intake (one batch of questions)

Ask the user to provide context in a single message — DON'T ask 30
questions sequentially. Surface a structured intake form:

```
To run the 30-point audit, share what you can across these 4 dimensions:

INFRASTRUCTURE
  - Sending domain(s) — primary and secondary
  - Inbox provider (GSuite / O365 / Smartlead / Instantly / custom)
  - Warm-up: how many mailboxes, ramped how long, current daily limits
  - SPF / DKIM / DMARC status (or paste DMARC TXT record)

TARGETING
  - ICP definition (one paragraph)
  - PSP (Pain Signal Profile) — what signals do you anchor on?
  - List source (apollo / clay / hand-built / scraped / referrals)
  - List size, send volume per week, response rate baseline

MESSAGING
  - Paste your current T1 opener
  - Paste your subject line (or top 3 subjects)
  - How many sequence touches, cadence in days
  - Personalization layer: none / variable / per-person-research

OPERATIONS
  - Reply handling: who, response SLA
  - Booking motion: link in email, link in reply, manual?
  - Hand-off to sales: who routes, when, what info
  - Reporting cadence: weekly / monthly / never
```

Don't grade until you have the user's answers. If they don't have
a dimension at all, that's a finding — note it as "Not in place".

### 2. Score against the 30-point rubric

Load `references/audit-rubric.md` and score each point 0 / 0.5 / 1.

The four dimensions:

| Dimension | Points | What it covers |
|---|---|---|
| Infrastructure | 8 | Domains, warm-up, DNS, sending architecture |
| Targeting | 8 | ICP, PSP, list source, segmentation |
| Messaging | 8 | Opener, body, CTA, sequence, personalization |
| Operations | 6 | Reply SLA, booking motion, hand-off, reporting |

Total: 30 points → normalize to a 0-100 score:

```
Score = (totalPoints / 30) * 100
```

### 3. Identify the top 3 levers

After scoring, find the 3 lowest-scoring points and rank them by
impact-per-day-of-effort. Don't just list the lowest scores — weight
by:

- **Compounding impact**: a fix to infrastructure compounds across
  every campaign forever; a subject-line tweak compounds for one
  campaign.
- **Effort**: an SPF flatten is 1 hour; a full PSP rewrite is 2 weeks.
- **Sequencing**: deliverability MUST be solid before any messaging
  iteration matters.

### 4. Output

Produce a structured report:

```markdown
# Outbound Audit — <company name>

## Score: <0-100>/100

| Dimension | Score | Grade |
|---|---|---|
| Infrastructure | <0-8>/8 | A / B / C / D / F |
| Targeting | <0-8>/8 | |
| Messaging | <0-8>/8 | |
| Operations | <0-6>/6 | |

## The top 3 levers

### 1. <Lever name> — <effort / impact>
<2-3 sentences on what to fix, why it compounds, how to ship in 7-14 days.>

### 2. <Lever name>
...

### 3. <Lever name>
...

## 90-day remediation order

| Days | Lever | Owner | Verify by |
|---|---|---|---|
| 1-14 | <Lever 1> | <role> | <metric> |
| 15-45 | <Lever 2> | | |
| 46-90 | <Lever 3> | | |

## Full point-by-point detail
<Optional: only if user asks. Otherwise keep concise.>
```

## Grade thresholds

| Score | Grade | Meaning |
|---|---|---|
| 90-100 | A | Mature program. Tune for scale. |
| 75-89 | B | Solid foundation. Iterate on messaging + ops. |
| 60-74 | C | Works in spurts. Fix the bottom-third before scaling. |
| 40-59 | D | Don't scale spend until top-3 levers are fixed. |
| 0-39 | F | Stop sending. Rebuild infrastructure first. |

## References

- `references/audit-rubric.md` — full 30-point rubric with scoring criteria
- `../../cold-email/references/jmc-framework.md` — the framework underneath
- The full **30-Point Outbound Audit Template** ships as a DOCX in
  [the free Cold Email Linter](https://jaymountconsulting.com/tools/cold-email-linter)
