# Pull Request Template

## Description

<!-- Provide a brief summary of the changes and the motivation behind them. Link to relevant issues. -->

**What changed:**


**Why it changed:**


**Related issues:**
- Fixes #[issue number]
- Relates to #[issue number]

---

## Type of Change

<!-- Mark the relevant option(s) with an [x] -->

- [ ] **Bug fix** (non-breaking change which fixes an issue)
- [ ] **New feature** (non-breaking change which adds functionality)
- [ ] **Breaking change** (fix or feature that would cause existing functionality to not work as expected)
- [ ] **Refactoring** (no functional changes, code improvement)
- [ ] **Documentation** (changes to documentation only)
- [ ] **Performance improvement** (non-breaking change that improves performance)
- [ ] **Test coverage** (adding or improving tests)
- [ ] **Dependency update** (updating libraries or packages)
- [ ] **Configuration change** (CI/CD, build, or environment config)

---

## How Has This Been Tested?

<!-- Describe the tests you ran to verify your changes. Provide instructions so reviewers can reproduce. -->

### Automated Tests

- [ ] **Unit tests** added/updated
- [ ] **Integration tests** added/updated
- [ ] **End-to-end tests** added/updated
- [ ] **All existing tests pass** locally

### Manual Testing

- [ ] Tested manually in **local environment**
- [ ] Tested in **staging environment**
- [ ] Tested on **multiple browsers** (if frontend changes)
- [ ] Tested on **mobile devices** (if applicable)

### Test Coverage

**Before**: X% coverage
**After**: Y% coverage
**Coverage change**: +Z%

---

## Testing Instructions for Reviewers

<!-- Provide step-by-step instructions for reviewers to test your changes -->

1. Checkout this branch: `git checkout feature/branch-name`
2. Install dependencies: `npm install` (if package.json changed)
3. Run migrations: `npm run migrate` (if database changed)
4. Start the application: `npm run dev`
5. Navigate to: `http://localhost:3000/feature-path`
6. Test scenario:
   - Step 1: [Description]
   - Step 2: [Description]
   - Expected result: [Description]

---

## Database Changes

<!-- If this PR includes database changes, describe them here -->

- [ ] **No database changes**
- [ ] **Migration created**: `migrations/YYYYMMDD_description.sql`
- [ ] **Rollback migration created**
- [ ] **Tested migration on staging data**
- [ ] **Data backfill needed**: [Describe]

**Schema changes:**
- Added table: `table_name`
- Added column: `table_name.column_name`
- Modified column: `table_name.column_name`
- Added index: `table_name(column_name)`

---

## Performance Impact

<!-- Describe any performance implications of your changes -->

- [ ] **No performance impact**
- [ ] **Performance improvement** (describe below)
- [ ] **Potential performance degradation** (describe mitigation below)

**Benchmarks:**
- Before: [metric] = X
- After: [metric] = Y
- Change: ±Z%

**Load test results:** (if applicable)
- Requests per second: X
- p95 latency: Xms
- Error rate: X%

---

## Security Considerations

<!-- Describe security implications and how they're addressed -->

- [ ] **No security impact**
- [ ] **Security improvement** (describe below)
- [ ] **New authentication/authorization** added
- [ ] **Input validation** implemented
- [ ] **Secrets management** updated (using environment variables, not hardcoded)

**Security review needed for:**
- [ ] Payment processing
- [ ] User authentication
- [ ] Data access controls
- [ ] API endpoint protection
- [ ] Sensitive data handling

---

## Breaking Changes

<!-- If this PR introduces breaking changes, describe them and provide migration path -->

- [ ] **No breaking changes**
- [ ] **Breaking changes** (describe below)

**What breaks:**


**Migration path for users:**


**Deprecation timeline:**
- Version X.Y: Deprecation warning added
- Version X.Y+1: Breaking change introduced
- Version X.Y+2: Old functionality removed

---

## Deployment Notes

<!-- Special instructions for deploying this change -->

- [ ] **Standard deployment** (no special steps)
- [ ] **Requires configuration changes** (describe below)
- [ ] **Requires manual steps** (describe below)
- [ ] **Feature flag** recommended

**Pre-deployment steps:**
1. [Step description]
2. [Step description]

**Post-deployment steps:**
1. [Step description]
2. [Step description]

**Rollback plan:**
- [ ] Can rollback via standard deployment revert
- [ ] Requires manual rollback steps (describe below)

---

## Checklist

<!-- Ensure all items are checked before requesting review -->

### Code Quality

- [ ] My code follows the **style guidelines** of this project
- [ ] I have performed a **self-review** of my own code
- [ ] I have **commented** my code, particularly in hard-to-understand areas
- [ ] I have removed **commented-out code** and **debug statements**
- [ ] I have removed **console.log** / **print** statements (unless intentional)
- [ ] My changes generate **no new warnings** (linter, TypeScript, etc.)

### Testing

- [ ] I have added **tests** that prove my fix is effective or that my feature works
- [ ] New and existing **unit tests pass** locally with my changes
- [ ] I have tested **edge cases** and **error scenarios**
- [ ] I have tested **backwards compatibility** (if applicable)

### Documentation

- [ ] I have made corresponding changes to the **documentation**
- [ ] I have updated the **README** (if applicable)
- [ ] I have updated **API docs** (if API changed)
- [ ] I have updated **inline comments** for complex logic
- [ ] I have updated **CHANGELOG** (if applicable)

### Dependencies

- [ ] Any dependent changes have been **merged and published** in downstream modules
- [ ] I have checked for **dependency vulnerabilities** (`npm audit` / `pip-audit`)
- [ ] I have updated **lock files** (`package-lock.json`, `Pipfile.lock`)

### Security

- [ ] I have reviewed for **security vulnerabilities**
- [ ] I have not introduced **hardcoded secrets** or API keys
- [ ] I have validated and **sanitized user inputs**
- [ ] I have added appropriate **authentication/authorization** checks

---

## Screenshots

<!-- Add screenshots for UI changes. Before/after comparisons are especially helpful. -->

### Before

[Screenshot or N/A]

### After

[Screenshot or N/A]

---

## Additional Context

<!-- Add any other context about the PR here -->

**Related PRs:**
- [Link to related PR in another repo]

**Follow-up work:**
- [ ] [Description of follow-up task] (#issue-number)

**Known limitations:**
- [Describe any known issues or limitations]

**Questions for reviewers:**
- [Any specific questions or areas you'd like reviewers to focus on]

---

## Reviewer Checklist

<!-- For reviewers: Use this checklist during review -->

- [ ] Code changes make sense and align with PR description
- [ ] Tests adequately cover new code
- [ ] No obvious bugs or logic errors
- [ ] Performance implications are acceptable
- [ ] Security considerations are addressed
- [ ] Documentation is updated
- [ ] Breaking changes are clearly communicated
- [ ] Code follows project conventions and style

---

**PR Created**: [Date]
**Ready for Review**: [Date]
**Target Merge Date**: [Date]
