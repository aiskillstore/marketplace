import { defineEventHandler } from "nitro/h3";
import { renderSvg } from "../../../../lib/diagram-svg";
import { resolveDiagramRequest } from "../../../../lib/diagram-route";

const escape = (value: string) => value.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

export default defineEventHandler(async (event) => {
  const url = new URL(event.req.url);
  if (Number(url.searchParams.get("exp")) * 1000 < Date.now()) return new Response("<!doctype html><title>Expired</title><p>This picture link has expired. Ask for a new one.</p>", { headers: { "content-type": "text/html; charset=utf-8" } });
  const resolved = await resolveDiagramRequest(event as any);
  if (!resolved.ok) return resolved.response;
  const svg = renderSvg(resolved.laidOut);
  return new Response(`<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>${escape(resolved.laidOut.workflow.label)}</title><style>body{margin:0;background:#f8fafc;font-family:system-ui}main{max-width:1400px;margin:auto;padding:24px}svg{width:100%;height:auto;background:white;border-radius:12px;box-shadow:0 1px 3px #0002}</style></head><body><main>${svg}</main></body></html>`, { headers: { "content-type": "text/html; charset=utf-8", "cache-control": "no-store" } });
});
