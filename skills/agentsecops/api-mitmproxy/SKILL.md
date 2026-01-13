---
name: api-mitmproxy
description: >
  Interactive HTTPS proxy for API security testing with traffic interception, modification, and
  replay capabilities. Supports HTTP/1, HTTP/2, HTTP/3, WebSockets, and TLS-protected protocols.
  Includes Python scripting API for automation and multiple interfaces (console, web, CLI). Use when:
  (1) Intercepting and analyzing API traffic for security testing, (2) Modifying HTTP/HTTPS requests
  and responses to test API behavior, (3) Recording and replaying API traffic for testing, (4)
  Debugging mobile app or thick client API communications, (5) Automating API security tests with
  Python scripts, (6) Exporting traffic in HAR format for analysis.
version: 0.1.0
maintainer: SirAppSec
category: appsec
tags: [api-testing, proxy, https, intercepting-proxy, traffic-analysis, mitmproxy, har-export, websockets]
frameworks: [OWASP]
dependencies:
  python: ">=3.9"
  tools: [mitmproxy, mitmweb, mitmdump]
references:
  - https://mitmproxy.org/
  - https://docs.mitmproxy.org/
---

# mitmproxy API Security Testing

## Overview

mitmproxy is an interactive, TLS-capable intercepting HTTP proxy for penetration testers and developers. It enables real-time inspection, modification, and replay of HTTP/HTTPS traffic including APIs, mobile apps, and thick clients. With support for HTTP/1, HTTP/2, HTTP/3, and WebSockets, mitmproxy provides comprehensive coverage for modern API security testing.

## Interfaces

**mitmproxy** - Interactive console interface with keyboard navigation
**mitmweb** - Web-based GUI for visual traffic inspection
**mitmdump** - Command-line tool for automated traffic capture and scripting

## Quick Start

Install and run mitmproxy:

```bash
# Install via pip
pip install mitmproxy

# Start interactive console proxy
mitmproxy

# Start web interface (default: http://127.0.0.1:8081)
mitmweb

# Start command-line proxy with output
mitmdump -w traffic.flow
```

Configure client to use proxy (default: localhost:8080)

## Core Workflows

### Workflow 1: Interactive API Traffic Inspection

For manual API security testing and analysis:

1. Start mitmproxy or mitmweb:
   ```bash
   # Console interface
   mitmproxy --mode regular --listen-host 0.0.0.0 --listen-port 8080

   # Or web interface
   mitmweb --mode regular --listen-host 0.0.0.0 --listen-port 8080
   ```
2. Configure target application to use proxy (HTTP: localhost:8080)
3. Install mitmproxy CA certificate on client device
4. Trigger API requests from the application
5. Intercept and inspect requests/responses in mitmproxy
6. Modify requests to test:
   - Authentication bypass attempts
   - Authorization flaws (IDOR, privilege escalation)
   - Input validation (SQLi, XSS, command injection)
   - Business logic vulnerabilities
7. Save flows for documentation and reporting

### Workflow 2: Mobile App API Security Testing

Progress:
[ ] 1. Install mitmproxy CA certificate on mobile device
[ ] 2. Configure device WiFi to use mitmproxy as proxy
[ ] 3. Start mitmweb for visual traffic inspection
[ ] 4. Launch mobile app and exercise all features
[ ] 5. Review API endpoints, authentication mechanisms, data flows
[ ] 6. Test for common API vulnerabilities (OWASP API Top 10)
[ ] 7. Export traffic as HAR for further analysis
[ ] 8. Document findings with request/response examples

Work through each step systematically. Check off completed items.

### Workflow 3: Automated API Traffic Recording

For capturing and analyzing API traffic at scale:

1. Start mitmdump with flow capture:
   ```bash
   mitmdump -w api-traffic.flow --mode regular
   ```
2. Run automated tests or manual app interaction
3. Stop mitmdump (Ctrl+C) to save flows
4. Replay captured traffic:
   ```bash
   # Replay to server
   mitmdump -nc -r api-traffic.flow

   # Replay with modifications via script
   mitmdump -s replay-script.py -r api-traffic.flow
   ```
5. Export to HAR format for analysis:
   ```bash
   # Using Python API
   python3 -c "from mitmproxy.io import FlowReader; from mitmproxy.tools.dump import DumpMaster;
   import sys; [print(flow.request.url) for flow in FlowReader(open('api-traffic.flow', 'rb')).stream()]"
   ```

### Workflow 4: Python Scripting for API Testing

For automated security testing with custom logic:

1. Create Python addon script (`api-test.py`):
   ```python
   from mitmproxy import http

   class APISecurityTester:
       def request(self, flow: http.HTTPFlow) -> None:
           # Modify requests on-the-fly
           if "api.example.com" in flow.request.pretty_url:
               # Test for authorization bypass
               flow.request.headers["X-User-ID"] = "1"

       def response(self, flow: http.HTTPFlow) -> None:
           # Analyze responses
           if flow.response.status_code == 200:
               if "admin" in flow.response.text:
                   print(f"[!] Potential privilege escalation: {flow.request.url}")

   addons = [APISecurityTester()]
   ```
