import { readFile } from "fs/promises";
import { join } from "path";

async function exists(path: string): Promise<boolean> {
  try { await readFile(path); return true; } catch { return false; }
}

async function listFiles(dir: string, prefix = "") {
  const { readdir, stat } = await import("fs/promises");
  const entries = await readdir(dir, { withFileTypes: true });
  for (const entry of entries) {
    if (entry.name.startsWith(".")) continue;
    const fullPath = join(dir, entry.name);
    if (entry.isDirectory()) {
      await listFiles(fullPath, prefix + entry.name + "/");
    } else if (entry.name.endsWith(".md")) {
      console.log(`  ${prefix}${entry.name}`);
    }
  }
}

export async function read(target: string) {
  const docsRoot = join(process.cwd(), "docs");
  const fullPath = join(docsRoot, target);

  if (await exists(fullPath)) {
    const content = await readFile(fullPath, "utf-8");
    console.log(`--- ${target} ---\n`);
    console.log(content);
  } else {
    console.error(`File not found: ${target}`);
    console.log(`\nAvailable files:`);
    await listFiles(docsRoot);
  }
}
