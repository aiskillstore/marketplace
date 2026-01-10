# Path Aliases

DevPrep AI uses TypeScript path aliases for clean, maintainable imports.

---

## Available Aliases

Configured in `tsconfig.json`:

| Alias | Maps To | Use For |
|-------|---------|---------|
| `@/*` | `./src/*` | Root-level imports |
| `@app/*` | `./src/app/*` | App Router pages |
| `@modules/*` | `./src/modules/*` | Feature modules |
| `@shared/*` | `./src/shared/*` | Shared UI, components, hooks, utils |
| `@lib/*` | `./src/lib/*` | External integrations (tRPC, Claude AI) |
| `@store` | `./src/store` | Zustand state management |
| `@/types/*` | `./src/types/*` | Global TypeScript types |

---

## Usage Examples

### Importing from Types
```typescript
// ✅ Correct: Use @/types alias
import type { IQuestion, IUserProfile } from "@/types/ai";

// ❌ Incorrect: Relative path
import type { IQuestion } from "../../../../types/ai";
```

### Importing from Shared
```typescript
// ✅ Correct: Use @shared alias
import { Button } from "@shared/ui/button";
import { Card } from "@shared/ui/card";
import { useDebounce } from "@shared/hooks/useDebounce";
import { formatDate } from "@shared/utils/time";

// ❌ Incorrect: Relative paths
import { Button } from "../../../shared/ui/button";
```

### Importing from Modules
```typescript
// ✅ Correct: Use @modules alias
import { QuestionCard } from "@modules/questions/components";
import { useAnalytics } from "@modules/analytics/hooks";

// ❌ Incorrect: Relative path
import { QuestionCard } from "../../questions/components";
```

### Importing from Lib
```typescript
// ✅ Correct: Use @lib alias
import { trpc } from "@lib/trpc/client";
import { generateQuestions } from "@lib/claude/questions";

// ❌ Incorrect: Relative path
import { trpc } from "../../../lib/trpc/client";
```

### Importing from Store
```typescript
// ✅ Correct: Use @store alias
import { usePracticeStore } from "@store/slices/practice";
import { useUserStore } from "@store/slices/user";

// ❌ Incorrect: Relative path
import { usePracticeStore } from "../../../store/slices/practice";
```

---

## Within-Module Imports

### Rule: Use relative imports ONLY within the same module

```typescript
// File: modules/analytics/components/AnalyticsChart.tsx

// ✅ Correct: Relative import within same module
import { formatChartData } from "../utils/helpers";
import { useAnalyticsData } from "../hooks/useAnalyticsData";

// ❌ Incorrect: Absolute alias for same-module imports
import { formatChartData } from "@modules/analytics/utils/helpers";
```

### Why?
- Keeps module portable
- Clear separation between internal and external imports
- Easier refactoring

---

## Cross-Module Rules

### ❌ Avoid Cross-Module Imports

```typescript
// ❌ Bad: Importing from another module
import { QuestionCard } from "@modules/questions/components";
import { useAssessment } from "@modules/assessment/hooks";
```

### ✅ Use Shared Instead

If multiple modules need something, move it to `@shared`:

```typescript
// ✅ Good: Import shared functionality
import { Card } from "@shared/ui/card";
import { useDebounce } from "@shared/hooks/useDebounce";
```

---

## Import Order Convention

Organize imports in this order:

```typescript
// 1. React and external libraries
import React, { useState, useEffect } from "react";
import { useForm } from "react-hook-form";

// 2. Global types
import type { IQuestion, IUserProfile } from "@/types/ai";

// 3. Shared imports
import { Button } from "@shared/ui/button";
import { Card } from "@shared/ui/card";
import { formatDate } from "@shared/utils/time";

// 4. Lib imports
import { trpc } from "@lib/trpc/client";

// 5. Store imports
import { usePracticeStore } from "@store/slices/practice";

// 6. Module-internal imports (relative)
import { formatChartData } from "../utils/helpers";
import { useAnalyticsData } from "../hooks/useAnalyticsData";
```

---

## Type Imports

### Rule: Use `import type` for types/interfaces

```typescript
// ✅ Correct: import type for types
import type { IQuestion } from "@/types/ai";
import type { IUserProfile } from "@/types/ai";

// ✅ Correct: regular import for components
import { Button } from "@shared/ui/button";

// ❌ Incorrect: regular import for types
import { IQuestion } from "@/types/ai";
```

### Why?
- TypeScript optimization (type-only imports)
- Enforced by `tsconfig.json` strict mode
- Better tree-shaking in production

---

## Common Patterns

### Component in Module
```typescript
// File: modules/analytics/components/AnalyticsChart.tsx
import React from "react";
import type { IChartData } from "@/types/ai";
import { Card } from "@shared/ui/card";
import { formatChartData } from "../utils/helpers";

interface IAnalyticsChartProps {
  data: IChartData[];
}

export function AnalyticsChart({ data }: IAnalyticsChartProps) {
  const formattedData = formatChartData(data);
  return <Card>{/* ... */}</Card>;
}
```

### Hook in Module
```typescript
// File: modules/analytics/hooks/useAnalytics.ts
import { useState, useEffect } from "react";
import type { IAnalyticsData } from "@/types/ai";
import { trpc } from "@lib/trpc/client";
import { usePracticeStore } from "@store/slices/practice";

export function useAnalytics() {
  const [data, setData] = useState<IAnalyticsData[]>([]);
  const { sessionId } = usePracticeStore();

  // Hook logic...

  return { data };
}
```

### Page in App Router
```typescript
// File: app/analytics/page.tsx
import { AnalyticsDashboard } from "@modules/analytics/components";

export default function AnalyticsPage() {
  return <AnalyticsDashboard />;
}
```

---

## Troubleshooting

### Error: "Cannot find module '@modules/...'"

**Solution:** Check `tsconfig.json` has correct paths configuration:

```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*"],
      "@modules/*": ["./src/modules/*"],
      "@shared/*": ["./src/shared/*"],
      "@lib/*": ["./src/lib/*"],
      "@store": ["./src/store"]
    }
  }
}
```

### Error: "Relative path too deep (../../../...)"

**Solution:** Use path aliases instead:
- `../../../shared/ui/button` → `@shared/ui/button`
- `../../../../types/ai` → `@/types/ai`
- `../../lib/trpc/client` → `@lib/trpc/client`

### Validation

The `validate-module.sh` script warns if you have too many relative imports (> 5).

---

## Summary

| Scenario | Use | Example |
|----------|-----|---------|
| Global types | `@/types/*` | `import type { IQuestion } from "@/types/ai"` |
| Shared UI | `@shared/ui/*` | `import { Button } from "@shared/ui/button"` |
| Shared hooks | `@shared/hooks/*` | `import { useDebounce } from "@shared/hooks/useDebounce"` |
| Shared utils | `@shared/utils/*` | `import { formatDate } from "@shared/utils/time"` |
| tRPC | `@lib/trpc/*` | `import { trpc } from "@lib/trpc/client"` |
| Zustand store | `@store/*` | `import { usePracticeStore } from "@store/slices/practice"` |
| Other modules | **Avoid** | Move shared code to `@shared` |
| Same module | Relative | `import { helper } from "../utils/helpers"` |

**Golden Rule:** Use aliases for cross-folder imports, relative for within-module imports.
