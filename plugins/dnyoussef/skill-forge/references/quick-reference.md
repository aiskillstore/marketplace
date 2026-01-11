# Skill Forge Quick Reference

This document provides a condensed reference for the seven-phase Skill Forge methodology. Consult the main SKILL.md for comprehensive guidance.

## Phase 1: Intent Archaeology
**Goal**: Understand what skill truly needs to be created

Key Actions:
- Apply extrapolated-volition principles to understand true intent
- Surface implicit assumptions and hidden constraints
- Map the problem space and contextual relationships
- Ask strategic clarifying questions when needed
- Document core understanding as foundation for design

Critical Questions:
- What triggers the need for this skill in real workflows?
- What makes this workflow challenging or repetitive?
- What do desired outputs look like concretely?
- What variations or edge cases need handling?
- What constraints must be satisfied?

## Phase 2: Use Case Crystallization
**Goal**: Transform abstract understanding into concrete examples

Key Actions:
- Generate 3-5 representative usage examples
- Validate examples match intended usage patterns
- Analyze examples to identify patterns and variations
- Ensure examples adequately cover skill scope

Output: Concrete examples that serve as design targets

## Phase 3: Structural Architecture
**Goal**: Design skill structure using progressive disclosure and prompting principles

Key Actions:
- Apply progressive disclosure across metadata, SKILL.md, and resources
- Identify requirements for scripts, references, and assets
- Structure SKILL.md content with hierarchical organization
- Apply evidence-based prompting techniques (self-consistency, plan-and-solve, etc.)
- Optimize for clarity and discoverability

Decisions:
- What goes in SKILL.md vs bundled resources?
- What prompting patterns apply to this skill type?
- How should information be organized for optimal understanding?

## Phase 4: Metadata Engineering
**Goal**: Craft strategic name and description for optimal discovery

Key Actions:
- Choose memorable, descriptive, distinct name
- Write 3-5 sentence description that clarifies purpose and triggers
- Incorporate terminology matching natural language queries
- Specify clear boundaries (what skill does and doesn't do)
- Use third-person voice ("Use when..." not "You use when...")

Remember: These ~100 words determine when Claude finds and activates the skill

## Phase 5: Instruction Crafting
**Goal**: Write clear, actionable skill content with prompting best practices

Key Actions:
- Adopt imperative voice (verb-first instructions)
- Provide clear procedural steps for workflows
- Include rationale for non-obvious design choices
- Specify success criteria and quality mechanisms
- Address known failure modes with guardrails
- Reference bundled resources with clear usage guidance

Style: "Analyze the data" not "You should analyze the data"

## Phase 6: Resource Development
**Goal**: Create reusable scripts, references, and assets

Key Actions:
- Develop well-commented scripts for deterministic operations
- Compile reference documentation with clear structure
- Curate production-quality asset files
- Maintain separation of concerns across resource types
- Document resource usage in SKILL.md

Organization:
- scripts/ = executable code
- references/ = documentation to load as needed
- assets/ = files used in outputs

## Phase 7: Validation and Iteration
**Goal**: Ensure skill meets quality standards before deployment

Key Actions:
- Run validation script to check structure and metadata
- Conduct functionality testing in realistic scenarios
- Assess clarity and usability
- Check for anti-patterns in design
- Iterate based on feedback
- Package for distribution once validated

Command: `python3 /mnt/skills/examples/skill-creator/scripts/package_skill.py <skill-path>`

## Strategic Design Principles

Apply throughout the process:

**Design for Discovery**: Create metadata enabling appropriate activation
**Optimize for Learning**: Structure skills to build understanding over time
**Balance Specificity and Flexibility**: Specific enough to be useful, flexible enough to adapt
**Prioritize Maintainability**: Make skills easy to understand, update, extend
**Think in Systems**: Consider how skills compose with others
**Emphasize Quality Over Quantity**: Fewer well-engineered skills beats many mediocre ones

## Evidence-Based Prompting Techniques

**Self-Consistency**: For analytical skills, build in validation and multiple perspectives
**Program-of-Thought**: For logical tasks, structure step-by-step explicit reasoning
**Plan-and-Solve**: For complex workflows, plan first, execute systematically, verify
**Structural Guardrails**: Critical info at start/end, clear delimiters, hierarchical organization
**Negative Examples**: For known failure patterns, include what to avoid

## Common Skill Patterns

**Workflow-Based**: Sequential processes (best for step-by-step procedures)
**Task-Based**: Tool collections (best for different operations/capabilities)
**Reference/Guidelines**: Standards or specifications (best for requirements/guidelines)
**Capabilities-Based**: Integrated systems (best for multiple interrelated features)

Patterns can be mixed and matched as needed.

## Validation Checklist

Before packaging, verify:
- [ ] YAML frontmatter format correct
- [ ] Name is memorable, descriptive, distinct
- [ ] Description clearly states what and when (3-5 sentences)
- [ ] Description uses third-person voice
- [ ] SKILL.md uses imperative voice throughout
- [ ] Instructions are clear and actionable
- [ ] Examples are concrete and representative
- [ ] Resources are properly organized (scripts/, references/, assets/)
- [ ] Known failure modes addressed
- [ ] Prompting principles applied appropriately
- [ ] Skill tested in realistic scenarios

## Installation Locations

**Personal Skills** (available across all projects):
```
~/.claude/skills/skill-name/
```

**Project Skills** (specific to one project):
```
.claude/skills/skill-name/
```

Changes take effect on next Claude Code session start.

## Continuous Improvement

After deployment:
- Observe skill performance in actual usage
- Note where Claude struggles or excels
- Identify instruction clarity issues
- Update based on feedback
- Build pattern library from successes
- Iterate continuously

Remember: Skill creation is iterative. Initial designs improve through use and refinement.
