# Error Detective Skill

Systematic debugging and error resolution using the TRACE framework.

## Overview

The Error Detective skill provides a comprehensive, methodical approach to debugging errors across multiple programming languages and frameworks. It guides you through the entire debugging process from initial error discovery to verified resolution.

## Core Components

### SKILL.md (593 lines)
Main skill file containing:
- TRACE framework methodology (Trace, Read, Analyze, Check, Execute)
- Common error patterns by language (Python, JavaScript, Java, Go)
- Debugging workflows and best practices
- Error severity classification
- Advanced debugging techniques

### Scripts

**debug_helper.py** - Python debugging utilities providing:
- Stack trace parsing for Python, JavaScript, Java, and Go
- Log file analysis and error aggregation
- Debug session management with timestamped notes

Usage:
```bash
# Parse stack trace
python scripts/debug_helper.py parse-trace error.log

# Analyze logs
python scripts/debug_helper.py analyze-log app.log --pattern ERROR

# Manage debug sessions
python scripts/debug_helper.py session start "Login error investigation"
python scripts/debug_helper.py session note "Tested with different browsers"
python scripts/debug_helper.py session close "Fixed: Added CORS headers"
```

### Examples

**debugging_workflow.md** - Complete workflow examples:
- Example 1: Python AttributeError (simple case)
- Example 2: JavaScript Promise rejection (async issue)
- Example 3: Java NullPointerException (multi-layer issue)

**common_errors.md** - Comprehensive error catalog:
- Python errors (AttributeError, KeyError, IndexError, TypeError, etc.)
- JavaScript errors (TypeError, ReferenceError, Promise rejections)
- Java errors (NullPointerException, ClassCastException, ConcurrentModificationException)
- Database errors (connection timeout, deadlocks)
- Network/API errors (404, 500, CORS)

**stack_traces.txt** - Annotated stack trace examples:
- Python Django stack trace
- JavaScript/Node.js stack trace
- Java stack trace with "Caused by"
- Go panic trace
- Includes reading tips and patterns to recognize

## Skill Characteristics

- **Complexity**: Medium-Complex (593 lines)
- **Languages Covered**: Python, JavaScript/TypeScript, Java, Go
- **Methodologies**: TRACE framework, systematic debugging
- **Tools**: Stack trace parser, log analyzer, session manager

## When to Use

Activate this skill when:
- Debugging errors or exceptions
- Analyzing stack traces
- Investigating production failures
- Performing root cause analysis
- Troubleshooting intermittent issues
- Learning debugging best practices

## Key Features

### The TRACE Framework
1. **T**race the Error - Capture complete error information
2. **R**ead the Error Message - Extract all information from the error
3. **A**nalyze the Context - Understand broader context
4. **C**heck for Root Cause - Identify underlying issue
5. **E**xecute the Fix - Implement and verify solution

### Debugging Patterns
- Stack trace analysis across multiple languages
- Error pattern recognition
- Root cause identification
- Hypothesis testing methodology
- Prevention strategies

### Practical Tools
- Automated stack trace parsing
- Log analysis and aggregation
- Debug session tracking
- Error pattern catalog

## File Structure
```
error-detective/
├── SKILL.md                      # Main skill (593 lines)
├── scripts/
│   └── debug_helper.py          # Debugging utilities
├── examples/
│   ├── debugging_workflow.md    # Complete workflow examples
│   ├── common_errors.md         # Error pattern catalog
│   └── stack_traces.txt         # Annotated stack traces
└── README.md                    # This file
```

## Quality Standards

✅ Follows SKILL_CREATION_GUIDE.md guidelines
✅ YAML frontmatter with clear description
✅ Systematic methodology (TRACE framework)
✅ Multiple language support
✅ Executable helper scripts
✅ Comprehensive examples
✅ Well-organized with progressive disclosure

---

Created following the Claude Skills Creation Guide standards for medium-complexity skills.
