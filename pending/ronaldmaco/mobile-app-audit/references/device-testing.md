# Device testing

## Environment preflight (before the first build)
- Free disk: `df -h <work folder>`; a build plus tests needs ~10 GB. Below that, ask the user to free space before starting (an ENOSPC mid-session stops every command).
- One derived data / build folder per session (e.g. `-derivedDataPath <work folder>/dd`), reused for builds and tests; delete it when the work is merged.
- Test target builds today? If not, say so before promising tests.
- Latest OS simulator/emulator available, plus the minimum supported OS if the bug may be OS-specific.

## Tools: use what the agent has
The shell works in every agent and is the default. Use a device tool when the agent has one: it adds element lists and taps without coordinates guesswork. Tool names differ per agent; match by what the tool does.

| Need | Shell (any agent) | mobile-mcp (any MCP client) | agent-device (CLI, or MCP via `agent-device mcp`) | Agent-specific simulator tools (e.g. Claude Code iOS Simulator) |
|---|---|---|---|---|
| Live view for the user | `open -a Simulator`; emulator window | n/a | n/a | attach / open panel |
| Install + launch | `xcrun simctl install booted <app>` + `xcrun simctl launch booted <bundle>`; `adb install`, `adb shell am start -n <pkg>/<activity>` | `mobile_install_app`, `mobile_launch_app` | `agent-device install <bundle> <path>`, `agent-device open <app> --platform ios\|android` | launch with the `.app` path |
| See the screen | `xcrun simctl io booted screenshot f.png`; `adb exec-out screencap -p > f.png`; Android elements: `adb shell uiautomator dump /dev/tty` | `mobile_list_elements_on_screen` (preferred), `mobile_take_screenshot` | `snapshot -i` (element tree with `@e` refs, preferred), `screenshot f.png` | screenshot (small scale) |
| Act | `adb shell input tap/text/swipe`; iOS has no shell tap: use Maestro or a device tool | `mobile_click_on_screen_at_coordinates`, `mobile_swipe_on_screen`, `mobile_type_keys` | `press @e2 --settle`, `fill @e7 "text"`, `scroll down --until '<selector>'` (iOS too) | tap, swipe, type, key, button |
| Read stored state | iOS: `plutil -p "$(xcrun simctl get_app_container booted <bundle> data)/Library/Preferences/<bundle>.plist"`; Android: `adb shell run-as <pkg> cat shared_prefs/<file>.xml` | n/a | n/a | shell |
| Deep links | `xcrun simctl openurl booted <url>`; `adb shell am start -a android.intent.action.VIEW -d <url>` | `mobile_open_url` | `open <app> "<url>"` | open URL |
| Push (simulated) | `xcrun simctl push booted <bundle> payload.apns`; Android: send a test message from the FCM console or backend | n/a | `push <bundle> payload.apns` (iOS), JSON payload (Android) | shell |
| Dark mode, rotation | `xcrun simctl ui booted appearance dark`; `adb shell cmd uimode night yes`; `adb shell settings put system user_rotation 1` | `mobile_set_orientation` | `settings appearance dark`, `orientation landscape-left` | appearance, rotate |
| Fresh state | `xcrun simctl uninstall booted <bundle>`; `adb shell pm clear <pkg>` | `mobile_clear_app_data` | `settings clear-app-state`, `reinstall <bundle> <path>` | reinstall |
| Logs, crashes | `xcrun simctl spawn booted log show --last 2m --predicate 'process == "<App>"'`; `adb logcat --pid=$(adb shell pidof <pkg>)` | `mobile_get_device_logs`, `mobile_list_crashes` | `logs clear --restart`, `logs path`, `network dump 25` | shell |
| Video evidence | `xcrun simctl io booted recordVideo out.mp4`; `adb shell screenrecord /sdcard/out.mp4` | `mobile_start/stop_screen_recording` | `record start out.mp4`, `record stop` | shell |
| Performance | Android: `adb shell dumpsys gfxinfo <pkg>` (janky frames), `adb shell dumpsys meminfo <pkg>`; iOS: `xcrun xctrace record --template 'Time Profiler' --attach <App> --time-limit 30s` | n/a | `perf frames`, `perf memory sample`, `perf cpu profile start\|stop\|report` | shell |
| Repeatable flows | `maestro test flows/` | Maestro | Maestro | Maestro |

If the agent has no way to tap on iOS, run the flow with Maestro or agent-device (both tap on iOS from a shell), or ask the user to perform the steps while you read logs and stored state.

agent-device is optional (install: `npm install -g agent-device@latest`, then `agent-device doctor`; needs Node.js 22.12+; `agent-device capabilities --platform <p>` lists what a target supports). Two limits: its `@e` refs are valid only for the latest snapshot, so snapshot again after each screen change; and its iOS `network dump` shows only what the app logs, so a request missing there is unproven, not "never sent".

Build with the project's tooling; test the **release** configuration before shipping. If the build cannot run here (signing), ask the user to build and give the product path.

