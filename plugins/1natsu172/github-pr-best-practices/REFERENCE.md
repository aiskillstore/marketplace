# GitHub PR Best Practices Reference

Detailed reference for conventional commits, PR formatting, and GitHub CLI usage.

## Conventional Commits Specification

### Full Format

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Type Reference

| Type | Purpose | When to Use | Example |
|------|---------|-------------|---------|
| `feat` | New feature | Adding functionality | `feat(auth): add OAuth2 login` |
| `fix` | Bug fix | Fixing issues | `fix(api): resolve timeout error` |
| `docs` | Documentation | README, comments, docs | `docs(api): add endpoint examples` |
| `style` | Formatting | Whitespace, formatting | `style(components): fix indentation` |
| `refactor` | Code restructuring | Improving code structure | `refactor(utils): simplify validation` |
| `perf` | Performance | Speed improvements | `perf(queries): optimize database calls` |
| `test` | Testing | Adding/updating tests | `test(auth): add login flow tests` |
| `build` | Build system | Build process, dependencies | `build(webpack): update config` |
| `ci` | CI/CD | CI configuration | `ci(actions): add test workflow` |
| `chore` | Maintenance | Routine tasks | `chore(deps): update dependencies` |
| `revert` | Reverting | Reverting changes | `revert: feat(auth): add OAuth2` |

### Scope Guidelines

The scope should identify the affected area:

**By module/package**:
```
feat(auth): ...
fix(payment): ...
docs(api): ...
```

**By component**:
```
feat(button): ...
fix(modal): ...
style(navbar): ...
```

**By layer**:
```
feat(frontend): ...
fix(backend): ...
refactor(database): ...
```

**No scope** (when change is global):
```
chore: update all dependencies
docs: update contributing guide
```

### Breaking Changes

Indicate breaking changes with `!` after type/scope:

```
feat(api)!: change endpoint response format

BREAKING CHANGE: API responses now use camelCase instead of snake_case
```

Or in footer:
```
feat(api): update user endpoint

BREAKING CHANGE: User ID is now returned as string instead of number
```

### Examples by Category

#### Features
```
feat(search): add fuzzy search capability
feat(export): support CSV export
feat(i18n): add Japanese localization
feat(api): implement rate limiting
```

#### Bug Fixes
```
fix(validation): prevent empty email submission
fix(cache): resolve race condition in cache updates
fix(ui): correct button alignment on mobile
fix(auth): handle expired token gracefully
```

#### Documentation
```
docs(readme): add installation instructions
docs(api): document new endpoints
docs(architecture): update system diagram
docs(contributing): add code review guidelines
```

#### Performance
```
perf(images): implement lazy loading
perf(queries): add database indexes
perf(cache): introduce Redis caching
perf(bundle): reduce JavaScript bundle size
```

#### Refactoring
```
refactor(auth): extract validation logic
refactor(components): convert to TypeScript
refactor(utils): simplify error handling
refactor(api): consolidate duplicate code
```

#### Tests
```
test(auth): add integration tests
test(utils): improve coverage to 90%
test(e2e): add checkout flow tests
test(unit): add edge case tests
```

## PR Description Templates

### Template: Simple Feature

**English**:
```markdown
## Summary
- Add [feature name] to improve [benefit]
- Implement [technical approach]
- Include comprehensive error handling

## Test plan
- [ ] Test happy path scenario
- [ ] Test edge cases
- [ ] Verify no regressions
- [ ] Check performance impact

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

**Japanese**:
```markdown
## 概要
- [機能名]を追加して[利点]を改善
- [技術的アプローチ]を実装
- 包括的なエラーハンドリングを含む

## テスト計画
- [ ] 正常系シナリオのテスト
- [ ] エッジケースのテスト
- [ ] リグレッションがないことを確認
- [ ] パフォーマンス影響をチェック

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

### Template: Bug Fix

**English**:
```markdown
## Summary
- Fix [issue description]
- Root cause was [explanation]
- Solution implements [approach]

## Test plan
- [ ] Reproduce original issue
- [ ] Verify fix resolves issue
- [ ] Test related functionality
- [ ] Add regression test

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

**Japanese**:
```markdown
## 概要
- [問題の説明]を修正
- 根本原因は[説明]
- 解決策は[アプローチ]を実装

## テスト計画
- [ ] 元の問題を再現
- [ ] 修正が問題を解決することを確認
- [ ] 関連機能をテスト
- [ ] リグレッションテストを追加

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

