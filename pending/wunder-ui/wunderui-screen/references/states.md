# States every data region needs

A screen is not finished until each region that shows data can show these. Make them reachable in development (a `status` prop on the region, or `?state=` in the URL) so they can be reviewed.

## Loading
- Charts: pass `loading` — they draw their own skeleton at the right height.
- `DataGrid`, lists, cards: `Skeleton` blocks in the same box as the content (same height, same radius). The layout must not jump when data arrives.
- Never a full-page spinner for a region that loads on its own.

## Empty
- `EmptyState` with `title` (what is missing, in the user's words), `description` (why, one sentence) and `action` (the one thing to do next, a `Button`).
- A filtered list with no results is a different empty state: say that the filter matched nothing and offer "Clear filters".
- First-run empty (nothing created yet) can carry a short illustration or icon; a search miss should not.

## Error
- `Alert variant="negative"` (it shows a warning triangle) saying what failed ("Couldn't load invoices"), why if known, and a retry `Button`.
- Keep the rest of the screen working — an error in one region does not blank the page.
- For agent or tool failures use `RunError`.

## Also check
- Long text: names and titles truncate or wrap inside their cell, never overflow.
- Zero and very large numbers format correctly (0, 1,204,330, negative values).
- Dark mode: no hard-coded colour shows up wrong.

## Library defaults to know
- `DataGrid` is `selectable` by default — pass `selectable={false}` for read-only tables. Columns without `width` share the space; give fixed widths only to short columns (status, amount, actions).
- Allowed values and defaults: `design.json` → `components[].props` has the full signature with its union types (also `node_modules/@wunderui/react/design.json`).
