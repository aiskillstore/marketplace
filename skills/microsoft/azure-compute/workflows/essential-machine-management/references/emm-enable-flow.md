# EMM Enable Flow

Copilot-guided step-by-step workflow for enabling Essential Machine Management on a subscription. Copilot orchestrates each step, triggering the necessary CLI commands or API calls on behalf of the user.

## Quick Reference

| Property | Value |
| -------- | ----- |
| Resource type | `Microsoft.ManagedOps/ManagedOps` |
| Resource provider | `Microsoft.ManagedOps` |
| API version | `2025-07-28-preview` |
| Deployment scope | Subscription-level |

## Workflow Steps

### Step 1: Select Target Subscription

Ask the user which subscription to enable EMM for. Use MCP tools to list subscriptions if needed.

| MCP Tool | Purpose |
| -------- | ------- |
| `mcp_azure_mcp_subscription_list` | List available subscriptions |

Store the selected `subscriptionId` and `tenant` for all subsequent steps.

### Step 2: Validate User Role Assignments

Check that the current user has the 3 required roles on the target subscription. This requires two API calls: one to get the user's role assignments, and one to get all role definitions. Then compare the user's assigned permissions against the required roles.

**Step 2a: Get current user's object ID**

```bash
az rest --method GET --url "https://graph.microsoft.com/v1.0/me" --query id -o tsv
```

**Step 2b: Get user's role assignments on the subscription**

```text
GET https://management.azure.com/subscriptions/{subscriptionId}/providers/Microsoft.Authorization/roleAssignments?api-version=2022-04-01&$filter=assignedTo('{objectId}')
```

> 💡 **Tip:** The `assignedTo` filter is self-scoped — it allows the user to query their own role assignments without needing `Microsoft.Authorization/roleAssignments/read`. However, a 403 will still occur if the user has no role on the subscription at all.

**Step 2c: Get all role definitions on the subscription**

```text
GET https://management.azure.com/subscriptions/{subscriptionId}/providers/Microsoft.Authorization/roleDefinitions?api-version=2022-04-01
```

**Step 2d: Join and check permissions**

For each role assignment, match `properties.roleDefinitionId` to the role definitions to resolve the role name and its `properties.permissions[]`. Then check whether the user's combined permissions cover all three required roles:

| Required Role | Key Permissions (actions) |
| ------------- | ------------------------ |
| Essential Machine Management Administrator | `Microsoft.ManagedOps/managedOps/*`, `Microsoft.Insights/dataCollectionRules/*`, `Microsoft.Monitor/accounts/*`, `Microsoft.OperationalInsights/workspaces/read`, `Microsoft.Security/pricings/*` |
| Managed Identity Operator | `Microsoft.ManagedIdentity/userAssignedIdentities/*/read`, `Microsoft.ManagedIdentity/userAssignedIdentities/*/assign/action` |
| Resource Policy Contributor | `Microsoft.Authorization/policyassignments/*`, `Microsoft.Authorization/policydefinitions/*`, `Microsoft.PolicyInsights/*` |

> 💡 **Tip:** If the user has **Owner** at subscription scope, they satisfy all required permissions. Check for these first as a fast path.

```text
Check result?
├─ All 3 roles covered → Proceed to Step 3
├─ Owner found → All roles satisfied, proceed to Step 3
└─ Missing roles → Inform user which roles are missing and how to assign them, then re-check
```

### Step 3: Select or Create a User-Assigned Managed Identity (UAMI)

Ask the user to provide an existing UAMI or create a new one. The UAMI must have **Contributor** on the target subscription.

Verify the UAMI's role using the same API pattern as Step 2, but filter by the UAMI's principal ID (object ID) instead of the user's:

```text
GET https://management.azure.com/subscriptions/{subscriptionId}/providers/Microsoft.Authorization/roleAssignments?api-version=2022-04-01&$filter=assignedTo('{uamiPrincipalId}')
```

Check that at least one assignment resolves to the **Contributor** role definition.

> 💡 **Tip:** If the UAMI lacks the Contributor role, guide the user to assign it before proceeding.

Store the full UAMI resource ID: `/subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.ManagedIdentity/userAssignedIdentities/<name>`

### Step 4: Select or Create Monitoring Workspaces

Ask the user for a **Log Analytics workspace** and an **Azure Monitor workspace**. Offer to create new ones if needed.

