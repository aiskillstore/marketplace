---
name: Spec-Kit Claude Code Workflow
category: Development Process
author: Claude
version: 1.0.0
tags: [speckit, claude-code, workflow, specification, development]
description: A conceptual skill for guiding the Spec-Kit + Claude Code development workflow
---

# Spec-Kit Claude Code Workflow Skill

## When to Use This Skill

Use this conceptual skill when you need to establish and follow an effective development workflow combining Spec-Kit specifications with Claude Code assistance. This skill is appropriate for:

- Starting new projects with clear specification-driven development
- Organizing multi-folder repositories with consistent workflows
- Guiding team members through Spec-Kit + Claude Code processes
- Establishing best practices for specification-driven development
- Iterating on specifications and implementations simultaneously
- Maintaining consistency across different development phases

This skill should NOT be used for:
- Projects without established specifications
- Ad-hoc development without structured processes
- Teams that prefer code-first approaches without specifications
- Rapid prototyping where specifications would slow development

## Prerequisites

- Understanding of Spec-Kit specification concepts
- Access to Claude Code for AI-assisted development
- Repository with established folder structure
- Clear understanding of project requirements and goals
- Commitment to specification-driven development approach

## Conceptual Implementation Framework

### CLAUDE.md Multi-Folder Repository Structure Capability
- Define repository-wide guidelines in root CLAUDE.md
- Create folder-specific CLAUDE.md files for specialized rules
- Establish inheritance patterns from root to subfolders
- Document cross-folder dependencies and interactions
- Maintain consistent configuration across all project folders
- Enable folder-specific overrides while preserving global rules

### Specification File Formatting Capability
- Define standardized specification structure and format
- Establish consistent naming conventions for spec files
- Create templates for different types of specifications
- Implement validation rules for specification quality
- Ensure specifications are clear, testable, and implementable
- Support multiple specification formats within the same project

### Claude Code Implementation Guidance Capability
- Guide Claude Code to reference specifications during implementation
- Ensure code generation aligns with specification requirements
- Provide context about project structure and conventions
- Enable Claude Code to ask clarifying questions about specifications
- Establish feedback loops between implementation and specification
- Maintain traceability between specifications and code artifacts

### Prompt Iteration and Refinement Capability
- Develop systematic approaches to refining prompts
- Create feedback mechanisms for prompt effectiveness
- Establish iteration cycles for specification and prompt improvement
- Document successful prompt patterns for reuse
- Enable collaborative prompt refinement across team members
- Track prompt evolution and effectiveness over time

## Expected Input/Output

### Input Requirements:

1. **Repository Structure Information**:
   - Multi-folder repository layout and organization
   - Project-specific requirements and constraints
   - Existing specification files and documentation
   - Team conventions and coding standards
   - Technology stack and architectural decisions

2. **Specification Artifacts**:
   - Feature specifications in various formats
   - User stories and requirements documentation
   - Technical architecture documents
   - API contracts and interface definitions
   - Success criteria and acceptance tests

3. **Development Context**:
   - Current development phase or sprint
   - Available resources and time constraints
   - Team member expertise and preferences
   - Project timeline and milestones
   - Quality and security requirements

### Output Formats:

1. **Structured Workflow**:
   - Clear process for specification creation and refinement
   - Defined steps for Claude Code integration
   - Organized repository structure with appropriate CLAUDE.md files
   - Consistent approach to implementation and validation

2. **Specification Alignment**:
   - Code that matches specification requirements
   - Traceability between specifications and implementations
   - Clear mapping of features to specification sections
   - Validation that implementation meets success criteria

3. **Iterative Improvement**:
   - Refined specifications based on implementation feedback
   - Improved prompts for better Claude Code results
   - Enhanced workflow processes based on experience
   - Documented lessons learned and best practices

4. **Quality Assurance**:
   - Consistent code quality across the project
   - Proper adherence to specifications
   - Clear documentation of decisions and changes
   - Maintained project organization and structure

## Workflow Integration Patterns

### Specification-First Approach
- Create comprehensive specifications before implementation
- Use specifications as the source of truth for development
- Validate implementations against specifications
- Update specifications based on implementation insights

### Iterative Development Cycle
- Plan specification → Implement → Review → Refine cycle
- Regular checkpoints to validate specification accuracy
- Continuous feedback between specification and implementation
- Adaptive approach based on learning and discoveries

### Claude Code Integration
- Provide Claude Code with clear specification context
- Use specifications to guide code generation
- Validate Claude Code output against specifications
- Leverage Claude Code for specification refinement

## Quality Assurance Framework

### Specification Quality
- Ensure specifications are complete, clear, and testable
- Verify that specifications align with business requirements
- Check that specifications are implementable and realistic
- Confirm that specifications include success criteria

### Implementation Quality
- Validate that code matches specification requirements
- Ensure code quality and maintainability standards
- Verify that implementation follows architectural patterns
- Confirm that error handling and edge cases are addressed

### Workflow Quality
- Maintain consistent application of workflow processes
- Ensure all team members follow established patterns
- Monitor and improve workflow effectiveness
- Document and share workflow best practices

## Performance Considerations

- Balance specification completeness with development speed
- Optimize prompt effectiveness for Claude Code efficiency
- Streamline iteration cycles to maintain momentum
- Minimize overhead while maintaining quality standards
- Ensure workflow scales appropriately with team size

## Error Handling and Validation

- Handle incomplete or ambiguous specifications appropriately
- Manage conflicts between specifications and implementation needs
- Address cases where specifications need rapid changes
- Validate that Claude Code outputs align with specifications
- Handle specification evolution during development cycles

## Communication and Collaboration

- Establish clear communication channels for specification changes
- Enable collaborative specification development
- Facilitate knowledge sharing about workflow practices
- Create feedback mechanisms for continuous improvement
- Support onboarding of new team members to the workflow