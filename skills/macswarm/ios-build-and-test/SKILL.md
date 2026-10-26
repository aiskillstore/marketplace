---
name: ios-build-and-test
description: Build, test, launch and screenshot an iOS app on a Mac with Xcode. Use when a task asks to compile an Xcode project or Swift package for iOS, run unit or UI tests on an iOS Simulator, reproduce a crash, check a screen visually, or attach Simulator screenshots and test results to a pull request. Works on a local Mac or a hosted Mac such as a Macswarm Pod.
---

# Build and test iOS on a Mac

You are on macOS with Xcode installed. Prove changes on a Simulator before you call a task done: a green build is not a passing test, and a passing test is not a screen anyone has looked at.

## 1. Check the machine

```bash
sw_vers -productVersion
xcodebuild -version
xcrun simctl list runtimes available
```

If `xcodebuild` is missing, stop and report it. Do not install Xcode yourself.

If an XcodeBuildMCP server is connected, you may use its build, test, launch and screenshot tools instead of the commands below. The steps and the evidence you collect stay the same.

## 2. Find the project, scheme and destination

```bash
ls *.xcworkspace *.xcodeproj Package.swift 2>/dev/null
xcodebuild -list -json                 # add -workspace X.xcworkspace or -project X.xcodeproj
xcrun simctl list devices available --json
```

- Prefer the `.xcworkspace` when one exists (CocoaPods and multi-project setups need it).
- Use the scheme named in the repository's `AGENTS.md` or `CLAUDE.md`. If none is named and there is more than one app scheme, ask before guessing.
- Pick a Simulator by UDID, not by name, so the command does not depend on which device models are installed. Prefer one that is already `Booted`.

Store the choices once for the session:

```bash
WS="-workspace App.xcworkspace"        # or PROJ="-project App.xcodeproj"
SCHEME="App"
UDID="<udid from simctl>"
DEST="platform=iOS Simulator,id=$UDID"
```

## 3. Build

```bash
xcodebuild $WS -scheme "$SCHEME" -destination "$DEST" \
  -derivedDataPath .build/DerivedData build 2>&1 | tail -n 80
```

Read the first `error:` line, not the last one. Fix the cause and rebuild. Never commit with a failing build.

On a shared Mac, builds may queue behind other agents. Keep working on something that does not need the compiler while you wait; do not start a second build of the same scheme.

## 4. Test

```bash
xcodebuild $WS -scheme "$SCHEME" -destination "$DEST" \
  -derivedDataPath .build/DerivedData \
  -resultBundlePath .build/Results.xcresult test 2>&1 | tail -n 80
xcrun xcresulttool get test-results summary --path .build/Results.xcresult
```

- Run only the affected tests first with `-only-testing:Target/Class/testName`, then the full suite before you open a PR.
- When a test fails, quote the failing test name and its assertion message in your report.
- Delete `.build/Results.xcresult` before rerunning; `xcodebuild` refuses to overwrite it.

## 5. Launch and look

```bash
xcrun simctl boot "$UDID" 2>/dev/null || true
APP=$(find .build/DerivedData/Build/Products -name "*.app" -path "*iphonesimulator*" | head -n 1)
BUNDLE_ID=$(/usr/libexec/PlistBuddy -c 'Print CFBundleIdentifier' "$APP/Info.plist")
xcrun simctl install "$UDID" "$APP"
xcrun simctl launch --console-pty "$UDID" "$BUNDLE_ID" &
sleep 5
mkdir -p .build/screens
xcrun simctl io "$UDID" screenshot ".build/screens/01-launch.png"
```

- Take one screenshot per screen you changed, numbered in the order a user reaches them.
- For crashes, collect the log: `xcrun simctl spawn "$UDID" log show --last 5m --predicate "process == \"$SCHEME\""`.
- Reset state between runs with `xcrun simctl uninstall "$UDID" "$BUNDLE_ID"` rather than erasing the device, which other agents may be using.

## 6. Report

Your final message and the PR description include:

1. The scheme, the Simulator (model and iOS version) and the Xcode version.
2. Build result, and test totals from the `xcresulttool` summary.
3. The screenshots, attached or committed under a path the reviewer can open.
4. Anything you could not verify, stated plainly.

Do not commit `.build/`. Add it to `.gitignore` if it is missing.
