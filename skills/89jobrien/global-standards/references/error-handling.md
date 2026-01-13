---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: reference
parent: global-standards
---

# Error Handling Standards

Comprehensive error handling patterns and best practices.

## Error Handling Patterns

### Try-Catch Blocks

- Wrap code that may throw errors
- Catch specific exception types when possible
- Provide meaningful error messages
- Clean up resources in finally blocks

### Custom Exceptions

- Create domain-specific exception types
- Build exception hierarchies
- Include context in error messages

### Error Propagation

- Catch errors at appropriate boundaries
- Propagate errors when they can't be handled locally
- Transform errors at layer boundaries

## Error Messages

### User-Facing Errors

- Clear, actionable messages
- Avoid technical jargon
- Suggest solutions when possible

### Developer Errors

- Include stack traces
- Provide context and state information
- Use appropriate logging levels

## Logging

- Log errors with appropriate severity
- Include context and stack traces
- Use structured logging when possible
- Don't log sensitive information

## Retry Logic

- Implement exponential backoff
- Retry only transient failures
- Set maximum retry limits
- Log retry attempts

## Circuit Breakers

- Implement for external service calls
- Prevent cascading failures
- Monitor circuit breaker state
- Provide fallback behavior
