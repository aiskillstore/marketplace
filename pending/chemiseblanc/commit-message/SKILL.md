---
name: commit-message
description: Format git commit messages combining Conventional Commits summary lines with Linux kernel-style bodies. Use when writing, reviewing, or formatting commit messages.
---

# Commit Message Formatting

## Summary Line

Use Conventional Commits format:

```
<type>(<scope>): <description>
```

- **type** (required): `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`
- **scope** (optional): component or area affected, in parentheses
- **description**: imperative mood, lowercase start, no period, max 50 chars (hard limit 72)
- For breaking changes: add `!` before colon: `feat(api)!: remove deprecated endpoint`

## Body

Separate from summary with blank line. Follow kernel style:

- Wrap at 72 columns
- Imperative mood ("Add feature" not "Added feature")
- Explain **why**, not what (the diff shows what)
- Describe user-visible impact and motivation
- Quantify improvements with numbers when applicable

When referencing commits, use 12+ char SHA with summary:

```
Commit e21d2170f36602ae2708 ("video: remove unnecessary
platform_set_drvdata()") introduced a regression...
```

## No Trailers

Omit all trailers: no `Signed-off-by`, `Reviewed-by`, `Acked-by`, `Tested-by`, `Cc`, `Fixes`, `Link`, etc.

## Examples

Single-line fix:

```
fix(parser): handle empty input without panic
```

Feature with body:

```
feat(auth): add OAuth2 PKCE flow support

Mobile and SPA clients cannot securely store client secrets. PKCE
allows these clients to authenticate safely without exposing
credentials in client-side code.

This reduces authentication failures for mobile users by eliminating
the insecure implicit flow workaround.
```

Breaking change:

```
feat(api)!: require authentication for all endpoints

Anonymous access created security vulnerabilities and complicated
rate limiting. Requiring auth simplifies the security model and
enables per-user quotas.

Clients must now include a valid Bearer token with every request.
```

Refactor:

```
refactor(db): extract connection pooling into dedicated module

The monolithic database module grew to 2000+ lines, making
maintenance difficult. Separating connection pooling improves
testability and allows independent configuration tuning.
```
