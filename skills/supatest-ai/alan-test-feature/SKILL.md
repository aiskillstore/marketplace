---
name: alan-test-feature
version: 1.1.1
description: Scope coverage, build a testing strategy, test the feature with agent-browser, capture screenshots/video (always mandatory), upload to S3, and create a structured test report (never skip)
---

## Task: Test Feature & Generate Demo Report

Analyze the current branch's changes, scope the coverage level with the user, build an explicit testing strategy, start the app's dev server, test the feature in a real browser using `agent-browser`, capture screenshots and video (**always — no exceptions**), upload everything to S3, and generate a structured test report (**always — never skip**).

---

## Phase 0: Environment Setup

### 1. Get artifact context IDs

Use the active task context when it is present in the prompt. Otherwise:

- The task ID is available from the `ALAN_TASK_ID` environment variable.
- The conversation ID is available from the `ALAN_SESSION_ID` environment variable.
- Resolve `teamId` with Alan MCP context/tools before creating the report.

When calling `create_test_report`, always pass `taskId`, `conversationId`, and `teamId` explicitly. Do not substitute one ID for another.

### 2. Verify agent-browser is available

`agent-browser` is a **CLI tool** by Vercel Labs (`npm: agent-browser`) — it is NOT a skill or MCP tool. It provides headless browser automation via bash commands (open, click, fill, screenshot, record). In sandboxes it is pre-installed by `runtime-bootstrap.ts`.

```bash
command -v agent-browser >/dev/null 2>&1 && echo "agent-browser: OK" || echo "agent-browser: MISSING"
```

**If missing**, install it:
```bash
npm install -g agent-browser && agent-browser install
```

If installation fails (e.g. no network, no npm), **STOP** and tell the user:
> "agent-browser is not available and could not be installed. Install it manually: `npm install -g agent-browser && agent-browser install`"

Do NOT proceed to Phase 2 without a working `agent-browser` — all browser testing depends on it.

### 3. Create workspace

All captures (screenshots, videos) MUST be written to `/tmp/alan-captures/`.

```bash
mkdir -p /tmp/alan-captures
```

> **CRITICAL — file path rules:**
> - **ONLY** write capture files to `/tmp/alan-captures/`. Never anywhere else.
> - **NEVER** write to `.claude/`, project directories, `reports/`, or any path inside the repo.
> - `.claude/` is a sensitive system directory — writing to it will be blocked and will abort the test run.
> - If you are tempted to create a `reports/` or `screenshots/` folder anywhere other than `/tmp/`, stop and use `/tmp/alan-captures/` instead.

---

## Phase 0.5: Coverage Scoping & Context Gathering (MANDATORY — do before anything else)

**Never skip this phase.** You must understand what the user wants before writing a single test step.

### 1. Ask about coverage level

Use `AskUserQuestion` to ask the user:

```
What level of test coverage do you want for this feature?

- light       — Happy path only. Quick smoke test to verify the main flow works.
- standard    — Happy path + key edge cases + basic error states. (Default)
- comprehensive — Full coverage: happy path, all edge cases, error states, non-happy paths, boundary values, accessibility, responsiveness.

Also: are there any specific flows, known bugs, or risky areas you want me to focus on?
```

Wait for the response before continuing.

### 2. Ask targeted follow-up questions

Based on the feature (which you may not know yet — do a quick `git diff --stat` first to get a hint), use `AskUserQuestion` to ask 1–3 targeted follow-up questions. Examples:

- "Is there an authenticated state I should test? If yes, what test credentials should I use?"
- "Are there any known edge cases or previous bugs related to this feature?"
- "What's the definition of 'working correctly' for this feature — what should I see?"
- "Are there any specific non-happy paths you're concerned about (e.g. invalid input, network errors, empty states)?"
- "Any pages or user roles I should specifically include or exclude?"

**Do not skip questions if context is unclear. Ask. A well-scoped test is 10× more valuable than a blind one.**

### 3. Confirm the plan

After gathering answers, summarize back to the user (no tool call needed — just a short message):
- Coverage level chosen
- Specific areas / flows to focus on
- Any known risks or edge cases to target
- Rough count of test scenarios expected

Only proceed to Phase 1 after this confirmation.

---

## Phase 1: Discover What to Test

### 1. Analyze the branch

Run these commands to understand what changed:

