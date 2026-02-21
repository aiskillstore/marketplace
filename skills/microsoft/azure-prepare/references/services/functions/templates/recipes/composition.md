# Composition Algorithm

Step-by-step algorithm for composing a base HTTP template with an integration recipe.

> **This is the authoritative process. Follow it exactly.**

> ⛔ **CRITICAL: Read [common/uami-bindings.md](common/uami-bindings.md) before any deployment.**
> Base templates use User Assigned Managed Identity (UAMI). ALL service bindings require
> explicit `credential` and `clientId` app settings. Failure to include these causes
> 500/401/403 errors at runtime.

## Algorithm

```
INPUT:
  - language:    dotnet | typescript | javascript | python | java | powershell
  - integration: http | cosmosdb | sql | servicebus | eventhubs | timer | blob | durable | mcp
  - iac:         bicep | terraform

OUTPUT:
  - Complete project directory ready for `azd up`
```

### Step 1: Fetch Base Template

```bash
# Determine template name
IF iac == 'bicep':
  TEMPLATE = base_templates[language].bicep    # e.g., functions-quickstart-dotnet-azd
ELSE IF iac == 'terraform':
  TEMPLATE = base_templates[language].terraform # e.g., functions-quickstart-dotnet-azd-tf

# Non-interactive init
ENV_NAME="$(basename "$PWD" | tr '[:upper:]' '[:lower:]' | tr ' _' '-')-dev"
azd init -t $TEMPLATE -e "$ENV_NAME" --no-prompt
```

### Step 2: Check if Recipe Needed

```
IF integration IN [http]:
  → DONE. Base template is complete.

IF integration IN [timer]:
  → Source-only recipe. Skip to Step 5.

IF integration IN [durable, mcp]:
  → Source-only recipe with storage configuration:
    - Set `enableQueue: true` in main.bicep (required for Durable task hub and MCP)
    - Set `enableTable: true` in main.bicep (required for Durable only; NOT required for MCP)
    Note: These are minimal parameter toggles, not structural changes to IaC.
  → Then skip to Step 5.

IF integration IN [cosmosdb, sql, servicebus, eventhubs, blob]:
  → Full recipe. Continue to Step 3.
```

### Step 3: Add IaC Module (for full recipes only)

**Bicep:**
1. Copy `recipes/{integration}/bicep/*.bicep` → `infra/app/`
2. Add module reference in `infra/main.bicep`:
   ```bicep
   module cosmos './app/cosmos.bicep' = {
     name: 'cosmos'
     scope: rg
     params: {
       name: name
       location: location
       tags: tags
       functionAppPrincipalId: app.outputs.SERVICE_API_IDENTITY_PRINCIPAL_ID
     }
   }
   ```
3. If VNET_ENABLED, also add the network module:
   ```bicep
   module cosmosNetwork './app/cosmos-network.bicep' = if (vnetEnabled) { ... }
   ```

**Terraform:**
1. Copy `recipes/{integration}/terraform/*.tf` → `infra/`
2. Merge `locals.{integration}_app_settings` into function app's `app_setting` block in `main.tf`
3. Networking is conditional (uses `count = var.vnet_enabled ? 1 : 0`)

### Step 4: Add App Settings

Read the recipe's `README.md` for required app settings. Add them to the function app config.

> **CRITICAL: User Assigned Managed Identity (UAMI) Configuration**
>
> The base templates use UAMI, not System Assigned MI. For service bindings (Event Hubs, Service Bus, etc.),
> you MUST include `credential` and `clientId` settings alongside the endpoint:
>
> ```bicep
> appSettings: {
>   // Endpoint
>   EventHubConnection__fullyQualifiedNamespace: eventhubs.outputs.fullyQualifiedNamespace
>   // UAMI credentials - REQUIRED
>   EventHubConnection__credential: 'managedidentity'
>   EventHubConnection__clientId: apiUserAssignedIdentity.outputs.clientId
> }
> ```
>
> Without these, the function will fail with 500/Unauthorized errors.

**Bicep Example (Cosmos DB):**
```bicep
appSettings: {
  COSMOS_CONNECTION__accountEndpoint: cosmos.outputs.cosmosAccountEndpoint
  COSMOS_CONNECTION__credential: 'managedidentity'
  COSMOS_CONNECTION__clientId: apiUserAssignedIdentity.outputs.clientId
  COSMOS_DATABASE_NAME: cosmos.outputs.cosmosDatabaseName
  COSMOS_CONTAINER_NAME: cosmos.outputs.cosmosContainerName
}
```

