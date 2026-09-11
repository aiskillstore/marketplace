import dagre from "@dagrejs/dagre";
import type { DiagramNode, WorkflowGraph } from "./diagram-spec";

export type Box = { x: number; y: number; width: number; height: number };
export type LaidOutGraph = WorkflowGraph & {
  positions: Record<string, Box>;
  groupBounds: Record<string, Box>;
  size: { width: number; height: number };
  edgeRoutes: Record<number, { points: { x: number; y: number }[]; x?: number; y?: number }>;
};

const SIZES: Record<DiagramNode["kind"], { width: number; height: number }> = {
  start: { width: 140, height: 44 },
  end: { width: 140, height: 44 },
  step: { width: 260, height: 76 },
  save: { width: 240, height: 60 },
  wait: { width: 240, height: 60 },
  decision: { width: 240, height: 60 },
};
const PADDING = 32;

export function layoutGraph(graph: WorkflowGraph): LaidOutGraph {
  const g = new dagre.graphlib.Graph({ compound: true, multigraph: true });
  g.setGraph({ rankdir: "TB", nodesep: 48, ranksep: 56, marginx: PADDING, marginy: PADDING });
  g.setDefaultEdgeLabel(() => ({}));
  for (const group of graph.groups) {
    g.setNode(group.id, { label: group.label, clusterLabelPos: "top", paddingTop: 44, paddingBottom: 20, paddingLeft: 20, paddingRight: 20 });
    if (group.parent) g.setParent(group.id, group.parent);
  }
  for (const node of graph.nodes) {
    const subtitle = [node.paidCalls?.length ? node.paidCalls.map((call) => `${call.provider}${call.model ? ` · ${call.model}` : ""} · ${call.unitCostUsd === undefined ? "cost varies" : `$${call.unitCostUsd} per row`}`).join(" · ") : [node.provider, node.model, node.unitCostUsd !== undefined ? `$${node.unitCostUsd} per row` : ""].filter(Boolean).join(" · "), node.spentUsd !== undefined ? `spent $${node.spentUsd.toFixed(2)}` : ""].filter(Boolean).join(" · ");
    const width = Math.max(SIZES[node.kind].width, (node.label.length + 12) * 8 + 40, subtitle.length * 7 + 40);
    g.setNode(node.id, { ...SIZES[node.kind], width: node.kind === "decision" ? width * 1.5 : width, label: node.label });
    if (node.group) g.setParent(node.id, node.group);
  }
  graph.edges.forEach((edge, index) => {
    if (edge.back) return;
    g.setEdge(edge.from, edge.to, { label: edge.label ?? "", width: edge.label ? 40 : 0, height: edge.label ? 16 : 0 }, `e${index}`);
  });
  dagre.layout(g);
  const positions: Record<string, Box> = {};
  for (const node of graph.nodes) {
    const placed = g.node(node.id);
    positions[node.id] = { x: placed.x - placed.width / 2, y: placed.y - placed.height / 2, width: placed.width, height: placed.height };
  }
  const groupBounds: Record<string, Box> = {};
  for (const group of graph.groups) {
    const placed = g.node(group.id);
    groupBounds[group.id] = { x: placed.x - placed.width / 2, y: placed.y - placed.height / 2, width: placed.width, height: placed.height };
  }
  const info = g.graph();
  const edgeRoutes: LaidOutGraph["edgeRoutes"] = {};
  graph.edges.forEach((edge, index) => {
    if (edge.back) return;
    const route = g.edge({ v: edge.from, w: edge.to, name: `e${index}` });
    if (route) edgeRoutes[index] = { points: route.points, x: route.x, y: route.y };
  });
  return {
    ...graph,
    positions,
    groupBounds,
    edgeRoutes,
    size: { width: Math.ceil(info.width ?? 0), height: Math.ceil(info.height ?? 0) },
  };
}
