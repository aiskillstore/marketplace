# npx -y @insforge/cli payments

Use this reference for shared Payments CLI rules and routing. Load the provider-specific reference before running setup commands:

- [stripe.md](stripe.md)
- [razorpay.md](razorpay.md)

For app code, load the matching `insforge` app skill provider guide:

- `skills/insforge/payments/stripe.md`
- `skills/insforge/payments/razorpay.md`

## Availability

Payments require a backend that exposes `/api/payments`.

Always start with the provider status command:

```bash
npx -y @insforge/cli payments stripe status
npx -y @insforge/cli payments razorpay status
```

If the CLI says `Payments are not available on this backend`, stop and ask the developer/admin to enable payments or upgrade the self-hosted backend. Do not work around this by storing provider keys with generic `secrets` commands or embedding secret keys in app code.

## Provider Command Map

| Need | Stripe | Razorpay |
|------|--------|----------|
| Status | `payments stripe status` | `payments razorpay status` |
| Configure keys | `payments stripe config ...` | `payments razorpay config ...` |
| Sync mirrored state | `payments stripe sync` | `payments razorpay sync` |
| Catalog read | `payments stripe catalog` | `payments razorpay catalog` |
| Customer read | `payments stripe customers` | `payments razorpay customers` |
| Subscription read | `payments stripe subscriptions` | `payments razorpay subscriptions` |
| Transaction read | `payments stripe transactions` | `payments razorpay transactions` |
| Catalog mutations | `payments stripe products`, `payments stripe prices` | `payments razorpay items`, `payments razorpay plans` |
| Webhook setup | `payments stripe webhooks configure` | Manual in Razorpay Dashboard |

Use `--environment test` while building. Use `--environment live` only after the developer explicitly approves production changes.

## Common Concepts

- `test` and `live` are the only supported payment environments.
- Provider secret keys belong in the managed payments config path, not generic secrets.
- `sync` mirrors provider catalog/customers/subscriptions/transactions into InsForge; it does not replace webhook delivery.
- Runtime checkout/order/subscription/customer portal calls belong in the app through `@insforge/sdk`, not CLI commands.
- App-facing billing state belongs in app-owned tables such as `public.orders`, `public.credit_ledger`, or `public.team_entitlements`.

## Fulfillment Model

Durable fulfillment should run from verified provider webhook rows:

- Trigger source: `payments.webhook_events`
- Dashboard/reporting projection: `payments.transactions`
- App-owned targets: `public.orders`, `public.credit_ledger`, `public.team_entitlements`, or similar

Do not fulfill from:

- Stripe success URLs
- Razorpay Checkout callback verification
- `payments.transactions`

Use `payments.transactions` for dashboard/reporting and provider reference IDs only.

Basic trigger shape:

```sql
CREATE OR REPLACE FUNCTION public.fulfill_from_payment_webhook()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.processing_status <> 'processed' THEN
    RETURN NEW;
  END IF;

  IF NEW.provider = 'stripe' THEN
    -- Stripe-specific event and payload handling.
    NULL;
  ELSIF NEW.provider = 'razorpay' THEN
    -- Razorpay-specific event and payload handling.
    NULL;
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER fulfill_from_payment_webhook
  AFTER INSERT OR UPDATE ON payments.webhook_events
  FOR EACH ROW
  EXECUTE FUNCTION public.fulfill_from_payment_webhook();
```

Make trigger functions idempotent. For external side effects such as email, shipping, CRM, or warehouse work, write an app-owned outbox row and process it from an edge function or worker.

Webhook events are processed independently with no cross-event ordering guarantee. Rows derived from an event are committed before that event is marked `processed`, but rows owned by other events — such as `payments.customer_mappings`, which checkout completion creates — may not exist yet when a trigger fires. Resolve billing subjects from the event payload first and treat lookups into rows owned by other events as fallbacks.

## Managed Tables

Provider-specific authorization tables:

| Provider | Runtime authorization tables |
|----------|------------------------------|
| Stripe | `payments.stripe_checkout_sessions`, `payments.stripe_customer_portal_sessions` |
| Razorpay | `payments.razorpay_orders`, `payments.razorpay_subscriptions` |

Provider-native and projection tables:

| Table | Purpose |
|-------|---------|
| `payments.webhook_events` | Verified provider event ledger. Use for durable fulfillment triggers. |
| `payments.transactions` | Dashboard/reporting projection for successful, failed, pending, and refunded payment activity. |
| `payments.customer_mappings` | Provider customer IDs mapped to app billing subjects. |
| `payments.stripe_products`, `payments.stripe_prices` | Stripe catalog mirror. |
| `payments.stripe_subscriptions`, `payments.stripe_subscription_items` | Stripe subscription mirror. |
| `payments.razorpay_items`, `payments.razorpay_plans` | Razorpay catalog mirror. |
| `payments.razorpay_subscriptions` | Razorpay subscription mirror and management authorization probe. |
| `payments.razorpay_orders` | Razorpay one-time order attempts. |

Do not expose provider-native or projection tables directly to end users. Use app-owned read models with app-specific RLS.

## Provider References

- Use [stripe.md](stripe.md) for Stripe keys, automated webhook registration, Products, Prices, Checkout Sessions, Billing Portal, and Stripe-specific RLS.
- Use [razorpay.md](razorpay.md) for Razorpay keys, manual webhook setup, Items, Plans, Orders, Subscriptions, Checkout.js, and Razorpay-specific RLS.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Running root payments commands without a provider | Use `payments stripe ...` or `payments razorpay ...` |
| Using generic secrets for provider keys | Use provider-specific `payments ... config` commands |
| Treating Stripe Prices and Razorpay Plans as equivalent | Use provider-native catalog concepts |
| Expecting Razorpay webhook auto-registration | Configure Razorpay webhooks manually in Razorpay Dashboard |
| Fulfilling from success/callback URLs | Fulfill from `payments.webhook_events` |
| Building app UI from `payments.transactions` | Build app-owned fulfillment tables with RLS |
