# Documentation Templates

Templates for generating AGENTS.md and consolidating project documentation.

## Minimal AGENTS.md Template

```markdown
# Project Name

Brief description of what this project does.

## Quick Start

\`\`\`bash
# Setup
npm install  # or pip install, etc.

# Run
npm start    # or relevant command
\`\`\`

## Key Files

- `src/` - Source code
- `tests/` - Test files
- `package.json` - Dependencies

## Conventions

- [Convention 1]
- [Convention 2]
```

## Standard AGENTS.md Template

```markdown
# Project Name

## Overview

Brief description of what this project does and its main purpose.

## Recommended Agents

| Agent | Use For |
|-------|---------|
| [agent-name] | [when to use] |

## Tech Stack

- **Language:** [language]
- **Framework:** [framework]
- **Database:** [database]
- **Deployment:** [platform]

## Key Workflows

### Development
\`\`\`bash
[dev commands]
\`\`\`

### Testing
\`\`\`bash
[test commands]
\`\`\`

### Deployment
\`\`\`bash
[deploy commands]
\`\`\`

## Project Structure

\`\`\`
project/
├── src/           # Source code
├── tests/         # Test files
├── docs/          # Documentation
└── config/        # Configuration
\`\`\`

## Conventions

### Code Style
- [style convention 1]
- [style convention 2]

### Naming
- [naming convention 1]
- [naming convention 2]

### Architecture
- [architecture pattern]
- [key decisions]

## Quick Commands

| Task | Command |
|------|---------|
| Install deps | `npm install` |
| Run dev server | `npm run dev` |
| Run tests | `npm test` |
| Build | `npm run build` |
```

## Comprehensive AGENTS.md Template

```markdown
# Project Name

## Overview

[Detailed project description - what it does, why it exists, who it's for]

## Recommended Agents

### Primary
| Agent | Use For |
|-------|---------|
| [framework-expert] | Main development work |
| [language-expert] | Core language tasks |

### Secondary
| Agent | Use For |
|-------|---------|
| [database-expert] | Data layer tasks |
| [testing-expert] | Test implementation |

### Specialized
| Agent | Use For |
|-------|---------|
| [deployment-expert] | Deployment tasks |
| [security-expert] | Security review |

## Tech Stack

### Core
- **Language:** [language with version]
- **Framework:** [framework with version]
- **Runtime:** [runtime]

### Data
- **Database:** [database]
- **Cache:** [cache system]
- **Queue:** [message queue]

### Infrastructure
- **Hosting:** [platform]
- **CDN:** [cdn]
- **CI/CD:** [ci system]

## Project Structure

\`\`\`
project/
├── src/
│   ├── components/    # UI components
│   ├── services/      # Business logic
│   ├── utils/         # Utilities
│   └── types/         # Type definitions
├── tests/
│   ├── unit/          # Unit tests
│   ├── integration/   # Integration tests
│   └── e2e/           # End-to-end tests
├── docs/              # Documentation
├── scripts/           # Build/deploy scripts
└── config/            # Configuration files
\`\`\`

## Key Workflows

### Local Development

\`\`\`bash
# Initial setup
git clone [repo]
cd [project]
[package manager] install

# Environment
cp .env.example .env
# Edit .env with local settings

# Start development
[dev command]
\`\`\`

### Testing

\`\`\`bash
# Unit tests
[unit test command]

# Integration tests
[integration test command]

# E2E tests
[e2e test command]

# Coverage
[coverage command]
\`\`\`

### Deployment

\`\`\`bash
# Build
[build command]

# Deploy to staging
[staging deploy]

# Deploy to production
[production deploy]
\`\`\`

## Conventions

### Code Style

- **Formatting:** [tool] with [config file]
- **Linting:** [linter] with [rules]
- **Import order:** [order]
- **File naming:** [pattern]

### Git

- **Branch naming:** `[type]/[ticket]-[description]`
- **Commit format:** `[type]: [description]`
- **PR process:** [process]

### Architecture

- **State management:** [pattern]
- **Error handling:** [pattern]
- **API design:** [pattern]
- **Database access:** [pattern]

### Testing

- **Unit test location:** `tests/unit/`
- **Naming:** `test_[function]_[scenario]`
- **Mocking strategy:** [strategy]
- **Coverage target:** [percentage]

## Environment Variables

| Variable | Purpose | Required |
|----------|---------|----------|
| `DATABASE_URL` | Database connection | Yes |
| `API_KEY` | External API key | Yes |
| `DEBUG` | Enable debug mode | No |

## Quick Commands

| Task | Command |
|------|---------|
| Install | `[install]` |
| Dev | `[dev]` |
| Test | `[test]` |
| Lint | `[lint]` |
| Format | `[format]` |
| Build | `[build]` |
| Deploy | `[deploy]` |

## Common Issues

### Issue: [Common problem]
**Solution:** [How to fix]

### Issue: [Another problem]
**Solution:** [How to fix]

## Resources

- [Documentation link]
- [API reference]
- [Related projects]
```

## Consolidation Template

When merging multiple doc files:

```markdown
# Project Name

<!-- Consolidated from: CLAUDE.md, WARP.md -->
<!-- Generated: YYYY-MM-DD -->

## Overview

[Merged overview from all sources]

## Recommended Agents

[Combined agent recommendations]

## Workflows

[Merged workflows, removing duplicates]

## Conventions

[Combined conventions]

<!-- Platform-specific notes -->

### Claude-specific
<!-- Source: CLAUDE.md -->
[Claude-specific instructions]

### Terminal-specific
<!-- Source: WARP.md -->
[Terminal-specific instructions]

---
*Consolidated from multiple documentation files. Originals archived in `.doc-archive/`*
```

## Generation Guidelines

When creating AGENTS.md from project analysis:

1. **Analyze project structure**
   - Check package.json, pyproject.toml, Cargo.toml
   - Identify framework from imports
   - Find test directories

2. **Identify conventions**
   - Check for linter configs (.eslintrc, ruff.toml)
   - Check for formatter configs (prettier, black)
   - Look at existing code patterns

3. **Extract commands**
   - From package.json scripts
   - From Makefile or justfile
   - From README.md

4. **Recommend agents**
   - Based on language/framework
   - Based on project complexity
   - Based on common tasks

5. **Keep it concise**
   - Focus on actionable info
   - Avoid redundancy
   - Update when project evolves
