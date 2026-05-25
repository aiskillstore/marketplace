# Example: Frame to FSD

A worked example that shows how a single design frame is decomposed across FSD layers. The example is generic and does not depend on any specific repository, framework, or component library.

## Source

A dashboard screen titled "Items". The frame contains:

- A sidebar with a workspace switcher, navigation, and the current user's avatar.
- A top bar with the page title "Items" and a primary "New item" button.
- A list of item cards. Each card shows: title, status badge, author avatar, scheduled date, and a "..." menu with `Edit`, `Duplicate`, `Delete`.
- An empty state and a loading skeleton, both present in the design.

## Decomposition

### `shared`

- `shared/ui/Button`, `shared/ui/Avatar`, `shared/ui/Badge`, `shared/ui/DropdownMenu`, `shared/ui/Skeleton` — taken from the project's primitive library, whichever it is. Do not re-implement.
- `shared/lib/format-date` — date formatter for the scheduled date.
- A global stylesheet declares the tokens used by the screen (`--color-surface`, `--color-border`, `--color-primary`, etc.).

### `entities`

- `entities/item/model` — `Item` type, status enum.
- `entities/item/ui/ItemStatusBadge` — Badge specialized for `Item['status']`. Server-rendered.
- `entities/item/ui/ItemMeta` — author avatar + scheduled date row. Server-rendered.
- `entities/user/ui/UserAvatar` — Avatar specialized for the user model. Server-rendered.

### `features`

- `features/item-create/ui/NewItemButton` — the primary "New item" CTA. Client, opens a creation flow.
- `features/item-actions/ui/ItemActionsMenu` — the "..." menu with Edit/Duplicate/Delete. Client.
- `features/workspace-switch/ui/WorkspaceSwitcher` — sidebar workspace picker. Client.

### `widgets`

- `widgets/item-list/ui/ItemList` — server-rendered. Receives `items: Item[]` and renders `ItemCard` for each.
- `widgets/item-list/ui/ItemCard` — server-rendered. Composes `entities/item/ui/*` and embeds `features/item-actions/ui/ItemActionsMenu` as a client island.
- `widgets/item-list/ui/ItemListEmpty` — empty state, server-rendered.
- `widgets/item-list/ui/ItemListSkeleton` — loading skeleton built from `shared/ui/Skeleton`.

### `app-shell`

- `app-shell/ui/AppShell` — the persistent sidebar + topbar frame. Server-rendered; renders client children for interactive controls (workspace switcher, user menu).

### `pages`

- `pages/items/ItemsPage` — server-rendered. Fetches items, handles loading/empty/error states, composes `widgets/item-list/*`.

### `app`

- Route entry for `/items` — imports and renders `ItemsPage`. No business logic.

The Server/Client annotations above apply only when the host framework distinguishes the two. For frameworks without that split, ignore them.

## Token mapping

Design variables in the frame:

- `color/surface/card` → `--color-surface`
- `color/text/primary` → `--color-foreground`
- `color/text/muted` → `--color-muted-foreground`
- `color/border/default` → `--color-border`
- `color/brand/primary` → `--color-primary`
- `radius/card` → `--radius-lg`

If the frame uses a one-off color not present in the design system, leave an arbitrary value with a `TODO(design)` comment instead of inventing a token.

## Server / Client split (when applicable)

- `ItemsPage`, `ItemList`, `ItemCard`, `ItemStatusBadge`, `ItemMeta`, `ItemListEmpty`, `ItemListSkeleton`, `AppShell` — server.
- `NewItemButton`, `ItemActionsMenu`, `WorkspaceSwitcher`, theme toggle, user menu — client.

The page stays server-rendered; interactivity is isolated to the smallest possible subtree.

## States covered

- default (items present)
- loading (skeleton)
- empty (no items yet)
- error (boundary at the page level)
- card hover, focus-visible, disabled (for the menu trigger)
- menu open/closed, keyboard navigation inside the menu

## What this example demonstrates

- Primitives come from the existing component library, never re-implemented.
- Domain UI lives in `entities` and contains no actions.
- Actions live in `features` and are the only client components on the screen.
- The page is composed by `widgets`, not by hand in the route entry.
- Tokens are mapped once and reused everywhere.
- When the host framework has an RSC split, server stays the default; client is the exception.
