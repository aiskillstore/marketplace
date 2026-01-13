# API Design Review Checklist

Use this checklist when designing or reviewing APIs to ensure consistency, usability, and best practices.

## Pre-Design Checklist

- [ ] **Requirements Gathered**: Clear understanding of what the API needs to accomplish
- [ ] **Stakeholders Identified**: Know who will use this API (frontend teams, partners, public)
- [ ] **API Style Chosen**: REST, GraphQL, or gRPC based on requirements
- [ ] **Versioning Strategy**: Decided how API will evolve (URI, header, or query param)
- [ ] **Authentication Method**: Chosen auth approach (JWT, API keys, OAuth2)

---

## REST API Design Checklist

### Resource Naming

- [ ] **Plural Nouns**: Resources use plural nouns (`/users`, not `/user`)
- [ ] **Hierarchical**: Relationships expressed through hierarchy (`/users/123/orders`)
- [ ] **Kebab-Case**: Multi-word resources use kebab-case (`/shopping-carts`)
- [ ] **No Verbs**: URLs don't contain actions (`/users`, not `/getUsers`)
- [ ] **Consistent Naming**: Same naming pattern across all resources

### HTTP Methods

- [ ] **GET for Retrieval**: Read operations use GET
- [ ] **POST for Creation**: New resources use POST
- [ ] **PUT for Replace**: Full replacement uses PUT
- [ ] **PATCH for Partial**: Partial updates use PATCH
- [ ] **DELETE for Removal**: Deletions use DELETE
- [ ] **Idempotent Operations**: PUT, DELETE, GET are idempotent
- [ ] **Safe Operations**: GET, HEAD don't modify resources

### Status Codes

- [ ] **2xx for Success**: Appropriate success codes (200, 201, 204)
- [ ] **4xx for Client Errors**: Correct client error codes (400, 401, 403, 404, 422, 429)
- [ ] **5xx for Server Errors**: Server errors use 5xx (500, 502, 503)
- [ ] **Consistent Usage**: Same code for same scenarios across API
- [ ] **Location Header**: 201 responses include `Location` header

### Request/Response

- [ ] **JSON Format**: Using `application/json` content type
- [ ] **Consistent Structure**: Same response structure across endpoints
- [ ] **Error Format**: Standardized error response with code, message, details
- [ ] **Timestamp Format**: ISO 8601 format for all dates/times
- [ ] **Field Naming**: Consistent convention (snake_case or camelCase)

### Pagination

- [ ] **Pagination Implemented**: Large lists are paginated
- [ ] **Cursor or Offset**: Chosen appropriate pagination strategy
- [ ] **Page Info Included**: Response includes pagination metadata
- [ ] **Configurable Limit**: Clients can specify page size
- [ ] **Max Limit Enforced**: Prevent excessive page sizes

### Filtering & Sorting

- [ ] **Filter Parameters**: Query params for filtering (e.g., `?status=active`)
- [ ] **Sort Parameter**: Query param for sorting (e.g., `?sort=created_at:desc`)
- [ ] **Field Selection**: Support partial responses (e.g., `?fields=id,name`)
- [ ] **Consistent Syntax**: Same filter/sort syntax across endpoints

### Versioning

- [ ] **Version Strategy Chosen**: URI, header, or query param versioning
- [ ] **Version Number Visible**: Clear which version is being used
- [ ] **Backward Compatibility**: Older versions supported for migration period
- [ ] **Deprecation Policy**: Plan for sunsetting old versions

### Authentication & Security

- [ ] **Auth Required**: Protected endpoints require authentication
- [ ] **Authorization Checked**: Verify user permissions for actions
- [ ] **HTTPS Only**: API only accessible over HTTPS in production
- [ ] **API Keys Secure**: Keys not exposed in URLs or logs
- [ ] **Rate Limiting**: Implemented to prevent abuse

### Rate Limiting

