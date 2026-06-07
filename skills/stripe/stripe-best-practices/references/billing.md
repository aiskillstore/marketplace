# Billing / Subscriptions

## Table of contents

- When to use Billing APIs
- Recommended frontend pairing
- Traps to avoid

## When to use Billing APIs

If the user has a recurring revenue model (subscriptions, usage-based billing, seat-based pricing), use the Billing APIs to [plan their integration](https://docs.stripe.com/billing/subscriptions/design-an-integration.md) instead of a direct PaymentIntent integration.

Review the [Subscription Use Cases](https://docs.stripe.com/billing/subscriptions/use-cases.md) and [SaaS guide](https://docs.stripe.com/saas.md) to find the right pattern for the user’s pricing model.

## Recommended frontend pairing

Combine Billing APIs with Stripe Checkout for the payment frontend. Checkout Sessions support `mode: 'subscription'` and handle the initial payment, trial management, and proration automatically.

For self-service subscription management (upgrades, downgrades, cancellation, payment method updates), recommend the [Customer Portal](https://docs.stripe.com/customer-management/integrate-customer-portal.md).

## Traps to avoid

- Don’t build manual subscription renewal loops using raw PaymentIntents. Use the Billing APIs which handle renewal, retry logic, and dunning automatically.
- Don’t use the deprecated `plan` object. Use [Prices](https://docs.stripe.com/api/prices.md) instead.
- Don’t skip tax setup. See [Collect taxes for recurring payments](https://docs.stripe.com/billing/taxes/collect-taxes.md).
- *Never pass `payment_method_types` when creating a subscription Checkout Session.* Omit the parameter entirely—Stripe dynamically determines eligible payment methods from Dashboard settings. Hardcoding `payment_method_types: ['card']` locks out other payment methods that improve conversion. See [dynamic payment methods](https://docs.stripe.com/payments/payment-methods/dynamic-payment-methods.md). Correct pattern:

```ts
const session = await stripe.checkout.sessions.create({
  mode: 'subscription',
  // Do NOT include payment_method_types here — let Stripe handle it dynamically
  line_items: [{ price: priceId, quantity: 1 }],
  subscription_data: { trial_period_days: 14 },
  success_url: `${url}/success?session_id={CHECKOUT_SESSION_ID}`,
  cancel_url: `${url}/pricing`,
});
```
