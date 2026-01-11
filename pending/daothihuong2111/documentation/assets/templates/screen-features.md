# Screen Features Template

Use this for `docs/screens/{screen-name}/features.md`

**Max Lines**: 400
**Purpose**: Detailed feature documentation
**When to Use**: Screen has 5+ complex features

---

```markdown
# {Screen Name} - Features

Detailed documentation of all features.

## Feature 1: Name

### Description

Detailed description of what this feature does.

### Usage

\```
Step-by-step usage example
\```

### Configuration

| Option     | Type   | Default | Description |
|------------|--------|---------|-------------|
| option1    | string | 'value' | Description |

### Examples

#### Example 1: Common Use Case

\```typescript
// Code example
\```

**Result**: Description of result

#### Example 2: Advanced Use Case

\```typescript
// Code example
\```

**Result**: Description of result

### Error Handling

| Error              | Cause            | Solution        |
|--------------------|------------------|-----------------|
| Error message      | What causes it   | How to fix      |

### Implementation

Brief technical note about implementation.

Reference: path/to/file.ts:line

---

## Feature 2: Name

[Repeat structure above for each feature]

---

## Feature Comparison

| Feature    | Screen 1 | Screen 2 | Notes      |
|------------|----------|----------|------------|
| Feature A  | ✅       |        | Note       |
| Feature B  | ✅       | ✅       | Note       |

## Future Enhancements

- [ ] Potential feature 1
- [ ] Potential feature 2
```

---

## Per-Feature Structure

Each feature should include:

1. **Description** - What it does
2. **Usage** - How to use it
3. **Examples** - At least 1-2 examples
4. **Error Handling** - Common errors (if applicable)
5. **Implementation Reference** - Code location

## Example

See: `docs/screens/home/features.md`