| Resource | CLI Command | Purpose |
| -------- | ----------- | ------- |
| Log Analytics workspace (list) | `az monitor log-analytics workspace list --subscription <subId> -o table` | List existing workspaces |
| Log Analytics workspace (create) | `az monitor log-analytics workspace create --workspace-name <name> --resource-group <rg> --subscription <subId> --location <location>` | Create new workspace |
| Azure Monitor workspace (list) | `az resource list --resource-type "Microsoft.Monitor/accounts" --subscription <subId> -o table` | List existing workspaces |
| Azure Monitor workspace (create) | `az resource create --resource-type "Microsoft.Monitor/accounts" --name <name> --resource-group <rg> --subscription <subId> --location <location> --properties "{}"` | Create new workspace |

> ⚠️ **Warning:** If workspaces are in a **different subscription** than the target:
> - Register `Microsoft.ManagedOps` RP in the workspace subscription
> - User needs **EMM Administrator** role on the workspace resource group
> - UAMI needs **Contributor** on the workspace resource group

Store both workspace resource IDs.

### Step 5: Configure Security Options

Ask the user about optional security add-ons.

| Feature | Default | Cost |
| ------- | ------- | ---- |
| Foundational CSPM | Always enabled | Free |
| Defender CSPM | Disabled | Paid |
| Defender for Cloud | Disabled | Paid |

Store user selections as `enabled` or `disabled`.

### Step 6: Register Resource Providers

Register required RPs on the target subscription before deployment.

```bash
az provider register --namespace Microsoft.ManagedOps --subscription <subscriptionId>
az provider register --namespace Microsoft.OperationsManagement --subscription <subscriptionId>
az provider register --namespace Microsoft.PolicyInsights --subscription <subscriptionId>
az provider register --namespace Microsoft.Insights --subscription <subscriptionId>
az provider register --namespace Microsoft.OperationalInsights --subscription <subscriptionId>
az provider register --namespace Microsoft.Monitor --subscription <subscriptionId>
az provider register --namespace Microsoft.ManagedIdentity --subscription <subscriptionId>
az provider register --namespace Microsoft.Security --subscription <subscriptionId>
```

> 💡 **Tip:** RP registration is idempotent — safe to run even if already registered.

### Step 7: Deploy EMM via ARM API

Submit the PUT request to enable EMM on the subscription.

```text
PUT /subscriptions/{subscriptionId}/providers/Microsoft.ManagedOps/managedOps/default?api-version=2025-07-28-preview
```

Request body:

```json
{
  "properties": {
    "desiredConfiguration": {
      "defenderCspm": "<enabled|disabled>",
      "defenderForServers": "<enabled|disabled>",
      "changeTrackingAndInventory": {
        "logAnalyticsWorkspaceId": "<log-analytics-workspace-resource-id>"
      },
      "userAssignedManagedIdentityId": "<uami-resource-id>",
      "azureMonitorInsights": {
        "azureMonitorWorkspaceId": "<azure-monitor-workspace-resource-id>"
      }
    }
  }
}
```

Populate the request body with the values collected in previous steps.

### Step 8: Verify Enrollment

After deployment completes, confirm the subscription is enrolled.

```text
GET /subscriptions/{subscriptionId}/providers/Microsoft.ManagedOps/managedOps/default?api-version=2025-07-28-preview
```

```text
Deployment status?
├─ Succeeded → Report success to user. All existing VMs will be enrolled via policy remediation.
├─ In progress → Wait and re-check after a short interval.
└─ Failed → Read error details and route to Error Handling in the parent workflow.
```

## Disable EMM (Offboard)

To disable EMM for a subscription:

```text
DELETE /subscriptions/{subscriptionId}/providers/Microsoft.ManagedOps/managedOps/default?api-version=2025-07-28-preview
```

> ⚠️ **Warning:** Disabling reverts pricing to standard per-service rates, which may increase costs. Existing VM configurations are not removed.

## Error Handling

| Error | Cause | Remediation |
| ----- | ----- | ----------- |
| 403 on role check | User has no RBAC role assignment on the subscription (the `assignedTo` filter is self-scoped and does not require `roleAssignments/read`, but the user must have at least one role on the subscription) | Inform user they lack Owner or Contributor role on this subscription and cannot proceed with EMM enrollment |
| Missing required roles | User missing EMM Administrator, Managed Identity Operator, or Resource Policy Contributor | Guide user to assign missing roles, then re-validate |
| UAMI lacks Contributor | Managed identity missing Contributor role | Assign Contributor to the UAMI at subscription scope |
| RP registration failed | Insufficient permissions to register providers | User needs Contributor or Owner on the subscription |
| PUT deployment fails | ARM validation error | Check error details; verify all prerequisites met |
| Cross-subscription error | Workspace in different sub without RP/role setup | Register `Microsoft.ManagedOps` in workspace sub; assign roles on workspace RG |
