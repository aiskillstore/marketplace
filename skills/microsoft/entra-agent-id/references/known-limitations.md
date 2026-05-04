# Known Limitations

Source: [Microsoft Entra Agent ID — known issues and gaps](https://learn.microsoft.com/en-us/entra/agent-id/identity-platform/preview-known-issues)

## API & Object Model

1. **Sponsors must be Users at Blueprint creation** — ServicePrincipals and Groups are not accepted as Blueprint sponsors. (Agent Identity sponsors may be Users or Groups.)
2. **BlueprintPrincipal not auto-created** — requires explicit `POST /servicePrincipals/microsoft.graph.agentIdentityBlueprintPrincipal` after Blueprint creation.
3. **Agent Identities cannot have password credentials** — credentials belong on the Blueprint only (`PropertyNotCompatibleWithAgentIdentity`).
4. **Agent Identities have no backing application object** — they are service-principal-only entities.
5. **Blueprint needs explicit `identifierUris`** — not set by default; required for OAuth2 scope resolution (`api://{app-id}/.default`).
6. **No Graph relationship filtering for Agent IDs** — `/ownedObjects`, `/deletedItems`, `/owners` return all types; filter client-side by `odata.type`.
7. **Orphaned agent users after deletion** — deleting a Blueprint or identity does NOT auto-delete its agent users; clean up manually via admin center or Graph API.

## Roles & Permissions

8. **`Directory.AccessAsUser.All` hard rejection** — if present on the client, all other Agent ID delegated permissions are ignored → 403 Forbidden.
9. **No viable delegated permission for creating Agent Identities** — use application permissions.
10. **No quick-start permission bundle** — discover and grant 18+ individual Agent Identity permissions.
11. **Permission propagation delay** — 30–120+ seconds after admin consent before tokens include new claims; prefer delegated permissions and add exponential backoff retry.
12. **Global Reader cannot list Agent Identities** — `GET /servicePrincipals/microsoft.graph.agentIdentity` returns 403; use `GET /servicePrincipals` and filter instead.
13. **Custom roles cannot include Agent ID actions** — use built-in roles (Agent ID Administrator, Agent ID Developer).
14. **Administrative units not supported** — cannot add Agent Identities, Blueprints, or BlueprintPrincipals to admin units; use `owners` instead.
15. **Agent ID Admin cannot update agent-user photos** — use User Administrator.

## Admin Center & Management

16. **No Blueprint management in Entra admin center** — use Microsoft Graph / PowerShell.
17. **`/me` endpoint unavailable** in `client_credentials` flow — use `az ad signed-in-user show` or Graph delegated permissions for user context.

## Authentication & Consent

18. **No SSO to web apps** — Agent IDs can't sign in via Entra ID sign-in pages (no OpenID Connect or SAML); use web APIs instead.
19. **Admin consent workflow (ACW) broken** for permissions requested by Agent IDs — contact tenant admin directly.
20. **Cannot grant app permissions to BlueprintPrincipals** — grant to individual Agent Identities.
21. **Cannot assign app roles where target resource is an Agent Identity** — use the BlueprintPrincipal as target resource.
22. **Risk-based step-up blocks consent silently** — no "risky" indication in the UX.

## Groups, Logs & Monitoring

23. **No dynamic group membership** — Agent Identities and agent users cannot be added to dynamic groups; use security groups with fixed membership.
24. **Audit logs do not distinguish Agent IDs** — operations on Blueprints/identities logged as `ApplicationManagement`, agent users as `User Management`; cross-reference object IDs via Graph to determine entity type.
25. **Graph activity logs do not distinguish Agent IDs** — agent-identity requests logged as applications, agent-user requests as users; join with sign-in logs.

## Performance & Scale

26. **Sequential creation requests may fail** — Blueprint → Principal → Identity in quick succession can return `400 Bad Request: Object with id {id} not found`, especially with application permissions. Prefer delegated permissions; add exponential backoff.

## Product Integrations

27. **Copilot Studio** — only custom engine agents are supported; Agent IDs are used for channel auth only (not connectors or tools).
28. **MSAL complexity** — Agent ID scenarios require managing Federated Identity Credentials manually. For .NET use [Microsoft.Identity.Web.AgentIdentities](https://github.com/AzureAD/microsoft-identity-web/blob/master/src/Microsoft.Identity.Web.AgentIdentities/README.AgentIdentities.md). For other languages use the [Microsoft Entra SDK for AgentID](https://learn.microsoft.com/en-us/entra/msidweb/agent-id-sdk/overview).

## Reporting Issues

Report unlisted issues via [aka.ms/agentidfeedback](https://aka.ms/agentidfeedback).
