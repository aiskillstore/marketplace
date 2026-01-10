# 6-Folder Architecture

DevPrep AI uses a simplified domain-driven architecture with 6 top-level folders.

## Folder Structure

```
frontend/src/
├── app/          # Next.js App Router (routes only)
├── modules/      # Feature-based business logic ← MODULES GO HERE
├── shared/       # Cross-cutting concerns
├── lib/          # External integrations
├── store/        # Global state (Zustand)
└── styles/       # Design system
```

---

## Where Do Modules Fit?

**Modules** (`modules/`) contain feature-based business logic. Each module is a self-contained domain.

### Module Guidelines

| ✅ DO | ❌ DON'T |
|-------|----------|
| Create modules for business domains | Put routing logic in modules |
| Keep modules independent | Create cross-module dependencies |
| Use feature-specific components | Duplicate shared UI components |
| Import from `@shared/ui/*` | Copy components between modules |
| Export via barrel exports (index.ts) | Export individual files directly |

---

## Module Internal Structure

Each module follows this structure:

```
modules/<module-name>/
├── components/      # Feature-specific components
│   ├── ComponentA.tsx
│   ├── ComponentB.tsx
│   └── index.ts    # Barrel exports
├── hooks/          # Feature-specific hooks (optional)
│   ├── useModuleData.ts
│   └── index.ts
├── utils/          # Feature utilities (optional)
│   ├── helpers.ts
│   └── index.ts
└── types.ts        # Module-specific types (optional)
```

---

## What Goes Where?

### `app/` - Routes Only
- **Purpose**: Next.js routing
- **Contains**: page.tsx, layout.tsx, loading.tsx
- **Rule**: NO business logic here, just routing

Example:
```tsx
// app/analytics/page.tsx
import { AnalyticsDashboard } from "@modules/analytics/components";

export default function AnalyticsPage() {
  return <AnalyticsDashboard />;
}
```

### `modules/` - Business Logic
- **Purpose**: Feature domains
- **Contains**: Components, hooks, utilities, types
- **Rule**: Self-contained, minimal cross-module imports

Examples:
- `modules/practice/` - Practice wizard, session logic
- `modules/assessment/` - Timed assessments
- `modules/results/` - Results display
- `modules/questions/` - Question generation

### `shared/` - Cross-Cutting Concerns
- **Purpose**: Reusable across all modules
- **Contains**: UI components, layouts, hooks, utilities
- **Rule**: NO domain logic, only generic reusable code

Subdirectories:
- `shared/ui/` - shadcn components (Button, Card, etc.)
- `shared/components/` - Layouts (AppLayout, AuthLayout)
- `shared/hooks/` - Generic hooks (useLocalStorage, useDebounce)
- `shared/utils/` - Helpers (cn, formatters)

### `lib/` - External Integrations
- **Purpose**: Third-party service integrations
- **Contains**: tRPC client, Claude AI service, React Query
- **Rule**: Integration logic only

Examples:
- `lib/trpc/` - tRPC routers, procedures, schemas
- `lib/claude/` - Claude AI service integration

### `store/` - Global State
- **Purpose**: Zustand state management
- **Contains**: Slices for global state
- **Rule**: Only truly global state (user, practice session, results)

Examples:
- `store/slices/practice/` - Practice session state
- `store/slices/user.ts` - User profile state

### `styles/` - Design System
- **Purpose**: Global styles and design tokens
- **Contains**: CSS files, design system
- **Rule**: No component-specific styles

Examples:
- `styles/globals.css` - Base styles, design tokens
- `styles/glassmorphism.css` - Glass effects, glows

---

## Module Independence

### ✅ Good: Module imports from shared/lib
```tsx
// modules/analytics/components/Chart.tsx
import { Card } from "@shared/ui/card";        // ✅ Shared UI
import { formatDate } from "@shared/utils/time"; // ✅ Shared utils
import { trpc } from "@lib/trpc/client";       // ✅ External integration
```

### ❌ Bad: Cross-module imports
```tsx
// modules/analytics/components/Chart.tsx
import { QuestionCard } from "@modules/questions/components"; // ❌ Cross-module
import { useAssessment } from "@modules/assessment/hooks";    // ❌ Cross-module
```

**Fix**: If you need shared functionality, move it to `shared/`.

---

## Benefits of This Structure

1. **Clear Boundaries**: Each folder has a single responsibility
2. **No Redundancy**: Zero duplication (6 folders vs. traditional 17)
3. **Domain-Driven**: Modules represent business domains
4. **Scalable**: Easy to add new modules without restructuring
5. **Maintainable**: Easy to find code (domain-based organization)

---

## Migration Path

When creating a new feature:

1. **Is it a new domain?** → Create new module in `modules/`
2. **Is it reusable UI?** → Add to `shared/ui/` or `shared/components/`
3. **Is it an API integration?** → Add to `lib/`
4. **Is it global state?** → Add slice to `store/`
5. **Is it a route?** → Add page to `app/`

---

## Common Mistakes

### ❌ Putting logic in app/
```tsx
// app/analytics/page.tsx
export default function AnalyticsPage() {
  const [data, setData] = useState([]);  // ❌ Logic in route
  useEffect(() => { /* ... */ }, []);     // ❌ Side effects in route
  return <div>{/* ... */}</div>;
}
```

### ✅ Correct: Logic in modules/
```tsx
// app/analytics/page.tsx
import { AnalyticsDashboard } from "@modules/analytics/components";

export default function AnalyticsPage() {
  return <AnalyticsDashboard />;  // ✅ Just routing
}

// modules/analytics/components/AnalyticsDashboard.tsx
export function AnalyticsDashboard() {
  const [data, setData] = useState([]);  // ✅ Logic in module
  useEffect(() => { /* ... */ }, []);     // ✅ Side effects in module
  return <div>{/* ... */}</div>;
}
```

---

## Questions?

**Q: Should every module have hooks/ and utils/?**
A: No, create them only when needed. `components/` is required, others optional.

**Q: Can modules import from each other?**
A: Avoid it. If needed, move shared code to `shared/`.

**Q: Where do global types go?**
A: Global types in `@/types/ai`, module-specific types in `modules/<name>/types.ts`.

**Q: How do I know if something is "shared" vs "module-specific"?**
A: If 2+ modules need it, it's shared. If only 1 module needs it, it's module-specific.
