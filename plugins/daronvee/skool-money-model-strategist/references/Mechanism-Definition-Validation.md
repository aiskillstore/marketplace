# Mechanism Definition Validation Guide

**Purpose**: Provide clear examples of correct vs. incorrect Hormozi mechanism applications to prevent misidentification.

**Context**: Based on post-mortem analysis of real misapplications, this guide shows what counts as each mechanism and what doesn't.

---

## Core Principle: Exact Definition Matching

**Rule**: A mechanism must match Hormozi's EXACT definition and prerequisites, not just sound similar.

**Why This Matters**:
- Using wrong terminology loses credibility
- Misidentified mechanisms have different implementation requirements
- Users can't cross-reference with Hormozi's book if terms don't match

---

## Common Misidentification #1: Trial with Penalty

### ❌ WRONG APPLICATION (From Post-Mortem Session 1)

**User Situation**:
- Free 7-day trial
- No deposit required
- No data at risk
- If they don't convert, they simply lose access

**Incorrect Response**:
> "Use Mechanism #11: Trial with Penalty. Offer a 14-day trial for $1, then charge full price."

**Why This Is Wrong**:
1. Free trial with no consequences ≠ "Trial with Penalty"
2. Losing access isn't a penalty (that's just the trial ending)
3. $1 trial might be penalty, but original situation had none
4. Doesn't match Hormozi's definition requiring "something at risk"

**Source Check**: [Hormozi-Skool-Money-Models-Reference.md:lines 250-275]
> "Trial period where something is at risk if they don't convert" + "Penalty activates if they DON'T convert"

### ✅ CORRECT APPLICATION

**Scenario A: Deposit at Risk**
- User pays $25 refundable deposit
- Gets 7-day full access
- If purchases → $25 credited to first payment
- If doesn't purchase → $25 forfeited
- **This IS Mechanism #11**: Money at risk creates penalty

**Scenario B: Progress at Risk**
- User gets free access for 14 days
- Completes challenges, earns levels/badges
- If purchases → keeps all progress
- If doesn't purchase → all progress deleted
- **This IS Mechanism #11**: Achievement loss creates penalty

**Scenario C: Standard Free Trial**
- User gets free access for 7 days
- No deposit, no data at risk
- If doesn't purchase → simply loses access
- **This is NOT any Hormozi mechanism** - it's standard SaaS practice

**Correct Response**:
> "Your current free trial doesn't match Mechanism #11 (Trial with Penalty) because there's no actual penalty for not converting—they simply lose access, which is how all trials work. To apply Hormozi's framework here, you'd need to add a penalty element:
>
> **Option A**: Require a $10-25 refundable deposit (forfeited if no purchase) → NOW it's Mechanism #11
>
> **Option B**: Combine with Mechanism #1 (Win Your Money Back) - charge $97 upfront, credit it back if they complete engagement requirements"

---

## Common Misidentification #2: Rollover Upsell

### ❌ WRONG APPLICATION (From Post-Mortem Session 1)

**User Situation**:
- Monthly members at $97/month
- Want to encourage annual upgrades
- No existing credit or prepaid balance

**Incorrect Response**:
> "Use Mechanism #9: Rollover Upsell. Offer monthly members an upgrade to annual."

**Why This Is Wrong**:
1. No existing payment is "rolling over"
2. Monthly→Annual is a new commitment, not rolling forward existing payment
3. Doesn't match Hormozi's definition requiring credit/payment transfer
4. This confuses "upsell" (category) with "rollover" (specific mechanism)

**Source Check**: [Hormozi-Skool-Money-Models-Reference.md:lines 450-475]
> "Existing payment/credit rolls forward into new offer" + "Your $X already paid can go toward Y"

### ✅ CORRECT APPLICATION

