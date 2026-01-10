# Growth Strategy

Modern growth hacking: loops + product-led growth + disciplined experimentation, under privacy and deliverability constraints.

## When to Use

- Designing growth strategy or GTM plans
- Planning experiments and A/B tests
- Optimizing activation, retention, or referral flows
- Building viral/referral loops
- Reviewing growth tactics for ethics/compliance

## Core Principle

**If a "hack" doesn't strengthen a loop or an input metric, it's noise.**

## 1. Growth Model First

### North Star Metric (NSM)

- Single metric aligning the whole org
- Plus input metrics (leading indicators you can move weekly)
- Avoid vanity metrics

### Growth Loops > Funnels

- **Loops**: Closed systems where outputs feed inputs → compounding growth
- **Funnels**: Linear → diminishing returns

Common loops:

| Loop Type | Example                                         |
| --------- | ----------------------------------------------- |
| Viral     | User creates → shares → new users               |
| UGC/SEO   | User creates content → indexed → new users find |
| Paid      | Revenue → reinvest in ads → more revenue        |
| Sales     | Customer → case study → new leads               |

### Product-Led Growth (B2B/SaaS)

Product itself drives: Acquisition → Activation → Retention → Monetization

## 2. Instrumentation

### Event Taxonomy

- Clean identity resolution: anonymous → user → account
- Cohort retention tracking
- Activation milestones defined

### Incrementality

- Holdouts / geo splits when attribution is noisy
- Don't trust last-click blindly

### Metric Categories

| Type       | Examples                                |
| ---------- | --------------------------------------- |
| Core       | NSM + input metrics                     |
| Guardrails | Churn, spam rate, refunds, latency, NPS |

## 3. Experimentation Engine

### Intake System

- Single queue + scoring (RICE/ICE)
- Weekly cadence

### Test Definition (Required)

- [ ] Hypothesis
- [ ] Target segment
- [ ] Success metric
- [ ] Guardrail metrics
- [ ] Sample size rule
- [ ] Kill criteria

### High-ROI Test Areas

- Onboarding steps
- Paywall copy
- Pricing/packaging
- Referral incentive
- Landing page variants
- Lifecycle messages

## 4. Lever-Specific Playbooks

### Activation & Onboarding (Highest ROI)

- Reduce time-to-value
- Templates, importers, "one-click first win"
- Progressive disclosure (ask when needed, not upfront)
- Guided setup flows

### Viral/Referral Loops

- Build shareable artifacts (reports, badges, embeds)
- "Invite teammates" as natural workflow
- Reward activated referrals, not just signups

### Content + SEO

- Programmatic SEO: template + real value + strong linking
- Audit/prune thin pages (don't endlessly generate)
- Quality > quantity

### Lifecycle (Email/Push)

**Deliverability is gating factor:**

- SPF/DKIM for all senders
- DMARC for bulk
- Keep complaint/spam rates low

### Community-Led Growth

- Seed right early members
- Great "first experience"
- Connect to business outcomes (support deflection, referrals)

## 5. Privacy & Measurement Constraints

### Expect

- Less reliable cross-site tracking
- Cookie-based attribution unstable
- Platform policy changes

### Adapt

- First-party data focus
- Server-side signals
- Incrementality testing
- Design measurement that survives policy changes

## 6. AI in Growth

### Good Uses

- Generate creative/landing page variants to test (humans review)
- Summarize qualitative feedback
- Cluster objections
- Speed up research

### Avoid

- "AI content spam" at scale without quality control
- Backfires in SEO and brand

## 7. Hard Red Lines

**If a tactic can't survive being in a postmortem or public doc, don't ship it.**

Never:

- Spam (email/SMS)
- Fake reviews
- Scraping that violates ToS
- Dark patterns
- Deceptive pricing/consent

## Output Format

When proposing growth initiatives:

```text
## Initiative: [Name]
**Loop/Lever**: [Which growth loop or lever this strengthens]
**Hypothesis**: [If we do X, Y metric will improve by Z because...]
**Input Metric**: [What leading indicator we're moving]
**Guardrails**: [Metrics that must not regress]

### Implementation
[Concrete steps]

### Measurement
[How we'll know it worked]

### Kill Criteria
[When to stop if failing]
```

## Quick Checklist

Before shipping any growth tactic:

- [ ] Does it strengthen a loop or input metric?
- [ ] Is the hypothesis testable?
- [ ] Are guardrails defined?
- [ ] Is it compliant with platform ToS?
- [ ] Would you put it in a public doc?
- [ ] Does it respect user privacy?
- [ ] Is deliverability accounted for (if email)?

See `references/` for detailed playbooks.
