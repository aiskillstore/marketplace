import { z } from 'zod';
import { Money } from './money';

export const Address = z.object({
  streetAddress: z.string(),
  city: z.string(),
  state: z.string().optional(),
  country: z.string(),
  zipCode: z.string(),
});

export const CheckoutRequest = z.object({
  userId: z.string(),
  userCurrency: z.string().length(3),
  address: Address,
  email: z.string().email(),
  creditCard: z.object({
    number: z.string().min(12),
    cvv: z.number().int(),
    expirationYear: z.number().int(),
    expirationMonth: z.number().int().min(1).max(12),
  }),
});

export const OrderResult = z.object({
  orderId: z.string().uuid(),
  shippingTrackingId: z.string(),
  shippingCost: Money,
  items: z.array(z.object({ productId: z.string(), quantity: z.number().int(), cost: Money })),
});
export type OrderResultT = z.infer<typeof OrderResult>;

export interface OrderPlacedEvent {
  orderId: string;
  userId: string;
  total: { currencyCode: string; units: number };
  itemCount: number;
}
