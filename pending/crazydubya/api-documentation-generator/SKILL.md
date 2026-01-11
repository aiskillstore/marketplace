---
name: api-documentation-generator
description: Generates OpenAPI/Swagger documentation from API route files. Use when working with REST APIs, Express routes, FastAPI endpoints, or when user requests API documentation.
allowed-tools: Read, Grep, Glob, Write, Edit
---

# API Documentation Generator

This skill automatically generates OpenAPI 3.0 (Swagger) documentation from API route files in your codebase.

## When to Use This Skill

- User asks to generate API documentation
- Working with REST API endpoints
- Need to create or update OpenAPI/Swagger specs
- Setting up API documentation for Express, FastAPI, Flask, NestJS, or similar frameworks

## Instructions

### 1. Discover API Routes

Search the codebase for API route definitions:

- **Express/Node.js**: Look for `app.get()`, `app.post()`, `router.get()`, etc.
- **FastAPI/Python**: Look for `@app.get()`, `@router.post()`, decorators
- **Flask**: Look for `@app.route()` decorators
- **NestJS**: Look for `@Get()`, `@Post()`, `@Controller()` decorators
- **Rails**: Look for routes in `config/routes.rb`

Use Glob to find route files (e.g., `**/*routes*.{js,ts,py}`, `**/controllers/**/*.{js,ts}`)

### 2. Analyze Route Patterns

For each discovered route, extract:

- **HTTP Method**: GET, POST, PUT, PATCH, DELETE
- **Path**: The endpoint URL (e.g., `/api/users/:id`)
- **Parameters**: Path params, query params, request body
- **Response**: Expected response structure
- **Authentication**: Whether auth is required
- **Description**: Comments or docstrings near the route

### 3. Generate OpenAPI Specification

Create or update an OpenAPI 3.0 specification file (typically `openapi.yaml` or `swagger.json`):

- Start with the template from `templates/openapi-3.0.yaml`
- Map each route to an OpenAPI path object
- Define request/response schemas using JSON Schema
- Include parameter definitions (path, query, body)
- Add authentication schemes if detected (Bearer, API Key, OAuth2)
- Group endpoints by tags (e.g., "Users", "Products", "Auth")

### 4. Validate Completeness

Check that the generated documentation includes:

- All discovered endpoints
- Accurate HTTP methods and paths
- Request/response examples where possible
- Error responses (400, 401, 404, 500, etc.)
- Security requirements

### 5. Output Location

- Save as `openapi.yaml` in the project root, or
- Place in `docs/` or `api/` directory if those exist
- Ask user for preferred location if unclear

## Framework-Specific Notes

### Express/Node.js
- Check for route middleware that might affect auth/validation
- Look for request validators (Joi, express-validator, etc.)
- Extract JSDoc comments for endpoint descriptions

### FastAPI
- FastAPI auto-generates OpenAPI docs, but this skill can enhance them
- Extract Pydantic models for request/response schemas
- Check for `response_model` and `status_code` parameters

### NestJS
- Look for DTOs (Data Transfer Objects) for schemas
- Check for Swagger decorators (`@ApiOperation`, `@ApiResponse`)
- Extract metadata from controller and method decorators

## Best Practices

1. **Use existing schemas**: If the codebase has TypeScript interfaces, Pydantic models, or similar, use them for accurate schemas
2. **Include examples**: Add request/response examples from tests if available
3. **Group logically**: Organize endpoints by resource or feature area using tags
4. **Version appropriately**: Use the API version from the codebase (e.g., "1.0.0")
5. **Add descriptions**: Use code comments/docstrings for endpoint descriptions

## Supporting Files

- `templates/openapi-3.0.yaml`: Base OpenAPI template
- `examples.md`: Framework-specific examples