```bash
git log main..HEAD --oneline 2>/dev/null || git log HEAD~5..HEAD --oneline
git diff main...HEAD --stat 2>/dev/null || git diff HEAD~1 --stat
```

Read the actual diff to understand the feature or bug fix. Identify:
- What part of the app is affected (which pages, components, API routes)
- What the expected behavior change is
- What URL path to navigate to for testing

### 2. Discover and start the dev server

Look at the project to figure out how to run it:

1. Read `package.json` — check `scripts.dev`, `scripts.start`, `scripts.serve`
2. Check for `docker-compose.yml` / `docker-compose.yaml` / `compose.yml`
3. Check for `Makefile` (look for `dev` or `serve` targets)
4. Check for `Procfile`, `.env`, `Pipfile`, `requirements.txt`, `Gemfile`
5. Check for framework-specific files: `next.config.*`, `vite.config.*`, `nuxt.config.*`, `angular.json`, `manage.py`, `config/routes.rb`

Start the dev server in the background. Common patterns:
```bash
# Node.js
npm run dev &
# or: pnpm dev &, yarn dev &, npx next dev &, npx vite &

# Python
python manage.py runserver &
# or: flask run &, uvicorn main:app &

# Ruby
bundle exec rails server &

# Docker
docker compose up -d
```

### 3. Wait for the server

Poll until the server is responding:
```bash
# Replace PORT with the discovered port
for i in $(seq 1 30); do
  curl -sf http://localhost:PORT >/dev/null 2>&1 && break
  sleep 2
done
```

Check common ports if unclear: 3000, 5173, 8080, 4200, 8000, 4000, 3001, 8888.

### 4. Determine the app URL

- Parse dev server stdout/stderr for "Local:" or "ready on" messages with URLs
- Check `.env` or `.env.local` for `PORT` or `VITE_PORT` or similar
- Test common ports with `curl -sf http://localhost:PORT >/dev/null`
- If you cannot determine it, ask the user via `AskUserQuestion`

### 5. Summarize before proceeding

Tell the user:
- What you found in the diff (feature/fix summary)
- What URL you will test
- What test scenarios you plan to cover

---

## Phase 1.5: Build Testing Strategy & Create Todos (MANDATORY)

Before opening the browser, you must have an explicit plan. Do not improvise test steps on the fly.

### 1. Draft the testing strategy

Based on:
- The coverage level the user chose in Phase 0.5
- The diff analysis from Phase 1
- The context gathered from the user

Write out the full test plan as a structured list. For each scenario, note:
- **Scenario name** — short label (e.g. "Happy path: create item")
- **Type** — happy path / non-happy path / edge case / error state / visual / navigation
- **Steps** — what to do
- **Expected outcome** — what "pass" looks like
- **Screenshot needed** — yes/no

Coverage requirements by level:
- **light**: happy path only (1–3 scenarios)
- **standard**: happy path + 2–4 non-happy paths + 1–2 error states
- **comprehensive**: happy path + all non-happy paths + all error states + boundary values + empty states + responsiveness + navigation

**Non-happy path examples to consider:**
- Invalid / missing required inputs
- Submitting with no data / empty state
- Duplicate entries (if applicable)
- Permission denied / unauthorized access
- Network error / API failure simulation (if testable)
- Rapid repeated actions (double-click, spam submit)
- Long input strings / special characters
- Back button / browser navigation mid-flow

### 2. Create todos for each scenario

Use `TodoWrite` to create a todo entry for each test scenario so progress is tracked. Each todo should be the scenario name.

### 3. Present the strategy

Output the full testing strategy as a numbered list before proceeding. The user should be able to see exactly what will be tested before Phase 2 starts.

---

## Phase 2: Test with agent-browser

> `agent-browser` is a CLI tool — invoke it via bash, not as an MCP tool or skill.
> Docs: https://github.com/vercel-labs/agent-browser
> Key commands: `open`, `snapshot`, `click`, `fill`, `screenshot`, `record`, `wait`, `find`, `close`

### 1. Open the app

```bash
agent-browser --session test-feature open http://localhost:PORT
agent-browser --session test-feature wait --load networkidle
```

### 2. Start video recording — MANDATORY

**Always start a video recording before any interaction. No exceptions.**

```bash
agent-browser --session test-feature record start /tmp/alan-captures/happy-path.webm
```

If video recording fails for technical reasons, note the failure but continue — screenshots are still required.

