# Making an arbitrary Bazel Apple project build on Limrun RBE

The generated `--config=limrun` is the whole happy path for an idiomatic
rules_apple / rules_swift project. When a build doesn't go green, it's almost
always one of the patterns below — each is a property of *the project's* Bazel
setup, not a Limrun bug. Symptom → cause → what to do.

## What the generated config / fleet already handle (don't re-derive these)

- **apple_support rule `load`s on Bazel 9** — the `.limrun/BUILD` loads
  `xcode_version` / `available_xcodes` / `xcode_config` from apple_support on
  Bazel 9 (where they're no longer native globals) and omits them on Bazel 8
  (where loading them fails). Driven off the workspace `.bazelversion`.
- **Xcode pinned to the fleet's, both remote and local** — the `.limrun/BUILD`
  declares the fleet's Xcode as both the remote AND local version and sets
  `--xcode_version` to it, so the build uses only the fleet's Xcode and resolves
  cleanly (no apple_support "…not available locally" notice). This is the
  "everything runs remotely" stance — see the local-Apple-actions pattern below
  if a project genuinely needs a Mac-local Apple action.
- **`--strategy=SwiftCompile=remote` / `--strategy=Genrule=remote`** — overrides
  the common local pins (rules_swift's worker, standalone genrules).
- **rules_apple `no-remote` / `no-remote-exec` stripped**
  (`--modify_execution_info=.*=-no-remote,.*=-no-remote-exec`): bundling,
  linking, and signing actions that rules_apple (or a repo's recommended
  `+no-remote` bazelrc) pins local are stripped so they run on the worker.
  Without this they fail on a thin (e.g. Linux) client with `cannot be executed
  with any of the available strategies: [remote]`.
- **A workspace `--remote_cache` is cleared** (`--remote_cache=`): a repo
  pointing `--remote_cache` at a separate backend (BuildBuddy, EngFlow) would
  split the CAS against Limrun's executor and fail with `Lost inputs no longer
  available remotely`. The generated config empties it under `--config=limrun`,
  and the repo's non-limrun builds keep their own cache.
- **Darwin exec platform on non-mac clients**, and `PATH` including `/usr/sbin`.
- **CoreSimulator IB utility devices** (actool/ibtool) — provisioned by the fleet.

## Patterns that require a project-side change

### A pinned Xcode version via a Starlark transition
A repo may lock the Xcode version for a sub-build with a `transition` outputting
`//command_line_option:xcode_version`. **A transition output overrides
`--xcode_version`** — no flag or bazelrc can win against it. If the pinned
version isn't on the fleet, analysis fails in `host_xcodes`. Fix: edit the
transition to drop the `xcode_version` output (or set it to the fleet's).

### Custom `remote_default_exec_properties`
Limrun's worker matches actions by an **exact** platform-property set
(`OSFamily=Darwin`). A project bazelrc that adds extra/mismatched properties
(a lowercase `OSFamily=darwin`, `Arch=arm64`, a `cache_bust=…`) makes the action
platform no longer match any worker → the build stalls or reports no usable
worker. Fix: neutralize those base `build --remote_default_exec_properties=…`
lines for the limrun path (the generated config sets the one the worker needs).

### Per-mnemonic strategy pins beyond Swift/Genrule
If a repo pins other mnemonics local (e.g. `--strategy=ObjcCompile=local`), those
actions run on the client and then need a local Xcode / can't run on a thin
Linux client. Symptom: an action runs `local`/`worker` and fails resolving a
local toolchain. Fix: override the offending mnemonic to `remote`.

### Foreign-build genrules (a host tool compiled from source)
A genrule that downloads a C/C++ tool's source and shells out to `cmake`/`make`
(probing `sysctl` for `-j`, etc.) is **not** sandbox/RBE-friendly: the cage
lacks those tools. Symptom: `sysctl: command not found` / `Exit 127` in a
`[for tool]` genrule once forced remote. Idiomatic host tools built as a normal
`cc_binary` compile fine remotely. Treat the genrule form as a project smell.

### codesign digest algorithm
A target that sets `codesignopts = ["--digest-algorithm=sha1"]` fails under
recent Xcode's codesign: `signing with only SHA1 not allowed`. Use `sha256`.

### A Mac-local Apple action that must use the client's own Xcode
The generated config pins Xcode to the fleet's version for **both** the remote
and local sets, and forces every action remote (`--spawn_strategy=remote`,
`--noremote_local_fallback`). That's deliberate: it makes the build identical on
a Mac and a Linux client and silences the "Xcode not available locally" notice.
The trade-off: if a project *forces* an Apple/Swift action to run on the Mac
client (e.g. a `--strategy=…=local` pin, or a rule that runs `xcode-locator`
against the host), it will look for the fleet's Xcode build locally and fail
(`xcode-locator … not available`) instead of using the Mac's own Xcode. This is
intended — under Limrun RBE everything is meant to run remotely. If you genuinely
need that local action: either drop the local strategy pin so it runs remote
like everything else (preferred), or, if you must keep it local, hand-edit
`.limrun/BUILD` to declare the client's *real* local Xcode as a distinct
`local_xcode` (a different major.minor from the fleet's, so its alias doesn't
collide) under `local_versions` — accepting the "not available locally" notice
back. Re-running `lim xcode rbe` regenerates `.limrun/`, so make the edit durable
elsewhere if you keep it.

## Expected, benign

- **A local sub-build before the remote build** — some example repos consume the
  ruleset via a *built release archive*, so the first thing you see is a local
  build of that archive, then the real target builds remote. Not an error.
- `compatibility_level` and `bazel_features` version mismatch **warnings**.

---
Append new patterns here as they're hit — keep them at the pattern level
(symptom → cause → fix), not as one-off patches for a specific app.
