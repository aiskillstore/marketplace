---
tags: [nimply]
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill]
---

We're a 6-person agency building an internal tool in Node. When the Nimply sales agent captures a lead from a client's Instagram DMs we want it written into our own Postgres CRM within a minute. We'd also like to pull the full DM transcript for that lead through the API so account managers can read it in our tool. How should we build this, and which API permissions do we need?
