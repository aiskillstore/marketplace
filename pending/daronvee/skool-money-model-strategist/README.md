# Skool Money Model Strategist - Claude Code Skill

A Claude Code skill that applies Alex Hormozi's $100M Money Models frameworks to design, evaluate, and improve Skool community monetization strategies.

**Created by Daron Vener**

## What This Skill Does

This skill helps Skool community owners:
- Design money models from scratch using Hormozi's 15 mechanisms
- Evaluate current monetization strategies against proven frameworks
- Get CAC-based stage diagnosis (5 stages) and 30-day cash gap analysis
- Receive Skool-specific setup instructions for implementing mechanisms
- Understand sequential implementation (simple scales, fancy fails)

**Core Principle**: Recommend maximum 1-2 mechanisms at a time, test until reliable, THEN add next.

## Key Features

- **5-Stage Business Evolution Framework**: Diagnose where you are (Stage 1-5) based on CAC vs 30-day revenue
- **15 Hormozi Mechanisms**: Complete implementation guide for all mechanisms with Skool setup steps
- **Two-Layer Monetization**: Group-level (how members join) + Classroom-level (what members buy inside)
- **Math Validation**: All financial calculations use deterministic Python code (no LLM arithmetic errors)
- **Progressive Disclosure**: One thing at a time - no information overload
- **Source Citation**: Every recommendation cites exact Hormozi definitions with line numbers

## Installation

This skill works in **three Claude environments**. Choose the method that matches how you use Claude:

### Method 1: Claude Web (claude.ai) - Easiest ⭐

**Best for**: Quick setup, no technical knowledge required

1. **Download the skill**:
   - Go to [Releases](../../releases)
   - Download `Source code (zip)` from the latest release

