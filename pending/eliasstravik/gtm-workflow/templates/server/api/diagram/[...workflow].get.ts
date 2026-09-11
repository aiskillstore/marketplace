import { defineEventHandler } from "nitro/h3";
import { resolveDiagramRequest } from "../../../lib/diagram-route";

export default defineEventHandler(async (event) => {
  const resolved = await resolveDiagramRequest(event as any);
  if (!resolved.ok) return resolved.response;
  return Response.json(resolved.laidOut, { headers: { "cache-control": "no-store" } });
});
