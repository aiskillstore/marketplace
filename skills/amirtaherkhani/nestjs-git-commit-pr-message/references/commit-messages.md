# Commit Messages

Describe the actual staged diff in the repository's established voice.

## Conventional Commit selection

| Type | Use for |
| --- | --- |
| `feat` | A user- or developer-visible capability |
| `fix` | Correcting faulty behavior |
| `docs` | Documentation-only changes |
| `test` | Test-only changes |
| `refactor` | Structural change without behavior change |
| `perf` | Measured performance improvement |
| `build` | Build system or packaged dependencies |
| `ci` | Automation and pipeline changes |
| `chore` | Maintenance not covered above |
| `style` | Formatting without semantic change |

Use the narrowest meaningful scope, commonly a NestJS feature module or package. Omit the scope for truly cross-cutting work. Do not list multiple scopes merely to reproduce every touched directory.

## Quality rules

- Use an imperative subject such as `add`, `prevent`, or `document`.
- Keep the subject concise and compatible with repository limits.
- Explain what and why in the body for non-trivial changes.
- Do not claim tests, migrations, security fixes, or breaking changes that the diff does not establish.
- Use `BREAKING CHANGE:` only for an incompatible public contract, configuration, schema, or operational requirement.
- Match existing capitalization, punctuation, body wrapping, and merge conventions.

## Ticket references

Use only identifiers supplied by the user or verified from the task context.

```text
Closes #42
Fixes owner/repository#87
PROJ-1234
```

Closing keywords should be used only when the change fully resolves the issue and the PR targets the repository's default branch. A bare `Ref #42` links related work without promising automatic closure.

## Examples

```text
feat(payments): add idempotent capture endpoint

Preserve the existing payment contract while rejecting conflicting
replays and returning the original result for duplicate requests.
```

```text
fix(auth): enforce tenant ownership before resource updates

Resolve the authenticated tenant from the request context and verify
resource ownership before invoking the update use case.

Fixes #87
```

```text
ci(docs): verify generated skill references before Pages deploy
```
