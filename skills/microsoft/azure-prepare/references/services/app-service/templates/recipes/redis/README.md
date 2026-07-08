# Azure Cache for Redis Recipe — REFERENCE ONLY

Adds Azure Cache for Redis integration to an App Service base template.

## Overview

This recipe composes with a Web API or Web App base template to add distributed caching with Azure Cache for Redis. Uses managed identity for passwordless access.

## Integration Type

| Aspect | Value |
|--------|-------|
| **Service** | Azure Cache for Redis |
| **Auth** | Managed identity (Entra ID access policy) |
| **SKU** | Basic C0 (dev) / Standard C1+ (production) |
| **Protocol** | Redis 6.0+ with TLS |
| **Local Auth** | Disabled — Entra ID only |

## Composition Steps

Apply these steps AFTER `azd init -t <base-template>`:

| # | Step | Details |
|---|------|---------|
| 1 | **Add IaC module** | Add Redis Bicep module to `infra/app/` |
| 2 | **Wire into main** | Add module reference in `main.bicep` |
| 3 | **Add app settings** | Add Redis host name + port settings |
| 4 | **Add source code** | Add cache client setup from examples below |
| 5 | **Add packages** | Add Redis client packages |

## App Settings

| Setting | Value | Purpose |
|---------|-------|---------|
| `REDIS_HOST` | `{name}.redis.cache.windows.net` | Redis host name |
| `REDIS_PORT` | `6380` | TLS port |

### Bicep App Settings Block

```bicep
appSettings: [
  { name: 'REDIS_HOST', value: redis.outputs.hostName }
  { name: 'REDIS_PORT', value: '6380' }
]
```

> **Note:** With managed identity, no access key is needed. The Redis client uses `DefaultAzureCredential` to obtain a token.

## RBAC Roles Required

| Role | GUID | Scope | Purpose |
|------|------|-------|---------|
| **Redis Cache Contributor** | `e0f68234-74aa-48ed-b826-c38b57376e17` | Redis cache | Manage cache |

> For data plane access with Entra ID, configure the Redis access policy to grant the managed identity `Data Owner` or `Data Contributor` access.

## Resources Created

| Resource | Type | Purpose |
|----------|------|---------|
| Redis Cache | `Microsoft.Cache/redis` | Distributed cache |
| Access Policy | `Microsoft.Cache/redis/accessPolicyAssignments` | MI data access |
| Private Endpoint | `Microsoft.Network/privateEndpoints` | VNet-only access (conditional) |

## Source Code Examples

| Language | Source File |
|----------|-------------|
| C# (ASP.NET Core) | [source/dotnet.md](source/dotnet.md) |
| Python | [source/python.md](source/python.md) |
| Node.js | [source/nodejs.md](source/nodejs.md) |

> ⚠️ **Token expiry:** Entra ID access tokens expire in ~1 hour. The C# example uses `ConfigureForAzureWithTokenCredentialAsync` which handles automatic token renewal. Python and Node.js examples require a connection factory pattern — see the source files for a refresh-capable implementation.

## Networking (when VNET_ENABLED=true)

| Component | Details |
|-----------|---------|
| **Private endpoint** | Redis → App Service VNet subnet |
| **Private DNS zone** | `privatelink.redis.cache.windows.net` |

## References

- [Azure Cache for Redis overview](https://learn.microsoft.com/en-us/azure/azure-cache-for-redis/cache-overview)
- [Use Entra ID with Redis](https://learn.microsoft.com/en-us/azure/azure-cache-for-redis/cache-azure-active-directory-for-authentication)
- [Redis + App Service tutorial](https://learn.microsoft.com/en-us/azure/azure-cache-for-redis/cache-web-app-howto)
