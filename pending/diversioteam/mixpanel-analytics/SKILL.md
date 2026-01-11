---
name: mixpanel-analytics
description: >
  MixPanel analytics tracking implementation and review Skill for Django4Lyfe
  optimo_analytics module. Implements new events following established patterns
  and reviews implementations for PII protection, schema design, and code quality.
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
  - Glob
  - Grep
  - TodoWrite
---

# MixPanel Analytics Skill

## When to Use This Skill

Use this Skill in the Django4Lyfe backend when working with MixPanel analytics
tracking in the `optimo_analytics` module:

- `/mixpanel-analytics:implement` – to **implement** new MixPanel tracking events
  or update existing ones following established patterns (7-step checklist).
- `/mixpanel-analytics:review` – to **review** MixPanel implementations for
  correctness, PII protection, and adherence to Django4Lyfe standards.

## Example Prompts

### Implement Mode

- "Use `/mixpanel-analytics:implement` to add a new event for tracking when a
  user completes their profile setup."
- "Run `/mixpanel-analytics:implement svc.surveys.reminder_sent` to add tracking
  for survey reminder notifications."
- "Implement MixPanel tracking for the new HRIS CSV validation feature using
  `/mixpanel-analytics:implement`."

### Review Mode

- "Run `/mixpanel-analytics:review staged` to check my staged MixPanel changes
  for PII violations and pattern compliance."
- "Use `/mixpanel-analytics:review branch` to audit all analytics changes on
  this feature branch."
- "Review the entire optimo_analytics module with `/mixpanel-analytics:review all`."

## Modes

This Skill behaves differently based on how it is invoked:

- `implement` mode – invoked via `/mixpanel-analytics:implement`:
  - Guides implementation of new MixPanel events through 7 steps.
  - Creates constants, schemas, registry entries, service methods, and tests.
  - Enforces PII protection and code patterns.
- `review` mode – invoked via `/mixpanel-analytics:review`:
  - Audits existing implementations for compliance.
  - Checks PII protection, schema design, service patterns, and test coverage.
  - Generates structured review reports with severity tags.

## Environment & Context Gathering

When this Skill runs, gather context first:

```bash
# Git context
git branch --show-current
git status --porcelain
git diff --cached --name-only | grep -E "optimo_analytics|mixpanel"

# Analytics module stats
grep -c "^    [A-Z_]* = " optimo_analytics/constants.py 2>/dev/null || echo "0"
grep -c "^class Mxp" optimo_analytics/schemas.py 2>/dev/null || echo "0"
grep -c "MixPanelEvent\." optimo_analytics/registry.py 2>/dev/null || echo "0"
ls -1 optimo_analytics/service/*.py 2>/dev/null | xargs -I{} basename {} .py
```

Read key reference files:
- `optimo_analytics/AGENTS.md` – module-level rules and PII guidelines
- `optimo_analytics/schemas.py` – existing schema patterns
- `optimo_analytics/service/AGENTS.md` – service layer patterns
- `optimo_analytics/tests/AGENTS.md` – test patterns

---

# Implementation Mode

## 7-Step Implementation Checklist

For each new event, complete these steps in order:

### Step 1: Add Event Constant (`optimo_analytics/constants.py`)

```python
# Event naming convention: {prefix}.{object}.{action}[.error]
# Examples:
#   - svc.surveys.survey_delivered
#   - svc.map.action_plan_created
#   - svc.hris_csv.upload.analysis_completed
#
# NOTE: Do NOT include "cron" in event names - use is_cron_job property instead

class MixPanelEvent:
    # Add under appropriate section with comment
    NEW_EVENT_NAME = "svc.domain.action_name"
```

### Step 2: Create Schema (`optimo_analytics/schemas.py`)

