# Frontend, accessibility, and interaction lens

Trigger: browser/app interaction, UI state, forms, asynchronous views, or client-side changes.

Trace user state across loading, success, error, retry, navigation, reconnect, cancellation, and unmount. Check stale responses overwriting newer input, duplicate submit, pending actions after logout/tenant switch, optimistic updates that cannot roll back, missing cleanup, and derived state drifting from the source of truth. Controlled deferred responses are more useful than fast happy-path mocks for races.

Inspect keyboard order, focus visibility and restoration, accessible names, semantic controls, disabled/error states, screen-reader announcements, contrast, zoom/reflow, motion preferences, touch targets, and non-color-only feedback where applicable. Use the project's target accessibility standard and primary official documentation when compliance is claimed. Do not call a visual inspection an accessibility certification.

Test responsive and overflow behavior with long labels, translated text, empty content, large content, and slow/failing requests. For forms, distinguish client guidance from server validation; the server still owns security and data invariants. Confirm destructive actions have the intended confirmation and recoverability, not simply a hidden button.

Inspect browser/server rendering boundaries, hydration assumptions, storage permissions, multi-tab state, history/back navigation, clipboard/file APIs, and focus traps only when present in the scope.

Evidence should identify the interaction sequence, snapshot, environment, expected/actual state, and screenshot or reproducible automated check where available. Test the original failure plus a neighboring schedule and normal behavior. If no browser is available, perform source-level review and explicitly label untested layout, accessibility, and runtime behavior.
