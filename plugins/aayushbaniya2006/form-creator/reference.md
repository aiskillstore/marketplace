# Form Architecture Reference

## Reference Implementation
**Canonical Example:** `src/components/forms/plan-form.tsx`
Refer to this file for:
- TypeScript interfaces
- Loading states (`isSubmitting`)
- UI layout and Shadcn usage

## Architecture

### 1. Schema
- Handle nullable/optional fields explicitly.
- Reuse DB schemas where possible but prefer specific form schemas.

### 2. Form Component
- **Dependencies**: `react-hook-form`, `@hookform/resolvers/zod`, `lucide-react`, `sonner`.
- **State**: Track `isSubmitting`.
- **Structure**: `<Form {...form}>` wrapper -> `<form>` -> `<FormField>`.

### 3. API Routes
- **GET (List)**: Return `{ data, pagination }`.
- **Error Handling**: Wrap in `try/catch`. Return JSON `{ error: "Message" }` with status code.

## Best Practices
1. **Type Safety**: No `any`. Use Zod inferred types.
2. **DRY Forms**: Use the same component for Create and Edit (differentiate via `initialData`).
3. **UX**: Show loading states. Use toast notifications.

