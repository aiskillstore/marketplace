# Future risk: what will break if nothing changes

Mode G, and part of mode D. Goal: list what will stop working, be rejected or become unsafe within a horizon (default 12 months) **while the code stays the same**, with a dated official source for every date.

## Rule: no date from memory
Deadlines move every year. Never write a date, version or deadline from memory or from this file. For each risk, open the official page (store, platform, vendor), quote the requirement in one line, and record the URL and the date you read it. No source found = **Suspected**, no date.

Official pages to start from (search for the current one if a link moved):
- Google Play target API level requirements: developer.android.com, "Target API level requirements for Google Play apps".
- Apple upcoming requirements: developer.apple.com/news/upcoming-requirements.
- Platform behaviour changes per OS release: Android "Behavior changes" pages per API level; Apple release notes for iOS and Xcode.
- Each SDK's own changelog, deprecation or end-of-life page (analytics, ads, auth, payments, maps, push, crash reporting).

## Checks
Run what applies to the stack. Record the command, the date and the relevant lines.

| Risk | Verify |
|---|---|
| **Store minimums** (target API level, required Xcode/SDK for uploads) | Android: `targetSdk`/`compileSdk` in `build.gradle(.kts)` vs the Play requirement page; `./gradlew lint` reports `OldTargetApi`. iOS: SDK of the last archive (`xcodebuild -version`, `DTSDKName` in the built `Info.plist`) vs Apple's upcoming requirements page. |
| **Deprecated APIs in use** | iOS: `xcodebuild build ... 2>&1 \| grep -i deprecated`. Android: `./gradlew compileReleaseKotlin` / `compileReleaseJavaWithJavac` warnings (add `-Xlint:deprecation` for Java), `./gradlew lint`. Flutter: `flutter analyze` (`deprecated_member_use`). RN/TS: `npx tsc --noEmit` with deprecation lint rules if the project has them. A deprecated API is a risk only if its removal is announced or the replacement is required; say which. |
| **Build tool deprecations** | `./gradlew build --warning-mode all` (lists what fails in the next Gradle/AGP major); `npx expo-doctor`; `npx expo install --check`; `flutter doctor -v`; CocoaPods or SPM status on its official site (registries can stop accepting or serving packages). |
| **Outdated or abandoned dependencies** | `npm outdated`, `flutter pub outdated` (marks discontinued packages), `pod outdated`, `./gradlew :app:dependencies --configuration releaseRuntimeClasspath` then check each key library's latest release. Abandoned: `gh api repos/<owner>/<repo> --jq '.archived, .pushed_at'`, `npm view <pkg> deprecated time.modified`. Archived or deprecated with no replacement = risk; old but maintained = Info. |
| **Known vulnerabilities** | `osv-scanner scan source -r .` (older versions: `osv-scanner -r .`); `npm audit --omit=dev`. List, do not upgrade without approval. |
| **SDK raises its minimum OS above the app's** | Each SDK's next major release notes vs the app's minimum OS (`IPHONEOS_DEPLOYMENT_TARGET`, `minSdk`). The app can stay on the old SDK only until that SDK's support ends; record that date with its source. |
| **OS behaviour changes** | For the next OS version: read its behaviour-change page and grep for each affected API (e.g. background work, permissions, edge-to-edge, notifications). Run the app on the newest beta simulator/emulator if available; a crash or visible change there is Verified. |
| **Expiring credentials and certificates** | TLS: `openssl s_client -connect <host>:443 -servername <host> </dev/null 2>/dev/null \| openssl x509 -noout -enddate` for every host the app uses. iOS profile: `security cms -D -i embedded.mobileprovision > p.plist && plutil -extract ExpirationDate raw p.plist`. Android upload/signing key: `keytool -list -v -keystore <ks>` ("until"). Push: APNs certificate (`.p12`) expiry or key status in the Apple developer account; FCM credentials in the Firebase console. Pinned certificates or keys that rotate before the app updates = Critical. |
| **Time bombs in code** | `grep -rnE '20[2-9][0-9]-[01][0-9]' <src>` and hard-coded years, "valid until" constants, feature flags with end dates, trial or promo logic with fixed dates, 32-bit timestamps. |
| **Server contracts** | API versions the app calls (`/v1/` paths, `Accept-Version` headers) vs the backend's deprecation notices or `Sunset`/`Deprecation` response headers (`curl -sI <endpoint>`). An old app build still in users' hands breaks when the server removes the version: check the forced-update path. |
| **Old builds still in use** | Store/telemetry share of users per app version (Play Console, App Store Connect, crash tool). A risk that hits old builds needs a forced-update or server-side plan, not only a code fix. |

## Output
A "Future risk" table in the report, most urgent first:

```
Risk | Where (file, dependency, host) | What changes | When (date, source URL, read on) | If ignored | Effort | Status
```
Status: **Verified** (official source read and the app is affected), **Suspected** (no dated source, or impact not confirmed). Effort: S (config), M (one library or API), L (migration). Offer fixes for S/M items with approval; L items get a plan, not a change.
