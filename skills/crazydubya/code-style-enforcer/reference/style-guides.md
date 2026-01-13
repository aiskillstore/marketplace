## Popular Style Guides by Language

### JavaScript/TypeScript

**Airbnb JavaScript Style Guide**
- URL: https://github.com/airbnb/javascript
- Most popular JS style guide
- Covers ES6+, React, best practices
- Opinionated but comprehensive

**Google JavaScript Style Guide**
- URL: https://google.github.io/styleguide/jsguide.html
- Conservative, less opinionated
- Good for large teams

**Standard JS**
- URL: https://standardjs.com/
- No configuration
- No semicolons, 2 spaces
- Auto-fixable

**TypeScript Style Guide**
- Official: https://www.typescriptlang.org/docs/handbook/declaration-files/do-s-and-don-ts.html
- Microsoft: https://github.com/Microsoft/TypeScript/wiki/Coding-guidelines

### Python

**PEP 8 - Style Guide for Python Code**
- URL: https://pep8.org/
- Official Python style guide
- Industry standard
- Covers naming, formatting, imports

**Google Python Style Guide**
- URL: https://google.github.io/styleguide/pyguide.html
- More detailed than PEP 8
- Adds Google-specific conventions

**Black (The Uncompromising Code Formatter)**
- URL: https://black.readthedocs.io/
- Auto-formatter with minimal config
- Enforces consistent style

### Ruby

**Ruby Style Guide (RuboCop default)**
- URL: https://rubystyle.guide/
- Community-driven
- Comprehensive

**GitHub Ruby Style Guide**
- URL: https://github.com/github/rubocop-github/blob/main/STYLEGUIDE.md
- Based on Rubystyle with tweaks

### Go

**Effective Go**
- URL: https://go.dev/doc/effective_go
- Official Go style guide
- `go fmt` enforces formatting

**Go Code Review Comments**
- URL: https://github.com/golang/go/wiki/CodeReviewComments
- Common mistakes and style issues

### Java

**Google Java Style Guide**
- URL: https://google.github.io/styleguide/javaguide.html
- Well-defined, comprehensive

**Oracle Code Conventions**
- URL: https://www.oracle.com/java/technologies/javase/codeconventions-contents.html
- Classic reference (older)

### C++

**Google C++ Style Guide**
- URL: https://google.github.io/styleguide/cppguide.html
- Opinionated but practical

**C++ Core Guidelines**
- URL: https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines
- By Bjarne Stroustrup and Herb Sutter

### Rust

**Rust Style Guidelines**
- URL: https://doc.rust-lang.org/1.0.0/style/
- `rustfmt` enforces style

### PHP

**PSR-12: Extended Coding Style Guide**
- URL: https://www.php-fig.org/psr/psr-12/
- PHP Framework Interop Group standard

### Swift

**Swift API Design Guidelines**
- URL: https://swift.org/documentation/api-design-guidelines/
- Official Apple guidelines

### Kotlin

**Kotlin Coding Conventions**
- URL: https://kotlinlang.org/docs/coding-conventions.html
- Official JetBrains guide

## General Best Practices

### Naming Conventions

**Variables:**
- camelCase: JavaScript, Java, C#
- snake_case: Python, Ruby, Rust
- Descriptive over short

**Constants:**
- UPPER_SNAKE_CASE: Most languages
- ALL_CAPS with underscores

**Classes:**
- PascalCase: Universal
- Nouns or noun phrases

**Functions/Methods:**
- camelCase: JavaScript, Java
- snake_case: Python, Ruby
- Verbs or verb phrases

**Booleans:**
- Prefix: `is`, `has`, `should`, `can`
- Example: `isActive`, `hasPermission`

**Private members:**
- Underscore prefix: `_private` (Python)
- No prefix, use scope: JavaScript, Java

### File Naming

**JavaScript/TypeScript:**
- Components: `PascalCase.tsx` (React)
- Utilities: `camelCase.ts` or `kebab-case.ts`
- Tests: `*.test.ts` or `*.spec.ts`

**Python:**
- Modules: `snake_case.py`
- Packages: `snake_case/`

**Ruby:**
- Files: `snake_case.rb`
- Classes match file: `UserController` → `user_controller.rb`

**Java:**
- Must match class: `UserService.java`

### Comment Styles

**Single-line:**
```javascript
// JavaScript, C-style
# Python, Ruby, Shell
-- SQL
```

**Multi-line:**
```javascript
/**
 * JSDoc style for documentation
 * @param {string} name
 */

/*
 * Block comment for regular comments
 */
```

**Documentation:**
- JSDoc (JavaScript/TypeScript)
- Docstrings (Python)
- RDoc (Ruby)
- JavaDoc (Java)

### Import Organization

**Standard order:**
1. Standard library imports
2. Third-party imports
3. Local/internal imports
4. Relative imports

**Formatting:**
```javascript
// External
import React from 'react';
import express from 'express';

// Internal
import { UserService } from '@/services';

// Relative
import { helpers } from './helpers';
```

```python
# Standard library
import os
import sys

# Third-party
import numpy as np
import pandas as pd

# Local
from .models import User
from .utils import helpers
```

## Tools for Enforcement

### Linters
- **ESLint**: JavaScript/TypeScript
- **Pylint/Flake8**: Python
- **RuboCop**: Ruby
- **golangci-lint**: Go
- **Checkstyle**: Java

### Formatters
- **Prettier**: JavaScript/TypeScript/CSS/JSON/etc.
- **Black**: Python
- **rustfmt**: Rust
- **gofmt**: Go
- **clang-format**: C/C++

### Editor Integration
- **EditorConfig**: Cross-editor configuration
- **LSP (Language Server Protocol)**: IDE integration
- **Format on save**: Most modern editors support

## Team Style Guide Template

```markdown
# [Project Name] Style Guide

## Language: [JavaScript/Python/etc.]

### Base Style Guide
We follow [Airbnb JavaScript Style Guide / PEP 8 / etc.]

### Modifications
- [Any deviations from base guide]

### Tooling
- Linter: [ESLint/Pylint/etc.] (config: [path])
- Formatter: [Prettier/Black/etc.] (config: [path])
- Pre-commit hooks: [Yes/No]

### Naming Conventions
- Files: [convention]
- Variables: [convention]
- Constants: [convention]
- Classes: [convention]
- Functions: [convention]

### File Organization
- [Describe directory structure]
- [Import ordering]
- [Export patterns]

### Comments
- Prefer self-documenting code
- Use JSDoc/Docstrings for public APIs
- TODO format: `// TODO(username): Description`

### Testing
- Test files: [naming and location]
- Test naming: [convention]

### Git Conventions
- Branch naming: [convention]
- Commit messages: [convention]
- PR templates: [location]

### Resources
- [Links to tools, guides, examples]
```

## References

- [Google Style Guides](https://google.github.io/styleguide/) - Multiple languages
- [Airbnb Style Guides](https://github.com/airbnb) - JavaScript, Ruby, etc.
- [Clean Code by Robert C. Martin](https://www.amazon.com/Clean-Code-Handbook-Software-Craftsmanship/dp/0132350882)
- [The Pragmatic Programmer](https://pragprog.com/titles/tpp20/)
