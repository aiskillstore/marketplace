# Ensure OKX A2A Communication Ready

Recovery procedure for the OKX A2A communication runtime. Use it only when the environment looks unavailable or uninitialized — e.g. `okx-a2a` is missing, or an `okx-a2a` command (daemon / switch-runtime / agent refresh / setup / session / xmtp-send / user notify) fails with a runtime or plugin error.

Readiness is owned entirely by the `okx-a2a` CLI. This file is just the two steps that install it and let it repair itself; do not reimplement daemon / runtime-switch / plugin logic here.

## Steps

### 1. Ensure `okx-a2a` is installed

```bash
command -v okx-a2a >/dev/null 2>&1 || npm i -g @okxweb3/a2a-node
```

If `npm` is missing, stop and tell the user Node.js + npm are required to bootstrap OKX A2A communication.

### 2. Repair the environment

```bash
okx-a2a doctor --fix --json
```

`doctor --fix` owns everything: package version (beta preserved), daemon start/restart, runtime/provider binding, agent refresh, and OpenClaw/Hermes plugin setup. Read `ready` from its JSON:

- `ready: true` → communication is ready; continue the upstream flow.
- `ready: false` → show `userMessage` and each entry in `nextActions` (its `why` and `command`); the environment needs a user/admin action (e.g. restart the Hermes gateway, bind an AI provider). Complete it, re-run `okx-a2a doctor --fix`, and continue only once `ready: true`.

If `okx-a2a doctor` is an unknown command, the installed build predates it (< 0.1.4, outdated by definition): run `npm i -g @okxweb3/a2a-node@latest`, then repeat step 2.

If either command exits non-zero for any other reason, show its output and stop; do not invent a manual recovery.
