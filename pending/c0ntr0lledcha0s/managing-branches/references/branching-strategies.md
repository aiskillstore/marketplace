# Branching Strategies Overview

This guide covers the most common Git branching strategies and helps you choose the right one for your project.

## Strategy Comparison

| Strategy | Complexity | Best For | Release Frequency |
|----------|------------|----------|-------------------|
| **Gitflow** | High | Scheduled releases, multiple versions | Weeks/Months |
| **GitHub Flow** | Low | Continuous deployment, SaaS | Daily/Hourly |
| **GitLab Flow** | Medium | Environment-based deployment | Days/Weeks |
| **Trunk-Based** | Low | High-velocity teams, CI/CD maturity | Continuous |

## Choosing a Strategy

### Use Gitflow When:
- You have scheduled releases (e.g., monthly, quarterly)
- You need to support multiple production versions
- Your team is larger (10+ developers)
- You need strict release management
- Your deployment process is complex

### Use GitHub Flow When:
- You deploy to production frequently
- You have a small to medium team
- You're building a web application or SaaS
- Your CI/CD pipeline is mature
- Simplicity is important

### Use GitLab Flow When:
- You have multiple deployment environments
- You need staged releases (dev → staging → prod)
- You have compliance requirements for promotion
- Environment-specific configurations are needed

### Use Trunk-Based When:
- You have excellent test coverage
- Your team practices continuous integration
- You use feature flags for incomplete work
- You need maximum development velocity
- Your branches live less than 2 days

## Strategy Details

### Gitflow

**Branch Structure:**
```
main ─────●─────────────●─────────● (releases only)
          │             │         │
          └─hotfix/*────┘         │
                                  │
develop ──●───●───●───●───●───●───● (integration)
          │   │   │   │   │   │
          └─feature/*─┘   │   │
                          └─release/*─┘
```

**Branches:**
- `main` - Production releases, tagged versions
- `develop` - Integration branch
- `feature/*` - New features
- `release/*` - Release preparation
- `hotfix/*` - Emergency production fixes
- `support/*` - Long-term support branches (optional)

**Workflow:**
1. Features branch from `develop`
2. Features merge back to `develop`
3. Release branches from `develop` for final prep
4. Release merges to `main` AND `develop`
5. Hotfixes branch from `main`
6. Hotfixes merge to `main` AND `develop`

**Pros:**
- Clear separation of concerns
- Parallel development of features
- Dedicated release preparation
- Support for multiple versions

**Cons:**
- Complex branching model
- Can lead to long-lived branches
- Merge conflicts more common
- Slower release cycle

---

### GitHub Flow

**Branch Structure:**
```
main ─────●───●───●───●───●───● (always deployable)
          │   │   │   │   │
          └─feature─┴─fix─┘
```

**Branches:**
- `main` - Single production branch
- Feature branches - All development work

**Workflow:**
1. Branch from `main`
2. Add commits
3. Open Pull Request
4. Review and discuss
5. Deploy and test
6. Merge to `main`

**Pros:**
- Simple and easy to understand
- Continuous deployment friendly
- Short-lived branches
- Fewer merge conflicts

**Cons:**
- No staging or release branches
- Less control over releases
- May need feature flags for partial work
- Not ideal for versioned releases

---

### GitLab Flow

**Branch Structure:**
```
main ─────●───●───●───● (development)
          ↓   ↓   ↓
staging ──●───●───●───● (pre-production)
          ↓   ↓   ↓
production ●──●───●───● (live)
```

**Branches:**
- `main` - Development/integration
- `staging` - Pre-production testing
- `production` - Live environment
- Feature branches - Development work

**Workflow:**
1. Feature branches from `main`
2. Features merge to `main`
3. Promote `main` to `staging` for testing
4. Promote `staging` to `production` for release

**Pros:**
- Clear environment mapping
- Controlled promotions
- Easy rollback per environment
- Good for compliance needs

**Cons:**
- Cherry-picking between environments
- Potential for environment drift
- More branches to maintain
- Slower feedback loop

---

### Trunk-Based Development

**Branch Structure:**
```
main/trunk ─●─●─●─●─●─●─●─● (single source of truth)
            │ │   │
            └─┴───┴─ very short-lived branches
```

**Branches:**
- `main` / `trunk` - Single long-lived branch
- Short-lived feature branches (optional, < 2 days)

**Workflow:**
1. Branch from `main` (or commit directly)
2. Complete work quickly
3. Merge back to `main` within hours/days
4. Use feature flags for incomplete work
5. Release from `main` at any time

**Pros:**
- Maximum velocity
- Minimal merge conflicts
- Always releasable
- Encourages small changes

**Cons:**
- Requires excellent testing
- Needs feature flag infrastructure
- Less isolation for complex features
- Direct commits can be risky

## Migration Between Strategies

### From Gitflow to GitHub Flow:
1. Merge `develop` to `main`
2. Delete `develop` branch
3. Create feature branches from `main`
4. Set up CI/CD for `main`
5. Use feature flags for long-running work

### From GitHub Flow to Gitflow:
1. Create `develop` from `main`
2. Set `develop` as default branch
3. Create feature branches from `develop`
4. Establish release branch workflow
5. Tag releases on `main`

### To Trunk-Based:
1. Merge all long-lived branches
2. Set up comprehensive CI/CD
3. Implement feature flag system
4. Establish short branch time limits
5. Enable auto-merge for passing PRs

## Best Practices (All Strategies)

### Branch Naming
- Use consistent prefixes
- Include issue/ticket numbers
- Keep names short but descriptive
- Use lowercase and hyphens

### Code Review
- Require PR reviews before merge
- Use automated checks (CI, linting)
- Keep PRs small and focused
- Review promptly

### Branch Hygiene
- Delete merged branches
- Clean up stale branches regularly
- Use branch protection rules
- Monitor branch age

### Testing
- Run tests on every branch
- Block merges on test failures
- Maintain high test coverage
- Include integration tests

## Related Resources

- [gitflow-guide.md](./gitflow-guide.md) - Detailed Gitflow workflow
- [github-flow-guide.md](./github-flow-guide.md) - GitHub Flow best practices
- [worktree-patterns.md](./worktree-patterns.md) - Git worktree patterns
