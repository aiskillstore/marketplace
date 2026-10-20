# Interactive Playwright Verification

Use this reference in Phase 5.

`Playwright` means standalone Node.js scripts that open the local app, drive the browser with real input, and save screenshots. It does not mean the repo's normal E2E test suite.

## Rules

<interactive_playwright_rules>

### Lifecycle Rules

- Run Phase 5 browser scripts through `task-workflow/scripts/playwright-lifecycle.mjs`.
- The first browser script run must establish lifecycle ownership. Do not run a script against an assumed existing local server and then treat `fetch failed`, redirects, stale data, or stale build output as a reason to manually start or kill servers.
- Use the lifecycle helper as the default owner for Playwright/app-server startup, including repo E2E commands when Phase 6 runs them. Put `pnpm exec playwright test ...` inside helper `--run` by default. Use repo Playwright `webServer` ownership only when the helper cannot own the server for that exact command, and record the reason before running it.
- Discover the repo's expected verification lifecycle from `AGENTS.md`, `package.json`, README/docs, Playwright config, and `tests/e2e` helpers before choosing commands. The expected pattern is a repo-owned setup command that prepares isolated E2E/test state and deterministic seed data, plus a repo-owned server command that starts the app against that isolated state.
- Pass the repo-owned verification server command to the lifecycle helper with `--server` when it exists. If the repo has no named server command for that pattern, use the normal local command only after proving it will run against isolated E2E/test state, not production/live data.
- Do not manually combine server cleanup, server start, sleeps, DB cleanup, and script execution in one shell command.
- Put only isolated repo-owned test/E2E setup such as test DB reset, test migration, or test seed into lifecycle `--setup "..."`; it is bounded and logged before the server starts. Never put production/live DB reset, seed, cleanup, direct SQLite, or verification-only migration in Phase 5 setup.
- Do not set database file/path env vars through helper `--env`, setup, server, or run commands. Do not change the repo's internal E2E/end-to-end database file path. Use the repo's existing E2E/end-to-end database configuration. `.dbs/database.db` is the live workspace/production database; production databases must never be used for testing or fixture setup. Deleting or corrupting live user data can cause the user to lose his job.
- If cleanup is needed, do it as a separate recorded recovery step before the helper run, then run the helper alone.

### Failure Triage Rules

- If a selector/action/assertion times out, first prove the page is in the expected state: URL, no not-found/error screen, required DB or fixture record exists, server log has no route/runtime error, and browser console has no fatal error. Do not rerun the same script while the page state is wrong; fix setup, seed, route, or app state first.
- If the helper times out or produces no useful output, inspect helper setup/server/run logs and readiness evidence before rerunning. The next run must change setup, server command, ready URL, test command, fixture, timeout reason, or diagnostic output.
- If the helper fails once or twice with a diagnosed lifecycle/tooling issue after a corrected invocation, record the helper logs and switch to the smallest fallback that can prove the task: repo Playwright `webServer`, explicit PID/port cleanup, or manual server management.
- If the server appears stale, wrong, or on the wrong port, inspect helper runtime logs/readiness output first; use repo Playwright `webServer` output only for commands where `webServer` owns lifecycle. Put only isolated test DB reset, test migration, test seed, or fixture setup in helper `--setup`, then restart through the lifecycle owner instead of switching to broad process cleanup.
- If manual fallback is unavoidable, keep PID ownership: capture the server PID/log path under `task-workflow/runtime/`, prove readiness, and clean up only that PID/process group. Do not use `nohup`, `disown`, or untracked background servers as the normal fallback.
- Do not run `playwright install` or any browser download command. The lifecycle helper sets `PLAYWRIGHT_BROWSERS_PATH=/ms-playwright` when the cache exists and fails early on a revision mismatch.

### Script Authoring Rules

- Prefer `127.0.0.1` over `localhost`.
- Write scripts under `task-workflow/playwright/`.
- Save screenshots under `task-workflow/screenshots/`.
- Run scripts from clean Node.js processes after each meaningful fix.
- Use normal input APIs such as `click`, `fill`, `press`, `selectOption`, and route navigation.
- Do not use screenshots alone as proof when a visible control needs interaction proof.
- Do not use `page.evaluate(...)` as a substitute for normal user interaction unless inspecting state that cannot be observed otherwise.

