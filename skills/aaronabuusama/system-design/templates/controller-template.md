# Controller Template (HTTP Adapter)

## Structure

```typescript
// src/interfaces/http/controllers/[Entity]Controller.ts

import type { [UseCase] } from '../../../application/ports/inbound';

export class [Entity]Controller {
  constructor(
    private readonly [useCase]: [UseCase]
  ) {}

  async [httpMethod](req: Request): Promise<Response> {
    // 1. Parse request (params, body, query)
    // 2. Call use case
    // 3. Map result to HTTP response
  }
}
```

## Complete Example: OrderController

```typescript
// src/interfaces/http/controllers/OrderController.ts

import type {
  PlaceOrderUseCase,
  GetOrderUseCase,
  CancelOrderUseCase,
  ListOrdersUseCase,
} from '../../../application/ports/inbound';

export class OrderController {
  constructor(
    private readonly placeOrder: PlaceOrderUseCase,
    private readonly getOrder: GetOrderUseCase,
    private readonly cancelOrder: CancelOrderUseCase,
    private readonly listOrders: ListOrdersUseCase
  ) {}

  // POST /api/orders
  async create(req: Request): Promise<Response> {
    try {
      const body = await req.json();

      // Validate request shape
      const validationError = this.validateCreateRequest(body);
      if (validationError) {
        return this.badRequest(validationError);
      }

      // Execute use case
      const result = await this.placeOrder.execute({
        customerId: body.customerId,
        items: body.items,
        paymentMethodId: body.paymentMethodId,
      });

      // Handle use case errors
      if ('type' in result) {
        return this.mapUseCaseError(result);
      }

      // Success
      return this.created(result);
    } catch (error) {
      return this.internalError(error);
    }
  }

  // GET /api/orders/:id
  async get(req: Request): Promise<Response> {
    try {
      const id = this.extractParam(req, 'id');
      if (!id) {
        return this.badRequest('Order ID is required');
      }

      const result = await this.getOrder.execute({ orderId: id });

      if ('type' in result) {
        if (result.type === 'NOT_FOUND') {
          return this.notFound(`Order ${id} not found`);
        }
        return this.mapUseCaseError(result);
      }

      return this.ok(result);
    } catch (error) {
      return this.internalError(error);
    }
  }

  // GET /api/orders?customerId=xxx&status=pending
  async list(req: Request): Promise<Response> {
    try {
      const url = new URL(req.url);
      const customerId = url.searchParams.get('customerId');
      const status = url.searchParams.get('status');
      const page = parseInt(url.searchParams.get('page') ?? '1');
      const limit = parseInt(url.searchParams.get('limit') ?? '20');

      const result = await this.listOrders.execute({
        customerId: customerId ?? undefined,
        status: status ?? undefined,
        pagination: { page, limit },
      });

      return this.ok(result);
    } catch (error) {
      return this.internalError(error);
    }
  }

  // DELETE /api/orders/:id
  async cancel(req: Request): Promise<Response> {
    try {
      const id = this.extractParam(req, 'id');
      if (!id) {
        return this.badRequest('Order ID is required');
      }

      const result = await this.cancelOrder.execute({ orderId: id });

      if ('type' in result) {
        return this.mapUseCaseError(result);
      }

      return this.noContent();
    } catch (error) {
      return this.internalError(error);
    }
  }

  // ===== Private Helpers =====

  private validateCreateRequest(body: unknown): string | null {
    if (!body || typeof body !== 'object') {
      return 'Request body is required';
    }

    const { customerId, items, paymentMethodId } = body as Record<string, unknown>;

    if (!customerId || typeof customerId !== 'string') {
      return 'customerId is required';
    }

    if (!Array.isArray(items) || items.length === 0) {
      return 'items must be a non-empty array';
    }

    if (!paymentMethodId || typeof paymentMethodId !== 'string') {
      return 'paymentMethodId is required';
    }

    return null;
  }

  private extractParam(req: Request, name: string): string | undefined {
    // Bun.serve provides params on the request
    return (req as any).params?.[name];
  }

  private mapUseCaseError(error: { type: string; [key: string]: unknown }): Response {
    switch (error.type) {
      case 'NOT_FOUND':
        return this.notFound(error.message as string ?? 'Not found');
      case 'CUSTOMER_NOT_FOUND':
        return this.badRequest('Customer not found');
      case 'EMPTY_ORDER':
        return this.badRequest('Order must have at least one item');
      case 'INSUFFICIENT_INVENTORY':
        return this.conflict(`Insufficient inventory for product ${error.productId}`);
      case 'PAYMENT_FAILED':
        return this.paymentRequired(error.reason as string);
      case 'ORDER_NOT_CANCELLABLE':
        return this.conflict('Order cannot be cancelled in current state');
      default:
        return this.badRequest(`Error: ${error.type}`);
    }
  }

  // ===== Response Helpers =====

  private ok(data: unknown): Response {
    return Response.json(data, { status: 200 });
  }

  private created(data: unknown): Response {
    return Response.json(data, { status: 201 });
  }

  private noContent(): Response {
    return new Response(null, { status: 204 });
  }

  private badRequest(message: string): Response {
    return Response.json({ error: message }, { status: 400 });
  }

  private notFound(message: string): Response {
    return Response.json({ error: message }, { status: 404 });
  }

  private conflict(message: string): Response {
    return Response.json({ error: message }, { status: 409 });
  }

  private paymentRequired(message: string): Response {
    return Response.json({ error: message }, { status: 402 });
  }

  private internalError(error: unknown): Response {
    console.error('Internal error:', error);
    return Response.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
```

