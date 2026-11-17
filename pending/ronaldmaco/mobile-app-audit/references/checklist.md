# Inventory and static checklist

Read the code path end to end for each area in scope and answer every question. Every "no" or "unclear" becomes a finding with file:line and a concrete trigger, and gets an impact map (SKILL.md 2.4).

## Inventory (modes C, D)
- Stack, minimum/target OS and SDK, build system, dependency manager, environments and base URLs (xcconfig, Info.plist, build.gradle, AndroidManifest, .env, pubspec.yaml, app.json/app.config, eas.json).
- Every screen and flow (storyboards, navigation graphs, routers), every endpoint (host, method, auth, caching), background work (push, deep links, timers), local persistence (keychain/keystore, user defaults/shared prefs, databases, caches), third-party SDKs, feature flags, remote config.
- **Shared data map:** for each piece of user data (preferences, filters, likes, profile), which screens read it and which requests send it. This is the "consumers" axis of every impact map.
- Test setup: which test targets exist and whether they build and run today.
- Ask only for what cannot be found: test accounts, devices/regions that matter, known complaints (recorded as hypotheses).
- **Completeness scan (mode D):** `grep -rnE 'TODO|FIXME|not implemented|placeholder|lorem ipsum|fatalError\("|TODO\(\)' <screen and feature folders>`, then cross-check the route list (navigation graph, router, storyboards) against screens that exist. Each hit is Suspected until opened on a device.

## Build health gates (modes D, E)
Run the project's own checks before reading code. Record each command, its exit code and the last lines of output. A check the project does not have is "not configured", never "passed".
- Android: `./gradlew lint test assembleRelease`.
- iOS: `xcodebuild test -scheme <scheme> -destination 'platform=iOS Simulator,name=<device>'`, then a Release build of the same scheme.
- Flutter: `flutter analyze && flutter test`, then `flutter build apk --release` or `flutter build ios --release --no-codesign`.
- React Native / Expo: the package scripts (`npm run lint`, `npm test`, `npx tsc --noEmit`); Expo: `npx expo-doctor`, `npx expo install --check`, `npx expo export`.
- App size vs the previous release: `bundletool get-size total --apks=<app>.apks`; `du -h` of the IPA/APK. Record it in the audit log; flag growth with its cause (new SDK, assets), not against an invented limit.

## Launch, lifecycle, navigation
- Correct lifecycle for the target SDK (iOS UIScene; Android activity/fragment lifecycle, process death; Flutter/RN app state).
- Root replacement does not stack screens; no duplicate presentations; back never lands on a screen that should be gone.
- Deep links and push work cold and warm; pending actions wait until the UI is ready.
- No force unwraps / `!!` / unchecked casts on data that can be missing.
- Callbacks that pop or dismiss check the screen is still on top.
- System notifications can arrive unpaired (keyboard hide without show, background without foreground); handlers do not assume the pair.
- After a lifecycle migration (e.g. UIScene), every URL entry point (deep links, social login callbacks, push) is retested cold and warm.

## Authentication and session
- Login, sign up, forgot and reset show the server's error in friendly words; success never shown on an error body.
- Public auth routes do not send a stale token.
- Session survives kill, reboot and locked device (keychain after first unlock; Android keystore).
- 401 logs out once, only for the app's own API host; token refresh is single-flight.
- Logout clears token, cached user, per-user caches and analytics identity.
- In-app account deletion exists when sign up exists, waits for the server and confirms.

## Networking
- Every request has a timeout; every failure reaches the UI (offline, timeout, 4xx, 5xx, HTML/non-JSON), including transport errors that have no response body.
- In-flight/loading flags are cleared on every outcome (success, failure, cancel); a new query supersedes the running one instead of being refused.
- A cached copy may stand in for a failed **read** (marked stale, with the error); never for a write.
- Caching: what is cached, keyed by what, when used. Writes and per-user reads never served stale as fresh.
- A completion can fire more than once? Only the first answer counts.
- Lenient parsing where the server can add or null fields.
- UI and shared state only on the main thread.
- No secrets in logs, URLs or query strings; HTTPS only.
- Every read uses a read method (GET); no write method used to fetch data.
- A non-2xx status is an error even when the body decodes into the model.
- **Request parameters:** what does an empty array, null, 0 or a missing key mean to the server? Never send "empty" when the user asked for something specific.

## Data, state, persistence
- Single source of truth for the current user and settings; local copy updated from the server response after writes.
- Refresh-on-appear cannot overwrite a newer value from a save in flight.
- Models compared by stable id, not full equality; if ids are unreliable (0, duplicates), by normalised name.
- Sentinel values ("none", 0, -1) never share a representation with real data.
- Hard-coded lists match the server.
- Stored data from older app versions decodes or migrates.

## Screens with actions (forms, pickers, toggles, likes, purchases)
- Loading shown, repeat taps disabled, waits for the server, then closes/updates.
- On failure: friendly message, input kept, retry possible, optimistic UI reverted.
- Validation matches the server.
- Toggles/likes match server state after restart and on other screens.
- Purchases: receipt validation, restore, pending/deferred states, entitlement refresh.

