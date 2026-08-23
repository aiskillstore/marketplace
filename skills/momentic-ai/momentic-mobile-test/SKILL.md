---
name: momentic-mobile-test
description: Create, run, and maintain Momentic mobile E2E tests and modules for Android and iOS. Use Momentic MCP tools for live device validation, and use direct v2 YAML edits only for high-confidence local mobile v2 changes.
---

# Momentic model

Momentic Mobile turns structured natural language into native and webview
automation on Android emulators and iOS simulators. Interactive steps resolve
targets into device actions; assertions can inspect screenshots, native
hierarchies, and webview state.

# Project files and formats

Mobile tests use `*.test.yaml`; modules use `*.module.yaml`. Test IDs live in the
test file's `id` field. Check `momentic.config.yaml` and test-level metadata
before assuming project defaults apply.

`fileType: momentic/mobile-test/v2` and
`fileType: momentic/mobile-module/v2` identify mobile v2. Treat missing or
different `fileType` as deprecated v1. Never edit v1 YAML directly; persist
changes through `momentic_test_splice_steps`.

Mobile v2 tests require `platform: ANDROID` or `platform: IOS`. Commands are
platform-specific.

V2 can reference modules, JavaScript, and injected files with relative paths.
Paths resolve from the YAML file containing the reference. Use `./...` or
`../...`, never absolute paths or `~`. Before moving, renaming, or deleting a
referenced file, grep its path and update or remove every reference. File-backed
JavaScript is v2-only; v1/MCP step strings carry code inline. Do not add internal
or generated fields to v2 YAML.

# Choose the workflow

Prefer these compact workflows unless the user requests something else:

- **Known v2 change:** inspect nearby patterns -> edit YAML -> lint when syntax
  or references are uncertain -> reload or restart if validating -> run the
  relevant range.
- **V1, unknown UI, or interactive validation:** start MCP session -> run any
  prerequisites -> preview a logical checkpoint -> splice it -> validate the
  saved range -> terminate.
- **New test:** create with `momentic_test_create` -> author a known v2 sequence
  in one YAML edit, or use MCP step-by-step when live discovery is needed.
  `momentic_session_start` only opens an existing test.

Use MCP as the default interactive interface. Preview and run wait 30 seconds by
default, then return a `stepRunnerId` while work continues. Leave
`timeoutSeconds` unset for most calls, especially single preset steps. Lower it
only when the coding agent's tool timeout is shorter; raise it only within a
larger tool timeout. Poll returned handles with `momentic_poll_runner`.

Prefer the test's configured remote device and app settings. Use local device or
app overrides only when the user explicitly requests them.

# Setup prerequisites

