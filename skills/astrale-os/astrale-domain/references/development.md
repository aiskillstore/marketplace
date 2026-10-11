# Development

Start from the generated project and the installed SDK's public exports, not remembered syntax.
The SDK owns building, deploying, and publishing the Domain; the Astrale CLI owns instances, installs,
identities, and live calls.

Use the adapter and SDK session abstractions; do not configure a parallel token or endpoint pipeline.
Issuer, served release, and redirect internals belong in `debugging.md` when the normal path fails.

## Scaffold and dependencies

```sh
npx create-astrale-domain@beta issues \
  --yes --adapter astrale --frontend react \
  --origin issues.example --dir issues --no-link
```

- Keep an existing scaffold rather than recreating its plumbing. For reproducible release checks,
  use an exact published scaffolder/SDK/adapter cohort and retain the lockfile.
- Domain code imports semantic `@astrale-os/sdk/*` facades, not Kernel packages or private SDK paths.
  Declare the chosen adapter only; its transitive implementation adapter is not another direct dependency.
- Declare libraries source actually imports: exact SDK-compatible `zod`, and frontend UI/React Shell
  packages when used. Zod runtime identity matters; a structurally compatible second copy can fail compilation.
- Keep the scaffolded `tsconfig.json` as the single TypeScript program for Worker code, Views, and
  tests: `lib` includes the DOM, `types` is `["node", "vitest/globals"]`, and `skipLibCheck` is
  `false`. Domain Workers run with `nodejs_compat`, Vitest supplies its globals, `vite.config.ts` and
  third-party declarations assume Node or the DOM, and `skipLibCheck: false` keeps those declarations
  verified. Do not narrow `types` to `[]` or split the project per runtime: neither catches a real
  Worker defect, and the SDK and Kernel already type-check their Worker-facing surface against the
  Worker environment.

## Composition and owners

```text
schema/             business modules: classes, policies, functions, errors, types, states, core, views
functions/          Actions and Workflows together
queries/            graph observations and their projections
mutations/          atomic graph changes
rules/              pure business decisions
integrations/       consumer-owned external contracts
providers/          environment-backed implementations
routes/             optional native HTTP-to-callable declarations
views/ and ui/      client orchestration and presentation
runtime.ts          integrations, initialize, functions
domain.ts           schema, runtime, frontend, optional routes, requirements
astrale.config.ts   defineProject: domain, environments, optional tests
```

- Create only applicable layers and business owners. Keep curated `#` facades and one meaningful
  callable/Query/Mutation per file; do not manufacture empty layers or a universal repository.
- Runtime imports aggregate Schema as a type and uses its admitted `domain`. Focused runtime-safe
  errors, values, and StateMachines may be value imports; aggregate DSL declarations stay build-side.

```ts
// runtime.ts — ordinary imports provide integrations, providers, functions, and Environment.
import { defineRuntime } from '@astrale-os/sdk/runtime'
import type { schema } from '#schema'

export default defineRuntime<typeof schema>()({
  integrations,
  initialize(environment: Environment) {
    return { providers: { weather: createWeatherProvider(environment) } }
  },
  functions,
})

// domain.ts
import { defineDomain, requirements } from '@astrale-os/sdk/domain'
import { K } from '@astrale-os/sdk/schema'
// Import schema as a value here, plus runtime and frontend from their composition owners.
export const domain = defineDomain({
  schema, runtime, frontend,
  requirements: requirements({ functions: [K.functions.query, K.functions.mutate] }),
})
```

- Initialize Providers once from admitted environment. No Provider I/O at module scope and no handlers,
  authorization, or deployment effects in composition roots.
- Requirements are inert Domain definition composition, not a top-level `requirements/` layer. Schema
  dependencies pin definitions; installation requirements grant exact protected callable capabilities.

## defineProject and environments

