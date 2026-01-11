---
name: pr-template-generator
description: Generate comprehensive pull request descriptions that help reviewers understand changes quickly a...
---

# PR Template Generator Skill

Generate comprehensive pull request descriptions that help reviewers understand changes quickly and improve team collaboration.

## Instructions

You are a pull request documentation expert. When invoked:

1. **Analyze Changes**:
   - Review git diff and commit history
   - Identify type of changes (feature, bugfix, refactor, etc.)
   - Understand the scope and impact
   - Detect breaking changes
   - Identify affected components

2. **Generate PR Description**:
   - Clear, concise title following conventions
   - Comprehensive summary of changes
   - Motivation and context
   - Technical approach and decisions
   - Testing strategy
   - Deployment considerations

3. **Include Checklist**:
   - Pre-merge requirements
   - Testing verification
   - Documentation updates
   - Breaking change warnings
   - Migration steps if needed

4. **Add Metadata**:
   - Related issues and tickets
   - Type labels (feature, bugfix, etc.)
   - Priority and urgency
   - Required reviewers
   - Estimated review time

5. **Communication Tips**:
   - Use clear, non-technical language where possible
   - Highlight reviewer focus areas
   - Include screenshots/recordings for UI changes
   - Link to relevant documentation
   - Explain trade-offs and alternatives considered

## PR Title Conventions

### Format Patterns

```
# Conventional Commits Style
feat: Add user profile page
fix: Resolve login redirect issue
refactor: Simplify authentication logic
docs: Update API documentation
test: Add integration tests for checkout
chore: Update dependencies
perf: Optimize database queries
style: Fix linting issues

# With Scope
feat(auth): Add OAuth2 provider support
fix(api): Handle null responses correctly
refactor(database): Migrate to connection pooling

# With Ticket Reference
feat: Add export functionality [JIRA-123]
fix: Memory leak in websocket handler (#456)

# Breaking Changes
feat!: Migrate to v2 API endpoints
refactor!: Remove deprecated methods
```

### Title Best Practices

```
✅ GOOD Titles:
- feat: Add real-time notification system
- fix: Prevent duplicate order submissions
- refactor: Extract payment processing logic
- perf: Reduce initial page load time by 40%

❌ BAD Titles:
- Update code
- Fix bug
- Changes
- WIP
- asdfasdf
```

## PR Description Templates

### Feature Addition Template

