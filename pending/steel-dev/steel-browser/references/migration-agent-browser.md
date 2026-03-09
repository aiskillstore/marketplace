# Migration from `agent-browser` to `steel browser`

Use this reference when users bring existing upstream scripts or habits.

## Core migration rule

For most scripts, replace command prefix only:

- Before: `agent-browser <command> ...`
- After: `steel browser <command> ...`

Steel keeps inherited runtime command behavior and adds lifecycle controls.

## Recommended migration process

1. Ensure Steel CLI is installed and authenticated (`steel login` or `STEEL_API_KEY`).
2. Replace command prefixes in scripts.
3. Run smoke validation:
   - `start`
   - `open`
   - `snapshot -i`
   - `stop`
4. Add explicit `--session <name>` for multi-step scripts.
5. If self-hosted, set `--api-url` for deterministic endpoint selection.

## Example conversion

```bash
# Before
agent-browser open https://example.com
agent-browser snapshot -i
agent-browser click @e3
agent-browser get text @e7

# After
steel browser open https://example.com
steel browser snapshot -i
steel browser click @e3
steel browser get text @e7
```

## Steel-native commands to introduce when helpful

- `steel browser start`
- `steel browser stop`
- `steel browser sessions`
- `steel browser live`

These are helpful for explicit session lifecycle management and debugging.

## Auth and environment differences

Cloud mode:

- Use `steel login` locally.
- Use `STEEL_API_KEY` in CI/automation.

Self-hosted mode:

- Prefer `--api-url <url>`.
- Alternative precedence still applies through env/config:
  `STEEL_BROWSER_API_URL`, `STEEL_LOCAL_API_URL`, config file.

## Attach behavior note

If a command already provides `--cdp` or `--auto-connect`, Steel forwards passthrough without adding bootstrap attach flags. Do not combine both flags in one call.

## Security note for logs

`steel browser start` and `steel browser sessions` output display-safe connect URLs with sensitive values redacted. Use session `id` + environment secrets for raw credentialed URLs when needed.
