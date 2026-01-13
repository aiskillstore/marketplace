# 002 - Preferences Service

## Goal

Create a service layer for preference operations with validation, defaults
merging, and clean separation from the model.

## Dependencies

- Requires: 001 (Preferences Model)
- Blocks: 003, 004

## Scope

**In scope:**
- `PreferencesService` class with get/update methods
- Deep merge of user preferences with defaults
- Validation via Pydantic schemas
- Preference key enumeration for type safety

**Out of scope:**
- API layer (task 003)
- Caching (task 004)
- Bulk operations

## Checklist

- [ ] Create `accounts/preferences/service.py` with `PreferencesService`
- [ ] Implement `get_preferences(user) -> UserPreferences`
- [ ] Implement `update_preferences(user, updates: dict) -> UserPreferences`
- [ ] Implement `reset_preferences(user, keys: list[str] | None)`
- [ ] Add `PreferenceKey` enum for valid preference paths
- [ ] Handle nested preference updates (e.g., `notifications.email_enabled`)
- [ ] Return full preferences after any update

## Tests

- [ ] `test_get_preferences_merges_defaults` - missing keys filled from defaults
- [ ] `test_update_nested_preference` - can update `notifications.email_enabled`
- [ ] `test_update_invalid_key_raises` - unknown keys rejected
- [ ] `test_update_invalid_value_raises` - type mismatches rejected
- [ ] `test_reset_preferences_single_key` - reset one key to default
- [ ] `test_reset_preferences_all` - reset all to defaults
- [ ] `test_preference_key_enum_complete` - enum has all valid keys

Run: `.bin/pytest accounts/tests/preferences/test_service.py -v --dc=TestLocalApp`

## Completion Criteria

- [ ] All checklist items complete
- [ ] All 7 tests pass
- [ ] Coverage ≥90% on `accounts/preferences/service.py`
- [ ] `.bin/ruff check accounts/preferences/` passes
- [ ] `.bin/ty accounts/preferences/` passes
- [ ] No TODO/FIXME comments

## Notes

- Use `pydantic.model_copy(update=...)` for partial updates
- Nested key paths like `notifications.email_enabled` should use dot notation
- Service should be stateless - instantiate per request or use class methods
