# Skool Tiers Feature - Complete Knowledge Extraction

**Source**: Sam Ovens presenting new Skool tier feature (YouTube transcript)
**Date Extracted**: 2025-10-29
**Purpose**: Understand Skool's tier monetization mechanics for CCGG application

---

## EXECUTIVE SUMMARY

Skool now supports **5 business models** with tier-based monetization, allowing communities to offer multiple pricing tiers with differentiated access to courses, calendar events, and other benefits. The two main models are **Freemium** (free-to-paid upgrades) and **Tiers** (paid tiers upfront).

**Key Innovation**: Members can upgrade/downgrade between tiers seamlessly within the community, with prorated billing and lifetime affiliate attribution.

**Terminology Clarification**:
- **"Freemium"** = The MODEL (free group with paid upgrade tiers)
- **"Premium"** = A TIER NAME (middle tier in Freemium or Tiers models)
- Don't confuse the model name with the tier name!

---

## THE 5 BUSINESS MODELS

### 1. FREE (Default)
- **Description**: Completely free community
- **Signup Flow**: Join freely, no payment required
- **Use Case**: Pure community building, lead generation
- **Nothing Changed**: Identical to old free model

### 2. SUBSCRIPTION (Legacy Model)
- **Description**: Monthly, annual, or monthly + annual pricing
- **Signup Flow**: Pay to join (one tier only)
- **Use Case**: Traditional paid membership
- **Nothing Changed**: Identical to old paid model

### 3. FREEMIUM (Free-to-Paid Upgrade Model)
- **Skool UI Name**: "Freemium"
- **Description**: Free to join + 1-2 paid upgrade tiers
- **Tier Structure**:
  - **Free tier** (required - everyone joins here)
  - **Premium tier** (optional paid upgrade - this is the TIER NAME, not the model name)
  - **VIP tier** (optional higher paid upgrade)
- **Signup Flow**: **Identical to free** - members don't see pricing until inside
- **Conversion Strategy**: Leverage 20%+ free group conversion rates, then upgrade inside
- **No Free Trial**: The free tier IS the free trial

**Key Insight**: Freemium groups APPEAR free on the outside. Members only discover paid upgrades AFTER joining. This preserves high free-group conversion rates while enabling monetization.

**Terminology Note**: Don't confuse "Freemium" (the MODEL) with "Premium" (the TIER NAME). Freemium model has Free → Premium → VIP tiers.

### 4. TIERS (Multi-Paid-Tier Model)
- **Skool UI Name**: "Tiers"
- **Description**: 2-3 paid tiers (no free tier required)
- **Tier Structure**:
  - **Standard tier** (lowest paid tier)
  - **Premium tier** (mid-level paid tier - same TIER NAME as in Freemium, but NO free tier)
  - **VIP tier** (highest paid tier)
- **Signup Flow**: **Members see all tiers IMMEDIATELY** when clicking join
- **Group Price Display**: Shows lowest tier price (e.g., "$1/month" if Standard is $1)
- **Free Trial**: Available (7 days, one-time per member, prevents abuse)

**Key Difference from Freemium**: Tiers are shown UPFRONT during signup (may impact conversion rates - test carefully).

### 5. ONE-TIME PAYMENT
- **Description**: Single one-time payment to join
- **Use Case**: Courses, workshops, lifetime access offers

---

## TIER UNLOCKING MECHANICS

### What Can Be Unlocked by Tier?

1. **Courses** (Classroom)
2. **Calendar Events**
3. **Custom Benefits** (text-based, defined by admin)
   - Services (e.g., "We'll run your Facebook ads")
   - Software access
   - In-person events
   - Coaching calls
   - Merchandise
   - Any custom benefit you define

### How Unlocking Works

**Admin Side**:
- Go to Classroom → Add Course → Private → Select Tier
- Go to Calendar → Add Event → Access → Select Tier
- Can layer multiple unlock mechanisms (e.g., "Level 7 OR Premium tier")

**User Side**:
- Locked content shows "Unlock with Premium" button
- Clicking button takes to `/plans` page (upgrade page)
- After upgrade, content unlocks instantly

**Plans Page**: `yourgroup.com/plans` - Direct link to show all tiers and allow upgrades

---

## PRICING MECHANICS

### Setting Prices

- **Admin**: Click on tier → Set monthly price and/or annual price → Save
- **Example**: Standard = $1/month or $10/year, Premium = $2/month or $20/year
- **Annual Savings**: Automatically calculated and displayed (e.g., "Save 17%")

### Price Changes

**Grandfathering**:
- Existing members stay on old price automatically
- New members see new price
- **NEW Feature**: Members can voluntarily switch to current price via `/plans` page

**Price Change Scenarios**:
- Free → Paid: Free members can now upgrade to paid
- Low → High: Members can upgrade to higher price
- High → Low: Members can downgrade to lower price
- Paid → Free: Members can downgrade to free

**Why This Matters**: Previously, changing prices locked existing members on old price with no way to move them without kicking them out. Now members can switch freely.

