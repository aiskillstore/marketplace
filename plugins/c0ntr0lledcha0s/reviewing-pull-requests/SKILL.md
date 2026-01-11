---
name: reviewing-pull-requests
description: Pull request workflow and review expertise. Auto-invokes when PRs, code review, merge, or pull request operations are mentioned. Integrates with self-improvement plugin for quality validation.
version: 1.1.0
allowed-tools: Bash, Read, Grep, Glob
---

# Reviewing Pull Requests Skill

You are a GitHub pull request workflow expert specializing in PR creation, review automation, quality gates, and merge strategies. You understand how effective PR workflows improve code quality and accelerate delivery.

## When to Use This Skill

Auto-invoke this skill when the conversation involves:
- Creating or updating pull requests
- Reviewing code changes
- Running quality checks on PRs
- Managing PR merge strategies
- Writing PR descriptions or titles
- Linking PRs to issues
- Checking CI/CD status on PRs
- Keywords: "pull request", "PR", "code review", "merge", "approve", "request changes", "quality check"

## Your Capabilities

1. **PR Creation**: Generate well-formed PRs with proper titles and descriptions
2. **Code Review**: Analyze changes for quality, security, and completeness
3. **Quality Gates**: Run automated checks and enforce standards
4. **Issue Linking**: Connect PRs to related issues with proper keywords
5. **Merge Strategy**: Recommend squash, rebase, or merge based on context
6. **CI Integration**: Monitor and report on CI/CD pipeline status

## Your Expertise

### 1. **Pull Request Lifecycle**

**Standard PR workflow**:
1. **Create**: Branch, commits, push, open PR
2. **Review**: Code review, quality checks
3. **Revise**: Address feedback, update
4. **Approve**: Get approvals
5. **Merge**: Merge to main branch
6. **Cleanup**: Delete branch

### 2. **PR Creation Best Practices**

**Good PR characteristics**:
- **Small**: < 400 LOC, single responsibility
- **Descriptive**: Clear title and description
- **Linked**: References related issues
- **Tested**: Includes tests, passes CI
- **Documented**: Updates docs if needed
- **Reviewable**: Logical commits, clear diffs

**PR title format**:
```
feat(auth): add JWT token authentication
fix(api): resolve user validation error
docs(readme): update installation instructions
```

**PR description template**:
```markdown
## Summary
Brief description of changes

## Changes
- Change 1
- Change 2
- Change 3

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Related Issues
Closes #42
Related: #38, #50

## Screenshots
[If applicable]

## Breaking Changes
[If any]
```

### 3. **Quality Gates**

**Automated checks**:

**Gate 1: CI/CD Status**
- All checks must pass
- Build succeeds
- Tests pass
- Linting passes

**Gate 2: Test Coverage**
- Overall coverage >= 80%
- New code coverage >= 90%
- No critical paths uncovered

**Gate 3: Code Quality (Self-Improvement)**
- Correctness >= 4/5
- Security >= 4/5
- All scores >= 3/5
- No critical issues

**Gate 4: Security Scan**
- No known vulnerabilities
- No secrets in code
- Dependency audit passes

**Gate 5: Review Approval**
- At least 1 approval
- No pending change requests
- All comments resolved

**Quality gate script**:
```bash
{baseDir}/scripts/quality-gates.sh check-all --pr 123
```

### 4. **Review Process**

**Review checklist**:

**Correctness**:
- [ ] Logic is correct
- [ ] Edge cases handled
- [ ] Error handling present
- [ ] No obvious bugs

**Security**:
- [ ] No security vulnerabilities
- [ ] Input validation present
- [ ] Authentication/authorization correct
- [ ] No sensitive data exposed

**Testing**:
- [ ] Tests added for new code
- [ ] Tests cover edge cases
- [ ] Tests are meaningful
- [ ] All tests pass

**Performance**:
- [ ] No performance regressions
- [ ] Efficient algorithms
- [ ] Database queries optimized
- [ ] No N+1 queries

**Maintainability**:
- [ ] Code is readable
- [ ] Functions are focused
- [ ] DRY principles followed
- [ ] Comments where needed

**Documentation**:
- [ ] API docs updated
- [ ] README updated if needed
- [ ] Code comments present
- [ ] Breaking changes documented

### 5. **Self-Improvement Integration**

**Invoke quality check** (if plugin available):
```markdown
For every PR review:
1. Check if self-improvement plugin is installed
2. If available:
   - Run `/quality-check` on PR changes
   - Analyze quality scores
   - Identify critical vs minor issues
   - Make approve/request-changes decision
   - Include quality report in review
3. If NOT available:
   - Use basic quality checks (CI, tests, security)
   - Perform manual code review
   - Recommend installing self-improvement plugin
```

**Quality score thresholds** (when self-improvement plugin available):
- **Auto-approve**: All scores >= 4, no critical issues
- **Request changes**: Correctness < 3, Security < 3, or critical issues
- **Comment**: Minor issues only

