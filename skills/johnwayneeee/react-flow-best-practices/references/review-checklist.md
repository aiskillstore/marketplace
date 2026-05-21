# React Flow Review Checklist

Use this checklist when reviewing React Flow components, custom nodes, workflow nodes, handles, or canvas behavior. Findings should be concrete, risk-focused, and include file/line references.

## Correctness

- Are `node.type` keys registered in `nodeTypes`?
- Are `edge.type` keys registered in `edgeTypes` or covered by `defaultEdgeOptions`?
- Do all `sourceHandle` and `targetHandle` values match actual rendered `Handle id` values?
- Are handle IDs stable across renders and data changes?
- Are dynamic handles followed by `useUpdateNodeInternals`?
- Are node and edge IDs deterministic and compatible with persisted data?
- Does rebuilding nodes/edges accidentally reset position, size, selection, or collapsed/open local state?
- Does the canvas handle the no-project/empty-state case without invalid nodes or edges?

## Type Safety

- Are node `data` objects typed for the specific node type?
- Are custom node components typed with `NodeProps<Node<Data, "type">>` where useful?
- Are custom edge components typed with `EdgeProps<Edge<Data, "type">>`?
- Are unsafe casts hiding mismatches between domain data and node data?
- Are optional fields guarded before rendering controls that depend on them?

## Interaction

- Are clickable controls inside nodes protected with `nodrag` and `nopan`?
- Are scrollable areas protected with `nowheel` where appropriate?
- Is `dragHandle` used when the node body contains many controls?
- Does auto-fit avoid overriding manual pan/zoom?
- Are keyboard shortcuts intentional and discoverable?
- Does delete behavior avoid removing nodes in read-only/static flows?
- Do `NodeToolbar` and `NodeResizer` appear only when useful?

## Performance

- Are `nodeTypes` and `edgeTypes` stable outside render or memoized?
- Are expensive custom nodes memoized when repeated?
- Do node components avoid subscribing to the full nodes/edges arrays?
- Are callbacks stable when passed to many nodes?
- Are frequent viewport, drag, hover, or selection values kept local/ref-based unless global state is needed?
- Are large lists inside nodes virtualized, paginated, or constrained if they can grow?

## Accessibility

- Is `@xyflow/react/dist/style.css` imported once?
- Does the canvas parent have reliable dimensions?
- Are `nodesFocusable`, `edgesFocusable`, and keyboard accessibility settings deliberate?
- Is `disableKeyboardA11y` left false unless there is a strong reason?
- Are controls, MiniMap, and handles labeled through `ariaLabelConfig` or component props?
- Do selected, active, locked, done, and error states work beyond color alone?
- Are edge labels and node controls reachable by keyboard if they are interactive?

## Suggested Review Output Shape

Start with findings, ordered by severity:

```md
**Findings**
- High: [file]:[line] - Edge `x` references handle `source-a`, but the node renders `source-b`; this breaks the connection path and can fail after layout recalculation.
- Medium: [file]:[line] - `nodeTypes` is recreated every render; React Flow warns about this and can remount custom nodes.
- Low: [file]:[line] - Edge label is visually clickable but lacks `nopan`, so clicks can start canvas panning.

**Residual Risk**
- Mention checks not run or behavior not manually verified.
```

If no findings are found, say that explicitly and list any meaningful residual testing gaps.
