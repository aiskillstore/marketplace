# Test Coverage Checklist

Use this checklist to ensure comprehensive test coverage across your application.

---

## Pre-Testing Setup

- [ ] **Testing Framework Installed**: Jest/Vitest/pytest configured
- [ ] **Coverage Tool Configured**: nyc/istanbul/coverage.py set up
- [ ] **CI/CD Integration**: Tests run automatically on commits
- [ ] **Test Environment**: Separate test database and environment variables
- [ ] **Fixture Management**: Test data fixtures and factories created
- [ ] **Mocking Strategy**: Decision made on what to mock vs use real dependencies

---

## Static Analysis (Foundation Layer)

### Linting
- [ ] **ESLint/Pylint Configured**: Linter installed with appropriate rules
- [ ] **Pre-commit Hooks**: Linting runs before commits (husky, lint-staged)
- [ ] **Zero Linting Errors**: All files pass linting checks
- [ ] **Consistent Formatting**: Prettier/Black configured and enforced

### Type Checking
- [ ] **TypeScript/mypy Configured**: Strict mode enabled
- [ ] **No Type Errors**: All files type-check successfully
- [ ] **Type Coverage**: Aim for 100% type coverage (no `any` in TypeScript)
- [ ] **Generic Constraints**: Proper type constraints on generic functions

### Code Quality
- [ ] **Complexity Analysis**: Functions with complexity > 10 identified
- [ ] **Duplication Detection**: DRY violations found and addressed
- [ ] **Security Scanning**: ESLint security plugin / Bandit configured

---

## Unit Testing (Base Layer - 20% of tests)

### Business Logic
- [ ] **Pure Functions**: All pure functions have unit tests
- [ ] **Edge Cases**: Boundary conditions tested (min, max, zero, negative, null, undefined)
- [ ] **Error Handling**: Exceptions and error paths tested
- [ ] **Input Validation**: Invalid inputs trigger appropriate errors
- [ ] **Coverage Target**: 90%+ line coverage for business logic

### Utility Functions
- [ ] **String Utilities**: formatDate, slugify, capitalize, etc. tested
- [ ] **Number Utilities**: round, clamp, percentage calculations tested
- [ ] **Array Utilities**: filter, map, reduce helpers tested
- [ ] **Object Utilities**: deep clone, merge, pick/omit tested

### Data Transformations
- [ ] **Serialization**: JSON/XML/CSV serializers tested
- [ ] **Deserialization**: Parsers tested with valid and invalid input
- [ ] **Data Mappers**: DTO <-> Entity conversions tested
- [ ] **Validators**: Schema validation logic tested

### Examples of Well-Tested Units:
```typescript
// ✅ calculateDiscount function
- Applies 20% discount correctly
- Throws error for negative price
- Throws error for discount > 100%
- Returns original price for 0% discount
- Handles decimal discounts (25.5%)
```

---

## Integration Testing (Main Layer - 70% of tests)

### API Endpoints
- [ ] **CRUD Operations**: Create, Read, Update, Delete tested for each resource
- [ ] **Request Validation**: Invalid payloads return 400/422
- [ ] **Authentication**: Protected endpoints require auth
- [ ] **Authorization**: Users can only access their own resources
- [ ] **Pagination**: List endpoints return paginated results
- [ ] **Filtering**: Query parameters filter results correctly
- [ ] **Sorting**: Sort parameters work as expected
- [ ] **Error Responses**: Consistent error format across endpoints

### Database Operations
- [ ] **Insert**: Records created correctly
- [ ] **Query**: Filters, joins, and sorting work
- [ ] **Update**: Changes persisted to database
- [ ] **Delete**: Records removed, cascades handled
- [ ] **Transactions**: Rollback on failure, commit on success
- [ ] **Constraints**: Unique, foreign key, check constraints enforced

### Service Integrations
- [ ] **External APIs**: Third-party API calls tested (mocked or stubbed)
- [ ] **Email Service**: Email sending tested (using test mailbox)
- [ ] **Payment Gateway**: Payment processing tested (sandbox mode)
- [ ] **File Storage**: S3/blob storage operations tested
- [ ] **Message Queue**: Kafka/RabbitMQ publish/consume tested

### Component Interactions
- [ ] **Service → Repository**: Service calls repository correctly
- [ ] **Controller → Service**: Controller delegates to service
- [ ] **Middleware**: Middleware processes requests/responses
- [ ] **Error Propagation**: Errors bubble up correctly

