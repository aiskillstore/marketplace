# Continuous integration and review guide

Run this suite in an isolated environment that has the application import path, test configuration, and non-production accounts required for the selected checks.

## Before the run

Confirm the revision, environment, applicable routes, expected rate limit, allowed origin, and account roles. Mark unavailable controls as out of scope before the run. Do not use a skipped check to support a release approval.

## During the run

Run `pytest security/ -v` from the target project root. Preserve the command result and a sanitized summary of each failure. Do not retry failures by weakening assertions, replacing configured routes with defaults, or changing test accounts without recording the reason.

## After the run

Review each failure with the application owner. Classify confirmed weaknesses, configuration errors, and unsupported controls separately. Attach the report template to the release decision, then record the verified scope and remaining boundaries.

## Release gate

Use `BLOCKED` for a confirmed weakness that must be corrected. Use `REVIEW REQUIRED` when a material gap or missing control needs a recorded owner decision. Use `PASS` only when configured checks are complete and no blocking or review-level issue remains.
