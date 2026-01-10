---
name: add-core-function
description: Add new core business logic functions to Catalyst-Relay. Use when creating pure functions, ADT operations, or library-consumable code.
---

# Adding Core Functions

## When to Use

- Creating new ADT operations (CRAUD, discovery, preview)
- Adding pure business logic functions
- Implementing library-consumable functionality

## One Function Per File

Each core function gets its own file. No multi-function files.

**Location:** `src/core/{domain}/{function}.ts`

```
core/adt/
├── index.ts              # Barrel exports
├── types.ts              # Shared types (AdtRequestor, ObjectConfig)
├── helpers.ts            # Internal helpers (not exported from barrel)
│
├── craud/
│   ├── read.ts           → readObject()
│   ├── create.ts         → createObject()
│   └── ...
│
└── discovery/
    ├── packages.ts       → getPackages()
    └── ...
```

## Import Hierarchy

Files must follow this hierarchy (no circular dependencies):

```
types.ts           (shared types, no imports from package)
    ↓
helpers.ts         (internal utilities, imports types)
    ↓
subfolder files    (import ../types and ../helpers)
    ↓
index.ts           (barrel exports, imports from subfolders)
```

**Relative path patterns:**
- `../types` — shared types
- `../helpers` — shared helpers
- `../../utils/xml` — core utilities
- `../../../types/result` — global types

## Function File Pattern

```typescript
// src/core/adt/discovery/packages.ts

import type { AdtRequestor } from '../types';
import type { AsyncResult } from '../../../types/result';

export interface Package {
    name: string;
    description: string;
}

export async function getPackages(
    requestor: AdtRequestor,
    filter?: string
): AsyncResult<Package[]> {
    // Implementation
    const response = await requestor.get('/packages', { params: { filter } });

    if (response.error) {
        return [null, response.error];
    }

    return [parsePackages(response.data), null];
}

// Internal helper (not exported)
function parsePackages(xml: string): Package[] {
    // ...
}
```

## Return Type Convention

Use Go-style error tuples:

```typescript
import type { AsyncResult } from '../../../types/result';

// Returns [data, null] on success, [null, error] on failure
export async function someOperation(): AsyncResult<Data> {
    // ...
}
```

## Barrel Exports

Add to `index.ts` for public API:

```typescript
// src/core/adt/index.ts

// Types
export type { AdtRequestor, ObjectConfig } from './types';

// Discovery
export { getPackages } from './discovery/packages';
export { getTree } from './discovery/tree';

// CRAUD
export { readObject } from './craud/read';
export { createObject } from './craud/create';
```

## Internal Helpers

Helpers not exported from barrel go in `helpers.ts`:

```typescript
// src/core/adt/helpers.ts

import type { AdtRequestor } from './types';

// Internal - not exported from index.ts
export function buildObjectUri(name: string, extension: string): string {
    // ...
}
```

## Checklist

```
- [ ] Create function file in src/core/{domain}/{subfolder}/
- [ ] Define types at top of file or in ../types.ts
- [ ] Use AsyncResult return type for async functions
- [ ] Follow import hierarchy (no circular deps)
- [ ] Export from index.ts if public API
- [ ] Put internal helpers in helpers.ts
- [ ] Run typecheck: bun run typecheck
```
