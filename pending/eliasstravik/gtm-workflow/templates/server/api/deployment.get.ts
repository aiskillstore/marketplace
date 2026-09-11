import { execFileSync } from "node:child_process";
import { defineEventHandler } from "nitro/h3";
import { getMigrationStatus } from "../../lib/db";

export default defineEventHandler(async (event) => {
  const secret = process.env.GTM_RUN_SECRET;
  if (!secret || event.req.headers.get("authorization") !== `Bearer ${secret}`) return Response.json({ error: { code: "unauthorized", message: "A valid bearer is required." } }, { status: 401 });
  const names = new URL(event.req.url).searchParams.get("names")?.split(",").filter(Boolean) ?? [];
  const present = names.filter((name) => process.env[name] !== undefined);
  let head = process.env.VERCEL_GIT_COMMIT_SHA ?? "local";
  if (head === "local") try { head = execFileSync("git", ["rev-parse", "HEAD"], { encoding: "utf8" }).trim(); } catch {}
  return Response.json({ head, present, missing: names.filter((name) => !present.includes(name)), migration: getMigrationStatus() });
});
