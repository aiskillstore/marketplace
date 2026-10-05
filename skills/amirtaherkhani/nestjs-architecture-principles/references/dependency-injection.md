# Dependency Injection and Ports

Use Nest's container as the composition mechanism. Dependency inversion is about source-code direction and ownership, not the number of interfaces.

## Choose a provider form intentionally

| Provider form | Use when |
| --- | --- |
| Class provider | One concrete implementation is the local default |
| `useValue` | Supplying configuration, a constant, or a test double |
| `useClass` | Selecting an implementation behind a stable token |
| `useExisting` | Providing an alias to the same singleton instance |
| `useFactory` | Construction depends on runtime configuration or other providers |

TypeScript interfaces do not exist at runtime, so they cannot be constructor tokens by themselves. Prefer a named `Symbol` for an application-owned port:

```typescript
export const PAYMENT_GATEWAY = Symbol('orders.payment-gateway');

export interface PaymentGateway {
  authorize(input: AuthorizePayment): Promise<Authorization>;
}

@Injectable()
export class PlaceOrder {
  constructor(
    @Inject(PAYMENT_GATEWAY)
    private readonly payments: PaymentGateway,
  ) {}
}
```

Register the adapter at the composition root:

```typescript
{
  provide: PAYMENT_GATEWAY,
  useClass: StripePaymentGateway,
}
```

An abstract class can be a runtime token, but it couples the port to a class hierarchy. Use it when the repository already follows that convention or shared behavior genuinely belongs in the base class; otherwise a `Symbol` plus interface is clearer.

## Ports belong to consumers

Place the port next to the application operation that needs it, not next to the vendor adapter. Name it by the capability it provides (`PaymentGateway`, `OrderStore`, `Clock`), not the current implementation (`StripeServiceInterface`).

Create a port when at least one is true:

- the edge is external or volatile;
- tests need a valuable deterministic seam;
- multiple implementations are real or planned by a known requirement;
- the dependency crosses an architectural boundary.

Do not add interfaces to pure local helpers only to satisfy a rule. An interface with one implementation and no boundary can increase navigation cost without reducing coupling.

## Keep contracts substitutable and consumer-shaped

Interface Segregation and Liskov Substitution apply to injected contracts, but they are object-design tests rather than reasons to create more tokens:

- expose only the operations a consumer needs instead of one broad `CommonService` or generic repository;
- make every implementation honor the same inputs, outputs, error categories, side effects, and lifetime assumptions;
- do not register a test double or alternate adapter that accepts states the production implementation rejects;
- split a contract when implementations need incompatible preconditions or semantics;
- prefer composition when a class hierarchy cannot preserve the contract.

Use the OOP and Design Patterns skill when the main question is collaborator behavior or substitutability; this reference owns Nest runtime tokens and composition.

## Scope rules

Default singleton scope is correct for most providers. A singleton must not store request-specific mutable state.

Use request scope only when the object truly has request lifetime and simpler context propagation is insufficient. Request scope bubbles up the dependency graph, causes dependent controllers/providers to be recreated, and adds latency and allocation pressure.

Before request scope, consider:

- passing explicit context to the application operation;
- an existing AsyncLocalStorage-based request context;
- extracting tenant/user data in a guard or decorator and passing a typed principal;
- keeping database connections pooled and selecting tenant/schema per operation.

Transient scope is useful when each consumer needs independent mutable state. It is not a general safety setting.

## Dynamic modules

Use a dynamic module for reusable infrastructure that consumers configure, especially a library with `register`/`registerAsync` or `forRoot`/`forRootAsync` APIs. Prefer Nest's `ConfigurableModuleBuilder` when it reduces repetitive wiring.

Do not turn ordinary feature modules into dynamic modules merely to pass business settings. Feature configuration should normally enter through validated configuration providers or explicit application inputs.

## Avoid service location

Constructor injection makes dependencies visible and testable. `ModuleRef.get()` or runtime discovery is appropriate for framework extensions, plugin systems, and lifecycle-sensitive lookups—not as a way to avoid declaring dependencies.

## Cycle repair

When two providers inject each other:

1. identify which behavior owns the workflow;
2. extract a coordinator or policy if a third responsibility exists;
3. replace the reverse synchronous call with an event if immediate consistency is not required;
4. expose a narrower query port if one side only reads;
5. use `forwardRef()` only as a documented transition or unavoidable framework integration.

## Test the wiring

- Unit-test application operations with hand-written fakes or provider overrides.
- Add a module compilation test for custom tokens and dynamic configuration.
- Use an integration/e2e test to prove the real adapter is wired at the boundary.
- Fail application startup when required configuration cannot construct a provider safely.

See the official NestJS documentation for [custom providers](https://docs.nestjs.com/fundamentals/custom-providers), [injection scopes](https://docs.nestjs.com/fundamentals/injection-scopes), [dynamic modules](https://docs.nestjs.com/fundamentals/dynamic-modules), and [circular dependencies](https://docs.nestjs.com/fundamentals/circular-dependency).
