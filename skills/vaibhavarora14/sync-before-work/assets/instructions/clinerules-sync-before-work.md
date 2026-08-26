# Synchronize before coding

Before the first edit in each code-changing task, invoke `sync-before-work` and execute its apply gate. Continue only after a safe success status. Stop on dirty state, detached HEAD, divergence, conflict, or recovery failure. Skip the gate for read-only tasks.
