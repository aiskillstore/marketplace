# Microsoft Entra SDK for AgentID: Polyglot Agent Authentication

Containerized companion service that handles token management for AI agents over HTTP — any language, any framework.

Image: `mcr.microsoft.com/entra-sdk/auth-sidecar:1.0.0-azurelinux3.0-distroless`. See [GitHub releases](https://github.com/AzureAD/microsoft-identity-web/releases) for tags.

For code patterns, deployment manifests, security hardening, and troubleshooting, see [sdk-sidecar-deployment.md](sdk-sidecar-deployment.md).

## Architecture

```
Client App → Your Agent (Python/Node/Go/Java)
          → Microsoft Entra SDK for AgentID (localhost:5000)
          → Microsoft Entra ID
                                            ↓
                                   Downstream APIs
```

The SDK runs as a companion container in the same pod or Docker network. Your agent calls it over HTTP — no SDK embedding required.

### Agent Integration (3P and Custom Agents)

Third-party and custom agents authenticate using the Blueprint → BlueprintPrincipal → Agent Identity hierarchy. The SDK acquires tokens on their behalf:

```
                                    GET /AuthorizationHeaderUnauthenticated/graph
                                    ?AgentIdentity={agent-app-id}
  ┌──────────────────┐            ┌─────────────────────────────┐
  │  Agent           │ ─────────▶ │  Microsoft Entra SDK for    │
  │  (any language)  │ ◀───────── │  AgentID (:5000)            │
  │                  │  { authorizationHeader: "Bearer eyJ..." }│
  └────────┬─────────┘            └──────────────┬──────────────┘
           │ Authorization: Bearer <JWT>                        │ OAuth 2.0
           ▼                                                    ▼
  ┌──────────────────────┐                      ┌──────────────────────────┐
  │  Downstream APIs     │                      │  Microsoft Entra ID      │
  │  · Microsoft Graph   │                      │  · Blueprint             │
  │  · Custom APIs       │                      │  · AgentIdentity         │
  │  · Azure Services    │                      │                          │
  └──────────────────────┘                      └──────────────────────────┘
```

## SDK Configuration

### Core Settings

```yaml
env:
- name: AzureAd__Instance
  value: "https://login.microsoftonline.com/"
- name: AzureAd__TenantId
  value: "<your-tenant-id>"
- name: AzureAd__ClientId
  value: "<blueprint-app-id>"
```

### Client Credentials

> Client secrets are for development only. Production deployments must use Federated Identity Credentials (FIC) via Workload Identity (`SignedAssertionFilePath`) or Managed Identity.

```yaml
# Dev ONLY — Client Secret
- name: AzureAd__ClientCredentials__0__SourceType
  value: "ClientSecret"
- name: AzureAd__ClientCredentials__0__ClientSecret
  value: "<secret>"

# Prod (AKS) — Federated Identity Credentials via Workload Identity (RECOMMENDED)
- name: AzureAd__ClientCredentials__0__SourceType
  value: "SignedAssertionFilePath"

# Prod (VM / App Service) — Managed Identity
- name: AzureAd__ClientCredentials__0__SourceType
  value: "SignedAssertionFromManagedIdentity"
- name: AzureAd__ClientCredentials__0__ManagedIdentityClientId
  value: "<managed-identity-client-id>"
```

### Downstream API

```yaml
- name: DownstreamApis__Graph__BaseUrl
  value: "https://graph.microsoft.com/v1.0/"
- name: DownstreamApis__Graph__Scopes__0
  value: "https://graph.microsoft.com/.default"
- name: DownstreamApis__Graph__RequestAppToken
  value: "true"
```

## Agent Identity Query Parameters

| Parameter | Purpose | Example |
|-----------|---------|---------|
| `AgentIdentity` | Agent app (client) ID — autonomous mode | `?AgentIdentity=<agent-client-id>` |
| `AgentIdentity` + `AgentUsername` | Interactive mode by UPN | `?AgentIdentity=<id>&AgentUsername=user@contoso.com` |
| `AgentIdentity` + `AgentUserId` | Interactive mode by Object ID | `?AgentIdentity=<id>&AgentUserId=<oid>` |

Rules:
- `AgentUsername`/`AgentUserId` require `AgentIdentity`
- `AgentUsername` and `AgentUserId` are mutually exclusive
- `AgentIdentity` alone = autonomous agent
- `AgentIdentity` + inbound bearer = interactive (OBO) agent

## Endpoint Reference

| Endpoint | Method | Auth Required | Purpose |
|----------|--------|---------------|---------|
| `/Validate` | GET | Yes | Validate inbound bearer, return claims |
| `/AuthorizationHeader/{name}` | GET | Yes | Validate inbound token + acquire downstream token (OBO) |
| `/AuthorizationHeaderUnauthenticated/{name}` | GET | No | Acquire app/agent token without inbound user token |
| `/DownstreamApi/{name}` | ANY | Yes | Validate + call downstream API with auto token |
| `/DownstreamApiUnauthenticated/{name}` | ANY | No | Call downstream API with app/agent token |
| `/healthz` | GET | No | Health probe |

## External Links

| Resource | URL |
|----------|-----|
| SDK Overview | https://learn.microsoft.com/en-us/entra/msidweb/agent-id-sdk/overview |
| Installation | https://learn.microsoft.com/en-us/entra/msidweb/agent-id-sdk/installation |
| Configuration | https://learn.microsoft.com/en-us/entra/msidweb/agent-id-sdk/configuration |
| Endpoints | https://learn.microsoft.com/en-us/entra/msidweb/agent-id-sdk/endpoints |
| Agent Identities | https://learn.microsoft.com/en-us/entra/msidweb/agent-id-sdk/agent-identities |
| Security | https://learn.microsoft.com/en-us/entra/msidweb/agent-id-sdk/security |
| OpenAPI Spec | https://github.com/AzureAD/microsoft-identity-web/blob/master/src/Microsoft.Identity.Web.Sidecar/OpenAPI/Microsoft.Identity.Web.AgentID.json |
