# Step 1 — Cluster Verification

**Goal**: Confirm prerequisites are met, validate the cluster connection, and inventory available nodes and GPUs.

## Prerequisites

Verify required CLI tools are available before proceeding:

```bash
# Check all required tools are installed
for tool in kubectl make curl; do
  command -v "$tool" >/dev/null 2>&1 && echo "✓ $tool found" || echo "✗ $tool NOT FOUND — install before continuing"
done
```

> See [powershell-notes.md](../powershell-notes.md) for the PowerShell equivalent.

If any tool is missing, **STOP** and tell the user which tools to install before continuing.

## Cluster Connection

```bash
# Confirm active context
kubectl config current-context

# Inventory all nodes
kubectl get nodes -o wide
```

## GPU Detection

```bash
# Extract GPU count and model per node (requires NVIDIA device plugin labels)
kubectl get nodes -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.allocatable['\''nvidia.com/gpu'\'']}{"\t"}{.metadata.labels['\''nvidia.com/gpu.product'\'']}{"\n"}{end}'
```

> **Note:** The above command relies on `nvidia.com/gpu.product` node labels, which are set by the NVIDIA device plugin or GPU operator. If the output shows empty GPU fields, try the fallback:
>
> ```bash
> # Fallback: check node descriptions for GPU capacity
> kubectl describe nodes | grep -A 5 "Allocatable:" | grep -i nvidia
> ```
>
> If neither approach shows GPUs but you know the nodes have GPU hardware, the NVIDIA device plugin may not be installed yet. Guide the user to install it before proceeding.

**Report to user:**
- Cluster context name
- Total node count and GPU node count
- Per GPU type: model, count, VRAM per card, total cluster VRAM

**Decision logic:**
- No kubeconfig context → **STOP**. Tell user to configure `kubeconfig` (e.g., `az aks get-credentials`) and retry.
- No GPU nodes detected → Note "CPU-only cluster" and proceed; CPU-only inference is available via KAITO + llama.cpp.