## Lists, search, filters, pagination
- Loading, empty, error and end-of-list states exist and are distinct.
- Refresh and pagination do not duplicate or skip; stale requests ignored when filters change.
- Every selected filter shows as selected **everywhere** (chips, filter sheet, settings) and is applied to the request; none is dropped silently.
- The result for each selected filter matches the API for the same parameters (oracle).
- A filter that can match nothing produces an honest empty state, not unfiltered results.
- Search debounced, cancels the previous request, handles no results.

## Media and web content
- Images: placeholders, disk caching (shows offline), failure fallback, no main-thread decoding; a late image for a reused cell is dropped.
- Video/web views on current APIs, handle no network and autoplay.
- External links open in the right place, return to the app, and do not 404.

## Push and background
- Permission flow, token sent to the backend and refreshed, cleared on logout.
- APNs/FCM config valid, not expiring, right environment.
- Notification taps route correctly cold/warm.

## Layout and device variety
- Small/large phones, tablets, rotation, dark mode, Dynamic Type, RTL if localized.
- Safe areas, keyboard covering inputs.
- No layout on deprecated/no-op APIs.

## Platform and dependencies
- Target/minimum SDK meet store requirements (`references/store.md`); deprecations and what breaks next year in `references/future-risk.md`.
- SDKs initialised once, on the right thread, versions supporting the current OS.
- Known vulnerabilities listed, not upgraded without approval.

## Analytics and logging
- Events fire once per action, after success, no personal data beyond policy.
- Event context is passed per call (parameters), never stored on shared enum constants or singletons.
- Debug logging reduced in release builds.

## Security
Run `references/security.md`: ranked checks (backend rules, server-side entitlements, races, tokens, OAuth, WebViews, release flags, storage, deep links, secrets, TLS, crypto, biometrics, OTA, privacy and consent), each with how to verify it.

## Performance
Measure, do not estimate. Compare with a baseline you recorded (previous build or release) instead of a fixed threshold. A metric you did not measure is a "not measured" row in the coverage table, never OK.
- **Launch:** Android `adb shell am start -S -W -n <pkg>/<activity>` (TotalTime), 5 runs, median. iOS: `xcrun xctrace record --template 'App Launch' --device <id> --launch -- <app path>`, or an XCTest with `XCTApplicationLaunchMetric`. The first launch after install is slower; judge normal relaunches.
- **Jank:** Android `adb shell dumpsys gfxinfo <pkg> reset`, run the flow, then `adb shell dumpsys gfxinfo <pkg>` (Janky frames %). iOS: `xcrun xctrace record --template 'Time Profiler' --attach <App> --time-limit 30s`, look for main-thread work. Flutter: DevTools performance view on a profile build (`flutter run --profile`). agent-device: `perf frames`, `perf cpu profile`.
- **Memory growth:** sample memory (`adb shell dumpsys meminfo <pkg>`; iOS Xcode memory gauge or `xcrun xctrace record --template 'Leaks'`; agent-device `perf memory sample`) before and after repeating one navigation 10 times. Steady growth is a finding; then find the unpaired resource statically: timers created vs invalidated, observers and listeners added vs removed, tasks, subscriptions and coroutines stored vs cancelled, `[weak self]` in long-lived closures. LeakCanary on Android debug builds names the leak.
- **ANRs / watchdog kills** in production reports (`references/telemetry.md`).

## Accessibility
- **Labels and target size from the UI tree:** Android `adb shell uiautomator dump /sdcard/ui.xml && adb pull /sdcard/ui.xml`; every node with `clickable="true"` needs a `text` or `content-desc`, and bounds of at least 48dp (px = dp x `adb shell wm density` / 160). iOS: Accessibility Inspector audit (Xcode, Open Developer Tool), or `try app.performAccessibilityAudit()` in an XCUITest; tappable elements need a label and 44pt. A device tool's element list works too.
- **Contrast:** Accessibility Inspector audit (iOS), Accessibility Scanner app (Android); WCAG AA.
- **Largest text:** rerun the main flows at the largest size (`xcrun simctl ui booted content_size accessibility-extra-extra-extra-large`; `adb shell settings put system font_scale 2.0`); clipped or overlapping text is a finding.
- Logical focus order (VoiceOver/TalkBack walk); no information by colour only; reduce motion respected.

## Localization
- No hard-coded user strings if localized; locale formats; long translations and RTL fit.

## Stack notes
- **iOS (UIKit/SwiftUI):** outlets, main-thread UI, `[weak self]`, Keychain accessibility class, scene URL handling, `Task` cancellation. spaces and symbols in the product name become underscores in the Swift module name; test targets need `TEST_HOST` matching the real product name.
- **Android:** lifecycle-aware coroutines, process death (`SavedStateHandle`), no network on main, R8 keep rules, `usesCleartextTraffic` / network security config, exported components. Legacy Kotlin + Java mixes: `var` on enum constants and `object` singletons (shared state), `!!` and platform types from Java (nullability lost), `random()`/`first()` on possibly empty lists, data binding expressions hiding logic in XML. Image libraries (Glide, Coil, Fresco, Picasso) usually cancel on view reuse; check before reporting a late-image bug.
- **Flutter:** `mounted` after `await`, `setState` after dispose, platform channel errors, release-only issues.
- **React Native / Expo:** unhandled rejections, effect cleanup, Hermes/release differences, Expo runtime version vs OTA channel, secrets in `app.config`.
