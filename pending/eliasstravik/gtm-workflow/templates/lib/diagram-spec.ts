export type DiagramStatus = "pending" | "active" | "done" | "failed";
export type NodeKind = "start" | "step" | "decision" | "wait" | "save" | "end";
export type PaidStage = { provider: string; model?: string; unitCostUsd?: number };
export type DiagramNode = { id: string; kind: NodeKind; label: string; step?: string; order?: number; unitCostUsd?: number; upperBound?: boolean; status?: DiagramStatus; spentUsd?: number; paidCalls?: PaidStage[]; provider?: string; model?: string; group?: string };
export type DiagramGroup = { id: string; kind: "loop" | "parallel"; label: string; parent?: string; completed?: number; failed?: number };
export type DiagramEdge = { from: string; to: string; label?: string; back?: boolean };
export type WorkflowGraph = { workflow: { path: string; label: string; runs: string; kind: string; table: string | null; summary?: string; schedule?: string }; nodes: DiagramNode[]; groups: DiagramGroup[]; edges: DiagramEdge[]; run?: { runKey: string; status: string; startedAt: number; costUsd: number; completed: number; failed: number } };

const BLOCK = /\/\*\*[\s\S]*?Diagram:\s*([\s\S]*?)\*\//;
const LINE = /^\s*\*?\s*(\d+)\.\s+(.+?)(?:\s+->\s*(\d+))?\s*$/;

export function parseDiagramSpec(source: string, path: string): WorkflowGraph {
  const body = source.match(BLOCK)?.[1];
  if (!body) throw new Error("Add a Diagram header to the workflow file.");
  const nodes: DiagramNode[] = [];
  const destinations = new Map<number, number>();
  let schedule: string | undefined;
  for (const raw of body.split("\n")) {
    const clean = raw.replace(/^\s*\*?\s?/, "").trim();
    const scheduleMatch = clean.match(/\[schedule:\s*([^\]]+)\]/);
    if (scheduleMatch) schedule = scheduleMatch[1].trim();
    const match = clean.match(LINE);
    if (!match) continue;
    const order = Number(match[1]);
    const step = match[2].match(/\[step:\s*([A-Za-z_$][\w$]*)\]/)?.[1];
    const cost = match[2].match(/\[cost:\s*(up to\s+)?\$([\d.]+)\/row\]/i);
    const decision = match[2].match(/\[decision:\s*([^\]]+)\]/i)?.[1];
    const label = match[2].replace(/\s*\[(?:step|cost|decision):[^\]]+\]/gi, "").trim();
    nodes.push({ id: `step-${order}`, kind: decision ? "decision" : /^save\b/i.test(label) ? "save" : "step", label: decision ?? label, step, order, unitCostUsd: cost ? Number(cost[2]) : undefined, upperBound: Boolean(cost?.[1]) });
    if (match[3]) destinations.set(order, Number(match[3]));
  }
  if (!nodes.length) throw new Error("The Diagram header needs numbered lines.");
  const all: DiagramNode[] = [{ id: "start", kind: "start", label: "Start" }, ...nodes, { id: "end", kind: "end", label: "Done" }];
  const edges = all.slice(0, -1).map((node, index) => ({ from: node.id, to: destinations.has(index) ? `step-${destinations.get(index)}` : all[index + 1].id }));
  const slug = path.split("/").at(-1) ?? path;
  return { workflow: { path, label: slug.replace(/-/g, " "), runs: "rows", kind: "workflow", table: null, schedule }, nodes: all, groups: [], edges };
}

export const diagramCost = (graph: WorkflowGraph) => graph.nodes.reduce((sum, node) => sum + (node.unitCostUsd ?? 0), 0);
