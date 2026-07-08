# AKS Automatic Migration Guide

Loaded when user asks about migration steps or after assessment is complete.

---

## Migration Checklist

### Phase 1 — Assessment (this skill)

- [ ] Run the AKS Automatic compatibility assessment (via `mcp_azure_mcp_aks({ action: "discover" })` then the assessment action returned, or the offline manifest scan)
- [ ] Resolve all `incompatible` findings — these are hard blockers
- [ ] Apply all `requiresChanges` fixes — these will be denied at admission
- [ ] Review `autoFixed` items — understand what AKS Automatic will mutate at runtime
- [ ] Address cluster-level Day-0 config issues (see below)

### Phase 2 — Create AKS Automatic Cluster (use `azure-kubernetes` skill)

```bash
az aks create \
  --resource-group <resource-group> \
  --name <new-cluster-name> \
  --sku automatic \
  --location <location> \
  --generate-ssh-keys
```

> 💡 **Tip:** AKS Automatic auto-enables: OIDC issuer, workload identity, Azure CNI Overlay, NAP, VPA, Azure Monitor Container Insights, Deployment Safeguards, and Pod Security Standards (Baseline). No manual configuration needed for these.

### Phase 3 — Validate on New Cluster

```bash
# Get credentials
az aks get-credentials \
  --resource-group <resource-group> \
  --name <new-cluster-name>

# Dry-run server-side apply — catches admission policy rejections
kubectl apply --dry-run=server -f <manifests-directory>/

# Deploy to a staging namespace first
kubectl create namespace staging
kubectl apply -f <manifests-directory>/ -n staging

# Watch pod startup
kubectl get pods -n staging -w

# Check events for admission rejections
kubectl get events -n staging --sort-by=.lastTimestamp | grep -i "denied\|error\|failed"
```

> ⚠️ **Keep the old cluster running** for a rollback window (recommended: 48 hours minimum) while you validate workloads on the new AKS Automatic cluster.

### Phase 4 — Decommission Old Cluster

```bash
# Only after confirming workloads are stable on AKS Automatic
az aks delete \
  --resource-group <resource-group> \
  --name <old-cluster-name> \
  --yes --no-wait
```

---

## Day-0 Decisions — Cluster-Level Configuration Requirements

Some settings require creating a **new** cluster; others can be enabled on existing clusters. Route to `azure-kubernetes` skill for cluster creation.

| Requirement | AKS Automatic default | What to do |
|---|---|---|
| API Server VNet Integration | Required, auto-enabled | Requires a new cluster |
| Network plugin | Azure CNI Overlay | Requires a new cluster if currently on kubenet |
| System node pool OS | Azure Linux | Recreate system node pool (user pools unaffected) |
| OIDC Issuer | Auto-enabled | Can be enabled on existing: `az aks update --enable-oidc-issuer` |
| Workload Identity | Auto-enabled | Can be enabled on existing: `az aks update --enable-workload-identity` |

---

## What AKS Automatic Auto-Enables

No manual setup needed for these — show this list when user asks "what do I get for free":

| Feature | Benefit |
|---|---|
| Node Auto Provisioning (NAP) | Replaces cluster autoscaler; right-sizes node pools automatically |
| Vertical Pod Autoscaler (VPA) | Auto-tunes resource requests after deployment |
| Azure Monitor Container Insights | Logs, metrics, and dashboards out of the box |
| Deployment Safeguards | 25 active deny policies + 2 webhook mutators at admission (resource-requests defaults + anti-affinity/topology-spread) |
| Pod Security Standards (Baseline) | Enforced cluster-wide; Restricted available opt-in |
| Managed OIDC Issuer | Required for workload identity |
| Azure Key Vault CSI Driver | Secret injection without static credentials |
| Ephemeral OS disks | Faster node provisioning by default |
| Azure Linux node OS | Smaller footprint, faster boot times |

---

## Post-Migration Verification Commands

```bash
# Verify all pods running
kubectl get pods -A | grep -v Running | grep -v Completed

# Check for pods stuck in Pending (may indicate resource quota or node issues)
kubectl get pods -A --field-selector status.phase=Pending

# Check Deployment Safeguards are active
kubectl get constrainttemplate -A

# Verify VPA is running
kubectl get vpa -A

# Check NAP node pools
az aks nodepool list \
  --resource-group <resource-group> \
  --cluster-name <cluster-name> \
  --query "[].{name:name, mode:mode, osType:osType, count:count}" \
  -o table

# View Container Insights metrics
az aks show \
  --resource-group <resource-group> \
  --name <cluster-name> \
  --query addonProfiles.omsagent.enabled
```
