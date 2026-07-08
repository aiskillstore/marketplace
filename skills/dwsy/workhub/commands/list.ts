import { readdir, stat, readFile } from "fs/promises";
import { join } from "path";

async function exists(path: string): Promise<boolean> {
  try { await stat(path); return true; } catch { return false; }
}

async function collect(dir: string, type: "issue" | "pr", results: Array<{ path: string; content: string }>) {
  const entries = await readdir(dir, { withFileTypes: true });
  for (const entry of entries) {
    if (entry.name.startsWith(".")) continue;
    const fullPath = join(dir, entry.name);
    if (entry.isDirectory()) {
      await collect(fullPath, type, results);
    } else if (entry.name.endsWith(".md")) {
      results.push({ path: fullPath, content: await readFile(fullPath, "utf-8") });
    }
  }
}

function extractStatus(content: string) {
  return content.match(/状态[:：]\s*[📝🚧✅⏸️❌]/) || "📝";
}

export async function listIssues() {
  const issuesDir = join(process.cwd(), "docs", "issues");
  if (!(await exists(issuesDir))) return console.log("No issues found.");

  console.log(`📋 Issues:\n`);
  const issues: Array<{ path: string; content: string }> = [];
  await collect(issuesDir, "issue", issues);

  for (const { path, content } of issues) {
    const status = extractStatus(content);
    const title = content.match(/^# Issue: (.+)$/m)?.[1] || path;
    console.log(`  [${status}] ${title}`);
    console.log(`    → ${path.replace(process.cwd() + "/", "")}\n`);
  }
  console.log(`Total: ${issues.length} issue(s)`);
}

export async function listPRs() {
  const prDir = join(process.cwd(), "docs", "pr");
  if (!(await exists(prDir))) return console.log("No PRs found.");

  console.log(`🔀 PRs:\n`);
  const prs: Array<{ path: string; content: string }> = [];
  await collect(prDir, "pr", prs);

  for (const { path, content } of prs) {
    const status = extractStatus(content);
    const title = content.match(/^# (.+)$/m)?.[1] || path;
    console.log(`  [${status}] ${title}`);
    console.log(`    → ${path.replace(process.cwd() + "/", "")}\n`);
  }
  console.log(`Total: ${prs.length} PR(s)`);
}