```python
# Schema naming: Mxp{Domain}{Action}EventSchema
# CRITICAL RULES:
#   - All UUIDs MUST be strings (str, not UUID)
#   - NO PII: no names, emails, phone numbers
#   - organization_name IS allowed (business approved)
#   - Use STRICT_MODEL_CONFIG (no aliases) or ALIASED_MODEL_CONFIG ($ aliases)

class MxpNewEventSchema(MixpanelSuperEventPropertiesSchema):
    """Properties for svc.domain.action_name event.

    Tracked when [describe when this event fires].
    """

    # Required fields (no defaults)
    employee_id: str = Field(description="Employee UUID as string")
    organization_id: str = Field(description="Organization UUID as string")
    organization_name: str = Field(description="Organization name for analytics")
    role: SystemRole | None = Field(description="User role")
    impersonation: bool = Field(description="Is impersonated session")

    # Event-specific fields
    custom_field: str = Field(description="What this field represents")

    # Use STRICT_MODEL_CONFIG for internal-only schemas
    # Use ALIASED_MODEL_CONFIG when field names need $ prefix for MixPanel (e.g., $device_id)
    model_config = STRICT_MODEL_CONFIG
```

### Step 3: Register in Registry (`optimo_analytics/registry.py`)

```python
# Add import at top
from optimo_analytics.schemas import MxpNewEventSchema

# Add to _EVENT_SCHEMA_REGISTRY dict
_EVENT_SCHEMA_REGISTRY: dict[str, type[MixpanelSuperEventPropertiesSchema]] = {
    # ... existing entries ...
    MixPanelEvent.NEW_EVENT_NAME: MxpNewEventSchema,
}
```

### Step 4: Add Tracking Helper (`optimo_analytics/service/{domain}.py`)

Choose appropriate service file or create new one:
- `auth.py` - Authentication events
- `survey.py` - Survey lifecycle events
- `risk.py` - Risk calculation events
- `map.py` - Manager Action Pipeline events
- `core.py` - Core/HRIS events

```python
class OptimoMixpanel{Domain}TrackHelper:
    """Helper class for {Domain} event tracking."""

    @classmethod
    def track_new_event(
        cls,
        *,  # CRITICAL: Force keyword-only arguments
        employee_id: str,
        # ... other params ...
    ) -> None:
        """
        Track new event (svc.domain.action_name).

        Tracked when [describe trigger condition].

        Args:
            employee_id: Employee UUID as string
        """
        try:
            cls._track_new_event(
                employee_id=employee_id,
                # ... pass all args ...
            )
        except Exception:
            # Fire-and-forget: log but don't propagate
            logger.exception(
                "mixpanel_new_event_tracking_failed",
                employee_id=employee_id,
            )

    @staticmethod
    def _track_new_event(
        *,
        employee_id: str,
        # ... other params ...
    ) -> None:
        """Track new event implementation."""
        emp_info = OptimoMixpanelService._fetch_required_emp_info(
            employee_id=employee_id
        )

        properties = MxpNewEventSchema(
            employee_id=employee_id,
            organization_id=str(emp_info.organization.uuid),
            organization_name=emp_info.organization.name,
            role=emp_info.role,
            impersonation=False,
            # ... event-specific fields ...
        )

        # distinct_id fallback hierarchy:
        # 1. User's UUID (primary)
        # 2. org_<organization_uuid> (fallback when no user)
        # 3. Context-specific: slack_<id>, apikey_<id>, webhook_<id>
        distinct_id = employee_id  # or f"org_{org_uuid}" if no user
        OptimoMixpanelService.track_event(
            distinct_id=distinct_id,
            event_name=MixPanelEvent.NEW_EVENT_NAME,
            properties=properties,
        )
```

### Step 5: Export from `__init__.py` (`optimo_analytics/service/__init__.py`)

```python
# Add to imports
from optimo_analytics.service.{domain} import OptimoMixpanel{Domain}TrackHelper

# Add to __all__
__all__ = [
    # ... existing ...
    "OptimoMixpanel{Domain}TrackHelper",
]
```

### Step 6: Add Tests (`optimo_analytics/tests/test_{event}_event.py`)

