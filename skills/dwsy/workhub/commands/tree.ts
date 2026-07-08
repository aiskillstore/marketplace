import { readdir, stat } from "fs/promises";
import { join } from "path";

async function exists(path: string): Promise<boolean> {
  try { await stat(path); return true; } catch { return false; }
}

async function treeRecursive(dir: string, prefix = "") {
  const entries = await readdir(dir, { withFileTypes: true });
  for (let i = 0; i < entries.length; i++) {
    const entry = entries[i];
    if (entry.name.startsWith(".")) continue;

    const isLast = i === entries.length - 1;
    const connector = isLast ? "└── " : "├── ";
    console.log(`${prefix}${connector}${entry.name}`);

    if (entry.isDirectory()) {
      await treeRecursive(join(dir, entry.name), prefix + (isLast ? "    " : "│   "));
    }
  }
}

export async function tree(docsRoot: string) {
  console.log(`📦 Docs Root: ${docsRoot}`);
  if (await exists(docsRoot)) {
    await treeRecursive(docsRoot);
  }
}
