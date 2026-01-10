---
adr: 0003
title: API Versioning Strategy Using URL Path Versioning
status: Accepted
date: 2024-11-01
decision_makers: Backend Architect, Frontend Lead, Product Manager
---

# ADR-0003: API Versioning Strategy Using URL Path Versioning

## Status

**Accepted** (2024-11-01)

## Context

As we build our microservices architecture (ADR-0001), we need a strategy for API versioning to support:
- Backward compatibility for existing clients (mobile apps, web, partners)
- Gradual rollout of breaking changes
- Clear deprecation path for old API versions
- Support for multiple active versions simultaneously

**Current Situation:**
- No formal versioning strategy in monolith
- Breaking changes cause immediate failures for mobile apps
- Mobile users on old app versions (30% still on v2.x)
- Partner integrations hard-coded to current API
- Difficult to introduce breaking changes

**Requirements:**
- Support mobile apps (iOS, Android) that update slowly
- Allow 6-12 month deprecation window for old versions
- Clear, discoverable version information
- Maintain backward compatibility where possible
- Enable gradual migration for breaking changes

**Constraints:**
- Mobile app force-upgrade is not acceptable (user experience)
- Must support at least 2 major versions simultaneously
- API gateway (AWS API Gateway) already in place
- RESTful API design principles
- Team size: 8 developers across 4 services

## Decision

We will adopt **URL path versioning** for all public-facing APIs using the format: `/v{major}/resource`.

**Specific Approach:**

1. **Version Format**:
   ```
   /v1/users
   /v2/users
   /v3/users
   ```
   - Major version only (no minor/patch in URL)
   - Prefix with 'v' for clarity
   - Integer version number (v1, v2, v3...)

2. **Versioning Policy**:
   - **Major version bump**: Breaking changes
     - Removing fields
     - Changing field types
     - Renaming fields
     - Changing validation rules (more restrictive)
     - Modifying authentication/authorization

   - **No version bump needed**: Non-breaking changes
     - Adding new optional fields
     - Adding new endpoints
     - Adding new query parameters
     - Deprecating fields (but still returning them)
     - Loosening validation rules

3. **Version Support**:
   - Support **N and N-1** versions (latest + previous)
   - Minimum support: 12 months after new version release
   - Deprecation warning headers in responses
   - Automatic redirect from legacy endpoints (where possible)

4. **Implementation Strategy**:
   ```typescript
   // Controller structure
   /src
     /controllers
       /v1
         UserController.ts
         OrderController.ts
       /v2
         UserController.ts
         OrderController.ts
     /services
       UserService.ts    // Shared business logic
   ```

5. **Deprecation Process**:
   - **Month 0**: Announce deprecation, add warning header
     ```
     Deprecation: version="v1", sunset="2025-06-01", link="/api/v2/users"
     ```
   - **Month 3**: Email notification to API consumers
   - **Month 6**: Prominent dashboard warnings
   - **Month 9**: Reduce rate limits for old version
   - **Month 12**: Sunset (return 410 Gone)

6. **Documentation**:
   - OpenAPI spec per version: `/docs/v1/openapi.yaml`
   - Interactive docs: `/docs/v1/`, `/docs/v2/`
   - Migration guides for each version transition
   - Changelog highlighting breaking changes

## Consequences

### Positive

✅ **Clear and Discoverable**:
- Version immediately visible in URL
- No need to inspect headers or documentation
- Easy to test different versions in browser/Postman
- Simple for developers to understand

✅ **Backward Compatibility**:
- Old clients continue working with v1
- No forced upgrades for mobile users
- Gradual migration possible (service by service)
- Reduces risk of breaking production integrations

✅ **Flexible Deployment**:
- Can deploy v2 while v1 still active
- A/B testing between versions possible
- Gradual traffic shifting (10% → 50% → 100%)
- Rollback is straightforward (route back to v1)

✅ **Caching-Friendly**:
- Different cache keys for different versions
- CDN can cache v1 and v2 separately
- No cache invalidation issues across versions

✅ **Simple Routing**:
- API Gateway routes by path prefix
- No custom header parsing needed
- Load balancer rules are straightforward

✅ **Client-Side Control**:
- Clients explicitly choose version
- No ambiguity about which version is being used
- Easy to test multiple versions in parallel

### Negative

⚠️ **URL Namespace Pollution**:
- URLs change with each major version
- More routes to maintain and monitor
- Can be confusing which version is "current"

⚠️ **Code Duplication**:
- Controllers may have similar logic across versions
- Risk of divergence if not carefully managed
- Testing overhead (test each version)

⚠️ **Maintenance Burden**:
- Supporting N + N-1 means double the endpoints
- Bug fixes may need to be applied to multiple versions
- Security patches must be backported

⚠️ **Documentation Complexity**:
- Need separate docs for each version
- Migration guides between versions
- Harder to keep documentation in sync

⚠️ **Breaking Changes Are Delayed**:
- Have to wait for major version to fix design mistakes
- Can't introduce breaking changes incrementally
- May accumulate technical debt between versions

### Neutral

🔄 **SEO Considerations**:
- Search engines may index multiple versions
- Canonical URLs needed to avoid duplicate content
- Not applicable for private APIs

