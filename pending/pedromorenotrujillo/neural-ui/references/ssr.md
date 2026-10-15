# SSR and hydration

Use Angular CLI's SSR setup and preserve its browser/server entrypoints. Configure provideClientHydration with withEventReplay in the shared application providers. Neural does not enable Angular hydration itself. No production backend or hosting service is required to install this skill; SSR verification uses a temporary local test server.

Use the same initial data, IDs, selected tab, theme mode, locale, timeZone and clock decisions on server and client. Configure optional locale/timeZone/now through the root provideNeuralUI contract when relevant. Do not independently call the current time on both sides for visible initial content; transfer or otherwise reuse an application-owned timestamp.

Keep browser APIs out of module scope, constructors and server render paths. Use Angular afterNextRender for browser-dependent work. Angular's DOCUMENT can target the SSR document; do not assume it is the global browser document. A civil date must not be accidentally converted into a timezone-dependent instant.

Render overlays from consistent application state and defer DOM measurements to the appropriate browser phase. Do not solve hydration failures with arbitrary delays or disabling hydration for the entire application.

The repository compiles the same example components into browser and server bundles, serves request-time SSR, checks HTML with JavaScript disabled, and then exercises hydrated interactions while rejecting browser errors. This covers the included examples. It does not establish SSR support for every optional component or every application environment.

Angular 22's SSR host restrictions must explicitly permit the application's intended hostnames. The fixture permits only localhost and 127.0.0.1 for local testing; do not copy that allowlist unchanged into a deployed application.

Source: [official SSR and hydration](https://ui.neuralui.org/v2/en/foundations/ssr-hydration).
