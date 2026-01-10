# Requirements Completeness Checklist

Use this checklist to ensure you have sufficient requirements before starting implementation.

---

## Task: [Task Name]

**Date:** [YYYY-MM-DD]
**Checked By:** [Agent name]

---

## Part 1: Functional Requirements

### Happy Path Scenarios

- [ ] **Primary use case defined**
  - What is the main user action?
  - What should happen when it succeeds?
  - What is the expected output?

- [ ] **User flow documented**
  - What are the steps the user takes?
  - What does the user see at each step?
  - Where does the flow end?

- [ ] **Success criteria clear**
  - How do we know it worked?
  - What indicates success to the user?
  - What data is returned/displayed?

**Happy Path Complete:** ✅ Yes / ❌ No

---

### Error Handling

- [ ] **Error scenarios identified**
  - What can go wrong?
  - What happens if network fails?
  - What happens if user provides invalid input?
  - What happens if external service is down?

- [ ] **Error messages defined**
  - What message does user see for each error?
  - Are error messages helpful and actionable?
  - Do errors include recovery suggestions?

- [ ] **Fallback behaviors specified**
  - What happens when errors occur?
  - Can user retry?
  - Is there graceful degradation?

**Error Handling Complete:** ✅ Yes / ❌ No

---

### Edge Cases

- [ ] **Boundary conditions identified**
  - What happens with empty input?
  - What happens with maximum input?
  - What happens with minimum input?
  - What about special characters?

- [ ] **Concurrent operations**
  - What if user clicks twice?
  - What if multiple users access same resource?
  - How are race conditions handled?

- [ ] **State transitions**
  - What are all possible states?
  - What transitions are allowed?
  - What transitions are forbidden?

**Edge Cases Complete:** ✅ Yes / ❌ No

---

### Input Validation

- [ ] **Valid inputs defined**
  - What formats are acceptable?
  - What ranges are allowed?
  - What types are expected?

- [ ] **Invalid inputs defined**
  - What should be rejected?
  - What validation errors can occur?
  - Where is validation performed (frontend/backend)?

- [ ] **Sanitization specified**
  - How is input cleaned?
  - What characters are escaped?
  - How is XSS prevented?

**Input Validation Complete:** ✅ Yes / ❌ No

---

### Output Specification

- [ ] **Output format defined**
  - What is the structure (JSON, HTML, etc)?
  - What fields are included?
  - What are the data types?

- [ ] **Output examples provided**
  - Sample success response?
  - Sample error response?
  - Sample edge case response?

- [ ] **Output validation**
  - How is output verified?
  - What makes output valid?
  - Are there schema definitions?

**Output Specification Complete:** ✅ Yes / ❌ No

---

## Part 2: Technical Requirements

### API Contracts

- [ ] **Endpoints defined**
  - What is the endpoint path?
  - What HTTP method is used?
  - What headers are required?

- [ ] **Request schema specified**
  ```json
  {
    "field1": "type",
    "field2": "type"
  }
  ```

- [ ] **Response schema specified**
  ```json
  {
    "field1": "type",
    "field2": "type"
  }
  ```

- [ ] **Status codes defined**
  - 200: Success
  - 400: Bad Request
  - 401: Unauthorized
  - 404: Not Found
  - 500: Server Error

**API Contracts Complete:** ✅ Yes / ❌ No

---

### Data Structures

- [ ] **Models/Types defined**
  ```typescript
  interface ModelName {
    field1: type;
    field2: type;
  }
  ```

- [ ] **Relationships documented**
  - One-to-many?
  - Many-to-many?
  - Belongs-to?

- [ ] **Constraints specified**
  - Required fields?
  - Unique fields?
  - Default values?
  - Validation rules?

**Data Structures Complete:** ✅ Yes / ❌ No

---

### Database Changes

- [ ] **Schema changes identified**
  - New tables/collections?
  - New columns/fields?
  - Modified fields?
  - Dropped fields?

- [ ] **Migration plan defined**
  - How to migrate existing data?
  - Is migration reversible?
  - What's the rollback plan?

- [ ] **Indexes specified**
  - What fields need indexing?
  - Any composite indexes?
  - Performance considerations?

**Database Changes Complete:** ✅ Yes / ❌ No / ⚪ N/A

---

### Authentication & Authorization

- [ ] **Authentication method**
  - JWT tokens?
  - Session cookies?
  - OAuth?
  - API keys?

- [ ] **Authorization rules**
  - Who can access this?
  - What roles are required?
  - What permissions are needed?

- [ ] **Security considerations**
  - Rate limiting?
  - CSRF protection?
  - Input sanitization?
  - SQL injection prevention?

**Auth Complete:** ✅ Yes / ❌ No / ⚪ N/A

---

### Performance Requirements

- [ ] **Latency requirements**
  - Maximum response time?
  - Target response time?
  - Acceptable percentile (p95, p99)?

- [ ] **Throughput requirements**
  - Requests per second?
  - Concurrent users?
  - Data volume?

- [ ] **Optimization strategies**
  - Caching?
  - Lazy loading?
  - Pagination?
  - Debouncing?

**Performance Complete:** ✅ Yes / ❌ No / ⚪ N/A

---

### Dependencies