```python
"""Tests for {Event} MixPanel tracking."""

from unittest.mock import patch
from uuid import uuid4

import pytest

from optimo_analytics.constants import MixPanelEvent
from optimo_analytics.registry import EVENT_SCHEMA_REGISTRY, is_event_registered
from optimo_analytics.schemas import MxpNewEventSchema
from optimo_analytics.service import OptimoMixpanel{Domain}TrackHelper

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def eager_jobs(settings):
    """Force synchronous job execution."""
    settings.OPTIMO_JOBS_EAGER_MODE = True
    yield
    settings.OPTIMO_JOBS_EAGER_MODE = False


@pytest.fixture
def mock_mixpanel():
    """Mock MixPanel client."""
    with patch("optimo_analytics.service.MixPanelFactory.get_client") as mock:
        yield mock.return_value


class TestNewEventSchema:
    """Test schema validation."""

    def test_schema_creation_with_valid_properties(self):
        """Schema accepts valid properties."""
        schema = MxpNewEventSchema(
            employee_id=str(uuid4()),
            organization_id=str(uuid4()),
            organization_name="Test Org",
            role=SystemRole.EMPLOYEE,
            impersonation=False,
        )
        assert schema.employee_id is not None


class TestNewEventRegistry:
    """Test registry registration."""

    def test_event_is_registered(self):
        """Event should be registered in schema registry."""
        assert is_event_registered(MixPanelEvent.NEW_EVENT_NAME)
        assert EVENT_SCHEMA_REGISTRY.get(MixPanelEvent.NEW_EVENT_NAME) is MxpNewEventSchema


class TestNewEventTracking:
    """Test service tracking method."""

    def test_tracking_calls_mixpanel(self, mock_mixpanel, optimo_employee):
        """Tracking should call MixPanel with correct properties."""
        OptimoMixpanel{Domain}TrackHelper.track_new_event(
            employee_id=str(optimo_employee.uuid),
        )
        mock_mixpanel.track.assert_called_once()


class TestNewEventNonBlocking:
    """Test fire-and-forget behavior."""

    def test_exception_does_not_propagate(self):
        """Tracking exceptions should be caught and logged."""
        with patch.object(
            OptimoMixpanel{Domain}TrackHelper,
            "_track_new_event",
            side_effect=Exception("boom"),
        ):
            # Should NOT raise
            OptimoMixpanel{Domain}TrackHelper.track_new_event(
                employee_id=str(uuid4()),
            )
```

### Step 7: Integrate with Business Logic

```python
from optimo_analytics.service import OptimoMixpanel{Domain}TrackHelper

def some_business_method(self, ...):
    # ... business logic ...

    # Track after successful operation
    OptimoMixpanel{Domain}TrackHelper.track_new_event(
        employee_id=str(employee.uuid),
    )
```

## Critical Rules (DO NOT VIOLATE)

### PII Protection

- **NEVER** send: names, emails, phone numbers, addresses
- **ALLOWED**: organization_name (business approved for analytics)
- **ALWAYS** use UUIDs as strings for identifiers

### Code Patterns

- **ALWAYS** use keyword-only arguments (`*,` in method signature)
- **ALWAYS** wrap tracking in try-except (fire-and-forget)
- **NEVER** let tracking failures break business logic
- **ALWAYS** use structured logging with IDs only

### Event Naming Convention

```text
{prefix}.{object}.{action}[.error]
```

Examples:
- `svc.surveys.survey_delivered`
- `svc.surveys.survey_delivered.error` (for failures)
- `svc.map.action_plan_created`

**Note**: Do NOT include execution context (like "cron") in event names.
Use `is_cron_job` property instead.

### When to Use `is_cron_job`

**NOT all background jobs need `is_cron_job=True`**. Only set it when you need:

1. **API time and tracking time to align** - the event `time` should reflect
   the original user action, not when the CRON ran
2. **Ordering events with same timestamp** - distinguish CRON-processed events
   from user-triggered ones

**When to set `is_cron_job=True`:**

```python
properties = MxpYourEventSchema(
    # ... other fields ...
    is_cron_job=True,
    cron_execution_timestamp=datetime_to_timestamp_ms(timezone.now()),
)
```

**Validation**: If `is_cron_job=True`, then `cron_execution_timestamp` is
required (enforced by `validate_cron_properties`).

### Schema Field Types

- UUIDs: `str` (never `UUID`)
- Timestamps: Use `datetime_to_timestamp_ms()` for MixPanel
- Enums: Use `SystemRole | None`, etc.
- Lists: `list[str]` for UUID lists

### Optional Values for String Fields

**NEVER override base schema fields as Optional** to handle `None` values. Instead:

