# Backend and APIs

- [Evolving public API contracts](../knowledge/backend/api-versioning.md) · Preserve real client expectations as response schemas, validation and semantics evolve.
- [Stable cursor pagination](../knowledge/backend/cursor-pagination.md) · Preserve deterministic traversal when rows arrive between paginated reads.
- [Durable scheduled work and missed runs](../knowledge/backend/durable-job-scheduling.md) · Define scheduling, catch-up and duplicate execution for work that must survive process restarts.
- [Idempotent event consumers and inboxes](../knowledge/backend/idempotent-consumer.md) · Apply broker messages in a recoverable way when multiple deliveries are possible.
- [Durable message delivery and acknowledgments](../knowledge/backend/message-acknowledgment.md) · Track durable messages across disconnection, acknowledgement loss and repeated delivery.
- [Resumable uploads and content integrity](../knowledge/backend/resumable-uploads.md) · Choose an upload protocol that preserves completeness across retry, interruption and finalization.
- [Schema validation at integration boundaries](../knowledge/backend/schema-validation.md) · Validate data received across trust and ownership boundaries before it changes state or reaches downstream code.
- [Short URL identifier allocation](../knowledge/backend/short-url-identifiers.md) · Allocate compact resolvable IDs with collision handling and explicit predictability requirements.
