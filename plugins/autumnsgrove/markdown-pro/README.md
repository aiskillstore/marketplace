# Professional Markdown Documentation

Professional Markdown documentation skill for creating polished README files, changelogs, contribution guides, and technical documentation.

## Overview

This skill provides comprehensive guidance for creating professional, well-structured Markdown documentation. It covers README files, changelogs, contribution guides, and technical documentation with modern formatting, badges, and best practices.

Use this skill for README generation with badges and sections, automated changelog from git history, table of contents generation, contribution guidelines, technical documentation formatting, and code documentation with syntax highlighting.

## Installation

No installation required for basic Markdown documentation.

Optional: Install helper script dependencies:

```bash
pip install markdown
```

## What's Included

### SKILL.md
Comprehensive guide covering README structure best practices, changelog formats, Markdown formatting best practices, badge creation, code syntax highlighting, tables, collapsible sections, alert boxes, links, images, and helper scripts.

### scripts/
- `markdown_helper.py` - Utility script for:
  - Automatic table of contents generation
  - Changelog generation from git history
  - Link validation

### examples/
- `README_template.md` - Complete, production-ready README template
- `CHANGELOG_template.md` - Properly formatted changelog following Keep a Changelog
- `CONTRIBUTING.md` - Contributor guidelines template

## Quick Start

### README Structure

**Essential Sections:**

```markdown
# Project Name

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-green.svg)](releases)

Brief one-line description of what the project does.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Feature 1**: Clear description with benefits
- **Feature 2**: What problems it solves
- **Feature 3**: Unique selling points

## Installation

```bash
pip install package-name
```

## Usage

```python
from package import Module

# Basic example
client = Module(api_key="your-key")
result = client.process(data)
```

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.
```

### Changelog Format

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- New feature description

### Changed
- Modification to existing feature

### Fixed
- Bug fixes

## [1.2.0] - 2025-01-15

