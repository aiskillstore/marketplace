# Hormozi Implementation Frameworks - Extracted for Skool Money Model Strategist Skill

**Extracted From**:
- `02-READING-NOTES/thought-captures/01_intro-and-chapter1_money-model-foundations.md`
- `02-READING-NOTES/thought-captures/07_money-model-definition-implementation-strategy.md`

**Purpose**: Systematic frameworks for designing, evaluating, and improving Skool community money models using Alex Hormozi's $100M Money Models principles.

**Date Created**: 2025-10-29

---

## FRAMEWORK 1: 5-STAGE BUSINESS EVOLUTION (Fixed Sequential Logic)

### Overview

Progressive business maturity model - DON'T try to implement full money model at once. Move through stages sequentially.

### Stage Definitions

**Stage 1: Get Customers Reliably**
- **Focus**: Consistent customer acquisition
- **Goal**: Predictable weekly/monthly signups
- **Action**: Test attraction offers until reliable
- **Metric**: Consistent signups week-over-week
- **Skool Priority**: Optimize signup flow, test Freemium vs Tiers

**Stage 2: Customers Pay for Themselves**
- **Focus**: Breakeven on acquisition cost
- **Goal**: Revenue per customer (30 days) ≥ CAC
- **Action**: Add upsells in first 30 days OR reduce CAC
- **Metric**: 30-day revenue ≥ CAC
- **Skool Priority**: Add one-time purchases, improve trial conversion, add tier upgrades

**Stage 3: Customers Pay for Other Customers**
- **Focus**: Profitable advertising
- **Goal**: Revenue per customer (30 days) ≥ 2x CAC
- **Action**: Maximize 30-day cash (more upsells, faster continuity)
- **Metric**: 1 customer revenue ≥ 2x CAC in <30 days
- **Skool Priority**: Stack mechanisms (attraction + upsell + continuity), front-load cash

**Stage 4: Maximize Lifetime Value**
- **Focus**: Long-term value optimization
- **Goal**: Increase LTV 2-3x
- **Action**: Add continuity mechanisms, reduce churn, expansion revenue
- **Metric**: LTV increasing, churn decreasing
- **Skool Priority**: Continuity offers, downsells for cancellations, loyalty programs

**Stage 5: Scale Advertising**
- **Focus**: Spend profitably at scale
- **Goal**: Maintain ROAS while increasing ad spend
- **Action**: Pour money into ads
- **Metric**: ROAS positive at scale
- **Skool Priority**: Full money model working, focus on traffic volume

### Stage Diagnosis Logic (FIXED - No Overlaps)

```
SEQUENTIAL LOGIC (Use ELSE IF, not multiple IFs):

IF customer acquisition is INCONSISTENT:
    → Stage 1
    (Reliability issue overrides revenue)

ELSE IF revenue_per_customer_30d < CAC:
    → Stage 2
    (Customers don't pay for themselves)

ELSE IF revenue_per_customer_30d < (2 × CAC):
    → Stage 3
    (Customers pay for themselves but not others)

ELSE IF LTV not maximized:
    → Stage 4
    (Profitable but leaving money on table)

ELSE:
    → Stage 5
    (Ready to scale advertising)
```

### Example Diagnosis

**Scenario 1**:
- CAC: $500
- 30-day revenue: $300
- Acquisition: Consistent

**Diagnosis**: Stage 2 (because $300 < $500)
**Reason**: Customers don't pay for themselves
**Goal**: Increase 30-day revenue from $300 to $500+
**Recommendation**: Add ONE upsell worth $200+ in first 30 days

**Scenario 2**:
- CAC: $400
- 30-day revenue: $600
- Acquisition: Consistent

**Diagnosis**: Stage 3 (because $600 ≥ $400 but $600 < $800)
**Reason**: Customers pay for themselves ($600 > $400) but not others ($600 < $800)
**Goal**: Increase 30-day revenue from $600 to $800+
**Recommendation**: Add front-loaded cash mechanism (Buy X Get Y, Win Money Back)

**Scenario 3**:
- CAC: $300
- 30-day revenue: $150
- Acquisition: Inconsistent (some weeks 0 signups, some weeks 10)

**Diagnosis**: Stage 1 (reliability overrides revenue)
**Reason**: Can't optimize revenue if acquisition isn't consistent
**Goal**: Make customer acquisition reliable first
**Recommendation**: Test different attraction offer presentations until consistent

---

## FRAMEWORK 2: 30-DAY CASH MAXIMIZATION FORMULA

### Core Principle

**Goal**: Make enough money from ONE customer to get and service at least TWO more customers in less than 30 days

