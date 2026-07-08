# EMM Enable Flow (Portal)

Step-by-step guide for enabling Essential Machine Management through the Azure portal UI.

## Quick Reference

| Property | Value |
| -------- | ----- |
| Portal blade | `EnableMachineManagement.ReactView` |
| Extension | `Microsoft_Azure_Computehub` |
| Portal path | Compute infrastructure → Monitoring+Operations → Essential Machine Management → Enable |
| Resource type | `Microsoft.ManagedOps/ManagedOps` |

## Enable Flow Steps

The portal enable flow is a multi-tab wizard with 4 tabs:

### Tab 1: Scope

Select the target subscription and managed identity.

| Field | Description | Required |
| ----- | ----------- | -------- |
| Subscription | The subscription to enable EMM for. Shows VM and Arc machine counts per subscription. | ✅ |
| User-assigned managed identity | UAMI with Contributor on the subscription. Used for onboarding VMs. | ✅ |

**Validation displayed:**
- Required user role assignments vs current user role assignments
- Required UAMI role assignments vs current UAMI role assignments

> 💡 **Tip:** If roles are missing, the UI shows exactly which roles are needed. Assign them before proceeding.

### Tab 2: Configure

Select or create the monitoring workspaces.

| Field | Description | Required |
| ----- | ----------- | -------- |
| Log Analytics workspace | Collects log data (Change Tracking & Inventory). Can create new inline. | ✅ |
| Azure Monitor workspace | Collects metrics data (VM Insights). Can create new inline. | ✅ |

**Notes:**
- Workspaces can be in a different subscription than the one being enabled
- If cross-subscription, additional RP registration and role assignments are needed (see [Prerequisites](emm-prerequisites.md))

### Tab 3: Security

Optional security add-ons.

| Feature | Description | Cost |
| ------- | ----------- | ---- |
| Foundational CSPM | Agentless, risk-prioritized cloud security posture insights. Always included. | Free |
| Defender CSPM | Advanced CSPM with attack path analysis. Optional toggle. | Paid |
| Defender for Cloud | Comprehensive server protection with EDR, vulnerability management, file integrity monitoring. Optional toggle. | Paid |

### Tab 4: Review & Enable

Displays a summary of all selections:
- Included features (always: Azure Monitor VM Insights, Azure Policy & Machine Configurations, Change Tracking & Inventory, Azure Update Manager)
- Selected scope (subscription, UAMI)
- Configure selections (Log Analytics workspace, Azure Monitor workspace)
- Security add-ons enabled
- Pricing information with links

Clicking **Enable** triggers:
1. Resource provider registrations on the target subscription
2. Cross-subscription RP registration if workspaces are in a different subscription
3. Subscription-level ARM template deployment

## What Happens After Enable

- A deployment is created: `ManagedOps_{uamiName}_{subscriptionId}`
- Policy assignments are created to configure all VMs in the subscription
- Remediation tasks are created for existing VMs
- New VMs added to the subscription are automatically enrolled
- The subscription appears in the browse view with status "Succeeded"
