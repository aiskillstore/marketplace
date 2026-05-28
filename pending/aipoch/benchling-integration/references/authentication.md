# Benchling Authentication Reference Guide

## Authentication Methods

Benchling supports three authentication methods, each suitable for different use cases.

### 1. API Key Authentication (Basic Auth)

**Best for:** Personal scripts, prototyping, single-user integrations

**How it works:**
- Use your API Key as the username in HTTP Basic Auth
- Leave the password field empty
- HTTPS is required for all requests

**Getting an API Key:**
1. Log in to your Benchling account
2. Navigate to Profile Settings
3. Find the "API Key" section
4. Generate a new API Key
5. Save it securely (it's shown only once)

**Python SDK Usage:**
```python
from benchling_sdk.benchling import Benchling
from benchling_sdk.auth.api_key_auth import ApiKeyAuth

benchling = Benchling(
    url="https://your-tenant.benchling.com",
    auth_method=ApiKeyAuth("your_api_key_here")
)
```

**Direct HTTP Usage:**
```bash
curl -X GET \
  https://your-tenant.benchling.com/api/v2/dna-sequences \
  -u "your_api_key_here:"
```
Note the colon after the API key and no password.

**Environment Variable Pattern:**
```python
import os
from benchling_sdk.benchling import Benchling
from benchling_sdk.auth.api_key_auth import ApiKeyAuth

api_key = os.environ.get("BENCHLING_API_KEY")
tenant_url = os.environ.get("BENCHLING_TENANT_URL")

benchling = Benchling(
    url=tenant_url,
    auth_method=ApiKeyAuth(api_key)
)
```

### 2. OAuth 2.0 Client Credentials

**Best for:** Multi-user apps, service accounts, production integrations

**How it works:**
1. Register an App in Benchling Developer Console
2. Get a Client ID and Client Secret
3. Exchange credentials for an access token
4. Use access token for API requests
5. Refresh token when expired

**Registering an App:**
1. Log in to Benchling as admin
2. Navigate to Developer Console
3. Create a new App
4. Record Client ID and Client Secret
5. Configure OAuth Redirect URIs and Permissions

**Python SDK Usage:**
```python
from benchling_sdk.benchling import Benchling
from benchling_sdk.auth.client_credentials_oauth2 import ClientCredentialsOAuth2

auth_method = ClientCredentialsOAuth2(
    client_id="your_client_id",
    client_secret="your_client_secret"
)

benchling = Benchling(
    url="https://your-tenant.benchling.com",
    auth_method=auth_method
)
```
The SDK handles token refresh automatically.

**Direct HTTP Token Flow:**
```bash
# Get Access Token
curl -X POST \
  https://your-tenant.benchling.com/api/v2/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials" \
  -d "client_id=your_client_id" \
  -d "client_secret=your_client_secret"

# Response:
# {
#   "access_token": "token_here",
#   "token_type": "Bearer",
#   "expires_in": 3600
# }

# Use Access Token
curl -X GET \
  https://your-tenant.benchling.com/api/v2/dna-sequences \
  -H "Authorization: Bearer access_token_here"
```

### 3. OpenID Connect (OIDC)

**Best for:** Enterprise integrations with existing Identity Providers, SSO scenarios

**How it works:**
- Authenticate user via your Identity Provider (Okta, Azure AD, etc.)
- IdP issues an ID Token with email claim
- Benchling verifies token against OpenID configuration endpoint
- Matches authenticated user via email

**Requirements:**
- Enterprise Benchling account
- Configured Identity Provider (IdP)
- IdP must issue tokens with email claim
- Email in token must match Benchling user email

**Identity Provider Configuration:**
1. Configure your IdP to issue OpenID Connect tokens
2. Ensure `email` claim is included
3. Provide IdP's OpenID Configuration URL to Benchling
4. Benchling validates tokens against this configuration

**Python Usage:**
```python
# Assuming you have retrieved the ID token from your IdP
from benchling_sdk.benchling import Benchling
from benchling_sdk.auth.oidc_auth import OidcAuth

auth_method = OidcAuth(id_token="id_token_from_idp")

benchling = Benchling(
    url="https://your-tenant.benchling.com",
    auth_method=auth_method
)
```

**Direct HTTP Usage:**
```bash
curl -X GET \
  https://your-tenant.benchling.com/api/v2/dna-sequences \
  -H "Authorization: Bearer id_token_here"
```

## Security Best Practices

### Credential Storage

**Do:**
- Store credentials in environment variables
- Use secrets managers (AWS Secrets Manager, HashiCorp Vault)
- Encrypt credentials at rest
- Use different credentials for Dev/Test/Prod

**Don't:**
- Commit credentials to version control
- Hardcode credentials in source files
- Share credentials via email/chat
- Store credentials in plain text files

**Example with Environment Variables:**
```python
import os
from dotenv import load_dotenv  # python-dotenv package

# Load from .env file (ensure .env is in .gitignore!)
load_dotenv()

api_key = os.environ["BENCHLING_API_KEY"]
tenant = os.environ["BENCHLING_TENANT_URL"]
```

### Credential Rotation

**API Key Rotation:**
1. Generate new API Key in Profile Settings
2. Update your application with new key
3. Verify new key works
4. Delete old API Key

**App Secret Rotation:**
1. Navigate to Developer Console
2. Select your App
3. Generate new Client Secret
4. Update application configuration
5. Delete old secret after verification

**Best Practice:** Rotate credentials regularly (e.g., every 90 days) and immediately upon compromise.

### Access Control

**Least Privilege:**
- Grant only minimum necessary permissions
- Use service accounts (Apps) for automation instead of personal accounts
- Review and audit permissions regularly

**App Permissions:**
Apps need explicit permission to access:
- Organizations
- Teams
- Projects
- Folders

Configure these in Developer Console when setting up the App.

**User Permissions:**
API access mirrors UI permissions:
- Users can only access data they can see/edit in UI
- Deactivated users lose API access
- Archived apps lose API access until unarchived

### Network Security

**HTTPS Only:**
All Benchling API requests must use HTTPS. HTTP requests will be rejected.

**IP Whitelisting (Enterprise):**
Some enterprise accounts restrict API access to specific IP ranges. Contact Benchling Support to configure.

**Rate Limiting:**
Benchling enforces rate limits to prevent abuse:
- Default: 100 requests per 10 seconds per user/app
- Returns 429 status code when exceeded
- SDK handles retries automatically with exponential backoff

### Audit Logs

**Tracking Usage:**
- All API calls are logged with user/app identity
- OAuth apps show full audit trail with user attribution
- API Key calls are attributed to the key owner
- View audit logs in Benchling Admin Console

**App Best Practice:**
Use OAuth instead of API Keys when multiple users interact through your app. This ensures the audit trail correctly attributes actions to the actual user, not just the app.

## Troubleshooting

### Common Auth Errors

**401 Unauthorized:**
- Invalid or expired credentials
- Incorrect API Key format
- Missing Authorization header

**Solution:**
- Verify credentials are correct
- Check if API Key has expired or been deleted
- Ensure header format is `Authorization: Bearer <token>`

**403 Forbidden:**
- Valid credentials but insufficient permissions
- User doesn't have access to requested resource
- App hasn't been granted access to Organization/Project

**Solution:**
- Check user/app permissions in Benchling
- Grant necessary access in Developer Console (for Apps)
- Verify resource exists and user has access

**429 Too Many Requests:**
- Rate limit exceeded
- Requesting too frequently in short window

**Solution:**
- Implement exponential backoff
- SDK handles this automatically
- Consider caching results
- Spread requests over longer period

### Testing Authentication

**Quick Test with curl:**
```bash
# Test API Key
curl -X GET \
  https://your-tenant.benchling.com/api/v2/users/me \
  -u "your_api_key:" \
  -v

# Test OAuth Token
curl -X GET \
  https://your-tenant.benchling.com/api/v2/users/me \
  -H "Authorization: Bearer your_token" \
  -v
```
The `/users/me` endpoint returns authenticated user info, useful for verifying credentials.

**Python SDK Test:**
```python
from benchling_sdk.benchling import Benchling
from benchling_sdk.auth.api_key_auth import ApiKeyAuth

try:
    benchling = Benchling(
        url="https://your-tenant.benchling.com",
        auth_method=ApiKeyAuth("your_api_key")
    )

    # Test authentication
    user = benchling.users.get_me()
    print(f"Authenticated as: {user.name} ({user.email})")

except Exception as e:
    print(f"Authentication failed: {e}")
```

## Multi-Tenant Considerations

If working with multiple Benchling tenants:

```python
# Configuration for multiple tenants
tenants = {
    "production": {
        "url": "https://prod.benchling.com",
        "api_key": os.environ["PROD_API_KEY"]
    },
    "staging": {
        "url": "https://staging.benchling.com",
        "api_key": os.environ["STAGING_API_KEY"]
    }
}

# Initialize clients
clients = {}
for name, config in tenants.items():
    clients[name] = Benchling(
        url=config["url"],
        auth_method=ApiKeyAuth(config["api_key"])
    )

# Use specific client
prod_sequences = clients["production"].dna_sequences.list()
```

## Advanced: Custom HTTP Client

For environments with self-signed certificates or corporate proxies:

```python
import httpx
from benchling_sdk.benchling import Benchling
from benchling_sdk.auth.api_key_auth import ApiKeyAuth

# Custom httpx client with cert verification
custom_client = httpx.Client(
    verify="/path/to/custom/ca-bundle.crt",
    timeout=30.0
)

benchling = Benchling(
    url="https://your-tenant.benchling.com",
    auth_method=ApiKeyAuth("your_api_key"),
    http_client=custom_client
)
```

## Resources

- **Official Authentication Docs:** https://docs.benchling.com/docs/authentication
- **Developer Console:** https://your-tenant.benchling.com/developer
- **SDK Documentation:** https://benchling.com/sdk-docs/
