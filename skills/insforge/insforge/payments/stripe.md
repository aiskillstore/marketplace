# Stripe Payments SDK Integration

Use this guide when writing app code for Stripe payments through `@insforge/sdk`. For CLI setup, catalog sync, webhook setup, and fulfillment migrations, use the `insforge-cli` payments references first.

## Mental Model

- Stripe uses Products and Prices. A subscription is still created through Checkout using recurring Prices.
- InsForge SDK creates Stripe Checkout Sessions and Billing Portal Sessions.
- Stripe hosts Checkout and Billing Portal; the app redirects to returned URLs.
- Checkout success URLs are UX redirects only. Durable fulfillment comes from verified rows in `payments.webhook_events`.
- `payments.transactions` is for dashboard/reporting. Do not use it as the primary business workflow.

Do not use Razorpay Orders, Items, Plans, or Checkout.js concepts in a Stripe flow.

## Setup Check

Before writing app code:

```bash
npx -y @insforge/cli payments stripe status
npx -y @insforge/cli payments stripe catalog --environment test
```

If Stripe is unconfigured, ask the developer/admin to configure a Stripe key and sync catalog first. Default to `test`; use `live` only after explicit approval.

## RLS Before Checkout

Checkout and portal creation use the caller's InsForge token. If the app exposes billing subjects such as teams or organizations, add RLS before wiring UI.

Use these managed tables for Stripe runtime authorization:

- `payments.stripe_checkout_sessions`: `INSERT` for creating Checkout attempts, `SELECT` for reading/retrying attempts.
- `payments.stripe_customer_portal_sessions`: `INSERT` for portal attempts, `SELECT` for reading attempts.

If checkout sends `idempotencyKey`, retries need `SELECT` on the matching `payments.stripe_checkout_sessions` row because the backend may find an existing row after `ON CONFLICT`.

Example for user-owned checkout:

```sql
ALTER TABLE payments.stripe_checkout_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE payments.stripe_customer_portal_sessions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "users create their stripe checkout sessions"
ON payments.stripe_checkout_sessions
FOR INSERT
TO authenticated
WITH CHECK (
  subject_type = 'user'
  AND subject_id = auth.uid()::text
);

CREATE POLICY "users read their stripe checkout sessions"
ON payments.stripe_checkout_sessions
FOR SELECT
TO authenticated
USING (
  subject_type = 'user'
  AND subject_id = auth.uid()::text
);

CREATE POLICY "users create their stripe portal sessions"
ON payments.stripe_customer_portal_sessions
FOR INSERT
TO authenticated
WITH CHECK (
  subject_type = 'user'
  AND subject_id = auth.uid()::text
);

CREATE POLICY "users read their stripe portal sessions"
ON payments.stripe_customer_portal_sessions
FOR SELECT
TO authenticated
USING (
  subject_type = 'user'
  AND subject_id = auth.uid()::text
);
```

For teams or organizations, replace `auth.uid()` with a `SECURITY DEFINER` membership helper. Do not let users submit arbitrary `subject` values without a matching policy.

## One-Time Checkout

Create the app-owned pending record first, then create Checkout:

```typescript
const { data: order, error: orderError } = await insforge.database
  .from('orders')
  .insert([{ user_id: user.id, status: 'pending' }])
  .select()
  .single()

if (orderError) throw orderError

const { data, error } = await insforge.payments.stripe.createCheckoutSession('test', {
  mode: 'payment',
  lineItems: [{ priceId: 'price_123', quantity: 1 }],
  successUrl: `${window.location.origin}/orders/${order.id}`,
  cancelUrl: `${window.location.origin}/pricing`,
  subject: { type: 'user', id: user.id },
  customerEmail: user.email ?? null,
  metadata: { order_id: order.id },
  idempotencyKey: `order:${order.id}`
})

if (error) throw error
if (data?.checkoutSession.url) {
  window.location.assign(data.checkoutSession.url)
}
```

For anonymous one-time purchases, `subject` can be omitted, but use a narrow app-owned correlation record and `customerEmail` when available.

## Subscription Checkout

Subscription checkout requires `subject` because ongoing entitlement belongs to an app-defined billing owner.

```typescript
const { data, error } = await insforge.payments.stripe.createCheckoutSession('test', {
  mode: 'subscription',
  lineItems: [{ priceId: 'price_monthly_123', quantity: 1 }],
  successUrl: `${window.location.origin}/billing/success`,
  cancelUrl: `${window.location.origin}/billing`,
  subject: { type: 'team', id: teamId },
  customerEmail: user.email,
  idempotencyKey: `team:${teamId}:pro-monthly`
})

if (error) throw error
if (data?.checkoutSession.url) {
  window.location.assign(data.checkoutSession.url)
}
```

## Customer Portal

Use Stripe Billing Portal for existing customers who need to manage payment methods, invoices, cancellations, or subscriptions.

```typescript
const { data, error } =
  await insforge.payments.stripe.createCustomerPortalSession('test', {
    subject: { type: 'team', id: teamId },
    returnUrl: `${window.location.origin}/billing`
  })

if (error) throw error
if (data?.customerPortalSession.url) {
  window.location.assign(data.customerPortalSession.url)
}
```

Portal creation requires an authenticated user and an existing `payments.customer_mappings` row for the billing subject. If the backend returns `404`, show a subscribe or checkout CTA instead.

## Webhooks And Fulfillment

Stripe webhooks are managed by InsForge when the backend has a public URL:

```bash
npx -y @insforge/cli payments stripe webhooks configure --environment test
```

InsForge's Stripe managed event set:

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

