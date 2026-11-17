# Security

Based on OWASP MASVS. Checks are ranked by how often they expose real user data or money in mobile apps, highest first. Each says where it runs: **S** static (code, config, built artifact), **D** device or simulator, **net** a request to the app's own backend.

Rules:
- Only the app owner's own systems, with test accounts. Reads from the backend are fine; any **write** (parallel requests, replayed purchases, edits with another user's token) needs the user's explicit OK and a test environment when one exists.
- A pattern in code is **Suspected** until a request, a device run or a concrete code path shows it is reachable. Run the "try to refute" pass (`references/report.md`) before calling anything Critical.
- Read config values (project ids, hosts, keys) from the app itself: `google-services.json`, `GoogleService-Info.plist`, `.env`, `app.config`, `Info.plist`, build configs. Never print tokens or secrets in the report; show the first 4 characters.
- No root, jailbreak or Frida is needed for any check here. When one would help, use a debug build or the simulator instead and say so.

## 1. Backend-as-a-service rules (Firebase, Supabase) - S + net
Why: open database rules expose every user's data to anyone with the project id, which ships in the app.
- Rules files: `database.rules.json`, `firestore.rules`, `storage.rules`. Look for `allow read, write: if true`, `".read": true`, and test-mode rules with an expiry date (`request.time < timestamp.date(...)`: an open database until that date, then the app breaks; also a future-risk item).
- Unauthenticated probes, expect a denial. Take the URLs from the app config: `$DB_URL` (`firebase_url` / `DATABASE_URL`), `$PROJECT`, `$BUCKET`, `$SUPABASE_URL`.
  - Realtime Database: `curl -s "$DB_URL/.json?shallow=true"` (expect `Permission denied`).
  - Firestore: `curl -s "$FIRESTORE_REST/projects/$PROJECT/databases/(default)/documents/<collection>"` (`$FIRESTORE_REST` is the Firestore REST base URL from Google's documentation) (expect `PERMISSION_DENIED`).
  - Storage: `curl -s "$STORAGE_REST/v0/b/$BUCKET/o"` (`$STORAGE_REST` is the Firebase Storage REST base URL) (expect 403).
  - Supabase: the anon key is public by design; safety comes from row level security. `curl -s "$SUPABASE_URL/rest/v1/<table>?select=*&limit=1" -H "apikey: <anon>" -H "Authorization: Bearer <anon>"` on every table with user data (expect `[]` or an error, never rows). In migrations, every table needs `enable row level security` and policies that use `auth.uid()`.
- Logged in as test user A, read user B's documents (expect denied).
- False positives: public collections by design (catalog, config); confirm with the owner.

## 2. Purchases and entitlements enforced on the server - S + D + net
Why: a paid feature unlocked by a local flag is free for anyone who edits that flag.
- Find premium checks: `grep -rnE 'isPremium|isPro|entitlement|subscribed|hasAccess' <src>`. Is the flag from the server (validated receipt or entitlement API) or only stored locally?
- Device: on the simulator or a debug build, flip the stored flag (iOS `plutil -replace <key> -bool YES "<container>/Library/Preferences/<bundle>.plist"`; Android `adb shell run-as <pkg>` and edit `shared_prefs`), relaunch. Premium content that loads from the server = finding.
- net: call a premium endpoint with a free or expired test account (expect 403). Replay a used receipt or purchase token to the app's validation endpoint (expect rejection; write, so ask first).
- Server must validate with the store (App Store Server API, Google Play Developer API), not trust the client.

## 3. Races and replay on writes - S + net
Why: double redeem of coupons, credits, likes or orders.
- Static: does the write use a transaction, a unique constraint or an idempotency key? Does the app disable the button and send one request per tap?
- net (test account, user OK): send the same write N times in parallel and count successes, expect one:
  `seq 10 | xargs -P10 -I{} curl -s -o /dev/null -w '%{http_code}\n' -X POST <url> -H "Authorization: Bearer <test token>" -d '<body>'`

## 4. Token lifecycle and object authorization - S + net
- Logout, then replay the old access token (expect 401). Replay an old refresh token after a refresh (expect failure if rotation is on).
- Decode the token header (`cut -d. -f1 <<< "$TOKEN" | base64 -d`): `alg` must not be `none`; `exp` must exist and be short.
- Object-level authorization (IDOR): with two test accounts, request A's object ids with B's token (expect 403 or 404). Ids that are sequential numbers make this urgent.
- Reset and magic-link tokens: single use and expiring (use one twice; expect the second to fail).

## 5. OAuth and social login in the app - S + D
- Login must run in the system browser (`ASWebAuthenticationSession`, Custom Tabs, the platform SDK), not an embedded WebView: grep `WKWebView`/`WebView` near login code. RFC 8252 (OAuth 2.0 for Native Apps, section 8.12) says native apps must not use embedded user-agents for authorization requests; Google sign-in in an embedded WebView fails with a `disallowed_useragent` error.
- PKCE: `code_challenge` with `S256` in the authorize URL (see it in a proxy or the debug log). No `client_secret` in the app: `grep -rn client_secret <src>` and in the built artifact.
- `state` (and `nonce` for OpenID) generated per login and checked on return.
- Redirects on verified links: Android `autoVerify="true"` and `/.well-known/assetlinks.json` served on the link domain; iOS associated domains and `/.well-known/apple-app-site-association` served on the link domain. A custom URL scheme alone can be claimed by another app.

## 6. WebViews - S
- Android: `addJavascriptInterface` (which origins can call it?), `setAllowFileAccess(true)`, `setAllowUniversalAccessFromFileURLs(true)`, `onReceivedSslError` calling `handler.proceed()`, `setWebContentsDebuggingEnabled(true)` not limited to debug builds, `loadUrl` with a URL taken from an intent or deep link without a check.
- iOS: `WKScriptMessageHandler` that does not check `message.frameInfo.securityOrigin`; `isInspectable = true` in release.
- React Native `react-native-webview`: `originWhitelist={['*']}` with an `onMessage` handler; Flutter `JavaScriptChannel` on pages from other origins.
- Host checks by `contains` or `startsWith` on the URL string are bypassable (an attacker host such as `<trusted host>.<attacker domain>` passes); compare the parsed host exactly.

## 7. Release flags on the built artifact - S
Check the artifact that ships, not only the source.
- Android: `aapt2 dump xmltree --file AndroidManifest.xml app.apk` (or `bundletool dump manifest --bundle app.aab`): `debuggable` must be absent or false; `allowBackup` and `dataExtractionRules`/`fullBackupContent` must exclude tokens and per-user data; `usesCleartextTraffic`; the network security config must not trust user certificates (`<certificates src="user"/>`) in release. `apksigner verify --print-certs app.apk`: a `CN=Android Debug` certificate is a debug build.
- iOS: `codesign -d --entitlements - App.app` (`get-task-allow` true = development build); `plutil -p App.app/Info.plist` for `NSAppTransportSecurity` (`NSAllowsArbitraryLoads` needs a reason).
- Exported Android components (activities, services, receivers, providers) with intent filters: each validates its input. `exported="true"` alone is not a finding.

## 8. Local storage across login, logout and reinstall - D
- List files before login, after login and after logout, and diff:
  iOS simulator `find "$(xcrun simctl get_app_container booted <bundle> data)" -type f`; Android debug build `adb shell run-as <pkg> find . -type f`.
- Search for the test account's email or token: `grep -rl '<test email>' <container>` (iOS); `adb shell run-as <pkg> grep -rl '<test email>' .` (Android). After logout, nothing per-user should remain.
- Tokens only in Keychain/Keystore (or an encrypted store using them), never in plain preferences or files.
- iOS Keychain items survive uninstall: does the app clear them on the first launch after a reinstall? Read the launch code.
- Logs: `adb logcat | grep -iE 'token|password|bearer|authorization'` during login; `xcrun simctl spawn booted log stream --predicate 'process == "<App>"' | grep -iE 'token|password|bearer'`.
- App switcher snapshot and screenshots on sensitive screens: Android `FLAG_SECURE`; iOS hide content when the app resigns active.

## 9. Deep links - D
- List them: Android intent filters in the manifest dump (section 7); iOS `CFBundleURLTypes` and associated domains.
- Logged out, open each one (`xcrun simctl openurl booted <url>`; `adb shell am start -a android.intent.action.VIEW -d <url>`): private screens need the login gate.
- Links that act (pay, delete, follow, change settings) need a confirmation screen, never act on open.

## 10. Secrets in the built app - S
- Android: `jadx -d out app.apk`, then `gitleaks dir out` (older gitleaks: `gitleaks detect --no-git --source out`). iOS: `strings App.app/<binary>`, and read bundled `.plist`/`.json`/`.js` files.
- Critical: server secrets (`sk_live_`/`sk_test_` payment keys, cloud service account JSON, private keys, database passwords, admin API tokens).
- Not secrets by themselves (Info): Firebase `AIza...` API keys in config files, publishable payment keys (`pk_`), Supabase anon keys, placeholders. They still need restrictions: test a Maps or other Google key from the shell (call the Geocoding API with only the key, e.g. `curl "$GEOCODE_URL?address=test&key=$KEY"`); a result means the key is not restricted to the app.

## 11. Network and TLS - S
- Certificate validation never disabled: Android custom `TrustManager` with an empty `checkServerTrusted`, `HostnameVerifier` returning true; iOS `URLSession` challenge handlers that call `.useCredential` without evaluating the trust; Dart `badCertificateCallback` returning true; React Native config that disables validation.
- Pinning, if present: has backup pins, and the pinned key does not rotate before users update (also a future-risk item).
- Per-user responses never cached by a CDN: `curl -sI -H "Authorization: Bearer <test token>" <endpoint>` must show `Cache-Control: private` or `no-store`. A shared cache of per-user data is Critical (`references/backend.md`).

## 12. Cryptography - S
`grep -rnE 'Cipher.getInstance\("AES"\)|AES/ECB|kCCOptionECBMode|IvParameterSpec\(new byte|SecretKeySpec\("|MD5|SHA1|java.util.Random|Math.random' <src>`:
ECB mode (also the Java default for `"AES"`), static or zero IVs, keys written in the code, MD5/SHA-1 for passwords, non-secure random for tokens. Prefer platform keystores and vetted libraries.

## 13. Biometrics - S
A finding only when biometrics protect a secret or a server action.
- Android `BiometricPrompt.authenticate(promptInfo)` without a `CryptoObject` is a UI gate only.
- iOS `LAContext.evaluatePolicy` alone is a UI gate; a Keychain item with `SecAccessControlCreateWithFlags` and a biometry flag ties the secret to the biometric check.

## 14. Dependencies and over-the-air updates - S
- Known vulnerabilities: `osv-scanner scan source -r .` (see `references/future-risk.md`).
- OTA updates signed: Expo `updates.codeSigningCertificate` in the app config; for other OTA services, check the vendor's signing option and that the service is still running.

## 15. Lower priority - S
- Secret fields: `secureTextEntry` / `textContentType` (iOS), `inputType="textPassword"` (Android), so the keyboard does not learn or the clipboard keep them.
- Sensitive confirm buttons on Android: `filterTouchesWhenObscured` against overlays.
- `PendingIntent` with an implicit intent must be `FLAG_IMMUTABLE`.
- Resilience (root or jailbreak detection, Play Integrity, App Attest, obfuscation): Info, unless the app handles money, health data or high-value accounts.

## Privacy and consent (keep)
- Every consent switch (analytics, ads, personalisation) is wired to every SDK it governs, reverts on a failed save, and logout resets SDK identities (`cases/005`).
- Per-user caches live in a non-backed-up location (iOS `Caches`, Android `cacheDir`), never store write responses, and are cleared on logout.
- Permissions asked only when needed, with purpose strings; collected data matches the privacy manifest and Data safety form (`references/store.md`).

## Avoid
- Generic "secret" regexes without reading the hit; flagging `exported="true"` alone; requiring root, jailbreak or Frida; calling an issue Critical before a request or device run shows it.
