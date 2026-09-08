# Razorpay Payments SDK Integration

Use this guide when writing app code for Razorpay payments through `@insforge/sdk`. For CLI setup, catalog sync, manual webhook instructions, and fulfillment migrations, use the `insforge-cli` payments references first.

## Mental Model

- Razorpay one-time payments use Orders plus Razorpay Checkout.js.
- Razorpay subscriptions use Plans. A Plan is a recurring definition around an Item.
- Razorpay Checkout runs inside the app; InsForge returns `checkoutOptions`, not a hosted redirect URL.
- Client signature verification proves the Checkout callback is authentic. It is not the durable fulfillment signal.
- Durable fulfillment comes from verified rows in `payments.webhook_events`.
- `payments.transactions` is for dashboard/reporting. Do not use it as the primary business workflow.

Do not use Stripe Checkout, Stripe Prices, or Billing Portal concepts in a Razorpay flow.

## Setup Check

Before writing app code:

```bash
npx -y @insforge/cli payments razorpay status
npx -y @insforge/cli payments razorpay catalog --environment test
```

If Razorpay is unconfigured, ask the developer/admin to configure Key ID and Key Secret first. Default to `test`; use `live` only after explicit approval.

Razorpay webhooks are manual. Confirm the developer configured the webhook URL, webhook secret, and recommended events in the Razorpay Dashboard before relying on fulfillment.

## RLS Before Orders And Subscriptions

Razorpay runtime routes use the caller's InsForge token for authorization probes.

Use these managed tables:

- `payments.razorpay_orders`: `INSERT` for one-time order creation. Add `SELECT` only when the app needs to read order attempts.
- `payments.razorpay_subscriptions`: `INSERT` for subscription creation.
- `payments.razorpay_subscriptions`: `UPDATE` policy for cancel, pause, and resume authorization. The backend only probes `updated_at`; it does not give frontend users direct access to state columns.

Example for team billing:

```sql
CREATE OR REPLACE FUNCTION public.is_team_billing_admin(team_id text)
RETURNS boolean
LANGUAGE sql
SECURITY DEFINER
SET search_path = public
AS $$
  SELECT EXISTS (
    SELECT 1
    FROM public.team_members
    WHERE team_members.team_id::text = is_team_billing_admin.team_id
      AND team_members.user_id = auth.uid()
      AND team_members.role IN ('owner', 'admin')
  );
$$;

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

For user-owned billing, replace the helper with `subject_type = 'user' AND subject_id = auth.uid()::text`. Do not let users submit arbitrary `subject` values without a matching policy.

## One-Time Order Flow

Load Razorpay Checkout.js in the app:

```html
<script src="https://checkout.razorpay.com/v1/checkout.js"></script>
```

Create an app-owned pending record first, then create a Razorpay Order:

```typescript
const { data: order, error: orderError } = await insforge.database
  .from('orders')
  .insert([{ team_id: teamId, status: 'pending' }])
  .select()
  .single()

if (orderError) throw orderError

const { data, error } = await insforge.payments.razorpay.createOrder('test', {
  amount: 50000,
  currency: 'INR',
  subject: { type: 'team', id: teamId },
  customerName: user.name ?? null,
  customerEmail: user.email ?? null,
  notes: { order_id: order.id }
})

if (error) throw error

const checkout = new Razorpay({
  ...data.checkoutOptions,
  handler: async (response) => {
    const verified = await insforge.payments.razorpay.verifyOrder('test', {
      orderId: response.razorpay_order_id,
      paymentId: response.razorpay_payment_id,
      signature: response.razorpay_signature
    })

    if (verified.error) throw verified.error
    window.location.assign(`/orders/${order.id}`)
  }
})

checkout.open()
```

Do not put UUIDs in Razorpay `receipt`. Razorpay limits `receipt` to a unique internal reference of at most 40 characters.
Omit it unless the app already has a short unique receipt number such as `RCP-10042`; keep app UUIDs in Razorpay `notes`.

After verification, show pending or processing state until the app-owned order is updated by webhook fulfillment.

## Subscription Flow

Create or sync the Razorpay Plan first. Then create the subscription and open Checkout:

```typescript
const { data, error } = await insforge.payments.razorpay.createSubscription('test', {
  planId: 'plan_123',
  totalCount: 12,
  subject: { type: 'team', id: teamId },
  customerName: user.name ?? null,
  customerEmail: user.email ?? null
})

if (error) throw error

const checkout = new Razorpay({
  ...data.checkoutOptions,
  handler: async (response) => {
    const verified = await insforge.payments.razorpay.verifySubscription('test', {
      subscriptionId: response.razorpay_subscription_id,
      paymentId: response.razorpay_payment_id,
      signature: response.razorpay_signature
    })

    if (verified.error) throw verified.error
    window.location.assign('/billing')
  }
})

checkout.open()
```

## Subscription Management

Razorpay does not have a hosted Billing Portal equivalent. Use backend routes through the SDK:

```typescript
await insforge.payments.razorpay.cancelSubscription('test', 'sub_123', {
  cancelAtCycleEnd: false
})

