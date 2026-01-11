# API Designer Skill

A comprehensive Claude skill for designing, documenting, and implementing RESTful and GraphQL APIs.

## Overview

This skill provides expert guidance on API design patterns, OpenAPI specification generation, authentication strategies, versioning approaches, and industry best practices.

## Contents

### SKILL.md
Main skill file containing:
- REST API design workflow
- GraphQL schema design
- Authentication patterns (OAuth 2.0, JWT, API Keys)
- API versioning strategies
- OpenAPI specification basics
- Best practices and quick reference

### scripts/
**api_helper.py** - Python utility for API development:
- Generate OpenAPI specifications
- Validate existing specs
- Create documentation from specs

Usage:
```bash
# Generate sample OpenAPI spec
python scripts/api_helper.py generate --sample --output openapi.yaml

# Validate existing spec
python scripts/api_helper.py validate --spec openapi.yaml

# Generate documentation
python scripts/api_helper.py docs --spec openapi.yaml --output api-docs.md
```

### examples/
**openapi_spec.yaml** - Complete OpenAPI 3.0 specification example:
- Authentication endpoints
- User management
- Blog posts and comments
- Pagination and filtering
- Error responses

**graphql_schema.graphql** - Full GraphQL schema example:
- Type definitions
- Queries and mutations
- Input types and payloads
- Subscriptions
- Custom directives

### references/
**rest_best_practices.md** - Comprehensive REST API patterns:
- URL design guidelines
- HTTP method usage
- Status code reference
- Authentication patterns
- Pagination strategies
- Rate limiting
- Caching
- CORS
- Documentation standards

## Quick Start

1. Read `SKILL.md` for core API design workflows
2. Reference `examples/openapi_spec.yaml` for OpenAPI structure
3. Review `references/rest_best_practices.md` for detailed patterns
4. Use `scripts/api_helper.py` to generate and validate specs

## Target Complexity

Medium complexity skill (667 lines in SKILL.md)
- Core workflows and patterns in main skill file
- Detailed references and examples in separate files
- Executable utilities for common tasks