- [ ] **Limits Defined**: Clear rate limits per endpoint/user
- [ ] **Headers Included**: `X-RateLimit-*` headers in responses
- [ ] **429 Status**: Returns 429 when limit exceeded
- [ ] **Retry-After Header**: Tells client when to retry

### Error Handling

- [ ] **Consistent Format**: All errors follow same structure
- [ ] **Error Codes**: Machine-readable error codes included
- [ ] **Helpful Messages**: Clear, actionable error messages
- [ ] **Field-Level Errors**: Validation errors specify which fields failed
- [ ] **Request IDs**: Each response includes unique request ID for support

---

## GraphQL API Design Checklist

### Schema Design

- [ ] **Nullable by Default**: Fields nullable unless explicitly required (!)
- [ ] **Connections for Lists**: Use Connection pattern for paginated lists
- [ ] **Input Types**: Mutations use Input types, not inline args
- [ ] **Enum Types**: Use enums for fixed sets of values
- [ ] **Interface/Union Types**: Reuse types appropriately

### Queries

- [ ] **Single Resource Queries**: Can fetch individual items by ID
- [ ] **List Queries**: Can fetch lists with filtering and pagination
- [ ] **Nested Queries**: Related data fetchable in single query
- [ ] **N+1 Prevention**: DataLoader or similar for batching

### Mutations

- [ ] **Input/Payload Pattern**: Mutations use `createUserInput` → `CreateUserPayload`
- [ ] **Return Complete Object**: Mutations return updated resource
- [ ] **Error Handling**: Payload includes errors array
- [ ] **Optimistic UI**: Mutations designed for optimistic updates

### Subscriptions

- [ ] **Real-Time Events**: Subscriptions for live updates
- [ ] **Filtered Subscriptions**: Clients can filter events
- [ ] **Subscription Cleanup**: Proper cleanup on disconnect

---

## gRPC API Design Checklist

### Proto Files

