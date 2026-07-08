# EMM Overview

Essential Machine Management (EMM) simplifies onboarding and configuration of management for Azure VMs and Arc-enabled servers at the subscription level.

## What is EMM?

When you enable a subscription for EMM, all VMs and Arc-enabled servers in that subscription are automatically enrolled and configured with a curated set of management features. Any new VMs added to the subscription are also automatically enrolled.

## Features Included

### Essentials Tier (Always Enabled)

| Feature | Description |
| ------- | ----------- |
| Azure Monitor VM Insights | Monitors VM performance and health, configures metric-based recommended alerts |
| Azure Update Manager | Automates OS update deployment |
| Azure Machine Configuration | Audits Azure security baseline policy |
| Change Tracking & Inventory | Tracks VM configuration changes, maintains resource inventory |

### Security Tier (Optional Add-ons)

| Feature | Description | Cost |
| ------- | ----------- | ---- |
| Foundational CSPM | Agentless, risk-prioritized security posture insights | Free |
| Defender CSPM | Advanced CSPM with attack path analysis | Paid |
| Defender for Cloud | EDR, vulnerability management, file integrity monitoring, threat detection | Paid |

## Pricing

- **Azure VMs:** Essentials tier features at no extra charge
- **Arc-enabled servers with Windows Server SA/PayGo/ESU:** No extra charge
- **Other Arc-enabled servers:** $9/server/month once billing is enabled (future date, currently free in preview)
- **Change Tracking & Inventory logs:** Incur separate Log Analytics ingestion charges
- **Security tier add-ons:** Standard Microsoft Defender pricing applies

## Key Characteristics

- **Subscription-level scope:** Enables for all VMs in a subscription at once
- **No VM exclusion:** Currently no ability to exclude individual VMs
- **Existing services preserved:** If a VM already has Update Manager with a maintenance schedule, it keeps that schedule
- **REST API available:** Official docs focus on the portal experience, but a REST API (`Microsoft.ManagedOps`) is available and used by the Copilot-guided flow
- **Resource type:** `Microsoft.ManagedOps/ManagedOps`

## Documentation Links

- [Essential Machine Management (Preview)](https://learn.microsoft.com/en-us/azure/operations/configuration-enrollment)
- [Troubleshoot EMM](https://learn.microsoft.com/en-us/azure/operations/configuration-enrollment-troubleshoot)
