# Investigation: [Component/Feature Name]

## Summary
[One-paragraph overview of what this is and what it does]

## Location

### Primary Implementation
- `path/to/main-file.ts:42-120` - [Brief description of this file's role]

### Related Files
- `path/to/related.ts:15-30` - [How it relates]
- `path/to/helper.ts:88-95` - [Supporting functionality]

## How It Works

1. **[Step 1 Name]** (`file.ts:42`)
   - [What happens in this step]
   - [Key logic or decision points]

2. **[Step 2 Name]** (`file.ts:67`)
   - [What happens in this step]
   - [Key logic or decision points]

3. **[Step 3 Name]** (`file.ts:95`)
   - [What happens in this step]
   - [Key logic or decision points]

## Key Components

- **[Component Name]**: [Purpose and responsibility]
- **[Component Name]**: [Purpose and responsibility]

## Data Flow

```
[Input] → [Transformation 1] → [Transformation 2] → [Output]
```

Or for more complex flows:
```
User Request
  → Middleware Validation (src/middleware/auth.ts:25)
  → Controller Handler (src/controllers/user.ts:42)
  → Service Logic (src/services/userService.ts:78)
  → Repository Query (src/repositories/userRepo.ts:33)
  → Database
  ← Response Formatting (src/controllers/user.ts:88)
```

## Patterns & Conventions

- [Pattern observed, e.g., "Uses Repository pattern for data access"]
- [Convention used, e.g., "Follows feature-based directory structure"]
- [Design pattern identified, e.g., "Implements Observer pattern for event handling"]

## Implementation Details

### Notable Code
```typescript
// path/to/file.ts:42-55
[Copy interesting or important code snippet here]
// Add explanation of why this code is notable
```

### Design Decisions
- [Why this approach was chosen]
- [Trade-offs made]
- [Alternative approaches considered]

## Architecture

### Component Relationships
```
[Component A] → uses → [Component B]
[Component B] → calls → [Service]
[Service] → queries → [Repository]
```

### Integration Points
- [System/component it integrates with]: [How it integrates]
- [External dependency]: [Purpose and usage]

## Analysis

### Strengths
- [What's well done]
- [Good patterns observed]
- [Quality code or architecture]

### Considerations
- [Potential improvements]
- [Edge cases to note]
- [Complexity areas that might need attention]

### Security/Performance Notes
- [Relevant security considerations]
- [Performance implications]
- [Resource usage patterns]

## Related Components

### Dependencies
- [Component/module it depends on]: [Why it's needed]
- [External package]: [Purpose]

### Dependents
- [What uses this component]: [How they use it]
- [Dependent feature]: [Relationship]

## Usage Examples

### Example 1: [Common usage scenario]
```typescript
// File: path/to/usage.ts:20
[Code showing how this is typically used]
```

### Example 2: [Edge case or special usage]
```typescript
// File: path/to/another-usage.ts:15
[Code showing different usage pattern]
```

## Next Steps

For further investigation:
- [ ] Explore [related area or feature]
- [ ] Trace [specific execution flow]
- [ ] Analyze [related component]
- [ ] Review [relevant documentation]
- [ ] Test [edge case or scenario]

---
*Investigated on: [YYYY-MM-DD]*
*Investigation depth: [quick/medium/thorough]*
*Investigator: Claude (research-agent plugin)*
