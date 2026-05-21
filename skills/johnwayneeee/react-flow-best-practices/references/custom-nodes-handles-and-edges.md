# Custom Nodes, Handles, And Edges

Use this reference when reviewing custom node components or custom edge renderers.

## Custom Node Structure

- Type node props as specifically as practical:

```ts
import type { Node, NodeProps } from "@xyflow/react";

type StylePreviewNodeData = {
  projectId?: string;
  workflowStatus: WorkflowStatus;
};

type StylePreviewNodeType = Node<StylePreviewNodeData, "stylePreview">;

export function StylePreviewNode({ id, data, selected }: NodeProps<StylePreviewNodeType>) {
  // ...
}
```

- Keep node UI focused on rendering its card and local interactions. Push domain transitions to features/stores/actions.
- Avoid defining child components inside node render functions unless they need closure state and are cheap.
- Use `selected`, `dragging`, and `id` from `NodeProps` for toolbars, resizers, and node updates instead of duplicating selection state.

## Handles

- Every handle used by an edge must have a stable `id`.
- Multiple handles on one node need distinct IDs. Edge `sourceHandle` and `targetHandle` must match exactly.
- Keep handle IDs semantic and stable, such as `source-style`, `source-preview-test-case`, or `target-left`.
- For static narrative workflows, `isConnectable={false}` is appropriate: edges remain visible but users cannot create accidental connections.
- For editable workflows, provide connection validation near the canvas or handle level and give users visible feedback.
- Do not hide handles with `display: none`; React Flow needs measurable handles. Use `visibility: hidden` or `opacity: 0` if a handle must be visually hidden while retaining layout measurements.
- If handles are added, removed, repositioned, or conditionally rendered after initial mount, call `useUpdateNodeInternals(nodeId)` after the DOM changes so React Flow recalculates handle bounds.

## Dynamic Handles

- Use dynamic handles only when the node's connection schema truly changes.
- Keep dynamic handle IDs deterministic from stable data, not array indexes that can reorder.
- After changing dynamic handle lists:

```ts
const updateNodeInternals = useUpdateNodeInternals();

useEffect(() => {
  updateNodeInternals(id);
}, [id, updateNodeInternals, handleSignature]);
```

- Derive `handleSignature` from stable handle IDs, such as `handles.map((h) => h.id).join("|")`.

## Drag, Pan, And Wheel Safety

- Use `dragHandle` on nodes that contain interactive cards. The selector should point to a visible, intentional grab area.
- Add `nodrag` to buttons, inputs, tabs, menus, toolbars, and clickable edge labels.
- Add `nopan` to controls that should not start canvas panning.
- Add `nowheel` to scrollable content inside a node when scrolling should stay inside the node instead of zooming/panning the canvas.
- Do not put critical interactions only on hover; selected/focused states should also reveal controls.

## NodeToolbar

- Use `NodeToolbar` for contextual controls that belong to a selected node but should not scale with zoom.
- Show it only when appropriate, usually `selected && !dragging`.
- Add `className="nopan"` and put `nodrag` on individual interactive elements when necessary.
- Hide or simplify toolbars when multiple nodes are selected unless bulk actions are intentional.

## NodeResizer

- Use `NodeResizer` for resizable preview panels or content nodes.
- Gate visibility with `selected && !dragging` to avoid visual noise while moving.
- Set `minWidth` and `minHeight` so content remains usable.
- If resized dimensions matter after reload, persist width/height through node state or domain data rather than relying only on transient React Flow state.

## Custom Edges

- Use `BaseEdge` for the path and React Flow path helpers such as `getBezierPath`, `getSmoothStepPath`, or `getStraightPath`.
- Type edge props with the edge data contract:

```ts
import type { Edge, EdgeProps } from "@xyflow/react";

type WorkflowEdgeData = {
  label?: string;
  interactiveLabel?: boolean;
};

export function WorkflowEdge(props: EdgeProps<Edge<WorkflowEdgeData, "workflow">>) {
  // ...
}
```

- Use `EdgeLabelRenderer` for labels rendered in HTML space.
- Position labels with `position: "absolute"` and the coordinates returned by the path helper.
- For interactive labels, add `pointer-events: all` through CSS or style, plus `nodrag` and `nopan`.
- Keep animated edges meaningful. Animation should indicate active progress or live processing, not decorative noise.
- Keep marker styles and stroke styles aligned with semantic edge states: locked, active, done, error.

## Accessibility In Nodes And Edges

- Use real `button`, `input`, `a`, and `label` elements for interactive content.
- Ensure custom icon-only controls have accessible names.
- Preserve visible focus styles inside nodes and edge labels.
- Verify color-only states have text, shape, icon, or motion alternatives.
- Keep handles large enough for pointer use if users can connect nodes manually.
- Provide useful `ariaLabelConfig` for React Flow controls, MiniMap, and handles.