### Template: Refactoring

**English**:
```markdown
## Summary
- Refactor [component/module] for better [maintainability/performance]
- No functional changes
- Improve code structure and readability

## Test plan
- [ ] All existing tests pass
- [ ] No behavioral changes
- [ ] Code coverage maintained or improved

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

**Japanese**:
```markdown
## 概要
- [コンポーネント/モジュール]をリファクタリングして[保守性/パフォーマンス]を向上
- 機能的な変更なし
- コード構造と可読性を改善

## テスト計画
- [ ] 既存のテストがすべてパス
- [ ] 動作の変更がないことを確認
- [ ] コードカバレッジの維持または改善

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

### Template: Documentation

**English**:
```markdown
## Summary
- Update [documentation type] to reflect [changes]
- Improve clarity and examples
- Fix outdated information

## Test plan
- [ ] Review for accuracy
- [ ] Verify code examples work
- [ ] Check links and references

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

**Japanese**:
```markdown
## 概要
- [ドキュメントタイプ]を更新して[変更]を反映
- 明確さと例を改善
- 古い情報を修正

## テスト計画
- [ ] 正確性をレビュー
- [ ] コード例が動作することを確認
- [ ] リンクと参照をチェック

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

### Template: Complex Change

**English**:
```markdown
## Summary
- [High-level description of changes]
- [Key improvement or benefit]
- [Important implementation detail]

## Background
[Explain the context or motivation for this change]

## Implementation Details
- [Approach taken]
- [Key design decisions]
- [Tradeoffs considered]

## Test plan
- [ ] Unit tests for new functionality
- [ ] Integration tests for workflows
- [ ] Performance benchmarks
- [ ] Security review completed

## Migration Notes
[If applicable, explain migration steps or breaking changes]

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

**Japanese**:
```markdown
## 概要
- [変更の概要]
- [主な改善または利点]
- [重要な実装詳細]

## 背景
[この変更のコンテキストまたは動機を説明]

## 実装の詳細
- [採用したアプローチ]
- [主要な設計決定]
- [検討したトレードオフ]

## テスト計画
- [ ] 新機能の単体テスト
- [ ] ワークフローの統合テスト
- [ ] パフォーマンスベンチマーク
- [ ] セキュリティレビュー完了

## マイグレーション注意事項
[該当する場合、マイグレーション手順または破壊的変更を説明]

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

## Language-Specific Phrase Guide

### Common Sections

| English | Japanese |
|---------|----------|
| Summary | 概要 |
| Test plan | テスト計画 |
| Background | 背景 |
| Implementation Details | 実装の詳細 |
| Migration Notes | マイグレーション注意事項 |
| Breaking Changes | 破壊的変更 |

### Common Actions

| English | Japanese |
|---------|----------|
| Add | 追加 |
| Update | 更新 |
| Fix | 修正 |
| Remove | 削除 |
| Refactor | リファクタリング |
| Improve | 改善 |
| Implement | 実装 |
| Optimize | 最適化 |

### Common Phrases

| English | Japanese |
|---------|----------|
| No functional changes | 機能的な変更なし |
| Breaking change | 破壊的変更 |
| Backward compatible | 後方互換性あり |
| Includes tests | テストを含む |
| Performance improvement | パフォーマンス改善 |
| Bug fix | バグ修正 |
| New feature | 新機能 |

## GitHub CLI Command Reference

### Creating Pull Requests

#### Basic Creation
```bash
# Create draft PR
gh pr create --draft --title "Title" --body "Description"

# Create ready PR
gh pr create --title "Title" --body "Description"

# With base branch
gh pr create --base develop --title "Title" --body "Description"
```

#### Using HEREDOC for Body
```bash
gh pr create --draft --title "feat(auth): add OAuth2" --body "$(cat <<'EOF'
## Summary
- Add OAuth2 authentication

## Test plan
- [ ] Test login flow

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

#### Using Template File
```bash
# If .github/pull_request_template.md exists
gh pr create --draft --title "feat: add feature" --body-file .github/pull_request_template.md
```

#### With Reviewers
```bash
gh pr create --title "Title" --body "Description" --reviewer user1,user2
```

### Managing Pull Requests

#### List PRs
```bash
# Your open PRs
gh pr list --author "@me"

# All open PRs
gh pr list

# Filter by state
gh pr list --state closed

# Filter by label
gh pr list --label bug
```

#### View PR
```bash
# View in terminal
gh pr view 123

# View in browser
gh pr view 123 --web

