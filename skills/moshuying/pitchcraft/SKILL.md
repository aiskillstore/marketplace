---
name: pitchcraft
description: Structured persuasion for tech leads, PMs, and founders—not activity logs. Five scenarios (kickoff, status update, wrap-up, investor pitch, solution selling) on one 5-part framework (Hook→Context→Proposal→Evidence→Ask). AI prompts for missing materials and audience context; pre-submit checklist. Claude Code plugin; Cursor, Codex, and chat via prompts.
---

**Languages:** English (this file) · 简体中文 → `SKILL.zh-CN.md`

# Persuasive briefings · Workflow

## Essence

This is not report writing—it is **persuasion**. In every scenario you do the same thing:

> In limited time, help a specific audience understand context, trust your judgment, and provide the support you need.

## Users & scenarios

| Role | Scenarios | Audience |
|---|---|---|
| Tech lead / engineering manager | Kickoff, milestone review, wrap-up | Business leaders, CTO, PMO |
| PM / product lead | Quarterly review, annual summary, requirements review | Director, VP |
| Founder / business owner | Investor pitch | Investors, partners |
| Pre-sales / solutions | Solution selling | Customer execs, technical evaluators |

---

## Core: 5-part persuasion framework

All briefing types share one backbone; section emphasis differs.

```
Part 1 · Hook
  → Why should they keep listening?
  → Opportunity / pain / urgency

Part 2 · Context
  → What is the situation?
  → What we have done and what we have

Part 3 · Proposal
  → What we will do / did?
  → Scope, path, pace

Part 4 · Evidence
  → Why we can succeed / succeeded?
  → Data, moat, team, cases

Part 5 · Ask
  → What do we need from them?
  → Decision / resources / partnership / investment
```

---

## Briefing types & templates

Each type is an instance of the 5-part framework.

### Project kickoff

**Goal:** Get leadership to approve start and allocate people and budget.

| Part | Section | Focus |
|---|---|---|
| Hook | Background & opportunity | Market, pain, competition, why now |
| Context | What we already have | Team, tech, data, prior assets |
| Proposal | Goals & scope | In/out of scope, milestones |
| Evidence | Why us | Differentiation, moat |
| Ask | Resources & risks | Support needed, top risks and mitigation |

```
# {Project} · Kickoff

## Background & opportunity

{Why now: market, pain, competition—2–4 sentences.

This is the persuasion entry—create “we should do this.”}

## What we already have

{Team, tech, data, business assets—not bragging, but trust.

Pattern: “We already have X, so this is not from zero.”}

## Goals & scope

**In scope**: {capabilities}
**Out of scope**: {explicit exclusions—prevent scope creep}

{Milestones and timeline}

## Why us

{Core difference vs alternatives. Moat: why others can’t or won’t match.}

## Resources & risks

{People / budget / cross-team needs
Top risk and mitigation}
```

### Status update

**Goal:** Convince leaders and stakeholders the work is on track and worth continued investment.

| Part | Section | Focus |
|---|---|---|
| Hook | One-line summary | 1–2 most important facts this period |
| Context | Period context | Position vs last period |
| Proposal | Key progress | By milestone or module |
| Evidence | Key metrics | Progress, quality, efficiency |
| Ask | Risks & decisions | Decisions and coordination needed |

```
# {Project} · Status update

## One-line summary

{1–2 facts; audience grasps core in 10 seconds}

## Key progress

{Completed items and metrics by milestone or module}

## Risks & response

Formula per item: {symptom} → {root cause} → {mitigation} → {status}

Decisions: options + recommendation—no open homework:
❌ "Dependency X uncertain—please advise"
✅ "Dependency X slipped 2 weeks. Option A (add people) vs B (move milestone). Recommend A; need Team Y support."

## Next phase

| Item | ETA | Dependencies | Risk |
|---|---|---|---|
```

### Wrap-up / annual review

**Goal:** Show delivered value and assets retained.

| Part | Section | Focus |
|---|---|---|
| Hook | Goal attainment overview | Did we succeed overall? |
| Context | Original goals | What we committed to |
| Evidence | Quantified outcomes | Data-led |
| Proposal | Lessons & assets | What remains |
| Ask | Next phase or handoff | What happens next |

```
# {Project} · Wrap-up / {Year} annual review

## Goal attainment

| Goal | Target | Actual | % | Notes |
|---|---|---|---|---|

Underperformance: root cause and improvement—say it before they ask.

## Core deliverables

3–5 items, each: {what} + {metric} + {business impact}

## Lessons

- **What worked**: reusable methods / architecture / process
- **What failed**: root cause + prevention
- **Assets left**: code / data / docs / team capability

## Next

If continuing → direction, goals, key results, resources
If ending → handoff so nothing is left unsupported
```

### Investor pitch

**Goal:** Spark interest for a deeper conversation.

