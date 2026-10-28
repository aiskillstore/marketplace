# Preflight Checks

## Flow

> Run once per conversation/task thread, before the first CLI command that
> requires this shared preflight. Do not rerun it for later user turns or
> sub-operations in the same thread. Rerun it only when the CLI requires it,
> the previous preflight action requests a retry, or the user explicitly asks
> to recheck or update the environment.

1. Run: `npx -y @okxweb3/onchainos-installer install --throttle --skill-version <this skill's frontmatter version>`


## Troubleshooting
- **A global install printed `PromptScript does not support global skill installation`** (only with `npx skills add … --yes -g`) → known upstream `npx skills` limitation: the skill files installed correctly. It's safe to ignore.
