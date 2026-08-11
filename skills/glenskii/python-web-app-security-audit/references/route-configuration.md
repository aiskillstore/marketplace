# Route Configuration

Configure only routes and controls that exist in the target application. The defaults in `.env.test.template` are examples, not assumptions about every project.

## Required review

- Set `TEST_PUBLIC_ROUTE` to a route that should accept unauthenticated traffic.
- Set `TEST_PROTECTED_ROUTE` to a route that requires a regular user.
- Set `TEST_ADMIN_ROUTE` only when the application has an administrator boundary.
- Set the login and registration routes only when those flows exist.
- Set `TEST_IDOR_ROUTE_TEMPLATE` only for a resource whose ownership behavior can be tested with dedicated accounts.

## Interpreting absent routes

A 404 from an example route is not a vulnerability. Configure the actual route or skip the related test with a recorded reason. A route that does not apply must not become an invented finding.

## Rate limits and origins

Set `TEST_RATE_LIMIT_THRESHOLD` to the value enforced by the target environment. Set `TEST_ALLOWED_ORIGIN` to an approved browser origin and `TEST_HOSTILE_ORIGIN` to an origin that must be rejected. Do not use production accounts, public endpoints, or traffic levels that could affect real users.
