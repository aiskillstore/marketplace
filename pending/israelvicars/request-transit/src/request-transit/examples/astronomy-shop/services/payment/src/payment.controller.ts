// SYNTHETIC: payment. The request is validated with Zod inside the handler.
import { Controller } from '@nestjs/common';
import { GrpcMethod } from '@nestjs/microservices';
import { z } from 'zod';
import { Money } from '@shop/schemas';

const ChargeRequest = z.object({
  amount: Money,
  creditCard: z.object({ number: z.string(), cvv: z.number().int(), expirationYear: z.number().int(), expirationMonth: z.number().int() }),
});

export interface ChargeResponse {
  transactionId: string;
}

@Controller()
export class PaymentController {
  @GrpcMethod('PaymentService', 'Charge')
  charge(data: unknown): ChargeResponse {
    const req = ChargeRequest.parse(data);
    return { transactionId: 'txn-' + req.amount.units };
  }
}
