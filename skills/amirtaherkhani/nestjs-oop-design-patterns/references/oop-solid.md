# OOP and SOLID in NestJS

## Encapsulation

Encapsulation protects behavior and invariants, not merely fields.

```typescript
class Order {
  private status: 'draft' | 'confirmed' = 'draft';

  confirm() {
    if (this.status !== 'draft') {
      throw new OrderAlreadyConfirmed();
    }
    this.status = 'confirmed';
  }
}
```

A public `setStatus(value: string)` exposes the invariant and is weaker even if the field remains private.

Use immutable objects for values and messages when practical. Entities can be mutable inside a controlled transaction, but mutations should be named business operations.

## Abstraction

An abstraction should hide a decision likely to change or a boundary worth testing. Good abstractions have a small vocabulary grounded in the consumer's need.

```typescript
interface Clock {
  now(): Date;
}
```

Avoid a wrapper that reproduces an entire third-party SDK method for method. It adds a layer but hides no meaningful decision.

## Composition over inheritance

Prefer collaborating policies:

```typescript
@Injectable()
class ShippingQuoteService {
  constructor(
    @Inject(SHIPPING_POLICY)
    private readonly policy: ShippingPolicy,
  ) {}
}
```

Inheritance is appropriate when subtypes have a genuine is-a relationship, share a stable contract, and remain substitutable. Framework base classes or templates can be valid; feature services rarely need a generic base CRUD class.

Warning signs in inheritance:

- subclasses override methods to throw "unsupported";
- callers inspect subtype names;
- protected mutable state coordinates behavior;
- base changes break unrelated features;
- decorators/metadata are assumed to inherit in ways the framework does not guarantee.

## Polymorphism

Use polymorphism for real variation:

```typescript
interface PricingPolicy {
  calculate(order: PricedOrder): Money;
}

class StandardPricing implements PricingPolicy { /* ... */ }
class PartnerPricing implements PricingPolicy { /* ... */ }
```

Keep the selection at the composition root or a focused factory. Avoid selecting a strategy from unvalidated user input.

## Single Responsibility Principle

Define responsibility as a cohesive policy or reason to change, not one method.

A `PlaceOrder` use case may load an order, enforce a policy, authorize payment, save, and publish an event. Its single responsibility is coordinating order placement. Persistence mapping and payment SDK calls belong elsewhere because they change for different reasons.

Split when:

- unrelated actors request changes;
- dependencies cluster into separate groups;
- tests require unrelated setup;
- state or lifecycle differs;
- part of the behavior has a clearer domain owner.

## Open/Closed Principle

First implement the direct case. When repeated changes reveal a stable operation with varying behavior, extract the variation.

```typescript
const TAX_POLICIES = new Map<Region, TaxPolicy>([
  ['eu', euTaxPolicy],
  ['us', usTaxPolicy],
]);
```

Do not replace a small stable conditional with a class hierarchy solely to avoid modifying a file.

## Liskov Substitution Principle

A subtype/implementation must preserve the contract:

- accepted inputs and preconditions;
- returned meaning and postconditions;
- error categories;
- side effects and idempotency;
- ordering and consistency expectations.

If `CachedOrderRepository.save()` silently drops writes when the cache is unavailable, it is not substitutable for `OrderRepository` even if the TypeScript signatures match.

## Interface Segregation Principle

Design ports from consumer use:

```typescript
interface FindOrder {
  byId(id: OrderId): Promise<Order | null>;
}

interface SaveOrder {
  save(order: Order): Promise<void>;
}
```

Separate read/write ports when consumers and semantics differ. Do not fragment an interface if every consumer always needs the same cohesive operations.

## Dependency Inversion Principle

The application defines what it needs; infrastructure implements it.

```text
PlaceOrder -> PaymentGateway <- StripePaymentGateway
```

Nest module wiring points from the outer adapter to the application-owned token. Domain/application source code never imports Stripe.

## OOP checklist

- [ ] Business mutations are named and preserve invariants.
- [ ] Public surface is smaller than internal representation.
- [ ] Composition is preferred unless substitution is proven.
- [ ] Abstractions correspond to real variation or boundaries.
- [ ] Implementations honor behavioral contracts, not only types.
- [ ] Constructor dependencies reveal collaboration clearly.
- [ ] Nest/ORM/vendor concerns remain at appropriate edges.
