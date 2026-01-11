# Conventional Commits Specification

## Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

## Types

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Changes that do not affect the meaning of the code (white-space, formatting, etc)
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **perf**: A code change that improves performance
- **test**: Adding missing tests or correcting existing tests
- **chore**: Changes to the build process or auxiliary tools
- **ci**: Changes to CI configuration files and scripts
- **build**: Changes that affect the build system or external dependencies
- **revert**: Reverts a previous commit

## Scope

Optional. Indicates the area of the codebase affected.

Examples: api, ui, auth, database, docs

## Subject

- Use imperative, present tense: "change" not "changed" nor "changes"
- Don't capitalize first letter
- No period (.) at the end
- Maximum 50 characters

## Body

- Use imperative, present tense
- Explain **what** and **why** vs. how
- Wrap at 72 characters

## Footer

- **BREAKING CHANGE**: describes breaking changes
- **Closes #N**: closes issue N
- **Ref #N**: references issue N

## Examples

### Simple Feature

```
feat(auth): add JWT token authentication

Implements JWT-based authentication for API endpoints.
Tokens expire after 24 hours.
```

### Bug Fix with Issue

```
fix(api): resolve user validation error

The user validation was failing for emails with plus signs.
Fixed regex pattern to allow all valid email formats.

Closes #156
```

### Breaking Change

```
feat(api)!: change authentication endpoint

BREAKING CHANGE: The /auth endpoint now requires OAuth2.
Update all clients to use the new OAuth2 flow at /oauth/token.
```

### Multiple Issues

```
fix(validation): resolve input validation errors

Fixes multiple validation issues across user forms.

Closes #123, closes #124, closes #125
```

## Best Practices

1. **Be atomic**: One logical change per commit
2. **Be specific**: Clearly describe what changed
3. **Link issues**: Always reference related issues
4. **Explain why**: Body should explain rationale
5. **Breaking changes**: Always document in footer
