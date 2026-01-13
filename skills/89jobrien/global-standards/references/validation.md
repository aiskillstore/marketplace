---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: reference
parent: global-standards
---

# Validation Standards

Input validation patterns and security best practices.

## Validation Principles

### Client and Server

- Always validate on the server side
- Provide immediate feedback on the client
- Never trust client-side validation alone

### Validation Libraries

- Use established libraries (Zod, Yup, Pydantic, Joi)
- Define schemas for consistency
- Reuse validation schemas across layers

## Input Sanitization

### Security

- Prevent XSS attacks
- Prevent SQL injection
- Prevent command injection
- Use allowlists over blocklists

### Data Types

- Validate types, formats, and ranges
- Check required fields
- Validate nested objects and arrays

## Business Rules

- Validate domain-specific rules
- Check sufficient balance, valid dates, permissions
- Implement custom validators when needed

## Error Messages

- Clear, actionable validation errors
- Show errors near the relevant input
- Provide real-time feedback when possible

## File Uploads

- Validate file size limits
- Check allowed file types
- Validate file content when possible
- Scan for malware if applicable