### Examples of Well-Tested Integrations:
```typescript
// ✅ POST /api/users endpoint
- Creates user and returns 201 with user data
- Returns 400 for missing required fields
- Returns 422 for duplicate email
- Returns 401 if not authenticated
- Sends welcome email after creation
- User persists in database
```

---

## End-to-End Testing (Top Layer - 10% of tests)

### Critical User Journeys
- [ ] **User Signup Flow**: Registration → Email verification → Login
- [ ] **User Login Flow**: Login → Session management → Logout
- [ ] **Checkout Flow**: Add to cart → Checkout → Payment → Confirmation
- [ ] **Password Reset**: Request reset → Email link → Set new password → Login
- [ ] **Order Management**: Create order → View order → Cancel order

### Cross-Feature Workflows
- [ ] **Multi-Step Wizards**: All steps complete successfully
- [ ] **Navigation Flows**: Users can navigate between pages
- [ ] **Form Submissions**: Multi-page forms persist data
- [ ] **Real-Time Updates**: WebSocket/SSE updates appear in UI

### Browsers and Devices (if applicable)
- [ ] **Chrome**: Latest version tested
- [ ] **Firefox**: Latest version tested
- [ ] **Safari**: Latest version tested (if Mac/iOS support)
- [ ] **Mobile**: Responsive layouts work on 375px and 768px viewports

### Examples of Well-Tested E2E Flows:
```typescript
// ✅ Complete checkout journey
- User logs in
- Searches for product
- Adds product to cart
- Navigates to cart
- Applies coupon code
- Proceeds to checkout
- Enters shipping info
- Completes payment
- Sees order confirmation
- Receives confirmation email
```

---

## Performance Testing

### Load Testing
- [ ] **Baseline Metrics**: p50, p95, p99 latencies established
- [ ] **Target Load**: System tested at expected peak load
- [ ] **Sustained Load**: 5-minute sustained load test passes
- [ ] **Ramp-Up/Ramp-Down**: Gradual load increase/decrease tested

### Stress Testing
- [ ] **Breaking Point**: Maximum capacity identified
- [ ] **Graceful Degradation**: System remains stable under stress
- [ ] **Recovery**: System recovers after stress removed

### Performance Benchmarks
- [ ] **API Response Times**: p95 < 500ms for all endpoints
- [ ] **Database Queries**: Slow queries (> 100ms) identified and optimized
- [ ] **Page Load Times**: TTI (Time to Interactive) < 3s
- [ ] **Asset Sizes**: JavaScript bundles < 200KB gzipped

---

## Security Testing

### Authentication & Authorization
- [ ] **Broken Auth**: Password requirements enforced
- [ ] **Session Management**: Sessions expire after timeout
- [ ] **JWT Security**: Tokens signed and validated correctly
- [ ] **RBAC**: Role-based access control enforced
- [ ] **Password Reset**: Reset tokens expire and are single-use

### Input Validation
- [ ] **SQL Injection**: Parameterized queries used, no SQL injection possible
- [ ] **XSS Protection**: User input sanitized, CSP headers set
- [ ] **CSRF Protection**: CSRF tokens required for state-changing operations
- [ ] **File Uploads**: File type and size restrictions enforced

### Security Headers
- [ ] **HTTPS Only**: All traffic uses HTTPS in production
- [ ] **Security Headers**: CSP, X-Frame-Options, HSTS configured
- [ ] **Rate Limiting**: Endpoints protected from abuse
- [ ] **API Keys**: Keys not exposed in client-side code

---

## Accessibility Testing (if applicable)

- [ ] **Keyboard Navigation**: All interactive elements accessible via keyboard
- [ ] **Screen Reader**: ARIA labels and roles properly set
- [ ] **Color Contrast**: WCAG AA compliance (4.5:1 for normal text)
- [ ] **Focus Indicators**: Visible focus states for all interactive elements
- [ ] **Form Validation**: Error messages announced to screen readers

---

## Coverage Metrics

### Quantitative Targets
- [ ] **Overall Line Coverage**: ≥ 80%
- [ ] **Branch Coverage**: ≥ 75%
- [ ] **Function Coverage**: ≥ 85%
- [ ] **Critical Paths**: 95-100% coverage