## Loop for every step
1. Look (element list if available, else a small screenshot).
2. Act on the centre of the element.
3. Verify the expected change before the next step; never act blind.
4. Record: case id, step, expected, actual, evidence file.

## Pitfalls that produce false results
- **Taps during scroll momentum or transitions land on the wrong row.** After a swipe, take a screenshot before tapping; use slow swipes (`duration` >= 1.5 s).
- **Taps right after a tab/screen change can be lost or hit the previous screen.** One action, then look.
- **Confirm saved state from storage or the server**, not only from the screen (e.g. read the stored user after "Done").
- `simctl launch` may start the app in the background; open it from its icon or the tool's `launch`.
- The first launch after a reinstall can show a long blank screen; judge launch time on a normal relaunch.
- Stray taps can open external pages; note them, close them, and do not report them as app bugs without reproducing.

## Conditions for critical flows
| Condition | How |
|---|---|
| Slow network | Network Link Conditioner; emulator `-netdelay`/`-netspeed` |
| Network lost mid-action | Wi-Fi off right after tapping; `adb shell svc wifi disable`; agent-device `settings wifi off` |
| Other region | VPN on host; confirm with ipinfo |
| App killed and relaunched | terminate, launch |
| Fresh install / upgrade | uninstall, or install old build then new |
| Locked device at launch | real device, for keychain flows |
| Dark mode, large text, rotation, tablet | appearance, font scale (agent-device `settings text-size accessibility-extra-large`), rotate, iPad |
| Oldest supported OS | simulator/emulator with the minimum OS |
| Background then resume after minutes | token expiry, sockets |

## Minimum scenario catalogue
- **Access:** sign up, log in (valid, wrong password, unconfirmed), forgot/reset (cold and warm link), log out, delete account, session survives kill and reboot.
- **Every write action:** persists after tab switch, kill, logout/login; offline failure keeps input; double tap saves once.
- **Every list/filter:** first load, refresh, paginate to the end, empty, offline, each filter shown as selected on every screen, count equals the oracle, search with/without results.
- **Every detail screen:** from list, deep link and push; media plays or fails gracefully.
- **Settings/account:** each row opens the right place, external links return, values match the server.
- **Purchases:** buy, cancel, restore, expired subscription.
- **Every modal and sheet:** closes while a request is in flight without a crash or a late update to the screen below.
- **Every failed load:** has a retry that works without killing the app.
- **Back, swipe back and process death:** keep what the user typed in a form (Android: `adb shell am kill <pkg>` while the app is in the background, then reopen it).

## First-time user sweep (modes C and D, onboarding to first success)
Run the path from first launch to the app's first real success (account created, first item saved, first purchase in test mode) as five users. Each one is a set of device conditions and a rule for acting; record every point where they get stuck, confused or lose input, with a screenshot.

| User | Conditions | Acts like this |
|---|---|---|
| **Impatient** | Normal device and network | Taps the first obvious button, skips every text, gives up at the first error or wait over a few seconds without feedback. |
| **Skeptic** | Normal | Opens privacy policy, terms, prices and permission prompts before signing up; every link must open and say what the app does with the data. A permission asked before it is needed, or a price not shown before paying, is a finding. |
| **Small and slow** | Smallest supported phone (`xcrun simctl list devicetypes`; Android `adb shell wm size 720x1280` and reset with `wm size reset`), largest text (`xcrun simctl ui booted content_size accessibility-extra-extra-extra-large`; `adb shell settings put system font_scale 2.0`), slow network (Network Link Conditioner; `adb emu network speed edge`, `adb emu network delay gprs`) | Normal use. Clipped text, hidden buttons, the keyboard covering inputs, spinners with no end and no retry are findings. |
| **Literal reader** | Another language and a pseudolocale (iOS: `xcrun simctl launch booted <bundle> -AppleLanguages "(de)"` or `-NSDoubleLocalizedStrings YES`; Android: `adb shell cmd locale set-app-locales <pkg> --locales de-DE`, or `en-XA` / `ar-XB` when `pseudoLocalesEnabled` is on in the debug build) | Does only what the screen literally says; no guessing from icons or habits. Untranslated strings, truncated labels, icon-only actions and unclear errors are findings. |
| **Breaker** | Normal; a test account and a test backend only | Double taps every button, pastes long text, emoji and symbols into every field, goes back or swipes back mid-flow, rotates, kills the app during a save. Android: `adb shell monkey -p <pkg> -s <seed> --throttle 200 -v 500` (record the seed so it can be replayed). Duplicate writes, lost input, crashes and stuck loading are findings. |

Merge the results: one finding per cause (not per user), with the users that hit it listed. Order by severity (`references/report.md`); within the same severity, the issue more users hit goes first. After the fixes, run the same five users again on the new build and attach before/after evidence; an issue is fixed only when none of them hit it.

Save evidence in the work folder with case ids in file names.
