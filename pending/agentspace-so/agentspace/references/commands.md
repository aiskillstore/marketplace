# Agent Space Commands

All commands take the path the user explicitly names. Do not default to `.` unless the user clearly said so.

## Share a folder or file

```bash
ascli share <path>
```

```bash
ascli share <path> --permission edit
```

```bash
ascli share <path> --permission view
```

```bash
ascli share <path> --expires-in-hours 24
```

## Without installing globally

```bash
npx @agentspace-so/ascli@latest share <path> --permission edit
```

## Repo-local (when working inside the agentspace-so monorepo)

```bash
pnpm --filter @agentspace-so/ascli exec tsx src/index.ts share <path>
```

```bash
pnpm --filter @agentspace-so/ascli exec tsx src/index.ts share <path> --permission edit
```

## Check binding status

```bash
ascli status <path>
```

## Notes

- `share` on an unbound path creates a temporary workspace, syncs once, and returns a link — no separate `sync` step is needed for one-off sharing.
- Only the named path is uploaded. All traffic goes to `agentspace.so`.
- Install via `npm install -g @agentspace-so/ascli@latest` if `ascli` is not already on `PATH`. Do not use `curl | bash`.
