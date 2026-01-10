# Plans Architecture Reference

## 1. Database Schema
- **File**: `src/db/schema/plans.ts`
- **Quotas**: JSONB column using `quotaSchema`.
- **Naming**: Use usage-based names (`images`) not time-bound (`monthly_images`).

## 2. Management UI
- **Form**: `src/components/forms/plan-form.tsx`.
- **Dashboard**: Super Admin dashboard is the source of truth.

## 3. Subscription Flow
- **Helper**: `src/lib/plans/getSubscribeUrl.ts`.
- **Usage**: `getSubscribeUrl({ codename, type, provider })`.

## Best Practices
1. **Dashboard First**: Do not manual seed plans. Ask user to use the UI.
2. **Schema Sync**: Keep DB, Validation, and Form schemas in sync.
3. **Provider IDs**: Ensure Stripe/Dodo/PayPal IDs are set in the plan (Ask user to set them in the plan dashboard).

