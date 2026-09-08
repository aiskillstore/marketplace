# SDK selection and framework wiring

## Table of contents

- [Package matrix](#package-matrix)
- [Client construction per language](#client-construction-per-language)
- [Configuration and environment variables](#configuration-and-environment-variables)
- [Framework wiring](#framework-wiring)
- [Background processing per ecosystem](#background-processing-per-ecosystem)
- [Multi-tenant credential patterns](#multi-tenant-credential-patterns)
- [Testing and mocking](#testing-and-mocking)
- [Deployment notes](#deployment-notes)

## Package matrix

| Language | Package | Install | Minimum runtime |
| --- | --- | --- | --- |
| TypeScript | `@sentdm/sentdm` | `npm install @sentdm/sentdm` | Node with ESM or CJS |
| Python | `sentdm` (imports as `sent_dm`) | `pip install sentdm` | Python 3.9 |
| Go | `github.com/sentdm/sent-dm-go` | `go get github.com/sentdm/sent-dm-go` | Go 1.22 |
| Java | `dm.sent:sent-java` | Maven or Gradle dependency | Java 8 |
| C# | `Sentdm` | `dotnet add package Sentdm` | .NET Standard 2.0 |
| PHP | `sentdm/sent-dm-php` | `composer require sentdm/sent-dm-php` | PHP 8.1 |
| Ruby | `sentdm` | `gem install sentdm` or Bundler | Ruby 3.2 |

The distribution name and the import name differ in Python (`sentdm` installs, `sent_dm` imports) and the Ruby send method is `messages.send_` with a trailing underscore because `send` is reserved. Both are common first-hour errors.

No SDK ships a webhook signature verifier in any language. That code is always application-owned.

## Client construction per language

```typescript
import SentDm from '@sentdm/sentdm';

// Reads SENT_DM_API_KEY. Options: apiKey, baseUrl, maxRetries, timeout, logLevel.
export const sent = new SentDm({ maxRetries: 3, timeout: 30_000 });

const response = await sent.messages.send({
  to: ['+14155551234'],
  template: { name: 'order_confirmation', parameters: { order_id: '12345' } },
});
```

```python
from sent_dm import Sent, AsyncSent

client = Sent(max_retries=2, timeout=60.0)      # reads SENT_DM_API_KEY
async_client = AsyncSent()

response = client.messages.send(
    to=["+14155551234"],
    template={"name": "order_confirmation", "parameters": {"order_id": "12345"}},
)
```

```go
client := sentdm.NewClient()                     // or option.WithAPIKey(...)
response, err := client.Messages.Send(ctx, sentdm.MessageSendParams{
    To: []string{"+14155551234"},
})
```

```java
SentClient client = SentOkHttpClient.fromEnv();  // SENT_DM_API_KEY or sent.dmApiKey
MessageSendResponse response = client.messages().send(params);
```

```csharp
using Sentdm;
SentClient client = new();                       // reads SENT_DM_API_KEY
var response = await client.Messages.Send(body);
```

```php
use SentDm\Client;
$client = new Client($_ENV['SENT_DM_API_KEY']);  // key is an explicit constructor argument
$result = $client->messages->send(to: ['+14155551234'], template: ['name' => 'order_confirmation']);
```

```ruby
require "sentdm"
client = Sentdm::Client.new                      # reads SENT_DM_API_KEY
client.messages.send_(to: ["+14155551234"], template: { name: "order_confirmation" })
```

Java and C# expose both synchronous and asynchronous clients; Python offers `Sent` and `AsyncSent`; TypeScript and C# are promise- or task-based only; Go and PHP and Ruby are synchronous, with Go carrying a `context.Context` on every call.

## Configuration and environment variables

| Variable | Purpose | Read automatically |
| --- | --- | --- |
| `SENT_DM_API_KEY` | REST credential sent as `x-api-key` | Yes, in every SDK except PHP |
| `SENT_DM_WEBHOOK_SECRET` | `whsec_`-prefixed webhook signing secret | No; application code reads it |
| `SENT_BASE_URL` | Override the API base URL | Java and C# read it; others take a constructor option |

Older documentation pages use `SENT_API_KEY` and `SENT_WEBHOOK_SECRET`. Both name sets appear in official material; standardize new code on the `SENT_DM_` names because the SDK defaults use them, and accept the shorter names as aliases when adopting existing code.

For a single-account service, validate the server-managed key at startup with the ecosystem's schema tooling — `zod` in Node, `pydantic-settings` in Python, `@nestjs/config`, `IOptions` with `[Required]` in .NET — so a missing key fails the deployment rather than the first customer send. For a multi-tenant proxy, validate non-secret configuration at startup and reject each request whose resolved credential is absent or malformed.

## Framework wiring

| Framework | Client placement | Webhook raw body |
| --- | --- | --- |
| Next.js | Shared module such as `lib/sent/client.ts` | `await request.text()`; keep the route on the Node runtime |
| Express | Module singleton | `express.raw({ type: 'application/json' })` scoped to the webhook path |
| NestJS | Provider in a `SentModule` | `req.rawBody` with `NestFactory.create(AppModule, { rawBody: true })` |
| FastAPI | Client built in the lifespan, injected as a dependency | `await request.body()` |
| Django | `@lru_cache` factory in a `client.py` | `request.body` |
| Flask | Cached on the app or request context | `request.get_data()` |
| Gin / Echo | Constructed in `main`, passed to handlers | `io.ReadAll(c.Request.Body)` |
| Spring Boot | `@Bean` in a configuration class | `@RequestBody String payload` |
| Laravel | Singleton in the service container | `$request->getContent()` in middleware |
| Symfony | Autowired service | `$request->getContent()` |
| Rails | Memoized in an initializer | `request.body.read` then `request.body.rewind` |
| Sinatra | Memoized module method | `request.body.read` then `request.body.rewind` |
| ASP.NET Core | Singleton via dependency injection | `new StreamReader(request.Body).ReadToEndAsync()` |

The recurring defect is a global JSON body parser that destroys the byte-exact body needed for signature verification. Scope the parser away from the webhook path, or read the raw bytes before any parsing occurs.

A minimal integration is four files regardless of stack: a client module, an outbound send route, an inbound webhook route, and a signature-verification helper.

## Background processing per ecosystem

Webhook handlers must acknowledge with `200` and then work asynchronously, because ten consecutive failed deliveries disable the endpoint and a slow handler manufactures those failures.

| Ecosystem | Mechanism |
| --- | --- |
| Node | BullMQ or an equivalent durable queue |
| Python | Celery or another durable queue; reserve FastAPI `BackgroundTasks` for non-critical local work |
| Go | A bounded worker pool or a job queue |
| Java | `@Async` with a `ThreadPoolTaskExecutor`, or a broker |
| PHP | Laravel queued jobs, Symfony Messenger |
| Ruby | ActiveJob or Sidekiq |
| .NET | A `BackgroundService` consuming a channel or queue |

Route bulk campaign traffic to a queue separate from transactional sends so a large campaign cannot starve time-sensitive messages, and set worker concurrency or a task rate limit that respects the 200-requests-per-minute budget.

## Multi-tenant credential patterns

Two patterns exist, and mixing them causes confusing `403` responses.

A **profile-scoped key** is confined to one profile, has its own rate-limit pool, and must not send `x-profile-id` — doing so returns `403`. Prefer it for runtime send paths so a leaked key affects one tenant.

An **organization key with `x-profile-id`** reaches permitted child profiles but draws on the organization's shared rate-limit pool, so one noisy tenant consumes everyone's quota. Prefer it for control-plane work such as provisioning.

When each tenant supplies its own key, resolve it for the request, construct the client with that credential, and discard both afterward. Do not retain tenant credentials in a client cache merely to preserve connection pooling; isolation and rotation correctness take priority. Queued work must resolve the authorized tenant credential just in time from a secret store rather than embedding it in the job payload. Never place a key in a browser, mobile app, or any client the organization does not control, and keep separate keys per environment. `x-sender-id` is legacy v1 and v2 terminology with no role in v3.

## Testing and mocking

Use `"sandbox": true` for integration tests: authentication and validation still run, so a malformed request still returns `400` or `422`, but nothing is written, queued, charged, or dispatched to a provider. It is the right default in continuous integration.

For unit tests, mock at the SDK boundary — `jest.fn()` on `messages.send`, a NestJS testing module override, a substituted `ISentClient` in .NET — and assert on the request payload rather than on transport behavior. For the receiver, generate valid headers locally with the webhook skill's signing script so tests cover the signature path without contacting Sent.

Two notes on live verification. `POST /v3/webhooks/{id}/test` delivers exactly once with no retry, so re-run it after each fix. And `DELETE /v3/webhooks/{id}` ignores `sandbox` and always deletes, so never treat the flag as a dry-run guard for deletion.

## Deployment notes

Keep webhook routes on runtimes that expose Node-style crypto and raw bodies rather than on edge runtimes. Close the HTTP server gracefully on `SIGTERM` so in-flight deliveries finish instead of failing and triggering retries. Ensure load balancer idle timeouts exceed the configured `timeout_seconds`, and keep container clocks NTP-synchronized so the 300-second replay window does not reject valid traffic. Keep the route outside user-auth middleware. If abuse controls are required, make them signature-aware and capacity-safe rather than placing a generic limiter in front of verification and manufacturing the failures that lead to auto-disable.
