import { readdir, stat, readFile } from "fs/promises";
import { join } from "path";

async function exists(path: string): Promise<boolean> {
  try { await stat(path); return true; } catch { return false; }
}

async function searchDir(dir: string, type: string, keyword: string, results: Array<{ type: string; path: string; matches: string[] }>) {
  const entries = await readdir(dir, { withFileTypes: true });
  for (const entry of entries) {
    if (entry.name.startsWith(".")) continue;
    const fullPath = join(dir, entry.name);
    if (entry.isDirectory()) {
      await searchDir(fullPath, type, keyword, results);
    } else if (entry.name.endsWith(".md")) {
      const content = await readFile(fullPath, "utf-8");
      const relPath = fullPath.replace(process.cwd() + "/docs/", "");
      const lines = content.split("\n");
      const matches: string[] = [];
      lines.forEach((line, i) => {
        if (line.toLowerCase().includes(keyword.toLowerCase())) {
          matches.push(`:${i + 1}: ${line.trim().substring(0, 100)}`);
        }
      });
      if (matches.length > 0) results.push({ type, path: relPath, matches });
    }
  }
}

export async function search(keyword: string) {
  if (!keyword) throw new Error("Keyword required");
  console.log(`🔍 Searching for "${keyword}"...\n`);

  const results: Array<{ type: string; path: string; matches: string[] }> = [];
  const docsRoot = join(process.cwd(), "docs");

  for (const [dir, type] of [["issues", "Issue"], ["pr", "PR"]] as const) {
    const path = join(docsRoot, dir);
    if (await exists(path)) await searchDir(path, type, keyword, results);
  }

  if (results.length === 0) {
    console.log("No results found.");
  } else {
    console.log(`Found ${results.length} result(s):\n`);
    for (const r of results) {
      console.log(`[${r.type}] ${r.path}`);
      r.matches.forEach(m => console.log(`  ${m}`));
      console.log();
    }
  }
}