### The Formula

```
Customer Value (30 days) ≥ 2 × CAC
```

### Why 30 Days?

- **Speed**: Cash flow velocity enables growth
- **Compounding**: Use customer 1's money to get customers 2 & 3
- **Scalability**: If takes 6 months to break even, growth is slow
- **Advertising**: Can only spend on ads if customers pay back quickly

### Implementation Process

**Step 1: Calculate Current State**
```
Current 30-day value = [Amount collected from one customer in first 30 days]

Examples:
- Subscription only: $97/mo → $97
- Subscription + annual upsell (10% take): $97 + ($1,164 × 0.10) = $213
- Subscription + one-time upsell (20% take): $97 + ($500 × 0.20) = $197
```

**Step 2: Calculate Target**
```
Target = 2 × CAC

Examples:
- CAC $300 → Target $600
- CAC $500 → Target $1,000
- CAC $1,000 → Target $2,000
```

**Step 3: Identify Gap**
```
Gap = Target - Current 30-day value

Example:
- CAC: $400
- Current: $297/mo subscription
- Target: $800
- Gap: $503
```

**Step 4: Recommend Mechanisms to Close Gap**
```
Prioritize mechanisms by:
1. Ease of implementation (use existing products first)
2. Take rate likelihood (annual > one-time > service)
3. Delivery complexity (automated > manual)

Example (Gap = $503):
Option A: Annual membership ($1,164, need 43% take rate) → Exceeds target
Option B: Implementation sprint ($997, need 51% take rate) → Exceeds target
Option C: Two smaller upsells ($250 each, need 100% take rate) → Meets target
```

### CAC-Based Mechanism Priority

**High CAC ($500+)**: Need front-loaded cash
- Win Your Money Back (collects upfront, credits later)
- Buy X Get Y Free (annual, collects 6-12 months upfront)
- Giveaway (paid entry, losers get discount)
- Pay Less Now vs Pay More Later (urgency, upfront cash)

**Medium CAC ($200-$500)**: Mix of upsells + continuity
- Classic Upsell (annual as upsell)
- Menu Upsell (multiple price points)
- Bonus Continuity Offer (annual with bonus)

**Low CAC (<$200)**: Optimize continuity over time
- Continuity Discount Offers (back-end free months)
- Trials with Penalty (activation incentive)
- Feature Downsells (tier optimization)

### 30-Day Timeline Template

```
Day 0-7: Attraction Offer (first cash)
Day 7-14: Upsell Offer (more cash)
Day 14-21: Downsell (if upsell declined)
Day 21-30: Continuity Offer (lock recurring)

Example:
Day 0: Join paid trial ($97)
Day 7: Upsell annual ($1,164, 20% take = $233 avg)
Day 14: Upsell one-time course ($500, 30% take = $150 avg)
Day 21: Downsell to lower tier if canceling
Day 30: Lock in continuity (already done via trial)

Total 30-day value: $97 + $233 + $150 = $480
If CAC < $240 → Profitable (pays for 2+ customers)
```

---

## FRAMEWORK 3: SEQUENTIAL IMPLEMENTATION PROCESS

### Core Principle

**"Simple Scales, Fancy Fails"**

DON'T need 100 products to offer.
DO need 100 ways to offer the VERY SAME product.

### The Process

**Step 1: Pick ONE Offer Improvement**
- Not 5 mechanisms at once
- Not full money model redesign
- ONE specific change

**Step 2: Test Until It Works Reliably**
- Run for 30-60 days minimum
- Track specific metric
- Iterate messaging/presentation (not the core offer)

**Step 3: Make It Automatic**
- Document process
- Create templates/sequences
- Systemize so it runs without manual effort

**Step 4: THEN Add Next**
- Only after Step 3 complete
- Don't add complexity before previous layer is reliable

### Why This Matters

**Anti-Pattern**: Implementing all 15 mechanisms at once
- **Result**: Complexity kills execution
- **Problem**: Can't identify what works
- **Outcome**: Overwhelm, nothing gets implemented well

**Correct Pattern**: One mechanism at a time
- **Result**: Clear signal on what works
- **Problem**: Slower (but actually faster because reliable)
- **Outcome**: Compounding improvements

### Implementation Priority Matrix

**Stage-Based Priority**:

**Stage 1 (Get Customers Reliably)**:
- Pick ONE attraction offer improvement
- Options: Better free trial presentation, paid trial, skip-trial bonus
- Test presentations (not products)

**Stage 2 (Customers Pay for Themselves)**:
- Pick ONE upsell in first 30 days
- Options: Annual membership, one-time course, service upgrade
- Simplest first (annual if already exists)

