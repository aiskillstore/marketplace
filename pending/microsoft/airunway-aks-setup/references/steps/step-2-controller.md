# Step 2 — Controller Status & Installation

**Goal**: Ensure the AI Runway controller and CRDs are installed and healthy.

```bash
# Check CRD presence
kubectl get crd modeldeployments.airunway.ai

# Check controller pod health
kubectl get pods -n airunway-system -l control-plane=controller-manager
```

**If already installed and healthy:** Report version and pod status, skip to Step 3.

**If not installed:** Ask user to confirm, then from the **repository root** run:

```bash
make controller-install   # Install CRDs
make controller-deploy    # Deploy controller manager
```

> **Note:** `make` targets must be run from the AI Runway repository root.

Verify rollout:

```bash
kubectl rollout status deployment/airunway-controller-manager -n airunway-system --timeout=120s
```

**Error handling:**
- `CrashLoopBackOff` → `kubectl logs -n airunway-system -l control-plane=controller-manager --previous`
- Rollout timeout → `kubectl describe deployment airunway-controller-manager -n airunway-system`
- `No rule to make target` → Navigate to repo root and retry
