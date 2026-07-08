# MCP Integration Reference

Loaded when troubleshooting MCP tool calls, debugging the fallback chain, or understanding the API response format.

---

## Tool Discovery

Always call `mcp_azure_mcp_aks` first to discover the current available tool surface. Do not assume a fixed action name — the available actions depend on the MCP server version deployed to the client.

```javascript
mcp_azure_mcp_aks({ action: "discover" })
```

The response lists available actions and their parameter schemas. Use the returned schema — do not hardcode parameter names.

---

## Assessment Call

After calling `discover`, use the assessment action name returned in the response. Pass parameters according to the discovered schema — do not hardcode action names or API versions.

Typical parameters include:
- `subscriptionId` — Azure subscription ID
- `resourceGroupName` — resource group containing the cluster
- `resourceName` — AKS cluster name
- `scope` (optional) — filter by namespaces or workload types

Example shape (use actual action name and schema from discover output):
```javascript
mcp_azure_mcp_aks({
  action: "<action-from-discover>",
  subscriptionId: "<subscription-id>",
  resourceGroupName: "<resource-group>",
  resourceName: "<cluster-name>",
  scope: {
    excludeNamespaces: ["kube-system", "gatekeeper-system", "azure-arc"],
    workloadTypes: ["Deployment", "StatefulSet", "DaemonSet", "CronJob", "Job"]
  }
})
```

All `scope` parameters are optional. If omitted, the API assesses all workloads excluding `kube-system` and `gatekeeper-system`.

---

## Required Permissions

```bash
# Check current role assignments
az role assignment list \
  --assignee $(az ad signed-in-user show --query id -o tsv) \
  --scope /subscriptions/<subscription-id>/resourceGroups/<rg>/providers/Microsoft.ContainerService/managedClusters/<cluster>

# Minimum permissions required:
# - Microsoft.ContainerService/managedClusters/read
# - Microsoft.ContainerService/managedClusters/listClusterUserCredential/action

# Assign if missing (requires Owner or User Access Administrator)
az role assignment create \
  --assignee <principal-id> \
  --role "Azure Kubernetes Service Cluster User Role" \
  --scope /subscriptions/<subscription-id>/resourceGroups/<rg>/providers/Microsoft.ContainerService/managedClusters/<cluster>
```

---

## Response Schema

The API returns three top-level sections:

### `summary`
```json
{
  "summary": {
    "totalWorkloads": 42,
    "compatible": 27,
    "requiresChanges": 12,
    "incompatible": 3,
    "autoFixed": 8,
    "clusterConfigIssues": 4
  }
}
```

### `clusterConfiguration`
```json
{
  "clusterConfiguration": [
    {
      "constraintId": "cluster-oidc-issuer",
      "severity": "requiresChanges",
      "description": "OIDC issuer not enabled",
      "remediation": "az aks update --enable-oidc-issuer --resource-group <rg> --name <cluster>",
      "documentationUrl": "https://learn.microsoft.com/azure/aks/..."
    }
  ]
}
```

### `workloads[]`
```json
{
  "workloads": [
    {
      "name": "sample-app",
      "namespace": "default",
      "kind": "Deployment",
      "overallStatus": "requiresChanges",
      "issues": [
        {
          "constraintId": "safeguard-images-no-latest",
          "severity": "requiresChanges",
          "description": "Container 'web' uses :latest image tag",
          "field": "/spec/containers/0/image",
          "suggestedPatch": null,
          "remediationGuide": "Pin the image to a specific version or SHA digest"
        }
      ]
    }
  ]
}
```

---

## Async Response Handling (HTTP 202 — Large Clusters)

For clusters with 500+ workloads, the API returns HTTP 202 Accepted with a `Location` header. Poll until complete:

```javascript
// Initial call returns: { status: 202, headers: { Location: "...", "Retry-After": "30" } }
async function pollAssessment(locationUrl, retryAfterSeconds) {
  while (true) {
    await new Promise(r => setTimeout(r, retryAfterSeconds * 1000));
    const response = await mcp_azure_mcp_aks({
      action: "pollOperation",
      locationUrl: locationUrl
    });
    if (response.status === "Succeeded") return response.result;
    if (response.status === "Failed") throw new Error(response.error.message);
    retryAfterSeconds = response.retryAfter ?? retryAfterSeconds;
  }
}
```

---

## Fallback Chain

Attempt each step in order. Do not ask the user which is available — just try:

```
1. mcp_azure_mcp_aks → discover, then call the assessment action returned
   ↓ fails (tool not found — Azure MCP server not configured)

2. Inform user to install Azure MCP, then fall back to offline validation
   kubectl get deployment,statefulset,daemonset,job,cronjob -A -o yaml > /tmp/workloads.yaml
   kubectl get pdb,storageclass -A -o yaml > /tmp/policies.yaml
```

If `mcp_azure_mcp_aks` is not available, say:
> "The Azure MCP server is not configured. To enable live cluster assessment, install it following [aka.ms/azure-mcp-setup](https://aka.ms/azure-mcp-setup). For now, I can validate your local manifests offline — export them with `kubectl get ... -o yaml` or share your manifest files."

Then proceed to offline manifest validation against `constraint-spec-v1.yaml`.

---

## Prerequisites Verification

Run these before attempting MCP or CLI assessment:

```bash
# 1. Verify Azure login
az account show --query "{name:name, id:id, state:state}" -o table

# 2. Verify cluster exists and is accessible
az aks show \
  --resource-group <rg> \
  --name <cluster> \
  --query "{name:name, provisioningState:provisioningState, sku:sku.name}" \
  -o table

# 3. Verify kubectl context
kubectl config current-context
kubectl cluster-info
```

```javascript
// 4. Verify MCP server is reachable (Azure MCP)
// If this returns available actions, MCP is configured
mcp_azure_mcp_aks({ action: "discover" })
```

---

## Common MCP Errors

| Error | Cause | Fix |
|---|---|---|
| `tool not found: mcp_azure_mcp_aks` | Azure MCP server not configured | Guide user to install: [aka.ms/azure-mcp-setup](https://aka.ms/azure-mcp-setup), then fall back to offline |
| `HTTP 401 Unauthorized` | Not logged in | `az login` |
| `HTTP 403 Forbidden` | Insufficient RBAC permissions | Ensure caller has read access to the cluster via AKS APIs |
| `HTTP 404 Not Found` | Wrong subscription, RG, or cluster name | Verify with `az aks list -o table` |
| `HTTP 202` with no Location header | API version mismatch | Ensure the MCP server version supports async polling; retry with the latest server |
| Timeout after 30s | Cluster too large (500+ workloads) | Implement async polling — see section above |
