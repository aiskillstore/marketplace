---
name: Next.js Better Auth Integration
category: Authentication
author: Claude
version: 1.0.0
tags: [nextjs, better-auth, authentication, app-router, sessions]
description: A conceptual skill for integrating Better Auth with Next.js App Router
---

# Next.js Better Auth Integration Skill

## When to Use This Skill

Use this conceptual skill when you need to implement authentication in a Next.js application using the App Router architecture with Better Auth. This skill is appropriate for:

- Adding user authentication to Next.js applications
- Implementing secure session management with Better Auth
- Enabling JWT-based authentication flows
- Creating protected routes and pages in Next.js
- Managing user sessions across the application
- Implementing social login capabilities

This skill should NOT be used for:
- Applications using the Pages Router (use _app.js instead)
- Applications that don't require user authentication
- Simple static sites without user interaction
- Applications with custom authentication requirements that conflict with Better Auth

## Prerequisites

- Next.js 13+ with App Router enabled
- Better Auth package installed and configured
- Understanding of Next.js middleware and server components
- Knowledge of authentication concepts and session management
- Environment for managing authentication secrets securely

## Conceptual Implementation Framework

### Better Auth Initialization Capability
- Configure Better Auth with appropriate providers and settings
- Set up authentication database or adapter configuration
- Define user model and authentication options
- Initialize authentication client for frontend usage
- Configure authentication callbacks and customizations

### JWT Token Enablement Capability
- Configure JWT token generation and validation settings
- Set token expiration and refresh mechanisms
- Define token payload structure and claims
- Enable secure token storage and transmission
- Configure token signing and verification algorithms

### App Wrapping for Session Management Capability
- Wrap the Next.js application with Better Auth provider
- Configure session context for client components
- Set up server-side session access in server components
- Establish session persistence across application routes
- Enable session synchronization between client and server

### Hook Usage Capability
- Provide access to authentication state via hooks
- Enable user session data retrieval in components
- Support authentication status checking in real-time
- Allow for custom authentication flows and callbacks
- Enable logout and session management functionality

### Protected Route Implementation Capability
- Create middleware for protecting application routes
- Implement server-side authentication checks
- Enable client-side session verification
- Handle unauthorized access scenarios appropriately
- Redirect users based on authentication status

## Expected Input/Output

### Input Requirements:

1. **Better Auth Configuration**:
   - Database connection settings
   - Authentication providers configuration
   - JWT settings and secrets
   - Customization options for UI and behavior
   - Callback URLs and redirect settings

2. **Next.js App Structure**:
   - App Router directory structure (/app)
   - Middleware configuration (middleware.ts)
   - Layout files that need authentication context
   - Pages requiring authentication protection

### Output Formats:

1. **Initialized Authentication System**:
   - Configured Better Auth instance
   - Ready-to-use authentication context
   - Properly set up session management
   - Working JWT token system

2. **Authenticated Component State**:
   - User session data available in components
   - Authentication status (logged in/out)
   - User profile information when authenticated
   - Session tokens and refresh mechanisms

3. **Protected Route Responses**:
   - HTTP 200 OK for authenticated users
   - HTTP 302/307 redirects for unauthenticated users
   - Proper error handling for authentication failures
   - Consistent session state across the application

4. **Hook Results**:
   - User authentication status
   - Session data when available
   - Loading states during authentication checks
   - Error states for authentication failures

## Integration Patterns

### App Router Integration
- Configure root layout to provide authentication context
- Implement middleware for route protection
- Use server components for server-side session access
- Leverage client components for interactive authentication UI

### Session Management
- Server-side session handling in server components
- Client-side session synchronization in client components
- Cross-component session state consistency
- Proper session cleanup and invalidation

### Authentication Flows
- Sign-in and sign-up process management
- Social authentication provider integration
- Password reset and account recovery
- Multi-factor authentication (if supported)

## Security Considerations

1. **Token Security**: Secure JWT token storage and transmission
2. **Session Management**: Proper session invalidation and refresh
3. **CSRF Protection**: Implement CSRF protection for forms
4. **Secure Cookies**: Use secure, HTTP-only cookies for sessions
5. **Input Validation**: Validate all authentication inputs
6. **Rate Limiting**: Implement rate limiting for authentication endpoints
7. **Secret Management**: Securely store authentication secrets

## Performance Implications

- Optimize session lookup performance in middleware
- Consider caching strategies for session data
- Minimize authentication overhead on each request
- Efficient token validation mechanisms
- Lazy loading of authentication context when possible

## Error Handling and Validation

- Handle authentication initialization failures
- Manage session expiration scenarios
- Provide appropriate feedback for failed authentication
- Validate authentication state consistency
- Handle network failures during authentication checks

## Testing Considerations

- Test authentication flow in server components
- Verify session persistence across requests
- Validate protected route access controls
- Test JWT token generation and validation
- Verify social login provider integration
- Test authentication edge cases and error states