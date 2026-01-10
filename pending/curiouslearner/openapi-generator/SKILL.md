---
name: openapi-generator
description: Generate comprehensive OpenAPI/Swagger specifications from existing code and APIs.
---

# OpenAPI Generator Skill

Generate comprehensive OpenAPI/Swagger specifications from existing code and APIs.

## Instructions

You are an OpenAPI/Swagger specification expert. When invoked:

1. **Generate OpenAPI Specs**:
   - Analyze existing API code
   - Extract endpoints, methods, and parameters
   - Document request/response schemas
   - Generate OpenAPI 3.0+ compliant specs
   - Include authentication schemes

2. **Enhance Specifications**:
   - Add detailed descriptions
   - Include example values
   - Document error responses
   - Add validation rules
   - Include deprecation warnings

3. **Generate Documentation**:
   - Create interactive API docs
   - Generate client SDKs
   - Create API reference guides
   - Export to various formats

4. **Validate Specifications**:
   - Check OpenAPI compliance
   - Validate schema definitions
   - Ensure consistency
   - Verify examples

## Usage Examples

```
@openapi-generator
@openapi-generator --from-code
@openapi-generator --validate
@openapi-generator --generate-docs
@openapi-generator --format yaml
```

## OpenAPI 3.0 Specification

### Basic Structure
```yaml
openapi: 3.0.3
info:
  title: User Management API
  description: API for managing users and authentication
  version: 1.0.0
  contact:
    name: API Support
    email: support@example.com
    url: https://example.com/support
  license:
    name: Apache 2.0
    url: https://www.apache.org/licenses/LICENSE-2.0.html

servers:
  - url: https://api.example.com/v1
    description: Production server
  - url: https://staging-api.example.com/v1
    description: Staging server
  - url: http://localhost:3000/v1
    description: Development server

tags:
  - name: Users
    description: User management operations
  - name: Authentication
    description: Authentication and authorization

paths:
  /users:
    get:
      summary: Get all users
      description: Retrieve a paginated list of users
      operationId: getUsers
      tags:
        - Users
      parameters:
        - name: page
          in: query
          description: Page number
          required: false
          schema:
            type: integer
            minimum: 1
            default: 1
        - name: limit
          in: query
          description: Number of items per page
          required: false
          schema:
            type: integer
            minimum: 1
            maximum: 100
            default: 10
        - name: sort
          in: query
          description: Sort field and direction
          required: false
          schema:
            type: string
            enum: [created_at, name, email]
            default: created_at
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
                      $ref: '#/components/schemas/User'
                  meta:
                    $ref: '#/components/schemas/PaginationMeta'
              examples:
                success:
                  value:
                    data:
                      - id: "123"
                        name: "John Doe"
                        email: "john@example.com"
                        role: "user"
                        createdAt: "2024-01-15T10:30:00Z"
                    meta:
                      page: 1
                      limit: 10
                      total: 42
                      totalPages: 5
        '401':
          $ref: '#/components/responses/UnauthorizedError'
        '500':
          $ref: '#/components/responses/InternalServerError'
      security:
        - bearerAuth: []

    post:
      summary: Create new user
      description: Create a new user account
      operationId: createUser
      tags:
        - Users
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateUserRequest'
            examples:
              user:
                value:
                  name: "John Doe"
                  email: "john@example.com"
                  password: "SecurePass123!"
                  role: "user"
      responses:
        '201':
          description: User created successfully
          headers:
            Location:
              schema:
                type: string
              description: URL of the created user
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
              examples:
                created:
                  value:
                    id: "123"
                    name: "John Doe"
                    email: "john@example.com"
                    role: "user"
                    createdAt: "2024-01-15T10:30:00Z"
        '400':
          $ref: '#/components/responses/BadRequestError'
        '409':
          description: User already exists
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
              examples:
                duplicate:
                  value:
                    code: "DUPLICATE_EMAIL"
                    message: "User with this email already exists"
        '401':
          $ref: '#/components/responses/UnauthorizedError'
      security:
        - bearerAuth: []

  /users/{userId}:
    get:
      summary: Get user by ID
      description: Retrieve a specific user by their ID
      operationId: getUserById
      tags:
        - Users
      parameters:
        - name: userId
          in: path
          required: true
          description: User ID
          schema:
            type: string
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '404':
          $ref: '#/components/responses/NotFoundError'
        '401':
          $ref: '#/components/responses/UnauthorizedError'
      security:
        - bearerAuth: []

    put:
      summary: Update user
      description: Update an existing user (full update)
      operationId: updateUser
      tags:
        - Users
      parameters:
        - name: userId
          in: path
          required: true
          schema:
            type: string
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UpdateUserRequest'
      responses:
        '200':
          description: User updated successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '400':
          $ref: '#/components/responses/BadRequestError'
        '404':
          $ref: '#/components/responses/NotFoundError'
      security:
        - bearerAuth: []

    patch:
      summary: Partially update user
      description: Update specific fields of a user
      operationId: patchUser
      tags:
        - Users
      parameters:
        - name: userId
          in: path
          required: true
          schema:
            type: string
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/PatchUserRequest'
      responses:
        '200':
          description: User updated successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '400':
          $ref: '#/components/responses/BadRequestError'
        '404':
          $ref: '#/components/responses/NotFoundError'
      security:
        - bearerAuth: []

    delete:
      summary: Delete user
      description: Delete a user account
      operationId: deleteUser
      tags:
        - Users
      parameters:
        - name: userId
          in: path
          required: true
          schema:
            type: string
      responses:
        '204':
          description: User deleted successfully
        '404':
          $ref: '#/components/responses/NotFoundError'
        '401':
          $ref: '#/components/responses/UnauthorizedError'
      security:
        - bearerAuth: []

  /auth/login:
    post:
      summary: Login
      description: Authenticate user and receive access token
      operationId: login
      tags:
        - Authentication
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - email
                - password
              properties:
                email:
                  type: string
                  format: email
                password:
                  type: string
                  format: password
            examples:
              credentials:
                value:
                  email: "user@example.com"
                  password: "password123"
      responses:
        '200':
          description: Login successful
          content:
            application/json:
              schema:
                type: object
                properties:
                  accessToken:
                    type: string
                  refreshToken:
                    type: string
                  expiresIn:
                    type: integer
                  tokenType:
                    type: string
              examples:
                success:
                  value:
                    accessToken: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
                    refreshToken: "refresh-token-here"
                    expiresIn: 3600
                    tokenType: "Bearer"
        '401':
          description: Invalid credentials
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

  /auth/refresh:
    post:
      summary: Refresh token
      description: Get new access token using refresh token
      operationId: refreshToken
      tags:
        - Authentication
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - refreshToken
              properties:
                refreshToken:
                  type: string
      responses:
        '200':
          description: Token refreshed
          content:
            application/json:
              schema:
                type: object
                properties:
                  accessToken:
                    type: string
                  expiresIn:
                    type: integer

components:
  schemas:
    User:
      type: object
      required:
        - id
        - name
        - email
        - role
      properties:
        id:
          type: string
          description: Unique user identifier
          example: "123"
        name:
          type: string
          description: User's full name
          minLength: 2
          maxLength: 100
          example: "John Doe"
        email:
          type: string
          format: email
          description: User's email address
          example: "john@example.com"
        role:
          type: string
          enum: [user, admin, moderator]
          description: User role
          example: "user"
        createdAt:
          type: string
          format: date-time
          description: Account creation timestamp
          example: "2024-01-15T10:30:00Z"
        updatedAt:
          type: string
          format: date-time
          description: Last update timestamp
          example: "2024-01-15T10:30:00Z"

    CreateUserRequest:
      type: object
      required:
        - name
        - email
        - password
      properties:
        name:
          type: string
          minLength: 2
          maxLength: 100
        email:
          type: string
          format: email
        password:
          type: string
          format: password
          minLength: 8
        role:
          type: string
          enum: [user, admin, moderator]
          default: user

    UpdateUserRequest:
      type: object
      required:
        - name
        - email
      properties:
        name:
          type: string
          minLength: 2
          maxLength: 100
        email:
          type: string
          format: email
        role:
          type: string
          enum: [user, admin, moderator]

    PatchUserRequest:
      type: object
      properties:
        name:
          type: string
          minLength: 2
          maxLength: 100
        email:
          type: string
          format: email
        role:
          type: string
          enum: [user, admin, moderator]
      minProperties: 1

    PaginationMeta:
      type: object
      properties:
        page:
          type: integer
          minimum: 1
        limit:
          type: integer
          minimum: 1
        total:
          type: integer
          minimum: 0
        totalPages:
          type: integer
          minimum: 0

    Error:
      type: object
      required:
        - code
        - message
      properties:
        code:
          type: string
          description: Error code
        message:
          type: string
          description: Error message
        details:
          type: object
          description: Additional error details

  responses:
    UnauthorizedError:
      description: Authentication required
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          examples:
            unauthorized:
              value:
                code: "UNAUTHORIZED"
                message: "Authentication required"

    BadRequestError:
      description: Invalid request
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          examples:
            validation:
              value:
                code: "VALIDATION_ERROR"
                message: "Invalid request data"
                details:
                  email: "Invalid email format"

    NotFoundError:
      description: Resource not found
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          examples:
            notFound:
              value:
                code: "NOT_FOUND"
                message: "Resource not found"

    InternalServerError:
      description: Internal server error
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          examples:
            error:
              value:
                code: "INTERNAL_ERROR"
                message: "An unexpected error occurred"

  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
      description: JWT authentication token

    apiKey:
      type: apiKey
      in: header
      name: X-API-Key
      description: API key for authentication

    oauth2:
      type: oauth2
      flows:
        authorizationCode:
          authorizationUrl: https://oauth.example.com/authorize
          tokenUrl: https://oauth.example.com/token
          scopes:
            read:users: Read user information
            write:users: Modify user information
            admin: Administrative access

security:
  - bearerAuth: []
```

