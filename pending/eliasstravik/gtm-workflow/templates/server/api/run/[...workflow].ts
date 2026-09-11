import { createHash, randomBytes } from "node:crypto";
import { defineEventHandler } from "nitro/h3";
import { start } from "workflow/api";
import {
  findLiveRun,
  findScheduledRun,
  insertRun,
  reconcileRun,
  updateRunPlain,
} from "../../../lib/db";
import { headCheck } from "../../../lib/head-check";
import { redact } from "../../../lib/redact";
import { scheduleWindow } from "../../../lib/schedule";

export default defineEventHandler(async (event) => {
  const requestedMethod = event.req.method;
  if (requestedMethod !== "GET" && requestedMethod !== "POST") {
    return new Response("method not allowed", {
      status: 405,
      headers: { Allow: "GET, POST" },
    });
  }
  const method: "GET" | "POST" = requestedMethod;

  const authorization = event.req.headers.get("authorization");
  const acceptedSecrets = [
    process.env.GTM_RUN_SECRET,
    ...(method === "GET" ? [process.env.CRON_SECRET] : []),
  ].filter(Boolean);
  if (!acceptedSecrets.some((secret) => authorization === `Bearer ${secret}`)) {
    return error(401, "unauthorized", "A valid bearer is required.");
  }

  const expectedHead = event.req.headers.get("x-gtm-workspace-head");
  const deployedHead = process.env.VERCEL_GIT_COMMIT_SHA;
  const refused = headCheck({ method, expectedHead, deployedHead });
  if (refused) return error(refused.status, refused.code, refused.message);

  const workflowPath = event.context.params?.workflow;
  if (!workflowPath) return error(400, "invalid_workflow", "workflow path required");
  const basename = workflowPath.split("/").at(-1)!;
  const functionName = basename.replace(/-([a-z0-9])/g, (_, character) =>
    character.toUpperCase(),
  );
  const workflowId = `workflow//./workflows/${workflowPath}//${functionName}`;
  const body = method === "POST" ? await event.req.json() : null;
  const requestUrl = new URL(event.req.url);
  const checkpointValue = requestUrl.searchParams.get("checkpoint");
  const checkpoint = checkpointValue === null ? null : Number(checkpointValue);
  if (
    checkpointValue !== null &&
    (!Number.isSafeInteger(checkpoint) || checkpoint! < 1 || method === "GET")
  ) {
    return error(400, "invalid_checkpoint", "checkpoint must be a positive POST integer");
  }

  const requestedDate = requestUrl.searchParams.get("scheduled-for");
  if (requestedDate !== null && !/^\d{4}-\d{2}-\d{2}$/.test(requestedDate)) {
    return error(400, "invalid_scheduled_for", "scheduled-for must be YYYY-MM-DD");
  }
  const scheduledFor = method === "GET" ? scheduleWindow(Date.now()) : requestedDate;
  if (scheduledFor) {
    const existing = await findScheduledRun(workflowPath, scheduledFor);
    if (existing) {
      return error(
        409,
        "already_ran_today",
        `${basename} already has a run for ${scheduledFor}`,
        { runKey: existing.runKey, runId: existing.runId, scheduledFor },
      );
    }
  }

  const input = stableJson(body);
  const inputHash = createHash("sha256").update(input).digest("hex");
  const runKey = randomBytes(16).toString("hex");
  const row = {
    runKey,
    runId: null,
    workflow: basename,
    path: workflowPath,
    method,
    input,
    inputHash,
    status: "running" as const,
    workspaceHead: expectedHead ?? deployedHead ?? null,
    checkpoint,
    scheduledFor,
    startedAt: Date.now(),
  };

  for (let attempt = 0; attempt < 2; attempt += 1) {
    try {
      await insertRun(row);
      break;
    } catch (caught) {
      if (scheduledFor) {
        const existing = await findScheduledRun(workflowPath, scheduledFor);
        if (existing) {
          return error(
            409,
            "already_ran_today",
            `${basename} already has a run for ${scheduledFor}`,
            { runKey: existing.runKey, runId: existing.runId, scheduledFor },
          );
        }
      }
      const existing = await findLiveRun(workflowPath, inputHash);
      if (!existing) throw caught;
      const reconciled = await reconcileRun(existing.runKey);
      if (reconciled.finishedAt !== null && attempt === 0) continue;
      return error(
        409,
        "run_in_progress",
        `${basename} is already running as ${existing.runKey}; inspect it before retrying`,
        { runKey: existing.runKey, runId: existing.runId },
      );
    }
  }

  const meta = { runKey, slug: basename, checkpoint, scheduledFor };
  let run;
  try {
    run =
      method === "GET"
        ? await start({ workflowId }, [null, meta], {
            attributes: runAttributes(runKey, basename, deployedHead, checkpoint),
          })
        : await start({ workflowId }, [body, meta], {
            attributes: runAttributes(runKey, basename, expectedHead, checkpoint),
          });
  } catch (caught) {
    await updateRunPlain(runKey, {
      status: "failed",
      error: redact(caught),
      finishedAt: Date.now(),
    });
    throw caught;
  }

  // The workflow's first library step writes the same run id. If this route
  // write fails after start(), the live row remains closed until that step does it.
  await updateRunPlain(runKey, { runId: run.runId }).catch(() => undefined);
  return Response.json({ runId: run.runId, runKey, workflow: workflowPath });
});

function runAttributes(
  runKey: string,
  workflow: string,
  workspaceHead: string | null | undefined,
  checkpoint: number | null,
) {
  return {
    gtmRunKey: runKey,
    workflow,
    workspaceHead: workspaceHead ?? "local",
    checkpoint: checkpoint === null ? "none" : String(checkpoint),
  };
}

function stableJson(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(stableJson).join(",")}]`;
  if (value && typeof value === "object") {
    return `{${Object.entries(value)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([key, item]) => `${JSON.stringify(key)}:${stableJson(item)}`)
      .join(",")}}`;
  }
  return JSON.stringify(value);
}

function error(
  status: number,
  code: string,
  message: string,
  extra: Record<string, unknown> = {},
) {
  return Response.json({ error: { code, message, ...extra } }, { status });
}
