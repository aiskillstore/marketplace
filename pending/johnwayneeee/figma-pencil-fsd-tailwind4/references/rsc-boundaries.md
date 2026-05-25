# Server / Client Boundaries

Applies only to frameworks that distinguish Server and Client components (React Server Components and similar). Skip this reference entirely if the project does not use such a split.

## Default

Every component is a Server Component until a real reason forces it to the client. The client marker is opt-in, not a default.

Reasons that justify marking a component as client:

- Component state (`useState`, `useReducer`) or refs (`useRef`).
- Effects (`useEffect`, `useLayoutEffect`).
- Event handlers attached to DOM (`onClick`, `onChange`, `onSubmit`).
- Browser-only APIs (`window`, `document`, `localStorage`, `IntersectionObserver`).
- Third-party libraries that internally require the client (most animation libs, charting libs, drag-and-drop, rich text editors).
- Context providers that hold client state.

Reasons that do NOT justify it:

- "It's a UI component."
- "The parent is interactive."
- "It might need state later."

## Per FSD layer

- `shared/ui` primitives: server by default. Mark as client only on intrinsically interactive primitives (Input, Switch, Popover, Tooltip, DropdownMenu). A presentational `Card`, `Badge`, or `Separator` stays on the server.
- `entities/*/ui`: server by default. They render domain data and rarely need the client.
- `features/*`: usually client. Forms, mutations, optimistic UI, filters, anything user-driven.
- `widgets/*`: split. Static composed sections stay server; interactive sections become client islands, ideally with the interactive subtree isolated in a child `features/*` component.
- `pages`: server. They fetch data and compose. Push the client marker to leaf components, not to the page root.
- `app-shell`: server where possible. Interactive shell controls (theme toggle, sidebar collapse, command menu) live in client child components.

## Data fetching

- Fetch on the server: in `pages`, or via server actions invoked from `features`.
- Avoid effect-based fetching when a server fetch is possible.
- Server actions belong next to the `features/*` that triggers them, marked with the framework's server-action directive.

## Composition patterns

- A server parent may render client children freely.
- A client parent may render server children only if they are passed in as `children` or props; a client component cannot `import` and render a server component directly.
- Use the "client island" pattern: keep the page and most widgets on the server, drop a small client component at the exact point where interactivity starts.

## Anti-patterns

- Marking a whole page as client because one button is interactive.
- Re-implementing server-fetchable data with effects in a client `features/*`.
- Passing server-only objects (database handles, large server-only types) into client components as props.
- Adding the client marker to `shared/ui` primitives "just in case".
- Wrapping the entire `app-shell` as a client component to support a theme toggle.