- [ ] **Package Name**: Follows convention (company.service.v1)
- [ ] **Versioned**: Version included in package name
- [ ] **Imports Organized**: Standard imports (google/protobuf/*)
- [ ] **Comments**: Services and messages documented

### Service Design

- [ ] **CRUD Operations**: Standard operations defined
- [ ] **Request/Response Messages**: Each RPC has dedicated messages
- [ ] **Streaming Where Appropriate**: Uses streaming for large data or live updates
- [ ] **Empty Responses**: Uses google.protobuf.Empty for no-content responses

### Message Design

- [ ] **Field Numbers**: Sequential, never reused
- [ ] **Required Fields**: Minimal required fields
- [ ] **Repeated Fields**: For lists/arrays
- [ ] **Oneof Fields**: For mutually exclusive fields
- [ ] **Enums Have Zero**: First enum value is UNSPECIFIED = 0

### Error Handling

- [ ] **gRPC Status Codes**: Uses standard status codes
- [ ] **Error Details**: Rich error info using google.rpc.Status
- [ ] **Retry Logic**: Idempotent operations identified

---

## API Documentation Checklist

### OpenAPI/AsyncAPI Specification

- [ ] **Specification Created**: OpenAPI 3.1 or AsyncAPI 3.0 document exists
- [ ] **Complete Coverage**: All endpoints documented
- [ ] **Examples Provided**: Request/response examples for each endpoint
- [ ] **Schema Definitions**: Reusable schemas in components section
- [ ] **Security Schemes**: Authentication methods documented

### Documentation Quality

- [ ] **Getting Started Guide**: Clear intro for new users
- [ ] **Authentication Guide**: How to authenticate explained
- [ ] **Error Handling Guide**: Common errors and solutions
- [ ] **Code Examples**: Working code samples in multiple languages
- [ ] **Changelog**: Version history and breaking changes documented

### API Reference

- [ ] **Endpoint List**: All endpoints listed with descriptions
- [ ] **Parameters Documented**: Query, path, header params explained
- [ ] **Status Codes**: All possible status codes documented
- [ ] **Rate Limits**: Limits and quotas clearly stated
- [ ] **Deprecation Notices**: Deprecated endpoints marked

---

## Performance Checklist

- [ ] **Pagination Default**: Reasonable default page size (20-50)
- [ ] **Field Selection**: Support for partial responses
- [ ] **Caching Headers**: Cache-Control, ETag headers where appropriate
- [ ] **Compression**: Gzip/Brotli compression enabled
- [ ] **Response Times**: < 200ms for simple queries, < 1s for complex
- [ ] **N+1 Queries Avoided**: Efficient database queries
- [ ] **Indexes Created**: Database indexes on frequently queried fields

---

## Testing Checklist

- [ ] **Unit Tests**: Business logic tested
- [ ] **Integration Tests**: API endpoints tested end-to-end
- [ ] **Contract Tests**: API contracts validated
- [ ] **Load Tests**: Performance under load verified
- [ ] **Security Tests**: Common vulnerabilities tested (OWASP)
- [ ] **Documentation Tests**: Examples in docs actually work

---

## Compliance & Standards

- [ ] **REST Principles**: Follows RESTful conventions (if REST)
- [ ] **GraphQL Spec**: Adheres to GraphQL specification (if GraphQL)
- [ ] **gRPC Style Guide**: Follows protobuf style guide (if gRPC)
- [ ] **Naming Conventions**: Consistent with org standards
- [ ] **Security Standards**: Meets security requirements
- [ ] **Privacy Compliance**: GDPR, CCPA compliance where applicable

---

## Pre-Launch Checklist

- [ ] **All Tests Passing**: 100% pass rate on test suite
- [ ] **Documentation Complete**: All endpoints documented
- [ ] **Security Review**: Security team approved
- [ ] **Load Testing**: Performance validated under expected load
- [ ] **Monitoring Setup**: Metrics, logging, alerting configured
- [ ] **Error Tracking**: Error monitoring (Sentry, etc.) configured
- [ ] **Rollback Plan**: Can revert if issues found
- [ ] **Stakeholder Approval**: Frontend/client teams signed off

---

## Post-Launch Checklist

- [ ] **Monitor Metrics**: Track API usage, error rates, latency
- [ ] **Collect Feedback**: Gather developer feedback
- [ ] **Document Issues**: Track bugs and feature requests
- [ ] **Iterate**: Plan improvements based on real usage
- [ ] **Deprecation Plan**: Plan for sunsetting old versions if applicable

---

## Common API Anti-Patterns to Avoid

❌ **Chatty APIs**: Too many round-trips required
✅ **Fix**: Batch operations, nested resources, GraphQL

❌ **Overfetching**: Returning more data than needed
✅ **Fix**: Field selection, GraphQL, partial responses

❌ **Underfetching**: Requiring multiple calls for related data
✅ **Fix**: Include related resources, nested endpoints, GraphQL

❌ **Breaking Changes**: Backward-incompatible changes without versioning
✅ **Fix**: Version API, deprecation periods, additive changes

❌ **Unclear Errors**: Generic "Error 500" messages
✅ **Fix**: Specific error codes, helpful messages, troubleshooting info

❌ **No Pagination**: Returning thousands of items
✅ **Fix**: Implement pagination with reasonable defaults

❌ **Ignoring HTTP**: Using POST for everything
✅ **Fix**: Use appropriate HTTP methods (GET, POST, PUT, DELETE)

❌ **Exposing Internal Details**: Database fields in API
✅ **Fix**: Map to business domain, hide implementation

---

## Reviewer Sign-Off

### Technical Review

- [ ] **Backend Architect**: Architectural soundness verified
- [ ] **Frontend Developer**: Developer experience validated
- [ ] **Security Team**: Security implications reviewed
- [ ] **DevOps**: Operational concerns addressed

### Business Review

- [ ] **Product Manager**: Business requirements met
- [ ] **API Governance**: Compliance with API standards

---

**Checklist Version**: 1.0.0
**Skill**: api-design-framework v1.0.0
**Last Updated**: 2025-10-31
