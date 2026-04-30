---
name: dice-easy-apply
description: Automate Dice.com Easy Apply searches and applications with Puppeteer/Chromium, resume and cover-letter uploads, remote-role filtering, and conservative application guardrails.
when_to_use: Use when you need an AI agent to search Dice.com jobs and submit Dice Easy Apply applications from a verified resume and cover letter.
license: MIT
metadata:
  supported_agents:
    - claude-code
    - openclaw
    - hermes
    - codex
    - cursor
    - windsurf
    - goose
    - aider
    - roo-code
    - cline
  tags: [jobs, dice, automation, puppeteer, easy-apply]
---

# Dice Easy Apply Automation

This skill helps an AI coding/operations agent build and run a repeatable Dice.com Easy Apply workflow.

It is intentionally public and credential-free. It contains no usernames, passwords, cookies, private profile paths, or user-specific secrets.

## What it does

- Searches Dice jobs using the explicit Remote workplace filter.
- Focuses on software, web, full-stack, frontend/backend, AI, GenAI, LLM, Claude/OpenAI/Codex-style roles.
- Uses Dice in-site Easy Apply flows only, unless the operator explicitly approves external ATS applications.
- Uploads a verified resume PDF and optional cover-letter PDF.
- Uses a persistent Chromium profile so login can be performed manually once and reused safely.
- Keeps state/log files so daily reruns avoid duplicates.
- Skips roles with explicit onsite/hybrid/local/travel/clearance constraints or unknown required questions.

## Safety rules

- Do not store job-board credentials in scripts, skills, memory, logs, or reports.
- Pass credentials only via one-off environment variables if absolutely necessary, or use a pre-authenticated browser profile.
- Stop for CAPTCHA, MFA, suspicious-login checks, identity verification, or account-security prompts.
- Do not fabricate answers. Skip forms requiring salary expectations, essays, custom cover letters, relocation preferences, travel, or unverifiable facts.
- Treat Dice match percentages as advisory only. Do not skip a role solely because Dice reports a low match score if the role title is inside the resume's wheelhouse.
- Gen AI / Generative AI Engineer should be treated as a software-engineering role when the resume supports web/software/AI work.

## Recommended search URL

Use Dice's remote filter directly, not a radius search:

```text
https://www.dice.com/jobs?filters.workplaceTypes=Remote&filters.easyApply=true&q=<QUERY>
```

For contract/direct-hire filtered searches, add Dice's employment and employer filters:

```text
https://www.dice.com/jobs?filters.easyApply=true&filters.employmentType=CONTRACTS&filters.employerType=Direct+Hire&filters.workplaceTypes=Remote&q=<QUERY>
```

Useful query set:

```text
gen ai engineer
generative ai engineer
llm engineer
ai full stack engineer
frontend ai engineer
web developer
full stack engineer
node react engineer
javascript engineer
typescript engineer
react developer
node.js developer
svelte developer
software engineer
```

## Environment variables

```bash
RESUME_PDF=/absolute/path/to/resume.pdf
COVER_PDF=/absolute/path/to/cover.pdf
CHROME_PROFILE=$HOME/.cache/dice-chrome
STATE_DIR=/tmp/dice-easyapply-daily
MAX_SCAN=120
MAX_APPLY=15
DRY_RUN=1
SEARCHES='gen ai engineer|llm engineer|full stack engineer|react developer'
EMPLOYMENT_FILTER=CONTRACTS
EMPLOYER_TYPE='Direct Hire'
```

## Puppeteer launch pattern

```js
const puppeteer = require('puppeteer');

const browser = await puppeteer.launch({
  headless: false,
  executablePath: process.env.CHROME_BIN || '/snap/bin/chromium',
  userDataDir: process.env.CHROME_PROFILE || `${process.env.HOME}/.cache/dice-chrome`,
  defaultViewport: null,
  args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--start-maximized']
});

let page = await browser.newPage();
page.setDefaultTimeout(30000);
page.on('dialog', async d => {
  try {
    if (d.type() === 'beforeunload') await d.accept();
    else await d.dismiss();
  } catch {}
});
```

## Core workflow

1. Verify local files exist:

```bash
test -f "$RESUME_PDF"
test -f "$COVER_PDF"
```

2. Open Dice with a persistent browser profile and verify login.
3. Search remote Easy Apply roles using the query list.
4. Extract Dice job IDs from `/job-detail/<id>` URLs.
5. Open each job detail page and inspect only the main job description, not footer/recommended-job/sidebar text.
6. Skip explicit onsite/hybrid/local/travel/clearance constraints.
7. Open the wizard:

```text
https://www.dice.com/job-applications/<job-id>/wizard
```

8. Replace any stale/default resume with the verified resume PDF.
9. Upload the cover-letter PDF where Dice supports it.
10. Continue to the review screen.
11. Confirm expected filenames and work authorization are visible.
12. Submit only if no unknown required questions remain.
13. Append a JSONL audit row and save state.

## Suggested state

```json
{
  "seen": {},
  "applied": {},
  "skipped": {},
  "alreadySubmitted": {}
}
```

Write state and logs to:

```text
/tmp/dice-easyapply-daily/state.json
/tmp/dice-easyapply-daily/results.jsonl
```

## Skip reasons

Common skip reasons:

- `not_remote_only_or_has_hybrid_location_text`
- `outside_resume_wheelhouse`
- `external_ats_not_approved`
- `unknown_required_question`
- `captcha_or_verification_required`
- `could_not_attach_resume`
- `could_not_attach_cover_letter`
- `already_submitted`

## Reporting

Report concise results:

```text
Submitted:
- Title — Company — URL

Skipped:
- Title — Company — URL — reason

State: /tmp/dice-easyapply-daily/state.json
Log: /tmp/dice-easyapply-daily/results.jsonl
```

## Pitfalls

- Dice may preselect an older profile resume. Always verify the filename before submitting.
- Dice pages can fire native `beforeunload` dialogs; register a Puppeteer dialog handler and accept beforeunload dialogs.
- Dice may close/detach a page after a submit attempt. If navigation reports `Target closed`, `Session closed`, or `frame was detached`, create a fresh page, re-register the dialog handler, and continue from state.
- Do not let unrelated recommendation/sidebar/footer text cause false remote/hybrid skips.
- Do not overfit to a single resume. Keep search queries and skip rules configurable.
