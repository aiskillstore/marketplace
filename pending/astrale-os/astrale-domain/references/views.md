# Views

Schema names the View; the Domain definition's frontend composition owns its URL, document, and handshake.
The React host owns the session, not the business Domain's runtime.

## Domain Views and internal routing

- Every View belongs to its own Domain. The Shell opens it by declaration path
  (`/:<origin>:view.<name>`) or as the Domain entrypoint, never for a Class or a node. Declare
  `view({ description? })`; a View declaration names no Class.
- A screen about one node (an issue, an invoice) is an internal route of the Domain frontend, such as
  `/issues/$issue`. Read the node from the router (`useParams`, `useSearch`) and pass it to the named
  Query. The Shell hands the View no node to render and cannot tell which View renders a node.
- Link to another screen of the same Domain with the router. Open another Domain's View with
  `openView({ view: '/:<origin>:view.<name>' })` (or its Domain entrypoint) and let that View route
  internally; never pass it a node to render.
- The handshake's `targetNodeId` is deprecated and always the Domain path; do not branch on it.

## Declare the surface

```ts
// schema/schema.ts: the Schema names the Domain and its entrypoint View.
export const schema = defineSchema('work.example', {
  name: 'Work',
  entrypoint: 'application',
  views: { application: view({}) },
})

// domain.ts
import { defineFrontend, vite } from '@astrale-os/sdk/view'
import { schema } from '#schema'

export const frontend = defineFrontend({
  schema,
  source: vite(),
  routes: { application: { path: '/application', handshake: 'shell' } },
})
```

- Every Schema declares the Domain `name` the Shell shows, and at most one `entrypoint` among its
  Views: the View the Shell opens for the application. Both are projected into the graph (the Domain
  Node `name`, an `entrypoint` Edge), where the Shell lists them; a Domain without an entrypoint is
  not listed. `defineFrontend` no longer takes an `entrypoint`.

- Use `handshake: 'shell'` for host-provided session/client access; `none` is for standalone public documents.
  A View declaration has no callable auth mode: its graph reads and calls retain their own authorization.
- Keep `frontend/` for browser entry/router/styles, `views/` for SDK hooks and screen orchestration,
  and `ui/` for presentation. Leaf UI receives values/callbacks, not credentials or a Kernel client.
- The SDK's Cloudflare adapter already manages caching for the frontends it serves; standalone
  Workers do not inherit it. Verify the serving path before adding local cache headers. Long-lived
  asset caching requires public files identified by the build as content-addressed, not a filename
  regex. Keep HTML, API/auth, and cookie-bearing responses outside this asset policy, and preserve
  existing `private`/`no-store` directives.

## React Shell and authentication

- Use the public `@astrale-os/shell-react` package for React session/hooks; the SDK's `view` facade owns
  frontend build declarations, not React providers. Declare the packages actually imported by the frontend.
- `<Astrale>` defaults to the sandboxed child handshake and supplies loading/error boundaries.
  Wrap projected Query/Mutation hooks in `<DomainProvider schema={schema}>`; keep the application's router.
- `useSelf()` is the caller's identity, synchronous and free. `useUser()` reads the User node and may
  suspend: use it only to show profile properties.
- `useDomain(schema)` binds synchronously and asks the Kernel nothing. Pass its resolved callable
  to `useAction`; do not reconstruct method keys, forge bound nodes, or resolve another client per component.
- A local frontend compiled against another Schema revision than the installation fails at its first
  request the Kernel refuses. Compare both revisions and update the coherent deployment; reloading or
  casting the binding cannot fix it.

