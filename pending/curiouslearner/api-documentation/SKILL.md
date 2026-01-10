---
name: api-documentation
description: Auto-generate comprehensive API documentation with examples, schemas, and interactive tools.
---

# API Documentation Skill

Auto-generate comprehensive API documentation with examples, schemas, and interactive tools.

## Instructions

You are an API documentation expert. When invoked:

1. **Generate Documentation**:
   - Create API reference documentation
   - Extract info from code comments
   - Generate from OpenAPI/Swagger specs
   - Include usage examples
   - Document authentication methods

2. **Interactive Documentation**:
   - Set up Swagger UI
   - Configure Redoc
   - Create interactive playgrounds
   - Add try-it-out features
   - Include code samples

3. **Documentation Types**:
   - API reference guides
   - Getting started tutorials
   - Authentication guides
   - Error handling documentation
   - Rate limiting policies

4. **Multi-Format Export**:
   - HTML documentation
   - Markdown files
   - PDF exports
   - Postman collections
   - SDK generation

## Usage Examples

```
@api-documentation
@api-documentation --from-openapi
@api-documentation --interactive
@api-documentation --export-postman
@api-documentation --generate-sdk
```

## Documentation Tools

### Swagger UI

#### Setup with Express
```javascript
const express = require('express');
const swaggerUi = require('swagger-ui-express');
const YAML = require('yamljs');

const app = express();

// Load OpenAPI spec
const swaggerDocument = YAML.load('./openapi.yaml');

// Serve Swagger UI
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerDocument, {
  customCss: '.swagger-ui .topbar { display: none }',
  customSiteTitle: 'My API Documentation',
  customfavIcon: '/favicon.ico'
}));

// Serve OpenAPI spec as JSON
app.get('/openapi.json', (req, res) => {
  res.json(swaggerDocument);
});

app.listen(3000, () => {
  console.log('API docs available at http://localhost:3000/api-docs');
});
```

#### Custom Swagger Options
```javascript
const options = {
  explorer: true,
  swaggerOptions: {
    persistAuthorization: true,
    displayRequestDuration: true,
    filter: true,
    syntaxHighlight: {
      activate: true,
      theme: 'monokai'
    }
  },
  customCss: `
    .swagger-ui .topbar { background-color: #2c3e50; }
    .swagger-ui .info .title { color: #2c3e50; }
  `,
  customSiteTitle: 'My API - Documentation',
  customfavIcon: '/assets/favicon.ico'
};

app.use('/docs', swaggerUi.serve, swaggerUi.setup(swaggerDocument, options));
```

### Redoc

#### Setup
```javascript
const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');

const app = express();

// Serve OpenAPI spec
app.get('/openapi.yaml', (req, res) => {
  res.sendFile(__dirname + '/openapi.yaml');
});

// Serve Redoc
app.get('/docs', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html>
      <head>
        <title>API Documentation</title>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
        <style>
          body { margin: 0; padding: 0; }
        </style>
      </head>
      <body>
        <redoc spec-url='/openapi.yaml'></redoc>
        <script src="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"></script>
      </body>
    </html>
  `);
});

app.listen(3000);
```

#### Redoc CLI
```bash
# Install
npm install -g redoc-cli

# Generate static HTML
redoc-cli bundle openapi.yaml -o docs/index.html

# Serve with live reload
redoc-cli serve openapi.yaml --watch

# Custom options
redoc-cli bundle openapi.yaml \
  --output docs/index.html \
  --title "My API Documentation" \
  --options.theme.colors.primary.main="#2c3e50"
```

### Stoplight Elements

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no" />
    <title>API Documentation</title>
    <script src="https://unpkg.com/@stoplight/elements/web-components.min.js"></script>
    <link rel="stylesheet" href="https://unpkg.com/@stoplight/elements/styles.min.css" />
  </head>
  <body>
    <elements-api
      apiDescriptionUrl="/openapi.yaml"
      router="hash"
      layout="sidebar"
    />
  </body>
</html>
```

## Documentation from Code

### JSDoc to OpenAPI

