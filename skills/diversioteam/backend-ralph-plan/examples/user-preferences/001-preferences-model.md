# 001 - Preferences Model

## Goal

Create the database model and schema for storing user preferences with sensible
defaults and type-safe access.

## Dependencies

- Requires: None (foundation task)
- Blocks: 002, 003

## Scope

**In scope:**
- JSONField on User model for preference storage
- Pydantic schema for preference validation
- Default preferences constant
- Migration for new field

**Out of scope:**
- API endpoints (task 003)
- Caching (task 004)
- Preference change history

## Checklist

- [ ] Add `preferences` JSONField to User model with default=dict
- [ ] Create `accounts/preferences/schemas.py` with Pydantic models:
  - `NotificationPreferences` (email_enabled, slack_enabled, digest_frequency)
  - `ThemePreferences` (mode: light/dark/system, accent_color)
  - `LocalePreferences` (language, timezone, date_format)
  - `UserPreferences` (combines all above)
- [ ] Create `accounts/preferences/defaults.py` with DEFAULT_PREFERENCES constant
- [ ] Add `get_preferences()` method to User model returning validated schema
- [ ] Add `update_preferences()` method with partial update support
- [ ] Create migration for preferences field

## Tests

- [ ] `test_user_has_default_preferences` - new user has defaults
- [ ] `test_get_preferences_returns_schema` - returns Pydantic model
- [ ] `test_update_preferences_partial` - can update single preference
- [ ] `test_update_preferences_validates` - invalid values rejected
- [ ] `test_preferences_schema_validation` - schema rejects bad data

Run: `.bin/pytest accounts/tests/preferences/test_model.py -v --dc=TestLocalApp`

## Completion Criteria

- [ ] All checklist items complete
- [ ] All 5 tests pass
- [ ] Coverage ≥90% on `accounts/preferences/`
- [ ] `.bin/ruff check accounts/preferences/` passes
- [ ] `.bin/ty accounts/preferences/` passes
- [ ] Migration runs without errors
- [ ] No TODO/FIXME comments

## Notes

- Use `pydantic.BaseModel` with `model_validate()` for schema validation
- JSONField should use `default=dict` not `default={}`
- Consider using `functools.cached_property` for `get_preferences()` performance