## Generating from Code

### Express.js (Node.js)
```javascript
// Using swagger-jsdoc
const swaggerJsdoc = require('swagger-jsdoc');

const options = {
  definition: {
    openapi: '3.0.0',
    info: {
      title: 'User API',
      version: '1.0.0',
    },
  },
  apis: ['./routes/*.js'],
};

const openapiSpecification = swaggerJsdoc(options);

// routes/users.js
/**
 * @openapi
 * /api/users:
 *   get:
 *     summary: Get all users
 *     tags: [Users]
 *     parameters:
 *       - in: query
 *         name: page
 *         schema:
 *           type: integer
 *         description: Page number
 *     responses:
 *       200:
 *         description: Success
 *         content:
 *           application/json:
 *             schema:
 *               type: array
 *               items:
 *                 $ref: '#/components/schemas/User'
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
 *         name:
 *           type: string
 *         email:
 *           type: string
 *           format: email
 */
```

### FastAPI (Python)
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List, Optional

app = FastAPI(
    title="User API",
    description="API for managing users",
    version="1.0.0"
)

class User(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: str = "user"

    class Config:
        schema_extra = {
            "example": {
                "id": "123",
                "name": "John Doe",
                "email": "john@example.com",
                "role": "user"
            }
        }

class CreateUserRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: Optional[str] = "user"

@app.get(
    "/api/users",
    response_model=List[User],
    summary="Get all users",
    description="Retrieve a paginated list of users",
    tags=["Users"]
)
async def get_users(
    page: int = 1,
    limit: int = 10
):
    """
    Get all users with pagination.

    - **page**: Page number (default: 1)
    - **limit**: Items per page (default: 10)
    """
    # Implementation
    return []

@app.post(
    "/api/users",
    response_model=User,
    status_code=201,
    summary="Create new user",
    tags=["Users"]
)
async def create_user(user: CreateUserRequest):
    """
    Create a new user account.

    - **name**: User's full name
    - **email**: User's email address
    - **password**: Account password (min 8 characters)
    - **role**: User role (default: user)
    """
    # Implementation
    return {}

# Auto-generated OpenAPI spec at /docs and /redoc
```

### Go (using go-swagger)
```go
// Package api User API
//
// API for managing users
//
//     Schemes: https
//     Host: api.example.com
//     BasePath: /v1
//     Version: 1.0.0
//
//     Consumes:
//     - application/json
//
//     Produces:
//     - application/json
//
//     Security:
//     - bearer:
//
//     SecurityDefinitions:
//     bearer:
//       type: apiKey
//       name: Authorization
//       in: header
//
// swagger:meta
package api

// User represents a user account
// swagger:model User
type User struct {
    // User ID
    // required: true
    // example: 123
    ID string `json:"id"`

    // User's name
    // required: true
    // min length: 2
    // max length: 100
    Name string `json:"name"`

    // User's email
    // required: true
    // format: email
    Email string `json:"email"`

    // User role
    // required: true
    // enum: user,admin,moderator
    Role string `json:"role"`
}

// swagger:route GET /api/users users getUsers
//
// Get all users
//
// Retrieve a paginated list of users
//
//     Produces:
//     - application/json
//
//     Parameters:
//       + name: page
//         in: query
//         type: integer
//         description: Page number
//       + name: limit
//         in: query
//         type: integer
//         description: Items per page
//
//     Responses:
//       200: UsersResponse
//       401: UnauthorizedError
//       500: InternalServerError
```

## Tools and Commands

### Swagger UI
```javascript
// Serve interactive docs with Express
const swaggerUi = require('swagger-ui-express');
const swaggerDocument = require('./openapi.json');

app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerDocument));
```

### OpenAPI Generator CLI
```bash
# Install
npm install -g @openapitools/openapi-generator-cli

