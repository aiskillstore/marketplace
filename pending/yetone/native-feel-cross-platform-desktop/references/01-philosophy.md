# 01 — The Architectural Philosophy

The central question this architecture answers:

> **How can a desktop app simultaneously deliver convenient cross-platform development AND near-native performance, when these two goals usually pull against each other?**

The default trade-off is forced: choose a stack and accept its consequences. Pure native gets you performance and loses cross-platform — every feature ships twice. Electron gets you cross-platform and loses performance — every interaction feels web. Tauri sits between them but inherits enough of both costs to satisfy neither.

This architecture refuses the trade-off. It does so by being precise about **what should be shared** and **what must diverge**, then placing the boundary at exactly the altitude where both can win.

Eight tenets follow from this central insight. Each one names a tension and the structural resolution. When advising, cite the tenet by number and short name.

---

## 1. Place the seam at the rendering surface

The cross-platform boundary should be drawn at the **WebView surface**, not at the app boundary and not at the business-logic boundary.

- **Below the WebView** — windowing, hotkeys, materials, file dialogs, system tray, accessibility, input methods — *must* be native, because no abstraction over these is fast or correct enough.
- **Above the WebView** — the React tree, business logic, extension API, AI orchestration — *should* be shared, because reimplementing these per OS doubles every feature's cost.

The seam exists because at this exact altitude, each side has the **least leverage to mimic the other**. Native code can't fake native materials through an abstraction layer; web code can't economically be rewritten twice. So you draw the line here, not at a more convenient-sounding place like "all UI in one stack" or "all platform code in one stack."

**Consequence:** Any cross-platform decision can be tested by asking: *is this above the rendering surface or below it?* Below → write it twice in idiomatic native. Above → write it once in TS/React. Refuse to draw the line anywhere else.

---

## 2. One schema, many languages

A four-runtime system (native shell, WebView, Node backend, Rust core) is normally a maintenance nightmare. Types drift, messages mismatch, debugging gets routed across boundaries no human can trace.

This architecture makes polyglot survivable by declaring **one schema** for all inter-process messages, then generating typed clients for every runtime. The polyglot cost is paid **once** at the declaration, never again at the call site. Drift becomes impossible because every language fails to compile when the schema changes.

**Consequence:** Hand-written marshalling between languages is forbidden. If you can't generate a typed client for a runtime, don't add that runtime to the system. (See `references/04-ipc-contract.md` for the UniFFI-based pattern that Raycast ships.)

---

## 3. Adopt the platform; don't compete with it

The platform's blur is faster than your blur. The platform's scrollbar is more correct than your scrollbar. The platform's dark mode follows the user's preference better than your dark mode. The platform's focus ring matches the user's other apps and yours does not.

Every time you reimplement a platform feature you are simultaneously *slower*, *less correct*, *more brittle to OS updates*, and *more annoying to the user who is fluent in their OS*. The work is paid for in performance, polish, and compatibility, and the return is essentially zero — because the platform was going to do this for you.

