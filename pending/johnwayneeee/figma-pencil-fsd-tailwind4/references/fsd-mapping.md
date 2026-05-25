# FSD Mapping

Feature-Sliced Design layers, applied to any component-based frontend project. Names follow the canonical FSD vocabulary. If the host repository uses different names (for example a custom layout slice in place of `app-shell`, or a page-view module in place of `pages`), see `project-contracts.md` and map accordingly.

## Canonical layers

Top to bottom, higher layers may import from lower layers, never the reverse.

- `app`        — application entry, providers, root routing, global styles.
- `pages`      — page composition for each route. The exact file shape depends on the host framework's routing convention.
- `widgets`    — large, reusable, composed UI sections (sidebars, headers, dashboard panels).
- `features`   — user actions and interactive flows (publish item, edit profile, filter list).
- `entities`   — domain objects and small domain-specific UI (UserCard, ItemMeta).
- `shared`     — primitives, tokens, utilities, API clients, formatters, hooks, types.

Optional layers some projects use:

- `app-shell` (or a `widgets/layout`): persistent layout frame around multiple pages. May be public or authenticated. Not limited to admin shells.
- A page-view module that the route entry re-exports. Treat as a sub-layer of `pages`.

## Core rule

Map UI to the highest reusable layer that still keeps dependency direction clean. A button used everywhere is `shared/ui`. A button that knows about a domain concept is `entities/<name>/ui`. A button that triggers a domain action is `features/<action>/ui`.

## Practical decisions

- Repeated across screens, no domain knowledge → `shared/ui`.
- Represents a business object → `entities/<name>`.
- An action, form, mutation, or interactive flow → `features/<action>`.
- A large composed section reused on multiple pages → `widgets/<name>`.
- The composition of one screen → `pages/<route>`.
- Persistent layout (sidebar + topbar + outlet) shared by many pages → `app-shell` or `widgets/layout`.

## Server vs Client Components (frameworks with RSC)

Applies only when the host framework distinguishes Server and Client components (for example any React framework with React Server Components). Skip this section otherwise.

Default to Server Components. Add the client marker only when the component needs browser-only APIs, event handlers, state, refs, or effects.

- `shared/ui` primitives: server by default. Mark as client only on intrinsically interactive primitives (Input, Switch, Popover, anything with `onClick`/state).
- `entities/*/ui`: server by default. They render domain data.
- `features/*`: usually client. Forms, mutations, optimistic UI, and most user actions cross the client boundary.
- `widgets/*`: split — static sections stay on the server; interactive sections become client islands, ideally with their interactivity isolated in a child `features/*` component.
- `pages`: server. They fetch data and compose. Push interactivity down into client children rather than marking the whole page client.
- `app-shell`: server where possible. Interactive shell controls (theme toggle, menu) live in client child components.

Data fetching belongs in server boundaries (`pages`, server actions invoked from `features`). Avoid effect-based fetching in `features` when a server fetch is possible.

## Import direction

- `shared` imports nothing from above.
- `entities` may import from `shared` only.
- `features` may import from `shared` and `entities`.
- `widgets` may import from `shared`, `entities`, and `features`.
- `pages` may import from any layer below.
- `app` and `app-shell` may import from any layer below.
- Cross-imports inside the same layer (one `features/*` importing another) are forbidden unless the host project explicitly allows it.

## Reuse of existing primitives

Before creating a new primitive in `shared/ui`, check whether the project already ships a primitive library (shadcn/ui, Radix, Mantine, Headless UI, an in-house design system). If a primitive exists, reuse it or wrap it. Do not re-implement `Button`, `Input`, `Dialog`, `Tabs`, `Tooltip` if the project already has them.

## Anti-patterns

- Business logic in route entry files. Pages compose; they do not implement.
- The same card or table duplicated across multiple pages instead of a `widgets/*` or `entities/*` extraction.
- Mixing layout shell and page content in one component.
- Page-specific copies of `shared/ui` primitives ("just a slightly different Button").
- Pushing domain knowledge into `shared`.
- Marking a whole page as client when only a small subtree needs interactivity.
