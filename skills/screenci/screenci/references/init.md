# `npm init screenci`

Use `npm init screenci -- --yes` to scaffold a new ScreenCI project without prompts.

## Commands

```bash
npm init screenci -- --yes
npm init screenci "My Project" -- --yes
npm init screenci "My Project" -- --verbose
```

## What It Creates

`npm init screenci -- --yes` creates a ready-to-run project in the current directory containing:

```text
screenci.config.ts
recordings/
  example.screenci.ts
package.json
.gitignore
.github/workflows/screenci.yaml (optional)
```

## Requirements

- Node.js 18+ required

## Notes

- `init` can be run at any time, but it is non-destructive and will not re-initialize an existing project. If the project is already initialized (a `screenci/` directory already exists), it fails on purpose and exits with an error like `screenci/ already exists`. That is expected. Do not delete the existing project to force a re-init: continue working with the project that is already there.
- No account or setup token is needed. `record` (see below) uploads under a local, anonymous trial session with no connection step at all.
- If the user already has a `SCREENCI_SECRET` from an existing account, pass it as init's first positional argument and init writes it into `screenci/.env`, so recordings upload straight to their organization instead of an anonymous trial.
- Prefer `--yes` for non-interactive setup. Without it, the command prompts for setup choices and defaults the project name to the current directory name when none is provided. A positional that looks like a `SCREENCI_SECRET` is treated as the secret, not the project name.
- The name is used as the ScreenCI project display name. Files are always created in the current directory.
- `--yes` accepts the defaults.
- `--agent <name>` is passed to the selected skills install command.
- `--verbose` shows more setup output.
- `record` uses local Playwright and uploads with or without `SCREENCI_SECRET` set.

## Typical Flow

```bash
npm init screenci@latest -- --yes  # scaffold, no account needed
npx screenci test   # verify the video works
npx screenci record # capture the final recording and upload
```
