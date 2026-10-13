---
name: limrun-bazel
description: "The default way to build any Bazel workspace on Limrun: build its iOS and Android targets on Limrun's shared build plane with `lim bazel setup` and `bazel build --config=limrun`, from any environment (Linux, Windows, macOS, VM, container, CI), with one remote cache shared across the organization. Use when the project is a Bazel workspace (MODULE.bazel) with rules_apple or rules_android and the user wants to build it remotely, run the built app on a Limrun simulator or emulator, set up Bazel remote execution in CI, or fix a `--config=limrun` build that fails on authentication, workers, or missing MODULE.bazel lines. limrun-xcode-bazel covers only the legacy `lim xcode rbe` flow; use it only when the workspace already runs on `lim xcode rbe` or the user asks for it. For non-Bazel Android builds, use limrun-gradle."
user-invocable: true
effort: high
---

# Bazel on Limrun's build plane

`lim bazel setup` points a Bazel workspace at Limrun's build plane: Apple
actions run on Limrun's Macs, Android actions on Limrun's Linux workers, and
every build of the organization shares one remote cache. Bazel keeps running
where it already does; no local Xcode or Android SDK is needed for the
remote actions.

## Auth and CLI

Install with npm: `npm install --global lim` (0.44.0 or later). The npm
package also installs `lim-bazel-credentials`, the credential helper Bazel
calls; the standalone tarball and DotSlash builds do not put it on `PATH`,
so Bazel cannot authenticate with them. Auth is `lim login` or `LIM_API_KEY`
(it may already be set even when the shell does not show it; check before
asking). The helper reads only `lim login` or `LIM_API_KEY`, never a key
passed with `--api-key`. The CLI is the source of truth: if a flag errors,
check `lim bazel setup --help` instead of guessing.

## Set up

Run inside the workspace (it walks up to the directory with `MODULE.bazel`):

```bash
lim bazel setup
```

It needs Bazel 8 or later and `rules_apple` or `rules_android` in the root
`MODULE.bazel`. It writes a gitignored `.limrun/` with the `--config=limrun`
configuration and adds a `try-import` to `.bazelrc`. Nothing secret is
written: Bazel asks the credential helper for a short-lived token.

- **Region:** setup picks the closest region that runs a build plane.
  `--region <name>` pins one.
- **Android:** Linux workers need `rules_cc`, `rules_java`, `protobuf` and
  `hermetic_android_toolchains` in the root `MODULE.bazel`. Setup prints the
  missing lines and asks; `--yes` adds them without asking. Without a
  terminal and without `--yes` it stops and prints the lines, so pass
  `--yes` in scripts and CI.
- **Java runtime:** a `--java_runtime_version` already in `.bazelrc` is
  kept; otherwise the limrun config uses `remotejdk_17`.
- Re-run setup after upgrading the CLI or when the workspace starts using
  Apple or Android rules. Do not hand-edit `.limrun/`.

## Build

```bash
bazel build --config=limrun //your:target
```

Build actions run remotely and Bazel downloads only the top-level outputs
(the `.apk` or `.ipa`). Without `--config=limrun`, Bazel builds as before.
Own flags for the limrun path go in `user.limrun.bazelrc` at the workspace
root; the generated config imports it last and it survives re-running setup.

In CI: install `lim` from npm, set `LIM_API_KEY` as a secret, run
`lim bazel setup --yes`, then build with `--config=limrun`.

## Run the app

Build for the simulator or emulator, then install the `.ipa` or `.apk` path
Bazel prints:

```bash
lim ios create && lim ios sync bazel-bin/App/App.ipa
lim android create && lim android install-app bazel-bin/app/app.apk
```

Re-run `lim ios sync` after each rebuild; it sends only the difference. To
drive the running app, use limrun-ios-simulator or limrun-android-emulator.

## Check results

The console's Bazel page (`https://console.limrun.com/bazel`) lists the
organization's builds from every region, with live output for running builds
and the remote cache hit rate per build.

## When a build fails

- **Bazel cannot authenticate** or reports a credential helper error: check
  that `lim-bazel-credentials` is on `PATH` (npm install) and that
  `lim login` or `LIM_API_KEY` is set where Bazel runs.
- **"the build plane could not start a worker"** or **"no linux worker is
  free"**: transient capacity; retry the build.
- **Missing `@androidsdk` or Android toolchain errors:** the `MODULE.bazel`
  lines are missing. Re-run `lim bazel setup` and accept them.
- **Each region keeps its own cache:** the first build in a new region
  starts cold.
