import { defineEventHandler } from "nitro/h3";
import { z } from "zod";
import { cancelRunTree, getRunRow, reconcileRun } from "../../../../lib/db";
import { redactValue } from "../../../../lib/redact";

const decision = z.object({
  reason: z.string().max(500).nullable().default(null),
});

export default defineEventHandler(async (event) => {
  const secret = process.env.GTM_RUN_SECRET;
  const authorization = event.req.headers.get("authorization");
  if (!secret || authorization !== `Bearer ${secret}`) {
    return error(401, "unauthorized", "A valid bearer is required.");
  }

  const identifier = event.context.params?.runId;
  if (!identifier) return error(400, "invalid_run", "run id or run key required");

  const text = await event.req.text();
  const parsed = decision.safeParse(text.trim() === "" ? {} : JSON.parse(text));
  if (!parsed.success) {
    return error(400, "invalid_decision", parsed.error.message);
  }

  let row = await getRunRow(identifier);
  if (!row) return error(404, "not_found", `Unknown run ${identifier}`);
  if (["running", "waiting", "cancelling"].includes(row.status)) {
    row = await reconcileRun(row.runKey);
  }
  if (row.finishedAt !== null || !["running", "waiting"].includes(row.status)) {
    return error(409, "run_not_active", `${row.workflow} is already ${row.status}`, {
      runKey: row.runKey,
      status: row.status,
    });
  }

  await cancelRunTree(row.runKey, parsed.data.reason);

  const cancelled = (await getRunRow(row.runKey))!;
  return Response.json(redactValue({
    ...cancelled,
    input: JSON.parse(cancelled.input),
    approval: cancelled.approval ? JSON.parse(cancelled.approval) : null,
    webhook_url: cancelled.webhookUrl,
  }));
});

function error(
  status: number,
  code: string,
  message: string,
  extra: Record<string, unknown> = {},
) {
  return Response.json({ error: { code, message, ...extra } }, { status });
}
