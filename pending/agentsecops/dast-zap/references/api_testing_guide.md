# ZAP API Security Testing Guide

Advanced guide for testing REST, GraphQL, SOAP, and WebSocket APIs using OWASP ZAP.

## Overview

Modern applications rely heavily on APIs. This guide covers comprehensive API security testing patterns using ZAP's API scanning capabilities.

## API Types Supported

- **REST APIs** (JSON, XML)
- **GraphQL APIs**
- **SOAP APIs** (WSDL-based)
- **gRPC APIs**
- **WebSocket APIs**

## REST API Testing

### Testing with OpenAPI/Swagger Specification

**Best Practice:** Always use API specifications when available for complete coverage.

```bash
# Basic OpenAPI scan
docker run -v $(pwd):/zap/wrk/:rw -t zaproxy/zap-stable zap-api-scan.py \
  -t https://api.example.com \
  -f openapi \
  -d /zap/wrk/openapi.yaml \
  -r /zap/wrk/api-report.html
```

### Testing Without Specification (Spider-Based)

When no specification is available:

```bash
# Use standard spider with API context
docker run -v $(pwd):/zap/wrk/:rw -t zaproxy/zap-stable zap-full-scan.py \
  -t https://api.example.com \
  -r /zap/wrk/api-report.html \
  -z "-config spider.parseComments=true -config spider.parseRobotsTxt=true"
```

### Authentication Patterns

#### Bearer Token (JWT)

```bash
# Obtain token first
TOKEN=$(curl -X POST https://api.example.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password"}' \
  | jq -r '.access_token')

# Scan with authentication
python3 scripts/zap_api_scan.py \
  --target https://api.example.com \
  --format openapi \
  --spec openapi.yaml \
  --header "Authorization: Bearer $TOKEN"
```

#### API Key Authentication

```bash
# API key in header
python3 scripts/zap_api_scan.py \
  --target https://api.example.com \
  --format openapi \
  --spec openapi.yaml \
  --header "X-API-Key: your-api-key-here"

# API key in query parameter
python3 scripts/zap_api_scan.py \
  --target https://api.example.com?api_key=your-api-key \
  --format openapi \
  --spec openapi.yaml
```

### Common REST API Vulnerabilities

#### 1. Broken Object Level Authorization (BOLA)

**Detection:** Test access to resources belonging to other users.

**Manual Test:**
```bash
# Request resource with different user IDs
curl -H "Authorization: Bearer $USER1_TOKEN" \
  https://api.example.com/users/123/profile

curl -H "Authorization: Bearer $USER2_TOKEN" \
  https://api.example.com/users/123/profile  # Should be denied
```

**ZAP Configuration:**
Add authorization test scripts to detect BOLA.

#### 2. Mass Assignment

**Detection:** Send additional fields not in API specification.

**Test Payload:**
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "is_admin": true,  # Unauthorized field
  "role": "admin"    # Unauthorized field
}
```

#### 3. Rate Limiting

**Detection:** Send multiple requests rapidly.

```bash
# Test rate limiting
for i in {1..100}; do
  curl https://api.example.com/endpoint -H "Authorization: Bearer $TOKEN"
done
```

**Expected:** HTTP 429 (Too Many Requests) after threshold.

## GraphQL API Testing

### Testing with GraphQL Schema

```bash
# Scan GraphQL endpoint with schema
docker run -v $(pwd):/zap/wrk/:rw -t zaproxy/zap-stable zap-api-scan.py \
  -t https://api.example.com/graphql \
  -f graphql \
  -d /zap/wrk/schema.graphql \
  -r /zap/wrk/graphql-report.html
```

### GraphQL Introspection

**Check if introspection is enabled:**

```bash
curl -X POST https://api.example.com/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __schema { types { name } } }"}'
```

**Security Note:** Disable introspection in production.

### GraphQL-Specific Vulnerabilities

#### 1. Query Depth/Complexity Attacks

**Malicious Query:**
```graphql
query {
  user {
    posts {
      comments {
        author {
          posts {
            comments {
              author {
                # ... deeply nested
              }
            }
          }
        }
      }
    }
  }
}
```

**Mitigation:** Implement query depth/complexity limits.

#### 2. Batch Query Attacks

**Malicious Query:**
```graphql
query {
  user1: user(id: 1) { name email }
  user2: user(id: 2) { name email }
  # ... repeated hundreds of times
  user500: user(id: 500) { name email }
}
```

**Mitigation:** Limit batch query size.

#### 3. Field Suggestions

When introspection is disabled, test field suggestions:

```graphql
query {
  user {
    nam  # Intentional typo to trigger suggestions
  }
}
```

## SOAP API Testing

### Testing with WSDL

```bash
# SOAP API scan with WSDL
docker run -v $(pwd):/zap/wrk/:rw -t zaproxy/zap-stable zap-api-scan.py \
  -t https://api.example.com/soap \
  -f soap \
  -d /zap/wrk/service.wsdl \
  -r /zap/wrk/soap-report.html
```

### SOAP-Specific Vulnerabilities

#### 1. XML External Entity (XXE)

**Test Payload:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<soap:Envelope>
  <soap:Body>
    <login>
      <username>&xxe;</username>
    </login>
  </soap:Body>
</soap:Envelope>
```

#### 2. XML Injection

**Test Payload:**
```xml
<username>admin</username><role>admin</role></user><user><username>attacker</username>
```

## WebSocket Testing

### Manual WebSocket Testing

ZAP can intercept WebSocket traffic:

1. Configure browser proxy to ZAP
2. Connect to WebSocket endpoint
3. Review messages in ZAP's WebSocket tab
4. Manually craft malicious messages