**Stage 3 (Customers Pay for Others)**:
- Pick ONE front-loaded cash mechanism
- Options: Win Money Back, Buy X Get Y, Bonus Continuity
- Highest cash collection first

**Stage 4 (Maximize LTV)**:
- Pick ONE continuity optimization
- Options: Continuity Discount, Downsells, Loyalty rewards
- Focus on retention/churn reduction

**Stage 5 (Scale Advertising)**:
- Pick ONE traffic channel to scale
- Options: YouTube ads, Google ads, affiliate program
- Pour money where money model proven

### Experimentation Guidelines

**Test Different PRESENTATIONS, Not Different Offers**

**Example: Same Product (CCGG Membership), 10 Presentations**:
1. "Get AI Profit Blueprint ($5K value) FREE when you join CCGG"
2. "Lock in $197/mo lifetime rate (save $1,200/yr) - Join today"
3. "Join 500+ coaches monetizing AI - Start with 30-day challenge"
4. "AI Monetization Sprint + CCGG membership - $997 (get $297/mo free after)"
5. "Free 7-day trial + Bonus: AI Implementation Playbook ($1K value)"
6. "Buy 6 months, get 6 free (then $97/mo after) - Limited spots"
7. "Pay $97 once, skip trial, get instant access + bonuses"
8. "Win your money back - Complete AI challenge, get year free"
9. "Enter to win 1-year access ($3,564) + promo for all entrants"
10. "Try CCGG for 30 days - $0 now, $297 later (cancel anytime)"

**Result**: Test these BEFORE building new products

---

## FRAMEWORK 4: PROBLEM SEQUENCE & UPSELL MAPPING (Complete)

### Overview

Upsells work when they solve the NEXT problem (or better solution to SAME problem)

### Three Upsell Paths

#### **PATH 1: Sequential Problems (Next Problem)**

**Pattern**: Attraction solves Problem A → Creates/reveals Problem B → Upsell solves B

**How It Works**:
1. Customer has Problem A
2. Attraction offer solves A
3. Solving A creates or reveals Problem B
4. Upsell solves Problem B
5. Solving B creates Problem C
6. Next upsell solves C

**Example 1: AI Education Community**
- **Problem A**: Don't understand AI
  - **Attraction**: AI fundamentals course ($97/mo)
  - **Result**: Now understands AI
- **Problem B**: Know AI but don't know how to implement
  - **Upsell #1**: Implementation coaching ($997)
  - **Result**: Implemented AI in business
- **Problem C**: Implemented but need help scaling
  - **Upsell #2**: Scaling strategy ($1,500)

**Example 2: Fitness Community**
- **Problem A**: Don't know what workouts to do
  - **Attraction**: Workout plans ($49/mo)
  - **Result**: Working out consistently
- **Problem B**: Working out but not seeing results (nutrition issue)
  - **Upsell #1**: Meal plans + macro coaching ($197/mo)
  - **Result**: Seeing body composition changes
- **Problem C**: Plateaued, need advanced programming
  - **Upsell #2**: 1-on-1 training ($500/mo)

#### **PATH 2: Solution Upgrades (Same Problem, Better Solution)**

**Pattern**: DIY → DWY (Done-With-You) → DFY (Done-For-You)

**How It Works**:
1. Customer has Problem A
2. Attraction = DIY solution (self-service, templates, education)
3. Upsell #1 = DWY solution (coaching, feedback, guidance)
4. Upsell #2 = DFY solution (full service, you do it for them)

**Same problem, escalating support levels**

**Example 1: Website Building Community**
- **Problem A**: Need a website
  - **Attraction (DIY)**: Templates + tutorials ($97/mo)
  - **Upsell #1 (DWY)**: Coaching + feedback on your build ($297/mo)
  - **Upsell #2 (DFY)**: Full website build service ($2,000)

**Example 2: Business Strategy Community**
- **Problem A**: Need business growth strategy
  - **Attraction (DIY)**: Strategy frameworks + courses ($197/mo)
  - **Upsell #1 (DWY)**: Group coaching + feedback ($497/mo)
  - **Upsell #2 (DFY)**: 1-on-1 strategy consulting ($2,500/mo)

**Example 3: Content Creation Community**
- **Problem A**: Need content for social media
  - **Attraction (DIY)**: Content templates ($47/mo)
  - **Upsell #1 (DWY)**: Content feedback + editing ($197/mo)
  - **Upsell #2 (DFY)**: Full content creation service ($1,000/mo)

