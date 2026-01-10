# Analyzing Patterns Skill Resources

This directory contains resources for the analyzing-patterns skill.

## Directory Structure

### scripts/
Automation scripts for pattern detection and analysis:
- `pattern-detector.py` - Automated pattern recognition in code
- `duplicate-finder.sh` - Find duplicate/similar code blocks
- `convention-analyzer.py` - Extract naming and style conventions
- `architecture-mapper.py` - Visualize architectural patterns

### references/
Comprehensive pattern catalogs and quick references:

**Primary Resources:**
- `pattern-catalog.md` - **Comprehensive pattern encyclopedia** covering:
  - Design Patterns (GoF): 12+ creational, structural, and behavioral patterns
  - Architectural Patterns: MVC, MVVM, Microservices, Hexagonal, Layered, etc.
  - Concurrency Patterns: Producer-Consumer, Circuit Breaker, Promises
  - Data Patterns: Repository, Active Record, Data Mapper, Unit of Work
  - API Patterns: REST, GraphQL, BFF
  - Frontend Patterns: Component-based, Atomic Design, Container/Presenter
  - Testing Patterns: Test Doubles, AAA, Test Pyramid
  - Anti-Patterns: God Object, Spaghetti Code, Magic Numbers, etc.
  - *Each pattern includes*: Purpose, identifying signatures, code examples, when to use

- `pattern-quick-reference.md` - **Fast lookup guide** for rapid pattern identification:
  - Search keywords table
  - Grep patterns for each pattern type
  - File structure clues
  - Code signatures
  - Framework-specific patterns
  - Pattern decision tree
  - Validation checklist

**Coming Soon:**
- `refactoring-catalog.md` - Pattern-based refactoring techniques
- `framework-patterns.md` - Framework-specific pattern implementations

### assets/
Templates for documenting pattern findings:
- `pattern-template.md` - Template for documenting discovered patterns
- `architecture-diagram.md` - Template for architecture visualization
- `refactoring-checklist.md` - Checklist for pattern-based refactoring

## Usage

These resources are referenced in SKILL.md using the `{baseDir}` variable and are loaded on-demand when needed during pattern analysis.

Example:
```markdown
Refer to `{baseDir}/references/design-patterns-catalog.md` for detailed pattern descriptions.
```

## Contributing

To add new patterns or improve existing documentation:
1. Create/update files in the appropriate directory
2. Include code examples where helpful
3. Reference real-world use cases
4. Update this README if adding new file types

---

*Part of research-agent plugin*
