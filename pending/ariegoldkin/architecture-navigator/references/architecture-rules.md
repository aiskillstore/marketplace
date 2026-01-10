# DevPrep AI Architecture Rules

This document defines where different types of code should be placed in the 7-folder structure.

## 7-Folder Structure Overview

```
frontend/src/
├── app/          - Next.js App Router (routes only, minimal logic)
├── modules/      - Feature-based domain logic (business logic, feature-specific UI)
├── shared/       - Cross-cutting concerns (reusable UI, hooks, utils)
├── lib/          - External integrations (tRPC, Claude AI, React Query setup)
├── store/        - Global state management (Zustand slices)
├── styles/       - Design system (globals, theme tokens, glassmorphism)
└── types/        - Global TypeScript definitions (AI types, store types, component types)
```

## Placement Rules

### 1. modules/ - Domain/Feature Logic

**Put here:**
- Feature-specific business logic
- Feature-specific components (used only within that feature)
- Feature-specific hooks
- Feature-specific types (if not shared)
- Feature-specific state (if not global)

**Structure:**
```
modules/
├── assessment/    - Assessment mode logic
├── practice/      - Practice mode logic
├── questions/     - Question management
├── results/       - Results & analytics
├── profile/       - User profile
└── home/          - Home/landing page
```

**Examples:**
- Authentication logic → `modules/auth/`
- Payment processing → `modules/payments/`
- Practice wizard → `modules/practice/components/PracticeWizard.tsx`
- Assessment timer → `modules/assessment/hooks/useAssessmentTimer.ts`

**Key rule:** If it's feature-specific and NOT reused across features, it goes in modules/.

---

### 2. shared/ - Reusable Cross-Cutting Concerns

**Put here:**
- UI components used across multiple features
- Utility functions used across features
- Custom hooks used across features
- Theme utilities
- Validators, formatters, helpers

**Structure:**
```
shared/
├── components/    - Reusable UI components
│   ├── ui/       - Base UI elements (Button, Input, Card)
│   └── ...       - Composite components (Modal, Toast, Layout)
├── hooks/        - Reusable custom hooks
├── utils/        - Utility functions
└── themes/       - Theme utilities
```

**Examples:**
- Button component used everywhere → `shared/components/ui/Button.tsx`
- useDebounce hook → `shared/hooks/useDebounce.ts`
- formatDate utility → `shared/utils/date.ts`
- Toast notification → `shared/components/Toast.tsx`

**Key rule:** If it's reused across 2+ features, it goes in shared/.

---

### 3. lib/ - External Integrations

**Put here:**
- tRPC setup and configuration
- API clients (Claude AI, external services)
- React Query setup
- Third-party library configurations
- SDK wrappers

**Structure:**
```
lib/
├── trpc/         - tRPC setup
│   ├── routers/  - API route handlers
│   ├── client.ts - Client configuration
│   └── server.ts - Server configuration
├── claude/       - Claude AI integration
└── react-query/  - React Query setup
```

**Examples:**
- Claude AI integration → `lib/claude/client.ts`
- tRPC router → `lib/trpc/routers/ai.ts`
- React Query config → `lib/react-query/provider.tsx`
- Analytics SDK → `lib/analytics/tracker.ts`

**Key rule:** If it wraps an external library or service, it goes in lib/.

---

### 4. store/ - Global State Management

**Put here:**
- Zustand store slices
- Global state types
- State actions and selectors

**Structure:**
```
store/
├── practiceStore.ts       - Practice mode state
├── questionStore.ts       - Question state
├── profileStore.ts        - User profile state
└── uiStore.ts            - UI state (modals, toasts)
```

**Examples:**
- Practice session state → `store/practiceStore.ts`
- Current user data → `store/profileStore.ts`
- Modal visibility state → `store/uiStore.ts`
- Dark mode toggle → `store/uiStore.ts`

**Key rule:** If it's global state shared across features, it goes in store/.

---

### 5. types/ - Global TypeScript Definitions

**Put here:**
- Shared TypeScript types and interfaces
- API request/response types
- Store types
- Global enums and constants

