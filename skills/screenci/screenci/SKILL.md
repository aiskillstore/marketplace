---
name: screenci
description: Create, show, and guide with ScreenCI videos in an already-initialized project by editing `.screenci.ts` files and running the Screenci workflow.
allowed-tools:
  - Bash(screenci:*)
  - Bash(npx:*)
  - Bash(npm:*)
---

# ScreenCI Video and Guide Skill

Use this skill when the task is about ScreenCI video recording in an existing project: creating a video, showing a flow as a video, or editing `.screenci.ts` / `screenci.config.ts` files.

Routing:

- If the user gives a URL for video context, use the `playwright-cli` skill first to discover the real page flow, stable selectors, and cookie/consent steps before editing the script.
- If the user gives source code for the target page, browser exploration is usually not needed first.
- If the request is only about application/source-code changes (not recording), do not use this skill.

## Quick Start

The project is already initialized. Add or edit scripts in `recordings/`. If you are creating new videos, remove the starter `recordings/example.screenci.ts`.

```bash
# verify repeatedly until green
npx screenci test

# run a subset with normal Playwright filters
npx screenci test recordings/signup.screenci.ts --grep "fills billing details"

# only record after tests pass
npx screenci record
```

`test` forwards normal `playwright test` arguments and still injects the resolved `screenci.config.ts`. `--config`/`-c` and `--verbose`/`-v` are reserved for the ScreenCI CLI, not forwarded to Playwright.

## What ScreenCI Adds

ScreenCI uses Playwright-style `.screenci.ts` files plus recording helpers:

- `video()` declares one output video per test.
- `hide()` cuts setup and loading sections from the final recording.
- `autoZoom()` follows navigation and click-driven flows with smooth camera motion. Use it for movement between targets.
- `zoomTo()` / `resetZoom()` hold a fixed frame for forms and steady editing sections.
- `video.narration({ ... })` is mandatory (see below).

Use the fixture that matches the requested content instead of working around it:

- `video.values(...)` for app-managed text or localized copy the app does not populate itself.
- `video.audio(...)` for background music or sound effects that should mix under the recording.
- `selected(name, options)` inside `video.overlays(...)` when the video should reuse another ScreenCI-made intro, outro, bumper, or screenshot instead of a repository asset file.

```ts
import { video, voices } from 'screenci'

// Voice is a render option (how narration is spoken), not part of the narration spec.
video.renderOptions({ narration: { voice: { name: voices.Ava } } }).narration({
  en: {
    intro:
      'This video shows how to update your billing details and save the changes.',
    explainForm:
      'We start on the billing page and update the company name, email, and tax ID.',
    saving: 'Now we save the changes and wait for the confirmation message.',
    nextPage:
      'Next, we open the invoices section to confirm the new billing details are in use.',
  },
})('Update billing details', async ({ page, narration }) => {
  await narration.intro()
  await narration.explainForm()
  await narration.saving.start()
  await page.getByRole('button', { name: 'Save changes' }).click()
  await narration.saving.end()
  await narration.nextPage()
  await page.getByRole('link', { name: 'Invoices' }).click()
})
```

### Narration

- Declare `video.narration({ ... })` on every video and speak throughout the demo. Pass a flat `cue -> text` object (shared across languages) or one keyed by language (`en`, `es`, ...).
- The opening line must state the video's purpose, then continue with the walkthrough.
- Trigger cues from the `narration` fixture: `await narration.key()` runs the full line before moving on. Use `await narration.key.start()` when narration should overlap the next action, and `await narration.key.end()` to close that cue later, especially before visible navigation or route changes.
- Use inline speech tags when needed: `[pronounce: ...]`, `[short pause]`, `[medium pause]`, `[long pause]`. Always guide pronunciation for URLs and domains, e.g. `screenci.com [pronounce: screen see eye dot com]`.

## Required Conventions

Every video MUST follow these:

