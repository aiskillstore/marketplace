# Azure Quota CLI Commands Reference

Comprehensive reference for Azure CLI quota commands.

## Prerequisites

**Install quota extension** (required):
```bash
az extension add --name quota
```

> **⚠️ CRITICAL: ALWAYS USE CLI FIRST**
>
> Azure CLI is the **ONLY reliable method** for quota checks. **Use `az quota` commands FIRST, always.**
>
> **DO NOT use REST API or Azure Portal as your first approach.** They are unreliable.
>
> **Required workflow:**
> 1. **FIRST:** Try `az quota list` / `az quota show` / `az quota usage show`
> 2. **If CLI returns `BadRequest`:** Resource provider doesn't support quota API → use [Azure service limits docs](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/azure-subscription-service-limits)
> 3. **Never start with REST API or Portal** - only use as fallback
>
> **Why REST API/Portal are unreliable:**
> - REST API returns "No Limit" or "Unlimited" values that are **MISLEADING**
> - "No Limit" **DOES NOT mean unlimited capacity** - usually means resource doesn't support quota API
> - Service-specific limits still apply even when REST API shows "No Limit"
> - Portal may show incomplete or cached quota data
> - REST API lacks proper error handling for unsupported providers
>
> **If you see "No Limit" in REST API/Portal:**
> - ❌ This is NOT unlimited capacity
> - ✅ It means quota API doesn't support that resource type
> - ✅ Check [Azure service limits docs](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/azure-subscription-service-limits) for actual limits
> - ✅ Regional capacity constraints may still exist

## Resource Name Mapping

**⚠️ CRITICAL:** No 1:1 mapping exists between ARM resource types and quota names. Always discover via `az quota list`.

**Discovery workflow**:
1. List all quotas: `az quota list --scope /subscriptions/{id}/providers/{Provider}/locations/{region}`
2. Match `properties.name.localizedValue` to your resource type
3. Use exact `name` value in subsequent commands

**Example mappings**:

| ARM Type | Quota Name |
|----------|-----------|
| `Microsoft.App/managedEnvironments` | `ManagedEnvironmentCount` |
| `Microsoft.Compute/virtualMachines` | `standardDSv3Family`, `cores`, `virtualMachines` |
| `Microsoft.Network/publicIPAddresses` | `PublicIPAddresses`, `IPv4StandardSkuPublicIpAddresses` |

## Command Summary

