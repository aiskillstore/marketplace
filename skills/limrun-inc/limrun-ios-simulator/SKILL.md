---
name: limrun-ios-simulator
description: "Drive an app running on a Limrun cloud iOS simulator: launch, tap, type, read the accessibility element tree, screenshot, record video, play a video file as the camera, and run timed action chains. Use after a build (from any builder) when the user wants to see, test, or interact with their app on a simulator, or says 'show me a screenshot', 'tap', 'run the UI test', 'record a video', 'mock the camera', or 'launch on simulator'. To build the app first, use limrun-xcode-bazel (Bazel workspaces) or limrun-xcode (xcodebuild projects)."
user-invocable: true
effort: high
---

# Limrun iOS Simulator

Interact with an app running on a Limrun cloud iOS simulator, from any
environment (Linux, Windows, macOS, VM, container). This skill is build-agnostic:
it assumes the app was already built and installed by a build skill
(`limrun-xcode-bazel` for Bazel, `limrun-xcode` for xcodebuild). Keep build
concerns in those skills; this one is about driving the running simulator.

Never use local Xcode, local simulators, or local macOS tools.

## Auth and CLI

Install if needed: `npm install --global lim`. Auth is `lim login` or
`LIM_API_KEY` (it may be set outside the project, so don't ask for it just
because it's missing from `.env` or the shell). The CLI is the source of truth:
the commands in this skill are verified, but if a flag errors or you need one
not shown here, check `lim ios <subcommand> --help` instead of guessing.

## Installing an app bundle

You can either use Limrun remote Bazel or Xcode services to build the app bundle and have
it installed to the simulator automatically or you can sync a pre-built local `.ipa`
file or `.app` folder to the simulator. The main requirement is that it must be
built for simulator.

### Build and install

A build skill usually attaches the simulator for you (`lim xcode rbe --ios`, or
`lim xcode build .` then attach). Check what's already there:

```bash
lim xcode get      # is a simulator attached to the current build target?
lim ios list       # all running iOS instances
```

If none is attached, create one. It installs the last build immediately, so you
don't need to rebuild:

```bash
lim ios create --attach
```

If the create (or `lim xcode rbe --ios`) output includes a signed stream URL,
share it with the user as a Markdown link, like
[Live simulator](<signed-stream-url>). If you have a browser the user can see,
open the URL there and tell them. Otherwise pass `--no-open` to `create`: it
skips opening the URL locally and still prints it for sharing.

`lim xcode get` prints a Limrun console URL instead. It opens the same live
view but requires a console login, so prefer the signed stream URL for sharing.
If the console URL is all you have, share it and mention it needs login.

### Install app from local

Create a new simulator:

```bash
lim ios create
```

Share the signed stream URL with the user as a Markdown link, like
[Live simulator](<signed-stream-url>). If you have a browser the user can see,
open the URL there and tell them.

You can then run the following command to upload a bundle from local:

```bash
lim ios sync <path to .ipa file or .app folder>
```

You can run the same command every time you need to install a new version of the
bundle. It will patch with the difference and reload it in the simulator.

## Targeting the right instance

Most `lim ios` commands default to the last created instance and resolve the
"current" one from the **git repo / worktree** of your cwd. So even when a
simulator is attached and `lim xcode get` shows it, a `lim ios` command can still
report `No instance ID provided and no recent ios instance found`, because your
cwd isn't the git worktree where the instance was created (or isn't a git repo at
all). This bites most often right after `lim xcode rbe --ios` in a fresh project.

The reliable recipe when that happens:

```bash
lim xcode get                          # shows the attached simulator's ID
lim ios element-tree --id <that-id>    # pass --id to EVERY lim ios command
```

`lim xcode get` is the dependable source for the attached simulator's ID
(`lim ios list` also works). Once you have it, pass `--id <ios-instance-id>` to
all `lim ios` calls for the rest of the session (screenshot, tap, type,
element-tree, record). Alternatively, `git init` the project so the workspace
resolves on its own. When controlling multiple instances, always pass `--id`.