```markdown
## Summary

This PR adds a comprehensive notification system that allows users to receive real-time updates about order status, messages, and system alerts.

## Motivation

**Problem**: Users currently have no way to receive updates about important events without refreshing the page or checking email. This leads to delayed responses and poor user experience.

**Solution**: Implement a WebSocket-based notification system with persistent storage, allowing users to:
- Receive real-time notifications
- View notification history
- Mark notifications as read
- Configure notification preferences

## Changes

### Added
- WebSocket server for real-time notifications (`src/websocket/`)
- Notification service and database schema (`src/models/Notification.js`)
- Frontend notification component with toast UI
- User notification preferences page
- Email fallback for offline users

### Modified
- Updated `User` model to include notification settings
- Enhanced authentication middleware to support WebSocket connections
- Modified dashboard to display notification bell icon

### Removed
- Old polling-based notification checker (deprecated)

## Technical Details

### Architecture
```
Client (React) <--WebSocket--> Server (Node.js) <--> Redis Pub/Sub <--> Database
```

### Key Implementation Decisions
1. **WebSocket vs. Server-Sent Events**: Chose WebSocket for bidirectional communication
2. **Redis Pub/Sub**: Enables horizontal scaling across multiple server instances
3. **Persistent Storage**: MongoDB for notification history (7-day retention)
4. **Email Fallback**: Queue-based email notifications for offline users

### Database Schema
```javascript
{
  userId: ObjectId,
  type: String,           // 'order', 'message', 'system'
  title: String,
  message: String,
  data: Object,           // Type-specific payload
  read: Boolean,
  createdAt: Date,
  expiresAt: Date        // TTL index for auto-cleanup
}
```

## Testing

### Unit Tests
- [x] Notification service (create, mark read, delete)
- [x] WebSocket connection handling
- [x] User preferences validation
- [x] Email fallback queue

### Integration Tests
- [x] End-to-end notification flow
- [x] Real-time delivery verification
- [x] Reconnection after disconnect
- [x] Multi-device synchronization

### Manual Testing
- [x] Tested in Chrome, Firefox, Safari
- [x] Mobile responsiveness verified
- [x] Tested with 100+ concurrent connections
- [x] Verified email fallback with offline users

## Screenshots

### Notification Toast
![Notification Toast](https://example.com/screenshots/toast.png)

### Notification Center
![Notification Center](https://example.com/screenshots/center.png)

### Settings Page
![Settings](https://example.com/screenshots/settings.png)

## Performance Impact

- WebSocket connection: ~5KB per user
- Redis memory: ~1MB per 10,000 notifications
- Database: 200 writes/sec tested (current load: 10/sec)
- Client bundle: +15KB gzipped

## Breaking Changes

None - This is a new feature with no breaking changes to existing APIs.

## Migration Guide

No migration needed. New notifications table will be created automatically via migration:

```bash
npm run migrate:latest
```

## Deployment Notes

### Prerequisites
- Redis server required (update docker-compose.yml included)
- Environment variables (see `.env.example`)
- Run database migration before deployment

### Configuration
```bash
REDIS_URL=redis://localhost:6379
WEBSOCKET_PORT=3001
NOTIFICATION_RETENTION_DAYS=7
EMAIL_FALLBACK_ENABLED=true
```

### Rollout Strategy
1. Deploy Redis infrastructure
2. Run database migrations
3. Deploy backend (rolling deployment)
4. Deploy frontend (feature flag enabled)
5. Monitor error rates and WebSocket connections
6. Gradual rollout: 10% → 50% → 100% over 3 days

## Documentation

- [x] API documentation updated
- [x] User guide created
- [x] WebSocket protocol documented
- [x] Troubleshooting guide added

## Dependencies

### New Dependencies
- `ws` (^8.0.0) - WebSocket library
- `ioredis` (^5.0.0) - Redis client
- `socket.io-client` (^4.0.0) - Frontend WebSocket client

### Security Audit
All new dependencies scanned with `npm audit` - no vulnerabilities found.

## Checklist

### Before Review
- [x] Code follows project style guidelines
- [x] All tests passing (unit + integration)
- [x] No console.log statements in production code
- [x] Documentation updated
- [x] Accessibility tested (keyboard navigation, screen readers)
- [x] Error handling implemented
- [x] Logging added for debugging

### Reviewer Focus Areas
- 🔍 **Security**: WebSocket authentication and authorization
- 🔍 **Performance**: Connection scaling and memory usage
- 🔍 **Error Handling**: Reconnection logic and edge cases
- 🔍 **UX**: Notification UI and user preferences

### Post-Merge
- [ ] Monitor error rates in production
- [ ] Verify WebSocket connection stability
- [ ] Check Redis memory usage
- [ ] Gather user feedback on notification UX

## Related Issues

Closes #234
Related to #189, #201

## Reviewers

- @backend-team (WebSocket and Redis implementation)
- @frontend-team (UI components and state management)
- @qa-team (Testing strategy verification)

**Estimated Review Time**: 30-45 minutes

## Additional Notes

- Feature flag: `ENABLE_NOTIFICATIONS` (default: false)
- Backwards compatible with existing systems
- Can be disabled without affecting core functionality
- Monitoring dashboard: `/admin/notifications/stats`

## Questions for Reviewers

1. Should we add rate limiting per user for notification creation?
2. Is 7-day retention sufficient, or should we increase it?
3. Should we add push notifications (PWA) in this PR or separate?

## Follow-up Tasks

- [ ] Add push notification support (PWA) - Ticket #245
- [ ] Implement notification grouping/bundling - Ticket #246
- [ ] Add notification analytics dashboard - Ticket #247
- [ ] Create notification templates system - Ticket #248
```

### Bug Fix Template

```markdown
## Summary

Fixes a critical bug where users were unable to submit orders when using discount codes that exceeded the order total, resulting in negative final amounts.

## Issue

**Bug Description**: When users applied discount codes worth more than their cart total, the checkout process would fail silently, leaving users unable to complete their purchase.

**Impact**:
- Severity: HIGH
- Affected Users: ~500 users/day
- Revenue Impact: Estimated $2,000/day in lost sales
- First Reported: 2024-01-10
- Browser: All browsers
- Environment: Production only

**Error Message**:
```
ValidationError: Order total cannot be negative
  at OrderService.validate (src/services/OrderService.js:45)
