# Entra ID / Easy Auth Recipe — REFERENCE ONLY

Adds authentication and authorization to an App Service base template using Microsoft Entra ID.

## Overview

This recipe configures authentication for App Service apps using either Easy Auth (built-in authentication) or MSAL SDK-based authentication. Easy Auth requires zero code changes; MSAL gives full control.

## Integration Type

| Aspect | Value |
|--------|-------|
| **Provider** | Microsoft Entra ID (Azure AD) |
| **Method** | Easy Auth (built-in) or MSAL SDK |
| **Protocols** | OpenID Connect, OAuth 2.0 |
| **Token validation** | Automatic (Easy Auth) or middleware (MSAL) |

## Option A: Easy Auth (Recommended for most apps)

Zero-code authentication built into App Service. Handles login, token management, and session cookies.

### Bicep Configuration

> 💡 Call `mcp_bicep_get_az_resource_type_schema` with resource type `Microsoft.Web/sites/config` to validate properties before generating this resource.

```bicep
resource authSettings 'Microsoft.Web/sites/config@2023-12-01' = {
  parent: webApp
  name: 'authsettingsV2'
  properties: {
    globalValidation: {
      requireAuthentication: true
      unauthenticatedClientAction: 'RedirectToLoginPage'
    }
    identityProviders: {
      azureActiveDirectory: {
        enabled: true
        registration: {
          openIdIssuer: 'https://login.microsoftonline.com/${tenant().tenantId}/v2.0'
          clientId: appRegistration.properties.appId
        }
        validation: {
          defaultAuthorizationPolicy: {
            allowedApplications: []
          }
        }
      }
    }
    login: {
      tokenStore: {
        enabled: true
      }
    }
  }
}
```

### App Registration

> 💡 Call `mcp_bicep_get_az_resource_type_schema` with resource type `Microsoft.Graph/applications` to validate properties before generating this resource. The `microsoftGraphV1_0` extension is required — declare it at the top of the Bicep file.

```bicep
extension microsoftGraphV1_0

resource appRegistration 'Microsoft.Graph/applications@v1.0' = {
  displayName: '${name}-app'
  web: {
    redirectUris: [
      'https://${webApp.properties.defaultHostName}/.auth/login/aad/callback'
    ]
  }
}
```

## Option B: MSAL SDK (Full control)

Use when you need custom token validation, API-only auth, or multi-tenant support.

| Language | Source File |
|----------|-------------|
| C# (ASP.NET Core) | [source/dotnet.md](source/dotnet.md) |
| Python (FastAPI) | [source/python.md](source/python.md) |
| Node.js (Express) | [source/nodejs.md](source/nodejs.md) |

## App Settings

| Setting | Value | Purpose |
|---------|-------|---------|
| `AZURE_TENANT_ID` | Entra tenant ID | Identity provider |
| `AZURE_CLIENT_ID` | App registration client ID | Application identity |

## References

- [Easy Auth overview](https://learn.microsoft.com/en-us/azure/app-service/overview-authentication-authorization)
- [Microsoft Identity Web](https://learn.microsoft.com/en-us/entra/msal/dotnet/microsoft-identity-web/)
- [Configure Entra ID auth](https://learn.microsoft.com/en-us/azure/app-service/configure-authentication-provider-aad)
