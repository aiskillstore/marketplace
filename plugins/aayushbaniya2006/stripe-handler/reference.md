# Stripe Payment Reference

## Core Files
- **Configuration**: `src/lib/stripe/index.ts` (Initializes Stripe client)
- **Webhook Handler**: `src/app/api/webhooks/stripe/route.ts` (Main entry point for events)
- **Success Page**: `src/app/(in-app)/app/subscribe/success/page.tsx`
- **Error Page**: `src/app/(in-app)/app/subscribe/error/page.tsx`
- **Inngest Client**: `src/lib/inngest/client.ts`

## Creating a Checkout Session (Server-Side)

Use this pattern in API routes or Server Actions for custom one-time payments.

```typescript
import stripe from "@/lib/stripe";
import { headers } from "next/headers";

export async function createCustomCheckout(userId: string, userEmail: string, priceId: string) {
  const checkoutSession = await stripe.checkout.sessions.create({
    mode: "payment", // or "subscription"
    customer_email: userEmail,
    // client_reference_id: userId, // Useful for matching in webhooks
    metadata: {
        type: "custom_product",
        userId: userId,
        productId: "prod_123"
    },
    line_items: [
      {
        price: priceId,
        quantity: 1,
      },
      // OR custom inline price
      /*
      {
        price_data: {
            currency: 'usd',
            product_data: {
                name: 'Custom Service',
            },
            unit_amount: 2000, // $20.00
        },
        quantity: 1,
      }
      */
    ],
    success_url: `${process.env.NEXT_PUBLIC_APP_URL}/app/subscribe/success?session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: `${process.env.NEXT_PUBLIC_APP_URL}/app/subscribe/error`,
  });

  return checkoutSession.url;
}
```

## Webhook Handling Pattern (with Inngest)

Use this pattern to offload processing to background workers, ensuring Stripe webhooks never timeout.
**Crucial**: Use `getOrCreateUser` to resolve the user from the Stripe payload, ensuring robustness.

### 1. Dispatch Event in Webhook
Located in `src/app/api/webhooks/stripe/route.ts`.

```typescript
import { inngest } from "@/lib/inngest/client";
import getOrCreateUser from "@/lib/users/getOrCreateUser"; // Ensure this is imported

// In onCheckoutSessionCompleted method
async onCheckoutSessionCompleted() {
    const object = this.data.object;
    const metadata = object.metadata;

    // 1. Check Metadata for custom type
    if (metadata?.type === "custom_product") {
        
        // 2. Resolve User (Best Practice)
        // Even if metadata has userId, this ensures we have the latest user state 
        // or creates one if missing (e.g. different email used).
        // Note: Adjust email/name extraction based on event object availability
        const email = object.customer_details?.email || object.customer_email;
        const name = object.customer_details?.name;

        if (email) {
             const { user } = await getOrCreateUser({
                emailId: email,
                name: name || undefined,
            });
            
            // 3. Dispatch Inngest event
            await inngest.send({
                name: "app/payment.custom_succeeded",
                data: {
                    sessionId: object.id,
                    userId: user.id, // Use the resolved user ID from DB
                    productId: metadata.productId,
                    amountTotal: object.amount_total,
                    metadata: metadata
                }
            });
            
            console.log("Dispatched Inngest event for custom product");
            return;
        }
    }
    
    // ... existing plan/credit logic ...
}
```

### 2. Handle Event in Background Function
Located in `src/app/api/inngest/functions/payment-fulfillment.ts`.

```typescript
import { inngest } from "@/lib/inngest/client";
import { db } from "@/db";
// import schemas...

export const handleCustomPayment = inngest.createFunction(
  { id: "handle-custom-payment" },
  { event: "app/payment.custom_succeeded" },
  async ({ event, step }) => {
    const { sessionId, userId, productId } = event.data;

    // Step 1: Idempotency Check (Optional but recommended)
    // const existingOrder = await step.run("check-existing", async () => {
    //   return await db.query.orders.findFirst({ where: eq(orders.paymentId, sessionId) });
    // });
    // if (existingOrder) return;

    // Step 2: Fulfill Order
    await step.run("fulfill-order", async () => {
        // e.g., unlock content, add to database
        console.log(`Fulfilling product ${productId} for user ${userId}`);
    });

    // Step 3: Send Confirmation Email
    await step.run("send-email", async () => {
        // await sendEmail(...)
    });

    return { success: true, sessionId };
  }
);
```

## Stripe CLI for Testing

Test webhooks locally.

```bash
# Login
stripe login

# Listen for events and forward to localhost
stripe listen --forward-to localhost:3000/api/webhooks/stripe

# Trigger specific events
stripe trigger payment_intent.succeeded
stripe trigger checkout.session.completed
stripe trigger invoice.paid
```

## Environment Variables

Ensure these are set in `.env.local`:

```env
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_... (Output from 'stripe listen')
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
```
