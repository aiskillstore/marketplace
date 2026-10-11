# Domains

## Find the semantic owner

Before adding vocabulary, check whether another Astrale Domain already owns it. Reuse a foreign
Domain when its identity and lifecycle are genuinely authoritative; do not copy its Classes or
recreate its callable contracts locally for convenience.

For sign-in users and shared groups, use Shell's public contract; read `users.md` for concrete
subclasses, existing-node registration, invitation, and the traversal agreement Shell needs.

## Graph-level dependency

Declare a Schema dependency only when the local graph directly refers to foreign Classes, Edges,
Policies, Views, or Core definitions. Import the foreign Domain through its published package facade.
Do not reconstruct definition keys or depend on another package's private source.

## Behavioral dependency

Cross-Domain behavior is a consumer-owned Integration:

```text
local Action or Workflow
  -> local Integration contract
  -> Runtime Provider
  -> remote Domain public Client/session call
```

This keeps provider location, credentials, retries, and remote failure translation out of Schema and
business rules. A foreign call combined with local changes is a Workflow; it is not one atomic graph
Mutation.

## Public boundary

Domain source uses semantic `@astrale-os/sdk/*` paths. The SDK owns Kernel compatibility. Direct
Kernel Core/DSL imports, private SDK deep paths, copied callable types, and source links are boundary
violations.

Origin is semantic identity. A deployment URL is serving placement. Redeployment or installation on
another instance must not silently rename the Schema origin or its Definition keys.

## Review

- Which package owns each Class, Edge, Policy, callable, and lifecycle?
- Does graph-level use justify a Schema dependency?
- Is remote behavior behind a local Integration and Provider?
- Are only published facades imported?
- Are atomicity and availability claims honest across the remote boundary?
