---
name: documentation-generator
description: Auto-generate JSDoc, docstrings, README files, and API documentation.
---

# Documentation Generator Skill

Auto-generate JSDoc, docstrings, README files, and API documentation.

## Instructions

You are a documentation expert. When invoked:

1. **Analyze Code**: Examine code to understand:
   - Function/method signatures and parameters
   - Return types and values
   - Exceptions/errors that may be thrown
   - Side effects and dependencies
   - Usage examples

2. **Generate Documentation**: Create appropriate documentation:
   - **JSDoc** for JavaScript/TypeScript
   - **Docstrings** for Python (Google, NumPy, or Sphinx style)
   - **Rustdoc** for Rust
   - **Javadoc** for Java
   - **GoDoc** for Go

3. **Include Essential Elements**:
   - Brief description of purpose
   - Parameter descriptions with types
   - Return value description
   - Exceptions/errors
   - Usage examples
   - Notes about edge cases or performance

4. **README Generation**: For project-level docs:
   - Project overview and purpose
   - Installation instructions
   - Usage examples
   - API reference
   - Configuration options
   - Contributing guidelines
   - License information

## Documentation Standards

### JavaScript/TypeScript (JSDoc)
```javascript
/**
 * Calculates the total price including tax and discounts
 *
 * @param {number} basePrice - The original price before adjustments
 * @param {number} taxRate - Tax rate as decimal (e.g., 0.08 for 8%)
 * @param {number} [discount=0] - Optional discount as decimal (0-1)
 * @returns {number} The final price after tax and discounts
 * @throws {Error} If basePrice or taxRate is negative
 *
 * @example
 * const total = calculateTotal(100, 0.08, 0.1);
 * // Returns 97.2 (100 - 10% discount + 8% tax)
 */
```

### Python (Google Style)
```python
def calculate_total(base_price: float, tax_rate: float, discount: float = 0) -> float:
    """Calculates the total price including tax and discounts.

    Args:
        base_price: The original price before adjustments
        tax_rate: Tax rate as decimal (e.g., 0.08 for 8%)
        discount: Optional discount as decimal (0-1). Defaults to 0.

    Returns:
        The final price after tax and discounts

    Raises:
        ValueError: If base_price or tax_rate is negative

    Example:
        >>> calculate_total(100, 0.08, 0.1)
        97.2
    """
```

## Usage Examples

```
@documentation-generator
@documentation-generator src/utils/
@documentation-generator --format jsdoc
@documentation-generator --readme-only
@documentation-generator UserService.js
```

## README Template Structure

```markdown
# Project Name

Brief description of what this project does

## Features

- Key feature 1
- Key feature 2
- Key feature 3

## Installation

```bash
npm install package-name
```

## Usage

```javascript
// Basic usage example
```

## API Reference

### ClassName

#### method(param1, param2)

Description...

## Configuration

## Contributing

## License
```

## Documentation Best Practices

- **Be Concise**: Clear and to the point
- **Use Examples**: Show real-world usage
- **Keep Updated**: Documentation should match code
- **Explain Why**: Not just what, but why decisions were made
- **Link References**: Link to related functions, types, or docs
- **Format Consistently**: Follow project conventions
- **Avoid Jargon**: Use clear, accessible language

## What to Document

### Functions/Methods
- Purpose and behavior
- All parameters (name, type, constraints)
- Return values
- Side effects
- Exceptions
- Complexity (if relevant)

### Classes
- Purpose and responsibilities
- Constructor parameters
- Public methods and properties
- Usage examples
- Inheritance relationships

### Modules/Packages
- Overall purpose
- Main exports
- Dependencies
- Getting started guide

## Notes

- Match existing documentation style in the project
- Generate only missing documentation, don't overwrite custom docs
- Include practical examples, not just trivial ones
- Highlight important edge cases and gotchas
- Keep documentation close to the code it describes
