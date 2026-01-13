---
name: project-interview
description: "Resources for conversational interviews to create learner profiles. Used by project-interviewer agent during /init."
allowed-tools: Read, Write, AskUserQuestion
---

# Project Interview Skill

This skill provides resources for conducting natural, conversational interviews with learners.

## Core Principle

**One goal**: Gather enough information to create a persona.md that fits the learner.

What to understand:

- What they want to learn (topic)
- Why they want to learn it (motivation, context)
- How much they already know (level)
- What kind of document they want (volume, style)

## Resources

| Resource | Purpose |
| -------- | ------- |
| [conversation-flow.md](conversation-flow.md) | Example conversations for reference |
| [interview-data-template.md](interview-data-template.md) | Template for saving conversation records |

## Approach

Instead of following rigid rules, act like a good counselor:

- Start with open questions
- Read a lot from what the learner says
- Ask more naturally when information is lacking
- Show the profile summary when you've understood enough
- Reflect any corrections they request

## Output

1. **persona.md** - Use template from project-scaffolder skill
2. **interview-data.md** - Save conversation record
3. **project_metadata XML** - Return to calling command
