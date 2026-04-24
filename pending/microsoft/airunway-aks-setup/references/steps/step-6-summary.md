# Step 6 — Summary & Smoke Test

**Goal**: Confirm everything is working and guide the user on next steps.

Report:
- Cluster context and node inventory (Step 1)
- Controller version and namespace (Step 2)
- GPU types and constraints in effect (Step 3)
- Provider installed and registration status (Step 4)
- Model deployed and endpoint URL (Step 5)

## Smoke Test

Retrieve the endpoint and test it (only after `STATUS = Ready`):

> Replace `<namespace>` with the namespace used during deployment (default: `default`).

```bash
ENDPOINT=$(kubectl get modeldeployment <model-name> -n <namespace> -o jsonpath='{.status.endpoint}')

if [ -z "$ENDPOINT" ]; then
  echo "Endpoint not yet available — model may still be starting"
else
  curl -X POST "${ENDPOINT}/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -d '{"model": "<model-id>", "messages": [{"role": "user", "content": "Hello!"}]}'
fi
```

> **If the endpoint is a cluster-internal URL** (e.g., `http://svc-name.namespace:port`), set up port-forwarding first:
>
> ```bash
> # Discover the service port (vLLM: 8000, llama.cpp: 8080)
> SERVICE_PORT=$(kubectl get svc <service-name> -n <namespace> -o jsonpath='{.spec.ports[0].port}')
>
> kubectl port-forward svc/<service-name> 8080:${SERVICE_PORT} -n <namespace> &
> # Then use http://localhost:8080 as the endpoint
> ```

> See [powershell-notes.md](../powershell-notes.md) for the PowerShell equivalent.

**Expected output:** A JSON response with a `choices` array containing the model's reply.

**Suggest next steps:**
- Open the AI Runway Web UI to browse and deploy additional models
- Configure an ingress gateway for external access
- Review `controller/config/samples/` for advanced ModelDeployment options
