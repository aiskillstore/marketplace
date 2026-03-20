# Snapshot refs lifecycle

## Deterministic loop

1. `open`
2. `snapshot -i`
3. interact with `@eN`
4. re-run `snapshot -i` after updates

## Why refs fail

Refs become stale after:
- navigation
- form submit with rerender
- modal open/close that rebuilds DOM
- SPA route transitions

## Safe usage pattern

```bash
agent-browser snapshot -i
agent-browser click @e3
agent-browser wait --load networkidle
agent-browser snapshot -i
```

## Snapshot minimization

Use smaller snapshots to control context size:

```bash
agent-browser snapshot -i -c
agent-browser snapshot -i -d 4
agent-browser snapshot -s "#content"
```

## Common recovery

- If click targets wrong element: snapshot again and verify label text.
- If element not found: wait by selector/ref, then snapshot.
- If tree is noisy: scope with `-s` and use compact mode.
