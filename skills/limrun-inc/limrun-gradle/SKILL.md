---
name: limrun-gradle
description: "Build an Android app on a remote Gradle sandbox with `lim gradle build` instead of local Gradle or Android Studio, from any environment (Linux, Windows, macOS, VM, container). Use when the user wants to build an APK or AAB, sign a release with an upload key, or prepare a Play Store publish, for native Android projects, React Native, and Expo. To run, tap, screenshot, or otherwise interact with the built APK on an emulator, use limrun-android-emulator. For iOS builds, use limrun-xcode or limrun-expo-development."
user-invocable: true
effort: high
---

# Remote Gradle build

Build Android projects on Limrun's remote Gradle sandboxes, from any
environment (Linux, Windows, macOS, VM, container). `lim gradle build` syncs
your sources to a remote instance, runs the project's own Gradle wrapper
there, and streams the build output. Never fall back to local Gradle, a local
Android SDK, or a local emulator. Your job doesn't end at a green build: get
the app running or the artifact delivered, and iterate until the user is
satisfied.

For iOS builds, use **`limrun-xcode`** instead of this skill. For the Expo
dev-client loop (Metro, hot reload) on either platform, use
**`limrun-expo-development`**; it comes back here for the Android Debug
build.

## Auth and CLI

Install if needed: `npm install --global lim`. Auth is `lim login` or
`LIM_API_KEY` (it may be set outside the project, so don't ask for it just
because it's missing from `.env` or the shell). The CLI is the source of truth:
the commands in this skill are verified, but if a flag errors or you need one
not shown here, check `--help` instead of guessing:

```bash
lim gradle --help
lim gradle build --help
```

## Build an APK

Instead of `./gradlew`, build with:

```bash
lim gradle build .
```

This creates or reuses the remembered Gradle instance, syncs the current
directory, and runs `assembleDebug` by default. Pick tasks explicitly with
`--task` (repeatable):

```bash
lim gradle build . --task :app:assembleRelease
```

Use `--project-path` when the Gradle root is nested and auto-discovery is
ambiguous (for example a bare React Native repo where Gradle lives in
`android/`; the server usually finds it on its own):

```bash
lim gradle build . --project-path android
```

Expo managed-workflow projects (no `android/` directory) are detected
automatically: the sandbox installs dependencies and runs `expo prebuild`
before Gradle. Setting `--expo-app-dir` (monorepos) or `--abi` forces that
pipeline and errors when no Expo app is detected:

```bash
lim gradle build ./my-monorepo --expo-app-dir apps/mobile
```

For iterating on an Expo app with Metro and hot reload rather than plain
builds, use **`limrun-expo-development`**.

## Run it on an emulator

Upload the built APK as a named asset, then install it on an Android instance:

```bash
lim gradle build . --upload myapp.apk
lim android create --install-asset=myapp.apk
```

Build uploads default to a 14-day TTL: each build pushes the asset's expiry
to 14 days from that upload. Pass `--upload-ttl` with a Go duration (e.g.
`720h`; `1d` is invalid) to change it.

Share the signed stream URL from the create output with the user as a
Markdown link, such as `[Live emulator](<signed-stream-url>)`. For rebuild
iterations, patch the installed APK in place instead of recreating the
instance:

```bash
lim android sync ./path/to/app-debug.apk
```

For everything else on the device (tapping, typing, element tree, screenshots,
video, logcat over adb), use **limrun-android-emulator**.

## Sign a release AAB

The default signing path needs NO credentials from the user:

```bash
lim gradle build . --sign --upload myapp.aab
```

On first use, Limrun generates an upload keystore, escrows it as the
organization's signing key for this app, and signs with it. Every later
`--sign` build of the same app, from any machine or CI, uses the same key, so
Play Store uploads keep matching. The key is named by the Android application
ID, detected from `app.json` (Expo) or `app/build.gradle(.kts)`; pass
`--application-id <id>` when detection fails or picks the wrong flavor.

`--sign` makes `bundleRelease` the default task and the build fails before
starting if an explicit `--task` list contains no bundle task. A SUCCEEDED
build means the AAB carries the signature (the server verifies it before
upload), so don't re-verify the artifact unless the user asks.

Expect one of these lines before the build starts and relay its meaning:

- `Signing with the organization's upload key for <app> (newly generated).`:
  first build of this app; the key now exists for the whole organization.
- `Signing with the organization's upload key for <app> (existing).`: reusing
  the escrowed key, as intended.

## Bring your own upload key

When the app already has a registered upload key (an existing Play listing),
sign with the user's keystore instead:

```bash
lim gradle build . \
  --keystore upload.jks --keystore-password "$KS_PASS" \
  --key-alias upload --key-password "$KEY_PASS" \
  --upload myapp.aab
```

All four flags travel together; the passwords can come from
`LIM_KEYSTORE_PASSWORD` and `LIM_KEY_PASSWORD` instead of argv. Add
`--save-key` to escrow the provided key so later builds can drop the flags and
use plain `--sign`. `--save-key` refuses to overwrite: if a DIFFERENT key is
already escrowed for the app it fails before any instance is created.

Collect from the user:

- the keystore file path (`.jks` or `.p12`); never commit it or paste its
  bytes into files,
- the keystore password and the key password (often the same value),
- the key alias (`keytool -list -keystore <file>` shows it if unknown).

Failure strings to recognize on the bring-your-own path:

- `The organization already has a different upload key escrowed for <app>`:
  `--save-key` conflict. Builds with `--sign` use the escrowed key; drop
  `--save-key` to sign with the provided keystore for this build only, or ask
  the user which key is the real upload key.
- `Signing with your own key requires ... as well`: the BYO flag group is
  incomplete; the message lists exactly the missing flags.
- `signing <field> contains an unsupported character`: the password or alias
  has characters outside ISO-8859-1. Change it in place with keytool
  (`-storepasswd`, `-keypasswd`, or `-changealias`) to a Latin-1 value. Never
  regenerate the key itself: that changes the upload key.

## Publish to Play Store

With Play credentials (a service-account JSON via
`--playstore-service-account`, or an access token via
`--playstore-access-token`), the build publishes the signed release AAB
directly, no browser involved:

```bash
lim gradle build . --sign --upload-to-playstore --playstore-service-account sa.json --auto-version-code
```

`--auto-version-code` makes the server resolve the next free versionCode from
Google Play before the build and stamp it into the workspace copy
(`expo.android.versionCode` in app.json for Expo projects, the single literal
`versionCode` in the conventional `app/` module build script for native
Gradle projects), so repeat publishes never collide. Without it, or on
projects with computed or flavor-split versionCodes (which it rejects at
request time), manage the versionCode yourself as below. Without Play
credentials you cannot run the publish itself: it is a browser flow with a
Google sign-in. Prepare the artifact, upload it as an asset, and hand off:

```bash
lim gradle build . --sign --upload <app>-v<versionCode>.aab
```

Tell the user to open https://console.limrun.com and, on the **Secrets** page,
click **Connect Play Console** to sign in with a Google account that has
release access to the app (the session lives in the browser only; nothing is
stored). Then on the **Registry** page they click **Publish to Play Store** on
the uploaded AAB and enter the package name (the application ID). The app
listing must already exist in Play Console. Google Play requires a versionCode
it has never seen: `--auto-version-code` handles that on publish builds;
without it, bump `versionCode` in `app/build.gradle(.kts)` (Expo:
`expo.android.versionCode` in app.json) before the build.

Failure strings to recognize on the `--sign` path:

- `Cannot determine the Android application ID for signing`: detection found
  no `app.json` android.package and no `applicationId` in
  `app/build.gradle(.kts)`; pass `--application-id <id>`.
- `--sign produces a Play-ready signed AAB; include a bundle task`: the
  explicit `--task` list has no bundle task; add `bundleRelease` or drop
  `--task`.
- `the built AAB carries no signature`: the server's post-build check found an
  unsigned bundle; the signing config was not applied. Not a problem in the
  user's code; retry, and report it if it persists.

## Gotchas

- **Build errors are your job to fix.** If a build fails, read the error
  output, fix the code, and rebuild. Don't ask the user to fix build errors.
- **Instance reuse is per git worktree.** Commands resolve the remembered
  instance from the worktree of your cwd; pass `--id <gradle-instance-id>`
  (from `lim gradle list`) to target a specific one.
- **versionCode must increase for every Play upload.** Prefer
  `--auto-version-code` on publish builds. A rejected publish
  saying the version code already exists means bump, rebuild, republish. If a
  publish RETRY reports it, the earlier attempt already succeeded; don't
  publish again.
- **Application ID detection reads the first uncommented `applicationId`.**
  Flavor-specific IDs and dynamic Gradle logic are out of its scope; use
  `--application-id` there.
- **Keystore passwords must be non-empty and ISO-8859-1.** Empty passwords and
  characters outside Latin-1 are rejected at request time instead of failing
  minutes into the build.
- **Keep synced files small and out of build dirs.** Root-level `build/`,
  `.gradle`, `.kotlin` and any `local.properties` never sync, and `.gitignore`
  files (including nested ones) are honored. Use `--ignore <regex>` for other
  large local artifacts and `--include <regex>` to force-sync gitignored
  inputs the build needs.
