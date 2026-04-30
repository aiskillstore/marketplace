---
name: linkedin-easy-apply
description: Automate LinkedIn Easy Apply searches and applications with Puppeteer/Chromium, a verified resume PDF, remote/job-title filtering, stateful daily reruns, and conservative answer guardrails.
when_to_use: Use when you need an AI agent to search LinkedIn jobs and submit LinkedIn Easy Apply applications from a verified resume PDF.
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
  tags: [jobs, linkedin, automation, puppeteer, easy-apply]
---

# LinkedIn Easy Apply Automation

This skill helps an AI coding/operations agent build and run a repeatable LinkedIn Easy Apply workflow.

It is intentionally public and credential-free. It contains no usernames, passwords, cookies, private profile paths, or user-specific secrets.

## What it does

- Searches LinkedIn Jobs with Easy Apply enabled.
- Supports remote-only and location-constrained searches.
- Focuses on configurable role keywords such as AI, LLM, Claude, OpenAI, Codex, full-stack, frontend, backend, web, software, JavaScript, TypeScript, Node, React, and Svelte.
- Opens the LinkedIn Easy Apply flow reliably with a direct apply URL when possible.
- Uploads a verified resume PDF.
- Answers only verified applicant facts.
- Skips unknown required questions, compensation questions, custom essays, or subjective fields.
- Keeps state and JSONL logs so daily reruns avoid duplicates.

## Safety rules

- Do not store LinkedIn credentials in scripts, skills, memory, logs, or reports.
- Prefer a persistent browser profile where the operator logs in manually once.
- Stop for CAPTCHA, MFA, suspicious-login checks, identity verification, or account-security prompts.
- Do not fabricate applicant facts.
- Do not answer custom freeform questions or compensation expectations without operator-provided answers.
- Re-check full job descriptions for hybrid/location constraints before submitting remote-only applications.

## Environment variables

```bash
RESUME_PDF=/absolute/path/to/resume.pdf
CHROME_PROFILE=$HOME/.cache/linkedin-chrome
STATE_DIR=/tmp/linkedin-easyapply-daily
MAX_SCAN=80
MAX_APPLY=10
DRY_RUN=1
SEARCHES='Claude|OpenAI|Codex|LLM engineer|AI engineer|full stack engineer|software engineer'
LOCATION='United States'
REMOTE_ONLY=1
```

## Puppeteer launch pattern

```js
const puppeteer = require('puppeteer');

const browser = await puppeteer.launch({
  headless: false,
  executablePath: process.env.CHROME_BIN || '/snap/bin/chromium',
  userDataDir: process.env.CHROME_PROFILE || `${process.env.HOME}/.cache/linkedin-chrome`,
  defaultViewport: null,
  args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--start-maximized']
});

const page = await browser.newPage();
page.setDefaultTimeout(30000);
page.on('dialog', async d => {
  try {
    if (d.type() === 'beforeunload') await d.accept();
    else await d.dismiss();
  } catch {}
});
```

## Search workflow

Build LinkedIn Jobs URLs using explicit filters:

- `f_AL=true` for Easy Apply.
- Remote filter when remote-only is required.
- Location such as `United States` when requested.
- Configurable keywords matching the resume and target market.

Keep candidates only when the card/page supports the requested constraints and the title/description matches the target role family.

## Direct Easy Apply URL

When a LinkedIn job ID is known, try the direct flow first:

```js
const applyUrl = `https://www.linkedin.com/jobs/view/${jobId}/apply/?openSDUIApplyFlow=true`;
await page.goto(applyUrl, { waitUntil: 'domcontentloaded', timeout: 60000 });
```

If the modal does not open, fall back to clicking visible `Easy Apply` controls across buttons and links.

## Conservative answer rules

Answer only facts that are verified by the resume, profile, or explicit operator instruction:

- Work authorization / eligible to work: yes only if verified.
- Visa sponsorship required: no only if verified.
- Remote willingness: yes only for remote-only searches.
- Years of experience: use resume-backed values or a user-approved mapping.
- Email/phone/location: use existing profile/resume facts.
- Middle name: blank if none provided.

Skip:

- Salary/compensation expectations.
- Cover-letter text prompts.
- Custom essays.
- Relocation/hybrid/travel if not approved.
- Unclear required inputs, radios, or selects.

## Multi-step apply loop

1. Open the apply flow.
2. Detect already-submitted applications.
3. Upload/select the verified resume PDF if needed.
4. Inspect each step's visible inputs/selects/radios.
5. Fill only safe verified answers.
6. Click `Next`, `Review`, then `Submit application` only when no unknown required fields remain.
7. Log submitted/skipped state.

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
/tmp/linkedin-easyapply-daily/state.json
/tmp/linkedin-easyapply-daily/results.jsonl
```

## Reporting

Report concise results:

```text
Submitted:
- Title — Company — URL

Skipped:
- Title — Company — URL — reason

State: /tmp/linkedin-easyapply-daily/state.json
Log: /tmp/linkedin-easyapply-daily/results.jsonl
```

## Pitfalls

- Built-in browser tools often time out on LinkedIn. Puppeteer with Chromium and Xvfb is usually more reliable.
- LinkedIn search cards can say Remote while the description includes hybrid/local constraints. Inspect the full page before applying.
- Broad keyword matching can create bad answers. Avoid treating generic words like `United States` or `comfortable` as approval.
- Direct DOM value assignment may not update React forms. Prefer click/type and dispatch input/change events.
- If a page detaches or a modal closes unexpectedly, create a new page and continue from the state file.
