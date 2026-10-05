# NestJS Module Boundaries

Nest modules create an application graph and encapsulate providers by default. Treat each module's exports as its public API.

## Define modules by capability

Good module names express business ownership: `OrdersModule`, `BillingModule`, `IdentityModule`. Technical modules such as `DatabaseModule` or `ObservabilityModule` are appropriate for shared infrastructure, not as a place to store business behavior.

A module boundary is strong when:

- its purpose can be stated without listing implementation classes;
- it owns related invariants and writes;
- consumers need only a small exported API;
- internal persistence or vendor changes do not ripple through consumers;
- it can be tested through its public operations.

## Export deliberately

```typescript
@Module({
  controllers: [OrdersController],
  providers: [PlaceOrder, OrderRepository],
  exports: [PlaceOrder],
})
export class OrdersModule {}
```

`OrderRepository` remains private. Exporting every provider turns module encapsulation into a folder convention only.

When another module needs order data, choose deliberately:

1. call an exported application operation for current authoritative behavior;
2. consume a domain/integration event for asynchronous reaction;
3. use a dedicated query/read-model API for high-volume cross-capability reads;
4. duplicate derived read data when autonomy is worth the consistency cost.

Do not reach into another feature's ORM repository or tables as the default shortcut.

## Shared and global modules

Use a shared infrastructure module for a stable capability such as logging, configuration, or a database connection. Do not create a generic `SharedModule` that accumulates unrelated services, domain helpers, and DTOs.

Use `@Global()` sparingly. Appropriate candidates are truly application-wide infrastructure registered once. Feature services should usually be imported explicitly so the dependency graph remains visible.

Questions before making a module global:

- Is the capability needed by nearly every module?
- Is there exactly one meaningful instance?
- Would an explicit import communicate important coupling?
- Can tests override it without bootstrapping unrelated behavior?

## Keep the graph acyclic

When `ModuleA` and `ModuleB` import each other, diagnose the ownership problem:

- Behavior belongs entirely to A or B: move it to the owner.
- Both coordinate one workflow: introduce an application coordinator in the owning capability.
- Both react independently: publish an event from the source of truth.
- Both depend on a stable policy: extract that policy, not a grab-bag shared module.
- One direction is read-only: expose a narrow query port.

`forwardRef()` can preserve compatibility during an incremental migration, but record why it exists and how the cycle will be removed. Constructor order must never carry business meaning.

## Composition root

The root module and feature modules assemble implementations. Keep environment and vendor selection at this edge:

```typescript
@Module({
  imports: [ConfigModule],
  providers: [
    PlaceOrder,
    {
      provide: PAYMENT_GATEWAY,
      useFactory: (config: ConfigService) =>
        config.getOrThrow('PAYMENTS_MODE') === 'live'
          ? new StripePaymentGateway(config.getOrThrow('STRIPE_KEY'))
          : new FakePaymentGateway(),
      inject: [ConfigService],
    },
  ],
})
export class OrdersModule {}
```

Business code receives `PAYMENT_GATEWAY`; it does not inspect environment variables or instantiate vendor clients.

## Boundary checklist

- [ ] Module name represents one cohesive capability or infrastructure concern.
- [ ] Exports are smaller than internal providers.
- [ ] Write ownership is unambiguous.
- [ ] Cross-module calls use public operations, ports, or events.
- [ ] No feature imports another feature's ORM repository.
- [ ] Global modules are rare and justified.
- [ ] Import graph is acyclic, or temporary cycles have a removal plan.
- [ ] Transport and persistence details stay at the edge of layered features.

See the official [NestJS modules documentation](https://docs.nestjs.com/modules) for framework semantics.
