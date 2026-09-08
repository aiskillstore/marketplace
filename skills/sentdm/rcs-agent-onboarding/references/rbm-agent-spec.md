# Current Sent RCS launch specification

## Approval boundary

RCS onboarding is coordinated through Sent and requires carrier approval. There is no public self-service provisioning flow in the current Sent v3 API.

## Required evidence

- Consumer-facing brand name and website
- Logo and primary brand color
- Privacy policy and terms
- Customer support details
- Consent/opt-in description
- Message purpose, audience, market, and volume
- Representative text messages
- Suggestion-chip labels/actions when used
- Sender Profile UUID and desired launch timeline

## Supported message capability

Current Sent RCS guidance supports text and up to four suggestion chips. Rich cards, carousels, and media attachments are roadmap features. Do not make them current approval prerequisites or capability declarations.

## Identity and credentials

Use the Sender Profile UUID. A profile key sends `x-api-key` alone; an organization key may scope with `x-profile-id`. `x-sender-id` is legacy v1/v2 terminology.

## Approval states

Carrier approval state is an operational Sent/carrier process. Do not invent an API enum or per-carrier status endpoint. Store the evidence Sent provides, date it, and surface unknown values safely.