### 3. Take initial screenshot — MANDATORY

**Always capture the initial page state before any interaction.**

```bash
agent-browser --session test-feature screenshot /tmp/alan-captures/step-00-initial-state.png
```

### 4. Execute each scenario from the testing strategy

Work through every scenario defined in Phase 1.5. For each scenario:

- Mark the corresponding todo as in-progress
- Use `agent-browser snapshot -i` to discover interactive elements
- Use `agent-browser click @eN`, `agent-browser fill @eN "text"`, etc. to interact
- Use `agent-browser wait --load networkidle` or `agent-browser wait 1500` between actions
- **Take a screenshot after every significant state change** — never go more than 2 meaningful actions without a screenshot:
  ```bash
  agent-browser --session test-feature screenshot /tmp/alan-captures/step-NN-description.png
  ```
  Name screenshots descriptively: `step-02-form-filled.png`, `step-03-submit-clicked.png`, `step-04-success-state.png`
- Re-snapshot after navigation or DOM changes (refs go stale)
- If elements are hard to find by ref, use semantic locators:
  ```bash
  agent-browser --session test-feature find text "Submit" click
  agent-browser --session test-feature find role button click --name "Save"
  ```
- Mark each todo as complete or failed based on outcome

**Mandatory coverage checklist (execute ALL that apply to the coverage level chosen):**

**Happy path (always required):**
- [ ] Main feature flow works end-to-end as expected
- [ ] Success state / confirmation is visible
- [ ] Data is persisted / reflected correctly after action

**Non-happy paths (required for standard + comprehensive):**
- [ ] Empty / missing required inputs — form validation fires, error messages shown
- [ ] Invalid input values — correct rejection, no crash
- [ ] Boundary values — minimum and maximum accepted values
- [ ] Duplicate / conflicting data (if applicable)
- [ ] Unauthorized / permission-denied state (if applicable)
- [ ] Empty list / zero-state view (if applicable)
- [ ] Rapid repeated actions (double-click submit, spam button)
- [ ] Long strings / special characters in text inputs

**Error states (required for standard + comprehensive):**
- [ ] API / network failure behavior (if simulatable)
- [ ] Partial failure — what happens if only part of the action succeeds
- [ ] Graceful degradation — app does not crash, user sees a meaningful message

**Visual & navigation (required for comprehensive):**
- [ ] Layout is correct, no overflow or broken UI
- [ ] Responsive on narrower viewport (resize if possible)
- [ ] Links and navigation work; back button does not break state
- [ ] Loading states / spinners shown while async work is in progress

### 5. Stop recording and clean up

```bash
agent-browser --session test-feature record stop
agent-browser --session test-feature screenshot /tmp/alan-captures/final-state.png
agent-browser --session test-feature close
```

**Keep the recording under 2 minutes.** If the feature requires more exploration, split into multiple recordings (e.g. `happy-path.webm`, `error-states.webm`).

### 6. Fix WebM duration metadata (MANDATORY if ffmpeg is available)

WebM files recorded by agent-browser often have `duration = Infinity` in the container header — the video player then shows 0:00. Fix every `.webm` file by remuxing it through ffmpeg, which reads the entire file, computes the real duration, and writes it into the output header:

```bash
for f in /tmp/alan-captures/*.webm; do
  if command -v ffmpeg >/dev/null 2>&1; then
    ffmpeg -y -i "$f" -c copy "${f%.webm}-fixed.webm" 2>/dev/null \
      && mv "${f%.webm}-fixed.webm" "$f" \
      || echo "ffmpeg remux failed for $f — uploading as-is"
  fi
done
```

If ffmpeg is not available, skip this step and continue — the video will still play, it just won't show the correct duration in the player.

---

## Phase 3: Upload Captures to S3

For each captured file, use the `mcp__alan__get_upload_url` MCP tool to get a presigned S3 URL, then `curl PUT` the file directly to S3.

### Per-file upload flow

1. **Get the file size** (needed by the MCP tool):
   ```bash
   SIZE=$(stat -c%s "/tmp/alan-captures/step-01.png" 2>/dev/null || stat -f%z "/tmp/alan-captures/step-01.png")
   ```