2. Run mitmproxy with script:
   ```bash
   mitmproxy -s api-test.py
   # Or for automation
   mitmdump -s api-test.py -w results.flow
   ```
3. Review automated findings and captured traffic
4. Export results for reporting

### Workflow 5: SSL/TLS Certificate Pinning Bypass

For testing mobile apps with certificate pinning:

1. Install mitmproxy CA certificate on device
2. Use certificate unpinning tools or framework modifications:
   - Android: Frida script for SSL unpinning
   - iOS: SSL Kill Switch or similar tools
3. Configure app traffic through mitmproxy
4. Alternatively, use reverse proxy mode:
   ```bash
   mitmproxy --mode reverse:https://api.example.com --listen-host 0.0.0.0 --listen-port 443
   ```
5. Modify /etc/hosts to redirect API domain to mitmproxy
6. Intercept and analyze traffic normally

## Operating Modes

mitmproxy supports multiple deployment modes:

**Regular Proxy Mode** (default):
```bash
mitmproxy --mode regular --listen-port 8080
```
Client configures proxy settings explicitly.

**Transparent Proxy Mode** (invisible to client):
```bash
mitmproxy --mode transparent --listen-port 8080
```
Requires iptables/pf rules to redirect traffic.

**Reverse Proxy Mode** (sits in front of server):
```bash
mitmproxy --mode reverse:https://api.example.com --listen-port 443
```
mitmproxy acts as the server endpoint.

**Upstream Proxy Mode** (chain proxies):
```bash
mitmproxy --mode upstream:http://corporate-proxy:8080
```
Routes traffic through another proxy.

## Certificate Installation

Install mitmproxy CA certificate for HTTPS interception:

**Browser/Desktop:**
1. Start mitmproxy and configure proxy settings
2. Visit http://mitm.it
3. Download certificate for your platform
4. Install in system/browser certificate store

**Android:**
1. Push certificate to device: `adb push ~/.mitmproxy/mitmproxy-ca-cert.cer /sdcard/`
2. Settings → Security → Install from SD card
3. Select mitmproxy certificate

**iOS:**
1. Email certificate or host on web server
2. Install profile on device
3. Settings → General → About → Certificate Trust Settings
4. Enable trust for mitmproxy certificate

## Common Patterns

### Pattern 1: API Authentication Testing

Test authentication mechanisms and token handling:

```python
# auth-test.py
from mitmproxy import http

class AuthTester:
    def __init__(self):
        self.tokens = []

    def request(self, flow: http.HTTPFlow):
        # Capture auth tokens
        if "authorization" in flow.request.headers:
            token = flow.request.headers["authorization"]
            if token not in self.tokens:
                self.tokens.append(token)
                print(f"[+] Captured token: {token[:20]}...")

        # Test for missing authentication
        if "api.example.com" in flow.request.url:
            flow.request.headers.pop("authorization", None)
            print(f"[*] Testing unauthenticated: {flow.request.path}")

addons = [AuthTester()]
```

### Pattern 2: API Parameter Fuzzing

Fuzz API parameters for injection vulnerabilities:

```python
# fuzz-params.py
from mitmproxy import http

class ParamFuzzer:
    def request(self, flow: http.HTTPFlow):
        if flow.request.method == "POST" and "api.example.com" in flow.request.url:
            # Clone and modify request
            original_body = flow.request.text
            payloads = ["' OR '1'='1", "<script>alert(1)</script>", "../../../etc/passwd"]

            for payload in payloads:
                # Modify parameters and test
                # (Implementation depends on content-type)
                print(f"[*] Testing payload: {payload}")

addons = [ParamFuzzer()]
```

### Pattern 3: GraphQL API Testing

Inspect and test GraphQL APIs:

```python
# graphql-test.py
from mitmproxy import http
import json

class GraphQLTester:
    def request(self, flow: http.HTTPFlow):
        if "/graphql" in flow.request.path:
            try:
                data = json.loads(flow.request.text)
                query = data.get("query", "")
                print(f"[+] GraphQL Query:\n{query}")

                # Test for introspection
                if "__schema" not in query:
                    introspection = {"query": "{__schema{types{name}}}"}
                    print(f"[*] Testing introspection")
            except:
                pass

addons = [GraphQLTester()]
```

### Pattern 4: HAR Export for Analysis

Export traffic as HTTP Archive for analysis:

```bash
# Export flows to HAR format
mitmdump -s export-har.py -r captured-traffic.flow

# export-har.py
from mitmproxy import http, ctx
import json

class HARExporter:
    def done(self):
        har_entries = []
        # Build HAR structure
        # (Simplified - use mitmproxy's built-in HAR addon)
        ctx.log.info(f"Exported {len(har_entries)} entries")

addons = [HARExporter()]
```

Or use built-in addon:
```bash
mitmdump --set hardump=./traffic.har
```

## Security Considerations

