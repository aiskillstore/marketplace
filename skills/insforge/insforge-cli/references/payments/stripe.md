# npx -y @insforge/cli payments stripe

Use this reference when configuring or inspecting Stripe payment infrastructure. For app checkout code, load `skills/insforge/payments/stripe.md`.

## Setup Flow

Always start with status:

```bash
npx -y @insforge/cli payments stripe status
```

If Stripe is unconfigured, add the environment key. `config set` validates the key and automatically syncs provider state when the key or account changes. Use `status` again after setup to verify key/account/sync/webhook health:

```bash
npx -y @insforge/cli payments stripe config set --environment test sk_test_xxx
npx -y @insforge/cli payments stripe status
```

Use `sync` later to manually refresh mirrored provider data or retry a failed sync:

```bash
npx -y @insforge/cli payments stripe sync --environment test
```

Use `--environment test` while building. Use `live` only after explicit production approval. Do not store Stripe secret keys with generic `secrets` commands.

## Webhooks

Stripe webhook registration is automated by InsForge when the backend has a public URL:

```bash
npx -y @insforge/cli payments stripe webhooks configure --environment test
```

InsForge configures these Stripe events:

- `customer.created`
- `customer.updated`
- `customer.deleted`
- `checkout.session.completed`
- `checkout.session.async_payment_succeeded`
- `checkout.session.async_payment_failed`
- `checkout.session.expired`
- `invoice.paid`
- `invoice.payment_failed`
- `payment_intent.succeeded`
- `payment_intent.payment_failed`
- `charge.refunded`
- `refund.created`
- `refund.updated`
- `refund.failed`
- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`
- `customer.subscription.paused`
- `customer.subscription.resumed`

Durable fulfillment belongs on `payments.webhook_events`, not Checkout success URLs and not `payments.transactions`.

## Catalog

Stripe catalog concepts:

- Product: sellable thing or plan family.
- Price: amount/currency/recurrence attached to a Product.
- Subscription checkout uses recurring Prices.

Commands:

```bash
npx -y @insforge/cli payments stripe catalog --environment test
npx -y @insforge/cli payments stripe products list --environment test
npx -y @insforge/cli payments stripe products get prod_123 --environment test
npx -y @insforge/cli payments stripe products create --environment test --name "Pro Plan"
npx -y @insforge/cli payments stripe products update prod_123 --environment test --description "Updated"
npx -y @insforge/cli payments stripe products delete prod_123 --environment test -y
npx -y @insforge/cli payments stripe prices list --environment test
npx -y @insforge/cli payments stripe prices create --environment test --product prod_123 --currency usd --unit-amount 2000
npx -y @insforge/cli payments stripe prices create --environment test --product prod_123 --currency usd --unit-amount 2000 --interval month
npx -y @insforge/cli payments stripe prices update price_123 --environment test --active false
npx -y @insforge/cli payments stripe prices archive price_123 --environment test
```

Stripe Price amount/currency/interval are immutable. Create a new Price and archive the old one instead of trying to mutate billing terms.

## Admin Reads

Use these for inspection and debugging:

```bash
npx -y @insforge/cli payments stripe customers --environment test
npx -y @insforge/cli payments stripe subscriptions --environment test
npx -y @insforge/cli payments stripe subscriptions --environment test --subject-type team --subject-id team_123
npx -y @insforge/cli payments stripe transactions --environment test
npx -y @insforge/cli payments stripe transactions --environment test --limit 20 --json
```

`--subject-type` and `--subject-id` are app billing subjects passed to InsForge, such as `team:team_123` or `user:user_123`. They are not Stripe customer, payment, price, or subscription IDs.

## RLS For Runtime App Code

Before building subscription checkout or Billing Portal UI, add app-specific RLS to the Stripe runtime authorization tables:

- `payments.stripe_checkout_sessions`: `INSERT` for creating Checkout attempts, `SELECT` for retry/idempotency reads.
- `payments.stripe_customer_portal_sessions`: `INSERT` for creating portal attempts, `SELECT` when the app reads attempts.

Example shape:

```sql
ALTER TABLE payments.stripe_checkout_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE payments.stripe_customer_portal_sessions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "team admins create stripe checkout"
ON payments.stripe_checkout_sessions
FOR INSERT
TO authenticated
WITH CHECK (
  subject_type = 'team'
  AND public.is_team_billing_admin(subject_id)
);

CREATE POLICY "team admins read stripe checkout"
ON payments.stripe_checkout_sessions
FOR SELECT
TO authenticated
USING (
  subject_type = 'team'
  AND public.is_team_billing_admin(subject_id)
);

CREATE POLICY "team admins create stripe portal"
ON payments.stripe_customer_portal_sessions
FOR INSERT
TO authenticated
WITH CHECK (
  subject_type = 'team'
  AND public.is_team_billing_admin(subject_id)
);
```

If app checkout sends `idempotencyKey`, include a matching `SELECT` policy on `payments.stripe_checkout_sessions` because retries may reuse an existing row.

## Fulfillment Trigger

Create triggers on `payments.webhook_events` and update app-owned tables:

```sql
CREATE OR REPLACE FUNCTION public.fulfill_stripe_billing_event()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.provider = 'stripe'
     AND NEW.processing_status = 'processed'
     AND NEW.event_type IN ('checkout.session.completed', 'invoice.paid') THEN
    -- Update public.orders, public.team_entitlements, or an app-owned outbox.
    NULL;
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER fulfill_stripe_billing_event
  AFTER INSERT OR UPDATE ON payments.webhook_events
  FOR EACH ROW
  EXECUTE FUNCTION public.fulfill_stripe_billing_event();
```

Make fulfillment idempotent. For email, warehouse, CRM, or other external side effects, write an app-owned outbox row and process it asynchronously.

Stripe gives no ordering guarantee across events: `invoice.paid` can be processed before `checkout.session.completed` creates the `payments.customer_mappings` row. For subscription events, resolve the billing subject from the payload first (`payload -> 'data' -> 'object' -> 'parent' -> 'subscription_details' -> 'metadata' ->> 'insforge_subject_id'` on invoices) and use `payments.customer_mappings` only as a fallback. See the `insforge` app-integration skill's Stripe guide for a complete subscription fulfillment trigger.

### Subscription Cancellation Fields

When mirroring subscription state into app-owned tables, store `cancel_at` as well as boolean flags. Stripe can schedule future cancellation by setting `cancel_at` while `cancel_at_period_end` remains `false`; `canceled_at` can be the cancellation request time, not the access end time. Use `status <> 'canceled' AND cancel_at IS NOT NULL` for "will cancel".

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Running root payments commands without a provider | Use `payments stripe ...` |
| Using provider-prefixed price fields in SDK checkout code | Use `priceId` |
| Marking orders paid from success URL | Fulfill from `payments.webhook_events` |
| Adding only `INSERT` RLS for idempotent checkout | Add matching `SELECT` |
| Checking only `cancel_at_period_end` for scheduled cancellation | Also read and store `cancel_at` |
| Expecting Razorpay Items or Plans | Use Stripe Products and Prices |