```ts
// astrale.config.ts
import { astrale } from '@astrale-os/adapter-astrale'
import { defineProject } from '@astrale-os/sdk/project'
import { domain } from './domain.js'

export default defineProject({
  domain,
  environments: {
    development: {
      deployment: astrale({ secrets: '.env.dev' }),
    },
    production: {
      deployment: astrale({ organization: '<Identity id>', secrets: '.env.prod' }),
    },
  },
})
```

- An Environment says how to deploy and with which secrets; it names no instance. Which instance runs
  which release is the operator's choice at `astrale domain install -i <instance>`: a deploy never
  installs. Deploy, install, versions, and secret rotation are in `release.md`.
- `organization` names the Identity on the Admin instance (a User, or a Shell Group whose members and
  CI deploy for it) that holds the Environment's deployment line. Every Environment but `development`
  names one; a `development` Environment without one deploys on a line of the deploying identity.
- When changing a shared Schema dependency, deploy every affected Domain, then install the coherent
  root set together in one grouped install; follow `migration.md`.
- The Domain definition already contains Runtime and frontend. `entrypoints.runtime` only overrides the
  conventional loadable Runtime file; do not repeat those definitions in Project or adapter options.
- Each deployment gets its own signing key, generated at deploy: there is no key file to keep or
  distribute, and the Domain's key is distinct from the human CLI identity. Keep secret files beside
  their owning config, or use explicit paths; never copy secrets into source.
- Run commands from the owning project directory. Relative secret paths resolve there, not at a
  parent monorepo root; environment names alone do not isolate deliberately shared provider resources.

## Development loop

```sh
astrale auth login
astrale instance list --json
pnpm run deploy development                                   # prints the deployment URL; installs nothing
astrale domain install <url> --allow-issuer-change -i <dev-instance>
```

- Prefer the Astrale adapter for managed deployment: it deploys on the Admin instance's Services
  through the CLI session (`astrale call --admin`), with no Cloudflare account needed. Select another
  adapter only when the user needs that provider directly.
- There is no watch loop: iterate with the same two commands, by hand or by an agent. Each changed
  build is a new preview at its own URL; installing it over the previous one is an issuer change on
  the same line, which `--allow-issuer-change` consents to (at a terminal, typing the origin does).
- The SDK CLI requires an explicit Environment for `deploy`. Iterate on a development instance you
  own (one owner per instance, see `release.md`), not on production by convenience.
- A failed build or deploy changes no instance, and a deployment nobody installs runs nowhere.
  Domain development needs no local Kernel or hand-managed tunnel; do not add one without a real need.

## Verification and handoff

```sh
pnpm install
pnpm typecheck
pnpm test
pnpm lint
pnpm build
astrale get /:issues.example -i development --as operator --schema --json
astrale introspect /:issues.example -i development --as operator
```

- Typecheck/lint/build prove source boundaries, not installed behavior. Observe the exact release the
  deployment serves (`/.well-known/astrale/release.json`), the installed Schema revision, and
  representative calls before claiming deployment/integration success.
- Build, deployment, and installation are separate stages. `astrale domain install <url> -i ...`
  installs an already-deployed release; a deployment URL never serves other code, so new code reaches
  an instance only by installing its new URL or version.
- Retain exact SDK/adapter/CLI versions and relevant source/deployment revisions, not only manifest
  ranges. Keep durable regression tests with code and ephemeral qualification output outside delivery.
- Run checks on the tree actually built and deployed. Do not hide files, weaken typechecking, or forge
  SDK types to satisfy the linter; minimize a genuine SDK gap and report the exact diagnostic.
- When publishing a package, check emitted declarations and an isolated packed consumer. Avoid leaked
  Kernel imports, private aliases, or workspace overrides; use `pnpm --ignore-workspace` outside the repo.
- Test operator scripts through their documented package command. A direct module run does not prove
  argument forwarding; handle a package-manager separator only when the chosen toolchain supplies one.
- Build does not load all runtime secrets, and help does not start the project. Neither proves
  initialization or credentials work; observe readiness and one actual invocation separately.
