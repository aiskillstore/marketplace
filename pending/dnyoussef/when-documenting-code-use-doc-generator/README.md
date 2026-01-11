# Documentation Generator - Quick Start

> Automated comprehensive code documentation generation with API docs, README files, inline comments, and architecture diagrams.

## What This Skill Does

Automatically generates complete documentation for your codebase:

1. **API Documentation** - OpenAPI, JSDoc, TypeDoc, Python docstrings
2. **README Files** - Comprehensive project documentation
3. **Inline Comments** - Context-aware code comments
4. **Architecture Diagrams** - Visual system documentation
5. **Code Analysis** - Extract structure and dependencies

## Quick Usage

### Generate All Documentation

```bash
# Analyze and generate complete documentation
/doc-generate
```

### Generate Specific Documentation

```bash
# API documentation only
/doc-api

# README generation only
/doc-readme

# Add inline comments to code
/doc-inline
```

## What Gets Generated

### 1. API Documentation (OpenAPI 3.0)

**Before**:
```javascript
app.get('/users/:id', async (req, res) => {
  const user = await db.findUser(req.params.id);
  res.json(user);
});
```

**After**:
```yaml
# docs/api.yml
paths:
  /users/{id}:
    get:
      summary: Get user by ID
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: User found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
```

### 2. Inline Comments (JSDoc)

**Before**:
```javascript
function calculateTotal(items, tax) {
  return items.reduce((sum, item) => sum + item.price, 0) * (1 + tax);
}
```

**After**:
```javascript
/**
 * Calculates the total price of items including tax
 *
 * @param {Array<{price: number}>} items - Array of items with prices
 * @param {number} tax - Tax rate as decimal (e.g., 0.08 for 8%)
 * @returns {number} Total price including tax
 *
 * @example
 * const total = calculateTotal([{price: 10}, {price: 20}], 0.08);
 * // Returns: 32.4 (30 * 1.08)
 */
function calculateTotal(items, tax) {
  // Sum all item prices
  return items.reduce((sum, item) => sum + item.price, 0) * (1 + tax);
}
```

### 3. README Generation

**Generated Structure**:
```markdown
# Project Name

> One-sentence description

## Features
- Key feature list

## Quick Start
### Prerequisites
### Installation
### Usage

## API Documentation
Links to generated docs

## Architecture
Diagrams and design docs

## Contributing
Guidelines

## License
```

### 4. Architecture Diagrams

**Generated**: SVG diagrams showing:
- System architecture overview
- Data flow diagrams
- API endpoint structure
- Component relationships

## Installation

This skill is already configured in your Claude Code environment at:
```
~/.claude/skills/documentation/when-documenting-code-use-doc-generator/
```

## Commands Available

| Command | Description | Output |
|---------|-------------|--------|
| `/doc-generate` | Generate all documentation | Complete doc set |
| `/doc-api` | API documentation only | OpenAPI spec |
| `/doc-readme` | README generation | README.md |
| `/doc-inline` | Add code comments | Updated source files |

## Configuration

### Set Documentation Standards

```javascript
// .claude/config/docs.json
{
  "commentStyle": "jsdoc",        // jsdoc, tsdoc, google, numpy
  "apiFormat": "openapi3",        // openapi3, swagger2, raml
  "diagramFormat": "svg",         // svg, png, pdf
  "minCoverage": 80,              // Minimum % coverage
  "includeExamples": true,        // Add usage examples
  "generateDiagrams": true        // Create architecture diagrams
}
```

## Project Structure

After running documentation generation:

```
project/
├── docs/
│   ├── API.md                  # API reference
│   ├── ARCHITECTURE.md         # System design
│   ├── api.yml                 # OpenAPI specification
│   └── diagrams/
│       ├── system-overview.svg
│       ├── data-flow.svg
│       └── api-structure.svg
├── README.md                   # Updated project README
└── src/                        # Source files with updated comments
```

## Documentation Standards

### Function Documentation

