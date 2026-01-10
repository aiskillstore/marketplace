# UX Waiting States Audit

> Audit how web applications handle long-running operations (30+ seconds) using AI-powered browser automation.

Built while improving wait time UX at [onsa.ai](https://onsa.ai) — a multi-agent B2B sales platform where AI agents take 30-60+ seconds to perform real research.

## The Problem

AI agent products often have long wait times. Users feel anxious, abandon operations, or perceive the product as "slow" — even when the wait is justified.

## The Psychology of Waiting

Research shows 5 key factors affect perceived wait time:

1. **Occupied time feels shorter** than unoccupied time (the "watched pot" effect)
2. **Known waits feel shorter** than uncertain waits
3. **Explained waits feel shorter** than unexplained waits
4. **Calm waits feel shorter** than anxious waits
5. **Group waits feel shorter** than solo waits

## The 10-Point Checklist

This audit evaluates:

| # | Category | Question |
|---|----------|----------|
| 1 | Progressive Value | Does user see partial results early? |
| 2 | Heartbeat Indicators | Are there signs system is actively working? |
| 3 | Time Estimation | Does user know how long to wait? |
| 4 | Process Explanation | Does user understand why it takes time? |
| 5 | Sunk Cost Visibility | Does user see accumulated work? |
| 6 | Work While Waiting | Can user do other tasks meanwhile? |
| 7 | Interruptible | Can user get "good enough" results early? |
| 8 | Graceful Degradation | Does partial failure still show results? |
| 9 | Completion Celebration | Is the ending a positive moment? |
| 10 | Anxiety Reduction | Is it clear system hasn't frozen? |

## Installation

### Claude Code Skill

1. Clone this repo or download the files
2. Add the skill to Claude Code:
   - Copy folder to `~/.claude/skills/ux-waiting-audit/`
   - Or import `ux-waiting-audit.skill` via Claude Code settings

3. Invoke with: *"Run a UX waiting audit on [URL]"*

### Manual Use

Use the checklist in [`references/checklist.md`](references/checklist.md) to manually evaluate any application.

## Files

| File | Description |
|------|-------------|
| `SKILL.md` | Main skill definition for Claude Code |
| `references/checklist.md` | Detailed 10-point evaluation criteria with detection scripts |
| `references/report-template.md` | Template for generating audit reports |
| `scripts/capture_state.js` | JavaScript helpers for detecting UI states |

## Usage Example

```
Audit the waiting UX on https://app.example.com

1. Navigate to the dashboard
2. Trigger a report generation (takes ~45 seconds)
3. Evaluate against the UX waiting checklist
4. Generate a report with screenshots and recommendations
```

## Sample Output

The audit generates:
- **Screenshots timeline** at T+0s, T+10s, T+30s, T+Complete
- **Score**: X/10 checklist items addressed
- **Strengths**: What works well
- **Critical gaps**: Missing elements hurting UX
- **Quick wins**: Low-effort, high-impact fixes
- **Priority matrix**: P1/P2/P3 recommendations

## Best-in-Class Examples

Reference implementations of excellent waiting UX:
- **Figma exports**: Progress bar + percentage + file count
- **Notion AI**: Streaming text + cursor animation
- **ChatGPT**: Token-by-token streaming + stop button
- **Linear search**: Instant partial results + refinement
- **Vercel deployments**: Step-by-step progress + logs

## Credits

- Built by [Bayram Annakov](https://linkedin.com/in/bayramannakov)
- Inspired by UX research at [onsa.ai](https://onsa.ai)

## License

MIT