```

## Root Cause

The discount validation logic in `OrderService.calculateTotal()` was checking for negative amounts AFTER applying the discount, but before the minimum order total constraint was applied.

```javascript
// ❌ BEFORE (Buggy Code)
const subtotal = calculateSubtotal(items);
const discountAmount = calculateDiscount(subtotal, discountCode);
const total = subtotal - discountAmount;

if (total < 0) {
  throw new ValidationError('Order total cannot be negative');
}

// Minimum order total check never reached
```

The issue occurred because:
1. Discount validation happened in wrong order
2. No cap on discount amount vs. order total
3. Frontend didn't validate before submission
4. Error message wasn't user-friendly

## Solution

### Backend Changes

```javascript
// ✅ AFTER (Fixed Code)
const subtotal = calculateSubtotal(items);
const discountAmount = calculateDiscount(subtotal, discountCode);

// Cap discount at subtotal amount
const cappedDiscount = Math.min(discountAmount, subtotal);
const total = Math.max(subtotal - cappedDiscount, 0);

// Ensure minimum order value if needed
if (total > 0 && total < MINIMUM_ORDER_TOTAL) {
  throw new ValidationError(
    `Order total must be at least $${MINIMUM_ORDER_TOTAL}`
  );
}
```

### Frontend Changes

Added client-side validation to prevent invalid submissions:
- Check discount vs. cart total before submission
- Display warning when discount exceeds total
- Show final amount preview
- Improved error messaging

## Testing

### Reproduction Steps (Before Fix)
1. Add item to cart ($10)
2. Apply discount code worth $15
3. Proceed to checkout
4. Click "Place Order"
5. ❌ Order fails with validation error

### Verification Steps (After Fix)
1. Add item to cart ($10)
2. Apply discount code worth $15
3. ✅ Discount capped at $10 (free order)
4. Proceed to checkout
5. ✅ Order succeeds with $0 total

### Test Cases Added

```javascript
describe('Order Discount Validation', () => {
  it('should cap discount at subtotal amount', () => {
    const order = { subtotal: 50, discount: 75 };
    const total = calculateTotal(order);
    expect(total).toBe(0);
  });

  it('should allow discounts equal to subtotal', () => {
    const order = { subtotal: 100, discount: 100 };
    const total = calculateTotal(order);
    expect(total).toBe(0);
  });

  it('should apply partial discounts correctly', () => {
    const order = { subtotal: 100, discount: 25 };
    const total = calculateTotal(order);
    expect(total).toBe(75);
  });

  it('should handle percentage discounts', () => {
    const order = { subtotal: 100, discountPercent: 150 };
    const total = calculateTotal(order);
    expect(total).toBe(0); // Capped at 100%
  });
});
```

### Regression Testing
- [x] Normal discount codes (under total)
- [x] Exact match discount codes
- [x] Excessive discount codes (over total)
- [x] Multiple discount codes
- [x] Expired discount codes
- [x] Invalid discount codes
- [x] Free shipping combinations
- [x] Tax calculations with discounts

## Changes Made

### Modified Files
- `src/services/OrderService.js` - Fixed discount calculation logic
- `src/validators/OrderValidator.js` - Added discount amount validation
- `src/controllers/OrderController.js` - Improved error messages
- `client/src/components/Checkout.jsx` - Added client-side validation
- `client/src/utils/priceCalculator.js` - Frontend discount preview

### Tests Added
- `tests/unit/OrderService.test.js` - Discount edge cases
- `tests/integration/checkout.test.js` - End-to-end checkout flow

## Deployment Plan

### Pre-Deployment
- [x] Notify customer support team about fix
- [x] Prepare FAQ for users who encountered issue
- [x] Database cleanup script for failed orders (if needed)

### Deployment
- Low-risk deployment (backwards compatible)
- No database migrations required
- Can be deployed during business hours
- Estimated downtime: 0 minutes (rolling deployment)

### Post-Deployment Monitoring
- Monitor order success rate (expect 2-3% increase)
- Track discount code usage patterns
- Alert on validation errors
- Customer support ticket volume

### Rollback Plan
If issues detected:
```bash
git revert <commit-hash>
npm run deploy:production
```

## Checklist

- [x] Bug reproduced and documented
- [x] Root cause identified
- [x] Fix implemented and tested
- [x] Unit tests added
- [x] Integration tests added
- [x] Manual testing completed
- [x] Edge cases covered
- [x] Error messages improved
- [x] Documentation updated
- [x] Customer support notified

## Related Issues

Fixes #312
Related to #298 (discount validation improvements)

## Additional Notes

### Future Improvements
- Add admin alert for excessive discount codes
- Implement discount code usage analytics
- Consider A/B testing discount UI improvements

### Known Limitations
- Does not address stacking multiple discount codes (separate issue #315)
- Minimum order total validation could be improved (tracked in #316)
```

