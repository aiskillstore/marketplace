import { stat } from "fs/promises";
import { join } from "path";

const REQUIRED_DIRS = ["adr", "architecture", "issues", "pr"];

async function exists(path: string): Promise<boolean> {
  try { await stat(path); return true; } catch { return false; }
}

const PURPOSE: Record<string, string> = {
  adr: "Architecture Decision Records",
  architecture: "System design & boundaries",
  issues: "Task tracking (yyyymmdd-[描述].md)",
  pr: "Change logs (yyyymmdd-[描述].md)"
};

export async function audit(docsRoot: string) {
  console.log(`Auditing docs at: ${docsRoot}\n`);
  if (!(await exists(docsRoot))) {
    console.error("❌ Critical: 'docs/' directory is missing!");
    process.exit(1);
  }

  let healthy = true;
  for (const dir of REQUIRED_DIRS) {
    const path = join(docsRoot, dir);
    if (await exists(path)) {
      console.log(`✅ [OK] ${dir}/`);
    } else {
      console.log(`❌ [Missing] ${dir}/ (${PURPOSE[dir]})`);
      healthy = false;
    }
  }

  console.log(healthy ? "\n✨ Documentation structure is healthy." : "\n⚠️  Needs improvement.");
}
