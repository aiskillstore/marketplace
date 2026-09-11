import { defineConfig } from "drizzle-kit";
import { getDatabaseConfig } from "./lib/db-url";

const database = getDatabaseConfig();

export default defineConfig({
  schema: ["./lib/schema.ts", "./db/tables/*.ts"],
  out: "./drizzle",
  dialect: database.dialect,
  dbCredentials: {
    url: database.url,
    ...(database.authToken ? { authToken: database.authToken } : {}),
  },
});
