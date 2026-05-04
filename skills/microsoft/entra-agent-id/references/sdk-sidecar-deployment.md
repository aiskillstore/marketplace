# SDK Sidecar — Code Patterns, Deployment, and Security

Companion to [sdk-sidecar.md](sdk-sidecar.md). This file covers calling-side code patterns in Python and TypeScript, container deployment manifests, security hardening, and troubleshooting.

## Code Patterns

### Autonomous 3P Agent (Python)

```python
import os
import requests

SIDECAR_URL = os.environ.get("SIDECAR_URL", "http://localhost:5000")
AGENT_APP_ID = os.environ["AGENT_CLIENT_ID"]

def get_agent_token(downstream_api: str = "Graph") -> str:
    url = f"{SIDECAR_URL}/AuthorizationHeaderUnauthenticated/{downstream_api}"
    resp = requests.get(url, params={"AgentIdentity": AGENT_APP_ID}, timeout=30)
    resp.raise_for_status()
    return resp.json()["authorizationHeader"]

def call_downstream_api(endpoint: str) -> dict:
    token = get_agent_token()
    resp = requests.get(endpoint, headers={"Authorization": token}, timeout=10)
    resp.raise_for_status()
    return resp.json()
```

### Interactive (OBO) Agent (Python)

```python
def get_delegated_token(user_token: str, downstream_api: str = "Graph") -> str:
    url = f"{SIDECAR_URL}/AuthorizationHeader/{downstream_api}"
    resp = requests.get(
        url,
        headers={"Authorization": f"Bearer {user_token}"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["authorizationHeader"]
```

### Autonomous Agent (TypeScript)

```typescript
const SIDECAR_URL = process.env.SIDECAR_URL ?? "http://localhost:5000";
const AGENT_APP_ID = process.env.AGENT_CLIENT_ID!;

async function getAgentToken(downstreamApi = "Graph"): Promise<string> {
  const url = new URL(
    `/AuthorizationHeaderUnauthenticated/${downstreamApi}`,
    SIDECAR_URL,
  );
  url.searchParams.set("AgentIdentity", AGENT_APP_ID);

  const res = await fetch(url.toString());
  if (!res.ok) {
    const errorText = await res.text().catch(() => "");
    throw new Error(
      `SDK error: ${res.status}${errorText ? ` - ${errorText}` : ""}`,
    );
  }
  const data = await res.json();
  return data.authorizationHeader;
}
```

### Token Validation Middleware

```python
def validate_incoming_token(bearer_token: str) -> dict:
    resp = requests.get(
        f"{SIDECAR_URL}/Validate",
        headers={"Authorization": f"Bearer {bearer_token}"},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()["claims"]
```

### Direct Downstream Call via SDK

```python
def call_graph_me(user_token: str) -> dict:
    resp = requests.get(
        f"{SIDECAR_URL}/DownstreamApi/Graph",
        params={"optionsOverride.RelativePath": "me"},
        headers={"Authorization": f"Bearer {user_token}"},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()["content"]
```

## Deployment

### Docker Compose (Development)

```yaml
version: '3.8'
services:
  sidecar:
    image: mcr.microsoft.com/entra-sdk/auth-sidecar:1.0.0-azurelinux3.0-distroless
    ports:
      - "5001:5000"
    environment:
      - AzureAd__Instance=https://login.microsoftonline.com/
      - AzureAd__TenantId=${TENANT_ID}
      - AzureAd__ClientId=${BLUEPRINT_APP_ID}
      - AzureAd__ClientCredentials__0__SourceType=ClientSecret
      - AzureAd__ClientCredentials__0__ClientSecret=${BLUEPRINT_CLIENT_SECRET}
      - DownstreamApis__Graph__BaseUrl=https://graph.microsoft.com/v1.0/
      - DownstreamApis__Graph__Scopes__0=https://graph.microsoft.com/.default
      - DownstreamApis__Graph__RequestAppToken=true
      - ASPNETCORE_URLS=http://+:5000

  agent:
    build: ./agent
    ports:
      - "3000:3000"
    environment:
      - SIDECAR_URL=http://sidecar:5000
      - AGENT_CLIENT_ID=${AGENT_CLIENT_ID}
    depends_on:
      - sidecar
```

### Kubernetes (Production)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agent-deployment
spec:
  replicas: 3
  template:
    metadata:
      labels:
        app: agent
        azure.workload.identity/use: "true"
    spec:
      serviceAccountName: agent-sa
      containers:
      - name: agent
        image: myregistry/agent:latest
        env:
        - name: SIDECAR_URL
          value: "http://localhost:5000"
      - name: sidecar
        image: mcr.microsoft.com/entra-sdk/auth-sidecar:1.0.0-azurelinux3.0-distroless
        ports:
        - containerPort: 5000
        env:
        - name: AzureAd__TenantId
          valueFrom:
            configMapKeyRef:
              name: agent-config
              key: tenant-id
        - name: AzureAd__ClientId
          valueFrom:
            configMapKeyRef:
              name: agent-config
              key: client-id
        - name: AzureAd__ClientCredentials__0__SourceType
          value: "SignedAssertionFilePath"
        - name: Kestrel__Endpoints__Http__Url
          value: "http://127.0.0.1:5000"
        resources:
          requests: { memory: "128Mi", cpu: "100m" }
          limits: { memory: "256Mi", cpu: "250m" }
        livenessProbe:
          httpGet: { path: /healthz, port: 5000 }
          initialDelaySeconds: 10
        readinessProbe:
          httpGet: { path: /healthz, port: 5000 }
          initialDelaySeconds: 5
```

## Security

> ⚠️ The SDK API must NOT be publicly accessible. Pod-local or same-Docker-network only.

1. **Bind to localhost** — `Kestrel__Endpoints__Http__Url=http://127.0.0.1:5000`
2. **Never expose via LoadBalancer or Ingress**
3. **Use Workload Identity in AKS** — `SignedAssertionFilePath` over client secrets
4. **Use Key Vault for certificates** — `SourceType=KeyVault` in production
5. **Separate ConfigMap from Secrets** in Kubernetes

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| 404 on `/AuthorizationHeader/{name}` | `{name}` not in config | Add `DownstreamApis__{name}__BaseUrl` env var |
| 400 `AgentUsername requires AgentIdentity` | Missing `AgentIdentity` param | Always pair user params with `AgentIdentity` |
| 400 `mutually exclusive` | Both `AgentUsername` and `AgentUserId` | Use one or the other |
| 401 on `/Validate` | Invalid/expired inbound token | Check token audience matches `AzureAd__ClientId` |
| 500 token acquisition failure | Wrong creds or missing admin consent | `kubectl logs <pod> -c sidecar` |
| Connection refused | SDK not ready or wrong URL | Verify `SIDECAR_URL` and `/healthz` |