| Part | Section | Focus |
|---|---|---|
| Hook | One-liner | Elevator pitch |
| Context | Market opportunity | Size, pain, why now |
| Proposal | Product | Solution, core features, stage |
| Evidence | Moat & traction | Tech, data, growth, team |
| Ask | Funding / partnership | Amount, use, milestones |

```
# {Project} · Pitch

## One-liner

{What we do, for whom, what value}

## Market opportunity

{Size, persona, pain, why now}

## Product

{How we solve, core features, architecture (brief), stage}

## Moat & traction

**Moat**: {tech / data / network / team—why others can’t}
**Metrics**: {users, growth, retention, revenue}
**Team**: {why this team can execute}

## Funding ask

{Amount, use of funds, milestones, next round goal}
```

### Solution selling

**Goal:** Convince customer executives your solution is the best fit.

| Part | Section | Focus |
|---|---|---|
| Hook | Pain alignment | Their problem in their words |
| Context | Current state | Gaps in status quo |
| Proposal | Solution | How we solve |
| Evidence | Cases & data | Proof |
| Ask | Partnership | How to start |

```
# {Project} · Proposal

## Pain alignment

{Customer language for the problem—accuracy builds trust fast}

## Current state

{Why status quo fails: features, cost, efficiency, risk}

## Our solution

{How we solve; capabilities and differentiation}

## Proof

{Same-industry cases with metrics}
{If no case: POC plan or demo roadmap}

## Partnership

{Engagement model, timeline, what we need from them}
```

---

## Writing rules

### 1. Their concerns first, your story second
❌ Five minutes on how hard the team worked and how clever the architecture is  
✅ First sentence answers “why should I care?”

### 2. Risks need judgment
❌ "Servers occasionally timeout—please monitor"  
✅ "Connection pool exhaustion; scaling in progress; expected recovery tomorrow"

### 3. Acknowledge peer teams first
❌ "We filled a gap no one else addressed"  
✅ "Team X has a mature Y; we extend with Z"

### 4. Metrics need source and definition
❌ "Conversion improved 20%"  
✅ "Conversion +20% (June vs May, same account pool)"

### 5. Bad news early when it matters
❌ Wins first, then buried "but we slipped"  
✅ Lead with material risks, then progress

### 6. No homework for the audience
❌ "Next: keep pushing forward"  
✅ "Integration Wed; risk is dependency Y—owner aligned"

---

## Workflow

```
Step 1 — Load memory
  Read leader context, business positioning, format prefs.
  Missing → ask user to supply.

Step 2 — Scenario & audience
  User picks type (kickoff / status / wrap-up·annual / pitch / solution selling).
  Probe audience:
  □ Role and level?
  □ How much do they already know?
  □ Top concerns (tech / business / cost / time)?

Step 3 — Material intake
  Check completeness by type; ask for gaps:

  Kickoff:
  □ Background / market analysis
  □ Competitive landscape
  □ Team capabilities
  □ Goals and KPIs
  □ Resources and budget
  □ Timeline

  Status:
  □ Completed work this period
  □ Key metrics (progress / quality / efficiency)
  □ Risk list with judgment and mitigation
  □ Next-phase plan
  □ Decisions needed from leadership

  Wrap-up / annual:
  □ Original goals
  □ Quantified outcomes
  □ Lessons learned
  □ Next plan or handoff

  Pitch:
  □ Market data and reports
  □ Product demo or MVP status
  □ Competition
  □ Team intro
  □ Financials and forecast
  □ Funding ask and use of funds

  Solution selling:
  □ Customer background and pain
  □ Alternative solutions
  □ Our solution and capabilities
  □ Cases or POC plan
  □ Pricing or engagement model

  If user says "you know everything—just write":
  → Pull from memory and prior context
  → Open with "Based on available info; may be missing XX"

Step 4 — Draft to template
  Pick template; apply writing rules.
  After each part, ask: "Does this answer what they care about?"

Step 5 — Final check
  □ First 10 seconds feel relevant?
  □ Every number sourced and defined?
  □ Every risk has root cause + response?
  □ No vague "needs attention" without judgment?
  □ Cross-team mentions acknowledge others first?

Step 6 — User confirmation
  Present → "What should we adjust?"
  Format issues → add to format memory
```

---

## Cross-scenario migration

| From → To | Change | Keep |
|---|---|---|
| Kickoff → Pitch | Hook: business pain → market opportunity; Evidence: tech moat → traction | 5-part structure, risk logic |
| Status → Kickoff (next phase) | Progress becomes Context; accumulated risks feed Risk | Metric definitions, team narrative |
| Wrap-up → Case study | De-identify internals; emphasize customer value | Quant methods, acceptance criteria |
| Solution selling → Kickoff | Customer pain → market opportunity; cases → evidence | Structure, risk foresight |
