# Redis Recipe — C# (.NET) — REFERENCE ONLY

## ASP.NET Core Distributed Cache Setup

### NuGet Packages

```xml
<PackageReference Include="Microsoft.Extensions.Caching.StackExchangeRedis" Version="8.0.*" />
<PackageReference Include="Azure.Identity" Version="1.13.*" />
```

### Program.cs (additions)

Add these lines — do NOT replace the existing file:

```csharp
using Azure.Identity;
using StackExchange.Redis;

var redisHost = builder.Configuration["REDIS_HOST"];
var configOptions = ConfigurationOptions.Parse($"{redisHost}:6380");
configOptions.Ssl = true;
configOptions.AbortOnConnectFail = false;

// ConfigureForAzureWithTokenCredentialAsync handles automatic token renewal
await configOptions.ConfigureForAzureWithTokenCredentialAsync(
    new DefaultAzureCredential());

builder.Services.AddStackExchangeRedisCache(options =>
{
    options.ConfigurationOptions = configOptions;
    options.InstanceName = "app:";
});
```

> 💡 `ConfigureForAzureWithTokenCredentialAsync` manages token acquisition and renewal automatically — no manual token refresh required.

### Usage

```csharp
using Microsoft.Extensions.Caching.Distributed;

app.MapGet("/api/cached", async (IDistributedCache cache) =>
{
    var value = await cache.GetStringAsync("my-key");
    if (value is null)
    {
        value = "computed-value";
        await cache.SetStringAsync("my-key", value,
            new DistributedCacheEntryOptions { AbsoluteExpirationRelativeToNow = TimeSpan.FromMinutes(5) });
    }
    return Results.Ok(new { value });
});
```

## Files to Modify

| File | Action |
|------|--------|
| `Program.cs` | Add Redis cache registration |
| `*.csproj` | Add NuGet packages |
