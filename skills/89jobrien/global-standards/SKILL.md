---
name: global-standards
description: Project-wide coding standards and conventions specialist. Use PROACTIVELY
  when writing code, making architectural decisions, or establishing project conventions.
  Covers coding style, commenting, error handling, validation, tech stack consistency,
  and project conventions across all languages and frameworks.
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: skill
---

# Project Standards

This skill provides comprehensive guidance on project-wide coding standards, conventions, and best practices that apply across the entire codebase regardless of language or framework.

## When to Use This Skill

Use this skill when:

- **Writing code** - Ensuring consistency with project standards
- **Making architectural decisions** - Following established patterns
- **Onboarding** - Understanding project conventions
- **Code review** - Checking adherence to standards
- **Refactoring** - Maintaining consistency during changes
- **Setting up new features** - Following project conventions

## Core Standards Areas

### 1. Coding Style

**When to apply:**

- Naming variables, functions, classes, modules, or files
- Structuring code for readability and maintainability
- Deciding on function size and single responsibility
- Removing unused code, commented-out blocks, or dead imports
- Extracting reusable logic to avoid duplication
- Applying consistent formatting and indentation
- Refactoring code for clarity and simplicity

**Principles:**

- Clear, descriptive names that reveal intent
- DRY (Don't Repeat Yourself) principle
- Single Responsibility Principle
- Self-documenting code through structure
- Consistent formatting across the codebase

**Applies to:** All code files (*.py,*.js, *.ts,*.jsx, *.tsx,*.vue, *.rb,*.go, *.java,*.rs, *.cpp,*.c, *.swift,*.kt)

### 2. Commenting Standards

**When to apply:**

- Deciding whether code needs a comment
- Documenting complex algorithms or non-obvious business logic
- Writing docstrings or function documentation
- Reviewing existing comments for relevance
- Removing outdated or misleading comments
- Explaining non-obvious code decisions or workarounds

**Principles:**

- Minimal, helpful comments
- Explain why, not what
- Keep code self-documenting through clear naming
- Comments should explain complex logic or business rules
- Avoid comments that restate what code does
- Keep comments evergreen and relevant

**Applies to:** All code files across the entire codebase

### 3. Error Handling

**When to apply:**

- Wrapping code in try-catch or try-except blocks
- Creating custom exception or error classes
- Implementing error boundaries (React, etc.)
- Handling HTTP errors from API calls
- Displaying user-friendly error messages
- Implementing retry logic with exponential backoff
- Cleaning up resources in finally blocks
- Deciding where to catch versus propagate errors
- Logging errors with appropriate severity levels
- Implementing circuit breakers for external services
- Handling validation errors with structured responses

**Principles:**

- User-friendly error messages
- Proper exception types and hierarchies
- Graceful degradation
- Comprehensive logging with context
- Resource cleanup in finally blocks
- Appropriate error propagation
- Retry logic for transient failures

**Applies to:** All code that may throw errors (API handlers, service functions, data processing, file operations, external integrations, network requests, database operations)

### 4. Input Validation

**When to apply:**

- Validating form inputs on the frontend
- Validating API request bodies, query parameters, and headers
- Implementing server-side validation logic
- Creating validation schemas (Zod, Yup, Pydantic, Joi)
- Sanitizing user input to prevent XSS, SQL injection
- Validating data types, formats, ranges, and required fields
- Implementing business rule validation
- Displaying validation error messages
- Writing custom validators for domain-specific rules
- Handling file upload validation

**Principles:**

- Validate on both client and server sides
- Use validation libraries for consistency
- Sanitize input to prevent security vulnerabilities
- Provide clear, actionable error messages
- Validate at system boundaries
- Use allowlists over blocklists

**Applies to:** Form components, API handlers, request validators, input sanitizers, schema definitions, validation middleware, file uploads, webhooks, external API integrations

### 5. Tech Stack Consistency

**When to apply:**

- Choosing libraries or packages for new functionality
- Implementing features using framework-specific patterns
- Setting up new services, integrations, or third-party APIs
- Configuring database connections, ORM settings, or query builders
- Adding authentication, authorization, or security features
- Setting up testing frameworks, tools, or test utilities
- Configuring deployment, CI/CD pipelines, or infrastructure
- Evaluating whether to add a new dependency
- Implementing caching, monitoring, logging, or observability
- Choosing between alternative approaches

**Principles:**

- Consistency with existing technology choices
- Follow framework-specific patterns and idioms
- Prefer existing tools over adding new dependencies
- Document technology decisions
- Maintain architectural consistency

**Applies to:** Frontend, backend, database, infrastructure, testing, deployment, third-party integrations

### 6. Project Conventions

**When to apply:**

- Organizing files and directory structure
- Writing git commit messages or PR descriptions
- Managing environment variables, configuration, and secrets
- Adding or updating project dependencies
- Setting up or modifying CI/CD workflows
- Implementing feature flags
- Updating README files or project documentation
- Establishing code review processes
- Maintaining changelogs or release notes
- Configuring linters, formatters, or pre-commit hooks
- Setting up development environments
- Managing monorepo or multi-package structures

**Principles:**

- Consistent file and directory organization
- Conventional commit messages
- Clear documentation
- Proper dependency management
- Automated quality checks
- Clear development workflows

**Applies to:** Configuration files (.env, package.json, requirements.txt, pyproject.toml, Dockerfile, docker-compose.yml, Makefile), directories (.github/, .gitlab-ci/, scripts/, docs/), documentation files (README.md, CHANGELOG.md, CONTRIBUTING.md)

## Reference Files

For detailed standards documentation, load reference files as needed:

- **`references/coding-style.md`** - Detailed coding style guidelines, naming conventions, formatting standards
- **`references/commenting.md`** - Commenting best practices, docstring standards, when to comment
- **`references/error-handling.md`** - Error handling patterns, exception hierarchies, logging strategies
- **`references/validation.md`** - Validation patterns, schema definitions, security considerations
- **`references/tech-stack.md`** - Technology stack reference, framework patterns, dependency guidelines
- **`references/conventions.md`** - Project conventions, file structure, git workflows, CI/CD standards

When working on specific areas, load the appropriate reference file for detailed guidance.

## Best Practices

### Consistency First

- Follow existing patterns in the codebase
- When in doubt, match the style of surrounding code
- Maintain consistency across all files

### Progressive Enhancement

- Start with simple, clear code
- Add complexity only when necessary
- Refactor for clarity and maintainability

### Documentation

- Keep documentation up to date
- Document decisions and trade-offs
- Include examples in documentation

### Quality Gates

- Use linters and formatters
- Run tests before committing
- Review code for standards adherence

## Integration with Other Skills

- **code-review**: Use when reviewing code for standards adherence
- **dead-code-removal**: Follow coding style when cleaning up code
- **debugging**: Apply error handling standards when analyzing errors
- **dependency-management**: Follow tech stack standards when managing dependencies
