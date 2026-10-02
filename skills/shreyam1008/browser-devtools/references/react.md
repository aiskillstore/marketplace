# React web: overview to detail

Use this for inspecting a running React app, locating its components, or diagnosing a slow interaction. Ordinary React implementation does not require a profiling session. Check the app's installed React/framework versions and development, production, or profiling build before choosing APIs.

## Discover the available React tools

Start with the native CLI's installed React help. In releases that support it, launch the owned session with `--enable react-devtools` **before React initializes**, then use `react tree`, `react inspect`, and `react renders` with their installed arguments. Reuse the same session for all calls. Attaching after React starts may lack the required hook; do not restart a user's existing browser to retrofit it. Use an appropriate fresh debug session or existing React DevTools instead.

The CLI's render recorder uses a tool-maintained React hook and reports aggregates; it is not full React DevTools Profiler parity or its export format. Check what it reports, how it groups components, and whether timing is instrumented. Instance counts and change summaries can be heuristic; they do not establish exact mounts or a complete update history. Same-name aggregates cannot isolate one component instance. A JSON envelope may contain a text report rather than raw timing records. Use Components/Profiler panels, supported Performance tracks, or public `<Profiler>` instrumentation for richer commit/effect or instance-level evidence.

For an existing official Chrome DevTools connection, discover page-registered third-party tools and their live schemas. React's experimental [Chrome DevTools integration](https://github.com/react/react/tree/main/packages/react-devtools-cdt-mcp) provides component inspection and per-commit profiling. It is a browser library registered in the target app, **not a separate MCP server**, and installing React DevTools alone does not register that page bridge. If needed, read the installed package's documentation and current [Chrome third-party-tool guidance](https://github.com/ChromeDevTools/chrome-devtools-mcp/blob/main/docs/third-party-developer-tools.md). Registration must run before React and stay out of server execution; scope it to an appropriate local/debug build. Prefer a fitting existing route over adding an app dependency.

Other supported routes are [React DevTools Components/Profiler panels](https://react.dev/learn/react-developer-tools), React [Performance tracks](https://react.dev/reference/dev-tools/react-performance-tracks) in a browser trace, and the public [`<Profiler>` API](https://react.dev/reference/react/Profiler) for scoped programmatic measurements. Use existing instrumentation first; adding it is a source change within the requested app/debugging scope. Follow the framework's current profiling-build support rather than prescribing a permanent bundler alias.

If React tree access is unavailable, say so. DOM/accessibility trees and CPU stacks can still help but are not the React component tree. Do not build a replacement inspector by scraping Fiber fields, global hook internals, or private DevTools bridge messages.

## Inspect progressively

1. **Overview:** Get a shallow component tree or search by component name/visible target. Report the relevant root/branch and current UI state; avoid dumping the entire application.
2. **Selected component:** Expand that branch, then inspect the specific props, state/context, or hooks needed for the symptom. Read props first; hook inspection can re-execute render code in some tools, so use it only when useful and outside timing captures. Redact sensitive values.
3. **Source and relationships:** Follow available source locations and parent/owner information. JSX ownership and mounted ancestry are different relationships. A DOM lookup may return a host component; trace its relationship to the application component before attributing the behavior. Keep DOM and React component identifiers distinct and refresh them after reload/remount.
4. **Profile overview:** Record the same focused interaction, wait for its expected UI and relevant effects to complete, then stop and summarize commits, render cost, and changed components. Stopping immediately after a commit can omit pending passive-effect timing in some tools. Drill into the expensive commit/subtree using available flamegraph, ranked, or commit-report views; retrieve detailed data only for that evidence.

Choose the entry point that fits: tree inspection needs no recording; a slow interaction may begin with profiling. Stop when the requested question is answered.

## Interpret the measurement

Read current tool/React documentation for timing fields. Missing, null, or placeholder durations mean unavailable timing, not zero cost; verify timing support before interpreting zero values. Separate subtree/inclusive time from self time and render time from commit/layout effects, passive effects, network, and paint. Do not sum parent and child inclusive durations or overlapping nested Profiler samples as independent work. A Profiler commit timestamp is not a commit duration, and its estimated base duration is not a measured before-change baseline.

Use React profile evidence to locate expensive or repeated work and a browser trace to check its effect on the actual interaction. Supported React Performance tracks can align component, scheduler, effect, and applicable server activity with the browser timeline; availability depends on React/build/tool support. Production profiling is usually disabled unless the appropriate profiling build is used. Development Strict Mode and instrumentation can add work, so compare equivalent builds/settings and label their limits. Do not disable Strict Mode simply to hide a defect.

Check actual prop/state/context changes, identity, remounts, or effect-driven updates before proposing memoization or blaming rerenders. Renders are not inherently bugs. Compiler configuration also matters. For a requested fix, use the project's React workflow (such as `react-best-practices` when available) for implementation, then repeat the same interaction and functional checks. Stop recordings and remove temporary instrumentation when the investigation is complete.
