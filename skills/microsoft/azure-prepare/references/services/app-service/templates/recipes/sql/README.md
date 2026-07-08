# SQL Database Recipe — REFERENCE ONLY

Adds Azure SQL Database integration to an App Service base template.

## Overview

This recipe composes with a Web API or Web App base template to add Azure SQL Database connectivity. It provides the IaC delta (SQL Server, database, firewall, RBAC) and per-language source code using EF Core, Prisma, or SQLAlchemy.

## Integration Type

| Aspect | Value |
|--------|-------|
| **Database** | Azure SQL Database (Serverless or Provisioned) |
| **Auth** | Managed identity (passwordless) |
| **ORM** | EF Core (.NET), Prisma (Node.js), SQLAlchemy (Python) |
| **Hosting** | App Service (from base template) |
| **Local Auth** | Disabled in Azure (Entra ID only); local dev may use SQL auth |

## Composition Steps

Apply these steps AFTER `azd init -t <base-template>`:

| # | Step | Details |
|---|------|---------|
| 1 | **Add IaC module** | Add SQL Server + Database Bicep module to `infra/app/` |
| 2 | **Wire into main** | Add module reference in `main.bicep` |
| 3 | **Add app settings** | Add SQL connection string (managed identity) |
| 4 | **Add source code** | Add ORM models, DbContext/client setup from `source/{lang}.md` |
| 5 | **Add packages** | Add ORM and SQL client packages |
| 6 | **Run migrations** | Add postprovision hook for DB schema setup |

## App Settings

| Setting | Value | Purpose |
|---------|-------|---------|
| `AZURE_SQL_CONNECTION_STRING` | `Server=tcp:{server}.database.windows.net;Database={db};Authentication=Active Directory Managed Identity;User Id={clientId};` | Passwordless SQL connection |

### Bicep App Settings Block

```bicep
appSettings: [
  {
    name: 'AZURE_SQL_CONNECTION_STRING'
    value: 'Server=tcp:${sqlServer.properties.fullyQualifiedDomainName},1433;Database=${sqlDatabase.name};Authentication=Active Directory Managed Identity;User Id=${managedIdentity.properties.clientId};Encrypt=True;TrustServerCertificate=False;'
  }
]
```

> **Note:** The `Authentication=Active Directory Managed Identity` setting tells the SQL client to use the app's managed identity. No passwords are stored.

## RBAC Roles Required

| Role | GUID | Scope | Purpose |
|------|------|-------|---------|
| **SQL DB Contributor** | `9b7fa17d-e63e-47b0-bb0a-15c516ac86ec` | SQL Server | Manage database |
| **Directory Readers** | `88d8e3e3-8f55-4a1e-953a-9b9898b8876b` | Entra ID | Read directory for MI auth |

> **Important:** Data plane access uses SQL-level roles (`db_datareader`, `db_datawriter`), assigned via a postprovision script that runs `ALTER ROLE` statements.

## Resources Created

| Resource | Type | Purpose |
|----------|------|---------|
| SQL Server | `Microsoft.Sql/servers` | Logical SQL server |
| SQL Database | `Microsoft.Sql/servers/databases` | Application database |
| Firewall Rule | `Microsoft.Sql/servers/firewallRules` | Allow Azure services |
| Entra Admin | `Microsoft.Sql/servers/administrators` | Set MI as admin |

## Files

| Path | Description |
|------|-------------|
| [source/dotnet.md](source/dotnet.md) | C# EF Core integration |
| [source/python.md](source/python.md) | Python SQLAlchemy integration |
| [source/nodejs.md](source/nodejs.md) | Node.js Prisma integration |

## References

- [Azure SQL passwordless connections](https://learn.microsoft.com/en-us/azure/azure-sql/database/azure-sql-passwordless-migration)
- [EF Core with Azure SQL](https://learn.microsoft.com/en-us/ef/core/providers/sql-server/)
- [Tutorial: App Service with SQL](https://learn.microsoft.com/en-us/azure/app-service/tutorial-dotnetcore-sqldb-app)
