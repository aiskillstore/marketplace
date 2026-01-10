# 2026-coach

Executive coaching skill that helps you plan your 2026 using research-backed process goals.

## Why Process Goals?

According to [Williamson et al. (2022)](https://doi.org/10.1080/1750984X.2022.2116723) meta-analysis of 27 studies:

| Goal Type | Effect Size | What It Means |
|-----------|-------------|---------------|
| **Process goals** | d=1.36 | Focus on daily behaviors you control 100% |
| Performance goals | d=0.44 | Short-term milestones |
| Outcome goals | d=0.09 | Long-term results |

**Process goals are 15x more effective than outcome goals.**

Why they work:
- **Total control** - You can always send 20 messages
- **Builds self-efficacy** - Small wins compound
- **Reduces anxiety** - Focus on input, not output
- **Fast feedback** - Know daily if you're on track

---

## Installation

### Option A: Claude Code (Recommended)

If you have [Claude Code](https://claude.ai/code) installed, run this in your terminal:

```bash
git clone https://github.com/BayramAnnakov/2026-coach ~/.claude/skills/2026-coach
```

Then use the skill:
```
/2026-coach
```

### Option B: Claude Desktop / Claude.ai (No Installation Needed)

**You don't need to install anything!** Just copy-paste this prompt into Claude:

```
Please act as my executive coach and help me plan my 2026 using the process goals methodology.

Research shows process goals are 15x more effective than outcome goals (Williamson et al. 2022):
- Outcome goal: "Make $100K" (you don't control this)
- Process goal: "Send 20 messages daily" (you control this 100%)

Please guide me through:
1. Discovery - Ask me about my current situation, vision for 2026, what worked/didn't in 2025
2. Create one clear outcome goal (my north star)
3. Break it into quarterly milestones
4. Convert to weekly process goals (behaviors I control)
5. Create daily checklists

At the end, create these files for me:
- 2026_PLAN.md - my annual plan
- COACHING_CONTEXT.md - context for future coaching sessions
- WEEK_01.md - first week's process goals with checkboxes
```

### Option C: Manual Download (Any Platform)

1. Go to https://github.com/BayramAnnakov/2026-coach
2. Click the green **"Code"** button
3. Click **"Download ZIP"**
4. Unzip the folder
5. Move the `2026-coach` folder to `~/.claude/skills/` (create this folder if it doesn't exist)

**Where is ~/.claude/skills/?**
- **Mac:** `/Users/YOUR_USERNAME/.claude/skills/`
- **Windows:** `C:\Users\YOUR_USERNAME\.claude\skills\`
- **Linux:** `/home/YOUR_USERNAME/.claude/skills/`

Note: The `.claude` folder may be hidden. On Mac, press `Cmd+Shift+.` in Finder to show hidden folders.

---

## What It Does

### 1. Discovery Phase
Guides you through 4 rounds of strategic questions:
- **Current State:** Role, stage, resources, constraints
- **Vision:** Where you want to be by Dec 2026
- **Strategy:** What worked/didn't in 2025, biggest bets
- **Process:** Available time, key behaviors, distractions

### 2. Goal Hierarchy
Builds a structured goal system:
```
Outcome Goal (Annual): Clear north star
├── Q1 Milestone
├── Q2 Milestone
├── Q3 Milestone
└── Q4 Milestone
    └── Weekly Process Goals
        └── Daily Behaviors (checkable)
```

### 3. Process Goal Conversion
Transforms outcomes into controllable behaviors:
- "Hit $100K MRR" → "Send 20 outbound messages daily"
- "Write a book" → "Write 500 words before breakfast"
- "Get fit" → "Exercise 30 mins before 9am"

### 4. Creates Tracking Files
- `2026_PLAN.md` - Annual strategic plan with quarterly roadmap
- `COACHING_CONTEXT.md` - Context for ongoing AI coaching sessions
- `WEEK_XX.md` - Weekly process goals with daily checklists

---

## Environment Compatibility

| Environment | How to Use |
|-------------|------------|
| **Claude Code** | Run `/2026-coach` after installation |
| **Claude Desktop** | Use the prompt from Option B above |
| **Claude.ai (web)** | Use the prompt from Option B above |
| **Other AI assistants** | Copy SKILL.md contents as a system prompt |

---

## Companion Skills

For tracking your process goals:
- [ActivityWatch Analysis Skill](https://github.com/BayramAnnakov/activitywatch-analysis-skill) - Track focus time, app switching, deep work sessions

---

## File Structure

```
2026-coach/
├── SKILL.md                              # Main skill definition
├── README.md                             # This file
└── references/
    ├── annual-plan-template.md           # Year plan template
    ├── weekly-plan-template.md           # Weekly checklist template
    └── coaching-context-template.md      # AI coaching context template
```

---

## FAQ

**Q: Do I need to know how to code?**
A: No! Use Option B (just copy-paste the prompt) or Option C (download ZIP).

**Q: Does this work with ChatGPT?**
A: Yes! Copy the prompt from Option B into ChatGPT. It works with any AI assistant.

**Q: What if I don't have Claude Code?**
A: Use Option B - no installation needed, just paste the prompt into claude.ai.

**Q: Where do my plan files get saved?**
A: The AI will create them wherever you specify, or show them in the chat for you to copy.

---

## License

MIT

## Author

[Bayram Annakov](https://github.com/BayramAnnakov)

---

*Perfect timing: It's January 2026 - everyone is goal-setting. Don't wait for "when you have time."*