### Prorating

**When Upgrading**:
- Unused time in current billing period is credited toward upgrade
- Example: Halfway through $1/month → upgrade to $2/month = 50 cents credit applied
- **Applies To**: Tier upgrades AND monthly → annual switches

**Why This Matters**: Removes friction from upgrading (members aren't penalized for upgrading mid-cycle)

---

## SIGNUP FLOW DIFFERENCES

### Freemium Model Signup
1. User sees group (appears free, no pricing shown)
2. User clicks "Join" → Immediately inside (same as free group)
3. User explores → Discovers locked courses/events → "Unlock with Premium" (Premium = tier name)
4. User clicks → Taken to `/plans` → Chooses tier → Upgrades

**Conversion Strategy**: Use free group's 20%+ conversion rate, then monetize AFTER they've experienced value.

### Tiers Model Signup
1. User sees group → Shows lowest tier price (e.g., "$1/month")
2. User clicks "Join" → **IMMEDIATELY sees tier selection page**
3. User selects tier (Standard, Premium, or VIP) → Enters payment → Joins

**Conversion Impact**: Unknown - new feature. May increase conversion (clear value) OR decrease (payment friction upfront). TEST CAREFULLY.

### Free Trial (Tiers Only)
- Enable 7-day free trial in settings
- All tiers show "Try for Free" during signup
- One free trial per member (prevents abuse)
- Not available for Freemium model (free tier IS the trial)

---

## MEMBER MANAGEMENT

### Viewing Members by Tier

**Members List**:
- Shows tier next to each member name (e.g., "VIP", "Premium", "$1/month")
- Old members (pre-tiers) show legacy price (e.g., "$1/month")
- **Filter by Tier**: Click filter → See all VIP members, all Premium members, etc.

### Migrating Existing Members

**When changing from Subscription → Freemium/Tiers**:

**Existing Paid Members**:
- Admin defines which tier they're treated as (Standard, Premium, or VIP)
- Example: Old $1/month members → Treat as "Standard" tier
- They get access to whatever that tier unlocks

**Existing Free Members**:
- Admin can grant them a tier (Standard, Premium, VIP) OR keep as free
- Example: Grant early free members "Standard" access as loyalty reward

**Can Change Anytime**: Admin can adjust tier assignments whenever needed

---

## UPGRADE/DOWNGRADE FLOWS

### User-Initiated Changes

**How Members Upgrade**:
1. Click locked content → "Unlock with Premium" (Premium = tier name) → Taken to `/plans`
2. Go to Settings → "Change Plan" → Choose new tier
3. Admin sends direct link: `yourgroup.com/plans`
4. Pin post with upgrade instructions

**What Members See on `/plans`**:
- Current plan (e.g., "You're on Free")
- All available tiers with benefits
- Monthly and annual pricing (annual shows savings %)
- "Change Plan" or "Upgrade" button

**Instant Access**: After upgrade, locked content unlocks immediately

### Cancel Flow (Churn Reduction)

**When member tries to cancel**:
1. Popup: "Are you sure you want to cancel? What about changing your plan instead?"
2. If they click "Change Plan" → Taken to `/plans` → Can downgrade instead of cancelling
3. **Goal**: Reduce churn by offering downgrade option (better than full cancellation)

**Downgrade Options**:
- VIP → Premium tier (lower tier)
- Premium tier → Standard tier (lowest tier)
- Any tier → Free (if Freemium model)

---

## AFFILIATE COMMISSIONS

### How Affiliates Work with Tiers

**Commission Rate**: 40% across all tiers (set once, applies everywhere)

**Lifetime Attribution**:
- **14-day last-touch cookie**: Standard cookie window for attribution
- **Locked referral after join**: Once member joins (free OR paid), referral is LOCKED to affiliate
- **Upgrade commissions**: If member upgrades later (even 6 months later), original affiliate gets 40%

**Example Scenario**:
1. Affiliate refers friend to free Freemium group (via affiliate link)
2. Friend joins free tier (affiliate gets nothing yet)
3. Friend upgrades to Premium tier ($50/month) 2 months later → Affiliate gets $20/month (40%)
4. Friend upgrades to VIP tier ($100/month) 6 months later → Affiliate gets $40/month (40%)

**Why This Matters**: Strong incentive to promote free groups with paid tiers. Affiliates can earn commissions without requiring upfront sales.

**Protection**: Once referral is locked, other members can't steal commission by sharing links inside group

---

## SKOOL GAMES INTEGRATION

### How Tiers Affect MRR for Skool Games

**Upgrades Count Toward MRR**:
- Member joins at $50/month → +$50 MRR
- Member upgrades to $100/month same month → +$100 MRR (total $150 MRR)
- **Both count** toward Skool Games leaderboard

**$100/Month Handicap Still Applies**:
- If member pays $1,000/month, only $100 counts toward Skool Games
- Prevents high-ticket communities from dominating leaderboard unfairly

**No Major Changes**: Skool Games mechanics mostly unchanged, upgrades just count as MRR additions

---

## REMOVED FEATURE: ANNUAL UNLOCK

### What Was Removed

**Old Feature**: "Annual Unlock" in Classroom
- Allowed admins to lock courses behind annual payment
- Example: "Upgrade to annual to unlock Advanced Course"

**Why Removed**: Incompatible with multi-tier system (which tier's annual? All three?)

### Migration Path

**Existing Annual Unlock Members**: Still have access (grandfathered)

**New Approach**: Use annual DISCOUNT as incentive (not more features)
- Standard model: Monthly = $10, Annual = $100 (save 17%)
- Premium tiers get same courses, just discounted annual pricing
- **Philosophy**: Like Zoom, Notion, Calendly - annual gives discount, not features

---

## WARNINGS & BEST PRACTICES

### Warnings from Sam Ovens

1. **Changing Models is Dangerous**:
   - If you have successful paid group, BE CAREFUL clicking around
   - Changing to "Free" makes group free → All members can downgrade
   - Test changes carefully, don't experiment on live paid groups

2. **Conversion Rate Risk (Tiers Model)**:
   - Tiers show pricing upfront (may reduce conversion vs. free)
   - Monitor conversion rates after switching
   - Might improve OR worsen - unknown (new feature)

3. **Don't Change Just Because It's New**:
   - If your paid group is working well, DON'T change it
   - New features ≠ better for everyone
   - Only change if you have clear strategy

### Best Practices

1. **Start Simple**:
   - Don't need 3 tiers for 10 members
   - Start with 1 paid tier, add second tier 6 months later
   - Example: Skool stayed at $99/month for 5 years before adding $9/month tier

2. **Freemium Model = Lowest Risk**:
   - Signup flow identical to free (preserves conversion rates)
   - Easiest way to monetize free groups
   - Most common use case

3. **Preview Before Launching**:
   - Click "Preview" button to see `/plans` page
   - Test user experience before going live
   - Add benefits, see exactly what members see

4. **Use `/plans` Link Strategically**:
   - Pin post with upgrade instructions
   - DM members with direct link
   - Mention on calls/webinars: "Go to yourgroup.com/plans"

5. **Annual as Discount, Not Features**:
   - Don't gate features behind annual
   - Use savings % as incentive (e.g., "Save 17%")
   - Follow software industry standard (Zoom, Notion, etc.)

---

## TECHNICAL DETAILS

### UI Changes

**Pricing Settings Page**:
- Select model: Free, Subscription, Premium, Tiers, One-Time
- Set tier prices by clicking on tier → Edit → Save
- Preview button to see member experience
- Treat existing members: Define tier assignments for old paid/free members

**Old Price List Removed**:
- Used to show long list of all historical prices
- Now: Click tier to change, grandfathering handled automatically
- Cleaner interface, less clutter

### Member Settings

**New "Change Plan" Option**:
- Available in member settings (even for free members)
- Takes to `/plans` page
- Shows current plan + upgrade options
- Works for all models (Freemium, Tiers, Subscription)

---

## IMPLEMENTATION IMPLICATIONS FOR CCGG

### Questions to Answer

1. **Model Selection**: Freemium vs. Tiers?
   - Freemium = Free to join, low friction, monetize inside
   - Tiers = Show pricing upfront, clear value prop, may reduce conversions

2. **Tier Structure**: How many tiers? What are they?
   - Standard, Premium, VIP?
   - What's unlocked at each level?

3. **Pricing Strategy**: Monthly? Annual? Both?
   - What's the discount for annual?
   - How to price each tier?

4. **Migration Plan**: Current CCGG members?
   - How to treat existing free members?
   - How to treat existing paid members?

5. **Unlock Strategy**: What gets tiered?
   - Which courses locked by tier?
   - Which events/benefits by tier?

6. **Free Trial**: Yes or no? (Only if using Tiers model)

### Next Steps for CCGG Application

1. Map current CCGG offers to Freemium vs. Tiers models
2. Design tier structure (names, pricing, benefits)
3. Define unlock strategy (courses, events, benefits)
4. Plan migration for existing members
5. Create upgrade messaging and flows

---

## KEY TAKEAWAYS

1. **Freemium = Free-to-Paid**: Free signup, paid upgrades inside (lowest risk)
2. **Tiers = Paid Upfront**: Show pricing immediately (higher risk, test conversion)
3. **Lifetime Affiliate Attribution**: Strong incentive for free group promotion
4. **Seamless Upgrades/Downgrades**: Members can change tiers anytime via `/plans`
5. **Prorating Removes Friction**: No penalty for upgrading mid-cycle
6. **Price Changes Are Flexible**: Free ↔ Paid, High ↔ Low all possible now
7. **Churn Reduction Built-In**: Cancel flow prompts downgrade instead
8. **Start Simple**: 1 tier → prove it → add more tiers later

---

**This is the complete knowledge base for Skool's tier feature. Use this to design CCGG's offer ladder and tier structure.**
