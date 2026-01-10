# OWASP API Security Top 10 2023 - Spectral Rule Mappings

This reference provides comprehensive Spectral rule mappings to OWASP API Security Top 10 2023, including custom rule examples for detecting each category of vulnerability.

## Table of Contents

- [API1:2023 - Broken Object Level Authorization](#api12023---broken-object-level-authorization)
- [API2:2023 - Broken Authentication](#api22023---broken-authentication)
- [API3:2023 - Broken Object Property Level Authorization](#api32023---broken-object-property-level-authorization)
- [API4:2023 - Unrestricted Resource Consumption](#api42023---unrestricted-resource-consumption)
- [API5:2023 - Broken Function Level Authorization](#api52023---broken-function-level-authorization)
- [API6:2023 - Unrestricted Access to Sensitive Business Flows](#api62023---unrestricted-access-to-sensitive-business-flows)
- [API7:2023 - Server Side Request Forgery](#api72023---server-side-request-forgery)
- [API8:2023 - Security Misconfiguration](#api82023---security-misconfiguration)
- [API9:2023 - Improper Inventory Management](#api92023---improper-inventory-management)
- [API10:2023 - Unsafe Consumption of APIs](#api102023---unsafe-consumption-of-apis)

---

## API1:2023 - Broken Object Level Authorization

**Description**: APIs tend to expose endpoints that handle object identifiers, creating a wide attack surface Level Access Control issue. Object level authorization checks should be considered in every function that accesses a data source using an input from the user.

### Spectral Rules

```yaml
# .spectral-api1.yaml
rules:
  # Require security on all operations
  operation-security-defined:
    description: All operations must have security requirements (OWASP API1)
    severity: error
    given: $.paths[*][get,post,put,patch,delete]
    then:
      - field: security
        function: truthy
    message: "Operations must define security requirements to prevent unauthorized object access (OWASP API1:2023)"

  # Detect ID parameters without authorization checks
  id-parameter-requires-security:
    description: Operations with ID parameters must have security defined
    severity: error
    given: $.paths[*][*].parameters[?(@.name =~ /^(id|.*[_-]id)$/i)]
    then:
      function: falsy
    message: "Path contains ID parameter - ensure operation has security requirements (OWASP API1:2023)"

  # Require authorization scopes for CRUD operations
  crud-requires-authorization-scope:
    description: CRUD operations should specify authorization scopes
    severity: warn
    given: $.paths[*][get,post,put,patch,delete].security[*]
    then:
      function: schema
      functionOptions:
        schema:
          type: object
          minProperties: 1
    message: "CRUD operations should specify authorization scopes (OWASP API1:2023)"
```

### Remediation

- Implement object-level authorization checks in API specification security requirements
- Define per-operation security schemes with appropriate scopes
- Document which user roles can access which objects
- Consider using OAuth 2.0 with fine-grained scopes

---

## API2:2023 - Broken Authentication

**Description**: Authentication mechanisms are often implemented incorrectly, allowing attackers to compromise authentication tokens or exploit implementation flaws to assume other users' identities.

### Spectral Rules

```yaml
# .spectral-api2.yaml
rules:
  # Require security schemes definition
  security-schemes-required:
    description: API must define security schemes (OWASP API2)
    severity: error
    given: $.components
    then:
      - field: securitySchemes
        function: truthy
    message: "API must define security schemes to prevent authentication bypass (OWASP API2:2023)"

  # Prohibit HTTP Basic authentication
  no-http-basic-auth:
    description: HTTP Basic auth is insecure for APIs
    severity: error
    given: $.components.securitySchemes[*]
    then:
      - field: scheme
        function: pattern
        functionOptions:
          notMatch: "^basic$"
    message: "HTTP Basic authentication transmits credentials in plain text (OWASP API2:2023)"

  # Require bearer token format specification
  bearer-format-required:
    description: Bearer authentication should specify token format (JWT recommended)
    severity: warn
    given: $.components.securitySchemes[?(@.type == 'http' && @.scheme == 'bearer')]
    then:
      - field: bearerFormat
        function: truthy
    message: "Bearer authentication should specify token format, preferably JWT (OWASP API2:2023)"

  # Require OAuth2 flow for authentication
  oauth2-recommended:
    description: OAuth2 provides secure authentication flows
    severity: info
    given: $.components.securitySchemes[*]
    then:
      - field: type
        function: enumeration
        functionOptions:
          values: [oauth2, openIdConnect, http]
    message: "Consider using OAuth2 or OpenID Connect for robust authentication (OWASP API2:2023)"
```

### Remediation

- Use OAuth 2.0 or OpenID Connect for authentication
- Implement JWT with proper expiration and signature validation
- Avoid HTTP Basic authentication for production APIs
- Document authentication flows and token refresh mechanisms

---

## API3:2023 - Broken Object Property Level Authorization

**Description**: This category combines API3:2019 Excessive Data Exposure and API6:2019 Mass Assignment, focusing on the root cause: the lack of or improper authorization validation at the object property level.

### Spectral Rules

```yaml
# .spectral-api3.yaml
rules:
  # Prohibit additionalProperties for security
  no-additional-properties:
    description: Prevent mass assignment by disabling additionalProperties
    severity: warn
    given: $.components.schemas[*]
    then:
      - field: additionalProperties
        function: falsy
    message: "Set additionalProperties to false to prevent mass assignment vulnerabilities (OWASP API3:2023)"

  # Require explicit property definitions
  schema-properties-required:
    description: Schemas should explicitly define all properties
    severity: warn
    given: $.components.schemas[?(@.type == 'object')]
    then:
      - field: properties
        function: truthy
    message: "Explicitly define all object properties to control data exposure (OWASP API3:2023)"

  # Warn on write-only properties
  detect-write-only-properties:
    description: Document write-only properties to prevent data exposure
    severity: info
    given: $.components.schemas[*].properties[*]
    then:
      - field: writeOnly
        function: truthy
    message: "Ensure write-only properties are properly handled (OWASP API3:2023)"

  # Require read-only for sensitive computed fields
  computed-fields-read-only:
    description: Computed fields should be marked as readOnly
    severity: warn
    given: $.components.schemas[*].properties[?(@.description =~ /calculated|computed|derived/i)]
    then:
      - field: readOnly
        function: truthy
    message: "Mark computed/calculated fields as readOnly (OWASP API3:2023)"
```

### Remediation

- Set `additionalProperties: false` in schemas to prevent mass assignment
- Use `readOnly` for properties that shouldn't be modified by clients
- Use `writeOnly` for sensitive input properties (passwords, tokens)
- Document which properties are accessible to which user roles

---

## API4:2023 - Unrestricted Resource Consumption

**Description**: Satisfying API requests requires resources such as network bandwidth, CPU, memory, and storage. Sometimes required resources are made available by service providers via API integrations, and paid for per request, such as sending emails/SMS/phone calls, biometrics validation, etc.

### Spectral Rules

```yaml
# .spectral-api4.yaml
rules:
  # Require rate limit documentation
  rate-limit-headers-documented:
    description: API should document rate limiting headers
    severity: warn
    given: $.paths[*][*].responses[*].headers
    then:
      function: schema
      functionOptions:
        schema:
          type: object
          properties:
            X-RateLimit-Limit:
              type: object
            X-RateLimit-Remaining:
              type: object
    message: "Document rate limiting headers (X-RateLimit-*) to communicate consumption limits (OWASP API4:2023)"

  # Detect pagination parameters
  pagination-required:
    description: List operations should support pagination
    severity: warn
    given: $.paths[*].get.parameters
    then:
      function: schema
      functionOptions:
        schema:
          type: array
          contains:
            anyOf:
              - properties:
                  name:
                    const: limit
              - properties:
                  name:
                    const: offset
    message: "List operations should support pagination (limit/offset or cursor) to prevent resource exhaustion (OWASP API4:2023)"

  # Maximum response size documentation
  response-size-limits:
    description: Document maximum response sizes
    severity: info
    given: $.paths[*][*].responses[*]
    then:
      - field: description
        function: pattern
        functionOptions:
          match: "(maximum|max|limit).*(size|length|count)"
    message: "Consider documenting maximum response sizes (OWASP API4:2023)"
```

### Remediation

- Implement rate limiting and document limits in API specification
- Use pagination for all list operations (limit/offset or cursor-based)
- Document maximum request/response sizes
- Implement request timeout and maximum execution time limits

---

## API8:2023 - Security Misconfiguration

**Description**: APIs and the systems supporting them typically contain complex configurations, meant to make the APIs more customizable. Software and DevOps engineers can miss these configurations, or don't follow security best practices when it comes to configuration, opening the door for different types of attacks.

### Spectral Rules

```yaml
# .spectral-api8.yaml
rules:
  # Require HTTPS for all servers
  servers-use-https:
    description: All API servers must use HTTPS
    severity: error
    given: $.servers[*].url
    then:
      function: pattern
      functionOptions:
        match: "^https://"
    message: "Server URLs must use HTTPS protocol for secure communication (OWASP API8:2023)"

  # Detect example.com in server URLs
  no-example-servers:
    description: Replace example server URLs with actual endpoints
    severity: error
    given: $.servers[*].url
    then:
      function: pattern
      functionOptions:
        notMatch: "example\\.com"
    message: "Replace example.com with actual server URL (OWASP API8:2023)"

  # Require security headers documentation
  security-headers-documented:
    description: Document security headers in responses
    severity: warn
    given: $.paths[*][*].responses[*].headers
    then:
      function: schema
      functionOptions:
        schema:
          type: object
          anyOf:
            - required: [X-Content-Type-Options]
            - required: [X-Frame-Options]
            - required: [Strict-Transport-Security]
    message: "Document security headers (X-Content-Type-Options, X-Frame-Options, HSTS) in responses (OWASP API8:2023)"

  # CORS configuration review
  cors-documented:
    description: CORS should be properly configured and documented
    severity: info
    given: $.paths[*].options
    then:
      - field: responses
        function: truthy
    message: "Ensure CORS is properly configured - review Access-Control-* headers (OWASP API8:2023)"
```

### Remediation

- Use HTTPS for all API endpoints
- Configure and document security headers (HSTS, X-Content-Type-Options, X-Frame-Options)
- Properly configure CORS with specific origins (avoid wildcard in production)
- Disable unnecessary HTTP methods
- Remove verbose error messages in production

---

## API9:2023 - Improper Inventory Management

**Description**: APIs tend to expose more endpoints than traditional web applications, making proper and updated documentation highly important. A proper inventory of hosts and deployed API versions also are important to mitigate issues such as deprecated API versions and exposed debug endpoints.

### Spectral Rules

```yaml
# .spectral-api9.yaml
rules:
  # Require API version
  api-version-required:
    description: API specification must include version
    severity: error
    given: $.info
    then:
      - field: version
        function: truthy
    message: "API version must be specified for proper inventory management (OWASP API9:2023)"

  # Version format validation
  semantic-versioning:
    description: Use semantic versioning for API versions
    severity: warn
    given: $.info.version
    then:
      function: pattern
      functionOptions:
        match: "^\\d+\\.\\d+\\.\\d+"
    message: "Use semantic versioning (MAJOR.MINOR.PATCH) for API versions (OWASP API9:2023)"

  # Require contact information
  contact-info-required:
    description: API must include contact information
    severity: warn
    given: $.info
    then:
      - field: contact
        function: truthy
    message: "Include contact information for API support and security issues (OWASP API9:2023)"

  # Require terms of service or license
  legal-info-required:
    description: API should include legal information
    severity: info
    given: $.info
    then:
      - field: license
        function: truthy
    message: "Include license or terms of service for API usage (OWASP API9:2023)"

  # Deprecation documentation
  deprecated-endpoints-documented:
    description: Deprecated endpoints must be clearly marked
    severity: warn
    given: $.paths[*][*][?(@.deprecated == true)]
    then:
      - field: description
        function: pattern
        functionOptions:
          match: "(deprecate|migrate|alternative|replacement)"
    message: "Document deprecation details and migration path (OWASP API9:2023)"
```

### Remediation

- Maintain up-to-date API specification with version information
- Use semantic versioning for API versions
- Document all endpoints, including internal and deprecated ones
- Include contact information for security issues
- Implement API inventory management and discovery tools
- Remove or properly secure debug/admin endpoints in production

---

## Complete OWASP Ruleset Example

```yaml
# .spectral-owasp-complete.yaml
extends: ["spectral:oas"]

rules:
  # API1: Broken Object Level Authorization
  operation-security-defined:
    severity: error
    message: "All operations must have security defined (OWASP API1:2023)"

  # API2: Broken Authentication
  no-http-basic-auth:
    description: Prohibit HTTP Basic authentication
    severity: error
    given: $.components.securitySchemes[*]
    then:
      field: scheme
      function: pattern
      functionOptions:
        notMatch: "^basic$"
    message: "HTTP Basic auth is insecure (OWASP API2:2023)"

  # API3: Broken Object Property Level Authorization
  no-additional-properties:
    description: Prevent mass assignment
    severity: warn
    given: $.components.schemas[?(@.type == 'object')]
    then:
      field: additionalProperties
      function: falsy
    message: "Set additionalProperties to false (OWASP API3:2023)"

  # API4: Unrestricted Resource Consumption
  pagination-for-lists:
    description: List operations should support pagination
    severity: warn
    given: $.paths[*].get
    then:
      function: truthy
    message: "Implement pagination for list operations (OWASP API4:2023)"

  # API8: Security Misconfiguration
  servers-use-https:
    description: All servers must use HTTPS
    severity: error
    given: $.servers[*].url
    then:
      function: pattern
      functionOptions:
        match: "^https://"
    message: "Server URLs must use HTTPS (OWASP API8:2023)"

  # API9: Improper Inventory Management
  api-version-required:
    description: API must specify version
    severity: error
    given: $.info
    then:
      field: version
      function: truthy
    message: "API version is required (OWASP API9:2023)"
```

## Additional Resources

- [OWASP API Security Top 10 2023](https://owasp.org/API-Security/editions/2023/en/0x11-t10/)
- [Spectral Rulesets Documentation](https://docs.stoplight.io/docs/spectral/docs/getting-started/rulesets.md)
- [OpenAPI Security Best Practices](https://swagger.io/docs/specification/authentication/)
