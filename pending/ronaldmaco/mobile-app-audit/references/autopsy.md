# Autopsy: how a failure happened

Mode F. Use when something already failed in production: a crash, an ANR, an incident, a release that broke a flow, a rejection. Goal: the exact mechanism, when it entered, why only some users hit it, why nothing caught it, and what stops it from coming back. Name what happened, never who did it.

## 1. Identify the exact build
- Version, build number, OS, device, app install source and time of the failure, from the report or telemetry.
- iOS: the crash report's `Binary Images` UUID must match the dSYM: `dwarfdump --uuid App.app.dSYM`. A mismatch means a different build: stop and find the right dSYM.
- Android: use the `mapping.txt` of that exact release build (versionCode).
- No crash file (user video, support ticket): take frames (SKILL.md 2.1), server logs filtered by app version and time, `adb bugreport`, or an iOS sysdiagnose from the user's device.

## 2. Symbolicate
| Stack | Command |
|---|---|
| iOS | `atos -arch arm64 -o App.app.dSYM/Contents/Resources/DWARF/App -l <load address> <address>`, or drop the `.ips`/`.crash` into Xcode (Devices and Simulators, View Device Logs) with the dSYM next to the archive |
| Android (R8) | `retrace mapping.txt stacktrace.txt` (Android SDK `cmdline-tools/latest/bin`) |
| Flutter | `flutter symbolize -i stacktrace.txt -d <split-debug-info folder>` |
| React Native (Hermes) | `npx metro-symbolicate <bundle>.map < stacktrace.txt`, with the source map of that exact build |
| Crash tool | Crashlytics, Sentry, Organizer, Play vitals already symbolicate when symbols were uploaded; check they were for this build |

An unsymbolicated frame is not evidence; say so and keep the cause Suspected.

## 3. Timeline
- **First seen:** first app version and date in telemetry. Compare with the previous version (users affected per version).
- **What changed:** `git log --oneline <last good tag>..<first bad tag> -- <paths in the stack>`; `git log -S'<symbol>' --oneline` to find when a call appeared or vanished; `git blame -L <start>,<end> <file>` on the crashing lines.
- **Bisect when a repro exists:** `git bisect start <bad> <good>` then `git bisect run <test command>`.
- **Outside the code:** backend deploys, remote config and feature flag history, CMS edits, CDN rules, SDK server-side changes, a new OS release, certificate or key expiry, all in the same window. A crash that starts with no app release points here.

## 4. Cause of death
Write three separate things:
- **Mechanism:** the chain from trigger to failure, with file:line ("nil dereference at X when Y returns an empty list").
- **Trigger:** the exact conditions (data, account state, OS, region, network, timing, upgrade path) and why only these users had them.
- **Contributing factors:** what made it possible or worse (no error handling, release-only minification, no staged rollout).

Prove it: reproduce with the trigger (SKILL.md 2.3) or show the code path and the data that takes it. Then run the "try to refute" pass (`references/report.md`).

## 5. Why nothing caught it
Check each and record the answer: no test for this path; test target not building; condition missing from the scenario catalogue; only the debug build was tested; no staged rollout or it was skipped; no crash or error alert; the alert fired and nobody owned it; the bug was "fixed" before (SKILL.md 2.2) and only the symptom changed.

## 6. Treatment and prevention
- Fix with the normal loop: impact map, review gate, regression test that fails on the bad build (SKILL.md 2.4 to 2.7).
- Same pattern in siblings (2.8).
- One prevention per "why nothing caught it" answer: a test, a guard, an alert, a rollout step. Propose; do not add process without approval.
- Users still on the bad build: forced update, server-side guard, or data repair (2.10).

## Report block
```
Autopsy: <flow or crash title>
Affected: versions, OS, share of users or sessions (from telemetry, with source)
Time: first seen, last seen, trigger window
Cause: mechanism (file:line)
Trigger: conditions
Contributing factors:
Why it was not caught:
Fix and prevention: what, status, owner
Status: Verified | Suspected (what evidence is missing)
```
