# Canvas State And Viewport

Use this reference when reviewing the root React Flow canvas, state conversion, viewport controls, MiniMap, Background, or provider boundaries.

## Controlled Flow State

- Prefer controlled `nodes` and `edges` for workflow canvases because node state is derived from domain status.
- Use `useNodesState(initialNodes)` and `useEdgesState(initialEdges)` when the component owns canvas state and passes `nodes`, `edges`, `onNodesChange`, and `onEdgesChange` into `<ReactFlow>`.
- Rebuild nodes/edges from domain data deliberately. If `setNodes(buildNodes(project))` runs on every project object identity change, check whether it resets user-dragged positions, dimensions, selection, or transient UI.
- Use functional setters when handling connections or updates: `setEdges((eds) => addEdge(params, eds))`.
- If layout should persist, store user-adjusted positions/sizes in domain state or a canvas-specific store before rebuilding nodes.

## Type Contracts

- Type custom nodes as unions when node data differs by `type`.
- Prefer explicit aliases:

```ts
import type { Edge, Node } from "@xyflow/react";

export type StylePreviewNode = Node<StylePreviewData, "stylePreview">;
export type WorkflowEdge = Edge<WorkflowEdgeData, "workflow">;
```

- Type `useReactFlow<CustomNode, CustomEdge>()` when using methods like `getNodes`, `getEdges`, `updateNodeData`, or `setViewport`.
- Avoid `Node[]` with untyped `data` in new code if a node consumes specific fields.

## NodeTypes And EdgeTypes

- Define `nodeTypes` and `edgeTypes` outside the component or memoize them with stable dependencies.
- Do not create these objects inline in the render body. React Flow wraps custom components internally, so new object identities can cause warnings and unnecessary re-renders.
- Keep type keys stable. A node with `type: "stylePreview"` must match `nodeTypes.stylePreview`.

## Provider And Next.js Boundaries

- In Next.js, React Flow canvases must live behind a client component boundary because the library depends on browser interaction APIs.
- Use `"use client"` at the top of the file that renders `<ReactFlow>` or uses React Flow hooks.
- `useReactFlow`, `useOnViewportChange`, `useStore`, `useNodesData`, and similar hooks require a React Flow provider context. They are safe inside children rendered under `<ReactFlow>`; otherwise wrap the subtree in `ReactFlowProvider`.
- Import `@xyflow/react/dist/style.css` once globally, normally in your app's global CSS file.
- Ensure the canvas parent has a real height and width. React Flow cannot render visibly inside a zero-height parent.

## Viewport Behavior

- Treat viewport as user-owned after manual interaction. Auto-fit is helpful on first load, project switch, or explicit status transition; it is annoying when it fights pan/zoom.
- Use a ref like `userInteractedRef` for high-frequency "has the user moved the viewport?" state to avoid re-render churn.
- Use `fitView({ duration, padding, maxZoom })` for focus changes. Pass `nodes: [{ id }]` when focusing a single workflow step.
- Use `setViewport({ x, y, zoom }, { duration })` for deterministic reset.
- Keep `minZoom` and `maxZoom` aligned with node density and readability.
- Do not call `fitView` in effects that depend on full `nodes` arrays unless the intended behavior is to refit for every node update.

## Canvas Interaction Settings

- Review `selectionKeyCode`, `multiSelectionKeyCode`, `panActivationKeyCode`, `zoomActivationKeyCode`, and `deleteKeyCode` together. They form the product's interaction contract.
- If nodes are mostly workflow cards with internal buttons, make dragging intentional through `dragHandle` selectors.
- Use `nodesDraggable`, `nodesFocusable`, `edgesFocusable`, `elevateNodesOnSelect`, and `elevateEdgesOnSelect` deliberately.
- Prefer `panOnDrag` for a spatial canvas, but protect embedded controls with `nodrag` and `nopan`.

## MiniMap, Background, And Panel

- Keep `MiniMap` colors derived from node state or semantic class names, not duplicated business logic when avoidable.
- Give MiniMap an accessible label and keep it visually subdued enough not to compete with the main workflow.
- Use `Panel` for viewport tools so controls stay anchored to the React Flow coordinate system and layering.
- Use `Background` for spatial texture, but make sure contrast does not obscure edges or selected/focused states.

## Performance Review Points

- Avoid subscribing many components to the full `nodes` or `edges` arrays.
- Prefer targeted hooks like `useNodesData`, `useNodeConnections`, or typed store selectors when a node only needs connected-node data.
- Memoize expensive derived status maps if they are recomputed frequently.
- Keep viewport changes, drag state, and hover state local unless another feature consumes them.
- Memoize custom node components with `React.memo` when they are heavy, receive stable props, and appear many times.