Create app-owned fulfillment triggers on `payments.webhook_events`, not on success URLs and not on `payments.transactions`.

Webhook events are verified and processed independently. InsForge commits all rows derived from an event before marking that event `processed`, but Stripe gives no ordering guarantee across events: `invoice.paid` can be processed before `checkout.session.completed`, so rows created by another event (such as `payments.customer_mappings`) may not exist yet when a trigger fires. Resolve the billing subject from the event payload first and use `payments.customer_mappings` only as a fallback. Never let fulfillment skip silently: log or dead-letter events that cannot be resolved.

### One-Time Fulfillment

```sql
CREATE OR REPLACE FUNCTION public.fulfill_stripe_paid_order()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.provider = 'stripe'
     AND NEW.processing_status = 'processed'
     AND NEW.event_type IN (
       'checkout.session.completed',
       'checkout.session.async_payment_succeeded',
       'payment_intent.succeeded',
       'invoice.paid'
     )
     AND (NEW.payload -> 'data' -> 'object' -> 'metadata' ->> 'order_id') IS NOT NULL THEN
    UPDATE public.orders
    SET status = 'paid',
        paid_at = COALESCE(NEW.processed_at, NOW())
    WHERE id::text = NEW.payload -> 'data' -> 'object' -> 'metadata' ->> 'order_id'
      AND status = 'pending';
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER fulfill_stripe_paid_order_from_webhook
  AFTER INSERT OR UPDATE ON payments.webhook_events
  FOR EACH ROW
  EXECUTE FUNCTION public.fulfill_stripe_paid_order();
```

### Subscription Fulfillment

Subscription events do not carry the app `metadata` sent at checkout. Resolve the billing subject from the subscription metadata embedded in the event payload — InsForge stamps `insforge_subject_type` and `insforge_subject_id` at checkout, and Stripe snapshots it onto subscription-generated invoices as `parent.subscription_details.metadata`. Check `invoice.metadata` next, then fall back to `payments.customer_mappings` (the same order InsForge uses internally):

```sql
CREATE OR REPLACE FUNCTION public.grant_subscription_access()
RETURNS TRIGGER AS $$
DECLARE
  v_subject_type TEXT;
  v_subject_id TEXT;
BEGIN
  IF NEW.provider = 'stripe'
     AND NEW.event_type = 'invoice.paid'
     AND NEW.processing_status = 'processed' THEN
    v_subject_type := COALESCE(
      NEW.payload -> 'data' -> 'object' -> 'parent'
        -> 'subscription_details' -> 'metadata' ->> 'insforge_subject_type',
      NEW.payload -> 'data' -> 'object' -> 'metadata' ->> 'insforge_subject_type'
    );
    v_subject_id := COALESCE(
      NEW.payload -> 'data' -> 'object' -> 'parent'
        -> 'subscription_details' -> 'metadata' ->> 'insforge_subject_id',
      NEW.payload -> 'data' -> 'object' -> 'metadata' ->> 'insforge_subject_id'
    );

    IF v_subject_id IS NULL THEN
      SELECT m.subject_type, m.subject_id
      INTO v_subject_type, v_subject_id
      FROM payments.customer_mappings m
      WHERE m.provider = NEW.provider
        AND m.environment = NEW.environment
        AND m.provider_customer_id = NEW.payload -> 'data' -> 'object' ->> 'customer';
    END IF;

    IF v_subject_id IS NULL THEN
      RAISE WARNING 'Stripe event % has no resolvable billing subject', NEW.provider_event_id;
      RETURN NEW;
    END IF;

    -- Branch on the subject type sent at checkout; team_id is a UUID here,
    -- so the type check also guards the cast.
    IF v_subject_type = 'team' THEN
      INSERT INTO public.team_entitlements (team_id, plan, active, updated_at)
      VALUES (v_subject_id::uuid, 'pro', true, NOW())
      ON CONFLICT (team_id) DO UPDATE SET
        plan = EXCLUDED.plan,
        active = true,
        updated_at = NOW();
    END IF;
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER grant_subscription_access_from_stripe_webhook
  AFTER INSERT OR UPDATE ON payments.webhook_events
  FOR EACH ROW
  EXECUTE FUNCTION public.grant_subscription_access();
```

Adjust the entitlement table to the billing subject type used at checkout. Handle revocation the same way from `customer.subscription.deleted` and `customer.subscription.updated` (`payload -> 'data' -> 'object' -> 'metadata'` holds the subject keys on subscription events).

Keep trigger functions idempotent. For external side effects such as email or warehouse work, write an app-owned outbox row and process it from an edge function or worker.

## Runtime State

Use app-owned tables for end-user state:

- `public.orders`
- `public.credit_ledger`
- `public.team_entitlements`
- `public.billing_status`

Use `payments.transactions` only for admin/debug dashboards and provider reference IDs. Do not expose `payments.customer_mappings`, `payments.transactions`, `payments.stripe_subscriptions`, or `payments.stripe_subscription_items` directly to end users.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Calling payment methods at the root `payments` namespace | Use `insforge.payments.stripe.*` |
| Sending provider-prefixed price fields | Send `priceId` |
| Marking paid from success URL | Fulfill from `payments.webhook_events` |
| Starting shared-subject checkout before RLS | Add policies on `payments.stripe_checkout_sessions` first |
| Idempotent retry fails after adding only `INSERT` | Add matching `SELECT` for retryable checkout rows |
| Trying to update a Stripe Price amount | Create a new Price and archive the old one |
| Resolving subscription subjects only via `payments.customer_mappings` | Read `insforge_subject_*` from the event payload first; events from other types may not have created the mapping yet |
