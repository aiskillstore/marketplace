# NestJS Feature Selection

Put a concern where its required context and lifecycle semantics exist.

## Responsibility matrix

| Feature | Appropriate responsibility | Common misuse |
| --- | --- | --- |
| Module | Encapsulation, provider wiring, public exports | One global module exporting everything |
| Provider | Application/domain/infrastructure behavior | Request state stored in a singleton field |
| Middleware | Raw request preprocessing, correlation IDs | Route authorization or business validation |
| Guard | Authentication/authorization decision | Response mapping or business transaction |
| Pipe | Validate/transform handler arguments | Database writes or external calls |
| Interceptor | Wrap execution, trace, time, map compatible responses | Hidden feature policy in a global interceptor |
| Exception filter | Map uncaught failures to a transport response | Swallowing errors or retrying business operations |
| Param decorator | Extract established request context | Performing I/O or authorization secretly |
| Controller/resolver | Adapt transport to an application operation | Owning invariants or querying several repositories |
| Event | Notify independent reactions to a completed fact | Request/response operation requiring an immediate result |
| Queue | Durable/deferred/bursty work | Hiding a required synchronous result |
| Scheduler | Time-triggered orchestration | Running once per replica unintentionally |
| Lifecycle hook | Start/stop managed resources | Starting untracked work without shutdown behavior |

## Binding scope

Choose the narrowest level that represents the policy:

- Global: an invariant for every matching request, such as baseline validation or tracing.
- Controller: a policy shared by all routes in one transport adapter.
- Route: behavior unique to one operation.
- Parameter: transformation/validation of one value.

Global components increase blast radius. Test ordering and error behavior before changing one.

When dependency injection is needed globally, register the component through Nest's provider mechanism (for example `APP_GUARD`, `APP_PIPE`, `APP_INTERCEPTOR`, or `APP_FILTER`) instead of constructing it manually outside the container.

## Authentication and authorization

Authentication establishes a principal. Authorization decides whether that principal can perform the operation on the target resource.

Typical split:

1. strategy/middleware/guard validates credentials and establishes a typed principal;
2. metadata declares coarse route policy when useful;
3. guard or application policy enforces authorization;
4. application/repository queries remain tenant/owner scoped as defense in depth.

Do not rely on a valid token as proof the user owns a requested resource.

## Validation

Validate untrusted transport data with DTO/schema tooling at the boundary. Use explicit transformation and reject unknown fields when the public contract requires it.

Validation proves shape and basic constraints. Domain construction still enforces business invariants and current-state rules.

## Cross-cutting behavior

Use interceptors for concerns that truly wrap many handlers: trace spans, request duration, response envelope mapping, compatible cache integration. Keep authorization in guards and argument conversion in pipes so order remains understandable.

Errors thrown by pipes, handlers, or providers skip to exception handling. Avoid duplicated error mapping in every controller.

## Events, queues, and schedules

- In-process event: fast, non-durable, same process only.
- Durable queue/broker: persisted work across processes; duplicates and reordering may occur.
- Scheduler: a trigger, not a distributed lock. Multiple replicas can execute the same schedule.

For scheduled work in a replicated deployment, choose one:

- platform scheduler invokes an idempotent endpoint/job;
- dedicated scheduler deployment with one replica;
- distributed lock with lease/expiry and observable ownership;
- enqueue a uniquely keyed job and let queue deduplication serialize it.

## Lifecycle hooks

Use initialization hooks for async setup that must finish before readiness. Enable shutdown hooks when the process must receive termination signals through Nest. Close servers, consumers, pools, and telemetry in a known order.

Request-scoped providers do not receive lifecycle hooks; do not depend on them for resource cleanup.

## Request lifecycle review

For HTTP, verify the effective order of:

1. global and module middleware;
2. global, controller, and route guards;
3. global, controller, and route interceptors on entry;
4. global, controller, route, and parameter pipes;
5. handler and providers;
6. route, controller, and global interceptors on return;
7. route, controller, and global filters for uncaught exceptions.

See the official [request lifecycle](https://docs.nestjs.com/faq/request-lifecycle) and [lifecycle events](https://docs.nestjs.com/fundamentals/lifecycle-events) documentation.
