# Console, sources, execution contexts, and UI

Start with an attached console/error listener and a fresh page snapshot. Use the correct page, frame, worker, and JavaScript execution context. Reproduce once without injected patches to preserve a trustworthy baseline.

## Console and source debugging

Capture the first relevant exception and its stack, including unhandled promise rejections, resource/CORS errors, and the action that caused it. Keep application console messages separate from uncaught exceptions. Correlate timestamps with network failures and application state; the last printed error may be a consequence of an earlier failure.

Use source maps to connect generated stack frames to repository code. Confirm the running build/version and map ownership; stale maps can point to the wrong source. Pretty-printing makes generated code readable but does not reconstruct original source. If maps are unavailable, report generated positions and investigate the matching bundle rather than invent source lines.

When breakpoints are needed, use the tool's supported debugger operation or DevTools Sources UI. Relevant CDP domains include `Debugger` and `Runtime`; match the current target schema. Prefer a scoped exception pause, source breakpoint, XHR/fetch breakpoint, or event-listener breakpoint tied to the failure. Disable irrelevant pauses and resume afterward. Paused execution distorts network timing, timers, and performance measurements.

Inspect selected locals and call stacks; avoid exporting whole globals or session objects. Evaluate bounded expressions returning small serializable summaries. `Runtime.evaluate` and browser evaluate tools execute real page code; arbitrary function calls, getters, or DOM clicks can have side effects. Read-only intent does not make an expression read-only. Release handles/object groups when using a low-level client so the debugger does not retain objects.

DevTools utilities such as `$0`, `getEventListeners`, or `debug` are console-specific. Do not assume they exist in ordinary page JavaScript; use a supported command-line API option or a real tool equivalent when needed. Do not monkey-patch `fetch` or `console` merely to duplicate an available network/console observer.

## DOM, CSS, rendering, and accessibility

For a broken control or layout, inspect the actual DOM node, computed style, box dimensions, state attributes, containing block, stacking/overflow, and event path. Pair the evidence with a screenshot where appearance matters. Refresh element handles/references after navigation or structural changes; stale references can silently address the wrong target.

Use an accessibility snapshot for roles/names/state and interaction targeting; it is not a visual-layout proof. Check keyboard focus/activation and actual disabled/hidden behavior when the task concerns interaction. Browser emulation is useful for viewport, DPR, media preferences, and throttling, but it does not establish real-device touch, screen-reader, or OS behavior.

Inspect responsive conditions and the cascade rather than guessing CSS overrides. Temporary style edits are experiments; a durable fix belongs in the intended source. If style/layout/paint/compositing cost is the symptom, collect a performance trace using [performance and memory](performance-memory.md).

## Workers and native webviews

Inspect worker/service-worker targets when the initiating code lives there; workers do not have the page DOM or ordinary window storage. Cross-origin and isolated execution contexts may require separate targeting. Do not evaluate in a different context solely to bypass an access boundary.

When the target is Electron, WebView2, Tauri, or another native host, use its approved debug surface and test the actual webview. Desktop Chrome success does not prove host messaging, clipboard, file dialogs, drag/drop, media, or native event behavior. Verify each affected OS with appropriate native checks when fixing the app.

Primary references: [Console overview](https://developer.chrome.com/docs/devtools/console/), [Console utilities](https://developer.chrome.com/docs/devtools/console/utilities/), [JavaScript debugging](https://developer.chrome.com/docs/devtools/javascript/), [source maps](https://developer.chrome.com/docs/devtools/javascript/source-maps/), [CSS inspection](https://developer.chrome.com/docs/devtools/css/), [Accessibility](https://developer.chrome.com/docs/devtools/accessibility/reference/).
