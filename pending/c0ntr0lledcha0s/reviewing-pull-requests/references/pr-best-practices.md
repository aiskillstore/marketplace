# Pull Request Best Practices

## PR Size Guidelines

| Size | LOC | Review Time | Recommendation |
|------|-----|-------------|----------------|
| XS | < 10 | 5 min | Ideal for fixes |
| S | 10-100 | 15 min | Good for features |
| M | 100-400 | 30 min | Acceptable |
| L | 400-1000 | 1 hour | Consider splitting |
| XL | > 1000 | 2+ hours | Split required |

## Title Format

```
<type>(<scope>): <description>
```

Examples:
- `feat(auth): add JWT token authentication`
- `fix(api): resolve validation error`
- `docs(readme): update installation guide`

## Description Structure

```markdown
## Summary
One-paragraph description of changes

## Changes
- Bullet point of each change

## Testing
How to test these changes

## Screenshots
[If UI changes]

Closes #123
```

## Review Guidelines

### For Authors
- Self-review before requesting reviews
- Respond to all comments
- Keep commits atomic and logical
- Update PR if requirements change

### For Reviewers
- Review within 24 hours
- Focus on logic, not style
- Provide constructive feedback
- Approve when satisfied

## Merge Strategies

| Strategy | When to Use | Result |
|----------|-------------|--------|
| Merge | Feature branches | Preserves history |
| Squash | Small features/fixes | Clean history |
| Rebase | Linear history needed | Rewritten commits |

## Quality Gates

PRs should pass:
- [ ] CI/CD pipeline
- [ ] Code review approval
- [ ] Test coverage threshold
- [ ] Security scan
- [ ] Lint checks

## Anti-Patterns

- PRs without descriptions
- Mixing unrelated changes
- Force-pushing after reviews
- Merging without CI passing
- Stale PRs (> 7 days)