Every public function should have:
- ✅ Brief description (one sentence)
- ✅ Parameter documentation with types
- ✅ Return value documentation
- ✅ At least one usage example
- ✅ Error/exception documentation

### README Requirements

Every project should have:
- ✅ Clear title and description
- ✅ Feature list
- ✅ Installation instructions
- ✅ Quick start guide
- ✅ API documentation link
- ✅ Contributing guidelines
- ✅ License information

### API Documentation

Every endpoint should have:
- ✅ Endpoint path and method
- ✅ Request parameters
- ✅ Request body schema
- ✅ Response schemas (all status codes)
- ✅ Authentication requirements
- ✅ Example requests/responses

## Quality Metrics

The skill tracks documentation coverage:

```
Documentation Coverage Report:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Public Functions:     95% (38/40)
Internal Functions:   82% (65/79)
Type Definitions:     100% (12/12)
API Endpoints:        100% (15/15)
Examples:            85% (34/40)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Overall Coverage:     88%
Target:              80%
Status:              ✅ PASS
```

## Workflow Integration

### Pre-commit Hook

```bash
# Validate documentation before commit
npm run docs:validate

# Auto-generate docs on commit
npm run docs:generate
```

### CI/CD Integration

```yaml
# .github/workflows/docs.yml
- name: Generate documentation
  run: npm run docs:generate

- name: Validate coverage
  run: npm run docs:coverage --min 80

- name: Deploy to GitHub Pages
  run: npm run docs:deploy
```

## Examples

### Example 1: Document Express API

```bash
# Generate API documentation for Express server
/doc-api

# Output:
# - docs/api.yml (OpenAPI 3.0 spec)
# - docs/API.md (Human-readable reference)
# - Swagger UI at /api-docs
```

### Example 2: Add Missing Comments

```bash
# Analyze and add inline comments
/doc-inline

# Adds JSDoc to all public functions
# Adds inline comments to complex logic
# Updates type definitions
```

### Example 3: Complete Project Documentation

```bash
# Generate everything
/doc-generate

# Creates:
# - README.md
# - docs/API.md
# - docs/ARCHITECTURE.md
# - docs/diagrams/*.svg
# - Updated inline comments
```

## Supported Languages

- ✅ JavaScript (JSDoc)
- ✅ TypeScript (TSDoc)
- ✅ Python (Google/NumPy style)
- ✅ Java (JavaDoc)
- ✅ C# (XML comments)
- ✅ Go (GoDoc)
- ✅ Rust (RustDoc)

## Troubleshooting

### Issue: Comments not appearing in IDE

**Solution**: Configure your IDE to show JSDoc/TSDoc comments:
```json
// VSCode settings.json
{
  "javascript.suggest.completeFunctionCalls": true,
  "typescript.suggest.completeFunctionCalls": true
}
```

### Issue: Diagrams not rendering

**Solution**: Install Graphviz:
```bash
# macOS
brew install graphviz

# Ubuntu/Debian
sudo apt install graphviz

# Windows
choco install graphviz
```

### Issue: API docs missing endpoints

**Solution**: Ensure routes are properly exported and use standard Express/FastAPI patterns.

## Best Practices

1. **Document as you code** - Don't defer documentation
2. **Keep comments concise** - Explain "why" not "what"
3. **Use examples** - Show real usage patterns
4. **Update diagrams** - Keep architecture docs current
5. **Validate before commit** - Use pre-commit hooks
6. **Review documentation** - Treat docs as first-class code

## Related Skills

- `code-review-assistant` - Reviews documentation in PRs
- `api-design-first` - Creates API docs from specs
- `refactoring-assistant` - Updates docs during refactoring

## Resources

- [JSDoc Documentation](https://jsdoc.app/)
- [OpenAPI Specification](https://swagger.io/specification/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Markdown Guide](https://www.markdownguide.org/)

## Support

For issues or questions:
1. Check [PROCESS.md](PROCESS.md) for detailed workflows
2. Review [SKILL.md](SKILL.md) for complete SOP
3. Examine generated documentation for patterns

---

**Version**: 1.0.0
**Last Updated**: 2025-10-30
