import { defineEventHandler } from "nitro/h3";
import { findLatestRun, reconcileRun } from "../../../lib/db";
import { redactValue } from "../../../lib/redact";

/** The newest run of one workflow, optionally only runs started from one workspace commit. */
export default defineEventHandler(async (event) => {
  const secret = process.env.GTM_RUN_SECRET;
  if (!secret || event.req.headers.get("authorization") !== `Bearer ${secret}`) {
    return Response.json({ error: { code: "unauthorized", message: "A valid bearer is required." } }, { status: 401 });
  }
  const url = new URL(event.req.url);
  const workflow = url.searchParams.get("workflow");
  const head = url.searchParams.get("head") ?? undefined;
  if (!workflow) return Response.json({ error: { code: "invalid_workflow", message: "workflow is required" } }, { status: 400 });
  let row = await findLatestRun(workflow, head);
  if (!row) return Response.json({ error: { code: "not_found", message: `No run of ${workflow} yet` } }, { status: 404 });
  if (["running", "waiting", "cancelling"].includes(row.status)) row = await reconcileRun(row.runKey);
  return Response.json(redactValue({ runKey: row.runKey, runId: row.runId, workflow: row.workflow, status: row.status, workspaceHead: row.workspaceHead, startedAt: row.startedAt, finishedAt: row.finishedAt, completed: row.completed, failed: row.failed, costUsd: row.costUsd, error: row.error, failedStep: row.failedStep }));
});
