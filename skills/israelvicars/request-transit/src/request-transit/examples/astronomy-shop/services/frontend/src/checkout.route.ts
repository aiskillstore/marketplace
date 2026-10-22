// SYNTHETIC: the storefront's checkout endpoint.
import { Router, Request, Response } from 'express';
import { CheckoutRequest, OrderResultT } from '@shop/schemas';
import { validate } from './validate';

export const router = Router();

router.post('/api/checkout', validate(CheckoutRequest), async (req: Request, res: Response<OrderResultT>) => {
  const order = await req.app.locals.checkout.placeOrder(req.body);
  res.json(order);
});