| Command | Description |
|---------|-------------|
| [az quota list](#az-quota-list) | List all quota limits for a scope |
| [az quota show](#az-quota-show) | Show quota limit for specific resource |
| [az quota usage list](#az-quota-usage-list) | List current usage for all resources |
| [az quota usage show](#az-quota-usage-show) | Show current usage for specific resource |
| [az quota update](#az-quota-update) | Request quota increase |
| [az quota create](#az-quota-create) | Create quota limit (advanced) |

See [advanced-commands.md](advanced-commands.md) for request status and operation commands.

---

## az quota list

List all quota limits for a scope. **Use this first to discover quota resource names.**

**Syntax**:
```bash
az quota list --scope SCOPE [--max-items N] [--next-token TOKEN]
```

**Required**:
- `--scope` - Azure resource URI: `/subscriptions/{id}/providers/{Provider}/locations/{region}`

**Examples**:
```bash
# List compute quotas
az quota list --scope /subscriptions/{id}/providers/Microsoft.Compute/locations/eastus

# List network quotas
az quota list --scope /subscriptions/{id}/providers/Microsoft.Network/locations/eastus

# Table format
az quota list --scope /subscriptions/{id}/providers/Microsoft.Compute/locations/eastus --output table
```

**Key output fields**:
- `name` - Quota resource name (use in other commands)
- `properties.name.localizedValue` - Human-readable description
- `properties.limit.value` - Quota limit

---

## az quota show

Show quota limit for a specific resource.

**Syntax**:
```bash
az quota show --resource-name NAME --scope SCOPE
```

**Required**:
- `--resource-name` - Quota resource name (from `az quota list`)
- `--scope` - Azure resource URI

**Example**:
```bash
# Get DSv3 family vCPU limit
az quota show \
  --resource-name standardDSv3Family \
  --scope /subscriptions/{id}/providers/Microsoft.Compute/locations/eastus
```

**Key output fields**:
- `properties.limit.value` - Quota limit
- `properties.name.localizedValue` - Human-readable description
- `properties.quotaPeriod` - Reset period (e.g., P1M = 1 month)

---

## az quota update

Request quota increase for a resource.

**Syntax**:
```bash
az quota update --resource-name NAME --scope SCOPE --limit-object value=N [--resource-type TYPE] [--no-wait]
```

**Required**:
- `--resource-name` - Quota resource name
- `--scope` - Azure resource URI  
- `--limit-object` - New limit value (format: `value=N`)

**Optional**:
- `--resource-type` - Resource type (e.g., dedicated, lowPriority)
- `--no-wait` - Don't wait for completion (true/false)

**Examples**:
```bash
# Increase FSv2 family vCPUs to 100
az quota update \
  --resource-name standardFSv2Family \
  --scope /subscriptions/{id}/providers/Microsoft.Compute/locations/eastus \
  --limit-object value=100 \
  --resource-type dedicated

# Non-blocking request
az quota update \
  --resource-name standardFSv2Family \
  --scope /subscriptions/{id}/providers/Microsoft.Compute/locations/eastus \
  --limit-object value=100 \
  --no-wait true
```

---

## az quota usage list

List current usage for all resources in a scope.

**Syntax**:
```bash
az quota usage list --scope SCOPE [--max-items N] [--next-token TOKEN]
```

**Required**:
- `--scope` - Azure resource URI

**Examples**:
```bash
# List compute usage
az quota usage list --scope /subscriptions/{id}/providers/Microsoft.Compute/locations/eastus

# Table format
az quota usage list --scope /subscriptions/{id}/providers/Microsoft.Compute/locations/eastus --output table
```

**Key output**:
- `properties.usages.value` - Current usage count
- Use with `az quota show` to calculate available capacity

---

## az quota usage show

Show current usage for a specific resource.

**Syntax**:
```bash
az quota usage show --resource-name NAME --scope SCOPE
```

**Required**:
- `--resource-name` - Quota resource name
- `--scope` - Azure resource URI

**Example**:
```bash
az quota usage show \
  --resource-name standardDSv3Family \
  --scope /subscriptions/{id}/providers/Microsoft.Compute/locations/eastus
```

**Calculate available capacity**:
1. Get limit: `az quota show --resource-name {name} --scope {scope}` → limit value
2. Get usage: `az quota usage show --resource-name {name} --scope {scope}` → current usage
3. Available = Limit - Usage

**Example calculation**:
- Limit (from `az quota show`): 350 vCPUs
- Usage (from `az quota usage show`): 12 vCPUs
- **Available**: 338 vCPUs

---

## az quota create

Create quota limit for a resource. **Rarely used** - typically use `az quota update` instead.

**Syntax**:
```bash
az quota create --resource-name NAME --scope SCOPE --limit-object value=N [--resource-type TYPE]
```

**Required**:
- `--resource-name` - Quota resource name
- `--scope` - Azure resource URI
- `--limit-object` - Quota limit value

**Examples**:
```bash
# Create network quota
az quota create \
  --resource-name MinPublicIpInterNetworkPrefixLength \
  --scope /subscriptions/{id}/providers/Microsoft.Network/locations/eastus \
  --limit-object value=10 \
  --resource-type MinPublicIpInterNetworkPrefixLength

# Create ML quota
az quota create \
  --resource-name TotalLowPriorityCores \
  --scope /subscriptions/{id}/providers/Microsoft.MachineLearningServices/locations/eastus \
  --limit-object value=10 \
  --resource-type lowPriority
```

---

## Troubleshooting

### Unsupported Resource Types

Not all Azure resource providers support the quota API. If you receive a `BadRequest` error when running `az quota list`, the provider likely doesn't support quota commands.

**Example - Microsoft.DocumentDB (Cosmos DB)**:
```bash
az quota list --scope /subscriptions/{id}/providers/Microsoft.DocumentDB/locations/eastus
# Error: (BadRequest) Bad request
```

**Workarounds**:
- Check [Azure subscription limits documentation](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/azure-subscription-service-limits)
- Use Azure Portal for quota management
- Check service-specific documentation

**Testing provider support**:
```bash
# Try listing quotas
az quota list --scope /subscriptions/{id}/providers/{Provider}/locations/{region}

# BadRequest error → not supported
# List of quotas → supported
```

### REST API "No Limit" Warning

> **⚠️ CRITICAL WARNING: REST API "No Limit" is MISLEADING**
>
> If you see "No Limit", "Unlimited", or similar values in REST API or Azure Portal responses:
>
> **This DOES NOT mean unlimited capacity!**
>
> It most likely means:
> - The resource provider doesn't support the quota API
> - Quota information isn't available through this API
> - The quota is managed at a different scope
>
> **DO NOT assume unlimited capacity. Always:**
> 1. Use `az quota` CLI commands first (preferred method)
> 2. If CLI returns `BadRequest`, check [Azure service limits documentation](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/azure-subscription-service-limits)
> 3. Consult service-specific documentation for actual limits
> 4. Consider regional capacity constraints even without quota enforcement

### Common Error Codes

| Error | Cause | Solution |
|-------|-------|----------|
| `BadRequest` | Provider not supported by quota API | Use CLI (preferred) or check [Azure service limits docs](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/azure-subscription-service-limits) |
| `ExtensionNotFound` | Quota extension not installed | Run `az extension add --name quota` |
| `MissingRegistration` | Microsoft.Quota provider not registered | Run `az provider register --namespace Microsoft.Quota` |
| `InvalidScope` | Incorrect scope format | Verify: `/subscriptions/{id}/providers/{namespace}/locations/{region}` |
| `QuotaNotAvailableForResource` | Resource not available in region | Try different region |
| `RequestThrottled` | Too many API calls | Implement exponential backoff |

### Known Support Status

**Unsupported**:
- ❌ Microsoft.DocumentDB (Cosmos DB)

**Supported**:
- ✅ Microsoft.Compute (VMs, disks, cores)
- ✅ Microsoft.Network (VNets, IPs, load balancers)
- ✅ Microsoft.App (Container Apps)
- ✅ Microsoft.Storage (storage accounts)
- ✅ Microsoft.MachineLearningServices
- ✅ Microsoft.ContainerService (AKS)
