# API Design Review Checklist

## Requirements & Scope

- Use cases, consumers, and constraints are documented.
- Read/write patterns and latency expectations are clear.
- Data sensitivity and compliance requirements are identified.

## Modeling & Naming

- Resource/type naming is consistent and readable.
- Identifiers are stable and relationships are clear.
- Naming styles are not mixed.

## Operation Design

- REST verbs or GraphQL Query/Mutation separation is correct.
- Idempotency is defined for high-risk operations.
- Long-running tasks have asynchronous patterns.

## Errors & Observability

- Error formats are consistent, including error codes and messages.
- Validation errors include field-level details.
- Request correlation identifiers are present.

## Pagination, Filtering, Sorting

- Pagination strategy is clear and consistent.
- Filtering and sorting rules are clear and controllable.
- Large lists are all paginated.

## Versioning & Deprecation

- Backward compatibility plans are in place.
- Deprecation timelines and migration guides are complete.

## Security

- Authentication and authorization rules are clear.
- Rate limiting and anti-abuse strategies are in place.
- Sensitive data is masked or excluded.

## Performance

- Applicable caching strategies are in place.
- GraphQL complexity protection is in place.