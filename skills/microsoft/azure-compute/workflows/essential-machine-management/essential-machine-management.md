# Essential Machine Management (EMM) Workflow

Routes EMM-related requests to the appropriate reference based on user intent.

## Overview

Essential Machine Management simplifies onboarding and configuration of management for Azure VMs and Arc-enabled servers at the subscription level. When enabled, all VMs in a subscription are automatically enrolled with a curated set of monitoring, security, and operations features.

> ⚠️ **Warning:** EMM is currently in **public preview**.

## Routing

```text
User intent?
├─ Enable / onboard / enroll subscription for EMM
│  └─ Copilot-guided (default) → Load [EMM Enable Flow](references/emm-enable-flow.md)
│
├─ User explicitly asks for portal guidance
│  └─ Load [EMM Enable Flow (Portal)](references/emm-enable-flow-portal-guidance.md)
│
├─ What is EMM / features / pricing / tiers
│  └─ Load [EMM Overview](references/emm-overview.md)
│
├─ Prerequisites / permissions / roles / managed identity
│  └─ Load [EMM Prerequisites](references/emm-prerequisites.md)
│
├─ View enrolled subscriptions / browse / status
│  └─ See "Browse Enrolled Subscriptions" below
│
├─ Offboard / disable EMM for a subscription
│  └─ See "Offboard a Subscription" below
│
└─ Troubleshoot EMM issues
   └─ See "Troubleshooting" below
```

| Signal | Reference |
| ------ | --------- |
| "enable EMM", "onboard subscription", "enroll VMs", "set up machine management" | [EMM Enable Flow](references/emm-enable-flow.md) |
| User explicitly mentions "portal", "Azure portal", "portal UI" | [EMM Enable Flow (Portal)](references/emm-enable-flow-portal-guidance.md) |
| "what is EMM", "features", "pricing", "tiers", "what does EMM include" | [EMM Overview](references/emm-overview.md) |
| "permissions", "roles", "prerequisites", "managed identity for EMM" | [EMM Prerequisites](references/emm-prerequisites.md) |

> ⚠️ **Important:** Only route to the portal guide when the user explicitly mentions "portal". All other enable requests use the Copilot-guided flow.

## Browse Enrolled Subscriptions

Query the EMM resource on each subscription to check enrollment status:

```text
GET https://management.azure.com/subscriptions/{subscriptionId}/providers/Microsoft.ManagedOps/managedOps/default?api-version=2025-07-28-preview
```

| Response | Meaning |
| -------- | ------- |
| `200` with `provisioningState: Succeeded` | Subscription is enrolled |
| `200` with `provisioningState: Failed` | Enrollment attempted but failed — check error details |
| `404` | Subscription is not enrolled |

When enrolled, the response includes:
- **SKU/tier** — e.g. Essential
- **Enabled services** — Azure Monitor Insights, Update Manager, Change Tracking, Policy & Machine Configuration, Defender CSPM, Defender for Servers
- **UAMI** — the user-assigned managed identity resource ID
- **Workspaces** — Log Analytics and Azure Monitor workspace resource IDs
- **Created by / date** — who enrolled and when (in `systemData`)

To scan multiple subscriptions, use `mcp_azure_mcp_subscription_list` to list available subscriptions, then query each one. Report results as a table:

```text
| Subscription | Status | SKU | Services Enabled |
```

## Offboard a Subscription

To disable EMM for a subscription, follow the "Disable EMM (Offboard)" section in [EMM Enable Flow](references/emm-enable-flow.md).

> ⚠️ **Warning:** When you disable a subscription, machines no longer use consolidated pricing. Pricing reverts to standard per-service pricing which may increase costs. Existing VM configurations are not removed — disable unneeded services manually.

## Troubleshooting

For common EMM issues, refer to the official documentation:
- [Troubleshoot Essential Machine Management (Preview)](https://learn.microsoft.com/en-us/azure/operations/configuration-enrollment-troubleshoot)

Common issues include:
- Missing role assignments (EMM Administrator, Managed Identity Operator, Resource Policy Contributor)
- Resource provider `Microsoft.ManagedOps` not registered in the subscription
- UAMI lacking Contributor permission on the subscription
- Cross-subscription workspace access requires additional RP registration

## Error Handling

| Error | Cause | Remediation |
| ----- | ----- | ----------- |
| Permission denied during enable | User lacks required roles | Assign EMM Administrator, Managed Identity Operator, and Resource Policy Contributor roles |
| UAMI role check fails | Managed identity lacks Contributor | Assign Contributor role to the UAMI at subscription scope |
| RP not registered | `Microsoft.ManagedOps` not registered | Register via `Register-AzResourceProvider -ProviderNamespace "Microsoft.ManagedOps"` |
| Cross-subscription workspace error | Workspace in different sub without RP registration | Register `Microsoft.ManagedOps` in the workspace subscription and assign EMM Administrator on the workspace resource group |
| Deployment fails | ARM template validation error | Check deployment link in browse view for detailed error; verify all prerequisites |
