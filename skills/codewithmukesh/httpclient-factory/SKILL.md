---
name: httpclient-factory
description: >
  IHttpClientFactory and typed HTTP clients for .NET 10 applications. Covers
  named/typed/keyed clients, DelegatingHandlers, resilience with
  Microsoft.Extensions.Http.Resilience, and testing patterns.
  Load this skill when configuring HTTP clients, adding retry/circuit breaker
  policies, or when the user mentions "HttpClient", "IHttpClientFactory",
  "AddHttpClient", "typed client", "named client", "DelegatingHandler",
  "resilience", "retry", "circuit breaker", "hedging", "Polly",
  "AddStandardResilienceHandler", "socket exhaustion", or "Refit".
---

# HttpClient Factory

## Core Principles

1. **Never `new HttpClient()` per request** — Raw `HttpClient` creation causes socket exhaustion under load and ignores DNS changes. Use `IHttpClientFactory` to manage handler lifetimes.
2. **Keyed clients over typed clients** — Keyed DI (`.AddAsKeyed()`) is the recommended pattern in .NET 10. Typed clients captured in singletons silently break handler rotation.
3. **Resilience is not optional** — Every external HTTP call needs retry, circuit breaker, and timeout. `AddStandardResilienceHandler()` provides sensible defaults in one line.
4. **DelegatingHandlers for cross-cutting concerns** — Auth tokens, correlation IDs, and logging belong in the handler pipeline, not scattered across service methods.

## Patterns

### Named Client with Resilience

```csharp
builder.Services.AddHttpClient("github", client =>
{
    client.BaseAddress = new Uri("https://api.github.com/");
    client.DefaultRequestHeaders.UserAgent.ParseAdd("MyApp/1.0");
    client.DefaultRequestHeaders.Accept.Add(
        new MediaTypeWithQualityHeaderValue("application/json"));
})
.AddStandardResilienceHandler();

// Usage via factory
public sealed class GitHubService(IHttpClientFactory factory)
{
    public async Task<Repo?> GetRepoAsync(string owner, string name, CancellationToken ct)
    {
        var client = factory.CreateClient("github");
        return await client.GetFromJsonAsync<Repo>($"repos/{owner}/{name}", ct);
    }
}
```

### Keyed Client (Recommended in .NET 10)

Combines named client configurability with direct injection. No string lookups.

```csharp
builder.Services.AddHttpClient("payments", client =>
{
    client.BaseAddress = new Uri("https://api.payments.example.com/");
})
.AddStandardResilienceHandler()
.AddAsKeyed();  // Register as keyed scoped service

// Inject directly — no IHttpClientFactory needed
app.MapPost("/charge", async (
    [FromKeyedServices("payments")] HttpClient httpClient,
    ChargeRequest request,
    CancellationToken ct) =>
{
    var response = await httpClient.PostAsJsonAsync("charges", request, ct);
    return response.IsSuccessStatusCode
        ? TypedResults.Ok()
        : TypedResults.Problem("Payment failed");
});
```

Global opt-in: `builder.Services.ConfigureHttpClientDefaults(b => b.AddAsKeyed());`

### Standard Resilience Handler

`AddStandardResilienceHandler()` chains 5 strategies:

| Strategy | Default |
|----------|---------|
| Rate limiter | 1000 concurrent requests |
| Total timeout | 30 seconds |
| Retry | 3 retries, exponential backoff with jitter |
| Circuit breaker | Opens at 10% failure rate |
| Attempt timeout | 10 seconds per attempt |

```csharp
builder.Services.AddHttpClient("api")
    .AddStandardResilienceHandler(options =>
    {
        options.Retry.MaxRetryAttempts = 5;
        options.Retry.Delay = TimeSpan.FromSeconds(1);
        options.TotalRequestTimeout.Timeout = TimeSpan.FromSeconds(60);
        options.AttemptTimeout.Timeout = TimeSpan.FromSeconds(15);

        // Disable retries for non-idempotent methods
        options.Retry.DisableForUnsafeHttpMethods();
    });
```

### DelegatingHandler for Auth Token Injection

```csharp
public sealed class AuthenticationHandler(ITokenService tokenService)
    : DelegatingHandler
{
    protected override async Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request, CancellationToken cancellationToken)
    {
        var token = await tokenService.GetAccessTokenAsync(cancellationToken);
        request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);
        return await base.SendAsync(request, cancellationToken);
    }
}

// Registration
builder.Services.AddTransient<AuthenticationHandler>();
builder.Services.AddHttpClient("api")
    .AddHttpMessageHandler<AuthenticationHandler>()
    .AddStandardResilienceHandler();
```

