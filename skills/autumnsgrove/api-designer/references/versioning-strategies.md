# API Versioning Strategies

Comprehensive guide to versioning APIs, managing breaking changes, and deprecating old versions.

## Table of Contents

- [Versioning Approaches](#versioning-approaches)
- [When to Version](#when-to-version)
- [Deprecation Process](#deprecation-process)
- [Migration Strategies](#migration-strategies)
- [Best Practices](#best-practices)

## Versioning Approaches

### URL Versioning

**Pattern**: Include version in URL path

```
https://api.example.com/v1/users
https://api.example.com/v2/users
https://api.example.com/v3/users
```

**Pros**:
- Very explicit and visible
- Easy to route to different codebases
- Simple to understand for developers
- Good for major breaking changes
- Easy to cache (different URLs)
- Browser-testable

**Cons**:
- URL proliferation
- Requires maintaining multiple codebases
- Can lead to code duplication
- Makes it harder to sunset old versions

**When to Use**:
- Major version changes with significant breaking changes
- When you need to maintain multiple versions long-term
- Public APIs consumed by many clients
- When you want maximum clarity

**Implementation Example**:
```python
# Flask example
from flask import Flask

app = Flask(__name__)

# Version 1
@app.route('/v1/users')
def get_users_v1():
    return {"users": [...], "version": "1.0"}

# Version 2
@app.route('/v2/users')
def get_users_v2():
    return {"data": {"users": [...]}, "version": "2.0"}
```

### Header Versioning

**Pattern**: Include version in request header

```http
GET /users
Accept: application/vnd.myapi.v2+json

# Or
GET /users
API-Version: 2

# Or
GET /users
Accept-Version: 2.0
```

**Pros**:
- Clean URLs (no version pollution)
- Same endpoint for all versions
- Good for content negotiation
- Follows HTTP standards (Accept header)
- Flexible versioning per resource

**Cons**:
- Less visible (harder to discover)
- Harder to test in browser
- Can complicate caching
- More complex routing logic
- May confuse some developers

**When to Use**:
- When you want clean URLs
- APIs with frequent minor updates
- Content negotiation is important
- Internal or partner APIs

**Implementation Example**:
```python
from flask import Flask, request

app = Flask(__name__)

@app.route('/users')
def get_users():
    version = request.headers.get('API-Version', '1')

    if version == '2':
        return {"data": {"users": [...]}, "version": "2.0"}
    else:
        return {"users": [...], "version": "1.0"}
```

### Query Parameter Versioning

**Pattern**: Include version in query string

```
GET /users?version=2
GET /users?api-version=2.0
GET /users?v=2
```

**Pros**:
- Simple to implement
- Easy to test
- Optional (can have default version)
- Works well with existing infrastructure

**Cons**:
- Not RESTful
- Can be accidentally omitted
- Harder to enforce
- Caching complications
- Query params should be for filtering, not versioning

**When to Use**:
- Quick prototypes or internal tools
- When you need easy testing
- Temporary versioning before better solution

**Not Recommended**: Generally avoid this approach for production APIs

### Media Type Versioning (Content Negotiation)

**Pattern**: Use custom media types with version

```http
GET /users
Accept: application/vnd.myapi.user.v2+json

# Or more specific
Accept: application/vnd.myapi.user.v2.full+json
```

**Pros**:
- Follows REST principles
- Fine-grained versioning per resource
- Supports different representations
- Standard HTTP content negotiation

**Cons**:
- Complex to implement
- Harder for clients to use
- Less discoverable
- Requires good documentation

**When to Use**:
- Mature, well-designed APIs
- When you need resource-level versioning
- APIs with multiple representation formats

### Semantic Versioning

**Format**: MAJOR.MINOR.PATCH (e.g., 2.1.3)

```
GET /v2.1/users  # Less common
# Or in header
API-Version: 2.1.3
```

**Version Components**:
- **MAJOR**: Breaking changes (v1 → v2)
- **MINOR**: New features, backward compatible (v2.1 → v2.2)
- **PATCH**: Bug fixes, backward compatible (v2.1.1 → v2.1.2)

**Best Practices**:
- Only include MAJOR version in URL/header
- Track MINOR/PATCH in response headers
- Communicate MINOR/PATCH in API documentation

```http
Response Headers:
API-Version: 2
API-Version-Full: 2.1.3
```

## When to Version

### Create New Version For

**Breaking Changes**:
- Removing endpoints
- Removing request/response fields
- Changing field data types
- Renaming fields
- Changing authentication methods
- Modifying error response structure
- Changing HTTP status codes
- Altering request/response semantics

**Examples**:
```json
// V1
{
  "user_id": "123",  // Field name changed
  "email": "test@example.com"
}

// V2
{
  "id": "123",       // Breaking: renamed field
  "email": "test@example.com"
}
```

```json
// V1
{
  "created": "2025-10-25"  // String
}

// V2
{
  "created": 1698336000    // Breaking: changed to Unix timestamp
}
```

### Don't Version For

**Backward Compatible Changes**:
- Adding new optional fields to responses
- Adding new endpoints
- Adding new optional query parameters
- Bug fixes
- Performance improvements
- Internal refactoring
- Documentation updates
- Adding new optional request fields

**Examples**:
```json
// V1
{
  "id": "123",
  "email": "test@example.com"
}

// V1 (backward compatible update)
{
  "id": "123",
  "email": "test@example.com",
  "username": "testuser"  // New field - clients can ignore
}
```

### Version Change Checklist

Before creating a new version, ask:

- [ ] Is this change absolutely necessary?
- [ ] Can we make it backward compatible?
- [ ] Have we exhausted all backward-compatible options?
- [ ] Is the benefit worth the maintenance cost?
- [ ] Have we documented the migration path?
- [ ] Have we planned the deprecation timeline?

## Deprecation Process

### Deprecation Timeline

**Recommended Process**:

```
Month 0: Announce deprecation
  ↓
Month 1-3: Deprecation warnings in responses
  ↓
Month 3-6: Migration support and documentation
  ↓
Month 6: Final warning (30 days to sunset)
  ↓
Month 7: Sunset (remove old version)
```

**Adjust timeline based on**:
- API usage and customer base
- Severity of changes
- Available alternatives
- Industry standards (some require 12+ months)

### Deprecation Headers

```http
# Standard headers
Sunset: Sat, 31 Dec 2025 23:59:59 GMT
Deprecation: true
Link: <https://docs.example.com/migration/v1-to-v2>; rel="deprecation"

# Custom headers for more detail
X-API-Deprecated: true
X-API-Sunset-Date: 2025-12-31
X-API-Migration-Guide: https://docs.example.com/migration/v1-to-v2
```

### Deprecation Warnings in Response

```json
{
  "data": {
    "users": [...]
  },
  "warnings": [
    {
      "code": "DEPRECATED_VERSION",
      "message": "API v1 is deprecated and will be removed on 2025-12-31",
      "severity": "warning",
      "migrationGuide": "https://docs.example.com/migration/v1-to-v2",
      "sunsetDate": "2025-12-31T23:59:59Z"
    }
  ]
}
```

### Deprecation Announcement Template

**Email/Blog Post**:
```
Subject: Important: API v1 Deprecation Notice

Dear API Users,

We are deprecating API v1 and introducing v2 with the following improvements:
- [List key improvements]
- [List new features]

Timeline:
- Today: v2 is now available
- [Date + 3 months]: Deprecation warnings added to v1 responses
- [Date + 6 months]: Final 30-day warning
- [Date + 7 months]: v1 will be shut down

Migration:
- Migration guide: [URL]
- API documentation: [URL]
- Support: [Contact info]

What you need to do:
1. Review the migration guide
2. Update your integration to use v2
3. Test thoroughly in our sandbox environment
4. Deploy to production before [sunset date]

We're here to help with the migration. Please reach out if you have questions.

Best regards,
API Team
```

## Migration Strategies

### Parallel Running

**Strategy**: Run both versions simultaneously

```
v1: https://api.example.com/v1/users (deprecated)
v2: https://api.example.com/v2/users (current)
```

**Timeline**:
```
Deploy v2 → Monitor adoption → Deprecate v1 → Sunset v1
```

**Monitoring**:
```json
{
  "metrics": {
    "v1": {
      "requests": 10000,
      "percentOfTotal": 15,
      "uniqueClients": 23
    },
    "v2": {
      "requests": 57000,
      "percentOfTotal": 85,
      "uniqueClients": 189
    }
  }
}
```

### Feature Flags for Gradual Rollout

```python
def get_users():
    # Check feature flag
    if user.has_feature('api_v2'):
        return v2_response()
    else:
        return v1_response()
```

**Benefits**:
- Gradual rollout to percentage of users
- Easy rollback if issues found
- A/B testing capabilities
- Per-user or per-account enabling

### Adapter Pattern

**Strategy**: Maintain one codebase, transform responses

```python
def get_users():
    # Core business logic
    users = fetch_users_from_db()

    # Version-specific transformation
    version = get_api_version()
    if version == 1:
        return transform_to_v1(users)
    elif version == 2:
        return transform_to_v2(users)
```

**Pros**:
- Single source of truth
- Less code duplication
- Easier to maintain business logic

**Cons**:
- Transformation overhead
- Can become complex with many versions

### Proxy/Gateway Pattern

**Strategy**: Use API gateway to route and transform

```
Client → API Gateway → Version Detection → Route to v1 or v2
                    → Transform response if needed
```

**Benefits**:
- Centralized version management
- Can translate between versions
- Easier to monitor and control

### Database Versioning

**Challenge**: Breaking database schema changes

**Strategies**:

1. **Expand-Contract Pattern**:
```sql
-- Phase 1: Expand (add new column, keep old)
ALTER TABLE users ADD COLUMN email_address VARCHAR(255);

-- Phase 2: Dual writes (write to both columns)
UPDATE users SET email_address = email;

-- Phase 3: Migrate clients to new field

-- Phase 4: Contract (remove old column)
ALTER TABLE users DROP COLUMN email;
```

2. **Database Views**:
```sql
-- v1 view
CREATE VIEW users_v1 AS
SELECT user_id as id, email FROM users;

-- v2 view
CREATE VIEW users_v2 AS
SELECT id, email_address as email FROM users;
```

## Best Practices

### Version Numbering

**Recommendations**:
- Start with v1 (not v0)
- Use integers for major versions (v1, v2, v3)
- Increment thoughtfully (v1 → v2 is significant)
- Consider semantic versioning internally
- Document what each version includes

**Avoid**:
- Dates in versions (v2025, v20251025)
- Too many major versions (v1 → v2 → v3 in 6 months)
- Fractional versions in URL (v1.5)

### Version Communication

**Document Clearly**:
- Current version
- Supported versions
- Deprecated versions with sunset dates
- Changelog for each version
- Migration guides

**Example Versions Page**:
```markdown
# API Versions

## Current Versions

- **v2** (Current) - Released 2025-01-15
  - Latest features and improvements
  - Recommended for all new integrations

- **v1** (Deprecated) - Sunset: 2025-12-31
  - Legacy version, please migrate to v2
  - Migration guide: [link]

## Changelog

### v2.0.0 (2025-01-15)
- Breaking: Changed user ID format from integer to string
- Breaking: Removed deprecated /users/search endpoint
- Added: New filtering capabilities on /users endpoint
- Improved: Response time by 40%

### v1.2.0 (2024-10-01)
- Added: New optional 'include' parameter for related resources
- Fixed: Pagination cursor encoding issue
```

### Support Policy

**Define Clear Policies**:
```markdown
## Version Support Policy

- **Current Version**: Full support, active development
- **Previous Version**: Security updates only, 12 months after new version release
- **Deprecated Versions**: No support, will be sunset after notice period

## Deprecation Notice Period

- Minor changes: 3 months minimum
- Major changes: 6 months minimum
- Critical breaking changes: 12 months minimum
```

### Monitoring and Metrics

**Track**:
- Requests per version
- Unique clients per version
- Error rates per version
- Response times per version
- Adoption rate of new version

**Set Alerts**:
- Spike in old version usage (regression?)
- Low adoption of new version
- Increase in errors after version release

### Testing Strategy

**Test Matrix**:
```
Test Suite:
├── v1 Integration Tests
│   ├── All v1 endpoints
│   └── Backward compatibility
├── v2 Integration Tests
│   ├── All v2 endpoints
│   └── New features
└── Cross-Version Tests
    ├── Data consistency
    └── Migration scenarios
```

### Client SDK Versioning

**Align SDK versions with API versions**:

```python
# SDK versioning
pip install myapi-client==1.0.0  # For API v1
pip install myapi-client==2.0.0  # For API v2

# Or support multiple versions in one SDK
from myapi_client.v1 import Client as ClientV1
from myapi_client.v2 import Client as ClientV2
```

### Avoid Version Hell

**Don't**:
- Support too many versions simultaneously (3+ active versions)
- Make breaking changes too frequently
- Skip version numbers arbitrarily
- Use confusing version schemes

**Do**:
- Plan major versions carefully
- Extend deprecation periods when usage is high
- Provide excellent migration documentation
- Offer migration assistance for large customers
- Consider backward compatibility first

### Emergency Breaking Changes

**If you absolutely must make emergency breaking changes**:

1. Communicate immediately
2. Provide very short migration window
3. Offer direct support
4. Document thoroughly
5. Learn and prevent future occurrences

```markdown
# Emergency Change Notice

⚠️ CRITICAL SECURITY UPDATE

We discovered a security vulnerability that requires an immediate breaking change.

**What's changing**: [Specific change]
**Why**: [Security reason]
**Timeline**:
  - Today: Change deployed, v1.x deprecated
  - 7 days: v1.x will be disabled

**Action required**: [Migration steps]
**Support**: [Emergency contact]
```