# Generate client SDK (TypeScript)
openapi-generator-cli generate \
  -i openapi.yaml \
  -g typescript-axios \
  -o ./generated/client

# Generate server stub (Node.js)
openapi-generator-cli generate \
  -i openapi.yaml \
  -g nodejs-express-server \
  -o ./generated/server

# Generate documentation
openapi-generator-cli generate \
  -i openapi.yaml \
  -g html2 \
  -o ./docs
```

### Validation
```bash
# Using Spectral
npm install -g @stoplight/spectral-cli

# Validate OpenAPI spec
spectral lint openapi.yaml

# With custom rules
spectral lint openapi.yaml --ruleset .spectral.yaml
```

### Convert YAML to JSON
```bash
# Using yq
yq eval -o=json openapi.yaml > openapi.json

# Using js-yaml
npx js-yaml openapi.yaml > openapi.json
```

## GraphQL to OpenAPI

### Converting GraphQL Schema
```javascript
const { printSchema } = require('graphql');
const { createSchema } = require('graphql-yoga');

// GraphQL schema
const schema = createSchema({
  typeDefs: `
    type User {
      id: ID!
      name: String!
      email: String!
    }

    type Query {
      users: [User!]!
      user(id: ID!): User
    }

    type Mutation {
      createUser(name: String!, email: String!): User!
    }
  `
});

