# Logging and observability

Choose signals that answer how often a user-visible behavior is delayed, fails, or produces an unexpected result. Use consistent event names, correlation identifiers, units, and useful low-cardinality labels. Preserve trace or request identity across relevant boundaries.

Record outcomes once where they become known. Keep secrets, payment details, and unnecessary personal values out of logs. Log error classes and recovery actions with enough information for a maintainer to identify the failing operation.

Test a failure path and confirm the signals identify the impacted operation. Relate alerts to a service objective or a clear response. See [structured logging](../knowledge/reliability/structured-logging.md).