### Common WebSocket Vulnerabilities

- **Message Injection:** Inject malicious payloads in WebSocket messages
- **Authentication Bypass:** Test if authentication is required for WebSocket connections
- **Message Tampering:** Modify messages in transit

## API Security Testing Checklist

### Authentication & Authorization

- [ ] Test unauthenticated access to protected endpoints
- [ ] Test authorization bypass (access other users' data)
- [ ] Test JWT token validation (expiration, signature)
- [ ] Test API key validation
- [ ] Test role-based access control (RBAC)

### Input Validation

- [ ] Test SQL injection in parameters
- [ ] Test NoSQL injection (MongoDB, etc.)
- [ ] Test command injection
- [ ] Test XML injection (for SOAP APIs)
- [ ] Test mass assignment vulnerabilities
- [ ] Test parameter pollution

### Rate Limiting & DoS

- [ ] Verify rate limiting is enforced
- [ ] Test resource exhaustion (large payloads)
- [ ] Test query complexity limits (GraphQL)
- [ ] Test batch request limits

### Data Exposure

- [ ] Check for sensitive data in responses
- [ ] Test verbose error messages
- [ ] Verify PII is properly protected
- [ ] Check for data leakage in logs

### Transport Security

- [ ] Verify HTTPS is enforced
- [ ] Test TLS configuration (strong ciphers only)
- [ ] Check certificate validation
- [ ] Verify HSTS header is set

### Business Logic

- [ ] Test state manipulation
- [ ] Test payment flow manipulation
- [ ] Test workflow bypass
- [ ] Test negative values/amounts

## ZAP Automation for API Testing

### Automation Framework Configuration

`api_automation.yaml`:

```yaml
env:
  contexts:
    - name: API-Context
      urls:
        - https://api.example.com
      includePaths:
        - https://api.example.com/.*
      authentication:
        method: header
        parameters:
          header: Authorization
          value: "Bearer ${API_TOKEN}"

jobs:
  - type: openapi
    parameters:
      apiFile: /zap/wrk/openapi.yaml
      apiUrl: https://api.example.com
      targetUrl: https://api.example.com
      context: API-Context

  - type: passiveScan-wait

  - type: activeScan
    parameters:
      context: API-Context
      policy: API-Scan-Policy
      user: api-user

  - type: report
    parameters:
      template: traditional-html
      reportDir: /zap/wrk/
      reportFile: api-security-report.html
      reportTitle: API Security Assessment
```

Run:

```bash
export API_TOKEN="your-token-here"
docker run -v $(pwd):/zap/wrk/:rw -t zaproxy/zap-stable \
  zap.sh -cmd -autorun /zap/wrk/api_automation.yaml
```

## Custom API Scan Policies

### Create API-Optimized Scan Policy

Disable irrelevant checks for APIs:
- Disable DOM XSS checks (no browser context)
- Disable CSRF checks (stateless APIs)
- Enable injection checks (SQL, NoSQL, Command)
- Enable authentication/authorization checks

See `assets/scan_policy_api.policy` for pre-configured policy.

## API Testing Tools Integration

### Postman Integration

Export Postman collection to OpenAPI:

```bash
# Use Postman's built-in export or newman
newman run collection.json --export-collection openapi.yaml
```

### cURL to OpenAPI Conversion

Use tools like `curl-to-openapi` to generate specs from cURL commands.

## Common API Testing Patterns

### Pattern 1: CRUD Operation Testing

Test all CRUD operations for each resource:

```bash
# CREATE
curl -X POST https://api.example.com/users \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"username":"testuser"}'

# READ
curl https://api.example.com/users/123 \
  -H "Authorization: Bearer $TOKEN"

# UPDATE
curl -X PUT https://api.example.com/users/123 \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"username":"updated"}'

# DELETE
curl -X DELETE https://api.example.com/users/123 \
  -H "Authorization: Bearer $TOKEN"
```

### Pattern 2: Multi-User Testing

Test with different user roles:

```bash
# Admin user
export ADMIN_TOKEN="admin-token"
python3 scripts/zap_api_scan.py --target https://api.example.com \
  --header "Authorization: Bearer $ADMIN_TOKEN"

# Regular user
export USER_TOKEN="user-token"
python3 scripts/zap_api_scan.py --target https://api.example.com \
  --header "Authorization: Bearer $USER_TOKEN"
```

### Pattern 3: Versioned API Testing

Test all API versions:

```bash
# v1
python3 scripts/zap_api_scan.py --target https://api.example.com/v1 \
  --spec openapi-v1.yaml

# v2
python3 scripts/zap_api_scan.py --target https://api.example.com/v2 \
  --spec openapi-v2.yaml
```

## Troubleshooting API Scans

### Issue: OpenAPI Import Fails

**Solution:** Validate OpenAPI spec:

```bash
# Use Swagger Editor or openapi-validator
npx @apidevtools/swagger-cli validate openapi.yaml
```

### Issue: Authentication Not Working

**Solution:** Test authentication manually first:

```bash
curl -v https://api.example.com/protected-endpoint \
  -H "Authorization: Bearer $TOKEN"
```

### Issue: Rate Limiting During Scan

**Solution:** Reduce scan speed:

```bash
docker run -t zaproxy/zap-stable zap-api-scan.py \
  -t https://api.example.com -f openapi -d /zap/wrk/spec.yaml \
  -z "-config scanner.delayInMs=1000"
```

## Additional Resources

- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [REST API Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html)
- [GraphQL Security](https://graphql.org/learn/authorization/)
- [ZAP OpenAPI Add-on](https://www.zaproxy.org/docs/desktop/addons/openapi-support/)
