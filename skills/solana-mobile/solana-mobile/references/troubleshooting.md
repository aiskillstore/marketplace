# Build and environment troubleshooting

Project, build, and emulator failures. For wallet connection and signing failures, see the
`solana-mobile-wallet` skill's troubleshooting reference.

Start here:

```bash
npx solana-mobile@latest doctor --verbose
```

It checks the local toolchain and recommends fixes. Most failures in this file are caught by
it, so run it before reading further.

## Wallet features do nothing, no errors

The app is running in Expo Go. MWA needs native Android modules that Expo Go does not bundle,
and there is no workaround.

```bash
npx expo run:android
```

This is the single most common cause of "the wallet integration does not work" reports.

## `expo prebuild` wiped native changes

`prebuild --clean` regenerates `android/` and `ios/` from configuration, discarding manual
edits. Recover them from git, then move the changes into a config plugin or the `app.json`
`plugins` array so they survive the next regeneration.

## Gradle build fails after adding a native module

Native modules need a real rebuild, not a Metro restart:

```bash
npx expo prebuild --clean
npx expo run:android
```

If it still fails, clear the Gradle cache:

```bash
cd android && ./gradlew clean && cd .. && npx expo run:android
```

## `SDK location not found` / `ANDROID_HOME` unset

```
> SDK location not found. Define a valid SDK location with an ANDROID_HOME environment
  variable or by setting the sdk.dir path in your project's local properties file
```

**`doctor` can report "Android build: ready" and this can still happen.** `doctor` finds the
SDK at its default location, which is enough for its own checks, but Gradle only reads
`ANDROID_HOME` or `android/local.properties`. A green `doctor` does not prove the build
environment is exported.

Export it in your shell profile:

```bash
export ANDROID_HOME="$HOME/Library/Android/sdk"
export PATH="$PATH:$ANDROID_HOME/platform-tools:$ANDROID_HOME/emulator"
```

Restart the shell before rebuilding — an inherited environment is a common reason a fix
appears not to work. Per-project alternative, which does not depend on the shell at all:

```bash
echo "sdk.dir=$HOME/Library/Android/sdk" > android/local.properties
```

`local.properties` is machine-specific and belongs in `.gitignore`.

## `Could not find device with name: emulator-5554`

`expo run:android --device` expects the **AVD name**, not the adb serial:

```bash
npx solana-mobile@latest emu status   # `name` column, not `serial`
npx expo run:android --device test-skills
```

Passing `emulator-5554` fails even though `adb devices` lists it. This bites as soon as more
than one emulator is running and you start naming a target explicitly.

## No emulator to run on

```bash
npx solana-mobile@latest emu status
npx solana-mobile@latest emu create
npx solana-mobile@latest emu start
```

`emu create` installs a system image if one is missing. To pick a device profile:

```bash
npx solana-mobile@latest emu create local_phone --device pixel_9
```

## Emulator runs but connect does nothing

A fresh emulator has no wallet app, so MWA has nothing to associate with. Install an
MWA-compatible wallet APK into the emulator, or use a physical Android device.

Anything gated on the Seeker Genesis Token needs a real Seeker device — an emulator cannot
hold one. See the `seeker-genesis-token` skill.

## `adb` cannot see a physical device

1. Enable Developer Options and USB debugging on the device.
2. Accept the debugging prompt when it appears.
3. Confirm with `adb devices` — the device should be `device`, not `unauthorized`.

If it stays `unauthorized`, revoke USB debugging authorizations on the device and reconnect.

## Metro resolves the wrong build of a package

Symptoms include the "secure context (`https`)" error from the MWA protocol package, or
Node-only APIs surfacing at runtime. Metro picked a browser or ESM entry point over the React
Native one.

Fix the resolution order in `metro.config.js` rather than deleting files from
`node_modules`, which the next install undoes. Compare against a scaffolded template's
`metro.config.js`:

```bash
npx solana-mobile@latest create /tmp/reference-app --template expo-kit-wallet --skip-install
```

## Warnings that are safe to ignore

These appear on a healthy build of a freshly scaffolded project. Do not spend time on them:

```
WARN Attempted to import the module ".../@noble/hashes/crypto.js" which is not listed in the
"exports" of ".../@noble/hashes" under the requested subpath "./crypto.js". Falling back to
file-based resolution.
```

Metro resolving a subpath `@noble/hashes` does not formally export, reached transitively
through `@solana/kit`. It falls back successfully and the bundle works.

```
Deprecated Gradle features were used in this build, making it incompatible with Gradle 10.
› Using react-native@0.86.0 instead of recommended react-native@0.86.2.
```

Both are informational. The template pins its own React Native version deliberately.

## Dependency versions drifted after an SDK upgrade

```bash
npx expo install --check
npx expo-doctor@latest
```

`expo install --check` reports dependencies whose versions do not match the installed Expo
SDK. Prefer `npx expo install <pkg>` over `npm install <pkg>` for anything Expo manages, so
versions stay aligned.
