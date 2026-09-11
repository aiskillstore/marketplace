import { createHmac, timingSafeEqual } from "node:crypto";

export type DiagramClaims = { path: string; run: string | null; exp: number };

const RUN_KEY = /^[0-9a-f]{32}(?:-batch-\d{3})?$/;

function canonical(claims: DiagramClaims): string {
  return `diagram|${claims.path}|${claims.run ?? "-"}|${claims.exp}`;
}

export function signDiagram(claims: DiagramClaims, secret: string): string {
  return createHmac("sha256", secret).update(canonical(claims)).digest("base64url");
}

export function diagramQuery(claims: DiagramClaims, secret: string): string {
  const query = new URLSearchParams();
  if (claims.run) query.set("run", claims.run);
  query.set("exp", String(claims.exp));
  query.set("sig", signDiagram(claims, secret));
  return query.toString();
}

export function verifyDiagram(
  query: URLSearchParams,
  path: string,
  secret: string,
  now = Date.now(),
): DiagramClaims | null {
  const exp = Number(query.get("exp"));
  const run = query.get("run");
  const signature = query.get("sig") ?? "";
  if (!Number.isInteger(exp) || exp * 1000 < now) return null;
  if (run !== null && !RUN_KEY.test(run)) return null;
  const claims: DiagramClaims = { path, run, exp };
  const expected = Buffer.from(signDiagram(claims, secret));
  const actual = Buffer.from(signature);
  if (expected.length !== actual.length || !timingSafeEqual(expected, actual)) return null;
  return claims;
}
