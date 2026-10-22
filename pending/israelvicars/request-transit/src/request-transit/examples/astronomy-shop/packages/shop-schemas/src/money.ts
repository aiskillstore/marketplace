import { z } from 'zod';

export const Money = z.object({
  currencyCode: z.string().length(3),
  units: z.number().int(),
  nanos: z.number().int().optional(),
});
export type MoneyT = z.infer<typeof Money>;
