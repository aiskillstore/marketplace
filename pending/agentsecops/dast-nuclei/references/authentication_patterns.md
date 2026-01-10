# Nuclei Authentication Patterns

## Table of Contents
- [Bearer Token Authentication](#bearer-token-authentication)
- [Cookie-Based Authentication](#cookie-based-authentication)
- [API Key Authentication](#api-key-authentication)
- [OAuth 2.0 Authentication](#oauth-20-authentication)
- [Custom Authentication Scripts](#custom-authentication-scripts)
- [Multi-Factor Authentication](#multi-factor-authentication)

## Bearer Token Authentication

### Basic Bearer Token

```bash
# Using header flag
nuclei -u https://api.target.com \
  -header "Authorization: Bearer $AUTH_TOKEN" \
  -severity critical,high

# Using environment variable
export AUTH_TOKEN="your-token-here"
nuclei -u https://api.target.com \
  -header "Authorization: Bearer $AUTH_TOKEN"
```

### JWT Token with Refresh

```bash
# Initial authentication to get token
TOKEN=$(curl -X POST https://api.target.com/auth/login \
  -d '{"username":"test","password":"test"}' \
  -H "Content-Type: application/json" | jq -r '.access_token')

# Scan with token
nuclei -u https://api.target.com \
  -header "Authorization: Bearer $TOKEN" \
  -tags api,cve

# Refresh token if needed
REFRESH_TOKEN=$(curl -X POST https://api.target.com/auth/refresh \
  -H "Authorization: Bearer $TOKEN" | jq -r '.access_token')
```

## Cookie-Based Authentication

### Session Cookie Authentication

```bash
# Login and extract session cookie
curl -c cookies.txt -X POST https://target-app.com/login \
  -d "username=testuser&password=testpass"

# Extract cookie value
SESSION=$(grep session cookies.txt | awk '{print $7}')

# Scan with session cookie
nuclei -u https://target-app.com \
  -header "Cookie: session=$SESSION" \
  -severity critical,high
```

### Multiple Cookies

```bash
# Multiple cookies can be specified
nuclei -u https://target-app.com \
  -header "Cookie: session=$SESSION; user_id=$USER_ID; csrf_token=$CSRF" \
  -tags cve,owasp
```

## API Key Authentication

### Header-Based API Key

```bash
# API key in header
nuclei -u https://api.target.com \
  -header "X-API-Key: $API_KEY" \
  -tags api,exposure

# Multiple API authentication headers
nuclei -u https://api.target.com \
  -header "X-API-Key: $API_KEY" \
  -header "X-Client-ID: $CLIENT_ID" \
  -tags api
```

### Query Parameter API Key

Create custom template for query parameter auth:

```yaml
id: api-scan-with-query-auth
info:
  name: API Scan with Query Parameter Auth
  author: security-team
  severity: info

http:
  - method: GET
    path:
      - "{{BaseURL}}/api/endpoint?api_key={{api_key}}"

    payloads:
      api_key:
        - "{{env('API_KEY')}}"
```

## OAuth 2.0 Authentication

### Client Credentials Flow

```bash
# Get access token
ACCESS_TOKEN=$(curl -X POST https://auth.target.com/oauth/token \
  -d "grant_type=client_credentials" \
  -d "client_id=$CLIENT_ID" \
  -d "client_secret=$CLIENT_SECRET" \
  -H "Content-Type: application/x-www-form-urlencoded" | jq -r '.access_token')

# Scan with OAuth token
nuclei -u https://api.target.com \
  -header "Authorization: Bearer $ACCESS_TOKEN" \
  -tags api,cve
```

### Authorization Code Flow

```bash
# Step 1: Manual authorization to get code
# Navigate to: https://auth.target.com/oauth/authorize?client_id=$CLIENT_ID&redirect_uri=$REDIRECT_URI&response_type=code

# Step 2: Exchange code for token
AUTH_CODE="received-from-redirect"
ACCESS_TOKEN=$(curl -X POST https://auth.target.com/oauth/token \
  -d "grant_type=authorization_code" \
  -d "code=$AUTH_CODE" \
  -d "client_id=$CLIENT_ID" \
  -d "client_secret=$CLIENT_SECRET" \
  -d "redirect_uri=$REDIRECT_URI" | jq -r '.access_token')

# Step 3: Scan
nuclei -u https://api.target.com \
  -header "Authorization: Bearer $ACCESS_TOKEN"
```

### OAuth Token Refresh

```bash
#!/bin/bash
# oauth_refresh_scan.sh

CLIENT_ID="your-client-id"
CLIENT_SECRET="your-client-secret"
REFRESH_TOKEN="your-refresh-token"

# Function to get fresh access token
get_access_token() {
  curl -s -X POST https://auth.target.com/oauth/token \
    -d "grant_type=refresh_token" \
    -d "refresh_token=$REFRESH_TOKEN" \
    -d "client_id=$CLIENT_ID" \
    -d "client_secret=$CLIENT_SECRET" | jq -r '.access_token'
}

# Get token and scan
ACCESS_TOKEN=$(get_access_token)
nuclei -u https://api.target.com \
  -header "Authorization: Bearer $ACCESS_TOKEN" \
  -tags api,cve,owasp
```

## Custom Authentication Scripts

### Form-Based Login Script

```python
#!/usr/bin/env python3
import requests
import subprocess
import sys

def login_and_get_session():
    """Login and return session cookie"""
    session = requests.Session()

    # Perform login
    login_data = {
        "username": "testuser",
        "password": "testpassword"
    }

    response = session.post(
        "https://target-app.com/login",
        data=login_data
    )

    if response.status_code != 200:
        print(f"Login failed: {response.status_code}", file=sys.stderr)
        sys.exit(1)

    # Extract session cookie
    session_cookie = session.cookies.get("session")
    return session_cookie

def run_nuclei_scan(session_cookie, target_url):
    """Run Nuclei with authenticated session"""
    cmd = [
        "nuclei",
        "-u", target_url,
        "-header", f"Cookie: session={session_cookie}",
        "-severity", "critical,high",
        "-tags", "cve,owasp"
    ]

    result = subprocess.run(cmd)
    return result.returncode

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "https://target-app.com"

    print("Authenticating...")
    session = login_and_get_session()

    print("Running Nuclei scan...")
    exit_code = run_nuclei_scan(session, target)

    sys.exit(exit_code)
```

### SAML Authentication

```python
#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import subprocess

def saml_login(idp_url, username, password):
    """Perform SAML authentication flow"""
    session = requests.Session()

    # Step 1: Get SAML request from SP
    sp_response = session.get("https://target-app.com/saml/login")

    # Step 2: Submit credentials to IdP
    soup = BeautifulSoup(sp_response.text, 'html.parser')
    saml_request = soup.find('input', {'name': 'SAMLRequest'})['value']

    idp_login = session.post(
        idp_url,
        data={
            'username': username,
            'password': password,
            'SAMLRequest': saml_request
        }
    )

    # Step 3: Submit SAML response back to SP
    soup = BeautifulSoup(idp_login.text, 'html.parser')
    saml_response = soup.find('input', {'name': 'SAMLResponse'})['value']

    sp_acs = session.post(
        "https://target-app.com/saml/acs",
        data={'SAMLResponse': saml_response}
    )

    # Return session cookie
    return session.cookies.get_dict()

# Use in Nuclei scan
cookies = saml_login(
    "https://idp.example.com/saml/login",
    "testuser",
    "testpass"
)

cookie_header = "; ".join([f"{k}={v}" for k, v in cookies.items()])
subprocess.run([
    "nuclei",
    "-u", "https://target-app.com",
    "-header", f"Cookie: {cookie_header}",
    "-severity", "critical,high"
])
```

## Multi-Factor Authentication

### TOTP-Based MFA

```python
#!/usr/bin/env python3
import pyotp
import requests
import subprocess

def login_with_mfa(username, password, totp_secret):
    """Login with username, password, and TOTP"""
    session = requests.Session()

    # Step 1: Submit username and password
    login_response = session.post(
        "https://target-app.com/login",
        data={
            "username": username,
            "password": password
        }
    )

    # Step 2: Generate and submit TOTP code
    totp = pyotp.TOTP(totp_secret)
    mfa_code = totp.now()

    mfa_response = session.post(
        "https://target-app.com/mfa/verify",
        data={"code": mfa_code}
    )

    if mfa_response.status_code != 200:
        raise Exception("MFA verification failed")

    return session.cookies.get("session")

# Use in scan
session_cookie = login_with_mfa(
    "testuser",
    "testpass",
    "JBSWY3DPEHPK3PXP"  # TOTP secret
)

subprocess.run([
    "nuclei",
    "-u", "https://target-app.com",
    "-header", f"Cookie: session={session_cookie}",
    "-tags", "cve,owasp"
])
```

### SMS/Email MFA (Manual Intervention)

```bash
#!/bin/bash
# mfa_manual_scan.sh

echo "Step 1: Performing initial login..."
curl -c cookies.txt -X POST https://target-app.com/login \
  -d "username=testuser&password=testpass"

echo "Step 2: MFA code sent. Please check your email/SMS."
read -p "Enter MFA code: " MFA_CODE

echo "Step 3: Submitting MFA code..."
curl -b cookies.txt -c cookies.txt -X POST https://target-app.com/mfa/verify \
  -d "code=$MFA_CODE"

echo "Step 4: Running Nuclei scan with authenticated session..."
SESSION=$(grep session cookies.txt | awk '{print $7}')
nuclei -u https://target-app.com \
  -header "Cookie: session=$SESSION" \
  -severity critical,high \
  -tags cve,owasp

echo "Scan complete!"
```

## Advanced Patterns

### Dynamic Token Rotation

```bash
#!/bin/bash
# token_rotation_scan.sh

TARGET_URL="https://api.target.com"
AUTH_ENDPOINT="https://auth.target.com/token"
CLIENT_ID="client-id"
CLIENT_SECRET="client-secret"

# Function to get new token
refresh_token() {
  curl -s -X POST $AUTH_ENDPOINT \
    -d "grant_type=client_credentials" \
    -d "client_id=$CLIENT_ID" \
    -d "client_secret=$CLIENT_SECRET" | jq -r '.access_token'
}

# Get initial token
TOKEN=$(refresh_token)

# Scan critical templates
nuclei -u $TARGET_URL \
  -header "Authorization: Bearer $TOKEN" \
  -severity critical \
  -tags cve

# Refresh token for next batch
TOKEN=$(refresh_token)

# Scan high severity templates
nuclei -u $TARGET_URL \
  -header "Authorization: Bearer $TOKEN" \
  -severity high \
  -tags owasp
```

### Authenticated Multi-Target Scanning

```bash
#!/bin/bash
# multi_target_auth_scan.sh

# Read targets from file
TARGETS_FILE="targets.txt"
AUTH_TOKEN="your-auth-token"

while IFS= read -r target; do
  echo "Scanning: $target"

  nuclei -u "$target" \
    -header "Authorization: Bearer $AUTH_TOKEN" \
    -severity critical,high \
    -o "results/$(echo $target | sed 's|https://||' | sed 's|/|_|g').txt"

  sleep 5  # Rate limiting between targets
done < "$TARGETS_FILE"

echo "All scans complete!"
```

## Best Practices

1. **Never Hardcode Credentials**: Use environment variables or secrets management
2. **Rotate Tokens**: Refresh authentication tokens for long-running scans
3. **Session Validation**: Verify session is still valid before scanning
4. **Rate Limiting**: Respect rate limits when authenticated (often higher quotas)
5. **Scope Validation**: Ensure authenticated access doesn't expand out of scope
6. **Audit Logging**: Log all authenticated scan activities
7. **Token Expiry**: Handle token expiration gracefully with refresh
8. **Least Privilege**: Use accounts with minimum necessary privileges for testing

## Troubleshooting

### Token Expired During Scan

```bash
# Add token refresh logic
nuclei -u https://api.target.com \
  -header "Authorization: Bearer $TOKEN" \
  -severity critical || {
    echo "Scan failed, refreshing token..."
    TOKEN=$(refresh_token)
    nuclei -u https://api.target.com \
      -header "Authorization: Bearer $TOKEN" \
      -severity critical
  }
```

### Session Cookie Not Working

```bash
# Debug session cookie
curl -v https://target-app.com/protected-page \
  -H "Cookie: session=$SESSION"

# Check cookie expiration
echo $SESSION | base64 -d | jq '.exp'

# Re-authenticate if expired
SESSION=$(re_authenticate)
```

### Multiple Authentication Methods

```bash
# Some APIs require multiple auth headers
nuclei -u https://api.target.com \
  -header "Authorization: Bearer $TOKEN" \
  -header "X-API-Key: $API_KEY" \
  -header "X-Client-ID: $CLIENT_ID" \
  -tags api
```

## Resources

- [OAuth 2.0 RFC](https://oauth.net/2/)
- [JWT.io](https://jwt.io/)
- [SAML 2.0](http://saml.xml.org/)
- [Nuclei Authentication Docs](https://docs.projectdiscovery.io/)
