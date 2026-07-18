---
name: Frontend API Client with JWT
category: API Integration
author: Claude
version: 1.0.0
tags: [nextjs, api-client, jwt, authentication, frontend]
description: A conceptual skill for building an API client in Next.js that handles JWT tokens
---

# Frontend API Client with JWT Skill

## When to Use This Skill

Use this conceptual skill when you need to implement a robust API client in Next.js that properly handles JWT tokens for authentication. This skill is appropriate for:

- Creating centralized API communication layer in Next.js applications
- Managing JWT-based authentication across multiple API endpoints
- Handling token expiration and refresh scenarios
- Standardizing error response parsing and handling
- Implementing secure API communication patterns

This skill should NOT be used for:
- Applications without JWT-based authentication
- Static sites without API communication needs
- Applications using alternative authentication methods (API keys, OAuth 2.0 client credentials, etc.)
- Simple applications with minimal API interaction

## Prerequisites

- Next.js application (either App Router or Pages Router)
- Understanding of JWT (JSON Web Token) concepts
- Knowledge of HTTP headers and authorization mechanisms
- Basic understanding of asynchronous JavaScript operations
- Awareness of client-side vs server-side execution contexts

## Conceptual Implementation Framework

### Authorization Header Attachment Capability
- Automatically attach JWT tokens to API requests as Authorization headers
- Determine when to include tokens based on request type and endpoint
- Handle token attachment for both client-side and server-side requests
- Manage token inclusion in cross-origin requests appropriately
- Ensure proper header formatting ("Bearer <token>")

### Token Expiry Handling Capability
- Detect JWT token expiration before making API requests
- Implement automatic token refresh mechanisms
- Handle token refresh failures gracefully
- Maintain session continuity during token refresh
- Coordinate token refresh across multiple concurrent requests
- Store updated tokens securely after refresh

### Error Response Parsing Capability
- Parse structured error responses from API endpoints
- Identify authentication-related errors (401, 403) for special handling
- Extract meaningful error messages for user feedback
- Handle different error response formats consistently
- Distinguish between client errors, server errors, and network issues
- Provide appropriate user feedback based on error types

### API Call Centralization Capability
- Create a unified interface for all API communications
- Standardize request and response handling across the application
- Implement consistent error handling and logging
- Manage request/response interceptors for cross-cutting concerns
- Provide type-safe API call patterns (when using TypeScript)
- Enable request caching and deduplication where appropriate

## Expected Input/Output

### Input Requirements:

1. **JWT Token Management**:
   - Valid JWT token for authorization
   - Token refresh endpoint configuration
   - Token storage mechanism (localStorage, cookies, etc.)
   - Token expiration time and refresh timing

2. **API Configuration**:
   - Base API URL for requests
   - Request timeout settings
   - Custom headers and request options
   - Endpoint-specific configurations

3. **Request Parameters**:
   - HTTP method (GET, POST, PUT, DELETE, etc.)
   - Request URL or endpoint identifier
   - Request body for POST/PUT operations
   - Query parameters and path variables

### Output Formats:

1. **Successful API Response**:
   - HTTP 200-299 status codes
   - Parsed response data matching expected format
   - Updated token information when applicable
   - Consistent response structure across all endpoints

2. **Authentication Error Response**:
   - HTTP 401 Unauthorized for expired/invalid tokens
   - Automatic token refresh attempt
   - Redirect to login page after refresh failure
   - Clear error messaging for authentication issues

3. **Authorization Error Response**:
   - HTTP 403 Forbidden for insufficient permissions
   - Appropriate error handling based on permission level
   - User feedback for access restriction

4. **General Error Response**:
   - Structured error object with message and code
   - Appropriate HTTP status code
   - Detailed error information for debugging
   - User-friendly error messages for UI display

## Integration Patterns

### Client-Side Integration
- Handle API calls from client components and client-side rendering
- Manage token storage and retrieval in browser context
- Implement request interceptors for header attachment
- Coordinate with authentication state management

### Server-Side Integration (when applicable)
- Handle API calls from server components
- Manage token transmission securely between server and client
- Implement server-side token validation
- Handle server-side error responses appropriately

### React Component Integration
- Provide hooks for API communication in functional components
- Enable context-based API client access
- Support both functional and class component patterns
- Implement proper cleanup and cancellation mechanisms

## Security Considerations

1. **Token Storage**: Secure JWT token storage to prevent XSS attacks
2. **Header Transmission**: Use HTTPS for all API communications
3. **Token Refresh**: Implement secure token refresh mechanisms
4. **Error Information**: Avoid exposing sensitive information in error messages
5. **Request Validation**: Validate request parameters before sending
6. **Response Validation**: Verify response integrity and format
7. **Cross-Site Requests**: Implement proper CORS handling

## Performance Implications

- Optimize token retrieval and attachment for minimal overhead
- Implement efficient token refresh to avoid blocking requests
- Consider request caching strategies for improved performance
- Minimize redundant API calls through proper state management
- Implement request batching where appropriate
- Monitor and optimize network request timing

## Error Handling and Validation

- Validate JWT token format and expiration before requests
- Handle network connectivity issues gracefully
- Implement retry mechanisms for transient failures
- Provide fallback behaviors for critical API failures
- Log errors appropriately for debugging without exposing sensitive information
- Implement circuit breaker patterns for service resilience

## Testing Considerations

- Test token attachment functionality with valid/invalid tokens
- Verify token refresh mechanisms work correctly
- Validate error response parsing across different error types
- Test API client behavior in both client and server contexts
- Verify proper cleanup and cancellation of requests
- Test concurrent request handling and token refresh coordination