**Consequence:** When a feature can be implemented by "let the OS do it," that is the implementation. Custom is the last resort, reserved for the small set of behaviors where the OS default actively *breaks* native feel (e.g., WebKit's browser-style context menu inside your app — see `references/03-webview-survival.md`).

---

## 4. Performance is a property of perception

The user does not experience MB or FPS. The user experiences "the launcher came up when I hit the hotkey" or "it didn't." "I typed and the result updated" or "it stuttered." "I dragged the window and it moved" or "it lagged."

System monitors measure *resources consumed*. The user measures *promises kept*. These are different. An app can show 400 MB resident and feel instant. An app can show 80 MB resident and feel sluggish. Optimization energy must go to the second metric, not the first.

**Consequence:** Before optimizing anything, define the perception target: a specific keystroke, a specific frame, a specific latency the user will feel. Then measure that. "Reduce memory by 20%" is not a target if the user cannot perceive the reduction. (See `references/05-memory-truths.md` for the six common measurement mistakes this principle prevents.)

---

## 5. The short iteration loop is the product

A native UI codebase iterates in ~30 seconds (recompile, relaunch, restate). A React UI codebase iterates in ~200 milliseconds (hot module reload, state preserved). Over a year of design work, this 150× gap is the difference between an app whose UI feels finished and one whose UI feels unfinished — not because the team is more talented, but because they could afford 150× more iterations.

This is *the* reason the architecture pays the cross-platform tax. The tax buys not only "runs on two OSes" but "iterates 150× faster on its hottest surface, where the design team spends 80% of its time." The iteration loop is the silent compound interest of the architecture.

**Consequence:** Any architectural change that lengthens the UI iteration loop — moving UI back to native, adding a build step, introducing a slower transpiler — must justify itself against this compounding cost. Almost none can.

---

## 6. Cross boundaries intentionally

The architecture has many process boundaries: native shell ↔ WebView, WebView ↔ Node, Node ↔ Rust, Rust ↔ native shell. Each crossing has a cost: serialization, scheduling, context switching, debugging difficulty. These costs are bearable only because boundaries are crossed **intentionally** — async, batched, schema-typed, observable — and never *accidentally*.

The failure mode is treating IPC like a function call. Accidental hot loops across a process boundary (e.g., a React effect that sends a message to Node on every keystroke that triggers a chain of further messages) destroy performance invisibly. Each individual hop looks cheap; the aggregate is catastrophic.

**Consequence:** Every IPC call is a design decision. Trace every call's frequency and payload in development. Batch where you can. Cache where it's safe. Treat the IPC layer as a public API of each process, not as a hidden implementation detail.

---

## 7. Identity is muscle memory

When this architecture is used to rewrite an existing app, it is rewriting *everything*: the language, the UI framework, the renderer, the process model. By any normal measure of "is this the same app," the answer should be no.

Yet to the user, it is the same app — if and only if the user's **muscle memory** still works. ⌘-Space still opens the launcher. The first result is still the one they were going to pick. The shortcuts they typed yesterday still work today. The rank order of fuzzy matches still feels right. *These* are the app, in the only sense the user cares about. Everything else is implementation detail.

**Consequence:** During a rewrite, treat muscle-memory invariants as the hard constraint and the implementation as the variable. The temptation to "modernize" UX details during the rewrite is the temptation to break identity in exchange for cosmetic novelty. Resist it.

---

## 8. Separate baseline cost from margin cost

Some costs are **baseline**: they come bundled with the architectural choice and cannot be reduced without abandoning the choice. The system WebView's ~50 MB. Node's ~12 MB. Chromium's GPU helper process. These costs are *rented* from the platform.

Other costs are **margin**: they are produced by code you wrote. Your bundle size, your dirty heap pages, your cache sizes, your subscription leaks. These costs are *owned* by you.

The classic mistake is to spend optimization energy on baseline costs (impossible) while ignoring margin costs (where every win is available). The reverse is the discipline: accept the baseline honestly, then attack margin with full force.

**Consequence:** Before any "make the app smaller / faster" project, classify each cost as baseline or margin. Margin is where the work goes. Baseline is what you communicate to the user, never apologize for, and design around.

---

## How the eight tenets resolve the central tension

| Tension | Resolved by |
|---|---|
| Cross-platform without losing native feel | T1 (seam at rendering surface) + T3 (adopt the platform) |
| Polyglot without drift | T2 (one schema, many languages) |
| Performance perception under a WebView baseline | T4 (perception, not measurement) + T8 (baseline vs margin) |
| Iteration speed under architectural complexity | T5 (iteration loop is the product) |
| IPC overhead in a four-process system | T6 (cross boundaries intentionally) |
| Continuity across a rewrite | T7 (identity is muscle memory) |

If a proposed change to the architecture appears to break the central tension's resolution, the change is suspect. Find which tenet it contradicts, name the tension that tenet was resolving, and ask whether the proposer has a better resolution for that same tension — or whether they're just accepting the trade-off the architecture refused.