- For `str` fields that might have no value, pass **empty string** `""`
- Do NOT duplicate `organization_id`, `organization_name`, `employee_id`, etc.
  with `Optional[str]` types in child schemas
- The base `MixpanelSuperEventPropertiesSchema` already defines these fields -
  inherit them, don't redefine

**BAD** - Don't do this:

```python
class MxpNewEventSchema(MixpanelSuperEventPropertiesSchema):
    # WRONG: duplicating base fields as Optional
    organization_id: str | None = Field(default=None, description="...")
    organization_name: str | None = Field(default=None, description="...")
```

**GOOD** - Do this instead:

```python
class MxpNewEventSchema(MixpanelSuperEventPropertiesSchema):
    # Inherit organization_id, organization_name from base schema
    # Pass empty string when value is not available
    pass

# In service method:
properties = MxpNewEventSchema(
    organization_id=str(org.uuid) if org else "",
    organization_name=org.name if org else "",
    # ...
)

## Post-Implementation Validations

```bash
# 1. Ruff lint and format
.bin/ruff check optimo_analytics/ --fix
.bin/ruff format optimo_analytics/

# 2. Type checking
.bin/ty check optimo_analytics/

# 3. Django checks
DJANGO_CONFIGURATION=DevApp uv run python manage.py check

# 4. Run tests
.bin/pytest optimo_analytics/tests/ -v --dc=TestLocalApp
```

---

# Review Mode

## Review Checklist

### 1. PII Protection (CRITICAL - P0)

**MUST CHECK**:
- [ ] No `first_name`, `last_name`, `full_name`, `display_name` in schemas
- [ ] No `email`, `email_address`, `user_email` fields
- [ ] No `phone`, `phone_number`, `phone_e164` fields
- [ ] No `address`, `city`, `country` as free-text fields
- [ ] All identifiers are UUIDs as strings (not UUID objects)
- [ ] `organization_name` is ONLY sent to MixPanel, never logged

### 2. Event Registration Completeness (P1)

**MUST VERIFY**:
- [ ] Event constant exists in `constants.py` under `MixPanelEvent`
- [ ] Schema class exists in `schemas.py`
- [ ] Event is registered in `registry.py` `_EVENT_SCHEMA_REGISTRY`
- [ ] Schema inherits from `MixpanelSuperEventPropertiesSchema`

### 3. Schema Design (P1)

**MUST VERIFY**:
- [ ] All UUID fields are typed as `str`, not `UUID`
- [ ] All required fields have `Field(description="...")`
- [ ] Uses `STRICT_MODEL_CONFIG` or `ALIASED_MODEL_CONFIG` appropriately
- [ ] Enum fields use `SystemRole | None` pattern
- [ ] Docstring describes when the event is tracked
- [ ] Base schema fields from `MixpanelSuperEventPropertiesSchema` are NOT
      redefined as `Optional[str]` - pass empty string `""` for missing values

### 4. Service Method Patterns (P1)

**MUST VERIFY**:
- [ ] Public method is `@classmethod`
- [ ] Uses keyword-only arguments (`*,` after cls)
- [ ] Has try-except wrapper (fire-and-forget)
- [ ] Exception handler logs with structured fields
- [ ] Private implementation is `@staticmethod`

### 5. Test Coverage (P2)

**MUST HAVE**:
- [ ] Schema validation tests
- [ ] Registry registration test
- [ ] Service tracking test with `mock_mixpanel`
- [ ] Non-blocking test (exception doesn't propagate)
- [ ] Uses `pytestmark = [pytest.mark.django_db]`

### 6. Naming Conventions (P2)

**Event names**: `{prefix}.{object}.{action}[.error]`
**Schema names**: `Mxp{Domain}{Action}EventSchema`
**Helper names**: `OptimoMixpanel{Domain}TrackHelper`

### 7. `is_cron_job` Usage (P2)

**NOTE**: Not all background jobs need `is_cron_job=True`. Only use when:
1. API time and tracking time need to align
2. Events with same timestamp need ordering

**IF `is_cron_job=True` is used, MUST VERIFY**:
- [ ] `cron_execution_timestamp` is provided as Unix milliseconds
- [ ] Event name does NOT contain "cron"

### 8. Timestamp Handling (P2)

**MUST VERIFY**:
- [ ] Uses `datetime_to_timestamp_ms()` for MixPanel timestamps
- [ ] Never sends ISO 8601 strings to MixPanel

### 9. distinct_id Selection (P1)

**distinct_id MUST strictly follow this fallback hierarchy**:

1. **Primary**: User's UUID (the authenticated user performing the action)
2. **Fallback 1**: `org_<organization_uuid>` (when no user context exists)
3. **Fallback 2**: Context-specific ID based on the entity being tracked:
   - Slack workspace: `slack_<slack_workspace_id>`
   - API key: `apikey_<api_key_id>`
   - Webhook: `webhook_<webhook_id>`

**NEVER pass organization_id directly as distinct_id** - always prefix with `org_`.

**MUST VERIFY**:

- [ ] distinct_id is user's UUID when user context is available
- [ ] distinct_id uses `org_<uuid>` prefix when falling back to organization
- [ ] distinct_id uses appropriate prefix for context-specific fallbacks
- [ ] distinct_id is NEVER a raw organization_id without prefix

### 10. Export Completeness (P3)

**MUST VERIFY**:
- [ ] New helper classes exported in `service/__init__.py`
- [ ] Added to `__all__` list

## Automated Checks

```bash
# 1. PII Scan
grep -rn "first_name\|last_name\|email\|phone\|address" optimo_analytics/schemas.py

