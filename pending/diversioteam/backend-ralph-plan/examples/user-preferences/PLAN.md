# User Preferences API

> **Status:** `in-progress`
> **Created:** 2026-01-06
> **Last Updated:** 2026-01-06

## Quick Start

```
/plan-directory:run user-preferences
```

Or with custom iteration limit:
```
/plan-directory:run user-preferences --max-iterations 50
```

## Overview

Add a user preferences API allowing users to configure notification settings,
theme preferences, and locale options.

## Goals

1. Store user preferences in database with sensible defaults
2. Expose REST API for reading/updating preferences
3. Validate preference values against allowed options
4. Cache preferences for performance

## Locked Decisions

- Use existing `User` model (no separate preferences table initially)
- JSON field for flexible preference storage
- Redis cache with 5-minute TTL
- Django Ninja for API endpoints

## Execution Order

| Order | Task | Dependencies | Critical Path |
|-------|------|--------------|---------------|
| 1 | 001 - Preferences Model | None | **Foundation** |
| 2 | 002 - Preferences Service | 001 | Core logic |
| 3 | 003 - API Endpoints | 001, 002 | |
| 4 | 004 - Caching Layer | 002 | Performance |

## Tasks

| # | Task | Status | File |
|---|------|--------|------|
| 001 | Preferences Model | `in-progress` | [001-preferences-model.md](./001-preferences-model.md) |
| 002 | Preferences Service | `pending` | [002-preferences-service.md](./002-preferences-service.md) |
| 003 | API Endpoints | `pending` | [003-api-endpoints.md](./003-api-endpoints.md) |
| 004 | Caching Layer | `pending` | [004-caching-layer.md](./004-caching-layer.md) |

## Progress

**Completed: 0/4 tasks (0%)**

```
[░░░░░░░░░░] 0%
```

## Task Completion Tracker

| Task | Status | Lint | Types | Tests | Coverage | Regression |
|------|--------|------|-------|-------|----------|------------|
| 001 - Model | `in-progress` | | | | | |
| 002 - Service | | | | | | |
| 003 - API | | | | | | |
| 004 - Cache | | | | | | |

## Quality Gates

| Gate | Command | Requirement |
|------|---------|-------------|
| Pre-commit | `/pre-commit` | All hooks pass |
| Lint | `.bin/ruff check accounts/preferences/` | Zero errors |
| Types | `.bin/ty accounts/preferences/` | Zero errors |
| Tests | `.bin/pytest -k "preferences" --dc=TestLocalApp` | 100% pass |
| Coverage | `--cov=accounts/preferences/` | ≥90% |
| Django | `.bin/django check` | No issues |

## Final Validation Checklist

**Task Completion:**
- [ ] 001 - Preferences Model: `completed` with all checks
- [ ] 002 - Preferences Service: `completed` with all checks
- [ ] 003 - API Endpoints: `completed` with all checks
- [ ] 004 - Caching Layer: `completed` with all checks

**Quality Gates:**
- [ ] `.bin/ruff check accounts/preferences/` → zero errors
- [ ] `.bin/ty accounts/preferences/` → zero errors
- [ ] `.bin/pytest accounts/tests/preferences/ -k "preferences" --dc=TestLocalApp` → all pass
- [ ] `.bin/django check` → no issues

**Code Quality:**
- [ ] `! grep -rE "TODO|FIXME|XXX|HACK|noqa|type: ignore" accounts/preferences/` → no matches

## Follow-ups (Not in Scope)

- Preference sync across devices
- Preference export/import
- Admin UI for viewing user preferences
- Preference change audit log

## Notes

- Preference schema defined in `accounts/preferences/schemas.py`
- Default preferences in `accounts/preferences/defaults.py`
- All preference keys must be documented