- [ ] **External services listed**
  - What APIs are called?
  - What libraries are used?
  - What services must be running?

- [ ] **Environment configuration**
  - What env vars are needed?
  - What default values?
  - What secrets are required?

- [ ] **Dependency availability**
  - Are dependencies ready?
  - Do they need setup?
  - Are they documented?

**Dependencies Complete:** ✅ Yes / ❌ No

---

## Part 3: Non-Functional Requirements

### Testing Requirements

- [ ] **Test scenarios defined**
  - Unit tests needed?
  - Integration tests needed?
  - E2E tests needed?

- [ ] **Coverage expectations**
  - Minimum coverage percentage?
  - Critical paths covered?
  - Edge cases tested?

- [ ] **Test data specified**
  - Sample test data provided?
  - Mock data defined?
  - Test fixtures ready?

**Testing Complete:** ✅ Yes / ❌ No

---

### Documentation

- [ ] **Code documentation**
  - JSDoc/docstrings required?
  - Inline comments for complex logic?
  - README updates needed?

- [ ] **API documentation**
  - OpenAPI/Swagger specs?
  - Example requests/responses?
  - Authentication docs?

- [ ] **User documentation**
  - User guide updates?
  - Feature announcements?
  - Help text/tooltips?

**Documentation Complete:** ✅ Yes / ❌ No / ⚪ N/A

---

### Accessibility

- [ ] **Keyboard navigation**
  - Can be used without mouse?
  - Tab order logical?
  - Focus indicators visible?

- [ ] **Screen reader support**
  - ARIA labels present?
  - Semantic HTML used?
  - Alt text for images?

- [ ] **WCAG compliance**
  - Color contrast sufficient?
  - Text resizable?
  - No flashing content?

**Accessibility Complete:** ✅ Yes / ❌ No / ⚪ N/A

---

## Completeness Summary

### Critical Requirements (MUST have all)

Count the ✅ in these sections:

- [ ] Happy Path Scenarios
- [ ] Error Handling
- [ ] API Contracts (if applicable)
- [ ] Data Structures
- [ ] Dependencies

**Critical Requirements Complete:** _____ / 5

**BLOCKING THRESHOLD:** If < 3 critical requirements complete → **BLOCKED**

---

### Important Requirements (SHOULD have most)

Count the ✅ in these sections:

- [ ] Edge Cases
- [ ] Input Validation
- [ ] Output Specification
- [ ] Database Changes (if applicable)
- [ ] Authentication & Authorization (if applicable)
- [ ] Testing Requirements

**Important Requirements Complete:** _____ / 6

**WARNING THRESHOLD:** If < 4 important requirements complete → **WARNING**

---

### Optional Requirements (NICE to have)

Count the ✅ in these sections:

- [ ] Performance Requirements
- [ ] Documentation
- [ ] Accessibility

**Optional Requirements Complete:** _____ / 3

---

## Gate Decision Based on Requirements

### Critical Questions Count

Count all ❌ "No" in Critical Requirements:

**Unanswered Critical Questions:** _____

**Gate Rule:** If > 3 unanswered critical questions → **BLOCKED**

---

## Final Assessment

**Requirements Completeness:** [Choose one]

- [ ] **✅ COMPLETE** - All critical + most important requirements defined
- [ ] **⚠️ MOSTLY COMPLETE** - All critical + some important requirements defined
- [ ] **❌ INCOMPLETE** - Missing critical requirements

**Can Proceed:** ✅ Yes / ⚠️ With Cautions / ❌ No

---

## Actions Required

### If INCOMPLETE (❌)

**Missing Critical Requirements:**
1. [What's missing]
2. [What's missing]
3. [What's missing]

**Actions to Complete:**
1. [What to do]
2. [What to do]
3. [What to do]

**Escalate to:** User / Product Owner / Studio Coach

---

### If MOSTLY COMPLETE (⚠️)

**Assumptions to Document:**
1. **Assumption:** [What are you assuming for missing requirement]
   - **Risk:** Low / Medium / High
   - **Mitigation:** [How to reduce risk]

2. **Assumption:** [What are you assuming]
   - **Risk:** Low / Medium / High
   - **Mitigation:** [How to reduce risk]

**Can Proceed With:** Documented assumptions and checkpoint plan

---

### If COMPLETE (✅)

**Ready to Proceed:** Yes

**Next Step:** Run full gate check using `gate-check-template.md`

---

## Context Recording

```javascript
// Record requirements check in context
context.requirements_checks = context.requirements_checks || [];
context.requirements_checks.push({
  task: "[Task description]",
  timestamp: new Date().toISOString(),
  critical_requirements_complete: [count],
  important_requirements_complete: [count],
  optional_requirements_complete: [count],
  unanswered_critical_questions: [count],
  completeness_status: "complete|mostly_complete|incomplete",
  can_proceed: true|false,
  assumptions: ["assumption1", "assumption2"]
});
```

---

## Sign-Off

**Checked By:** [Agent name]
**Date:** [YYYY-MM-DD HH:MM:SS]
**Status:** ✅ Complete / ⚠️ Mostly Complete / ❌ Incomplete
**Can Proceed:** ✅ Yes / ⚠️ With Cautions / ❌ No
