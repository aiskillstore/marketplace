# `screenci record`

Use `screenci record` to capture ScreenCI videos from `.screenci.ts` scripts.

Assume the ScreenCI project is already initialized. Add new video scripts under `recordings/`.
If you are creating new videos, remove the starter `recordings/example.screenci.ts` file.

## Commands

```bash
npx screenci record
npx screenci record -c screenci.config.ts
```

## What It Does

- Runs ScreenCI video tests
- Starts the recording pipeline
- Saves output under `.screenci/<video-name>/`
- Produces at least `recording.mp4` and `data.json`

## Connecting to an Account (optional)

`record` needs no account or setup step: without a `SCREENCI_SECRET`, it uploads under a local, anonymous trial session and prints a link to view the result.

To upload straight to an existing organization instead, get `SCREENCI_SECRET` into `screenci/.env` before the final recording (it does not block authoring or testing):

- Pass it to `init` as an argument: `npm init screenci@latest <SCREENCI_SECRET> -- --yes`.
- Or ask the user to copy `SCREENCI_SECRET` from their secrets page into `screenci/.env`. The org secret is shared across projects.

## Runtime Behavior

- Recording runs with local Playwright.
- `record` uploads every successful recording, with or without `SCREENCI_SECRET` set.
- Without an account, or on the free tier, renders include a ScreenCI watermark; after upload `record` prints a link that removes it.
- Playwright arguments can be passed through after the command.
- After a successful `record`, report the URL it printed (starts with the app's domain, e.g. `https://app.screenci.com/record/...`) back to the user so they can open it. Without a `SCREENCI_SECRET`, this is also how they view and claim the anonymous trial recording.

## Recommended Workflow

```bash
# first verify the flow
npx screenci test

# then record
npx screenci record
```

## Workflow

Always run `npx screenci test` until it passes before running `npx screenci record`. Fix failures and rerun until green.

```bash
npx screenci test   # verify selectors, flow, and narration
npx screenci record # capture the final recording
```
