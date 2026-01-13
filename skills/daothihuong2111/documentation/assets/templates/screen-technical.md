# Screen Technical Template

Use this for `docs/screens/{screen-name}/technical.md`

**Max Lines**: 500
**Purpose**: Implementation details and code examples

---

```markdown
# {Screen Name} - Technical

## Architecture

### Components

- **Component.tsx**: Main component (Presentation Layer)
- **Presenter.ts**: Business logic (Core Layer)
- **useHook.ts**: State management hook
- **Model.ts**: Domain model (Core Layer)

### Dependencies

\```
Component (CLI)
  ├── useNavigation()
  ├── useCustomHook()
  │   └── Presenter
  │       ├── Service
  │       └── Repository
  └── useKeyboardHook()
\```

## State Management

### State Interface

\```typescript
interface ComponentState {
  field1: Type;
  field2: Type;
  field3: Type;
}
\```

### State Flow

\```
Initial State
  → User Action
  → State Update
  → Re-render
  → New State
\```

## Implementation Details

### Key Functions

\```typescript
function keyFunction(param: Type): ReturnType {
  // Implementation description
  // Reference: path/to/file.ts:line
}
\```

### Event Handling

\```typescript
useInput((input, key) => {
  if (key.return) {
    // Handle Enter
  }
  if (key.escape) {
    // Handle Escape
  }
});
\```

## Validation

### Validation Rules

\```typescript
function validate(value: string): {valid: boolean; error?: string} {
  if (condition) {
    return {valid: false, error: 'Error message'};
  }
  return {valid: true};
}
\```

## Persistence (if applicable)

### Storage Location

Description of where data is stored.

### Format

\```json
{
  "field": "value"
}
\```

## Testing

### Unit Tests

\```typescript
describe('Component', () => {
  test('should do something', () => {
    expect(result).toBe(expected);
  });
});
\```

### Integration Tests

Description of integration test approach.

## Performance

- **Optimization 1**: Description
- **Optimization 2**: Description
- **Metrics**: Key performance metrics

## Security (if applicable)

- **Security consideration 1**: Description
- **Security consideration 2**: Description

## Related Files

- `path/to/file.ts:line` - Description
- `path/to/file.ts:line` - Description
```

---

## Variables

- `{Screen Name}` → Capitalized (e.g., "Home", "Config")

## Sections

**Required:**
- Architecture (Components + Dependencies)
- State Management
- Implementation Details

**Optional:**
- Validation (if applicable)
- Persistence (if applicable)
- Testing (recommended)
- Performance
- Security

## Example

See: `docs/screens/home/technical.md`
