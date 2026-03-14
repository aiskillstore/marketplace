# DB Craft Installation And Prerequisites

## Platform Support

- `Windows` only for the current public package.
- The skill assumes a local DB Craft app can be started from a Windows environment with PowerShell support.

## Required Local Runtime

- `Node.js` must be installed locally and available on `PATH`.
- A local browser is required to open `http://127.0.0.1:3000`.
- PowerShell must be available because the current launcher uses `launch-dbdesigner.ps1`.

## What Users Install Or Prepare

- The local DB Craft application files.
- A working local Node runtime.
- If AI table generation is needed:
  - either configure an API key in `Settings -> AI Config`
  - or use the built-in `Send to Codex` fallback instead of direct model API calls

## First Launch Experience

1. Open the skill.
2. The skill first checks whether `http://127.0.0.1:3000` is already reachable.
3. If the service is already running, the skill reuses it and opens the page directly.
4. If the service is not running, the skill starts the local server and then opens the page.
5. After the page opens, the user should see the current project/workspace path and the active `*.dbmodel.json` model location.

## If The Service Is Not Running

- The skill should try to start the local service automatically.
- If startup succeeds, the page opens normally.
- If startup fails, the user should be told clearly what blocked startup, for example:
  - `Node.js is not installed`
  - the local DB Craft app directory is missing
  - port `3000` is blocked or another unexpected process is using it

## If The Service Starts Slowly

- The skill should wait until `http://127.0.0.1:3000` becomes reachable instead of opening a broken page immediately.
- The user-facing message should say whether DB Craft was:
  - `reused from an existing running service`
  - or `started as a new local service`

## AI Expectations

- AI table generation does not require a server-side `OPENAI_API_KEY` if the user configures a model and key in the DB Craft UI.
- If no key is available, the recommended fallback is `AI Build -> Send to Codex`.

## Marketplace Positioning Notes

- This is a `local visual schema tool`, not a hosted SaaS product.
- The marketplace listing should state clearly that DB Craft opens and operates a local app.
- The marketplace listing should not imply support for macOS or Linux until those startup paths are implemented and tested.