### Refactoring Template

```markdown
## Summary

Refactors the payment processing module to improve code maintainability, testability, and separation of concerns. No functional changes or breaking changes.

## Motivation

The current payment processing code has become difficult to maintain due to:
- Multiple payment providers mixed in single file (~1,200 lines)
- Tight coupling between business logic and provider APIs
- Difficult to test (requires mocking multiple external services)
- Code duplication across payment methods
- Hard to add new payment providers

**Technical Debt**: This refactoring addresses item #45 in our technical debt register.

## Refactoring Goals

1. **Separation of Concerns**: Extract provider-specific logic
2. **Testability**: Enable mocking and unit testing
3. **Maintainability**: Reduce file size and complexity
4. **Extensibility**: Make adding new providers easier
5. **Type Safety**: Add TypeScript interfaces

## Changes Overview

### Before (Problematic Structure)
```
src/services/
  └── PaymentService.js (1,200 lines)
      ├── Stripe logic
      ├── PayPal logic
      ├── Square logic
      └── Common logic (mixed)
```

### After (Improved Structure)
```
src/services/payment/
  ├── PaymentService.js (200 lines)      // Orchestration layer
  ├── PaymentProvider.interface.ts       // Provider contract
  ├── providers/
  │   ├── StripeProvider.js (150 lines)
  │   ├── PayPalProvider.js (180 lines)
  │   └── SquareProvider.js (160 lines)
  ├── utils/
  │   ├── currencyConverter.js
  │   └── paymentValidator.js
  └── tests/
      ├── PaymentService.test.js
      └── providers/
          ├── StripeProvider.test.js
          ├── PayPalProvider.test.js
          └── SquareProvider.test.js
```

## Technical Details

### Payment Provider Interface

```typescript
interface PaymentProvider {
  // Provider identification
  readonly name: string;
  readonly supportedCurrencies: string[];

  // Core payment operations
  createPaymentIntent(amount: number, currency: string, metadata?: object): Promise<PaymentIntent>;
  capturePayment(paymentId: string): Promise<PaymentResult>;
  refundPayment(paymentId: string, amount?: number): Promise<RefundResult>;

  // Customer management
  createCustomer(customerData: CustomerData): Promise<Customer>;
  attachPaymentMethod(customerId: string, paymentMethodId: string): Promise<void>;

  // Webhooks
  verifyWebhookSignature(payload: string, signature: string): boolean;
  handleWebhookEvent(event: WebhookEvent): Promise<void>;
}
```

### Refactored Service Layer

```javascript
// ✅ AFTER: Clean orchestration
class PaymentService {
  constructor() {
    this.providers = {
      stripe: new StripeProvider(config.stripe),
      paypal: new PayPalProvider(config.paypal),
      square: new SquareProvider(config.square)
    };
  }

  async processPayment(orderId, paymentMethod, amount, currency) {
    const provider = this.getProvider(paymentMethod);

    try {
      // Business logic
      const order = await this.validateOrder(orderId);
      const convertedAmount = await this.convertCurrency(amount, currency);

      // Delegate to provider
      const result = await provider.createPaymentIntent(
        convertedAmount,
        currency,
        { orderId, customerId: order.customerId }
      );

      // Store transaction
      await this.saveTransaction(orderId, result);

      return result;
    } catch (error) {
      await this.handlePaymentError(error, orderId);
      throw error;
    }
  }

  getProvider(method) {
    const provider = this.providers[method];
    if (!provider) {
      throw new Error(`Unsupported payment method: ${method}`);
    }
    return provider;
  }
}
```

## Benefits

### Improved Testability

```javascript
// ✅ Easy to mock providers
describe('PaymentService', () => {
  it('should process payment with selected provider', async () => {
    const mockProvider = {
      createPaymentIntent: jest.fn().mockResolvedValue({ id: '123' })
    };

    const service = new PaymentService();
    service.providers.stripe = mockProvider;

    await service.processPayment('order-1', 'stripe', 100, 'USD');

    expect(mockProvider.createPaymentIntent).toHaveBeenCalledWith(
      100,
      'USD',
      expect.objectContaining({ orderId: 'order-1' })
    );
  });
});
```

### Reduced Complexity

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Cyclomatic Complexity | 45 | 8 | 82% ↓ |
| Lines of Code (main file) | 1,200 | 200 | 83% ↓ |
| Test Coverage | 45% | 87% | 93% ↑ |
| Number of Files | 1 | 12 | Better organization |

### Easier to Extend

Adding a new payment provider now requires:

```javascript
// 1. Create new provider class
class NewProvider implements PaymentProvider {
  // Implement interface methods
}

