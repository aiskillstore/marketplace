---
name: chrome-webstore-release-blueprint
description: Guide a user end-to-end through setting up Chrome Web Store API release automation in any repository. Use when asked to walk someone through OAuth/CWS credential setup, refresh token creation, local/CI secret setup, version-based publish automation, and submission status checks.
---

# Chrome Web Store Release Blueprint

Use this skill as a hands-on setup guide. The agent should lead the user step-by-step, ask for confirmations, and only automate the parts that can be done locally/in CI.

## What This Skill Is For

- Helping a user set up Chrome Web Store release automation from scratch.
- Giving clear manual instructions for Google/CWS dashboard steps.
- Implementing repo-side scripts/workflows after the user provides credentials.
- Verifying submission state (`PUBLISHED`, `PENDING_REVIEW`, etc.).

## Agent Behavior Rules

- Treat dashboard/OAuth tasks as user-driven; do not imply you performed them.
- Give one clear step at a time and wait for confirmation before moving on.
- Ask for exact values only when needed, and tell user where each value comes from.
- Mask secrets in logs and never commit secret values to git.
- If `gh` is available, offer secret upload automation; if not, provide manual fallback.

## Step 1: Project Discovery (Before Any Credential Work)

Collect these inputs:

- manifest path containing extension version
- build command
- zip/package command and output file name/path
- CI platform (GitHub Actions by default)
- release branch policy (`main`, tags, or manual dispatch)
- local secret file convention (`.env`, `.env.local`, etc.)

Ask explicitly:
- "Do you want CI to publish only when version changes?"
- "Do you want me to wire GitHub secret upload via `gh`?"

## Step 2: Detailed Credential Walkthrough (User + Agent)

### 2.1 Enable API in Google Cloud

Tell user to open:
- `https://console.cloud.google.com/apis/library/chromewebstore.googleapis.com`

User actions:
1. Select the intended Google Cloud project.
2. Click `Enable` for Chrome Web Store API.

Agent prompt example:
- "When Chrome Web Store API shows as Enabled, tell me and I will move to OAuth setup."

### 2.2 Configure OAuth Consent Screen

Tell user to open one of:
- `https://console.cloud.google.com/apis/credentials/consent`
- If UI redirects, continue in Google Auth Platform consent screen pages.

User actions:
1. Choose `External` user type (for non-Workspace internal apps).
2. Fill app name, support email, developer contact email.
3. Save and continue through scopes unless custom scopes are required.
4. Add your own Google account as a test user if app is in Testing mode.
5. Save.

Agent guidance:
- If user wants stable long-lived refresh token behavior, recommend moving consent screen to Production when ready.

### 2.3 Create OAuth Client

Tell user to open:
- `https://console.cloud.google.com/apis/credentials`

User actions:
1. Click `Create Credentials` -> `OAuth client ID`.
2. Choose application type `Web application`.
3. Add authorized redirect URI exactly:
- `https://developers.google.com/oauthplayground`
4. Create client.

Capture values:
- `CWS_CLIENT_ID`
- `CWS_CLIENT_SECRET`

Agent prompt example:
- "Paste `CWS_CLIENT_ID` and `CWS_CLIENT_SECRET` when ready (I will treat them as secrets)."

### 2.4 Generate Refresh Token (OAuth Playground)

Tell user to open:
- `https://developers.google.com/oauthplayground/`

User actions:
1. Click the settings gear icon.
2. Enable `Use your own OAuth credentials`.
3. Paste `CWS_CLIENT_ID` and `CWS_CLIENT_SECRET`.
4. In Step 1, enter scope:
- `https://www.googleapis.com/auth/chromewebstore`
5. Click `Authorize APIs`.
6. Sign in with the same Google account that owns/publishes the extension.
7. Click `Exchange authorization code for tokens`.
8. Copy refresh token.

Capture value:
- `CWS_REFRESH_TOKEN`

Agent prompt example:
- "Paste `CWS_REFRESH_TOKEN` now. I will only place it in local secret storage/CI secrets."

### 2.5 Capture Store IDs

Capture:
- `CWS_EXTENSION_ID` (the extension item ID from store/developer listing URL)
- `CWS_PUBLISHER_ID` (developer/publisher ID from Chrome Web Store developer account context)

Agent instruction:
- If user is unsure, ask them to open the Chrome Web Store Developer Dashboard and copy IDs from item/account URLs or account details.

### 2.6 Credential Checklist

