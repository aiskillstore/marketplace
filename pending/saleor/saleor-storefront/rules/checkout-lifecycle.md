# Saleor Checkout Lifecycle

Understanding how Saleor checkout sessions work — creation, persistence, completion, and common failure modes — prevents payment errors and lost orders.

> **Source**: [Saleor Docs - Checkout](https://docs.saleor.io/developer/checkout/overview)

## Core Concept

A Saleor Checkout is a mutable object that tracks:
- Line items (variants + quantities)
- Shipping/billing addresses
- Shipping method
- Payment transactions
- Channel (set at creation, immutable)

When payment succeeds, `checkoutComplete` converts it to an immutable **Order**.

## Checkout ID

Checkout IDs are base64-encoded Saleor global IDs:

```javascript
atob("Q2hlY2tvdXQ6YThjN2Y4YjgtZmU0NS00ZTRkLThhZmItZDdjYWI2YTM5MTdm");
// → "Checkout:a8c7f8b8-fe45-4e4d-8afb-d7cab6a3917f"
```

Common storage strategies:
- **Cookie**: `checkoutId-{channel}` (survives page refreshes)
- **URL query param**: `/checkout?checkout=Q2hlY2...` (shareable)
- **localStorage**: Alternative to cookies

## Lifecycle

```
1. User adds first item → checkoutCreate mutation
2. Checkout ID stored in cookie/URL
3. User adds more items → checkoutLinesAdd
4. User sets address → checkoutShippingAddressUpdate
5. User picks shipping → checkoutDeliveryMethodUpdate
6. Payment initiated → transactionInitialize
7. Payment authorized → transactionProcess
8. checkoutComplete → Checkout becomes Order
9. Clear stored checkout ID → ready for new cart
```

### Creation

A new checkout is created when:
- User adds first item to an empty cart
- No valid checkout ID exists in storage
- Existing checkout is not found in Saleor (expired/deleted)

### Completion

When `checkoutComplete` succeeds:
- Checkout is converted to an Order
- The checkout ID becomes invalid
- A new checkout must be created for future purchases

## Common Errors

### "CHECKOUT_NOT_FULLY_PAID"

```
The authorized amount doesn't cover the checkout's total amount.
```

**Causes**:
1. Payment app is down — transaction created but authorization failed
2. Stale checkout — previous partial transactions accumulated
3. Amount mismatch — checkout total changed after transaction init (e.g., shipping added)

**Debug steps**:
1. Query the checkout's `transactions` to see their status
2. Check if `transactionEvent.type` is `AUTHORIZATION_FAILURE`
3. If so, check if the payment app is healthy

### "AUTHORIZATION_FAILURE"

```json
{
	"transactionEvent": {
		"message": "Failed to delivery request.",
		"type": "AUTHORIZATION_FAILURE"
	}
}
```

**Cause**: The payment app (Stripe, Adyen, Dummy Gateway) is not responding.

**Fix**: Check Saleor Dashboard → Apps for payment app health.

### Stale Checkout with Failed Transactions

If payment fails multiple times, the checkout accumulates partial transactions. Fresh checkout is needed:
- Clear the checkout cookie
- Navigate to checkout without the `?checkout=` URL param
- Test in incognito mode

## Debugging

### Inspect Checkout State

```graphql
query {
	checkout(id: "Q2hlY2tvdXQ6...") {
		id
		totalPrice { gross { amount currency } }
		lines { variant { name } quantity }
		shippingMethod { name }
		transactions {
			id
			chargedAmount { amount }
			authorizedAmount { amount }
		}
	}
}
```

### Check Cookie in Browser

```javascript
document.cookie.split(";").find(c => c.includes("checkoutId"));
```

## Best Practices

1. **Always use live checkout data for payment amounts** — Never use cached prices
2. **Handle "checkout not found" gracefully** — Create a new checkout
3. **Clear checkout after completion** — Stale IDs cause confusing errors
4. **Test with fresh checkouts** when debugging payment issues
5. **Check payment app health** when transactions fail with `AUTHORIZATION_FAILURE`

## Anti-patterns

❌ **Don't cache checkout data** — It's transactional, always fetch fresh  
❌ **Don't reuse checkout IDs after completion** — They become invalid  
❌ **Don't ignore failed transactions** — They accumulate and block checkout completion  
❌ **Don't display cached prices at payment time** — Use live checkout totals
