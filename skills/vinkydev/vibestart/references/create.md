# Creating projects

## Discover and preview

```sh
npx --yes vibestart-cli --help
npx --yes vibestart-cli --list --json
```

Use the current list to resolve supported choices and legal combinations. Ask for missing consequential choices rather than silently selecting a different architecture. The destination must be absent or empty.

Example: a React SPA with Hono, oRPC, SQLite, authentication, and the default extensions:

```sh
npx --yes vibestart-cli create my-app --framework spa --backend hono --api orpc --database sqlite --auth better-auth --desktop none --deployment none --runtime node --package-manager pnpm --addons knip,ultracite --dry-run --json
```

Inspect `ok`, `stack`, `addons`, `packageManager`, `files`, and `nextSteps`. When the resolved plan matches the request, run the same command without `--dry-run`. The `create` keyword is optional. Neither form accepts `--yes`, `--cwd`, or `--full-check`.

If the preview reports `incomplete-stack`, supply the remaining choices. If it reports `illegal-stack`, inspect the reported fixes and choose one consistent with the user's requirements. Do not retry by dropping their requested capabilities.

## Package manager, runtime, and extensions

- pnpm and Node.js are the defaults. Set `--package-manager bun` for Bun dependency management, `--runtime bun` for Hono on Bun, or both. Bun runtime requires Hono; it does not select the runtime of other frameworks or the Vite+ toolchain.
- Running the launcher through `pnpm dlx`, `npx`, or `bunx` does not select the generated project's package manager.
- `--addons knip,ultracite` uses comma-separated IDs. `--addons none` explicitly excludes all extensions. Omitting the flag selects the release's defaults.
- Docker is a deployment choice at creation: `--deployment docker`, not `--addons docker`. For existing projects, use `add docker`.
- Flags with `none` are supported only for optional kinds. Obtain the choices from `--list` rather than inventing values.
- Unit and integration tests always run on Vitest. `--testing` picks the runner of a web project's end-to-end tests: `playwright` (Playwright: fully scripted tests on a stable 1.x API) or `e2e` (TesterArmy e2e: the same scripted tests, plus optional natural-language steps an AI agent runs; before 1.0). Choose from the user's needs, and leave the flag out when they have none: the stack then gets the kind's default from `--list --json`. An API-only project has no end-to-end tests, and the generated tests of either runner need no AI credentials.

## Use a recipe

```sh
npx --yes vibestart-cli create my-app --recipe /actual/path/vibestart.jsonc --dry-run --json
```

Replace the example path. A recipe may be a file, directory, or URL. Stack flags override its choices. A recipe reproduces configuration; it does not preserve business edits. Its `name` and `version` describe the project it came from; the new project records its own.

## Installation and validation

Normal creation writes files, initializes Git, installs dependencies, runs generated setup and `vp fmt`, then runs `vp check`. Inspect returned steps and next steps; it does not run the full `ready` chain by default.

| Option             | Effect                                                                  |
| ------------------ | ----------------------------------------------------------------------- |
| `--dry-run`        | Resolve and list files without writing                                  |
| `--json`           | Emit one JSON object and disable prompts                                |
| `--no-interactive` | Disable prompts; unresolved choices fail                                |
| `--no-git`         | Skip repository initialization                                          |
| `--no-install`     | Write files without installation, setup, formatting, or checks          |
| `--no-check`       | Skip the final `vp check`; installation, setup and formatting still run |

If installation was intentionally skipped, follow the generated `nextSteps` in order when the environment allows it. Maintenance commands do not replace this initial setup.

## JSON and exit codes

Creation returns `ok: true` for success. Failures return `ok: false` with an `error` object containing `code`, `message`, and, where relevant, resolution details. Exit codes are `0` for success, `1` for failure, and `130` for cancellation. Do not assume the maintenance error shape applies to creation.
