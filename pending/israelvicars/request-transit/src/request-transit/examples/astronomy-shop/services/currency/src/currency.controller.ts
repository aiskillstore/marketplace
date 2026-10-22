// SYNTHETIC: currency conversion. Plain TypeScript interfaces, no runtime validation.
import { Controller } from '@nestjs/common';
import { GrpcMethod } from '@nestjs/microservices';
import type { MoneyT } from '@shop/schemas';

interface CurrencyConversionRequest {
  from: MoneyT;
  toCode: string;
}

@Controller()
export class CurrencyController {
  @GrpcMethod('CurrencyService', 'Convert')
  convert(req: CurrencyConversionRequest): MoneyT {
    return { currencyCode: req.toCode, units: req.from.units };
  }
}
