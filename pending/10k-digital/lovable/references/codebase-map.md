# Codebase Map Generation Reference

This reference defines how to scan and generate a Project Structure Map for Lovable projects.

## Purpose

The codebase map helps Claude navigate user projects faster by providing:
- Directory structure with purposes
- Key files and their roles
- Component organization patterns
- Data flow overview

Target: ~60 lines, optimized for token efficiency while remaining useful.

---

## Scanning Algorithm

### Step 1: Scan Directory Structure

Scan these directories in order:

```
1. src/                    # Main source code
   ├── components/         # UI components
   ├── pages/              # Route pages
   ├── hooks/              # Custom React hooks
   ├── lib/                # Utilities and helpers
   ├── utils/              # Alternative utilities location
   ├── services/           # API services
   ├── contexts/           # React contexts
   ├── stores/             # State management (zustand, etc.)
   ├── types/              # TypeScript definitions
   ├── integrations/       # External service integrations
   │   └── supabase/       # Supabase client and types
   └── assets/             # Static assets

2. supabase/               # Backend
   ├── functions/          # Edge Functions
   └── migrations/         # Database migrations

3. public/                 # Static files

4. Root config files       # vite.config, tailwind.config, etc.
```

### Step 2: Detect Component Organization Pattern

Check `src/components/` structure:

**Flat Pattern** (all components at same level):
```
components/
├── Button.tsx
├── Card.tsx
├── Modal.tsx
└── ...
```

**Feature-Based Pattern** (grouped by feature):
```
components/
├── auth/
│   ├── LoginForm.tsx
│   └── SignupForm.tsx
├── dashboard/
│   ├── StatsCard.tsx
│   └── ActivityFeed.tsx
└── ui/                    # shadcn/ui primitives
```

**Atomic Pattern** (atoms/molecules/organisms):
```
components/
├── atoms/
├── molecules/
└── organisms/
```

### Step 3: Identify Key Files

Scan for these important files:

| Pattern | Purpose |
|---------|---------|
| `src/App.tsx` | Main app entry, routing |
| `src/main.tsx` | React DOM entry point |
| `src/index.tsx` | Alternative entry point |
| `src/lib/utils.ts` | Shared utilities (cn helper) |
| `src/lib/supabase.ts` | Supabase client |
| `src/integrations/supabase/client.ts` | Supabase client (Lovable default) |
| `src/hooks/use*.ts` | Custom hooks |
| `src/contexts/*Context.tsx` | React contexts |
| `src/types/*.ts` | Type definitions |
| `vite.config.ts` | Vite configuration |
| `tailwind.config.js` | Tailwind configuration |
| `tsconfig.json` | TypeScript configuration |

### Step 4: Detect Routing Structure

Check for routing patterns:

**React Router** (check `src/App.tsx` or `src/routes/`):
- Look for `<Routes>`, `<Route>`, `<BrowserRouter>`
- Extract route paths and their components

**File-based routing** (if using TanStack Router):
- Check `src/routes/` directory
- Extract page structure from file names

### Step 5: Detect State Management

Check for state management patterns:

| Pattern | Detection |
|---------|-----------|
| React Context | `createContext`, `useContext` in `src/contexts/` |
| Zustand | `create` from 'zustand' in `src/stores/` |
| Redux | `configureStore`, `createSlice` |
| TanStack Query | `useQuery`, `useMutation` usage |

### Step 6: Detect Data Flow

Build simplified data flow based on imports:

```
Pages → Components → Hooks → Services/Integrations → Supabase/API
```

Check for:
- Supabase client usage in hooks
- API service files
- Edge function invocations

---

## Map Template

Generate this structure (~60 lines):

```markdown
## Project Structure Map

> Quick navigation guide - run `/lovable:map --update` to refresh

### Directory Layout
```
src/
├── components/    # [COMPONENT_PATTERN] UI components
│   └── ui/        # shadcn/ui primitives (Button, Card, Dialog, etc.)
├── pages/         # Route pages ([PAGE_COUNT] pages)
├── hooks/         # Custom React hooks ([HOOK_COUNT] hooks)
├── lib/           # Utilities and helpers
├── integrations/  # External integrations
│   └── supabase/  # Supabase client and generated types
└── [OTHER_DIRS]   # [PURPOSE]

supabase/
├── functions/     # Edge Functions ([FUNCTION_COUNT] functions)
└── migrations/    # Database migrations ([MIGRATION_COUNT] migrations)
```

### Key Files
| File | Purpose |
|------|---------|
| `src/App.tsx` | [DETECTED_PURPOSE] |
| `src/lib/utils.ts` | Shared utilities (cn, formatters) |
| `src/integrations/supabase/client.ts` | Supabase client configuration |
| [OTHER_KEY_FILES] | [PURPOSE] |

### Patterns
- **Components**: [COMPONENT_PATTERN_DESCRIPTION]
- **State**: [STATE_MANAGEMENT_PATTERN]
- **Data Flow**: Pages → Hooks → Supabase Client → Edge Functions

### Quick Lookup
| Looking for... | Check here |
|----------------|------------|
| UI components | `src/components/ui/` |
| Page routes | `src/pages/` or `src/App.tsx` |
| API calls | `src/hooks/` or `src/integrations/` |
| Types | `src/types/` or `src/integrations/supabase/types.ts` |
| Edge functions | `supabase/functions/[name]/index.ts` |

*Last updated: [TIMESTAMP]*
```

---

## Edge Cases

### Missing Directories

If a standard directory doesn't exist, omit it from the map. Don't show empty directories.

### Non-Standard Structures

If structure doesn't match Lovable/React patterns:
1. List top-level directories with best-guess purposes
2. Identify entry point (package.json main/module field)
3. Note: "Non-standard structure - map may be incomplete"

### Large Projects

If > 50 components or > 20 pages:
- Group by subdirectory instead of listing all
- Show counts: "components/ (45 components in 8 categories)"

### Monorepo Detection

If `packages/` or `apps/` directory exists:
- Note monorepo structure
- Focus map on the primary app (usually `apps/web/` or `packages/app/`)

---

## Integration Points

### With /lovable:init

Add Question 8.5:
```
Would you like me to generate a Project Structure Map?
This helps me navigate your codebase faster by documenting:
- Directory structure and purposes
- Key files and their roles
- Component organization patterns

Generate map? (yes/no)
Default: yes (recommended)
```

### With /lovable:sync

Add `--refresh-map` flag:
- If map section exists in CLAUDE.md, optionally refresh it
- Detect if structure changed significantly since last generation
- Skip if no major changes to avoid unnecessary updates

### With /lovable:map command

Standalone command options:
```
/lovable:map              # Generate and display map
/lovable:map --update     # Update CLAUDE.md with new map
/lovable:map --verbose    # Show detailed scanning output
```

---

## Token Efficiency Guidelines

1. **Use tree format** - More compact than prose descriptions
2. **Counts over lists** - "12 components" not listing all 12
3. **Tables for key info** - Scannable, compact
4. **Skip obvious files** - Don't document package.json, .gitignore
5. **Merge similar items** - "hooks/" not "hooks/useAuth.ts, hooks/useData.ts..."
6. **Purpose over description** - "Auth handling" not "This file handles authentication..."

Target: Map should be quickly scannable in 10 seconds to find what you need.