// 2. Register in service
this.providers.newprovider = new NewProvider(config);

// That's it! No changes to existing code.
```

## Testing

### Test Coverage

- [x] All existing tests still passing (100% backwards compatible)
- [x] New unit tests for each provider (87% coverage)
- [x] Integration tests for payment flows
- [x] Error handling scenarios
- [x] Provider switching logic

### Regression Testing

Extensive testing performed:
- [x] All payment methods tested in staging
- [x] Refund flows verified
- [x] Webhook handling tested
- [x] Currency conversion edge cases
- [x] Error scenarios and retries

## Migration Notes

### Backwards Compatibility

✅ **100% backwards compatible**

All existing API interfaces remain unchanged:
```javascript
// Old code still works
paymentService.processPayment(orderId, 'stripe', 100, 'USD');
```

### Database Changes

None required - this is purely code reorganization.

### Configuration Changes

Optional: New config structure (old structure still supported):

```javascript
// New recommended structure
{
  payment: {
    providers: {
      stripe: { apiKey: '...', webhookSecret: '...' },
      paypal: { clientId: '...', clientSecret: '...' },
      square: { accessToken: '...', locationId: '...' }
    }
  }
}
```

## Code Quality Improvements

### ESLint Results
- Before: 47 warnings, 12 errors
- After: 0 warnings, 0 errors

### Type Safety
- Added TypeScript interfaces for all provider contracts
- Improved IntelliSense and autocomplete
- Compile-time error detection

### Documentation
- [x] JSDoc comments added to all public methods
- [x] README updated with new architecture
- [x] Provider implementation guide created
- [x] Migration guide for future providers

## Performance Impact

### Benchmarks

No performance regression detected:

| Operation | Before | After | Change |
|-----------|--------|-------|--------|
| Payment creation | 245ms | 242ms | -1.2% |
| Refund processing | 180ms | 178ms | -1.1% |
| Webhook handling | 95ms | 93ms | -2.1% |

Bundle size impact:
- Main bundle: +2KB (0.1% increase)
- Code splitting enabled: Individual provider modules loaded on demand

## Deployment Plan

### Risk Assessment
- **Risk Level**: LOW (refactoring only, no business logic changes)
- **Rollback Complexity**: Easy (git revert)
- **Testing Coverage**: High (87% test coverage)

### Deployment Strategy
1. Deploy to staging environment
2. Run full regression test suite
3. Monitor for 24 hours
4. Deploy to production (rolling deployment)
5. Monitor payment success rates

### Monitoring
- Track payment success/failure rates
- Monitor provider-specific metrics
- Alert on any regression in processing times

## Checklist

- [x] All existing tests pass
- [x] New tests added (87% coverage)
- [x] Code review completed
- [x] No functional changes
- [x] Performance benchmarked (no regression)
- [x] Documentation updated
- [x] Type definitions added
- [x] ESLint/Prettier applied
- [x] Backwards compatible

## Future Work

This refactoring enables:
- [ ] Add Google Pay provider (#401)
- [ ] Implement payment retry logic (#402)
- [ ] Add payment analytics dashboard (#403)
- [ ] Optimize currency conversion caching (#404)

## Related Issues

Addresses technical debt item #45
Related to #389 (payment provider abstraction discussion)

## Review Notes

**Focus Areas for Reviewers**:
- Architecture and design patterns
- Provider interface completeness
- Test coverage and scenarios
- Migration path for new providers

**Estimated Review Time**: 45-60 minutes (larger refactor)
```

## Usage Examples

```
@pr-template-generator
@pr-template-generator --type feature
@pr-template-generator --type bugfix
@pr-template-generator --type refactor
@pr-template-generator --include-screenshots
@pr-template-generator --minimal
```

## PR Description Checklist

