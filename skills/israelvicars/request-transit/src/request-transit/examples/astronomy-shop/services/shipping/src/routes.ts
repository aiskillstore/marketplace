// SYNTHETIC: shipping quotes and orders, Express + Joi.
import express, { Request, Response } from 'express';
import Joi from 'joi';
import { celebrate } from 'celebrate';

const app = express();

const CartItem = Joi.object({
  productId: Joi.string().required(),
  quantity: Joi.number().integer().min(1).required(),
});

const Address = Joi.object({
  streetAddress: Joi.string().required(),
  city: Joi.string().required(),
  state: Joi.string(),
  country: Joi.string().required(),
  zipCode: Joi.string().required(),
});

const GetQuoteBody = Joi.object({
  address: Address.required(),
  items: Joi.array().items(CartItem).required(),
});

const ShipOrderBody = Joi.object({
  address: Address.required(),
  items: Joi.array().items(CartItem).required(),
});

interface QuoteResponse {
  costUsd: { currencyCode: string; units: number; nanos: number };
}

interface ShipOrderResponse {
  trackingId: string;
}

app.post('/get-quote', celebrate({ body: GetQuoteBody }), async (req: Request, res: Response<QuoteResponse>) => {
  res.json({ costUsd: { currencyCode: 'USD', units: 19, nanos: 450000000 } });
});

app.post('/ship-order', celebrate({ body: ShipOrderBody }), (req: Request, res: Response<ShipOrderResponse>) => {
  res.json({ trackingId: 'TRK-0001' });
});
