# Spectral Custom Rules Development Guide

This guide covers creating custom security rules for Spectral to enforce organization-specific API security standards.

## Table of Contents

- [Rule Structure](#rule-structure)
- [JSONPath Expressions](#jsonpath-expressions)
- [Built-in Functions](#built-in-functions)
- [Security Rule Examples](#security-rule-examples)
- [Testing Custom Rules](#testing-custom-rules)
- [Best Practices](#best-practices)

## Rule Structure

Every Spectral rule consists of:

```yaml
rules:
  rule-name:
    description: Human-readable description
    severity: error|warn|info|hint
    given: JSONPath expression targeting specific parts of spec
    then:
      - field: property to check (optional)
        function: validation function
        functionOptions: function-specific options
    message: Error message shown when rule fails
```

### Severity Levels

- **error**: Critical security issues that must be fixed
- **warn**: Important security recommendations
- **info**: Best practices and suggestions
- **hint**: Style guide and documentation improvements

## JSONPath Expressions

### Basic Path Selection

```yaml
# Target all paths
given: $.paths[*]

# Target all GET operations
given: $.paths[*].get

# Target all HTTP methods
given: $.paths[*][get,post,put,patch,delete]

# Target security schemes
given: $.components.securitySchemes[*]

# Target all schemas
given: $.components.schemas[*]
```

### Advanced Filters

```yaml
# Filter by property value
given: $.paths[*][?(@.security)]

# Filter objects by type
given: $.components.schemas[?(@.type == 'object')]

# Filter parameters by location
given: $.paths[*][*].parameters[?(@.in == 'query')]

# Regular expression matching
given: $.paths[*][*].parameters[?(@.name =~ /^(id|.*_id)$/i)]

# Nested property access
given: $.paths[*][*].responses[?(@property >= 400)]
```

## Built-in Functions

### truthy / falsy

Check if field exists or doesn't exist:

```yaml
# Require field to exist
then:
  - field: security
    function: truthy

# Require field to not exist
then:
  - field: additionalProperties
    function: falsy
```

### pattern

Match string against regex pattern:

```yaml
# Match HTTPS URLs
then:
  function: pattern
  functionOptions:
    match: "^https://"

# Ensure no sensitive terms
then:
  function: pattern
  functionOptions:
    notMatch: "(password|secret|api[_-]?key)"
```

### enumeration

Restrict to specific values:

```yaml
# Require specific auth types
then:
  field: type
  function: enumeration
  functionOptions:
    values: [apiKey, oauth2, openIdConnect]
```

### length

Validate string/array length:

```yaml
# Minimum description length
then:
  field: description
  function: length
  functionOptions:
    min: 10
    max: 500
```

### schema

Validate against JSON Schema:

```yaml
# Require specific object structure
then:
  function: schema
  functionOptions:
    schema:
      type: object
      required: [error, message]
      properties:
        error:
          type: string
        message:
          type: string
```

### alphabetical

Ensure alphabetical ordering:

```yaml
# Require alphabetically sorted tags
then:
  field: tags
  function: alphabetical
```

## Security Rule Examples

### Prevent PII in URL Parameters

```yaml
no-pii-in-query-params:
  description: Query parameters must not contain PII
  severity: error
  given: $.paths[*][*].parameters[?(@.in == 'query')].name
  then:
    function: pattern
    functionOptions:
      notMatch: "(?i)(ssn|social.?security|credit.?card|password|passport|driver.?license|tax.?id|national.?id)"
  message: "Query parameter names suggest PII - use request body instead"
```

### Require API Key for Authentication

```yaml
require-api-key-security:
  description: APIs must use API key authentication
  severity: error
  given: $.components.securitySchemes
  then:
    function: schema
    functionOptions:
      schema:
        type: object
        minProperties: 1
        patternProperties:
          ".*":
            anyOf:
              - properties:
                  type:
                    const: apiKey
              - properties:
                  type:
                    const: oauth2
              - properties:
                  type:
                    const: openIdConnect
  message: "API must define apiKey, OAuth2, or OpenID Connect security"
```

### Enforce Rate Limiting Headers

```yaml
rate-limit-headers-present:
  description: Responses should include rate limit headers
  severity: warn
  given: $.paths[*][get,post,put,patch,delete].responses[?(@property == '200' || @property == '201')].headers
  then:
    function: schema
    functionOptions:
      schema:
        type: object
        anyOf:
          - required: [X-RateLimit-Limit]
          - required: [X-Rate-Limit-Limit]
  message: "Include rate limit headers (X-RateLimit-Limit, X-RateLimit-Remaining) in success responses"
```

### Detect Missing Authorization for Sensitive Operations

```yaml
sensitive-operations-require-security:
  description: Sensitive operations must have security requirements
  severity: error
  given: $.paths[*][post,put,patch,delete]
  then:
    - field: security
      function: truthy
  message: "Write operations must have security requirements defined"
```

### Prevent Verbose Error Messages

```yaml
no-verbose-error-responses:
  description: Error responses should not expose internal details
  severity: warn
  given: $.paths[*][*].responses[?(@property >= 500)].content.application/json.schema.properties
  then:
    function: schema
    functionOptions:
      schema:
        type: object
        not:
          anyOf:
            - required: [stack_trace]
            - required: [stackTrace]
            - required: [debug_info]
            - required: [internal_message]
  message: "5xx error responses should not expose stack traces or internal details"
```

### Require Audit Fields in Schemas

```yaml
require-audit-fields:
  description: Data models should include audit fields
  severity: info
  given: $.components.schemas[?(@.type == 'object' && @.properties)]
  then:
    function: schema
    functionOptions:
      schema:
        type: object
        properties:
          properties:
            type: object
            anyOf:
              - required: [created_at, updated_at]
              - required: [createdAt, updatedAt]
  message: "Consider adding audit fields (created_at, updated_at) to data models"
```

### Detect Insecure Content Types

```yaml
no-insecure-content-types:
  description: Avoid insecure content types
  severity: warn
  given: $.paths[*][*].requestBody.content
  then:
    function: schema
    functionOptions:
      schema:
        type: object
        not:
          required: [text/html, text/xml, application/x-www-form-urlencoded]
  message: "Prefer application/json over HTML, XML, or form-encoded content types"
```

### Validate JWT Security Configuration

```yaml
jwt-proper-configuration:
  description: JWT bearer authentication should be properly configured
  severity: error
  given: $.components.securitySchemes[?(@.type == 'http' && @.scheme == 'bearer')]
  then:
    - field: bearerFormat
      function: pattern
      functionOptions:
        match: "^JWT$"
  message: "Bearer authentication should specify 'JWT' as bearerFormat"
```

### Require CORS Documentation

```yaml
cors-options-documented:
  description: CORS preflight endpoints should be documented
  severity: warn
  given: $.paths[*]
  then:
    function: schema
    functionOptions:
      schema:
        type: object
        if:
          properties:
            get:
              type: object
        then:
          properties:
            options:
              type: object
              required: [responses]
  message: "Document OPTIONS method for CORS preflight requests"
```

### Prevent Numeric IDs in URLs

```yaml
prefer-uuid-over-numeric-ids:
  description: Use UUIDs instead of numeric IDs to prevent enumeration
  severity: info
  given: $.paths.*~
  then:
    function: pattern
    functionOptions:
      notMatch: "\\{id\\}|\\{.*_id\\}"
  message: "Consider using UUIDs instead of numeric IDs to prevent enumeration attacks"
```

## Testing Custom Rules

### Create Test Specifications

```yaml
# test-specs/valid-auth.yaml
openapi: 3.0.0
info:
  title: Valid API
  version: 1.0.0
components:
  securitySchemes:
    apiKey:
      type: apiKey
      in: header
      name: X-API-Key
security:
  - apiKey: []
```

```yaml
# test-specs/invalid-auth.yaml
openapi: 3.0.0
info:
  title: Invalid API
  version: 1.0.0
components:
  securitySchemes:
    basicAuth:
      type: http
      scheme: basic
security:
  - basicAuth: []
```

### Test Rules

```bash
# Test custom ruleset
spectral lint test-specs/valid-auth.yaml --ruleset .spectral-custom.yaml

# Expected: No errors

spectral lint test-specs/invalid-auth.yaml --ruleset .spectral-custom.yaml

# Expected: Error about HTTP Basic auth
```

### Automated Testing Script

```bash
#!/bin/bash
# test-rules.sh - Test custom Spectral rules

RULESET=".spectral-custom.yaml"
TEST_DIR="test-specs"
PASS=0
FAIL=0

for spec in "$TEST_DIR"/*.yaml; do
    echo "Testing: $spec"

    if spectral lint "$spec" --ruleset "$RULESET" > /dev/null 2>&1; then
        if [[ "$spec" == *"valid"* ]]; then
            echo "  ✓ PASS (correctly validated)"
            ((PASS++))
        else
            echo "  ✗ FAIL (should have detected issues)"
            ((FAIL++))
        fi
    else
        if [[ "$spec" == *"invalid"* ]]; then
            echo "  ✓ PASS (correctly detected issues)"
            ((PASS++))
        else
            echo "  ✗ FAIL (false positive)"
            ((FAIL++))
        fi
    fi
done

echo ""
echo "Results: $PASS passed, $FAIL failed"
```

## Best Practices

### 1. Start with Built-in Rules

Extend existing rulesets instead of starting from scratch:

```yaml
extends: ["spectral:oas", "spectral:asyncapi"]

rules:
  # Add custom rules here
  custom-security-rule:
    # ...
```

### 2. Use Descriptive Names

Rule names should clearly indicate what they check:

```yaml
# Good
no-pii-in-query-params:
require-https-servers:
jwt-bearer-format-required:

# Bad
check-params:
security-rule-1:
validate-auth:
```

### 3. Provide Actionable Messages

```yaml
# Good
message: "Query parameters must not contain PII (ssn, credit_card) - use request body instead"

# Bad
message: "Invalid parameter"
```

### 4. Choose Appropriate Severity

```yaml
# error - Must fix (security vulnerabilities)
severity: error

# warn - Should fix (security best practices)
severity: warn

# info - Consider fixing (recommendations)
severity: info

# hint - Nice to have (style guide)
severity: hint
```

### 5. Document Rule Rationale

```yaml
rules:
  no-numeric-ids:
    description: |
      Use UUIDs instead of auto-incrementing numeric IDs in URLs to prevent
      enumeration attacks where attackers can guess valid IDs sequentially.
      This follows OWASP API Security best practices for API1:2023.
    severity: warn
    # ...
```

### 6. Use Rule Overrides for Exceptions

```yaml
# Allow specific paths to violate rules
overrides:
  - files: ["**/internal-api.yaml"]
    rules:
      require-https-servers: off

  - files: ["**/admin-api.yaml"]
    rules:
      no-http-basic-auth: warn  # Downgrade to warning
```

### 7. Organize Rules by Category

```yaml
# .spectral.yaml - Main ruleset
extends:
  - .spectral-auth.yaml        # Authentication rules
  - .spectral-authz.yaml       # Authorization rules
  - .spectral-data.yaml        # Data protection rules
  - .spectral-owasp.yaml       # OWASP mappings
```

### 8. Version Control Your Rulesets

```bash
# Track ruleset evolution
git log -p .spectral.yaml

# Tag stable ruleset versions
git tag -a ruleset-v1.0 -m "Production-ready security ruleset"
```

## Additional Resources

- [Spectral Rulesets Documentation](https://docs.stoplight.io/docs/spectral/docs/getting-started/rulesets.md)
- [JSONPath Online Evaluator](https://jsonpath.com/)
- [Custom Functions Guide](./custom_functions.md)
- [OWASP API Security Mappings](./owasp_api_mappings.md)
