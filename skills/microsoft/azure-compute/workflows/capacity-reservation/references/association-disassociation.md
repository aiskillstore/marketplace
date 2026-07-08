# Associating and Disassociating VMs/VMSS with a Capacity Reservation Group

## Association Model

```text
Capacity Reservation Group (CRG)
├── Capacity Reservation: Standard_D4s_v5 × 5 (Zone 1)
├── Capacity Reservation: Standard_D4s_v5 × 3 (Zone 2)
└── Capacity Reservation: Standard_E8s_v5 × 2 (Zone 1)

VM / VMSS
└── capacityReservationGroup.id = <CRG resource ID>
    └── Azure auto-matches to a reservation with the right VM size + zone
```

### Associating VMs

Set the `capacityReservationGroup` property when creating or updating a VM.

#### New VM

```bash
az vm create \
  -g <rg> \
  -n <vm-name> \
  --image <image> \
  --size Standard_D4s_v5 \
  --zone 1 \
  --capacity-reservation-group <crg-id>
```

#### Existing VM

Zonal VMs can be associated while running:

```bash
az vm update -g <rg> -n <vm-name> --capacity-reservation-group <crg-id>
```

Regional VMs (no zone) must be deallocated first:

```bash
az vm deallocate -g <rg> -n <vm-name>
az vm update -g <rg> -n <vm-name> --capacity-reservation-group <crg-id>
az vm start -g <rg> -n <vm-name>
```

### Associating VMSS

```bash
az vmss create \
  -g <rg> \
  -n <vmss-name> \
  --image <image> \
  --vm-sku Standard_D4s_v5 \
  --instance-count 5 \
  --zones 1 \
  --capacity-reservation-group <crg-id>
```

Existing VMSS can be associated using `az vmss update` similarly to VMs. Regional VMSS must be deallocated first. Zonal VMSS can be associated without deallocating, but this is currently a [Preview feature](https://learn.microsoft.com/en-us/azure/virtual-machines/capacity-reservation-associate-virtual-machine-scale-set).

## Disassociating from a Capacity Reservation Group

Both the VM/VMSS and the underlying capacity reservation logically occupy capacity. Azure imposes constraints to avoid ambiguous allocation states, so you cannot simply remove the association while resources are running against it.

There are three ways to disassociate. The commands below use `az vm` — for VMSS, substitute `az vmss` and add `az vmss update-instances --instance-ids "*"` as a final step when using a **Manual** upgrade policy.

### Option 1: Deallocate, then remove association

Best when the VM/VMSS can tolerate downtime.

```bash
az vm deallocate -g <rg> -n <vm-name>
az vm update -g <rg> -n <vm-name> --capacity-reservation-group None
az vm start -g <rg> -n <vm-name>   # optional
```

### Option 2: Set reserved quantity to zero, then remove association

Best when the VM/VMSS cannot be deallocated and the reservation is no longer needed.

```bash
az capacity reservation update \
  -g <rg> --capacity-reservation-group <crg> \
  -n <reservation-name> --capacity 0
az vm update -g <rg> -n <vm-name> --capacity-reservation-group None
```

### Option 3: Delete the VM/VMSS

Deleting the resource automatically removes the association. Some latency may occur before the capacity reservation allocation state updates.

### VMSS Upgrade Policy Behavior

| Policy        | Behavior                                                               |
|---------------|------------------------------------------------------------------------|
| **Automatic** | Instances update automatically — no further action needed              |
| **Rolling**   | Instances update in batches with an optional pause between them        |
| **Manual**    | You must run `az vmss update-instances --instance-ids "*"` per update  |

## Learn More

- [Associate a VM to a Capacity Reservation Group](https://learn.microsoft.com/en-us/azure/virtual-machines/capacity-reservation-associate-vm)
- [Remove/disassociate a VM from a Capacity Reservation Group](https://learn.microsoft.com/en-us/azure/virtual-machines/capacity-reservation-remove-vm)
- [Remove/disassociate a VMSS from a Capacity Reservation Group](https://learn.microsoft.com/en-us/azure/virtual-machines/capacity-reservation-remove-virtual-machine-scale-set)
