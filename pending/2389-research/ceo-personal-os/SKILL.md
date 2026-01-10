---
name: ceo-personal-os
description: This skill should be used when building a personal productivity or operating system for a CEO, founder, or executive. Triggers on "personal OS", "annual review", "life planning", "goal setting system", "Bill Campbell", "Trillion Dollar Coach", "startup failure patterns", "Good to Great", "Level 5 Leadership", "Buy Back Your Time", "E-Myth", "Customer Development", "Steve Blank", "Small Is Beautiful", "Schumacher", "human-scale", "subsidiarity", "Buddhist economics", "permanence".
---

# CEO Personal Operating System

## Overview

Build a **reflection system**, not a task manager. This is a private, single-user operating system for executives that combines thoughtful frameworks with coaching-style prompts.

**Core principle:** Clarity over productivity theater. No hustle culture. No corporate jargon.

**Tone:** Calm, executive-level, direct, insightful. Like an executive coach, chief of staff, and accountability partner.

## When This Skill Applies

- User wants a "personal operating system" or "personal productivity system"
- Building annual review or goal-setting system for an executive
- Creating reflection frameworks for a CEO/founder
- User mentions any of the 11 frameworks (Campbell, Collins, Blank, Martell, Gerber, Eisenmann, Schumacher, etc.)
- User mentions search vs execute mode, pivot decisions, working ON vs IN business

## First Run: Onboarding Flow

### If No Directory Exists

Say:
> "I'll help you build your personal operating system. This is a reflection system - think executive coach, not task manager.
>
> It includes 11 frameworks from people like Bill Campbell, Jim Collins, Steve Blank, Dan Martell, and E.F. Schumacher, plus 11 coaching-style interview scripts.
>
> **Ready to set it up?**"

Then use TodoWrite to track building the full structure.

### If Directory Exists

Say:
> "Welcome back. What would you like to do?"
> 1. Run a review (daily, weekly, quarterly, annual)
> 2. Run an interview (stress patterns, time audit, failure detection, etc.)
> 3. Update goals (1-year, 3-year, 10-year)
> 4. Explore a framework
> 5. Extract patterns from past reviews

## Required Structure

Create in `ceo-personal-os/`:

```
ceo-personal-os/
├── README.md                    # How to use (personalize in 15 min)
├── principles.md                # User's core operating principles
├── memory.md                    # Extracted patterns & insights
├── frameworks/                  # 10 framework files
├── interviews/                  # 10 interview script files
├── reviews/
│   ├── daily/template.md
│   ├── weekly/template.md
│   ├── quarterly/template.md
│   └── annual/template.md
├── goals/
│   ├── 1_year.md
│   ├── 3_year.md
│   └── 10_year.md
└── uploads/                     # Past reviews for analysis
```

## The 11 Frameworks

Build each from the reference files in `references/frameworks/`:

| Framework | Reference | Focus |
|-----------|-----------|-------|
| Gustin Annual Review | `gustin-annual-review.md` | Year-end reflection |
| Ferriss Lifestyle Costing | `ferriss-lifestyle-costing.md` | TMI calculation |
| Robbins Vivid Vision | `robbins-vivid-vision.md` | 3-year visualization |
| Lieberman Life Map | `lieberman-life-map.md` | 6-domain assessment |
| Campbell Coaching | `campbell-coaching.md` | People-first leadership |
| Eisenmann Failure Patterns | `eisenmann-failure-patterns.md` | Venture health |
| Collins Good to Great | `collins-good-to-great.md` | Level 5 Leadership |
| Martell Buy Back Your Time | `martell-buyback-time.md` | Time reclamation |
| Gerber E-Myth | `gerber-emyth.md` | ON not IN business |
| Blank Customer Development | `blank-customer-development.md` | Search vs execute |
| Schumacher Human-Scale | `schumacher-human-scale.md` | Purpose, permanence, scale |

## Interview Scripts

Use coach-style questions from `references/interviews/interview-scripts.md`:
- Past Year Reflection
- Identity & Values
- Future Self Interview
- Team & People Reflection (Campbell-style)
- Failure Pattern Detection (Eisenmann-style)
- Time Audit (Martell-style)
- Business Role Assessment (Gerber-style)
- Good to Great Assessment (Collins-style)
- Customer Development Check (Blank-style)
- Human-Scale Economics (Schumacher-style)
- Leadership Stress Patterns (McWilliams-informed)

## Review Cadences

| Cadence | Time | Focus |
|---------|------|-------|
| **Daily** | 5 min max | Energy (1-10), one win, one friction, priority for tomorrow |
| **Weekly** | 30-45 min | What moved needle vs. noise, time leaks |
| **Quarterly** | 2-3 hours | Goal progress, all framework checks |
| **Annual** | 4-6 hours | Full Gustin reflection, Life Map, Vivid Vision |

### Quarterly Review Checks

Include in every quarterly review:
- Campbell: "Who have I developed?"
- Eisenmann: "Which failure patterns am I vulnerable to?"
- Collins: "Is the flywheel building momentum?"
- Martell: "Am I in my Production Quadrant?"
- Gerber: "Am I working ON or IN the business?"
- Blank: "Am I searching or executing?"
- Schumacher: "Am I building for permanence or extracting?"
- McWilliams: "What stress patterns showed up?"

## Memory & Pattern Extraction

When user uploads past reviews to `uploads/`:
1. Summarize the document
2. Extract patterns (goals, failures, strengths, themes)
3. Append insights to `memory.md`
4. Reference in future reviews

## Tone Requirements

**DO:** Calm, executive-level, direct, clear, insightful questions, psychologically safe

**DON'T:** Hustle culture ("crush it"), therapy speak ("holding space"), corporate jargon ("synergize"), productivity porn ("10x your output")

## Red Flags - STOP

If you catch yourself:
- Using generic frameworks (Eisenhower, 80/20) instead of specified ones
- Creating a task manager instead of a reflection system
- Skipping memory.md or uploads structure
- Using hustle culture language

**Re-read this skill. Follow the specifications.**

## Framework References

All detailed framework content is in:
- `references/frameworks/` - 10 framework files with full content
- `references/interviews/interview-scripts.md` - All interview questions