## Route Configuration

```typescript
// src/interfaces/http/routes.ts

import type { Container } from '../../config';

export function createRoutes(container: Container) {
  const { orderController, customerController } = container;

  return {
    // Order routes
    '/api/orders': {
      POST: (req: Request) => orderController.create(req),
      GET: (req: Request) => orderController.list(req),
    },
    '/api/orders/:id': {
      GET: (req: Request) => orderController.get(req),
      DELETE: (req: Request) => orderController.cancel(req),
    },

    // Customer routes
    '/api/customers': {
      POST: (req: Request) => customerController.create(req),
      GET: (req: Request) => customerController.list(req),
    },
    '/api/customers/:id': {
      GET: (req: Request) => customerController.get(req),
      PATCH: (req: Request) => customerController.update(req),
    },

    // Health check
    '/health': {
      GET: () => Response.json({ status: 'ok' }),
    },
  };
}
```

## Server Setup (Bun)

```typescript
// src/interfaces/http/index.ts

import { createRoutes } from './routes';
import type { Container } from '../../config';

export function createServer(container: Container) {
  const routes = createRoutes(container);

  return Bun.serve({
    port: process.env.PORT ?? 3000,
    routes,
    development: {
      hmr: true,
      console: true,
    },
    error(error) {
      console.error('Server error:', error);
      return Response.json(
        { error: 'Internal server error' },
        { status: 500 }
      );
    },
  });
}
```

## Testing Controllers

```typescript
// src/interfaces/http/controllers/OrderController.test.ts

import { describe, test, expect, beforeEach } from 'bun:test';
import { OrderController } from './OrderController';
import { FakePlaceOrderUseCase } from '../../../application/use-cases/__fakes__/FakePlaceOrderUseCase';

describe('OrderController', () => {
  let controller: OrderController;
  let placeOrder: FakePlaceOrderUseCase;

  beforeEach(() => {
    placeOrder = new FakePlaceOrderUseCase();
    controller = new OrderController(
      placeOrder,
      /* other use cases */
    );
  });

  describe('POST /api/orders', () => {
    const validBody = {
      customerId: 'customer-123',
      items: [{ productId: 'product-1', quantity: 2 }],
      paymentMethodId: 'pm-123',
    };

    test('returns 201 on success', async () => {
      placeOrder.willReturn({ orderId: 'order-123', total: 100, currency: 'USD' });

      const req = new Request('http://localhost/api/orders', {
        method: 'POST',
        body: JSON.stringify(validBody),
        headers: { 'Content-Type': 'application/json' },
      });

      const res = await controller.create(req);

      expect(res.status).toBe(201);
      const body = await res.json();
      expect(body.orderId).toBe('order-123');
    });

    test('returns 400 when customerId missing', async () => {
      const req = new Request('http://localhost/api/orders', {
        method: 'POST',
        body: JSON.stringify({ ...validBody, customerId: undefined }),
        headers: { 'Content-Type': 'application/json' },
      });

      const res = await controller.create(req);

      expect(res.status).toBe(400);
    });

    test('returns 400 when use case returns CUSTOMER_NOT_FOUND', async () => {
      placeOrder.willReturn({ type: 'CUSTOMER_NOT_FOUND' });

      const req = new Request('http://localhost/api/orders', {
        method: 'POST',
        body: JSON.stringify(validBody),
        headers: { 'Content-Type': 'application/json' },
      });

      const res = await controller.create(req);

      expect(res.status).toBe(400);
    });

    test('returns 402 when payment fails', async () => {
      placeOrder.willReturn({ type: 'PAYMENT_FAILED', reason: 'Card declined' });

      const req = new Request('http://localhost/api/orders', {
        method: 'POST',
        body: JSON.stringify(validBody),
        headers: { 'Content-Type': 'application/json' },
      });

      const res = await controller.create(req);

      expect(res.status).toBe(402);
    });
  });
});
```

## Key Principles

1. **Controllers are thin** - Only handle HTTP concerns
2. **No business logic** - Delegate to use cases
3. **Map errors consistently** - Use case errors → HTTP status codes
4. **Validate request shape** - But not business rules
5. **Catch all errors** - Never leak stack traces