Do not proceed until all five exist:
- `CWS_CLIENT_ID`
- `CWS_CLIENT_SECRET`
- `CWS_REFRESH_TOKEN`
- `CWS_PUBLISHER_ID`
- `CWS_EXTENSION_ID`

## Step 3: Local Secret File and CI Secret Setup

Create a local template file (no real values committed):

```env
CWS_CLIENT_ID=
CWS_CLIENT_SECRET=
CWS_REFRESH_TOKEN=
CWS_PUBLISHER_ID=
CWS_EXTENSION_ID=
```

Ensure real secret file path is gitignored.

If using GitHub Actions, ask user if `gh` automation is desired.

If yes, verify:

```bash
gh --version
gh auth status
```

If `gh` auth is missing, tell user to run:
- `gh auth login`

Then implement a helper script that:
- reads secret values from local env file
- validates all required keys are present
- supports `--dry-run`
- masks values in dry-run output
- uploads with `gh secret set ... --repo ...`
- fails fast on missing keys/auth

If user declines `gh`, provide manual secret entry checklist for repository settings.

## Step 4: Release Workflow Blueprint (Version-Triggered)

Design the CI workflow around this logic:

1. Read local manifest version.
2. Optionally compare with a secondary version file and fail on mismatch.
3. Exchange refresh token for access token:
- `POST https://oauth2.googleapis.com/token`
4. Fetch CWS status:
- `GET https://chromewebstore.googleapis.com/v2/publishers/<publisherId>/items/<extensionId>:fetchStatus`
5. Extract current published version from:
- `publishedItemRevisionStatus.distributionChannels[0].crxVersion`
6. If local version == published version, skip publish.
7. If version changed:
- build package zip
- upload zip:
  `POST https://chromewebstore.googleapis.com/upload/v2/publishers/<publisherId>/items/<extensionId>:upload`
- handle async upload state with polling when needed
- publish:
  `POST https://chromewebstore.googleapis.com/v2/publishers/<publisherId>/items/<extensionId>:publish`

Treat these publish states as successful submission:
- `PENDING_REVIEW`
- `PUBLISHED`
- `PUBLISHED_TO_TESTERS`
- `STAGED`

## Step 5: Submission Status Checker Blueprint

Create a script dedicated to "what is the latest submission state?".

Required behavior:
- accepts env values (and optional `--env-file`)
- optionally accepts `--manifest` for local version comparison
- supports `--json`
- calls token endpoint + `fetchStatus`
- outputs normalized fields:
  - `itemId`
  - `localVersion`
  - `publishedVersion`
  - `publishedState`
  - `submittedVersion`
  - `submittedState`
  - `upToDate`
  - `pendingReview`
- exits non-zero on auth/API/input errors

Helpful checks to include:
- flag version mismatch between manifest and package metadata
- show whether uploaded version is pending review but not yet published
- print concise human summary when `--json` is not used

## Step 6: Guided Verification Flow

Run this with the user:

1. Confirm status checker runs successfully before release.
2. Bump extension version (patch) in all version sources.
3. Push branch and trigger workflow.
4. Confirm workflow either:
- skips (if no version change), or
- uploads and submits publish.
5. Re-run status checker:
- expect `PENDING_REVIEW` first in many cases
- later expect published channel to match local version

## Troubleshooting Script (What Agent Should Say)

- `invalid_grant`:
- likely wrong/expired refresh token, wrong OAuth client, or wrong account
- `403` from CWS endpoint:
- account lacks publisher permissions for that extension
- workflow no-op:
- local version equals published version by design
- upload failure:
- inspect API response and packaged zip structure/manifest validity
- version mismatch guard failure:
- align all declared version files before publishing

## Practical Links (Share During Guidance)

- Chrome Web Store API overview:
`https://developer.chrome.com/docs/webstore/using-api`
- Publish endpoint:
`https://developer.chrome.com/docs/webstore/publish`
- OAuth Playground:
`https://developers.google.com/oauthplayground/`
- API enablement page:
`https://console.cloud.google.com/apis/library/chromewebstore.googleapis.com`
- Credentials page:
`https://console.cloud.google.com/apis/credentials`

## Guardrails

- Never commit credentials.
- Never hardcode secrets in workflow YAML.
- Never auto-publish every push without version comparison.
- Keep setup instructions explicit and user-confirmed at each manual step.
- Prefer repeatable helper scripts over ad-hoc one-off commands.
