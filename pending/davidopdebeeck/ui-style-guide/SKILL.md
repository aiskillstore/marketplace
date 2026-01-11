---
name: ui-style-guide
description: Frontend coding standards, component patterns, and design system for the Guessimate Angular UI. Reference when writing or reviewing frontend code.
---

# Frontend Style Guide & Coding Conventions

This document defines the coding standards, architectural patterns, and design system for the Guessimate Angular frontend.

## 1. Technology Stack

- **Framework:** Angular 20+
- **Styling:** Tailwind CSS 4
- **State Management:** Angular Signals & RxJS
- **Build System:** Angular CLI (Esbuild)

## 2. Project Structure

We follow a **Feature-Based** directory structure. Code is organized by domain feature rather than technical type.

```
src/app/
├── core/            # Global singletons (Guards, Interceptors, Global Services)
├── layout/          # Layout components (Navigation, Footer, Shell)
├── features/        # Feature modules (Domain logic)
│   ├── home/
│   ├── session/
│   │   ├── components/  # Dumb/Presentational components
│   │   ├── pages/       # Smart/Container components (Routed)
│   │   ├── services/    # Feature-specific state/logic
│   │   └── models/      # Feature-specific types
│   └── ...
├── websocket/       # WebSocket infrastructure
└── shared/          # Shared utilities (Pipes, Directives, Generic UI)
```

### Naming Conventions

- **Files:** Kebab-case (e.g., `session-page.component.ts`, `auth.service.ts`).
- **Classes:** PascalCase (e.g., `SessionPageComponent`, `AuthService`).
- **Selectors:** `app-` prefix, kebab-case (e.g., `app-user-profile`).
- **Signals:** No suffix, descriptive noun/verb (e.g., `user()`, `isLoading()`).
- **Observables:** `$` suffix (e.g., `user$`).

## 3. Component Standards

### Definition

- Use **Standalone Components** (`standalone: true` is default in v19+).
- Prefer **Inline Templates** for most components to keep logic and view co-located.
- Avoid external CSS files; use **Tailwind CSS** utility classes directly in the template.

```typescript

@Component({
    selector: 'app-example',
    imports: [CommonModule, RouterLink], // Explicit imports
    template: `
    <div class="p-4 bg-surface-100 rounded-lg">
      <h1 class="text-2xl font-bold text-gray-900">{{ title() }}</h1>
    </div>
  `
})
export class ExampleComponent {
    title = signal('Hello World');
}
```

### Control Flow

Use the new built-in Angular Control Flow syntax.

```html
<!-- Good -->
@if (isLoading()) {
<app-spinner/>
} @else {
@for (item of items(); track item.id) {
<app-item [data]="item"/>
}
}
```

### Dependency Injection

Prefer the `inject()` function over constructor injection for better type inference and cleaner code.

```typescript
// Good
private readonly
route = inject(ActivatedRoute);
private readonly
store = inject(SessionStore);

// Avoid if possible
constructor(private
route: ActivatedRoute
)
{
}
```

## 4. State Management

- **Local State:** Use `signal()` for primitive state.
- **Shared State:** Use **Signal Stores** (Services using Signals) provided at the appropriate level (Root or Component).
- **Reactive Data:** Use `computed()` for derived state and `effect()` sparingly for side effects.

```typescript

@Injectable()
export class SessionStore {
    // State
    private readonly _state = signal<SessionState>(initialState);

    // Selectors
    readonly lobby = computed(() => this._state().lobby);
    readonly connection = computed(() => this._state().connection);

    // Actions
    setLobby(lobby: Lobby) {
        this._state.update(s => ({...s, lobby}));
    }
}
```

## 5. Styling & Design System

We use **Tailwind CSS 4** with a semantic color palette defined in `styles.css`.

### Usage Rules

1. **Utility-First:** Write classes directly in HTML.
2. **No Magic Numbers:** Use theme values (e.g., `p-4` not `p-[16px]`).
3. **Dark Mode:** Use the `dark:` modifier for all color-related classes.

### Color Palette

The application uses a semantic naming convention mapped to Tailwind colors.

#### Core Colors

| Category          | Semantic Name   | Light Mode    | Dark Mode        | Usage                                |
|:------------------|:----------------|:--------------|:-----------------|:-------------------------------------|
| **Background**    | `background`    | `gray-50`     | `gray-950`       | Main application background          |
| **Surface**       | `surface`       | `white`       | `gray-900`       | Cards, modals, sections              |
| **Surface Alt**   | `surface-alt`   | `gray-100`    | `gray-800`       | Secondary backgrounds, input fields  |
| **Primary**       | `brand`         | `blue-600`    | `blue-600`       | Primary actions, buttons, highlights |
| **Primary Muted** | `brand-muted`   | `blue-50`     | `blue-900/30`    | Selected states, light highlights    |
| **Success**       | `success`       | `emerald-500` | `emerald-600`    | Success states, confirmation         |
| **Success Muted** | `success-muted` | `emerald-50`  | `emerald-900/30` | Success backgrounds                  |
| **Danger**        | `danger`        | `red-600`     | `red-600`        | Errors, destructive actions          |
| **Danger Muted**  | `danger-muted`  | `red-50`      | `red-900/30`     | Error backgrounds                    |
| **Warning**       | `warning`       | `amber-500`   | `amber-600`      | Warnings, pending states             |
| **Warning Muted** | `warning-muted` | `amber-50`    | `amber-900/30`   | Warning backgrounds                  |

#### Typography & Borders

| Category      | Light Mode | Dark Mode  | Usage                              |
|:--------------|:-----------|:-----------|:-----------------------------------|
| **Primary**   | `gray-900` | `white`    | Main headings and body text        |
| **Secondary** | `gray-500` | `gray-400` | Subtitles, labels, secondary info  |
| **Muted**     | `gray-400` | `gray-500` | Disabled text, placeholders        |
| **Border**    | `gray-200` | `gray-800` | Standard dividers and card borders |

### Implementation in `styles.css`

Colors are defined using CSS variables in the `@theme` block:

```css
@theme {
    --color-brand-600: var(--color-blue-600);
    --color-surface-100: var(--color-stone-100);
    /* ... */
}
```

## 6. Common Component Patterns

### Cards & Containers

Standard styling for content containers (like estimation cards, lists):

```html

<div class="flex flex-col bg-surface-100/60 border border-surface-200 dark:bg-gray-900/40 dark:border-gray-800/60 rounded-md shadow-sm">
    <!-- Content -->
</div>
```

- **Background:** `bg-surface-100/60` (Light) / `dark:bg-gray-900/40` (Dark)
- **Border:** `border border-surface-200` (Light) / `dark:border-gray-800/60` (Dark)
- **Rounding:** `rounded-md` (Standard)
- **Dividers:** `divide-y divide-surface-300 dark:divide-gray-800`

### Typography Headers

```html

<div class="flex flex-col gap-1">
    <h2 class="text-2xl font-semibold leading-none text-gray-900 dark:text-white">Title</h2>
    <span class="text-sm font-normal text-gray-600 dark:text-gray-400">Subtitle description</span>
</div>
```
