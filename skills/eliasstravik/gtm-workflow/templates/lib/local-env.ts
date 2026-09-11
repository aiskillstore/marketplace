import { randomBytes } from "node:crypto";
import { readFile, rename, writeFile } from "node:fs/promises";
import { join } from "node:path";

/**
 * Local servers need a run secret for their own routes. Generate one into .env
 * the first time a local command runs so a keyboard user never has to invent it.
 * The hosted sandbox never holds a secret, so nothing is written there.
 */
export async function ensureRunSecret(root: string, env: Record<string, string | undefined> = process.env): Promise<string | undefined> {
  if (env.GTM_SANDBOX === "1") return undefined;
  if (env.GTM_RUN_SECRET) return env.GTM_RUN_SECRET;
  const file = join(root, ".env");
  const secret = randomBytes(32).toString("hex");
  let content = "";
  try { content = await readFile(file, "utf8"); } catch {}
  const line = `GTM_RUN_SECRET=${secret}`;
  const next = /^GTM_RUN_SECRET=.*$/m.test(content)
    ? content.replace(/^GTM_RUN_SECRET=.*$/m, line)
    : `${content}${content && !content.endsWith("\n") ? "\n" : ""}${line}\n`;
  // Create the replacement owner-only and move it into place, so the secret never sits in a file with wider permissions.
  const temporary = `${file}.${process.pid}.tmp`;
  await writeFile(temporary, next, { mode: 0o600, flag: "wx" });
  await rename(temporary, file);
  env.GTM_RUN_SECRET = secret;
  return secret;
}
