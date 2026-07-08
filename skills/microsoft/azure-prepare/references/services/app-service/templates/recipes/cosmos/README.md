# Cosmos DB Recipe — REFERENCE ONLY

Adds Azure Cosmos DB (NoSQL) integration to an App Service base template.

## Overview

This recipe composes with a Web API or Web App base template to add Cosmos DB data access. It provides the IaC delta (Cosmos account, database, container, RBAC) and per-language source code using the Cosmos DB SDK.

## Integration Type

| Aspect | Value |
|--------|-------|
| **Database** | Azure Cosmos DB for NoSQL |
| **Auth** | Managed identity (DefaultAzureCredential) |
| **SDK** | Microsoft.Azure.Cosmos (.NET), @azure/cosmos (Node.js), azure-cosmos (Python) |
| **Hosting** | App Service (from base template) |
| **Local Auth** | Disabled (`disableLocalAuth: true`) — RBAC-only |

## Composition Steps

Apply these steps AFTER `azd init -t <base-template>`:

| # | Step | Details |
|---|------|---------|
| 1 | **Add IaC module** | Add Cosmos DB Bicep module to `infra/app/` |
| 2 | **Wire into main** | Add module reference in `main.bicep` |
| 3 | **Add app settings** | Add Cosmos endpoint + database + container settings |
| 4 | **Add source code** | Add Cosmos client setup from `source/{lang}.md` |
| 5 | **Add packages** | Add Cosmos SDK + Azure Identity packages |

## App Settings

| Setting | Value | Purpose |
|---------|-------|---------|
| `COSMOS_ENDPOINT` | `https://{account}.documents.azure.com:443/` | Cosmos account endpoint |
| `COSMOS_DATABASE_NAME` | `app-db` | Target database |
| `COSMOS_CONTAINER_NAME` | `items` | Target container |

### Bicep App Settings Block

```bicep
appSettings: [
  { name: 'COSMOS_ENDPOINT', value: cosmos.outputs.endpoint }
  { name: 'COSMOS_DATABASE_NAME', value: cosmos.outputs.databaseName }
  { name: 'COSMOS_CONTAINER_NAME', value: cosmos.outputs.containerName }
]
```

> **Note:** No connection string or key is needed. The SDK uses `DefaultAzureCredential` which automatically resolves to the app's managed identity in Azure.

## RBAC Roles Required

| Role | GUID | Scope | Purpose |
|------|------|-------|---------|
| **Cosmos DB Account Reader** | `fbdf93bf-df7d-467e-a4d2-9458aa1360c8` | Cosmos account | Read account metadata |
| **Cosmos DB Built-in Data Contributor** | `00000000-0000-0000-0000-000000000002` | Cosmos account (SQL role) | Read/write data |

> **Important:** Cosmos DB uses its own SQL RBAC system (`sqlRoleAssignments`) for data plane operations, not standard Azure RBAC.

## Networking (when VNET_ENABLED=true)

| Component | Details |
|-----------|---------|
| **Private endpoint** | Cosmos account → App Service VNet subnet |
| **Private DNS zone** | `privatelink.documents.azure.com` |

## Resources Created

| Resource | Type | Purpose |
|----------|------|---------|
| Cosmos DB Account | `Microsoft.DocumentDB/databaseAccounts` | Serverless NoSQL database |
| SQL Database | `databaseAccounts/sqlDatabases` | Application database |
| Container | `sqlDatabases/containers` | Data container with partition key |
| Role Assignment | `Microsoft.Authorization/roleAssignments` | Control plane access |
| SQL Role Assignment | `databaseAccounts/sqlRoleAssignments` | Data plane access |

## Source Code Examples

| Language | Source File |
|----------|-------------|
| C# (.NET) | [source/dotnet.md](source/dotnet.md) |
| Python | [source/python.md](source/python.md) |
| Node.js | [source/nodejs.md](source/nodejs.md) |

## References

- [Cosmos DB + App Service tutorial](https://learn.microsoft.com/en-us/azure/cosmos-db/nosql/tutorial-dotnet-web-app)
- [Passwordless Cosmos DB connections](https://learn.microsoft.com/en-us/azure/cosmos-db/nosql/how-to-dotnet-get-started)
- [Cosmos DB RBAC](https://learn.microsoft.com/en-us/azure/cosmos-db/how-to-setup-rbac)
