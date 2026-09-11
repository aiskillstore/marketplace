import { readFile } from "node:fs/promises";
import { defineEventHandler } from "nitro/h3";
import { diagramQuery } from "../../../lib/sign";
import { ensureMigrated } from "../../../lib/db";

export default defineEventHandler(async (event) => {
  await ensureMigrated();
  const secret = process.env.GTM_RUN_SECRET;
  if (!secret || event.req.headers.get("authorization") !== `Bearer ${secret}`) return Response.json({ error: { code: "unauthorized", message: "A valid bearer is required." } }, { status: 401 });
  const path = event.context.params?.workflow ?? "";
  const url = new URL(event.req.url); const origin = `${url.protocol}//${url.host}`;
  const run = url.searchParams.get("run"); const exp = Math.floor(Date.now() / 1000) + 7 * 86400;
  const query = diagramQuery({ path, run, exp }, secret);
  let pkg: any = {}; try { pkg = JSON.parse(await readFile("package.json", "utf8")); } catch {}
  const hosted = Boolean(process.env.VERCEL);
  const vercel = pkg.gtm?.vercel ?? {};
  const database = process.env.TURSO_DATABASE_URL ?? "";
  const host = database.replace(/^libsql:\/\//, "").split(".")[0];
  const split = host.lastIndexOf("-"); const db = split > 0 ? host.slice(0, split) : ""; const org = split > 0 ? host.slice(split + 1) : "";
  return Response.json({ diagram: `${origin}/gtm/diagram/${path}?${query}`, image: `${origin}/api/diagram-image/${path}?${query}`, runs: hosted && vercel.team && vercel.project ? `https://vercel.com/${vercel.team}/${vercel.project}/observability/workflows` : `${origin}/_workflow`, data: hosted && db && org ? `https://app.turso.tech/${org}/databases/${db}` : hosted ? "https://app.turso.tech" : "https://local.drizzle.studio" });
});
