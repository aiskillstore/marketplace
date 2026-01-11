# Workflow: Adding Examples to Documentation

**When to use**: Documentation lacks examples or new usage pattern discovered

## Prerequisites

- [ ] Identified sections needing examples
- [ ] Have working code to use as examples

## Steps

### 1. Identify Missing Examples

Read through documentation and note:
- Features without code examples
- Concepts without usage examples
- Commands without output examples
- Patterns without implementation examples

### 2. Write Examples

For each feature/concept:

**Code Example:**
```typescript
// Real, working code
const result = useFeature({
  option: 'value'
});
```

**Command Example:**
```bash
# Real command
command --flag value
```

**Output Example:**
```
Expected output from command
```

### 3. Test Examples

**For code examples:**
1. Copy example code
2. Create test file or paste into existing code
3. Run and verify it works
4. Capture actual output/result

**For command examples:**
1. Run command in terminal
2. Verify it works
3. Copy actual output

### 4. Add to Documentation

**Format:**

```markdown
### Feature Name

Description of feature.

**Example:**
\```typescript
// Example code
const result = useFeature({
  option: 'value'
});
\```

**Result:**
\```
Expected output or behavior
\```

**Location:** source/path/to/file.ts:123
```

### 5. Validate

```bash
# Check file size
wc -l docs/path/to/file.md

# If approaching 500 lines, see split-large-file.md
```

### 6. Commit

```bash
git add docs/path/to/file.md
git commit -m "docs(topic): add usage examples

- Add 5 working code examples
- Include expected outputs
- Add code references
"
```

## Example Types

### 1. Basic Usage

```markdown
### Basic Usage

\```typescript
// Simplest use case
const state = useHomeLogic();
\```
```

### 2. Advanced Usage

```markdown
### Advanced Usage

\```typescript
// Complex configuration
const state = useHomeLogic({
  streaming: true,
  autoSave: true,
  onError: (err) => console.error(err)
});
\```
```

### 3. Common Patterns

```markdown
### Common Pattern: Error Handling

\```typescript
try {
  const result = await api.call();
} catch (error) {
  if (error.code === 'NETWORK_ERROR') {
    // Handle network error
  }
}
\```
```

### 4. CLI Examples

```markdown
### Save Session

\```bash
codeh --save my-session
\```

**Output:**
\```
Session saved to ~/.codeh/sessions/my-session.json
\```
```

### 5. Configuration Examples

```markdown
### Configuration

\```json
{
  "provider": "anthropic",
  "model": "claude-3-5-sonnet",
  "maxTokens": 4096
}
\```
```

## Best Practices

### ✅ DO:

- Use real, working code
- Test every example
- Show expected output/result
- Include code references (file:line)
- Use complete, runnable examples
- Show both input and output

###  DON'T:

- Use pseudo-code or fake examples
- Skip testing examples
- Leave out expected results
- Omit code references
- Use partial, incomplete examples
- Show only input or only output

## Checklist

- [ ] All examples tested and working
- [ ] Examples include expected results
- [ ] Code references added (file:line)
- [ ] Examples are complete and runnable
- [ ] File still under 500 lines
- [ ] Committed changes

## Tips

**For complex examples:**
- Break into steps
- Show intermediate results
- Explain each part

**For error examples:**
- Show the error
- Explain the cause
- Show the fix

**For configuration:**
- Show minimal config
- Show full config
- Explain each option

## Example

See: `docs/screens/home/features.md` for good examples of:
- Slash command usage
- Expected outputs
- Error handling
- Code references
