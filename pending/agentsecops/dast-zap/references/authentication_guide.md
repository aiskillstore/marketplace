# ZAP Authentication Configuration Guide

Comprehensive guide for configuring authenticated scanning in OWASP ZAP for form-based, token-based, and OAuth authentication.

## Overview

Authenticated scanning is critical for testing protected application areas that require login. ZAP supports multiple authentication methods:

- **Form-Based Authentication** - Traditional username/password login forms
- **HTTP Authentication** - Basic, Digest, NTLM authentication
- **Script-Based Authentication** - Custom authentication flows (OAuth, SAML)
- **Token-Based Authentication** - Bearer tokens, API keys, JWT

## Form-Based Authentication

### Configuration Steps

1. **Identify Login Parameters**
   - Login URL
   - Username field name
   - Password field name
   - Submit button/action

2. **Create Authentication Context**

```bash
# Use bundled script
python3 scripts/zap_auth_scanner.py \
  --target https://app.example.com \
  --auth-type form \
  --login-url https://app.example.com/login \
  --username testuser \
  --password-env APP_PASSWORD \
  --verification-url https://app.example.com/dashboard \
  --output authenticated-scan-report.html
```

3. **Configure Logged-In Indicator**

Specify a regex pattern that appears only when logged in:
- Example: `Welcome, testuser`
- Example: `<a href="/logout">Logout</a>`
- Example: Check for presence of dashboard elements

### Manual Context Configuration

Create `auth-context.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <context>
        <name>WebAppAuth</name>
        <desc>Authenticated scanning context</desc>
        <inscope>true</inscope>
        <incregexes>https://app\.example\.com/.*</incregexes>

        <authentication>
            <type>formBasedAuthentication</type>
            <form>
                <loginurl>https://app.example.com/login</loginurl>
                <loginbody>username={%username%}&amp;password={%password%}</loginbody>
                <loginpageurl>https://app.example.com/login</loginpageurl>
            </form>
            <loggedin>\QWelcome,\E</loggedin>
            <loggedout>\QYou are not logged in\E</loggedout>
        </authentication>

        <users>
            <user>
                <name>testuser</name>
                <credentials>
                    <credential>
                        <name>username</name>
                        <value>testuser</value>
                    </credential>
                    <credential>
                        <name>password</name>
                        <value>SecureP@ssw0rd</value>
                    </credential>
                </credentials>
                <enabled>true</enabled>
            </user>
        </users>

        <sessionManagement>
            <type>cookieBasedSessionManagement</type>
        </sessionManagement>
    </context>
</configuration>
```

Run scan with context:

```bash
docker run --rm \
  -v $(pwd):/zap/wrk/:rw \
  -t zaproxy/zap-stable \
  zap-full-scan.py \
  -t https://app.example.com \
  -n /zap/wrk/auth-context.xml \
  -r /zap/wrk/auth-report.html
```

## Token-Based Authentication (Bearer Tokens)

### JWT/Bearer Token Configuration

1. **Obtain Authentication Token**

```bash
# Example: Login to get token
TOKEN=$(curl -X POST https://api.example.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password"}' \
  | jq -r '.token')
```

2. **Configure ZAP to Include Token**

Use ZAP Replacer to add Authorization header:

```bash
python3 scripts/zap_auth_scanner.py \
  --target https://api.example.com \
  --auth-type bearer \
  --token-env API_TOKEN \
  --output api-auth-scan.html
```

### Manual Token Configuration

Using ZAP automation framework (`zap_automation.yaml`):

```yaml
env:
  contexts:
    - name: API-Context
      urls:
        - https://api.example.com
      authentication:
        method: header
        parameters:
          header: Authorization
          value: "Bearer ${API_TOKEN}"
      sessionManagement:
        method: cookie

jobs:
  - type: spider
    parameters:
      context: API-Context
      user: api-user

  - type: activeScan
    parameters:
      context: API-Context
      user: api-user
```

## OAuth 2.0 Authentication

### Authorization Code Flow

1. **Manual Browser-Based Token Acquisition**

```bash
# Step 1: Get authorization code (open in browser)
https://oauth.example.com/authorize?
  client_id=YOUR_CLIENT_ID&
  redirect_uri=http://localhost:8080/callback&
  response_type=code&
  scope=openid profile

# Step 2: Exchange code for token
TOKEN=$(curl -X POST https://oauth.example.com/token \
  -d "grant_type=authorization_code" \
  -d "code=AUTH_CODE_FROM_STEP_1" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "redirect_uri=http://localhost:8080/callback" \
  | jq -r '.access_token')

# Step 3: Use token in ZAP scan
export API_TOKEN="$TOKEN"
python3 scripts/zap_auth_scanner.py \
  --target https://api.example.com \
  --auth-type bearer \
  --token-env API_TOKEN
```

### Client Credentials Flow (Service-to-Service)

```bash
# Obtain token using client credentials
TOKEN=$(curl -X POST https://oauth.example.com/token \
  -d "grant_type=client_credentials" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "scope=api.read api.write" \
  | jq -r '.access_token')

export API_TOKEN="$TOKEN"

# Run authenticated scan
python3 scripts/zap_auth_scanner.py \
  --target https://api.example.com \
  --auth-type bearer \
  --token-env API_TOKEN
```

## HTTP Basic/Digest Authentication

### Basic Authentication

