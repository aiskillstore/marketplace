# README Update Cookbook

Guidelines for updating README.md after code implementation.

## When to Update README

Update README when:
- Adding a new public feature
- Adding or changing public API
- Changing installation instructions
- Changing usage examples
- Adding new dependencies with user impact
- Making breaking changes

Do NOT update README for:
- Internal refactoring
- Bug fixes (unless they change documented behavior)
- Performance improvements
- Test additions
- Documentation-only changes

## README Section Updates

### Features Section

Add new features with a brief, user-focused description:

```markdown
## Features

- **Existing Feature** - Existing description
- **New Feature** - Brief description of what it does and why users care

### New in v2.0
- Feature 1: Description
- Feature 2: Description
```

### Installation Section

Update if new dependencies or requirements are added:

```markdown
## Installation

```bash
pip install mypackage

# New optional dependency for feature X
pip install mypackage[feature-x]
```

### Prerequisites (if changed)

- Python 3.10+ (was 3.9+)
- PostgreSQL 15+ (was 14+)
```

### Usage Section

Update examples when API changes:

```markdown
## Usage

### Basic Usage

```python
from mypackage import Client

# Initialize with new required parameter
client = Client(api_key="your-key", region="us-east-1")

# New method
result = client.new_feature(param="value")
```

### Advanced Usage

```python
# New advanced feature
from mypackage.advanced import AdvancedClient

client = AdvancedClient(config=advanced_config)
```
```

### API Section

Add new public functions/classes:

```markdown
## API Reference

### `new_function(param: str, option: bool = False) -> Result`

Brief description of what the function does.

**Parameters:**
- `param` - Description of the parameter
- `option` - Optional flag to enable X behavior (default: False)

**Returns:**
- `Result` - Description of the return value

**Example:**
```python
result = new_function("input", option=True)
print(result.data)
```

**Raises:**
- `ValueError` - If param is empty
- `ConnectionError` - If service is unavailable
```

### Configuration Section

Update when new configuration options are added:

```markdown
## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `EXISTING_VAR` | `value` | Existing description |
| `NEW_VAR` | `default` | New configuration option for X |

### Configuration File

```yaml
# config.yaml
existing_option: value
new_option: default  # New: enables feature X
```
```

## Breaking Change Documentation

When making breaking changes:

1. Add a prominent notice at the top:

```markdown
> **Breaking Changes in v2.0**: See [Migration Guide](docs/migration.md)
```

2. Update affected examples with before/after:

```markdown
### Migration from v1.x

**Before (v1.x):**
```python
client.old_method(arg1, arg2)
```

**After (v2.0):**
```python
client.new_method(config=Config(arg1=arg1, arg2=arg2))
```
```

3. Add deprecation warnings:

```markdown
> **Deprecated**: `old_function()` will be removed in v3.0. Use `new_function()` instead.
```

## Template for New Feature

```markdown
### Feature Name

Brief description of the feature and its use case.

**Installation** (if additional dependencies):
```bash
pip install mypackage[feature-name]
```

**Quick Start:**
```python
from mypackage import FeatureName

feature = FeatureName(config=Config())
result = feature.run()
```

**Configuration:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `option1` | `str` | `None` | Description |
| `option2` | `bool` | `True` | Description |

**Example Output:**
```json
{
  "status": "success",
  "data": {...}
}
```
```

## README Style Guidelines

1. **Keep it scannable**: Use headers, bullets, and code blocks
2. **Lead with value**: What does this help users do?
3. **Show, don't tell**: Include working examples
4. **Be consistent**: Match existing style in the file
5. **Link to details**: Reference docs/ for deep dives

## Common Mistakes

### Too Much Detail

**Bad:**
```markdown
## Features

- **Authentication** - This feature provides a comprehensive authentication
  system that supports OAuth2, JWT tokens, API keys, and session-based auth
  with configurable expiration, refresh token rotation, and...
```

**Good:**
```markdown
## Features

- **Authentication** - Flexible auth with OAuth2, JWT, and API keys.
  [Learn more](docs/authentication.md)
```

### Missing Examples

**Bad:**
```markdown
## Usage

Use the `process()` function to process data.
```

**Good:**
```markdown
## Usage

```python
from mypackage import process

# Process a single item
result = process({"key": "value"})

# Process in batch
results = process([item1, item2, item3])
```
```

### Outdated Examples

Always verify examples still work after changes:

```bash
# Run README examples
python -m doctest README.md
# Or use pytest with doctest
pytest --doctest-glob="*.md"
```