### Essential Elements
- [ ] Clear title following conventions
- [ ] Summary of changes (what and why)
- [ ] Type of change (feature, bugfix, refactor, etc.)
- [ ] Testing performed
- [ ] Breaking changes documented
- [ ] Related issues linked

### Context and Motivation
- [ ] Problem statement
- [ ] Why this approach was chosen
- [ ] Alternatives considered
- [ ] Impact on users/system
- [ ] Business value delivered

### Technical Details
- [ ] Architecture changes explained
- [ ] Key implementation decisions documented
- [ ] Database schema changes (if any)
- [ ] API changes (if any)
- [ ] Performance implications

### Testing and Quality
- [ ] Unit test coverage
- [ ] Integration tests
- [ ] Manual testing steps
- [ ] Edge cases considered
- [ ] Regression testing performed

### Documentation
- [ ] Code comments added
- [ ] API docs updated
- [ ] User documentation updated
- [ ] README changes (if needed)
- [ ] Migration guide (if needed)

### Deployment
- [ ] Deployment plan outlined
- [ ] Configuration changes documented
- [ ] Environment variables updated
- [ ] Migration scripts included
- [ ] Rollback plan defined

### Visual Changes
- [ ] Screenshots included
- [ ] Before/after comparisons
- [ ] Mobile screenshots
- [ ] Accessibility tested
- [ ] Browser compatibility verified

### Collaboration
- [ ] Specific reviewers assigned
- [ ] Review focus areas highlighted
- [ ] Questions for reviewers listed
- [ ] Estimated review time provided
- [ ] Related team members tagged

## Best Practices

### Writing Clear Descriptions

**DO**:
- Use bullet points for easy scanning
- Include code examples for complex changes
- Add visual aids (screenshots, diagrams, recordings)
- Explain the "why" not just the "what"
- Be specific about impacts and trade-offs
- Link to relevant documentation
- Call out areas needing extra attention

**DON'T**:
- Use vague descriptions ("updated code", "fixed stuff")
- Assume reviewers have full context
- Skip testing information
- Forget to link related issues
- Ignore breaking changes
- Rush the description
- Use jargon without explanation

### For Reviewers

Help reviewers by:
- Estimating review time
- Highlighting complex areas
- Providing test accounts/data if needed
- Including step-by-step testing guide
- Asking specific questions
- Explaining non-obvious decisions

### For Complex PRs

For large or complex PRs:
- Break into smaller PRs when possible
- Provide architecture diagrams
- Record video walkthrough
- Schedule synchronous review session
- Create detailed testing guide
- Explain migration strategy thoroughly

## Communication Tips

### Tone and Style
- Be clear and concise
- Use active voice
- Be respectful and collaborative
- Acknowledge uncertainty
- Ask for feedback
- Explain trade-offs objectively

### Screenshots and Videos

When to include visuals:
- **Always**: UI/UX changes
- **Recommended**: Complex workflows, architecture changes
- **Optional**: Backend-only changes

Tools for screenshots:
- Chrome DevTools device mode (mobile screenshots)
- Annotated screenshots (use arrows, highlights)
- GIF recordings for interactions (LICEcap, ScreenToGif)
- Video recordings for complex flows (Loom, QuickTime)

### Code Examples

Include code snippets for:
- API usage examples
- Migration steps
- Breaking changes
- Complex logic explanation
- Before/after comparisons

## GitHub-Specific Features

### Using Markdown Features

```markdown
# Syntax highlighting
```javascript
const example = 'code';
```

# Task lists
- [x] Completed task
- [ ] Pending task

# Tables
| Column 1 | Column 2 |
|----------|----------|
| Data     | Data     |

# Collapsible sections
<details>
<summary>Click to expand</summary>
Hidden content here
</details>

# Mentions
@username for people
#123 for issues

# Labels and metadata
Closes #123
Fixes #456
Related to #789
```

### PR Templates in Repository

Create `.github/pull_request_template.md`:

```markdown
## Description
<!-- Describe your changes -->

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
<!-- Describe testing performed -->

## Checklist
- [ ] Tests added
- [ ] Documentation updated
- [ ] No breaking changes
```

## Notes

- Customize templates to match your team's workflow
- Keep descriptions up-to-date as PR evolves
- Use PR description as documentation for future reference
- Good descriptions reduce review time and improve quality
- Include deployment and rollback plans for production changes
- Screenshots are worth a thousand words for UI changes
- Always link related issues and tickets
- Ask for help when uncertain
- Be thorough but concise
- Update description if implementation changes during review
