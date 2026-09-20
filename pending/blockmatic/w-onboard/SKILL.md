---
name: w-onboard
description: Get a new developer from clone to a running local app.
disable-model-invocation: true
---

Walk setup using this repository's scripts and docs. Do not open a PR unless asked.

1. Run the documented root setup script (Basilic: `pnpm setup`).
2. Decide local-only vs remote from the development-environments page named in `AGENTS.md`.
3. Start the documented web and API dev command (Basilic: `pnpm dev`).
4. Optional: start mobile with the filter command in the mobile README.
5. Verify the app loads and reaches the API. Point at `/w-pr` when they are ready to publish work.
6. Docs: `/w-docs` if behavior or commands changed.
