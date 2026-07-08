# Capacity Reservation Overview

Reference material for Azure Capacity Reservation Groups and Capacity Reservations.

## What Is a Capacity Reservation Group?

A Capacity Reservation Group (CRG) is a logical container for one or more capacity reservations. It acts as the association point for VMs and VMSS — you associate a VM or scale set with the **group**, and Azure matches the VM to a suitable reservation within that group.

## Constraints

| Constraint                     | Detail                                                                                                     |
|--------------------------------|------------------------------------------------------------------------------------------------------------|
| **Region-scoped**              | A CRG and all its reservations must be in the same Azure region                                            |
| **Zone-specific**              | Each reservation targets a specific Availability Zone (or is non-zonal)                                    |
| **Subscription-scoped**        | A CRG lives in a single subscription but can be shared with other subscriptions via the `sharing` property |
| **VM size per reservation**    | Each capacity reservation covers exactly one VM size                                                       |
| **Billing starts immediately** | You are charged for reserved capacity whether or not VMs are running against it                            |

## Association and Disassociation

See [association-disassociation.md](association-disassociation.md) for how to associate and disassociate VMs/VMSS with a CRG.

## Common CLI Commands

| Action                      | Command                                                                                                     |
|-----------------------------|-------------------------------------------------------------------------------------------------------------|
| List CRGs                   | `az capacity reservation group list`                                                                        |
| Show CRG                    | `az capacity reservation group show -g <rg> -n <crg> --instance-view`                                       |
| Delete CRG                  | `az capacity reservation group delete -g <rg> -n <crg>`                                                     |
| List reservations           | `az capacity reservation list -g <rg> --capacity-reservation-group <crg>`                                   |
| Update reservation quantity | `az capacity reservation update -g <rg> --capacity-reservation-group <crg> -n <res> --capacity <new-count>` |
| Delete reservation          | `az capacity reservation delete -g <rg> --capacity-reservation-group <crg> -n <res>`                        |

## Finding Valid CRGs for a VM

To associate a VM with a CRG, the CRG must contain a capacity reservation that matches the VM's **size**, **region**, and **zone** (if zonal). While `az capacity reservation group list` can enumerate CRGs at the subscription level, filtering down to matching reservations across many groups is inefficient. Azure Resource Graph is recommended for cross-resource-group discovery.

### Option 1: Azure Resource Graph (recommended)

ARG can query all capacity reservations across resource groups in a single call, filtering by location, VM size, and zone. This is the most efficient approach.

> ⚠️ **Prerequisite:** `az extension add --name resource-graph`

You must collapse this query to a **single line** before running it:

```bash
az graph query -q "
  Resources
  | where type =~ 'Microsoft.Compute/capacityReservationGroups/capacityReservations'
  | where location =~ '<region>'
  | where properties.provisioningState =~ 'Succeeded'
  | where sku.name =~ '<vm-size>'
  | project id,
            crgId = extract('(.*)/capacityReservations', 1, id),
            resourceGroup,
            zones,
            size = sku.name,
            capacity = coalesce(sku.capacity, 0),
            associationCount = coalesce(array_length(properties.virtualMachinesAssociated), 0),
            location
" --query "data[]" -o table
```

The `crgId` in the output is the parent Capacity Reservation Group resource ID — this is the value to use when associating a VM or VMSS.

To further narrow results for zonal VMs, add a zone filter:

```kql
| where zones has '<zone>'
```

### Option 2: CLI enumeration

If ARG is unavailable, list CRGs per resource group and inspect their reservations:

```bash
# List all CRGs
az capacity reservation group list -o table

# List reservations within a CRG and check for matching size/capacity
az capacity reservation list \
  -g <rg> \
  --capacity-reservation-group <crg-name> \
  --query "[?sku.name=='<vm-size>'].{name:name, size:sku.name, capacity:sku.capacity, zones:zones}" \
  -o table
```

## Estimating Reservation Cost

Capacity reservations are billed at the same pay-as-you-go rate as the underlying VM size, whether or not VMs are running against them. Use the [Retail Prices API guide](../../../references/retail-prices-api.md) (unauthenticated) to look up hourly rates.

**Estimated monthly cost:** `quantity × hourly rate × 730`

> ⚠️ Prices returned are **estimates based on current retail pay-as-you-go rates**, not a final cost or contractual commitment. Actual charges may vary due to taxes, discounts (Reserved Instances, Savings Plans), or price changes.

## Important Notes

- **Deletion is blocked until prerequisites are met:** Azure rejects a CRG delete unless all VMs/VMSS are disassociated and all capacity reservations are deleted. Order: disassociate VMs/VMSS → delete reservations → delete group.
- **Quota required:** Capacity reservations consume vCPU quota just like running VMs.

## Learn More

- [Azure Capacity Reservations documentation](https://learn.microsoft.com/en-us/azure/virtual-machines/capacity-reservation-overview)
- [Create a Capacity Reservation](https://learn.microsoft.com/en-us/azure/virtual-machines/capacity-reservation-create)
- [Association and disassociation](association-disassociation.md)