🔄 **Monitoring**:
- Need separate metrics per version
- Dashboard showing v1 vs v2 traffic split
- Alerts for usage spikes in deprecated versions

## Alternatives Considered

### Alternative 1: Header-Based Versioning

**Description:**
- Version specified in HTTP header
- URL remains constant: `/users`
- Header: `Accept: application/vnd.company.v2+json`

**Pros:**
- Clean URLs (no version in path)
- Follows REST "resource" principle
- More "RESTful" by some definitions
- GitHub uses this approach

**Cons:**
- Not discoverable (hidden in headers)
- Harder to test (can't just change URL)
- Caching complexity (Vary: Accept header)
- API Gateway harder to configure
- Team unfamiliar with this approach

**Why not chosen:**
Discoverability is critical for our API consumers (many are external partners with varying technical expertise). URL versioning is more intuitive and easier to debug.

### Alternative 2: Query Parameter Versioning

**Description:**
- Version in query string: `/users?version=2`
- Default to latest if omitted

**Pros:**
- Optional parameter (can default to latest)
- Easy to add to existing endpoints
- URL-based (like path versioning)

**Cons:**
- Version can be accidentally omitted
- Unclear if version is required or optional
- Query params feel "wrong" for versioning
- Caching issues (query params often ignored by CDN)
- Routing harder in API Gateway

**Why not chosen:**
Query parameters should be for filtering/pagination, not API contracts. Risk of clients forgetting to specify version and breaking unexpectedly.

### Alternative 3: Subdomain Versioning

**Description:**
- Version in subdomain: `v2.api.company.com/users`
- Separate subdomains per version

**Pros:**
- Complete isolation between versions
- Different DNS records, SSL certs per version
- Can deploy to different infrastructure
- Easy to deprecate (remove DNS entry)

**Cons:**
- DNS/SSL certificate management overhead
- Harder to set up locally (local.v1.api, local.v2.api)
- CORS complexity (different origins)
- Overkill for our use case
- More expensive (separate infrastructure)

**Why not chosen:**
Too much operational overhead for our team size. Path versioning provides sufficient isolation without the infrastructure complexity.

### Alternative 4: No Versioning (Continuous Evolution)

**Description:**
- Add only non-breaking changes
- Use feature flags for gradual rollouts
- Never remove fields, only deprecate

**Pros:**
- Simpler implementation
- No version management overhead
- Forces backward compatibility thinking
- Works well for internal APIs

**Cons:**
- **Impossible to make breaking changes**
- API grows indefinitely (deprecated fields forever)
- Complex logic handling old + new fields
- Poor for public APIs
- Technical debt accumulates

**Why not chosen:**
Not realistic for long-term API evolution. We need the ability to make breaking changes (e.g., fixing design mistakes, security improvements). Stripe tried this and eventually added versioning.

## References

- [Stripe API Versioning](https://stripe.com/docs/api/versioning)
- [Twilio API Versioning Best Practices](https://www.twilio.com/docs/usage/api/versioning)
- [REST API Versioning Strategies](https://restfulapi.net/versioning/)
- [RFC 5988 - Web Linking (deprecation headers)](https://tools.ietf.org/html/rfc5988)
- Meeting Notes: API Design Review 2024-10-28
- Related ADRs:
  - ADR-0001 (Adopt Microservices Architecture)
  - ADR-0004 (To be written: API Gateway Configuration)

## Implementation Plan

**Owner**: Backend Architect (with API team)

**Phase 1 - Infrastructure** (Week 1-2):
- [ ] Update API Gateway routing rules for /v1/* and /v2/*
- [ ] Add version detection middleware
- [ ] Set up separate OpenAPI specs per version
- [ ] Configure monitoring dashboards per version

**Phase 2 - Migration** (Week 3-4):
- [ ] Move existing endpoints to /v1/* namespace
- [ ] Update clients to use /v1/* URLs (backward compatible)
- [ ] Deploy v1 with deprecation headers pointing to future v2
- [ ] Verify all clients successfully migrated to /v1/*

**Phase 3 - V2 Development** (Week 5-8):
- [ ] Implement breaking changes in /v2/* endpoints
- [ ] Write migration guide (v1 → v2)
- [ ] Beta testing with select partners
- [ ] Performance testing both versions

**Phase 4 - V2 Launch** (Week 9-10):
- [ ] Deploy v2 endpoints to production
- [ ] Update documentation site with v2 docs
- [ ] Announce v2 availability to all API consumers
- [ ] Start 12-month deprecation timeline for v1

**Success Criteria**:
- [ ] Both v1 and v2 APIs running simultaneously
- [ ] Zero downtime during v1 → v2 transition
- [ ] < 5% error rate increase during migration
- [ ] Documentation complete for both versions
- [ ] Mobile apps support both v1 and v2

**Risks & Mitigations**:
- **Risk**: Clients forget to update to versioned URLs
  - **Mitigation**: Redirect legacy URLs to /v1/* with warning
- **Risk**: Bug exists in one version but not the other
  - **Mitigation**: Shared service layer, thorough testing
- **Risk**: Confusion about which version to use
  - **Mitigation**: Clear docs, version comparison guide

---

**Decision Date**: 2024-11-01
**Last Updated**: 2024-11-01
**Next Review**: 2025-05-01 (after v2 launch)