```bash
# Option 1: Using environment variable
export BASIC_AUTH="dGVzdHVzZXI6cGFzc3dvcmQ="  # base64(testuser:password)

# Option 2: Using script
python3 scripts/zap_auth_scanner.py \
  --target https://app.example.com \
  --auth-type http \
  --username testuser \
  --password-env HTTP_PASSWORD
```

### Digest Authentication

Similar to Basic, but ZAP automatically handles the challenge-response:

```bash
docker run --rm \
  -v $(pwd):/zap/wrk/:rw \
  -t zaproxy/zap-stable \
  zap-full-scan.py \
  -t https://app.example.com \
  -n /zap/wrk/digest-auth-context.xml \
  -r /zap/wrk/digest-auth-report.html
```

## Session Management

### Cookie-Based Sessions

**Default Behavior:** ZAP automatically manages cookies.

**Custom Configuration:**
- Set session cookie name in context
- Configure session timeout
- Define re-authentication triggers

### Token Refresh Handling

For tokens that expire during scan:

```yaml
# zap_automation.yaml
env:
  contexts:
    - name: API-Context
      authentication:
        method: script
        parameters:
          script: |
            // JavaScript to refresh token
            function authenticate(helper, paramsValues, credentials) {
              var loginUrl = "https://api.example.com/auth/login";
              var postData = '{"username":"' + credentials.getParam("username") +
                             '","password":"' + credentials.getParam("password") + '"}';

              var msg = helper.prepareMessage();
              msg.setRequestHeader("POST " + loginUrl + " HTTP/1.1");
              msg.setRequestBody(postData);
              helper.sendAndReceive(msg);

              var response = msg.getResponseBody().toString();
              var token = JSON.parse(response).token;

              // Store token for use in requests
              helper.getHttpSender().setRequestHeader("Authorization", "Bearer " + token);
              return msg;
            }
```

## Verification and Troubleshooting

### Verify Authentication is Working

1. **Check Logged-In Indicator**

Run a spider scan and verify protected pages are accessed:

```bash
# Look for dashboard, profile, or other authenticated pages in spider results
```

2. **Monitor Authentication Requests**

Enable ZAP logging to see authentication attempts:

```bash
docker run --rm \
  -v $(pwd):/zap/wrk/:rw \
  -e ZAP_LOG_LEVEL=DEBUG \
  -t zaproxy/zap-stable \
  zap-full-scan.py -t https://app.example.com -n /zap/wrk/context.xml
```

3. **Test with Manual Request**

Send a manual authenticated request via ZAP GUI or API to verify credentials work.

### Common Authentication Issues

#### Issue: Session Expires During Scan

**Solution:** Configure re-authentication:

```python
# In zap_auth_scanner.py, add re-authentication trigger
--re-authenticate-on 401,403 \
--verification-interval 300  # Check every 5 minutes
```

#### Issue: CSRF Tokens Required

**Solution:** Use anti-CSRF token handling:

```yaml
# zap_automation.yaml
env:
  contexts:
    - name: WebApp
      authentication:
        verification:
          method: response
          loggedInRegex: "\\QWelcome\\E"
      sessionManagement:
        method: cookie
        parameters:
          antiCsrfTokens: true
```

#### Issue: Rate Limiting Blocking Authentication

**Solution:** Slow down scan:

```bash
docker run -t zaproxy/zap-stable zap-full-scan.py \
  -t https://app.example.com \
  -z "-config scanner.delayInMs=2000 -config scanner.threadPerHost=1"
```

#### Issue: Multi-Step Login (MFA)

**Solution:** Use script-based authentication with Selenium or manual token acquisition.

## Security Best Practices

1. **Never Hardcode Credentials**
   - Use environment variables
   - Use secrets management tools (Vault, AWS Secrets Manager)

2. **Use Dedicated Test Accounts**
   - Create accounts specifically for security testing
   - Limit permissions to test data only
   - Monitor for abuse

3. **Rotate Credentials Regularly**
   - Change test account passwords after each scan
   - Rotate API tokens frequently

4. **Log Authentication Attempts**
   - Monitor for failed authentication attempts
   - Alert on unusual patterns

5. **Secure Context Files**
   - Never commit context files with credentials to version control
   - Use `.gitignore` to exclude `*.context` files
   - Encrypt context files at rest

## Examples by Framework

### Django Application

```bash
# Django CSRF token handling
python3 scripts/zap_auth_scanner.py \
  --target https://django-app.example.com \
  --auth-type form \
  --login-url https://django-app.example.com/accounts/login/ \
  --username testuser \
  --password-env DJANGO_PASSWORD \
  --verification-url https://django-app.example.com/dashboard/
```

### Spring Boot Application

```bash
# Spring Security form login
python3 scripts/zap_auth_scanner.py \
  --target https://spring-app.example.com \
  --auth-type form \
  --login-url https://spring-app.example.com/login \
  --username testuser \
  --password-env SPRING_PASSWORD
```

### React SPA with JWT

```bash
# Get JWT from API, then scan
TOKEN=$(curl -X POST https://api.example.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}' \
  | jq -r '.token')

export API_TOKEN="$TOKEN"

python3 scripts/zap_auth_scanner.py \
  --target https://spa.example.com \
  --auth-type bearer \
  --token-env API_TOKEN
```

## Additional Resources

- [ZAP Authentication Documentation](https://www.zaproxy.org/docs/desktop/start/features/authentication/)
- [ZAP Session Management](https://www.zaproxy.org/docs/desktop/start/features/sessionmanagement/)
- [OAuth 2.0 RFC 6749](https://tools.ietf.org/html/rfc6749)
