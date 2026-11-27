# API contracts and errors

Define the request, response, authentication boundary, and validation before implementation. Validate untrusted inputs where they cross into the system. Check domain rules at the operation that owns the state. Give clients a stable error code and enough context to recover without exposing internals or secrets.

Make pagination order deterministic and scope IDs or cursors to the relevant resource and caller. For retried writes, decide what identifies one logical attempt, who can reuse it, and what happens after a lost response. Note whether a failure can be retried, when the client should stop, and which state remains authoritative.

Test successful and invalid input, authorization and scope, duplicate actions when applicable, and backward compatibility with existing callers. Read [API versioning](../knowledge/backend/api-versioning.md) when contract changes reach independent clients.