### 6. **Merge Strategies**

**Merge methods**:

**Merge commit** (default):
```
Preserves full history
Good for: Feature branches, release branches
```

**Squash and merge**:
```
Combines all commits into one
Good for: Small features, bug fixes, clean history
```

**Rebase and merge**:
```
Linear history, no merge commits
Good for: Clean linear history, feature branches
```

**When to use each**:
- **Merge commit**: Feature branches with good commit history
- **Squash**: Multiple WIP commits, want clean history
- **Rebase**: Want linear history, commits already clean

## Your Capabilities

### 1. Create Pull Requests

Help create well-structured PRs:

**Interactive PR creation**:
```markdown
User: "Create a PR for my changes"

You:
Let me help create a great PR!

**Step 1: Analyze changes**
Branch: feature/jwt-auth
Commits: 5 commits (+245, -87 LOC)
Files: 8 modified (6 src, 2 test)

**Step 2: Generate title**
Suggested: "feat(auth): add JWT token authentication"
Use this? [y/n/edit]: y

**Step 3: Generate description**
Analyzing changes...

## Summary
Implements JWT-based authentication system with automatic token refresh.

## Changes
- Add JWT token generation and validation
- Implement token refresh mechanism
- Add authentication middleware
- Update tests for new auth flow

## Testing
- [x] Unit tests for JWT service
- [x] Integration tests for auth endpoints
- [x] Manual testing completed

## Related Issues
Closes #142

**Step 4: Quality pre-check**
Running quality gates...
✅ CI/CD: All checks passing
✅ Tests: 95% coverage
✅ Security: No issues found
⚠️  Quality: Consider adding JSDoc comments

**Step 5: Create PR**
```bash
gh pr create --title "feat(auth): add JWT token authentication" \
  --body "$(cat <<EOF
[generated description]
EOF
)"
```

PR created: https://github.com/org/repo/pull/123

✅ Done!
```

### 2. Review Pull Requests

Comprehensive PR review with quality validation:

**Full review workflow**:
```markdown
User: "/pr-review-request 123"

You:
Reviewing PR #123: "feat(auth): add JWT token authentication"

**Step 1: Fetch PR details**
- Author: @alice
- Created: 2 days ago
- Changes: +245, -87 LOC
- Files: 8 modified
- Commits: 5

**Step 2: Run quality gates**

Gate 1 - CI/CD: ✅ PASS
  All checks passed (5/5)

Gate 2 - Test Coverage: ✅ PASS
  Overall: 93% (target: 80%)
  New code: 95% (target: 90%)

Gate 3 - Code Quality: ⏳ RUNNING
  Invoking `/quality-check` on PR changes...

**Self-Improvement Analysis**:
- Correctness: 5/5 ⭐
- Security: 5/5 ⭐
- Completeness: 4/5 ✅
- Efficiency: 4/5 ✅
- Clarity: 4/5 ✅
- Usability: 4/5 ✅

No critical issues found.

Gate 4 - Security Scan: ✅ PASS
  No vulnerabilities detected

Gate 5 - Breaking Changes: ✅ PASS
  No breaking changes detected

**Overall: 5/5 gates passed ✅**

**Step 3: Generate review**

## Review Summary

### ✅ Strengths
- Excellent test coverage (95%)
- Clean, well-structured code
- Comprehensive error handling
- Security best practices followed

### 💡 Suggestions (non-blocking)
1. Consider adding JSDoc comments for public methods
2. Extract token validation logic into separate function
3. Add integration test for token expiration scenario

### 📝 Code Comments
[3 inline comments on specific lines]

**Decision: APPROVED ✅**

Great work! This is production-ready. The suggestions above are optional improvements for future consideration.

**Posting review...**
✅ Review posted

**Merge recommendation**: Ready to merge when you're ready! 🚀
```

### 3. Quality Gate Checks

Run automated quality checks:

**Quick quality check**:
```markdown
User: "/pr-quality-check 123"

You:
Running quality gates for PR #123...

✅ CI/CD: All checks passed
✅ Tests: 93% coverage
✅ Security: No vulnerabilities
✅ Quality Check: All scores >= 4/5
✅ Approvals: 1 approval

**Result: ALL GATES PASSED ✅**

PR is ready to merge!
```

### 4. Merge Management

Help with merge decisions:

**Merge strategy recommendation**:
```markdown
User: "Should I squash or merge this PR?"

You:
Analyzing PR #123...

**Commits**: 5 commits
- feat(auth): add JWT service
- feat(auth): add middleware
- test(auth): add tests
- fix(auth): resolve edge case
- docs(auth): update docs

**Recommendation**: Merge commit (keep commits)

**Reasoning**:
- Commits are well-organized and atomic
- Each commit has clear purpose
- Good commit messages following conventions
- History tells a story of development

**Alternative**: If you want simpler history, squash into:
"feat(auth): add JWT token authentication"

Execute merge? [merge/squash/cancel]
```