### DelegatingHandler for Correlation ID Propagation

```csharp
public sealed class CorrelationIdHandler(IHttpContextAccessor httpContextAccessor)
    : DelegatingHandler
{
    protected override Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request, CancellationToken cancellationToken)
    {
        if (httpContextAccessor.HttpContext?.Request.Headers
                .TryGetValue("X-Correlation-Id", out var correlationId) is true)
        {
            request.Headers.Add("X-Correlation-Id", correlationId.ToString());
        }
        return base.SendAsync(request, cancellationToken);
    }
}
```

### SocketsHttpHandler Configuration

```csharp
builder.Services.AddHttpClient("advanced")
    .UseSocketsHttpHandler((handler, _) =>
    {
        handler.PooledConnectionLifetime = TimeSpan.FromMinutes(2);
        handler.PooledConnectionIdleTimeout = TimeSpan.FromMinutes(1);
        handler.MaxConnectionsPerServer = 100;
        handler.AutomaticDecompression =
            DecompressionMethods.GZip | DecompressionMethods.Brotli;
    });
```

### Testing with Mock Handler

```csharp
public sealed class MockHttpHandler(
    HttpStatusCode statusCode,
    string content) : HttpMessageHandler
{
    protected override Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request, CancellationToken cancellationToken)
    {
        return Task.FromResult(new HttpResponseMessage(statusCode)
        {
            Content = new StringContent(content, Encoding.UTF8, "application/json")
        });
    }
}

// In test
var handler = new MockHttpHandler(HttpStatusCode.OK, """{"id":1}""");
var client = new HttpClient(handler) { BaseAddress = new Uri("https://api.test/") };
var service = new MyService(client);
```

## Anti-patterns

### Don't Create HttpClient Per Request

```csharp
// BAD — socket exhaustion under load, ignores DNS changes
public async Task<string> GetDataAsync()
{
    using var client = new HttpClient();
    return await client.GetStringAsync("https://api.example.com/data");
}

// GOOD — factory-managed
public async Task<string> GetDataAsync(CancellationToken ct)
{
    var client = factory.CreateClient("api");
    return await client.GetStringAsync("https://api.example.com/data", ct);
}
```

### Don't Capture Typed Clients in Singletons

```csharp
// BAD — transient HttpClient captured by singleton defeats handler rotation
services.AddSingleton<MySingletonService>();
services.AddHttpClient<MySingletonService>();

// GOOD — use keyed client or IHttpClientFactory in singletons
services.AddSingleton<MySingletonService>();
services.AddHttpClient("myservice").AddAsKeyed(ServiceLifetime.Singleton);
```

### Don't Mutate DefaultRequestHeaders on Shared Clients

```csharp
// BAD — not thread-safe
httpClient.DefaultRequestHeaders.Authorization =
    new AuthenticationHeaderValue("Bearer", token);

// GOOD — use DelegatingHandler or per-request HttpRequestMessage
using var request = new HttpRequestMessage(HttpMethod.Get, "/api/data");
request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);
await httpClient.SendAsync(request, ct);
```

### Don't Forget CancellationToken

```csharp
// BAD — no cancellation support
var result = await httpClient.GetFromJsonAsync<Order>("/orders/1");

// GOOD — always pass CancellationToken
var result = await httpClient.GetFromJsonAsync<Order>("/orders/1", cancellationToken);
```

### Don't Stack Multiple Resilience Handlers

```csharp
// BAD — conflicting resilience strategies
builder.AddStandardResilienceHandler();
builder.AddStandardHedgingHandler();

// GOOD — one standard handler, or a custom pipeline
builder.AddStandardResilienceHandler();
```

## Decision Guide

| Scenario | Recommendation |
|----------|---------------|
| New .NET 10 project | Keyed clients with `AddAsKeyed()` |
| Singleton service needs HttpClient | Named client via `IHttpClientFactory` or keyed singleton |
| External API calls | `AddStandardResilienceHandler()` on every client |
| Auth token injection | `DelegatingHandler` registered with `AddHttpMessageHandler` |
| Hedging (parallel requests) | `AddStandardHedgingHandler()` for latency-sensitive calls |
| Non-idempotent methods | `DisableForUnsafeHttpMethods()` on retry options |
| Custom retry logic | `AddResilienceHandler("name", builder => ...)` |
| Connection pooling control | `UseSocketsHttpHandler` with `PooledConnectionLifetime` |
| API client generation | Refit with `AddRefitClient<T>()` |
| Integration testing | Custom `HttpMessageHandler` or `MockHttpMessageHandler` |
