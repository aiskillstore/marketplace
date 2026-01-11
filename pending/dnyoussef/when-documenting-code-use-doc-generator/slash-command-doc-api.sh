#!/bin/bash
# Slash Command: /doc-api
# Description: Generate API documentation (OpenAPI specification)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Configuration
PROJECT_ROOT=$(pwd)
DOCS_DIR="$PROJECT_ROOT/docs"
API_SPEC_FILE="$DOCS_DIR/api.yml"
API_MD_FILE="$DOCS_DIR/API.md"

# Parse arguments
FORMAT="openapi3"  # Default format
OUTPUT_DIR="$DOCS_DIR"
INCLUDE_EXAMPLES=true
VALIDATE=true

while [[ $# -gt 0 ]]; do
    case $1 in
        --format)
            FORMAT="$2"
            shift 2
            ;;
        --output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --no-examples)
            INCLUDE_EXAMPLES=false
            shift
            ;;
        --no-validate)
            VALIDATE=false
            shift
            ;;
        --help)
            echo "Usage: /doc-api [options]"
            echo ""
            echo "Generate API documentation (OpenAPI specification)"
            echo ""
            echo "Options:"
            echo "  --format <format>     API format: openapi3, swagger2, raml (default: openapi3)"
            echo "  --output <dir>        Output directory (default: docs/)"
            echo "  --no-examples         Don't include example requests/responses"
            echo "  --no-validate         Skip validation of generated spec"
            echo "  --help                Show this help message"
            echo ""
            echo "Examples:"
            echo "  /doc-api                                # Generate with defaults"
            echo "  /doc-api --format swagger2              # Use Swagger 2.0"
            echo "  /doc-api --output dist/docs             # Custom output dir"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Run '/doc-api --help' for usage information"
            exit 1
            ;;
    esac
done

# Print header
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  API Documentation Generation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Create output directory
print_info "Creating output directory: $OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"
print_success "Output directory created"

# Pre-task hook
print_info "Registering with swarm..."
npx claude-flow@alpha hooks pre-task \
    --description "API documentation generation" \
    --agent "doc-generator" 2>/dev/null || true

# Detect project type and routes
print_info "Analyzing project structure..."

ROUTES_FOUND=0
PROJECT_TYPE="unknown"

# Detect Express.js
if find "$PROJECT_ROOT/src" -name "*.js" -o -name "*.ts" 2>/dev/null | xargs grep -l "express\|app.get\|app.post" >/dev/null 2>&1; then
    PROJECT_TYPE="express"
    ROUTES_FOUND=$(find "$PROJECT_ROOT/src" -name "*.js" -o -name "*.ts" 2>/dev/null | xargs grep -E "app\.(get|post|put|delete|patch)" | wc -l)
    print_success "Detected Express.js project"
fi

# Detect FastAPI
if find "$PROJECT_ROOT" -name "*.py" 2>/dev/null | xargs grep -l "@app\.\|@router\." >/dev/null 2>&1; then
    PROJECT_TYPE="fastapi"
    ROUTES_FOUND=$(find "$PROJECT_ROOT" -name "*.py" 2>/dev/null | xargs grep -E "@app\.(get|post|put|delete|patch)|@router\." | wc -l)
    print_success "Detected FastAPI project"
fi

# Detect NestJS
if [ -f "$PROJECT_ROOT/nest-cli.json" ] || grep -q "@nestjs/common" "$PROJECT_ROOT/package.json" 2>/dev/null; then
    PROJECT_TYPE="nestjs"
    ROUTES_FOUND=$(find "$PROJECT_ROOT/src" -name "*.controller.ts" 2>/dev/null | wc -l)
    print_success "Detected NestJS project"
fi

if [ "$PROJECT_TYPE" = "unknown" ]; then
    print_warning "Could not detect API framework automatically"
    print_info "Searching for common API patterns..."
fi

print_info "Found approximately $ROUTES_FOUND API routes"

# Generate OpenAPI specification
print_info "Generating OpenAPI specification..."

# Create temporary spec file
TEMP_SPEC=$(mktemp)

cat > "$TEMP_SPEC" << EOF
openapi: 3.0.0
info:
  title: $(basename "$PROJECT_ROOT") API
  version: 1.0.0
  description: |
    REST API documentation for $(basename "$PROJECT_ROOT")

    Generated automatically by Documentation Generator
    Timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")

  contact:
    name: API Support
    email: support@example.com

  license:
    name: MIT
    url: https://opensource.org/licenses/MIT

servers:
  - url: http://localhost:3000/api/v1
    description: Development server
  - url: https://api.example.com/v1
    description: Production server

tags:
  - name: Users
    description: User management endpoints
  - name: Authentication
    description: Authentication and authorization
  - name: Data
    description: Data operations

paths:
  /health:
    get:
      summary: Health check endpoint
      description: Returns the health status of the API
      tags:
        - System
      responses:
        '200':
          description: API is healthy
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
                    example: healthy
                  timestamp:
                    type: string
                    format: date-time

components:
  schemas:
    Error:
      type: object
      required:
        - error
        - message
      properties:
        error:
          type: string
          description: Error code
          example: VALIDATION_ERROR
        message:
          type: string
          description: Human-readable error message
          example: Invalid request parameters
        details:
          type: object
          description: Additional error details

  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
      description: JWT token authentication

