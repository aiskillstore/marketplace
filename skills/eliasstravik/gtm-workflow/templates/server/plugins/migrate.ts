import { ensureMigrated } from "../../lib/db";

export default async function migrate() {
  void ensureMigrated().catch((error) => console.error(`Migration failed: ${String(error).split("\n")[0]}`));
}
