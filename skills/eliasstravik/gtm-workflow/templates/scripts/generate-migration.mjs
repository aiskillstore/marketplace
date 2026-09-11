import { spawn } from "node:child_process";
import { createHash } from "node:crypto";
import { readFile, readdir, writeFile } from "node:fs/promises";
import { join } from "node:path";

const root = process.cwd();
const plainFailure = "This change renames or drops something. Add the new column first, switch the workflow, and drop the old one later.";
function run() {
  return new Promise((resolve) => {
    const child = spawn(join(root, "node_modules/.bin/drizzle-kit"), ["generate", ...process.argv.slice(2)], { cwd: root, stdio: ["ignore", "pipe", "pipe"] });
    let output = "";
    child.stdout.on("data", (value) => output += value); child.stderr.on("data", (value) => output += value);
    const timer = setTimeout(() => child.kill("SIGKILL"), 30_000);
    child.on("close", (code, signal) => { clearTimeout(timer); resolve({ code, signal, output }); });
  });
}
async function emit() {
  const journal = JSON.parse(await readFile(join(root, "drizzle/meta/_journal.json"), "utf8"));
  const files = (await readdir(join(root, "drizzle"))).filter((name) => name.endsWith(".sql")).sort();
  const migrations = await Promise.all(files.map(async (file, index) => {
    const sql = await readFile(join(root, "drizzle", file), "utf8");
    const entry = journal.entries.find((item) => item.tag === file.slice(0, -4));
    return { tag: file.slice(0, -4), hash: createHash("sha256").update(sql).digest("hex"), sql, createdAt: entry?.when ?? index };
  }));
  await writeFile(join(root, "lib/migrations.generated.ts"), `export const migrations = ${JSON.stringify(migrations, null, 2)} as const;\n`);
}
const result = await run();
if (result.signal || result.code !== 0 || /created or renamed|create or rename|interactive/i.test(result.output)) { console.error(plainFailure); process.exitCode = 1; }
else { await emit(); console.log(result.output.trim() || "No schema changes."); }