2. **Upload to Claude**:
   - Go to [claude.ai](https://claude.ai)
   - Click Settings (gear icon, bottom left) → Capabilities
   - Ensure "Code execution and file creation" is **enabled**
   - Scroll to Skills section
   - Click **"Upload skill"**
   - Select the downloaded ZIP file
   - Claude will validate and install automatically

3. **Verify installation**:
   - Start a new chat
   - The skill appears in your Skills list
   - Invoke with: "Use skool-money-model-strategist skill"

**Requirements**: Claude Pro, Max, Team, or Enterprise plan with code execution enabled

---

### Method 2: Claude Desktop - Easy

**Best for**: Native app users, offline access

1. **Download the skill**:
   - Go to [Releases](../../releases)
   - Download `Source code (zip)` from the latest release

2. **Upload to Claude Desktop**:
   - Open Claude Desktop app
   - Go to Settings → Capabilities
   - Ensure "Code execution and file creation" is **enabled**
   - Scroll to Skills section
   - Click **"Upload skill"**
   - Drag and drop the ZIP file or click to browse
   - Claude validates and installs automatically

3. **Verify installation**:
   - Start a new conversation
   - Invoke with: "Use skool-money-model-strategist skill"

**Requirements**: Claude Desktop app installed, Pro/Max/Team/Enterprise plan with code execution enabled

---

### Method 3: Claude Code (CLI) - For Developers

**Best for**: Terminal users, automation workflows, developers

1. **Download the skill**:
   - Go to [Releases](../../releases)
   - Download `Source code (zip)` from the latest release

2. **Extract to skills directory**:
   ```bash
   # Windows
   # Extract to: C:\Users\[YourName]\.claude\skills\skool-money-model-strategist\

   # macOS/Linux
   # Extract to: ~/.claude/skills/skool-money-model-strategist/
   ```

3. **Verify installation**:
   - Open Claude Code in terminal
   - The skill appears in your skills list
   - Invoke with: "Use skool-money-model-strategist skill"

**Requirements**: [Claude Code](https://claude.com/claude-code) installed

**Directory structure after extraction**:
```
~/.claude/skills/skool-money-model-strategist/
├── SKILL.md                  # Main skill definition
├── README.md                 # This file
├── references/               # Hormozi frameworks & Skool knowledge
│   ├── Hormozi-Skool-Money-Models-Reference.md
│   ├── Hormozi-Implementation-Frameworks.md
│   ├── Mechanism-Prerequisites-Matrix.md
│   ├── Mechanism-Definition-Validation.md
│   ├── Skool-Tiers-Feature-Knowledge-Extraction.md
│   ├── Skool-One-Time-Purchases-Addendum.md
│   ├── Tier-Design-Strategies.md
│   └── Conversion-Benchmarks-Guide.md
└── scripts/                  # Python math validation helpers
    └── math_helpers.py
```

---

### Important Notes

- **Custom skills are private** - Only you can see/use skills you upload
- **Code execution required** - Must be enabled in Settings → Capabilities
- **One ZIP per platform** - Same ZIP file works for all three methods
- **Trusted sources only** - Only install skills from sources you trust

## Quick Start

Once installed (in any Claude environment), invoke the skill:

```
"Use skool-money-model-strategist skill to help me design my Skool money model"
```

Or simply:

```
"Use skool-money-model-strategist skill"
```

You'll be asked 5 essential questions:
1. **CAC** (Customer Acquisition Cost)
2. **Skool dashboard metrics** (MRR, paid members, churn, etc.)
3. **Current Skool model** (Free, Subscription, Freemium, Tiers, One-Time)
4. **Classroom one-time purchases** (courses/products members can buy separately)
5. **Primary goal** (Increase 30-day cash, reduce churn, improve conversions)

Then you'll receive:
- Stage diagnosis (1-5)
- 30-day cash gap analysis
- Recommended mechanism(s) with Skool setup steps
- Test plan with success metrics

## The 15 Hormozi Mechanisms

### Category 1: ATTRACTION OFFERS (Get Cash)
1. Win Your Money Back
2. Giveaways
3. Decoy Offer
4. Buy X Get Y Free
5. Pay Less Now vs Pay More Later

### Category 2: UPSELLS (Get More Cash)
6. Classic Upsell
7. Menu Upsell
8. Anchor Upsell
9. Rollover Upsell

### Category 3: DOWNSELLS (Keep Cash)
10. Payment Plans
11. Trials with Penalty
12. Feature Downsells

### Category 4: CONTINUITY (Get Most Cash)
13. Bonus Continuity Offer
14. Continuity Discount Offers
15. Waive Fee Offer

## Key Frameworks

1. **5-Stage Business Evolution**: Progressive implementation - don't bootstrap with full money model
2. **30-Day Cash Maximization**: Make enough from ONE customer to get TWO+ in <30 days
3. **Sequential Implementation**: Simple scales, fancy fails - ONE mechanism → test → next
4. **Problem Sequence Mapping**: Three upsell paths (Next Problem, Solution Upgrade, Awareness Creation)
5. **Skool Model Selection**: Decision tree for choosing the right Skool business model

## Example Use Cases

### Example 1: Early-Stage Owner (Stage 2)
- **Input**: CAC $300, 30-day revenue $97 (monthly subscription only)
- **Output**: Stage 2 diagnosis, gap of $203, recommendation for annual upsell with bonus stacking
- **Result**: 20% take annual → $330/customer → Stage 2 complete

### Example 2: Overwhelmed Owner
- **Input**: "I want 3 tiers, giveaway, annual discount, upsell course, downsell plan, AND loyalty program"
- **Output**: Challenge complexity, recommend ONE mechanism based on stage, sequence remaining for later
- **Result**: Clear next action, no overwhelm, sequential roadmap

## What This Skill Will NOT Do

- Write sales copy (provides structure/positioning only)
- Predict specific conversion/churn rates (uses benchmark ranges)
- Solve non-Skool problems (stays within scope)
- Create content (no courses, emails, GPTs)
- Guarantee results (provides frameworks, not promises)

## Requirements

- **Python 3.x** (for math_helpers.py calculations) - Optional but recommended for validation
- **CAC data** (Customer Acquisition Cost) - Required for stage diagnosis

## Author

**Created by Daron Vener**

## Version

**Current Version**: v1.0.0 (November 2025)

## License

This skill is provided for educational and commercial use by Skool community owners.

## Credits

- **Frameworks**: Alex Hormozi's $100M Offers and $100M Money Models
- **Platform**: Skool community platform
- **Author**: Daron Vener
- **Built with**: Claude Code by Anthropic

---

**Ready to design your Skool money model? Install the skill and let's start with context gathering.**
