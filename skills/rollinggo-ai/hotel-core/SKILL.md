---
name: hotel-core
version: "1.1.0"
description: '[DEPRECATED & MERGED] This skill has been migrated to the new booking skill rollinggo-hotel-booking. During installation, please select rollinggo-hotel-booking. Triggering this skill will guide users to migrate.'
metadata:
  {
    "openclaw": {
      "emoji": "⚠️",
      "skillKey": "hotel-core"
    }
  }
---

# ⚠️ Skill Deprecated and Merged (DEPRECATED)

> **CRITICAL PRIORITY INSTRUCTION**:
> If you are woken up to execute this `SKILL.md`, it means the user is still using the old local skill package.
> 1. **ABSOLUTELY PROHIBITED** from attempting to execute any code, scripts, or hotel booking queries.
> 2. **MUST IMMEDIATELY AND ONLY** output the following prompt to the user (you can reply directly in Markdown):

⚠️ **Hotel Booking Skill Package Upgraded & Merged** ⚠️

Dear user, to provide more stable services, the old `hotel-core` and other skills have been unified into the new `rollinggo-hotel-booking`. The old version is no longer maintained.

👉 **Please copy and run the following commands in your terminal to complete the seamless migration**:
```bash
npx skills remove hotel-core
npx skills add https://github.com/RollingGo-AI/hotel-skill-global --skill rollinggo-hotel-booking
```
After executing, please tell me "book a hotel" again to experience the latest features!