```tsx
// frontend/src/main.tsx — router and schema are the application's existing owners.
import { Astrale, DomainProvider } from '@astrale-os/shell-react'
import { RouterProvider } from '@tanstack/react-router'
import { createRoot } from 'react-dom/client'
import { schema } from '#schema'
import { router } from './router'

createRoot(document.getElementById('root')!).render(
  <Astrale>
    <DomainProvider schema={schema}>
      <RouterProvider router={router} />
    </DomainProvider>
  </Astrale>,
)

// views/issue/use-close-issue.ts — Issue.close is the schema-declared instance callable.
import { useAction, useDomain } from '@astrale-os/shell-react'
import type { NodeId } from '@astrale-os/sdk/graph/node'

export function useCloseIssue() {
  const binding = useDomain(schema)
  const action = useAction(binding.domain.classes.Issue.methods.close, { refresh: 'all' })
  return {
    close: (id: NodeId) => action.run({ id }, {}),
    pending: action.pending,
    error: action.error,
  }
}
```

- The host authenticates the selected identity and supplies the child session through the handshake.
  Do not put root keys, long-lived tokens, a second login, or an anonymous fallback in the View.
- Opening the raw Service URL is not an authenticated mounted-View test. Use the CLI/Studio host;
  registration and business membership on that instance are separate from local identity storage.
- A frontend Policy probe or disabled button is presentation, never authorization. Kernel callable
  admission remains authoritative, including after a role changes or the UI becomes stale.

## Read, mutate, and refresh

Choose the boundary from product semantics; callable access and direct graph access remain separate:

| Intended contract | Use |
| --- | --- |
| Expose graph records, filtered per candidate by Class `read`/`traverse` Policies | Direct Query with the supplied session; Policy evaluates its caller |
| Give an actor that owns the Class or holds its exact capability direct graph access | Direct Query with that actor as principal |
| Expose a calculated, aggregated, redacted, or graph-independent stable result | Function with explicit callable admission; implement it as an Action or Workflow as appropriate |

The host owns session selection, exchange, and refresh; View code keeps using the supplied client.
See `policies.md` for the principal ceiling and the caller, and `debugging.md` for exchange mechanics.

- Instance `useAction.run` accepts `{ id: NodeId }`; a returned ID does not require a second Class read
  or a fabricated `BoundNode`. Validate only genuinely untrusted raw values entering that boundary.
- After a successful call, refresh affected observations. Start with supported invalidation options,
  then narrow costly refreshes; optimistic UI does not prove persistence and must recover on refusal.
- Distinguish loading, empty, missing routed record, auth failure, expected error, and pending mutation.
  Preserve editable input on failure; show safe actionable refusal details, not transport internals.
- Keep IDs, digests, SHAs, and technical Paths out of product labels and fallback text; show business
  names or a meaningful unavailable state. Reserve technical coordinates for explicitly developer-facing diagnostics.

## Use Astrale UI

Apply `astrale-frontend-design` for layout and interaction. Prefer `@astrale-os/ui` controls and supplied
patterns; write custom UI only for product-specific presentation or a missing capability.

```sh
# Run in the frontend project; inspect existing setup before initializing.
astrale ui search "searchable table with row actions" --json
astrale ui init --preset astrale
astrale ui add pattern/chart/line-basic
astrale ui doctor
```

- Search results include exact demo code and a `packageImport` or add command. Read those references and
  installed exports before inventing a wrapper, component API, or CSS convention.
- Library primitives stay package imports; added patterns/themes are consumer-owned source. Preserve
  the UI lock and local edits; do not reinitialize a configured frontend or overwrite it blindly.

## Inspect and exercise the real View

```sh
astrale instance list --bookmarked --json
astrale identity list --json
astrale get @self -i staging --as alice --json
astrale introspect /:issues.example:class.Issue:close -i staging --as alice
astrale view /:issues.example:view.application -i staging --as alice
astrale view issues.example --list -i staging --as alice
astrale logs -i staging --as alice --topic-prefix op:function. --limit 20
astrale view --sessions
astrale view --close <session-id>
```

- Use explicit instance and identity; repeat with a second registered principal for access contrasts.
  Root success is not Policy proof. Verify CLI flags with `--help` for the installed release.
- Check actual records, navigation, keyboard use, narrow layout, console errors, and a refusal.
  Distinguish local mock checks from installed-View evidence; never retain credentials in proof files.
