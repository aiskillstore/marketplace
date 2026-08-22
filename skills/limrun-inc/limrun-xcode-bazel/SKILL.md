---
name: limrun-xcode-bazel
description: "Build a Bazel-based iOS / macOS / Apple app on Limrun's remote build execution (RBE) instead of a local Mac, and install it on a remote iOS simulator. Use when the project is a Bazel workspace (MODULE.bazel / WORKSPACE) building rules_apple / rules_swift targets and the user wants to `bazel build` it or run it on a simulator, or when a `--config=limrun` build or install misbehaves. To then tap, type, screenshot, or otherwise interact with the running app, use limrun-ios-simulator. For non-Bazel (plain xcodebuild) projects use limrun-xcode instead."
user-invocable: true
effort: high
---

# Bazel iOS builds on Limrun RBE

Build Bazel Apple projects on Limrun's remote Mac workers — from any environment
(Linux, Windows, macOS, VM, container), no local Xcode. `lim xcode rbe` brings up
a remote RBE stack, tunnels it to a local port, and writes a `.limrun/` config so
`bazelisk build --config=limrun` runs Apple actions remotely. Never fall back to
local Xcode or build tools.

## Auth and CLI

Install if needed: `npm install --global lim`. Auth is `lim login` or
`LIM_API_KEY` (may be set outside the project — don't ask for it just because
it's absent). The CLI is the source of truth: the commands in this skill are
verified, but if a flag errors or you need one not shown here, check
`lim xcode rbe --help` instead of guessing.

## Build

1. From the **Bazel workspace root** (has `MODULE.bazel` / `WORKSPACE`), run
   `lim xcode rbe`. It sets up the instance + `.limrun/` config and **prints the
   exact build command**. The tunnel runs in the background (prints a PID);
   `--no-daemon` keeps it foreground.
2. Run the printed command, e.g.
   `bazelisk --digest_function=sha256 build --config=limrun //App`.

Don't hand-write `.limrun/` or the flags — the CLI generates them for the fleet's
Xcode and your OS. Re-run `lim xcode rbe` (after `--stop`) to refresh after a
fleet Xcode upgrade.

To add your own Bazel flags to the limrun path without editing the generated
config, put them in **`user.limrun.bazelrc`** at the workspace root. The
generated config try-imports it last, so your `build:limrun --…` lines win, and
it survives `lim xcode rbe` regeneration (`.limrun/` does not).

## Run on a simulator

`lim xcode rbe` is build-only; attach a simulator when the user wants to see or
run the app. Check or attach (it installs the last build immediately, so no
rebuild is needed):

```bash
lim xcode get             # is a simulator already attached?
lim ios create --attach   # attach one
```

Add `--no-open` when you have no browser to show the user; it skips opening
the stream URL locally and still prints it for sharing.

If the attach output includes a signed stream URL, share it with the user as a
Markdown link, such as [Live simulator](<signed-stream-url>).

With a simulator attached, every successful `--config=limrun` build automatically
reinstalls and relaunches the app, no separate install step:

```bash
bazelisk --digest_function=sha256 build --config=limrun //App
```

Notes:
- **Attach upfront** if you already know you want a sim: `lim xcode rbe --ios`
  (attaches at startup, removed on `--stop`).
- Auto-install happens server-side from the build's events; there is no
  `lim xcode rbe install` subcommand or `--target` flag. To force a reinstall,
  rebuild (a cache-hit rebuild is seconds).
- It fires when the successful invocation produced a single app, so in a
  multi-app workspace build one app target per invocation (`//App`, not
  `//...`); a multi-app build succeeds but installs nothing.

To tap, type, read the element tree, screenshot, or record the running app,
switch to the **`limrun-ios-simulator`** skill.

## Upload builds as assets

To publish a build as a Limrun asset (preview links, installing on other
simulators, CI artifacts), arm uploads at tunnel start or upload one build
after the fact:

```bash
lim xcode rbe --auto-upload preview/my-app --upload-ttl 24h  # every successful build refreshes the asset
lim xcode rbe upload preview/my-app --ttl 24h                # one-shot: the newest successful build
```

- `--auto-upload` holds for the tunnel's lifetime: each successful
  `--config=limrun` build re-uploads the app under that asset name, no
  post-build step. Upload results land in `.limrun/rbe.log`.
- `rbe upload` runs from the workspace root and needs a background tunnel
  plus at least one successful build; it errors otherwise.
- TTLs are Go durations (`24h`, `30m`; `1d` is invalid) and optional; each
  upload without one pushes the asset's expiry to 14 days from that upload.
- To change the `--auto-upload` config of a running tunnel, `--stop` and
  re-run; the CLI refuses a mismatched re-arm instead of silently ignoring it.
- Preview an uploaded app in a browser at
  `https://console.limrun.com/preview?asset=<name>&platform=ios`.

## Teardown

Stop with **`lim xcode rbe --stop`** (~20s to tear the remote stack down) and delete the instance with **`lim xcode delete <id>`**

## Gotchas

- **Always pass `--digest_function=sha256` before `build`** (use the command the
  CLI prints verbatim). The Limrun cache is SHA256-only; Bazel 9 defaults to
  BLAKE3. It's a startup flag, so it can't live in `--config=limrun`. Symptoms:
  build → `Cannot use hash function BLAKE3 with remote cache`; install →
  `non-SHA256 digest … rebuild with --digest_function=sha256`.
- **Run `lim xcode rbe` from the workspace root**, not a subdirectory — it writes
  `.limrun/` there and fails fast otherwise.
- **A green build doesn't prove remote execution** — cache hits (`action cache
  hit` / `remote cache hit`) make builds pass even with the tunnel gone. To force
  and verify real remote execution, see `references/verify-remote.md`.
- **The printed `.ipa` path won't exist on your machine** — the build command
  carries `--remote_download_outputs=minimal`, which keeps the artifact in the
  instance's cache and downloads nothing. Bazel still prints its usual
  `Target //App:App up-to-date: …/App.ipa` line, but that file is **not** on
  disk. This is expected, not a failed build. With a simulator attached, the
  build auto-installs from the artifact's cache digest (read from the build event
  log, not the local file). Only if you genuinely need the `.ipa` locally, drop
  `--remote_download_outputs=minimal` from the build command and Bazel downloads
  the top-level output; auto-install keeps working either way.
- **A fresh instance can fail the first build with `Lost inputs no longer
  available remotely`** (e.g. `… Assets.car`). It's a transient cache eviction
  between instances, not a code error; Bazel prints `Found transient remote cache
  error, retrying the build...` and the retry succeeds. To avoid hitting it
  mid-demo, pre-warm with a full build right after `lim xcode rbe`.
- **`You don't have permission to save … in "CoreSimulator"`** (actool/ibtool) is
  a fleet-side device gap, not your config. Retry; if it persists, report it to
  Limrun.
- **The project's own Bazel settings can fight RBE** (Xcode pinned via a Starlark
  transition, custom `remote_default_exec_properties`, sandbox-hostile genrules).
  These are per-project, not Limrun bugs — walk
  `references/project-compatibility.md` before concluding RBE is broken.
