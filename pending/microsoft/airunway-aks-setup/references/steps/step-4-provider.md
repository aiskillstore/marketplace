# Step 4 — Provider Recommendation & Installation

**Goal**: Select and install the right inference provider for the detected hardware.

```bash
# Check if providers are already registered
kubectl get inferenceproviderconfigs --all-namespaces 2>/dev/null || kubectl get inferenceproviderconfigs
```

> See [powershell-notes.md](../powershell-notes.md) for the PowerShell equivalent.

**If providers already registered:** Show name and status, skip installation.

**Provider recommendation logic:**

| Hardware | Use Case | Recommended Provider |
|----------|----------|---------------------|
| CPU-only | Any | KAITO (llama.cpp) |
| GPUs | Standard inference (most users start here) | KAITO |
| GPUs | High-throughput serving with separate prefill/decode phases | Dynamo |
| GPUs | Already using Ray for ML workloads | KubeRay |

> **Default to KAITO** unless the user has a specific reason to choose otherwise. KAITO is the simplest to set up and handles most use cases. Dynamo is for teams that need to independently scale the prefill and decode stages of inference for high throughput. KubeRay is for teams already invested in the Ray ecosystem.

Present recommendation with reasoning. Ask user to confirm before installing.

**Installation** — from the **repository root**:

First, check the provider's Makefile or README for the default image:

```bash
# List available providers and their default images
ls providers/
cat providers/<provider>/Makefile | grep -E 'IMG\s*\?='
```

> See [powershell-notes.md](../powershell-notes.md) for the PowerShell equivalent.

Then deploy:

```bash
cd providers/<provider>
make deploy IMG=<image>
```

> **Tip:** If the Makefile defines a default `IMG`, you can omit the `IMG=` argument and just run `make deploy`.

**Verify registration:**

```bash
kubectl get inferenceproviderconfigs <provider> -o yaml
```

Check `status.ready: true`. If not ready within 2 minutes, inspect provider pod logs with `kubectl logs <pod-name>` and optionally use `kubectl describe pod <pod-name>` to review events and pod status.
