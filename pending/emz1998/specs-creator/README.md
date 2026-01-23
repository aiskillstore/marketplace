# Specs Creator Skill

A comprehensive Agent Skill for creating detailed specifications from client needs.

## Overview

This skill helps gather and document client requirements into comprehensive, development-ready specifications. It supports creating:

- **Product Specifications (PRD)** - User-facing features, business goals, product requirements
- **Technical Specifications** - Architecture, implementation details, technology stack
- **Design Specifications** - UI/UX requirements, visual design, interaction patterns
- **API Specifications** - Endpoint definitions, request/response schemas, authentication

## File Structure

```
specs-creator/
├── SKILL.md                    # Main skill instructions (loaded when triggered)
├── README.md                   # This file
├── PRODUCT-TEMPLATE.md         # Product specification template
├── TECHNICAL-TEMPLATE.md       # Technical specification template
├── DESIGN-TEMPLATE.md          # Design specification template
├── API-TEMPLATE.md             # API specification template
└── scripts/
    └── validate-spec.py        # Specification validation script
```

## How It Works

### Progressive Disclosure

The skill uses a three-level loading system:

1. **Metadata (Always Loaded)**: Skill name and description in YAML frontmatter
2. **Main Instructions (Loaded When Triggered)**: SKILL.md with core workflow and guidance
3. **Resources (Loaded As Needed)**: Template files and validation scripts

### Workflow

When creating a specification, Claude follows this systematic process:

1. **Identify Specification Type** - Determine what type of spec is needed
2. **Gather Requirements** - Ask targeted questions based on spec type
3. **Organize Information** - Structure collected requirements
4. **Create Specification** - Use appropriate template
5. **Validate Completeness** - Check for gaps and ambiguities
6. **Review and Finalize** - Final review and formatting

## Templates

Each template provides a complete structure for that specification type:

### Product Template
- Executive summary, problem statement, user stories
- Requirements (must-have, should-have, nice-to-have)
- Success metrics, dependencies, timeline
- Full validation checklist

### Technical Template
- System architecture, technology stack
- Components, data models, API specifications
- Security, performance requirements
- Testing strategy, deployment plan

### Design Template
- Design goals, user personas, user flows
- Visual design system (colors, typography, spacing)
- Component library, interaction patterns
- Accessibility requirements, responsive design

### API Template
- Authentication, rate limiting, error handling
- Endpoint documentation with examples
- Data models, webhooks
- Versioning strategy, SDK documentation

## Validation Script

The `validate-spec.py` script checks specifications for:

- **Clarity**: No vague terms, includes examples and measurable criteria
- **Completeness**: Has acceptance criteria, dependencies, out-of-scope items
- **Consistency**: Consistent terminology, date formats
- **Type-Specific**: Validates requirements specific to each spec type

### Usage

```bash
# Auto-detect spec type
python scripts/validate-spec.py path/to/spec.md

# Specify spec type
python scripts/validate-spec.py path/to/spec.md --type technical
```

### Exit Codes

- `0`: All validations passed
- `1`: Validation failures found

## Usage Examples

### Creating a Product Specification

```
User: "I need to create a product spec for a new user authentication feature"

Claude:
1. Identifies this as a product specification
2. Asks discovery questions about user needs, business goals, constraints
3. Gathers requirements through structured questions
4. Creates specification using PRODUCT-TEMPLATE.md
5. Validates for completeness
6. Returns polished product specification
```

### Creating an API Specification

```
User: "Create API specs for our REST API endpoints"

Claude:
1. Identifies this as an API specification
2. Asks about authentication, endpoints, data models
3. Gathers endpoint details, error handling, rate limits
4. Creates specification using API-TEMPLATE.md
5. Includes request/response examples
6. Returns complete API documentation
```

## Best Practices

### Good Specifications Have:
- Specific, measurable acceptance criteria
- Concrete examples with input/output
- Well-defined edge cases and error handling
- Explicit dependencies and assumptions
- Quantified performance requirements
- Structured, easy-to-navigate format

### Avoid:
- Vague requirements ("fast", "user-friendly", "secure")
- Missing acceptance criteria
- Conflicting requirements
- Undefined technical terms
- No prioritization
- Missing error handling

## Question Patterns

The skill uses targeted question patterns:

### Discovery Questions
- "What happens when [edge case]?"
- "How should the system handle [error condition]?"
- "What are the performance expectations for [scenario]?"

### Clarification Questions
- "When you say [term], do you mean [A] or [B]?"
- "Can you provide an example of [requirement]?"
- "What does success look like for [feature]?"

### Constraint Questions
- "What are the technical constraints?"
- "What is the timeline for delivery?"
- "What compliance requirements must be met?"

### Prioritization Questions
- "If you could only have three features, which would they be?"
- "What is absolutely required for launch vs. what can wait?"

## Integration with Development Workflow

Specifications created with this skill are ready for:

1. **Design Handoff** - Designers can use specs to create mockups
2. **Development Handoff** - Engineers have clear requirements
3. **Testing** - QA has acceptance criteria to validate against
4. **Stakeholder Review** - Business stakeholders can approve
5. **Documentation** - Specs serve as project documentation

## Validation Checklist

Each template includes a validation checklist covering:

- **Clarity**: All terms defined, requirements specific and measurable
- **Completeness**: All sections filled, dependencies identified
- **Consistency**: Different sections align, naming is consistent
- **Feasibility**: Requirements technically achievable, timelines realistic

## Version History

- **1.0.0** (2025-01-17) - Initial release
  - Product specification template
  - Technical specification template
  - Design specification template
  - API specification template
  - Validation script
  - Comprehensive workflow guidance

## License

This skill is part of the Avaris project.
