# Angular implementation

How the universal principles map to Angular. Read after detecting an Angular project.

## Reusability and components
- Extract repeated templates into components; extract repeated logic into services or reusable pipes/directives.
- One component per file; follow Angular's naming (`feature.component.ts`). Keep components focused.
- Use standalone components (modern Angular) or well-scoped modules — consistently, not mixed ad hoc.

## Separation of concerns
- Components handle presentation; services handle data access and business logic (injected via DI).
- Never put HTTP calls directly in components — wrap them in a service.

## Design tokens
- Centralize colors, typography, and spacing as CSS/SCSS variables; reference them, never hardcode per component.
- If using Angular Material, configure its theme rather than overriding styles ad hoc.

## State management
- Local state in the component; shared state via services with observables/signals, or a store (NgRx) when complexity warrants it.
- Use signals or `computed`/derived observables instead of duplicating state.

## Navigation
- Use the Angular Router with centralized route definitions; navigate via `routerLink` / `Router.navigate`, consistently.
- Use route guards for UX gating (remembering: guards are not a security boundary — the backend enforces auth).

## Polish
- Set title via `Title` service per route; configure favicon and meta in `index.html` / `Meta` service.
- Include the viewport meta tag.

## Security specifics
- Angular escapes interpolated values by default — do not bypass it with `bypassSecurityTrustHtml` on untrusted content; sanitize first.
- `environment.ts` files are bundled into the client — never put real secrets there; they ship to the browser.
- Keep secret-bearing logic on the backend; the Angular app calls it through services over HTTPS.
- Prefer httpOnly cookies for auth tokens over `localStorage`.

## Dependency note
- Angular has defined LTS support windows per major version — target a current supported major, not a just-released one mid-stabilization, and keep within the support window for security patches.

## Correctness gotchas
- Clean up subscriptions: unsubscribe from observables (via `takeUntilDestroyed`, the `async` pipe, or manual teardown in `ngOnDestroy`). Unmanaged subscriptions are a common memory-leak source.
- Render defensively: guard against `null`/`undefined`/empty data (use the `async` pipe with `*ngIf` and fallbacks); handle loading and error states explicitly.
- Use `trackBy` with `*ngFor` for stable identity on reordering lists.
