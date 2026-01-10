---
name: CRUD with Spec-Kit
category: Development
author: Claude
version: 1.0.0
tags: [spec-kit, crud, scaffolding, automation, development]
description: A conceptual skill for implementing CRUD features driven by Spec-Kit and Claude Code
---

# CRUD with Spec-Kit Skill

## When to Use This Skill

Use this conceptual skill when you need to implement CRUD (Create, Read, Update, Delete) operations for applications using Spec-Kit and Claude Code. This skill is appropriate for:

- Building data-driven applications with well-defined specifications
- Generating backend APIs from feature specifications
- Creating frontend clients that consume CRUD APIs
- Ensuring implementation aligns with specified success criteria
- Rapidly scaffolding CRUD functionality based on specifications
- Maintaining consistency between specification and implementation

This skill should NOT be used for:
- Applications without clear specifications
- Systems requiring complex business logic beyond basic CRUD
- Prototypes where specifications are still evolving rapidly
- Applications with non-standard data access patterns

## Prerequisites

- Spec-Kit specification files describing the desired features
- Claude Code for AI-assisted development
- Understanding of CRUD operations and REST API concepts
- Development environment with appropriate tools for target platform
- Clear understanding of data models and relationships

## Conceptual Implementation Framework

### Specification Reading Capability
- Parse and interpret feature specifications from spec files
- Extract entity definitions, attributes, and relationships
- Identify required CRUD operations for each entity
- Map specification requirements to implementation patterns
- Validate specification completeness before starting implementation

### Backend Route Generation Capability
- Generate RESTful API endpoints based on entity definitions
- Create appropriate HTTP methods (GET, POST, PUT, DELETE) for each operation
- Implement proper request/response handling according to specification
- Generate request validation and error handling patterns
- Create data access layer methods matching specification requirements

### Frontend Client Generation Capability
- Generate API client code for consuming CRUD endpoints
- Create data models matching backend entities
- Implement UI components for CRUD operations (forms, lists, etc.)
- Generate service layers for API communication
- Create state management patterns for frontend applications

### Success Criteria Enforcement Capability
- Validate implementation against specification-defined success criteria
- Ensure all required functionality is implemented
- Verify that error handling matches specification requirements
- Confirm that data validation aligns with specification constraints
- Test that API responses conform to specified formats

### Code Scaffolding Capability
- Generate consistent code structure following best practices
- Create standardized file organization patterns
- Implement reusable components and utilities
- Generate boilerplate code for common operations
- Maintain consistent coding standards across the application

## Expected Input/Output

### Input Requirements:

1. **Specification Files**:
   - Feature specifications in Spec-Kit format
   - Entity definitions with attributes and relationships
   - Required operations and constraints
   - Success criteria and validation rules
   - API endpoint definitions

2. **Specification Elements**:
   - Entity names and descriptions
   - Attribute types and constraints
   - Relationship definitions
   - Required CRUD operations
   - Expected response formats

### Output Formats:

1. **Generated Backend Routes**:
   - RESTful endpoints following specification
   - Request/response models matching entity definitions
   - Proper HTTP status codes for different operations
   - Error responses matching specification requirements

2. **Generated Frontend Clients**:
   - Type-safe API client code
   - Data models matching backend entities
   - Service methods for each CRUD operation
   - UI component templates for data manipulation

3. **Scaffolding Output**:
   - Consistent file structure and organization
   - Standardized code patterns and conventions
   - Ready-to-use implementation templates
   - Documentation matching the specification

4. **Validation Results**:
   - Success/failure status of criteria enforcement
   - List of implemented vs. specified features
   - Compliance report against specification
   - Gap analysis between specification and implementation

## Development Workflow Integration

### Specification Analysis Phase
- Read and parse specification files to understand requirements
- Identify all entities and their relationships
- Extract validation rules and constraints
- Map specification elements to implementation patterns

### Code Generation Phase
- Generate backend API routes based on entity definitions
- Create frontend client code for API consumption
- Implement data access patterns matching specification
- Generate UI components for CRUD operations

### Validation Phase
- Verify generated code against specification requirements
- Ensure all success criteria are met
- Validate API responses match specification formats
- Confirm error handling follows specification patterns

## Quality Assurance Framework

### Specification Compliance
- Verify that all specified entities are implemented
- Ensure all required operations are available
- Validate that constraints are properly enforced
- Confirm that success criteria are met

### Code Quality Standards
- Maintain consistent coding patterns across generated code
- Follow platform-specific best practices
- Ensure generated code is maintainable and readable
- Validate that error handling is comprehensive

### Testing Integration
- Generate test cases based on specification requirements
- Create validation tests for CRUD operations
- Implement integration tests for API endpoints
- Generate unit tests for individual components

## Integration Patterns

### Spec-Kit Integration
- Read specification files in Spec-Kit format
- Map specification elements to implementation patterns
- Generate code that directly reflects specification requirements
- Maintain traceability between specification and implementation

### Claude Code Integration
- Leverage AI assistance for code generation
- Use Claude Code for complex implementation patterns
- Generate code that follows best practices and standards
- Ensure generated code is consistent and maintainable

### Development Pipeline Integration
- Integrate with CI/CD pipelines for automated generation
- Support version control for specification-driven changes
- Enable collaborative development based on specifications
- Facilitate specification-driven testing and validation

## Performance Considerations

- Optimize code generation for large specification files
- Consider performance implications of generated code
- Balance automation with maintainability requirements
- Monitor generation time for complex specifications
- Plan for scalability of generated applications

## Error Handling and Validation

- Validate specification files before code generation
- Handle malformed or incomplete specifications gracefully
- Provide clear error messages for specification issues
- Generate appropriate error handling in generated code
- Validate generated code against specification requirements