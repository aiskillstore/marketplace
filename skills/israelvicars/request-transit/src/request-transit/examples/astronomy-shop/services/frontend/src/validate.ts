import type { ZodTypeAny } from 'zod';
export const validate = (schema: ZodTypeAny) => (req: any, _res: any, next: any) => { schema.parse(req.body); next(); };
