---
title: Rule Title Here
impact: MEDIUM
impactDescription: Optional description of impact (e.g., "reduces flakiness by 80%")
tags: tag1, tag2
---

## Rule Title Here

**Impact: MEDIUM (optional impact description)**

Brief explanation of the rule and why it matters. This should be clear and concise, explaining the stability, performance, or maintainability implications for Playwright tests.

## When to Use

Clear, structured guidance on when this rule applies:

- **Use this approach when**: Specific scenarios where this rule should be applied
- **Consider alternatives when**: Scenarios where other approaches might be better
- **Required for**: Specific project types, test scales, or team structures

## Guidelines

Formal do's and don'ts for implementing this best practice:

### Do

- Specific action or pattern to follow
- Another recommended practice
- Additional guidance point

### Don't

- Specific pattern or approach to avoid
- Another anti-pattern
- Common mistake to prevent

### Tool Usage Patterns

When applicable, describe which Playwright tools and APIs to use:

- **Primary tools**: List of recommended Playwright methods/APIs
- **Configuration**: Any playwright.config.ts settings that support this rule
- **Helper utilities**: Custom utilities or patterns that support this approach

## Edge Cases and Constraints

### Limitations

Describe constraints or limitations of this approach:

- Known limitation or boundary condition
- Performance considerations at scale
- Browser or environment-specific constraints

### Edge Cases

Document specific edge cases and how to handle them:

1. **Edge case name**: Description and handling approach
2. **Another edge case**: Description and solution
3. **Complex scenario**: Detailed handling instructions

### What Breaks If Ignored

Explicit consequences of not following this rule:

- Specific failure mode or problem
- Performance degradation or flakiness impact
- Maintenance or debugging challenges

**Incorrect (description of what's wrong):**

```typescript
// Bad code example here
import { test, expect } from '@playwright/test';

test('bad example', async ({ page }) => {
  // Problematic test code
  // Include comments explaining why this is problematic
});
```

**Why this fails:**
- Specific reason why this approach is incorrect
- Potential errors or flakiness introduced
- Impact on test reliability or maintainability

**Correct (description of what's right):**

```typescript
// Good code example here
import { test, expect } from '@playwright/test';

test('good example', async ({ page }) => {
  // Better test code
  // Include comments explaining why this works better
});
```

**Why this works:**
- Specific benefit of this approach
- How it improves reliability, performance, or maintainability
- Additional advantages

## Common Mistakes

Beyond the main incorrect example, document other common mistakes:

### Mistake 1: [Name]

```typescript
// Example of this mistake
test('mistake example', async ({ page }) => {
  // Problematic pattern
});
```

**Why this is wrong**: Explanation of the issue

**How to fix**: 

```typescript
// Corrected version
test('fixed example', async ({ page }) => {
  // Correct pattern
});
```

### Mistake 2: [Name]

Similar structure for additional common mistakes.

## Advanced Patterns

Optional section for advanced usage, complex scenarios, or integration with other best practices.

```typescript
// Advanced example showing sophisticated usage
import { test, expect } from '@playwright/test';

test('advanced example', async ({ page }) => {
  // Sophisticated test implementation
  // Demonstrates complex scenarios or optimizations
});
```

**When to use this pattern**: Guidance on when advanced patterns are appropriate

## Integration with Other Best Practices

How this rule combines with other best practices:

- **Rule X**: How these practices work together
- **Rule Y**: Interaction considerations
- **Scale considerations**: How this scales with other practices (e.g., 100+ tests)

## Expected Input/Output

For complex patterns, document expected behavior:

**Input scenario**: Description of test scenario or context

**Expected outcome**: What should happen when following this rule correctly

**Failure scenario**: What happens when rule is violated

**Expected error**: Specific error messages or behaviors in failure cases

## Examples at Scale

Real-world scale considerations:

```typescript
// Example showing pattern at larger scale
// E.g., 100+ tests, 50+ page objects, complex CI/CD pipeline
```

Reference: [Link to Playwright documentation or resource](https://playwright.dev)
