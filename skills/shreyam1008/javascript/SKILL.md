---
name: javascript
description: "Implements or debugs JavaScript/TypeScript language behavior, async work, data transformations, and runtime memory. Use for JS/TS logic issues; React rendering and UI design have separate workflows."
---

# JavaScript

Modern JS is expressive and fast — most footguns come from async handling, mutation, and equality/coercion surprises. Prefer clarity and immutability; let the engine optimize.

## Language baseline

- `const` by default, `let` when reassigning, never `var`.
- Use `===`/`!==`; avoid `==` (coercion surprises). Know that `NaN !== NaN` (use `Number.isNaN`).
- Prefer pure functions and immutable updates (`{...obj}`, `[...arr]`, `.map`/`.filter`/`.reduce`) over in-place mutation of shared data.
- Optional chaining `?.` and nullish coalescing `??` (distinct from `||`, which also catches `0`/`""`).
- Use modules (`import`/`export`); no global leakage. Keep imports at the top.
- Prefer `for...of` / array methods over index loops; `Map`/`Set` over object-as-dict for dynamic keys.

## Async done right

- Prefer `async`/`await`; always handle rejection (`try/catch` or `.catch`).
- Run independent work concurrently with `Promise.all`; use `Promise.allSettled` when partial failure is acceptable.
- Never leave a floating promise where errors matter — await it or explicitly handle it.
- Don't mix `await` inside a `forEach` (it won't wait). Use `for...of` with `await`, or map to promises + `Promise.all`.
- Cancel stale fetches and signal-aware event listeners with `AbortController`. Cancel timers with `clearTimeout` / `clearInterval` (or an explicit signal-aware wrapper).

```js
// parallel, not serial
const [user, posts] = await Promise.all([getUser(id), getPosts(id)]);

// cancellable fetch
const ac = new AbortController();
const res = await fetch(url, { signal: ac.signal });
```

## Data & correctness

- Validate/parse external data at the boundary (a schema lib like Zod, or explicit checks) — don't trust shapes.
- Keep untrusted text out of code/HTML sinks: prefer `textContent`; sanitize rich HTML with a reviewed sanitizer before `innerHTML` or `insertAdjacentHTML`. A `TrustedHTML` value is safe only if its policy actually validates/sanitizes input; the type alone does not sanitize. Avoid `eval` and string-form timers. Enforce Trusted Types with CSP where feasible.
- Beware floating-point money math; use integer minor units or a decimal lib.
- Prefer copying array methods (`toSorted`, `toReversed`, `toSpliced`, `with`); copy-then-mutate only for compatibility. Use `structuredClone` only for cloneable values and handle `DataCloneError` at untrusted boundaries.
- Use `Intl` for dates/numbers/currency formatting, not hand-rolled string math.

## Performance & memory

- Don't allocate in hot loops; hoist constants and reused objects out.
- Debounce/throttle high-frequency events (scroll, resize, input); use `requestAnimationFrame` for visual updates.
- Offload heavy CPU work to a Web Worker to keep the main thread responsive (see `web-performance` and `wasm-rust`).
- Remove event listeners/observers/timers on teardown to avoid leaks; detached DOM nodes held by closures leak.
- Use `WeakMap` for object-keyed metadata that must not retain its keys. Reserve `WeakRef` for recomputable, best-effort values—collection timing is deliberately nondeterministic.

## TypeScript (when present)

- Keep `strict` on; avoid `any` — use `unknown` and narrow. Type the boundary, infer internally.
- Model invalid states out of existence with unions; use exhaustive `switch` with a `never` default.
- Explicit return types on exported functions; avoid unsafe assertions (`as`).

## Tooling hygiene

- Lint + format (ESLint + Prettier/Biome) and run in CI.
- Prefer the platform/standard library before adding a dependency; check bundle cost.

## Reference

- MDN JavaScript reference; "JavaScript guide".
- `GoogleChrome/modern-web-guidance-src` (JS/DOM guides).
- MDN: `AbortController`, copying array methods, `WeakMap`/`WeakRef`, `innerHTML`, and Trusted Types CSP.
- TC39 proposals; "You Don't Know JS" (Kyle Simpson); web.dev performance guides.
