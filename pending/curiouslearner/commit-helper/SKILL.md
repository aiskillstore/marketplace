---
name: commit-helper
description: Intelligent commit message generation following conventional commit format.
---

# Commit Helper Skill

Intelligent commit message generation following conventional commit format.

## Instructions

You are a git commit message expert. When invoked:

1. **Review Changes**: Analyze staged changes using `git diff --staged`
2. **Categorize Changes**: Determine the commit type:
   - `feat`: New feature
   - `fix`: Bug fix
   - `docs`: Documentation only
   - `style`: Code style (formatting, missing semicolons, etc.)
   - `refactor`: Code refactoring (no functional changes)
   - `perf`: Performance improvements
   - `test`: Adding or updating tests
   - `chore`: Maintenance tasks (deps, build, etc.)
   - `ci`: CI/CD changes
   - `revert`: Revert a previous commit

3. **Identify Scope**: Determine the affected component/module (optional but recommended)

4. **Write Message**: Generate a commit message following this format:
   ```
   <type>(<scope>): <subject>

   <body>

   <footer>
   ```

5. **Review History**: Check recent commits with `git log --oneline -10` to match the project's style

## Commit Message Rules

- **Subject line**:
  - Max 50 characters
  - Imperative mood ("add" not "added" or "adds")
  - No period at the end
  - Lowercase after type (e.g., "feat: add user authentication")

- **Body** (optional):
  - Wrap at 72 characters
  - Explain the "what" and "why", not the "how"
  - Separate from subject with blank line

- **Footer** (optional):
  - Reference issues: `Fixes #123`
  - Breaking changes: `BREAKING CHANGE: description`

## Usage Examples

```
@commit-helper
@commit-helper --scope api
@commit-helper --type fix
```

## Example Commits

```
feat(auth): add JWT token refresh mechanism

Implement automatic token refresh to improve user experience
and reduce authentication failures.

- Add refresh token endpoint
- Update auth middleware to handle token expiry
- Add token refresh logic to client

Fixes #456
```

```
fix(validation): handle null values in email validator

Previous implementation threw error on null input.
Now returns false for null/undefined values.
```

```
docs: update API documentation for v2 endpoints
```

## Notes

- Analyze the actual code changes, don't just describe file names
- Focus on the user-facing impact
- Keep messages clear and concise
- Follow existing project commit conventions
- Never include implementation details in the subject line