// Convert to OpenAPI
// Manual mapping or use tools like graphql-to-rest
```

## Best Practices

### Documentation Quality
- Write clear, concise descriptions
- Include meaningful examples
- Document all error responses
- Specify validation rules
- Add deprecation warnings when needed

### Schema Design
- Use consistent naming conventions
- Reuse components with $ref
- Define common response types
- Use appropriate data types and formats
- Include validation constraints

### Examples
- Provide realistic example values
- Include edge cases
- Show error response examples
- Demonstrate authentication
- Cover all major use cases

### Versioning
- Version your API in the URL (/v1, /v2)
- Document breaking changes
- Maintain backwards compatibility
- Provide migration guides
- Support multiple versions

### Security
- Document authentication methods
- Specify required scopes/permissions
- Include security examples
- Document rate limits
- Mention HTTPS requirement

## Auto-Generation Tools

### Swagger Editor
- Online: https://editor.swagger.io
- Desktop: https://github.com/swagger-api/swagger-editor

### Stoplight Studio
- Visual OpenAPI editor
- Auto-generate from examples
- Built-in validation

### Postman
- Generate OpenAPI from collections
- Import/export OpenAPI specs
- Auto-sync with API

### ReadMe
- API documentation platform
- Import OpenAPI specs
- Interactive API explorer

## Notes

- Keep specifications up-to-date with code changes
- Automate spec generation in CI/CD
- Use linting tools to enforce standards
- Version control your OpenAPI specs
- Generate client SDKs automatically
- Test generated code thoroughly
- Include OpenAPI spec in API responses (/openapi.json)
- Use tags to organize endpoints
- Provide comprehensive examples
- Document rate limits and quotas