**Bicep Example (Event Hubs):**
```bicep
appSettings: {
  EventHubConnection__fullyQualifiedNamespace: eventhubs.outputs.fullyQualifiedNamespace
  EventHubConnection__credential: 'managedidentity'
  EventHubConnection__clientId: apiUserAssignedIdentity.outputs.clientId
  EVENTHUB_NAME: eventhubs.outputs.eventHubName
  EVENTHUB_CONSUMER_GROUP: eventhubs.outputs.consumerGroupName
}
```

**Terraform:** Merge recipe locals into function app:
```hcl
app_setting = merge(local.base_app_settings, local.cosmos_app_settings)
```

### Step 4.5: VALIDATE App Settings (MANDATORY)

**Before proceeding, verify these UAMI settings exist for EVERY service binding:**

| Setting Pattern | Required? | Example |
|-----------------|-----------|---------|
| `{Connection}__fullyQualifiedNamespace` or `{Connection}__accountEndpoint` | ✅ Yes | `EventHubConnection__fullyQualifiedNamespace` |
| `{Connection}__credential` | ✅ Yes | `EventHubConnection__credential: 'managedidentity'` |
| `{Connection}__clientId` | ✅ Yes | `EventHubConnection__clientId: uamiClientId` |

**Validation Checklist:**
- [ ] Each service binding has all THREE settings (namespace/endpoint + credential + clientId)
- [ ] `credential` value is exactly `'managedidentity'` (not `'ManagedIdentity'` or other)
- [ ] `clientId` references the UAMI from base template (e.g., `apiUserAssignedIdentity.outputs.clientId`)
- [ ] No connection strings or SAS keys are used

> ⛔ **STOP if any check fails.** The function WILL fail at runtime with 500/Unauthorized errors.

### Step 5: Replace Source Code

1. Read `recipes/{integration}/source/{language}.md`
2. Create the new trigger file(s) as specified
3. Remove the HTTP trigger files listed in "Files to Remove"
4. Add any package dependencies (NuGet, npm, pip, Maven)

### Step 6: Update azure.yaml (if needed)

Some recipes require hooks (e.g., Cosmos firewall scripts for VNet):
```yaml
hooks:
  postprovision:
    posix:
      shell: sh
      run: ./infra/scripts/add-cosmos-firewall.sh
    windows:
      shell: pwsh
      run: ./infra/scripts/add-cosmos-firewall.ps1
```

### Step 7: Validate and Deploy

**Required Environment Setup:**
```bash
azd env set AZURE_LOCATION eastus2      # Required: deployment region
azd env set VNET_ENABLED false          # Required: VNet isolation (true/false)
```

**Deployment Strategy — Two Options:**

**Option A: Single command** (fast, may fail on first deploy due to RBAC propagation)
```bash
azd up --no-prompt
```

**Option B: Two-phase** (recommended for reliability)
```bash
azd provision --no-prompt     # Create resources + RBAC assignments
sleep 60                       # Wait for RBAC propagation (Azure AD needs 30-60s)
azd deploy --no-prompt        # Deploy code (RBAC now active)
```

> **CRITICAL: Never enable `allowSharedKeyAccess: true`** as a workaround for 403 errors.
> The correct solution is waiting for RBAC propagation, not disabling security.

## Base Template Lookup

| Language | Bicep Template | Terraform Template |
|----------|---------------|-------------------|
| dotnet | `functions-quickstart-dotnet-azd` | `functions-quickstart-dotnet-azd-tf` |
| typescript | `functions-quickstart-typescript-azd` | `functions-quickstart-typescript-azd-tf` |
| javascript | `functions-quickstart-javascript-azd` | `functions-quickstart-javascript-azd-tf` |
| python | `functions-quickstart-python-http-azd` | `functions-quickstart-python-http-azd-tf` |
| java | `azure-functions-java-flex-consumption-azd` | `azure-functions-java-flex-consumption-azd-tf` |
| powershell | `functions-quickstart-powershell-azd` | `functions-quickstart-powershell-azd-tf` |

## Storage Endpoint Requirements

Some integrations require additional storage endpoints. Toggle these in `main.bicep` BEFORE provisioning:

| Integration | enableBlob | enableQueue | enableTable | Notes |
|-------------|:----------:|:-----------:|:-----------:|-------|
| HTTP        | ✓          | -           | -           | Default |
| Timer       | ✓          | -           | -           | Checkpointing uses blob |
| Cosmos DB   | ✓          | -           | -           | Standard |
| **Durable** | ✓          | **✓**       | **✓**       | Queue=task hub, Table=history |
| **MCP**     | ✓          | **✓**       | -           | Queue=state mgmt + backplane |