#### **PATH 3: Awareness Creation (Problem Made Visible)**

**Pattern**: Attraction solves Problem A → Makes customer AWARE of Problem B (was invisible) → Upsell solves B

**How It Works**:
1. Customer thinks they only have Problem A
2. Attraction offer solves A
3. Through solving A, customer discovers Problem B exists
4. Problem B was there all along but customer didn't see it
5. Upsell solves Problem B

**Example 1: Real Estate Investing Community**
- **Problem A**: Don't know how to find deals
  - **Attraction**: Deal-finding strategies ($97/mo)
  - **Result**: Finding deals consistently
- **Problem B** (NOW VISIBLE): Need financing to close deals
  - **Discovery**: "I can find deals but can't close them without capital"
  - **Upsell #1**: Financing strategies + lender network ($497)

**Example 2: AI Coaching Community**
- **Problem A**: Don't know how AI can help my business
  - **Attraction**: AI use case library ($97/mo)
  - **Result**: Understands AI potential
- **Problem B** (NOW VISIBLE): Need audience to sell AI services to
  - **Discovery**: "I could offer AI services but I have no audience"
  - **Upsell #1**: Audience building program ($997)

**Example 3: Productivity Community**
- **Problem A**: Feeling overwhelmed, need systems
  - **Attraction**: Task management frameworks ($47/mo)
  - **Result**: Tasks organized
- **Problem B** (NOW VISIBLE): Realize the problem is delegation, not organization
  - **Discovery**: "I'm organized but doing too much myself"
  - **Upsell #1**: Delegation + team building training ($297/mo)

### Skill Application Questions

**To Identify Path**:
1. "What problem does your Skool community solve?" (Problem A)
2. "After solving that, what problem do customers face NEXT?" (Problem B)
3. "Is your upsell solving a NEW problem or a BETTER solution to the SAME problem?"
   - NEW problem → Path 1 (Sequential) or Path 3 (Awareness)
   - BETTER solution → Path 2 (Solution Upgrade)
4. "Do customers already know about Problem B, or do they discover it after joining?"
   - Already know → Path 1
   - Discover after → Path 3

### Validation Rules

**Path 1 (Sequential Problems)**:
- ✅ Problem B must genuinely emerge from solving Problem A
- ❌ Don't fabricate random next problem
- ✅ Customer should naturally ask "What's next?" after solving A

**Path 2 (Solution Upgrades)**:
- ✅ Progression must make logical sense (DIY → DWY → DFY)
- ❌ Don't jump from DIY to DFY without DWY option
- ✅ Each level should be significantly different in support/delivery

**Path 3 (Awareness Creation)**:
- ✅ Problem B must be genuinely invisible at start
- ❌ Don't manufacture fake problems
- ✅ Customer should have "aha moment" realizing B exists

---

## FRAMEWORK 5: SKOOL MODEL SELECTION DECISION TREE

### The 5 Skool Business Models

1. **Free** - Completely free community
2. **Subscription** - Single paid tier (monthly/annual)
3. **Freemium** - Free + 1-2 paid upgrade tiers
4. **Tiers** - 2-3 paid tiers (no free tier)
5. **One-Time Payment** - Single payment for lifetime access

### Decision Tree

#### **Choose FREE if:**
- Building audience (not monetizing yet)
- Lead generation for external offers
- Brand building / thought leadership
- Testing community concept before charging

**Trade-offs**:
- ✅ Highest conversion rates (20%+ signup)
- ❌ No direct revenue from community
- ❌ Can attract tire-kickers

---

#### **Choose SUBSCRIPTION if:**
- Simple single-tier model working well
- Community size < 100 members (too early for complexity)
- Don't need price segmentation yet
- Want simple, proven model

**Trade-offs**:
- ✅ Simple to manage
- ✅ Clear value proposition
- ❌ Leaves money on table (no upsells/downsells)
- ❌ Single conversion point (all-or-nothing)

**When to Upgrade from Subscription:**
- When you have 100+ members AND want to add upsells/downsells
- When you see demand for higher/lower tiers
- When you want to monetize free trial users who won't pay full price

---

#### **Choose FREEMIUM if:**
- Want to preserve free-group conversion rates (20%+)
- Monetize AFTER value demonstration
- Low-friction acquisition is priority
- Have existing free group to monetize