### Added
- User authentication system (#123)
- Export to CSV functionality (#145)

### Fixed
- Fixed memory leak in background processor (#139)
```

## Key Features

### README Generation
- Project overview and description
- Installation instructions
- Usage examples with code blocks
- API documentation
- Badges and shields
- Feature highlights
- Screenshots and demos

### Changelog Automation
- Semantic versioning format
- Git history parsing
- Automated release notes
- Breaking changes highlighting
- Contributor attribution

### Technical Documentation
- Clear section hierarchy
- Code syntax highlighting
- API reference formatting
- Table of contents
- Cross-referencing
- Collapsible sections

## Markdown Formatting Best Practices

### Code Blocks with Syntax Highlighting

```markdown
```python
def hello_world():
    """Print hello world message."""
    print("Hello, World!")
\```

```javascript
function helloWorld() {
    console.log("Hello, World!");
}
\```

```bash
# Install dependencies
npm install
\```
```

### Tables

```markdown
| Feature | Description | Status |
|---------|-------------|--------|
| Auth | User authentication | ✅ Complete |
| API | RESTful API endpoints | ✅ Complete |
| Docs | Documentation | 🚧 In Progress |
| Tests | Unit & Integration | ❌ Planned |
```

### Collapsible Sections

```markdown
<details>
<summary>Click to expand advanced configuration</summary>

## Advanced Options

Configure advanced settings:

```yaml
advanced:
  cache_size: 1000
  timeout: 30
\```

</details>
```

### Alert Boxes

```markdown
> **Note**: This feature requires Python 3.8 or higher.

> **Warning**: This operation is irreversible!

> **Important**: Always backup your data before upgrading.
```

## Badge Creation

### Common Badge Patterns

```markdown
<!-- License -->
![License](https://img.shields.io/badge/license-MIT-blue.svg)

<!-- Version -->
![Version](https://img.shields.io/badge/version-1.0.0-green.svg)

<!-- Build Status -->
![Build](https://img.shields.io/badge/build-passing-brightgreen.svg)

<!-- Coverage -->
![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen.svg)

<!-- Language -->
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)

<!-- Platform -->
![Platform](https://img.shields.io/badge/platform-windows%20%7C%20macOS%20%7C%20linux-lightgrey.svg)
```

## Helper Scripts

### Generate Table of Contents

```bash
python scripts/markdown_helper.py toc README.md
```

### Generate Changelog from Git

```bash
python scripts/markdown_helper.py changelog --since v1.0.0 --output CHANGELOG.md
```

### Validate Markdown Links

```bash
python scripts/markdown_helper.py validate docs/
```

## Best Practices

### Do's
- Use clear, descriptive headers
- Include code examples for every major feature
- Add badges for quick project status overview
- Keep line length under 100 characters for readability
- Use syntax highlighting for code blocks
- Include table of contents for documents >300 lines
- Add alt text for all images
- Link to related documentation

### Don'ts
- Don't use generic titles like "My Project"
- Don't include wall-of-text paragraphs (break into sections)
- Don't forget to update changelog with releases
- Don't use bare URLs (always use descriptive link text)
- Don't mix heading styles (use consistent hierarchy)
- Don't include screenshots without descriptions
- Don't hardcode version numbers everywhere (use variables/badges)

## Header Hierarchy

```markdown
# H1 - Project Title (only one per document)
## H2 - Major Sections
### H3 - Subsections
#### H4 - Minor Points
##### H5 - Rare, for deep nesting
```

## List Formatting

```markdown
<!-- Unordered -->
- Item 1
- Item 2
  - Nested item
  - Another nested item

<!-- Ordered -->
1. First step
2. Second step
3. Third step

<!-- Task list -->
- [x] Completed task
- [ ] Pending task
- [ ] Another pending task
```

## Emphasis

```markdown
*italic* or _italic_
**bold** or __bold__
***bold italic*** or ___bold italic___
~~strikethrough~~
`inline code`
```

## API Documentation Format

```markdown
### `Module.process(data, options=None)`

Process input data with optional configuration.

**Parameters:**
- `data` (str|dict): Input data to process
- `options` (dict, optional): Configuration options
  - `verbose` (bool): Enable verbose output (default: False)
  - `format` (str): Output format - 'json', 'yaml', 'xml' (default: 'json')

**Returns:**
- `dict`: Processed results with metadata

**Raises:**
- `ValueError`: If data is invalid
- `APIError`: If API request fails

**Example:**
```python
result = client.process(
    data={"key": "value"},
    options={"verbose": True, "format": "json"}
)
\```
```

## Links and References

```markdown
<!-- External link -->
[Documentation](https://docs.example.com)

<!-- Internal link -->
See [Installation](#installation) section.

<!-- Reference-style links -->
Check out [project homepage][homepage] and [documentation][docs].

[homepage]: https://example.com
[docs]: https://docs.example.com
```

## Images

```markdown
<!-- Standard image -->
![Project Logo](assets/logo.png)

<!-- Image with alt text and title -->
![Dashboard Screenshot](screenshots/dashboard.png "Main Dashboard View")

<!-- Linked image -->
[![Demo Video](thumbnail.jpg)](https://youtube.com/watch?v=example)
```

## Templates

### Professional README Template

See `examples/README_template.md` for a complete, production-ready README template with all recommended sections.

### Changelog Template

See `examples/CHANGELOG_template.md` for a properly formatted changelog following Keep a Changelog format.

### Contributing Guidelines

See `examples/CONTRIBUTING.md` for contributor guidelines template including code of conduct, development setup, and PR process.

## Common Use Cases

### Creating Project Documentation
Generate comprehensive README files for GitHub projects with proper structure and formatting.

### Maintaining Changelogs
Automate changelog generation from git commit history following semantic versioning.

### API Documentation
Create clear, well-formatted API reference documentation with code examples.

### Contribution Guidelines
Provide clear guidelines for contributors with setup instructions and PR process.

## Documentation

See `SKILL.md` for comprehensive documentation, detailed formatting patterns, and advanced techniques.

## Requirements

No requirements for basic Markdown documentation. The skill provides templates and best practices.

Optional:
- Python 3.7+ (for helper scripts)
- markdown (Python library, for advanced features)