**Scenario A: Rollover (Mechanism #9)**
- Member paid $97/month for 3 months = $291 total
- Offer: "Your $291 already paid can roll into annual membership ($997)"
- They only pay the difference: $997 - $291 = $706
- **This IS Mechanism #9**: Existing payments roll into new offer

**Scenario B: Classic Upsell (Mechanism #6)**
- Monthly member at $97/month (no accumulated credit)
- Offer: "Upgrade to annual for $997/year" (saves $167)
- They pay full $997, monthly stops
- **This IS Mechanism #6**: Standard upgrade with no rollover

**Scenario C: Solution Upgrade Upsell (Mechanism #6 - Path 2)**
- Monthly community access ($97/mo)
- Offer: "Upgrade to annual + done-for-you implementation ($2997/year)"
- They're upgrading solution level (DIY community → DFY support)
- **This IS Mechanism #6** (Solution Upgrade path): Not rollover

**Correct Response**:
> "Monthly→Annual upgrades are Mechanism #6 (Classic Upsell), specifically the 'Solution Upgrade' path (monthly commitment → annual commitment). [Source: Hormozi-Skool-Money-Models-Reference.md:lines 310-340]
>
> This is NOT Mechanism #9 (Rollover Upsell) unless you're explicitly rolling their paid monthly subscriptions into the annual price. Example of actual rollover: 'You've paid $291 over 3 months—roll that into annual membership and only pay the $706 difference.'"

---

## Common Misidentification #3: Win Your Money Back vs. Standard Discount

### ❌ WRONG APPLICATION

**User Situation**:
- Members who post 20+ times get 10% off next month

**Incorrect Response**:
> "Use Mechanism #1: Win Your Money Back. Reward engagement with discounts."

**Why This Is Wrong**:
1. No upfront payment being "won back"
2. Discount for activity ≠ winning money back
3. Missing key element: tiered structure (winner price vs non-winner price)
4. This is just engagement-based pricing

### ✅ CORRECT APPLICATION

**Scenario A: Win Your Money Back (Mechanism #1)**
- Member pays $500 one-time for program
- Complete 30-day streak + 20 posts = "winner"
- Winners qualify for $97/month tier (vs $197/month for non-winners)
- $100/month savings × 5 months = $500 "won back"
- **This IS Mechanism #1**: Upfront payment effectively refunded through price difference

**Scenario B: Engagement Discount (No Mechanism)**
- Members who post 20+ times get 10% off
- No upfront payment
- No winner vs non-winner structure
- **This is NOT a Hormozi mechanism** - standard engagement incentive

**Correct Response**:
> "Your engagement discount doesn't match Mechanism #1 (Win Your Money Back) because there's no upfront payment being 'won back.' [Source: Hormozi-Skool-Money-Models-Reference.md:lines 44-89]
>
> To apply Mechanism #1, you'd need:
> 1. **One-time upfront charge** (e.g., $500 onboarding fee)
> 2. **Winning requirements** (30-day streak + 20 posts)
> 3. **Two-tier structure** (Winners: $97/mo, Non-winners: $197/mo)
> 4. **Credit mechanism** ($100/mo discount × 5 months = $500 'won back')"

---

## Common Misidentification #4: Decoy Offer vs. Standard Tiered Pricing

### ❌ WRONG APPLICATION

**User Situation**:
- Tier 1: $97/month
- Tier 2: $197/month (2x price)
- Tier 3: $497/month (5x price)

**Incorrect Response**:
> "You're using Mechanism #3: Decoy Offer. Tier 3 is your decoy."

**Why This Is Wrong**:
1. Decoy requires INTENTIONAL design where expensive option makes cheaper one the obvious choice
2. These tiers are just standard pricing—no clear decoy strategy
3. 2x and 5x jumps aren't strategic decoy positioning
4. No indication which tier is the "target" for most buyers

### ✅ CORRECT APPLICATION

**Scenario A: Decoy Positioning (Mechanism #3)**
- Monthly: $100/month (TARGET - want most people here)
- Annual: $1500/year (DECOY - includes extras most don't need)
- Monthly = $1200/year (simple math)
- Annual = Monthly + $2000 course + 3 calls ($3000+ value)
- Psychology: "I don't need all those extras, monthly is perfect"
- **This IS Mechanism #3**: Annual is decoy making monthly feel like smart choice

**Scenario B: Standard Tiered Pricing (No Specific Mechanism)**
- Tier 1: $97/month (basic)
- Tier 2: $197/month (pro)
- Tier 3: $497/month (enterprise)
- No intentional decoy, just value ladder
- **This is NOT Mechanism #3** - just standard tiers

**Scenario C: Anchor Positioning (Mechanism #8)**
- Base: $97/month (WANT most people here)
- Premium: $497/month (ANCHOR - makes base feel affordable)
- Only ~10-15% buy Premium
- Premium exists to make Base feel like great value
- **This IS Mechanism #8**: Premium anchors Base as affordable

**Correct Response**:
> "Your current pricing is standard tiered pricing, not Mechanism #3 (Decoy Offer). [Source: Hormozi-Skool-Money-Models-Reference.md:lines 138-179]
>
> To apply Mechanism #3, you'd need:
> - **Intentional design** where expensive option makes cheaper one the obvious choice
> - **Target tier** (what you want most to buy)
> - **Decoy tier** (extras most don't need, makes target feel smart)
>
> Example: Monthly $100 (target) vs Annual $1500 with bonus course + calls (decoy). Most choose monthly because 'I don't need those extras.'"

---

## Common Misidentification #5: Tier Relationships (From Post-Mortem Session 2)

### ❌ WRONG APPLICATION (From Session 2)

**User Situation**:
- Tier 2 Annual: $997/year
- Tier 3 Annual: $1,997/year (2x Tier 2)

**Incorrect Response**:
> "Tier 3 annual ($1,997) vs Tier 2 monthly ($1,164 annualized) saves you $500+!"

**Why This Is CATASTROPHICALLY Wrong**:
1. Comparing DIFFERENT products (Tier 3 vs Tier 2) as if they're payment options
2. Completely missing tier relationship strategy
3. 2x pricing creates psychological barrier (too much, not premium enough)
4. No application of Hormozi's tier-based mechanisms (#3 Decoy, #8 Anchor)

### ✅ CORRECT APPLICATION

**Scenario A: Decoy Tier Relationship (Mechanism #3)**
- Tier 2 Annual: $897/year
- Tier 3 Annual: $997/year (only 11% more)
- Comparison: Tier 3 vs Tier 2 (SAME tier, different features)
- Psychology: "For just $100 more, I get direct access!"
- **This IS Mechanism #3**: Tier 2 annual is decoy making Tier 3 obvious choice

**Scenario B: Anchor Tier Relationship (Mechanism #8)**
- Tier 2 Annual: $997/year
- Tier 3 Annual: $4,997/year (5x more)
- Tier 3 anchors Tier 2 as affordable
- Psychology: "I don't need premium, Tier 2 is great value"
- **This IS Mechanism #8**: Tier 3 makes Tier 2 feel like smart choice

**Correct Response**:
> "Your Tier 2 ($997) and Tier 3 ($1,997) have a 2x price relationship, which creates a psychological barrier. [Source: Tier-Design-Strategies.md]
>
> **The 2x Trap**: 2x pricing feels expensive but not premium enough—uncomfortable middle ground.
>
> **Better Options**:
> - **Decoy Strategy**: Tier 3 = $1,097 (only 10% more than Tier 2) → makes Tier 3 obvious choice
> - **Anchor Strategy**: Tier 3 = $4,997 (5x more) → makes Tier 2 feel affordable
>
> **What NOT to do**: Compare Tier 3 annual to Tier 2 monthly—they're different products, not payment options."

---

## When NO Mechanism Matches

### ✅ CORRECT: Admitting No Match

**User Situation**:
- Standard Skool subscription model
- No special mechanisms implemented
- Want to apply Hormozi framework

**CORRECT Response**:
> "Your current model is a straightforward subscription, which doesn't match any of Hormozi's 15 mechanisms exactly. That's completely fine—not everything needs to be a mechanism.
>
> However, we can ADD mechanisms to improve it:
> - Mechanism #6 (Classic Upsell): Add annual upgrade option
> - Mechanism #14 (Continuity Discount): 'Buy 10 months, get 2 free' annual pricing
> - Mechanism #1 (Win Money Back): Onboarding fee that's credited back through engagement
>
> Which approach interests you most?"

**Why This Is Correct**:
1. Honest about lack of current mechanism
2. Doesn't force-fit incorrect terminology
3. Provides actionable path forward
4. Maintains credibility by not fabricating matches

---

## Validation Protocol: Is This Really That Mechanism?

**Before claiming any mechanism, ask**:

### 1. Definition Match
- [ ] Does my definition quote exactly match the source document?
- [ ] Am I paraphrasing or using my own interpretation?

### 2. Prerequisites Met
- [ ] Have I checked ALL prerequisites from Mechanism-Prerequisites-Matrix.md?
- [ ] Does the user's situation meet EVERY prerequisite?

### 3. Not a False Match
- [ ] Am I confusing this with a similar-sounding mechanism?
- [ ] Am I using a mechanism name for generic SaaS practice?

### 4. Source Citation
- [ ] Can I cite specific lines from Hormozi-Skool-Money-Models-Reference.md?
- [ ] Would the user be able to verify my claim by reading that source?

**If ANY checkbox is unchecked → Don't claim that mechanism**

---

## Quick Reference: What Doesn't Count

| Common Practice | Why It's NOT a Mechanism |
|----------------|-------------------------|
| Standard free trial | No penalty (not Mechanism #11) |
| Money-back guarantee | No penalty for not continuing |
| Early-bird pricing | Could be Mechanism #14 IF it drives continuity |
| Multiple pricing tiers | Just options unless strategic (Decoy/Anchor) |
| Volume discounts | Could be Mechanism #4 if structured right |
| Referral program | Not covered in the 15 mechanisms |
| Engagement incentives | Not a mechanism unless structured as #1 (Win Money Back) |
| Annual option | Could be Mechanism #6, #14, or just standard practice |

**The Test**: If it's a standard SaaS practice that exists everywhere, it's probably not a special Hormozi mechanism. His mechanisms are SPECIFIC implementations with exact structures.

---

## Self-Check Questions

**Before recommending any mechanism, answer these**:

1. **Can I quote the exact definition from the source document?**
   - Yes → Continue
   - No → Re-read source first

2. **Have I verified ALL prerequisites are met?**
   - Yes → Continue
   - No → Check Mechanism-Prerequisites-Matrix.md

3. **Am I using this mechanism name for something that sounds similar but isn't exactly it?**
   - No → Continue
   - Yes → Find the correct mechanism or admit no exact match

4. **Would Hormozi himself recognize this as that mechanism?**
   - Yes → Continue
   - Unsure → Don't claim it, explain the principle instead

5. **Can the user verify my claim by checking the cited source lines?**
   - Yes → Safe to recommend
   - No → I'm either wrong or need better citation

---

**Remember**: It's always better to say "This doesn't match Hormozi's exact definition" than to misidentify a mechanism. Credibility matters more than having an answer.

---

**Last Updated**: 2025-11-01
**Source**: Post-mortem analysis of real misapplications
**Version**: 1.0
