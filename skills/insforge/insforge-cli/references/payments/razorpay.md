# npx -y @insforge/cli payments razorpay

Use this reference when configuring or inspecting Razorpay payment infrastructure. For app order/subscription code, load `skills/insforge/payments/razorpay.md`.

## Setup Flow

Always start with status:

```bash
npx -y @insforge/cli payments razorpay status
```

If Razorpay is unconfigured, add Key ID and Key Secret. `config set` validates the keys and automatically syncs provider state when the key or account changes. Use `status` again after setup to verify key/account/sync/webhook health:

```bash
npx -y @insforge/cli payments razorpay config set --environment test --key-id rzp_test_xxx --key-secret xxx
npx -y @insforge/cli payments razorpay status
```

Use `sync` later to manually refresh mirrored provider data or retry a failed sync:

```bash
npx -y @insforge/cli payments razorpay sync --environment test
```

Use `--environment test` while building. Use `live` only after explicit production approval. Do not store Razorpay keys with generic `secrets` commands.

## Webhooks

Razorpay does not support InsForge-style automatic webhook registration with only API keys. Configure webhooks manually in the Razorpay Dashboard.

From the InsForge dashboard (Dashboard -> Payments -> Settings -> Webhooks), copy:

- Webhook URL, for example `/api/webhooks/razorpay/test`
- Webhook secret

Razorpay can only deliver webhooks to a public HTTPS URL. Localhost will not receive Razorpay webhooks.

Create a webhook in the Razorpay Dashboard with that URL and secret, and select these events:

- `payment.authorized`
- `payment.captured`
- `payment.failed`
- `subscription.created`
- `subscription.activated`
- `subscription.charged`
- `subscription.updated`
- `subscription.cancelled`
- `subscription.paused`
- `subscription.resumed`
- `subscription.halted`
- `subscription.completed`
- `subscription.expired`
- `refund.created`
- `refund.processed`
- `refund.failed`
- `invoice.paid`
- `invoice.expired`
- `order.paid`

Durable fulfillment belongs on `payments.webhook_events`, not Razorpay Checkout callback verification and not `payments.transactions`.

## Catalog

Razorpay catalog concepts are not Stripe concepts:

- Item: the sellable thing plus amount/currency.
- Plan: recurring billing definition around an Item.
- Order: one-time payment attempt.
- Subscription: recurring agreement created from a Plan.

Commands:

```bash
npx -y @insforge/cli payments razorpay catalog --environment test
npx -y @insforge/cli payments razorpay items list --environment test
npx -y @insforge/cli payments razorpay items create --environment test --name "Pro Plan" --amount 200000 --currency inr
npx -y @insforge/cli payments razorpay items update item_123 --environment test --active false
npx -y @insforge/cli payments razorpay plans list --environment test
npx -y @insforge/cli payments razorpay plans create --environment test --period monthly --interval 1 --item-name "Pro Plan" --item-amount 200000 --item-currency inr
```

Do not map Razorpay Plans to Stripe Prices. A Razorpay Plan is a subscription billing definition that wraps an Item.

## Admin Reads

Use these for inspection and debugging:

```bash
npx -y @insforge/cli payments razorpay customers --environment test
npx -y @insforge/cli payments razorpay subscriptions --environment test
npx -y @insforge/cli payments razorpay subscriptions --environment test --subject-type team --subject-id team_123
npx -y @insforge/cli payments razorpay transactions --environment test
npx -y @insforge/cli payments razorpay transactions --environment test --limit 20 --json
```

`--subject-type` and `--subject-id` are app billing subjects passed to InsForge, such as `team:team_123` or `user:user_123`. They are not Razorpay customer, order, payment, plan, or subscription IDs.

## RLS For Runtime App Code

Before building Razorpay Checkout UI, add app-specific RLS to the Razorpay runtime authorization tables:

- `payments.razorpay_orders`: `INSERT` for one-time order creation. Add `SELECT` only if the app reads order attempts.
- `payments.razorpay_subscriptions`: `INSERT` for subscription creation.
- `payments.razorpay_subscriptions`: `UPDATE` policy for cancel, pause, and resume authorization. The backend only probes `updated_at`; frontend users do not directly mutate provider state columns.

Example shape:

```sql
ALTER TABLE payments.razorpay_orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE payments.razorpay_subscriptions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "team admins create razorpay orders"
ON payments.razorpay_orders
FOR INSERT
TO authenticated
WITH CHECK (
  subject_type = 'team'
  AND public.is_team_billing_admin(subject_id)
);

CREATE POLICY "team admins create razorpay subscriptions"
ON payments.razorpay_subscriptions
FOR INSERT
TO authenticated
WITH CHECK (
  subject_type = 'team'
  AND public.is_team_billing_admin(subject_id)
);

CREATE POLICY "team admins manage razorpay subscriptions"
ON payments.razorpay_subscriptions
FOR UPDATE
TO authenticated
USING (
  subject_type = 'team'
  AND public.is_team_billing_admin(subject_id)
)
WITH CHECK (
  subject_type = 'team'
  AND public.is_team_billing_admin(subject_id)
);
```

For user-owned billing, use `subject_type = 'user' AND subject_id = auth.uid()::text`.

## Fulfillment Trigger

Create triggers on `payments.webhook_events` and update app-owned tables:

```sql
CREATE OR REPLACE FUNCTION public.fulfill_razorpay_billing_event()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.provider = 'razorpay'
     AND NEW.processing_status = 'processed'
     AND NEW.event_type IN ('payment.captured', 'order.paid', 'invoice.paid') THEN
    -- Update public.orders, public.team_entitlements, or an app-owned outbox.
    NULL;
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER fulfill_razorpay_billing_event
  AFTER INSERT OR UPDATE ON payments.webhook_events
  FOR EACH ROW
  EXECUTE FUNCTION public.fulfill_razorpay_billing_event();
```

Make fulfillment idempotent. For email, warehouse, CRM, or other external side effects, write an app-owned outbox row and process it asynchronously.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Expecting `payments razorpay webhooks configure` | Configure Razorpay webhooks manually in the Razorpay Dashboard |
| Treating Checkout callback verification as fulfillment | Fulfill from `payments.webhook_events` |
| Expecting a hosted Checkout redirect URL | Use Razorpay Checkout.js in the app |
| Treating Razorpay Plans as Stripe Prices | Use Razorpay Items and Plans natively |
| Letting any authenticated user manage subscriptions | Add app-specific `UPDATE` RLS on `payments.razorpay_subscriptions` |