```javascript
/**
 * @openapi
 * /api/users:
 *   get:
 *     summary: Get all users
 *     description: Retrieve a paginated list of all users
 *     tags:
 *       - Users
 *     parameters:
 *       - in: query
 *         name: page
 *         schema:
 *           type: integer
 *           minimum: 1
 *           default: 1
 *         description: Page number
 *       - in: query
 *         name: limit
 *         schema:
 *           type: integer
 *           minimum: 1
 *           maximum: 100
 *           default: 10
 *         description: Number of items per page
 *     responses:
 *       200:
 *         description: Successful response
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 data:
 *                   type: array
 *                   items:
 *                     $ref: '#/components/schemas/User'
 *                 meta:
 *                   $ref: '#/components/schemas/PaginationMeta'
 *       401:
 *         $ref: '#/components/responses/UnauthorizedError'
 *     security:
 *       - bearerAuth: []
 */
router.get('/users', async (req, res) => {
  // Implementation
});

/**
 * @openapi
 * components:
 *   schemas:
 *     User:
 *       type: object
 *       required:
 *         - id
 *         - name
 *         - email
 *       properties:
 *         id:
 *           type: string
 *           description: User ID
 *           example: "123"
 *         name:
 *           type: string
 *           description: User's full name
 *           example: "John Doe"
 *         email:
 *           type: string
 *           format: email
 *           description: User's email address
 *           example: "john@example.com"
 */
```

### TypeDoc (TypeScript)

```typescript
/**
 * User management API
 * @module UserAPI
 */

/**
 * Represents a user in the system
 * @interface User
 */
interface User {
  /** Unique user identifier */
  id: string;
  /** User's full name */
  name: string;
  /** User's email address */
  email: string;
  /** User role */
  role: 'user' | 'admin';
}

/**
 * Get all users
 * @route GET /api/users
 * @param {number} page - Page number (default: 1)
 * @param {number} limit - Items per page (default: 10)
 * @returns {Promise<User[]>} List of users
 * @throws {UnauthorizedError} If not authenticated
 */
export async function getUsers(
  page: number = 1,
  limit: number = 10
): Promise<User[]> {
  // Implementation
}

/**
 * Create a new user
 * @route POST /api/users
 * @param {CreateUserRequest} data - User data
 * @returns {Promise<User>} Created user
 * @throws {ValidationError} If data is invalid
 * @throws {ConflictError} If email already exists
 */
export async function createUser(data: CreateUserRequest): Promise<User> {
  // Implementation
}
```

### Python Docstrings (FastAPI)

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(
    title="User Management API",
    description="API for managing users and authentication",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

class User(BaseModel):
    """
    User model representing a user account.

    Attributes:
        id: Unique user identifier
        name: User's full name
        email: User's email address
        role: User role (user or admin)
    """
    id: str
    name: str
    email: str
    role: str = "user"

@app.get("/api/users", response_model=List[User], tags=["Users"])
async def get_users(
    page: int = 1,
    limit: int = 10
) -> List[User]:
    """
    Get all users with pagination.

    Args:
        page: Page number (default: 1)
        limit: Number of items per page (default: 10)

    Returns:
        List of users

    Raises:
        HTTPException: If unauthorized (401)
    """
    # Implementation
    return []

@app.post("/api/users", response_model=User, status_code=201, tags=["Users"])
async def create_user(user: User) -> User:
    """
    Create a new user account.

    Args:
        user: User data including name, email, and optional role

    Returns:
        Created user object

    Raises:
        HTTPException: If validation fails (400)
        HTTPException: If email already exists (409)
    """
    # Implementation
    return user
```

## Documentation Templates

### Markdown API Reference

```markdown
# API Reference

Base URL: `https://api.example.com/v1`

## Authentication

All API requests require authentication using a Bearer token:

```bash
Authorization: Bearer YOUR_ACCESS_TOKEN
```

Get your access token by calling the `/auth/login` endpoint.

## Endpoints

### Users

#### Get All Users

```http
GET /api/users
```

Retrieve a paginated list of users.

**Parameters**

| Name  | Type    | In    | Required | Description              |
|-------|---------|-------|----------|--------------------------|
| page  | integer | query | No       | Page number (default: 1) |
| limit | integer | query | No       | Items per page (max: 100)|

**Response**

```json
{
  "data": [
    {
      "id": "123",
      "name": "John Doe",
      "email": "john@example.com",
      "role": "user"
    }
  ],
  "meta": {
    "page": 1,
    "limit": 10,
    "total": 42,
    "totalPages": 5
  }
}
```

**Status Codes**

- `200 OK` - Success
- `401 Unauthorized` - Missing or invalid authentication
- `500 Internal Server Error` - Server error

**Example Request**

```bash
curl -X GET "https://api.example.com/v1/api/users?page=1&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

```javascript
const response = await fetch('https://api.example.com/v1/api/users?page=1&limit=10', {
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN'
  }
});
const data = await response.json();
```

```python
import requests

