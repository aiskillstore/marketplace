# REST API Design Principles

## Goals

- Resource models are stable and intuitive.
- Consistent use of HTTP semantics.
- APIs are predictable and easy to evolve.

## Resource Modeling

- Use nouns for resources, not verbs (e.g., `/orders`, `/orders/{order_id}`).
- Use sub-resources to express ownership or containment relationships (`/users/{user_id}/addresses`).
- Prefer stable identifiers if natural keys are subject to change.
- Path hierarchy should not be too deep (usually no more than 2 levels) unless there is a clear sense of ownership.

## Naming and URL Rules

- Use plural nouns for collections (`/projects`, `/projects/{id}`).
- Use kebab-case or snake_case consistently; avoid mixing them.
- Avoid action verbs in paths; actions should be expressed by HTTP verbs.
- Use sub-resources for custom actions (`/orders/{id}/cancel`).

## HTTP Verbs and Semantics

- `GET` for retrieval, `POST` for creation, `PUT` for replacement, `PATCH` for updates, `DELETE` for deletion.
- `PUT` must be idempotent; `POST` does not require idempotency.
- Avoid using `POST` for reads unless there is a strong reason (e.g., very large query bodies).

## Status Codes

- `200` for successful reads and updates.
- `201` for creation, returning a `Location` header.
- `204` for successful deletions or empty responses.
- `400` validation failure, `401` unauthorized, `403` forbidden, `404` resource not found.
- `409` conflict, `429` rate limiting, `5xx` server errors.

## Error Model

- Return a consistent error structure.
- Include `code`, `message`, and `details`.
- Adopt RFC 7807 problem+json when necessary.

Example:
```json
{
  "code": "invalid_argument",
  "message": "email must be a valid address",
  "details": {"field": "email"}
}
```

## Pagination, Filtering, Sorting

- Prefer cursor-based pagination for large datasets.
- Use `limit` and `cursor`, returning `next_cursor`.
- Filtering example: `?status=active&created_at_gte=2024-01-01`.
- Sorting example: `?sort=created_at,-priority` (`-` denotes descending order).
- Return total count only when necessary and cost-effective.

## Versioning and Deprecation

- Prefer versioning in Headers or media types to keep URLs clean.
- If URL versioning is mandatory, use a consistent `/v1/` prefix.
- Deprecate fields before removing them, with a clear timeline.

## Caching and Concurrency Control

- Use `ETag` and `If-Match` for optimistic concurrency control.
- Set `Cache-Control` for cacheable GET requests.
- Avoid cacheable responses for private or sensitive user data.

## Idempotency and Retries

- Support idempotency keys for high-risk creations (payments, orders).
- Clearly define idempotency behavior in documentation and error responses.

## Long-running Tasks

- Use `202 Accepted` and provide a status resource (`/operations/{id}`).
- Return progress and the location of the final result.

## Observability

- Include `request_id`/`trace_id` in responses.
- Record correlation identifiers in logs.