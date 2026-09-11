import { mkdirSync } from "node:fs";
import { dirname, resolve } from "node:path";

export type DatabaseConfig = {
  url: string;
  authToken: string | undefined;
  dialect: "sqlite" | "turso";
};

export function getDatabaseConfig(): DatabaseConfig {
  const url = process.env.TURSO_DATABASE_URL || "file:./data/gtm.db";
  const authToken = process.env.TURSO_AUTH_TOKEN || undefined;
  const dialect = url.startsWith("file:") ? "sqlite" : "turso";

  if (process.env.GTM_SANDBOX === "1" && dialect === "sqlite") {
    throw new Error(
      "GTM_SANDBOX=1 requires TURSO_DATABASE_URL; a sandbox cannot use a file database.",
    );
  }

  if (dialect === "sqlite") {
    const filename = url.slice("file:".length);
    mkdirSync(dirname(resolve(filename)), { recursive: true });
  }

  return { url, authToken, dialect };
}
