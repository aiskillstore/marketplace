# Project Planner Skill

A comprehensive skill that establishes Claude as a **Project Architect** to generate detailed planning documents that serve as blueprints for AI-assisted software development.

## What This Skill Does

This skill transforms Claude into a System Architect who creates comprehensive project documentation by:

1. **Defining the complete system architecture upfront** - All components, data flows, and integration points
2. **Setting clear project boundaries** - What's in scope, out of scope, and key constraints
3. **Creating traceable documentation** - Requirements → Design → Implementation tasks

The skill generates three essential documents:

1. **Requirements Document** - User stories with testable acceptance criteria and traceable IDs
2. **Design Document** - Complete system architecture with component maps, data flows, and integration specifications
3. **Implementation Plan** - Hierarchical task breakdown with requirement tracing and clear deliverables

## The Architect Approach

**Why it works:** Setting clear roles, responsibilities, and deliverables upfront dramatically improves output quality. By explicitly defining system components, data flows, and integration points before diving into details, the documentation becomes comprehensive and actionable.

## Quick Start

### Generate Documents Using the Script

```bash
# Basic usage
python scripts/generate_project_docs.py "My Project Name"

# Specify project type
python scripts/generate_project_docs.py "Trading Bot" --type web-app

# Custom features and components
python scripts/generate_project_docs.py "E-commerce Site" \
  --features "user authentication" "product catalog" "shopping cart" \
  --components "Auth Service" "Product Service" "Order Service" \
  --output ./docs
```

### Validate Your Documents

```bash
# Validate all documents
python scripts/validate_documents.py \
  --requirements requirements.md \
  --design design.md \
  --tasks tasks.md
```

## Document Types

### Requirements Document
- User stories in standard format
- Testable acceptance criteria using SHALL statements
- Requirement numbering for traceability
- Glossary of domain terms

### Design Document  
- System architecture diagrams
- Component responsibilities and interfaces
- Data models and schemas
- Error handling strategies
- Deployment configuration

### Implementation Plan
- Hierarchical task breakdown
- Requirement tracing (links tasks to requirements)
- Dependency management between tasks
- Progress tracking with checkboxes

## Project Types Supported

- **web-app**: Full-stack web applications
- **cli-tool**: Command-line tools and utilities
- **api-service**: REST/GraphQL API services
- **generic**: General purpose projects

## Files Included

### Scripts
- `generate_project_docs.py` - Automated document generation
- `validate_documents.py` - Document validation and completeness checking

### References
- `domain-templates.md` - Domain-specific templates and patterns

### Assets
- `requirements-template.md` - Basic requirements document template

## Best Practices

1. **Start with Requirements** - Define what the system should do before how
2. **Be Specific** - Use measurable criteria (e.g., "within 100ms" not "fast")
3. **Trace Requirements** - Link every task back to requirements
4. **Include Non-Functional Requirements** - Performance, security, scalability
5. **Define Clear Interfaces** - Specify how components interact
6. **Plan Incrementally** - Break large tasks into smaller, manageable pieces

## Common Use Cases

### Starting a New Project
```
User: "I want to build a real-time chat application"
AI: [Uses this skill to generate complete project documentation]
```

### Expanding Existing Project
```
User: "Add user authentication to my project requirements"
AI: [Adds properly formatted requirements with acceptance criteria]
```

### Creating Technical Specification
```
User: "Design the architecture for a microservices e-commerce platform"
AI: [Generates design document with components, interfaces, and deployment]
```

## Tips for AI Implementation

When using these documents for AI-assisted development:

1. **Requirements First** - Implement in order of requirement priority
2. **Follow Task Dependencies** - Complete prerequisite tasks first
3. **Test Against Acceptance Criteria** - Each SHALL statement is a test case
4. **Reference Design Interfaces** - Use the specified APIs and data models
5. **Track Progress** - Check off completed tasks in the implementation plan

## Validation Checklist

Before using documents for implementation:

- [ ] All placeholders ([PLACEHOLDER]) filled in
- [ ] Requirements have testable acceptance criteria
- [ ] Design includes all major components
- [ ] Tasks reference requirement IDs
- [ ] Dependencies between tasks identified
- [ ] Non-functional requirements specified
- [ ] Deployment configuration included

## Example Output

The generated documents follow industry-standard formats that are:
- **Machine-readable** - Structured for AI parsing
- **Human-readable** - Clear for developers to understand  
- **Version-control friendly** - Plain text Markdown format
- **Traceable** - Requirements linked through all documents

This skill transforms high-level project ideas into actionable specifications that AI agents can use to build working software.
