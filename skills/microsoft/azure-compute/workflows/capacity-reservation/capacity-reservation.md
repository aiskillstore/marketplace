# Azure Capacity Reservation

Helps users create and configure Azure Capacity Reservation Groups (CRGs) to guarantee VM compute capacity in a specific region without deploying VMs.

## Reference Files

Read these before responding to the user:

| Signal                                           | Reference                                                                    |
|--------------------------------------------------|------------------------------------------------------------------------------|
| General CRG concepts, CLI commands, finding CRGs | [Capacity Reservation Overview](references/capacity-reservation-overview.md) |
| Associate/disassociate VM or VMSS with a CRG     | [Association & Disassociation](references/association-disassociation.md)     |

## When to Use This Workflow

Activate this workflow when the user explicitly asks about Capacity Reservation Groups (CRGs) or capacity reservations.

Also **proactively suggest** CRG when the user's scenario matches any of these patterns:

- **Deployment failure is unacceptable** — disaster recovery, customer-facing services, or mission-critical workloads where capacity unavailability would cause an outage
- **Known scale-out events** — product launches, seasonal traffic spikes, or planned migrations where capacity must be guaranteed ahead of time
- **In-demand SKUs** — GPU, high-memory, or new/popular VM sizes that are frequently capacity-constrained
- **Specific SKU + zone + region required** — the workload cannot fall back to a different size, zone, or region
- **Centralized capacity pooling** — capacity is being managed centrally across multiple subscriptions (CRGs support cross-subscription sharing)

> **Note:** CRGs are typically used for critical workloads only, not all deployments. They are SLA-backed but billed at pay-as-you-go rates whether capacity is consumed or not.

## Key Concepts

| Concept                           | Description                                                                                                      |
|-----------------------------------|------------------------------------------------------------------------------------------------------------------|
| **Capacity Reservation Group**    | A logical container that holds one or more capacity reservations; must be associated with VMs at deployment time |
| **Capacity Reservation**          | A reservation for a specific VM size and quantity in a specific Availability Zone                                |
| **Scope**                         | CRGs are scoped to a single Azure region and subscription                                                        |
| **Billing**                       | Charges begin as soon as the reservation is created, whether or not VMs are deployed against it                  |

## Workflow

### Step 1: Gather Requirements

Ask the user for (infer when possible, except where noted):

| Requirement              | Required | Notes                                                                                                                                                                                                  |
|--------------------------|----------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Region**               | Yes      | Infer from context if possible (e.g., eastus, westeurope)                                                                                                                                              |
| **VM size(s)**           | Yes      | e.g., Standard_D4s_v5, Standard_E8s_v5                                                                                                                                                                 |
| **Quantity**             | Yes      | **Always ask — do not infer.**                                                                                                                                                                         |
| **Availability Zone(s)** | No       | CRGs can be created without zones. Only include zones if the user explicitly requests a zonal reservation. **Do not pick a zone on the user's behalf** unless they explicitly ask for any/random zone  |
| **Resource group**       | Yes      | Existing or new resource group name                                                                                                                                                                    |

### Step 2: Create Capacity Reservation Group and Reservation

> ⚠️ **PowerShell users:** Replace `\` line continuations with backticks (`` ` ``) or collapse commands to a single line.

```bash
# Create the CRG
# Zonal (specify one or more zones the group will support):
az capacity reservation group create \
  -g <resource-group> \
  -n <crg-name> \
  -l <region> \
  --zones 1 2 3

# Non-zonal (omit --zones for regional-only reservations):
az capacity reservation group create \
  -g <resource-group> \
  -n <crg-name> \
  -l <region>

# Create the reservation
# If the CRG is zonal, specify --zone matching one of the group's zones.
# If the CRG is non-zonal, omit --zone.
az capacity reservation create \
  -g <resource-group> \
  -c <crg-name> \
  -n <reservation-name> \
  --sku <vm-size> \
  --capacity <quantity> \
  --zone <zone>            # omit if CRG is non-zonal
```

### Step 3: Verify Reservation

```bash
az capacity reservation show \
  -g <resource-group> \
  -c <crg-name> \
  -n <reservation-name> \
  --query "{name:name, sku:sku, capacity:sku.capacity, provisioningState:provisioningState}"
```

### Step 4: Offer Next Steps

- Associate VMs or VMSS with the Capacity Reservation Group at deployment time
- See [Capacity Reservation Overview](references/capacity-reservation-overview.md) for detailed guidance

## Managing Existing Reservations

For operations beyond creation, see the relevant section in the [Capacity Reservation Overview](references/capacity-reservation-overview.md):

- **Associate a VM or VMSS** with a CRG — see [Association & Disassociation](references/association-disassociation.md)
- **Disassociate a VM or VMSS** from a CRG — see [Association & Disassociation](references/association-disassociation.md)
- **Find a matching CRG** for a VM, or enumerate all reservations/groups — see [Finding Valid CRGs](references/capacity-reservation-overview.md#finding-valid-crgs-for-a-vm)

## Error Handling

| Scenario                             | Action                                                                                                                                                                                        |
|--------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| SKU not available in region/zone     | Run `az vm list-skus --location <region> --size <vm-size> --resource-type virtualMachines -o table`. Suggest alternatives from output                                                         |
| Quota exceeded                       | Use the **azure-quotas** skill to check usage and request an increase                                                                                                                         |
| Insufficient platform capacity       | Azure lacks physical hardware in the region/zone. Suggest a different zone, region, or VM size                                                                                                |
| Duplicate SKU + zone in CRG          | Only one reservation per VM size per zone (or per size if non-zonal) is allowed in a CRG. Update the existing reservation's capacity instead                                                  |