## Launching the app

The build skills reinstall and relaunch the app after every successful build,
so you usually don't need to launch it yourself. When the app is closed (a
fresh attach to an old build, or after a terminate), launch it by bundle ID:

```bash
lim ios launch-app <bundle-id>                            # foregrounds it if already running
lim ios launch-app <bundle-id> --mode RelaunchIfRunning   # restart for a clean state
lim ios terminate-app <bundle-id>                         # stop it, e.g. to reset app state
```

If you don't know the bundle ID, run `lim ios list-apps`.

The `lim ios launch-app` will stream the logs from the app in realtime for you
to debug. If you'd like to launch and forget, you can use `--detach` flag.

## Testing changes

When simulator interaction is part of the task, test new or changed
functionality with the interaction commands after each build. Focus on what
changed, plus a quick smoke test of core flows. Start by reading the element
tree to see what's on screen before acting:

```bash
lim ios element-tree
```

## Interacting with the app

Prefer tapping by accessibility id, then by label, then coordinates as a last
resort:

```bash
lim ios tap-element --ax-unique-id startButton
lim ios tap-element --ax-label "Save"
lim ios tap 201 450
```

`tap-element` taps with a real synthesized touch. Elements the accessibility
tree can see are scrolled into view automatically. A selector that matches
nothing in the tree fails in about a second; iOS creates list rows lazily, so
a below-the-fold row often isn't in the tree at all. For those, pass
`--scroll-search`: the CLI pages the screen (a few pages down, then up)
retrying the tap until the row materializes, which can take ~10s. Pass
`--activate ax` to use an accessibility press instead of a touch (no
scrolling, works on elements without a usable frame).

**Toolbar / nav-bar items usually can't be tapped by id.** SwiftUI collapses
toolbar children into a single nav-bar group, and those items report
`AXUniqueId: null` even when you set `.accessibilityIdentifier(...)` (regular
content `Button`s do expose it). So `tap-element --ax-unique-id` finds nothing
for a nav-bar button. Set an `.accessibilityLabel` / `.accessibilityIdentifier`
anyway for documentation, but to actually tap it, read its `AXFrame` from the
element tree and tap the center by coordinate:

```bash
lim ios element-tree --id <id> | grep -i -A6 -B2 moon   # find the item's AXFrame
lim ios tap <x> <y> --id <id>                           # tap the frame's center
```

For text input, focus a field first (tap it), then type:

```bash
lim ios type "hello world"     # real key events; errors if no field is focused
lim ios type "hi" --no-require-focus  # skip the focus check: for fields focused by coordinate taps when the accessibility focus scan is unreliable
lim ios press-key backspace
lim ios press-key @            # shifted symbols work directly
```

`type` presses real keys, so text delegates fire and the field's own keyboard
behavior applies (a default text field autocapitalizes the first letter, for
example). To set a value verbatim with no keyboard behavior, use `set-text`:

```bash
lim ios set-text "P@ssw0rd!" --focused                 # into the focused field
lim ios set-text "hello" --ax-unique-id emailField     # by selector
```

For scrolling and drags:

```bash
lim ios scroll down --amount 300                       # from the screen center
lim ios scroll down --amount 300 --coordinate 200,400  # from a specific point
lim ios swipe --from 200,600 --to 200,200              # explicit drag; --duration 800 for a slower, precise one
```

After every interaction, re-run `element-tree` to confirm the UI transitioned.
No sleep is needed between a tap and `element-tree`; the tap blocks until done.

```bash
lim ios element-tree
```

Chain multiple actions with precise timing via `perform`:

```bash
lim ios perform --action type=tap,x=100,y=200 --action "type=typeText,text=Hello World"
lim ios perform --action type=wait,durationMs=1000 --action type=pressKey,key=enter
lim ios perform --file ./actions.yaml
```

Run `lim ios perform --help` for the full action grammar.

## Screenshots and video

Screenshot takes a **positional path** (not `-o`):