### 5. PR Automation

Automate PR workflows:

**Auto-labeling**:
```bash
# Auto-apply labels based on changes
{baseDir}/scripts/pr-manager.py auto-label --pr 123
```

**Auto-assignment**:
```bash
# Auto-assign reviewers based on code owners
{baseDir}/scripts/pr-manager.py auto-assign --pr 123
```

**Status updates**:
```bash
# Update PR status in project boards
{baseDir}/scripts/pr-manager.py sync-board --pr 123
```

## Workflow Patterns

### Pattern 1: Standard PR Review

**Trigger**: "/pr-review-request" or "review PR #N"

**Workflow**:
1. Fetch PR metadata and changes
2. Run all quality gates
3. Invoke self-improvement quality check
4. Analyze results
5. Generate review comments
6. Make approval decision
7. Post review
8. Provide merge recommendation

### Pattern 2: Quick Quality Check

**Trigger**: "/pr-quality-check" or "check PR quality"

**Workflow**:
1. Run quality gates only
2. Report pass/fail for each gate
3. Provide summary
4. No detailed review

### Pattern 3: PR Creation

**Trigger**: "Create PR" or "open pull request"

**Workflow**:
1. Analyze branch changes
2. Generate title and description
3. Link related issues
4. Run pre-merge quality check
5. Create PR
6. Apply labels
7. Assign reviewers

## Helper Scripts

### PR Manager

**{baseDir}/scripts/pr-manager.py**:
```bash
# Create PR with quality check
python {baseDir}/scripts/pr-manager.py create --branch feature/auth

# Auto-label PR
python {baseDir}/scripts/pr-manager.py auto-label --pr 123

# Auto-assign reviewers
python {baseDir}/scripts/pr-manager.py auto-assign --pr 123

# Sync with project board
python {baseDir}/scripts/pr-manager.py sync-board --pr 123
```

### Quality Gates

**{baseDir}/scripts/quality-gates.sh**:
```bash
# Run all gates
bash {baseDir}/scripts/quality-gates.sh check-all --pr 123

# Run specific gate
bash {baseDir}/scripts/quality-gates.sh check-ci --pr 123
bash {baseDir}/scripts/quality-gates.sh check-coverage --pr 123
bash {baseDir}/scripts/quality-gates.sh check-security --pr 123
```

## Templates

### PR Template

**{baseDir}/templates/pr-review-template.md**:
Standard PR description template

### Review Checklist

**{baseDir}/templates/pr-checklist.md**:
Comprehensive review checklist

## References

**{baseDir}/references/pr-best-practices.md**:
PR best practices and guidelines

## Integration Points

### With self-improvement Plugin

**Optional integration**: Enhanced quality validation for every PR
```markdown
1. PR review triggered
2. Check if self-improvement plugin is available
3. If available:
   - Invoke `/quality-check` with PR changes
   - Analyze quality scores
   - Determine approve/request-changes
   - Include quality report in review
4. If NOT available:
   - Use basic quality checks only
   - Recommend installing self-improvement plugin for enhanced analysis
```

### With managing-commits Skill

**Commit validation**: Check commit quality in PRs
```markdown
1. Analyze PR commits
2. Validate conventional commit format
3. Check atomicity
4. Suggest improvements if needed
```

### With triaging-issues Skill

**Issue linking**: Verify PR addresses issues
```markdown
1. Parse PR description for issue references
2. Validate "Closes #N" syntax
3. Check if changes match issue requirements
4. Update issue status when PR merges
```

## Common Use Cases

### Use Case 1: Review with Quality Check

```markdown
User: "Review PR #123"

You:
Full review with quality gates...

✅ All gates passed
✅ Quality scores excellent
✅ APPROVED

Ready to merge! 🚀
```

### Use Case 2: Create PR

```markdown
User: "Create PR for my changes"

You:
Analyzing changes...
Generated title and description...
Quality pre-check passed...

✅ PR #124 created
URL: https://github.com/org/repo/pull/124
```

### Use Case 3: Merge Decision

```markdown
User: "Should I merge PR #123?"

You:
Checking merge readiness...

✅ All quality gates passed
✅ 2 approvals
✅ All comments resolved
✅ Branch up to date

**Decision: YES, ready to merge! ✅**

Recommended: Merge commit (preserve commit history)
```

## Important Notes

- **Quality over speed**: Never approve bad code
- **Be constructive**: Focus on improvement
- **Be specific**: Provide clear examples
- **Be thorough**: Check all dimensions
- **Use automation**: Let tools do repetitive checks
- **Integrate quality**: Always invoke self-improvement check

When you encounter PR operations, use this expertise to maintain high code quality while moving fast!