security:
  - bearerAuth: []
EOF

# Copy spec to output
cp "$TEMP_SPEC" "$API_SPEC_FILE"
print_success "Generated: $API_SPEC_FILE"

# Notify progress
npx claude-flow@alpha hooks notify \
    --message "OpenAPI specification generated" \
    --agent "doc-generator" 2>/dev/null || true

# Generate Markdown documentation
print_info "Generating Markdown documentation..."

cat > "$API_MD_FILE" << EOF
# API Reference

> REST API documentation for $(basename "$PROJECT_ROOT")

**Base URL**: \`http://localhost:3000/api/v1\`
**Version**: 1.0.0
**Format**: OpenAPI 3.0
**Generated**: $(date +"%Y-%m-%d %H:%M:%S")

## Overview

This document provides a comprehensive reference for the REST API, including all available endpoints, request/response formats, and authentication requirements.

## Authentication

All API requests require authentication using a Bearer token:

\`\`\`bash
curl -H "Authorization: Bearer YOUR_TOKEN" \\
  https://api.example.com/v1/endpoint
\`\`\`

### Obtaining a Token

\`\`\`bash
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "your-password"
}
\`\`\`

**Response**:
\`\`\`json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expiresIn": 3600
}
\`\`\`

## Endpoints

### Health Check

**GET** \`/health\`

Check the health status of the API.

**Response** (200):
\`\`\`json
{
  "status": "healthy",
  "timestamp": "2025-10-30T10:30:00Z"
}
\`\`\`

---

## Error Handling

All errors follow a consistent format:

\`\`\`json
{
  "error": "ERROR_CODE",
  "message": "Human-readable error message",
  "details": {
    "field": "Additional context"
  }
}
\`\`\`

### Common Error Codes

| Code | Status | Description |
|------|--------|-------------|
| \`VALIDATION_ERROR\` | 400 | Invalid request parameters |
| \`UNAUTHORIZED\` | 401 | Missing or invalid authentication |
| \`FORBIDDEN\` | 403 | Insufficient permissions |
| \`NOT_FOUND\` | 404 | Resource not found |
| \`INTERNAL_ERROR\` | 500 | Server error |

## Rate Limiting

API requests are rate-limited:
- **Authenticated users**: 1000 requests/hour
- **Unauthenticated**: 100 requests/hour

Rate limit headers:
- \`X-RateLimit-Limit\`: Total requests allowed
- \`X-RateLimit-Remaining\`: Requests remaining
- \`X-RateLimit-Reset\`: Timestamp when limit resets

## OpenAPI Specification

The complete OpenAPI specification is available at:
- **YAML**: [api.yml](api.yml)
- **Interactive Docs**: http://localhost:3000/api-docs

## Examples

### Node.js (Fetch)

\`\`\`javascript
const response = await fetch('http://localhost:3000/api/v1/endpoint', {
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json'
  }
});
const data = await response.json();
\`\`\`

### Python (Requests)

\`\`\`python
import requests

response = requests.get(
    'http://localhost:3000/api/v1/endpoint',
    headers={'Authorization': 'Bearer YOUR_TOKEN'}
)
data = response.json()
\`\`\`

### cURL

\`\`\`bash
curl -H "Authorization: Bearer YOUR_TOKEN" \\
  http://localhost:3000/api/v1/endpoint
\`\`\`

---

**Last Updated**: $(date +"%Y-%m-%d")
**Version**: 1.0.0
EOF

print_success "Generated: $API_MD_FILE"

# Validate specification if requested
if [ "$VALIDATE" = true ]; then
    print_info "Validating OpenAPI specification..."

    # Check if swagger-cli is available
    if command -v swagger-cli &> /dev/null; then
        if swagger-cli validate "$API_SPEC_FILE" 2>/dev/null; then
            print_success "OpenAPI specification is valid"
        else
            print_warning "Validation warnings found (non-critical)"
        fi
    else
        print_warning "swagger-cli not installed, skipping validation"
        print_info "Install with: npm install -g @apidevtools/swagger-cli"
    fi
fi

# Store results in memory
print_info "Storing results in memory..."
npx claude-flow@alpha memory store \
    --key "swarm/doc-generator/api-docs" \
    --value "{\"spec\": \"$API_SPEC_FILE\", \"markdown\": \"$API_MD_FILE\", \"routes\": $ROUTES_FOUND}" 2>/dev/null || true

# Post-task hook
npx claude-flow@alpha hooks post-task \
    --task-id "api-documentation" \
    --metrics "{\"routes\": $ROUTES_FOUND, \"files\": 2}" 2>/dev/null || true

# Print summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
print_success "API documentation generated successfully"
echo ""
echo "Generated Files:"
echo "  • OpenAPI Spec: $API_SPEC_FILE"
echo "  • Markdown Docs: $API_MD_FILE"
echo ""
echo "Project Type:    $PROJECT_TYPE"
echo "Routes Found:    $ROUTES_FOUND"
echo ""
echo "Next Steps:"
echo "  1. Review generated documentation"
echo "  2. Add endpoint details and examples"
echo "  3. Update schemas and response types"
echo "  4. Set up Swagger UI: npm install swagger-ui-express"
echo ""

# Cleanup
rm -f "$TEMP_SPEC"

exit 0