2. **Call the MCP tool** to get a presigned upload URL:
   ```
   Tool: mcp__alan__get_upload_url
   Parameters: {
     "taskId": "<active task ID or value of ALAN_TASK_ID>",
     "filename": "step-01.png",
     "mimeType": "image/png",
     "size": <SIZE from step 1>
   }
   ```
   Returns: `{ "uploadUrl": "https://...", "s3Key": "sandbox-captures/..." }`

3. **Upload the file** to S3 using the presigned URL:
   ```bash
   curl -sf -X PUT "<uploadUrl>" \
     -H "Content-Type: image/png" \
     --data-binary @/tmp/alan-captures/step-01.png
   ```

4. **Save the `s3Key`** — you will pass it to `create_test_report` in Phase 4.

Repeat for each screenshot and video file. Common MIME types:
- Screenshots: `image/png`
- Video recordings: `video/webm`

**If uploads fail**: Continue to Phase 4 anyway — omit the `screenshotUrl`, `videoUrl`, and `screenshotUrls` fields. The structured report is still valuable without media.

---

## Phase 4: Create Structured Test Report (MANDATORY — NEVER SKIP)

**CRITICAL: You MUST call `mcp__alan__create_test_report` to complete this skill. This is non-negotiable.**

- Do NOT output the report as markdown text
- Do NOT summarize findings in chat only
- Do NOT skip this phase for any reason — not because of time, not because uploads failed, not because testing was partial
- The report MUST be persisted via this MCP tool call so the UI renders it as an interactive artifact
- **Skipping this step means the entire test session is wasted and untracked**

If uploads failed in Phase 3, create the report anyway — omit the media URLs but include all steps, issues, and summary text.

Call the `mcp__alan__create_test_report` MCP tool with structured data from your testing.

Gather all the data from the previous phases and call the tool:

```
Tool: mcp__alan__create_test_report
Parameters: {
  "title": "<short description of what was tested>",
  "taskId": "<active task ID or value of ALAN_TASK_ID, if set>",
  "conversationId": "<active conversation ID or value of ALAN_SESSION_ID>",
  "teamId": "<resolved team ID>",
  "branch": "<current branch name from git>",
  "baseBranch": "main",
  "commits": [
    { "sha": "<commit sha>", "message": "<commit message>" }
  ],
  "changedFiles": [
    { "path": "src/components/Feature.tsx", "description": "Added new feature component" }
  ],
  "appUrl": "<the URL you tested>",
  "summary": "<1-2 paragraph summary of what was tested and the outcome>",
  "status": "pass | fail | mixed",
  "steps": [
    {
      "name": "Navigate to feature page",
      "status": "pass | fail | skip",
      "screenshotUrl": "<s3Key from Phase 3 — e.g. sandbox-captures/org/task/step-01.png — omit if upload failed>",
      "notes": "Page loaded correctly"
    }
  ],
  "issues": [
    {
      "title": "Button misaligned on mobile",
      "severity": "critical | high | medium | low",
      "description": "The submit button overflows on viewports < 375px",
      "screenshotUrl": "<s3Key from Phase 3 showing the issue — omit if upload failed>"
    }
  ],
  "videoUrl": "<s3Key from Phase 3 for the happy-path recording — omit if upload failed>",
  "screenshotUrls": ["<s3Key 1 from Phase 3>", "<s3Key 2 from Phase 3>"]
}
```

### Field guidelines

- **status**: "pass" if all steps passed, "fail" if any critical step failed, "mixed" if some passed and some failed
- **steps**: one entry per distinct test action (navigate, click, fill, verify). Include the screenshot URL for that step if you took one.
- **issues**: only include actual problems found. Each issue should have a severity and clear description.
- **screenshotUrls**: flat list of ALL screenshot s3Keys from Phase 3 (for gallery display). Use the `s3Key` field returned by `get_upload_url`, **not** the `uploadUrl`. Omit if no uploads succeeded.
- **commits** and **changedFiles**: from git analysis in Phase 1

### Output

After calling `mcp__alan__create_test_report`, tell the user:
- The test report title, so the user can find the generated artifact in the Alan UI
- A link to the artifact when you have enough context to form one (usually `/teams/<teamId>/docs?artifactId=<artifactId>`)
- A brief summary: what was tested, how many steps passed/failed, any issues found
- List any bugs or concerns discovered during testing

Do not lead with a raw UUID. Only include the artifact/report ID as secondary debug context if no usable title or link is available.

**Do NOT render the full report as markdown. The MCP tool call creates the report as a structured artifact that the UI displays interactively.**
