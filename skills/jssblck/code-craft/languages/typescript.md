# TypeScript / JavaScript dialect

How the universal core is spelled in TypeScript, plus TS/JS-specific idioms. The
overriding rule: let the type system do work, and keep `any` out.

## Tooling baseline

Default to the oxc toolchain: `oxfmt` for formatting and `oxlint` for linting,
not Prettier + ESLint and not Biome:

```sh
oxfmt --check .            # format check (oxfmt --write . applies)
oxlint --type-aware .      # lint, including type-aware rules
tsc --noEmit               # type-check (oxlint does not replace tsc; CI must run this)
```

One `.oxlintrc.json`, committed. `--type-aware` needs `oxlint-tsgolint` and a
`tsconfig.json`; it turns on `no-floating-promises`, `no-misused-promises`, and
`switch-exhaustiveness-check`. See
[`../principles/new-project-defaults.md`](../principles/new-project-defaults.md).

### Ban the type-system escape hatches (default)

Turn `any` into an error, and while you are there ban the other ways code lies to
the checker. This is the default for new TS projects. Vendor
[anti-slop](https://github.com/dmmulroy/anti-slop) (`npx skills add
dmmulroy/anti-slop --skill install-anti-slop`, then ask the agent to install it)
and enable every rule:

```jsonc
// .oxlintrc.json
{
  "$schema": "./node_modules/oxlint/configuration_schema.json",
  "ignorePatterns": ["tools/oxlint/anti-slop/**", ".agents/**", ".claude/**", ".codex/**"],
  "jsPlugins": [{ "name": "anti-slop", "specifier": "./tools/oxlint/anti-slop/index.ts" }],
  "categories": { "correctness": "error" },
  "rules": {
    "typescript/no-explicit-any": "error",
    "typescript/no-non-null-assertion": "error",
    "typescript/no-floating-promises": "error",
    "typescript/no-misused-promises": "error",
    "typescript/switch-exhaustiveness-check": "error",
    "eqeqeq": "error",
    "no-empty": "error",
    "prefer-const": "error",
    "anti-slop/no-chained-type-assertions": "error",
    "anti-slop/no-conditional-empty-object-spread": "error",
    "anti-slop/no-known-value-widening": "error",
    "anti-slop/no-module-mocking": "error",
    "anti-slop/no-object-parameters": "error",
    "anti-slop/no-reflect-apply": "error",
    "anti-slop/no-reflect-get": "error",
    "anti-slop/no-runtime-typeof": "error",
    "anti-slop/no-shape-in-symbol-names": "error",
    "anti-slop/no-unknown-parameters": "error",
    "anti-slop/no-unknown-returns": "error",
    "anti-slop/no-unknown-type-aliases": "error",
    "anti-slop/no-unsafe-dictionary-type": "error",
    "anti-slop/no-widen-then-assert": "error",
    "anti-slop/require-safety-comment-for-type-assertion": "error"
  }
}
```

The plugin is TypeScript ESM, so `package.json` needs `"type": "module"` and
`@oxlint/plugins` must be installed at the same version as `oxlint`.

What each layer stops:

- `no-explicit-any` bans `any`; `no-non-null-assertion` bans `!` (handle the
  null); `no-floating-promises` bans dropped rejections.
- `require-safety-comment-for-type-assertion` allows `as` only behind a
  `// SAFETY:` line that names the checked invariant, and `no-chained-type-assertions`
  and `no-widen-then-assert` close the `as unknown as T` and widen-then-cast
  laundering routes. Parse, do not assert.
- `no-unknown-parameters`, `no-unknown-returns`, `no-object-parameters`, and
  `no-unsafe-dictionary-type` keep `unknown`, `object`, and `Record<string, unknown>`
  out of function contracts; parse at the boundary and pass named types inward.
- `no-runtime-typeof` rejects ad hoc `typeof` narrowing in favor of schema
  parsing (set `allowInTypeGuards: true` in a schema-free project).
- `no-known-value-widening` rejects `const h: Record<string, X> = {...}` when
  inference or `satisfies` would keep the known keys.
- `no-module-mocking` bans `vi.mock` / `jest.mock` (see Testing below).

`tsconfig.json` non-negotiables:

```jsonc
{
  "compilerOptions": {
    "strict": true,                     // the whole strict family
    "noUncheckedIndexedAccess": true,   // arr[i] is T | undefined; huge bug catcher
    "exactOptionalPropertyTypes": true,
    "noImplicitOverride": true,
    "noFallthroughCasesInSwitch": true
  }
}
```

`strict: true` is the floor, not the ceiling. `noUncheckedIndexedAccess` in
particular turns a whole class of "undefined is not a function" runtime crashes
into compile errors.

## Illegal states (core 1, 4)

- **Discriminated unions for state.** This is the single most valuable TS
  pattern. Replace boolean/optional soup with a tagged union and `switch` on the
  tag:
  ```ts
  type State<T> =
    | { kind: "loading" }
    | { kind: "error"; message: string }
    | { kind: "ready"; data: T };
  ```
  The `ready` branch is the only place `data` exists, so you cannot read it while
  loading. Use a `never`-returning `assertNever(x)` in the `default` case to get
  exhaustiveness checking: adding a variant becomes a compile error everywhere
  it is unhandled.
- **Branded (nominal) types** for newtypes, since TS is structural:
  ```ts
  type UserId = string & { readonly __brand: "UserId" };
  const UserId = (raw: string): UserId => {
    if (raw.length === 0) throw new Error("empty UserId");
    // SAFETY: the check above is the whole UserId invariant.
    return raw as UserId;
  };
  ```
  Now a bare `string` will not pass where `UserId` is required. Brand IDs, units,
  and validated values.
- `unknown`, never `any`. `any` disables the type checker locally and infectiously.
  Parse `unknown` at the boundary into a named type; do not let `unknown` into
  function signatures. If you must escape, `as` with a `// SAFETY:` comment and
  a runtime check, not `any`.
- `readonly` and `as const` for immutability; `satisfies` to check a literal
  against a type without widening it.
- Prefer unions of string literals over `enum` (enums have surprising runtime
  and nominal behavior); reach for `enum` only when you need its specific
  features.

## Parse, don't validate (core 2)

- **Schema-parse external data at the boundary** with zod, valibot, or arktype.
  The schema is the parser and the type source:
  ```ts
  const Config = z.object({ port: z.number().int().positive(), host: z.string() });
  type Config = z.infer<typeof Config>;
  const config = Config.parse(rawJson);   // throws on bad shape; config is typed
  ```
  Do not hand-write `isValidConfig(x): boolean` and keep passing the raw object.
  Parse once, pass `Config` inward.
- This matters more in TS than anywhere else: `JSON.parse` returns `any`, network
  responses are lies, `process.env` values are `string | undefined`. Every one of
  those is a boundary that must be parsed, not trusted.
- `z.infer` so the static type and the runtime check cannot drift.

## Errors (core 3)

- **Throw for exceptional, return for expected.** Two viable styles; be
  consistent within a module:
  - Idiomatic TS: `throw` a typed `Error` subclass, `catch` at a known seam.
    Always extend `Error` (never `throw "string"`), set `cause` to chain:
    `throw new ConfigError("loading profile", { cause: err })`.
  - Result style: return a `{ ok: true; value } | { ok: false; error }` union (or
    neverthrow's `Result`) when you want the error in the signature and
    exhaustive handling. Good for expected, branchy failure.
- **Never swallow:** no empty `catch {}`, no unhandled promise. A floating
  promise drops its rejection; `await` it or `.catch` it explicitly. The
  type-aware `no-floating-promises` and `no-misused-promises` rules gate this.
- **Fail closed** in gates: a guard that throws or times out denies.
- Async errors: `async`/`await` with `try/catch`, not raw `.then` chains. Use
  `Promise.all` for parallel, `Promise.allSettled` when you need every result
  regardless of individual failures.

## Naming and style

`camelCase` values/functions, `PascalCase` types/classes/components,
`UPPER_SNAKE` consts. Booleans `is`/`has`/`can`. No Hungarian, no `I` prefix on
interfaces. Files: match the project (kebab-case is common). Prefer named exports
over default exports (better refactor/autocomplete).

## Async (TS-specific)

- `async`/`await` throughout; never mix with bare callbacks.
- `Promise.all([...])` for independent parallel work, not sequential awaits in a
  loop when the iterations are independent. `Promise.allSettled` to collect all
  outcomes. `AbortController` / `AbortSignal` for cancellation and timeouts.
- Beware the sequential-await-in-a-loop performance trap; batch with
  `Promise.all` when order-independent.

## Functional and immutability

Prefer `map`/`filter`/`reduce` and immutable updates over in-place mutation where
it reads clearly. `const` by default. Do not mutate function arguments. Keep
side effects at the edges so the core is testable.

## Project structure

Organize by feature/domain, not by technical layer (`user/` not
`controllers/ models/ views/` split across the app). Barrel files (`index.ts`)
sparingly: they help the public surface but can create import cycles and slow
tooling. Keep the public API of a module explicit.

## Testing (core 6)

- Vitest or Jest; `tsc --noEmit` is part of the test gate (a green test suite
  with type errors is not green).
- Test behavior through the module's public surface. `vi.mock` / `jest.mock` are
  lint errors (`anti-slop/no-module-mocking`); avoid `vi.spyOn` on your own
  functions too. Both pin implementation. Use real implementations, a real
  in-memory store, MSW for HTTP boundaries, real temp dirs.
- `fast-check` for property-based tests. Deterministic: fake timers
  (`vi.useFakeTimers`) instead of real `setTimeout` waits; inject the clock and
  RNG.
- Descriptive `describe`/`it` names that read as behavior sentences.

## React: effect discipline

`useEffect` synchronizes a component with a system React does not own. It is not
a data-flow tool. Effect chains (an effect sets state, which triggers another
effect) turn a component from a readable tree into a timeline that a reader,
human or agent, must simulate step by step. Default to zero effects; see
[You Might Not Need an Effect](https://react.dev/learn/you-might-not-need-an-effect).

- **Never** use an effect for:
  - Derived state: compute it during render (`useMemo` if expensive).
  - Resetting state when a prop changes: pass a `key` instead.
  - Reacting to a user event: put the logic in the event handler.
  - Data fetching: use the project's data-fetching layer (TanStack Query, SWR,
    or the framework loader), which handles races, caching, and cancellation.
- **Allowed:** synchronizing with an external system: DOM APIs, subscriptions,
  timers, third-party widgets, analytics. Every such effect returns a cleanup
  function and lists honest dependencies. For external stores, prefer
  `useSyncExternalStore` over a hand-rolled subscribe effect.
- **Ban the import in product code (default).** External-system effects live in
  a small allow-listed directory of wrapper hooks (`useEventListener`,
  `useInterval`, the analytics hook); components compose those wrappers and
  stay effect-free. Ban `useLayoutEffect` with the same rule, or it becomes the
  dodge:
  ```jsonc
  // .oxlintrc.json additions
  "plugins": ["react"],
  "rules": {
    "react-hooks/rules-of-hooks": "error",
    "react-hooks/exhaustive-deps": "error",
    "no-restricted-imports": ["error", {
      "paths": [{
        "name": "react",
        "importNames": ["useEffect", "useLayoutEffect"],
        "message": "Derive during render, handle in the event handler, or use the data-fetching layer. External-system sync goes in src/hooks/effects/."
      }]
    }]
  },
  "overrides": [
    { "files": ["src/hooks/effects/**"], "rules": { "no-restricted-imports": "off" } }
  ]
  ```
  The allow-listed wrappers still obey the hooks rules: never suppress
  `exhaustive-deps` (a mount-only effect with silenced dependencies captures
  stale props and state), and do not add a `useMountEffect`-style wrapper that
  hides the dependency array. In review, reject `React.useEffect` member calls;
  with the modern JSX transform nothing needs the React namespace import.

## Anti-patterns to refuse

`any` (use `unknown` + narrowing); non-null `!` to silence the checker instead of
handling the null; `as` casts that lie about runtime shape; `enum` by reflex;
floating promises; empty `catch`; `JSON.parse` result used untyped; boolean-flag
soup instead of a discriminated union; default exports everywhere; mocking your
own modules; `==` (use `===`). The oxlint + anti-slop config above makes every
one of these a hard error rather than a review nit.