## Recipe Classification

| Category | Integrations | What Recipe Provides |
|----------|-------------|---------------------|
| **Source-only** | timer, durable, mcp | Source code snippet; may require minimal parameter toggles (e.g., `enableQueue`) but no new IaC modules |
| **Full recipe** | cosmosdb, sql, servicebus, eventhubs, blob | IaC modules + RBAC + networking + source code |

## Critical Rules

1. **NEVER synthesize Bicep or Terraform from scratch** — always start from base template IaC
2. **Do not restructure or replace base IaC files** — only ADD recipe modules alongside them and perform minimal parameter toggles (e.g., `enableQueue: true`) where the algorithm explicitly requires
3. **ALWAYS use recipe RBAC role GUIDs** — never let the LLM guess role IDs
4. **ALWAYS use `--no-prompt`** — the agent must never elicit user input during azd commands
5. **ALWAYS verify the base template initialized successfully** before applying recipe
6. **ALWAYS keep `allowSharedKeyAccess: false`** — never enable local auth on storage
7. **ALWAYS keep `disableLocalAuth: true`** — never enable local auth on Cosmos DB/Event Hubs/Service Bus
8. **ALWAYS wait for RBAC propagation** — use two-phase deploy if 403 errors occur
9. **ALWAYS include ALL THREE UAMI settings for every binding** — see [common/uami-bindings.md](common/uami-bindings.md):
   - `{Connection}__fullyQualifiedNamespace` or `{Connection}__accountEndpoint`
   - `{Connection}__credential: 'managedidentity'`
   - `{Connection}__clientId: apiUserAssignedIdentity.outputs.clientId`
10. **ALWAYS use recipe module's `appSettings` output** — do not manually construct app settings; use `union(baseSettings, recipe.outputs.appSettings)` to prevent missing UAMI settings

## Terraform-Specific Requirements

Validated requirements from production deployments with Azure policy enforcement:

### Storage Account Configuration

```hcl
resource "azurerm_storage_account" "storage" {
  # ... standard config ...
  allow_nested_items_to_be_public = false     # Required by Azure policy
  local_user_enabled              = false     # Required for RBAC-only
  shared_access_key_enabled       = false     # Required by Azure policy
}
```

### Function App with Managed Identity Storage

```hcl
provider "azurerm" {
  features {}
  storage_use_azuread = true   # Required for MI-based storage access
}

resource "azurerm_linux_function_app" "function" {
  # ... standard config ...
  storage_uses_managed_identity = true   # Use MI instead of access key
  
  # When using MI storage, assign RBAC BEFORE creating function:
  depends_on = [azurerm_role_assignment.storage_blob_owner]
}

# RBAC for deploying user (required to create function with MI storage)
resource "azurerm_role_assignment" "storage_blob_owner" {
  scope                = azurerm_storage_account.storage.id
  role_definition_name = "Storage Blob Data Owner"
  principal_id         = data.azurerm_client_config.current.object_id
}

# RBAC for function app after creation
resource "azurerm_role_assignment" "function_storage_blob" {
  scope                = azurerm_storage_account.storage.id
  role_definition_name = "Storage Blob Data Owner"
  principal_id         = azurerm_linux_function_app.function.identity[0].principal_id
}
```

### Service Bus with Disabled Local Auth

```hcl
resource "azurerm_servicebus_namespace" "sb" {
  # ... standard config ...
  local_auth_enabled = false   # Required by Azure policy - RBAC only
}
```

### Event Hubs with Disabled Local Auth

```hcl
resource "azurerm_eventhub_namespace" "main" {
  # ... standard config ...
  local_authentication_enabled = false   # Required by Azure policy - RBAC only
}
```

### Cosmos DB with Disabled Local Auth

```hcl
resource "azurerm_cosmosdb_account" "cosmos" {
  # ... standard config ...
  local_authentication_disabled = true   # Required by Azure policy - RBAC only
}
```

### Required: azd-service-name Tag

```hcl
resource "azurerm_linux_function_app" "function" {
  # ... standard config ...
  tags = {
    "azd-service-name" = "api"   # MUST match service name in azure.yaml
  }
}
```

> ⚠️ **Without `azd-service-name` tag, `azd deploy` fails with:**
> `resource not found: unable to find a resource tagged with 'azd-service-name: api'`

### Terraform Provider Configuration

```hcl
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"   # Use AzureRM 4.x for latest features
    }
  }
}
```
