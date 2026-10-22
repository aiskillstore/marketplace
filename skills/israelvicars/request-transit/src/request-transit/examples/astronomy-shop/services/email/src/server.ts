// SYNTHETIC: order confirmation emails. No response type is declared, so the response stays a gap.
import express from 'express';
import { z } from 'zod';

const app = express();

const OrderConfirmation = z.object({
  email: z.string().email(),
  order: z.object({
    orderId: z.string(),
    shippingTrackingId: z.string(),
    items: z.array(z.object({ productId: z.string(), quantity: z.number().int() })),
  }),
});

app.post('/send_order_confirmation', async (req, res) => {
  const body = OrderConfirmation.parse(req.body);
  await sendMail(body.email, body.order);
  res.status(200).end();
});

async function sendMail(_to: string, _order: unknown) {}
