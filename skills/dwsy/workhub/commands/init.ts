import { stat, mkdir } from "fs/promises";
import { join } from "path";

const REQUIRED_DIRS = ["adr", "architecture", "issues", "pr"];

async function exists(path: string): Promise<boolean> {
  try { await stat(path); return true; } catch { return false; }
}

export async function init(docsRoot: string) {
  console.log(`📦 Initializing docs at: ${docsRoot}\n`);

  if (!(await exists(docsRoot))) {
    await mkdir(docsRoot, { recursive: true });
    console.log(`✅ Created: ${docsRoot}`);
  }

  for (const dir of REQUIRED_DIRS) {
    const path = join(docsRoot, dir);
    if (!(await exists(path))) {
      await mkdir(path, { recursive: true });
      console.log(`✅ Created: ${path}/`);
    }
  }

  console.log("\n✨ Documentation structure initialized!");
}
