# Modularity and existing-service reuse

Trace from the real input to the side effect and search callers before adding a helper. Inspect documented contracts, tests, and use sites. Reuse the existing operation when inputs, authorization, consistency guarantees, and errors match the new requirement. Extend the owner of a domain rule when the behavior belongs there.

Keep a simple function local when it computes one clear result. Use a private helper to name a distinct step inside that implementation. Extract an independent module for a separately tested policy or several callers. Put coordinated rules and I/O behind a domain service when a business operation needs one owner, such as reserving a room and recording the booking together. Share a service when real callers need the same contract and guarantees. A separately deployed service needs an operational reason described in [architecture](architecture.md).

Expose the invariant through a small interface. Place validation where the boundary has sufficient information, keep database details in the storage adapter, and prove behavior through the normal entry point. For a shuffle, queue storage can use the same selection policy without making the policy depend on playback or a database.
