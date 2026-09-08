# npx -y @insforge/cli posthog setup

One-shot command that ensures the InsForge dashboard has a PostHog connection, then prints the official PostHog wizard command so the user can wire PostHog into their app code in their own terminal.

> ⚠️ **For coding agents:** `npx -y @insforge/cli posthog setup` itself is safe to run from your shell — it just ensures the dashboard connection and exits. **`posthog setup` alone does NOT instrument the app: it writes no env vars and installs no SDK, so zero events flow until the wizard step below happens.** The **wizard command it prints at the end** (`npx -y @posthog/wizard@latest`) is interactive: it prompts on stdin (framework picker), opens a browser for OAuth, and waits for the user to pick a PostHog project. It will **not** work via the agent shell or the `!` prefix — it has to be run in the user's real terminal app (Terminal.app, iTerm, etc.). After `posthog setup` exits, ask the user to switch to their terminal and run:
>
> ```bash
> npx -y @posthog/wizard@latest
> ```
>
> ⚠️ If the user can't run the wizard (headless, or they just want you to do it), wire it manually instead: `posthog setup` prints the connected project's public client API key (`phc_…`) and host in its `Next step` note (also in `--json` output under `connection`). Install the framework's PostHog SDK and set its env vars with those values. The `phc_` key is public by design — it ships in frontend bundles — and using the printed one guarantees events land in the same PostHog project the InsForge Analytics page reads from.
>
> Note: if the InsForge dashboard isn't connected to PostHog yet, `posthog setup` also opens a browser for the user to authorize that step — let the user know to check their browser.

## Availability

InsForge Cloud projects only. Self-hosted backends don't expose `/integrations/posthog/v1/*` and this command won't work there; users on self-hosted should install PostHog directly per [PostHog's docs](https://posthog.com/docs/libraries). If the CLI fails with `PostHog connect flow unavailable (HTTP 404)`, the linked backend doesn't expose this integration — typically a self-hosted backend or the wrong project linked; check `npx -y @insforge/cli current`, or fall back to the direct PostHog install above. On cloud projects, do not substitute a `phc_` key from a separate PostHog account in the app's env — events will flow to PostHog but the InsForge Analytics page reads from a server-side OAuth-backed `posthog_connections` row that only `posthog setup` populates, so the page stays empty even though the integration "looks" wired. Use the key that `posthog setup` prints instead.

## Usage

```bash
cd /path/to/your/app
npx -y @insforge/cli link --project-id <insforge-project-id>   # if not already linked
npx -y @insforge/cli posthog setup
# CLI exits after the dashboard connection is ensured. Then run the wizard
# command it prints (something like `npx -y @posthog/wizard@latest`) in your
# own terminal.
```

| Flag | Description |
|------|-------------|
| `--skip-browser` | Don't auto-open the browser for InsForge's OAuth step; only print the URL (useful for headless / SSH sessions). |

Inherited global flags (e.g. `--json`, `--api-url`) work too — see the main CLI skill.

## What the CLI does in order

1. Reads `.insforge/project.json` from the current directory to find your InsForge project ID
2. Calls cloud-backend `/integrations/posthog/v1/cli-start`. Two outcomes:
   - **Already connected**: dashboard already has a PostHog connection → go straight to step 3
   - **Not connected**: cloud-backend returns an authorize URL. CLI opens it in the browser (unless `--skip-browser`) and polls `/connection` until the dashboard receives the OAuth callback
3. Prints a ⚠️ `Next step` note with the `npx -y @posthog/wizard@latest` command plus the connected project's details (name/id, public `phc_` API key, host) and exits

CLI does NOT spawn the wizard — that's left to the user. The wizard:
- Opens its own browser for PostHog OAuth (independent of step 2)
- Lets the user pick a PostHog project
- Detects the app's framework, installs the SDK, writes env vars, and adds the SDK init / provider code

## Two OAuths, briefly explained

The whole flow involves two OAuths in sequence, both targeting PostHog but for different consumers:

| Step | What it sets up | Driver | What it writes |
|------|-----------------|--------|----------------|
| 2 — InsForge cli-start | Server-side connection so the InsForge dashboard Analytics page can query PostHog on the user's behalf | `npx -y @insforge/cli posthog setup` | `posthog_connections` row in cloud-backend |
| post-step 3 — `@posthog/wizard` | Client-side instrumentation so events flow from the app to PostHog | User runs `npx -y @posthog/wizard@latest` themselves | Env vars + SDK init in the app code |

Practically the user signs in with the same PostHog account both times and ends up on the same PostHog project.

> ⚠️ **Pick the same PostHog project in both OAuths.** The two flows don't auto-coordinate: if step 2 connects InsForge to project A but the wizard installs the SDK pointing at project B, the app will emit events to B while the InsForge Analytics page reads from A — the dashboard will stay empty even though events are visibly flowing in PostHog. Fix: re-run `npx -y @posthog/wizard@latest` and pick the same project that InsForge cli-start connected to. (Re-running `posthog setup` alone won't help — cli-start short-circuits to "connected" once a `posthog_connections` row exists; to change the dashboard-side project, the user has to disconnect in the InsForge dashboard first.)

## Common Mistakes

| Mistake | Solution |
|---------|----------|
| Running `npx -y @insforge/cli posthog setup` outside the linked project directory | The CLI reads `.insforge/project.json` from cwd. Run it from the project root after `npx -y @insforge/cli link --project-id <id>` |
| Headless environment, browser doesn't open for the InsForge OAuth step | Pass `--skip-browser` and copy the printed URL onto a machine with a browser |
| Agent ran `posthog setup` and the wizard command printed at the end was never executed | The wizard is interactive (stdin prompts + browser OAuth) and won't run via agent shell or `!` prefix — the user has to run it in their real terminal app. The InsForge dashboard connection is already in place, but app-code instrumentation is not: no env vars, no SDK, no events. Either have the user run the wizard, or instrument manually with the `phc_` key/host that `posthog setup` printed. |
