# 004 - Caching Layer

## Goal

Add Redis caching to the preferences service for improved read performance.

## Dependencies

- Requires: 002 (Preferences Service)
- Blocks: None

## Scope

**In scope:**
- Cache preferences in Redis with 5-minute TTL
- Cache invalidation on preference updates
- Fallback to database on cache miss
- Cache key format: `user:{user_id}:preferences`

**Out of scope:**
- Cache warming on application start
- Distributed cache invalidation (single Redis instance assumed)
- Cache statistics/monitoring

## Checklist

- [ ] Add `get_cached_preferences(user_id)` to service
- [ ] Add `invalidate_preferences_cache(user_id)` to service
- [ ] Update `get_preferences()` to check cache first
- [ ] Update `update_preferences()` to invalidate cache after update
- [ ] Update `reset_preferences()` to invalidate cache after reset
- [ ] Configure cache TTL as setting (default 300 seconds)

## Tests

- [ ] `test_get_preferences_cache_hit` - returns cached value without DB query
- [ ] `test_get_preferences_cache_miss` - fetches from DB and caches
- [ ] `test_update_preferences_invalidates_cache` - cache cleared on update
- [ ] `test_reset_preferences_invalidates_cache` - cache cleared on reset
- [ ] `test_cache_ttl_expiry` - cached value expires after TTL

Run: `.bin/pytest accounts/tests/preferences/test_caching.py -v --dc=TestLocalApp`

## Completion Criteria

- [ ] All checklist items complete
- [ ] All 5 tests pass
- [ ] Coverage ≥90% on caching code
- [ ] `.bin/ruff check accounts/preferences/` passes
- [ ] `.bin/ty accounts/preferences/` passes
- [ ] No TODO/FIXME comments

## Notes

- Use Django's cache framework with Redis backend
- Cache key should include a version prefix for easy invalidation on schema changes
- Consider using `cache.get_or_set()` for atomic get-and-cache operation
- Test with `@override_settings(CACHES=...)` to use local memory cache in tests