### Qualitative Targets
- [ ] **Happy Paths**: All main workflows tested
- [ ] **Error Paths**: Error handling tested
- [ ] **Edge Cases**: Boundary conditions tested
- [ ] **Regression**: Previously fixed bugs have regression tests

### Coverage Gaps
Identify areas with insufficient coverage:
- [ ] **Untested Modules**: List modules with < 80% coverage
- [ ] **Untested Branches**: Identify uncovered if/else branches
- [ ] **Untested Error Handlers**: Catch blocks without tests
- [ ] **Dead Code**: Unreachable code identified and removed

---

## Test Quality Metrics

### Test Reliability
- [ ] **No Flaky Tests**: Tests pass consistently (99%+ pass rate)
- [ ] **Deterministic**: Tests produce same results every run
- [ ] **Isolated**: Tests don't depend on execution order
- [ ] **Fast Execution**: Unit tests < 100ms each, full suite < 15 min

### Test Maintainability
- [ ] **DRY Tests**: Common setup extracted to helpers/fixtures
- [ ] **Clear Assertions**: Test failures have meaningful error messages
- [ ] **Descriptive Names**: Test names clearly describe what's tested
- [ ] **Focused Tests**: Each test validates one behavior

---

## Continuous Testing

### CI/CD Pipeline
- [ ] **Automated Execution**: Tests run on every commit
- [ ] **Fast Feedback**: Test results available within 10 minutes
- [ ] **Quality Gates**: Merges blocked if tests fail or coverage drops
- [ ] **Parallel Execution**: Tests run in parallel for speed

### Test Reporting
- [ ] **Coverage Reports**: Generated and published (Codecov, Coveralls)
- [ ] **Test Results**: Pass/fail status visible in PR
- [ ] **Performance Trends**: Execution time tracked over time
- [ ] **Flaky Test Detection**: Flaky tests flagged automatically

---

## Documentation

- [ ] **Testing Guide**: README includes how to run tests
- [ ] **Test Organization**: Test structure matches source structure
- [ ] **Naming Conventions**: Consistent test file naming (*.test.ts, test_*.py)
- [ ] **Test Data**: Fixtures and factories documented

---

## Pre-Release Checklist

Before deploying to production:

- [ ] **All Tests Pass**: 100% pass rate on main branch
- [ ] **Coverage Targets Met**: Overall coverage ≥ 80%
- [ ] **No Critical Bugs**: All P0/P1 bugs resolved
- [ ] **Performance Benchmarks**: All benchmarks within targets
- [ ] **Security Scan**: No high-severity vulnerabilities
- [ ] **E2E Tests Pass**: All critical journeys working
- [ ] **Smoke Tests**: Production smoke tests prepared
- [ ] **Rollback Plan**: Can revert if issues found

---

## Post-Release Validation

After deploying:

- [ ] **Smoke Tests**: Critical paths verified in production
- [ ] **Monitoring**: Error rates and performance metrics normal
- [ ] **User Feedback**: No major user-reported issues
- [ ] **Canary Deployment**: Gradual rollout successful

---

## Common Coverage Gaps

### Often Missed Areas:
- ❌ **Error Handlers**: Try/catch blocks without tests
- ❌ **Async Operations**: Promises, callbacks, async/await error paths
- ❌ **Edge Cases**: Null, undefined, empty arrays, empty strings
- ❌ **Timeouts**: Retry logic, exponential backoff
- ❌ **Cleanup**: Resource cleanup in finally blocks
- ❌ **Cron Jobs**: Scheduled tasks and background jobs
- ❌ **Webhooks**: Incoming webhook handlers
- ❌ **Admin Features**: Admin-only functionality

### How to Find Gaps:
1. Run coverage report with `--coverage` flag
2. Review coverage HTML report (line-by-line view)
3. Identify untested branches (if/else, switch cases)
4. Add tests for uncovered code
5. Repeat until targets met

---

## Test Review Checklist

When reviewing tests:

- [ ] **Tests Actually Test Something**: Assertions are meaningful
- [ ] **No False Positives**: Tests fail when they should
- [ ] **No Test Implementation Details**: Tests focus on behavior, not internals
- [ ] **Proper Cleanup**: Resources released after tests
- [ ] **Realistic Scenarios**: Test data resembles production data
- [ ] **Performance Conscious**: Tests don't create unnecessary overhead

---

**Checklist Version**: 1.0.0
**Skill**: testing-strategy-builder v1.0.0
**Last Updated**: 2025-10-31
