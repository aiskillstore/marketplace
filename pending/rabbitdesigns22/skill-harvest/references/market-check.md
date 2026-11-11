# Market check

Goal: never spend a week building what already exists, and never publish a
clone.

## Searches
- At least 3 queries per candidate: the plain task ("whatsapp cloud api"),
  the platform or tool ("meta webhook"), and the outcome ("onboard client
  number").
- `npx skills find "<query>"` — returns name, installs and a skills.sh link.
- Also check the official sources first: `anthropics/skills`,
  `vercel-labs/agent-skills`, and the big community indexes.

## Read before judging
For every result with 1K+ installs, or the top 3 if none has that many:
1. Open its `SKILL.md` (raw GitHub URL from the repo tree API:
   `https://api.github.com/repos/<owner>/<repo>/git/trees/HEAD?recursive=1`).
2. Note its stars, last push date, and what it covers in one line.
3. Ask: does it cover the evidence quotes from step 4? Quote by quote.

## Verdict (write one per candidate)
| Verdict | When | Action |
|---|---|---|
| EXISTS-GOOD | covers most evidence quotes, 1K+ installs or a trusted author | install / point the session to it |
| EXISTS-WEAK | exists but misses a named part of the evidence | build only the missing part; say what it lacks |
| GAP | nothing covers the evidence | may go to the gate |

Measured example (Nov 2026): "WhatsApp Cloud API" had a 681-install skill
that is an API reference (send, webhooks). The user's evidence was about
onboarding a client's number in Meta Business (portfolio, registration PIN,
number already used by another app). Verdict: EXISTS-WEAK, the missing part
is the onboarding and block diagnosis.

Install counts measure popularity, not quality. A 400K-install skill can
still miss your case; a 5-install skill can be excellent. Read it.
