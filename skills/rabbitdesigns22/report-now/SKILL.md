---
name: report-now
description: >-
  Load when the user asks for a report, a status or an update ("give me the report", "how are things", "what happened", "status?", "dame el reporte", "¿cómo va?", "¿qué pasó?"). The report must describe the situation RIGHT NOW: the agent first checks the live sources (systems, dashboards, logs, inboxes, files) at this moment, then reports with the exact current time. It never hands back an old report from hours or days ago as if it were current. If it needs a minute to check, it says "let me check now" and then delivers.
license: MIT
---

# Report now

When someone asks "what's the status?", they mean **now**, not the last time you happened to look. An old report presented as current is worse than no report: it hides what broke since.

## 1. Never answer from memory

- Do not paste or summarize a previous report, log entry or note as the answer.
- Old notes are only a map of **what to check**, not the result.
- If checking takes a moment, say one line first: "Checking everything now, I'll report in a minute." Then do it.

## 2. Get the real time

Read the current date and time from the system or a time tool, with the user's time zone. Every report starts with it: "Report as of Thursday 5 Nov, 8:59 pm."

## 3. Check every live source now

For each thing the user cares about (services, clients, campaigns, deployments, tasks), run the cheapest real check:
- service: health endpoint or a test request, now;
- numbers (sales, leads, spend, messages): read them from the source for today and the current period;
- queues and inboxes: what is waiting and since when;
- anything "pending" in the last report: is it still pending?
- errors: logs or alerts since the last check.

Record the time of each check. If a source cannot be reached, say so; do not fill the gap with old data.

## 4. Deliver a serious, complete report

In the user's language, short:

1. **Time of the report** and what was checked.
2. **Bottom line**: one or two sentences. Is everything working? What is the one thing that needs attention?
3. **By area**: per service, client or project: status (ok / warning / broken), the key number for today, what changed since the last report.
4. **Problems found now**: what, since when, impact, what you already did, what is next.
5. **Needs the user**: only decisions or actions only they can take.
6. **Not verified**: anything you could not check, and why.

Compare with the previous report only to say what changed ("since 2 pm: 3 new leads, the payment cleared, the error is gone").

## 5. Rules

- Every number has a source and a time.
- "Unknown" beats "probably fine".
- If something is broken and you can fix it safely, fix it and report it as fixed (with the proof).
- Save the report with its timestamp, so the next one can show what changed.
