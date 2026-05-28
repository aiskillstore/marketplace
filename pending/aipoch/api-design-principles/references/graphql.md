# GraphQL API Design Principles

## Goals

- Provide flexible data shapes without breaking clients.
- Schema should be stable, explicit, and discoverable.
- Predictable performance.

## Schema Modeling

- Use nouns for types and fields (`User`, `Order`, `lineItems`).
- Maintain consistent field ownership; avoid cycles and ambiguity.
- Separate output types from input types (`CreateOrderInput`).
- Use Enums for finite sets; avoid free-form strings.

## Query and Mutation

- Queries should not have side effects.
- Mutations return the updated object and relevant error information.
- Use standard structures for `input` and `clientMutationId` when necessary.

Example:
```graphql
mutation CreateOrder($input: CreateOrderInput!) {
  createOrder(input: $input) {
    order { id status }
    errors { code message field }
  }
}
```

## Nullability and Errors

- Use non-null types for required fields to keep the Schema truthful.
- Prefer returning explicit error objects over nulling out large chunks of data.
- Avoid returning partial data without explaining the reason for failure.

## Pagination

- Use the Connection pattern (`edges`, `node`, `pageInfo`).
- Support `first/after` (and `last/before` where necessary).
- Keep `pageInfo` consistent across all connections.

## Performance and Complexity

- Implement query cost analysis and depth limiting.
- Use dataloader/batch loading to mitigate N+1 issues.
- Avoid unbounded lists for non-paginated fields.

## Version Evolution

- Prioritize incremental changes; avoid breaking renames.
- Use `@deprecated` to annotate reasons and timelines.
- Add new fields instead of changing existing semantics.

## Authorization

- Perform permission checks in field resolvers where necessary.
- Fields requiring permissions must have safeguards.
- Return a consistent error structure upon authorization failure.

## Caching

- Cache at the resolver or dataloader layer.
- Use persisted queries to optimize client and server-side caching.

## Subscriptions

- Use subscriptions when real-time pushes are required.
- Define clear event types and payload structures.