response = requests.get(
    'https://api.example.com/v1/api/users',
    headers={'Authorization': 'Bearer YOUR_TOKEN'},
    params={'page': 1, 'limit': 10}
)
data = response.json()
```

#### Create User

```http
POST /api/users
```

Create a new user account.

**Request Body**

```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "role": "user"
}
```

**Response**

```json
{
  "id": "123",
  "name": "John Doe",
  "email": "john@example.com",
  "role": "user",
  "createdAt": "2024-01-15T10:30:00Z"
}
```

**Status Codes**

- `201 Created` - User created successfully
- `400 Bad Request` - Invalid request data
- `409 Conflict` - Email already exists
- `401 Unauthorized` - Authentication required

## Error Handling

All errors follow a consistent format:

```json
{
  "code": "ERROR_CODE",
  "message": "Human-readable error message",
  "details": {
    "field": "Additional error details"
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| UNAUTHORIZED | 401 | Authentication required |
| FORBIDDEN | 403 | Insufficient permissions |
| NOT_FOUND | 404 | Resource not found |
| VALIDATION_ERROR | 400 | Invalid input data |
| RATE_LIMIT_EXCEEDED | 429 | Too many requests |

## Rate Limiting

API requests are limited to:
- **100 requests per minute** for authenticated users
- **20 requests per minute** for unauthenticated requests

Rate limit headers are included in all responses:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1610000000
```

## Pagination

All list endpoints support pagination with these parameters:

- `page` - Page number (default: 1)
- `limit` - Items per page (default: 10, max: 100)

Responses include pagination metadata:

```json
{
  "data": [...],
  "meta": {
    "page": 1,
    "limit": 10,
    "total": 100,
    "totalPages": 10
  }
}
```

## Versioning

The API uses URL versioning:

- Current version: `v1`
- Base URL: `https://api.example.com/v1`

Breaking changes will be introduced in new versions (v2, v3, etc.)
```

### Getting Started Guide

```markdown
# Getting Started

This guide will help you make your first API request.

## 1. Get Your API Key

Sign up at [https://example.com/signup](https://example.com/signup) to get your API key.

## 2. Make Your First Request

### Using curl

```bash
curl -X GET https://api.example.com/v1/api/users \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Using JavaScript

```javascript
const response = await fetch('https://api.example.com/v1/api/users', {
  headers: {
    'Authorization': 'Bearer YOUR_API_KEY'
  }
});

const users = await response.json();
console.log(users);
```

### Using Python

```python
import requests

response = requests.get(
    'https://api.example.com/v1/api/users',
    headers={'Authorization': 'Bearer YOUR_API_KEY'}
)

users = response.json()
print(users)
```

## 3. Create a Resource

```bash
curl -X POST https://api.example.com/v1/api/users \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com"
  }'
```

## 4. Handle Errors

Always check the response status:

```javascript
try {
  const response = await fetch('https://api.example.com/v1/api/users', {
    headers: { 'Authorization': 'Bearer YOUR_API_KEY' }
  });

  if (!response.ok) {
    const error = await response.json();
    console.error('Error:', error.message);
    return;
  }

  const data = await response.json();
  console.log(data);
} catch (error) {
  console.error('Network error:', error);
}
```

## Next Steps

- Read the [API Reference](/api-reference)
- Explore [code examples](/examples)
- Check out [best practices](/best-practices)
- Join our [developer community](https://community.example.com)
```

## Documentation Generation Tools

### Docusaurus (Facebook)

```bash
# Create new site
npx create-docusaurus@latest my-docs classic

# Install OpenAPI plugin
npm install docusaurus-plugin-openapi-docs

# Configure
# docusaurus.config.js
module.exports = {
  plugins: [
    [
      'docusaurus-plugin-openapi-docs',
      {
        id: 'api',
        docsPluginId: 'classic',
        config: {
          api: {
            specPath: 'openapi.yaml',
            outputDir: 'docs/api',
            sidebarOptions: {
              groupPathsBy: 'tag'
            }
          }
        }
      }
    ]
  ]
};

# Generate docs
npm run docusaurus gen-api-docs all

# Serve
npm run start
```

### Slate (Beautiful API Docs)

```bash
# Clone template
git clone https://github.com/slatedocs/slate.git my-api-docs
cd my-api-docs

# Install dependencies
bundle install

# Edit source/index.html.md
# Run server
bundle exec middleman server

# Build static site
bundle exec middleman build
```

### ReadMe.io

```bash
# Install CLI
npm install -g rdme

# Upload OpenAPI spec
rdme openapi openapi.yaml --key YOUR_README_API_KEY

# Sync with GitHub
rdme openapi openapi.yaml --github --key YOUR_README_API_KEY
```

### MkDocs (Python)

```bash
# Install
pip install mkdocs mkdocs-material

# Create new project
mkdocs new my-api-docs
cd my-api-docs

# Configure mkdocs.yml
site_name: My API Documentation
theme:
  name: material
  features:
    - navigation.tabs
    - navigation.sections
    - toc.integrate

nav:
  - Home: index.md
  - Getting Started: getting-started.md
  - API Reference: api-reference.md
  - Examples: examples.md

# Serve locally
mkdocs serve

# Build
mkdocs build
```

## Code Examples Generator

### Automatic Code Generation

```javascript
// From OpenAPI spec
const CodeGen = require('openapi-client-axios-typegen');

async function generateSDK() {
  const api = await CodeGen.generateClient('openapi.yaml');

  // Generated TypeScript client
  const users = await api.getUsers({ page: 1, limit: 10 });
  const newUser = await api.createUser({
    name: 'John Doe',
    email: 'john@example.com'
  });
}
```

### Multi-Language Examples

```javascript
// examples-generator.js
const examples = {
  getUsersCurl: `curl -X GET "https://api.example.com/v1/api/users?page=1&limit=10" \\
  -H "Authorization: Bearer YOUR_TOKEN"`,

  getUsersJavaScript: `const response = await fetch('https://api.example.com/v1/api/users?page=1&limit=10', {
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN'
  }
});
const data = await response.json();`,

  getUsersPython: `import requests

response = requests.get(
    'https://api.example.com/v1/api/users',
    headers={'Authorization': 'Bearer YOUR_TOKEN'},
    params={'page': 1, 'limit': 10}
)
data = response.json()`,

  getUsersGo: `client := &http.Client{}
req, _ := http.NewRequest("GET", "https://api.example.com/v1/api/users?page=1&limit=10", nil)
req.Header.Add("Authorization", "Bearer YOUR_TOKEN")
resp, _ := client.Do(req)`,

  getUsersRuby: `require 'net/http'

uri = URI('https://api.example.com/v1/api/users?page=1&limit=10')
req = Net::HTTP::Get.new(uri)
req['Authorization'] = 'Bearer YOUR_TOKEN'
res = Net::HTTP.start(uri.hostname, uri.port, use_ssl: true) { |http| http.request(req) }`
};
```

## Best Practices

### Documentation Content
- Write clear, concise descriptions
- Include code examples in multiple languages
- Provide real-world use cases
- Document all error codes
- Include rate limits and quotas
- Show authentication examples
- Explain pagination
- Document versioning strategy

### Interactive Features
- Add "Try it out" functionality
- Include request/response examples
- Show syntax highlighting
- Provide copy-to-clipboard buttons
- Add search functionality
- Include navigation menu

### Maintenance
- Keep docs synchronized with code
- Automate documentation generation
- Version documentation with API
- Review and update regularly
- Test all code examples
- Collect user feedback

### SEO and Discovery
- Use descriptive titles
- Add meta descriptions
- Create sitemap
- Use proper heading structure
- Include keywords
- Make docs publicly accessible

## Notes

- Auto-generate docs from OpenAPI specs when possible
- Include interactive API explorers
- Provide examples in multiple programming languages
- Keep documentation up-to-date with code changes
- Use version control for documentation
- Make documentation searchable
- Include getting started guides
- Document authentication thoroughly
- Show error handling examples
- Test all code examples before publishing
- Collect and incorporate user feedback
- Use consistent formatting and style
