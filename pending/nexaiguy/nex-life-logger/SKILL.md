---
name: nex-life-logger
description: 'Logs browser history, active windows and watched videos locally, then lets your agent answer questions about what you were doing. Use when: Reconstruct workdays for accurate billing and timesheets; Find forgotten websites or videos using natural language search; Analyze weekly productivity patterns and time distribution.'
license: MIT
metadata:
  author: Nex AI
  version: '1.0'
  agensi-slug: nex-life-logger
compatibility: Compatible with SKILL.md-compatible agents including Claude Code, Cursor, and Aider.
---

# Nex Life Logger

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/nex-life-logger). Scripts, extension source, and templates from the original package are not in this folder.

## What it does

- Collects browser history, active window titles and YouTube watch events into a local SQLite index on your own machine.
- Exposes a query layer so an agent can answer what was I doing at 3pm yesterday with the actual activity trail.
- Summarises time per project or per application across a day or a week.
- Keeps every byte local, with LLM features off unless you explicitly configure a provider.

## Use cases

- Reconstructing a workday for timesheets or client billing
- Seeing where your hours actually went this week
- Finding a page or video you visited but cannot name
- A privacy-respecting alternative to cloud time trackers

## Known limitations

Captures activity metadata, not screen content, so it cannot tell you what you typed. Browser support depends on the history format on your machine. LLM features require you to configure a provider yourself, nothing is sent anywhere by default.

## Example

**Request**

What was I doing between 2 PM and 4 PM yesterday?

**Result**

Between 2:00 PM and 4:00 PM yesterday, you were primarily:
- Browsing documentation for React and Tailwind CSS in Chrome.
- Working in VS Code on the 'auth-module' project.
- Watched a 15-minute YouTube video: 'Advanced TypeScript Patterns'.

## Questions

### Where is my activity data stored?

All data is stored in a local SQLite database on your machine. No data is sent to the cloud unless you explicitly configure an LLM provider.

### Does it record my screen or keystrokes?

It currently tracks browser history from major browsers, active window titles, and YouTube watch events. It does not record keystrokes or screen content.

### Can I filter my history by date?

Yes, it provides a search command with filters for dates, activity types (URL, YouTube, App Focus), and specific browsers.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