# 2. UUID Type Check
grep -rn ": UUID" optimo_analytics/schemas.py

# 3. Registration Check
for event in $(grep "^    [A-Z_]* = " optimo_analytics/constants.py | cut -d'=' -f1 | tr -d ' '); do
    grep -q "$event" optimo_analytics/registry.py || echo "UNREGISTERED: $event"
done

# 4. Keyword-only Check
grep -rn "def track_" optimo_analytics/service/*.py | while read line; do
    file=$(echo $line | cut -d: -f1)
    linenum=$(echo $line | cut -d: -f2)
    if ! sed -n "$((linenum+1)),$((linenum+5))p" "$file" | grep -q '\*,'; then
        echo "MISSING *,: $line"
    fi
done
```

## Review Output Format

```markdown
# MixPanel Implementation Review

**Branch**: {branch}
**Scope**: {scope}
**Date**: {date}

## Summary

| Category | Status | Issues |
|----------|--------|--------|
| PII Protection | PASS/FAIL | {count} |
| Event Registration | PASS/FAIL | {count} |
| Schema Design | PASS/FAIL | {count} |
| Service Patterns | PASS/FAIL | {count} |
| Test Coverage | PASS/FAIL | {count} |

## Issues Found

### [P0] CRITICAL - {title}
**File**: `path:line`
**Issue**: Description
**Fix**: How to fix

### [P1] HIGH - {title}
...

## Recommendations

1. ...
2. ...
```

## Severity Tags

- `[P0]` CRITICAL – PII violations, security issues; must fix before merge
- `[P1]` HIGH – Missing registrations, pattern violations; strongly recommended
- `[P2]` MEDIUM – Test coverage gaps, naming issues; should fix
- `[P3]` LOW – Minor improvements; nice to have

---

## Post-Review Actions

After review, if issues found:
1. Create todo list of fixes
2. Apply fixes using `/mixpanel-analytics:implement`
3. Re-run review to verify

If review passes:
1. Run `/monty-code-review:code-review` for general code quality
2. Run `/backend-atomic-commit:pre-commit` for commit preparation
3. Run tests: `.bin/pytest optimo_analytics/tests/ -v --dc=TestLocalApp`

## Compatibility Notes

This skill is designed to work with both **Claude Code** and **OpenAI Codex**.

For Codex users:
- Install via skill-installer with `--repo DiversioTeam/agent-skills-marketplace
  --path plugins/mixpanel-analytics/skills/mixpanel-analytics`.
- Use `$skill mixpanel-analytics` to invoke.

For Claude Code users:
- Install via `/plugin install mixpanel-analytics@diversiotech`.
- Use `/mixpanel-analytics:implement` or `/mixpanel-analytics:review` to invoke.