- **Narration on every video, no exceptions.** Videos without narration are not acceptable.
- **Open with the video's purpose** before the step-by-step.
- **Start on the requested page.** The visible video begins on the page the user asked for.
- **Hide initial setup.** Wrap page load, auth, navigation to the start page, loading spinners, and cookie-banner dismissal in `hide()`. After the initial navigation, find and click any cookie consent accept button inside that hidden block.
- **Navigate visibly with clicks** after hidden setup, not `page.goto()`.
- **Prefer mouse-driven selection after typing** into search boxes, comboboxes, autocomplete, or command menus: click the visible result rather than `press('Enter')` when a clickable target exists.
- **Prefer native Playwright APIs over `page.evaluate()`** when a locator method already covers the interaction (e.g. `locator.blur()`).
- **Prefer default action options.** For `autoZoom()` and locator actions (`click`, `fill`, `pressSequentially`, `check`, `selectOption`, ...), start with ScreenCI's defaults. Do not add a separate `click()` before `fill()`/`pressSequentially()` just to focus, and do not add `zoom`/`click`/`position`/timing overrides unless the user asks or the flow clearly needs it.

## Zooming

Prefer stable manual zoom for edit-heavy sections; use `autoZoom()` for movement between targets, and let each `autoZoom()` block finish before a navigation or page change (start a new block on the next page). Keep `autoZoom()` usage sparse: justify each block by movement between targets, not simple text entry.

```ts
// Forms and steady editing: fixed frame.
await zoomTo(page.getByRole('form', { name: /profile settings/i }))
await page.getByLabel('Name').fill('Jane Doe')
await page.getByRole('checkbox', { name: 'Email notifications' }).check()
await page.getByRole('button', { name: 'Save changes' }).click()
await resetZoom()

// Navigation and click-driven flows: follow the movement.
await autoZoom(async () => {
  await page.getByRole('link', { name: 'Reports' }).click()
  await page.getByRole('button', { name: 'Open filters' }).click()
  await page.getByRole('option', { name: 'Last 30 days' }).click()
  await page.getByRole('button', { name: 'Apply' }).click()
})
```

## Connecting to an Account (optional)

`record` needs no account: without a `SCREENCI_SECRET` it uploads under a local, anonymous trial session and prints a link to view the result. Mention this and keep going.

To upload straight to an existing organization, get `SCREENCI_SECRET` into `screenci/.env` before the final `record` (it does not block authoring or testing):

1. **Pass it to init:** `npm init screenci@latest <SCREENCI_SECRET> -- --yes` writes it into `screenci/.env`.
2. **Secrets page:** ask the user to copy `SCREENCI_SECRET` from their secrets page into `screenci/.env`. The org secret is shared across projects. Keep building and testing while they do it; only `record` needs it.

Renders without an account, and renders on the free tier, include a ScreenCI watermark. Do not add a separate upgrade upsell after `record`; report the result URL unless the user asks about plans or watermark removal.

## Recording Workflow

1. Add or edit `.screenci.ts` files in `recordings/` (remove `example.screenci.ts` if creating new videos).
2. Run `npx screenci test` until it passes. Fix selectors/flow/narration and rerun until green.
3. Run `npx screenci record` yourself once tests pass. Do not stop and ask the user to record. It uploads immediately, with or without `SCREENCI_SECRET`.
4. ScreenCI writes `.screenci/<video-name>/recording.mp4` and `data.json` per video.
5. Report the URL `record` printed (starts with the app's domain, e.g. `https://app.screenci.com/record/...`) so the user can open it. Without a `SCREENCI_SECRET`, this is also how they view and claim the anonymous trial recording.

`screenci init` (or `npm init screenci`) scaffolds a new project and fails on purpose if one already exists (`screenci/ already exists`). That is expected: keep working with the existing project, do not delete it to re-init.

## Specific Tasks

- **Recording videos** [references/record.md](references/record.md)
  </content>
  </invoke>