# View diff
gh pr diff 123
```

#### Checkout PR
```bash
# Checkout PR branch
gh pr checkout 123

# With branch name
gh pr checkout 123 --branch my-review-branch
```

#### Update PR
```bash
# Convert draft to ready
gh pr ready 123

# Add reviewers
gh pr edit 123 --add-reviewer user1,user2

# Update title
gh pr edit 123 --title "New title"

# Update body
gh pr edit 123 --body "New description"
```

#### Merge PR
```bash
# Squash merge
gh pr merge 123 --squash

# Merge commit
gh pr merge 123 --merge

# Rebase
gh pr merge 123 --rebase

# Auto-merge when checks pass
gh pr merge 123 --auto --squash
```

#### Close/Reopen PR
```bash
# Close PR
gh pr close 123

# Reopen PR
gh pr reopen 123
```

### PR Status and Checks

```bash
# View status
gh pr status

# View checks
gh pr checks 123

# Watch checks
gh pr checks 123 --watch
```

### PR Comments and Reviews

```bash
# Add comment
gh pr comment 123 --body "Great work!"

# Review
gh pr review 123 --approve
gh pr review 123 --request-changes --body "Please fix X"
gh pr review 123 --comment --body "Question about Y"
```

## Best Practices Checklist

### Before Creating PR

- [ ] All commits follow conventional commit format
- [ ] Branch is up to date with base branch
- [ ] All tests pass locally
- [ ] Code is properly formatted
- [ ] No debug code or comments
- [ ] Documentation is updated

### PR Title

- [ ] Follows conventional commit format
- [ ] Has appropriate type (feat, fix, etc.)
- [ ] Includes scope when applicable
- [ ] Is clear and descriptive
- [ ] No emojis
- [ ] Under 72 characters

### PR Description

- [ ] Has summary section (1-3 points)
- [ ] Has test plan with checkboxes
- [ ] Includes Claude Code signature
- [ ] Uses correct language (en/ja)
- [ ] Follows template structure (if exists)
- [ ] No custom sections added to template

### Code Quality

- [ ] Follows project coding standards
- [ ] Includes appropriate tests
- [ ] Has no linting errors
- [ ] Performance is acceptable
- [ ] Security considerations addressed

### Review Process

- [ ] Self-review completed
- [ ] Appropriate reviewers requested
- [ ] CI/CD checks are passing
- [ ] No merge conflicts
- [ ] Ready for review (not draft)

## Common Mistakes and Solutions

### Mistake 1: Manual Push Before gh pr create

**Wrong**:
```bash
git push -u origin feature-branch
gh pr create
```

**Correct**:
```bash
# gh pr create handles push automatically
gh pr create
```

### Mistake 2: Including Emojis

**Wrong**:
```
✨ feat: add new feature
🐛 fix: resolve bug
```

**Correct**:
```
feat: add new feature
fix: resolve bug
```

### Mistake 3: Vague Descriptions

**Wrong**:
```markdown
## Summary
- Updated stuff
- Fixed things
- Made improvements
```

**Correct**:
```markdown
## Summary
- Add OAuth2 authentication support
- Fix timeout issue in API requests
- Improve query performance by 50%
```

### Mistake 4: Ignoring All Commits

**Wrong**:
```bash
# Only looking at latest commit
git log -1
```

**Correct**:
```bash
# Analyze all commits from merge base
MERGE_BASE=$(git merge-base origin/main HEAD)
git log $MERGE_BASE..HEAD
```

### Mistake 5: Wrong Conventional Commit Format

**Wrong**:
```
Add new feature
Fixed the bug
Update documentation
```

**Correct**:
```
feat: add new feature
fix: resolve authentication bug
docs: update API documentation
```

### Mistake 6: Mixed Languages

**Wrong**:
```markdown
## Summary
- Add 新機能
- Fix バグ

## テスト計画
- [ ] Test login flow
```

**Correct (English)**:
```markdown
## Summary
- Add new feature
- Fix bug

## Test plan
- [ ] Test login flow
```

**Correct (Japanese)**:
```markdown
## 概要
- 新機能を追加
- バグを修正

## テスト計画
- [ ] ログインフローをテスト
```

## Related Resources

- [Conventional Commits Specification](https://www.conventionalcommits.org/)
- [GitHub CLI Documentation](https://cli.github.com/manual/)
- [GitHub Pull Request Documentation](https://docs.github.com/en/pull-requests)
- [Semantic Versioning](https://semver.org/)
