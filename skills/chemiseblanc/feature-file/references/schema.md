# Feature File Schema Reference

Complete documentation for `features.yml` format.

## File Structure

Multi-document YAML file with `---` separators. Each document represents one feature.

```yaml
feature: "Feature Name"
phase: Requirements
version: 1
changelog: |
  ## [1]
  ### Added
  - Initial feature
requirements:
  req-id:
    description: "Requirement description"
    status: Not-Started
---
feature: "Second Feature"
# ...
```

## Feature-Level Fields

### `feature` (required)
- **Type**: string
- **Description**: Name or brief description of the feature
- **Example**: `"User Authentication System"` or multiline with `|`

### `phase` (required)
- **Type**: enum
- **Values**: `Requirements` | `Design` | `Implementation` | `Testing` | `Complete`
- **Description**: Current waterfall phase of the feature

### `version` (required)
- **Type**: integer
- **Description**: Version number, incremented when shipping milestones
- **Example**: `1`, `2`, `3`

### `changelog` (required)
- **Type**: multiline string
- **Description**: Keepachangelog-style log, organized by version
- **Format**:
  ```yaml
  changelog: |
    ## [3]
    ### Added
    - New capability
    ### Changed
    - Modified behavior
    ### Removed
    - Deprecated feature
    ### Fixed
    - Bug fix
    
    ## [2]
    ### Added
    - Previous addition
  ```

### `decisions` (optional)
- **Type**: list of strings
- **Description**: Architectural and design decisions made for this feature
- **Example**:
  ```yaml
  decisions:
    - Use bcrypt for password hashing over argon2 (library compatibility)
    - JWT tokens for session management
  ```

### `known-issues` (optional)
- **Type**: list of strings
- **Description**: Known bugs, limitations, or technical debt
- **Example**:
  ```yaml
  known-issues:
    - Session refresh race condition under high load
    - Mobile layout not optimized for tablets
  ```

### `requirements` (required)
- **Type**: map of requirement objects
- **Description**: Requirements for this feature, keyed by unique ID
- **Key format**: Use descriptive IDs like `req-auth-login`, `req-api-rate-limit`

### `test-cases` (optional)
- **Type**: map of test-case objects
- **Description**: Test cases linked to requirements, keyed by unique ID
- **Key format**: Use descriptive IDs like `test-login-success`, `test-rate-limit-exceeded`

## Requirement Fields

Each requirement is keyed by a unique ID under `requirements:`.

### `description` (required)
- **Type**: string
- **Description**: Requirement statement, preferably using EARS syntax
- **EARS patterns**:
  - Ubiquitous: "The system SHALL [action]"
  - Event-driven: "When [event], the system SHALL [action]"
  - State-driven: "While [state], the system SHALL [action]"
  - Optional: "Where [condition], the system SHALL [action]"
- **Example**: `"When the user submits valid credentials, the system SHALL authenticate and create a session"`

### `status` (required)
- **Type**: enum
- **Values**: `Not-Started` | `In-Progress` | `Needs-Work` | `Complete`
- **Description**: Current status of this requirement

### `tested-by` (optional)
- **Type**: list of test-case IDs
- **Description**: References to test-cases that verify this requirement
- **Example**: `[test-login-success, test-login-invalid]`

## Test-Case Fields

Each test-case is keyed by a unique ID under `test-cases:`.

### `name` (required)
- **Type**: string
- **Description**: Test function name as it appears in code (for filtering/running)
- **Example**: `"test_login_with_valid_credentials"`

### `file` (required)
- **Type**: string
- **Description**: Path to source file containing the test
- **Example**: `"tests/test_auth.py"`

### `description` (required)
- **Type**: string
- **Description**: Human-readable test description, preferably Given/When/Then
- **Example**: `"Given valid credentials, when login is attempted, then a session is created"`

### `passing` (required)
- **Type**: boolean
- **Values**: `true` | `false`
- **Description**: Whether the test is currently passing

### `type` (optional)
- **Type**: string or list of strings
- **Description**: Category/categories of test for reporting breakdown
- **Examples**: 
  - `type: unit`
  - `type: [integration, rainy-day]`
  - `type: [unit, failure-simulation]`
- **Default**: Tests without type (or with empty list) are grouped as "Uncategorized"
- **Note**: Types are case-insensitive. A test can belong to multiple types; the breakdown counts such tests in each applicable type (category totals may exceed actual test count).

## Phase Transition Rules

Validation rules enforced when checking phase validity:

| Current Phase | Next Phase | Conditions |
|---------------|------------|------------|
| Requirements | Design | All requirements have non-empty `description` |
| Design | Implementation | At least one decision in `decisions` list, OR explicit empty list `[]` |
| Implementation | Testing | All requirements are `In-Progress` or `Complete` |
| Testing | Complete | All requirements are `Complete` AND all linked tests have `passing: true` |

## Status Definitions

| Status | Meaning |
|--------|---------|
| `Not-Started` | Work has not begun on this requirement |
| `In-Progress` | Currently being worked on |
| `Needs-Work` | Was started but needs additional work (bugs, incomplete) |
| `Complete` | Requirement is fully implemented and verified |

## Complete Example

```yaml
feature: "User Authentication System"
phase: Implementation
version: 3
changelog: |
  ## [3]
  ### Added
  - OAuth2 support for Google
  ### Fixed
  - Session timeout now properly invalidates tokens

  ## [2]
  ### Added
  - Password reset flow
  
  ## [1]
  ### Added
  - Basic login/logout functionality

decisions:
  - Use bcrypt for password hashing over argon2 (library compatibility)
  - JWT tokens with 24h expiry for session management
  - Store refresh tokens in httpOnly cookies

known-issues:
  - Session refresh race condition under high load

requirements:
  req-auth-login:
    description: "When the user submits valid credentials, the system SHALL authenticate and create a session"
    status: Complete
    tested-by: [test-login-success, test-login-invalid]
  
  req-auth-logout:
    description: "When the user clicks logout, the system SHALL invalidate the session"
    status: Complete
    tested-by: [test-logout]

  req-auth-oauth:
    description: "The system SHALL support OAuth2 authentication with Google and GitHub"
    status: In-Progress
    tested-by: [test-oauth-google]

test-cases:
  test-login-success:
    name: "test_login_with_valid_credentials"
    file: "tests/test_auth.py"
    description: "Given valid credentials, when login is attempted, then a session is created"
    passing: true
    type: unit

  test-login-invalid:
    name: "test_login_with_invalid_credentials"
    file: "tests/test_auth.py"
    description: "Given invalid credentials, when login is attempted, then authentication fails with 401"
    passing: true
    type: [unit, rainy-day]

  test-logout:
    name: "test_logout_invalidates_session"
    file: "tests/test_auth.py"
    description: "Given an active session, when logout is called, then the session token is invalidated"
    passing: true
    type: integration

  test-oauth-google:
    name: "test_oauth_google_flow"
    file: "tests/test_oauth.py"
    description: "Given a valid Google OAuth code, when exchanged, then user is authenticated"
    passing: false
    type: [integration, e2e]
---
feature: "API Rate Limiting"
phase: Design
version: 1
changelog: |
  ## [1]
  ### Added
  - Initial rate limiting design

decisions:
  - Use sliding window algorithm over fixed window (smoother limiting)
  - Store counters in Redis for distributed support

requirements:
  req-rate-limit:
    description: "The system SHALL limit API requests to 100 per minute per user"
    status: Not-Started
    tested-by: []

  req-rate-headers:
    description: "The system SHALL include X-RateLimit-* headers in all API responses"
    status: Not-Started
    tested-by: []
```