Run `npx momentic-mobile doctor` for initial setup and launch, driver, device,
or connectivity failures. Use `--json` when collecting a support report. See
the [doctor reference](https://momentic.ai/docs/cli-reference/momentic-mobile/commands/doctor).

Remote Android requires adb and `ANDROID_HOME`; local Android also requires
Java and Android Studio. Local iOS requires macOS and Xcode; remote iOS does not
once a simulator build is available. Follow the
[Android](https://momentic.ai/docs/platforms/android/app-setup) or
[iOS](https://momentic.ai/docs/platforms/ios/app-setup) setup guide rather than
guessing at missing dependencies.

Android WebView automation requires a build with WebView debugging enabled.
Debug builds usually provide it; release builds must enable it explicitly.
Missing debugging commonly appears as `No browser controller is attached to
the requested webview`. Mobile WebViews run through the device and do not need
a local Chromium installation.

# Before editing

Confirm the goal, user-visible success criteria, platform, app source, provider,
auth, and env requirements. Ask before previewing or running any step or AI
action that may submit, purchase, delete, send, create, or cause another
non-idempotent side effect. If approved, execute it at most once. Also ask before
using local device overrides, editing a shared module, restarting a long flow, or
running an expensive full test.

# Authoring rules

- Prefer natural-language targets. Use coordinates only for surfaces the AI
  cannot see, such as canvases, maps, games, or non-semantic custom views.
- Use native mobile steps for device actions and checks. See **JavaScript** under
  **Test execution behavior** for the exceptions.
- Do not add an initial launch/open-app step unless the test must switch apps or
  recover app state.
- Keep assertions minimal and user-driven. Validate material state changes
  before dependent actions.
- Prefer element or screen checks for deterministic state and AI checks for
  semantic visual state. Use visual-only AI checks only when the condition is
  fully visible and hierarchy data is unavailable, unreliable, or irrelevant.
- Use AI actions only when the user requests one or the existing test already
  uses one.
- Do not add optional or default-valued fields unless correctness requires them.
- Keep changes narrow. Preserve unrelated values, comments, ordering, and step
  style. Do not weaken a test to hide an app, asset, permission, data, or backend
  failure.
- Preserve the existing `before` / `steps` / `after` structure unless the test
  intent requires a change.

# Test execution behavior

## Cache and memory

Momentic caches native selectors, XML nodes, visible text, webview state,
coordinates, and other metadata. AI checks may also reuse past-result memory.
Stale cache or memory can explain a fast wrong-target action or a repeated
borderline verdict.

Cache is scoped by git metadata, including branch. Protected branches read cache
but do not write it unless `--save-cache` is used or `CI` is set.

- Change a step description when its intent changes. Never add
  `DANGEROUS_FORCE_DYNAMIC` or `--disable-cache` to locator steps; built-in cache
  validation refinds changing targets.
- Carry a successful preview's `CacheId` into the exact step being spliced.
- Reword an assertion when old memory no longer matches its intended condition.

## Readiness and timing

`emulator.smartWaitingTimeoutMs` budgets readiness before AI locate, cached
element retries, and other single-interaction waits. `emulator.waitForStability`
instead waits after each interactive step so its effects land before the next
step begins. Turn on `waitForStability` for apps that load incrementally,
animate between screens, or are broadly slow. It does not control pre-targeting
waits.

Within smart waiting, do not add sleeps. For longer or semantic readiness, use
an element, screen, or AI check that describes the required positive state.
Checks retry until their timeout; increase that timeout instead of polling with
JavaScript. See
[mobile configuration](https://momentic.ai/docs/configuration/mobile) for
project-wide timing settings.

## Common execution pitfalls

- Keyboard and input animations can race with typing. For slow iOS inputs, use
  TYPE's keyboard-settling option. For masked or formatted fields that move the
  cursor, target the input explicitly and add a keypress delay when needed.
- Scroll describes the content to reveal; swipe describes the finger gesture.
  Scrolling down finds lower content, while swiping up moves the finger up to
  reveal it.

## Devices, apps, and settings

Test-level settings can override project platform, app asset, emulator, locale,
timezone, geolocation, timeout, header, and environment defaults. Inspect both
levels before changing behavior.

For managed assets, use the `channels` artifact from
`momentic_get_artifacts` as the source of truth for valid platform channels,
tags, and aliases. Follow the current tool description for `defaultChannel` and
`defaultTag` behavior.

## Test context

Each run has a test-scoped `env` that persists across steps and modules.

- In v2, save returned values with `saveAs`; in MCP step strings, use
  `--env-key`. Use `setVariable(name, value)` in JavaScript when saving several
  values.
- Use `env.NAME` in JavaScript and module input expressions. Use
  `{{ env.NAME }}` in string fields, but not inside JavaScript source.
- Module inputs are JavaScript fragments stored as strings. Quote literal
  strings and use `env.X` for variables.

## JavaScript

Use native tap, type, swipe, scroll, wait, and check steps for device behavior.
They retain Momentic's targeting, smart waiting, cache, and traces. Do not use
JavaScript to reproduce those actions or poll UI state when a check can retry.

Use mobile JavaScript for test setup, data generation, APIs, databases,
OTP/email/SMS, assertions, and context writes that no native step expresses.
Keep one-off code short; for reusable v2 scripts, follow nearby project
conventions. See the
[mobile JavaScript command](https://momentic.ai/docs/reference/mobile-commands/javascript)
for current syntax.

# Working with mobile v2 YAML

Mobile v2 is human-editable. Tests use `before`, `steps`, and `after`; modules use
`steps`. Each step has one command key, durations are milliseconds, and runnable
step IDs are not stored in YAML.

Make the smallest edit and match nearby syntax. Common pitfalls:

- Android-only commands in iOS tests.
- Coordinates outside `0..100` in v2 YAML or `0..1` in MCP step strings.
- Adding IDs, cache blobs, artifacts, or the wrong detailed target field.

Consult the [v2 test format](https://momentic.ai/docs/core-concepts/test-format)
when syntax is unclear. Run `npx momentic-mobile lint` when schema or
file-reference risk warrants it.

After a disk edit, reload the active MCP test if available; otherwise terminate
and restart the session. `momentic_test_get` reads persisted state but does not
refresh an active session.

# MCP device workflow

Use tool descriptions and the platform-specific Step Authoring Guide returned by
session start for current arguments and step syntax. Do not duplicate that
reference material from this skill.

## Start and fetch context

Do not call context tools as session-start boilerplate. Use them on demand and
follow their descriptions, especially when they offer filters or return large
project data.

- If the test ID is known, start `momentic_session_start` by itself. Its Test
  Content provides active steps and runnable IDs; the platform comes from the
  test.
- Use `momentic_get_artifacts` only to discover unknown tests, modules,
  environments, local devices, simulators, or managed asset channels. Avoid
  redundant refreshes.
- Use `momentic_test_get` to inspect persisted state before starting, or to read
  a different test. Prefer active session and splice responses afterward.
- Use filtered `momentic_get_environment_variables` only when a step needs env
  data that is not already known.
- Use `momentic_module_recommend` -> `momentic_module_get` only when evaluating
  reuse; recommendation invokes AI and is not required to start a session.

Only one device operation may run per session. Do not issue concurrent preview,
run, state, or splice operations against the same session.

## Preview -> splice -> validate

1. For mid-test work, run through the preceding step once and keep the same
   session so authoring starts from the correct screen.
2. Preview forward in logical checkpoints such as login complete, permission
   handled, form ready, submission complete, or confirmation visible.
3. Read the returned screenshot first. Request emulator state only when the
   image lacks enough targeting or diagnostic context; request it again once if
   the app may still be settling.
4. Splice the successful checkpoint. Attach each returned `CacheId` only to its
   exact step, then read the splice response for current step refs.
5. Run the next dependent saved step or range. If a preview or run returns a
   `stepRunnerId`, poll it instead of starting another device operation.
6. Before finishing, when safe, run the smallest saved range covering the
   prerequisites, changed step, and next dependent contract. Reset first only
   when accumulated state could mask a failure.
7. Terminate the session when finished.

Batch obvious low-risk steps. Preview uncertain targets individually. For a
non-idempotent action, preview setup, splice the checkpoint, then run the
approved saved action at most once.

MCP screenshots are the default signal. Request serialized emulator state for
accessible names, native XML, webview structure, screen bounds, or offscreen
context. Read environment and installed-app artifacts only when diagnosing data,
launch, or install behavior.

# Modules

For a logical flow of roughly four or more reusable steps, check
`momentic_module_recommend` -> `momentic_module_get` -> reuse or inline. Modules
cannot contain modules. Ask before changing a shared module.

Respect declared parameters, defaults, and enum values. Module inputs are
JavaScript fragments, not `{{ }}` templates.

# Troubleshooting

## Device state and timing

- Wrong or stale screen: inspect the latest screenshot or emulator state; retry
  state capture once if the app is settling.
- Slow readiness at one checkpoint: add the narrowest element, screen, or AI
  check, or increase the existing check's timeout. Checks already retry; do not
  poll with JavaScript.
- Broadly slow targeting across the project: consider increasing
  `emulator.smartWaitingTimeoutMs`. Do not use it to mask one slow assertion.
- Long jobs or uploads: check for a stable positive result with an appropriate
  timeout, not a sleep.
- Permission dialog or system sheet: handle it explicitly before continuing.
- Drifted session: rerun the required saved range with `resetSession: true`.

## Infrastructure and app health

- Treat WDA, Appium, adb, emulator bootstrap or death, provider connectivity,
  lost webview context, and repeated device-state capture failures as
  infrastructure or app-environment signals. Start with the doctor check above,
  inspect logs and device health, and retry from a clean session before editing
  the test.
- If the app never becomes idle, continuous animation, video, or background UI
  work can block iOS accessibility snapshots. Prefer a test-mode switch that
  disables it; longer waits do not make a permanently busy app idle.
- Do not weaken assertions or inflate step timeouts to hide infrastructure
  failures. Report the failing subsystem and supporting evidence separately
  from test logic.

## Targeting and assertions

- Element absent: debug the prerequisite or scroll state. Element visible but
  not found: use visible text, role/name, and nearby context.
- Fast wrong-target action: consider stale cache, then correct the description.
- Use coordinate targets only when semantic targeting is unavailable. MCP
  fractions use `0..1`; v2 YAML uses percentages from `0..100`.
- Use `SCROLL_TO` when searching for a target. Use manual `SWIPE` only when no
  target exists or scrolling is not appropriate.
- Quoted text is literal. Quote only when the exact text must appear; otherwise
  describe meaning.
- Make assertions concrete about region, object, count, or state. Visual-only
  checks cannot inspect offscreen content or hierarchy.
- AI checks retry instantaneous snapshots until timeout. Prefer stable final
  state; use deterministic element or screen checks when they express the
  contract. See
  [Writing assertions](https://momentic.ai/docs/core-concepts/writing-assertions).

## Format and data

- V2 load failure: lint the file and check platform and relative references.
- Module failure: re-check parameters, defaults, enums, and input expressions.
- Missing env value: verify the producing save and `env.X` versus
  `{{ env.X }}` at the consumer.
- App launch/install issue: inspect test settings, channels/tags, installed-apps
  artifacts, and whether the session is remote or local.

After about three attempts at the same failure, stop and ask the user for
direction.
