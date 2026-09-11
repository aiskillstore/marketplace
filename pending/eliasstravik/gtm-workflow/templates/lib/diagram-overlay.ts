import { executeSelect } from "./db";
import type { DiagramStatus, WorkflowGraph } from "./diagram-spec";

const literal = (value: string) => `'${value.replace(/'/g, "''")}'`;

export async function overlayRun(graph: WorkflowGraph, identifier: string): Promise<WorkflowGraph> {
  const run = (await executeSelect(`select run_key, workflow, status, failed_step, started_at, cost_usd, completed, failed from workflow_runs where run_key=${literal(identifier)} or run_id=${literal(identifier)} limit 1`))[0];
  if (!run) throw new Error(`Unknown run ${identifier}`);
  if (run.workflow !== graph.workflow.path.split("/").at(-1)) throw new Error("workflow_mismatch");
  const ledger = await executeSelect(`select step, status, coalesce(sum(cost_usd),0) cost_usd from enrichment_runs where run_key=${literal(String(run.run_key))} and step is not null group by step,status`);
  const paid = new Map<string, { statuses: Set<string>; cost: number }>();
  for (const row of ledger) {
    const item = paid.get(String(row.step)) ?? { statuses: new Set(), cost: 0 };
    item.statuses.add(String(row.status)); item.cost += Number(row.cost_usd ?? 0); paid.set(String(row.step), item);
  }
  const terminal = ["completed", "failed", "cancelled", "stopped", "timed_out"].includes(String(run.status));
  for (const node of graph.nodes) {
    const item = node.step ? paid.get(node.step) : undefined;
    let status: DiagramStatus = "pending";
    if (node.kind === "start") status = "done";
    else if (node.kind === "end") status = run.status === "completed" ? "done" : run.status === "failed" ? "failed" : "pending";
    else if (node.step === run.failed_step || item?.statuses.has("error") || item?.statuses.has("lost")) status = "failed";
    else if (item?.statuses.has("pending")) status = "active";
    else if (item || run.status === "completed") status = "done";
    else if (!terminal) status = "active";
    node.status = status;
    if (item) node.spentUsd = item.cost;
  }
  graph.run = { runKey: String(run.run_key), status: String(run.status), startedAt: Number(run.started_at), costUsd: Number(run.cost_usd ?? 0), completed: Number(run.completed ?? 0), failed: Number(run.failed ?? 0) };
  return graph;
}