**Structure:**
```
types/
├── ai/           - AI-related types (questions, evaluation)
│   ├── api.ts    - API types (Zod-inferred)
│   └── models.ts - Domain models
├── store/        - Store-related types
└── components/   - Component prop types
```

**Examples:**
- Question type → `types/ai/models.ts`
- API schemas → `types/ai/api.ts`
- Store slice types → `types/store/practice.ts`
- Global enums → `types/common.ts`

**Key rule:** If it's a type used in 2+ folders, it goes in types/.

---

### 6. styles/ - Design System

**Put here:**
- Global CSS
- Design tokens (colors, spacing, typography)
- Theme definitions
- Glassmorphism utilities
- Tailwind configuration

**Structure:**
```
styles/
├── globals.css         - Global styles
├── glassmorphism.css  - Glassmorphism utilities
└── tokens.css         - Design tokens
```

**Examples:**
- CSS variables → `styles/tokens.css`
- Global resets → `styles/globals.css`
- Glassmorphism classes → `styles/glassmorphism.css`

**Key rule:** If it's pure styling/theme, it goes in styles/.

---

### 7. app/ - Next.js Routes

**Put here:**
- Page route files (page.tsx)
- Layout files (layout.tsx)
- Loading states (loading.tsx)
- Error boundaries (error.tsx)
- Route metadata

**Structure:**
```
app/
├── page.tsx              - Home page route
├── layout.tsx            - Root layout
├── practice/
│   └── page.tsx         - Practice page route
└── results/
    └── page.tsx         - Results page route
```

**Key rules:**
- Keep route files MINIMAL - just import and render from modules/
- NO business logic in app/ - delegate to modules/
- Example: `app/practice/page.tsx` should import `modules/practice/PracticePage.tsx`

---

## Import Rules

### Allowed Import Directions

```
app/          →  modules/, shared/, lib/, store/
modules/      →  shared/, lib/, store/, types/
shared/       →  lib/, types/
lib/          →  types/
store/        →  types/
types/        →  (no dependencies)
```

### Forbidden Imports

❌ `modules/` should NOT import from other `modules/`
❌ `shared/` should NOT import from `modules/`
❌ `app/` should NOT contain business logic (move to `modules/`)
❌ Circular dependencies between any folders

---

## Decision Tree: "Where Should This Go?"

### 1. Is it a route/page?
→ **YES**: `app/` (but keep it minimal, import from modules/)

### 2. Is it feature-specific?
→ **YES**: `modules/{feature}/`
→ **NO**: Continue...

### 3. Is it reusable UI/logic?
→ **YES**: `shared/`
→ **NO**: Continue...

### 4. Is it external integration?
→ **YES**: `lib/`
→ **NO**: Continue...

### 5. Is it global state?
→ **YES**: `store/`
→ **NO**: Continue...

### 6. Is it a shared type?
→ **YES**: `types/`
→ **NO**: Continue...

### 7. Is it pure styling?
→ **YES**: `styles/`

---

## Examples of Common Placement Questions

| Question | Answer |
|----------|--------|
| Where should social login go? | `modules/auth/` (feature-specific) |
| Where should a Button component go? | `shared/components/ui/` (reusable) |
| Where should payment Stripe integration go? | `lib/stripe/` (external integration) |
| Where should shopping cart state go? | `store/cartStore.ts` (global state) |
| Where should API types go? | `types/ai/api.ts` (shared types) |
| Where should theme colors go? | `styles/tokens.css` (design system) |
| Where should notification logic go? | If feature-specific: `modules/{feature}/`, if global: `shared/` |
| Where should a date formatter go? | `shared/utils/date.ts` (reusable utility) |

---

## Key Principles

1. **Domain-Driven**: Group by feature (modules/) before technical concern
2. **Single Source of Truth**: No duplication across folders
3. **Clear Dependencies**: Follow import direction rules strictly
4. **Minimal Routes**: app/ should be thin, delegate to modules/
5. **Shared When Needed**: Don't prematurely share - move to shared/ when 2nd use appears
6. **Types Are Global**: Put shared types in types/ to avoid circular dependencies
