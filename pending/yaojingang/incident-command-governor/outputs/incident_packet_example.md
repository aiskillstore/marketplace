# Incident Command Packet

## Summary
Primary API latency spiked after a rollout and customer dashboard requests timed out for 14 minutes.

## Severity
SEV1, because the event was customer-facing and required rollback.

## Timeline
- 09:02 deploy started
- 09:05 error rate increased
- 09:09 rollback decision made
- 09:16 latency returned to baseline

## Impact Scope
Dashboard API and alert notifications

## Owners And Actions
- API on-call: verify no residual latency
- Release manager: confirm rollback completeness

## Communications
- Internal: responders and leadership receive explicit timeline plus next checkpoint
- External: customer-facing update references impact, mitigation, and next status time

## Governance Note
Review packet structure and severity policy at the next monthly governance review.