**How It Works**:
- Signup flow: IDENTICAL to free (users don't see pricing until inside)
- Inside: Locked courses/events/benefits show "Unlock with Premium"
- Conversion strategy: Experience value first, THEN upgrade

**Trade-offs**:
- ✅ Preserves high free signup rates
- ✅ Enables "try before you buy" at scale
- ✅ Reduces perceived risk
- ❌ Requires content to tier-lock
- ❌ Some free members never convert

**Ideal For**:
- Stage 1-2 businesses (building customer base)
- Communities with strong value demonstration (courses, events)
- Low CAC strategies (organic, referrals)

---

#### **Choose TIERS if:**
- Want to show value proposition upfront
- Have clear differentiation between tiers
- Ready to sacrifice some conversion for clarity
- Community size 100+ (enough for segmentation)

**How It Works**:
- Signup flow: Shows all tiers IMMEDIATELY when clicking "Join"
- User selects tier (Standard, Premium, VIP) during signup
- Group displays lowest tier price publicly (e.g., "$1/month")

**Trade-offs**:
- ✅ Clear value proposition upfront
- ✅ Enables price segmentation (whales + budget buyers)
- ✅ Professional positioning
- ❌ May reduce conversion rates vs Freemium (unknown - new feature)
- ❌ Pricing friction at signup

**Ideal For**:
- Stage 3-4 businesses (money model dialed in)
- High-value differentiation between tiers
- Professional/B2B communities (buyers expect tiers)

---

#### **Choose ONE-TIME PAYMENT if:**
- Selling courses, workshops, certifications
- Lifetime access offer (no recurring needed)
- Event-based (cohort, bootcamp)
- Want simplicity (no churn management)

**Trade-offs**:
- ✅ High upfront cash collection
- ✅ No churn to manage
- ❌ No recurring revenue
- ❌ Lower LTV than subscriptions

---

### Model Selection Logic

**For Skill to Use:**

```
IF Stage 1 (inconsistent acquisition):
    → Start with Freemium or simple Subscription
    (Freemium if have content to lock, Subscription if starting simple)

IF Stage 2 (revenue < CAC):
    → Consider Freemium (preserves conversion, monetizes inside)
    OR Tiers if have strong differentiation

IF Stage 3 (revenue < 2x CAC):
    → Use Tiers with front-loaded cash mechanisms
    (Tiers + Buy X Get Y, Win Money Back)

IF Stage 4-5 (optimizing LTV / scaling):
    → Tiers with full money model (upsells, downsells, continuity)

```

### Conversion Impact Considerations

**Freemium vs Tiers (Unknown - Test Carefully)**:

**Freemium**:
- Signup conversion: ~20%+ (free-group rates)
- Free → Paid conversion: ~10-20% (inside community)
- Total paid conversion: ~2-4% of visitors

**Tiers**:
- Signup conversion: UNKNOWN (pricing shown upfront may reduce)
- Immediate paid conversion: UNKNOWN (could be higher than Freemium total)
- Total paid conversion: UNKNOWN (new feature, no data yet)

**Recommendation**: If switching from working paid model to Tiers, TEST CAREFULLY and monitor conversion rates closely.

---

## HOW TO USE THESE FRAMEWORKS

### For Stage Diagnosis
1. Ask user for CAC + 30-day revenue + acquisition consistency
2. Apply Framework 1 (5-Stage Evolution) with FIXED sequential logic
3. Output: Stage + reasoning + next milestone

### For Gap Analysis
1. Calculate current 30-day value from Skool metrics
2. Apply Framework 2 (30-Day Cash Maximization)
3. Output: $ gap + mechanism recommendations prioritized by CAC level

### For Upsell Design
1. Ask about customer problem sequence
2. Apply Framework 4 (Problem Sequence & Upsell Mapping)
3. Identify Path 1, 2, or 3
4. Output: Upsell strategy aligned with problem flow

### For Implementation Roadmap
1. Confirm current stage from Framework 1
2. Apply Framework 3 (Sequential Implementation)
3. Recommend MAXIMUM 1-2 mechanisms (not all 15)
4. Output: Start with X, test until reliable, then add Y

### For Model Selection
1. Assess stage, conversion priorities, content availability
2. Apply Framework 5 (Skool Model Selection)
3. Output: Recommended model (Freemium vs Tiers vs Subscription) with reasoning

---

## CRITICAL REMINDERS

1. **CAC is REQUIRED** - All analysis depends on CAC
2. **Stage logic is SEQUENTIAL** - Use ELSE IF, not multiple IFs
3. **Recommend MAX 1-2 mechanisms** - Simple scales, fancy fails
4. **Upsells have 3 paths** - Next problem, better solution, or awareness creation
5. **Test carefully when switching models** - Conversion rates will change

---

**End of Framework Extraction**

These 5 frameworks form the systematic foundation for the Skool Money Model Strategist skill.