</interactive_playwright_rules>

## Lifecycle Helper Pattern

```bash
node task-workflow/scripts/playwright-lifecycle.mjs \
	--setup "pnpm run prepare:e2e" \
	--server "pnpm run start:e2e" \
	--ready-url "http://127.0.0.1:4444" \
	--run "node task-workflow/playwright/verify-main-flow.mjs" \
	--command-timeout-ms 20000
```

`prepare:e2e` and `start:e2e` are example names for the expected repo-owned isolated setup/server pattern. Use those exact commands when the repo provides them. In older repos, map the example to equivalent repo-owned commands or task-local setup that preserves the same isolation. Do not copy this example with raw production `db:migrate`, `seed`, `rm .dbs/database.db`, or any command that writes the live/default database. The helper writes server and command logs under `task-workflow/runtime/`. Cite those paths in the Phase 5 artifact when output is too long to paste directly.

Timeout increases are not a retry strategy. Start with the smallest practical timeout: `15000`-`20000` ms for Phase 5 launch/page-state/custom-script probes and up to `30000` ms for first-run Phase 6 targeted E2E where Playwright runner startup adds overhead. If the run fails with any useful error, assertion output, not-found state, console/runtime error, route error, fixture/DB miss, or helper diagnostic, use that evidence to diagnose; do not retry with a larger timeout. A larger timeout is allowed only when the first run ended only because the timer expired with no useful response or explanation, and only after helper logs, readiness, URL, not-found/error state, required DB/fixture records, server runtime logs, browser console, and network/page state prove the app and test are in the correct state to run. Only then may one rerun use `60000` ms, and never more than `120000` ms for one targeted script/spec. Record timeout values, quiet-run evidence, triage checks, and longer-rerun reasons in the current phase artifact. If one targeted run needs more than two minutes, split the verifier or diagnose lifecycle, setup, fixture, page-state, console, network, or test-design failure before increasing timeout.

## Minimal Script Pattern

```js
import { chromium } from 'playwright';

const targetUrl = process.env.TARGET_URL ?? 'http://127.0.0.1:4444';
const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({
	viewport: { width: 1440, height: 960 }
});
const page = await context.newPage();

try {
	await page.goto(targetUrl, { waitUntil: 'domcontentloaded' });
	await page.screenshot({ path: 'task-workflow/screenshots/home-desktop.png', type: 'png' });
} finally {
	await context.close().catch(() => {});
	await browser.close().catch(() => {});
}
```

## Mobile Pattern

```js
const context = await browser.newContext({
	viewport: { width: 390, height: 844 },
	isMobile: true,
	hasTouch: true
});
```

## Required Coverage

Cover all routes, states, and interactions touched or implied by the task:

- primary navigation
- create/edit/delete flows
- save/cancel flows
- forms and validation
- menus, dialogs, drawers, tabs, and filters
- table/list row actions
- loading, empty, error, and success states when relevant
- responsive visual quality for mobile, tablet, desktop, standard `1920x1080`, and large `2560x1440` desktop when the task changes UI
- no broken UI at required viewports: overlapping controls, clipped content, unreadable text, inaccessible navigation, unusable menus/dialogs, accidental horizontal scrolling, or controls outside the viewport
- no excessive dead space on normal desktop/1080p screens. `2560x1440` may have some extra whitespace, but not broad empty regions that make the UI feel unfinished. Large empty regions are acceptable on 4K/ultrawide only when the content width is intentionally constrained and the screen still looks designed.

## What Does Not Count

- opening the app without interacting
- taking only one screenshot
- testing only mobile, only one desktop size, or skipping `1920x1080`/`2560x1440` when the task changes layout/UI
- relying on stale browser state
- relying only on unit/E2E test runner output
- recording paths that do not exist
- ignoring console/runtime errors discovered during verification
