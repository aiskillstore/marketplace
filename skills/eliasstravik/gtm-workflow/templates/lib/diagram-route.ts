import { useStorage } from "nitro/storage";
import { parseDiagramSpec } from "./diagram-spec";
import { overlayRun } from "./diagram-overlay";
import { layoutGraph, type LaidOutGraph } from "./layout";
import { verifyDiagram, type DiagramClaims } from "./sign";
import { ensureMigrated } from "./db";

const PATH_PATTERN = /^(?:[a-z0-9]+(?:-[a-z0-9]+)*\/)*[a-z0-9]+(?:-[a-z0-9]+)*$/;

type RouteEvent = { req: Request; context: { params?: Record<string, string | undefined> } };

export type DiagramRequest =
  | { ok: true; claims: DiagramClaims; laidOut: LaidOutGraph; origin: string; search: string }
  | { ok: false; response: Response };

function deny(status: number, code: string, message: string): Response {
  return Response.json({ error: { code, message } }, { status, headers: { "cache-control": "no-store" } });
}

export function publicOrigin(event: RouteEvent): string {
  const url = new URL(event.req.url);
  const host = event.req.headers.get("x-forwarded-host") ?? event.req.headers.get("host") ?? url.host;
  const protocol = event.req.headers.get("x-forwarded-proto") ?? url.protocol.replace(":", "");
  return `${protocol}://${host}`;
}

export async function resolveDiagramRequest(event: RouteEvent): Promise<DiagramRequest> {
  await ensureMigrated();
  const secret = process.env.GTM_RUN_SECRET;
  if (!secret) return { ok: false, response: deny(503, "unconfigured", "The run secret is not configured.") };
  const path = event.context.params?.workflow ?? "";
  if (!PATH_PATTERN.test(path)) return { ok: false, response: deny(400, "invalid_workflow", "workflow path required") };
  const url = new URL(event.req.url);
  const claims = verifyDiagram(url.searchParams, path, secret);
  if (!claims) return { ok: false, response: deny(401, "unauthorized", "A valid signed link is required.") };
  const source = await readWorkflowSource(path);
  if (source === null) return { ok: false, response: deny(404, "not_found", `No workflow named ${path}`) };
  const graph = parseDiagramSpec(source, path);
  if (claims.run) {
    try {
      await overlayRun(graph, claims.run);
    } catch {
      return { ok: false, response: deny(404, "not_found", "Unknown run for this workflow.") };
    }
  }
  return { ok: true, claims, laidOut: layoutGraph(graph), origin: publicOrigin(event), search: url.search };
}

export async function readWorkflowSource(path: string): Promise<string | null> {
  const raw = await useStorage("assets/workflows").getItemRaw(`${path.split("/").join(":")}.ts`);
  if (raw === null || raw === undefined) return null;
  return typeof raw === "string" ? raw : Buffer.from(raw as Uint8Array).toString("utf8");
}

export async function readFontBytes(): Promise<Uint8Array> {
  const raw = await useStorage("assets/fonts").getItemRaw("Inter-Regular.ttf");
  if (raw === null || raw === undefined) throw new Error("Inter-Regular.ttf is missing from server assets.");
  return typeof raw === "string" ? Buffer.from(raw, "binary") : new Uint8Array(raw as ArrayBufferLike);
}