```bash
lim ios screenshot screenshot.png
lim ios screenshot screenshot.png --id <ios-instance-id>
```

Use the element tree for functional assertions (element existence, labels, state
changes) and screenshots only for visual properties. For anything involving
motion (animations, gameplay, streaming UI), prefer video:

```bash
lim ios record start                       # non-blocking
lim ios record stop -o /tmp/recording.mp4
```

For UI changes, include a demo video in the pull request so the user can see it.

## App container files

List an app's data container before pulling a file so you use the exact path the
app created. Keep the same `--bundle-id` and `--container-type` flags for list,
pull, push, and delete:

```bash
lim ios ls Documents --bundle-id com.example.app --container-type data
lim ios pull-file Documents/recording.mov ./recording.mov \
  --bundle-id com.example.app --container-type data
lim ios push-file ./fixture.json Documents/fixture.json \
  --bundle-id com.example.app --container-type data
lim ios delete-file Documents/fixture.json \
  --bundle-id com.example.app --container-type data
```

`lim ios ls` defaults to the staging-folder root. With `--bundle-id`, it
defaults to the app bundle (`--container-type app`); use `data` for the app's
writable `Documents`, `Library`, and `tmp` directories. Paths in `ls` output are
relative to the selected root and can be copied directly into the other file
commands.

## Simulate the camera with a video

For camera-driven flows (QR-code scanning, document capture, video calls),
play a local video file as the simulator's camera. The app sees the frames
through its normal capture pipeline:

```bash
lim ios camera play ./fixtures/qr-scan.mp4            # loops by default
lim ios camera play ./fixtures/intro.mp4 --no-loop    # play once, freeze on last frame
lim ios camera clear                                  # restore the default camera
```

Any AVFoundation-decodable file works (H.264/HEVC in `.mp4`/`.mov`). Use
`--no-loop` when the app must observe the end of the clip exactly once (the
feed freezes on the last frame rather than stalling).

## Preview URL for humans

Upload the `.ipa` file directly or targz archive of the `.app` folder
to Limrun Asset Storage and return a preview URL for the user to open it and
test the app manually in the browser.

Here is how to upload it:
```bash
export ASSET_NAME=myapp.tar.gz # can be any name
lim asset push ${ASSET_NAME}

echo "https://console.limrun.com/preview?asset=${ASSET_NAME}&platform=ios"
```

Once the command finishes, you can give the following URL to the user to
click to see a simulator where this bundle is pre-installed.

```
https://console.limrun.com/preview?asset=${ASSET_NAME}&platform=ios
```

## Cleanup

When the work is completed, you can delete the iOS simulator.

```bash
lim ios delete
```

## Gotchas

- **Instance resolution can miss in a non-git dir.** See "Targeting the right
  instance" above; pass `--id` when in doubt.
- **`element-tree` can be large.** Pipe through `grep` / `jq` to extract what you
  need rather than dumping the whole tree into context.
- **`type` / `perform typeText` may not drive SwiftUI (or React Native) state.**
  Automated text injection sets the field's value through accessibility, which
  does **not** always fire a SwiftUI `@Binding` / `onChange` the way a real
  keystroke does. Symptom: the text appears in the field (and in `element-tree`),
  but reactive UI tied to it doesn't update (a send button stays disabled, a
  character counter doesn't move) and submit handlers see empty state. A real
  keyboard on the live stream works. When automating, drive submit through a
  tappable control (a button, a suggestion chip) rather than relying on text
  bound to reactive state, or have the app expose a test affordance.
- **Toolbar / nav-bar items aren't tappable by id.** See "Interacting with the
  app" above: read the `AXFrame` from `element-tree` and tap by coordinate.
- **Bundle ID discovery.** If you don't know the bundle ID, run
  `lim ios list-apps` after a successful install.
- **Build errors are the build skill's job.** If the app isn't installing, the
  failure is upstream; go back to `limrun-xcode-bazel` / `limrun-xcode`.
