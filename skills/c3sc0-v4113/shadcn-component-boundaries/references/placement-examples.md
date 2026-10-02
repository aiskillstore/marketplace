# Placement examples

Paths assume `components.json` resolves `components` to `src/components` and `ui` to `src/components/ui`; substitute the project's resolved aliases.

| Component | Ownership | Path |
| --- | --- | --- |
| `Button` added with `shadcn add button` | registry primitive | `src/components/ui/button.tsx` |
| `ConfirmButton` wrapping `Button` + `AlertDialog`, used app-wide | reusable product | `src/components/common/confirm-button.tsx` |
| `InvoiceTable` used only by the billing feature | feature | `src/components/billing/invoice-table.tsx` |
| Dashboard page composing cards and tables | route composition | framework route directory |
| Brand accent color | theme token | global stylesheet variable |

Edge cases:

- A registry primitive needs a new look used in several places → add a variant to the primitive; do not create a styled copy in `common/`.
- A feature component becomes reused by a second feature → move it to `common/` and remove feature-specific behavior first.
- Re-running `shadcn add` overwrites a primitive → keep product behavior outside `ui` so the overwrite loses nothing.