- **Sensitive Data Handling**: Captured traffic may contain credentials, tokens, PII. Encrypt and secure stored flows. Never commit flow files to version control
- **Access Control**: Restrict access to mitmproxy instance. Use authentication for mitmweb (--web-user/--web-password flags)
- **Audit Logging**: Log all intercepted traffic and modifications for security auditing and compliance
- **Compliance**: Ensure proper authorization before intercepting production traffic. Comply with GDPR, PCI-DSS for sensitive data
- **Safe Defaults**: Use isolated testing environments. Avoid intercepting production traffic without explicit authorization

## Integration Points

### Penetration Testing Workflow

1. Reconnaissance: Identify API endpoints via mitmproxy
2. Authentication testing: Capture and analyze auth tokens
3. Authorization testing: Modify user IDs, roles, permissions
4. Input validation: Inject payloads to test for vulnerabilities
5. Business logic: Test workflows for logical flaws
6. Export findings as HAR for reporting

### CI/CD Integration

Run automated API security tests:

```bash
# Run mitmdump with test script in CI
mitmdump -s api-security-tests.py --anticache -w test-results.flow &
PROXY_PID=$!

# Run API tests through proxy
export HTTP_PROXY=http://localhost:8080
export HTTPS_PROXY=http://localhost:8080
pytest tests/api_tests.py

# Stop proxy and analyze results
kill $PROXY_PID
python3 analyze-results.py test-results.flow
```

### Mobile App Security Testing

Standard workflow for iOS/Android apps:
1. Configure device to use mitmproxy
2. Install CA certificate
3. Bypass SSL pinning if needed
4. Exercise app functionality
5. Analyze API security (OWASP Mobile Top 10)
6. Document API vulnerabilities

## Advanced Features

### Traffic Filtering

Filter displayed traffic by expression:

```bash
# Show only API calls
mitmproxy --view-filter '~d api.example.com'

# Show only POST requests
mitmproxy --view-filter '~m POST'

# Show responses with specific status
mitmproxy --view-filter '~c 401'

# Combine filters
mitmproxy --view-filter '~d api.example.com & ~m POST'
```

### Request/Response Modification

Modify traffic using built-in mappers:

```bash
# Replace request headers
mitmproxy --modify-headers '/~u example/Authorization/Bearer fake-token'

# Replace response body
mitmproxy --modify-body '/~s & ~b "error"/success'
```

### WebSocket Interception

Intercept and modify WebSocket traffic:

```python
# websocket-test.py
from mitmproxy import websocket

class WebSocketTester:
    def websocket_message(self, flow):
        message = flow.messages[-1]
        print(f"[+] WebSocket: {message.content[:100]}")

        # Modify messages
        if message.from_client:
            message.content = message.content.replace(b"user", b"admin")

addons = [WebSocketTester()]
```

## Troubleshooting

### Issue: SSL Certificate Errors

**Solution**: Ensure mitmproxy CA certificate is properly installed and trusted:
```bash
# Verify certificate location
ls ~/.mitmproxy/

# Regenerate certificates if needed
rm -rf ~/.mitmproxy/
mitmproxy  # Regenerates on startup
```

### Issue: Mobile App Not Sending Traffic Through Proxy

**Solution**:
- Verify WiFi proxy configuration
- Check firewall rules aren't blocking proxy port
- Ensure mitmproxy is listening on correct interface (0.0.0.0)
- Test with browser first to verify proxy works

### Issue: Certificate Pinning Blocking Interception

**Solution**: Use SSL unpinning tools:
```bash
# Android with Frida
frida -U -l universal-android-ssl-pinning-bypass.js -f com.example.app

# Or modify app to disable pinning (development builds)
```

### Issue: Cannot Intercept HTTP/2 or HTTP/3

**Solution**: mitmproxy supports HTTP/2 by default. For HTTP/3:
```bash
# Enable HTTP/3 support (experimental)
mitmproxy --set http3=true
```

## OWASP API Security Top 10 Testing

Use mitmproxy to test for OWASP API Security Top 10 vulnerabilities:

- **API1: Broken Object Level Authorization** - Modify object IDs in requests
- **API2: Broken Authentication** - Test token validation, session management
- **API3: Broken Object Property Level Authorization** - Test for mass assignment
- **API4: Unrestricted Resource Consumption** - Test rate limiting, pagination
- **API5: Broken Function Level Authorization** - Modify roles, escalate privileges
- **API6: Unrestricted Access to Sensitive Business Flows** - Test business logic
- **API7: Server Side Request Forgery** - Inject URLs in parameters
- **API8: Security Misconfiguration** - Check headers, CORS, error messages
- **API9: Improper Inventory Management** - Enumerate undocumented endpoints
- **API10: Unsafe Consumption of APIs** - Test third-party API integrations

## References

- [mitmproxy Documentation](https://docs.mitmproxy.org/)
- [mitmproxy GitHub](https://github.com/mitmproxy/mitmproxy)
- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [mitmproxy Addon Examples](https://github.com/mitmproxy/mitmproxy/tree/main/examples)
