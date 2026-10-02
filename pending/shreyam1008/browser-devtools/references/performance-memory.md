# Performance, CPU, and memory

Identify the actual symptom: slow loading, delayed input, a stuttering animation, CPU usage, or growth after repeated actions. Use a representative production build when available; development instrumentation changes costs. Record browser/OS/device, viewport/DPR, headless mode, build, cache/worker state, and any CPU/network throttling.

## Choose the artifact

| Artifact | Answers | Does not establish |
|---|---|---|
| Chrome performance trace | Loading/rendering tasks, interactions, layout/paint, critical paths | Field population percentiles or every native/device behavior |
| V8 CPU profile | Which sampled JavaScript stacks consume execution time | Network wait or complete paint/GPU cost |
| React profile | Component render costs and commit changes; see [React workflow](react.md) | Complete interaction, network, paint, or GPU cost |
| Heap snapshot/allocation recording | Object retention, retaining paths, allocation patterns | Every process/GPU/native allocation |
| HAR/network timings | Request transaction and transfer evidence | Main-thread responsiveness |
| Lighthouse audit | The categories/metrics actually produced | Functional correctness or real-user distribution |

The native CLI's current `profiler` uses CDP Tracing and exports Chrome performance trace JSON, including sampled CPU data when its categories enable it. It does not export a standalone V8 `.cpuprofile`. Confirm this against installed help and the actual artifact; other `trace` commands can record different evidence. Optional MCP tools/flags vary. Check the Lighthouse categories actually included before promising a performance score.

## Record and analyze

Start the appropriate trace/profile before the target navigation or interaction. Record a short focused scenario, stop reliably, and save the artifact. Observe app readiness and the completed interaction. Continuous sockets or background work make network-idle a poor universal boundary.

Start with the native CLI's focused profiler for Chrome traces. Use official Chrome DevTools for deeper trace insights or heap capture/retainer analysis that the installed CLI lacks. Discover its tools in the live schema. If recording performs a reload, first select the intended URL as documented; do not reload-record a blank or unrelated page. For manual recording, start before the action/navigation being measured.

For a CDP fallback, use the supported `Tracing` and/or `Profiler` operations; select relevant categories rather than every category. If the protocol returns a stream, drain it through `IO` until EOF and close it. A start response alone is not a completed trace. CPU profiling and tracing change execution costs; label instrumentation.

Follow the dominant measured cost:

- Loading: document/server wait, resource discovery/priority, render-blocking chains, decoding, and the actual LCP candidate.
- Responsiveness: input delay, handler/main-thread work, and presentation delay. Follow long tasks and initiating/source-mapped stacks.
- Rendering: repeated style/layout, forced reflow, paint/composite work, frame misses, resource uploads or readbacks when visible. A CPU trace alone cannot prove GPU time.

Validate a suspected cause by changing one relevant condition and repeating the same action. Compare equivalent cache/build/profile conditions. For a performance claim, use several comparable runs and summarize a typical result and variability; do not choose the fastest run. A single trace can still locate a bug without establishing a benchmark improvement.

Lab observations of LCP, CLS, or interaction latency do not establish field Core Web Vitals. A page load without representative interactions does not measure an INP distribution. Use current [Web Vitals guidance](https://web.dev/articles/vitals) if the task requires thresholds or real-user assessment. Hand implementation decisions back to the app's existing performance workflow when available.

## Memory growth

Use an isolated test session. Warm up, take a baseline, repeat the same mount/unmount or open/close action, then compare snapshots at equivalent settled points. If you force GC through supported tooling, apply it consistently and label it; do not require users to launch with weakened security or speculative V8 flags.

Look for surviving detached DOM trees, growing listener/subscription counts, retained closures, and retaining paths. Distinguish retained size from shallow size and a stable cache from unbounded growth. Heap totals alone do not prove a leak. Inspect enough repeated cycles to distinguish warmup from continued accumulation.

Avoid holding candidate objects in console variables/handles while measuring their collectability. Heap dumps may capture secrets and impose pauses/large allocations, so keep captures bounded to a suitable environment. Stop allocation recording and release loaded snapshots/handles when done.

Primary references: [Performance panel](https://developer.chrome.com/docs/devtools/performance/), [performance reference](https://developer.chrome.com/docs/devtools/performance/reference/), [memory problems](https://developer.chrome.com/docs/devtools/memory-problems/), [heap snapshots](https://developer.chrome.com/docs/devtools/memory-problems/heap-snapshots/), [CDP Tracing](https://chromedevtools.github.io/devtools-protocol/tot/Tracing/) and [Profiler](https://chromedevtools.github.io/devtools-protocol/tot/Profiler/) (match the target schema).
