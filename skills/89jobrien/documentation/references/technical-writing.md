---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: reference
parent: documentation
---

# Technical Writing

Best practices for technical writing, user guides, README files, architecture documentation, and content organization.

## Writing Principles

### Write for Your Audience

**Know Your Audience:**

- Skill level (beginner, intermediate, advanced)
- Technical background
- Use case and goals
- Prior knowledge assumptions

**Adapt Your Writing:**

- Use appropriate terminology
- Provide context when needed
- Explain acronyms and jargon
- Include troubleshooting for common issues

### Lead with the Outcome

**Structure:**

1. What users will accomplish
2. Why it matters
3. How to do it (steps)
4. What to do next

**Example:**

```markdown
# Setting Up Your Development Environment

By the end of this guide, you'll have a fully functional development
environment running locally. This takes about 10 minutes and requires
no prior setup experience.

## What You'll Get

- Local development server running
- Database configured and seeded
- All dependencies installed
- Ready to start coding

## Prerequisites

- Node.js 18+ installed
- Git installed
- Text editor of your choice

## Steps

[Step-by-step instructions...]
```

### Use Active Voice

**Active Voice:**

- "Click the Submit button"
- "Run the test suite"
- "Install the dependencies"

**Passive Voice (Avoid):**

- "The Submit button should be clicked"
- "The test suite should be run"
- "Dependencies should be installed"

## User Guides

### Structure

1. **Overview**: What the guide covers and what users will learn
2. **Prerequisites**: What's needed before starting
3. **Steps**: Clear, numbered steps
4. **Examples**: Real examples with expected outcomes
5. **Troubleshooting**: Common issues and solutions
6. **Next Steps**: What to do after completing the guide

### Example: User Guide Template

```markdown
# User Guide: [Feature Name]

## What You'll Learn

By the end of this guide, you'll be able to:
- [Outcome 1]
- [Outcome 2]
- [Outcome 3]

## Prerequisites

- [Requirement 1]
- [Requirement 2]

## Step 1: [Action]

[Clear instructions with screenshots or code examples]

**Expected Result:**
[What users should see]

## Step 2: [Action]

[Continue with clear steps...]

## Troubleshooting

### Problem: [Common Issue]
**Solution**: [How to fix it]

### Problem: [Another Issue]
**Solution**: [How to fix it]

## Next Steps

- [Related guide or feature]
- [Additional resources]
```

## README Files

### Essential Sections

**Required:**

- Project title and description
- Installation instructions
- Quick start guide
- Usage examples
- License

**Recommended:**

- Badges (build status, version, license)
- Features list
- Contributing guidelines
- Changelog link
- Support/contact information

### README Template

```markdown
# Project Name

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://example.com)
[![Version](https://img.shields.io/badge/version-1.0.0-blue)](https://example.com)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

A brief description of what your project does and why it exists.

## Features

- Feature 1
- Feature 2
- Feature 3

## Installation

\`\`\`bash
npm install project-name
\`\`\`

## Quick Start

\`\`\`javascript
import { ProjectName } from 'project-name';

const instance = new ProjectName();
instance.doSomething();
\`\`\`

## Usage

[Detailed usage examples]

## Documentation

See [docs/](docs/) for full documentation.

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT
```

## Architecture Documentation

### Structure

1. **Overview**: High-level system architecture
2. **Components**: Major components and their responsibilities
3. **Data Flow**: How data moves through the system
4. **Technology Stack**: Technologies used and why
5. **Design Decisions**: Key architectural decisions and rationale
6. **Integration Points**: How components integrate
7. **Scaling Considerations**: How the system scales

### Example: Architecture Doc Template

```markdown
# System Architecture

## Overview

[High-level description of the system]

## Architecture Diagram

[Diagram showing components and relationships]

## Components

### [Component Name]
- **Purpose**: [What it does]
- **Responsibilities**: [Key responsibilities]
- **Technologies**: [Technologies used]
- **Interfaces**: [How other components interact with it]

## Data Flow

[Description of how data flows through the system]

## Technology Stack

- **Frontend**: [Framework and libraries]
- **Backend**: [Framework and libraries]
- **Database**: [Database technology]
- **Infrastructure**: [Infrastructure choices]

## Design Decisions

### Decision 1: [Decision]
**Rationale**: [Why this decision was made]
**Alternatives Considered**: [Other options]
**Trade-offs**: [What was traded off]

## Integration Points

[How components integrate with each other and external systems]

## Scaling Considerations

[How the system scales horizontally and vertically]
```

## Code Documentation

### Docstrings

**Python:**

```python
def calculate_total(items):
    """
    Calculate the total price of items.

    Args:
        items: List of items with 'price' attribute

    Returns:
        float: Total price of all items

    Raises:
        ValueError: If items list is empty
    """
    if not items:
        raise ValueError("Items list cannot be empty")
    return sum(item.price for item in items)
```

**JavaScript (JSDoc):**

```javascript
/**
 * Calculate the total price of items.
 *
 * @param {Array<{price: number}>} items - List of items with price
 * @returns {number} Total price of all items
 * @throws {Error} If items list is empty
 */
function calculateTotal(items) {
  if (!items.length) {
    throw new Error('Items list cannot be empty');
  }
  return items.reduce((sum, item) => sum + item.price, 0);
}
```

### Inline Comments

**When to Comment:**

- Complex algorithms or business logic
- Non-obvious code decisions
- Workarounds or hacks
- Why code exists (not what it does)

**When Not to Comment:**

- Obvious code
- Code that restates what's already clear
- Outdated information

## Content Organization

### Heading Structure

**Hierarchy:**

- # Main Title (H1) - One per document

- ## Major Sections (H2)

- ### Subsections (H3)

- #### Details (H4)

**Best Practices:**

- Use descriptive headings
- Maintain consistent hierarchy
- Don't skip heading levels
- Use heading levels for structure, not styling

### Navigation

**Table of Contents:**

```markdown
## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Examples](#examples)
- [Contributing](#contributing)
```

**Cross-References:**

```markdown
See [Installation Guide](./installation.md) for setup instructions.
Refer to [API Documentation](./api.md#authentication) for auth details.
```

## Best Practices

### Writing Guidelines

1. **Clarity**: Use simple, clear language
2. **Structure**: Organize with clear headings
3. **Examples**: Include real, working examples
4. **Testing**: Test all instructions yourself
5. **Feedback**: Include ways for users to provide feedback

### Content Quality

- **Accuracy**: Verify all information is correct
- **Completeness**: Cover all necessary topics
- **Currency**: Keep documentation up to date
- **Consistency**: Use consistent terminology and style
- **Accessibility**: Write for diverse audiences

### Formatting

- **Code Blocks**: Use syntax highlighting
- **Lists**: Use bullet points for unordered, numbers for steps
- **Tables**: Use tables for structured data
- **Images**: Include alt text and captions
- **Links**: Use descriptive link text
