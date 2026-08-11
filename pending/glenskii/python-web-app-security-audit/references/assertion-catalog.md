# Assertion catalog

Use this catalog to choose the checks that apply to the target service. Configure a check only after confirming the route, policy, and expected result.

## Authentication and authorization

Verify that protected routes reject unauthenticated requests. Verify that role and ownership boundaries reject a configured lower-privilege account. Do not infer a policy from a route name alone.

## Input and errors

Verify that malformed payloads receive a controlled response and that error output does not disclose configuration, credentials, or internal paths. Keep hostile inputs bounded and relevant to the configured endpoint.

## Browser-facing controls

Verify relevant response headers, allowed origins, cookie flags, and preflight handling. Record when a control belongs to a reverse proxy or another layer outside the in-process application.

## Rate limits and methods

Verify the configured threshold and expected response code. Verify that unsupported methods are rejected where the application defines such a policy. Do not generate traffic levels that can affect real users or shared services.

## Configuration

Verify the configured application does not expose debug behavior, unsafe route defaults, or known test-only settings. Treat deployment secrets, certificate handling, and external infrastructure as separate evidence areas.
