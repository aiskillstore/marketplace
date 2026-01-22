---
title: Rule Title Here
impact: MEDIUM
impactDescription: Optional description of impact (e.g., "reduces flakiness by 80%")
tags: tag1, tag2
---

## Rule Title Here

**Impact: MEDIUM (optional impact description)**

Brief explanation of the rule and why it matters. This should be clear and concise, explaining the stability, performance, or maintainability implications for Playwright tests.

**Incorrect (description of what's wrong):**

```typescript
// Bad code example here
import { test, expect } from '@playwright/test';

test('bad example', async ({ page }) => {
  // Problematic test code
});
```

**Correct (description of what's right):**

```typescript
// Good code example here
import { test, expect } from '@playwright/test';

test('good example', async ({ page }) => {
  // Better test code
});
```

Optional explanatory text after examples. Explain why the correct approach is better, what problems it solves, and any additional considerations.

Reference: [Link to Playwright documentation or resource](https://playwright.dev)