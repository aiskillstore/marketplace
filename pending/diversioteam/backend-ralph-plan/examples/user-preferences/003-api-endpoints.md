# 003 - API Endpoints

## Goal

Expose REST API endpoints for reading and updating user preferences using
Django Ninja.

## Dependencies

- Requires: 001 (Preferences Model), 002 (Preferences Service)
- Blocks: None

## Scope

**In scope:**
- GET `/api/users/me/preferences/` - retrieve current preferences
- PATCH `/api/users/me/preferences/` - partial update preferences
- POST `/api/users/me/preferences/reset/` - reset to defaults
- Request/response schemas with validation

**Out of scope:**
- Bulk operations for multiple users
- Preference history/audit log
- Admin endpoints

## Checklist

- [ ] Create `accounts/api/preferences.py` with Django Ninja router
- [ ] Implement GET endpoint returning `UserPreferences` schema
- [ ] Implement PATCH endpoint accepting partial preference updates
- [ ] Implement POST reset endpoint with optional `keys` parameter
- [ ] Add authentication requirement (`auth=django_auth`)
- [ ] Register router in main API configuration

## Tests

- [ ] `test_get_preferences_authenticated` - returns current preferences
- [ ] `test_get_preferences_unauthenticated` - returns 401
- [ ] `test_patch_preferences_partial` - updates single field
- [ ] `test_patch_preferences_invalid` - rejects bad values
- [ ] `test_reset_preferences_all` - resets to defaults
- [ ] `test_reset_preferences_single_key` - resets specific key

Run: `.bin/pytest accounts/tests/preferences/test_api.py -v --dc=TestLocalApp`

## Completion Criteria

- [ ] All checklist items complete
- [ ] All 6 tests pass
- [ ] Coverage ≥90% on `accounts/api/preferences.py`
- [ ] `.bin/ruff check accounts/api/` passes
- [ ] `.bin/ty accounts/api/` passes
- [ ] OpenAPI schema includes new endpoints
- [ ] No TODO/FIXME comments

## Notes

- Use `@router.get`, `@router.patch`, `@router.post` decorators
- Return 404 if user somehow has no preferences (shouldn't happen with defaults)
- Validate preference keys in PATCH to prevent arbitrary JSON injection
