import { defineEventHandler } from "nitro/h3";
import { readFontBytes, resolveDiagramRequest } from "../../../lib/diagram-route";
import { renderPng, renderSvg } from "../../../lib/diagram-svg";

export default defineEventHandler(async (event) => {
  const resolved = await resolveDiagramRequest(event as any);
  if (!resolved.ok) return resolved.response;
  const png = renderPng(renderSvg(resolved.laidOut), await readFontBytes());
  return new Response(png, { headers: { "content-type": "image/png", "cache-control": "private, max-age=60" } });
});
