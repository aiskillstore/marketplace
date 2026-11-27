# Safe refactoring

Capture the observable behavior at the current entry point before a structural change. List public commands, APIs, serialized data, or callers that must continue to work. Prefer a focused change with a clear reason, such as a duplicated policy, a test seam, or an incoherent state owner.

Use existing naming and imports where possible. Keep behavioral corrections separately visible and include migrations or compatibility shims when consumers need them. Make changes in small reversible steps, with tests for old stored data or mixed versions when relevant.

Run the normal entry point and the triggering regression before reporting completion. During an audit-only request, describe these steps as findings or verification recommendations.
