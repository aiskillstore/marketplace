import { defineEventHandler } from "nitro/h3";
import { HookNotFoundError } from "workflow/errors";
import { approvalDecision, approvalHook } from "../../../lib/approve";
import { getRunRow, updateRunPlain } from "../../../lib/db";
import { redactValue } from "../../../lib/redact";

export default defineEventHandler(async (event) => {
  const secret = process.env.GTM_RUN_SECRET;
  const authorization = event.req.headers.get("authorization");
  if (!secret || authorization !== `Bearer ${secret}`) {
    return error(401, "unauthorized", "A valid bearer is required.");
  }
  const token = event.context.params?.token;
  if (!token) return error(400, "invalid_token", "approval token required");

  const parsed = approvalDecision.safeParse(await event.req.json());
  if (!parsed.success) {
    return error(400, "invalid_decision", parsed.error.message);
  }

  const runKey = token.split(".")[1];
  const row = runKey ? await getRunRow(runKey) : undefined;
  const pending = row?.approval ? JSON.parse(row.approval) : null;
  if (
    !row ||
    row.finishedAt !== null ||
    row.status !== "waiting" ||
    pending?.token !== token ||
    pending?.resolved_at
  ) {
    return error(409, "approval_not_pending", "approval is no longer pending");
  }

  try {
    await approvalHook.resume(token, parsed.data);
    const resolved = redactValue({
      ...pending,
      ...parsed.data,
      resolved_at: Date.now(),
    });
    await updateRunPlain(row.runKey, {
      status: parsed.data.approved ? "running" : "stopped",
      stopReason: parsed.data.approved ? null : "operator_denied",
      approval: JSON.stringify(resolved),
    });
    return Response.json({ approved: parsed.data.approved });
  } catch (caught) {
    if (HookNotFoundError.is(caught)) {
      return error(409, "approval_not_pending", "approval is no longer pending");
    }
    throw caught;
  }
});

function error(status: number, code: string, message: string) {
  return Response.json({ error: { code, message } }, { status });
}
