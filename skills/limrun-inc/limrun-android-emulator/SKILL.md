---
name: limrun-android-emulator
description: "Drive an app running on a Limrun cloud Android emulator: install an APK, launch and terminate apps with crash reports, tap, type, read the UI element tree, screenshot, record video, inject microphone audio, shape network bandwidth, read app logs, run shell commands, transfer files, tunnel the app's network destinations through your machine with HTTP inspection and HAR capture, and use adb over the CLI's tunnel for full logcat and interactive tools. Use after a build (from limrun-gradle or any builder) when the user wants to see, test, or interact with their app on an emulator, or says 'show me a screenshot', 'tap', 'run it on the emulator', 'check logcat', 'record a video', 'inspect network traffic', or 'reach my local server from the emulator'. To build the APK or AAB first, use limrun-gradle."
user-invocable: true
effort: high
---

# Limrun Android Emulator

Interact with an app running on a Limrun cloud Android emulator, from any
environment (Linux, Windows, macOS, VM, container). This skill is
build-agnostic: it assumes the APK was already built, usually by
**limrun-gradle**. Keep build concerns in that skill; this one is about
driving the running emulator.

Never use a local emulator, a local Android SDK, or Android Studio.

## Auth and CLI

Install if needed: `npm install --global lim`. Auth is `lim login` or
`LIM_API_KEY` (it may be set outside the project, so don't ask for it just
because it's missing from `.env` or the shell). The CLI is the source of truth:
the commands in this skill are verified, but if a flag errors or you need one
not shown here, check `lim android <subcommand> --help` instead of guessing.

## Installing an app

You can build with Limrun's remote Gradle service and have the APK installed
on a fresh emulator automatically, or install a pre-built local APK or a URL.
One default to know first: `lim android create` opens an ADB tunnel
(`--connect`) and a browser tab with the live stream (`--open`) unless told
otherwise. As an agent, pass `--no-open` always, and `--no-connect` unless you
need adb right away.

### Build and install

Upload the APK built by **limrun-gradle** as a named asset, then create an
emulator with it pre-installed:

```bash
lim gradle build . --upload myapp.apk
lim android create --install-asset myapp.apk --no-open --no-connect
```

Create blocks until the instance is ready to drive; no boot wait is needed.
The create output includes a signed stream URL; share it with the user as a
Markdown link, like `[Live emulator](<signed-stream-url>)`. If you have a
browser the user can see, open the URL there and tell them. Create also
prints a console URL: it opens the same live view but requires a console
login, so prefer the signed stream URL for sharing.

Useful create flags: `--reuse-if-exists` (reuse a running instance with the
same labels), `--rm` (delete when the CLI exits), `--jurisdiction us|eu|as`
(where the instance runs; don't use `--region`, it is deprecated),
`--inactivity-timeout` / `--hard-timeout`, `--display-name`, and `--label k=v`
(find labeled instances later with `lim android list --label-selector k=v`).

### Install app from local

Create a new emulator, then install a local file or a URL:

```bash
lim android create --no-open --no-connect
lim android install-app ./app-debug.apk
lim android install-app https://example.com/app.apk
```

A local path is uploaded to Limrun Asset Storage first; a URL is fetched by
the instance itself, which is much faster for large APKs than uploading from
your machine. `install-app` returns as soon as the app is sent; the install
finishes in the background within seconds. Newly installed apps land in the
app drawer, not the home screen, so don't look for their icon; just launch
the app with `lim android launch-app <package> --detach` (without `--detach`
it blocks watching the app until it exits), or confirm with
`lim android adb-shell -- sh -c "pm list packages | grep <name>"`.

Every time you need to install a new version of the APK, sync it instead of
reinstalling:

```bash
lim android sync ./app-debug.apk
```

It sends only a delta against the APK already on the instance, then
reinstalls. `--watch` keeps re-syncing on file changes, and
`--launch-mode ForegroundIfRunning|RelaunchIfRunning` controls what happens to
the running app after each install.

## Targeting the right instance

Most `lim android` commands default to the last created instance and resolve
the "current" one from the **git repo / worktree** of your cwd. In a different
directory (or outside any git repo) a command can report that no recent
instance was found even though one is running. The reliable recipe:

```bash
lim android list                          # shows all instances and their IDs
lim android element-tree --id <that-id>   # pass --id to EVERY lim android command
```

Once you have the ID (format `android_<region>_<ulid>`), pass
`--id <android-instance-id>` to all `lim android` calls for the rest of the
session. Alternatively, `git init` the project so the workspace resolves on
its own. When controlling multiple instances, always pass `--id`.

## Launching the app

Launch and stop installed apps by package name:

```bash
lim android launch-app com.example.app --detach                  # launch and return
lim android launch-app com.example.app                           # launch and watch until it exits
lim android launch-app com.example.app --mode RelaunchIfRunning  # restart for a clean state
lim android terminate-app com.example.app                        # stop it, e.g. to reset app state
```

Without `--detach`, `launch-app` blocks watching the app: when it crashes,
ANRs, or is stopped, the command prints the exit reason, crash details with
the stack trace, and a recent app log tail, then returns. That report is the
way to see why an app died without adb; for logs while the app is running,
use `lim android app-log` (below). There is no `list-apps`; discover package
names with `lim android adb-shell -- pm list packages`, or take the
application ID from the build.

## App logs

One app's logs need no tunnel:

```bash
lim android app-log com.example.app --tail 100   # recent lines (app must be running)
lim android app-log com.example.app --follow     # stream live lines until Ctrl+C; don't stream into context
```

## Shell and files

One-shot shell commands and file transfer need no tunnel either:

```bash
lim android adb-shell -- pm list packages -3                     # like adb shell; args go after --
lim android adb-shell -- sh -c "dumpsys battery | grep level"    # pipes need an explicit shell
lim android push-file ./fixture.json /sdcard/Download/fixture.json
lim android pull-file /sdcard/Download/out.json ./out.json
```

They run with the same permissions the adb shell user has, and `adb-shell`
exits with the command's exit code.

## Full logcat and interactive adb over the tunnel

Full-device logcat and anything interactive (Android Studio, scrcpy,
streaming) go through plain `adb` over the CLI's tunnel. Start the tunnel in
a background shell and keep it alive:

```bash
lim android connect        # prints "Tunnel started on 127.0.0.1:<port>."
```

`connect` runs `adb connect` for you (use `--adb-path` if adb isn't on PATH).
The printed `127.0.0.1:<port>` is the device serial; pass it with `-s` to
every adb call (`adb devices` also lists it):

```bash
SERIAL=127.0.0.1:<port>
adb -s $SERIAL logcat -d | tail -100    # dump recent full-device logs, don't stream into context
```

The tunnel lives and dies with the process that started it: when that shell
exits, `adb devices` shows the serial as `offline` while the instance keeps
running. Just run `lim android connect` again to get a new tunnel (the port
changes each time). Stale offline serials are harmless; `adb disconnect`
clears them.

## Testing changes

When emulator interaction is part of the task, test new or changed
functionality with the interaction commands after each install or sync. Focus
on what changed, plus a quick smoke test of core flows. Start by reading the
element tree to see what's on screen before acting:

```bash
lim android element-tree
```

The output is the raw UIAutomator XML hierarchy on a single line, so a plain
grep echoes the whole document. Split it into one node per line first, then
grep for the `text`, `resource-id`, `content-desc`, or `bounds` you need
rather than dumping the whole tree into context:

```bash
lim android element-tree | sed 's/></>\n</g' | grep -i "save"
```

## Interacting with the app

Prefer tapping by resource id, then by visible text or content description,
then coordinates as a last resort:

```bash
lim android tap-element --resource-id com.example.app:id/startButton
lim android tap-element --text "Save"
lim android tap-element --content-desc "Open menu"
lim android tap 360 800
```

Selector values match **exactly**, not by substring: `--text "Save"` does not
match a "Save draft" button. Copy the value verbatim from `element-tree`. A
selector that matches nothing fails in a couple of seconds with
`No element found for selector`. Other selectors: `--class-name`,
`--package-name`, `--index`, `--clickable`, `--enabled`, `--focused`, and
`--bounds-contains-x/y`; combine them to narrow a match. On web pages in the
browser, resource ids are the page's own DOM ids (like `searchIcon`) and are
often empty; select by `--text` plus `--class-name` there, or fall back to
coordinates from the node's `bounds`. To inspect matches without tapping, use
`find-element` with the same selectors:

```bash
lim android find-element --text "Save"   # table of matches with bounds
```

For text input, target the field directly; no prior focus tap is needed.
`type` takes the same selectors as `tap-element` (`--class-name
android.widget.EditText --focused` works for a field with no resource id):

```bash
lim android type "hello world" --resource-id com.example.app:id/searchBox
lim android type "hello" --x 360 --y 400   # by coordinate
lim android press-key enter
lim android press-key backspace            # --modifier shift/control/alt/command to combine
```

For scrolling and navigation:

```bash
lim android scroll down --amount 600
lim android scroll up --amount 300
lim android press-key back
lim android press-key home
lim android open-url "https://example.com"   # opens in the default browser; also fires deep links
```

After every interaction, re-run `element-tree` to confirm the UI transitioned.
No sleep is needed between a tap and `element-tree`; the tap blocks until
done. A page load after `open-url` is asynchronous though: re-run
`element-tree` until the node you expect appears. A present but childless
`android.webkit.WebView` means the page is still loading, not a broken tree.

```bash
lim android element-tree
```

### When the element tree is empty

Some React Native and Expo apps expose no accessibility nodes at all, which
leaves `element-tree`, `tap-element`, and `find-element` blind (system dialogs
still expose nodes). Fall back to driving by pixels: take a screenshot, read
the coordinates of the target, and use `tap x y` / `type --x --y`. Screenshot
pixels map 1:1 to tap coordinates, so a button centered at (360, 1322) in the
image is tapped with `lim android tap 360 1322`. Re-screenshot after each
action to confirm the result.

## Screenshots and video

Screenshot takes a **positional path** (not `-o`):

```bash
lim android screenshot screenshot.png
lim android screenshot screenshot.png --id <android-instance-id>
```

Use the element tree for functional assertions (element existence, text, state
changes) and screenshots only for visual properties. For anything involving
motion (animations, gameplay, streaming UI), prefer video:

```bash
lim android record start                     # non-blocking
lim android record stop -o /tmp/recording.mp4
```

`record stop` accepts `--quality 5-10`. Recorded frames are half the
screenshot resolution, so read tap coordinates from screenshots, never from
video frames. For UI changes, include a demo video in the pull request so the
user can see it.

## Simulate the microphone with an audio file

For voice-driven flows (assistants, speech-to-text, audio calls), play a local
audio file as the emulator's microphone. The app hears the audio through its
normal capture pipeline:

```bash
lim android play-on-microphone ./fixtures/command.wav          # loops by default
lim android play-on-microphone ./fixtures/command.mp3 --once
```

WAV and MP3 work. The file is pushed over adb, so this command needs a local
`adb` binary (`--adb-path` if it's not on PATH) and opens its own short-lived
tunnel. Camera injection is iOS-only; for camera-driven test flows use
**limrun-ios-simulator**.

## Shape network bandwidth

Test slow-network behavior by capping the instance's Wi-Fi bandwidth:

```bash
lim android set-wifi-bandwidth --down-kbps 1000 --up-kbps 500
lim android set-wifi-bandwidth --down-kbps 0 --up-kbps 0       # 0 clears the limit
```

## Tunnel the app's traffic through your machine

When the app must reach a service only your machine can reach (a local dev
server, a VPN-only staging API), or you need to see its HTTP traffic, start a
destination tunnel. Only the destinations you select are rerouted through
the machine running `lim`; everything else leaves the instance directly.

```bash
lim android tunnel --selector localhost:8080 --detach --id <android-instance-id>
```

- An exact selector (`localhost:port` or `IP:port`, port >= 1024) becomes a
  listener on the emulator, also reachable as `10.0.2.2:<port>`; the app's
  connections to it land on your machine and are dialed there.
- Domain selectors (`api.example.com`, `"*.corp.example"`) are intercepted
  on the emulator and dialed from your machine, so your DNS and VPN apply.
  Apps that resolve DNS themselves over HTTPS bypass domain interception.
- Start the tunnel **before** launching the app: connections opened earlier
  keep their original route. One tunnel per instance; a second start fails.

As an agent, always pass `--detach`: it returns once the tunnel is READY and
keeps it alive in a background process. Manage it with:

```bash
lim android tunnel status --id <android-instance-id>   # state, per-selector binds, last dial failure
lim android tunnel stop --id <android-instance-id>
```

### Inspect HTTP traffic, capture HAR, persist a network log

Inspection is on by default: every HTTP and HTTPS request through the tunnel
is decoded, printed as one summary line per request (in the tunnel log file
when detached), and shown live in the console's network panel.

```bash
lim android tunnel --selector "*.api.example" --har ./traffic.har --detach   # write HAR 1.2 with bodies
lim android tunnel --selector "*.api.example" --persist --detach             # network log survives the instance
```

`--persist` uploads a body-inclusive network log as a session artifact when
the tunnel stops or the instance terminates; it appears on the instance's
session page in the console with a HAR download (default lifetime 3 days,
`--ttl <seconds>` up to 30 days). HTTPS is decoded with an emulator-trusted
CA, so **apps with certificate pinning fail through inspected domain
selectors**: leave the pinned host out of the selectors or pass
`--no-inspect` to relay bytes opaquely (no summaries, HAR, or persistence).

## Preview URL for humans

Upload the APK to Limrun Asset Storage and return a preview URL for the user
to open and test the app manually in the browser:

```bash
export ASSET_NAME=myapp.apk   # can be any name
lim asset push ./app-debug.apk -n ${ASSET_NAME}

echo "https://console.limrun.com/preview?asset=${ASSET_NAME}&platform=android"
```

Opening the link in the Limrun console provisions an emulator with the APK
pre-installed.

## Cleanup

When the work is completed, you can delete the emulator. `delete` takes a
**positional** ID (`--id` is not a valid flag here, unlike other commands):

```bash
lim android delete <android-instance-id>
```

## Gotchas

- **The fleet is x86_64.** Emulators report `x86_64,arm64-v8a` ABIs and run
  arm64 code through translation, but an APK whose native libraries are
  arm64-only for some vendor SDKs installs fine and then crashes with
  `UnsatisfiedLinkError` when that code first loads. Build with x86_64 native
  libs included.
- **Selectors match exactly.** `tap-element --text` and `find-element --text`
  need the full, exact string from `element-tree`; substrings match nothing.
- **`install-app` returns before the install finishes.** The app lands a few
  seconds later; verify with `find-element` or `pm list packages` before
  launching. Prefer `install-app <URL>` or `create --install-asset` over raw
  `adb install`: a big APK over `adb install` streams with zero progress
  output and looks hung for minutes, and killing it mid-stream corrupts the
  install.
- **The ADB tunnel is session-bound.** It dies with the shell that started it
  while the instance keeps running; reconnect with `lim android connect` and
  re-read the port, it changes every time.
- **Failed create pipes can still leak an instance.** If a `create` invocation
  errors client-side (broken pipe, JSON parse), check `lim android list`; the
  instance may exist anyway and should be deleted.
- **Empty element tree usually means a React Native app**, not a broken
  instance. See "When the element tree is empty" above.
- **`element-tree` can be large.** Pipe through `grep` to extract what you
  need rather than dumping the whole tree into context.
- **Instance resolution can miss in a non-git dir.** See "Targeting the right
  instance" above; pass `--id` when in doubt.
- **Build errors are the build skill's job.** If the APK isn't building, the
  failure is upstream; go back to **limrun-gradle**.
