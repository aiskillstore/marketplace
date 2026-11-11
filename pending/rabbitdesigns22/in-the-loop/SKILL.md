---
name: in-the-loop
description: >-
  Load at the start of every task when several agents, chats or sessions work for the same person or team, and again before reviewing, deploying, reporting or changing anything shared. Each agent reads a shared live board (what the others just did: versions deployed, settings changed, decisions, what the user is working on right now) before acting, and writes one line to it after any change that others should know about. Stops the "I was reviewing the old version" and "I didn't know you already changed that" mistakes. Agents stay informed without stepping into each other's work.
license: MIT
---

# In the loop

When many agents work for the same person, each one sees only its own conversation. One deploys version 2.4 while another keeps reviewing 2.3; one changes a setting and another "fixes" it back. The user then has to repeat the news to every agent. This skill gives all of them one shared, live board.

## The board

One plain file that every agent can read and write, at a fixed path agreed for the workspace (default: `LIVE.md` at the root of the shared workspace). Newest line on top. Each line:

```
YYYY-MM-DD HH:MM (time zone) · AGENT/CHAT · AREA · what changed · how to check it
```

Examples:
```
2026-11-05 20:10 CDMX · Apps supervisor · App A · v1.2.12 live (new "Activate number" button) · /health says 1.2.12
2026-11-05 19:50 CDMX · Apps supervisor · Client B · webhook moved to new domain · read back in the platform: active
2026-11-05 19:30 CDMX · User · working now in the Apps supervisor chat on Client C's WhatsApp setup
```

Keep it short: one line per event, no secrets (never keys, tokens, passwords or personal data), no essays. Trim lines older than 14 days into an archive file.

## 1. Before acting: read the board

At the start of a task, and again right before you review, deploy, report on or change anything shared:
1. Read the top of the board (last 24-48 hours, or since your last read).
2. Note anything that touches your area: new versions, changed settings, decisions, what the user is doing right now.
3. Work from the current state. If the board says v1.2.12 is live, check and review v1.2.12, not what you remember.
4. If the board and reality disagree, trust a live check (health endpoint, version number, file), then fix the board.

## 2. After a change: write one line

Write a line whenever you do something another agent could trip over:
- a deploy or version change;
- a setting, credential location, domain, webhook or integration changed (describe it, never paste secrets);
- a decision the user made that affects other areas;
- something broken that others depend on, or fixed;
- what the user is focused on right now, if it matters to others ("user is setting up Client C, don't message him about C").

Write it **right after** the change, with the real current time, and include how to verify it.

## 3. Stay in your lane

Knowing is not touching. If you see something in another agent's area:
- don't change it;
- if it looks wrong or risky, tell that agent directly (or the coordinator), in one line;
- only tell the user when they must act.

## 4. Never pretend

Don't say "I just noticed you released a new version" about something that is on the board since hours ago: read the board first. If you were not in the loop because you skipped the board, say so plainly and catch up.
