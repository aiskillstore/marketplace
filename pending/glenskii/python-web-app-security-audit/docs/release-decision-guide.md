# Release Decision Guide

## Use the result honestly

The suite checks only the configured application, routes, accounts, and environment. A passing result means those checks did not find a blocking or review-level issue. It does not prove that every route, deployment setting, dependency, or external service is secure.

## Classify each result

Use **BLOCKED** when a configured check confirms a weakness that must be fixed before release. Use **REVIEW REQUIRED** when a material risk, untested control, or environment boundary needs an owner decision. Use **PASS** only when configured checks are complete, failures are resolved or disproven, and remaining boundaries are clearly documented.

## Record the release evidence

Include the application revision, environment, configured routes, test account type, test command, failures, skipped checks, and retest result. Keep credentials, session values, tokens, and personal data out of the report.

## Escalate beyond this suite

Use separate review for dependency vulnerabilities, reverse proxies, certificates, cloud configuration, WAF controls, external identity providers, and production traffic behavior. These controls cannot be established by an in-process application test suite.
