# Step 5 — First Model Deployment

**Goal**: Deploy a starter model that fits the cluster's GPU capacity and reach `Ready` status.

**Model recommendations** (based on cluster VRAM from Step 3 — see [gpu-profiles.md](../gpu-profiles.md) for full sizing guide):

| Cluster Capacity | Recommended Model | Provider | Notes |
|-----------------|-------------------|----------|-------|
| CPU-only | `google/gemma-3-1b-it-qat-q8_0-gguf` | KAITO (llama.cpp) | GGUF Q8 quantized; runs on CPU |
| 1× T4 (16 GB) | `microsoft/Phi-3-mini-4k-instruct` | KAITO (vLLM) | Small, fast; fits T4 with headroom |
| 1× A10G or L4 (24 GB) | `meta-llama/Llama-3.1-8B-Instruct` | KAITO (vLLM) | Good general-purpose starter (gated — needs HF token) |
| 1× A100 40 GB | `microsoft/Phi-3-medium-128k-instruct` | KAITO (vLLM) | ~28 GB float16; non-gated; MIT license |
| 1× A100 80 GB / H100 | `meta-llama/Llama-3.1-8B-Instruct` | KAITO (vLLM) | Oversized for 8B; suggest 70B with tensor parallelism if more GPUs available |
| 4× A100 80 GB | `meta-llama/Llama-3.1-70B-Instruct` | KAITO (vLLM, tensor parallel) | Large model; requires tensor parallelism; gated — needs HF token |

Present recommendation. Ask user to confirm or choose their own model.

## Naming Convention

- **`model-name`**: A DNS-safe Kubernetes resource name derived from the model ID (e.g., `meta-llama/Llama-3.1-8B-Instruct` → `llama-3-1-8b-instruct`)
- **`model-id`**: The full HuggingFace model identifier (e.g., `meta-llama/Llama-3.1-8B-Instruct`)

## Gated Models (HuggingFace Token)

Llama-family models are gated on HuggingFace and require an access token. Read the token interactively to avoid exposing it in shell history:

```bash
# Read token without echo, store in a securely permissioned temp file
hf_token_file="$(mktemp)"
trap 'rm -f "$hf_token_file"' EXIT

read -r -s -p "Enter HuggingFace token: " hf_token
printf '\n'
printf '%s' "$hf_token" > "$hf_token_file"
chmod 600 "$hf_token_file"
unset hf_token

kubectl create secret generic hf-token \
  --from-file=token="$hf_token_file" \
  -n <namespace> \
  --dry-run=client -o yaml | kubectl apply -f -
```

> See [powershell-notes.md](../powershell-notes.md) for the PowerShell equivalent.

## Apply the ModelDeployment CR

Use the appropriate manifest based on whether the model is gated.

**For gated models (Llama etc. — requires HuggingFace token):**

```bash
kubectl apply -f - <<EOF
apiVersion: airunway.ai/v1alpha1
kind: ModelDeployment
metadata:
  name: <model-name>
  namespace: <namespace>
spec:
  model:
    id: <model-id>
    huggingFaceTokenSecretRef:
      name: hf-token
      key: token
  provider:
    name: <provider-name>
EOF
```

**For non-gated models (Phi-3, Gemma etc. — no token required):**

```bash
kubectl apply -f - <<EOF
apiVersion: airunway.ai/v1alpha1
kind: ModelDeployment
metadata:
  name: <model-name>
  namespace: <namespace>
spec:
  model:
    id: <model-id>
  provider:
    name: <provider-name>
EOF
```

> See [powershell-notes.md](../powershell-notes.md) for the PowerShell equivalent.

## Monitor Deployment

```bash
kubectl get modeldeployment <model-name> -n <namespace> -w
```

Wait until `STATUS = Ready`. If not ready within 10 minutes:
- `kubectl describe modeldeployment <model-name> -n <namespace>` — check events
- `kubectl get pods -l modeldeployment=<model-name> -n <namespace>` — check pod status

> **Note:** Large models (13B+) may take significantly longer than 10 minutes because weights must be downloaded first. For 70B models, expect 20–40+ minutes depending on network speed. Check pod logs to confirm download progress rather than assuming failure.
