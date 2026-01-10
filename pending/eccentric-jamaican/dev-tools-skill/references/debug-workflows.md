# Debug Workflows (Detailed)

## A) UI/Interaction Bugs
1. Snapshot -> locate target node text and role.
2. If unclear, screenshot to confirm visual state.
3. Use `evaluate_script` to read computed styles, bounding boxes, and text content.
4. Reproduce with `click`/`hover`/`press_key`.
5. Hypothesize: CSS specificity, missing data, overlay, z-index, pointer-events.
6. Propose minimal fix and validation steps.

## B) Performance/Lag
1. Start trace with reload.
2. Identify LCP/FCP/CLS issues via `performance_analyze_insight`.
3. Check network for large/slow assets.
4. Suggest: code splitting, image optimization, defer scripts, reduce reflows.

## C) Network/API
1. Find failing request (status >= 400 or stalled).
2. Capture request/response headers and payload.
3. Check console for CORS and fetch errors.
4. Suggest: endpoint fix, auth headers, payload schema, retries, caching.

## D) Runtime Errors
1. Read full stack trace; find first app frame.
2. Identify reproducible steps.
3. Inspect variables via `evaluate_script`.
4. Suggest smallest safe code change and rollback note.
