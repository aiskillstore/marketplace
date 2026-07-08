# Azure Region Availability Index

> **AUTHORITATIVE SOURCE** — Consult service-specific files BEFORE recommending any region.
>
> Official reference: https://azure.microsoft.com/en-us/explore/global-infrastructure/products-by-region/table

## How to Use

1. Check if your architecture includes any **limited availability** services below
2. If yes → consult the service-specific file or use the MCP tool to list supported regions with sufficient quota for that service, and only offer regions that support ALL services
3. If all services are "available everywhere" → offer common regions

## MCP Tools Used

| Tool | Purpose |
|------|---------|
| `mcp_azure_mcp_quota` | Check Azure region availability and quota by setting `command` to `quota_usage_check` or `quota_region_availability_list` |

---

## Services with LIMITED Region Availability

| Service | Availability | Details |
|---------|--------------|---------|
| Static Web Apps | Limited (5 regions) | [Region Details](services/static-web-apps/region-availability.md) |
| Azure AI Foundry | Very limited (by model) | [Region Details](services/foundry/region-availability.md) |
| Azure Kubernetes Service (AKS) | Limited in some regions | To get available regions with enough quota, use `mcp_azure_mcp_quota` tool. |
| Azure Database for PostgreSQL | Limited in some regions | To get available regions with enough quota, use `mcp_azure_mcp_quota` tool. |

---

## Services Available in Most Regions

These services are available in all major Azure regions — no special consideration needed:

- Container Apps
- Azure Functions
- App Service
- Azure SQL Database
- Cosmos DB
- Key Vault
- Storage Account
- Service Bus
- Event Grid
- Application Insights / Log Analytics


