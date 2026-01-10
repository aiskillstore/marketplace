# TypeScript Hexagonal Scaffold

## Complete Folder Structure

```
src/
├── domain/
│   ├── entities/
│   │   ├── [EntityName].ts
│   │   └── index.ts
│   ├── value-objects/
│   │   ├── [ValueObjectName].ts
│   │   └── index.ts
│   ├── events/
│   │   ├── [DomainEvent].ts
│   │   └── index.ts
│   ├── errors/
│   │   ├── [DomainError].ts
│   │   └── index.ts
│   └── index.ts
│
├── application/
│   ├── ports/
│   │   ├── inbound/
│   │   │   ├── [UseCase].ts
│   │   │   └── index.ts
│   │   └── outbound/
│   │       ├── [Repository].ts
│   │       ├── [Gateway].ts
│   │       └── index.ts
│   ├── use-cases/
│   │   ├── [UseCaseName]/
│   │   │   ├── [UseCaseName].ts
│   │   │   ├── [UseCaseName].test.ts
│   │   │   └── index.ts
│   │   └── index.ts
│   └── index.ts
│
├── infrastructure/
│   ├── persistence/
│   │   ├── [Repository]Impl.ts
│   │   ├── mappers/
│   │   │   └── [EntityMapper].ts
│   │   └── index.ts
│   ├── external/
│   │   ├── [GatewayName]/
│   │   │   └── [GatewayName]Impl.ts
│   │   └── index.ts
│   └── index.ts
│
├── interfaces/
│   ├── http/
│   │   ├── routes.ts
│   │   ├── controllers/
│   │   │   └── [Controller].ts
│   │   └── index.ts
│   └── index.ts
│
├── shared/
│   ├── types/
│   │   └── index.ts
│   └── utils/
│       └── index.ts
│
├── config/
│   └── index.ts
│
└── main.ts
```

## Layer Dependencies

```typescript
// domain/ - NO imports from other src/ directories
// Only standard library and pure utilities

// application/ - Can import from domain/
import { Order } from '../domain/entities';

// infrastructure/ - Can import from domain/ and application/
import { Order } from '../domain/entities';
import { OrderRepository } from '../application/ports/outbound';

// interfaces/ - Can import from application/ (and domain/ for types)
import { PlaceOrderUseCase } from '../application/ports/inbound';
```

## Main Entry Point

```typescript
// src/main.ts
import { createServer } from './interfaces/http';
import { createContainer } from './config';

async function main() {
  // Composition root - wire all dependencies
  const container = createContainer();

  // Start server with injected dependencies
  const server = createServer(container);

  server.listen(3000, () => {
    console.log('Server running on port 3000');
  });
}

main().catch(console.error);
```

## Dependency Injection Setup

```typescript
// src/config/index.ts
import { PlaceOrderUseCase } from '../application/use-cases/PlaceOrder';
import { PostgresOrderRepository } from '../infrastructure/persistence/PostgresOrderRepository';
import { StripePaymentGateway } from '../infrastructure/external/stripe/StripePaymentGateway';
import { OrderController } from '../interfaces/http/controllers/OrderController';

export interface Container {
  // Ports (interfaces)
  orderRepository: OrderRepository;
  paymentGateway: PaymentGateway;

  // Use cases
  placeOrderUseCase: PlaceOrderUseCase;

  // Controllers
  orderController: OrderController;
}

export function createContainer(): Container {
  // Create driven adapters (outbound)
  const orderRepository = new PostgresOrderRepository(/* db config */);
  const paymentGateway = new StripePaymentGateway(/* stripe config */);

  // Create use cases
  const placeOrderUseCase = new PlaceOrderUseCase(
    orderRepository,
    paymentGateway
  );

  // Create driving adapters (inbound)
  const orderController = new OrderController(placeOrderUseCase);

  return {
    orderRepository,
    paymentGateway,
    placeOrderUseCase,
    orderController,
  };
}
```

## Index File Pattern

Each directory exports its contents cleanly:

```typescript
// src/domain/entities/index.ts
export { Order } from './Order';
export { OrderItem } from './OrderItem';
export { Customer } from './Customer';

// src/domain/index.ts
export * from './entities';
export * from './value-objects';
export * from './events';
export * from './errors';
```

## Bun-Specific Server Setup

```typescript
// src/interfaces/http/routes.ts
import type { Container } from '../../config';

export function createRoutes(container: Container) {
  return {
    '/api/orders': {
      POST: (req: Request) => container.orderController.create(req),
      GET: (req: Request) => container.orderController.list(req),
    },
    '/api/orders/:id': {
      GET: (req: Request) => container.orderController.get(req),
      DELETE: (req: Request) => container.orderController.cancel(req),
    },
  };
}

// src/interfaces/http/index.ts
import { createRoutes } from './routes';
import type { Container } from '../../config';

export function createServer(container: Container) {
  const routes = createRoutes(container);

  return Bun.serve({
    routes,
    development: {
      hmr: true,
    },
  });
}
```

## Test Structure

```
src/
├── domain/
│   └── entities/
│       ├── Order.ts
│       └── Order.test.ts      # Unit test - no mocks needed
│
├── application/
│   └── use-cases/
│       └── PlaceOrder/
│           ├── PlaceOrder.ts
│           └── PlaceOrder.test.ts  # Unit test - mock ports
│
├── infrastructure/
│   └── persistence/
│       ├── PostgresOrderRepository.ts
│       └── PostgresOrderRepository.test.ts  # Integration test
│
└── interfaces/
    └── http/
        └── controllers/
            ├── OrderController.ts
            └── OrderController.test.ts  # Integration test
```
