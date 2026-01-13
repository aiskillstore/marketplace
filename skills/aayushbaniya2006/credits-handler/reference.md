# Credits Architecture Reference

## 1. Configuration
- **File**: `src/lib/credits/config.ts`
- **Type Schema**: `export const creditTypeSchema = z.enum([...]);`

## 2. Database
- **Transactions**: `src/db/schema/credits.ts`.
- **User Balance**: Cached in `users.credits` (JSONB).
- **Data Types**:
  - `transactionType`: "credit" | "debit" | "expired"
  - `metadata`: JSONB (reason, source, planId)

## 3. Key Operations
- **Allocation**: `src/lib/credits/allocatePlanCredits.ts`.
- **Recalculation**: `src/lib/credits/recalculate.ts`.

## Best Practices
1. **Stable Core**: Rely on exported functions (`addCredits`, `useCredits`). Avoid changing `recalculate.ts`.
2. **Idempotency**: Always provide a `paymentId` for additions.
3. **Atomic**: Never manually update `users.credits`. Use the helpers.

