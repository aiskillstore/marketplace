---
name: mobile-app-audit
description: Audit, QA, debug and bug-verify a mobile app (iOS, Android, Flutter, React Native, any stack) with evidence - code review, device testing, backend/CDN, security, performance, accessibility, store readiness - and fix without changing the design. Use whenever users, testers or reviewers report that something in a mobile app is wrong, wrong only for some users, intermittent, or still failing after a fix (for example payments, checkout, login, screens that never load), to find the root cause and fix it; also to audit, test or validate an app, to confirm a reported bug or a claimed fix, before store submission or after a rejection.
---

# Mobile App Audit

Goal: every screen and flow does what the user expects under real conditions (slow or no network, other regions, killed app, old data, old builds), with no visible change to the design, and every claim backed by evidence. Nothing is "fixed" until the whole impact map of the bug passes on the build the real user will run, so the same bug cannot come back through another path.

<!--
Maintainer notes
- Author: Ronald Maco (https://github.com/ronaldmaco)
- v2.6.0 (2026-11-17): modes F (autopsy) and G (future risk); references security.md, store.md (rules read
  on official pages), telemetry.md, autopsy.md, future-risk.md; build health gates, measured performance,
  refute pass, first-time user sweep. Evals e015-e018: 4/4 with, 2/4 without (1 run each; favour the skill).
  Description unchanged (trigger not re-measured).
- v2.5.0 (2026-11-12): description also covers user/tester/reviewer reports of wrong, intermittent or still-failing behaviour; trigger eval 8/8 should, 0/6 should not (1 run each; 2.4.1: 6/8, 0/6).
- v2.4.1 (2026-11-11): README and version metadata only (honest claims on findings, evals and agents); skill unchanged.
- v2.4: sibling check method, Android patterns from cases 008-012.
- v2.3 (2026-11-06): agent-neutral wording (tools by capability, work folder), install for any agent.
- v2.2 (2026-11-06): cases 002-007, evals/, example report; patterns and checks from those cases.
- v2.1 (2026-11-05): core file + references loaded on demand (token economy); impact map, ground-truth
  oracle, backend catalog sweep, fix review gate, environment preflight, new patterns from a real case
  (a fix that dropped id 0 filters made the API ignore the filter). See cases/.
- v2 (2026-11-04): single file with modes, verification loop, delivery check, security, performance.
- v1: static checklist, backend checks, device testing, store review.
- Revert: check out the previous tag/commit of https://github.com/ronaldmaco/mobile-app-audit.
-->

## 0. Pick the mode first

Say which mode you use. Do not run a full audit when a targeted one answers the question.

| Mode | When | Run |
|---|---|---|
| **A. Bug verification** | A user reported a bug, sent videos/screenshots, or a fix "did not work" | Section 2 (all of it) |
| **B. Fix verification** | Someone says a bug is fixed | 2.3, 2.5 to 2.10 |
| **C. Targeted audit** | One area (login, filters, payments, push...) | Inventory of that area + `references/checklist.md` for it + 2.4 impact map per finding |
| **D. Full audit** | Before a release, new codebase, "make sure the app has no bugs" | Everything, in order, including the first-time user sweep (`references/device-testing.md`) and mode G |
| **E. Store readiness** | Before submission or after a rejection | `references/store.md` + backend checks from the review region |
| **F. Autopsy** | Something already failed in production (crash, ANR, incident, broken release): how, when, why it was missed | `references/autopsy.md`, then 2.4 to 2.10 for the fix |
| **G. Future risk** | "Will it still work next year?", before a big upgrade, yearly check | `references/future-risk.md` |

References (read only the one you need, when you need it):
- `references/checklist.md` - inventory, build health gates, static checklist, performance, accessibility, stack notes.
- `references/security.md` - ranked security checks (OWASP MASVS based), each with a static, device or request check.
- `references/backend.md` - endpoint checks, CDN/WAF, catalog sweep, ground-truth oracle scripts.
- `references/device-testing.md` - tools, environment preflight, step loop, conditions, scenario catalogue, first-time user sweep, pitfalls.
- `references/store.md` - App Store / Google Play rules confirmed on the official pages, each with how to verify it.
- `references/telemetry.md` - production crash, ANR and error data.
- `references/report.md` - finding and report format, audit log.
- `references/autopsy.md` - production failure postmortem: exact build, symbolication, timeline, cause, why it was missed.
- `references/future-risk.md` - what breaks within a year with no code change: store minimums, deprecations, abandoned dependencies, expiring certificates; dated official sources only.

## 1. Principles

1. **Evidence over opinion.** Each finding is **Verified** (reproduced, proven by a request, or seen in code with a concrete trigger) or **Suspected**. Never present a suspicion as fact or mark something tested that was not.
2. **Reproduce before you fix**, with the reporter's exact state (selection, account, build), not a similar one.
3. **Root cause, not symptom.** Ask "why" until the answer is a mechanism with file:line. If the cause is in the backend/CMS, it is a finding of its own with an owner, even if the app also gets a patch.
4. **Fix the whole class, not the instance.** Every bug gets an impact map (2.4). The fix must pass all of it.
5. **Never hide the user's input.** A fix that drops, skips, defaults or hides what the user chose or what the server sent is a workaround: name its user-visible consequence and prefer an honest result (empty, error, explanation).
6. **Same look, correct behaviour.** Keep layout, copy and navigation. Allowed: loading states, clear errors, retry. Anything else is proposed, not done.
7. **Smallest safe fix**, in the surrounding style, no unrelated refactors or upgrades without approval.
8. **One step at a time.** Describe, get approval, show the diff, commit only when asked, in the project's commit format.
9. **Siblings.** Check every finding in the other platform and sibling apps sharing code or backend, unless the user excludes them.
10. **Secrets stay secret.** Never print tokens or passwords; prefer test accounts.
11. **"Done" means delivered** (2.10).

## 1a. Agent and tools

Works in any agent that reads `SKILL.md` (Claude Code, Codex, Cursor, Gemini CLI, GitHub Copilot, OpenCode...). It needs only file reading and a shell. Device tools (mobile-mcp or an agent's own simulator tool), a browser and sub-agents are optional; `references/device-testing.md` maps each need to the shell and to those tools. Tool names differ between agents: pick tools by what they do.

**Work folder:** keep evidence, oracle scripts, sweep data and builds in the agent's scratch or temp folder, outside the app repo, unless the user asks otherwise.

## 1b. Token economy (always)

- Read the audit log and project docs first; then targeted search (grep the screen, endpoint, error string). Read whole files only on the path that matters.
- One question, one cheap probe: ask the API or read stored state (`plutil`, `adb shell run-as ... cat`) before navigating the UI by hand.
- Batch API probes in one script that prints only counts, ids and names, never full JSON.
- Screenshots at scale 0.3-0.4; full scale only to read small text. Prefer element dumps when the tool has them.
- Filter logs before reading (`grep`, `--predicate`, a time window).
- Videos: key frames only (2.1).
- Stop exploring when the cause is proven; spend the saved effort on the impact map.
- If the agent can run sub-agents or background tasks, delegate wide "where is X used" sweeps to one and keep only its conclusion.
- Load a reference file only when its section is needed; never all of them up front.

## 2. Bug verification loop

### 2.1 Intake: turn the report into a test case
Get (or ask only for what is missing): exact steps and state (what was selected/typed), expected vs actual, frequency, device, OS, app version **and build**, install source (store, TestFlight, internal, OTA channel), region/network, account, time of failure.
From videos extract frames, do not watch everything:
```bash
ffmpeg -i in.mp4 -vf "select='gt(scene,0.3)',scale=720:-1" -vsync vfr frames/s_%03d.png
ffmpeg -ss 00:00:12 -i in.mp4 -frames:v 1 frames/at_12s.png
```
Write it as: precondition, steps, expected, actual.

### 2.2 History check
`git log` for earlier fixes of the same area. If this bug was "fixed" before, read that diff first: a previous fix is the first suspect (it may have patched a symptom or hidden data).

### 2.3 Confirm what runs, then reproduce
- Build installed (version + build, OTA id) and its commit; backend/environment it talks to.
- Reproduce on the same conditions. Repeat "sometimes" bugs 5+ times, under slow network, network loss mid-action and app kill.
- **Ground-truth oracle:** call the API with the exact parameters the app sends for that state and compare with the screen (`references/backend.md`). A match explains the bug in one step ("the app sends no venue filter, so the API returns every event in the category").
- Not reproducible: list the differences with the user's setup and what to collect next. Status stays Suspected.

### 2.4 Root cause and impact map
Trace UI action -> state -> request -> response -> parsing -> persistence -> UI, plus the backend data. Then build the **impact map** before writing any fix:

| Axis | List every... |
|---|---|
| Input classes | valid, empty, null, 0/-1/sentinel ids, duplicates, unknown or removed on the server, very long, special characters, other locale |
| Consumers | every screen, component and request that reads the same data (list, chips, filter sheet, home, favourites, onboarding, settings, widgets, deep links, analytics) |
| States | fresh install, upgrade with old stored data, logged out/in, offline, after kill, other account, both platforms |
| Data source | is the backend data itself valid? (`references/backend.md` catalog sweep) |

Each cell gets an expected result taken from the oracle or the spec, not from the current code. The expected result is **per consumer**: an explicit filter or search must show an honest empty state, while a curated feed (Home) may widen its query, visibly and in a documented order (`cases/003`). Cells that fail are findings; cells you cannot test are listed as not tested with the reason.

### 2.5 Fix (with approval) and review gate
Smallest change at the cause. Before proposing it, answer in writing:
- Does it drop, skip, default or hide any user choice or server value? If yes, what does the user see instead, and is that honest?
- What does an **empty** value mean to every consumer? (Empty filter = "any" for most APIs.)
- Which impact map cells change behaviour, and are they all still correct?
- Does it need a backend/CMS change too? Name the owner and the exact data to fix.

### 2.6 Regression tests
A test that fails before and passes after, per failing impact map row, at the cheapest level (XCTest, JUnit, `flutter test`, Jest; Maestro/XCUITest/Espresso for UI; a curl script for backend). First confirm the test target builds and runs at all; fix that setup if needed (with approval) and say so.

### 2.7 Verify
Re-run the exact reported scenario and the whole impact map on device, compare each with the oracle, then a short regression of neighbouring flows. Use the **release** configuration before shipping. Attach before/after evidence.

### 2.8 Sibling check
Same pattern in other screens, the other platform and sibling apps (or note the user excluded them). Cheap method (`cases/008`): use the fix commits of one platform as the checklist; for each, grep the other platform for the same endpoint, field or screen, read only that path, and mark Verified present / Verified fixed / Not applicable (a library may already handle it) with file:line. Port the same behaviour so both platforms act alike.

### 2.9 Record the case
Update the audit log (`references/report.md`). If the skill missed something, propose an anonymised case for the skill repo's `cases/`, and write it only with the user's OK. Anonymise before writing anything outside the app's own repo: change the domain, rename every class, field, key, endpoint and user-visible string, drop exact counts, ids and versions, and name SDKs/CMS by kind ("an analytics SDK"). Keep only the mechanism. Never copy app code; write a new minimal fixture.

### 2.10 Delivery check
- [ ] Merged into the release branch; release build made after the merge; new build number above what is already in TestFlight/Play.
- [ ] Both platforms / sibling apps include it, or the gap is stated.
- [ ] Backend/CMS/config deployed to production; permissions saved; caches (CDN, API, app HTTP/image) purged or versioned.
- [ ] OTA published to the right channel and runtime version.
- [ ] Store build released; forced-update path if old builds stay broken.
- [ ] Old local data migrated or cleared.
- [ ] Reporter told which version has the fix, and what still depends on someone else (e.g. CMS data).

Why "fixed" bugs come back: old build; symptom patched or data hidden; another path triggers it; one platform only; backend not deployed; cache; stale local data; region/CDN rule; a race the test setup does not hit; backend data still wrong.

## 3. Recurring patterns (check explicitly)

- **Empty filter means "any":** dropping invalid values leaves an empty list and the API returns everything.
- **Sentinel ids colliding:** id 0/-1 used both for "none" and for real options the server could not map.
- **Silent drop:** invalid or unknown values removed without telling the user; the screen shows something the user did not ask for.
- **Orphan backend data:** options with no linked content, content with no category, links that 404.
- **Double callback / stale cache:** failure callback then cached success; stale value applied as fresh.
- **Read racing a write:** refresh overwrites a newer local value while a save is in flight.
- **Optimistic close:** form closes before the server confirms.
- **Equality on decorated models:** full equality where one side has extra fields; compare by stable id (or normalised name when ids are unreliable).
- **Hard-coded labels or ids** drifted from the server list.
- **Errors swallowed:** connection/parse errors without a response show no message.
- **Geo/WAF challenge** returning HTML to apps or the review region.
- **Stale token on public auth routes.**
- **Token refresh stampede.**
- **Lifecycle/SDK drift:** APIs no-op or removed on the latest OS; keychain before first unlock.
- **Release-only crashes:** minification, Hermes/AOT differences.
- **Bad local data survives updates.**
- **Fix on one platform or one sibling only.**
- **Main-thread SDK or analytics calls.**
- **Dead test setup:** test target that has not built for years, so "tests pass" means nothing.
- **Write used as a read:** a fetch done with PUT/POST/PATCH; needs write permission, touches timestamps, can overwrite data.
- **Empty result shown as an error:** "no data for these preferences" rendered like a failure; check the whole combination space, not one case.
- **Unpaired events:** hide without show, resume without pause, end without begin; handlers that assume the pair crash.
- **Late async result on a reused view:** an image or response arrives for a cell that now shows another item.
- **Consent not reaching the SDK:** a privacy switch saved locally but never passed to analytics/ads/push SDKs.
- **Flag reset only on success:** a loading/in-flight flag that a failure never clears blocks every later load.
- **Refuse-new plus drop-stale guards:** "already loading" rejects the new query and "not current" drops the old answer, so the screen shows the wrong content.
- **Errors without a body vanish:** timeouts and offline have no response body; a handler that needs one never reports them.
- **Cache returned as success:** a failed request answered from cache, including writes that never reached the server.
- **Non-deterministic getter:** random, time- or counter-based computed property read more than once (shown item is not the opened one); `random()`/`first()` on an empty list.
- **Mutable shared constants as context:** properties set on enum constants, singletons or companion objects leak into the next caller.

## 4. Definition of done

Closed only when: cause explained with evidence; impact map built and every cell passes or is listed as not tested with a reason; fix approved; regression tests pass; reported scenario passes on the release configuration; siblings checked; backend owner notified if the data is wrong; delivery check complete; audit log updated. Otherwise report the exact state ("fixed in code, not released", "app fixed, CMS data pending").