await insforge.payments.razorpay.pauseSubscription('test', 'sub_123')
await insforge.payments.razorpay.resumeSubscription('test', 'sub_123')
```

These routes evaluate `UPDATE` policies on `payments.razorpay_subscriptions`; they do not let the user directly mutate provider-managed subscription state.

## Webhooks And Fulfillment

Razorpay webhook setup is manual. From the InsForge dashboard (Dashboard -> Payments -> Settings -> Webhooks), copy:

- Webhook URL, for example `/api/webhooks/razorpay/test`
- Webhook secret

Then create a webhook in the Razorpay Dashboard with that URL and secret, and select the events InsForge handles.

Razorpay can only deliver webhooks to a public HTTPS URL.

Events InsForge handles:

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

Create app-owned fulfillment triggers on `payments.webhook_events`, not on Checkout callback verification and not on `payments.transactions`.

```sql
CREATE OR REPLACE FUNCTION public.fulfill_razorpay_order()
RETURNS TRIGGER AS $$
DECLARE
  app_order_id text;
BEGIN
  app_order_id := COALESCE(
    NEW.payload -> 'payload' -> 'payment' -> 'entity' -> 'notes' ->> 'order_id',
    NEW.payload -> 'payload' -> 'order' -> 'entity' -> 'notes' ->> 'order_id',
    NEW.payload -> 'payload' -> 'invoice' -> 'entity' -> 'notes' ->> 'order_id'
  );

  IF NEW.provider = 'razorpay'
     AND NEW.processing_status = 'processed'
     AND NEW.event_type IN ('payment.captured', 'order.paid', 'invoice.paid')
     AND app_order_id IS NOT NULL THEN
    UPDATE public.orders
    SET status = 'paid',
        paid_at = COALESCE(NEW.processed_at, NOW())
    WHERE id::text = app_order_id
      AND status = 'pending';
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER fulfill_razorpay_order_from_webhook
  AFTER INSERT OR UPDATE ON payments.webhook_events
  FOR EACH ROW
  EXECUTE FUNCTION public.fulfill_razorpay_order();
```

For subscriptions, resolve the billing subject from the subscription entity's `notes` in the event payload — InsForge stamps `insforge_subject_type` and `insforge_subject_id` into notes at subscription creation (and creates the `payments.customer_mappings` row at the same time, so the mapping is also a safe fallback):

```sql
CREATE OR REPLACE FUNCTION public.grant_razorpay_subscription_access()
RETURNS TRIGGER AS $$
DECLARE
  v_subject_type TEXT;
  v_subject_id TEXT;
BEGIN
  IF NEW.provider = 'razorpay'
     AND NEW.event_type = 'subscription.charged'
     AND NEW.processing_status = 'processed' THEN
    v_subject_type := NEW.payload -> 'payload' -> 'subscription' -> 'entity'
                      -> 'notes' ->> 'insforge_subject_type';
    v_subject_id := NEW.payload -> 'payload' -> 'subscription' -> 'entity'
                    -> 'notes' ->> 'insforge_subject_id';

    IF v_subject_id IS NULL THEN
      SELECT m.subject_type, m.subject_id
      INTO v_subject_type, v_subject_id
      FROM payments.customer_mappings m
      WHERE m.provider = NEW.provider
        AND m.environment = NEW.environment
        AND m.provider_customer_id = NEW.payload -> 'payload' -> 'subscription'
                                     -> 'entity' ->> 'customer_id';
    END IF;

    IF v_subject_id IS NULL THEN
      RAISE WARNING 'Razorpay event % has no resolvable billing subject', NEW.provider_event_id;
      RETURN NEW;
    END IF;

    -- Branch on the subject type sent at creation; team_id is a UUID here,
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

CREATE TRIGGER grant_razorpay_subscription_access_from_webhook
  AFTER INSERT OR UPDATE ON payments.webhook_events
  FOR EACH ROW
  EXECUTE FUNCTION public.grant_razorpay_subscription_access();
```

Handle revocation the same way from `subscription.cancelled`, `subscription.halted`, and `subscription.expired`.

Keep trigger functions idempotent. For external side effects such as email or warehouse work, write an app-owned outbox row and process it from an edge function or worker.

## Runtime State

Use app-owned tables for end-user state:

- `public.orders`
- `public.credit_ledger`
- `public.team_entitlements`
- `public.billing_status`

Use `payments.transactions` only for admin/debug dashboards and provider reference IDs. Do not expose `payments.customer_mappings`, `payments.transactions`, or provider-native subscription rows directly to end users.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Expecting a hosted Checkout URL | Load Razorpay Checkout.js and pass `checkoutOptions` |
| Treating `verifyOrder` as fulfillment | Use verified webhook rows in `payments.webhook_events` |
| Using Stripe Prices for Razorpay subscriptions | Use Razorpay Items and Plans |
| Forgetting manual webhook setup | Configure Razorpay Dashboard webhook URL, secret, and events |
| Letting users manage another team's subscription | Add `UPDATE` RLS on `payments.razorpay_subscriptions` |
| Reading `payments.transactions` as app state | Maintain app-owned order or entitlement tables |
