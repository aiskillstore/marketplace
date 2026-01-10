# Conventional Commits Specification

A specification for adding human and machine readable meaning to commit messages.

## Summary
The commit message should be structured as follows:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

## Types
- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Formatting, missing semi-colons, etc. (no code change)
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **perf**: A code change that improves performance
- **test**: Adding missing tests or correcting existing tests
- **build**: Changes that affect the build system or external dependencies
- **ci**: Changes to CI configuration files and scripts
- **chore**: Other changes that don't modify src or test files
- **revert**: Reverts a previous commit

## Description
- Use the imperative, present tense: "change" not "changed" nor "changes"
- Don't capitalize first letter
- Don't put a period at the end

## Body
- Optional, can be multiple paragraphs
- Use to explain the problem and solution
- Use to explain "why" not "what"
- Wrap at 72 characters

## Footer
- Optional
- Contains metadata about the commit
- Common formats:
  - `BREAKING CHANGE: <description>`
  - `Closes #123`
  - `Fixes #456`
  - `Refs #789`

## Examples

### Commit message with description and breaking change footer
```
feat: allow provided config object to extend other configs

BREAKING CHANGE: `extends` key in config file is now used for extending other config files
```

### Commit message with no body
```
docs: correct spelling of CHANGELOG
```

### Commit message with multi-paragraph body and multiple footers
```
fix: prevent racing of requests

Introduce a request id and a reference to latest request. Dismiss
incoming responses other than most recent one.

BREAKING CHANGE: `window.addEventListener` no longer returns a promise
Closes #123
Refs #456
```
