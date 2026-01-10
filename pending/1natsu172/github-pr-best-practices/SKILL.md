---
name: github-pr-best-practices
description: Best practices for creating GitHub pull requests including conventional commits, PR formatting, and multi-language support (en/ja). Use when creating PRs, writing PR descriptions, or formatting commit messages.
---

# GitHub Pull Request Best Practices

This Skill provides comprehensive guidance for creating high-quality pull requests following industry best practices and conventional commit standards.

## Capabilities

- Generate conventional commit formatted PR titles
- Structure PR descriptions with proper sections
- Support multiple languages (English/Japanese)
- Follow GitHub PR template conventions
- Avoid common PR mistakes

## When to Use

Use this Skill when you need to:
- Create a new pull request
- Write PR titles and descriptions
- Format commit messages
- Follow conventional commit standards
- Generate PR content in English or Japanese

## PR Title Format

### Conventional Commits Standard

PR titles must follow [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <description>
```

**Important**: NO emojis in PR titles or descriptions.

### Common Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks, dependencies

### Scope (Optional but Recommended)

The scope should indicate what part of the codebase is affected:

- Module name: `feat(auth): add OAuth2 support`
- Component name: `fix(button): resolve click handler issue`
- Area of code: `docs(api): update endpoint documentation`

### Description

- Use imperative mood ("add" not "added" or "adds")
- No capitalization of first letter
- No period at the end
- Clear and concise (under 50 characters when possible)

### Examples

**Good**:
```
feat(auth): add OAuth2 authentication
fix(api): resolve timeout on large requests
docs(readme): update installation instructions
refactor(database): optimize query performance
test(auth): add integration tests for login flow
chore(deps): update dependencies to latest versions
```

**Bad**:
```
✨ Add new feature  (has emoji)
Fixed bug  (not following format, wrong tense)
Update.  (vague, has period)
FEAT: NEW STUFF  (all caps, vague)
```

## PR Description Structure

### Standard Template

```markdown
## Summary
- Brief description of changes (1-3 bullet points)
- Focus on what and why, not how
- Keep each point concise

## Test plan
- [ ] Test case 1
- [ ] Test case 2
- [ ] Verified no regressions

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

### Key Principles

1. **Summary Section**
   - 1-3 bullet points maximum
   - Explain what changed and why
   - Avoid implementation details (those are in the code)
   - Use present tense

2. **Test Plan Section**
   - Use checkbox format (`- [ ]`)
   - List specific test scenarios
   - Include regression testing
   - Be specific and actionable

3. **Signature**
   - Always include the Claude Code signature
   - Placed at the bottom

### Detailed Explanation (When Needed)

For complex PRs, add additional sections before the signature:

```markdown
## Summary
- Main changes

## Background
Context or motivation for changes

## Implementation Details
High-level overview of approach

## Test plan
- [ ] Tests

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

## Multi-Language Support

### English (Default)

Use English when no language is specified or when language is `en`:

```markdown
## Summary
- Add user authentication with OAuth2
- Implement token refresh mechanism
- Add comprehensive error handling

## Test plan
- [ ] Test OAuth2 login flow
- [ ] Test token refresh
- [ ] Test error scenarios
```

### Japanese

Use Japanese when language is `ja`:

```markdown
## 概要
- OAuth2によるユーザー認証を追加
- トークンリフレッシュ機能を実装
- 包括的なエラーハンドリングを追加

## テスト計画
- [ ] OAuth2ログインフローのテスト
- [ ] トークンリフレッシュのテスト
- [ ] エラーシナリオのテスト
```

### Language Selection Guidelines

- Default to English if no language specified
- Use the language specified by the caller
- Be consistent throughout the entire PR
- Don't mix languages within a single PR

## PR Template Integration

### Using Project Templates

If the project has a PR template at `.github/pull_request_template.md`:

1. Read the template file
2. Follow its structure exactly
3. Don't modify section headers
4. Don't add custom sections
5. Fill in all required sections (use "N/A" if not applicable)

### Template Best Practices

- **Preserve section headers**: Keep them exactly as in template
- **Complete all sections**: Even if marking as "N/A"
- **Follow order**: Maintain the template's section order
- **Don't improvise**: Stick to template structure

## GitHub CLI Best Practices

### Creating PRs with gh

**Basic command structure**:
```bash
gh pr create --draft --title "feat(scope): description" --body "$(cat <<'EOF'
## Summary
- Changes

## Test plan
- [ ] Tests

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

**Important notes**:
1. Use HEREDOC format for multi-line descriptions
2. Start with `--draft` flag for work in progress
3. Use `cat <<'EOF'` (with quotes) to prevent variable expansion
4. `gh pr create` automatically pushes the branch (no manual push needed)

### Draft vs Ready

**Start as draft when**:
- Work is still in progress
- Tests are not complete
- Need early feedback

**Convert to ready when**:
```bash
gh pr ready <PR-NUMBER>
```

### Common Mistakes to Avoid

1. **Manual Push Before PR Creation**
   - ❌ `git push -u origin branch && gh pr create`
   - ✅ `gh pr create` (handles push automatically)

2. **Including Emojis**
   - ❌ `✨ feat: add new feature`
   - ✅ `feat: add new feature`

3. **Incorrect Conventional Commit Format**
   - ❌ `Add new feature`
   - ✅ `feat: add new feature`

4. **Vague Descriptions**
   - ❌ `## Summary\n- Updated stuff`
   - ✅ `## Summary\n- Add OAuth2 authentication support`

5. **Ignoring Language Argument**
   - ❌ Always using English
   - ✅ Using specified language (en/ja)

6. **Modifying Template Structure**
   - ❌ Adding custom sections to template
   - ✅ Following template structure exactly

## Analyzing Commits for PR

### Use All Commits, Not Just Latest

When creating a PR, analyze **ALL commits** from the merge base:

```bash
# Get merge base
MERGE_BASE=$(git merge-base origin/main HEAD)

# Get ALL commits from merge base
git log $MERGE_BASE..HEAD
```

**Why this matters**:
- PR should represent all work on the branch
- Latest commit might not capture full scope
- Users expect PR to reflect entire branch

### Extracting PR Content from Commits

```bash
# Get commit messages for summary
git log --format="- %s" $MERGE_BASE..HEAD

# Get changed files for context
git diff --name-only $MERGE_BASE..HEAD

# Get commit count
git log --oneline $MERGE_BASE..HEAD | wc -l
```

## Quality Checklist

Before creating a PR, verify:

- [ ] Title follows conventional commit format
- [ ] No emojis in title or description
- [ ] Summary is clear and concise (1-3 points)
- [ ] Test plan is specific and actionable
- [ ] Language matches specified preference
- [ ] Template structure is followed (if exists)
- [ ] All commits are analyzed (not just latest)
- [ ] Claude Code signature is included

## Related Skills

- `git-analysis`: Use to gather commit and branch information
- Project-specific templates: Check `.github/pull_request_template.md`

## Additional Resources

See [REFERENCE.md](REFERENCE.md) for:
- Detailed conventional commits specification
- Language-specific examples
- Advanced PR patterns
- GitHub CLI command reference
